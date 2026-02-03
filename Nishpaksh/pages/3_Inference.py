# pages/3_Inference.py
# Inference & Fairness Evaluation — STORY-DRIVEN + CONTRACT-SAFE

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
    /* Import font */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    
    /* Base typography */
    .stApp {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    
    /* Gradient headings */
    h1 code, h2 code, h3 code {
    -webkit-text-fill-color: initial !important;
    background: none !important;
    color: #2563eb !important;   /* readable blue */
    font-weight: 700;}

    
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
# --------------------------------------------------
# Preconditions (flat authoritative keys)
# --------------------------------------------------
data = st.session_state.get("uploaded_data")
ground_truth = st.session_state.get("ground_truth")
num_protected = st.session_state.get("num_protected_attrs")

if not isinstance(data, pd.DataFrame) or data.empty:
    st.warning("No dataset available. Complete earlier steps first.")
    st.stop()

if not isinstance(ground_truth, str) or ground_truth == "":
    st.error("Ground truth must be set on the Home page.")
    st.stop()

if not isinstance(num_protected, int) or num_protected < 1:
    st.error("Protected attributes not configured on Home page.")
    st.stop()

# --------------------------------------------------
# Reconstruct protected attributes
# --------------------------------------------------
protected_attrs = []
for i in range(1, num_protected + 1):
    attr = st.session_state.get(f"protected_attribute_{i}")
    priv = st.session_state.get(f"privileged_class_{i}")

    if not isinstance(attr, str) or not isinstance(priv, str):
        st.error(f"Protected attribute {i} is not fully configured.")
        st.stop()

    protected_attrs.append(
        {"attribute": attr, "privileged_class": priv}
    )

# --------------------------------------------------
# Detect prediction columns
# --------------------------------------------------
pred_cols = [
    c for c in data.columns
    if c != ground_truth
    and set(pd.Series(data[c]).dropna().unique()).issubset({0, 1})
]

if not pred_cols:
    st.error("No prediction columns detected.")
    st.stop()

# --------------------------------------------------
# Positive class selectors
# --------------------------------------------------
def _guess_positive(vals):
    for v in vals:
        if str(v).lower() in {"1", "true", "yes", "approved", "positive"}:
            return v
    return sorted(vals)[-1]

label_vals = data[ground_truth].astype(str).unique().tolist()
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
# Deterministic compute key
# --------------------------------------------------
def make_compute_key():
    h = hashlib.sha256()
    h.update(str(ground_truth).encode())
    for p in protected_attrs:
        h.update(p["attribute"].encode())
        h.update(p["privileged_class"].encode())
    h.update(str(POS_TRUE).encode())
    h.update(str(POS_PRED).encode())
    h.update(",".join(pred_cols).encode())
    h.update(str(data.shape).encode())
    return h.hexdigest()

compute_key = make_compute_key()

# --------------------------------------------------
# Heavy computation (multi-sensitive)
# --------------------------------------------------
def compute_all_metrics_multi_sensitive(
    df, label_col, pred_cols, protected_attrs, pos_true, pos_pred, B=20
):
    results_by_attr = {}
    bootstrap_by_attr = {}

    y_true = _as01(df[label_col].values, positive=pos_true)

    for p in protected_attrs:
        sens_col = p["attribute"]
        priv_val = p["privileged_class"]
        sens_arr = df[sens_col].astype(str).values

        rows = []
        fairness_bootstrap = {}

        for col in pred_cols:
            y_pred = _as01(df[col].values, positive=pos_pred)

            perf = GroupMetrics(y_true, y_pred).get_all()
            fair = FairnessMetrics(
                y_true, y_pred, sens_arr,
                privileged_value=priv_val
            ).get_all()

            rows.append({"Model": col, **perf, **fair})

            for m in fair:
                fairness_bootstrap.setdefault(m, {})[col] = []
                for _ in range(B):
                    idx = np.random.choice(len(y_true), len(y_true), replace=True)
                    fb = FairnessMetrics(
                        y_true[idx],
                        y_pred[idx],
                        sens_arr[idx],
                        privileged_value=priv_val,
                    ).get_all()
                    fairness_bootstrap[m][col].append(fb[m])

        results_by_attr[sens_col] = pd.DataFrame(rows)
        bootstrap_by_attr[sens_col] = fairness_bootstrap

    return results_by_attr, bootstrap_by_attr, y_true

# --------------------------------------------------
# Compute trigger
# --------------------------------------------------
if st.button("Compute metrics"):
    with st.spinner("Computing metrics…"):
        results_by_attr, bootstrap_by_attr, y_true = compute_all_metrics_multi_sensitive(
            data,
            ground_truth,
            pred_cols,
            protected_attrs,
            POS_TRUE,
            POS_PRED,
        )

        st.session_state["inference"] = {
            "completed": True,
            "compute_key": compute_key,
            "results_by_attr": results_by_attr,
            "bootstrap_by_attr": bootstrap_by_attr,
            "y_true": y_true,
        }
        st.session_state["metrics_ready"] = True

if not st.session_state.get("metrics_ready"):
    st.stop()

inference = st.session_state["inference"]
if inference["compute_key"] != compute_key:
    st.warning("Inputs changed. Please recompute metrics.")
    st.stop()

results_by_attr = inference["results_by_attr"]
bootstrap_by_attr = inference["bootstrap_by_attr"]
y_true = inference["y_true"]

# --------------------------------------------------
# Subpage navigation (UNCHANGED STRUCTURE)
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
# 1. Model Readiness
# ==================================================
if subpage == " Model Readiness":
    for sens_col, df_res in results_by_attr.items():
        st.markdown(f"## Model Readiness — `{sens_col}`")
        st.dataframe(df_res.set_index("Model"), use_container_width=True)
        st.pyplot(plot_bar_single_metric(df_res, "Accuracy"))

# ==================================================
# 2. Outcome Distribution & Parity
# ==================================================
elif subpage == " Outcome Distribution & Parity":
    for sens_col, df_res in results_by_attr.items():
        st.markdown(f"## Outcome Distribution & Parity — `{sens_col}`")

        metric = st.selectbox(
            f"Fairness metric ({sens_col})",
            [
                c for c in df_res.columns
                if c in [
                    "Statistical Parity Difference",
                    "Disparate Impact",
                    "Average Odds Difference",
                    "Error Rate Difference",
                    "Equal Opportunity Difference",
                ]
            ],
            key=f"parity_{sens_col}",
        )

        st.pyplot(plot_bar_single_metric(df_res, metric))

# ==================================================
# 3. Error Disparities
# ==================================================
elif subpage == " Error Disparities":
    for sens_col in results_by_attr:
        st.markdown(f"## Error Disparities — `{sens_col}`")

        model = st.selectbox(
            f"Model ({sens_col})",
            pred_cols,
            key=f"err_model_{sens_col}",
        )

        sens_arr = data[sens_col].astype(str).values

        fig, stats = plot_disparity_in_performance(
            y_true,
            data[model].values,
            sens_arr,
            positive_true=POS_TRUE,
            positive_pred=POS_PRED,
        )
        st.pyplot(fig)
        st.dataframe(stats["per_group"])

        st.pyplot(
            plot_group_error_panel(
                y_true,
                data[model].values,
                sens_arr,
                group_name=sens_col,
                positive_true=POS_TRUE,
                positive_pred=POS_PRED,
            )
        )

# ==================================================
# 4. Fairness–Performance Tradeoffs
# ==================================================
elif subpage == " Fairness–Performance Tradeoffs":

    # Use the first sensitive attribute's results as representative
    df_res = next(iter(results_by_attr.values()))

    st.markdown("## Fairness–Performance Trade-offs")

    fairness_metric = st.selectbox(
        "Fairness metric",
        [c for c in df_res.columns if c not in ["Model", "Accuracy"]],
        key="trade_fair_global",
    )

    performance_metric = st.selectbox(
        "Performance metric",
        ["Accuracy", "TPR (Recall)", "FPR", "FNR"],
        key="trade_perf_global",
    )

    st.pyplot(
        plot_fairness_accuracy_scatter(
            df_res,
            fairness_metric=fairness_metric,
            performance_metric=performance_metric,
        )
    )

# ==================================================
# 5. Model Comparison & Risk Summary (REMOVED PLOTS)
# ==================================================
elif subpage == " Model Comparison & Risk Summary":
    for sens_col, df_res in results_by_attr.items():
        st.markdown(f"## Model Comparison & Risk Summary — `{sens_col}`")

        st.pyplot(plot_fairness_error_bars(bootstrap_by_attr[sens_col]))

        st.dataframe(df_res.set_index("Model"), use_container_width=True)
