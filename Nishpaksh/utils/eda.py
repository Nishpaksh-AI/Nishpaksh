import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as ss

from sklearn.preprocessing import LabelEncoder
from sklearn.feature_selection import mutual_info_classif
from sklearn.decomposition import PCA


def cramers_v(x, y):
    confusion_matrix = pd.crosstab(x, y)
    chi2 = ss.chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum().sum()
    return np.sqrt(chi2 / (n * (min(confusion_matrix.shape) - 1)))


def run_eda(df, prediction_cols, ground_truth_col=None, sensitive_col=None, ignore_cols=None):
    """
    Run exploratory data analysis on the dataframe and display plots in Streamlit.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataset.
    prediction_cols : list
        Columns that are model predictions (will be dropped for EDA).
    ground_truth_col : str, optional
        Column name of ground truth / target variable.
    sensitive_col : str, optional
        Column name of sensitive attribute.
    ignore_cols : list, optional
        Columns to ignore in plots (not dropped from df).
    """
    if ignore_cols is None:
        ignore_cols = []

    st.subheader("Exploratory Data Analysis")
    eda_df = df.drop(columns=prediction_cols, errors="ignore")

    st.write("Data sample")
    st.dataframe(eda_df.head())

    st.write("Summary statistics")
    with st.expander("Show summary statistics table"):
        st.dataframe(eda_df.describe(include="all"))

    # ----------------------
    # Class Balance
    # ----------------------
    if ground_truth_col:
        st.subheader("Class Balance")
        class_counts = df[ground_truth_col].value_counts(normalize=True) * 100
        fig, ax = plt.subplots()
        class_counts.plot(kind="bar", ax=ax)
        ax.set_ylabel("Percentage")
        ax.set_title("Target Class Distribution")
        for i, v in enumerate(class_counts.values):
            ax.text(i, v + 0.5, f"{v:.1f}%", ha="center")
        st.pyplot(fig)

    # ----------------------
    # Missing Data Heatmap
    # ----------------------
    st.subheader("Missing Data Heatmap")
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.heatmap(eda_df.isnull(), cbar=False, yticklabels=False, ax=ax)
    ax.set_title("Missing Data Heatmap")
    st.pyplot(fig)

    # ----------------------
    # Feature Distributions
    # ----------------------
    st.subheader("Feature Distributions")
    numeric_features = eda_df.select_dtypes(include=[np.number]).columns
    categorical_features = eda_df.select_dtypes(exclude=[np.number]).columns

    if len(numeric_features) > 0:
        st.markdown("**Numeric Features**")
        for col in numeric_features[:5]:
            fig, ax = plt.subplots()
            sns.histplot(eda_df[col].dropna(), bins=30, kde=True, ax=ax)
            ax.set_title(f"Distribution of {col}")
            st.pyplot(fig)

    if len(categorical_features) > 0:
        st.markdown("**Categorical Features**")
        for col in categorical_features[:5]:
            fig, ax = plt.subplots()
            eda_df[col].value_counts().plot(kind="bar", ax=ax)
            ax.set_title(f"Distribution of {col}")
            st.pyplot(fig)

    # ----------------------
    # Boxplots vs Target
    # ----------------------
    if ground_truth_col and len(numeric_features) > 0:
        st.subheader("Boxplots by Target")
        for col in numeric_features[:3]:
            fig, ax = plt.subplots()
            sns.boxplot(x=df[ground_truth_col], y=df[col], ax=ax)
            ax.set_title(f"{col} by {ground_truth_col}")
            st.pyplot(fig)

    # ----------------------
    # Correlation Heatmap (Numeric Features)
    # ----------------------
    st.subheader("Correlation Heatmap (Numeric Features)")
    exclude_for_heatmap = set(ignore_cols)
    if sensitive_col:
        exclude_for_heatmap.add(sensitive_col)
    if ground_truth_col:
        exclude_for_heatmap.add(ground_truth_col)
    exclude_for_heatmap.update(prediction_cols)

    numeric_df = df.drop(columns=exclude_for_heatmap, errors="ignore").select_dtypes(include=[np.number])
    if numeric_df.empty:
        st.info("No numeric features available for correlation heatmap after exclusions.")
    else:
        try:
            corr = numeric_df.corr(numeric_only=True)
        except TypeError:
            corr = numeric_df.corr()
        do_annot = corr.shape[0] <= 12
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.heatmap(corr, annot=do_annot, cmap="coolwarm", ax=ax, fmt=".2f" if do_annot else "")
        ax.set_title("Feature Correlations")
        st.pyplot(fig)

    # ----------------------
    # Correlation with Target
    # ----------------------
    if ground_truth_col and len(numeric_features) > 0:
        st.subheader("Correlation of Numeric Features with Target")
        try:
            target_corr = df[numeric_features + [ground_truth_col]].corr()[ground_truth_col].drop(ground_truth_col)
            target_corr = target_corr.sort_values(key=lambda x: abs(x), ascending=False)
            fig, ax = plt.subplots(figsize=(8, 4))
            target_corr.plot(kind="bar", ax=ax)
            ax.set_title("Correlation with Target")
            st.pyplot(fig)
        except Exception:
            st.info("Could not compute correlations with target.")

    # ----------------------
    # Sensitive Attribute vs Target
    # ----------------------
    if sensitive_col and ground_truth_col:
        st.subheader("Sensitive Attribute vs Target")
        ct = pd.crosstab(df[sensitive_col], df[ground_truth_col], normalize="index")
        fig, ax = plt.subplots()
        ct.plot(kind="bar", stacked=True, ax=ax)
        ax.set_ylabel("Proportion")
        ax.set_title(f"{ground_truth_col} Distribution by {sensitive_col}")
        st.pyplot(fig)

    # ----------------------
    # Mutual Information
    # ----------------------
    if ground_truth_col and len(numeric_features) + len(categorical_features) > 0:
        st.subheader("Feature Importance via Mutual Information")
        try:
            X_mi = pd.get_dummies(df.drop(columns=[ground_truth_col] + prediction_cols, errors="ignore"), drop_first=True)
            y_mi = df[ground_truth_col]
            if y_mi.dtype == "object" or str(y_mi.dtype).startswith("category"):
                y_mi = LabelEncoder().fit_transform(y_mi)
            mi = mutual_info_classif(X_mi.fillna(0), y_mi, discrete_features="auto")
            mi_series = pd.Series(mi, index=X_mi.columns).sort_values(ascending=False).head(20)
            fig, ax = plt.subplots(figsize=(8, 4))
            mi_series.plot(kind="bar", ax=ax)
            ax.set_title("Mutual Information with Target")
            st.pyplot(fig)
        except Exception as e:
            st.info(f"Mutual information computation failed: {e}")

    # ----------------------
    # Cramér’s V Heatmap
    # ----------------------
    if len(categorical_features) > 1:
        st.subheader("Cramér’s V Heatmap (Categorical Associations)")
        cramers = pd.DataFrame(index=categorical_features, columns=categorical_features, dtype=float)
        for col1 in categorical_features:
            for col2 in categorical_features:
                if col1 == col2:
                    cramers.loc[col1, col2] = 1.0
                else:
                    try:
                        cramers.loc[col1, col2] = cramers_v(df[col1], df[col2])
                    except Exception:
                        cramers.loc[col1, col2] = np.nan
        fig, ax = plt.subplots(figsize=(6, 5))
        sns.heatmap(cramers.astype(float), annot=False, cmap="coolwarm", ax=ax)
        ax.set_title("Cramér’s V Heatmap (Categoricals)")
        st.pyplot(fig)

    # ----------------------
    # PCA 2D Projection
    # ----------------------
    if len(numeric_features) > 1:
        st.subheader("PCA Projection (2D)")
        try:
            X_pca = eda_df[numeric_features].fillna(0)
            pca = PCA(n_components=2)
            comps = pca.fit_transform(X_pca)
            fig, ax = plt.subplots()
            scatter = ax.scatter(
                comps[:, 0],
                comps[:, 1],
                c=df[ground_truth_col] if ground_truth_col else "blue",
                cmap="viridis",
                alpha=0.7
            )
            ax.set_title("PCA Projection (first 2 components)")
            if ground_truth_col:
                legend1 = ax.legend(*scatter.legend_elements(), title=ground_truth_col)
                ax.add_artist(legend1)
            st.pyplot(fig)
        except Exception as e:
            st.info(f"PCA projection failed: {e}")
