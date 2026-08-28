with source as (

    select *
    from {{ source('raw', 'trips') }}

),

renamed as (

    select
        ride_id,
        lower(trim(rideable_type)) as rideable_type,

        cast(started_at as timestamp) as started_at,
        cast(ended_at as timestamp) as ended_at,

        nullif(trim(start_station_name), '') as start_station_name,
        nullif(trim(start_station_id), '') as start_station_id,

        nullif(trim(end_station_name), '') as end_station_name,
        nullif(trim(end_station_id), '') as end_station_id,

        start_lat,
        start_lng,
        end_lat,
        end_lng,

        lower(trim(member_casual)) as member_casual,

        cast(year as integer) as source_year,
        cast(month as integer) as source_month

    from source

)

select *
from renamed