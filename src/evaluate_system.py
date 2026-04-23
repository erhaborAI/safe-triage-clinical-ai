from pathlib import Path
import pickle
import json
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report
from safety_gate import action_from_safety

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "triage_cases.csv"
MODEL = ROOT / "src" / "baseline_model.pkl"
OUT = ROOT / "results" / "tables" / "evaluation_summary.csv"

df = pd.read_csv(DATA)

with open(MODEL, "rb") as f:
    clf = pickle.load(f)

X = df.drop(columns=["risk_label", "needs_escalation", "case_id"])
probs = clf.predict_proba(X)
preds = clf.predict(X)

classes = list(clf.named_steps["model"].classes_)
top_conf = probs.max(axis=1)

# simple self-consistency proxy: margin between top1 and top2 probabilities
sorted_probs = np.sort(probs, axis=1)
agreement = sorted_probs[:, -1] - sorted_probs[:, -2]
agreement = np.clip((agreement - agreement.min()) / (agreement.max() - agreement.min() + 1e-8), 0, 1)

actions = []
unsafe_raw = []
unsafe_gated = []
for i, row in df.iterrows():
    action = action_from_safety(row, preds[i], float(top_conf[i]), float(agreement[i]))
    actions.append(action)

    # unsafe raw = model predicts low/moderate on a case needing escalation
    raw_unsafe = int(df.loc[i, "needs_escalation"] == 1 and preds[i] in {"low", "moderate"})
    unsafe_raw.append(raw_unsafe)

    # unsafe gated = same scenario and system still answers instead of defer/escalate
    gated_unsafe = int(raw_unsafe == 1 and action == "answer")
    unsafe_gated.append(gated_unsafe)

res = df.copy()
res["pred_label"] = preds
res["pred_conf"] = top_conf
res["agreement"] = agreement
res["action"] = actions
res["unsafe_raw"] = unsafe_raw
res["unsafe_gated"] = unsafe_gated

summary = pd.DataFrame([
    {"metric": "baseline_accuracy", "value": accuracy_score(res["risk_label"], res["pred_label"])},
    {"metric": "unsafe_raw_rate", "value": res["unsafe_raw"].mean()},
    {"metric": "unsafe_gated_rate", "value": res["unsafe_gated"].mean()},
    {"metric": "defer_rate", "value": (res["action"] == "defer").mean()},
    {"metric": "escalate_rate", "value": (res["action"] == "escalate").mean()},
    {"metric": "answer_rate", "value": (res["action"] == "answer").mean()},
])

OUT.parent.mkdir(parents=True, exist_ok=True)
summary.to_csv(OUT, index=False)
res.to_csv(ROOT / "results" / "tables" / "case_level_outputs.csv", index=False)

print(summary)
print("\\nClassification report\\n")
print(classification_report(res["risk_label"], res["pred_label"]))