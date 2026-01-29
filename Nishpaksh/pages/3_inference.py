# pages/3_Inference.py
# Inference & Fairness Evaluation 

import streamlit as st
import pandas as pd
import numpy as np


import hashlib

from utils.two_class_metrics import GroupMetrics, FairnessMetrics
from utils.viz_utils import (
    _as01,
    plot_bar_single_metric,
    plot_line_single_metric,
    plot_fairness_error_bars,
    plot_by_group_bars,
    plot_models_groups_heatmap,
    plot_disparity_in_performance,
    plot_group_error_panel,
    plot_fairness_accuracy_scatter,
)

# --------------------------------------------------
# Page setup (UNCHANGED)
# --------------------------------------------------
st.set_page_config(layout="wide")
st.title("Inference & Fairness Evaluation")
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
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# Preconditions
# --------------------------------------------------
data = st.session_state.get("uploaded_data")
label_col = st.session_state.get("ground_truth_col")
sensitive_col = st.session_state.get("sensitive_col")
privileged_value = st.session_state.get("privileged_value")

if not isinstance(data, pd.DataFrame) or data.empty:
    st.warning("No dataset available. Complete earlier steps first.")
    st.stop()

if None in (label_col, sensitive_col, privileged_value):
    st.error("Ground truth, sensitive attribute, and privileged group must be set.")
    st.stop()

# --------------------------------------------------
# Detect prediction columns
# --------------------------------------------------
pred_cols = [
    c for c in data.columns
    if c not in {label_col, sensitive_col}
    and set(pd.Series(data[c]).dropna().unique()).issubset({0, 1})
]

if not pred_cols:
    st.error("No prediction columns detected.")
    st.stop()

# --------------------------------------------------
# Positive class selectors (UNCHANGED)
# --------------------------------------------------
def _guess_positive(vals):
    for v in vals:
        if str(v).lower() in {"1", "true", "yes", "approved", "positive"}:
            return v
    return sorted(vals)[-1]

label_vals = data[label_col].astype(str).unique().tolist()
pred_vals = sorted({str(v) for c in pred_cols for v in data[c].dropna().unique()})

c1, c2 = st.columns(2)
POS_TRUE = c1.selectbox(
    "Positive class (ground truth)",
    label_vals,
    index=label_vals.index(_guess_positive(label_vals)),
)
POS_PRED = c2.selectbox(
    "Positive class (predictions)",
    pred_vals,
    index=pred_vals.index(_guess_positive(pred_vals)),
)

# --------------------------------------------------
# Deterministic computation fingerprint
# --------------------------------------------------
def make_compute_key():
    h = hashlib.sha256()
    h.update(str(label_col).encode())
    h.update(str(sensitive_col).encode())
    h.update(str(privileged_value).encode())
    h.update(str(POS_TRUE).encode())
    h.update(str(POS_PRED).encode())
    h.update(",".join(pred_cols).encode())
    h.update(str(data.shape).encode())
    return h.hexdigest()

compute_key = make_compute_key()

# --------------------------------------------------
# Heavy computation (PURE FUNCTION, NO CACHE)
# --------------------------------------------------
def compute_all_metrics(
    df, label_col, sensitive_col, pred_cols,
    privileged_value, pos_true, pos_pred, B=20
):
    y_true = _as01(df[label_col].values, positive=pos_true)
    sens_arr = df[sensitive_col].astype(str).values

    rows = []
    fairness_bootstrap = {}

    for col in pred_cols:
        y_pred = _as01(df[col].values, positive=pos_pred)

        perf = GroupMetrics(y_true, y_pred).get_all()
        fair = FairnessMetrics(
            y_true, y_pred, sens_arr,
            privileged_value=privileged_value
        ).get_all()

        rows.append({"Model": col, **perf, **fair})

        for m in fair.keys():
            fairness_bootstrap.setdefault(m, {})[col] = []
            for _ in range(B):
                idx = np.random.choice(len(y_true), len(y_true), replace=True)
                fb = FairnessMetrics(
                    y_true[idx], y_pred[idx], sens_arr[idx],
                    privileged_value=privileged_value
                ).get_all()
                fairness_bootstrap[m][col].append(fb.get(m))

    return pd.DataFrame(rows), fairness_bootstrap, y_true, sens_arr

# --------------------------------------------------
# Compute trigger (ARCHITECTURALLY FIXED)
# --------------------------------------------------
if st.button("Compute metrics"):
    with st.spinner("Computing metrics…"):
        results_df, fairness_bootstrap, y_true, sens_arr = compute_all_metrics(
            data, label_col, sensitive_col, pred_cols,
            privileged_value, POS_TRUE, POS_PRED
        )

        def safe_table(df, cols):
            keep = [c for c in cols if c in df.columns]
            return df[["Model"] + keep]

        PERFORMANCE_COLS = [
            "TP", "TN", "FP", "FN",
            "Accuracy", "TPR (Recall)", "TNR",
            "FPR", "FNR", "Precision (PPV)",
            "NPV", "FDR", "FOR", "F1"
        ]

        FAIRNESS_COLS = [
            "Statistical Parity Difference",
            "Disparate Impact",
            "Average Odds Difference",
            "Error Rate Difference",
            "Equal Opportunity Difference",
            "Equalized Odds",
            "Thiel Index",
        ]

        # 🔒 CONTRACT PRESERVED
        st.session_state["inference"] = {
            "completed": True,
            "compute_key": compute_key,
            "results_df": results_df,
            "fairness_bootstrap": fairness_bootstrap,
            "y_true": y_true,
            "sensitive_attr": sens_arr,
            "positive_class": {
                "ground_truth": POS_TRUE,
                "prediction": POS_PRED,
            },
            "tables": {
                "performance": safe_table(results_df, PERFORMANCE_COLS),
                "fairness": safe_table(results_df, FAIRNESS_COLS),
            },
        }

        st.session_state["metrics_ready"] = True

# --------------------------------------------------
# Guard: freeze UI until computed
# --------------------------------------------------
if not st.session_state.get("metrics_ready"):
    st.stop()

# --------------------------------------------------
# Unpack (READ-ONLY, SAFE)
# --------------------------------------------------
inference = st.session_state["inference"]

# Recompute protection
if inference.get("compute_key") != compute_key:
    st.warning("Inputs changed. Please recompute metrics.")
    st.stop()

results_df = inference["results_df"]
fairness_bootstrap = inference["fairness_bootstrap"]
y_true = inference["y_true"]
sens_arr = inference["sensitive_attr"]

AVAILABLE_FAIRNESS_METRICS = [
    c for c in [
        "Statistical Parity Difference",
        "Disparate Impact",
        "Average Odds Difference",
        "Error Rate Difference",
        "Equal Opportunity Difference",
        "Equalized Odds",
        "Thiel Index",
    ]
    if c in results_df.columns
]

# --------------------------------------------------
# Sidebar navigation (UNCHANGED)
# --------------------------------------------------
subpage = st.sidebar.radio(
    "Inference & Fairness Story",
    [
        " Model Readiness",
        " Outcome Distribution & Parity",
        " Error Disparities",
        " Fairness–Performance Tradeoffs",
        " Model Comparison & Risk Summary",
    ],
)

# ==================================================
# 1️⃣ Model Readiness
# ==================================================
if subpage == " Model Readiness":
    st.dataframe(inference["tables"]["performance"].set_index("Model"), use_container_width=True)
    st.pyplot(plot_bar_single_metric(results_df, "Accuracy"))
    st.pyplot(plot_line_single_metric(results_df, "Accuracy"))

# ==================================================
# 2️⃣ Outcome Distribution & Parity
# ==================================================
elif subpage == " Outcome Distribution & Parity":
    st.dataframe(inference["tables"]["fairness"].set_index("Model"), use_container_width=True)

    metric = st.selectbox("Outcome fairness metric", AVAILABLE_FAIRNESS_METRICS)
    st.pyplot(plot_bar_single_metric(results_df, metric))

    model = st.selectbox("Model for group outcomes", pred_cols)
    group_df = (
        pd.DataFrame({
            sensitive_col: sens_arr,
            "selection_rate": _as01(data[model].values, POS_PRED),
        })
        .groupby(sensitive_col, as_index=False)
        .mean()
    )

    st.pyplot(
        plot_by_group_bars(
            group_df,
            sensitive_col=sensitive_col,
            value_col="selection_rate",
            title="Selection Rate by Group",
        )
    )

# ==================================================
# 3️⃣ Error Disparities
# ==================================================
elif subpage == " Error Disparities":
    model = st.selectbox("Model", pred_cols)

    fig, stats = plot_disparity_in_performance(
        y_true, data[model].values, sens_arr,
        positive_true=POS_TRUE, positive_pred=POS_PRED
    )
    st.pyplot(fig)
    st.dataframe(stats["per_group"])

    st.pyplot(
        plot_group_error_panel(
            y_true, data[model].values, sens_arr,
            group_name=sensitive_col,
            positive_true=POS_TRUE, positive_pred=POS_PRED
        )
    )

# ==================================================
# 4️⃣ Fairness–Performance Tradeoffs
# ==================================================
elif subpage == " Fairness–Performance Tradeoffs":
    st.pyplot(
        plot_fairness_accuracy_scatter(
            results_df,
            fairness_metric=st.selectbox("Fairness metric", AVAILABLE_FAIRNESS_METRICS),
            performance_metric=st.selectbox(
                "Performance metric", ["Accuracy", "TPR (Recall)", "FPR", "FNR"]
            ),
        )
    )

# ==================================================
# 5️⃣ Model Comparison & Risk Summary
# ==================================================
elif subpage == " Model Comparison & Risk Summary":
    st.pyplot(plot_fairness_error_bars(fairness_bootstrap))

    heatmap_df = results_df.set_index("Model")[AVAILABLE_FAIRNESS_METRICS]
    st.pyplot(plot_models_groups_heatmap(heatmap_df))

    st.dataframe(
        inference["tables"]["fairness"].set_index("Model"),
        use_container_width=True
    )

