SELECT
    timestamp,
    COUNT(*) AS record_count

FROM {{ ref('stg_entsoe_prices') }}

GROUP BY timestamp

HAVING COUNT(*) > 1