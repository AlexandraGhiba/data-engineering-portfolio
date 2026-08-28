select
    ride_id,
    trip_duration_seconds
from {{ ref('fct_trips') }}
where trip_duration_seconds <= 0