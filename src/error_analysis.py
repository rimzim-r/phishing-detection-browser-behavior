import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from features import HYBRID

SEED = 42
df = pd.read_csv("data/phiusiil_clean.csv")
y = (df["label"] == 0).astype(int)  # phishing = 1
_, test_idx = train_test_split(df.index, test_size=0.2, stratify=y, random_state=SEED)

model = joblib.load("models/xgb_hybrid.joblib")
test = df.loc[test_idx].copy()
test["actual"] = y.loc[test_idx]
test["pred"] = model.predict(test[HYBRID])
test["phish_prob"] = model.predict_proba(test[HYBRID])[:, 1]

fn = test[(test["actual"] == 1) & (test["pred"] == 0)]
fp = test[(test["actual"] == 0) & (test["pred"] == 1)]
print("Missed phishing (FN):", len(fn))
print("False alarms (FP):", len(fp))

show = ["URL", "phish_prob", "NoOfExternalRef", "NoOfSelfRef", "IsHTTPS",
        "HasTitle", "HasSocialNet", "HasCopyrightInfo", "URLLength"]

def short(d):
    d = d[show].copy()
    d["URL"] = d["URL"].str[:55]
    return d.round(3)

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 20)
print("\n--- Missed phishing pages ---")
print(short(fn).to_string(index=False))
print("\n--- Legitimate pages wrongly flagged ---")
print(short(fp).to_string(index=False))

# average feature values: correct vs wrong
key = ["NoOfExternalRef", "NoOfSelfRef", "IsHTTPS", "HasTitle",
       "HasSocialNet", "HasCopyrightInfo", "URLLength"]
groups = {
    "Phishing caught": test[(test["actual"] == 1) & (test["pred"] == 1)],
    "Phishing missed (FN)": fn,
    "Legit correct": test[(test["actual"] == 0) & (test["pred"] == 0)],
    "Legit flagged (FP)": fp,
}
summary = pd.DataFrame({name: g[key].mean() for name, g in groups.items()}).T
print("\n--- Average feature values by group ---")
print(summary.round(2).to_string())

errors = pd.concat([fn.assign(error="FN"), fp.assign(error="FP")])
errors[["error", "URL", "phish_prob"] + key].to_csv("results/error_analysis.csv", index=False)
print("\nSaved results/error_analysis.csv")
