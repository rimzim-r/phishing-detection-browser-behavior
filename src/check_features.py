import pandas as pd
from features import URL_FEATURES, CONSISTENCY_FEATURES, BEHAVIOR_FEATURES, BASELINE, HYBRID

df = pd.read_csv("data/phiusiil_clean.csv")

missing = [c for c in HYBRID if c not in df.columns]
print("Missing columns:", missing)
print("URL features:", len(URL_FEATURES))
print("Consistency features:", len(CONSISTENCY_FEATURES))
print("Behavior features:", len(BEHAVIOR_FEATURES))
print("Baseline total:", len(BASELINE))
print("Hybrid total:", len(HYBRID))
