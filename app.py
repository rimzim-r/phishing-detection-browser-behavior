import joblib
import pandas as pd
import streamlit as st
import sys

sys.path.append("src")
from url_features import extract_url_features

st.set_page_config(page_title="Phishing URL Checker", page_icon="??")
st.title("Phishing URL Checker")
st.caption("Demo: classifies a URL from its text only. The page is never opened.")


@st.cache_resource
def load_model():
    bundle = joblib.load("models/xgb_url_app.joblib")
    return bundle["model"], bundle["features"]


model, feature_names = load_model()

url = st.text_input("Paste a URL (include http:// or https://)")

if st.button("Check") and url.strip():
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
        st.info("No http:// or https:// found, so https:// was added.")

    feats = extract_url_features(url)
    row = pd.DataFrame([feats])[feature_names]
    prob = float(model.predict_proba(row)[0, 1])

    if prob >= 0.5:
        st.error(f"Likely PHISHING (probability {prob:.1%})")
    else:
        st.success(f"Likely LEGITIMATE (phishing probability {prob:.1%})")

    if len(url) > 100 or "?" in url:
        st.warning(
            "Low confidence: this URL is long or has a query string. "
            "The training data mostly contains short homepage-style legitimate URLs, "
            "so the model often flags long legitimate URLs (for example search results) as phishing."
        )

    with st.expander("Features used"):
        st.dataframe(row.T.rename(columns={0: "value"}))

st.markdown("---")
st.caption(
    "Limits: trained on the PhiUSIIL dataset using 15 URL-text features. "
    "It can be wrong on real-world URLs, so treat it as a demo, not a security tool."
)
