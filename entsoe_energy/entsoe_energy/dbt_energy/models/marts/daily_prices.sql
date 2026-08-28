WITH source AS (

    SELECT
        price_date,
        price_eur_mwh

    FROM {{ ref('stg_entsoe_prices') }}

),

daily AS (

    SELECT
        price_date,
        AVG(price_eur_mwh) AS average_price_eur_mwh,
        MIN(price_eur_mwh) AS minimum_price_eur_mwh,
        MAX(price_eur_mwh) AS maximum_price_eur_mwh,
        COUNT(*) AS price_observations

    FROM source

    GROUP BY price_date

)

SELECT *
FROM daily
ORDER BY price_date