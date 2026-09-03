SELECT
    timestamp,
    price_eur_mwh

FROM {{ ref('stg_entsoe_prices') }}

WHERE price_eur_mwh < -1000
   OR price_eur_mwh > 10000