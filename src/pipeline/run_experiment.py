from __future__ import annotations

from pathlib import Path

from src.data.load_from_dbrepo import load_weather_data_from_dbrepo
from src.features.build_features import build_ml_dataset
from src.models.evaluate_model import evaluate_models
from src.models.train_model import train_models


def main() -> None:
    data = load_weather_data_from_dbrepo()
    X, y = build_ml_dataset(data)
    models, split_data = train_models(X, y)
    metrics, artefacts = evaluate_models(
        models=models,
        X_test=split_data["X_test"],
        y_test=split_data["y_test"],
    )

    print("DBRepo wet-month experiment complete.")
    print(f"Rows loaded: {len(data)}")
    print(f"Features used: {X.shape[1]}")
    print(f"Split strategy: {split_data['split_strategy']}")
    print("\nTest metrics:")
    print(metrics.to_string(index=False, float_format=lambda value: f"{value:.3f}"))
    print("\nOutput artefacts:")
    for key, path in sorted(artefacts.items()):
        print(f"- {key}: {_display_path(path)}")


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    main()
