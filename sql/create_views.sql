-- T2.4 DBRepo View Definitions
-- Vienna Weather Wet-Month Prediction Experiment
--
-- These SQL view definitions describe the query-ready data structures
-- used by the machine learning pipeline.

-- ============================================================
-- View 1: Full ML feature table
-- ============================================================

CREATE OR REPLACE VIEW weather_features_all AS
SELECT
    wm.measurement_id,
    wm.station_num,
    wm.time_id,

    td.ref_year,
    td.ref_month,

    s.station_name,
    s.nuts_code,
    s.district_code,
    s.sub_district_code,
    s.latitude_deg,
    s.longitude_deg,
    s.altitude_m,

    wm.t_mean_c,
    wm.t_max_c,
    wm.t_min_c,
    wm.mean_t_max_c,
    wm.mean_t_min_c,

    wm.p_mean_hpa,
    wm.p_max_hpa,
    wm.p_min_hpa,

    wm.precp_sum_mm,
    wm.num_precp_01,

    wm.rel_hum_pct,
    wm.rel_hum_max_pct,
    wm.rel_hum_min_pct,

    wm.wind_vel_ms,
    wm.wind_vel_max_ms,
    wm.num_wind_vel60,

    wm.sun_h,
    wm.num_clear,
    wm.num_cloud,

    wm.num_frost,
    wm.num_ice,
    wm.num_summer,
    wm.num_heat,

    CASE
        WHEN wm.precp_sum_mm >= 60 THEN 1
        ELSE 0
    END AS wet_month_label

FROM weather_measurement_v2 wm
JOIN time_dimension td
    ON wm.time_id = td.time_id
JOIN station s
    ON wm.station_num = s.station_num;


-- ============================================================
-- View 2: Training split
-- ============================================================

CREATE OR REPLACE VIEW weather_train AS
SELECT *
FROM weather_features_all
WHERE ref_year <= 2016;


-- ============================================================
-- View 3: Validation split
-- ============================================================

CREATE OR REPLACE VIEW weather_validation AS
SELECT *
FROM weather_features_all
WHERE ref_year BETWEEN 2017 AND 2019;


-- ============================================================
-- View 4: Test split
-- ============================================================

CREATE OR REPLACE VIEW weather_test AS
SELECT *
FROM weather_features_all
WHERE ref_year >= 2020;


-- ============================================================
-- View 5: Monthly precipitation summary
-- ============================================================

CREATE OR REPLACE VIEW monthly_precipitation_summary AS
SELECT
    ref_month,
    AVG(precp_sum_mm) AS avg_precipitation_mm,
    MIN(precp_sum_mm) AS min_precipitation_mm,
    MAX(precp_sum_mm) AS max_precipitation_mm,
    COUNT(*) AS observation_count
FROM weather_features_all
GROUP BY ref_month;