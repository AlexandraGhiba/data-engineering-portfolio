from dagster import Definitions, ScheduleDefinition

from .assets import (
    crypto_dbt_models,
    crypto_dbt_tests,
    crypto_anomaly_check,
    crypto_metrics_to_sheets,
)


crypto_pipeline_schedule = ScheduleDefinition(
    name="crypto_pipeline_10min",
    cron_schedule="*/10 * * * *",
    target=[
        crypto_dbt_models,
        crypto_dbt_tests,
        crypto_anomaly_check,
        crypto_metrics_to_sheets,
    ],
)


defs = Definitions(
    assets=[
        crypto_dbt_models,
        crypto_dbt_tests,
        crypto_anomaly_check,
        crypto_metrics_to_sheets,
    ],
    schedules=[
        crypto_pipeline_schedule,
    ],
)