import random
from datetime import datetime


# ============================================================
# SUPPLY PRESCRIPT - LIVE SHIPMENT DATA GENERATOR
# ============================================================

# -----------------------------
# Master data
# -----------------------------

SUPPLIERS = [
    f"SUP{str(i).zfill(3)}"
    for i in range(1, 21)
]

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


# ============================================================
# Delay calculation
# ============================================================

def calculate_delay(
    weather,
    traffic,
    supplier_reliability,
    inventory_level,
    warehouse_load,
    priority,
    distance_km,
    transport_mode
):
    """
    Calculate synthetic shipment delay based on
    multiple operational risk factors.
    """

    risk_score = 0.0

    # -----------------------------
    # Weather risk
    # -----------------------------

    weather_risk = {
        "Low": 0.0,
        "Medium": 0.5,
        "High": 1.5,
        "Severe": 3.0
    }

    risk_score += weather_risk[weather]

    # -----------------------------
    # Traffic risk
    # -----------------------------

    traffic_risk = {
        "Low": 0.0,
        "Medium": 0.5,
        "High": 1.5
    }

    risk_score += traffic_risk[traffic]

    # -----------------------------
    # Supplier reliability
    # Lower reliability = higher risk
    # -----------------------------

    risk_score += (1 - supplier_reliability) * 5

    # -----------------------------
    # Inventory risk
    # -----------------------------

    if inventory_level < 30:
        risk_score += 2.0

    elif inventory_level < 50:
        risk_score += 1.0

    # -----------------------------
    # Warehouse congestion
    # -----------------------------

    if warehouse_load > 0.85:
        risk_score += 2.0

    elif warehouse_load > 0.70:
        risk_score += 1.0

    # -----------------------------
    # Priority risk
    # -----------------------------

    priority_risk = {
        "Low": 0.0,
        "Medium": 0.3,
        "High": 0.8,
        "Critical": 1.2
    }

    risk_score += priority_risk[priority]

    # -----------------------------
    # Distance risk
    # -----------------------------

    if distance_km > 2000:
        risk_score += 1.5

    elif distance_km > 1000:
        risk_score += 0.7

    # -----------------------------
    # Transport mode risk
    # -----------------------------

    transport_risk = {
        "Road": 0.5,
        "Rail": 0.4,
        "Air": 0.1,
        "Sea": 0.8
    }

    risk_score += transport_risk[transport_mode]

    # -----------------------------
    # Random operational variation
    # -----------------------------

    risk_score += random.uniform(-1.0, 1.0)

    # -----------------------------
    # Convert risk score to delay
    # -----------------------------

    if risk_score < 3:
        delay_days = 0

    elif risk_score < 5:
        delay_days = random.randint(1, 2)

    elif risk_score < 7:
        delay_days = random.randint(2, 4)

    elif risk_score < 9:
        delay_days = random.randint(4, 7)

    else:
        delay_days = random.randint(7, 14)

    # -----------------------------
    # Delay status
    # -----------------------------

    if delay_days > 0:
        delay_status = "DELAYED"
    else:
        delay_status = "ON_TIME"

    return delay_days, delay_status


# ============================================================
# Shipment generator
# ============================================================

def generate_shipment(shipment_number):
    """
    Generate one synthetic supply-chain shipment.
    """

    # -----------------------------
    # Route
    # -----------------------------

    origin = random.choice(CITIES)

    destination = random.choice(
        [
            city
            for city in CITIES
            if city != origin
        ]
    )

    # -----------------------------
    # Operational conditions
    # -----------------------------

    transport_mode = random.choice(
        TRANSPORT_MODES
    )

    weather = random.choice(
        WEATHER_LEVELS
    )

    traffic = random.choice(
        TRAFFIC_LEVELS
    )

    priority = random.choice(
        PRIORITY_LEVELS
    )

    # -----------------------------
    # Numerical variables
    # -----------------------------

    distance_km = random.randint(
        100,
        3000
    )

    lead_time_days = random.randint(
        2,
        20
    )

    supplier_reliability = round(
        random.uniform(0.65, 0.99),
        2
    )

    inventory_level = random.randint(
        10,
        100
    )

    order_value = round(
        random.uniform(5000, 250000),
        2
    )

    fuel_price_index = round(
        random.uniform(90, 150),
        2
    )

    warehouse_load = round(
        random.uniform(0.30, 0.98),
        2
    )

    # -----------------------------
    # Actual shipment outcome
    # -----------------------------

    actual_delay_days, delay_status = calculate_delay(
        weather=weather,
        traffic=traffic,
        supplier_reliability=supplier_reliability,
        inventory_level=inventory_level,
        warehouse_load=warehouse_load,
        priority=priority,
        distance_km=distance_km,
        transport_mode=transport_mode
    )

    # -----------------------------
    # Final shipment record
    # -----------------------------

    shipment = {
        "shipment_id": f"SHP{str(shipment_number).zfill(7)}",

        "supplier_id": random.choice(
            SUPPLIERS
        ),

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

        "actual_delay_days": actual_delay_days,

        "delay_status": delay_status,

        "generated_at": datetime.now().isoformat()
    }

    return shipment


# ============================================================
# Test generator
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("SUPPLY PRESCRIPT - SHIPMENT DATA GENERATOR")
    print("=" * 70)

    print("\nGenerating 5 sample shipments...\n")

    for i in range(1, 6):

        shipment = generate_shipment(i)

        print(f"Shipment {i}")
        print("-" * 70)

        for key, value in shipment.items():
            print(f"{key}: {value}")

        print()