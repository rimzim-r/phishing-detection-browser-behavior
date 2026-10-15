import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from xgboost import XGBClassifier
from features import URL_FEATURES, CONSISTENCY_FEATURES, BEHAVIOR_FEATURES

SEED = 42
df = pd.read_csv("data/phiusiil_clean.csv")
y = (df["label"] == 0).astype(int)  # phishing = 1
train_idx, test_idx = train_test_split(df.index, test_size=0.2, stratify=y, random_state=SEED)

sets = {
    "URL only": URL_FEATURES,
    "URL + consistency": URL_FEATURES + CONSISTENCY_FEATURES,
    "URL + behavior": URL_FEATURES + BEHAVIOR_FEATURES,
    "URL + consistency + behavior": URL_FEATURES + CONSISTENCY_FEATURES + BEHAVIOR_FEATURES,
}

rows = []
for name, cols in sets.items():
    model = XGBClassifier(n_estimators=200, max_depth=6, learning_rate=0.1,
                          eval_metric="logloss", random_state=SEED, n_jobs=-1)
    model.fit(df.loc[train_idx, cols], y.loc[train_idx])
    pred = model.predict(df.loc[test_idx, cols])
    tn, fp, fn, tp = confusion_matrix(y.loc[test_idx], pred).ravel()
    rows.append({
        "Feature set": name,
        "Features": len(cols),
        "Accuracy": accuracy_score(y.loc[test_idx], pred),
        "Precision": precision_score(y.loc[test_idx], pred),
        "Recall": recall_score(y.loc[test_idx], pred),
        "F1": f1_score(y.loc[test_idx], pred),
        "Missed phishing (FN)": fn,
        "False alarms (FP)": fp,
    })

out = pd.DataFrame(rows)
out.to_csv("results/ablation_results.csv", index=False)
pd.set_option("display.width", 200)
print(out.round(4).to_string(index=False))
