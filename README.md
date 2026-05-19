# FAIR Vienna Wet Month Prediction

Machine learning experiment predicting whether a month in Vienna is wet or dry using historical weather data from Hohe Warte station.

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
utils/:  helper functions

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

| Ontology | Namespace | Used for |
|---|---|---|
| QUDT | `http://qudt.org/vocab/quantitykind/` | All physical weather quantities |
| W3C OWL-Time | `http://www.w3.org/2006/time#` | Calendar year and month references |
| W3C WGS84 | `http://www.w3.org/2003/01/geo/wgs84_pos#` | Geodetic coordinates |
| W3C SOSA/SSN | `http://www.w3.org/ns/sosa/` | Weather station (platform) name |
| EU NUTS | `http://data.europa.eu/nuts/code` | NUTS region, district, and sub-district codes |
| Dublin Core Terms | `http://purl.org/dc/terms/` | Surrogate-key identifiers |

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
units using QUDT URIs.

QUDT was selected as a practical fallback to the SI Digital Framework because
it provides stable and widely used URIs for all units needed in this weather
dataset, including degree Celsius, hectopascal, millimeter, meter per second,
percent, hour, meter, and dimensionless quantities.

Physical measurement columns were mapped to their corresponding scientific
units, while count-based columns (such as number of frost days or cloudy days)
were mapped to `number`. Numeric identifiers and administrative codes were
mapped to `unitless` because they represent references or codes rather than
physical measurements.

The mappings are stored in `docs/unit_mapping.csv` and validated against the
live DBRepo schema through the DBRepo Python client.

An attempt was made to integrate the mappings directly into DBRepo metadata
through the REST API. However, the current DBRepo test instance does not expose
a stable public endpoint for updating column-level unit metadata, therefore
the mappings are maintained within the repository as FAIR metadata resources.



## DBRepo views

The experiment defines several SQL views to expose query-ready data for the machine learning pipeline.

### `weather_features_all`

Main ML-ready feature view. It joins monthly weather measurements with the time dimension and station metadata. It contains all weather input features, temporal variables, station information, and the derived binary target variable `wet_month_label`.

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

In addition to the SQL definitions, a DBRepo-compatible view named `weather_measurement_features` was created through the DBRepo Python API. This view exposes the measurement columns from the `weather_measurement` table and can be retrieved through the DBRepo view API.

The SQL definitions are stored in `sql/create_views.sql`, and the DBRepo view creation is implemented in `notebooks/04_create_dbrepo_views.ipynb`.


## Licences

Input dataset: CC BY 4.0 (source data.gv.at)
Source code: MIT License
Generated outputs: To be assigned in later stages

