-- Dimension table containing one row per unique product variant.
-- Grain: one row per unique combination of
-- product_id, product_name, category, and sub_category.

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
            order by
                product_id,
                product_name,
                category,
                sub_category
        ) as product_key,
        product_id,
        product_name,
        category,
        sub_category
    from products

)

select *
from final