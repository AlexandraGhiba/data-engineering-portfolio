{% snapshot stations_snapshot %}

{{
    config(
        target_schema='main',
        unique_key='station_id',
        strategy='check',
        check_cols=[
            'station_name',
            'latitude',
            'longitude'
        ]
    )
}}

select
    station_id,
    station_name,
    latitude,
    longitude,
    source_year,
    source_month,
    effective_from,
    observed_at

from {{ ref('int_station_current') }}

{% endsnapshot %}