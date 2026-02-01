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
st.sidebar.title("Navigation")

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
