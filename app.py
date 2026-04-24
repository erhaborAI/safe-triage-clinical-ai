import streamlit as st
import pandas as pd
import numpy as np
import pickle
from pathlib import Path

st.set_page_config(page_title="SafeTriage Demo", layout="centered")

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "src" / "baseline_model.pkl"

RISK_LABELS = ["low", "moderate", "urgent", "emergent"]


def rule_based_risk(row: dict) -> str:
    """Fallback risk model if pickle model is unavailable."""
    score = 0

    if row["heart_rate"] >= 130:
        score += 2
    elif row["heart_rate"] >= 110:
        score += 1

    if row["systolic_bp"] < 90:
        score += 2
    elif row["systolic_bp"] < 100:
        score += 1

    if row["resp_rate"] >= 30:
        score += 2
    elif row["resp_rate"] >= 22:
        score += 1

    if row["spo2"] < 90:
        score += 2
    elif row["spo2"] < 94:
        score += 1

    if row["temperature"] >= 39.0 or row["temperature"] < 35.0:
        score += 1

    if row["pain_score"] >= 8:
        score += 1

    if row["mental_status"] != "normal":
        score += 2

    if row["chest_pain"]:
        score += 1

    if row["shortness_of_breath"]:
        score += 1

    if row["bleeding"]:
        score += 2

    if row["pregnant"]:
        score += 1

    if score >= 7:
        return "emergent"
    if score >= 5:
        return "urgent"
    if score >= 3:
        return "moderate"
    return "low"


def rule_based_confidence(row: dict, pred_label: str) -> float:
    """Simple confidence approximation for the demo."""
    conf = 0.85

    if row["missing_critical_info"]:
        conf -= 0.25
    if row["mental_status"] != "normal":
        conf -= 0.05
    if pred_label in ["urgent", "emergent"]:
        conf -= 0.05

    return float(max(0.35, min(0.95, conf)))


def risk_rule_trigger(row: dict) -> bool:
    """High-risk rule triggers that force escalation."""
    return any(
        [
            row["systolic_bp"] < 90,
            row["spo2"] < 90,
            row["heart_rate"] >= 140,
            row["resp_rate"] >= 32,
            row["mental_status"] in ["confused", "unresponsive"],
            row["bleeding"],
        ]
    )


def action_from_safety(row: dict, pred_label: str, pred_conf: float) -> tuple[str, list[str]]:
    """Safety gate decides whether to answer, defer, or escalate."""
    reasons = []

    if risk_rule_trigger(row):
        reasons.append("High-risk rule trigger detected")
        reasons.append("Model prediction may underestimate risk; safety rules override due to abnormal vital signs or high-risk conditions.")
        return "ESCALATE", reasons

    if row["missing_critical_info"]:
        reasons.append("Missing critical information")
        return "DEFER", reasons

    if pred_conf < 0.70:
        reasons.append(f"Low confidence ({pred_conf:.2f})")
        return "DEFER", reasons

    if pred_label == "emergent":
        reasons.append("Predicted emergent risk")
        return "ESCALATE", reasons

    if pred_label == "urgent":
        reasons.append("Predicted urgent risk")
        return "ESCALATE", reasons

    reasons.append("Sufficient confidence without high-risk safety triggers")
    return "ANSWER", reasons


def load_model():
    if MODEL_PATH.exists():
        try:
            with open(MODEL_PATH, "rb") as f:
                return pickle.load(f)
        except Exception:
            return None
    return None


def model_predict(row: dict):
    """Use trained model if available; otherwise use rule-based fallback."""
    model = load_model()

    if model is not None:
        feature_row = pd.DataFrame(
            [
                {
                    "age": row["age"],
                    "heart_rate": row["heart_rate"],
                    "systolic_bp": row["systolic_bp"],
                    "resp_rate": row["resp_rate"],
                    "temperature": row["temperature"],
                    "spo2": row["spo2"],
                    "pain_score": row["pain_score"],
                    "chest_pain": int(row["chest_pain"]),
                    "shortness_of_breath": int(row["shortness_of_breath"]),
                    "bleeding": int(row["bleeding"]),
                    "pregnant": int(row["pregnant"]),
                    "mental_status": row["mental_status"],
                }
            ]
        )

        try:
            pred = model.predict(feature_row)[0]
            if hasattr(model, "predict_proba"):
                probs = model.predict_proba(feature_row)[0]
                conf = float(np.max(probs))
            else:
                conf = 0.75
            return pred, conf, "trained baseline model"
        except Exception:
            pass

    pred = rule_based_risk(row)
    conf = rule_based_confidence(row, pred)
    return pred, conf, "rule-based fallback model"


st.title("SafeTriage")
st.caption("Safety-gated clinical AI system for answer, defer, and escalate decisions under uncertainty.")

with st.form("triage_form"):
    st.subheader("Clinical Case Input")

    age = st.slider("Age", 0, 100, 45)

    col1, col2 = st.columns(2)
    with col1:
        heart_rate = st.number_input("Heart rate", min_value=30, max_value=220, value=92)
        systolic_bp = st.number_input("Systolic BP", min_value=50, max_value=250, value=118)
        resp_rate = st.number_input("Respiratory rate", min_value=8, max_value=50, value=18)
        temperature = st.number_input("Temperature (°C)", min_value=30.0, max_value=43.0, value=37.0, step=0.1)

    with col2:
        spo2 = st.number_input("SpO2 (%)", min_value=50, max_value=100, value=98)
        pain_score = st.slider("Pain score", 0, 10, 3)
        mental_status = st.selectbox("Mental status", ["normal", "confused", "unresponsive"])

    st.subheader("Clinical Flags")
    chest_pain = st.checkbox("Chest pain")
    shortness_of_breath = st.checkbox("Shortness of breath")
    bleeding = st.checkbox("Active bleeding")
    pregnant = st.checkbox("Pregnant")
    missing_critical_info = st.checkbox("Missing critical information")

    submitted = st.form_submit_button("Run SafeTriage")

if submitted:
    row = {
        "age": age,
        "heart_rate": heart_rate,
        "systolic_bp": systolic_bp,
        "resp_rate": resp_rate,
        "temperature": temperature,
        "spo2": spo2,
        "pain_score": pain_score,
        "mental_status": mental_status,
        "chest_pain": chest_pain,
        "shortness_of_breath": shortness_of_breath,
        "bleeding": bleeding,
        "pregnant": pregnant,
        "missing_critical_info": missing_critical_info,
    }

    pred_label, pred_conf, model_used = model_predict(row)
    action, reasons = action_from_safety(row, pred_label, pred_conf)
    uncertainty = 1 - pred_conf

    st.subheader("SafeTriage Decision")

    if action == "ANSWER":
        st.success(f"Final Action: {action}")
    elif action == "DEFER":
        st.warning(f"Final Action: {action}")
    else:
        st.error(f"Final Action: {action}")

    c1, c2, c3 = st.columns(3)
    c1.metric("Predicted Risk", pred_label.upper())
    c2.metric("Confidence", f"{pred_conf:.2f}")
    c3.metric("Uncertainty", f"{uncertainty:.2f}")

    st.markdown("### Model Layer")
    st.write(f"Model used: **{model_used}**")
    st.write(f"Baseline prediction: **{pred_label.upper()}**")
    st.write(f"Prediction confidence: **{pred_conf:.2f}**")

    st.markdown("### Counterfactual Behavior")
    st.write(
        f"Without the safety-gated action layer, the baseline model output would have been treated as: **{pred_label.upper()}**."
    )

    st.markdown("### Safety Gate")

    if action == "ESCALATE":
        st.error("Safety override: escalation required.")
        st.write(
            "The safety gate overrode the baseline model output because predefined high-risk clinical conditions were detected."
        )
    elif action == "DEFER":
        st.warning("Safety hold: insufficient certainty for autonomous output.")
        st.write(
            "The safety gate deferred the baseline model output due to uncertainty or missing critical information that prevents safe autonomous decision-making."
        )
    else:
        st.success("Safety gate: autonomous output permitted.")
        st.write(
            "The safety gate permitted the baseline model output because confidence was sufficient and no predefined safety trigger was detected."
        )

    st.markdown("### Why this decision?")
    for reason in reasons:
        if reason == "Model prediction may underestimate risk; safety rules override due to abnormal vital signs or high-risk conditions.":
            st.markdown(
                "- **Model prediction may underestimate risk; safety constraints enforce override when clinical risk signals exceed acceptable thresholds.**"
            )
        else:
            st.markdown(f"- **{reason}**")

    st.markdown("### Uncertainty and Reliability")
    st.write(f"Uncertainty score: **{uncertainty:.2f}**")

    if action == "ESCALATE":
        st.warning(
            "Safety constraints override autonomous use when clinical risk signals conflict with or exceed model-derived confidence."
        )
    elif action == "DEFER":
        st.warning(
            "Autonomous output is deferred because reliability is insufficient under the available information."
        )
    elif uncertainty > 0.30:
        st.warning("Model reliability may be reduced because uncertainty is elevated.")
    else:
        st.info("Model uncertainty is within the acceptable range for this prototype.")