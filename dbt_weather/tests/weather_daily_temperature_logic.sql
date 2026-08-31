SELECT *
FROM {{ ref('weather_daily') }}
WHERE min_temperature > avg_temperature
   OR avg_temperature > max_temperature