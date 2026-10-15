import pandas as pd

df = pd.read_csv("data/phiusiil.csv")
print("Shape:", df.shape)
print(df.columns.tolist())
print(df["label"].value_counts())
