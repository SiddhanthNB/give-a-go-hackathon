from pydantic_ai.models.groq import GroqModel
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.models.mistral import MistralModel

import lib.utils.constants as constants


def get_model():
    """
    Utility to return the Pydantic AI model instance based on your constant.
    """
    if constants.LLM_PROVIDER == 'groq':
        return GroqModel('llama-3.1-8b-instant')
    elif constants.LLM_PROVIDER == 'mistral':
        return MistralModel('ministral-8b-2410')

    return GoogleModel('gemini-2.5-flash-lite')
