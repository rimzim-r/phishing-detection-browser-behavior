import time
import joblib
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, roc_auc_score)
from xgboost import XGBClassifier
from features import BASELINE, HYBRID

SEED = 42
df = pd.read_csv("data/phiusiil_clean.csv")

# phishing = 1 (positive class), legitimate = 0
y = (df["label"] == 0).astype(int)

train_idx, test_idx = train_test_split(
    df.index, test_size=0.2, stratify=y, random_state=SEED)

def get_models():
    return {
        "Logistic Regression": make_pipeline(
            StandardScaler(), LogisticRegression(max_iter=1000)),
        "Decision Tree": DecisionTreeClassifier(random_state=SEED),
        "Random Forest": RandomForestClassifier(
            n_estimators=100, random_state=SEED, n_jobs=-1),
        "XGBoost": XGBClassifier(
            n_estimators=200, max_depth=6, learning_rate=0.1,
            eval_metric="logloss", random_state=SEED, n_jobs=-1),
    }

feature_sets = {"Baseline (URL only)": BASELINE, "Hybrid (URL + behavior)": HYBRID}

os.makedirs("models", exist_ok=True)
rows = []

for set_name, cols in feature_sets.items():
    X_train, X_test = df.loc[train_idx, cols], df.loc[test_idx, cols]
    y_train, y_test = y.loc[train_idx], y.loc[test_idx]

    for model_name, model in get_models().items():
        t0 = time.time()
        model.fit(X_train, y_train)
        train_time = time.time() - t0

        t0 = time.time()
        pred = model.predict(X_test)
        pred_time = time.time() - t0
        proba = model.predict_proba(X_test)[:, 1]

        rows.append({
            "Feature set": set_name,
            "Model": model_name,
            "Accuracy": accuracy_score(y_test, pred),
            "Precision": precision_score(y_test, pred),
            "Recall": recall_score(y_test, pred),
            "F1": f1_score(y_test, pred),
            "ROC-AUC": roc_auc_score(y_test, proba),
            "Train time (s)": train_time,
            "Predict time (s)": pred_time,
        })
        print("Done:", set_name, "-", model_name)

        if model_name == "XGBoost":
            key = "baseline" if set_name.startswith("Baseline") else "hybrid"
            joblib.dump(model, f"models/xgb_{key}.joblib")

results = pd.DataFrame(rows)
results.to_csv("results/model_results.csv", index=False)
pd.set_option("display.width", 200)
print()
print(results.round(4).to_string(index=False))
print("\nTest rows:", len(test_idx))
