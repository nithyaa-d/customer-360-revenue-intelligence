"""Tests for revenue and customer KPI analytics."""

import pandas as pd
import pytest

from analytics.revenue_analysis import (
    build_customer_kpis,
    build_revenue_analysis,
)


@pytest.fixture
def sample_customers():
    return pd.DataFrame({
        "customer_id": ["CUST-001", "CUST-002", "CUST-003"],
        "country": ["Sweden", "Sweden", "Germany"],
        "industry": ["Technology", "Finance", "Technology"],
        "acquisition_channel": [
            "Organic Search", "Referral", "Organic Search"
        ],
        "annual_revenue": [100000, 200000, 300000],
        "account_status": ["Active", "At Risk", "Churned"],
        "is_churned": [False, False, True],
    })


def test_customer_kpis_calculates_customer_counts(sample_customers):
    kpis = build_customer_kpis(sample_customers)

    assert kpis["total_customers"] == 3
    assert kpis["active_customers"] == 1
    assert kpis["at_risk_customers"] == 1
    assert kpis["churned_customers"] == 1


def test_customer_kpis_calculates_churn_rate(sample_customers):
    kpis = build_customer_kpis(sample_customers)

    assert kpis["churn_rate_pct"] == 33.33


def test_customer_kpis_calculates_revenue(sample_customers):
    kpis = build_customer_kpis(sample_customers)

    assert kpis["total_annual_customer_revenue"] == 600000
    assert kpis["average_annual_revenue_per_customer"] == 200000


def test_revenue_analysis_by_country(sample_customers):
    result = build_revenue_analysis(sample_customers, "country")

    sweden = result[result["country"] == "Sweden"].iloc[0]

    assert sweden["customer_count"] == 2
    assert sweden["total_annual_revenue"] == 300000


def test_revenue_analysis_by_industry(sample_customers):
    result = build_revenue_analysis(sample_customers, "industry")

    technology = result[result["industry"] == "Technology"].iloc[0]

    assert technology["customer_count"] == 2
    assert technology["total_annual_revenue"] == 400000


def test_revenue_analysis_rejects_invalid_dimension(sample_customers):
    with pytest.raises(ValueError, match="Unsupported dimension"):
        build_revenue_analysis(sample_customers, "customer_name")


def test_revenue_analysis_rejects_empty_data():
    empty_dataframe = pd.DataFrame()

    with pytest.raises(ValueError, match="Missing required columns"):
        build_customer_kpis(empty_dataframe)


def test_revenue_analysis_detects_duplicate_customers(sample_customers):
    duplicate_data = pd.concat(
        [sample_customers, sample_customers.iloc[[0]]],
        ignore_index=True,
    )

    with pytest.raises(ValueError, match="Duplicate customer IDs"):
        build_customer_kpis(duplicate_data)
