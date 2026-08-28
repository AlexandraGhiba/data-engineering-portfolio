SELECT *
FROM {{ source('crypto', 'raw_crypto_trades') }}
WHERE price <= 0
   OR price IS NULL
