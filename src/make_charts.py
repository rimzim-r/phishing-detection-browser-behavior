import joblib
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix
from features import BASELINE, HYBRID, URL_FEATURES, CONSISTENCY_FEATURES

SEED = 42
df = pd.read_csv("data/phiusiil_clean.csv")
y = (df["label"] == 0).astype(int)  # phishing = 1
_, test_idx = train_test_split(df.index, test_size=0.2, stratify=y, random_state=SEED)
y_test = y.loc[test_idx]

base_model = joblib.load("models/xgb_baseline.joblib")
hyb_model = joblib.load("models/xgb_hybrid.joblib")

# 1) Confusion matrices
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
for ax, model, cols, title in [
    (axes[0], base_model, BASELINE, "Baseline (URL only)"),
    (axes[1], hyb_model, HYBRID, "Hybrid (URL + behavior)"),
]:
    pred = model.predict(df.loc[test_idx, cols])
    cm = confusion_matrix(y_test, pred)
    ConfusionMatrixDisplay(cm, display_labels=["Legitimate", "Phishing"]).plot(
        ax=ax, cmap="Greys", colorbar=False, values_format="d")
    ax.set_title(title)
    tn, fp, fn, tp = cm.ravel()
    print(f"{title}: missed phishing (FN) = {fn}, false alarms (FP) = {fp}, phishing in test = {fn + tp}")
plt.suptitle("XGBoost confusion matrices")
plt.tight_layout()
plt.savefig("results/confusion_matrix.png", dpi=150)
plt.close()

# 2) Feature importance (hybrid XGBoost, top 15)
imp = pd.Series(hyb_model.feature_importances_, index=HYBRID).sort_values(ascending=False)
top = imp.head(15)[::-1]
def group_color(name):
    if name in URL_FEATURES:
        return "lightgrey"
    if name in CONSISTENCY_FEATURES:
        return "grey"
    return "black"
plt.figure(figsize=(8, 6))
plt.barh(top.index, top.values, color=[group_color(n) for n in top.index], edgecolor="black")
plt.title("Top 15 features (Hybrid XGBoost)")
plt.xlabel("Importance")
from matplotlib.patches import Patch
plt.legend(handles=[
    Patch(facecolor="lightgrey", edgecolor="black", label="URL"),
    Patch(facecolor="grey", edgecolor="black", label="Page consistency"),
    Patch(facecolor="black", edgecolor="black", label="Browser behavior"),
], loc="lower right")
plt.tight_layout()
plt.savefig("results/feature_importance.png", dpi=150)
plt.close()
print("\nTop 10 features:")
print(imp.head(10).round(4).to_string())

# 3) Recall comparison
res = pd.read_csv("results/model_results.csv")
piv = res.pivot(index="Model", columns="Feature set", values="Recall")
piv = piv[["Baseline (URL only)", "Hybrid (URL + behavior)"]]
ax = piv.plot(kind="bar", figsize=(9, 5), color=["lightgrey", "black"], edgecolor="black")
ax.set_ylim(0.990, 1.0005)
ax.set_ylabel("Phishing recall (axis starts at 0.990)")
ax.set_title("Phishing recall: baseline vs hybrid")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("results/recall_comparison.png", dpi=150)
plt.close()

print("\nSaved 3 charts in the results folder.")
