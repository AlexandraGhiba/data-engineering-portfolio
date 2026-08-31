-- Selects the relevant columns from the raw weather source

SELECT
    city,
    timestamp,
    temperature,
    humidity,
    wind_speed,
    precipitation,
    cloud_cover
FROM {{ source('weather_data', 'weather_data') }}