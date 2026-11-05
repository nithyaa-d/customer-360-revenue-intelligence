
import pandas as pd
import pytest

from ai_assistant.query_engine import answer_question, execute_query


def test_total_customer_question():

    result = answer_question(
        "How many customers do we have?"
    )

    assert isinstance(result, dict)
    assert "answer" in result
    assert "1,000" in result["answer"] or "1000" in result["answer"]


def test_country_revenue_question():

    result = answer_question(
        "Which country has the highest revenue?"
    )

    assert isinstance(result, dict)
    assert "Sweden" in result["answer"]


def test_high_churn_risk_question():

    result = answer_question(
        "How many customers are high churn risk?"
    )

    assert isinstance(result, dict)
    assert "431" in result["answer"]


def test_industry_revenue_question():

    result = answer_question(
        "Which industry has the highest revenue?"
    )

    assert isinstance(result, dict)
    assert isinstance(result["answer"], str)
    assert len(result["answer"]) > 0


def test_acquisition_channel_question():

    result = answer_question(
        "Show acquisition channel performance"
    )

    assert isinstance(result, dict)
    assert isinstance(result["answer"], str)
    assert len(result["answer"]) > 0


def test_top_customers_question():

    result = answer_question(
        "Show the top customers by revenue"
    )

    assert isinstance(result, dict)
    assert isinstance(result["answer"], str)

    data = result.get("data")

    assert isinstance(data, pd.DataFrame)
    assert not data.empty


def test_execute_read_only_query():

    result = execute_query(
        "SELECT 1 AS test_value"
    )

    assert isinstance(result, pd.DataFrame)
    assert result.iloc[0]["test_value"] == 1


def test_database_rejects_write_operations():

    with pytest.raises(Exception):

        execute_query(
            "CREATE TABLE assistant_security_test "
            "(id INTEGER)"
        )
