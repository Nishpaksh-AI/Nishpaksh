"""
Survey page — INPUT ONLY (governance risk assessment)

Responsibilities:
- Render governance / audit survey using utils.survey.render_survey()


Hard rules:
- No DOCX / PDF generation
- No filesystem writes
- No report logic
"""

import streamlit as st
import matplotlib.pyplot as plt
import traceback
from typing import Dict, Any




# --------------------------------------------------
# Import survey renderer (unchanged)
# --------------------------------------------------
try:
    from utils.survey import render_survey
except Exception:
    render_survey = None


# --------------------------------------------------
# Helpers
# --------------------------------------------------
def extract_governance_outputs(submission: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract and normalize governance-risk outputs from survey submission.
    This function is CONTRACT-ALIGNED with utils/survey.py.
    """
    if not isinstance(submission, dict):
        raise ValueError("Invalid survey submission format")

    total_risk = submission.get("total_risk_score")
    risk_category = submission.get("risk_category")
    proxy_subscores = submission.get("subscores", {})
    answers = submission.get("answers", {})

    # ---- compute section-level average risk (1–5 scale) ----
    section_avg_risk: Dict[str, float] = {}
    for section, responses in answers.items():
        risk_sum = 0
        count = 0
        for resp in responses.values():
            # utils.survey already excluded "Not Applicable" during scoring,
            # but we stay defensive here.
            from utils.survey import get_risk_score
            score = get_risk_score(resp)
            if score > 0:
                risk_sum += score
                count += 1
        section_avg_risk[section] = (risk_sum / count) if count > 0 else 0.0

    return {
        "total_risk_score": float(total_risk) if total_risk is not None else None,
        "risk_category": risk_category,
        "proxy_subscores": proxy_subscores,
        "section_avg_risk": section_avg_risk,
        "raw_submission": submission,
    }


def make_proxy_risk_plot(proxy_scores: Dict[str, float]):
    """
    Preview plot: Proxy-bucket risk contributions (0–20 each).
    This matches the governance aggregation logic exactly.
    """
    labels = list(proxy_scores.keys())
    values = [proxy_scores[k] for k in labels]

    fig, ax = plt.subplots(figsize=(7.5, 3.5))
    y = range(len(labels))

    ax.barh(y, values)
    ax.set_yticks(y)
    ax.set_yticklabels([l.replace("_", " ").title() for l in labels])
    ax.set_xlim(0, 20)
    ax.invert_yaxis()

    for i, v in enumerate(values):
        ax.text(v + 0.4, i, f"{v:.0f}", va="center")

    ax.set_title("Governance Risk Drivers (Proxy Contributions)")
    ax.set_xlabel("Risk Contribution (0–20 per proxy)")
    plt.tight_layout()
    return fig


# --------------------------------------------------
# Streamlit Page
# --------------------------------------------------
st.set_page_config(layout="wide")
st.title("Survey — Governance & Audit Risk Assessment")
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
    h1, h2, h3 {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
        letter-spacing: -0.02em;
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
if render_survey is None:
    st.error("Survey renderer not available. Ensure utils/survey.py exports render_survey().")
    st.stop()

# --------------------------------------------------
# Render Survey
# --------------------------------------------------
try:
    submission = render_survey(embedded=False, require_identity=False)
except Exception:
    st.error("Survey renderer raised an exception.")
    st.code(traceback.format_exc())
    st.stop()

# Survey not finished yet
if not submission:
    st.info("Please complete and submit the survey to proceed.")
    st.stop()

st.success("Survey completed successfully.")

# --------------------------------------------------
# Normalize + Store Outputs (ONCE)
# --------------------------------------------------
if not st.session_state.get("survey_completed"):

    outputs = extract_governance_outputs(submission)

    st.session_state["survey_outputs"] = outputs

    # minimal plotting payload (no raw submission duplication)
    st.session_state["survey_plot_data"] = {
        "proxy_subscores": outputs["proxy_subscores"]
    }

    st.session_state["survey_completed"] = True

# --------------------------------------------------
# Display Stored Summary
# --------------------------------------------------
survey_outputs = st.session_state.get("survey_outputs", {})


# --------------------------------------------------
# Preview: Proxy Risk Drivers (Ephemeral)
# --------------------------------------------------
plot_data = st.session_state.get("survey_plot_data")

if plot_data and plot_data.get("proxy_subscores"):
    st.subheader("Risk Driver Preview")
    fig = make_proxy_risk_plot(plot_data["proxy_subscores"])
    st.pyplot(fig)
    plt.close(fig)
else:
    st.info("No proxy-level risk data available for visualization.")

# --------------------------------------------------
# Lock Notice
# --------------------------------------------------
st.markdown("---")
st.caption(
    "✔ Survey results are locked and stored for downstream reporting. "
    "To modify responses, reset the session."
)
