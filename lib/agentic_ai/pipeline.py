from datetime import date
from lib.agentic_ai.models.models import UserRequest, UserResponse
from lib.agentic_ai.agents.guardrail import guardrail_agent
from lib.agentic_ai.agents.translator import translator_agent
from lib.agentic_ai.agents.strategist import strategist_agent
from lib.utils.sql_engine import run_sql_engine
from app.core.db import db_session

async def run_pipeline(user_input: str):
    """
    Orchestrates the multi-agent flow with the SQL Engine short-circuit.
    """
    request = UserRequest(query=user_input, current_date=date.today())

    guard_result = await guardrail_agent.run(request.query)
    if not guard_result.output.is_valid:
        return UserResponse(
            headline="Query Restricted",
            analysis=guard_result.output.reason or "This query is out of scope.",
            status="error"
        )

    translation = await translator_agent.run(request.query)

    db_result = run_sql_engine(translation.output, db_session)
    if db_result.is_empty:
        return UserResponse(
            headline="Insufficient Data",
            analysis="No data found for the requested period.",
            status="error"
        )

    final_report = await strategist_agent.run(
        f"User Question: {request.query}\n\nData Results: {db_result.model_dump_json()}"
    )

    return final_report.data