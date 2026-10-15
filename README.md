# A Lightweight AI-Based Phishing Detection System Using Browser Behavior Analysis

Does adding page-consistency and browser-related features to URL features improve phishing detection? This project tests that with a baseline model (URL features only) and a hybrid model, runs an ablation to see which feature group actually helps, analyses the model's mistakes, and adds a small demo app and a Selenium proof of concept for recording real browser behavior.

## Dataset

PhiUSIIL Phishing URL Dataset (UCI Machine Learning Repository): 235,795 URLs, of which 235,370 remain after removing 425 duplicate URLs. The dataset is not included in this repository because of its size.

## Method

- Features were split into three groups: URL (19), page consistency (10) and browser behavior (8).
- Three columns (URLSimilarityIndex, TLDLegitimateProb, URLCharProb) were excluded because they are computed from other URLs in the dataset and could inflate results.
- Models: Logistic Regression, Decision Tree, Random Forest, XGBoost.
- Evaluation: 80/20 stratified split (47,074 test URLs), phishing as the positive class.

## Results

XGBoost, baseline vs hybrid:

| Feature set | Accuracy | Precision | Recall | F1 | Missed phishing |
|---|---|---|---|---|---|
| Baseline (URL only, 19 features) | 0.9976 | 0.9996 | 0.9948 | 0.9972 | 104 |
| Hybrid (all 37 features) | 0.9996 | 0.9996 | 0.9994 | 0.9995 | 13 |

The hybrid model reduced missed phishing URLs from 104 to 13 (about 87% fewer) out of roughly 20,100 phishing URLs in the test set. All four models improved with the hybrid feature set. Full results are in `results/model_results.csv`.

### Ablation (XGBoost)

| Feature set | Features | Missed phishing | False alarms |
|---|---|---|---|
| URL only | 19 | 104 | 9 |
| URL + page consistency | 29 | 14 | 8 |
| URL + browser behavior | 27 | 106 | 13 |
| URL + consistency + behavior | 37 | 13 | 8 |

Almost all of the improvement comes from the page-consistency features (for example, the number of external references). The browser-behavior features alone gave no improvement over URL-only features and added one extra catch on top of the consistency features.

### Error analysis

The hybrid model missed 13 phishing pages and wrongly flagged 8 legitimate pages.

| Group | External links | Self links | HTTPS | URL length |
|---|---|---|---|---|
| Phishing caught | 1.1 | 0.5 | 49% | 45 |
| Phishing missed | 7.3 | 1.7 | 100% | 26 |
| Legitimate, correct | 84 | 113 | 100% | 26 |
| Legitimate, flagged wrongly | 1.1 | 1.1 | 100% | 32 |

Missed phishing pages look like normal sites, and wrongly flagged legitimate pages are very thin. The model partly measures how rich a page is, so a phishing page cloned from a content-rich site could evade it. The groups are small, so these are indications, not proof. Details are in `results/error_analysis.csv`.

### Extra URL features

Dot count, hyphen count, "@" in the URL, URL shorteners and "https" in the domain (suggested in the project plan, not in PhiUSIIL) were computed from the URL text and tested. They made no measurable difference (104 to 109 missed for the baseline, 13 to 12 for the hybrid). Results are in `results/extra_features_results.csv`.

### Charts

![Confusion matrices](results/confusion_matrix.png)
![Feature importance](results/feature_importance.png)
![Recall comparison](results/recall_comparison.png)

## Demo app (Streamlit)

`app.py` classifies a URL from its text alone. It never opens the page. It uses 15 URL features computed by `src/url_features.py` and an XGBoost model trained on those same features.

The hybrid model is not used in the app. Its page features were extracted by the dataset authors from HTML files that are not part of the dataset, so our own code cannot reproduce them reliably.

| Model | Features | Missed phishing | False alarms |
|---|---|---|---|
| Dataset baseline | 19 | 104 | 9 |
| App model | 15 | 171 | 56 |

Known limitation: a normal Bing search URL was flagged as phishing with very high probability, while `https://www.wikipedia.org` was marked legitimate. PhiUSIIL's legitimate URLs are mostly short homepage-style links, so the model tends to treat long URLs with query strings as phishing. The app shows a low-confidence warning for those URLs. It is a demo, not a security tool.

## Browser behavior module (proof of concept)

`src/browser_behavior.py` opens a page in headless Chrome using Selenium and records redirects, popups, hidden iframes, hidden fields, password fields, forms that submit to another domain, and disabled right-click.

It was tested only on three harmless mock pages in `demo_pages/`. The legitimate-looking page scored zero on every behavior. The phishing-like page showed 1 redirect, 2 popups, 1 iframe, 2 hidden fields, 1 password field, 1 external form submit and a disabled right-click (`results/browser_behavior_demo.csv`).

It has not been run on live phishing sites, which is unsafe outside an isolated virtual machine, and its output has not been used to train a model.

## Limitations

- The "browser behavior" columns in PhiUSIIL are extracted from static page HTML, not recorded from a live browser session.
- The URL-only baseline is already very strong (about 99.7% accuracy), so the room for improvement is small.
- All results come from one dataset snapshot and have not been tested on an independent dataset or on live pages.
- The demo app is weaker than the research models and unreliable on long URLs with query strings.
- The Selenium module is a proof of concept tested on mock pages only.

## Future scope

- Run the Selenium module on live pages inside a virtual machine and use its output to train a model.
- A browser extension that warns users in real time.
- Test on a second, independent dataset.
- Multilingual phishing detection.

## Project structure

    app.py         Streamlit demo app
    data/          dataset files (not tracked)
    demo_pages/    mock pages for the Selenium test
    models/        saved XGBoost models
    notebooks/     phishing_analysis.ipynb (results walkthrough)
    results/       result tables and charts
    src/           scripts for cleaning, features, training, analysis and the browser module

## How to run

1. Download the PhiUSIIL dataset from UCI and save it as `data/phiusiil.csv`.
2. Create and activate a virtual environment, then install the libraries:

        python -m venv venv
        venv\Scripts\activate
        pip install -r requirements.txt

3. Run the scripts in this order:

        python src\clean_data.py
        python src\train_models.py
        python src\make_charts.py
        python src\ablation.py
        python src\error_analysis.py
        python src\extra_features_experiment.py
        python src\train_app_model.py
        python src\browser_behavior.py

4. Start the demo app:

        streamlit run app.py

5. Open `notebooks/phishing_analysis.ipynb` to see the results.