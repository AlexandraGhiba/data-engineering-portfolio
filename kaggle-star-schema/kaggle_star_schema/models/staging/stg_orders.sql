-- Staging model for raw_orders:
-- standardizes source column names to snake_case
-- while preserving the original row-level grain and values.

select
    "Row ID" as row_id,
    "Order ID" as order_id,
    "Order Date" as order_date,
    "Ship Date" as ship_date,
    "Ship Mode" as ship_mode,
    "Customer ID" as customer_id,
    "Customer Name" as customer_name,
    "Segment" as segment,
    "Country" as country,
    "City" as city,
    "State" as state,
    "Postal Code" as postal_code,
    "Region" as region,
    "Retail Sales People" as retail_sales_person,
    "Product ID" as product_id,
    "Category" as category,
    "Sub-Category" as sub_category,
    "Product Name" as product_name,
    "Returned" as returned,
    "Sales" as sales,
    "Quantity" as quantity,
    "Discount" as discount,
    "Profit" as profit
from {{ source('raw', 'orders') }}
