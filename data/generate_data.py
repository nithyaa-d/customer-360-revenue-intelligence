
"""Generate synthetic CRM customer data for the portfolio project."""

from pathlib import Path

import numpy as np
import pandas as pd


def generate_customers(number_of_customers: int = 1000) -> pd.DataFrame:
    """Generate a reproducible synthetic customer dataset."""

    rng = np.random.default_rng(seed=42)

    countries = [
        "Sweden", "Germany", "United Kingdom", "India", "France",
        "Netherlands", "Norway", "Denmark", "United States"
    ]

    industries = [
        "Technology", "Retail", "Manufacturing", "Finance",
        "Healthcare", "Telecommunications", "Education"
    ]

    acquisition_channels = [
        "Organic Search", "Paid Search", "Referral",
        "Social Media", "Email Campaign", "Events"
    ]

    # Generate customer signup dates
    signup_dates = pd.to_datetime(
        rng.choice(
            pd.date_range("2022-01-01", "2026-10-31"),
            size=number_of_customers
        )
    )

    # Generate customer activity dates
    activity_offsets = rng.integers(
        0, 365, size=number_of_customers
    )

    last_activity_dates = signup_dates + pd.to_timedelta(
        activity_offsets, unit="D"
    )

    reference_date = pd.Timestamp("2026-11-05")

    last_activity_dates = pd.to_datetime(
        [
            min(date, reference_date)
            for date in last_activity_dates
        ]
    )

    # Generate realistic synthetic churn behaviour
    days_since_activity = (
        reference_date - last_activity_dates
    ).days

    # Longer inactivity increases churn probability
    churn_probability = 1 / (
        1 + np.exp(-(days_since_activity - 150) / 45)
    )

    is_churned = (
        rng.random(number_of_customers) < churn_probability
    )

    is_at_risk = (
        (~is_churned)
        & (days_since_activity >= 90)
    )

    account_status = np.where(
        is_churned,
        "Churned",
        np.where(is_at_risk, "At Risk", "Active")
    )

    # Generate customer identifiers
    customer_ids = [
        f"CUST-{number:05d}"
        for number in range(1, number_of_customers + 1)
    ]

    customer_names = [
        f"Customer {number}"
        for number in range(1, number_of_customers + 1)
    ]

    # Build the customer dataset
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
        "account_status": account_status,
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

    print("\nCustomer status distribution:")
    print(dataframe["account_status"].value_counts())


if __name__ == "__main__":
    main()
