from dataclasses import dataclass, field
from typing import Dict, List, Optional, Literal

# Standardizing our intent and date types per README requirements
IntentType = Literal["metric_value", "breakdown", "trend", "comparison", "briefing"]
DateField = Literal["stay_date", "create_datetime"]

@dataclass
class MetricDefinition:
    name: str
    description: str
    date_field: DateField
    revenue_field: Optional[str] = None
    exclude_cancelled_by_default: bool = True
    reservation_count_method: str = "COUNT(DISTINCT reservation_id)"
    room_night_method: str = "SUM(number_of_spaces)"
    allowed_group_bys: List[str] = field(default_factory=list)
    allowed_filters: List[str] = field(default_factory=list)
    synonyms: List[str] = field(default_factory=list)
    unit: str = "number"
    default_aggregation: str = "sum"
    business_rule: Optional[str] = None

METRIC_CATALOG: Dict[str, MetricDefinition] = {
    "revenue": MetricDefinition(
        name="revenue",
        description="Total hotel revenue (Room + Packages). Use for bottom-line financials.",
        date_field="stay_date",
        revenue_field="daily_total_revenue_before_tax",
        exclude_cancelled_by_default=True,
        allowed_group_bys=["stay_date", "channel_code", "market_code", "space_type"],
        allowed_filters=["date_range", "channel_code", "market_code", "space_type", "future_only"],
        synonyms=["revenue", "sales", "total revenue", "otb revenue", "booked revenue"],
        unit="currency",
        business_rule="Calculated on stay_date. Excludes cancelled records."
    ),
    "room_nights": MetricDefinition(
        name="room_nights",
        description="Total room nights sold. README Rule: Accounts for multi-room reservations.",
        date_field="stay_date",
        exclude_cancelled_by_default=True,
        room_night_method="SUM(number_of_spaces)",
        allowed_group_bys=["stay_date", "channel_code", "market_code", "space_type"],
        allowed_filters=["date_range", "channel_code", "market_code", "space_type", "future_only"],
        synonyms=["room nights", "rooms sold", "nights sold"],
        unit="count",
    ),
    "adr": MetricDefinition(
        name="adr",
        description="Average Daily Rate. README Rule: Calculated using room revenue only.",
        date_field="stay_date",
        revenue_field="daily_room_revenue_before_tax",
        exclude_cancelled_by_default=True,
        allowed_group_bys=["stay_date", "channel_code", "market_code", "space_type"],
        allowed_filters=["date_range", "channel_code", "market_code", "space_type", "future_only"],
        synonyms=["adr", "average daily rate", "average rate"],
        unit="currency",
        default_aggregation="derived",
        business_rule="Formula: SUM(room_revenue) / NULLIF(SUM(number_of_spaces), 0)."
    ),
    "reservations": MetricDefinition(
        name="reservations",
        description="Distinct reservation count. README Rule: 1 row is NOT 1 reservation.",
        date_field="stay_date",
        exclude_cancelled_by_default=True,
        reservation_count_method="COUNT(DISTINCT reservation_id)",
        allowed_group_bys=["stay_date", "channel_code", "market_code", "space_type"],
        allowed_filters=["date_range", "channel_code", "market_code", "space_type", "future_only"],
        synonyms=["reservations", "bookings", "reservation count", "booking count"],
        unit="count",
        default_aggregation="distinct_count",
    ),
    "occupancy": MetricDefinition(
        name="occupancy",
        description="Occupancy percentage. Uses total hotel capacity.",
        date_field="stay_date",
        exclude_cancelled_by_default=True,
        unit="percent",
        default_aggregation="derived",
        business_rule="Calculated against capacity in room_type_lookup."
    ),
    "lead_time": MetricDefinition(
        name="lead_time",
        description="Average days between booking creation and arrival.",
        date_field="create_datetime",
        exclude_cancelled_by_default=False,
        unit="days",
        default_aggregation="avg",
        business_rule="Useful for detecting shifts in how far out guests book."
    ),
    "cancelled_reservations": MetricDefinition(
        name="cancelled_reservations",
        description="Distinct count of cancelled reservations.",
        date_field="stay_date",
        exclude_cancelled_by_default=False,
        reservation_count_method="COUNT(DISTINCT reservation_id)",
        allowed_group_bys=["stay_date", "channel_code", "market_code", "space_type"],
        allowed_filters=["date_range", "channel_code", "market_code", "space_type", "future_only"],
        synonyms=["cancelled reservations", "cancellations", "cancelled bookings"],
        unit="count",
        default_aggregation="distinct_count",
    ),
    "pickup_room_nights": MetricDefinition(
        name="pickup_room_nights",
        description="Rooms booked within a window. README Rule: Uses creation date.",
        date_field="create_datetime",
        exclude_cancelled_by_default=True,
        room_night_method="SUM(number_of_spaces)",
        allowed_group_bys=["create_datetime", "channel_code", "market_code", "space_type", "stay_date"],
        allowed_filters=["date_range", "channel_code", "market_code", "space_type", "future_only"],
        synonyms=["pickup", "pickup room nights", "booking pace", "pace"],
        unit="count",
    ),
    "group_share": MetricDefinition(
        name="group_share",
        description="Revenue percentage from group blocks (is_block=True).",
        date_field="stay_date",
        unit="percent",
        default_aggregation="derived",
        business_rule="Monitors concentration risk in group business."
    ),
}

SEGMENT_MAPPING = {
    "leisure": "Leisure",
    "vacation": "Leisure",
    "holiday": "Leisure",
    "corporate": "Corporate",
    "business": "Corporate",
    "group": "Group",
    "conference": "Group",
    "event": "Group",
    "wholesale": "Wholesale",
    "tour operator": "Wholesale",
}

DIMENSION_ALIASES = {
    "segment": "market_code",
    "market segment": "market_code",
    "channel": "channel_code",
    "room type": "space_type",
    "date": "stay_date",
    "stay date": "stay_date",
    "booking date": "create_datetime",
    "arrival date": "arrival_date",
    "departure date": "departure_date",
    "company": "company_name",
}

# --- HELPER FUNCTIONS ---
def get_metric_definition(metric_name: str) -> MetricDefinition:
    if metric_name not in METRIC_CATALOG:
        raise ValueError(f"Unsupported metric: {metric_name}")
    return METRIC_CATALOG[metric_name]

def get_catalog_markdown() -> str:
    header = "| Metric Name | Description | Date Field | Business Rule |\n| :--- | :--- | :--- | :--- |\n"
    rows = []
    for key, m in METRIC_CATALOG.items():
        rule = m.business_rule if m.business_rule else "Standard aggregation"
        rows.append(f"| {key} | {m.description} | {m.date_field} | {rule} |")
    return header + "\n".join(rows)
