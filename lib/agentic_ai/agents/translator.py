from datetime import datetime
from pathlib import Path
from pydantic_ai import Agent
from lib.agentic_ai.models.models import TranslatedMetric
from lib.agentic_ai.config import get_model

from lib.utils.metrics_catalog import get_catalog_markdown, SEGMENT_MAPPING, DIMENSION_ALIASES

prompt_path = Path(__file__).parent.parent / "prompts" / "system" / "translator.md"
prompt = prompt_path.read_text()

translator_agent = Agent(
    get_model(),
    output_type=TranslatedMetric
)

@translator_agent.system_prompt
def add_system_prompt():
    catalog_md = get_catalog_markdown()
    today = datetime.now().date().isoformat()

    return (
        prompt
        .replace("{{ current_date }}", today)
        .replace("{{ metric_catalog_markdown }}", catalog_md)
        .replace("{{ segment_mapping }}", str(SEGMENT_MAPPING))
        .replace("{{ dimension_mapping }}", str(DIMENSION_ALIASES))
    )
