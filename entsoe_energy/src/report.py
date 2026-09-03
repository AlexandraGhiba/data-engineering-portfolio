import duckdb
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "data" / "energy.duckdb"


def show_daily_prices():
    """Display the daily ENTSO-E price report."""

    con = duckdb.connect(str(DATABASE_PATH))

    query = """
        SELECT
            price_date,
            ROUND(average_price_eur_mwh, 2) AS avg_price_eur_mwh,
            ROUND(minimum_price_eur_mwh, 2) AS min_price_eur_mwh,
            ROUND(maximum_price_eur_mwh, 2) AS max_price_eur_mwh,
            price_observations
        FROM daily_prices
        ORDER BY price_date
    """

    rows = con.execute(query).fetchall()

    print()
    print("=" * 95)
    print("ENTSO-E DAILY ENERGY PRICE REPORT")
    print("=" * 95)
    print()

    print(
        f"{'DATE':<15}"
        f"{'AVG PRICE':>15}"
        f"{'MIN PRICE':>15}"
        f"{'MAX PRICE':>15}"
        f"{'OBSERVATIONS':>15}"
    )

    print("-" * 95)

    for row in rows:
        price_date, avg_price, min_price, max_price, observations = row

        print(
            f"{str(price_date):<15}"
            f"{avg_price:>15.2f}"
            f"{min_price:>15.2f}"
            f"{max_price:>15.2f}"
            f"{observations:>15}"
        )

    print()
    print("=" * 95)

    con.close()


if __name__ == "__main__":
    show_daily_prices()