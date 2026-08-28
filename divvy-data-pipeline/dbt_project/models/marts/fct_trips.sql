{{ config(
    materialized='incremental',
    unique_key='ride_id'
) }}

with trips as (

    select *
    from {{ ref('int_trips_enriched') }}

    where is_invalid_duration = false

    {% if is_incremental() %}
      and started_at >= (
          select coalesce(max(started_at), timestamp '1900-01-01')
          from {{ this }}
      )
    {% endif %}

),

stations as (

    select *
    from {{ ref('dim_stations') }}

),

final as (

    select
        t.ride_id,
        t.rideable_type,
        t.started_at,
        t.ended_at,

        t.start_station_id,
        t.start_station_name,

        start_station.station_version_key
            as start_station_version_key,

        t.end_station_id,
        t.end_station_name,

        end_station.station_version_key
            as end_station_version_key,

        t.member_casual,

        t.trip_duration_seconds,
        t.trip_duration_minutes,
        t.is_implausibly_long_trip,

        t.source_year,
        t.source_month

    from trips t

    left join stations start_station
        on t.start_station_id = start_station.station_id
        and t.started_at >= start_station.valid_from
        and (
            t.started_at < start_station.valid_to
            or start_station.valid_to is null
        )

    left join stations end_station
        on t.end_station_id = end_station.station_id
        and t.ended_at >= end_station.valid_from
        and (
            t.ended_at < end_station.valid_to
            or end_station.valid_to is null
        )

)

select *
from final