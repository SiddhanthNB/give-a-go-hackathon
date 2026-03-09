import random
import asyncio
from datetime import datetime
from pydantic_ai import Agent, exceptions
from lib.agentic_ai.models.models import UserRequest, UserResponse, AgentContext
from lib.agentic_ai.agents.guardrail import guardrail_agent
from lib.agentic_ai.agents.translator import translator_agent
from lib.agentic_ai.agents.strategist import strategist_agent
from lib.utils.sql_engine import make_db_query
from app.core.db import db_session

async def _robust_agent_run(role_label: str, agent: Agent, max_retries: int = 3, base_delay: float = 1.0, **kwargs):
    for attempt in range(max_retries):
        try:
            print(f"[{role_label}] Attempt {attempt+1} running agent...")
            return await agent.run(**kwargs)
        except (exceptions.UsageLimitExceeded, exceptions.ModelAPIError) as e:
            if attempt == max_retries - 1:
                raise

            wait_time = (base_delay * (2 ** attempt)) + random.uniform(0, 0.5)
            print(f"[{role_label}] 429/503 detected. Retry {attempt+1}/{max_retries} in {wait_time:.2f}s...")
            await asyncio.sleep(wait_time)
        except Exception as e:
            raise

async def run_pipeline(user_input: str, current_ts: datetime):
    """
    Orchestrates the multi-agent flow with the SQL Engine short-circuit.
    """
    request = UserRequest(query=user_input, current_ts=current_ts)
    context = AgentContext(current_ts=request.current_ts)

    guard_result = await _robust_agent_run(
        "Guardrail",
        guardrail_agent,
        user_prompt=request.query,
        deps=context
    )

    if not guard_result.output.is_valid:
        return UserResponse(
            error=f"Guardrail check failed: {guard_result.output.reason}",
            success=False
        )

    translation = await _robust_agent_run(
        "Translator",
        translator_agent,
        user_prompt=request.query,
        deps=context
    )

    with db_session() as db:
        db_result = make_db_query(translation.output, db)

    if db_result.is_empty:
        return UserResponse(
            error="No relevant data found for the given query.",
            success=False
        )

    final_report = await _robust_agent_run(
        "Strategist", strategist_agent,
        user_prompt=f"User Question: {request.query}\n\nData Results: {db_result.model_dump_json()}",
        deps=context
    )

    return UserResponse(data=final_report.output)
