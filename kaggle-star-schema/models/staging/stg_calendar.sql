-- Staging model for raw_calendar:
-- standardizes source column names to snake_case
-- while preserving the original calendar attributes.

select
    "Date" as date_day,
    "Year" as year,
    "Quarter" as quarter,
    "Quarter (Q)" as quarter_label,
    "Quarter & Year" as quarter_year,
    "Month" as month,
    "Month Name" as month_name,
    "Month & Year" as month_year,
    "Week of Year" as week_of_year,
    "Week of Year (W)" as week_label,
    "Day of Week" as day_of_week,
    "Day Name" as day_name
from {{ source('raw', 'calendar') }}
