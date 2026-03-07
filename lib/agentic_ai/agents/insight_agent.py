from pydantic_ai import Agent, RunContext
from lib.agentic_ai.config import get_model
from lib.agentic_ai.models.insights import CommercialJudgment
from lib.agentic_ai.models.metrics import MetricRequest
from lib.agentic_ai.agents.metric_agent import metric_agent
from lib.helpers.query import run_query
from pathlib import Path

prompt_path = Path(__file__).parent.parent / "prompts" / "insight_system.md"
system_prompt = prompt_path.read_text()

insight_agent = Agent(
    get_model(),
    output_type=CommercialJudgment,
    system_prompt=system_prompt,
    output_retries=3,
    retries=2,
)
print("[DEBUG][agent] insight_agent initialized")

# Renamed to match the prompt's 'call_metric_analyst' instruction
@insight_agent.tool
async def call_metric_analyst(ctx: RunContext[None], user_query: str) -> str:
    """
    Retrieves hotel KPI summaries (Revenue, ADR, Occupancy, etc.) from the Analyst.
    Use this for high-level performance questions.
    """
    print("[DEBUG][agent] call_metric_analyst start")
    # 1. Get structured MetricRequest from the Metric Agent
    print("[DEBUG][agent] running metric_agent")
    try:
        translation = await metric_agent.run(user_query)
        metric_request = translation.output
    except Exception as exc:
        print(f"[DEBUG][agent] metric_agent error: {exc}")
        metric_request = MetricRequest()
        print("[DEBUG][agent] using default MetricRequest")
    print("[DEBUG][agent] metric_agent complete")

    # 2. Execute the query using the extracted data
    print("[DEBUG][agent] running query")
    data_results = run_query(metric_request)
    print("[DEBUG][agent] query complete")

    # 3. Return as JSON string using the correct Pydantic method
    print("[DEBUG][agent] returning data_results")
    return data_results.model_dump_json()

@insight_agent.tool
async def query_db_layer(ctx: RunContext[None], user_query: str) -> str:
    """
    Provides raw reservation data for deep inspection of specific dates or cancellations.
    """
    print("[DEBUG][agent] query_db_layer start")
    # For a hackathon, we can route both through the same analyst logic
    return await call_metric_analyst(ctx, user_query)
