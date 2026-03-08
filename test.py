import asyncio
from lib.agentic_ai.pipeline import run_pipeline

user_input = 'helllo'

asyncio.run(run_pipeline(user_input))
