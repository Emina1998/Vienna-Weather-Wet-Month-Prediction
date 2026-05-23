from __future__ import annotations

import warnings
from typing import Any

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

RANDOM_STATE = 42


def train_models(
    X: pd.DataFrame, y: pd.Series
) -> tuple[dict[str, Any], dict[str, Any]]:
    if X.empty or y.empty:
        raise RuntimeError("Cannot train models on an empty dataset.")
    if len(X) != len(y):
        raise RuntimeError("Feature matrix and target vector have different lengths.")

    split_data = _split_dataset(X, y)
    y_train = split_data["y_train"]
    if y_train.nunique() < 2:
        raise RuntimeError(
            "Training data contains only one target class. Load enough DBRepo "
            "rows to include both wet and dry months before training."
        )

    models: dict[str, Any] = {
        "logreg": Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
                (
                    "classifier",
                    LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
                ),
            ]
        ),
        "randomforest": Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median")),
                (
                    "classifier",
                    RandomForestClassifier(
                        n_estimators=200,
                        random_state=RANDOM_STATE,
                        n_jobs=-1,
                    ),
                ),
            ]
        ),
    }

    for model in models.values():
        model.fit(split_data["X_train"], y_train)

    return models, split_data


def _split_dataset(X: pd.DataFrame, y: pd.Series) -> dict[str, Any]:
    if "ref_year" in X.columns and _chronological_split_possible(X):
        ref_year = pd.to_numeric(X["ref_year"], errors="coerce")
        train_mask = ref_year <= 2016
        validation_mask = ref_year.between(2017, 2019)
        test_mask = ref_year >= 2020
        return {
            "X_train": X.loc[train_mask].copy(),
            "X_validation": X.loc[validation_mask].copy(),
            "X_test": X.loc[test_mask].copy(),
            "y_train": y.loc[train_mask].copy(),
            "y_validation": y.loc[validation_mask].copy(),
            "y_test": y.loc[test_mask].copy(),
            "split_strategy": "chronological",
        }

    print(
        "Warning: chronological split is not possible with the available "
        "years; falling back to random train/validation/test split "
        "with random_state=42."
    )
    warnings.warn(
        "Chronological split is not possible; using random split with "
        "random_state=42.",
        RuntimeWarning,
        stacklevel=2,
    )
    return _random_split(X, y)


def _chronological_split_possible(X: pd.DataFrame) -> bool:
    ref_year = pd.to_numeric(X["ref_year"], errors="coerce")
    if ref_year.isna().all():
        return False

    train_count = int((ref_year <= 2016).sum())
    validation_count = int(ref_year.between(2017, 2019).sum())
    test_count = int((ref_year >= 2020).sum())
    return train_count > 0 and validation_count > 0 and test_count > 0


def _random_split(X: pd.DataFrame, y: pd.Series) -> dict[str, Any]:
    if len(X) < 5:
        raise RuntimeError(
            "At least five rows are required for the fallback random "
            "train/validation/test split."
        )

    stratify = _stratify_or_none(y)
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=stratify,
    )

    validation_stratify = _stratify_or_none(y_train_val)
    X_train, X_validation, y_train, y_validation = train_test_split(
        X_train_val,
        y_train_val,
        test_size=0.25,
        random_state=RANDOM_STATE,
        stratify=validation_stratify,
    )

    return {
        "X_train": X_train.copy(),
        "X_validation": X_validation.copy(),
        "X_test": X_test.copy(),
        "y_train": y_train.copy(),
        "y_validation": y_validation.copy(),
        "y_test": y_test.copy(),
        "split_strategy": "random",
    }


def _stratify_or_none(y: pd.Series) -> pd.Series | None:
    counts = y.value_counts()
    if len(counts) < 2 or counts.min() < 2:
        return None
    return y
