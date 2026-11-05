
"""Verify the dbt Gold tables in the local DuckDB database."""

from pathlib import Path

import duckdb


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATABASE_FILE = PROJECT_ROOT / "customer_360_analytics.duckdb"

def main():
    """Check that both Gold tables exist and contain records."""

    connection = duckdb.connect(str(DATABASE_FILE), read_only=True)

    for table in ["dim_customer_360", "fct_customer_revenue"]:
        result = connection.execute(
            f"SELECT COUNT(*) FROM main.{table}"
        ).fetchone()

        print(f"{table}: {result[0]} rows")

    connection.close()


if __name__ == "__main__":
    main()
