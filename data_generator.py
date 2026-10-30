"""
Smart Drinking Water Quality Monitoring System — Simulated Sensor Data Generator
Generates realistic simulated sensor telemetry for residential water storage monitoring.
"""

from datetime import datetime, timedelta
import random
import numpy as np
import pandas as pd

# Demonstration residential water storage tanks
TANKS = [
    {
        "id": "TANK-01",
        "name": "Tank A — Residential Block A",
        "short_name": "Tank A",
        "location": "Rooftop Storage Unit, Block A",
        "capacity": "10,000 Liters",
        "description": "Domestic potable water supply for Block A apartments.",
    },
    {
        "id": "TANK-02",
        "name": "Tank B — Residential Block B",
        "short_name": "Tank B",
        "location": "Rooftop Storage Unit, Block B",
        "capacity": "10,000 Liters",
        "description": "Domestic potable water supply for Block B apartments.",
    },
    {
        "id": "TANK-03",
        "name": "Tank C — Community Water Storage",
        "short_name": "Tank C",
        "location": "Central Ground Storage Reservoir",
        "capacity": "35,000 Liters",
        "description": "Central buffer reservoir receiving municipal and treated water supply.",
    },
]

# Baseline parameter metadata and acceptable standards
PARAMETER_METADATA = {
    "ph": {
        "name": "pH Level",
        "unit": "",
        "short_unit": "",
        "bis_standard": "6.5 – 8.5",
        "description": "Measures hydrogen-ion concentration. Values outside 6.5-8.5 indicate acidic corrosive water or alkaline scale-forming tendencies.",
    },
    "tds": {
        "name": "Total Dissolved Solids (TDS)",
        "unit": "mg/L",
        "short_unit": "mg/L",
        "bis_standard": "<= 500 mg/L",
        "description": "Total concentration of dissolved inorganic salts and minerals. Elevated TDS affects taste and hardness.",
    },
    "turbidity": {
        "name": "Turbidity",
        "unit": "NTU",
        "short_unit": "NTU",
        "bis_standard": "<= 1.0 NTU",
        "description": "Measure of water clarity. Values above 1.0 NTU indicate suspended particles requiring filtration check.",
    },
    "temperature": {
        "name": "Water Temperature",
        "unit": "°C",
        "short_unit": "°C",
        "bis_standard": "15.0 – 32.0 °C",
        "description": "Monitors ambient water storage temperatures.",
    },
}

# Configurable demonstration thresholds
DEFAULT_THRESHOLDS = {
    "ph_min": 6.5,
    "ph_max": 8.5,
    "tds_max": 500.0,         # mg/L
    "turbidity_max": 1.0,     # NTU
    "temp_min": 15.0,         # °C
    "temp_max": 32.0,         # °C
}

# Baseline values for realistic simulation
TANK_BASELINES = {
    "TANK-01": {"ph": 7.35, "tds": 260.0, "turbidity": 0.45, "temp": 24.2},
    "TANK-02": {"ph": 7.42, "tds": 285.0, "turbidity": 0.52, "temp": 24.8},
    "TANK-03": {"ph": 7.28, "tds": 310.0, "turbidity": 0.68, "temp": 23.5},
}


def generate_single_reading(tank_id: str, timestamp: datetime = None, force_anomaly: bool = False, anomaly_param: str = None) -> dict:
    """
    Generate a single simulated sensor reading record.
    If force_anomaly is True, forces one parameter to exceed configured limits
    for alert verification.
    """
    if timestamp is None:
        timestamp = datetime.now()

    base = TANK_BASELINES.get(tank_id, {"ph": 7.3, "tds": 280.0, "turbidity": 0.5, "temp": 24.0})

    # Add gentle realistic Gaussian noise
    ph = round(base["ph"] + random.gauss(0, 0.10), 2)
    tds = round(base["tds"] + random.gauss(0, 12.0), 1)
    turbidity = round(max(0.12, base["turbidity"] + random.gauss(0, 0.12)), 2)
    temperature = round(base["temp"] + random.gauss(0, 0.7), 1)

    is_anomaly = force_anomaly
    if not force_anomaly and random.random() < 0.08:
        is_anomaly = True
        chosen_param = random.choice(["ph", "tds", "turbidity", "temperature"])
    else:
        chosen_param = anomaly_param

    if is_anomaly:
        if chosen_param == "ph" or (anomaly_param == "ph"):
            ph = round(random.choice([random.uniform(5.9, 6.3), random.uniform(8.7, 9.2)]), 2)
        elif chosen_param == "tds" or (anomaly_param == "tds"):
            tds = round(random.uniform(540.0, 680.0), 1)
        elif chosen_param == "turbidity" or (anomaly_param == "turbidity"):
            turbidity = round(random.uniform(2.2, 4.6), 2)
        elif chosen_param == "temperature" or (anomaly_param == "temperature"):
            temperature = round(random.choice([random.uniform(12.0, 14.2), random.uniform(33.5, 36.5)]), 1)

    tank_obj = next((t for t in TANKS if t["id"] == tank_id), TANKS[0])

    return {
        "timestamp": timestamp,
        "tank_id": tank_id,
        "tank_name": tank_obj["name"],
        "ph": float(ph),
        "tds": float(tds),
        "turbidity": float(turbidity),
        "temperature": float(temperature),
        "is_simulated": True,
        "source": "Simulated Sensor Engine",
    }


def generate_initial_history(records_per_tank: int = 35) -> pd.DataFrame:
    """
    Generates realistic historical time-series records spanning the past 24 hours.
    """
    records = []
    now = datetime.now()
    step_minutes = int((24 * 60) / max(records_per_tank, 1))

    for tank in TANKS:
        t_id = tank["id"]
        base = TANK_BASELINES[t_id]

        curr_ph = base["ph"]
        curr_tds = base["tds"]
        curr_turb = base["turbidity"]
        curr_temp = base["temp"]

        # Ensure demonstration anomalies are included
        spike_index_turb = max(1, int(records_per_tank * 0.45)) if t_id == "TANK-03" else -1
        spike_index_ph = max(1, int(records_per_tank * 0.70)) if t_id == "TANK-02" else -1

        for i in range(records_per_tank):
            t_stamp = now - timedelta(minutes=(records_per_tank - 1 - i) * step_minutes)
            
            # Diurnal temperature cycle
            hour_fraction = t_stamp.hour + t_stamp.minute / 60.0
            diurnal_temp = 1.6 * np.sin((hour_fraction - 8.0) * np.pi / 12.0)

            # Random walk drift
            curr_ph = np.clip(curr_ph + random.gauss(0, 0.04), 6.6, 8.4)
            curr_tds = np.clip(curr_tds + random.gauss(0, 3.5), 230.0, 450.0)
            curr_turb = np.clip(curr_turb + random.gauss(0, 0.03), 0.25, 0.90)
            curr_temp = np.clip(curr_temp + random.gauss(0, 0.12), 21.0, 27.0)

            ph_val = float(round(curr_ph, 2))
            tds_val = float(round(curr_tds, 1))
            turb_val = float(round(curr_turb, 2))
            temp_val = float(round(curr_temp + diurnal_temp, 1))

            if i == spike_index_turb:
                turb_val = 3.45
            elif i == spike_index_ph:
                ph_val = 8.85

            records.append({
                "timestamp": t_stamp,
                "tank_id": t_id,
                "tank_name": tank["name"],
                "ph": ph_val,
                "tds": tds_val,
                "turbidity": turb_val,
                "temperature": temp_val,
                "is_simulated": True,
                "source": "Simulated Sensor Engine",
            })

    df = pd.DataFrame(records)
    df = df.sort_values(by="timestamp", ascending=True).reset_index(drop=True)
    return df
