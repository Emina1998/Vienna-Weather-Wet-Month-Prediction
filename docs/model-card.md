# Model Card: Vienna Wet-Month Classifiers (v1)

This model card covers two binary classification models trained to predict whether a calendar month
in Vienna is a "wet month" (total precipitation ≥ 60 mm). Both models are part of the FAIR Vienna
Wet Month Prediction experiment and share the same training data, feature set, and evaluation protocol.

---

## 1. Model Description

Two scikit learn classification models were trained as part of this experiment:

- **Logistic Regression (`model_logreg_v1.pkl`)**: A scikit-learn `Pipeline` consisting of a median
  imputer, a standard scaler, and a `LogisticRegression` classifier (`max_iter=1000`, `C=1`,
  `penalty=l2`, `solver=lbfgs`, `random_state=42`). Logistic Regression provides a linear decision
  boundary and serves as the interpretable baseline model in this experiment. It was chosen because
  its coefficients can be inspected to understand which meteorological features contribute most to
  the wet-month prediction.

- **Random Forest (`model_randomforest_v1.pkl`)**: A scikit learn `Pipeline` consisting of a median
  imputer and a `RandomForestClassifier` (200 trees, `criterion=gini`, `max_features=sqrt`,
  `random_state=42`, `n_jobs=-1`). Random Forest is a non-linear ensemble method that captures
  complex interactions between meteorological features. It serves as the primary model in this
  experiment due to its generally stronger performance on tabular data.

Both models are serialised as Python `joblib` pickle files (`.pkl`) and require scikit-learn ≥ 1.0
and Python ≥ 3.10 to load and run. They are versioned at `v1.0.0` and were created on 2026-05-23.

---

## 2. Intended Use

These models are intended for **research and educational purposes**, specifically to demonstrate a
reproducible, FAIR-compliant machine learning experiment using historical weather observations from
the Vienna Hohe Warte meteorological station. They may be used to explore the predictability of wet
months from standard meteorological features in a temperate Central European climate. The experiment
is part of the FAIR Data Science course at TU Wien (DaSt 2026) and is designed to show the best
practices in open science, like data citation, metadata standards and model documentation.

---

## 3. Out-of-Scope Uses

These models are **not** intended for operational weather forecasting or any climate-sensitive
decision-making in real-world applications. They should not be applied to meteorological stations
other than Hohe Warte (Vienna) without retraining and thorough validation on local data, as the
models have been trained exclusively on one station's historical record. They are not suitable for
predicting extreme precipitation events, short-term weather forecasts, or for use in flood risk
assessment, agricultural planning, or any safety-critical context.

---

## 4. Training Data

Both models were trained on monthly weather observations from the **Hohe Warte meteorological
station** in Vienna, Austria, spanning **1872 to 2016** (training split). The data was sourced from
Stadt Wien / MA 23 and published on the Austrian open government data portal under a
**CC BY 4.0** licence.

- **Source URL**: https://www.data.gv.at/datasets/69a06550-1ede-4f50-9c36-e7fb5cf6e7e8
- **TUWRD deposit DOI**: `PLACEHOLDER_TUWRD_MODEL_DEPOSIT_DOI` *(update after T3.9 deposit)*
- **Split strategy**: Chronological — training on years ≤ 2016, validation on 2017–2019, test on
  years ≥ 2020
- **Features**: 27 meteorological and spatial features including temperature (mean, max, min),
  atmospheric pressure, relative humidity, wind velocity, sunshine hours, precipitation-day counts,
  and station coordinates
- **Target**: Binary label `wet_month_label` — 1 if monthly precipitation ≥ 60 mm, else 0
- **Missing values**: Median imputation applied to all numeric features prior to training

---

## 5. Evaluation Results

Both models were evaluated on the **chronological test split** (years ≥ 2020). All metrics below
are reported for the positive class (wet month = 1).

| Model               | Accuracy | Precision | Recall | F1 Score |
|---------------------|----------|-----------|--------|----------|
| Logistic Regression | 0.747    | 0.688     | 0.440  | 0.537    |
| Random Forest       | 0.760    | 0.706     | 0.480  | 0.571    |

The Random Forest outperforms Logistic Regression across all metrics. Both models show moderate
recall, meaning they miss a notable proportion of actual wet months; this is partly attributable to
class imbalance in the dataset (wet months are less frequent than dry months) and the relatively
small test set (years 2020 and  after). Confusion matrices for both models are available at
`outputs/figures/fig_confusion_matrix_logreg_v1.png` and
`outputs/figures/fig_confusion_matrix_randomforest_v1.png`.

---

## 6. Limitations

- Both models are trained on data from a **single station** which is Hohe Warte, Vienna and are not likely going
  to generalize to other geographic locations or climate zones without retraining.
- Historical records **before 1951** have structural missing values for several features (e.g.
  `rel_hum_max_pct`, `wind_vel_max_ms`, `sun_h`), which are imputed with medians; this may
  introduce systematic bias for predictions involving the early historical period.
- The **chronological test split** evaluates the models only on the most recent years (2020
  and after), which may not represent the full range of climate variability present in the 150 year
  dataset.
- **Class imbalance** between wet and dry months is not explicitly addressed (e.g. via oversampling
  or class weights), which contributes to the relatively low recall values of 0.44 and 0.48.
- The **Random Forest model is not easily interpretable**; feature importance values are available
  but do not provide causal explanations of the predictions.

---

## 7. Ethical Considerations

The dataset used to train these models does not contain any personal data.  All observations
are meteorological measurements from a weather station. No sensitive attributes (demographic,
financial, health-related, or otherwise) are in the data or used as features. The models'
predictions carry no direct societal risk in their intended research and educational context. The
source data is published by a public authority (Stadt Wien) under an open licence (CC BY 4.0),
and proper attribution is given throughout this experiment.

---

## 8. Licence

The trained model artefacts (`model_logreg_v1.pkl`, `model_randomforest_v1.pkl`) are released
under the **Creative Commons Attribution 4.0 International (CC BY 4.0)** licence. You are free to
share and adapt these artefacts for any purpose, provided appropriate credit is given, a link to the
licence is provided, and any changes are indicated.

Licence text: https://creativecommons.org/licenses/by/4.0/

---

## References

- FAIR4ML metadata (Logistic Regression): `docs/fair4ml/fair4ml_logreg_v1.json`
- FAIR4ML metadata (Random Forest): `docs/fair4ml/fair4ml_randomforest_v1.json`
- RO-Crate: `ro-crate-metadata.json` *(to be added — T3.1)*
- Source dataset: https://www.data.gv.at/datasets/69a06550-1ede-4f50-9c36-e7fb5cf6e7e8
- Code repository: https://github.com/Emina1998/Vienna-Weather-Wet-Month-Prediction