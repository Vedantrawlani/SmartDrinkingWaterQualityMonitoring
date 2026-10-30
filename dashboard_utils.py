"""
Smart Drinking Water Quality Monitoring System — UI & Visualization Utilities
Provides custom CSS styling, metric cards, Plotly visualizers, and UI components.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Parameter styling palette
PARAM_COLORS = {
    "ph": "#0284c7",          # Ocean Sky Blue
    "tds": "#0d9488",         # Teal
    "turbidity": "#6366f1",   # Indigo
    "temperature": "#ea580c", # Warm Amber
}

def get_custom_css() -> str:
    """Returns custom CSS for a modern, responsive, water-management aesthetic."""
    return """
    <style>
    /* Google Fonts import */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #0f172a;
    }

    /* Top Demo Notice Banner */
    .demo-notice-banner {
        background: linear-gradient(90deg, #eff6ff 0%, #f0fdfa 50%, #eff6ff 100%);
        border: 1px solid #bfdbfe;
        border-left: 5px solid #0284c7;
        border-radius: 10px;
        padding: 10px 16px;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .demo-notice-text {
        color: #0369a1;
        font-size: 0.86rem;
        font-weight: 700;
        margin: 0;
    }
    .demo-notice-sub {
        color: #64748b;
        font-size: 0.78rem;
        margin: 0;
    }
    .demo-tag-pill {
        background: #0284c7;
        color: #ffffff;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 20px;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        white-space: nowrap;
    }

    /* Top App Title Card */
    .app-header-box {
        background: #ffffff;
        border-radius: 12px;
        padding: 18px 22px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
        margin-bottom: 20px;
    }
    .app-main-title {
        color: #0f2744;
        font-size: 1.65rem;
        font-weight: 800;
        margin: 0 0 4px 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .app-sub-title {
        color: #475569;
        font-size: 0.92rem;
        font-weight: 500;
        margin: 0 0 10px 0;
    }
    .status-badge-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        align-items: center;
    }
    .status-pill {
        background: #f1f5f9;
        color: #0369a1;
        font-size: 0.76rem;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 6px;
        border: 1px solid #e2e8f0;
    }
    .status-pill-highlight {
        background: #e0f2fe;
        color: #0284c7;
        font-weight: 700;
        border-color: #bae6fd;
    }

    /* Metric Cards */
    .metric-card-wrapper {
        background: #ffffff;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        padding: 16px 18px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .metric-card-wrapper:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.06);
    }
    .metric-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    .metric-param-title {
        font-size: 0.86rem;
        font-weight: 700;
        color: #334155;
        letter-spacing: 0.02em;
    }
    .metric-val-row {
        display: flex;
        align-items: baseline;
        gap: 6px;
        margin: 4px 0 8px 0;
    }
    .metric-number {
        font-size: 2.1rem;
        font-weight: 800;
        color: #0f172a;
        line-height: 1;
        font-feature-settings: "tnum";
    }
    .metric-unit {
        font-size: 0.88rem;
        font-weight: 600;
        color: #64748b;
    }
    .metric-range-meta {
        font-size: 0.78rem;
        color: #475569;
        background: #f8fafc;
        padding: 5px 9px;
        border-radius: 6px;
        border: 1px solid #f1f5f9;
        margin-bottom: 8px;
    }
    .metric-status-badge {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        font-size: 0.76rem;
        font-weight: 700;
        padding: 3px 9px;
        border-radius: 20px;
        width: fit-content;
    }

    /* System Indicator Ribbon */
    .indicator-ribbon {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 12px 18px;
        margin-bottom: 20px;
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 16px;
    }
    .indicator-item {
        display: flex;
        flex-direction: column;
        gap: 2px;
    }
    .indicator-label {
        font-size: 0.72rem;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .indicator-value {
        font-size: 0.92rem;
        font-weight: 700;
        color: #0f172a;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .indicator-pill-amber {
        color: #b45309;
        background: #fef3c7;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.78rem;
        font-weight: 700;
        border: 1px solid #fde68a;
    }
    .indicator-pill-blue {
        color: #0369a1;
        background: #e0f2fe;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.78rem;
        font-weight: 700;
        border: 1px solid #bae6fd;
    }

    /* Status Pill Badges */
    .status-pill-normal {
        background: #dcfce7;
        color: #15803d;
        border: 1px solid #bbf7d0;
    }
    .status-pill-warning {
        background: #fef3c7;
        color: #b45309;
        border: 1px solid #fde68a;
    }
    .status-pill-inspection {
        background: #fee2e2;
        color: #b91c1c;
        border: 1px solid #fecaca;
    }

    /* Alert cards in Alerts page */
    .alert-card {
        background: #ffffff;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    .alert-card-critical {
        border-left: 5px solid #dc2626;
    }
    .alert-card-warning {
        border-left: 5px solid #d97706;
    }
    .alert-card-resolved {
        border-left: 5px solid #059669;
        opacity: 0.85;
    }

    /* Water Quality Score Box */
    .wqi-box {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 4px 10px rgba(2, 132, 199, 0.2);
    }

    /* Tank Card */
    .tank-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
        height: 100%;
    }

    /* Streamlit overrides */
    div[data-testid="stSidebarNav"] {
        padding-top: 0.5rem;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    </style>
    """


def render_demo_banner_html() -> str:
    """Renders clean visible notice regarding simulated data."""
    return """
    <div class="demo-notice-banner">
        <div style="display:flex; align-items:center; gap:10px;">
            <span style="font-size:1.25rem;">💧</span>
            <div>
                <p class="demo-notice-text">DEMO MODE — Simulated Sensor Telemetry</p>
                <p class="demo-notice-sub">Displaying real-time simulated IoT sensor data for residential water storage monitoring.</p>
            </div>
        </div>
        <span class="demo-tag-pill">Simulation Mode</span>
    </div>
    """


def render_header_html() -> str:
    """Renders application title header box without any badge pills."""
    return """
    <div class="app-header-box">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
            <div>
                <h1 class="app-main-title">
                    <span>💧</span> Smart Drinking Water Quality Monitoring System
                </h1>
                <p class="app-sub-title" style="margin:0;">Real-Time IoT Telemetry & Community Water Storage Quality Surveillance</p>
            </div>
            <div style="text-align:right;">
                <span style="font-size:0.72rem; color:#64748b; font-weight:700; display:block; letter-spacing:0.04em;">SYSTEM STATUS</span>
                <span class="indicator-pill-amber" style="display:inline-block; margin-top:4px;">Demo Mode — Disconnected</span>
            </div>
        </div>
    </div>
    """


def render_system_indicators_html(
    tank_count: int,
    flagged_params_count: int,
    latest_timestamp: datetime,
    open_alerts_count: int
) -> str:
    """Renders the system health indicator ribbon."""
    time_str = latest_timestamp.strftime("%Y-%m-%d %H:%M:%S") if latest_timestamp else "N/A"
    
    flag_color = "#dc2626" if flagged_params_count > 0 else "#059669"
    alert_badge = f'<span style="color:{flag_color}; font-weight:800;">{open_alerts_count} Open</span>' if open_alerts_count > 0 else '<span style="color:#059669; font-weight:700;">0 Active</span>'

    return f"""
    <div class="indicator-ribbon">
        <div class="indicator-item">
            <span class="indicator-label">Monitored Tanks</span>
            <span class="indicator-value">🏛️ {tank_count} Tanks</span>
        </div>
        <div class="indicator-item">
            <span class="indicator-label">Active Alerts</span>
            <span class="indicator-value">🔔 {alert_badge}</span>
        </div>
        <div class="indicator-item">
            <span class="indicator-label">Flagged Parameters</span>
            <span class="indicator-value">⚠️ {flagged_params_count} Parameter(s)</span>
        </div>
        <div class="indicator-item">
            <span class="indicator-label">Telemetry Source</span>
            <span class="indicator-value"><span class="indicator-pill-blue">Simulated Feed</span></span>
        </div>
        <div class="indicator-item">
            <span class="indicator-label">Hardware Connection</span>
            <span class="indicator-value"><span class="indicator-pill-amber">Demo Mode — Disconnected</span></span>
        </div>
        <div class="indicator-item">
            <span class="indicator-label">Latest Sample</span>
            <span class="indicator-value" style="font-size:0.82rem; font-weight:600;">🕒 {time_str}</span>
        </div>
    </div>
    """


def render_parameter_card_html(
    param_key: str,
    title: str,
    value: float,
    unit: str,
    range_str: str,
    eval_dict: Dict[str, Any],
    delta: Optional[float] = None
) -> str:
    """Renders a single high-visibility parameter card with clean typography (no code formatting)."""
    status = eval_dict.get("status", "Normal")
    if status == "Normal":
        status_class = "status-pill-normal"
        icon = "✓"
    elif status == "Warning":
        status_class = "status-pill-warning"
        icon = "⚠"
    else:
        status_class = "status-pill-inspection"
        icon = "✕"

    val_str = f"{value:.2f}" if param_key in ["ph", "turbidity"] else f"{value:.1f}"

    delta_html = ""
    if delta is not None:
        delta_color = "#64748b" if abs(delta) < 0.05 else ("#059669" if delta < 0 and param_key != "ph" else "#dc2626")
        arrow = "↑" if delta > 0 else ("↓" if delta < 0 else "→")
        delta_html = f'<span style="font-size:0.75rem; color:{delta_color}; font-weight:600; margin-left:6px;">{arrow} {abs(delta):.2f}</span>'

    unit_display = unit if unit else ""

    return f"""
    <div class="metric-card-wrapper">
        <div>
            <div class="metric-card-header">
                <span class="metric-param-title">{title}</span>
                <span class="metric-status-badge {status_class}">{icon} {status}</span>
            </div>
            <div class="metric-val-row">
                <span class="metric-number">{val_str}</span>
                <span class="metric-unit">{unit_display}</span>
                {delta_html}
            </div>
            <div class="metric-range-meta">
                <strong>Acceptable Range:</strong> {range_str}
            </div>
        </div>
        <div style="font-size:0.75rem; color:#475569; margin-top:6px; line-height:1.3;">
            {eval_dict.get('message', '')}
        </div>
    </div>
    """


def build_parameter_chart(
    df: pd.DataFrame,
    param_key: str,
    param_title: str,
    unit: str,
    thresholds: Dict[str, float],
    height: int = 340
) -> go.Figure:
    """
    Builds an interactive Plotly time-series chart with reference lines,
    custom hover templates, and theme styling.
    """
    fig = go.Figure()

    if df.empty or param_key not in df.columns:
        fig.add_annotation(
            text="No telemetry records available for this selection.",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="#64748b")
        )
        fig.update_layout(height=height, margin=dict(l=20, r=20, t=30, b=20))
        return fig

    # Group by tank for distinct traces if multiple tanks are present
    tanks = df["tank_name"].unique()
    colors = ["#0284c7", "#0d9488", "#6366f1", "#f59e0b"]

    for idx, tank_name in enumerate(tanks):
        sub_df = df[df["tank_name"] == tank_name].sort_values("timestamp")
        color = colors[idx % len(colors)]
        
        unit_str = f" {unit}".strip()
        hover_tmpl = (
            f"<b>{tank_name}</b><br>"
            "Time: %{x|%Y-%m-%d %H:%M:%S}<br>"
            f"{param_title}: <b>%{{y:.2f}}{unit_str}</b><extra></extra>"
        )

        fig.add_trace(go.Scatter(
            x=sub_df["timestamp"],
            y=sub_df[param_key],
            mode="lines+markers",
            name=tank_name,
            line=dict(color=color, width=2.5),
            marker=dict(size=6, color=color),
            hovertemplate=hover_tmpl
        ))

    # Add threshold reference lines
    if param_key == "ph":
        ph_min = thresholds.get("ph_min", 6.5)
        ph_max = thresholds.get("ph_max", 8.5)
        fig.add_hline(
            y=ph_min, line_dash="dash", line_color="#dc2626", line_width=1.5,
            annotation_text=f"Min Limit ({ph_min})", annotation_position="bottom right",
            annotation_font=dict(size=10, color="#dc2626")
        )
        fig.add_hline(
            y=ph_max, line_dash="dash", line_color="#dc2626", line_width=1.5,
            annotation_text=f"Max Limit ({ph_max})", annotation_position="top right",
            annotation_font=dict(size=10, color="#dc2626")
        )
    elif param_key == "tds":
        tds_max = thresholds.get("tds_max", 500.0)
        fig.add_hline(
            y=tds_max, line_dash="dash", line_color="#dc2626", line_width=1.5,
            annotation_text=f"Max Threshold ({tds_max:.0f} mg/L)", annotation_position="top right",
            annotation_font=dict(size=10, color="#dc2626")
        )
    elif param_key == "turbidity":
        turb_max = thresholds.get("turbidity_max", 1.0)
        fig.add_hline(
            y=turb_max, line_dash="dash", line_color="#dc2626", line_width=1.5,
            annotation_text=f"Clarity Limit ({turb_max:.1f} NTU)", annotation_position="top right",
            annotation_font=dict(size=10, color="#dc2626")
        )
    elif param_key == "temperature":
        t_min = thresholds.get("temp_min", 15.0)
        t_max = thresholds.get("temp_max", 32.0)
        fig.add_hline(
            y=t_min, line_dash="dash", line_color="#ea580c", line_width=1.5,
            annotation_text=f"Min Temp ({t_min:.1f} °C)", annotation_position="bottom right",
            annotation_font=dict(size=10, color="#ea580c")
        )
        fig.add_hline(
            y=t_max, line_dash="dash", line_color="#ea580c", line_width=1.5,
            annotation_text=f"Max Temp ({t_max:.1f} °C)", annotation_position="top right",
            annotation_font=dict(size=10, color="#ea580c")
        )

    fig.update_layout(
        title=dict(
            text=f"<b>{param_title} Trend</b> ({unit if unit else 'Level'})",
            font=dict(size=14, color="#1e293b", family="Plus Jakarta Sans")
        ),
        xaxis=dict(
            title="",
            showgrid=True,
            gridcolor="#f1f5f9",
            tickfont=dict(size=11, color="#64748b"),
        ),
        yaxis=dict(
            title=unit if unit else "Value",
            showgrid=True,
            gridcolor="#f1f5f9",
            tickfont=dict(size=11, color="#64748b"),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11)
        ),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        height=height,
        margin=dict(l=40, r=40, t=50, b=30),
        hovermode="closest",
    )
    return fig


def build_combined_overview_chart(df: pd.DataFrame, height: int = 420) -> go.Figure:
    """
    Renders 4 synchronized subplots for pH, TDS, Turbidity, and Temperature
    for clean multi-parameter analysis.
    """
    if df.empty:
        fig = go.Figure()
        fig.update_layout(height=height)
        return fig

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("pH Level", "TDS (mg/L)", "Turbidity (NTU)", "Temperature (°C)"),
        vertical_spacing=0.18,
        horizontal_spacing=0.08
    )

    tanks = df["tank_name"].unique()
    colors = ["#0284c7", "#0d9488", "#6366f1", "#f59e0b"]

    for idx, tank in enumerate(tanks):
        sub_df = df[df["tank_name"] == tank].sort_values("timestamp")
        c = colors[idx % len(colors)]

        # Row 1, Col 1: pH
        fig.add_trace(go.Scatter(x=sub_df["timestamp"], y=sub_df["ph"], name="pH ("+tank+")", line=dict(color=c, width=2), showlegend=False), row=1, col=1)
        # Row 1, Col 2: TDS
        fig.add_trace(go.Scatter(x=sub_df["timestamp"], y=sub_df["tds"], name="TDS ("+tank+")", line=dict(color=c, width=2), showlegend=False), row=1, col=2)
        # Row 2, Col 1: Turbidity
        fig.add_trace(go.Scatter(x=sub_df["timestamp"], y=sub_df["turbidity"], name="Turbidity ("+tank+")", line=dict(color=c, width=2), showlegend=False), row=2, col=1)
        # Row 2, Col 2: Temperature
        fig.add_trace(go.Scatter(x=sub_df["timestamp"], y=sub_df["temperature"], name="Temp ("+tank+")", line=dict(color=c, width=2), showlegend=False), row=2, col=2)

    fig.update_layout(
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        height=height,
        margin=dict(l=30, r=30, t=50, b=30),
    )
    fig.update_xaxes(showgrid=True, gridcolor="#f1f5f9")
    fig.update_yaxes(showgrid=True, gridcolor="#f1f5f9")
    return fig


def build_water_quality_gauge(score: float) -> go.Figure:
    """Builds a gauge chart for the Water Quality Index score."""
    color = "#059669" if score >= 85 else ("#d97706" if score >= 65 else "#dc2626")
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "<b>Water Quality Index</b><br><span style='font-size:0.8em;color:#64748b;'>Composite Parameter Score</span>", 'font': {'size': 14}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#94a3b8"},
            'bar': {'color': color, 'thickness': 0.28},
            'bgcolor': "#ffffff",
            'borderwidth': 1,
            'bordercolor': "#e2e8f0",
            'steps': [
                {'range': [0, 65], 'color': '#fee2e2'},
                {'range': [65, 85], 'color': '#fef3c7'},
                {'range': [85, 100], 'color': '#ecfdf5'}
            ],
            'threshold': {
                'line': {'color': "#0f172a", 'width': 3},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    fig.update_layout(
        height=220,
        margin=dict(l=25, r=25, t=40, b=10),
        paper_bgcolor="#ffffff",
        font=dict(family="Plus Jakarta Sans", color="#0f172a")
    )
    return fig
