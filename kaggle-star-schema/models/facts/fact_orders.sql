{{ config(materialized='table') }}

SELECT
    o.order_id,
    o.row_id,

    d.date_key,
    c.customer_key,
    l.location_key,
    p.product_key,

    o.sales,
    o.quantity,
    o.discount,
    o.profit

FROM {{ ref('stg_orders') }} o

LEFT JOIN {{ ref('dim_date') }} d
    ON o.order_date = d.date_day

LEFT JOIN {{ ref('dim_customer') }} c
    ON o.customer_id = c.customer_id

LEFT JOIN {{ ref('dim_location') }} l
    ON o.city = l.city
    AND o.state = l.state
    AND o.postal_code = l.postal_code
    AND o.region = l.region

LEFT JOIN {{ ref('dim_product') }} p
    ON o.product_id = p.product_id
    AND o.product_name = p.product_name
    AND o.category = p.category
    AND o.sub_category = p.sub_category