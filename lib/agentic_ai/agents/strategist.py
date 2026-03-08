from datetime import datetime
from pathlib import Path
from pydantic_ai import Agent
from lib.agentic_ai.models import UserResponse
from lib.agentic_ai.config import get_model

prompt_path = Path(__file__).parent.parent / "prompts" / "system" / "strategist.md"
prompt = prompt_path.read_text()

strategist_agent = Agent(
    get_model(),
    output_type=UserResponse,
    system_prompt=prompt
)
