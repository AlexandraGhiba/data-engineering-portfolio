import os
import requests
import xml.etree.ElementTree as ET
import logging
import time

from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

BASE_URL = "https://web-api.tp.entsoe.eu/api"
ROMANIA_DOMAIN = "10YRO-TEL------P"

ENTSOE_API_TOKEN = os.getenv("ENTSOE_API_TOKEN")

ROMANIA_TZ = ZoneInfo("Europe/Bucharest")


def get_api_token():
    """Get the ENTSO-E API token from environment variables."""

    if not ENTSOE_API_TOKEN:
        raise RuntimeError(
            "ENTSOE_API_TOKEN is not configured. "
            "Add it to the .env file."
        )

    return ENTSOE_API_TOKEN


def get_day_ahead_prices(period_start, period_end):
    """Retrieve day-ahead electricity prices from ENTSO-E."""

    token = get_api_token()

    params = {
        "securityToken": token,
        "documentType": "A44",
        "in_Domain": ROMANIA_DOMAIN,
        "out_Domain": ROMANIA_DOMAIN,
        "contract_MarketAgreement.type": "A01",
        "periodStart": period_start,
        "periodEnd": period_end,
    }

    max_attempts = 5
    retryable_statuses = {
        429,
        500,
        502,
        503,
        504,
    }

    for attempt in range(1, max_attempts + 1):
        request_start = time.perf_counter()

        try:
            response = requests.get(
                BASE_URL,
                params=params,
                timeout=30,
            )

        except requests.RequestException:
            duration = time.perf_counter() - request_start

            logger.warning(
                "entsoe_request_failed "
                "attempt=%s/%s "
                "duration_seconds=%.2f",
                attempt,
                max_attempts,
                duration,
            )

            if attempt == max_attempts:
                raise RuntimeError(
                    "ENTSO-E API request failed after "
                    f"{max_attempts} attempts."
                ) from None

            wait_seconds = 2 ** attempt

            logger.info(
                "entsoe_retry "
                "wait_seconds=%s",
                wait_seconds,
            )

            time.sleep(wait_seconds)
            continue

        duration = time.perf_counter() - request_start

        logger.info(
            "entsoe_response "
            "attempt=%s/%s "
            "status=%s "
            "duration_seconds=%.2f",
            attempt,
            max_attempts,
            response.status_code,
            duration,
        )

        if response.status_code == 200:
            logger.info(
                "entsoe_request_success "
                "response_chars=%s",
                len(response.text),
            )

            return response.text

        if response.status_code in retryable_statuses:
            if attempt < max_attempts:
                retry_after = response.headers.get(
                    "Retry-After"
                )

                if retry_after and retry_after.isdigit():
                    wait_seconds = int(retry_after)
                else:
                    wait_seconds = 2 ** attempt

                logger.warning(
                    "entsoe_temporary_error "
                    "status=%s "
                    "retry_in_seconds=%s",
                    response.status_code,
                    wait_seconds,
                )

                time.sleep(wait_seconds)
                continue

            raise RuntimeError(
                "ENTSO-E API temporarily unavailable "
                f"after {max_attempts} attempts "
                f"(HTTP {response.status_code})."
            )

        raise RuntimeError(
            "ENTSO-E API request failed "
            f"with HTTP {response.status_code}."
        )

    raise RuntimeError(
        "ENTSO-E API request failed unexpectedly."
    )


def get_local_day_period(target_date):
    """
    Return the ENTSO-E UTC period covering one full Romanian
    calendar day.

    Romania is UTC+2 in winter and UTC+3 in summer, so we
    calculate the UTC boundaries using the Europe/Bucharest
    timezone instead of hard-coding an offset.
    """

    local_start = datetime.combine(
        target_date,
        datetime.min.time(),
        tzinfo=ROMANIA_TZ,
    )

    local_end = local_start + timedelta(days=1)

    utc_start = local_start.astimezone(ZoneInfo("UTC"))
    utc_end = local_end.astimezone(ZoneInfo("UTC"))

    period_start = utc_start.strftime("%Y%m%d%H%M")
    period_end = utc_end.strftime("%Y%m%d%H%M")

    return period_start, period_end


def parse_day_ahead_prices(xml_text, target_date=None):
    """
    Convert the ENTSO-E XML response into price records.

    If target_date is provided, only observations belonging to
    that Romanian calendar date are returned.

    Timestamps remain timezone-aware UTC timestamps. DuckDB can
    convert them to Europe/Bucharest when displaying/querying.
    """

    root = ET.fromstring(xml_text)

    namespace = {
        "ns": (
            "urn:iec62325.351:tc57wg16:"
            "451-3:publicationdocument:7:3"
        )
    }

    prices = []

    for period in root.findall(
        ".//ns:TimeSeries/ns:Period",
        namespace,
    ):

        start_element = period.find(
            "ns:timeInterval/ns:start",
            namespace,
        )

        resolution = period.find(
            "ns:resolution",
            namespace,
        )

        if start_element is None or resolution is None:
            continue

        start_time = datetime.fromisoformat(
            start_element.text.replace("Z", "+00:00")
        )

        if resolution.text == "PT15M":
            interval_minutes = 15
        elif resolution.text == "PT60M":
            interval_minutes = 60
        else:
            raise ValueError(
                f"Unsupported resolution: {resolution.text}"
            )

        for point in period.findall(
            "ns:Point",
            namespace,
        ):

            position = point.find(
                "ns:position",
                namespace,
            )

            price = point.find(
                "ns:price.amount",
                namespace,
            )

            if position is None or price is None:
                continue

            timestamp = start_time + timedelta(
                minutes=(int(position.text) - 1) * interval_minutes
            )

            if target_date is not None:
                local_timestamp = timestamp.astimezone(
                    ROMANIA_TZ
                )

                if local_timestamp.date() != target_date:
                    continue

            prices.append(
                {
                    "timestamp": timestamp.isoformat(),
                    "price_eur_mwh": float(price.text),
                }
            )

    prices.sort(key=lambda item: item["timestamp"])

    return prices


if __name__ == "__main__":

    try:
        target_date = date(2026, 8, 18)

        period_start, period_end = get_local_day_period(
            target_date
        )

        print(
            f"Romanian date: {target_date}"
        )

        print(
            f"ENTSO-E period: "
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

        print(f"Parsed records: {len(prices)}")

        print("FIRST:")
        for price in prices[:3]:
            print(price)

        print("LAST:")
        for price in prices[-3:]:
            print(price)

    except Exception as error:
        print(f"ERROR: {error}")