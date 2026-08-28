SELECT
    CAST(timestamp AS TIMESTAMP) AS timestamp,
    UPPER(symbol) AS symbol,
    CAST(price AS DOUBLE) AS price,
    CAST(quantity AS DOUBLE) AS quantity,
    CAST(trade_id AS BIGINT) AS trade_id

FROM {{ source('crypto', 'raw_crypto_trades') }}

WHERE price > 0
  AND quantity > 0