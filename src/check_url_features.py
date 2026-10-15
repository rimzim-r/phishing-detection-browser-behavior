import numpy as np
import pandas as pd
from url_features import extract_url_features

df = pd.read_csv("data/phiusiil_clean.csv").sample(3000, random_state=1).reset_index(drop=True)
computed = pd.DataFrame([extract_url_features(u) for u in df["URL"]])

print("Share of rows where our value matches the dataset:")
for col in computed.columns:
    match = np.isclose(computed[col], df[col], atol=0.01).mean()
    print(f"{col:30s} {match:.1%}")

    if match < 0.99:
        bad = np.where(~np.isclose(computed[col], df[col], atol=0.01))[0][:3]
        for i in bad:
            print(f"    e.g. {df['URL'][i][:60]} | ours={computed[col][i]:.3f} dataset={df[col][i]:.3f}")
