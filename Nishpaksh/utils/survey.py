# utils/survey.py
"""
Refined multi-page survey module for Nishpaksh with improved options.
- Each question now has only ONE zero-weight option (typically "Not Applicable")
- Options are more intuitive and aligned with the questions asked
- Risk scoring from 1 (lowest risk) to 5 (highest risk), with 0 for N/A only
"""

import streamlit as st
import json
import os
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

SURVEY_KEY = "survey_submission"
SURVEY_FOLDER = "survey_responses"

def _ensure_folder(folder: str):
    os.makedirs(folder, exist_ok=True)

def save_submission(payload: dict, folder: str = SURVEY_FOLDER) -> str:
    """Save the survey submission to disk as JSON and return filename."""
    _ensure_folder(folder)
    fname = f"{folder}/submission_{payload['submission_id']}.json"
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)
    return fname

def map_score_to_category(total: float) -> str:
    if total >= 80:
        return "Very High"
    if total >= 60:
        return "High"
    if total >= 40:
        return "Medium"
    if total >= 20:
        return "Low"
    return "Very Low"

# ---------- REFINED SURVEY_SECTIONS ----------
SURVEY_SECTIONS = {
    "Data": {
        "description": "Bias in this stage can arise from various activities, including data gathering, augmentation, merging, cleaning, pre-processing, encoding, and splitting.",
        "questions": {
            "historical_bias": {
                "question": "Does the data reflect historical or societal biases that could lead to unfair outcomes for certain groups?",
                "type": "Process Factor",
                "options": ["No Historical Bias Detected", "Minor Historical Bias Present", "Moderate Historical Bias Present", "Significant Historical Bias Present", "Severe Historical Bias Present", "Not Applicable"]
            },
            "data_relevance": {
                "question": "Is the data directly relevant to the specific use case and context of the AI model?",
                "type": "Process Factor",
                "options": ["Highly Relevant and Aligned", "Mostly Relevant", "Somewhat Relevant", "Minimally Relevant", "Not Relevant", "Not Applicable"]
            },
            "representation": {
                "question": "Are there any groups or populations that are under-represented in the dataset?",
                "type": "Process Factor",
                "options": ["All Groups Well Represented", "Minor Under-representation", "Moderate Under-representation", "Significant Under-representation", "Severe Under-representation", "Not Applicable"]
            },
            "completeness": {
                "question": "Is the data complete, or does it suffer from missing values or inputs from uncalibrated sources?",
                "type": "Process Factor",
                "options": ["Highly Complete and Validated", "Mostly Complete", "Somewhat Complete", "Significant Gaps Present", "Severe Incompleteness", "Not Applicable"]
            },
            "retraining_data": {
                "question": "If the model is retrained, is the new data checked for potential biases before being incorporated?",
                "type": "Process Factor",
                "options": ["Always Thoroughly Checked", "Usually Checked", "Sometimes Checked", "Rarely Checked", "Never Checked", "Not Applicable"]
            },
            "imputation": {
                "question": "How are missing data points handled? Are they filled in using imputation methods that might introduce or amplify bias?",
                "type": "Technical Factor",
                "options": ["Bias-Aware Methods Used", "Standard Statistical Methods", "Basic Imputation Methods", "Ad-hoc Imputation", "No Systematic Approach", "Not Applicable"]
            },
            "data_removal": {
                "question": "Have any duplicate data or outliers been removed? What was the rationale and could this process disproportionately affect certain groups?",
                "type": "Technical Factor",
                "options": ["Bias-Aware Removal Process", "Systematic Evidence-Based Removal", "Basic Statistical Removal", "Ad-hoc Removal", "No Systematic Removal", "Not Applicable"]
            },
            "data_transformation": {
                "question": "What methods are used for feature selection, normalization, and discretization? Could these choices introduce bias?",
                "type": "Technical Factor",
                "options": ["Bias-Aware Transformation Methods", "Standard Statistical Methods", "Basic Transformation Methods", "Ad-hoc Methods", "No Systematic Methods", "Not Applicable"]
            },
            "annotations": {
                "question": "Are there any inconsistencies in data annotations or labeling that could introduce bias?",
                "type": "Technical Factor",
                "options": ["No Inconsistencies Detected", "Minor Inconsistencies", "Moderate Inconsistencies", "Significant Inconsistencies", "Severe Inconsistencies", "Not Applicable"]
            },
            "proxies": {
                "question": "Are any proxies used for sensitive attributes (e.g., using zip code as a proxy for race)?",
                "type": "Technical Factor",
                "options": ["No Proxies Used", "Validated Non-Biased Proxies", "Some Unvalidated Proxies", "Multiple Unvalidated Proxies", "Many High-Risk Proxies", "Not Applicable"]
            },
            "causal_relationships": {
                "question": "Have any causal relationships in the data been assumed but not validated?",
                "type": "Technical Factor",
                "options": ["All Relationships Validated", "Most Relationships Validated", "Some Relationships Validated", "Few Relationships Validated", "No Validation Performed", "Not Applicable"]
            }
        }
    },
    "Model": {
        "description": "Bias can be introduced during the modeling phase through choices related to features, training, and testing.",
        "questions": {
            "pretrained_models": {
                "question": "If a pre-trained model is used, has it been vetted for biases inherited from its original training data?",
                "type": "Process Factor",
                "options": ["Thoroughly Vetted for Bias", "Partially Vetted", "Basic Assessment Done", "Minimal Assessment", "Not Vetted", "Not Applicable"]
            },
            "model_quality": {
                "question": "Is there an assessment of the quality of associated or connected models that could influence this system?",
                "type": "Process Factor",
                "options": ["Comprehensive Quality Assessment", "Substantial Assessment", "Basic Assessment", "Minimal Assessment", "No Assessment", "Not Applicable"]
            },
            "training_extent": {
                "question": "Has the duration or extent of model training been evaluated for its potential to introduce bias?",
                "type": "Process Factor",
                "options": ["Thoroughly Evaluated", "Substantially Evaluated", "Partially Evaluated", "Minimally Evaluated", "Not Evaluated", "Not Applicable"]
            },
            "objective_definition": {
                "question": "How is the model's objective defined? Could this definition inadvertently disadvantage certain groups?",
                "type": "Process Factor",
                "options": ["Bias-Aware Fair Objective", "Standard Objective with Fairness Review", "Standard Objective", "Potentially Problematic Objective", "High-Risk Objective", "Not Applicable"]
            },
            "adversarial_exposure": {
                "question": "Is the model exposed to adversarial attacks or data poisoning through system feedback processes?",
                "type": "Process Factor",
                "options": ["Well Protected Against Attacks", "Moderately Protected", "Basic Protection", "Minimal Protection", "Highly Vulnerable", "Not Applicable"]
            },
            "model_choice": {
                "question": "What was the rationale for choosing the specific model architecture, including the number of layers?",
                "type": "Technical Factor",
                "options": ["Bias-Aware Architecture Selection", "Performance-Based with Fairness Review", "Performance-Based Selection", "Standard Architecture Choice", "Ad-hoc Choice", "Not Applicable"]
            },
            "feature_choices": {
                "question": "How were features selected? Do these choices rely on inferences or proxies that could be biased?",
                "type": "Technical Factor",
                "options": ["Bias-Aware Feature Selection", "Systematic Selection with Review", "Standard Statistical Selection", "Basic Feature Selection", "Ad-hoc Selection", "Not Applicable"]
            },
            "training_parameters": {
                "question": "How were the seed, epoch, batch size, learning rate, and dropouts selected?",
                "type": "Technical Factor",
                "options": ["Systematic Optimization with Validation", "Grid Search or Similar", "Basic Hyperparameter Tuning", "Minimal Tuning", "Default Values Used", "Not Applicable"]
            },
            "optimization": {
                "question": "What activation, loss, and optimizer choices were made, and how might they impact fairness?",
                "type": "Technical Factor",
                "options": ["Fairness-Aware Choices", "Performance Optimized with Fairness Review", "Standard Optimization Choices", "Basic Choices", "Default Choices", "Not Applicable"]
            },
            "testing_metrics": {
                "question": "What metrics are used for testing the model's performance?",
                "type": "Technical Factor",
                "options": ["Comprehensive Fairness and Performance Metrics", "Performance with Some Fairness Metrics", "Standard Performance Metrics Only", "Basic Metrics Only", "Minimal Metrics", "Not Applicable"]
            },
            "tuning": {
                "question": "What choices were made during the model tuning process?",
                "type": "Technical Factor",
                "options": ["Bias-Aware Systematic Tuning", "Systematic Performance Tuning", "Standard Tuning Process", "Basic Tuning", "Ad-hoc Tuning", "Not Applicable"]
            },
            "performance_monitoring": {
                "question": "What metrics are used for monitoring the model's performance over time?",
                "type": "Technical Factor",
                "options": ["Comprehensive Fairness and Performance Monitoring", "Performance with Fairness Tracking", "Standard Performance Monitoring", "Basic Monitoring", "Minimal or No Monitoring", "Not Applicable"]
            }
        }
    },
    "Pipeline & Infrastructure": {
        "description": "Biases can also originate from the pipelines and infrastructure due to choices related to architecture, robustness, and optimization.",
        "questions": {
            "pipeline_quality": {
                "question": "Are there known errors or defects in the data or model pipelines?",
                "type": "Process Factor",
                "options": ["No Known Defects", "Minor Defects Present", "Moderate Defects Present", "Significant Defects Present", "Severe Defects Present", "Not Applicable"]
            },
            "uncertainty_calibrations": {
                "question": "How well the uncertainty is calibrated within the pipeline?",
                "type": "Process Factor",
                "options": ["Well calibrated with validation", "Moderately calibrated", "Basic calibration", "Minimal calibration", "Not calibrated", "Not Applicable"]
            },
            "robustness": {
                "question": "Is the pipeline robust against potential data leakage or security exposures?",
                "type": "Process Factor",
                "options": ["Highly Robust with Multiple Safeguards", "Moderately Robust", "Basic Robustness Measures", "Minimal Protection", "Vulnerable to Leakage", "Not Applicable"]
            },
            "optimization_choices": {
                "question": "What optimization choices have been made for throughput, latency, scalability, and resource usage? Could these choices impact system fairness?",
                "type": "Technical Factor",
                "options": ["Fairness-Aware Optimization", "Balanced Performance and Fairness", "Performance-Focused Optimization", "Basic Optimization", "Ad-hoc Optimization", "Not Applicable"]
            }
        }
    },
    "Interface & Integrations": {
        "description": "Bias can arise from the user interface (UI/UX) and how the AI system integrates with other tools, potentially leading to disparate impacts.",
        "questions": {
            "accessibility": {
                "question": "Has the system been designed considering social and technological accessibility for all users, including those with disabilities or specific hardware requirements?",
                "type": "Process Factor",
                "options": ["Fully Accessible to All Users", "Mostly Accessible", "Partially Accessible", "Minimally Accessible", "Limited Accessibility", "Not Applicable"]
            },
            "integration_quality": {
                "question": "Have potential defects, failures, or adversities in the system's integration points been examined?",
                "type": "Process Factor",
                "options": ["Thoroughly Examined and Tested", "Substantially Examined", "Partially Examined", "Minimally Examined", "Not Examined", "Not Applicable"]
            },
            "design_preferences": {
                "question": "Does the interface design (e.g., position of choices) unfavorably affect minority-related options?",
                "type": "Technical Factor",
                "options": ["No Unfavorable Effects Detected", "Minor Potential Effects", "Moderate Unfavorable Effects", "Significant Unfavorable Effects", "Severe Unfavorable Effects", "Not Applicable"]
            },
            "nudges_deception": {
                "question": "Does the user choice architecture employ nudges or deceptive designs that could introduce bias?",
                "type": "Technical Factor",
                "options": ["No Deceptive Design Elements", "Minor Nudging Present", "Moderate Nudging", "Significant Manipulative Design", "Severe Deceptive Patterns", "Not Applicable"]
            }
        }
    },
    "Deployment": {
        "description": "Bias can emerge during deployment due to differences between the training and deployment environments.",
        "questions": {
            "distribution_differences": {
                "question": "Are there statistical differences between the data used for training and the data encountered in the deployment environment?",
                "type": "Process Factor",
                "options": ["No Significant Differences", "Minor Differences", "Moderate Differences", "Significant Differences", "Severe Distribution Shift", "Not Applicable"]
            },
            "changes_meaning": {
                "question": "Has the meaning of inferences or user choices changed since the model was trained?",
                "type": "Process Factor",
                "options": ["No Changes Detected", "Minor Changes", "Moderate Changes", "Significant Changes", "Severe Changes", "Not Applicable"]
            },
            "user_interactions": {
                "question": "How does the system adapt to user interactions? Is there a feedback collection mechanism in place to monitor for bias?",
                "type": "Technical Factor",
                "options": ["Comprehensive Bias Monitoring System", "Good Monitoring with Feedback", "Basic Monitoring System", "Minimal Monitoring", "No Monitoring System", "Not Applicable"]
            }
        }
    },
    "Human-in-the-Loop (HIL)": {
        "description": "Human decisions and judgments, when incorporated into the AI system, can introduce their own biases.",
        "questions": {
            "hil_fitment": {
                "question": "How is the human-in-the-loop component integrated into the overall model lifecycle?",
                "type": "Process Factor",
                "options": ["Well Integrated with Clear Protocols", "Moderately Integrated", "Partially Integrated", "Poorly Integrated", "Not Integrated Systematically", "Not Applicable"]
            },
            "observing_outcomes": {
                "question": "What is the approach towards observing outcomes influenced by human decisions?",
                "type": "Technical Factor",
                "options": ["Systematic Observation and Analysis", "Regular Observation", "Occasional Observation", "Minimal Observation", "No Systematic Observation", "Not Applicable"]
            },
            "inferences_conclusions": {
                "question": "Are conclusions or inferences reached based on unvalidated causalities?",
                "type": "Technical Factor",
                "options": ["All Causalities Validated", "Most Causalities Validated", "Some Causalities Validated", "Few Causalities Validated", "Many Unvalidated Causalities", "Not Applicable"]
            },
            "beliefs_actions": {
                "question": "How do human beliefs and their subsequent actions influence the system's outcomes?",
                "type": "Technical Factor",
                "options": ["Well Understood and Documented", "Substantially Understood", "Partially Understood", "Minimally Understood", "Not Understood", "Not Applicable"]
            }
        }
    },
    "AI-based System (Overall)": {
        "description": "This final section considers bias from a holistic perspective, looking at the overall system design and its impact.",
        "questions": {
            "system_design": {
                "question": "Does the overall system design contribute to biased outcomes?",
                "type": "Process Factor",
                "options": ["No Bias Contribution Detected", "Minor Bias Risk", "Moderate Bias Risk", "Significant Bias Risk", "High Bias Risk", "Not Applicable"]
            },
            "disparate_errors": {
                "question": "Does the system produce disparate error rates for different subgroups of users?",
                "type": "Process Factor",
                "options": ["No Disparate Errors Detected", "Minor Disparate Errors", "Moderate Disparate Errors", "Significant Disparate Errors", "Severe Disparate Errors", "Not Applicable"]
            },
            "overall_accessibility": {
                "question": "From an overall system perspective, is the application accessible to all intended user groups?",
                "type": "Process Factor",
                "options": ["Fully Accessible to All Groups", "Mostly Accessible", "Partially Accessible", "Minimally Accessible", "Limited Accessibility", "Not Applicable"]
            },
            "user_journey_map": {
                "question": "Has the user journey been mapped and analyzed to identify points where bias could be introduced?",
                "type": "Technical Factor",
                "options": ["Comprehensive Mapping and Analysis", "Substantial Mapping Done", "Partial Mapping Done", "Minimal Mapping", "No Mapping Performed", "Not Applicable"]
            }
        }
    }
}
# ---------- end SURVEY_SECTIONS ----------

# REFINED RISK MAPPING - Only "Not Applicable" carries 0 weight
RISK_MAPPING = {
    # Risk Score 1 (Lowest Risk - Best Practice)
    "No Historical Bias Detected": 1,
    "Highly Relevant and Aligned": 1,
    "All Groups Well Represented": 1,
    "Highly Complete and Validated": 1,
    "Always Thoroughly Checked": 1,
    "Bias-Aware Methods Used": 1,
    "Bias-Aware Removal Process": 1,
    "Bias-Aware Transformation Methods": 1,
    "No Inconsistencies Detected": 1,
    "No Proxies Used": 1,
    "All Relationships Validated": 1,
    "Thoroughly Vetted for Bias": 1,
    "Comprehensive Quality Assessment": 1,
    "Thoroughly Evaluated": 1,
    "Bias-Aware Fair Objective": 1,
    "Well Protected Against Attacks": 1,
    "Bias-Aware Architecture Selection": 1,
    "Bias-Aware Feature Selection": 1,
    "Systematic Optimization with Validation": 1,
    "Fairness-Aware Choices": 1,
    "Comprehensive Fairness and Performance Metrics": 1,
    "Bias-Aware Systematic Tuning": 1,
    "Comprehensive Fairness and Performance Monitoring": 1,
    "No Known Defects": 1,
    "Well Calibrated with Validation": 1,
    "Highly Robust with Multiple Safeguards": 1,
    "Fairness-Aware Optimization": 1,
    "Fully Accessible to All Users": 1,
    "Thoroughly Examined and Tested": 1,
    "No Unfavorable Effects Detected": 1,
    "No Deceptive Design Elements": 1,
    "No Significant Differences": 1,
    "No Changes Detected": 1,
    "Comprehensive Bias Monitoring System": 1,
    "Well Integrated with Clear Protocols": 1,
    "Systematic Observation and Analysis": 1,
    "All Causalities Validated": 1,
    "Well Understood and Documented": 1,
    "No Bias Contribution Detected": 1,
    "No Disparate Errors Detected": 1,
    "Fully Accessible to All Groups": 1,
    "Comprehensive Mapping and Analysis": 1,

    # Risk Score 2 (Low Risk)
    "Minor Historical Bias Present": 2,
    "Mostly Relevant": 2,
    "Minor Under-representation": 2,
    "Mostly Complete": 2,
    "Usually Checked": 2,
    "Standard Statistical Methods": 2,
    "Systematic Evidence-Based Removal": 2,
    "Standard Statistical Methods": 2,
    "Minor Inconsistencies": 2,
    "Validated Non-Biased Proxies": 2,
    "Most Relationships Validated": 2,
    "Partially Vetted": 2,
    "Substantial Assessment": 2,
    "Substantially Evaluated": 2,
    "Standard Objective with Fairness Review": 2,
    "Moderately Protected": 2,
    "Performance-Based with Fairness Review": 2,
    "Systematic Selection with Review": 2,
    "Grid Search or Similar": 2,
    "Performance Optimized with Fairness Review": 2,
    "Performance with Some Fairness Metrics": 2,
    "Systematic Performance Tuning": 2,
    "Performance with Fairness Tracking": 2,
    "Minor Defects Present": 2,
    "Moderately Calibrated": 2,
    "Moderately Robust": 2,
    "Balanced Performance and Fairness": 2,
    "Mostly Accessible": 2,
    "Substantially Examined": 2,
    "Minor Potential Effects": 2,
    "Minor Nudging Present": 2,
    "Minor Differences": 2,
    "Minor Changes": 2,
    "Good Monitoring with Feedback": 2,
    "Moderately Integrated": 2,
    "Regular Observation": 2,
    "Most Causalities Validated": 2,
    "Substantially Understood": 2,
    "Minor Bias Risk": 2,
    "Minor Disparate Errors": 2,
    "Mostly Accessible": 2,
    "Substantial Mapping Done": 2,

    # Risk Score 3 (Medium Risk)
    "Moderate Historical Bias Present": 3,
    "Somewhat Relevant": 3,
    "Moderate Under-representation": 3,
    "Somewhat Complete": 3,
    "Sometimes Checked": 3,
    "Basic Imputation Methods": 3,
    "Basic Statistical Removal": 3,
    "Basic Transformation Methods": 3,
    "Moderate Inconsistencies": 3,
    "Some Unvalidated Proxies": 3,
    "Some Relationships Validated": 3,
    "Basic Assessment Done": 3,
    "Basic Assessment": 3,
    "Partially Evaluated": 3,
    "Standard Objective": 3,
    "Basic Protection": 3,
    "Performance-Based Selection": 3,
    "Standard Statistical Selection": 3,
    "Basic Hyperparameter Tuning": 3,
    "Standard Optimization Choices": 3,
    "Standard Performance Metrics Only": 3,
    "Standard Tuning Process": 3,
    "Standard Performance Monitoring": 3,
    "Moderate Defects Present": 3,
    "Basic Calibration": 3,
    "Basic Robustness Measures": 3,
    "Performance-Focused Optimization": 3,
    "Partially Accessible": 3,
    "Partially Examined": 3,
    "Moderate Unfavorable Effects": 3,
    "Moderate Nudging": 3,
    "Moderate Differences": 3,
    "Moderate Changes": 3,
    "Basic Monitoring System": 3,
    "Partially Integrated": 3,
    "Occasional Observation": 3,
    "Some Causalities Validated": 3,
    "Partially Understood": 3,
    "Moderate Bias Risk": 3,
    "Moderate Disparate Errors": 3,
    "Partially Accessible": 3,
    "Partial Mapping Done": 3,

    # Risk Score 4 (High Risk)
    "Significant Historical Bias Present": 4,
    "Minimally Relevant": 4,
    "Significant Under-representation": 4,
    "Significant Gaps Present": 4,
    "Rarely Checked": 4,
    "Ad-hoc Imputation": 4,
    "Ad-hoc Removal": 4,
    "Ad-hoc Methods": 4,
    "Significant Inconsistencies": 4,
    "Multiple Unvalidated Proxies": 4,
    "Few Relationships Validated": 4,
    "Minimal Assessment": 4,
    "Minimal Assessment": 4,
    "Minimally Evaluated": 4,
    "Potentially Problematic Objective": 4,
    "Minimal Protection": 4,
    "Standard Architecture Choice": 4,
    "Basic Feature Selection": 4,
    "Minimal Tuning": 4,
    "Basic Choices": 4,
    "Basic Metrics Only": 4,
    "Basic Tuning": 4,
    "Basic Monitoring": 4,
    "Significant Defects Present": 4,
    "Minimal Calibration": 4,
    "Minimal Protection": 4,
    "Basic Optimization": 4,
    "Minimally Accessible": 4,
    "Minimally Examined": 4,
    "Significant Unfavorable Effects": 4,
    "Significant Manipulative Design": 4,
    "Significant Differences": 4,
    "Significant Changes": 4,
    "Minimal Monitoring": 4,
    "Poorly Integrated": 4,
    "Minimal Observation": 4,
    "Few Causalities Validated": 4,
    "Minimally Understood": 4,
    "Significant Bias Risk": 4,
    "Significant Disparate Errors": 4,
    "Minimally Accessible": 4,
    "Minimal Mapping": 4,

    # Risk Score 5 (Highest Risk - Critical Issues)
    "Severe Historical Bias Present": 5,
    "Not Relevant": 5,
    "Severe Under-representation": 5,
    "Severe Incompleteness": 5,
    "Never Checked": 5,
    "No Systematic Approach": 5,
    "No Systematic Removal": 5,
    "No Systematic Methods": 5,
    "Severe Inconsistencies": 5,
    "Many High-Risk Proxies": 5,
    "No Validation Performed": 5,
    "Not Vetted": 5,
    "No Assessment": 5,
    "Not Evaluated": 5,
    "High-Risk Objective": 5,
    "Highly Vulnerable": 5,
    "Ad-hoc Choice": 5,
    "Ad-hoc Selection": 5,
    "Default Values Used": 5,
    "Default Choices": 5,
    "Minimal Metrics": 5,
    "Ad-hoc Tuning": 5,
    "Minimal or No Monitoring": 5,
    "Severe Defects Present": 5,
    "Not Calibrated": 5,
    "Vulnerable to Leakage": 5,
    "Ad-hoc Optimization": 5,
    "Limited Accessibility": 5,
    "Not Examined": 5,
    "Severe Unfavorable Effects": 5,
    "Severe Deceptive Patterns": 5,
    "Severe Distribution Shift": 5,
    "Severe Changes": 5,
    "No Monitoring System": 5,
    "Not Integrated Systematically": 5,
    "No Systematic Observation": 5,
    "Many Unvalidated Causalities": 5,
    "Not Understood": 5,
    "High Bias Risk": 5,
    "Severe Disparate Errors": 5,
    "Limited Accessibility": 5,
    "No Mapping Performed": 5,

    # Zero weight - Only for Not Applicable
    "Not Applicable": 0
}

def get_risk_score(response: str) -> int:
    return RISK_MAPPING.get(response, 0)

# ---------- Rest of the code remains the same ----------
def calculate_progress_for_section(section_name: str) -> (int, int):
    """Return (answered_count, total_count) for a section."""
    if 'responses_temp' not in st.session_state:
        return 0, len(SURVEY_SECTIONS[section_name]["questions"])
    sec = st.session_state.get("responses_temp", {})
    answered = len(sec.get(section_name, {}))
    total = len(SURVEY_SECTIONS[section_name]["questions"])
    return answered, total

def calculate_overall_progress() -> (int, int):
    total_answered = 0
    total_questions = 0
    for section in SURVEY_SECTIONS.keys():
        a, t = calculate_progress_for_section(section)
        total_answered += a
        total_questions += t
    return total_answered, total_questions

def compute_submission_from_responses(responses: Dict[str, Dict[str, str]], model_name: str, owner: str) -> Dict[str, Any]:
    """Convert the collected multi-section responses into the submission structure."""
    subscores = {}
    total_points = 0
    count_applicable = 0

    proxy_buckets = {
        "decision_impact": ["AI-based System (Overall)", "Deployment"],
        "data_provenance": ["Data"],
        "population_scope": ["Data", "Human-in-the-Loop (HIL)"],
        "model_complexity": ["Model"],
        "governance_oversight": ["Pipeline & Infrastructure", "Interface & Integrations", "Human-in-the-Loop (HIL)"]
    }

    section_avg = {}
    for section_name, sec_meta in SURVEY_SECTIONS.items():
        responses_in_section = responses.get(section_name, {})
        section_risk_sum = 0
        section_count = 0
        for qid, resp in responses_in_section.items():
            if resp not in ("Not Applicable", ""):
                val = get_risk_score(resp)
                section_risk_sum += val
                section_count += 1
        avg = (section_risk_sum / section_count) if section_count > 0 else 0
        section_avg[section_name] = avg

    def avg_to_points(a: float) -> float:
        if a >= 4.0:
            return 20.0
        if a >= 2.0:
            return 10.0
        return 0.0

    for key, sections in proxy_buckets.items():
        vals = [section_avg.get(s, 0) for s in sections]
        if vals:
            avg_of_vals = sum(vals) / len(vals)
        else:
            avg_of_vals = 0.0
        subscores[key] = avg_to_points(avg_of_vals)
        total_points += subscores[key]

    total_points = max(0.0, min(100.0, float(total_points)))
    submission = {
        "submission_id": str(uuid.uuid4()),
        "submitted_at": datetime.utcnow().isoformat() + "Z",
        "model_name": model_name,
        "owner": owner,
        "answers": responses,
        "subscores": subscores,
        "total_risk_score": total_points,
        "risk_category": map_score_to_category(total_points)
    }
    return submission

def _init_temp_storage():
    """Internal: ensure temporary response storage while user is filling."""
    if "responses_temp" not in st.session_state:
        st.session_state["responses_temp"] = {}

    if "survey_page" not in st.session_state:
        first = list(SURVEY_SECTIONS.keys())[0]
        st.session_state["survey_page"] = first

def _render_question(section_name: str, q_id: str, q_data: Dict[str, Any]):
    """Render a single question and persist selection to session state."""
    if section_name not in st.session_state["responses_temp"]:
        st.session_state["responses_temp"][section_name] = {}

    q_key = f"{section_name}__{q_id}"
    label = q_data.get("question", q_id)
    options = [""] + q_data.get("options", [])
    current = st.session_state["responses_temp"][section_name].get(q_id, "")
    default_index = options.index(current) if current in options else 0

    response = st.selectbox(label, options=options, index=default_index, key=q_key, help="Choose the option that best describes your AI system")
    if response:
        st.session_state["responses_temp"][section_name][q_id] = response

        score = get_risk_score(response)
        if score >= 4:
            st.write("High Risk response (score: {})".format(score))
        elif score >= 3:
            st.write("Medium Risk (score: {})".format(score))
        elif score >= 2:
            st.write("Low Risk (score: {})".format(score))
        elif score >= 1:
            st.write("Best Practice (score: {})".format(score))

def _render_section(section_name: str):
    """Render all questions for a given section."""
    sec = SURVEY_SECTIONS[section_name]
    st.header(section_name)
    st.write(sec.get("description", ""))

    answered, total = calculate_progress_for_section(section_name)
    st.progress(answered / total if total > 0 else 0)
    st.write(f"Progress for section: {answered}/{total}")

    process_qs = []
    technical_qs = []
    for qid, qdat in sec["questions"].items():
        if qdat.get("type", "").lower().startswith("process"):
            process_qs.append((qid, qdat))
        else:
            technical_qs.append((qid, qdat))

    if process_qs:
        st.subheader("Process Factor Questions")
        for qid, qd in process_qs:
            _render_question(section_name, qid, qd)
            st.markdown("---")

    if technical_qs:
        st.subheader("Technical Factor Questions")
        for qid, qd in technical_qs:
            _render_question(section_name, qid, qd)
            st.markdown("---")

def display_summary_and_metrics(responses: Dict[str, Dict[str, str]]):
    """Show summary table and overall metrics."""
    st.subheader("Assessment Summary")

    summary_rows = []
    total_risk_sum = 0
    total_applicable = 0

    for section_name in SURVEY_SECTIONS.keys():
        answered, total = len(responses.get(section_name, {})), len(SURVEY_SECTIONS[section_name]["questions"])
        sec_sum = 0
        sec_count = 0
        for resp in responses.get(section_name, {}).values():
            if resp not in ("Not Applicable", ""):
                val = get_risk_score(resp)
                sec_sum += val
                sec_count += 1
        avg_risk = (sec_sum / sec_count) if sec_count > 0 else 0
        total_risk_sum += sec_sum
        total_applicable += sec_count

        if avg_risk >= 4.0:
            risk_lvl = "High Risk"
        elif avg_risk >= 3.0:
            risk_lvl = "Medium Risk"
        elif avg_risk >= 2.0:
            risk_lvl = "Low Risk"
        elif avg_risk >= 1.0:
            risk_lvl = "Best Practice"
        else:
            risk_lvl = "Not Assessed"

        summary_rows.append({
            "Section": section_name,
            "Answered": f"{answered}/{total}",
            "Avg Risk Score": f"{avg_risk:.2f}",
            "Risk Level": risk_lvl
        })

    overall_avg = (total_risk_sum / total_applicable) if total_applicable > 0 else 0.0

    c1, c2, c3 = st.columns(3)
    c1.metric("Overall Risk Score", f"{overall_avg:.2f}")
    if overall_avg >= 4.0:
        overall_level = "High Risk"
    elif overall_avg >= 3.0:
        overall_level = "Medium Risk"
    elif overall_avg >= 2.0:
        overall_level = "Low Risk"
    elif overall_avg >= 1.0:
        overall_level = "Best Practice"
    else:
        overall_level = "Not Assessed"
    c2.metric("Risk Level", overall_level)
    answered_all, total_all = calculate_overall_progress()
    completion_pct = (answered_all / total_all) * 100 if total_all > 0 else 0.0
    c3.metric("Overall Completion", f"{completion_pct:.1f}%")

    st.dataframe(summary_rows, use_container_width=True)

def export_results_json(responses: Dict[str, Dict[str, str]]) -> Optional[str]:
    """Return JSON string of the collected responses and summary."""
    if not responses:
        return None

    results = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "responses": responses,
        "summary": {}
    }
    for section_name in SURVEY_SECTIONS.keys():
        sec_sum = 0
        sec_count = 0
        for resp in responses.get(section_name, {}).values():
            if resp not in ("Not Applicable", ""):
                sec_sum += get_risk_score(resp)
                sec_count += 1
        avg = (sec_sum / sec_count) if sec_count > 0 else 0
        results["summary"][section_name] = {
            "average_risk_score": avg,
            "risk_level": ("High Risk" if avg >= 4 else "Medium Risk" if avg >= 3 else "Low Risk" if avg >= 2 else "Best Practice" if avg >= 1 else "Not Assessed"),
            "applicable_questions": sec_count
        }
    return json.dumps(results, indent=2)

def render_survey(embedded: bool = True, require_identity: bool = True) -> Optional[Dict[str, Any]]:
    """
    Render the full multi-page survey and return the final submission dict when complete.
    - embedded: if True, survey will be rendered compactly on the calling page
    - require_identity: whether to require model name and owner before final save
    Returns: submission dict if survey completed and saved, otherwise None
    """
    if SURVEY_KEY in st.session_state:
        return st.session_state[SURVEY_KEY]

    _init_temp_storage()

    st.caption("Answer the sections to evaluate potential bias across the system lifecycle.")
    if embedded and "survey_started" not in st.session_state:
        if st.button("Start Full Assessment"):
            st.session_state["survey_started"] = True
        else:
            return None

    with st.sidebar:
        st.header("Survey navigation")
        for sec in SURVEY_SECTIONS.keys():
            a, t = calculate_progress_for_section(sec)
            label = f"{sec} ({a}/{t})"
            if st.button(label, key=f"nav_{sec}"):
                st.session_state["survey_page"] = sec
        st.markdown("---")
        st.write("Actions")
        if st.button("Summary"):
            st.session_state["survey_page"] = "Summary"
        if st.button("Reset survey (start over)"):
            if "responses_temp" in st.session_state:
                del st.session_state["responses_temp"]
            if "survey_page" in st.session_state:
                st.session_state["survey_page"] = list(SURVEY_SECTIONS.keys())[0]
            st.experimental_rerun()

    current_page = st.session_state.get("survey_page", list(SURVEY_SECTIONS.keys())[0])

    if current_page == "Summary":
        responses = st.session_state.get("responses_temp", {})
        display_summary_and_metrics(responses)
        st.markdown("---")
        st.subheader("Finalize and save")
        model_name = st.text_input("Model name or identifier", key="survey_full_model_name")
        owner = st.text_input("Model owner or team", key="survey_full_owner")
        if st.button("Save and finish"):
            if require_identity and (not model_name or not owner):
                st.error("Please provide Model name and Model owner (required).")
            else:
                submission = compute_submission_from_responses(responses, model_name=model_name or "unnamed", owner=owner or "unknown")
                saved = save_submission(submission)
                st.session_state[SURVEY_KEY] = submission
                if "responses_temp" in st.session_state:
                    del st.session_state["responses_temp"]
                st.success(f"Survey saved. Risk: {submission['total_risk_score']:.1f} — {submission['risk_category']}")
                with st.expander("Show submission JSON"):
                    st.json(submission)
                    st.write("Saved file:", saved)
                return submission
        json_export = export_results_json(responses)
        if json_export:
            st.download_button("Download responses (JSON)", data=json_export, file_name=f"survey_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json", mime="application/json")
        return None

    if current_page in SURVEY_SECTIONS:
        _render_section(current_page)

        sections = list(SURVEY_SECTIONS.keys())
        idx = sections.index(current_page)
        cols = st.columns([1, 2, 1])
        with cols[0]:
            if idx > 0:
                if st.button("Previous Section"):
                    st.session_state["survey_page"] = sections[idx - 1]
                    st.experimental_rerun()
        with cols[1]:
            st.write(f"Section {idx + 1} of {len(sections)}")
        with cols[2]:
            if idx < len(sections) - 1:
                if st.button("Next Section"):
                    st.session_state["survey_page"] = sections[idx + 1]
                    st.experimental_rerun()
            else:
                if st.button("Go to Summary"):
                    st.session_state["survey_page"] = "Summary"
                    st.experimental_rerun()

    return None