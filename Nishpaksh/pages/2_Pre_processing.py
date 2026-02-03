"""
Pre-processing page — DATA & MODEL PREPARATION ONLY

Responsibilities:
- Light EDA (preview only)
- Leakage / proxy check (preview only)
- Train baseline models and append predictions
- Collect user-authored system descriptions (verbatim)
- Store all outputs in st.session_state
- NO report generation
- NO filesystem writes
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(layout="wide")
st.title("Pre-processing — Data & Model Preparation")

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
# Preconditions (UPDATED: flat authoritative keys)
# --------------------------------------------------
if "uploaded_data" not in st.session_state or not isinstance(
    st.session_state["uploaded_data"], pd.DataFrame
):
    st.warning("Upload a dataset on the Home page before proceeding.")
    st.stop()

df = st.session_state["uploaded_data"]

ground_truth = st.session_state.get("ground_truth")
num_protected = st.session_state.get("num_protected_attrs")

if not isinstance(ground_truth, str) or ground_truth == "":
    st.warning("Ground truth column not set on Home page.")
    st.stop()

if not isinstance(num_protected, int) or num_protected < 1:
    st.warning("Protected attributes not configured on Home page.")
    st.stop()

# --------------------------------------------------
# Reconstruct protected attributes (AUTHORITATIVE)
# --------------------------------------------------
protected_attrs = []

for i in range(1, num_protected + 1):
    attr = st.session_state.get(f"protected_attribute_{i}")
    priv = st.session_state.get(f"privileged_class_{i}")

    if not isinstance(attr, str) or not isinstance(priv, str):
        st.warning(f"Protected attribute {i} not fully configured.")
        st.stop()

    protected_attrs.append(
        {
            "attribute": attr,
            "privileged_class": priv,
        }
    )

# --------------------------------------------------
# Initialize session_state container (once)
# --------------------------------------------------
if "preproc" not in st.session_state:
    st.session_state["preproc"] = {
        "ignore_cols": [],
        "eda_done": False,
        "leakage": {},
        "models": None,
        "user_narratives": {},
        "completed": False,
    }

PREPROC = st.session_state["preproc"]

# --------------------------------------------------
# Section selector
# --------------------------------------------------
section = st.sidebar.radio(
    "Pre-processing section",
    [
        "Exploratory Data Analysis",
        "Leakage / Proxy Check",
        "Model Training & Prediction Append",
        
    ],
)

# ==================================================
# 1. Exploratory Data Analysis (UNCHANGED)
# ==================================================
if section == "Exploratory Data Analysis":
    st.subheader("Exploratory Data Analysis (Preview)")

    st.dataframe(df.head())

    with st.expander("Summary statistics"):
        st.dataframe(df.describe(include="all"))

    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.shape[1] > 1:
        fig, ax = plt.subplots(figsize=(7, 5))
        sns.heatmap(numeric_df.corr(), cmap="coolwarm", ax=ax)
        ax.set_title("Numeric feature correlations")
        st.pyplot(fig)
        plt.close(fig)

    PREPROC["eda_done"] = True

# ==================================================
# 2. Leakage / Proxy Check (UPDATED ONLY HERE)
# ==================================================
elif section == "Leakage / Proxy Check":
    st.subheader("Sensitive Attribute Leakage / Proxy Check")

    ignore_cols = st.multiselect(
        "Columns to exclude",
        options=df.columns.tolist(),
        default=PREPROC.get("ignore_cols", []),
    )
    PREPROC["ignore_cols"] = ignore_cols

    leakage_results = {}

    for p in protected_attrs:
        sens_col = p["attribute"]
        priv_class = p["privileged_class"]

        st.markdown(f"### Proxy analysis for `{sens_col}`")
        st.caption(f"Privileged class: `{priv_class}`")

        feature_cols = [
            c
            for c in df.columns
            if c not in ignore_cols
            and c != sens_col
            and c != ground_truth
        ]

        if not feature_cols:
            st.warning("No usable features after exclusions.")
            continue

        X = pd.get_dummies(df[feature_cols].fillna("NA"))
        y = df[sens_col].astype(str)

        if y.nunique() < 2:
            st.warning("Sensitive attribute has fewer than two unique values.")
            continue

        y_enc = LabelEncoder().fit_transform(y)

        from sklearn.feature_selection import mutual_info_classif

        mi = mutual_info_classif(
            X,
            y_enc,
            discrete_features="auto",
            random_state=42,
        )

        mi_df = (
            pd.DataFrame(
                {
                    "feature": X.columns,
                    "mutual_information": mi,
                }
            )
            .sort_values("mutual_information", ascending=False)
            .head(20)
        )

        # ---- Plot (proxy strength) ----
        fig, ax = plt.subplots(figsize=(7, 4))
        mi_df.iloc[::-1].set_index("feature")["mutual_information"].plot(
            kind="barh", ax=ax
        )
        ax.set_title(f"Top proxy features for `{sens_col}`")
        ax.set_xlabel("Mutual Information")
        st.pyplot(fig)
        plt.close(fig)

        st.dataframe(mi_df, use_container_width=True)

        leakage_results[sens_col] = {
            "privileged_class": priv_class,
            "top_proxy_features": mi_df,
        }

    PREPROC["leakage"] = leakage_results

# ==================================================
# 3. Model Training & Prediction Append (UNCHANGED)
# ==================================================
elif section == "Model Training & Prediction Append":
    st.subheader("Baseline Model Training")

    model_map = {
        "LogisticRegression": LogisticRegression(max_iter=200),
        "RandomForest": RandomForestClassifier(n_estimators=200, random_state=42),
        "GradientBoosting": GradientBoostingClassifier(random_state=42),
        "KNN": KNeighborsClassifier(),
        "SVC": SVC(probability=True, random_state=42),
    }

    models_to_run = st.multiselect(
        "Select models to train",
        list(model_map.keys()),
        default=list(model_map.keys()),
    )

    ignore_cols = PREPROC.get("ignore_cols", [])

    X = df.drop(columns=ignore_cols + [ground_truth], errors="ignore")
    y = LabelEncoder().fit_transform(df[ground_truth].astype(str))

    num_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = X.select_dtypes(exclude=[np.number]).columns.tolist()

    preprocessor = ColumnTransformer(
        [
            ("num", Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())]), num_cols),
            ("cat", Pipeline([("imp", SimpleImputer(strategy="most_frequent")), ("oh", OneHotEncoder(handle_unknown="ignore"))]), cat_cols),
        ]
    )

    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=42)

    results = []

    for name in models_to_run:
        model = model_map[name]
        pipe = Pipeline([("prep", preprocessor), ("clf", model)])
        pipe.fit(Xtr, ytr)

        preds = pipe.predict(X)
        df[f"predicted_{name}"] = preds

        yhat = pipe.predict(Xte)
        results.append(
            {
                "Model": name,
                "Accuracy": accuracy_score(yte, yhat),
                "Precision": precision_score(yte, yhat, zero_division=0),
                "Recall": recall_score(yte, yhat, zero_division=0),
                "F1": f1_score(yte, yhat, zero_division=0),
            }
        )

    res_df = pd.DataFrame(results)
    st.dataframe(res_df.set_index("Model").style.format("{:.3f}"))

    st.session_state["uploaded_data"] = df
    PREPROC["models"] = res_df


# --------------------------------------------------
# Footer
# --------------------------------------------------
st.markdown("---")
st.caption(
    "Pre-processing page stores structured evidence and user-authored text only. "
    "Final Report page will compile all sections deterministically."
)
