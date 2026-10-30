"""
Smart Drinking Water Quality Monitoring System — Monitoring & Threshold Evaluation Engine
Evaluates sensor readings dynamically against user-configured thresholds.
Produces categorical statuses: 'Normal', 'Warning', and 'Requires Inspection'.
"""

from typing import Dict, Any, Tuple


def evaluate_parameter(param_name: str, value: float, thresholds: Dict[str, float]) -> Dict[str, Any]:
    """
    Evaluates a single parameter value against active demonstration thresholds.
    Returns status ('Normal', 'Warning', 'Requires Inspection'), severity level,
    color, badge styling, and explanatory remarks.
    """
    if value is None:
        return {
            "status": "Unknown",
            "severity": "info",
            "color": "#64748b",
            "bg_color": "#f1f5f9",
            "message": "No reading available",
            "is_breach": False,
        }

    val = float(value)
    ph_min = thresholds.get("ph_min", 6.5)
    ph_max = thresholds.get("ph_max", 8.5)
    tds_max = thresholds.get("tds_max", 500.0)
    turbidity_max = thresholds.get("turbidity_max", 1.0)
    temp_min = thresholds.get("temp_min", 15.0)
    temp_max = thresholds.get("temp_max", 32.0)

    if param_name == "ph":
        if ph_min <= val <= ph_max:
            return {
                "status": "Normal",
                "severity": "normal",
                "color": "#059669",      # Green
                "bg_color": "#ecfdf5",
                "message": f"Optimal pH within configured demo range ({ph_min} – {ph_max})",
                "is_breach": False,
            }
        elif (ph_min - 0.3 <= val < ph_min) or (ph_max < val <= ph_max + 0.3):
            return {
                "status": "Warning",
                "severity": "warning",
                "color": "#d97706",      # Amber
                "bg_color": "#fffbeb",
                "message": f"pH slightly deviating from target demo range ({ph_min} – {ph_max})",
                "is_breach": True,
            }
        else:
            return {
                "status": "Requires Inspection",
                "severity": "critical",
                "color": "#dc2626",      # Red
                "bg_color": "#fef2f2",
                "message": f"pH reading ({val:.2f}) significantly outside acceptable range ({ph_min} – {ph_max})",
                "is_breach": True,
            }

    elif param_name == "tds":
        warning_thresh = tds_max * 0.75
        if val <= warning_thresh:
            return {
                "status": "Normal",
                "severity": "normal",
                "color": "#059669",
                "bg_color": "#ecfdf5",
                "message": f"TDS within optimal baseline range (<= {tds_max:.0f} mg/L)",
                "is_breach": False,
            }
        elif warning_thresh < val <= tds_max:
            return {
                "status": "Warning",
                "severity": "warning",
                "color": "#d97706",
                "bg_color": "#fffbeb",
                "message": f"TDS approaching maximum threshold ({val:.1f} / {tds_max:.0f} mg/L)",
                "is_breach": False,
            }
        else:
            return {
                "status": "Requires Inspection",
                "severity": "critical",
                "color": "#dc2626",
                "bg_color": "#fef2f2",
                "message": f"TDS exceeds configured demonstration threshold ({val:.1f} > {tds_max:.0f} mg/L)",
                "is_breach": True,
            }

    elif param_name == "turbidity":
        warning_thresh = turbidity_max * 2.5
        if val <= turbidity_max:
            return {
                "status": "Normal",
                "severity": "normal",
                "color": "#059669",
                "bg_color": "#ecfdf5",
                "message": f"Turbidity meets clarity limit (<= {turbidity_max:.1f} NTU)",
                "is_breach": False,
            }
        elif turbidity_max < val <= warning_thresh:
            return {
                "status": "Warning",
                "severity": "warning",
                "color": "#d97706",
                "bg_color": "#fffbeb",
                "message": f"Mild cloudiness detected ({val:.2f} NTU > {turbidity_max:.1f} NTU)",
                "is_breach": True,
            }
        else:
            return {
                "status": "Requires Inspection",
                "severity": "critical",
                "color": "#dc2626",
                "bg_color": "#fef2f2",
                "message": f"High turbidity ({val:.2f} NTU); visible suspended sediment or floc",
                "is_breach": True,
            }

    elif param_name == "temperature":
        if temp_min <= val <= temp_max:
            return {
                "status": "Normal",
                "severity": "normal",
                "color": "#059669",
                "bg_color": "#ecfdf5",
                "message": f"Water temperature within normal range ({temp_min:.1f} – {temp_max:.1f} °C)",
                "is_breach": False,
            }
        elif (temp_min - 2.5 <= val < temp_min) or (temp_max < val <= temp_max + 2.5):
            return {
                "status": "Warning",
                "severity": "warning",
                "color": "#d97706",
                "bg_color": "#fffbeb",
                "message": f"Water temperature deviating near boundary ({val:.1f} °C)",
                "is_breach": True,
            }
        else:
            return {
                "status": "Requires Inspection",
                "severity": "critical",
                "color": "#dc2626",
                "bg_color": "#fef2f2",
                "message": f"Temperature outside monitored bounds ({val:.1f} °C)",
                "is_breach": True,
            }

    return {
        "status": "Normal",
        "severity": "normal",
        "color": "#059669",
        "bg_color": "#ecfdf5",
        "message": "Reading within expected demo bounds",
        "is_breach": False,
    }


def evaluate_reading_overview(reading: Dict[str, Any], thresholds: Dict[str, float]) -> Dict[str, Any]:
    """
    Evaluates all parameters for a complete reading.
    Returns evaluation for each parameter and overall tank status.
    """
    eval_ph = evaluate_parameter("ph", reading.get("ph"), thresholds)
    eval_tds = evaluate_parameter("tds", reading.get("tds"), thresholds)
    eval_turb = evaluate_parameter("turbidity", reading.get("turbidity"), thresholds)
    eval_temp = evaluate_parameter("temperature", reading.get("temperature"), thresholds)

    all_evals = [eval_ph, eval_tds, eval_turb, eval_temp]
    
    requires_inspection_count = sum(1 for e in all_evals if e["status"] == "Requires Inspection")
    warning_count = sum(1 for e in all_evals if e["status"] == "Warning")

    if requires_inspection_count > 0:
        overall_status = "Requires Inspection"
        overall_color = "#dc2626"
        overall_bg = "#fef2f2"
        badge_class = "badge-danger"
    elif warning_count > 0:
        overall_status = "Warning"
        overall_color = "#d97706"
        overall_bg = "#fffbeb"
        badge_class = "badge-warning"
    else:
        overall_status = "Normal"
        overall_color = "#059669"
        overall_bg = "#ecfdf5"
        badge_class = "badge-success"

    # Compute a demonstration Water Quality Index (WQI) score (0-100)
    # Heuristic penalty approach
    score = 100.0
    for e in all_evals:
        if e["status"] == "Requires Inspection":
            score -= 25.0
        elif e["status"] == "Warning":
            score -= 10.0
    score = max(0.0, min(100.0, score))

    return {
        "overall_status": overall_status,
        "overall_color": overall_color,
        "overall_bg": overall_bg,
        "badge_class": badge_class,
        "wqi_score": round(score, 1),
        "parameters": {
            "ph": eval_ph,
            "tds": eval_tds,
            "turbidity": eval_turb,
            "temperature": eval_temp,
        },
        "flagged_count": requires_inspection_count + warning_count,
        "inspection_count": requires_inspection_count,
        "warning_count": warning_count,
    }
