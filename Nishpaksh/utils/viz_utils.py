


# utils/viz_utils_matplotlib.py
# Visualization utilities for the fairness dashboard
# - Matplotlib charts (professional styling)
# - Robust handling of non-numeric labels
# 

from typing import Dict, List, Optional, Tuple

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import seaborn as sns

# Set professional styling
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Professional color schemes
COLORS = {
    'primary': '#1F77B4',
    'secondary': '#FF7F0E',
    'success': '#2CA02C',
    'warning': '#F39C12',
    'danger': '#D62728',
    'info': '#17BECF',
    'purple': '#9467BD',
    'pink': '#E377C2',
    'brown': '#8C564B',
    'grey': '#7F7F7F',
}

# Color palette for multiple models
MODEL_COLORS = ['#1F77B4', '#FF7F0E', '#2CA02C', '#D62728', '#9467BD', 
                '#8C564B', '#E377C2', '#7F7F7F', '#BCBD22', '#17BECF']


# ============================ Helpers ============================

def _coerce_numeric(series: pd.Series) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce")
    return s.replace([np.inf, -np.inf], np.nan)


def _sort_models_axis(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    df_sorted = df.copy()
    vals = _coerce_numeric(df_sorted[metric])
    order = np.argsort(-vals.fillna(-np.inf).values)  # descending; NaN last
    df_sorted = df_sorted.iloc[order].copy()
    df_sorted["Model"] = pd.Categorical(df_sorted["Model"], categories=df_sorted["Model"], ordered=True)
    return df_sorted


def _as01(arr, positive: Optional[object] = None) -> np.ndarray:
    """Coerce labels to {0,1}. If positive provided, equality->1 else 0."""
    a = pd.Series(arr).copy()

    if positive is not None:
        return (a.astype(str) == str(positive)).astype(int).to_numpy()

    uniq = pd.unique(a.dropna())
    # Already numeric {0,1}?
    if pd.api.types.is_numeric_dtype(a) and set(map(float, uniq)).issubset({0.0, 1.0}):
        return a.fillna(0).astype(int).to_numpy()

    # Booleans
    if a.dtype == bool:
        return a.fillna(False).astype(int).to_numpy()

    # Strings/mixed with two uniques -> guess positive
    uniq_str = [str(u) for u in uniq]
    looks_pos = {"1", "true", "yes", "y", "approved", "accept", "accepted", "positive"}
    if len(uniq_str) == 2:
        pos_guess = None
        for u in uniq_str:
            if u.lower() in looks_pos:
                pos_guess = u
                break
        if pos_guess is None:
            pos_guess = sorted(uniq_str)[-1]  # deterministic
        return (a.astype(str) == pos_guess).astype(int).to_numpy()

    # Fallback: non-null -> 1
    return a.notna().astype(int).to_numpy()


def _setup_professional_style(fig: Figure, ax: Axes):
    """Apply professional styling to figure and axes."""
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    fig.patch.set_facecolor('white')
    ax.set_facecolor('#F8F9FA')


# ============ Global comparisons across models ============

def plot_bar_single_metric(results_df: pd.DataFrame, metric: str, title: Optional[str] = None) -> Figure:
    if "Model" not in results_df.columns or metric not in results_df.columns:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, "Metric not available", ha='center', va='center', fontsize=14)
        ax.set_title(title or "Metric not available")
        return fig

    df = results_df[["Model", metric]].copy()
    df[metric] = _coerce_numeric(df[metric])
    df = _sort_models_axis(df, metric)

    if title is None:
        title = f"{metric} across models"

    fig, ax = plt.subplots(figsize=(12, 6))
    
    x_pos = np.arange(len(df))
    bars = ax.bar(x_pos, df[metric], color=COLORS['primary'], alpha=0.8, edgecolor='black', linewidth=1.2)
    
    # Add value labels on top of bars
    for i, (bar, val) in enumerate(zip(bars, df[metric])):
        if pd.notna(val):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01 * ax.get_ylim()[1],
                   f'{val:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels(df["Model"], rotation=45, ha='right')
    ax.set_xlabel("Model", fontsize=12, fontweight='bold')
    ax.set_ylabel(metric, fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    _setup_professional_style(fig, ax)
    plt.tight_layout()
    return fig


def plot_line_single_metric(results_df: pd.DataFrame, metric: str, title: Optional[str] = None) -> Figure:
    if "Model" not in results_df.columns or metric not in results_df.columns:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, "Metric not available", ha='center', va='center', fontsize=14)
        ax.set_title(title or "Metric not available")
        return fig

    df = results_df[["Model", metric]].copy()
    df[metric] = _coerce_numeric(df[metric])
    df = _sort_models_axis(df, metric)

    if title is None:
        title = f"{metric} trend across models"

    fig, ax = plt.subplots(figsize=(12, 6))
    
    x_pos = np.arange(len(df))
    ax.plot(x_pos, df[metric], marker='o', linewidth=2.5, markersize=10, 
            color=COLORS['primary'], markeredgecolor='black', markeredgewidth=1.5)
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels(df["Model"], rotation=45, ha='right')
    ax.set_xlabel("Model", fontsize=12, fontweight='bold')
    ax.set_ylabel(metric, fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    _setup_professional_style(fig, ax)
    plt.tight_layout()
    return fig


def plot_fairness_error_bars(
    metrics_bootstrap: Dict[str, Dict[str, List[float]]],
    ci: float = 95.0,
    title: str = "Fairness metrics (bootstrap CI)",
) -> Figure:
    if not metrics_bootstrap:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, title, ha='center', va='center', fontsize=14)
        return fig

    records: List[dict] = []
    alpha = (100.0 - ci) / 2.0

    for metric, per_model in metrics_bootstrap.items():
        for model, values in per_model.items():
            if not values:
                continue
            arr = pd.to_numeric(pd.Series(values), errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
            if arr.empty:
                continue

            mean = float(arr.mean())
            lower = float(np.percentile(arr, alpha))
            upper = float(np.percentile(arr, 100.0 - alpha))

            if any(v is None or (isinstance(v, float) and (math.isnan(v) or math.isinf(v))) for v in [mean, lower, upper]):
                continue

            records.append({"Metric": metric, "Model": model, "Mean": mean, "Lower": lower, "Upper": upper})

    if not records:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, title, ha='center', va='center', fontsize=14)
        return fig

    df = pd.DataFrame(records)
    metrics = df["Metric"].unique()
    models = df["Model"].unique()
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    x = np.arange(len(metrics))
    width = 0.8 / len(models)
    
    for i, model in enumerate(models):
        model_data = df[df["Model"] == model]
        offset = (i - len(models)/2 + 0.5) * width
        
        means = []
        errors_lower = []
        errors_upper = []
        
        for metric in metrics:
            row = model_data[model_data["Metric"] == metric]
            if not row.empty:
                means.append(row["Mean"].values[0])
                errors_lower.append(row["Mean"].values[0] - row["Lower"].values[0])
                errors_upper.append(row["Upper"].values[0] - row["Mean"].values[0])
            else:
                means.append(0)
                errors_lower.append(0)
                errors_upper.append(0)
        
        ax.bar(x + offset, means, width, label=model, 
               yerr=[errors_lower, errors_upper], capsize=5,
               color=MODEL_COLORS[i % len(MODEL_COLORS)], alpha=0.8,
               edgecolor='black', linewidth=1, error_kw={'linewidth': 2})
    
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, rotation=45, ha='right')
    ax.set_xlabel("Metric", fontsize=12, fontweight='bold')
    ax.set_ylabel("Value", fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='best', framealpha=0.9, edgecolor='black')
    
    _setup_professional_style(fig, ax)
    plt.tight_layout()
    return fig


# ============ disaggregated views ============

def plot_by_group_bars(group_df: pd.DataFrame, sensitive_col: str, value_col: str, title: Optional[str] = None) -> Figure:
    df = group_df[[sensitive_col, value_col]].copy()
    df[value_col] = _coerce_numeric(df[value_col])
    
    if title is None:
        title = f"{value_col} by {sensitive_col}"
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x_pos = np.arange(len(df))
    bars = ax.bar(x_pos, df[value_col], color=COLORS['info'], alpha=0.8, 
                  edgecolor='black', linewidth=1.2)
    
    # Add value labels
    for bar, val in zip(bars, df[value_col]):
        if pd.notna(val):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01 * ax.get_ylim()[1],
                   f'{val:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels(df[sensitive_col], rotation=45, ha='right')
    ax.set_xlabel("Group", fontsize=12, fontweight='bold')
    ax.set_ylabel(value_col, fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    _setup_professional_style(fig, ax)
    plt.tight_layout()
    return fig


def plot_models_groups_heatmap(matrix_df: pd.DataFrame, title: str = "Metric by model and group") -> Figure:
    df = matrix_df.copy()
    df = df.apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Create heatmap with annotations
    im = ax.imshow(df.values, cmap='Blues', aspect='auto')
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.ax.set_ylabel('Value', rotation=270, labelpad=20, fontweight='bold')
    
    # Set ticks and labels
    ax.set_xticks(np.arange(len(df.columns)))
    ax.set_yticks(np.arange(len(df.index)))
    ax.set_xticklabels(df.columns, rotation=45, ha='right')
    ax.set_yticklabels(df.index)
    
    # Add text annotations
    for i in range(len(df.index)):
        for j in range(len(df.columns)):
            val = df.values[i, j]
            if pd.notna(val):
                text = ax.text(j, i, f'{val:.2f}', ha='center', va='center', 
                             color='white' if val > df.values[pd.notna(df.values)].mean() else 'black',
                             fontweight='bold')
    
    ax.set_xlabel("Group", fontsize=12, fontweight='bold')
    ax.set_ylabel("Model", fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    fig.patch.set_facecolor('white')
    plt.tight_layout()
    return fig


# ============  trade-off  plot (no threshold sweep) ============

def plot_fairness_accuracy_scatter(
    results_df: pd.DataFrame,
    fairness_metric: str = "Statistical Parity Difference",
    performance_metric: str = "Accuracy",
    title: str = "Fairness vs Performance",
    jitter: float = 0.0,
) -> Figure:
    if fairness_metric not in results_df.columns or performance_metric not in results_df.columns:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, "Metrics not available", ha='center', va='center', fontsize=14)
        ax.set_title(title)
        return fig

    df = results_df[["Model", fairness_metric, performance_metric]].copy()
    df[fairness_metric] = _coerce_numeric(df[fairness_metric])
    df[performance_metric] = _coerce_numeric(df[performance_metric])

    if jitter and jitter > 0:
        df[fairness_metric] = df[fairness_metric] + np.random.normal(0, jitter, size=len(df))

    fig, ax = plt.subplots(figsize=(12, 8))
    
    models = df["Model"].unique()
    for i, model in enumerate(models):
        model_data = df[df["Model"] == model]
        ax.scatter(model_data[performance_metric], model_data[fairness_metric],
                  s=25, alpha=0.7, edgecolors='darkslategrey', linewidths=2,
                  color=MODEL_COLORS[i % len(MODEL_COLORS)], label=model)
    
    ax.set_xlabel(performance_metric, fontsize=12, fontweight='bold')
    ax.set_ylabel(fairness_metric, fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='best', framealpha=0.9, edgecolor='black')
    
    _setup_professional_style(fig, ax)
    plt.tight_layout()
    return fig


# ============ disparity in performance ============

def _group_error_breakdown(
    y_true,
    y_pred,
    groups,
    positive_true: Optional[object] = None,
    positive_pred: Optional[object] = None,
) -> Tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    y_t = _as01(y_true, positive=positive_true)
    y_p = _as01(y_pred, positive=positive_pred)
    g = pd.Series(groups).astype(str)

    df = pd.DataFrame({"y_true": y_t, "y_pred": y_p, "g": g})
    out = []
    for gval, sub in df.groupby("g"):
        n = len(sub)
        if n == 0:
            continue
        under = ((sub["y_true"] == 1) & (sub["y_pred"] == 0)).sum() / n  # FN / group size
        over  = ((sub["y_true"] == 0) & (sub["y_pred"] == 1)).sum() / n  # FP / group size
        acc   = (sub["y_true"] == sub["y_pred"]).mean()
        out.append({"group": str(gval), "n": n, "under": float(under), "over": float(over), "acc": float(acc)})
    return pd.DataFrame(out).sort_values("group"), y_t, y_p


def plot_disparity_in_performance(
    y_true,
    y_pred,
    sensitive_attr,
    title: str = "Disparity in performance",
    positive_true: Optional[object] = None,
    positive_pred: Optional[object] = None,
):
    """
    Under/overprediction split per group (-style):
      - Left (negative): underprediction rate = FN / group size
      - Right (positive): overprediction rate = FP / group size
    """
    gdf, y_t, y_p = _group_error_breakdown(y_true, y_pred, sensitive_attr, positive_true=positive_true, positive_pred=positive_pred)
    if gdf.empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, title, ha='center', va='center', fontsize=14)
        return fig, {"overall_accuracy": np.nan, "disparity_in_accuracy": np.nan, "per_group": gdf}

    overall_acc = float((y_t == y_p).mean())
    disparity_acc = float(gdf["acc"].max() - gdf["acc"].min())

    under_vals = -gdf["under"].values  # left
    over_vals  =  gdf["over"].values   # right
    y_order = list(gdf["group"])

    fig, ax = plt.subplots(figsize=(12, 8))
    
    y_pos = np.arange(len(y_order))
    
    # Underprediction bars (left, negative)
    bars1 = ax.barh(y_pos, under_vals, color='#F39C12', alpha=0.8, 
                    edgecolor='black', linewidth=1.2, label='Underprediction (pred=0, true=1)')
    
    # Overprediction bars (right, positive)
    bars2 = ax.barh(y_pos, over_vals, color='#1F77B4', alpha=0.8,
                    edgecolor='black', linewidth=1.2, label='Overprediction (pred=1, true=0)')
    
    # Add center line at zero
    ax.axvline(x=0, color='black', linewidth=1.5, linestyle='-')
    
    # Add percentage labels
    xmax = max(abs(under_vals).max() if len(under_vals) else 0, abs(over_vals).max() if len(over_vals) else 0, 0.01)
    tiny = xmax * 0.02
    
    for i, (u, o) in enumerate(zip(under_vals, over_vals)):
        # Underprediction label
        x_u = u if u != 0 else -tiny
        ax.text(x_u, i, f'{abs(u)*100:.1f}%', 
               ha='right' if x_u < 0 else 'center', va='center',
               fontsize=11, fontweight='bold', color='#5D3A00')
        
        # Overprediction label
        x_o = o if o != 0 else tiny
        ax.text(x_o, i, f'{abs(o)*100:.1f}%',
               ha='left' if x_o > 0 else 'center', va='center',
               fontsize=11, fontweight='bold', color='#0A3B66')
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(y_order)
    ax.set_xlabel("Error rate by group size", fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    # Format x-axis as percentage
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x*100:.0f}%'))
    
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=2, 
             framealpha=0.9, edgecolor='black')
    
    _setup_professional_style(fig, ax)
    ax.margins(x=0.15)
    plt.tight_layout()

    stats = {
        "overall_accuracy": round(overall_acc, 4),
        "disparity_in_accuracy": round(disparity_acc, 4),
        "per_group": gdf.assign(under=lambda d: d["under"].round(4), over=lambda d: d["over"].round(4), acc=lambda d: d["acc"].round(4)),
    }
    return fig, stats


# ============ Simple by-group error panel (Accuracy, FPR, FNR) ============

def _by_group_rates(y_true, y_pred, groups, positive_true=None, positive_pred=None) -> pd.DataFrame:
    y_t = _as01(y_true, positive=positive_true)
    y_p = _as01(y_pred, positive=positive_pred)
    g   = pd.Series(groups).astype(str)

    rows = []
    for grp, sub_idx in g.groupby(g).groups.items():
        yt = y_t[sub_idx]
        yp = y_p[sub_idx]

        TP = int(((yt == 1) & (yp == 1)).sum())
        TN = int(((yt == 0) & (yp == 0)).sum())
        FP = int(((yt == 0) & (yp == 1)).sum())
        FN = int(((yt == 1) & (yp == 0)).sum())

        n = len(yt)
        acc = (TP + TN) / n if n > 0 else np.nan
        neg = TN + FP
        pos = TP + FN
        fpr = FP / neg if neg > 0 else np.nan
        fnr = FN / pos if pos > 0 else np.nan

        rows.append({
            "group": grp,
            "accuracy": acc,
            "false_positive_rate": fpr,
            "false_negative_rate": fnr,
        })
    df = pd.DataFrame(rows).sort_values("group")
    return df


def plot_group_error_panel(
    y_true,
    y_pred,
    sensitive_attr,
    group_name: str = "Group",
    positive_true=None,
    positive_pred=None,
    title: str = "By-group error panel",
) -> Figure:
    """
    Three small bar charts (accuracy, false_positive_rate, false_negative_rate)
    computed strictly by the given sensitive attribute column.
    """
    df = _by_group_rates(y_true, y_pred, sensitive_attr, positive_true, positive_pred)

    cols = [
        ("accuracy", "Accuracy"),
        ("false_positive_rate", "False Positive Rate"),
        ("false_negative_rate", "False Negative Rate"),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    
    for i, (col_key, col_title) in enumerate(cols):
        ax = axes[i]
        
        x_pos = np.arange(len(df))
        bars = ax.bar(x_pos, df[col_key], color=MODEL_COLORS[i % len(MODEL_COLORS)], 
                     alpha=0.8, edgecolor='black', linewidth=1.2)
        
        # Add value labels
        for bar, val in zip(bars, df[col_key]):
            if pd.notna(val):
                ax.text(bar.get_x() + bar.get_width()/2, 
                       bar.get_height() + 0.02,
                       f'{val*100:.1f}%', ha='center', va='bottom', 
                       fontsize=10, fontweight='bold')
            else:
                ax.text(bar.get_x() + bar.get_width()/2, 0.01,
                       '—', ha='center', va='bottom', 
                       fontsize=12, fontweight='bold')
        
        ax.set_xticks(x_pos)
        ax.set_xticklabels(df["group"], rotation=45, ha='right')
        ax.set_xlabel(group_name, fontsize=11, fontweight='bold')
        ax.set_title(col_title, fontsize=12, fontweight='bold', pad=10)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, p: f'{y*100:.0f}%'))
        
        _setup_professional_style(fig, ax)
    
    fig.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()

    return fig


