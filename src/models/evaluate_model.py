from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any

os.environ.setdefault("XDG_CACHE_HOME", str(Path(tempfile.gettempdir()) / "cache"))
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "matplotlib"))

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

MODEL_FILE_STEMS = {
    "logreg": "logreg",
    "randomforest": "randomforest",
}


def evaluate_models(
    models: dict[str, Any],
    X_test: pd.DataFrame,
    y_test: pd.Series,
    output_root: str | Path = "outputs",
) -> tuple[pd.DataFrame, dict[str, Path]]:
    if X_test.empty or y_test.empty:
        raise RuntimeError("Cannot evaluate models on an empty test set.")

    output_root = Path(output_root)
    predictions_dir = output_root / "predictions"
    figures_dir = output_root / "figures"
    models_dir = output_root / "models"
    for directory in (predictions_dir, figures_dir, models_dir):
        directory.mkdir(parents=True, exist_ok=True)

    metrics_rows: list[dict[str, float | str]] = []
    predictions = pd.DataFrame({"row_index": y_test.index, "y_true": y_test.to_numpy()})
    artefacts: dict[str, Path] = {}

    for model_name, model in models.items():
        y_pred = model.predict(X_test)
        predictions[f"y_pred_{model_name}"] = y_pred

        metrics_rows.append(
            {
                "model": model_name,
                "accuracy": accuracy_score(y_test, y_pred),
                "precision": precision_score(y_test, y_pred, zero_division=0),
                "recall": recall_score(y_test, y_pred, zero_division=0),
                "f1": f1_score(y_test, y_pred, zero_division=0),
            }
        )

        confusion_path = figures_dir / f"fig_confusion_matrix_{model_name}_v1.png"
        _save_confusion_matrix(y_test, y_pred, model_name, confusion_path)
        artefacts[f"confusion_matrix_{model_name}"] = confusion_path

        model_stem = MODEL_FILE_STEMS.get(model_name, model_name)
        model_path = models_dir / f"model_{model_stem}_v1.pkl"
        joblib.dump(model, model_path)
        artefacts[f"model_{model_name}"] = model_path

    metrics = pd.DataFrame(metrics_rows)
    metrics_path = predictions_dir / "model_metrics_v1.csv"
    predictions_path = predictions_dir / "predictions_test_v1.csv"
    comparison_path = figures_dir / "fig_model_comparison_v1.png"

    metrics.to_csv(metrics_path, index=False)
    predictions.to_csv(predictions_path, index=False)
    _save_model_comparison(metrics, comparison_path)

    artefacts["metrics"] = metrics_path
    artefacts["predictions"] = predictions_path
    artefacts["model_comparison"] = comparison_path

    return metrics, artefacts


def _save_confusion_matrix(
    y_true: pd.Series,
    y_pred: pd.Series,
    model_name: str,
    output_path: Path,
) -> None:
    matrix = confusion_matrix(y_true, y_pred, labels=[0, 1])
    display = ConfusionMatrixDisplay(
        confusion_matrix=matrix,
        display_labels=["dry", "wet"],
    )
    fig, ax = plt.subplots(figsize=(5, 4))
    display.plot(ax=ax, values_format="d")
    ax.set_title(f"Confusion matrix: {model_name}")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def _save_model_comparison(metrics: pd.DataFrame, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 4))
    metrics.set_index("model")[["accuracy", "precision", "recall", "f1"]].plot(
        kind="bar",
        ax=ax,
    )
    ax.set_ylim(0, 1)
    ax.set_ylabel("Score")
    ax.set_title("Model comparison")
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
