from pydantic import BaseModel, Field, field_validator
from typing import List, Literal, Optional, Any
from datetime import date, timedelta
from lib.helpers.metrics_catalog import METRIC_CATALOG

AvailableMetrics = Literal[tuple(METRIC_CATALOG.keys())]

class MetricRequest(BaseModel):
    """The structured parameters for the Query Layer."""
    intent: str = Field(default="metric_value", description="One of: metric_value, breakdown, trend, comparison, briefing")
    metrics: List[str] = Field(default_factory=lambda: ["revenue"])
    start_date: date = Field(default_factory=date.today)
    end_date: date = Field(default_factory=lambda: date.today() + timedelta(days=30))
    segments: Optional[List[str]] = Field(default=None)
    comparison_period: Optional[str] = Field(default=None, description="e.g., 'last_year'")

    @field_validator('metrics', mode='after')
    @classmethod
    def validate_metrics(cls, v: List[str]) -> List[str]:
        valid_keys = set(METRIC_CATALOG.keys())
        synonym_map = {}
        for key, metric_def in METRIC_CATALOG.items():
            synonym_map[key.lower()] = key
            for syn in metric_def.synonyms:
                synonym_map[syn.lower()] = key

        normalized = []
        for metric in v:
            if metric in valid_keys:
                normalized.append(metric)
                continue

            key = synonym_map.get(metric.lower().strip())
            if key:
                normalized.append(key)
                continue

            raise ValueError(
                f"Invalid metric: '{metric}'. "
                f"Must be one of: {', '.join(valid_keys)}"
            )

        return normalized

class DataResponse(BaseModel):
    """What the Query Layer returns to the Agent."""
    data: List[dict] = Field(description="The raw rows from the DB")
    summary: dict = Field(description="Aggregated totals/averages calculated by Python")
    metadata: dict = Field(default_factory=dict)
