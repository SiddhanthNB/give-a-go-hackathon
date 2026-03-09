from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
from datetime import date, datetime

# --- INPUT LAYER ---
class UserRequest(BaseModel):
    """The raw entry point into the pipeline."""
    query: str = Field(..., description="The user's natural language question")
    current_ts: datetime = Field(..., description="The reference timestamp for relative date math")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Auth or context data")

class AgentContext(BaseModel):
    """Shared context passed to all agents."""
    current_ts: datetime = Field(..., description="Pipeline reference timestamp for relative calculations")

# --- GUARDRAIL LAYER ---
class GuardrailResponse(BaseModel):
    """The output of the Guardrail Agent."""
    is_valid: bool = Field(..., description="Whether the query passed the guardrails")
    reason: Optional[str] = Field(None, description="If invalid, a polite explanation")

# --- TRANSLATION LAYER ---
class DateBucket(BaseModel):
    """Defines a specific time window for comparison or single-period analysis."""
    label: str = Field(..., description="Unique label like 'this_week' or 'last_month'")
    start_date: date
    end_date: date

class TranslatedMetric(BaseModel):
    """The structured output of the Translator Agent."""
    metrics: List[str] = Field(..., description="Metric keys from catalog, e.g., ['total_revenue']")
    buckets: List[DateBucket] = Field(..., description="Date ranges to query")
    group_by: List[str] = Field(default_factory=list, description="Dimensions like ['market_name']")
    filters: Dict[str, List[Any]] = Field(default_factory=dict, description="Column-value filters")
    exclude_cancelled: bool = True


# --- DATA LAYER ---
class SQLResult(BaseModel):
    """The deterministic output from the database execution."""
    raw_rows: List[Dict[str, Any]]
    is_empty: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


# --- OUTPUT LAYER ---
class StrategicOutcome(BaseModel):
    """The raw output from the Strategist Agent before final formatting."""
    headline: str = Field(..., description="The 'What': High-stakes executive summary")
    highlights: List[str] = Field(default_factory=list, description="The 'Pulse': 3-4 numerical facts/observations found in the data")
    judgment: str = Field(..., description="The 'Why': Concise narrative (max 3 sentences) on the strategic meaning behind the highlights")
    recommendations: List[str] = Field(default_factory=list, description="The 'Action': Prescriptive steps")

class UserResponse(BaseModel):
    """The final payload for the UI."""
    data: Optional[StrategicOutcome] = Field(None, description="The structured response to be rendered in the UI")
    error: Optional[str] = Field(None, description="Error message if something went wrong")
    success: bool = True
