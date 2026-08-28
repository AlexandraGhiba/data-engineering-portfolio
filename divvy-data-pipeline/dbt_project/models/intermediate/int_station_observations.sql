with start_stations as (

    select
        start_station_id as station_id,
        start_station_name as station_name,
        start_lat as latitude,
        start_lng as longitude,

        source_year,
        source_month,

        started_at as observed_at

    from {{ ref('stg_trips') }}

    where start_station_id is not null

),

end_stations as (

    select
        end_station_id as station_id,
        end_station_name as station_name,
        end_lat as latitude,
        end_lng as longitude,

        source_year,
        source_month,

        ended_at as observed_at

    from {{ ref('stg_trips') }}

    where end_station_id is not null

),

combined as (

    select * from start_stations

    union all

    select * from end_stations

),

ranked as (

    select
        *,

        row_number() over (
            partition by
                station_id,
                source_year,
                source_month
            order by observed_at desc
        ) as row_num

    from combined

)

select
    station_id,
    station_name,
    latitude,
    longitude,

    source_year,
    source_month,

    observed_at

from ranked

where row_num = 1