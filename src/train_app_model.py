import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from xgboost import XGBClassifier
from url_features import extract_url_features

SEED = 42
df = pd.read_csv("data/phiusiil_clean.csv")
print("Computing features for", len(df), "URLs...")
X = pd.DataFrame([extract_url_features(u) for u in df["URL"]])
cols = list(X.columns)
y = (df["label"] == 0).astype(int)  # phishing = 1

train_idx, test_idx = train_test_split(df.index, test_size=0.2, stratify=y, random_state=SEED)

model = XGBClassifier(n_estimators=200, max_depth=6, learning_rate=0.1,
                      eval_metric="logloss", random_state=SEED, n_jobs=-1)
model.fit(X.loc[train_idx], y.loc[train_idx])
pred = model.predict(X.loc[test_idx])
tn, fp, fn, tp = confusion_matrix(y.loc[test_idx], pred).ravel()

print("\nApp URL model (15 features, our own extractor)")
print("Accuracy :", round(accuracy_score(y.loc[test_idx], pred), 4))
print("Precision:", round(precision_score(y.loc[test_idx], pred), 4))
print("Recall   :", round(recall_score(y.loc[test_idx], pred), 4))
print("F1       :", round(f1_score(y.loc[test_idx], pred), 4))
print("Missed phishing (FN):", fn, "| False alarms (FP):", fp)

joblib.dump({"model": model, "features": cols}, "models/xgb_url_app.joblib")
print("\nSaved models/xgb_url_app.joblib")
