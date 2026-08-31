-- Dimension table containing one row per unique geographic location.
-- The grain is one unique combination of country, city, state,
-- postal code, and region.

with locations as (

    select distinct
        country,
        city,
        state,
        postal_code,
        region
    from {{ ref('stg_orders') }}

),

final as (

    select
        row_number() over (
            order by country, state, city, postal_code
        ) as location_key,
        country,
        city,
        state,
        postal_code,
        region
    from locations

)

select *
from final