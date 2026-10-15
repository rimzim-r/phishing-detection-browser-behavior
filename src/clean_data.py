import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("data/phiusiil.csv")
print("Rows before:", len(df))

print("\nMissing values:", int(df.isna().sum().sum()))
print("Duplicate URLs:", int(df["URL"].duplicated().sum()))

df = df.drop_duplicates(subset="URL").reset_index(drop=True)
print("Rows after removing duplicate URLs:", len(df))

print("\nClass counts after cleaning:")
print(df["label"].value_counts())

df.to_csv("data/phiusiil_clean.csv", index=False)

ax = df["label"].map({0: "Phishing", 1: "Legitimate"}).value_counts().plot(
    kind="bar", color=["black", "grey"])
ax.set_title("Class balance (after cleaning)")
ax.set_ylabel("Number of URLs")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("results/class_balance.png", dpi=150)
print("\nSaved data/phiusiil_clean.csv and results/class_balance.png")
