import pandas as pd
from sqlalchemy import text
from datetime import timedelta
from lib.agentic_ai.models.metrics import MetricRequest, DataResponse
from lib.helpers.metrics_catalog import get_metric_definition
from app.db import db_session

TOTAL_ROOMS_AVAILABLE = 150

def run_query(request: MetricRequest) -> DataResponse:
    print("[DEBUG][query] run_query start")
    # 1. Identify the primary metric and its date field
    # We use the first metric to determine if we query by stay_date or create_datetime
    primary_metric = request.metrics[0]
    metric_def = get_metric_definition(primary_metric)
    date_col = metric_def.date_field
    print(f"[DEBUG][query] primary_metric={primary_metric} date_col={date_col}")

    def fetch_data(start, end):
        """Helper to run the actual SQL for a specific date range."""
        print(f"[DEBUG][query] fetch_data start={start} end={end}")
        # Fix: Pulling ALL columns needed for the summaries (status, revenue, rooms)
        sql = f"""
            SELECT
                {date_col},
                market_code as segment,
                daily_total_revenue_before_tax as revenue,
                daily_room_revenue_before_tax as room_revenue,
                number_of_spaces,
                reservation_status
            FROM reservations_hackathon
            WHERE {date_col} BETWEEN :start AND :end
        """
        params = {"start": start, "end": end}
        if request.segments:
            sql += " AND market_code IN :segments"
            params["segments"] = tuple(request.segments)
            print(f"[DEBUG][query] segments filter={params['segments']}")

        print("[DEBUG][query] executing SQL")
        with db_session() as db:
            df_local = pd.read_sql(text(sql), db.get_bind(), params=params)
        print(f"[DEBUG][query] rows fetched={len(df_local)}")
        if not df_local.empty:
            print(f"[DEBUG][query] sample row={df_local.iloc[0].to_dict()}")
        return df_local

    # 2. Fetch Current Period Data
    df = fetch_data(request.start_date, request.end_date)

    if df.empty:
        print("[DEBUG][query] no data found")
        return DataResponse(data=[], summary={"message": "No data found"}, metadata={})

    # 3. Calculate Summaries
    # Fix: derive 'is_cancelled' from 'reservation_status' to avoid KeyError
    print("[DEBUG][query] computing summaries")
    df['is_cancelled'] = df['reservation_status'].str.lower() == 'cancelled'

    # Only calculate performance on non-cancelled rows per your rules
    active_df = df[~df['is_cancelled']]

    summary = {
        "total_revenue": float(active_df['revenue'].sum()),
        "average_adr": float(active_df['room_revenue'].sum() / active_df['number_of_spaces'].sum()) if active_df['number_of_spaces'].sum() > 0 else 0,
        "total_room_nights": int(active_df['number_of_spaces'].sum()),
        "cancellation_rate": float((df['is_cancelled'].sum() / len(df)) * 100) if len(df) > 0 else 0,
        "occupancy": float((active_df['number_of_spaces'].sum() / (TOTAL_ROOMS_AVAILABLE * len(df[date_col].unique()))) * 100) if not active_df.empty else 0
    }
    print(f"[DEBUG][query] summary={summary}")

    # 4. Implement YoY Comparison (No more shortcuts)
    if request.comparison_period == "last_year":
        print("[DEBUG][query] comparison_period=last_year")
        # Shift dates by exactly 364 days to align day-of-week (e.g., Friday vs Friday)
        ly_start = request.start_date - timedelta(days=364)
        ly_end = request.end_date - timedelta(days=364)

        ly_df = fetch_data(ly_start, ly_end)

        if not ly_df.empty:
            print("[DEBUG][query] last_year data found")
            ly_df['is_cancelled'] = ly_df['reservation_status'].str.lower() == 'cancelled'
            ly_active = ly_df[~ly_df['is_cancelled']]
            ly_rev = ly_active['revenue'].sum()

            summary["yo_y_revenue_change_pct"] = float(((summary["total_revenue"] - ly_rev) / ly_rev) * 100) if ly_rev > 0 else 0
            summary["last_year_revenue"] = float(ly_rev)
        else:
            print("[DEBUG][query] last_year data empty")

    # 5. Return Structured Response
    print("[DEBUG][query] returning response")
    return DataResponse(
        data=active_df.head(100).to_dict(orient="records"), # Limit UI payload
        summary=summary,
        metadata={
            "query_period": f"{request.start_date} to {request.end_date}",
            "metric_used": primary_metric,
            "date_field_queried": date_col
        }
    )
