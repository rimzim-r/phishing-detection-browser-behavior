import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from xgboost import XGBClassifier
from features import BASELINE, HYBRID

SEED = 42
SHORTENERS = {"bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly", "is.gd",
              "buff.ly", "rebrand.ly", "cutt.ly", "shorturl.at", "tiny.cc", "rb.gy"}

df = pd.read_csv("data/phiusiil_clean.csv")
url = df["URL"].astype(str).str.lower()
domain = df["Domain"].astype(str).str.lower().str.replace(r"^www\.", "", regex=True)

df["NoOfDotsInURL"] = url.str.count(r"\.")
df["NoOfHyphensInURL"] = url.str.count("-")
df["HasAtSymbol"] = url.str.contains("@", regex=False).astype(int)
df["IsShortener"] = domain.isin(SHORTENERS).astype(int)
df["HttpsTokenInDomain"] = domain.str.contains("https", regex=False).astype(int)

EXTRA = ["NoOfDotsInURL", "NoOfHyphensInURL", "HasAtSymbol", "IsShortener", "HttpsTokenInDomain"]
print("URLs where each new feature is above zero:")
print((df[EXTRA] > 0).sum().to_string())

y = (df["label"] == 0).astype(int)  # phishing = 1
train_idx, test_idx = train_test_split(df.index, test_size=0.2, stratify=y, random_state=SEED)

sets = {
    "Baseline (19)": BASELINE,
    "Baseline + extra URL (24)": BASELINE + EXTRA,
    "Hybrid (37)": HYBRID,
    "Hybrid + extra URL (42)": HYBRID + EXTRA,
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
        "Accuracy": accuracy_score(y.loc[test_idx], pred),
        "Precision": precision_score(y.loc[test_idx], pred),
        "Recall": recall_score(y.loc[test_idx], pred),
        "F1": f1_score(y.loc[test_idx], pred),
        "Missed phishing (FN)": fn,
        "False alarms (FP)": fp,
    })

out = pd.DataFrame(rows)
out.to_csv("results/extra_features_results.csv", index=False)
pd.set_option("display.width", 200)
print()
print(out.round(4).to_string(index=False))
