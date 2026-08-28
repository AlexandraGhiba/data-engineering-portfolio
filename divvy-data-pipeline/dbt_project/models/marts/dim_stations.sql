with station_versions as (

    select
        dbt_scd_id as station_version_key,

        station_id,
        station_name,
        latitude,
        longitude,

        effective_from as valid_from

    from {{ ref('stations_snapshot') }}

),

with_valid_to as (

    select
        *,

        lead(valid_from) over (
            partition by station_id
            order by valid_from
        ) as valid_to

    from station_versions

)

select
    station_version_key,

    station_id,
    station_name,
    latitude,
    longitude,

    valid_from,
    valid_to

from with_valid_to