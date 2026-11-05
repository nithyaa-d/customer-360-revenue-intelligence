"""Tests for the Gold-layer Customer 360 dataset."""

import pandas as pd
import pytest

from transformations.build_customer_360 import build_customer_360


@pytest.fixture
def sample_customers():
    """Create sample Silver customer records."""

    return pd.DataFrame({
        "customer_id": ["CUST-001", "CUST-002", "CUST-003"],
        "annual_revenue": [30000, 120000, 350000],
        "customer_tenure_days": [30, 180, 500],
        "days_since_last_activity": [10, 60, 120],
        "account_status": ["Active", "Active", "Churned"],
        "is_churned": [False, False, True],
    })


def test_customer_360_creates_all_segments(sample_customers):
    gold = build_customer_360(sample_customers)

    expected_columns = [
        "revenue_segment",
        "engagement_segment",
        "customer_lifecycle_stage",
        "customer_value_segment",
    ]

    for column in expected_columns:
        assert column in gold.columns


def test_customer_360_assigns_revenue_segments(sample_customers):
    gold = build_customer_360(sample_customers)

    assert gold["revenue_segment"].tolist() == [
        "SMB", "Mid-Market", "Enterprise"
    ]


def test_customer_360_assigns_engagement_segments(sample_customers):
    gold = build_customer_360(sample_customers)

    assert gold["engagement_segment"].tolist() == [
        "Highly Engaged",
        "Moderately Engaged",
        "Low Engagement",
    ]


def test_customer_360_assigns_lifecycle_stages(sample_customers):
    gold = build_customer_360(sample_customers)

    assert gold["customer_lifecycle_stage"].tolist() == [
        "New", "Established", "Mature"
    ]


def test_customer_360_rejects_missing_columns(sample_customers):
    sample_customers = sample_customers.drop(
        columns=["annual_revenue"]
    )

    with pytest.raises(ValueError, match="Missing required columns"):
        build_customer_360(sample_customers)


def test_customer_360_rejects_empty_data():
    empty_dataframe = pd.DataFrame(columns=[
        "customer_id",
        "annual_revenue",
        "customer_tenure_days",
        "days_since_last_activity",
        "account_status",
        "is_churned",
    ])

    with pytest.raises(ValueError, match="empty"):
        build_customer_360(empty_dataframe)
