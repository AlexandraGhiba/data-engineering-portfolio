SELECT *
FROM {{ source('crypto', 'raw_crypto_trades') }}
WHERE quantity <= 0
   OR quantity IS NULL
