from pydantic_ai import Agent, RunContext
from lib.agentic_ai.config import get_model
from lib.agentic_ai.models.metrics import MetricRequest
from datetime import datetime
from pathlib import Path

# Import all required mapping data
from lib.helpers.metrics_catalog import (
    METRIC_CATALOG,
    SEGMENT_MAPPING,
    DIMENSION_ALIASES,
    get_catalog_markdown,
)

prompt_path = Path(__file__).parent.parent / "prompts" / "metric_system.md"

metric_agent = Agent(
    get_model(),
    output_type=MetricRequest,
    output_retries=3,
    retries=2,
)
print("[DEBUG][agent] metric_agent initialized")

@metric_agent.system_prompt
def inject_catalog(ctx: RunContext[None]) -> str:
    print("[DEBUG][agent] inject_catalog start")
    raw_prompt = prompt_path.read_text()

    # Derived lists for date interpretation rules
    stay_metrics = [k for k, v in METRIC_CATALOG.items() if v.date_field == "stay_date"]
    book_metrics = [k for k, v in METRIC_CATALOG.items() if v.date_field == "create_datetime"]

    # Replacement Map
    replacements = {
        "{{ metric_catalog }}": get_catalog_markdown(),
        "{{ segment_mapping }}": "\n".join([f"- {k} -> {v}" for k, v in SEGMENT_MAPPING.items()]),
        "{{ dimension_mapping }}": "\n".join([f"- {k} -> {v}" for k, v in DIMENSION_ALIASES.items()]),
        "{{ stay_date_metrics }}": ", ".join(stay_metrics),
        "{{ booking_date_metrics }}": ", ".join(book_metrics),
        "{{ current_date }}": datetime.now().strftime('%Y-%m-%d')
    }

    for placeholder, value in replacements.items():
        raw_prompt = raw_prompt.replace(placeholder, value)

    print("[DEBUG][agent] inject_catalog complete")
    return raw_prompt
