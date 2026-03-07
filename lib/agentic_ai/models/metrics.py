from pydantic import BaseModel, Field, field_validator
from typing import List, Literal, Optional, Any
from datetime import date
from lib.helpers.metrics_catalog import METRIC_CATALOG

AvailableMetrics = Literal[tuple(METRIC_CATALOG.keys())]

class MetricRequest(BaseModel):
    """The structured parameters for the Query Layer."""
    intent: str = Field(description="One of: metric_value, breakdown, trend, comparison, briefing")
    metrics: List[str]
    start_date: date
    end_date: date
    segments: Optional[List[str]] = Field(default=None)
    comparison_period: Optional[str] = Field(default=None, description="e.g., 'last_year'")

    @field_validator('metrics', mode='after')
    @classmethod
    def validate_metrics(cls, v: List[str]) -> List[str]:
        valid_keys = set(METRIC_CATALOG.keys())
        for metric in v:
            if metric not in valid_keys:
                raise ValueError(
                    f"Invalid metric: '{metric}'. "
                    f"Must be one of: {', '.join(valid_keys)}"
                )
        return v

class DataResponse(BaseModel):
    """What the Query Layer returns to the Agent."""
    data: List[dict] = Field(description="The raw rows from the DB")
    summary: dict = Field(description="Aggregated totals/averages calculated by Python")
    metadata: dict = Field(default_factory=dict)
