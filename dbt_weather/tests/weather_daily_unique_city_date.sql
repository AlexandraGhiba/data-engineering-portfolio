SELECT
    city,
    weather_date,
    COUNT(*) AS row_count
FROM {{ ref('weather_daily') }}
GROUP BY
    city,
    weather_date
HAVING COUNT(*) > 1