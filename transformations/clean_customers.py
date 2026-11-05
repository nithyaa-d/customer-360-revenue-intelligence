"""Clean and enrich raw CRM customer data."""

import pandas as pd


def clean_customers(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize customer data and create analytical features.
    """

    cleaned = dataframe.copy()

    required_columns = [
        "customer_id",
        "email",
        "signup_date",
        "last_activity_date",
        "country",
        "industry",
        "annual_revenue",
        "acquisition_channel",
        "account_status",
    ]

    missing_columns = [
        column for column in required_columns
        if column not in cleaned.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Standardize text fields
    text_columns = [
        "customer_id",
        "customer_name",
        "email",
        "country",
        "industry",
        "acquisition_channel",
        "account_status",
    ]

    for column in text_columns:
        if column in cleaned.columns:
            cleaned[column] = cleaned[column].astype("string").str.strip()

    # Standardize email addresses
    cleaned["email"] = cleaned["email"].str.lower()

    # Standardize dates
    cleaned["signup_date"] = pd.to_datetime(
        cleaned["signup_date"], errors="coerce"
    )

    cleaned["last_activity_date"] = pd.to_datetime(
        cleaned["last_activity_date"], errors="coerce"
    )

    # Convert revenue to numeric
    cleaned["annual_revenue"] = pd.to_numeric(
        cleaned["annual_revenue"], errors="coerce"
    )

    if cleaned[required_columns].isnull().any().any():
        raise ValueError(
            "Invalid or missing values found in required columns."
        )

    if (cleaned["annual_revenue"] < 0).any():
        raise ValueError("Annual revenue cannot be negative.")

    if (cleaned["last_activity_date"] < cleaned["signup_date"]).any():
        raise ValueError(
            "Last activity date cannot be before signup date."
        )

    # Create analytical features
    reference_date = pd.Timestamp("2026-11-05")

    cleaned["customer_tenure_days"] = (
        reference_date - cleaned["signup_date"]
    ).dt.days

    cleaned["days_since_last_activity"] = (
        reference_date - cleaned["last_activity_date"]
    ).dt.days

    cleaned["is_churned"] = (
        cleaned["account_status"].str.lower() == "churned"
    )

    # Reset index
    cleaned = cleaned.reset_index(drop=True)

    return cleaned
