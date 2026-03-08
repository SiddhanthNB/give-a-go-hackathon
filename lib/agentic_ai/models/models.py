from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal, Optional
from datetime import date

# --- INPUT LAYER ---
class UserRequest(BaseModel):
    """The raw entry point into the pipeline."""
    query: str = Field(..., description="The user's natural language question")
    current_date: date = Field(..., description="The reference 'today' for relative date math")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Auth or context data")

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
class Insight(BaseModel):
    """A specific observation made by the Strategist."""
    type: str = Field(..., description="trend, alert, or opportunity")
    message: str
    impact: Optional[str] = None

class UserResponse(BaseModel):
    """The final payload for the UI."""
    headline: str = Field(..., description="Punchy summary of the result")
    analysis: str = Field(..., description="Markdown-formatted deep dive")
    comparison_data: Optional[List[Dict[str, Any]]] = None
    insights: List[Insight] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    status: Literal["success", "error"] = "success"
