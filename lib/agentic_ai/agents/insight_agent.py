from pydantic_ai import Agent, RunContext
from lib.agentic_ai.config import get_model
from lib.agentic_ai.models.insights import CommercialJudgment # Matches your image
from lib.agentic_ai.agents.metric_agent import metric_agent
from lib.helpers.query import run_query # Your database function
from pathlib import Path

# This points to insight_system.md
prompt_path = Path(__file__).parent.parent / "prompts" / "insight_system.md"
system_prompt = prompt_path.read_text()

insight_agent = Agent(
    get_model(),
    result_type=CommercialJudgment,
)

@insight_agent.system_prompt
def add_instructions(ctx: RunContext[None]) -> str:
    return system_prompt


@insight_agent.tool
async def get_hotel_data(ctx: RunContext[None], user_query: str) -> str:
    """
    Call this tool to fetch hotel metrics (ADR, RevPAR, Occupancy, etc.)
    when the user asks about performance or trends.
    """
    translation = await metric_agent.run(user_query)

    data_results = run_query(translation.data)

    return data_results.to_json()
