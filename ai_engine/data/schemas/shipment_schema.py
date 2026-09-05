from dataclasses import dataclass
from typing import Optional


@dataclass
class ShipmentSchema:
    shipment_id: str
    supplier_id: str
    origin: str
    destination: str
    transport_mode: str
    distance_km: int
    lead_time_days: int
    weather_severity: str
    traffic_level: str
    inventory_level: int
    supplier_reliability: float
    order_value: float
    priority: str
    fuel_price_index: float
    warehouse_load: float
    actual_delay_days: Optional[int] = None
    delay_status: Optional[str] = None
    generated_at: Optional[str] = None