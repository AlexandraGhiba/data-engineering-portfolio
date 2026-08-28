with date_bounds as (

    select
        min(cast(started_at as date)) as min_date,
        max(cast(started_at as date)) as max_date
    from {{ ref('fct_trips') }}

),

weekdays as (

    select
        cast(gs.calendar_date as date) as trip_date

    from date_bounds b

    cross join generate_series(
        b.min_date,
        b.max_date,
        interval 1 day
    ) as gs(calendar_date)

    where extract(isodow from gs.calendar_date) between 1 and 5

),

rider_types as (

    select 'member' as member_casual
    union all
    select 'casual'

),

station_weekday_spine as (

    select
        d.station_version_key,
        d.station_id,
        d.station_name,
        r.member_casual,
        w.trip_date

    from {{ ref('dim_stations') }} d

    cross join rider_types r
    cross join weekdays w

    where
        w.trip_date >= cast(d.valid_from as date)
        and (
            d.valid_to is null
            or w.trip_date < cast(d.valid_to as date)
        )

),

daily_departures as (

    select
        cast(started_at as date) as trip_date,
        start_station_version_key as station_version_key,
        member_casual,
        count(*) as departures

    from {{ ref('fct_trips') }}

    where
        start_station_version_key is not null
        and extract(isodow from started_at) between 1 and 5

    group by 1, 2, 3

),

daily_arrivals as (

    select
        cast(ended_at as date) as trip_date,
        end_station_version_key as station_version_key,
        member_casual,
        count(*) as arrivals

    from {{ ref('fct_trips') }}

    where
        end_station_version_key is not null
        and extract(isodow from ended_at) between 1 and 5

    group by 1, 2, 3

),

daily_station_balance as (

    select
        s.station_version_key,
        s.station_id,
        s.station_name,
        s.member_casual,
        s.trip_date,

        coalesce(d.departures, 0) as departures,
        coalesce(a.arrivals, 0) as arrivals,

        coalesce(d.departures, 0)
        - coalesce(a.arrivals, 0) as net_imbalance

    from station_weekday_spine s

    left join daily_departures d
        on s.station_version_key = d.station_version_key
        and s.member_casual = d.member_casual
        and s.trip_date = d.trip_date

    left join daily_arrivals a
        on s.station_version_key = a.station_version_key
        and s.member_casual = a.member_casual
        and s.trip_date = a.trip_date

)

select
    station_version_key,
    station_id,
    station_name,
    member_casual,

    avg(departures) as avg_weekday_departures,
    avg(arrivals) as avg_weekday_arrivals,
    avg(net_imbalance) as avg_weekday_net_imbalance,

    abs(avg(net_imbalance))
        as absolute_avg_weekday_imbalance

from daily_station_balance

group by
    station_version_key,
    station_id,
    station_name,
    member_casual