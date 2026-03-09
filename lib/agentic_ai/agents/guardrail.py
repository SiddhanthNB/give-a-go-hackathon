from pathlib import Path
from pydantic_ai import Agent
from lib.agentic_ai.models import GuardrailResponse
from lib.agentic_ai.config import get_model

prompt_path = Path(__file__).parent.parent / "prompts" / "system" / "guardrail.md"
prompt = prompt_path.read_text()

guardrail_agent = Agent(
    get_model('guardrail'),
    output_type=GuardrailResponse,
    system_prompt=prompt
)
