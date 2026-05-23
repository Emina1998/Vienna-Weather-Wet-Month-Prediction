from __future__ import annotations

import warnings

import pandas as pd

TARGET_COLUMN = "wet_month_label"
PRECIPITATION_COLUMN = "precp_sum_mm"
WET_MONTH_THRESHOLD_MM = 60.0

ID_COLUMNS = ["measurement_id", "station_num", "time_id"]

FEATURE_COLUMNS = [
    "t_mean_c",
    "t_max_c",
    "t_min_c",
    "mean_t_max_c",
    "mean_t_min_c",
    "p_mean_hpa",
    "p_max_hpa",
    "p_min_hpa",
    "num_precp_01",
    "rel_hum_pct",
    "rel_hum_max_pct",
    "rel_hum_min_pct",
    "wind_vel_ms",
    "wind_vel_max_ms",
    "num_wind_vel60",
    "sun_h",
    "num_clear",
    "num_cloud",
    "num_frost",
    "num_ice",
    "num_summer",
    "num_heat",
    "ref_year",
    "ref_month",
    "latitude_deg",
    "longitude_deg",
    "altitude_m",
]


def build_ml_dataset(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Build model features and binary wet-month target from DBRepo data."""

    if df.empty:
        raise RuntimeError("Cannot build ML dataset from an empty DataFrame.")

    data = _normalise_column_names(df)
    if PRECIPITATION_COLUMN not in data.columns:
        raise RuntimeError(
            f"Cannot create target: missing required column "
            f"'{PRECIPITATION_COLUMN}'."
        )

    data = data.copy()
    data[PRECIPITATION_COLUMN] = pd.to_numeric(
        data[PRECIPITATION_COLUMN], errors="coerce"
    )
    missing_target = data[PRECIPITATION_COLUMN].isna()
    if missing_target.any():
        warnings.warn(
            f"Dropping {int(missing_target.sum())} rows with missing "
            f"{PRECIPITATION_COLUMN}; the wet-month target cannot be inferred "
            "for those records.",
            RuntimeWarning,
            stacklevel=2,
        )
        data = data.loc[~missing_target].copy()

    if data.empty:
        raise RuntimeError(
            "No rows remain after removing records with missing precipitation."
        )

    data[TARGET_COLUMN] = (data[PRECIPITATION_COLUMN] >= WET_MONTH_THRESHOLD_MM).astype(
        int
    )

    available_features = [
        column for column in FEATURE_COLUMNS if column in data.columns
    ]
    missing_features = [
        column for column in FEATURE_COLUMNS if column not in data.columns
    ]
    if missing_features:
        warnings.warn(
            "Missing optional feature column(s) will be skipped: "
            f"{', '.join(missing_features)}",
            RuntimeWarning,
            stacklevel=2,
        )

    if not available_features:
        raise RuntimeError("No usable ML feature columns are available.")

    drop_columns = set(ID_COLUMNS + [PRECIPITATION_COLUMN, TARGET_COLUMN])
    feature_columns = [
        column for column in available_features if column not in drop_columns
    ]
    X = data[feature_columns].copy()
    for column in X.columns:
        X[column] = pd.to_numeric(X[column], errors="coerce")

    X = _median_impute_numeric_features(X)
    y = data[TARGET_COLUMN].astype(int)
    y.name = TARGET_COLUMN

    return X, y


def _median_impute_numeric_features(X: pd.DataFrame) -> pd.DataFrame:
    imputed = X.copy()
    for column in imputed.columns:
        median = imputed[column].median()
        if pd.isna(median):
            warnings.warn(
                f"Feature '{column}' contains only missing values; filling with 0.",
                RuntimeWarning,
                stacklevel=2,
            )
            median = 0
        imputed[column] = imputed[column].fillna(median)
    return imputed


def _normalise_column_names(df: pd.DataFrame) -> pd.DataFrame:
    renamed = {
        column: str(column).strip().lower()
        for column in df.columns
        if str(column).strip().lower() != column
    }
    return df.rename(columns=renamed)
