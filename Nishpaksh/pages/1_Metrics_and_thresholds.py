# pages/4_Metrics_and_Thresholds.py
"""

- User selects problem type (classification/regression/clustering/recommendation)
- Metrics selection is a checkbox grid (with Select all / Clear selection)
- Threshold numeric inputs appear inline when a metric is checked
- Optional notes removed (per request)
- Thresholds saved to st.session_state['thresholds'] 
"""

import streamlit as st
import pandas as pd
import math

st.set_page_config(layout="wide", page_title="Metrics & Thresholds")

st.title("Model type and group fairness metrics")

st.markdown(
    "Choose the problem type, then tick the group/fairness metrics you want to configure. "
    "When a metric is checked, its threshold input appears inline. "
    
)

st.markdown(
    """
    <style>
    /* Import font */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    
    /* Base typography */
    .stApp {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    
    /* Gradient headings */
    h1, h2, h3 {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
        letter-spacing: -0.02em;
    }
    
    /* Navigation sidebar - boxed style */
    [data-testid="stSidebarNav"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        margin: 1rem 0.5rem !important;
    }
    
    [data-testid="stSidebarNav"] a {
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
        padding: 0.75rem 1rem !important;
        margin-bottom: 0.5rem !important;
        transition: all 0.2s ease !important;
    }
    
    [data-testid="stSidebarNav"] a:hover {
        border-color: #60a5fa !important;
        background-color: rgba(96, 165, 250, 0.1) !important;
        transform: translateX(4px);
    }
    
    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background: linear-gradient(135deg, #2563eb 0%, #0ea5e9 100%) !important;
        border-color: transparent !important;
    }
    
    /* Content cards - smaller padding */
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 16px !important;
        padding: 1.5rem !important;
        margin-bottom: 1rem !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Radio button containers */
    div[data-testid="stRadio"] > div {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }
    
    /* Primary buttons */
    button[kind="primary"] {
        background: linear-gradient(135deg, #2563eb 0%, #0ea5e9 100%) !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 700 !important;
    }
    
    /* File uploader */
    div[data-testid="stFileUploader"] {
        border-radius: 12px !important;
        padding: 1.5rem !important;
    }
    
    /* Metrics */
    div[data-testid="stMetric"] {
        border-radius: 12px !important;
        padding: 1rem !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Logo positioning */
    .nishpaksh-logo {
        position: fixed;
        top: 16px;
        left: 16px;
        width: 120px;
        z-index: 9999;
    }
    
    [data-testid="stSidebarNav"] {
        margin-top: 120px;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #2563eb 0%, #0ea5e9 100%);
        border-radius: 10px;
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

# --------------------------------------------------
# Guard + reconstruct protected attributes (AUTHORITATIVE)
# --------------------------------------------------
num_protected = st.session_state.get("num_protected_attrs")

if not isinstance(num_protected, int) or num_protected < 1:
    st.warning("Protected attributes not configured on Home page.")
    st.stop()

protected_attrs = []

for i in range(1, num_protected + 1):
    attr_key = f"protected_attribute_{i}"
    priv_key = f"privileged_class_{i}"

    attr = st.session_state.get(attr_key)
    priv = st.session_state.get(priv_key)

    if not isinstance(attr, str) or not isinstance(priv, str):
        st.warning(
            f"Protected attribute {i} or its privileged class is missing."
        )
        st.stop()

    protected_attrs.append(
        {
            "attribute": attr,
            "privileged_class": priv,
        }
    )

# --------------------------------------------------
# Ground truth check (AUTHORITATIVE)
# --------------------------------------------------
ground_truth = st.session_state.get("ground_truth")

if not isinstance(ground_truth, str) or ground_truth == "":
    st.warning("Ground truth not configured on Home page.")
    st.stop()

# --------------------------------------------------
# Fairness metrics (UNCHANGED)
# --------------------------------------------------
GROUP_METRICS = [
    "Statistical Parity Difference",
    "Disparate Impact",
    "Average Odds Difference",
    "Equal Opportunity Difference",
    "Error Rate Difference",
    "Calibration Difference (global)",
]

DEFAULTS = {
    "Statistical Parity Difference": 0.10,
    "Disparate Impact": 0.20,
    "Average Odds Difference": 0.10,
    "Equal Opportunity Difference": 0.10,
    "Error Rate Difference": 0.10,
    "Calibration Difference (global)": 0.05,
}

# --------------------------------------------------
# Initialize thresholds store (AUTHORITATIVE)
# --------------------------------------------------
if "thresholds" not in st.session_state:
    st.session_state["thresholds"] = {}

# --------------------------------------------------
# Metric selection PER protected attribute (ZOOM-SAFE)
# --------------------------------------------------
for p in protected_attrs:
    attr = p["attribute"]

    st.markdown(f"## Metrics & thresholds for **{attr}**")

    if attr not in st.session_state["thresholds"]:
        st.session_state["thresholds"][attr] = {}

    attr_thresholds = st.session_state["thresholds"][attr]

    sel_key = f"metric_selection_{attr}"
    prob_key = f"_metric_problem_{attr}"

    if sel_key not in st.session_state or st.session_state.get(prob_key) != problem:
        st.session_state[sel_key] = {m: True for m in GROUP_METRICS}
        st.session_state[prob_key] = problem

    # -------------------------------
    # Select / Clear buttons (2-col)
    # -------------------------------
    b1, b2 = st.columns(2)

    with b1:
        if st.button(
            "Select all",
            key=f"select_all_{attr}",
            use_container_width=True,
        ):
            for m in GROUP_METRICS:
                st.session_state[sel_key][m] = True

    with b2:
        if st.button(
            "Clear all",
            key=f"clear_all_{attr}",
            use_container_width=True,
        ):
            for m in GROUP_METRICS:
                st.session_state[sel_key][m] = False
            attr_thresholds.clear()

    st.markdown("### Choose fairness metrics")

    # -------------------------------
    # Metrics grid (2 × 3, HARD SAFE)
    # Each metric in its OWN container
    # -------------------------------
    col_left, col_right = st.columns(2, gap="large")
    metric_cols = [col_left, col_right]

    for idx_m, metric in enumerate(GROUP_METRICS):
        target_col = metric_cols[idx_m // 3]

        with target_col:
            with st.container():  # 🔒 CRITICAL: isolates CSS
                chk_key = f"chk_{attr}_{problem}_{metric}"
                th_key = f"th_{attr}_{problem}_{metric}"

                checked = st.checkbox(
                    metric,
                    value=st.session_state[sel_key].get(metric, True),
                    key=chk_key,
                )

                st.session_state[sel_key][metric] = checked

                if checked:
                    if metric not in attr_thresholds:
                        attr_thresholds[metric] = {
                            "value": DEFAULTS[metric],
                            "problem": problem,
                        }

                    val = st.number_input(
                        "Threshold",
                        value=float(attr_thresholds[metric]["value"]),
                        step=0.01,
                        format="%.4f",
                        key=th_key,
                    )

                    attr_thresholds[metric] = {
                        "value": float(val),
                        "problem": problem,
                    }
                else:
                    attr_thresholds.pop(metric, None)

    st.markdown("---")

# --------------------------------------------------
# Final controls
# --------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    if st.button("Save thresholds"):
        st.success("Thresholds saved for all protected attributes.")

with c2:
    if st.button("Clear thresholds"):
        del st.session_state["thresholds"]
        st.success("All thresholds cleared.")
