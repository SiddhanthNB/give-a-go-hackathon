from dataclasses import dataclass, field
from typing import Dict, List, Optional, Literal


IntentType = Literal[
    "metric_value",
    "breakdown",
    "trend",
    "comparison",
    "briefing",
]

DateField = Literal["stay_date", "create_datetime"]


@dataclass
class MetricDefinition:
    name: str
    description: str
    date_field: DateField
    revenue_field: Optional[str] = None
    exclude_cancelled_by_default: bool = True
    reservation_count_method: Optional[str] = None
    room_night_method: Optional[str] = None
    allowed_group_bys: List[str] = field(default_factory=list)
    allowed_filters: List[str] = field(default_factory=list)
    synonyms: List[str] = field(default_factory=list)
    unit: str = "number"
    default_aggregation: str = "sum"


METRIC_CATALOG: Dict[str, MetricDefinition] = {
    "revenue": MetricDefinition(
        name="revenue",
        description="Total hotel revenue using daily_total_revenue_before_tax",
        date_field="stay_date",
        revenue_field="daily_total_revenue_before_tax",
        exclude_cancelled_by_default=True,
        allowed_group_bys=["stay_date", "channel_code", "market_code", "space_type"],
        allowed_filters=["date_range", "channel_code", "market_code", "space_type", "future_only"],
        synonyms=["revenue", "sales", "total revenue", "otb revenue", "booked revenue"],
        unit="currency",
        default_aggregation="sum",
    ),
    "room_nights": MetricDefinition(
        name="room_nights",
        description="Total room nights using SUM(number_of_spaces)",
        date_field="stay_date",
        exclude_cancelled_by_default=True,
        room_night_method="sum(number_of_spaces)",
        allowed_group_bys=["stay_date", "channel_code", "market_code", "space_type"],
        allowed_filters=["date_range", "channel_code", "market_code", "space_type", "future_only"],
        synonyms=["room nights", "rooms sold", "nights sold"],
        unit="count",
        default_aggregation="sum",
    ),
    "adr": MetricDefinition(
        name="adr",
        description="Average Daily Rate = room revenue / room nights",
        date_field="stay_date",
        revenue_field="daily_room_revenue_before_tax",
        exclude_cancelled_by_default=True,
        room_night_method="sum(number_of_spaces)",
        allowed_group_bys=["stay_date", "channel_code", "market_code", "space_type"],
        allowed_filters=["date_range", "channel_code", "market_code", "space_type", "future_only"],
        synonyms=["adr", "average daily rate", "average rate"],
        unit="currency",
        default_aggregation="derived",
    ),
    "reservations": MetricDefinition(
        name="reservations",
        description="Distinct reservation count using COUNT(DISTINCT reservation_id)",
        date_field="stay_date",
        exclude_cancelled_by_default=True,
        reservation_count_method="count(distinct reservation_id)",
        allowed_group_bys=["stay_date", "channel_code", "market_code", "space_type"],
        allowed_filters=["date_range", "channel_code", "market_code", "space_type", "future_only"],
        synonyms=["reservations", "bookings", "reservation count", "booking count"],
        unit="count",
        default_aggregation="distinct_count",
    ),
    "cancelled_reservations": MetricDefinition(
        name="cancelled_reservations",
        description="Distinct cancelled reservation count",
        date_field="stay_date",
        exclude_cancelled_by_default=False,
        reservation_count_method="count(distinct reservation_id)",
        allowed_group_bys=["stay_date", "channel_code", "market_code", "space_type"],
        allowed_filters=["date_range", "channel_code", "market_code", "space_type", "future_only"],
        synonyms=["cancelled reservations", "cancellations", "cancelled bookings"],
        unit="count",
        default_aggregation="distinct_count",
    ),
    "cancelled_revenue": MetricDefinition(
        name="cancelled_revenue",
        description="Revenue associated with cancelled reservations",
        date_field="stay_date",
        revenue_field="daily_total_revenue_before_tax",
        exclude_cancelled_by_default=False,
        allowed_group_bys=["stay_date", "channel_code", "market_code", "space_type"],
        allowed_filters=["date_range", "channel_code", "market_code", "space_type", "future_only"],
        synonyms=["cancelled revenue", "cancellation revenue", "lost revenue"],
        unit="currency",
        default_aggregation="sum",
    ),
    "pickup_room_nights": MetricDefinition(
        name="pickup_room_nights",
        description="Pickup in room nights based on booking creation time",
        date_field="create_datetime",
        exclude_cancelled_by_default=True,
        room_night_method="sum(number_of_spaces)",
        allowed_group_bys=["create_datetime", "channel_code", "market_code", "space_type", "stay_date"],
        allowed_filters=["date_range", "channel_code", "market_code", "space_type", "future_only"],
        synonyms=["pickup", "pickup room nights", "booking pace", "pace"],
        unit="count",
        default_aggregation="sum",
    ),
    "pickup_revenue": MetricDefinition(
        name="pickup_revenue",
        description="Pickup in revenue based on booking creation time",
        date_field="create_datetime",
        revenue_field="daily_total_revenue_before_tax",
        exclude_cancelled_by_default=True,
        allowed_group_bys=["create_datetime", "channel_code", "market_code", "space_type", "stay_date"],
        allowed_filters=["date_range", "channel_code", "market_code", "space_type", "future_only"],
        synonyms=["pickup revenue", "revenue pickup"],
        unit="currency",
        default_aggregation="sum",
    ),
    "ota_share": MetricDefinition(
        name="ota_share",
        description="Share of revenue from OTA business",
        date_field="stay_date",
        revenue_field="daily_total_revenue_before_tax",
        exclude_cancelled_by_default=True,
        allowed_group_bys=["stay_date", "market_code", "space_type"],
        allowed_filters=["date_range", "market_code", "space_type", "future_only"],
        synonyms=["ota share", "ota dependency", "ota mix"],
        unit="percent",
        default_aggregation="derived",
    ),
    "segment_mix": MetricDefinition(
        name="segment_mix",
        description="Revenue or room-night mix by market segment",
        date_field="stay_date",
        exclude_cancelled_by_default=True,
        allowed_group_bys=["market_code", "stay_date"],
        allowed_filters=["date_range", "channel_code", "space_type", "future_only"],
        synonyms=["segment mix", "segment share", "market mix"],
        unit="percent",
        default_aggregation="derived",
    ),
    "channel_mix": MetricDefinition(
        name="channel_mix",
        description="Revenue or room-night mix by booking channel",
        date_field="stay_date",
        exclude_cancelled_by_default=True,
        allowed_group_bys=["channel_code", "stay_date"],
        allowed_filters=["date_range", "market_code", "space_type", "future_only"],
        synonyms=["channel mix", "channel share", "distribution mix"],
        unit="percent",
        default_aggregation="derived",
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


DEFAULT_METRICS_BY_INTENT = {
    "metric_value": ["revenue"],
    "breakdown": ["revenue"],
    "trend": ["revenue"],
    "comparison": ["revenue"],
    "briefing": ["revenue", "cancelled_revenue", "pickup_room_nights", "ota_share"],
}


def normalize_metric(user_text: str) -> Optional[str]:
    text = user_text.lower().strip()

    for metric_key, metric_def in METRIC_CATALOG.items():
        if metric_key == text:
            return metric_key
        for synonym in metric_def.synonyms:
            if synonym in text:
                return metric_key
    return None


def normalize_dimension(user_text: str) -> Optional[str]:
    text = user_text.lower().strip()
    for alias, canonical in DIMENSION_ALIASES.items():
        if alias in text:
            return canonical
    return None


def normalize_segment(user_text: str) -> Optional[str]:
    text = user_text.lower().strip()
    for alias, canonical in SEGMENT_MAPPING.items():
        if alias in text:
            return canonical
    return None


def is_metric_supported(metric_name: str) -> bool:
    return metric_name in METRIC_CATALOG


def get_metric_definition(metric_name: str) -> MetricDefinition:
    if metric_name not in METRIC_CATALOG:
        raise ValueError(f"Unsupported metric: {metric_name}")
    return METRIC_CATALOG[metric_name]

def get_catalog_markdown() -> str:
    header = "| Metric Name | Description | Synonyms | Date Field |\n| :--- | :--- | :--- | :--- |\n"
    rows = []
    for key, m in METRIC_CATALOG.items():
        synonyms = ", ".join(m.synonyms)
        rows.append(f"| {key} | {m.description} | {synonyms} | {m.date_field} |")
    return header + "\n".join(rows)

def get_mapping_markdown() -> str:
    # Quick helpers for segments and dimensions
    segments = ", ".join([f"{k} -> {v}" for k, v in SEGMENT_MAPPING.items()])
    dimensions = ", ".join([f"{k} -> {v}" for k, v in DIMENSION_ALIASES.items()])
    return f"Segments: {segments}\nDimensions: {dimensions}"
