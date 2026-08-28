with trips as (

    select
        date_trunc('month', started_at) as trip_month,
        member_casual,
        trip_duration_minutes

    from {{ ref('fct_trips') }}

),

aggregated as (

    select
        trip_month,
        member_casual,

        count(*) as trip_count,

        avg(trip_duration_minutes)
            as avg_trip_duration_minutes

    from trips

    group by
        trip_month,
        member_casual

),

monthly_totals as (

    select
        trip_month,
        sum(trip_count) as total_monthly_trips

    from aggregated

    group by trip_month

)

select
    a.trip_month,
    a.member_casual,

    a.trip_count,
    a.avg_trip_duration_minutes,

    a.trip_count * 1.0
        / nullif(t.total_monthly_trips, 0)
        as rider_type_share

from aggregated a

join monthly_totals t
    on a.trip_month = t.trip_month