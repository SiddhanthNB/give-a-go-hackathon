from pydantic_ai import Agent, RunContext
from lib.agentic_ai.config import get_model
from lib.helpers.query import run_query
from lib.agentic_ai.models.metrics import MetricRequest
from datetime import datetime
from pathlib import Path

from lib.helpers.metrics_catalog import get_catalog_markdown, get_mapping_markdown

prompt_path = Path(__file__).parent.parent / "prompts" / "metric_system.md"
system_prompt = prompt_path.read_text()

metric_agent = Agent(
    get_model(),
    result_type=MetricRequest,
)

@metric_agent.system_prompt
def inject_catalog(ctx: RunContext[None]) -> str:
    raw_prompt = prompt_path.read_text()

    full_prompt = raw_prompt.replace("{{ metric_catalog }}", get_catalog_markdown())
    full_prompt = full_prompt.replace("{{ segment_mapping }}", get_mapping_markdown())
    full_prompt = full_prompt.replace("{{ current_date }}", datetime.now().strftime('%Y-%m-%d'))

    return full_prompt
