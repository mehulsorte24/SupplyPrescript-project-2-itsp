import random
from datetime import datetime

SUPPLIERS = [f"SUP{str(i).zfill(3)}" for i in range(1, 21)]

CITIES = [
    "Mumbai",
    "Delhi",
    "Pune",
    "Bangalore",
    "Hyderabad",
    "Chennai",
    "Nagpur",
    "Ahmedabad",
    "Kolkata",
    "Jaipur"
]

TRANSPORT_MODES = [
    "Road",
    "Rail",
    "Air",
    "Sea"
]

WEATHER_LEVELS = [
    "Low",
    "Medium",
    "High",
    "Severe"
]

TRAFFIC_LEVELS = [
    "Low",
    "Medium",
    "High"
]

PRIORITY_LEVELS = [
    "Low",
    "Medium",
    "High",
    "Critical"
]


def generate_shipment(shipment_number):
    """
    Generate one synthetic supply-chain shipment record.
    """

    origin = random.choice(CITIES)
    destination = random.choice(
        [city for city in CITIES if city != origin]
    )

    transport_mode = random.choice(TRANSPORT_MODES)
    weather = random.choice(WEATHER_LEVELS)
    traffic = random.choice(TRAFFIC_LEVELS)
    priority = random.choice(PRIORITY_LEVELS)

    distance_km = random.randint(100, 3000)
    lead_time_days = random.randint(2, 20)

    supplier_reliability = round(
        random.uniform(0.65, 0.99), 2
    )

    inventory_level = random.randint(10, 100)

    order_value = round(
        random.uniform(5000, 250000), 2
    )

    fuel_price_index = round(
        random.uniform(90, 150), 2
    )

    warehouse_load = round(
        random.uniform(0.30, 0.98), 2
    )

    shipment = {
        "shipment_id": f"SHP{str(shipment_number).zfill(7)}",
        "supplier_id": random.choice(SUPPLIERS),
        "origin": origin,
        "destination": destination,
        "transport_mode": transport_mode,
        "distance_km": distance_km,
        "lead_time_days": lead_time_days,
        "weather_severity": weather,
        "traffic_level": traffic,
        "inventory_level": inventory_level,
        "supplier_reliability": supplier_reliability,
        "order_value": order_value,
        "priority": priority,
        "fuel_price_index": fuel_price_index,
        "warehouse_load": warehouse_load,
        "generated_at": datetime.now().isoformat()
    }

    return shipment


if __name__ == "__main__":
    for i in range(1, 6):
        shipment = generate_shipment(i)
        print(shipment)