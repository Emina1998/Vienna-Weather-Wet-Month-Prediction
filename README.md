# Vienna Weather Wet-Month Prediction

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20364604.svg)](https://doi.org/10.5281/zenodo.20364604)

A reproducible, FAIR-compliant machine learning experiment that predicts whether
a given calendar month in Vienna is a "wet month" (total precipitation ≥ 60 mm)
using 150 years of historical weather observations from the Hohe Warte station.
The experiment trains two binary classifiers — Logistic Regression and Random
Forest — on monthly meteorological data published by Stadt Wien under CC BY 4.0.
All data is stored and retrieved from DBRepo. The full experiment is reproducible from this repository.

---

## Requirements and installation

**Python version:** 3.11.0

Install dependencies using pip:

```bash
pip install -r requirements.txt
```

The `requirements.txt` includes:

- `pandas` — data loading and transformation
- `numpy` — numerical operations
- `scikit-learn` — model training and evaluation
- `matplotlib` — figure generation
- `joblib` — model serialisation
- `python-dotenv` — environment variable management
- `dbrepo==1.13.4` — DBRepo Python REST client

Before running the experiment, copy `.env.example` to `.env` and fill in your
DBRepo credentials:

```bash
cp .env.example .env
```

---

## Reproducing the experiment

Follow these steps in order to fully reproduce the experiment from scratch.

**Step 1 — Clone the repository**

```bash
git clone https://github.com/Emina1998/Vienna-Weather-Wet-Month-Prediction.git
cd Vienna-Weather-Wet-Month-Prediction
```

**Step 2 — Install dependencies**

```bash
pip install -r requirements.txt
```

**Step 3 — Configure DBRepo credentials**

Copy `.env.example` to `.env` and fill in your DBRepo username and password.
The database and table IDs are already set to the correct values above.

**Step 4 — (Optional) Set up DBRepo from scratch**

If you want to recreate the database and load the data yourself, run the
following notebooks in order:

1. `notebooks/dbRepo_setup.ipynb` — creates the database and tables in DBRepo
2. `notebooks/t2_2_semantic_mapping.ipynb` — adds semantic concept mappings
3. `notebooks/t2_3_unit_mapping.ipynb` — adds unit of measurement mappings
4. `notebooks/t2_4_create_dbrepo_views.ipynb` — creates the DBRepo view
5. `notebooks/t2_5_load_data_to_dbrepo.ipynb` — loads the cleaned data into DBRepo

**Step 5 — Run the experiment**

```bash
python -m src.pipeline.run_experiment
```

This will load data from DBRepo, train both models, evaluate them on the
chronological test split (2020 onwards), and write all output artefacts to
`outputs/`.

**Step 6 — (Optional) Verify DBRepo reimplementation**

To confirm the DBRepo-based pipeline produces identical results to the original
local-file version:

```bash
python -m src.pipeline.compare_local_vs_dbrepo --raw-csv data/raw/weather_raw_vienna_hohewarte_v1.csv
```

---

## Inputs and outputs

### Input dataset

| File                                           | Description                                                                                | Source                                                                             |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------- |
| `data/raw/weather_raw_vienna_hohewarte_v1.csv` | Raw monthly weather observations from Hohe Warte station, 1872–2026, 1847 rows, 29 columns | [data.gv.at](https://www.data.gv.at/datasets/69a06550-1ede-4f50-9c36-e7fb5cf6e7e8) |
| `data/processed/station_v1.csv`                | Cleaned station metadata                                                                   | Derived from raw CSV                                                               |
| `data/processed/time_dimension_v1.csv`         | Normalised year/month references                                                           | Derived from raw CSV                                                               |
| `data/processed/weather_measurement_v1.csv`    | Cleaned measurement table                                                                  | Derived from raw CSV                                                               |

The raw dataset contains monthly measurements of temperature, atmospheric
pressure, precipitation, relative humidity, wind speed, sunshine duration, and
counts of special weather days (frost days, ice days, summer days, heat days).
Two rows with missing pressure values were excluded before loading into DBRepo,
leaving 1845 usable observations. Structural missing values in humidity, wind,
and sunshine columns before 1951 are preserved as NULL.

### Output artefacts

| File                                                       | Description                                                       |
| ---------------------------------------------------------- | ----------------------------------------------------------------- |
| `outputs/models/model_logreg_v1.pkl`                       | Trained Logistic Regression pipeline (scikit-learn)               |
| `outputs/models/model_randomforest_v1.pkl`                 | Trained Random Forest pipeline (scikit-learn)                     |
| `outputs/predictions/model_metrics_v1.csv`                 | Accuracy, precision, recall, F1 for both models on the test split |
| `outputs/predictions/predictions_test_v1.csv`              | Row-level predictions on the test set                             |
| `outputs/figures/fig_confusion_matrix_logreg_v1.png`       | Confusion matrix for Logistic Regression                          |
| `outputs/figures/fig_confusion_matrix_randomforest_v1.png` | Confusion matrix for Random Forest                                |
| `outputs/figures/fig_model_comparison_v1.png`              | Bar chart comparing both models across all metrics                |

### Model performance (test split, ref_year ≥ 2020)

| Model               | Accuracy | Precision | Recall | F1    |
| ------------------- | -------- | --------- | ------ | ----- |
| Logistic Regression | 0.747    | 0.688     | 0.440  | 0.537 |
| Random Forest       | 0.760    | 0.706     | 0.480  | 0.571 |

---

## File organisation

### data/

raw/: Contains the original dataset as obtained from the source (source data.gv.at)

- processed/: Contains cleaned and transformed datasets used for model training.
- external/: additional sources

### src/

Python source code, organized by functionality:
data/: data loading scripts
features/: feature engineering
models/: model training
evaluation/: evaluation scripts
utils/: helper functions

### outputs/

Generated results:
figures/: plots and visualizations
models/: trained model artefacts
predictions/: prediction outputs

### docs/

Documentation, metadata, validation files.

### config/

Contains configuration files for models and data processing.

### sql/

Contains SQL definitions for the database schema and DBRepo views.

### File naming convention

A consistent naming convention is applied across all files:

#### Input datasets

weather_raw_hohewarte_v1.csv
weather_processed_monthly_v1.csv

#### Figures

fig_distribution_precipitation_v1.png
fig_confusion_matrix_rf_v1.png
fig_model_comparison_v1.png

#### Models

model_logreg_v1.pkl
model_randomforest_v1.pkl

#### Predictions

predictions_test_v1.csv

#### Scripts

load_data.py
preprocess_data.py
train_model.py
evaluate_model.py

#### Configuration files

config_model.yaml
config_data.yaml

## Ontology selection

We use **QUDT (Quantities, Units, Dimensions and Types)** for all physical weather quantities, including temperature, pressure, precipitation, relative humidity, wind velocity, sunshine duration, altitude, and count-based weather-day variables. QUDT is suitable because it provides curated, machine-readable concepts for scientific quantity kinds and aligns directly with the unit mapping performed in T2.3. It is a widely adopted standard for representing measurable physical phenomena, making it preferable to generic vocabularies for these fields.

For temporal calendar components (`ref_year`, `ref_month`), we use **W3C OWL-Time** (`time:year`, `time:month`), which provides explicit concepts for year and month as calendar subdivisions. This is more precise than QUDT's generic `Time` quantity kind, which describes time as a physical dimension rather than a structured calendar reference.

For geodetic coordinates (`latitude_deg`, `longitude_deg`), we use the **W3C WGS84 geo vocabulary** (`wgs84_pos:lat`, `wgs84_pos:long`), the standard linked-data vocabulary for geographic point locations. For the station name, we use **W3C SOSA/SSN** (`sosa:Platform`), as a weather station is formally a platform that hosts sensors — making SOSA the most semantically accurate domain-specific choice.

For all three administrative division codes (`nuts_code`, `district_code`, `sub_district_code`), we use the **EU NUTS linked-data vocabulary** (`data.europa.eu/nuts/code`), which directly models European administrative identifiers. All three fields hold typed NUTS codes (e.g. `AT13`, `91900`, `91905`) and are therefore correctly represented by the NUTS vocabulary. For remaining identifier and surrogate-key fields (`measurement_id`, `station_num`, `time_id`), **Dublin Core Terms** (`dcterms:identifier`) is used as a fallback, as these fields carry no domain-specific physical or spatial meaning.

Two QUDT quantity kinds deviate intentionally from the base spec for greater semantic precision:

- `precp_sum_mm` maps to `qudt:LengthOrDepth` rather than `qudt:Length`, because precipitation accumulation is conventionally expressed as a depth (mm of water column), not a generic linear length.
- `sun_h` maps to `qudt:Duration` rather than `qudt:Time`, because sunshine hours represent an elapsed duration, not a point in time or a time coordinate.

Both choices remain within QUDT and are more accurate representations of the underlying physical quantities.

---

## Ontologies used

| Ontology          | Namespace                                  | Used for                                      |
| ----------------- | ------------------------------------------ | --------------------------------------------- |
| QUDT              | `http://qudt.org/vocab/quantitykind/`      | All physical weather quantities               |
| W3C OWL-Time      | `http://www.w3.org/2006/time#`             | Calendar year and month references            |
| W3C WGS84         | `http://www.w3.org/2003/01/geo/wgs84_pos#` | Geodetic coordinates                          |
| W3C SOSA/SSN      | `http://www.w3.org/ns/sosa/`               | Weather station (platform) name               |
| EU NUTS           | `http://data.europa.eu/nuts/code`          | NUTS region, district, and sub-district codes |
| Dublin Core Terms | `http://purl.org/dc/terms/`                | Surrogate-key identifiers                     |

---

## Database schema

Three tables are defined in `create_schema.sql`:

- `station` — metadata for each measurement station (location, administrative codes, coordinates)
- `time_dimension` — normalised year/month time reference
- `weather_measurement` — all monthly meteorological observations, keyed to station and time

---

## Semantic mapping

All column-to-ontology mappings are documented in `docs/semantic_mapping.csv` using the header:

```
table_name,column_name,ontology_uri,ontology_label
```

The file covers all 38 columns across the three tables.

---

## Dataset notes

- Source: Hohe Warte meteorological station, Vienna (data.gv.at, CC BY 4.0)
- Time span: April 1872 – present (1,847 monthly rows)
- Two station numbers are present: `5901` (1872–1992) and `5904` (1993–present), reflecting a station renumbering in 1993
- Missing values in `REL_HUM_MAX`, `REL_HUM_MIN`, `WIND_VEL_MAX`, `NUM_WIND_VEL60` before 1951, and `SUN_H` before 1921, are structural — the instruments did not yet exist. These are stored as `NULL`.

---

## DBRepo metadata integration

Semantic mappings are added to DBRepo metadata via the REST API using the notebook at `notebooks/t2_2_semantic_mapping_upload.ipynb`.

## Unit mapping

All numeric attributes in the database schema were mapped to ontology-based
units using OM-2 (Ontology of Units of Measure) URIs.

OM-2 was selected instead of the recommended SI Digital Framework because it is
already registered and supported within the DBRepo metadata registry, making
direct API integration possible. It provides stable, widely used URIs for all
units needed in this dataset, including degree Celsius, hectopascal, millimetre,
metre per second, percent, hour, metre, year, month, and dimensionless quantities.

Physical measurement columns were mapped to their corresponding scientific
units, while count-based columns (such as number of frost days or cloudy days)
were mapped to `om-2/one` (number). Numeric identifiers and administrative codes
were also mapped to `om-2/one` (unitless) because they represent references or
codes rather than physical measurements.

The mappings are stored in `docs/unit_mapping.csv` and were pushed to DBRepo
column metadata via the REST API using `notebooks/t2_3_unit_mapping.ipynb`.

## DBRepo views

The experiment defines several SQL views to expose query-ready data for the machine learning pipeline.

### `weather_features_all`

Main ML-ready feature view. It joins monthly weather measurements from `weather_measurement_v2` with the time dimension and station metadata. It contains all weather input features, temporal variables, station information, and the derived binary target variable `wet_month_label`.

The target variable is defined as:

```sql
CASE WHEN precp_sum_mm >= 60 THEN 1 ELSE 0 END
```

where `1` indicates a wet month and `0` indicates a dry month.

### `weather_train`

Training split containing observations up to and including 2016.

### `weather_validation`

Validation split containing observations from 2017 to 2019.

### `weather_test`

Held-out test split containing observations from 2020 onward.

### `monthly_precipitation_summary`

Aggregation view that summarizes average, minimum, and maximum monthly precipitation by calendar month. This view is used for exploratory analysis and for checking seasonal precipitation patterns.

### DBRepo-compatible view

In addition to the SQL definitions, a DBRepo-compatible view named `weather_measurement_v2_features` was created through the DBRepo Python API. This view exposes the measurement columns from the corrected `weather_measurement_v2` table and can be retrieved through the DBRepo view API.

The DBRepo-compatible view contains measurement-table columns only. Therefore, the final ML pipeline first attempts to load this view and then falls back to loading the three DBRepo base tables (`weather_measurement_v2`, `time_dimension`, `station`) and joining them locally in pandas when temporal and station metadata are required.

The SQL definitions are stored in `sql/create_views.sql`, and the DBRepo view creation is implemented in `notebooks/t2_4_create_dbrepo_views.ipynb`.

## DBRepo data loading

The real input data is loaded into DBRepo using the notebook `notebooks/t2_5_load_data_to_dbrepo.ipynb`.

The normalized DBRepo schema consists of:

- `station` — station metadata for Hohe Warte, including the two historical station numbers
- `time_dimension` — normalized year/month references
- `weather_measurement_v2` — monthly meteorological measurements linked to station and time

The loaded DBRepo dataset contains:

- `weather_measurement_v2`: 1845 rows
- `time_dimension`: 1845 rows
- `station`: 2 rows

Two source records were excluded before loading because all pressure fields (`p_mean_hpa`, `p_max_hpa`, `p_min_hpa`) were missing. This removes 2 of the original 1847 rows and avoids replacing missing pressure values with artificial zeros. Structural missing values in historical humidity, wind, and sunshine columns are preserved as `NULL`.

The DBRepo-compatible view `weather_measurement_v2_features` returns 1845 rows, matching the loaded measurement table.

## DBRepo API reimplementation

The final experiment code retrieves data exclusively from DBRepo via the REST/Python API. It does not read local CSV files during model training or evaluation.

- DBRepo base URL: `https://test.dbrepo.tuwien.ac.at`
- Database ID: `a181cad5-4bdb-48b2-937e-3e75293f6a7b`
- Preferred DBRepo view: `weather_measurement_v2_features`
- Base-table fallback: `weather_measurement_v2`, `time_dimension`, `station`
- Authentication method: DBRepo username/password loaded from `.env`

The following environment variables are required:

```env
DBREPO_ENDPOINT=https://test.dbrepo.tuwien.ac.at
DBREPO_USERNAME=<your-username>
DBREPO_PASSWORD=<your-password>
DBREPO_DATABASE_ID=a181cad5-4bdb-48b2-937e-3e75293f6a7b
DBREPO_TABLE_WEATHER_MEASUREMENT_ID=3674fea3-a7be-4dfe-8356-bc692bd1ff6c
DBREPO_TABLE_TIME_DIMENSION_ID=fa248a2c-bfb6-4d8e-a89b-2dbd19ab8cde
DBREPO_TABLE_STATION_ID=ab02386c-e27c-4c1f-a27d-93034ce3fa79
```

The pipeline first attempts to load the DBRepo view `weather_measurement_v2_features`. Since this DBRepo-compatible view contains only measurement-table columns, the loader falls back to retrieving the three DBRepo base tables and joins them locally in pandas. No local CSV files are used in the final experiment pipeline.

Run the full DBRepo-based experiment with:

```bash
python -m src.pipeline.run_experiment
```

The pipeline trains Logistic Regression and Random Forest classifiers using a chronological split and writes these artefacts:

- `outputs/predictions/model_metrics_v1.csv`
- `outputs/predictions/predictions_test_v1.csv`
- `outputs/figures/fig_confusion_matrix_logreg_v1.png`
- `outputs/figures/fig_confusion_matrix_randomforest_v1.png`
- `outputs/figures/fig_model_comparison_v1.png`
- `outputs/models/model_logreg_v1.pkl`
- `outputs/models/model_randomforest_v1.pkl`

The DBRepo API reimplementation can be verified against the original local-file preprocessing pipeline with:

```bash
python -m src.pipeline.compare_local_vs_dbrepo --raw-csv data/raw/weather_raw_vienna_hohewarte_v1.csv
```

This comparison script is used only for verification. It applies the same documented cleaning rule to the local raw CSV and confirms that the DBRepo API version produces the same cleaned dataset: 1845 observations, identical target labels, and equivalent feature values.

## Croissant metadata

Croissant JSON-LD metadata for the raw input weather dataset is stored at `docs/croissant/weather_raw_hohewarte_croissant.json`. The record describes the raw CSV field names, data types, OM-2 unit URIs, source and distribution information, and licence.

The unit URIs are based on `docs/unit_mapping.csv` and the DBRepo unit metadata from T2.3. The source dataset is published by Stadt Wien via data.gv.at and is licensed under CC BY 4.0.

## Licences

### Input Data

The source dataset (_Wetter seit 1872 — Hohe Warte Wien_) is published by
Stadt Wien under **CC BY 4.0** (`CC-BY-4.0`, Creative Commons Attribution 4.0
International). Use of this dataset for research and machine learning purposes
is explicitly permitted under this licence. Attribution to Stadt Wien —
data.gv.at is required in any derived work. CC BY 4.0 contains no ShareAlike
clause, meaning derived works and output data are not required to adopt the
same licence.

### Software / Code

All code in this repository is released under the **MIT Licence** (`MIT`)
(see `LICENSE`). MIT was chosen because it is a simple, permissive open-source
licence that imposes no conditions conflicting with the CC BY 4.0 input data
licence. It allows free use, modification, and distribution of the software
for any purpose, which is appropriate for an open academic research project.

### Output / Generated Data

All output artefacts produced by this experiment — including trained models,
model predictions, evaluation figures, confusion matrices, and classification
results — are released under **CC BY 4.0** (`CC-BY-4.0`, Creative Commons
Attribution 4.0 International). This is consistent with the input data
licence, ensures outputs remain openly reusable with attribution, and satisfies
the requirements of the TU Wien Research Data Repository deposit (T3.10).

## Contributors

Role | Name | Orcid
Azra Sisic(Person A) | [0009-0006-0701-5821](https://orcid.org/0009-0006-0701-5821) |
Raja Shahroz (Person B) | [0009-0003-5130-1049](https://orcid.org/0009-0003-5130-1049) |
Emina Skrijelj(Person C) | [0009-0002-0794-5341](https://orcid.org/0009-0002-0794-5341) |
Kerim Halilovic (Person D) | [0009-0001-9615-5191](https://orcid.org/0009-0001-9615-5191) |

---
