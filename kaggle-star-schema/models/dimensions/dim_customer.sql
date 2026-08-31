-- Dimension table containing one row per customer.
-- Customer attributes are limited to fields that remain consistent
-- for a given customer across the source transactions.
-- Geographic attributes are modeled separately in dim_location.

with customers as (

    select distinct
        customer_id,
        customer_name,
        segment
    from {{ ref('stg_orders') }}

),

final as (

    select
        row_number() over (order by customer_id) as customer_key,
        customer_id,
        customer_name,
        segment
    from customers

)

select *
from final