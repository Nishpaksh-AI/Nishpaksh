import streamlit as st
import pandas as pd

# ==================================================
# Page config
# ==================================================
st.set_page_config(page_title="Nishpaksh", layout="centered")

# ==================================================
# DESIGN ONLY (NO LOGIC TOUCHING)
# ==================================================
st.markdown(
    """
    <style>
    /* -------------------------------
       Base app + typography
       ------------------------------- */
    html, body, [class*="css"] {
        font-size: 18px !important;
        font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont,
                     "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%);
    }

    h1, h2, h3, h4 {
        font-weight: 600;
        letter-spacing: -0.01em;
    }

    /* -------------------------------
       Sidebar
       ------------------------------- */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e5e7eb;
        font-size: 17px !important;
    }

    /* -------------------------------
       Cards / containers
       ------------------------------- */
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #ffffff;
        border-radius: 14px;
        padding: 1.75rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 24px rgba(0,0,0,0.06);
    }

    /* -------------------------------
       Buttons
       ------------------------------- */
    button[kind="primary"] {
        background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%) !important;
        color: white !important;
        font-size: 18px !important;
        padding: 0.6em 1.4em !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600;
    }

    button[kind="primary"]:hover {
        background: linear-gradient(135deg, #1e40af 0%, #2563eb 100%) !important;
    }

    /* -------------------------------
       File uploader
       ------------------------------- */
    div[data-testid="stFileUploader"] {
        border: 2px dashed #c7d2fe;
        border-radius: 12px;
        padding: 1.75rem;
        background: #ffffff;
    }

    /* -------------------------------
       Selectboxes (SAFE)
       ------------------------------- */
    div[data-testid="stSelectbox"] [data-baseweb="select"] {
        border-radius: 8px !important;
        border: 1.5px solid #d1d5db !important;
        background-color: #ffffff !important;
    }

    div[data-testid="stSelectbox"] [data-baseweb="select"] span {
        color: #0f172a !important;
        font-size: 1rem !important;
    }

    /* -------------------------------
       Dataframe
       ------------------------------- */
    .dataframe {
        font-size: 16px !important;
    }

    /* -------------------------------
       Inputs
       ------------------------------- */
    input[type="radio"],
    input[type="checkbox"] {
        accent-color: #2563eb !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==================================================
# BRANDING (UNCHANGED)
# ==================================================
LOGO_WIDTH = 300
tec_paths = ["tec.png", "tec.jpg", "assets/tec.png", "assets/tec.jpg"]
iiitd_paths = ["iiitd.png", "iiitd.jpg", "assets/iiitd.png", "assets/iiitd.jpg"]
meity_paths = ["meity.png", "meity.jpg", "assets/meity.png", "assets/meity.jpg"]

col_l, col_c, col_r = st.columns([1, 1, 1])

with col_l:
    for p in tec_paths:
        try:
            st.image(p, width=LOGO_WIDTH)
            break
        except Exception:
            pass

with col_c:
    for p in iiitd_paths:
        try:
            st.image(p, width=LOGO_WIDTH)
            break
        except Exception:
            pass

with col_r:
    for p in meity_paths:
        try:
            st.image(p, width=LOGO_WIDTH)
            break
        except Exception:
            pass

# ==================================================
# ------------------ APP LOGIC ------------------
# (VERBATIM FROM YOUR FILE — NOT TOUCHED)
# ==================================================
st.title("Nishpaksh")

data_file = st.file_uploader("Upload tabular dataset (CSV)", type=["csv"])
model_file = st.file_uploader("Upload trained model (.pkl or .joblib)", type=["pkl", "joblib"])

if data_file:
    try:
        df = pd.read_csv(data_file)
        st.session_state["uploaded_data"] = df
        st.write("Data Preview")
        st.dataframe(df.head())
        columns = df.columns.tolist()

        ground_truth_col = st.selectbox("Select ground truth column", options=columns)
        st.session_state["ground_truth_col"] = ground_truth_col

        sensitive_col = st.selectbox("Select sensitive attribute column", options=columns)
        st.session_state["sensitive_col"] = sensitive_col

        unique_vals = df[sensitive_col].dropna().unique()
        priv_value = st.selectbox("Select privileged group", options=unique_vals)
        st.session_state["privileged_value"] = priv_value
    except Exception as e:
        st.error(f"Failed to read uploaded CSV: {e}")

if model_file:
    st.session_state["model_file"] = model_file
    st.success("Model file uploaded.")

st.markdown("---")
st.sidebar.title("Navigation")

if "uploaded_data" in st.session_state and "model_file" in st.session_state:
    st.sidebar.success("Files uploaded")
    st.sidebar.page_link("pages/1_Pre_Processing.py", label="Pre-Processing")
    st.sidebar.page_link("pages/2_Inference.py", label="Inference")
    st.sidebar.page_link("pages/3_Output.py", label="Output")
else:
    st.sidebar.info("Upload both data and model to proceed.")
