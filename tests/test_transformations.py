"""Tests for Silver-layer customer transformations."""

import pandas as pd
import pytest

from transformations.clean_customers import clean_customers


@pytest.fixture
def sample_customers():
    """Create sample customer records for testing."""

    return pd.DataFrame({
        "customer_id": [" CUST-001 ", "CUST-002"],
        "customer_name": [" Customer One ", "Customer Two"],
        "email": ["USER1@EXAMPLE.COM", "USER2@EXAMPLE.COM"],
        "signup_date": ["2025-01-01", "2025-06-01"],
        "last_activity_date": ["2026-01-01", "2026-10-01"],
        "country": [" Sweden ", "Germany"],
        "industry": [" Technology ", "Finance"],
        "annual_revenue": [100000, 200000],
        "acquisition_channel": [" Organic Search ", "Referral"],
        "account_status": ["Active", "Churned"],
    })


def test_clean_customers_standardizes_text(sample_customers):
    cleaned = clean_customers(sample_customers)

    assert cleaned.loc[0, "customer_id"] == "CUST-001"
    assert cleaned.loc[0, "email"] == "user1@example.com"
    assert cleaned.loc[0, "country"] == "Sweden"


def test_clean_customers_creates_analytical_features(sample_customers):
    cleaned = clean_customers(sample_customers)

    assert "customer_tenure_days" in cleaned.columns
    assert "days_since_last_activity" in cleaned.columns
    assert "is_churned" in cleaned.columns

    assert cleaned.loc[0, "is_churned"] == False
    assert cleaned.loc[1, "is_churned"] == True


def test_clean_customers_converts_data_types(sample_customers):
    cleaned = clean_customers(sample_customers)

    assert pd.api.types.is_datetime64_any_dtype(cleaned["signup_date"])
    assert pd.api.types.is_numeric_dtype(cleaned["annual_revenue"])


def test_clean_customers_rejects_negative_revenue(sample_customers):
    sample_customers.loc[0, "annual_revenue"] = -100

    with pytest.raises(ValueError, match="cannot be negative"):
        clean_customers(sample_customers)


def test_clean_customers_rejects_activity_before_signup(sample_customers):
    sample_customers.loc[0, "last_activity_date"] = "2024-01-01"

    with pytest.raises(ValueError, match="before signup date"):
        clean_customers(sample_customers)


def test_clean_customers_rejects_missing_columns(sample_customers):
    sample_customers = sample_customers.drop(columns=["email"])

    with pytest.raises(ValueError, match="Missing required columns"):
        clean_customers(sample_customers)
