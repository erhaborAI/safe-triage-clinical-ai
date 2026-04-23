import numpy as np
import pandas as pd

HIGH_RISK_COMPLAINTS = {"chest pain", "shortness of breath", "syncope", "confusion", "seizure-like episode", "trauma"}

def risk_rule_trigger(row: pd.Series) -> bool:
    cc = row["chief_complaint"]
    if cc in HIGH_RISK_COMPLAINTS:
        return True
    if pd.notna(row["spo2"]) and row["spo2"] < 92:
        return True
    if pd.notna(row["systolic_bp"]) and row["systolic_bp"] < 90:
        return True
    if pd.notna(row["heart_rate"]) and (row["heart_rate"] > 130 or row["heart_rate"] < 45):
        return True
    if row.get("altered_mental_status", 0) == 1:
        return True
    if row.get("major_bleeding", 0) == 1:
        return True
    return False

def missing_critical_info(row: pd.Series) -> bool:
    crit = ["heart_rate", "systolic_bp", "resp_rate", "spo2"]
    missing_count = sum(pd.isna(row[c]) for c in crit)
    return missing_count >= 2

def action_from_safety(row: pd.Series, pred_label: str, pred_conf: float, agreement: float) -> str:
    if risk_rule_trigger(row):
        return "escalate"
    if missing_critical_info(row):
        return "defer"
    if pred_conf < 0.45:
        return "defer"
    if agreement < 0.45:
        return "defer"
    if pred_label == "emergent":
        return "escalate"
    if pred_label == "urgent" and pred_conf < 0.70:
        return "escalate"
    return "answer"