import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(page_title="Nishpaksh", layout="centered")

#css and html block
st.markdown(""" 
    <style>
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
        
        --text-primary: #0f172a;
        --text-secondary: #475569;
        --text-muted: #64748b;
    }

    * {
        font-family: 'Inter', sans-serif !important;
    }

    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e0f2fe 100%);
    }

    /* ================= SELECTBOX ================= */

    div[data-testid="stSelectbox"] {
        margin-bottom: 1.5rem !important;
    }

    div[data-testid="stSelectbox"] label {
        font-weight: 600 !important;
        color: var(--text-primary) !important;
    }

    /* BaseWeb select container */
    div[data-testid="stSelectbox"] [data-baseweb="select"] {
        background: var(--bg-card) !important;
        border: 2px solid var(--border) !important;
        border-radius: 8px !important;
    }

    /* Selected value text */
    div[data-testid="stSelectbox"] [data-baseweb="select"] span {
        color: var(--text-primary) !important;
        font-size: 1rem !important;
    }

    /* Input height & alignment */
    div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
        min-height: 44px !important;
        display: flex;
        align-items: center;
    }

    div[data-testid="stSelectbox"] [data-baseweb="select"]:hover {
        border-color: var(--primary) !important;
    }

    div[data-testid="stSelectbox"] [data-baseweb="select"]:focus-within {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15) !important;
    }

    </style>
""", unsafe_allow_html=True)

# ------------------ Main Application ------------------

st.markdown("## Upload Files")

if "data_uploaded" not in st.session_state:
    st.session_state["data_uploaded"] = False

if "model_uploaded" not in st.session_state:
    st.session_state["model_uploaded"] = False

data_file = st.file_uploader("Upload tabular dataset (CSV)", type=["csv"])
model_file = st.file_uploader("Upload trained model (.pkl or .joblib)", type=["pkl", "joblib"])

if data_file and not st.session_state["data_uploaded"]:
    df = pd.read_csv(data_file)
    st.session_state["uploaded_data"] = df
    st.session_state["data_uploaded"] = True
    st.rerun()

if model_file and not st.session_state["model_uploaded"]:
    st.session_state["model_file"] = model_file
    st.session_state["model_uploaded"] = True
    st.success("Model file uploaded successfully")

if "uploaded_data" in st.session_state:
    df = st.session_state["uploaded_data"]

    st.markdown("## Data Configuration")
    st.dataframe(df.head())

    columns = df.columns.tolist()

    ground_truth_col = st.selectbox(
        "Select ground truth column",
        options=columns,
        key="ground_truth_col"
    )

    sensitive_col = st.selectbox(
        "Select sensitive attribute column",
        options=columns,
        key="sensitive_col"
    )

    if sensitive_col:
        priv_value = st.selectbox(
            "Select privileged group",
            options=df[sensitive_col].dropna().unique().tolist(),
            key="privileged_value"
        )

        if ground_truth_col and sensitive_col and priv_value is not None:
            st.success("Configuration Complete")

st.sidebar.title("Navigation")

if "uploaded_data" in st.session_state and "model_file" in st.session_state:
    st.sidebar.success("Files uploaded")
    st.sidebar.page_link("pages/0_survey.py", label="Survey")
    st.sidebar.page_link("pages/1_thresholds_and_metrics.py", label="Thresholds and metrics")
    st.sidebar.page_link("pages/2_pre_processing.py", label="Inference")
    st.sidebar.page_link("pages/3_inference.py", label="Inference")
    st.sidebar.page_link("pages/4_results.py", label="Results")
    st.sidebar.page_link("pages/5_report.py", label="Report")


    
else:
    st.sidebar.info("Upload both data and model to proceed.")


