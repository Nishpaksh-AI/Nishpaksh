# pages/4_Results.py
# Results — Fairness Judgment, Evidence & Verdict

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("Results — Fairness Assessment & Verdict")
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
inference = st.session_state.get("inference")
if not inference or not inference.get("completed"):
    st.warning("Inference results not available. Please complete the Inference step.")
    st.stop()

results_by_attr = inference.get("results_by_attr")
if not isinstance(results_by_attr, dict) or not results_by_attr:
    st.error("No protected-attribute-wise results found.")
    st.stop()

# --------------------------------------------------
# Fairness metric definitions (IDEALS)
# --------------------------------------------------
FAIRNESS_METRICS = [
    ("Statistical Parity Difference", 0.0),
    ("Disparate Impact", 1.0),
    ("Average Odds Difference", 0.0),
    ("Equal Opportunity Difference", 0.0),
    ("Error Rate Difference", 0.0),
]

# --------------------------------------------------
# Bias Index computation (PER PROTECTED ATTRIBUTE)
# BI_i = sqrt( (1/n) * sum_j (M_ij - M'_j)^2 )
# --------------------------------------------------
def compute_bias_index(row: pd.Series, metrics):
    diffs = []
    metric_vals = {}

    for name, ideal in metrics:
        if name in row and pd.notna(row[name]):
            val = float(row[name])
            metric_vals[name] = val
            diffs.append((val - ideal) ** 2)

    if not diffs:
        return np.nan, metric_vals

    bi = float(np.sqrt(np.mean(diffs)))
    return bi, metric_vals

# --------------------------------------------------
# Model selection (shared)
# --------------------------------------------------
model_candidates = list(
    next(iter(results_by_attr.values()))["Model"].values
)

st.markdown("### Model under evaluation")
model = st.selectbox("Select model", model_candidates)

# --------------------------------------------------
# Compute BI per protected attribute
# --------------------------------------------------
attr_BI = {}
attr_metric_maps = {}

for attr, df_attr in results_by_attr.items():
    row = df_attr[df_attr["Model"] == model].iloc[0]

    available_metrics = [
        (m, ideal) for m, ideal in FAIRNESS_METRICS if m in df_attr.columns
    ]

    bi, metric_map = compute_bias_index(row, available_metrics)
    attr_BI[attr] = bi
    attr_metric_maps[attr] = {
        "metrics": metric_map,
        "available_metrics": available_metrics,
    }

# --------------------------------------------------
# Fairness Score aggregation (SYSTEM LEVEL)
# FS = 1 - sqrt( (1/m) * sum_i (BI_i)^2 )
# --------------------------------------------------
BI_values = [v for v in attr_BI.values() if pd.notna(v)]

if BI_values:
    FS_system = float(1.0 - np.sqrt(np.mean(np.square(BI_values))))
else:
    FS_system = np.nan

# --------------------------------------------------
# Verdict rules (UNCHANGED)
# --------------------------------------------------
FS_PASS = 0.85
FS_CONDITIONAL = 0.70

if pd.isna(FS_system):
    verdict = "INSUFFICIENT DATA"
    verdict_color = "#9E9E9E"
elif FS_system >= FS_PASS:
    verdict = "PASS"
    verdict_color = "#2E7D32"
elif FS_system >= FS_CONDITIONAL:
    verdict = "CONDITIONAL"
    verdict_color = "#ED6C02"
else:
    verdict = "FAIL"
    verdict_color = "#C62828"

# --------------------------------------------------
# SYSTEM-LEVEL DECISION SUMMARY
# --------------------------------------------------
st.markdown("### Final Fairness Decision (System Level)")

c1, c2 = st.columns(2)

c1.metric(
    "Fairness Score (FS)",
    f"{FS_system:.3f}" if pd.notna(FS_system) else "N/A",
    help="FS = 1 − sqrt(mean(BI_i²)) across protected attributes"
)

c2.markdown(
    f"""
    <div style="
        padding: 1.1rem;
        border-radius: 0.75rem;
        background-color: {verdict_color};
        color: white;
        text-align: center;
        font-size: 1.4rem;
        font-weight: 700;
    ">
        {verdict}
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# --------------------------------------------------
# PER-PROTECTED ATTRIBUTE EVIDENCE (NO PLOTS MISSED)
# --------------------------------------------------
st.markdown("## Bias Index by Protected Attribute")

for attr, bi in attr_BI.items():
    st.markdown(f"### Protected Attribute: `{attr}`")

    # ---- BI Card ----
    st.metric(
        "Bias Index (BI)",
        f"{bi:.3f}" if pd.notna(bi) else "N/A",
        help="Root-mean-square deviation of fairness metrics from ideal values"
    )

    metric_map = attr_metric_maps[attr]["metrics"]
    available_metrics = attr_metric_maps[attr]["available_metrics"]

    # ---- Fairness metric component plot ----
    if metric_map:
        metric_names = list(metric_map.keys())
        values = [metric_map[m] for m in metric_names]

        fig, ax = plt.subplots(figsize=(8, 4))
        bars = ax.bar(metric_names, values)

        for m, ideal in available_metrics:
            if m in metric_names:
                ax.axhline(
                    y=ideal,
                    linestyle="--",
                    linewidth=1,
                    alpha=0.6,
                    color="black"
                )

        ax.set_ylabel("Metric value")
        ax.set_title(f"Fairness Metrics — {attr}")
        ax.set_xticklabels(metric_names, rotation=30, ha="right")

        for b, v in zip(bars, values):
            ax.text(
                b.get_x() + b.get_width() / 2,
                b.get_height(),
                f"{v:.3f}",
                ha="center",
                va="bottom",
                fontsize=9
            )

        plt.tight_layout()
        st.pyplot(fig)

        st.caption(
            "Dashed reference lines indicate ideal metric values. "
            "These metrics are aggregated into the Bias Index (BIᵢ)."
        )
    else:
        st.info("No fairness metrics available for this protected attribute.")

    st.markdown("---")

# --------------------------------------------------
# SYSTEM-LEVEL AGGREGATION PLOT (BI → FS)
# --------------------------------------------------
st.markdown("## Aggregation Across Protected Attributes")

attrs = list(attr_BI.keys())
bi_vals = [attr_BI[a] for a in attrs]

fig, ax = plt.subplots(figsize=(7, 4))
bars = ax.bar(attrs, bi_vals)

ax.set_ylabel("Bias Index (BIᵢ)")
ax.set_title("Bias Index per Protected Attribute")

for b, v in zip(bars, bi_vals):
    if pd.notna(v):
        ax.text(
            b.get_x() + b.get_width() / 2,
            b.get_height(),
            f"{v:.3f}",
            ha="center",
            va="bottom",
            fontsize=9
        )

plt.tight_layout()
st.pyplot(fig)

# --------------------------------------------------
# Decision rationale (STANDARD-COMPLIANT)
# --------------------------------------------------
st.markdown("### Decision Rationale")

st.markdown(
    f"""
- **Bias Index (BIᵢ)** is computed **per protected attribute** as the root-mean-square
  deviation of fairness metrics from their ideal values.
- **Fairness Score (FS)** is computed at the **system level** as:

\[
FS = 1 - \sqrt{{\\frac{{1}}{{m}} \sum_{{i=1}}^{{m}} BI_i^2}}
\]

where *m* is the number of protected attributes.

**Decision thresholds applied**:
- FS ≥ {FS_PASS} → **PASS**
- FS ≥ {FS_CONDITIONAL} → **CONDITIONAL**
- Otherwise → **FAIL**

**Final verdict for `{model}`**: **{verdict}**
"""
)

# --------------------------------------------------
# Persist results
# --------------------------------------------------
st.session_state["results"] = {
    "selected_model": model,
    "FS_system": FS_system,
    "BI_per_attribute": attr_BI,
    "verdict": verdict,
    "thresholds": {
        "FS_pass": FS_PASS,
        "FS_conditional": FS_CONDITIONAL,
    },
}

st.success("Fairness assessment completed using standard-compliant aggregation.")
