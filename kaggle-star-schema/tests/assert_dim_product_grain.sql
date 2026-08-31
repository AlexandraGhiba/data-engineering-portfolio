select
    product_id,
    product_name,
    count(*) as row_count
from {{ ref('dim_product') }}
group by
    product_id,
    product_name
having count(*) > 1
