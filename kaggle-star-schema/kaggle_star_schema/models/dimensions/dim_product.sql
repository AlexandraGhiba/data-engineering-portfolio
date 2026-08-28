-- Dimension table containing one row per unique product.
-- The grain is one row per product_id.

with products as (

    select distinct
        product_id,
        product_name,
        category,
        sub_category
    from {{ ref('stg_orders') }}

),

final as (

    select
        row_number() over (
            order by product_id
        ) as product_key,
        product_id,
        product_name,
        category,
        sub_category
    from products

)

select *
from final