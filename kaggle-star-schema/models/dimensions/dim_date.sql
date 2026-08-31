-- Dimension table containing one row per calendar date.
-- Provides descriptive date attributes used by the fact table
-- for time-based analysis.

select
    cast(strftime(date_day, '%Y%m%d') as integer) as date_key,
    date_day,
    year,
    quarter,
    quarter_label,
    quarter_year,
    month,
    month_name,
    month_year,
    week_of_year,
    week_label,
    day_of_week,
    day_name
from {{ ref('stg_calendar') }}