import pandas as pd
from sqlalchemy import text
from typing import Dict, Any
from sqlalchemy.orm.session import Session
from lib.agentic_ai.models.models import TranslatedMetric, SQLResult
from lib.utils.metrics_catalog import METRIC_CATALOG

BASE_VIEW = """
SELECT
    res.*,
    rt.display_name as room_display_name, rt.room_class, rt.number_of_rooms as type_capacity,
    mc.market_name, mc.macro_group,
    cc.channel_name, cc.channel_group
FROM public.reservations_hackathon res
LEFT JOIN public.room_type_lookup rt ON res.space_type = rt.space_type
LEFT JOIN public.market_code_lookup mc ON res.market_code = mc.market_code
LEFT JOIN public.channel_code_lookup cc ON res.channel_code = cc.channel_code
"""

def make_db_query(translation: TranslatedMetric, db: Session) -> SQLResult:
    params: Dict[str, Any] = {}

    primary_metric = translation.metrics[0] if translation.metrics else "revenue"
    metric_def = METRIC_CATALOG.get(primary_metric)
    date_col = metric_def.date_field if metric_def else "stay_date"

    case_conditions = []
    for i, bucket in enumerate(translation.buckets):
        s_key, e_key = f"s{i}", f"e{i}"
        case_conditions.append(f"WHEN {date_col} BETWEEN :{s_key} AND :{e_key} THEN '{bucket.label}'")
        params[s_key] = bucket.start_date
        params[e_key] = bucket.end_date

    bucket_label_sql = f"CASE {' '.join(case_conditions)} ELSE 'out_of_range' END AS bucket_label"

    aggs = []
    for m_key in translation.metrics:
        m = METRIC_CATALOG.get(m_key)
        if not m: continue

        sql_fragment = ""
        if m_key == "adr":
            sql_fragment = "SUM(daily_room_revenue_before_tax) / NULLIF(SUM(number_of_spaces), 0)"

        elif m_key == "occupancy":
            sql_fragment = "SUM(number_of_spaces)::float / NULLIF(133 * COUNT(DISTINCT stay_date), 0) * 100"

        elif m_key == "group_share":
            sql_fragment = "SUM(CASE WHEN is_block = TRUE THEN daily_total_revenue_before_tax ELSE 0 END) / NULLIF(SUM(daily_total_revenue_before_tax), 0) * 100"

        elif m.default_aggregation == "distinct_count":
            sql_fragment = m.reservation_count_method
        elif m.revenue_field:
            sql_fragment = f"SUM({m.revenue_field})"
        else:
            sql_fragment = m.room_night_method

        aggs.append(f"{sql_fragment} AS {m_key}")

    group_dims = ["bucket_label"] + translation.group_by
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
        result = db.execute(text(query), params)

        raw_rows = [dict(row) for row in result.mappings()]

        return SQLResult(
            raw_rows=raw_rows,
            summary={
                "metrics": translation.metrics,
                "date_context": date_col,
                "row_count": len(raw_rows)
            },
            is_empty=len(raw_rows) == 0
        )
    except Exception as e:
        return SQLResult(raw_rows=[], summary={"error": str(e)}, is_empty=True)
