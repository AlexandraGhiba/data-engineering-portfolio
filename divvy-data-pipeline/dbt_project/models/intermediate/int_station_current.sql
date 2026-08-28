with monthly_stations as (

    select *
    from {{ ref('int_station_observations') }}

)

select
    station_id,
    station_name,
    latitude,
    longitude,
    source_year,
    source_month,

    make_date(
        source_year,
        source_month,
        1
    ) as effective_from,

    observed_at

from monthly_stations

where source_year = {{ var('processing_year') }}
  and source_month = {{ var('processing_month') }}