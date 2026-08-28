{{ config(materialized='table') }}
SELECT
    city,
    DATE_TRUNC('day', timestamp) AS weather_date,
    MIN(temperature) AS min_temperature,
    MAX(temperature) AS max_temperature,
    AVG(temperature) AS avg_temperature,
    AVG(humidity) AS avg_humidity,
    AVG(wind_speed) AS avg_wind_speed,
    SUM(precipitation) AS total_precipitation
FROM {{ ref('stg_weather') }}
GROUP BY
    city,
    DATE_TRUNC('day', timestamp)