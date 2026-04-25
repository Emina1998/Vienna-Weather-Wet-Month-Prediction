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

## Licences

Input dataset: CC BY 4.0 (source data.gv.at)
Source code: MIT License
Generated outputs: To be assigned in later stages