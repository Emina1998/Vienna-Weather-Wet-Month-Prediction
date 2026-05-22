-- Station 
CREATE TABLE station (
    station_num       INTEGER PRIMARY KEY,  -- STAT_NUM e.g. 5901
    nuts_code         VARCHAR(10) NOT NULL, -- e.g. AT13
    district_code     INTEGER NOT NULL,     -- e.g. 91900
    sub_district_code INTEGER NOT NULL,     -- e.g. 91905
    station_name      VARCHAR(100) NOT NULL,
    latitude_deg      NUMERIC(9,6),
    longitude_deg     NUMERIC(9,6),
    altitude_m        NUMERIC(6,1)
);

-- Time dim
CREATE TABLE time_dimension (
    time_id INTEGER PRIMARY KEY,
    ref_year  SMALLINT NOT NULL CHECK (ref_year >= 1872),
    ref_month SMALLINT NOT NULL CHECK (ref_month BETWEEN 1 AND 12),
    UNIQUE (ref_year, ref_month)
);

-- Weather measurements
CREATE TABLE weather_measurement_v2 (
    measurement_id  INTEGER  PRIMARY KEY,
    station_num     INTEGER NOT NULL REFERENCES station(station_num),
    time_id         INTEGER NOT NULL REFERENCES time_dimension(time_id),
    UNIQUE (station_num, time_id),

    -- Temperature (°C)
    t_mean_c        NUMERIC(5,1),  -- T
    t_max_c         NUMERIC(5,1),  -- T_MAX
    t_min_c         NUMERIC(5,1),  -- T_MIN
    mean_t_max_c    NUMERIC(5,1),  -- MEAN_T_MAX
    mean_t_min_c    NUMERIC(5,1),  -- MEAN_T_MIN

    -- Pressure (hPa)
    p_mean_hpa      NUMERIC(7,1),  -- P
    p_max_hpa       NUMERIC(7,1),  -- P_MAX
    p_min_hpa       NUMERIC(7,1),  -- P_MIN

    -- Precipitation & humidity
    precp_sum_mm    NUMERIC(7,1),  -- PRECP_SUM
    num_precp_01    SMALLINT,      -- NUM_PRECP_01 (days >= 0.1mm)
    rel_hum_pct     NUMERIC(5,1),  -- REL_HUM
    rel_hum_max_pct NUMERIC(5,1),  -- REL_HUM_MAX
    rel_hum_min_pct NUMERIC(5,1),  -- REL_HUM_MIN

    -- Wind (m/s)
    wind_vel_ms     NUMERIC(5,1),  -- WIND_VEL
    wind_vel_max_ms NUMERIC(5,1),  -- WIND_VEL_MAX
    num_wind_vel60  SMALLINT,      -- NUM_WIND_VEL60 (days >= 60 km/h)

    -- Sunshine & cloudiness
    sun_h           NUMERIC(7,1),  -- SUN_H (hours)
    num_clear       SMALLINT,      -- NUM_CLEAR
    num_cloud       SMALLINT,      -- NUM_CLOUD

    -- Special day counts (dimensionless)
    num_frost       SMALLINT,      -- NUM_FROST (T_min < 0°C)
    num_ice         SMALLINT,      -- NUM_ICE (T_max < 0°C)
    num_summer      SMALLINT,      -- NUM_SUMMER (T_max >= 25°C)
    num_heat        SMALLINT       -- NUM_HEAT (T_max >= 30°C)
);
