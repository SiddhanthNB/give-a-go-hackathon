import pandas as pd
from sqlalchemy import text
from typing import Dict, Any
from lib.agentic_ai.models import TranslatedMetric, SQLResult

BASE_VIEW = """
SELECT
    res.*,
    rt.display_name as room_display_name, rt.room_class,
    mc.market_name, mc.macro_group,
    cc.channel_name, cc.channel_group
FROM public.reservations_hackathon res
LEFT JOIN public.room_type_lookup rt ON res.space_type = rt.space_type
LEFT JOIN public.market_code_lookup mc ON res.market_code = mc.market_code
LEFT JOIN public.channel_code_lookup cc ON res.channel_code = cc.channel_code
"""

METRIC_SQL_MAP = {
    "total_revenue": "SUM(daily_total_revenue_before_tax)",
    "room_revenue": "SUM(daily_room_revenue_before_tax)",
    "res_count": "COUNT(DISTINCT reservation_id)",
    "room_nights": "SUM(number_of_spaces)",
    "adr": "SUM(daily_room_revenue_before_tax) / NULLIF(SUM(number_of_spaces), 0)"
}

def run_sql_engine(translation: TranslatedMetric, db_session) -> SQLResult:
    """
    Executes an agile, multi-bucket aggregate query based on Translator Agent output.
    """
    params: Dict[str, Any] = {}

    case_conditions = []
    for i, bucket in enumerate(translation.buckets):
        s_key, e_key = f"s{i}", f"e{i}"
        case_conditions.append(f"WHEN stay_date BETWEEN :{s_key} AND :{e_key} THEN '{bucket.label}'")
        params[s_key] = bucket.start_date
        params[e_key] = bucket.end_date

    bucket_label_sql = f"CASE {' '.join(case_conditions)} ELSE 'out_of_range' END AS bucket_label"

    group_dims = ["bucket_label"] + translation.group_by

    aggs = [f"{METRIC_SQL_MAP.get(m, 'SUM(number_of_spaces)')} AS {m}" for m in translation.metrics]

    where_clauses = ["bucket_label != 'out_of_range'"]

    if translation.exclude_cancelled:
        where_clauses.append("reservation_status != 'Cancelled'")

    for col, values in translation.filters.items():
        param_key = f"filter_{col}"
        where_clauses.append(f"{col} IN :{param_key}")
        params[param_key] = tuple(values)

    query = f"""
    WITH labeled_data AS (
        SELECT *, {bucket_label_sql}
        FROM ({BASE_VIEW}) AS source
    )
    SELECT
        {', '.join(group_dims)},
        {', '.join(aggs)}
    FROM labeled_data
    WHERE {' AND '.join(where_clauses)}
    GROUP BY {', '.join(group_dims)}
    ORDER BY bucket_label DESC
    """

    try:
        df = pd.read_sql(text(query), db_session.bind, params=params)

        if df.empty:
            return SQLResult(raw_rows=[], summary={}, is_empty=True)

        return SQLResult(
            raw_rows=df.to_dict(orient="records"),
            summary={"total_buckets": len(translation.buckets), "metrics_calculated": translation.metrics},
            metadata={"sql_logic": "multi_bucket_aggregate"},
            is_empty=False
        )
    except Exception as e:
        return SQLResult(raw_rows=[], summary={"error": str(e)}, is_empty=True)
