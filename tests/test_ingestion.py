"""Tests for the CRM data ingestion modules."""

import pandas as pd
import pytest

from ingestion.extract import extract_csv
from ingestion.validate import validate_dataframe


def test_extract_csv_success(tmp_path):
    """Verify that a valid CSV file can be extracted."""

    source_file = tmp_path / "customers.csv"

    dataframe = pd.DataFrame({
        "customer_id": ["CUST-00001", "CUST-00002"],
        "email": ["customer1@example.com", "customer2@example.com"],
    })

    dataframe.to_csv(source_file, index=False)

    result = extract_csv(source_file)

    assert len(result) == 2
    assert "customer_id" in result.columns


def test_extract_csv_file_not_found():
    """Verify that missing files raise FileNotFoundError."""

    with pytest.raises(FileNotFoundError):
        extract_csv("missing_customers.csv")


def test_extract_csv_invalid_extension(tmp_path):
    """Verify that non-CSV files are rejected."""

    source_file = tmp_path / "customers.txt"
    source_file.write_text("sample data")

    with pytest.raises(ValueError):
        extract_csv(source_file)


def test_validate_dataframe_success():
    """Verify that a valid dataset passes validation."""

    dataframe = pd.DataFrame({
        "customer_id": ["CUST-00001", "CUST-00002"],
        "email": ["customer1@example.com", "customer2@example.com"],
    })

    report = validate_dataframe(
        dataframe,
        required_columns=["customer_id", "email"],
        unique_columns=["customer_id"],
    )

    assert report["status"] == "PASSED"
    assert report["duplicate_count"] == 0


def test_validate_dataframe_detects_duplicates():
    """Verify that duplicate customer IDs are detected."""

    dataframe = pd.DataFrame({
        "customer_id": ["CUST-00001", "CUST-00001"],
        "email": ["customer1@example.com", "customer1@example.com"],
    })

    report = validate_dataframe(
        dataframe,
        required_columns=["customer_id", "email"],
        unique_columns=["customer_id"],
    )

    assert report["status"] == "FAILED"
    assert report["duplicate_count"] == 1


def test_validate_dataframe_detects_missing_columns():
    """Verify that missing required columns are detected."""

    dataframe = pd.DataFrame({
        "customer_id": ["CUST-00001"],
    })

    report = validate_dataframe(
        dataframe,
        required_columns=["customer_id", "email"],
    )

    assert report["status"] == "FAILED"
    assert any("Missing required columns" in error for error in report["errors"])


def test_validate_dataframe_detects_empty_dataset():
    """Verify that empty datasets fail validation."""

    dataframe = pd.DataFrame(
        columns=["customer_id", "email"]
    )

    report = validate_dataframe(
        dataframe,
        required_columns=["customer_id", "email"],
    )

    assert report["status"] == "FAILED"
