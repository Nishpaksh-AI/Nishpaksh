# home.py
import streamlit as st
import pandas as pd

# Page config
st.set_page_config(page_title="Nishpaksh", layout="centered")


st.markdown(""" 
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

    h4 {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
    }

    p, .stMarkdown p {
        color: var(--text-secondary) !important;
        font-size: 1rem !important;
        line-height: 1.7 !important;
        max-width: 75ch;
    }

    /* ======================================================
       LOGO SECTION
       ====================================================== */
    div[data-testid="column"] img {
        border-radius: 12px;
        box-shadow: var(--shadow-sm);
        transition: all 0.3s ease;
    }

    div[data-testid="column"] img:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-md);
    }

    /* ======================================================
       CARDS & CONTAINERS
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
       FILE UPLOADER
       ====================================================== */
    div[data-testid="stFileUploader"] {
        background: var(--bg-card) !important;
        border: 2px dashed var(--border) !important;
        border-radius: 12px !important;
        padding: 2rem !important;
        transition: all 0.3s ease;
    }

    div[data-testid="stFileUploader"]:hover {
        border-color: var(--primary) !important;
        background: var(--bg-hover) !important;
    }

    div[data-testid="stFileUploader"] label {
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
    }

    div[data-testid="stFileUploader"] section {
        border: none !important;
    }

    /* File uploader button */
    div[data-testid="stFileUploader"] button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        border: none !important;
        box-shadow: var(--shadow-sm) !important;
        transition: all 0.3s ease !important;
    }

    div[data-testid="stFileUploader"] button:hover {
        background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary) 100%) !important;
        transform: translateY(-2px);
        box-shadow: var(--shadow-md) !important;
    }

    /* ======================================================
       SELECTBOX
       ====================================================== */
    div[data-testid="stSelectbox"] {
        margin-bottom: 1.5rem !important;
    }

    div[data-testid="stSelectbox"] label {
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        margin-bottom: 0.5rem !important;
    }

    div[data-testid="stSelectbox"] > div > div {
        background: var(--bg-card) !important;
        border: 2px solid var(--border) !important;
        border-radius: 8px !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        transition: all 0.2s ease !important;
    }

    div[data-testid="stSelectbox"] > div > div:hover {
        border-color: var(--primary) !important;
    }

    div[data-testid="stSelectbox"] > div > div:focus-within {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
    }

    /* ======================================================
       DATAFRAME
       ====================================================== */
    div[data-testid="stDataFrame"] {
        border-radius: 12px !important;
        overflow: hidden;
        box-shadow: var(--shadow-md) !important;
        border: 1px solid var(--border) !important;
    }

    .dataframe {
        font-size: 0.95rem !important;
        border: none !important;
    }

    .dataframe thead tr th {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 1rem !important;
        border: none !important;
    }

    .dataframe tbody tr:nth-child(even) {
        background: var(--bg-section) !important;
    }

    .dataframe tbody tr:hover {
        background: var(--bg-hover) !important;
    }

    .dataframe tbody td {
        padding: 0.75rem 1rem !important;
        border-bottom: 1px solid var(--border) !important;
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
        font-size: 1.5rem !important;
    }

    section[data-testid="stSidebar"] li {
        border-radius: 8px !important;
        margin-bottom: 0.5rem !important;
        transition: all 0.2s ease !important;
    }

    section[data-testid="stSidebar"] li:hover {
        background: var(--bg-hover) !important;
    }

    section[data-testid="stSidebar"] a {
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        padding: 0.75rem 1rem !important;
        display: block !important;
        text-decoration: none !important;
        transition: all 0.2s ease !important;
    }

    section[data-testid="stSidebar"] a:hover {
        color: var(--primary) !important;
        padding-left: 1.5rem !important;
    }

    /* ======================================================
       ALERTS / STATUS MESSAGES
       ====================================================== */
    div[data-testid="stAlert"] {
        border-radius: 12px !important;
        border: none !important;
        box-shadow: var(--shadow-sm) !important;
        padding: 1.25rem 1.5rem !important;
        margin: 1rem 0 !important;
    }

    div[data-testid="stAlert"][data-baseweb="notification"][kind="info"] {
        background: linear-gradient(135deg, #dbeafe 0%, #e0f2fe 100%) !important;
        border-left: 5px solid var(--accent) !important;
        color: var(--text-primary) !important;
    }

    div[data-testid="stAlert"][data-baseweb="notification"][kind="success"] {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%) !important;
        border-left: 5px solid var(--success) !important;
        color: var(--text-primary) !important;
    }

    div[data-testid="stAlert"][data-baseweb="notification"][kind="warning"] {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%) !important;
        border-left: 5px solid var(--warning) !important;
        color: var(--text-primary) !important;
    }

    div[data-testid="stAlert"][data-baseweb="notification"][kind="error"] {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%) !important;
        border-left: 5px solid var(--danger) !important;
        color: var(--text-primary) !important;
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
       FORM INPUTS
       ====================================================== */
    input[type="text"],
    input[type="number"],
    input[type="email"],
    textarea {
        font-size: 1rem !important;
        line-height: 1.6 !important;
        border-radius: 8px !important;
        padding: 0.75rem 1rem !important;
        border: 2px solid var(--border) !important;
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
        transition: all 0.2s ease !important;
    }

    input[type="text"]:focus,
    input[type="number"]:focus,
    input[type="email"]:focus,
    textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
        outline: none !important;
    }

    /* Radio and checkbox accent color */
    input[type="radio"], 
    input[type="checkbox"] {
        accent-color: var(--primary) !important;
        width: 18px !important;
        height: 18px !important;
    }

    label {
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        font-size: 1rem !important;
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
    }
    </style>
""", unsafe_allow_html=True)

# ---- Branding: three logos (TEC - IIITD - MeitY) ----
LOGO_WIDTH = 300
tec_paths = ["tec.png", "tec.jpg", "assets/tec.png", "assets/tec.jpg"]
iiitd_paths = ["iiitd.png", "iiitd.jpg", "assets/iiitd.png", "assets/iiitd.jpg"]
meity_paths = ["meity.png", "meity.jpg", "assets/meity.png", "assets/meity.jpg"]

col_l, col_c, col_r = st.columns([1, 1, 1])

with col_l:  # TEC left
    shown = False
    for p in tec_paths:
        try:
            st.image(p, width=LOGO_WIDTH)
            shown = True
            break
        except Exception:
            continue
    if not shown: st.write("")

with col_c:  # IIITD center
    shown = False
    for p in iiitd_paths:
        try:
            st.image(p, width=LOGO_WIDTH)
            shown = True
            break
        except Exception:
            continue
    if not shown: st.write("")

with col_r:  # MeitY right
    shown = False
    for p in meity_paths:
        try:
            st.image(p, width=LOGO_WIDTH)
            shown = True
            break
        except Exception:
            continue
    if not shown: st.write("")

# ------------------ App Logic ------------------
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

