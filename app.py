"""
Smart Drinking Water Quality Monitoring System — Interactive IoT Dashboard
Real-time water quality intelligence and community tank surveillance.
"""

from datetime import datetime, timedelta
import pandas as pd
import streamlit as st

# Custom modules
from data_generator import (
    TANKS,
    DEFAULT_THRESHOLDS,
    PARAMETER_METADATA,
    generate_initial_history,
    generate_single_reading,
)
from monitoring import (
    evaluate_parameter,
    evaluate_reading_overview,
)
from alerts import (
    process_reading_for_alerts,
    generate_initial_alerts,
    update_alert_status,
)
from dashboard_utils import (
    get_custom_css,
    render_demo_banner_html,
    render_header_html,
    render_system_indicators_html,
    render_parameter_card_html,
    build_parameter_chart,
    build_combined_overview_chart,
    build_water_quality_gauge,
)

# -----------------------------------------------------------------------------
# 1. STREAMLIT CONFIGURATION & SESSION STATE INITIALIZATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Smart Drinking Water Quality Monitoring System",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject custom styling
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Initialize Session State
if "thresholds" not in st.session_state:
    st.session_state.thresholds = dict(DEFAULT_THRESHOLDS)

if "history_df" not in st.session_state:
    st.session_state.history_df = generate_initial_history(records_per_tank=30)

if "alerts" not in st.session_state or "next_alert_id" not in st.session_state:
    init_alerts, next_id = generate_initial_alerts(
        st.session_state.history_df,
        st.session_state.thresholds
    )
    st.session_state.alerts = init_alerts
    st.session_state.next_alert_id = next_id

if "selected_tank_id" not in st.session_state:
    st.session_state.selected_tank_id = "TANK-01"


# -----------------------------------------------------------------------------
# 2. HELPER FUNCTIONS FOR INTERACTIVE SIMULATION
# -----------------------------------------------------------------------------
def handle_new_sample(tank_id: str, force_anomaly: bool = False, anomaly_param: str = None):
    """Generates a new simulated sample, updates history, and checks for threshold breaches."""
    new_record = generate_single_reading(
        tank_id=tank_id,
        timestamp=datetime.now(),
        force_anomaly=force_anomaly,
        anomaly_param=anomaly_param,
    )
    # Append to session state history dataframe
    new_row_df = pd.DataFrame([new_record])
    st.session_state.history_df = pd.concat([st.session_state.history_df, new_row_df], ignore_index=True)

    # Process alerts
    updated_alerts, new_alert_id = process_reading_for_alerts(
        new_record,
        st.session_state.thresholds,
        st.session_state.alerts,
        st.session_state.next_alert_id,
    )
    st.session_state.alerts = updated_alerts
    st.session_state.next_alert_id = new_alert_id


# -----------------------------------------------------------------------------
# 3. SIDEBAR NAVIGATION & CONTROLS
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div style="text-align:center; padding:6px 0 14px 0;">
            <span style="font-size:2.2rem;">💧</span>
            <h2 style="margin:4px 0 0 0; color:#0f2744; font-size:1.2rem; font-weight:800;">Water Quality Monitor</h2>
            <p style="margin:0; font-size:0.75rem; color:#64748b; font-weight:600;">IoT Telemetry Dashboard</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🧭 Dashboard Navigation")
    nav_selection = st.radio(
        label="Select Dashboard View",
        options=[
            "Overview Dashboard",
            "Live Monitoring",
            "Historical Analytics",
            "Alerts & Notifications",
            "Water Tanks",
        ],
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("---")
    # Quick Simulation Generator in Sidebar
    st.markdown("### ⚡ Telemetry Generator")
    quick_tank = st.selectbox(
        "Target Tank:",
        options=[t["id"] for t in TANKS],
        format_func=lambda x: next(t["short_name"] for t in TANKS if t["id"] == x),
        key="sb_quick_tank"
    )
    
    col_sb1, col_sb2 = st.columns(2)
    with col_sb1:
        if st.button("➕ Sample", use_container_width=True, help="Generate a normal simulated reading"):
            handle_new_sample(quick_tank, force_anomaly=False)
            st.toast(f"New reading generated for {quick_tank}!", icon="💧")
            st.rerun()

    with col_sb2:
        if st.button("🚨 Spike", use_container_width=True, help="Simulate a threshold breach to test alerts"):
            handle_new_sample(quick_tank, force_anomaly=True)
            st.toast(f"Simulated threshold breach for {quick_tank}!", icon="⚠️")
            st.rerun()

    st.markdown("---")
    # Threshold Configuration Expander
    with st.expander("⚙️ Threshold Settings", expanded=False):
        st.caption("Adjust operational parameters. Defaults reference standard drinking water baselines.")
        
        new_ph_min = st.number_input("Min pH", min_value=4.0, max_value=8.0, value=float(st.session_state.thresholds["ph_min"]), step=0.1)
        new_ph_max = st.number_input("Max pH", min_value=7.5, max_value=11.0, value=float(st.session_state.thresholds["ph_max"]), step=0.1)
        new_tds_max = st.number_input("Max TDS (mg/L)", min_value=100.0, max_value=2000.0, value=float(st.session_state.thresholds["tds_max"]), step=25.0)
        new_turb_max = st.number_input("Max Turbidity (NTU)", min_value=0.5, max_value=10.0, value=float(st.session_state.thresholds["turbidity_max"]), step=0.5)
        new_temp_min = st.number_input("Min Temp (°C)", min_value=5.0, max_value=25.0, value=float(st.session_state.thresholds["temp_min"]), step=0.5)
        new_temp_max = st.number_input("Max Temp (°C)", min_value=25.0, max_value=45.0, value=float(st.session_state.thresholds["temp_max"]), step=0.5)

        if st.button("Update Thresholds", use_container_width=True):
            st.session_state.thresholds["ph_min"] = float(new_ph_min)
            st.session_state.thresholds["ph_max"] = float(new_ph_max)
            st.session_state.thresholds["tds_max"] = float(new_tds_max)
            st.session_state.thresholds["turbidity_max"] = float(new_turb_max)
            st.session_state.thresholds["temp_min"] = float(new_temp_min)
            st.session_state.thresholds["temp_max"] = float(new_temp_max)
            st.success("Thresholds updated!")
            st.rerun()

        if st.button("Reset to Standard Defaults", use_container_width=True):
            st.session_state.thresholds = dict(DEFAULT_THRESHOLDS)
            st.info("Reset to baseline thresholds.")
            st.rerun()

    # System Status badge in sidebar
    open_alerts_count = sum(1 for a in st.session_state.alerts if a["status"] == "Open")
    st.markdown(f"""
        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:10px; margin-top:15px; font-size:0.75rem;">
            <div style="color:#0369a1; font-weight:700; margin-bottom:4px;">SYSTEM METRICS</div>
            <div>• Monitored Tanks: <strong>{len(TANKS)}</strong></div>
            <div>• Open Alerts: <strong style="color:{'#dc2626' if open_alerts_count > 0 else '#059669'};">{open_alerts_count}</strong></div>
            <div>• Total Records: <strong>{len(st.session_state.history_df)}</strong></div>
            <div>• Mode: <strong>Live Simulation</strong></div>
        </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 4. RENDER COMMON HEADER
# -----------------------------------------------------------------------------
st.markdown(render_header_html(), unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 5. PAGE: OVERVIEW DASHBOARD
# -----------------------------------------------------------------------------
if nav_selection == "Overview Dashboard":
    st.markdown("### 📊 System Overview & Health Status")

    # Filter by tank for summary cards
    t_col1, t_col2 = st.columns([3, 1])
    with t_col1:
        st.write("Real-time telemetry indicators and status summary across monitored community water storage units.")
    with t_col2:
        overview_tank = st.selectbox(
            "Filter Overview by Tank:",
            options=["ALL"] + [t["id"] for t in TANKS],
            format_func=lambda x: "All Tanks (Aggregate)" if x == "ALL" else next(t["name"] for t in TANKS if t["id"] == x),
            key="overview_tank_select"
        )

    # Determine latest reading
    if overview_tank == "ALL":
        latest_df = st.session_state.history_df.sort_values("timestamp").groupby("tank_id").last().reset_index()
        most_recent_row = st.session_state.history_df.sort_values("timestamp").iloc[-1]
        active_reading = {
            "timestamp": most_recent_row["timestamp"],
            "tank_id": "ALL",
            "tank_name": "All Monitored Water Tanks",
            "ph": float(round(latest_df["ph"].mean(), 2)),
            "tds": float(round(latest_df["tds"].mean(), 1)),
            "turbidity": float(round(latest_df["turbidity"].mean(), 2)),
            "temperature": float(round(latest_df["temperature"].mean(), 1)),
        }
    else:
        tank_records = st.session_state.history_df[st.session_state.history_df["tank_id"] == overview_tank].sort_values("timestamp")
        active_reading = tank_records.iloc[-1].to_dict() if not tank_records.empty else generate_single_reading(overview_tank)

    # Evaluate overview reading
    overview_eval = evaluate_reading_overview(active_reading, st.session_state.thresholds)
    open_alerts_count = sum(1 for a in st.session_state.alerts if a["status"] == "Open")

    # Render System Indicators Ribbon
    st.markdown(render_system_indicators_html(
        tank_count=len(TANKS),
        flagged_params_count=overview_eval["flagged_count"],
        latest_timestamp=active_reading["timestamp"],
        open_alerts_count=open_alerts_count
    ), unsafe_allow_html=True)

    # 4 Primary Parameter Cards (clean labels, no code tags)
    col_ph, col_tds, col_turb, col_temp = st.columns(4)

    with col_ph:
        ph_range = f"{st.session_state.thresholds['ph_min']:.1f} – {st.session_state.thresholds['ph_max']:.1f}"
        st.markdown(render_parameter_card_html(
            param_key="ph",
            title="pH Level",
            value=active_reading["ph"],
            unit="",
            range_str=ph_range,
            eval_dict=overview_eval["parameters"]["ph"]
        ), unsafe_allow_html=True)

    with col_tds:
        tds_range = f"<= {st.session_state.thresholds['tds_max']:.0f} mg/L"
        st.markdown(render_parameter_card_html(
            param_key="tds",
            title="Total Dissolved Solids",
            value=active_reading["tds"],
            unit="mg/L",
            range_str=tds_range,
            eval_dict=overview_eval["parameters"]["tds"]
        ), unsafe_allow_html=True)

    with col_turb:
        turb_range = f"<= {st.session_state.thresholds['turbidity_max']:.1f} NTU"
        st.markdown(render_parameter_card_html(
            param_key="turbidity",
            title="Turbidity",
            value=active_reading["turbidity"],
            unit="NTU",
            range_str=turb_range,
            eval_dict=overview_eval["parameters"]["turbidity"]
        ), unsafe_allow_html=True)

    with col_temp:
        temp_range = f"{st.session_state.thresholds['temp_min']:.1f} – {st.session_state.thresholds['temp_max']:.1f} °C"
        st.markdown(render_parameter_card_html(
            param_key="temperature",
            title="Water Temperature",
            value=active_reading["temperature"],
            unit="°C",
            range_str=temp_range,
            eval_dict=overview_eval["parameters"]["temperature"]
        ), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Mid section: Water Quality Score Gauge & Recent Alerts
    col_gauge, col_alert_snip = st.columns([1, 2])

    with col_gauge:
        st.plotly_chart(build_water_quality_gauge(overview_eval["wqi_score"]), use_container_width=True)
        st.caption("ℹ️ Water Quality Score: 100 represents all parameters within optimal thresholds.")

    with col_alert_snip:
        st.markdown("#### 🔔 Recent System Alerts & Action Items")
        recent_open_alerts = [a for a in st.session_state.alerts if a["status"] == "Open"][:3]
        if recent_open_alerts:
            for alert in recent_open_alerts:
                badge_color = "#dc2626" if alert["severity"] == "Critical" else "#d97706"
                st.markdown(f"""
                    <div style="background:#ffffff; border:1px solid #e2e8f0; border-left:4px solid {badge_color}; border-radius:8px; padding:10px 14px; margin-bottom:8px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <strong>{alert['alert_id']} — {alert['tank_name']}</strong>
                            <span style="background:#fee2e2; color:#b91c1c; font-size:0.75rem; font-weight:700; padding:2px 8px; border-radius:12px;">{alert['severity']}</span>
                        </div>
                        <div style="font-size:0.84rem; color:#1e293b; margin:4px 0;">
                            <strong>{alert['parameter']}:</strong> Observed <span style="font-weight:700; color:#dc2626;">{alert['observed_value']}</span> ({alert['breach_detail']})
                        </div>
                        <div style="font-size:0.78rem; color:#475569;">
                            👉 <em>Action:</em> {alert['suggested_action']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ All monitored parameters across water storage tanks are currently within configured bounds.")

    st.markdown("---")
    # Tank Overview Table
    st.markdown("#### 🏛️ Monitored Tanks Status Summary")
    tank_summary_rows = []
    for t in TANKS:
        t_records = st.session_state.history_df[st.session_state.history_df["tank_id"] == t["id"]].sort_values("timestamp")
        latest = t_records.iloc[-1].to_dict() if not t_records.empty else {}
        t_eval = evaluate_reading_overview(latest, st.session_state.thresholds) if latest else {}
        t_alerts = sum(1 for a in st.session_state.alerts if a["tank_id"] == t["id"] and a["status"] == "Open")
        
        tank_summary_rows.append({
            "Tank ID": t["id"],
            "Tank Name": t["name"],
            "Location": t["location"],
            "Latest Sample": latest.get("timestamp").strftime("%H:%M:%S") if latest.get("timestamp") else "N/A",
            "pH": latest.get("ph", "N/A"),
            "TDS (mg/L)": latest.get("tds", "N/A"),
            "Turbidity (NTU)": latest.get("turbidity", "N/A"),
            "Temp (°C)": latest.get("temperature", "N/A"),
            "Overall Status": t_eval.get("overall_status", "Normal"),
            "Open Alerts": t_alerts,
        })
    df_tank_summary = pd.DataFrame(tank_summary_rows)
    st.dataframe(
        df_tank_summary,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Overall Status": st.column_config.TextColumn("Overall Status"),
            "Open Alerts": st.column_config.NumberColumn("Open Alerts")
        }
    )


# -----------------------------------------------------------------------------
# 6. PAGE: LIVE MONITORING
# -----------------------------------------------------------------------------
elif nav_selection == "Live Monitoring":
    st.markdown("### 📡 Live Water Quality Monitoring")
    st.write(
        "Generate simulated telemetry on demand, test alert triggers with simulated spikes, "
        "and inspect real-time sensor records preserved in session state."
    )

    # Tank selector and interactive controls
    c_ctrl1, c_ctrl2, c_ctrl3 = st.columns([2, 1, 1])

    with c_ctrl1:
        selected_tank = st.selectbox(
            "Select Water Tank to Monitor:",
            options=[t["id"] for t in TANKS],
            format_func=lambda x: next(f"{t['name']} ({t['location']})" for t in TANKS if t["id"] == x),
            key="live_demo_tank_select"
        )
        current_tank_info = next(t for t in TANKS if t["id"] == selected_tank)

    with c_ctrl2:
        st.write("&nbsp;")
        if st.button("🔄 Generate New Reading", use_container_width=True, type="primary"):
            handle_new_sample(selected_tank, force_anomaly=False)
            st.toast(f"New sample recorded for {current_tank_info['short_name']}!", icon="💧")
            st.rerun()

    with c_ctrl3:
        st.write("&nbsp;")
        anomaly_choice = st.selectbox(
            "Inject Simulated Spike:",
            options=["ph", "tds", "turbidity", "temperature"],
            format_func=lambda x: f"Spike {PARAMETER_METADATA[x]['name']}",
            key="anomaly_param_pick"
        )
        if st.button("⚠️ Trigger Breach", use_container_width=True, help="Simulate a threshold breach to verify alert generation"):
            handle_new_sample(selected_tank, force_anomaly=True, anomaly_param=anomaly_choice)
            st.warning(f"Simulated {anomaly_choice.upper()} threshold breach recorded for {current_tank_info['short_name']}!")
            st.rerun()

    st.markdown("---")

    # Get latest reading for selected tank
    tank_data = st.session_state.history_df[st.session_state.history_df["tank_id"] == selected_tank].sort_values("timestamp")
    latest_reading = tank_data.iloc[-1].to_dict() if not tank_data.empty else generate_single_reading(selected_tank)
    prev_reading = tank_data.iloc[-2].to_dict() if len(tank_data) >= 2 else latest_reading

    reading_eval = evaluate_reading_overview(latest_reading, st.session_state.thresholds)

    # Info bar for the selected tank
    st.markdown(f"""
        <div style="background:#f1f5f9; border-radius:8px; padding:12px 18px; margin-bottom:18px; border:1px solid #cbd5e1; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
            <div>
                <strong>Monitoring Target:</strong> {current_tank_info['name']} &nbsp;|&nbsp; 
                <strong>Location:</strong> {current_tank_info['location']} &nbsp;|&nbsp; 
                <strong>Capacity:</strong> {current_tank_info['capacity']}
            </div>
            <div style="font-size:0.85rem; color:#0369a1; font-weight:700;">
                Latest Sample: {latest_reading['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 4 Parameter Metric Cards (clean labels, no code tags)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        delta_ph = latest_reading["ph"] - prev_reading.get("ph", latest_reading["ph"])
        st.markdown(render_parameter_card_html(
            "ph", "pH Level", latest_reading["ph"], "",
            f"{st.session_state.thresholds['ph_min']:.1f} – {st.session_state.thresholds['ph_max']:.1f}",
            reading_eval["parameters"]["ph"], delta=delta_ph
        ), unsafe_allow_html=True)

    with c2:
        delta_tds = latest_reading["tds"] - prev_reading.get("tds", latest_reading["tds"])
        st.markdown(render_parameter_card_html(
            "tds", "Total Dissolved Solids", latest_reading["tds"], "mg/L",
            f"<= {st.session_state.thresholds['tds_max']:.0f} mg/L",
            reading_eval["parameters"]["tds"], delta=delta_tds
        ), unsafe_allow_html=True)

    with c3:
        delta_turb = latest_reading["turbidity"] - prev_reading.get("turbidity", latest_reading["turbidity"])
        st.markdown(render_parameter_card_html(
            "turbidity", "Turbidity", latest_reading["turbidity"], "NTU",
            f"<= {st.session_state.thresholds['turbidity_max']:.1f} NTU",
            reading_eval["parameters"]["turbidity"], delta=delta_turb
        ), unsafe_allow_html=True)

    with c4:
        delta_temp = latest_reading["temperature"] - prev_reading.get("temperature", latest_reading["temperature"])
        st.markdown(render_parameter_card_html(
            "temperature", "Water Temperature", latest_reading["temperature"], "°C",
            f"{st.session_state.thresholds['temp_min']:.1f} – {st.session_state.thresholds['temp_max']:.1f} °C",
            reading_eval["parameters"]["temperature"], delta=delta_temp
        ), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Recent Readings Table (Latest 20)
    st.markdown("#### 📋 Recent Telemetry Records (Latest 20 Samples)")
    recent_20 = tank_data.tail(20).sort_values("timestamp", ascending=False).copy()
    
    # Format table for display cleanly
    display_table = pd.DataFrame({
        "Timestamp": recent_20["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S"),
        "Tank": recent_20["tank_name"],
        "pH Level": recent_20["ph"].map("{:.2f}".format),
        "TDS (mg/L)": recent_20["tds"].map("{:.1f}".format),
        "Turbidity (NTU)": recent_20["turbidity"].map("{:.2f}".format),
        "Temp (°C)": recent_20["temperature"].map("{:.1f}".format),
    })

    st.dataframe(display_table, use_container_width=True, hide_index=True)

    # Download CSV
    csv_data = recent_20.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Recent Telemetry as CSV",
        data=csv_data,
        file_name=f"water_telemetry_{selected_tank}.csv",
        mime="text/csv",
    )


# -----------------------------------------------------------------------------
# 7. PAGE: HISTORICAL ANALYTICS
# -----------------------------------------------------------------------------
elif nav_selection == "Historical Analytics":
    st.markdown("### 📈 Historical Analytics & Multi-Parameter Trends")
    st.write(
        "Interactive trend analysis with configurable time windows, customizable threshold reference lines, "
        "and calculated summary statistics."
    )

    # Analytics Filters
    f_col1, f_col2, f_col3 = st.columns([2, 2, 2])
    with f_col1:
        hist_tank = st.selectbox(
            "Filter by Water Tank:",
            options=["ALL"] + [t["id"] for t in TANKS],
            format_func=lambda x: "All Tanks (Combined)" if x == "ALL" else next(t["name"] for t in TANKS if t["id"] == x),
            key="hist_tank_select"
        )
    with f_col2:
        time_window = st.selectbox(
            "Select Time Window:",
            options=["Last 1 Hour", "Last 6 Hours", "Last 24 Hours", "All Records"],
            index=2,
            key="hist_time_window"
        )
    with f_col3:
        chart_view_mode = st.selectbox(
            "Visualization Mode:",
            options=["Detailed Parameter Tabs", "Synchronized Multi-Trend View"],
            index=0,
            key="hist_view_mode"
        )

    # Filter dataframe based on selections
    df_filtered = st.session_state.history_df.copy()
    if hist_tank != "ALL":
        df_filtered = df_filtered[df_filtered["tank_id"] == hist_tank]

    now = datetime.now()
    if time_window == "Last 1 Hour":
        df_filtered = df_filtered[df_filtered["timestamp"] >= (now - timedelta(hours=1))]
    elif time_window == "Last 6 Hours":
        df_filtered = df_filtered[df_filtered["timestamp"] >= (now - timedelta(hours=6))]
    elif time_window == "Last 24 Hours":
        df_filtered = df_filtered[df_filtered["timestamp"] >= (now - timedelta(hours=24))]

    df_filtered = df_filtered.sort_values("timestamp")

    if df_filtered.empty:
        st.warning("No records match the current filter criteria. Use the Telemetry Generator in the sidebar to create new readings.")
    else:
        # Dynamic Summary Statistics Calculation
        st.markdown("#### 📊 Parameter Statistics (Calculated from Active Telemetry)")
        s1, s2, s3, s4 = st.columns(4)

        thresh = st.session_state.thresholds
        ph_breaches = int(((df_filtered["ph"] < thresh["ph_min"]) | (df_filtered["ph"] > thresh["ph_max"])).sum())
        tds_breaches = int((df_filtered["tds"] > thresh["tds_max"]).sum())
        turb_breaches = int((df_filtered["turbidity"] > thresh["turbidity_max"]).sum())
        temp_breaches = int(((df_filtered["temperature"] < thresh["temp_min"]) | (df_filtered["temperature"] > thresh["temp_max"])).sum())

        with s1:
            st.metric(
                label="pH Statistics",
                value=f"Avg {df_filtered['ph'].mean():.2f}",
                delta=f"{ph_breaches} exceedances" if ph_breaches > 0 else "0 exceedances",
                delta_color="inverse" if ph_breaches > 0 else "normal"
            )
            st.caption(f"Min: {df_filtered['ph'].min():.2f} | Max: {df_filtered['ph'].max():.2f} | Samples: {len(df_filtered)}")

        with s2:
            st.metric(
                label="TDS Statistics",
                value=f"Avg {df_filtered['tds'].mean():.1f} mg/L",
                delta=f"{tds_breaches} exceedances" if tds_breaches > 0 else "0 exceedances",
                delta_color="inverse" if tds_breaches > 0 else "normal"
            )
            st.caption(f"Min: {df_filtered['tds'].min():.1f} | Max: {df_filtered['tds'].max():.1f} mg/L")

        with s3:
            st.metric(
                label="Turbidity Statistics",
                value=f"Avg {df_filtered['turbidity'].mean():.2f} NTU",
                delta=f"{turb_breaches} exceedances" if turb_breaches > 0 else "0 exceedances",
                delta_color="inverse" if turb_breaches > 0 else "normal"
            )
            st.caption(f"Min: {df_filtered['turbidity'].min():.2f} | Max: {df_filtered['turbidity'].max():.2f} NTU")

        with s4:
            st.metric(
                label="Temperature Statistics",
                value=f"Avg {df_filtered['temperature'].mean():.1f} °C",
                delta=f"{temp_breaches} exceedances" if temp_breaches > 0 else "0 exceedances",
                delta_color="inverse" if temp_breaches > 0 else "normal"
            )
            st.caption(f"Min: {df_filtered['temperature'].min():.1f} | Max: {df_filtered['temperature'].max():.1f} °C")

        st.markdown("<br>", unsafe_allow_html=True)

        # Plotly Visualizations
        if chart_view_mode == "Synchronized Multi-Trend View":
            st.plotly_chart(build_combined_overview_chart(df_filtered), use_container_width=True)
        else:
            tab_ph, tab_tds, tab_turb, tab_temp = st.tabs([
                "💧 pH Trend",
                "🧂 TDS Trend (mg/L)",
                "🌫️ Turbidity Trend (NTU)",
                "🌡️ Temperature Trend (°C)"
            ])

            with tab_ph:
                st.plotly_chart(build_parameter_chart(
                    df_filtered, "ph", "pH Level", "", thresh, height=360
                ), use_container_width=True)

            with tab_tds:
                st.plotly_chart(build_parameter_chart(
                    df_filtered, "tds", "Total Dissolved Solids (TDS)", "mg/L", thresh, height=360
                ), use_container_width=True)

            with tab_turb:
                st.plotly_chart(build_parameter_chart(
                    df_filtered, "turbidity", "Turbidity", "NTU", thresh, height=360
                ), use_container_width=True)

            with tab_temp:
                st.plotly_chart(build_parameter_chart(
                    df_filtered, "temperature", "Water Temperature", "°C", thresh, height=360
                ), use_container_width=True)


# -----------------------------------------------------------------------------
# 8. PAGE: ALERTS & NOTIFICATIONS
# -----------------------------------------------------------------------------
elif nav_selection == "Alerts & Notifications":
    st.markdown("### 🔔 Alerts & Incident Management")
    st.write("Real-time automated incident tracking based on operational parameter threshold evaluations.")

    # Filter controls
    a_col1, a_col2 = st.columns([1, 1])
    with a_col1:
        status_filter = st.radio(
            "Filter Alerts by Status:",
            options=["All", "Open", "Acknowledged", "Resolved"],
            horizontal=True,
            index=0
        )
    with a_col2:
        tank_filter = st.selectbox(
            "Filter Alerts by Tank:",
            options=["ALL"] + [t["id"] for t in TANKS],
            format_func=lambda x: "All Tanks" if x == "ALL" else next(t["name"] for t in TANKS if t["id"] == x),
            key="alert_tank_filter"
        )

    # Filtered alert list
    alerts_to_show = st.session_state.alerts
    if status_filter != "All":
        alerts_to_show = [a for a in alerts_to_show if a["status"] == status_filter]
    if tank_filter != "ALL":
        alerts_to_show = [a for a in alerts_to_show if a["tank_id"] == tank_filter]

    st.markdown(f"**Showing {len(alerts_to_show)} Alert(s)**")

    if not alerts_to_show:
        st.info("No alerts match the selected status and tank filters.")
    else:
        for alert in alerts_to_show:
            alert_id = alert["alert_id"]
            status = alert["status"]
            severity = alert["severity"]

            card_border = "#dc2626" if severity == "Critical" else ("#d97706" if severity == "Warning" else "#059669")
            if status == "Resolved":
                card_border = "#059669"

            st.markdown(f"""
                <div style="background:#ffffff; border:1px solid #e2e8f0; border-left:5px solid {card_border}; border-radius:10px; padding:16px 20px; margin-bottom:14px; box-shadow:0 1px 3px rgba(0,0,0,0.03);">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:8px;">
                        <div>
                            <span style="font-weight:700; color:#0369a1; font-size:0.95rem;">{alert_id}</span>
                            <span style="font-weight:700; color:#0f172a; margin-left:8px; font-size:0.95rem;">— {alert['tank_name']}</span>
                        </div>
                        <div style="display:flex; gap:6px;">
                            <span style="background:{'#fee2e2' if severity=='Critical' else '#fffbeb'}; color:{'#b91c1c' if severity=='Critical' else '#b45309'}; font-size:0.75rem; font-weight:700; padding:2px 8px; border-radius:12px;">{severity}</span>
                            <span style="background:{'#fef2f2' if status=='Open' else ('#fef3c7' if status=='Acknowledged' else '#ecfdf5')}; color:{'#991b1b' if status=='Open' else ('#92400e' if status=='Acknowledged' else '#166534')}; font-size:0.75rem; font-weight:700; padding:2px 8px; border-radius:12px;">Status: {status}</span>
                        </div>
                    </div>
                    <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:10px; margin:12px 0; font-size:0.85rem;">
                        <div><strong>Timestamp:</strong> {alert['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}</div>
                        <div><strong>Parameter:</strong> {alert['parameter']}</div>
                        <div><strong>Observed Value:</strong> <span style="font-weight:700; color:#dc2626;">{alert['observed_value']}</span></div>
                        <div><strong>Configured Limit:</strong> {alert['configured_threshold']}</div>
                    </div>
                    <div style="background:#f8fafc; border:1px solid #f1f5f9; border-radius:6px; padding:8px 12px; margin-bottom:10px; font-size:0.82rem;">
                        <strong>👉 Suggested Action:</strong> {alert['suggested_action']}
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Workflow action buttons
            btn_col1, btn_col2, _ = st.columns([1, 1, 3])
            with btn_col1:
                if status == "Open":
                    if st.button("Acknowledge", key=f"ack_{alert_id}"):
                        st.session_state.alerts = update_alert_status(
                            st.session_state.alerts, alert_id, "Acknowledged",
                            notes="Acknowledged by operator; site inspection initiated."
                        )
                        st.success(f"Alert {alert_id} marked as Acknowledged.")
                        st.rerun()

            with btn_col2:
                if status in ["Open", "Acknowledged"]:
                    if st.button("Mark Resolved", key=f"res_{alert_id}"):
                        st.session_state.alerts = update_alert_status(
                            st.session_state.alerts, alert_id, "Resolved",
                            notes="Resolved after verification and inspection."
                        )
                        st.success(f"Alert {alert_id} marked as Resolved.")
                        st.rerun()


# -----------------------------------------------------------------------------
# 9. PAGE: WATER TANKS
# -----------------------------------------------------------------------------
elif nav_selection == "Water Tanks":
    st.markdown("### 🚰 Water Storage Tanks")
    st.write(
        "Infrastructure monitoring overview across residential water storage facilities."
    )

    for tank in TANKS:
        t_id = tank["id"]
        t_records = st.session_state.history_df[st.session_state.history_df["tank_id"] == t_id].sort_values("timestamp")
        latest = t_records.iloc[-1].to_dict() if not t_records.empty else {}
        t_eval = evaluate_reading_overview(latest, st.session_state.thresholds) if latest else {}
        open_alerts = [a for a in st.session_state.alerts if a["tank_id"] == t_id and a["status"] == "Open"]

        status_color = t_eval.get("overall_color", "#059669")
        status_name = t_eval.get("overall_status", "Normal")

        st.markdown(f"""
            <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:20px; margin-bottom:16px; box-shadow:0 2px 4px rgba(0,0,0,0.03);">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:10px;">
                    <div>
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span style="font-size:1.4rem;">🚰</span>
                            <h3 style="margin:0; font-size:1.15rem; color:#0f2744;">{tank['name']}</h3>
                            <span style="background:#f1f5f9; color:#0369a1; font-size:0.75rem; font-weight:700; padding:2px 8px; border-radius:4px;">{t_id}</span>
                        </div>
                        <p style="margin:4px 0 10px 0; font-size:0.84rem; color:#475569;">📍 <strong>Location:</strong> {tank['location']} &nbsp;|&nbsp; <strong>Capacity:</strong> {tank['capacity']}</p>
                        <p style="margin:0; font-size:0.8rem; color:#64748b;">{tank['description']}</p>
                    </div>
                    <div style="text-align:right;">
                        <span style="background:{status_color}18; color:{status_color}; font-size:0.82rem; font-weight:700; padding:4px 12px; border-radius:20px; border:1px solid {status_color}40;">
                            {status_name}
                        </span>
                        <div style="font-size:0.75rem; color:#64748b; margin-top:6px;">Open Alerts: <strong style="color:{'#dc2626' if len(open_alerts)>0 else '#059669'};">{len(open_alerts)}</strong></div>
                    </div>
                </div>
                <hr style="margin:14px 0; border:none; border-top:1px solid #f1f5f9;">
                <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(130px, 1fr)); gap:12px;">
                    <div style="background:#f8fafc; padding:8px 12px; border-radius:8px; border:1px solid #f1f5f9;">
                        <span style="font-size:0.72rem; color:#64748b; font-weight:600;">pH Level</span>
                        <div style="font-size:1.15rem; font-weight:700; color:#0f172a;">{latest.get('ph', 'N/A')}</div>
                    </div>
                    <div style="background:#f8fafc; padding:8px 12px; border-radius:8px; border:1px solid #f1f5f9;">
                        <span style="font-size:0.72rem; color:#64748b; font-weight:600;">TDS</span>
                        <div style="font-size:1.15rem; font-weight:700; color:#0f172a;">{latest.get('tds', 'N/A')} <span style="font-size:0.75rem; font-weight:500;">mg/L</span></div>
                    </div>
                    <div style="background:#f8fafc; padding:8px 12px; border-radius:8px; border:1px solid #f1f5f9;">
                        <span style="font-size:0.72rem; color:#64748b; font-weight:600;">Turbidity</span>
                        <div style="font-size:1.15rem; font-weight:700; color:#0f172a;">{latest.get('turbidity', 'N/A')} <span style="font-size:0.75rem; font-weight:500;">NTU</span></div>
                    </div>
                    <div style="background:#f8fafc; padding:8px 12px; border-radius:8px; border:1px solid #f1f5f9;">
                        <span style="font-size:0.72rem; color:#64748b; font-weight:600;">Temperature</span>
                        <div style="font-size:1.15rem; font-weight:700; color:#0f172a;">{latest.get('temperature', 'N/A')} <span style="font-size:0.75rem; font-weight:500;">°C</span></div>
                    </div>
                    <div style="background:#f8fafc; padding:8px 12px; border-radius:8px; border:1px solid #f1f5f9;">
                        <span style="font-size:0.72rem; color:#64748b; font-weight:600;">Last Sampled</span>
                        <div style="font-size:0.95rem; font-weight:600; color:#0369a1;">{latest.get('timestamp').strftime('%H:%M:%S') if latest.get('timestamp') else 'N/A'}</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
