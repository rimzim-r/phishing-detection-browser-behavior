from ucimlrepo import fetch_ucirepo

ds = fetch_ucirepo(id=967)
df = ds.data.features.copy()
df["label"] = ds.data.targets["label"]
df.to_csv("data/phiusiil.csv", index=False)

print("Saved. Shape:", df.shape)
print(df["label"].value_counts())
