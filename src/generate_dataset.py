from pathlib import Path
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parents[1] / "data" / "processed" / "triage_cases.csv"
rng = np.random.default_rng(42)

chief_complaints = [
    "chest pain", "shortness of breath", "fever", "abdominal pain", "headache",
    "dizziness", "weakness", "vomiting", "trauma", "palpitations", "confusion",
    "cough", "seizure-like episode", "back pain", "syncope"
]

def assign_risk(row):
    score = 0
    cc = row["chief_complaint"]
    if cc in {"chest pain", "shortness of breath", "syncope", "seizure-like episode", "confusion", "trauma"}:
        score += 2
    if row["spo2"] < 92:
        score += 3
    elif row["spo2"] < 95:
        score += 2
    if row["systolic_bp"] < 90:
        score += 3
    elif row["systolic_bp"] < 100:
        score += 2
    if row["heart_rate"] > 130 or row["heart_rate"] < 45:
        score += 3
    elif row["heart_rate"] > 110:
        score += 2
    if row["resp_rate"] > 28:
        score += 2
    if row["temp_c"] >= 39.2:
        score += 1
    if row["altered_mental_status"] == 1:
        score += 3
    if row["major_bleeding"] == 1:
        score += 4
    if row["age"] >= 75:
        score += 1

    if score <= 1:
        return "low"
    elif score <= 4:
        return "moderate"
    elif score <= 7:
        return "urgent"
    return "emergent"

def escalation_needed(row):
    return int(row["risk_label"] in {"urgent", "emergent"})

rows = []
for i in range(800):
    cc = rng.choice(chief_complaints)
    row = {
        "case_id": i+1,
        "age": int(rng.integers(18, 91)),
        "sex": rng.choice(["female", "male"]),
        "chief_complaint": cc,
        "temp_c": np.round(rng.normal(37.2, 1.0), 1),
        "heart_rate": int(np.clip(rng.normal(92, 22), 35, 180)),
        "systolic_bp": int(np.clip(rng.normal(122, 24), 70, 210)),
        "resp_rate": int(np.clip(rng.normal(18, 5), 8, 40)),
        "spo2": int(np.clip(rng.normal(97, 4), 75, 100)),
        "pain_score": int(rng.integers(0, 11)),
        "altered_mental_status": int(rng.random() < 0.08),
        "major_bleeding": int(rng.random() < 0.04),
        "missing_vitals": int(rng.random() < 0.12),
    }

    if cc == "chest pain":
        row["heart_rate"] += int(rng.integers(0, 20))
    if cc == "shortness of breath":
        row["spo2"] -= int(rng.integers(0, 8))
        row["resp_rate"] += int(rng.integers(0, 12))
    if cc == "confusion":
        row["altered_mental_status"] = 1
    if cc == "trauma":
        row["major_bleeding"] = int(rng.random() < 0.18)
        row["systolic_bp"] -= int(rng.integers(0, 30))
    if cc == "seizure-like episode":
        row["altered_mental_status"] = int(rng.random() < 0.5)

    row["risk_label"] = assign_risk(row)
    row["needs_escalation"] = escalation_needed(row)

    # randomly blank some critical vitals when missing_vitals=1
    for fld in ["heart_rate", "systolic_bp", "resp_rate", "spo2"]:
        if row["missing_vitals"] and rng.random() < 0.45:
            row[fld] = np.nan

    rows.append(row)

df = pd.DataFrame(rows)
OUT.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUT, index=False)
print(f"Saved {len(df)} cases to {OUT}")