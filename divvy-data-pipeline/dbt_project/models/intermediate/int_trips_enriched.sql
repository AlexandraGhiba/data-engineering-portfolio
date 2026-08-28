with trips as (

    select *
    from {{ ref('stg_trips') }}

),

enriched as (

    select
        *,

        datediff(
            'second',
            started_at,
            ended_at
        ) as trip_duration_seconds,

        datediff(
            'second',
            started_at,
            ended_at
        ) / 60.0 as trip_duration_minutes,

        case
            when ended_at <= started_at then true
            else false
        end as is_invalid_duration,

        case
            when datediff('second', started_at, ended_at) > 86400 then true
            else false
        end as is_implausibly_long_trip

    from trips

)

select *
from enriched