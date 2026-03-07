import pandas as pd
from sqlalchemy import text
from lib.agentic_ai.models.metrics import MetricRequest, DataResponse
from lib.helpers.metrics_catalog import get_metric_definition
from app.db import engine # Assuming engine is defined here

def run_query(request: MetricRequest) -> DataResponse:
    metric_def = get_metric_definition(request.metrics[0])

    date_col = metric_def.date_field # Automatically switches between stay_date and booking_date

    sql = f"""
        SELECT {date_col}, segment, revenue, adr
        FROM reservations
        WHERE {date_col} BETWEEN :start AND :end
    """

    params = {
        "start": request.start_date,
        "end": request.end_date
    }

    # 2. Add Dynamic Filters (Segments)
    if request.segments:
        sql += " AND segment IN :segments"
        params["segments"] = tuple(request.segments)

    # 3. Execute and Load into Pandas
    with engine.connect() as conn:
        df = pd.read_sql(text(sql), conn, params=params)

    if df.empty:
        return DataResponse(data=[], summary={"message": "No data found"}, metadata={})

    # 4. Calculate Summaries (The 'Analyst' work)
    # We do this in Python to keep the SQL simple
    summary = {
        "total_revenue": float(df['revenue'].sum()),
        "average_adr": float(df['adr'].mean()),
        "total_bookings": len(df),
        "cancellation_rate": float(df['is_cancelled'].mean() * 100),
        "occupancy_estimate": float((len(df) / 150) * 100) # Assuming 150 total rooms
    }

    # 5. Handle Comparison (Lean logic for YoY/MoM)
    if request.comparison_period == "last_year":
        # Hackathon shortcut: In a real app, you'd run a second query for last year.
        # For now, let's just tag the metadata.
        summary["comparison_note"] = "YoY Comparison requested but not yet processed."

    # 6. Return the Structured Response
    return DataResponse(
        data=df.to_dict(orient="records"),
        summary=summary,
        metadata={"query_period": f"{request.start_date} to {request.end_date}"}
    )
