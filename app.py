import streamlit as st
from collections import Counter, defaultdict
from datetime import datetime
import pandas as pd

# 1. Page Configuration
st.markdown("<p style='color:#6B7280'>Simulated Network Operations Monitoring System</p>", unsafe_allow_html=True)
st.set_page_config(page_title="Aura Sentinel | Log Intelligence", layout="wide")

# 2. Advanced CSS: Flexbox & Neon Professional Theme
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');

        .stApp { background-color: #08090A; font-family: 'Plus Jakarta Sans', sans-serif; }

        .main-container {
            display: flex; flex-direction: column;
            max-width: 1100px; margin: auto; padding: 20px;
        }

        .brand-name { color: #8B5CF6; font-size: 14px; font-weight: 800; text-transform: uppercase; letter-spacing: 2px; }
        .main-title { color: #FFFFFF !important; font-size: 48px; font-weight: 800; margin-top: -10px; margin-bottom: 30px; }

        /* Hero Card Flexbox */
        .hero-card {
            background: linear-gradient(135deg, #1A1C1E 0%, #0D0E10 100%);
            border: 1px solid #2D2E32;
            border-radius: 24px; padding: 40px;
            display: flex; justify-content: space-between; align-items: center;
            margin-bottom: 30px; box-shadow: 0 20px 40px rgba(0,0,0,0.4);
        }

        /* Issue Item Flexbox */
        .issue-box {
            display: flex; justify-content: space-between; align-items: center;
            background: #111214; padding: 20px; border-radius: 16px;
            margin-bottom: 12px; border: 1px solid #1C1E22;
        }

        .issue-info b { color: #FFFFFF !important; font-size: 16px; display: block; }
        .issue-info span { color: #6B7280 !important; font-size: 13px; }

        /* Button Styling */
        div.stButton > button {
            background: #8B5CF6 !important; color: white !important;
            border: none !important; border-radius: 10px !important;
            font-weight: 600 !important; transition: 0.3s;
        }
        div.stButton > button:hover { transform: scale(1.05); box-shadow: 0 0 15px rgba(139, 92, 246, 0.4); }

        /* Hide Streamlit default headers */
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 3. Initialize Session State (The "Memory" of the App)
if 'resolved_errors' not in st.session_state:
    st.session_state.resolved_errors = set()
if 'log_data' not in st.session_state:
    st.session_state.log_data = None

# 4. Header Section
st.markdown('<div class="main-container">', unsafe_allow_html=True)
st.markdown('<p class="brand-name">Project Aura Sentinel</p>', unsafe_allow_html=True)
st.markdown('<h1 class="main-title">Network Pulse</h1>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload logs to analyze system health", type=["txt"])

if uploaded_file:
    # Save file to session state so it doesn't disappear on button click
    content = uploaded_file.read().decode("utf-8").splitlines()
    st.session_state.log_data = content

if st.session_state.log_data:
    # --- Logic: Processing Logs ---
    error_counter = Counter()
    hourly_errors = defaultdict(int)
    total_errors = 0

    for line in st.session_state.log_data:
        parts = line.strip().split(" ", 3)
        if len(parts) >= 4:
            ts, lvl, msg = parts[0] + " " + parts[1], parts[2], parts[3]
            
            # Skip errors the user has already "Resolved"
            if lvl == "ERROR" and msg not in st.session_state.resolved_errors:
                total_errors += 1
                error_counter[msg] += 1
                try:
                    h = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").strftime("%H:00")
                    hourly_errors[h] += 1
                except: pass

    # --- UI: Dashboard ---
    if total_errors > 0:
        peak_h = max(hourly_errors, key=hourly_errors.get) if hourly_errors else "--:--"
        
        # Hero Card
        st.markdown(f"""
            <div class="hero-card">
                <div>
                    <p style="color: #6B7280; font-weight: 600; margin: 0;">PEAK INCIDENT WINDOW</p>
                    <h1 style="color:white; font-size: 60px; margin:0;">{peak_h}</h1>
                </div>
                <div style="text-align: right;">
                    <p style="color: #34D399; font-size: 32px; font-weight: 800; margin:0;">{total_errors}</p>
                    <p style="color: #6B7280; font-size: 12px; margin:0;">ACTIVE ANOMALIES</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        col_left, col_right = st.columns([1, 1.2], gap="large")

        with col_left:
            st.markdown("### <span style='color:white'>Unresolved Issues</span>", unsafe_allow_html=True)
            for error, count in error_counter.most_common(5):
                # Create a row with Flexbox behavior using Streamlit columns
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"""
                        <div style="margin-bottom: 20px;">
                            <b style="color:white; display:block;">{error}</b>
                            <span style="color:#6B7280; font-size:12px;">Captured {count} times</span>
                        </div>
                    """, unsafe_allow_html=True)
                with c2:
                    # When clicked, add the error to our "Resolved" set
                    if st.button("RESOLVE", key=f"res_{error}"):
                        st.session_state.resolved_errors.add(error)
                        st.rerun() # Refresh page to update list

        with col_right:
            st.markdown("### <span style='color:white'>Trend Velocity</span>", unsafe_allow_html=True)
            if hourly_errors:
                chart_df = pd.DataFrame({
                    'Time': list(hourly_errors.keys()),
                    'Incidents': list(hourly_errors.values())
                }).set_index('Time')
                st.bar_chart(chart_df, color="#8B5CF6")
    else:
        # State when all errors are resolved
        st.balloons()
        st.success("System is Healthy. All detected anomalies have been resolved.")
        if st.button("Reset Analysis"):
            st.session_state.resolved_errors = set()
            st.rerun()

else:
    # Empty State
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.image("https://illustrations.popsy.co/white/abstract-art-4.svg", width=500)
    st.markdown("<p style='text-align: center; color: #4B5563;'>Awaiting log stream for Sentinel analysis...</p>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
