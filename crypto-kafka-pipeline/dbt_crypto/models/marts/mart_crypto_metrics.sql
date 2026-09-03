{{ config(materialized='table') }}

SELECT
    date_trunc('minute', timestamp) AS minute_bucket,
    symbol,
    COUNT(*) AS trade_count,
    AVG(price) AS avg_price,
    MAX(price) AS max_price,
    MIN(price) AS min_price,
    SUM(quantity) AS volume,
    SUM(price * quantity) AS traded_value

FROM {{ ref('stg_crypto_trades') }}

GROUP BY 1, 2

ORDER BY minute_bucket ASC