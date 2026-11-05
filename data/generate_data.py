"""Generate synthetic CRM customer data for the portfolio project."""

from pathlib import Path

import numpy as np
import pandas as pd


def generate_customers(number_of_customers: int = 1000) -> pd.DataFrame:
    """Generate a reproducible synthetic customer dataset."""

    rng = np.random.default_rng(seed=42)

    countries = ["Sweden", "Germany", "United Kingdom", "India", "France",
                 "Netherlands", "Norway", "Denmark", "United States"]

    industries = ["Technology", "Retail", "Manufacturing", "Finance",
                  "Healthcare", "Telecommunications", "Education"]

    acquisition_channels = [
        "Organic Search", "Paid Search", "Referral",
        "Social Media", "Email Campaign", "Events"
    ]

    account_statuses = ["Active", "At Risk", "Churned"]

    signup_dates = pd.to_datetime(
        rng.choice(
            pd.date_range("2022-01-01", "2026-10-31"),
            size=number_of_customers
        )
    )

    activity_offsets = rng.integers(0, 365, size=number_of_customers)

    last_activity_dates = signup_dates + pd.to_timedelta(
        activity_offsets, unit="D"
    )

    last_activity_dates = pd.to_datetime(
        [
            min(date, pd.Timestamp("2026-11-05"))
            for date in last_activity_dates
        ]
    )

    customer_ids = [
        f"CUST-{number:05d}"
        for number in range(1, number_of_customers + 1)
    ]

    customer_names = [
        f"Customer {number}"
        for number in range(1, number_of_customers + 1)
    ]

    dataframe = pd.DataFrame({
        "customer_id": customer_ids,
        "customer_name": customer_names,
        "email": [
            f"customer{number}@example.com"
            for number in range(1, number_of_customers + 1)
        ],
        "signup_date": signup_dates,
        "last_activity_date": last_activity_dates,
        "country": rng.choice(countries, size=number_of_customers),
        "industry": rng.choice(industries, size=number_of_customers),
        "annual_revenue": rng.integers(
            5000, 500001, size=number_of_customers
        ),
        "acquisition_channel": rng.choice(
            acquisition_channels, size=number_of_customers
        ),
        "account_status": rng.choice(
            account_statuses,
            size=number_of_customers,
            p=[0.70, 0.20, 0.10]
        ),
    })

    return dataframe


def main() -> None:
    """Generate and save the synthetic customer dataset."""

    project_root = Path(__file__).resolve().parent.parent
    output_path = project_root / "data" / "raw" / "customers.csv"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    dataframe = generate_customers()

    dataframe.to_csv(output_path, index=False)

    print(f"Generated {len(dataframe)} synthetic customers.")
    print(f"Saved dataset to: {output_path}")


if __name__ == "__main__":
    main()
