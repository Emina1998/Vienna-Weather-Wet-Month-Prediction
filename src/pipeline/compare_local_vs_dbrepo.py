from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from src.data.load_from_dbrepo import load_weather_data_from_dbrepo

PRESSURE_REQUIRED_COLS = ["p_mean_hpa", "p_max_hpa", "p_min_hpa"]

NULLABLE_NUMERIC_COLS = [
    "rel_hum_max_pct",
    "rel_hum_min_pct",
    "wind_vel_max_ms",
    "num_wind_vel60",
    "sun_h",
]

WEATHER_COLUMNS = [
    "measurement_id",
    "station_num",
    "time_id",
    "t_mean_c",
    "t_max_c",
    "t_min_c",
    "mean_t_max_c",
    "mean_t_min_c",
    "p_mean_hpa",
    "p_max_hpa",
    "p_min_hpa",
    "precp_sum_mm",
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
]

TIME_COLUMNS = ["time_id", "ref_year", "ref_month"]

STATION_COLUMNS = [
    "station_num",
    "nuts_code",
    "district_code",
    "sub_district_code",
    "station_name",
    "latitude_deg",
    "longitude_deg",
    "altitude_m",
]

COMPARE_COLUMNS = [
    "measurement_id",
    "station_num",
    "time_id",
    "ref_year",
    "ref_month",
    "nuts_code",
    "district_code",
    "sub_district_code",
    "station_name",
    "latitude_deg",
    "longitude_deg",
    "altitude_m",
    "t_mean_c",
    "t_max_c",
    "t_min_c",
    "mean_t_max_c",
    "mean_t_min_c",
    "p_mean_hpa",
    "p_max_hpa",
    "p_min_hpa",
    "precp_sum_mm",
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
    "wet_month_label",
]


def parse_number(series: pd.Series) -> pd.Series:
    return pd.to_numeric(
        series.astype(str)
        .str.strip()
        .str.replace(",", ".", regex=False)
        .replace({"": pd.NA, "nan": pd.NA, "None": pd.NA}),
        errors="coerce",
    )


def _parse_ref_month(raw: pd.Series) -> pd.Series:
    raw_str = raw.astype(str).str.strip()

    is_yyyymm = raw_str.str.fullmatch(r"\d{6}")
    if is_yyyymm.all():
        months = raw_str.str[-2:].astype(int)

        if not months.between(1, 12).all():
            bad = raw_str[~months.between(1, 12)].head(5).tolist()
            raise ValueError(f"Invalid YYYYMM REF_DATE month values: {bad}")

        return months

    numeric = pd.to_numeric(raw_str, errors="coerce")
    if numeric.notna().all() and numeric.between(1, 12).all():
        return numeric.astype(int)

    parsed = pd.to_datetime(raw_str, errors="coerce", dayfirst=True)

    if parsed.isna().any():
        bad = raw_str[parsed.isna()].head(5).tolist()
        raise ValueError(f"Could not parse REF_DATE values, examples: {bad}")

    return parsed.dt.month.astype(int)


def load_local_cleaned_dataset(raw_csv_path: Path) -> pd.DataFrame:
    if not raw_csv_path.exists():
        raise FileNotFoundError(f"Raw CSV not found: {raw_csv_path}")

    raw = pd.read_csv(raw_csv_path, sep=";")
    raw.columns = [c.strip().upper() for c in raw.columns]

    required_raw_cols = {
        "STAT_NUM",
        "NUTS",
        "DISTRICT_CODE",
        "SUB_DISTRICT_CODE",
        "REF_YEAR",
        "REF_DATE",
        "T",
        "T_MAX",
        "T_MIN",
        "MEAN_T_MAX",
        "MEAN_T_MIN",
        "P",
        "P_MAX",
        "P_MIN",
        "PRECP_SUM",
        "NUM_PRECP_01",
        "REL_HUM",
        "REL_HUM_MAX",
        "REL_HUM_MIN",
        "WIND_VEL",
        "WIND_VEL_MAX",
        "NUM_WIND_VEL60",
        "SUN_H",
        "NUM_CLEAR",
        "NUM_CLOUD",
        "NUM_FROST",
        "NUM_ICE",
        "NUM_SUMMER",
        "NUM_HEAT",
    }

    missing = sorted(required_raw_cols - set(raw.columns))
    if missing:
        raise ValueError(f"Raw CSV is missing required columns: {missing}")

    ref_year = pd.to_numeric(raw["REF_YEAR"], errors="coerce").astype(int)
    ref_month = _parse_ref_month(raw["REF_DATE"])
    time_id = ref_year * 100 + ref_month

    weather = pd.DataFrame(
        {
            "measurement_id": np.arange(1, len(raw) + 1, dtype="int64"),
            "station_num": parse_number(raw["STAT_NUM"]),
            "time_id": time_id,
            "t_mean_c": parse_number(raw["T"]),
            "t_max_c": parse_number(raw["T_MAX"]),
            "t_min_c": parse_number(raw["T_MIN"]),
            "mean_t_max_c": parse_number(raw["MEAN_T_MAX"]),
            "mean_t_min_c": parse_number(raw["MEAN_T_MIN"]),
            "p_mean_hpa": parse_number(raw["P"]),
            "p_max_hpa": parse_number(raw["P_MAX"]),
            "p_min_hpa": parse_number(raw["P_MIN"]),
            "precp_sum_mm": parse_number(raw["PRECP_SUM"]),
            "num_precp_01": parse_number(raw["NUM_PRECP_01"]),
            "rel_hum_pct": parse_number(raw["REL_HUM"]),
            "rel_hum_max_pct": parse_number(raw["REL_HUM_MAX"]),
            "rel_hum_min_pct": parse_number(raw["REL_HUM_MIN"]),
            "wind_vel_ms": parse_number(raw["WIND_VEL"]),
            "wind_vel_max_ms": parse_number(raw["WIND_VEL_MAX"]),
            "num_wind_vel60": parse_number(raw["NUM_WIND_VEL60"]),
            "sun_h": parse_number(raw["SUN_H"]),
            "num_clear": parse_number(raw["NUM_CLEAR"]),
            "num_cloud": parse_number(raw["NUM_CLOUD"]),
            "num_frost": parse_number(raw["NUM_FROST"]),
            "num_ice": parse_number(raw["NUM_ICE"]),
            "num_summer": parse_number(raw["NUM_SUMMER"]),
            "num_heat": parse_number(raw["NUM_HEAT"]),
        }
    )

    weather = weather.dropna(subset=PRESSURE_REQUIRED_COLS).copy()

    weather["measurement_id"] = pd.to_numeric(
        weather["measurement_id"], errors="coerce"
    ).astype("int64")

    int_cols = [
        "measurement_id",
        "station_num",
        "time_id",
        "num_precp_01",
        "num_clear",
        "num_cloud",
        "num_frost",
        "num_ice",
        "num_summer",
        "num_heat",
    ]

    for col in int_cols:
        weather[col] = pd.to_numeric(weather[col], errors="coerce").astype("int64")

    for col in NULLABLE_NUMERIC_COLS:
        weather[col] = pd.to_numeric(weather[col], errors="coerce")

    time_dimension = (
        weather[["time_id"]]
        .drop_duplicates()
        .assign(
            ref_year=lambda df: df["time_id"] // 100,
            ref_month=lambda df: df["time_id"] % 100,
        )[TIME_COLUMNS]
        .copy()
    )

    station = (
        raw[["STAT_NUM", "NUTS", "DISTRICT_CODE", "SUB_DISTRICT_CODE"]]
        .drop_duplicates()
        .rename(
            columns={
                "STAT_NUM": "station_num",
                "NUTS": "nuts_code",
                "DISTRICT_CODE": "district_code",
                "SUB_DISTRICT_CODE": "sub_district_code",
            }
        )
        .copy()
    )

    station["station_num"] = parse_number(station["station_num"]).astype("int64")
    station["district_code"] = parse_number(station["district_code"]).astype("int64")
    station["sub_district_code"] = parse_number(station["sub_district_code"]).astype(
        "int64"
    )

    station["station_name"] = "Wien - Hohe Warte"
    station["latitude_deg"] = 48.248611
    station["longitude_deg"] = 16.356944
    station["altitude_m"] = 202.0

    station = station[STATION_COLUMNS]

    joined = weather.merge(
        time_dimension, on="time_id", how="left", validate="many_to_one"
    ).merge(station, on="station_num", how="left", validate="many_to_one")

    joined["wet_month_label"] = (joined["precp_sum_mm"] >= 60).astype(int)

    return normalise_for_comparison(joined)


def normalise_for_comparison(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]

    numeric_cols = [
        col for col in COMPARE_COLUMNS if col not in {"nuts_code", "station_name"}
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "wet_month_label" not in df.columns:
        df["wet_month_label"] = (
            pd.to_numeric(df["precp_sum_mm"], errors="coerce") >= 60
        ).astype(int)

    missing = sorted(set(COMPARE_COLUMNS) - set(df.columns))
    if missing:
        raise ValueError(f"Dataframe is missing comparison columns: {missing}")

    df = df[COMPARE_COLUMNS]
    df = df.sort_values(["time_id", "station_num"]).reset_index(drop=True)

    return df


def compare_dataframes(local_df: pd.DataFrame, dbrepo_df: pd.DataFrame) -> None:
    print("\nComparison summary")
    print("==================")
    print(f"Local rows : {len(local_df)}")
    print(f"DBRepo rows: {len(dbrepo_df)}")
    print(f"Same shape : {local_df.shape == dbrepo_df.shape}")
    print(f"Same columns: {list(local_df.columns) == list(dbrepo_df.columns)}")

    if local_df.shape != dbrepo_df.shape:
        raise AssertionError(
            f"Shape mismatch: local {local_df.shape}, DBRepo {dbrepo_df.shape}"
        )

    non_numeric_cols = ["nuts_code", "station_name"]
    numeric_cols = [col for col in COMPARE_COLUMNS if col not in non_numeric_cols]

    numeric_equal = np.allclose(
        local_df[numeric_cols].to_numpy(dtype=float),
        dbrepo_df[numeric_cols].to_numpy(dtype=float),
        equal_nan=True,
    )

    text_equal = True
    for col in non_numeric_cols:
        same_col = (
            local_df[col]
            .fillna("")
            .astype(str)
            .equals(dbrepo_df[col].fillna("").astype(str))
        )
        print(f"Text column equal ({col}): {same_col}")
        text_equal = text_equal and same_col

    target_equal = local_df["wet_month_label"].equals(dbrepo_df["wet_month_label"])

    print(f"Numeric values equivalent: {numeric_equal}")
    print(f"Target labels identical  : {target_equal}")

    if not numeric_equal:
        diff = local_df[numeric_cols].compare(dbrepo_df[numeric_cols])
        print("\nNumeric differences:")
        print(diff.head(20))
        raise AssertionError("Numeric values differ between local and DBRepo data.")

    if not text_equal:
        raise AssertionError("Text values differ between local and DBRepo data.")

    if not target_equal:
        raise AssertionError("Target labels differ between local and DBRepo data.")

    print("\nVerification passed.")
    print(
        "The DBRepo API reimplementation produces the same cleaned dataset as "
        "the original local-file preprocessing pipeline."
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--raw-csv",
        type=Path,
        default=Path("data/raw/weather_raw_hohewarte_v1.csv"),
        help="Path to the original raw weather CSV.",
    )
    args = parser.parse_args()

    print("Loading local cleaned dataset...")
    local_df = load_local_cleaned_dataset(args.raw_csv)

    print("\nLoading DBRepo dataset...")
    dbrepo_df = load_weather_data_from_dbrepo()
    dbrepo_df = normalise_for_comparison(dbrepo_df)

    compare_dataframes(local_df, dbrepo_df)


if __name__ == "__main__":
    main()
