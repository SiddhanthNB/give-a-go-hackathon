import lib.utils.constants as constants
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings

def get_model(role: str) -> GoogleModel:
    model_name = 'gemini-2.5-flash-lite'
    provider = GoogleProvider(api_key=constants.GOOGLE_API_KEY, vertexai=False)
    match role:
        case 'translator':
            settings = GoogleModelSettings(
                temperature=0.1,
                max_tokens=1024,
                google_thinking_config={'thinking_level': 'minimal'}
            )
        case 'strategist':
            settings = GoogleModelSettings(
                temperature=0.7,
                max_tokens=2048,
                google_thinking_config={'thinking_level': 'medium'}
            )
        case 'guardrail':
            settings = GoogleModelSettings(
                temperature=0.0,
                max_tokens=512,
                google_thinking_config={'thinking_level': 'low'}
            )
        case _:
            raise ValueError(f"Unknown role: {role}")

    return GoogleModel(model_name=model_name, provider=provider, settings=settings)
