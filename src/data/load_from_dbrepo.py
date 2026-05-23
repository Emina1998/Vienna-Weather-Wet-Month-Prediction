from __future__ import annotations

import math
import os
import warnings
from typing import Any, Callable

import pandas as pd
from dotenv import load_dotenv

DEFAULT_PAGE_SIZE = 100_000
FEATURE_VIEW_NAME = "weather_measurement_v2_features"
DATABASE_EMPTY_MESSAGE = (
    "DBRepo returned zero rows. T2.5 data loading must be completed before "
    "training can run."
)

TABLE_ENV_VARS = {
    "weather_measurement_v2": "DBREPO_TABLE_WEATHER_MEASUREMENT_ID",
    "time_dimension": "DBREPO_TABLE_TIME_DIMENSION_ID",
    "station": "DBREPO_TABLE_STATION_ID",
}

REQUIRED_ENV_VARS = (
    "DBREPO_ENDPOINT",
    "DBREPO_USERNAME",
    "DBREPO_PASSWORD",
    "DBREPO_DATABASE_ID",
)

MINIMUM_FEATURE_COLUMNS = {
    "precp_sum_mm",
    "ref_year",
    "ref_month",
    "latitude_deg",
    "longitude_deg",
    "altitude_m",
}


def load_weather_data_from_dbrepo() -> pd.DataFrame:
    config = _load_config()
    client = _create_client(
        endpoint=config["DBREPO_ENDPOINT"],
        username=config["DBREPO_USERNAME"],
        password=config["DBREPO_PASSWORD"],
    )

    database_id = config["DBREPO_DATABASE_ID"]

    view_df = _try_load_feature_view(client, database_id)
    if view_df is not None:
        return view_df

    table_frames = _load_base_tables(client, database_id)
    joined = _join_base_tables(
        weather=table_frames["weather_measurement_v2"],
        time_dimension=table_frames["time_dimension"],
        station=table_frames["station"],
    )
    _raise_if_empty(joined, "joined weather feature table")
    return joined


def load_data() -> pd.DataFrame:
    return load_weather_data_from_dbrepo()


def _load_config() -> dict[str, str]:
    load_dotenv()
    missing = [name for name in REQUIRED_ENV_VARS if not os.getenv(name)]
    if missing:
        raise RuntimeError(
            "Missing DBRepo environment variable(s): "
            f"{', '.join(missing)}. Configure them in .env before running the "
            "experiment."
        )

    return {name: os.environ[name] for name in REQUIRED_ENV_VARS}


def _create_client(endpoint: str, username: str, password: str) -> Any:
    try:
        from dbrepo.RestClient import RestClient
    except ImportError as exc:
        raise RuntimeError(
            "The dbrepo package is required. Install dependencies from "
            "requirements.txt before running the experiment."
        ) from exc

    try:
        return RestClient(endpoint=endpoint, username=username, password=password)
    except Exception as exc:
        raise RuntimeError(
            "Could not create DBRepo RestClient. Check DBREPO_ENDPOINT, "
            "DBREPO_USERNAME, and DBREPO_PASSWORD."
        ) from exc


def _try_load_feature_view(client: Any, database_id: str) -> pd.DataFrame | None:
    try:
        views = client.get_views(database_id)
    except Exception as exc:
        warnings.warn(
            "Could not list DBRepo views; falling back to base tables. "
            f"Original error: {exc}",
            RuntimeWarning,
            stacklevel=2,
        )
        return None

    view = _find_resource_by_name(views, FEATURE_VIEW_NAME)
    if view is None:
        warnings.warn(
            f"DBRepo view '{FEATURE_VIEW_NAME}' was not found; falling back to "
            "base tables.",
            RuntimeWarning,
            stacklevel=2,
        )
        return None

    view_id = _resource_id(view)
    try:
        count = client.get_view_data_count(database_id, view_id)
    except Exception as exc:
        warnings.warn(
            f"Could not count rows in DBRepo view '{FEATURE_VIEW_NAME}'; "
            f"falling back to base tables. Original error: {exc}",
            RuntimeWarning,
            stacklevel=2,
        )
        return None

    if count == 0:
        warnings.warn(
            f"DBRepo view '{FEATURE_VIEW_NAME}' returned zero rows; falling "
            "back to base tables.",
            RuntimeWarning,
            stacklevel=2,
        )
        return None

    df = _fetch_paginated_dataframe(
        count=count,
        fetch_page=lambda page, size: client.get_view_data(
            database_id, view_id, page=page, size=size
        ),
        label=f"view '{FEATURE_VIEW_NAME}'",
    )
    df = _normalise_column_names(df)

    missing_columns = sorted(MINIMUM_FEATURE_COLUMNS - set(df.columns))
    if missing_columns:
        warnings.warn(
            f"DBRepo view '{FEATURE_VIEW_NAME}' is missing ML feature columns "
            f"{missing_columns}; falling back to base tables.",
            RuntimeWarning,
            stacklevel=2,
        )
        return None

    _raise_if_empty(df, f"DBRepo view '{FEATURE_VIEW_NAME}'")
    return df


def _load_base_tables(client: Any, database_id: str) -> dict[str, pd.DataFrame]:
    table_ids = _resolve_table_ids(client, database_id)
    frames: dict[str, pd.DataFrame] = {}
    for table_name, table_id in table_ids.items():
        try:
            count = client.get_table_data_count(database_id, table_id)
        except Exception as exc:
            raise RuntimeError(
                f"Could not count rows in DBRepo table '{table_name}'. Check "
                "credentials, network access, and DBRepo table IDs."
            ) from exc

        if count == 0:
            raise RuntimeError(DATABASE_EMPTY_MESSAGE)

        frames[table_name] = _fetch_paginated_dataframe(
            count=count,
            fetch_page=lambda page, size, tid=table_id: client.get_table_data(
                database_id, tid, page=page, size=size
            ),
            label=f"table '{table_name}'",
        )
        frames[table_name] = _normalise_column_names(frames[table_name])
        _raise_if_empty(frames[table_name], f"DBRepo table '{table_name}'")

    return frames


def _resolve_table_ids(client: Any, database_id: str) -> dict[str, str]:
    ids_from_env = {
        table_name: os.getenv(env_var)
        for table_name, env_var in TABLE_ENV_VARS.items()
        if os.getenv(env_var)
    }
    if len(ids_from_env) == len(TABLE_ENV_VARS):
        return {
            table_name: str(table_id) for table_name, table_id in ids_from_env.items()
        }

    try:
        tables = client.get_tables(database_id)
    except Exception as exc:
        raise RuntimeError(
            "Could not list DBRepo tables. Check DBREPO_DATABASE_ID, "
            "credentials, and network access."
        ) from exc

    ids_by_name = {
        _resource_name(table): _resource_id(table)
        for table in tables
        if _resource_name(table) and _resource_id(table)
    }

    resolved: dict[str, str] = {}
    missing: list[str] = []
    for table_name, env_var in TABLE_ENV_VARS.items():
        resolved_id = os.getenv(env_var) or ids_by_name.get(table_name)
        if resolved_id:
            resolved[table_name] = resolved_id
        else:
            missing.append(table_name)

    if missing:
        available = ", ".join(sorted(ids_by_name)) or "none"
        raise RuntimeError(
            "Missing required DBRepo table(s): "
            f"{', '.join(missing)}. Available tables: {available}. "
            "Set the DBREPO_TABLE_*_ID variables in .env or create the tables "
            "before running the experiment."
        )

    return resolved


def _join_base_tables(
    weather: pd.DataFrame, time_dimension: pd.DataFrame, station: pd.DataFrame
) -> pd.DataFrame:
    _require_columns(weather, {"time_id", "station_num"}, "weather_measurement")
    _require_columns(
        time_dimension, {"time_id", "ref_year", "ref_month"}, "time_dimension"
    )
    _require_columns(
        station,
        {"station_num", "latitude_deg", "longitude_deg", "altitude_m"},
        "station",
    )

    weather = weather.copy()
    time_dimension = time_dimension.copy()
    station = station.copy()

    for frame, column in (
        (weather, "time_id"),
        (time_dimension, "time_id"),
        (weather, "station_num"),
        (station, "station_num"),
    ):
        frame[column] = frame[column].astype(str)

    try:
        joined = weather.merge(
            time_dimension,
            on="time_id",
            how="left",
            validate="many_to_one",
        ).merge(
            station,
            on="station_num",
            how="left",
            validate="many_to_one",
        )
    except Exception as exc:
        raise RuntimeError(
            "Could not join DBRepo base tables. Check that time_id and "
            "station_num keys are present and unique in the dimension tables."
        ) from exc

    missing_join_data = [
        column
        for column in (
            "ref_year",
            "ref_month",
            "latitude_deg",
            "longitude_deg",
            "altitude_m",
        )
        if joined[column].isna().any()
    ]
    if missing_join_data:
        raise RuntimeError(
            "Base DBRepo tables could be loaded, but the join produced missing "
            f"values in {missing_join_data}. Check station_num and time_id keys."
        )

    return joined


def _fetch_paginated_dataframe(
    count: int,
    fetch_page: Callable[[int, int], Any],
    label: str,
    page_size: int = DEFAULT_PAGE_SIZE,
) -> pd.DataFrame:
    if count <= 0:
        raise RuntimeError(DATABASE_EMPTY_MESSAGE)

    page_count = max(1, math.ceil(count / page_size))
    frames: list[pd.DataFrame] = []
    for page in range(page_count):
        try:
            response = fetch_page(page, page_size)
        except Exception as exc:
            raise RuntimeError(
                f"Could not fetch data from DBRepo {label}. Check "
                "credentials, network access, and DBRepo object IDs."
            ) from exc

        frame = _coerce_to_dataframe(response, label)
        frames.append(frame)

    data = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    _raise_if_empty(data, f"DBRepo {label}")
    return data


def _coerce_to_dataframe(response: Any, label: str) -> pd.DataFrame:
    if isinstance(response, pd.DataFrame):
        return response.copy()

    if isinstance(response, list):
        return pd.DataFrame(response)

    if isinstance(response, dict):
        for key in ("data", "rows", "items", "results"):
            if key in response:
                return _coerce_to_dataframe(response[key], label)
        raise RuntimeError(
            f"Unexpected response shape from DBRepo {label}: dictionary does "
            "not contain a recognised row collection key."
        )

    raise RuntimeError(
        f"Unexpected response type from DBRepo {label}: "
        f"{type(response).__name__}. Expected a pandas DataFrame or row list."
    )


def _normalise_column_names(df: pd.DataFrame) -> pd.DataFrame:
    renamed = {
        column: str(column).strip().lower()
        for column in df.columns
        if str(column).strip().lower() != column
    }
    return df.rename(columns=renamed)


def _find_resource_by_name(resources: list[Any], name: str) -> Any | None:
    return next(
        (resource for resource in resources if _resource_name(resource) == name), None
    )


def _resource_name(resource: Any) -> str | None:
    if isinstance(resource, dict):
        return resource.get("name")
    return getattr(resource, "name", None)


def _resource_id(resource: Any) -> str:
    if isinstance(resource, dict):
        resource_id = resource.get("id")
    else:
        resource_id = getattr(resource, "id", None)
    if not resource_id:
        raise RuntimeError(f"DBRepo resource has no id: {resource!r}")
    return str(resource_id)


def _require_columns(df: pd.DataFrame, columns: set[str], table_name: str) -> None:
    missing = sorted(columns - set(df.columns))
    if missing:
        raise RuntimeError(
            f"DBRepo table '{table_name}' is missing required column(s): "
            f"{', '.join(missing)}."
        )


def _raise_if_empty(df: pd.DataFrame, label: str) -> None:
    if df.empty:
        raise RuntimeError(f"{label} is empty. {DATABASE_EMPTY_MESSAGE}")
