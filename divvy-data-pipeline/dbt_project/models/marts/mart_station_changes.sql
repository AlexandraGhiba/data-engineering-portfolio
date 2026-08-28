with station_history as (

    select
        station_version_key,
        station_id,
        station_name,
        latitude,
        longitude,
        valid_from,
        valid_to,

        lag(station_version_key) over (
            partition by station_id
            order by valid_from
        ) as previous_station_version_key,

        lag(station_name) over (
            partition by station_id
            order by valid_from
        ) as previous_station_name,

        lag(latitude) over (
            partition by station_id
            order by valid_from
        ) as previous_latitude,

        lag(longitude) over (
            partition by station_id
            order by valid_from
        ) as previous_longitude

    from {{ ref('dim_stations') }}

),

movement_calculation as (

    select
        *,

        case
            when previous_latitude is null
              or previous_longitude is null
            then null
            else
                6371000 * 2 * asin(
                    sqrt(
                        power(
                            sin(radians(latitude - previous_latitude) / 2),
                            2
                        )
                        +
                        cos(radians(previous_latitude))
                        * cos(radians(latitude))
                        * power(
                            sin(radians(longitude - previous_longitude) / 2),
                            2
                        )
                    )
                )
        end as movement_meters

    from station_history

),

classified_changes as (

    select
        *,

        station_name <> previous_station_name
            as was_renamed,

        movement_meters >= 100
            as was_relocated,

        (
            station_name <> previous_station_name
            and movement_meters >= 1000
        ) as is_reissued_id_candidate

    from movement_calculation

),

version_trip_counts as (

    select
        start_station_version_key as station_version_key,
        count(*) as start_trip_count

    from {{ ref('fct_trips') }}

    where start_station_version_key is not null

    group by 1

)

select
    c.station_id,

    c.previous_station_name,
    c.station_name,

    c.previous_station_version_key,
    c.station_version_key,

    c.valid_from,
    c.valid_to,

    c.movement_meters,

    c.was_renamed,
    c.was_relocated,
    c.is_reissued_id_candidate,

    coalesce(previous_trips.start_trip_count, 0)
        as previous_version_trip_count,

    coalesce(current_trips.start_trip_count, 0)
        as current_version_trip_count,

    coalesce(previous_trips.start_trip_count, 0)
        + coalesce(current_trips.start_trip_count, 0)
        as naive_combined_trip_count,

    coalesce(previous_trips.start_trip_count, 0)
        as trips_wrongly_merged_into_current_identity

from classified_changes c

left join version_trip_counts previous_trips
    on c.previous_station_version_key =
       previous_trips.station_version_key

left join version_trip_counts current_trips
    on c.station_version_key =
       current_trips.station_version_key

where
    c.previous_station_version_key is not null
    and (
        c.was_renamed
        or c.was_relocated
    )

order by
    trips_wrongly_merged_into_current_identity desc,
    movement_meters desc