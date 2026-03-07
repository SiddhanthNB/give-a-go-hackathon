from pydantic import BaseModel, Field
from typing import List

class Recommendation(BaseModel):
    action: str = Field(description="The specific step the GM should take")
    rationale: str = Field(description="The 'Why' based on the data")
    expected_impact: str = Field(description="Estimated revenue or occupancy gain")

class CommercialJudgment(BaseModel):
    """The final structured output for the Streamlit UI."""
    headline: str = Field(description="A punchy summary of the situation")
    analysis: str = Field(description="Deep dive into trends (Pacing, Yield, Risk)")
    risks: List[str] = Field(description="Potential threats identified")
    opportunities: List[str] = Field(description="Potential wins identified")
    recommendations: List[Recommendation]
    priority_score: int = Field(ge=1, le=10, description="How urgent is this? 10 is critical.")
