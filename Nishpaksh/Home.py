import streamlit as st
import pandas as pd

import base64

def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# ==================================================
# Page config
# ==================================================
st.set_page_config(page_title="Nishpaksh", layout="centered")

# ==================================================
# DESIGN ONLY 
# ==================================================
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
        margin-top: 200px;
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
logo_b64 = img_to_base64("nishpaksh_logo.png")

st.sidebar.markdown(
    f"""
    <div class="nishpaksh-logo">
        <img src="data:image/png;base64,{logo_b64}" width="150"/>
    </div>
    """,
    unsafe_allow_html=True,
)
# ==================================================
# ------------------ APP LOGIC ------------------
# ==================================================
st.title("Nishpaksh")

# --------------------------------------------------
# Initialize session state variables
# --------------------------------------------------
if "ground_truth" not in st.session_state:
    st.session_state["ground_truth"] = None

if "num_protected_attrs" not in st.session_state:
    st.session_state["num_protected_attrs"] = 1

# --------------------------------------------------
# File uploads (widget-only)
# --------------------------------------------------
data_file = st.file_uploader(
    "Upload tabular dataset (CSV)",
    type=["csv"],
    key="data_file_input",
)

model_file = st.file_uploader(
    "Upload trained model (.pkl or .joblib)",
    type=["pkl", "joblib"],
    key="model_file_input",
)

# --------------------------------------------------
# Dataset persistence (authoritative)
# --------------------------------------------------
if data_file is not None:
    try:
        df = pd.read_csv(data_file)

        # Detect dataset change
        if (
            "uploaded_data" not in st.session_state
            or not st.session_state["uploaded_data"].equals(df)
        ):
            st.session_state["uploaded_data"] = df
            
            # Reset config on new data
            st.session_state["ground_truth"] = None
            st.session_state["num_protected_attrs"] = 1
            # Clear any previous protected attributes
            for key in list(st.session_state.keys()):
                if key.startswith("protected_attribute_") or key.startswith("privileged_class_"):
                    del st.session_state[key]

    except Exception as e:
        st.error(f"Failed to read uploaded CSV: {e}")
        st.stop()

elif "uploaded_data" in st.session_state:
    df = st.session_state["uploaded_data"]
else:
    df = None

# --------------------------------------------------
# Configuration UI
# --------------------------------------------------
if df is not None:
    st.write("Data Preview")
    st.dataframe(df.head())

    columns = df.columns.tolist()

    # ------------------------------
    # Ground truth
    # ------------------------------
    gt_index = 0
    if st.session_state["ground_truth"] and st.session_state["ground_truth"] in columns:
        gt_index = columns.index(st.session_state["ground_truth"]) + 1

    gt = st.selectbox(
        "Select ground truth column",
        options=[""] + columns,
        index=gt_index,
        key="ground_truth_input",
    )

    if gt != "":
        st.session_state["ground_truth"] = gt

    # ------------------------------
    # Number of protected attributes
    # ------------------------------
    num = st.radio(
        "How many protected attributes are there?",
        options=[1, 2, 3],
        horizontal=True,
        index=[1, 2, 3].index(st.session_state["num_protected_attrs"]),
        key="num_protected_input",
    )

    st.session_state["num_protected_attrs"] = num

    # ------------------------------
    # Protected attributes
    # ------------------------------
    for i in range(st.session_state["num_protected_attrs"]):
        st.markdown(f"### Protected Attribute {i + 1}")

        # Get saved values
        saved_attr = st.session_state.get(f"protected_attribute_{i+1}", None)
        saved_priv = st.session_state.get(f"privileged_class_{i+1}", None)

        # Attribute selectbox
        attr_index = 0
        if saved_attr and saved_attr in columns:
            attr_index = columns.index(saved_attr) + 1

        attr = st.selectbox(
            f"Select protected attribute {i + 1}",
            options=[""] + columns,
            index=attr_index,
            key=f"protected_attr_input_{i}",
        )

        if attr != "":
            st.session_state[f"protected_attribute_{i+1}"] = attr

            # Get unique values for this attribute
            values = df[attr].dropna().astype(str).unique().tolist()

            # Privileged class selectbox
            priv_index = 0
            if saved_priv and saved_priv in values:
                priv_index = values.index(saved_priv) + 1

            priv = st.selectbox(
                f"Select privileged class for {attr}",
                options=[""] + values,
                index=priv_index,
                key=f"privileged_value_input_{i}",
            )

            if priv != "":
                st.session_state[f"privileged_class_{i+1}"] = priv

# --------------------------------------------------
# Model file persistence
# --------------------------------------------------
if model_file is not None:
    st.session_state["model_file"] = model_file

# --------------------------------------------------
# DEBUG — AUTHORITATIVE STATE
# --------------------------------------------------
st.markdown("---")
st.subheader("Authoritative Configuration")

# Build display dict
config_display = {
    "ground_truth": st.session_state.get("ground_truth"),
    "num_protected_attrs": st.session_state.get("num_protected_attrs"),
}

for i in range(1, 4):
    if f"protected_attribute_{i}" in st.session_state:
        config_display[f"protected_attribute_{i}"] = st.session_state[f"protected_attribute_{i}"]
    if f"privileged_class_{i}" in st.session_state:
        config_display[f"privileged_class_{i}"] = st.session_state[f"privileged_class_{i}"]

config_display["uploaded_data_present"] = "uploaded_data" in st.session_state
config_display["model_file_present"] = "model_file" in st.session_state

st.json(config_display)

# --------------------------------------------------
# Sidebar status
# --------------------------------------------------


# Check if configuration is complete
config_complete = (
    st.session_state.get("ground_truth") is not None
    and st.session_state.get("model_file") is not None
)

# Check if all protected attributes are configured
for i in range(1, st.session_state.get("num_protected_attrs", 1) + 1):
    if (
        f"protected_attribute_{i}" not in st.session_state
        or f"privileged_class_{i}" not in st.session_state
    ):
        config_complete = False
        break

if config_complete:
    st.sidebar.success("Configuration complete")
else:
    st.sidebar.warning("Complete configuration on Home page")

# --------------------------------------------------
# Partner Logos in Sidebar
# --------------------------------------------------
st.sidebar.markdown("---")

LOGO_WIDTH = 70
tec_paths = ["tec.png", "tec.jpg", "assets/tec.png", "assets/tec.jpg"]
iiitd_paths = ["iiitd.png", "iiitd.jpg", "assets/iiitd.png", "assets/iiitd.jpg"]
meity_paths = ["meity.png", "meity.jpg", "assets/meity.png", "assets/meity.jpg"]

col1, col2, col3 = st.sidebar.columns(3)

with col1:
    for p in tec_paths:
        try:
            st.image(p, use_container_width =True)
            break
        except Exception:
            pass

with col2:
    for p in iiitd_paths:
        try:
            st.image(p, use_container_width =True)
            break
        except Exception:
            pass

with col3:
    for p in meity_paths:
        try:
            st.image(p,use_container_width =True)
            break
        except Exception:
            pass
