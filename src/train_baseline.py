from pathlib import Path
import pickle
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "triage_cases.csv"
MODEL = ROOT / "src" / "baseline_model.pkl"

df = pd.read_csv(DATA)

X = df.drop(columns=["risk_label", "needs_escalation", "case_id"])
y = df["risk_label"]

num_cols = ["age", "temp_c", "heart_rate", "systolic_bp", "resp_rate", "spo2", "pain_score", "altered_mental_status", "major_bleeding", "missing_vitals"]
cat_cols = ["sex", "chief_complaint"]

pre = ColumnTransformer(
    transformers=[
        ("num", Pipeline([("imputer", SimpleImputer(strategy="median"))]), num_cols),
        ("cat", Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore"))
        ]), cat_cols),
    ]
)

clf = Pipeline([
    ("pre", pre),
    ("model", LogisticRegression(max_iter=1000))
])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
clf.fit(X_train, y_train)
pred = clf.predict(X_test)

print(classification_report(y_test, pred))

with open(MODEL, "wb") as f:
    pickle.dump(clf, f)

print(f"Saved model to {MODEL}")