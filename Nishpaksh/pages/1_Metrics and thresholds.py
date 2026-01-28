# pages/4_Metrics_and_Thresholds.py
"""
Standalone Metrics & Thresholds page 
- User selects problem type (classification/regression/clustering/recommendation)
- Metrics selection is a checkbox grid (with Select all / Clear selection)
- Threshold numeric inputs appear inline when a metric is checked
- Optional notes removed (per request)
- Thresholds saved to st.session_state['thresholds']
"""

import streamlit as st
import pandas as pd
import math

st.set_page_config(layout="centered", page_title="Metrics & Thresholds")

st.title("Model type and group fairness metrics")

st.markdown(
    "Choose the problem type, then tick the group/fairness metrics you want to configure. "
    "When a metric is checked, its threshold input appears inline. "
    
)

st.markdown(
    """
    <style>
    /* ======================================================
       IMPORTS & ROOT VARIABLES
       ====================================================== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --primary: #2563eb;
        --primary-dark: #1e40af;
        --primary-light: #3b82f6;
        --accent: #0ea5e9;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        
        --bg-app: #f8fafc;
        --bg-card: #ffffff;
        --bg-section: #f1f5f9;
        --bg-hover: #e0f2fe;
        
        --border: #e2e8f0;
        --border-strong: #cbd5e1;
        --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        
        --text-primary: #0f172a;
        --text-secondary: #475569;
        --text-muted: #64748b;
        --text-light: #94a3b8;
    }

    /* ======================================================
       GLOBAL BASE
       ====================================================== */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
    }

    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e0f2fe 100%);
        color: var(--text-primary);
    }

    html, body {
        font-size: 16px;
        line-height: 1.6;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    /* ======================================================
       TYPOGRAPHY
       ====================================================== */
    h1 {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.025em !important;
        margin-bottom: 0.5rem !important;
        color: var(--text-primary) !important;
        background: linear-gradient(135deg, #2563eb 0%, #0ea5e9 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    h1::after {
        content: "";
        display: block;
        width: 80px;
        height: 4px;
        background: linear-gradient(90deg, var(--primary) 0%, var(--accent) 100%);
        margin-top: 12px;
        border-radius: 2px;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.3);
    }

    h2 {
        font-size: 1.75rem !important;
        font-weight: 700 !important;
        margin-top: 2.5rem !important;
        margin-bottom: 1rem !important;
        color: var(--text-primary) !important;
        padding-left: 1rem !important;
        border-left: 5px solid var(--primary) !important;
        background: linear-gradient(90deg, rgba(37, 99, 235, 0.05) 0%, transparent 100%);
        padding: 0.75rem 0 0.75rem 1rem !important;
        border-radius: 0 8px 8px 0;
    }

    h3 {
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        margin-bottom: 0.75rem !important;
    }

    p, .stMarkdown p {
        color: var(--text-secondary) !important;
        font-size: 1rem !important;
        line-height: 1.7 !important;
        max-width: 75ch;
    }

    .stCaption {
        color: var(--text-muted) !important;
        font-size: 0.9rem !important;
    }

    /* ======================================================
       SURVEY NAVIGATION SIDEBAR
       ====================================================== */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(button) {
        background: var(--bg-card) !important;
        border: 2px solid var(--border) !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        margin-bottom: 1.5rem !important;
        box-shadow: var(--shadow-md) !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] h3 {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        margin-bottom: 1rem !important;
        padding-bottom: 0.75rem !important;
        border-bottom: 2px solid var(--border) !important;
    }

    /* Navigation buttons */
    div[data-testid="stVerticalBlockBorderWrapper"] button {
        width: 100% !important;
        text-align: left !important;
        padding: 0.75rem 1rem !important;
        margin-bottom: 0.5rem !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        background: var(--bg-section) !important;
        color: var(--text-secondary) !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] button:hover {
        background: var(--bg-hover) !important;
        border-color: var(--primary) !important;
        color: var(--primary) !important;
        transform: translateX(4px);
        box-shadow: var(--shadow-sm) !important;
    }

    /* ======================================================
       MAIN CONTENT CARDS
       ====================================================== */
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 16px !important;
        padding: 2rem !important;
        margin-bottom: 1.5rem !important;
        box-shadow: var(--shadow-md) !important;
        transition: all 0.3s ease;
    }

    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        box-shadow: var(--shadow-lg) !important;
        border-color: var(--border-strong) !important;
    }

    /* ======================================================
       SURVEY QUESTIONS (EXPANDERS) - KEY IMPROVEMENTS
       ====================================================== */
    div[data-testid="stExpander"] {
        margin-bottom: 1.25rem !important;
        border-radius: 12px !important;
        overflow: hidden;
        box-shadow: var(--shadow-sm) !important;
        transition: all 0.3s ease;
    }

    div[data-testid="stExpander"]:hover {
        box-shadow: var(--shadow-md) !important;
    }

    /* Question headers */
    div[data-testid="stExpander"] > details > summary {
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%) !important;
        padding: 1.25rem 1.5rem !important;
        border-radius: 12px !important;
        border: 2px solid var(--border) !important;
        border-left: 6px solid var(--primary) !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        line-height: 1.6 !important;
        min-height: 60px;
        display: flex;
        align-items: center;
    }

    div[data-testid="stExpander"] > details > summary:hover {
        background: linear-gradient(135deg, var(--bg-hover) 0%, #e0f2fe 100%) !important;
        border-left-color: var(--accent) !important;
        transform: translateX(4px);
        box-shadow: var(--shadow-sm) !important;
    }

    div[data-testid="stExpander"] > details[open] > summary {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%) !important;
        color: white !important;
        border-color: var(--primary-dark) !important;
        border-left-color: var(--accent) !important;
        border-radius: 12px 12px 0 0 !important;
    }

    /* Question content area */
    div[data-testid="stExpander"] > details > div {
        background-color: var(--bg-card) !important;
        padding: 1.5rem 1.75rem !important;
        border-left: 6px solid var(--border-strong) !important;
        border-right: 2px solid var(--border) !important;
        border-bottom: 2px solid var(--border) !important;
        border-radius: 0 0 12px 12px !important;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.02);
    }

    /* ======================================================
       FORM INPUTS & CONTROLS
       ====================================================== */
    label {
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        font-size: 0.95rem !important;
        margin-bottom: 0.5rem !important;
        display: block !important;
    }

    /* Text inputs and textareas */
    textarea, 
    input[type="text"],
    input[type="number"] {
        font-size: 1rem !important;
        line-height: 1.6 !important;
        border-radius: 8px !important;
        padding: 0.75rem 1rem !important;
        border: 2px solid var(--border) !important;
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }

    textarea:focus,
    input[type="text"]:focus,
    input[type="number"]:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
        outline: none !important;
    }

    /* Radio buttons and checkboxes */
    div[data-testid="stRadio"] > div,
    div[data-testid="stCheckbox"] > div {
        background: var(--bg-section) !important;
        padding: 1rem !important;
        border-radius: 8px !important;
        border: 1px solid var(--border) !important;
        margin-bottom: 0.5rem !important;
        transition: all 0.2s ease !important;
    }

    div[data-testid="stRadio"] > div:hover,
    div[data-testid="stCheckbox"] > div:hover {
        background: var(--bg-hover) !important;
        border-color: var(--primary) !important;
    }

    /* Radio button labels */
    div[data-testid="stRadio"] label {
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        padding: 0.5rem 0 !important;
    }

    /* ======================================================
       BUTTONS
       ====================================================== */
    button[kind="primary"] {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        border-radius: 10px !important;
        padding: 0.875rem 2rem !important;
        border: none !important;
        box-shadow: var(--shadow-md) !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    button[kind="primary"]:hover {
        background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary) 100%) !important;
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg) !important;
    }

    button[kind="secondary"] {
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
        border: 2px solid var(--border) !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        padding: 0.875rem 2rem !important;
        transition: all 0.2s ease !important;
    }

    button[kind="secondary"]:hover {
        border-color: var(--primary) !important;
        color: var(--primary) !important;
        background: var(--bg-hover) !important;
    }

    /* ======================================================
       METRICS & INFO BOXES
       ====================================================== */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-section) 100%) !important;
        padding: 1.5rem !important;
        border-radius: 12px !important;
        border: 2px solid var(--border) !important;
        box-shadow: var(--shadow-md) !important;
    }

    div[data-testid="stMetric"] label {
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        color: var(--text-secondary) !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: var(--primary) !important;
    }

    /* Info/Success/Warning boxes */
    div[data-testid="stAlert"] {
        border-radius: 12px !important;
        border: none !important;
        box-shadow: var(--shadow-sm) !important;
        padding: 1.25rem 1.5rem !important;
    }

    div[data-testid="stAlert"][data-baseweb="notification"][kind="info"] {
        background: linear-gradient(135deg, #dbeafe 0%, #e0f2fe 100%) !important;
        border-left: 5px solid var(--accent) !important;
    }

    div[data-testid="stAlert"][data-baseweb="notification"][kind="success"] {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%) !important;
        border-left: 5px solid var(--success) !important;
    }

    div[data-testid="stAlert"][data-baseweb="notification"][kind="warning"] {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%) !important;
        border-left: 5px solid var(--warning) !important;
    }

    div[data-testid="stAlert"][data-baseweb="notification"][kind="error"] {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%) !important;
        border-left: 5px solid var(--danger) !important;
    }

    /* ======================================================
       SIDEBAR
       ====================================================== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%) !important;
        border-right: 2px solid var(--border) !important;
        box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: var(--text-primary) !important;
        padding-left: 0.5rem !important;
    }

    section[data-testid="stSidebar"] li {
        border-radius: 8px !important;
        margin-bottom: 0.25rem !important;
        transition: all 0.2s ease !important;
    }

    section[data-testid="stSidebar"] li:has(a[aria-current="page"]) {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%) !important;
        box-shadow: var(--shadow-sm) !important;
    }

    section[data-testid="stSidebar"] li:has(a[aria-current="page"]) a {
        color: white !important;
        font-weight: 600 !important;
    }

    section[data-testid="stSidebar"] li:hover {
        background: var(--bg-hover) !important;
    }

    /* ======================================================
       PROGRESS & INDICATORS
       ====================================================== */
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--primary) 0%, var(--accent) 100%) !important;
        border-radius: 10px !important;
        height: 8px !important;
    }

    /* ======================================================
       DIVIDERS
       ====================================================== */
    hr {
        border: none !important;
        border-top: 2px solid var(--border) !important;
        margin: 2.5rem 0 !important;
        opacity: 0.6;
    }

    /* ======================================================
       SCROLLBAR STYLING
       ====================================================== */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }

    ::-webkit-scrollbar-track {
        background: var(--bg-section);
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, var(--primary) 0%, var(--accent) 100%);
        border-radius: 10px;
        border: 2px solid var(--bg-section);
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, var(--primary-dark) 0%, var(--primary) 100%);
    }

    /* ======================================================
       RESPONSIVE IMPROVEMENTS
       ====================================================== */
    @media (max-width: 768px) {
        h1 {
            font-size: 2rem !important;
        }
        
        h2 {
            font-size: 1.5rem !important;
        }
        
        div[data-testid="stExpander"] > details > summary {
            font-size: 0.95rem !important;
            padding: 1rem 1.25rem !important;
        }
    }

    /* ======================================================
       ANIMATIONS
       ====================================================== */
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    div[data-testid="stVerticalBlock"] > div {
        animation: slideIn 0.3s ease-out;
    }

    /* ======================================================
       FOCUS STATES
       ====================================================== */
    button:focus-visible,
    input:focus-visible,
    textarea:focus-visible {
        outline: 3px solid rgba(37, 99, 235, 0.5) !important;
        outline-offset: 2px !important;
    }
/* ======================================================
       HORIZONTAL RADIO BUTTONS - CLEAN & SPACIOUS
       ====================================================== */
    /* Container for horizontal radio group */
    div[role="radiogroup"][data-baseweb="radio"] {
        display: flex !important;
        flex-direction: row !important;
        gap: 1rem !important;
        flex-wrap: wrap !important;
        margin: 1rem 0 !important;
    }

    /* Individual radio button cards */
    div[role="radiogroup"] > label {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        background: var(--bg-card) !important;
        padding: 1rem 1.75rem !important;
        border-radius: 12px !important;
        border: 2px solid var(--border) !important;
        margin: 0 !important;
        cursor: pointer !important;
        transition: all 0.25s ease !important;
        white-space: nowrap !important;
        min-width: 180px !important;
        justify-content: center !important;
        box-shadow: var(--shadow-sm) !important;
    }

    div[role="radiogroup"] > label:hover {
        background: var(--bg-hover) !important;
        border-color: var(--primary-light) !important;
        transform: translateY(-3px);
        box-shadow: var(--shadow-md) !important;
    }

    /* Selected radio button state */
    div[role="radiogroup"] > label:has(input:checked) {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%) !important;
        border-color: var(--primary-dark) !important;
        color: white !important;
        font-weight: 600 !important;
        box-shadow: var(--shadow-md) !important;
        transform: translateY(-2px);
    }

    div[role="radiogroup"] > label:has(input:checked):hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-lg) !important;
    }

    /* Radio button text */
    div[role="radiogroup"] > label > div:last-child {
        font-size: 1rem !important;
        font-weight: 500 !important;
        margin-left: 0.75rem !important;
        letter-spacing: 0.01em !important;
    }

    /* Selected state text color */
    div[role="radiogroup"] > label:has(input:checked) > div:last-child {
        color: white !important;
        font-weight: 600 !important;
    }

    /* Radio button circle indicator - make it larger and cleaner */
    div[role="radiogroup"] > label > div:first-child {
        flex-shrink: 0 !important;
        width: 20px !important;
        height: 20px !important;
    }

    /* Hide the actual radio input visually but keep it accessible */
    div[role="radiogroup"] input[type="radio"] {
        width: 20px !important;
        height: 20px !important;
    }

    /* Fix horizontal block container */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        gap: 0 !important;
        flex-wrap: wrap !important;
        width: 100% !important;
    }

    div[data-testid="stHorizontalBlock"] > div {
        flex: 0 1 auto !important;
        min-width: fit-content !important;
    }

    /* Question label styling */
    div[data-testid="stRadio"] > label {
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        margin-bottom: 1rem !important;
        display: block !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Problem selection
problem = st.radio(
    "Which kind of problem is this model solving?",
    ("classification", "regression", "clustering", "recommendation"),
    index=0,
    horizontal=True
)

st.markdown(f"**Problem type:** `{problem}`")

# Group fairness metrics (kept same for simplicity)
GROUP_METRICS = [
    "Statistical Parity Difference",
    "Disparate Impact",
    "Average Odds Difference",
    "Equal Opportunity Difference",
    "Error Rate Difference",
    "Calibration Difference (global)"
]

# sensible defaults
DEFAULTS = {
    "Statistical Parity Difference": 0.10,
    "Disparate Impact": 0.80,
    "Average Odds Difference": 0.10,
    "Equal Opportunity Difference": 0.10,
    "Error Rate Difference": 0.10,
    "Calibration Difference (global)": 0.05,
}

# Load existing thresholds if present
saved_thresholds = st.session_state.get("thresholds", {}) if "thresholds" in st.session_state else {}

# Keep an internal selection state so Select all / Clear selection work smoothly
if "metric_selection" not in st.session_state or st.session_state.get("_metric_selection_problem") != problem:
    # initialize selection: checked if present in saved thresholds OR default to checked
    st.session_state["metric_selection"] = {m: (m in saved_thresholds or True) for m in GROUP_METRICS}
    st.session_state["_metric_selection_problem"] = problem

# header controls: select all / clear all
col_a, col_b, _ = st.columns([1, 1, 6])
with col_a:
    if st.button("Select all metrics"):
        for m in GROUP_METRICS:
            st.session_state["metric_selection"][m] = True
with col_b:
    if st.button("Clear all"):
        for m in GROUP_METRICS:
            st.session_state["metric_selection"][m] = False

st.markdown("### Choose group/fairness metrics to configure")

# Render checkboxes in two columns for compactness
ncols = 2
cols = st.columns(ncols)
for i, m in enumerate(GROUP_METRICS):
    col = cols[i % ncols]
    key_chk = f"chk_{problem}_{m}"
    # default checked state from session state
    default_checked = st.session_state["metric_selection"].get(m, True)
    checked = col.checkbox(label=m, value=default_checked, key=key_chk)
    # persist into metric_selection map so select-all/clear-all reflect current state
    st.session_state["metric_selection"][m] = checked

    # inline threshold input appears immediately below the checkbox (indented)
    if checked:
        # Use a small number_input; keep format flexible for different metric types
        key_th = f"th_{problem}_{m}"
        # decide initial value: saved thresholds -> saved, else DEFAULTS
        init_val = saved_thresholds.get(m, {}).get("value", DEFAULTS.get(m, 0.0))
        # If init_val might be non-finite, fallback
        try:
            init_val = float(init_val)
            if math.isnan(init_val) or math.isinf(init_val):
                init_val = float(DEFAULTS.get(m, 0.0))
        except Exception:
            init_val = float(DEFAULTS.get(m, 0.0))
        # layout: place threshold input immediately after the checkbox
        col.number_input(f"Threshold for {m}", value=init_val, step=0.01, format="%.4f", key=key_th)

st.markdown("---")
# Build thresholds dict from current checkbox states + inputs
thresholds = {}
for m in GROUP_METRICS:
    if st.session_state["metric_selection"].get(m, False):
        key_th = f"th_{problem}_{m}"
        # number_input always exists as a widget when metric is checked; try to read. If missing, fallback.
        val = st.session_state.get(key_th, DEFAULTS.get(m, 0.0))
        thresholds[m] = {"value": float(val), "problem": problem}

col1, col2 = st.columns([1,1])
with col1:
    if st.button("Save thresholds to session"):
        st.session_state["thresholds"] = thresholds
        st.success("Saved thresholds to session.")
with col2:
    if st.button("Clear thresholds from session"):
        if "thresholds" in st.session_state:
            del st.session_state["thresholds"]
        st.success("Cleared thresholds from session.")



