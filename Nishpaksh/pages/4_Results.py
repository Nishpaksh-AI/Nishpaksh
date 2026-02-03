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
    font-weight: 700;
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
    
    /* Push main content down to avoid logo overlap */
    section[data-testid="stMain"] > div:first-child {
        padding-top: 3rem !important;
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
# Get selected metrics from session state (configured in Metrics & Thresholds page)
# --------------------------------------------------
selected_thresholds = st.session_state.get("thresholds", {})

if not selected_thresholds:
    st.warning("No metrics have been selected. Please configure metrics on the 'Metrics and Thresholds' page.")
    st.stop()

# Map metric names to their ideal values
METRIC_IDEALS = {
    "Statistical Parity Difference": 0.0,
    "Disparate Impact": 1.0,
    "Average Odds Difference": 0.0,
    "Equal Opportunity Difference": 0.0,
    "Error Rate Difference": 0.0,
    "Calibration Difference (global)": 0.0,
}

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
# Display selected metrics summary
# --------------------------------------------------
st.markdown("### Selected Fairness Metrics")

# Calculate total metrics selected across all attributes
total_metrics_selected = 0
for attr, metrics_dict in selected_thresholds.items():
    valid_metrics = [m for m in metrics_dict.keys() if m in METRIC_IDEALS]
    total_metrics_selected += len(valid_metrics)

st.info(f"{total_metrics_selected} total metrics selected across all protected attributes. The Bias Index will be calculated using only these selected metrics.")

with st.expander("View selected metrics per protected attribute", expanded=False):
    for attr, metrics_dict in selected_thresholds.items():
        selected_metric_names = [m for m in metrics_dict.keys() if m in METRIC_IDEALS]
        st.markdown(f"**{attr}** ({len(selected_metric_names)} metrics):")
        if selected_metric_names:
            for metric_name in selected_metric_names:
                threshold = metrics_dict[metric_name].get('value', 'N/A')
                st.markdown(f"  - {metric_name} (threshold: {threshold})")
        else:
            st.markdown("  - *No valid metrics selected*")
        st.markdown("")

# --------------------------------------------------
# Compute BI per protected attribute (USING SELECTED METRICS ONLY)
# --------------------------------------------------
attr_BI = {}
attr_metric_maps = {}

try:
    for attr, df_attr in results_by_attr.items():
        row = df_attr[df_attr["Model"] == model].iloc[0]
        
        # Get selected metrics for this protected attribute
        if attr not in selected_thresholds:
            st.warning(f"No metrics selected for protected attribute '{attr}'. Skipping.")
            continue
        
        # Build list of selected metrics with their ideal values
        available_metrics = []
        for metric_name, metric_config in selected_thresholds[attr].items():
            # Check if this metric exists in the results DataFrame
            if metric_name in df_attr.columns and metric_name in METRIC_IDEALS:
                ideal_value = METRIC_IDEALS[metric_name]
                available_metrics.append((metric_name, ideal_value))

        if not available_metrics:
            st.warning(f"No valid metrics found for protected attribute '{attr}'. Skipping.")
            continue

        bi, metric_map = compute_bias_index(row, available_metrics)
        attr_BI[attr] = bi
        attr_metric_maps[attr] = {
            "metrics": metric_map,
            "available_metrics": available_metrics,
        }
except Exception as e:
    st.error(f"Error computing Bias Index: {str(e)}")
    st.error(f"Available attributes: {list(results_by_attr.keys())}")
    st.error(f"Selected model: {model}")
    st.error(f"Selected thresholds: {list(selected_thresholds.keys())}")
    st.stop()

# Verify attr_BI was populated
if not attr_BI:
    st.error("No Bias Index values were computed. Please check that you have selected metrics for your protected attributes.")
    st.stop()

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
st.markdown("### Aggregated Fairness score")

c1, c2 = st.columns(2)

c1.metric(
    "Fairness Score (FS)",
    f"{FS_system:.3f}" if pd.notna(FS_system) else "N/A",
    help="FS = 1 − sqrt(mean(BI_i²)) across protected attributes"
)

#c2.markdown(
#    f"""
#    <div style="
#        padding: 1.1rem;
#        border-radius: 0.75rem;
#        background-color: {verdict_color};
#        color: white;
#        text-align: center;
#        font-size: 1.4rem;
#        font-weight: 700;
#    ">
#        {verdict}
#    </div>
#    """,
#    unsafe_allow_html=True
#)

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
        
        # Cap Disparate Impact values at 2.0 for visualization purposes
        values_capped = []
        for m, v in zip(metric_names, values):
            if m == "Disparate Impact" and v > 2.0:
                values_capped.append(2.0)
            else:
                values_capped.append(v)

        fig, ax = plt.subplots(figsize=(10, 5))
        
        # Get thresholds for this attribute
        attr_thresholds = selected_thresholds.get(attr, {})
        
        # Create horizontal scatter plot
        y_positions = range(len(metric_names))
        
        # Plot threshold buffer zones (shaded rectangles around ideal values)
        buffer_plotted = False
        for i, (m, ideal) in enumerate(available_metrics):
            if m in metric_names:
                idx = metric_names.index(m)
                threshold_val = attr_thresholds.get(m, {}).get('value', 0.1)
                
                # Determine buffer range based on metric type
                if ideal == 1.0:  # Disparate Impact (ideal = 1.0)
                    lower_bound = ideal - threshold_val
                    upper_bound = ideal + threshold_val
                else:  # Other metrics (ideal = 0.0)
                    lower_bound = ideal - threshold_val
                    upper_bound = ideal + threshold_val
                
                # Draw shaded buffer zone in dark blue
                if not buffer_plotted:
                    ax.barh(idx, upper_bound - lower_bound, left=lower_bound, 
                           height=0.5, color='#1e3a8a', alpha=0.3, 
                           edgecolor='none', label='Threshold Buffer')
                    buffer_plotted = True
                else:
                    ax.barh(idx, upper_bound - lower_bound, left=lower_bound, 
                           height=0.5, color='#1e3a8a', alpha=0.3, 
                           edgecolor='none')
        
        # Plot ideal value lines (vertical dashed lines)
        ideal_plotted = False
        for m, ideal in available_metrics:
            if m in metric_names:
                if not ideal_plotted:
                    ax.axvline(x=ideal, color='gray', linestyle='--', 
                              linewidth=1.5, alpha=0.7, zorder=1, label='Ideal Value')
                    ideal_plotted = True
                else:
                    ax.axvline(x=ideal, color='gray', linestyle='--', 
                              linewidth=1.5, alpha=0.7, zorder=1)
        
        # Plot actual values as scatter points
        colors = []
        markers = []
        for m, v, v_capped in zip(metric_names, values, values_capped):
            ideal = next((ideal for name, ideal in available_metrics if name == m), None)
            threshold_val = attr_thresholds.get(m, {}).get('value', 0.1)
            
            if ideal is not None:
                deviation = abs(v - ideal)
                if deviation <= threshold_val:
                    colors.append('#10b981')  # Green - within threshold
                else:
                    colors.append('#ef4444')  # Red - outside threshold
            else:
                colors.append('#94a3b8')  # Gray - unknown
            
            # Use triangle marker if value was capped
            if m == "Disparate Impact" and v > 2.0:
                markers.append('>')
            else:
                markers.append('o')
        
        # Plot points with different markers
        for i, (v_capped, color, marker) in enumerate(zip(values_capped, colors, markers)):
            ax.scatter(v_capped, i, s=200, c=color, marker=marker,
                      edgecolors='black', linewidths=2, zorder=3, alpha=0.9)
        
        # Add value labels next to points
        for i, (v, v_capped, m) in enumerate(zip(values, values_capped, metric_names)):
            if m == "Disparate Impact" and v > 2.0:
                label = f'  {v:.4f} (capped at 2.0)'
            else:
                label = f'  {v:.4f}'
            ax.text(v_capped, i, label, 
                   va='center', ha='left', fontsize=10, fontweight='bold')
        
        # Configure axes
        ax.set_yticks(y_positions)
        ax.set_yticklabels(metric_names, fontsize=11)
        ax.set_xlabel('Metric Value', fontsize=12, fontweight='bold')
        ax.set_title(f'Fairness Metrics for {attr}', fontsize=14, fontweight='bold', pad=20)
        ax.grid(axis='x', alpha=0.3, linestyle='--', linewidth=0.5)
        ax.invert_yaxis()  # Top to bottom
        ax.legend(loc='best', fontsize=10, framealpha=0.9)
        
        # Set x-axis limits with some padding
        all_values = values_capped + [ideal for _, ideal in available_metrics]
        x_min = min(all_values) - 0.1
        x_max = max(all_values) + 0.2
        ax.set_xlim(x_min, x_max)
        
        plt.tight_layout()
        st.pyplot(fig)
        
        # Add explanation for DI capping
        has_capped_di = any(m == "Disparate Impact" and v > 2.0 for m, v in zip(metric_names, values))
        if has_capped_di:
            st.info(
                "Note: Disparate Impact (DI) values greater than 2.0 are capped at 2.0 for visualization clarity. "
                "DI values can range from 0 to infinity, where 1.0 represents perfect parity. "
                "Values significantly above 2.0 indicate extreme disparity but can make the chart difficult to read. "
                "The actual (uncapped) values are shown in the labels and detailed table below."
            )

        
        # Show metrics contributing to BI
        with st.expander(f"Metric details for {attr}", expanded=False):
            metric_details = []
            for m in metric_names:
                ideal = next((ideal for name, ideal in available_metrics if name == m), None)
                actual = metric_map[m]
                threshold_val = attr_thresholds.get(m, {}).get('value', 'N/A')
                deviation = abs(actual - ideal) if ideal is not None else None
                within_threshold = deviation <= threshold_val if (deviation is not None and threshold_val != 'N/A') else 'N/A'
                metric_details.append({
                    "Metric": m,
                    "Actual Value": f"{actual:.4f}",
                    "Ideal Value": f"{ideal:.4f}" if ideal is not None else "N/A",
                    "Threshold": f"{threshold_val:.4f}" if threshold_val != 'N/A' else "N/A",
                    "Deviation": f"{deviation:.4f}" if deviation is not None else "N/A",
                    "Within Threshold": "Yes" if within_threshold == True else "No" if within_threshold == False else "N/A"
                })
            st.dataframe(pd.DataFrame(metric_details), use_container_width=True, hide_index=True)
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
FS = 1 − sqrt(mean(BI_i²)) across protected attributes
\]



**Decision thresholds applied**:
- FS ≥ {FS_PASS} → **Model is fair**
- FS ≥ {FS_CONDITIONAL} → **Slightly more unfairness, but acceptable**
- Otherwise → **Model is unfair**


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
