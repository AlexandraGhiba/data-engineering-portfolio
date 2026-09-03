WITH source AS (

    SELECT
        timestamp,
        price_eur_mwh

    FROM {{ source('entsoe', 'raw_entsoe_prices') }}

),

renamed AS (

    SELECT
        timestamp,
        price_eur_mwh,
        CAST(timestamp AS DATE) AS price_date

    FROM source

)

SELECT *
FROM renamed