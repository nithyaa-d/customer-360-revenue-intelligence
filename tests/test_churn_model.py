
"""Tests for customer churn prediction and scoring."""

import pandas as pd
import pytest

from machine_learning.train_churn_model import (
    build_model,
    prepare_features,
)
from machine_learning.score_customers import (
    assign_risk_category,
    score_customers,
)


@pytest.fixture
def sample_customers():
    """Create a small synthetic customer dataset for testing."""

    return pd.DataFrame({
        "customer_id": [
            "CUST-001",
            "CUST-002",
            "CUST-003",
            "CUST-004",
            "CUST-005",
            "CUST-006",
        ],
        "customer_name": [
            "Customer 1",
            "Customer 2",
            "Customer 3",
            "Customer 4",
            "Customer 5",
            "Customer 6",
        ],
        "email": [
            f"customer{i}@example.com"
            for i in range(1, 7)
        ],
        "signup_date": pd.date_range(
            "2024-01-01", periods=6
        ),
        "last_activity_date": pd.date_range(
            "2026-01-01", periods=6
        ),
        "country": [
            "Sweden", "India", "Germany",
            "Sweden", "India", "Germany"
        ],
        "industry": [
            "Technology", "Retail", "Finance",
            "Technology", "Retail", "Finance"
        ],
        "acquisition_channel": [
            "Organic Search", "Referral", "Email Campaign",
            "Organic Search", "Referral", "Email Campaign"
        ],
        "annual_revenue": [
            10000, 50000, 150000,
            20000, 75000, 250000
        ],
        "customer_tenure_days": [
            500, 400, 300, 200, 100, 50
        ],
        "days_since_last_activity": [
            10, 30, 60, 120, 180, 250
        ],
        "account_status": [
            "Active", "Active", "Active",
            "At Risk", "Churned", "Churned"
        ],
        "is_churned": [
            False, False, False, False, True, True
        ],
    })


def test_prepare_features_excludes_target_and_identifiers(
    sample_customers,
):
    X, y = prepare_features(sample_customers)

    assert "is_churned" not in X.columns
    assert "account_status" not in X.columns
    assert "customer_id" not in X.columns
    assert len(X) == len(y)
    assert y.sum() == 2


def test_prepare_features_keeps_business_features(sample_customers):
    X, _ = prepare_features(sample_customers)

    assert "annual_revenue" in X.columns
    assert "country" in X.columns
    assert "industry" in X.columns


def test_build_model_trains_and_predicts(sample_customers):
    X, y = prepare_features(sample_customers)

    model = build_model(X)

    model.fit(X, y)

    predictions = model.predict(X)
    probabilities = model.predict_proba(X)

    assert len(predictions) == len(X)
    assert probabilities.shape == (len(X), 2)
    assert set(predictions).issubset({0, 1})


@pytest.mark.parametrize(
    "probability, expected",
    [
        (0.85, "High"),
        (0.70, "High"),
        (0.55, "Medium"),
        (0.40, "Medium"),
        (0.20, "Low"),
        (0.10, "Low"),
    ],
)
def test_assign_risk_category(probability, expected):
    assert assign_risk_category(probability) == expected


def test_score_customers_returns_expected_columns():
    results = score_customers()

    expected_columns = [
        "customer_id",
        "country",
        "industry",
        "annual_revenue",
        "days_since_last_activity",
        "churn_probability",
        "predicted_churn",
        "risk_category",
    ]

    assert list(results.columns) == expected_columns
    assert len(results) == 1000
    assert results["churn_probability"].between(0, 1).all()
    assert set(results["risk_category"].unique()).issubset(
        {"High", "Medium", "Low"}
    )


def test_score_customers_sorted_by_risk():
    results = score_customers()

    probabilities = results["churn_probability"].tolist()

    assert probabilities == sorted(probabilities, reverse=True)
