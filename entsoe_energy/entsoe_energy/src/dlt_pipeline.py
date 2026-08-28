from pathlib import Path
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
import sys

import dlt

from entsoe_api import (
    get_day_ahead_prices,
    get_local_day_period,
    parse_day_ahead_prices,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "data" / "energy.duckdb"

ROMANIA_TZ = ZoneInfo("Europe/Bucharest")


pipeline = dlt.pipeline(
    pipeline_name="entsoe_energy",
    destination=dlt.destinations.duckdb(
        str(DATABASE_PATH)
    ),
    dataset_name="raw",
)


def get_target_date():
    """
    Return the Romanian calendar date to process.

    If a date is provided as a command-line argument,
    use it.

    Otherwise, process yesterday.
    """

    if len(sys.argv) > 1:

        try:
            return datetime.strptime(
                sys.argv[1],
                "%Y-%m-%d",
            ).date()

        except ValueError as error:

            raise ValueError(
                "Date must be provided in YYYY-MM-DD format."
            ) from error

    return date.today() - timedelta(days=1)


@dlt.resource(
    name="raw_entsoe_prices",
    write_disposition="merge",
    primary_key="timestamp",
)
def entsoe_prices():

    target_date = get_target_date()

    period_start, period_end = get_local_day_period(
        target_date
    )

    print()
    print(
        f"Fetching ENTSO-E prices for "
        f"Romanian date {target_date}"
    )

    print(
        f"UTC period: "
        f"{period_start} -> {period_end}"
    )

    xml_response = get_day_ahead_prices(
        period_start,
        period_end,
    )

    prices = parse_day_ahead_prices(
        xml_response,
        target_date,
    )

    print(
        f"Parsed {len(prices)} price observations "
        f"for {target_date}"
    )

    if len(prices) != 96:
        print(
            f"WARNING: expected 96 observations, "
            f"but received {len(prices)}."
        )

    yield prices


load_info = pipeline.run(entsoe_prices())

print(load_info)