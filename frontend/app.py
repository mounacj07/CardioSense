import streamlit as st
import requests
import json
import os
import time
import re

# Page config
st.set_page_config(
    page_title="CardioSense AI",
    page_icon="🫀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inline CSS - full redesign
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@400;500&family=Outfit:wght@300;400;500;600;700&display=swap');

:root {
    --bg-primary: #0a0c0f;
    --bg-secondary: #10141a;
    --bg-card: #141920;
    --bg-card-hover: #1a2130;
    --border: #1e2a3a;
    --border-bright: #2a3a52;
    --accent: #00d4aa;
    --accent-dim: rgba(0, 212, 170, 0.12);
    --accent-glow: rgba(0, 212, 170, 0.25);
    --danger: #ff4d6d;
    --danger-dim: rgba(255, 77, 109, 0.12);
    --warning: #f5a623;
    --warning-dim: rgba(245, 166, 35, 0.12);
    --text-primary: #e8edf5;
    --text-secondary: #6b7d96;
    --text-muted: #3d4f66;
    --font-display: 'DM Serif Display', serif;
    --font-body: 'Outfit', sans-serif;
    --font-mono: 'DM Mono', monospace;
}

/* ── BASE ── */
html, body, .stApp {
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    font-family: var(--font-body) !important;
}

/* Subtle grid background */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(0,212,170,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,212,170,0.025) 1px, transparent 1px);
    background-size: 48px 48px;
    pointer-events: none;
    z-index: 0;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background-color: var(--bg-secondary) !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 0 !important;
}

/* ── SIDEBAR HEADER ── */
.sidebar-brand {
    background: linear-gradient(135deg, #0d1f35 0%, #0a1628 100%);
    border-bottom: 1px solid var(--border);
    padding: 28px 24px 24px;
    margin-bottom: 8px;
}
.sidebar-brand .brand-icon {
    font-size: 2rem;
    display: block;
    margin-bottom: 10px;
    filter: drop-shadow(0 0 12px rgba(0,212,170,0.6));
}
.sidebar-brand .brand-name {
    font-family: var(--font-display);
    font-size: 1.55rem;
    color: var(--text-primary);
    letter-spacing: -0.02em;
    line-height: 1.1;
}
.sidebar-brand .brand-tagline {
    font-size: 0.72rem;
    color: var(--accent);
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-top: 4px;
    font-weight: 500;
    font-family: var(--font-mono);
}

/* ── SIDEBAR TEXT ── */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown p {
    color: var(--text-secondary) !important;
    font-size: 0.82rem !important;
    font-weight: 400 !important;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: var(--text-primary) !important;
    font-family: var(--font-body) !important;
    font-weight: 600 !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
}

/* ── SECTION DIVIDER ── */
.input-section-label {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--text-muted);
    font-family: var(--font-mono);
    padding: 16px 0 8px;
    border-top: 1px solid var(--border);
    margin-top: 8px;
}

/* ── NUMBER INPUTS ── */
[data-testid="stSidebar"] .stNumberInput input {
    background-color: var(--bg-card) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-bright) !important;
    border-radius: 6px !important;
    font-family: var(--font-mono) !important;
    font-size: 1rem !important;
    font-weight: 500 !important;
}
[data-testid="stSidebar"] .stNumberInput input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px var(--accent-glow) !important;
    outline: none !important;
}

/* Step buttons in number input */
[data-testid="stSidebar"] [data-testid="stNumberInputStepDown"],
[data-testid="stSidebar"] [data-testid="stNumberInputStepUp"] {
    background-color: var(--border) !important;
    color: var(--text-secondary) !important;
    border: none !important;
}

/* ── RUN BUTTON ── */
[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, var(--accent) 0%, #00b894 100%) !important;
    color: #000 !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: var(--font-body) !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.06em !important;
    padding: 14px 20px !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 20px var(--accent-glow) !important;
    text-transform: uppercase !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 28px var(--accent-glow) !important;
}

/* ── MAIN HEADER ── */
.main-header {
    padding: 40px 0 32px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 32px;
}
.main-header .header-eyebrow {
    font-size: 0.68rem;
    font-family: var(--font-mono);
    color: var(--accent);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.main-header h1 {
    font-family: var(--font-display) !important;
    font-size: 2.8rem !important;
    font-weight: 400 !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.03em !important;
    line-height: 1.05 !important;
    margin: 0 !important;
}
.main-header h1 em {
    color: var(--accent);
    font-style: italic;
}
.main-header .header-sub {
    font-size: 0.85rem;
    color: var(--text-secondary);
    margin-top: 10px;
    font-weight: 300;
    letter-spacing: 0.01em;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background-color: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background-color: transparent !important;
    color: var(--text-muted) !important;
    font-family: var(--font-body) !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    padding: 14px 20px !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    transition: all 0.15s ease !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--text-secondary) !important;
}
.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
    background-color: transparent !important;
}

/* ── METRIC CARDS ── */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 20px 22px !important;
    position: relative;
    overflow: hidden;
}
[data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent), transparent);
}
[data-testid="stMetricLabel"] {
    font-size: 0.65rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
    font-family: var(--font-mono) !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.8rem !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
    font-family: var(--font-display) !important;
    letter-spacing: -0.03em !important;
    line-height: 1.1 !important;
}
[data-testid="stMetricDelta"] {
    font-size: 0.75rem !important;
}

/* ── EXPANDERS ── */
.streamlit-expanderHeader, [data-testid="stExpanderToggleIcon"] {
    background-color: var(--bg-card) !important;
    color: var(--text-secondary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    font-family: var(--font-body) !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
}
.streamlit-expanderContent {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
}

/* ── ALERTS ── */
.stAlert {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border-bright) !important;
    border-radius: 8px !important;
    color: var(--text-secondary) !important;
}

/* ── INFO BOX (advice) ── */
.stAlert [data-testid="stMarkdownContainer"] p {
    color: var(--text-secondary) !important;
    font-size: 0.9rem !important;
    line-height: 1.7 !important;
}

/* ── JSON VIEWER ── */
.stJson {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-family: var(--font-mono) !important;
    font-size: 0.78rem !important;
}

/* ── SPINNER ── */
.stSpinner > div {
    border-top-color: var(--accent) !important;
}

/* ── CUSTOM COMPONENTS ── */

/* Risk gauge */
.risk-panel {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 28px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}
.risk-panel.high-risk {
    border-color: var(--danger);
    background: linear-gradient(135deg, var(--bg-card), rgba(255,77,109,0.04));
}
.risk-panel.moderate-risk {
    border-color: var(--warning);
    background: linear-gradient(135deg, var(--bg-card), rgba(245,166,35,0.04));
}
.risk-panel.low-risk {
    border-color: var(--accent);
    background: linear-gradient(135deg, var(--bg-card), rgba(0,212,170,0.04));
}
.risk-panel .risk-label {
    font-size: 0.65rem;
    font-family: var(--font-mono);
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 6px;
}
.risk-panel .risk-value {
    font-family: var(--font-display);
    font-size: 2.2rem;
    letter-spacing: -0.03em;
    line-height: 1;
}
.risk-panel.high-risk .risk-value { color: var(--danger); }
.risk-panel.moderate-risk .risk-value { color: var(--warning); }
.risk-panel.low-risk .risk-value { color: var(--accent); }

.risk-panel .risk-conf {
    font-size: 0.78rem;
    color: var(--text-muted);
    font-family: var(--font-mono);
    margin-top: 6px;
}

/* Confidence bar */
.conf-bar-wrap {
    margin-top: 14px;
}
.conf-bar-bg {
    height: 4px;
    background: var(--border);
    border-radius: 2px;
    overflow: hidden;
}
.conf-bar-fill {
    height: 100%;
    border-radius: 2px;
    transition: width 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}
.high-risk .conf-bar-fill { background: linear-gradient(90deg, var(--danger), #ff8fa3); }
.moderate-risk .conf-bar-fill { background: linear-gradient(90deg, var(--warning), #ffc04d); }
.low-risk .conf-bar-fill { background: linear-gradient(90deg, var(--accent), #00f5d4); }

/* Grounding score ring indicator */
.grounding-panel {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 28px;
    margin-bottom: 20px;
}
.grounding-panel .g-header {
    font-size: 0.65rem;
    font-family: var(--font-mono);
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 16px;
}
.grounding-panel .g-score {
    font-family: var(--font-display);
    font-size: 2.2rem;
    color: var(--text-primary);
    letter-spacing: -0.03em;
}

/* Status badge */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 12px;
    border-radius: 4px;
    font-size: 0.72rem;
    font-weight: 700;
    font-family: var(--font-mono);
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin: 12px 0;
}
.status-badge.grounded {
    background: rgba(0,212,170,0.1);
    color: var(--accent);
    border: 1px solid rgba(0,212,170,0.3);
}
.status-badge.partial {
    background: var(--warning-dim);
    color: var(--warning);
    border: 1px solid rgba(245,166,35,0.3);
}
.status-badge.unverified {
    background: var(--danger-dim);
    color: var(--danger);
    border: 1px solid rgba(255,77,109,0.3);
}

/* Claim flag */
.claim-flag {
    background: var(--danger-dim);
    border-left: 3px solid var(--danger);
    border-radius: 0 6px 6px 0;
    padding: 12px 16px;
    margin: 8px 0;
    font-size: 0.82rem;
    color: #ff8fa3;
    font-family: var(--font-body);
    line-height: 1.5;
}
.claim-flag .flag-label {
    font-size: 0.62rem;
    font-family: var(--font-mono);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--danger);
    margin-bottom: 4px;
    display: block;
}

/* Evidence card */
.evidence-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 20px 22px;
    margin-bottom: 12px;
}
.evidence-card .ev-source {
    font-size: 0.65rem;
    font-family: var(--font-mono);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.evidence-card .ev-source::before {
    content: '';
    display: block;
    width: 20px; height: 1px;
    background: var(--accent);
}
.evidence-card .ev-content {
    font-size: 0.85rem;
    color: var(--text-secondary);
    line-height: 1.7;
}

/* Trace card */
.trace-step {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 20px 22px;
    margin-bottom: 10px;
    display: flex;
    gap: 18px;
    align-items: flex-start;
}
.trace-step .ts-icon {
    width: 36px; height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.9rem;
    flex-shrink: 0;
    margin-top: 2px;
}
.ts-success .ts-icon { background: rgba(0,212,170,0.12); }
.ts-warning .ts-icon { background: var(--warning-dim); }
.ts-failed .ts-icon { background: var(--danger-dim); }
.ts-running .ts-icon { background: rgba(99,179,237,0.12); }

.trace-step .ts-body { flex: 1; }
.trace-step .ts-name {
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 3px;
}
.trace-step .ts-summary {
    font-size: 0.78rem;
    color: var(--text-secondary);
    line-height: 1.5;
}
.trace-step .ts-time {
    font-size: 0.68rem;
    font-family: var(--font-mono);
    color: var(--text-muted);
    flex-shrink: 0;
    margin-top: 4px;
}

/* Stat mini-card for eval */
.eval-stat {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 20px;
    text-align: center;
}
.eval-stat .es-label {
    font-size: 0.62rem;
    font-family: var(--font-mono);
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 8px;
}
.eval-stat .es-value {
    font-family: var(--font-display);
    font-size: 1.8rem;
    letter-spacing: -0.03em;
    color: var(--text-primary);
}

/* Advice block */
.advice-block {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 24px 26px;
    margin-top: 4px;
}
.advice-block .advice-label {
    font-size: 0.62rem;
    font-family: var(--font-mono);
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.advice-block .advice-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border-bright);
}
.advice-block .advice-text {
    font-size: 0.9rem;
    line-height: 1.5;
    color: var(--text-secondary);
    white-space: pre-wrap;
}
.advice-block .advice-text p {
    margin: 0 0 6px 0;
}
.advice-block .advice-text br {
    display: block;
    content: '';
    margin-top: 4px;
}
.advice-block .advice-text ol,
.advice-block .advice-text ul {
    margin: 4px 0 4px 18px;
    padding: 0;
}
.advice-block .advice-text li {
    margin-bottom: 4px;
    line-height: 1.5;
}
.section-header {
    font-size: 0.65rem;
    font-family: var(--font-mono);
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 12px;
}
.section-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border-bright); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

/* Hide Streamlit defaults */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 0 !important; max-width: 1100px !important; }
</style>
""", unsafe_allow_html=True)

# Helper to convert basic markdown to HTML for the advice display
def md_to_html(text):
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # Numbered list items: lines starting with "1. ", "2. " etc.
    text = re.sub(r'^(\d+\.\s)', r'<br>\1', text, flags=re.MULTILINE)
    # Replace double newlines with a single break (no giant paragraph gaps)
    text = re.sub(r'\n{2,}', '<br>', text)
    # Single newlines
    text = text.replace('\n', '<br>')
    return text

# ── API Endpoint ──────────────────────────────────────────
API_URL = "http://127.0.0.1:8000/analyze"

# ── SIDEBAR ───────────────────────────────────────────────
st.sidebar.markdown("""
<div class="sidebar-brand">
  <span class="brand-icon">🫀</span>
  <div class="brand-name">CardioSense AI</div>
  <div class="brand-tagline">Agentic Cardiovascular Diagnostics</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown('<div class="input-section-label">Patient Vitals</div>', unsafe_allow_html=True)

age         = st.sidebar.number_input("Age (years)", min_value=1, max_value=120, value=45)
sex         = st.sidebar.selectbox("Sex", options=["Male", "Female"])
bp          = st.sidebar.number_input("Resting Blood Pressure (mmHg)", min_value=70, max_value=250, value=120)
cholesterol = st.sidebar.number_input("Cholesterol (mg/dL)", min_value=100, max_value=400, value=200)

st.sidebar.markdown('<div class="input-section-label">Symptoms</div>', unsafe_allow_html=True)

chest_pain_label = st.sidebar.selectbox(
    "How would you describe your chest discomfort?",
    options=[
        "Sharp, squeezing pain — especially during exertion",
        "Chest discomfort that doesn't follow a clear pattern",
        "Chest tightness or pressure, but not typical heart pain",
        "No chest pain or discomfort at all"
    ]
)
fasting_glucose     = st.sidebar.number_input("Fasting Blood Sugar (mg/dL)", min_value=50, max_value=500, value=90,
    help="Your blood sugar after not eating for 8+ hours. Normal is below 100 mg/dL.")
exercise_chest_pain = st.sidebar.checkbox("Chest pain or tightness when exercising or walking fast?", value=False)

# Convert to model values
sex_val   = 1 if sex == "Male" else 0
cp_map    = {
    "Sharp, squeezing pain — especially during exertion": 1,
    "Chest discomfort that doesn't follow a clear pattern": 2,
    "Chest tightness or pressure, but not typical heart pain": 3,
    "No chest pain or discomfort at all": 4
}
cp_val    = cp_map[chest_pain_label]
fbs_val   = 1 if fasting_glucose > 120 else 0
exang_val = 1 if exercise_chest_pain else 0

st.sidebar.markdown("<br>", unsafe_allow_html=True)

if st.sidebar.button("Run Analysis", use_container_width=True):
    with st.spinner("Agentic pipeline running…"):
        payload = {
            "age": age, "sex": sex_val, "chest_pain": cp_val,
            "bp": bp, "cholesterol": cholesterol,
            "high_blood_sugar": fbs_val, "exercise_chest_pain": exang_val
        }

        try:
            response = requests.post(API_URL, json=payload)
            if response.status_code == 200:
                data = response.json()
                st.session_state["result"] = data
                # Reset typing animation and chat history for new analysis
                st.session_state.pop("animated_advice", None)
                st.session_state["chat_history"] = []
            else:
                st.error(f"API error: {response.text}")
        except requests.exceptions.ConnectionError:
            st.error("Backend unreachable. Start FastAPI on port 8000 first.")

st.sidebar.markdown("""
<div style="margin-top:24px;padding:16px 20px;border-top:1px solid #1e2a3a;text-align:center;">
  <div style="font-size:0.62rem;color:#3d4f66;font-family:'DM Mono',monospace;line-height:1.6;">
    ML &middot; RAG &middot; LLM<br>
    Explainable AI Pipeline
  </div>
</div>
""", unsafe_allow_html=True)


# ── RESULTS ───────────────────────────────────────────────
if "result" in st.session_state:
    res = st.session_state["result"]

    if "error" in res:
        st.error(res["error"])
    else:
        tab1, tab2, tab3 = st.tabs(["Results", "Evidence", "Agent Trace"])

        pred           = res["prediction"]["prediction"]
        conf           = res["prediction"]["confidence"]
        adjusted_label = res["prediction"].get("adjusted_label", "High Risk" if pred == 1 else "Low Risk")
        ml_label       = res["prediction"].get("ml_label", adjusted_label)

        risk_text = adjusted_label
        risk_cls  = {"High Risk": "high-risk", "Moderate Risk": "moderate-risk", "Low Risk": "low-risk"}.get(adjusted_label, "low-risk")
        risk_icon = {"High Risk": "⚠", "Moderate Risk": "~", "Low Risk": "✓"}.get(adjusted_label, "✓")

        # ── TAB 1: RESULTS ──────────────────────────────
        with tab1:
            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown(f"""
                <div class="risk-panel {risk_cls}">
                  <div class="risk-label">Cardiovascular Risk</div>
                  <div class="risk-value">{risk_icon} {risk_text}</div>
                  <div class="risk-conf">ML confidence: {conf:.1%} &nbsp;|&nbsp; ML base: {ml_label}</div>
                  <div class="conf-bar-wrap">
                    <div class="conf-bar-bg">
                      <div class="conf-bar-fill" style="width:{conf*100:.1f}%"></div>
                    </div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

            # Clinical Flags
            flags = res.get("clinical_flags", [])
            if flags:
                flag_colors = {"danger": "#ff4b6e", "warning": "#f59e0b", "info": "#38bdf8"}
                flag_icons  = {"danger": "🚨", "warning": "⚠️", "info": "ℹ️"}
                flags_html  = ""
                for flag in flags:
                    color = flag_colors.get(flag["level"], "#f59e0b")
                    icon  = flag_icons.get(flag["level"], "⚠️")
                    flags_html += f"""
                    <div style="display:flex;align-items:flex-start;gap:10px;padding:10px 14px;
                                border-left:3px solid {color};background:rgba(255,255,255,0.03);
                                border-radius:6px;margin-bottom:8px;">
                      <span style="font-size:1rem;margin-top:2px">{icon}</span>
                      <span style="font-size:0.82rem;color:#c9d6e3;line-height:1.5;">{flag['text']}</span>
                    </div>"""
                st.markdown(f'<div style="margin-top:16px;margin-bottom:4px">{flags_html}</div>',
                            unsafe_allow_html=True)

            # AI Advice
            st.markdown('<div class="section-header" style="margin-top:24px">Generated AI Advice</div>', unsafe_allow_html=True)
            advice_placeholder = st.empty()
            
            if st.session_state.get("animated_advice") != res["advice"]:
                displayed_text = ""
                # Split by words for a slightly faster, smoother typing effect than character-by-character
                words = res["advice"].split(" ")
                for i, word in enumerate(words):
                    displayed_text += word + " "
                    # Convert markdown to HTML as we go
                    advice_placeholder.markdown(f"""
                    <div class="advice-block">
                      <div class="advice-label">Clinical Guidance</div>
                      <div class="advice-text">{md_to_html(displayed_text)}▌</div>
                    </div>
                    """, unsafe_allow_html=True)
                    time.sleep(0.05)
                st.session_state["animated_advice"] = res["advice"]

            # Final state without the cursor
            advice_placeholder.markdown(f"""
            <div class="advice-block">
              <div class="advice-label">Clinical Guidance</div>
              <div class="advice-text">{md_to_html(res["advice"])}</div>
            </div>
            """, unsafe_allow_html=True)

            # ── FOLLOW-UP CHAT ────────────────────────────────
            st.markdown('<div class="section-header" style="margin-top:32px">Ask a Follow-up Question</div>', unsafe_allow_html=True)

            if "chat_history" not in st.session_state:
                st.session_state["chat_history"] = []

            # Display past messages
            for msg in st.session_state["chat_history"]:
                with st.chat_message(msg["role"]):
                    st.markdown(md_to_html(msg["content"]), unsafe_allow_html=True)

            # Chat input
            if user_q := st.chat_input("Ask anything about your results…"):
                st.session_state["chat_history"].append({"role": "user", "content": user_q})
                with st.chat_message("user"):
                    st.markdown(user_q)

                clean_q = user_q.strip().lower().rstrip("!.?")
                if clean_q in ["thanks", "thank you", "ok", "okay", "thanks a lot", "thank you so much", "thx"]:
                    reply = "You are very welcome! I'm glad I could help. Remember to take things one day at a time, and don't hesitate to reach out if you have any more questions about your health and wellness journey. Take care!"
                    with st.chat_message("assistant"):
                        reply_placeholder = st.empty()
                        streamed = ""
                        for word in reply.split(" "):
                            streamed += word + " "
                            reply_placeholder.markdown(md_to_html(streamed) + "▌", unsafe_allow_html=True)
                            time.sleep(0.04)
                        reply_placeholder.markdown(md_to_html(reply), unsafe_allow_html=True)
                        st.session_state["chat_history"].append({"role": "assistant", "content": reply})
                else:
                    system_prompt = f"""You are CardioSense AI, a professional, objective, and empathetic clinical AI assistant. A user is asking a follow-up question.

=== PATIENT PROFILE ===
- Age: {age}, Sex: {sex}
- BP: {bp} mmHg, Cholesterol: {cholesterol} mg/dL
- Fasting Glucose: {fasting_glucose} mg/dL
- Physical discomfort notes: {chest_pain_label}
- Activity discomfort: {'Yes' if exercise_chest_pain else 'No'}

=== PREVIOUS ADVICE PROVIDED ===
{res['advice']}

=== TONE & STYLE RULES ===
1. Tone: Highly professional, objective, formal, and respectful.
2. Vocabulary: Use formal language. Keep the explanation precise, patient-focused, and practical.
3. Content: Focus purely on healthy living recommendations, stress management, and nutrition. Remind the user to consult their healthcare provider for medical diagnostics or symptoms."""

                    with st.chat_message("assistant"):
                        reply_placeholder = st.empty()
                        # Show thinking indicator immediately
                        reply_placeholder.markdown(
                            '<span style="color:#3d4f66;font-family:\'DM Mono\',monospace;font-size:0.82rem;">'
                            '⬤ &nbsp;⬤ &nbsp;⬤ &nbsp; Thinking…</span>',
                            unsafe_allow_html=True
                        )
                        try:
                            import ollama as _ollama
                            reply_resp = _ollama.chat(
                                model='llama3.2:1b',
                                messages=[
                                    {'role': 'system', 'content': system_prompt},
                                    {'role': 'user', 'content': user_q}
                                ]
                            )
                            reply = reply_resp['message']['content']
                            # Stream reply word by word
                            streamed = ""
                            for word in reply.split(" "):
                                streamed += word + " "
                                reply_placeholder.markdown(md_to_html(streamed) + "▌", unsafe_allow_html=True)
                                time.sleep(0.04)
                            reply_placeholder.markdown(md_to_html(reply), unsafe_allow_html=True)
                            st.session_state["chat_history"].append({"role": "assistant", "content": reply})
                        except Exception as e:
                            reply_placeholder.error(f"Could not get response: {e}")

        # ── TAB 2: EVIDENCE ─────────────────────────────
        with tab2:
            evidence = res["evidence"]
            st.markdown('<div class="section-header">Retrieved Medical Evidence</div>', unsafe_allow_html=True)
            if not evidence:
                st.warning("No relevant evidence retrieved from knowledge base.")
            else:
                for idx, ev in enumerate(evidence):
                    st.markdown(f"""
                    <div class="evidence-card">
                      <div class="ev-source">{ev['source']} — Chunk {idx+1}</div>
                      <div class="ev-content">{ev['content']}</div>
                    </div>
                    """, unsafe_allow_html=True)

        # ── TAB 3: AGENT TRACE ──────────────────────────
        with tab3:
            trace = res["trace"]
            st.markdown('<div class="section-header">Step-by-Step Execution</div>', unsafe_allow_html=True)

            icon_map   = {"success": "✓", "warning": "⚑", "failed": "✕", "running": "◎"}
            class_map  = {"success": "ts-success", "warning": "ts-warning",
                          "failed": "ts-failed",  "running": "ts-running"}

            for step in trace:
                status_lc  = step["status"].lower()
                icon       = icon_map.get(status_lc, "·")
                cls        = class_map.get(status_lc, "ts-running")

                st.markdown(f"""
                <div class="trace-step {cls}">
                  <div class="ts-icon">{icon}</div>
                  <div class="ts-body">
                    <div class="ts-name">{step['step']}</div>
                    <div class="ts-summary">{step['summary']}</div>
                  </div>
                  <div class="ts-time">{step['timestamp']}</div>
                </div>
                """, unsafe_allow_html=True)

                if step.get("details"):
                    with st.expander("View payload"):
                        st.json(step["details"])



else:
    # ── EMPTY STATE ─────────────────────────────────────
    st.markdown("""
    <div style="text-align:center;padding:80px 40px;">
      <div style="font-size:3rem;margin-bottom:20px;opacity:0.3">🫀</div>
      <div style="font-family:'DM Serif Display',serif;font-size:1.6rem;color:#3d4f66;letter-spacing:-0.02em;margin-bottom:12px">
        No analysis running yet
      </div>
      <div style="font-size:0.82rem;color:#2a3a52;font-family:'DM Mono',monospace;letter-spacing:0.08em">
        Enter patient vitals in the sidebar and click Run Analysis
      </div>
    </div>
    """, unsafe_allow_html=True)