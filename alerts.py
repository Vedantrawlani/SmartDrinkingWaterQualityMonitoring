"""
Smart Drinking Water Quality Monitoring System — Alerts & Notifications Engine
Simulates threshold-based alert generation, acknowledgement, and resolution workflows.
Persists alert states within Streamlit session state.
"""

from datetime import datetime
from typing import List, Dict, Any, Tuple
import pandas as pd

SUGGESTED_ACTIONS = {
    "ph": "Inspect the water source and arrange confirmatory testing.",
    "tds": "Investigate the source of elevated dissolved solids and verify with appropriate testing.",
    "turbidity": "Inspect the tank and water supply; arrange further water-quality testing.",
    "temperature": "Review storage conditions and investigate if necessary.",
}

PARAM_DISPLAY_NAMES = {
    "ph": "pH",
    "tds": "Total Dissolved Solids (TDS)",
    "turbidity": "Turbidity",
    "temperature": "Temperature",
}

PARAM_UNITS = {
    "ph": "",
    "tds": "mg/L",
    "turbidity": "NTU",
    "temperature": "°C",
}


def evaluate_parameter_breach(param: str, value: float, thresholds: Dict[str, float]) -> Tuple[bool, str, str, str]:
    """
    Checks if a parameter breaches configured thresholds.
    Returns: (is_breached, severity, threshold_str, breach_direction)
    """
    ph_min = thresholds.get("ph_min", 6.5)
    ph_max = thresholds.get("ph_max", 8.5)
    tds_max = thresholds.get("tds_max", 500.0)
    turbidity_max = thresholds.get("turbidity_max", 1.0)
    temp_min = thresholds.get("temp_min", 15.0)
    temp_max = thresholds.get("temp_max", 32.0)

    if param == "ph":
        if value < ph_min:
            severity = "Critical" if value < ph_min - 0.3 else "Warning"
            return True, severity, f"Min {ph_min}", f"Below acceptable lower limit ({value:.2f} < {ph_min})"
        elif value > ph_max:
            severity = "Critical" if value > ph_max + 0.3 else "Warning"
            return True, severity, f"Max {ph_max}", f"Above acceptable upper limit ({value:.2f} > {ph_max})"

    elif param == "tds":
        if value > tds_max:
            severity = "Critical" if value > tds_max * 1.25 else "Warning"
            return True, severity, f"Max {tds_max:.0f} mg/L", f"Exceeds acceptable limit ({value:.1f} > {tds_max:.0f} mg/L)"

    elif param == "turbidity":
        if value > turbidity_max:
            severity = "Critical" if value > turbidity_max * 2.5 else "Warning"
            return True, severity, f"Max {turbidity_max:.1f} NTU", f"Exceeds clarity standard ({value:.2f} > {turbidity_max:.1f} NTU)"

    elif param == "temperature":
        if value < temp_min:
            severity = "Critical" if value < temp_min - 2.5 else "Warning"
            return True, severity, f"Min {temp_min:.1f} °C", f"Below monitoring baseline ({value:.1f} < {temp_min:.1f} °C)"
        elif value > temp_max:
            severity = "Critical" if value > temp_max + 2.5 else "Warning"
            return True, severity, f"Max {temp_max:.1f} °C", f"Above monitoring baseline ({value:.1f} > {temp_max:.1f} °C)"

    return False, "Normal", "", ""


def process_reading_for_alerts(
    reading: Dict[str, Any],
    thresholds: Dict[str, float],
    existing_alerts: List[Dict[str, Any]],
    next_alert_id: int
) -> Tuple[List[Dict[str, Any]], int]:
    """
    Inspects a single reading record. If any parameter violates configured thresholds,
    creates a simulated alert in 'Open' status.
    Returns: (updated_alerts_list, updated_next_alert_id)
    """
    updated_alerts = list(existing_alerts)
    new_id = next_alert_id

    for param in ["ph", "tds", "turbidity", "temperature"]:
        val = reading.get(param)
        if val is None:
            continue

        is_breached, severity, thresh_desc, breach_detail = evaluate_parameter_breach(param, float(val), thresholds)
        if is_breached:
            # Check if there's already an active open alert for this tank and parameter within the same reading timestamp
            duplicate = any(
                a["tank_id"] == reading["tank_id"] and
                a["parameter_key"] == param and
                a["timestamp"] == reading["timestamp"]
                for a in updated_alerts
            )
            if not duplicate:
                unit = PARAM_UNITS[param]
                unit_str = f" {unit}".rstrip()
                alert_obj = {
                    "alert_id": f"ALT-2026-{new_id:04d}",
                    "timestamp": reading["timestamp"],
                    "tank_id": reading["tank_id"],
                    "tank_name": reading["tank_name"],
                    "parameter_key": param,
                    "parameter": PARAM_DISPLAY_NAMES[param],
                    "observed_value": f"{val:.2f}{unit_str}" if param in ["ph", "turbidity"] else f"{val:.1f}{unit_str}",
                    "numeric_value": float(val),
                    "configured_threshold": thresh_desc,
                    "breach_detail": breach_detail,
                    "severity": severity,
                    "suggested_action": SUGGESTED_ACTIONS[param],
                    "status": "Open",  # Open, Acknowledged, Resolved
                    "acknowledged_at": None,
                    "resolved_at": None,
                    "notes": "Simulated alert automatically generated on threshold breach.",
                }
                updated_alerts.insert(0, alert_obj)
                new_id += 1

    return updated_alerts, new_id


def generate_initial_alerts(df_history: pd.DataFrame, thresholds: Dict[str, float]) -> Tuple[List[Dict[str, Any]], int]:
    """
    Scans the generated history dataframe to build realistic initial alerts.
    Marks older alerts as acknowledged or resolved to present a rich, authentic demo state.
    """
    alerts = []
    alert_id = 1

    # Sort ascending to simulate real arrival
    df_sorted = df_history.sort_values(by="timestamp", ascending=True)

    for _, row in df_sorted.iterrows():
        reading_dict = row.to_dict()
        alerts, alert_id = process_reading_for_alerts(reading_dict, thresholds, alerts, alert_id)

    # For realistic demonstration, mark 1-2 older alerts as Acknowledged / Resolved
    # while leaving recent ones Open
    for idx, alert in enumerate(reversed(alerts)):
        if idx == 0 and len(alerts) > 2:
            alert["status"] = "Resolved"
            alert["resolved_at"] = datetime.now()
            alert["notes"] = "Resolved after confirmatory water sample testing verified compliance."
        elif idx == 1 and len(alerts) > 1:
            alert["status"] = "Acknowledged"
            alert["acknowledged_at"] = datetime.now()
            alert["notes"] = "Acknowledged by residential facility supervisor; site inspection scheduled."

    return alerts, alert_id


def update_alert_status(alerts: List[Dict[str, Any]], alert_id: str, new_status: str, notes: str = None) -> List[Dict[str, Any]]:
    """
    Updates the status of an alert (Open -> Acknowledged -> Resolved).
    Preserves state in session.
    """
    updated = []
    for a in alerts:
        a_copy = dict(a)
        if a_copy["alert_id"] == alert_id:
            a_copy["status"] = new_status
            if new_status == "Acknowledged":
                a_copy["acknowledged_at"] = datetime.now()
            elif new_status == "Resolved":
                a_copy["resolved_at"] = datetime.now()
            if notes:
                a_copy["notes"] = notes
        updated.append(a_copy)
    return updated
