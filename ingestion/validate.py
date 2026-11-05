
"""Data quality validation for incoming CRM datasets."""

import logging
from typing import Sequence

import pandas as pd

logger = logging.getLogger(__name__)


def validate_dataframe(
    dataframe: pd.DataFrame,
    required_columns: Sequence[str],
    unique_columns: Sequence[str] | None = None,
) -> dict:
    """
    Validate a DataFrame against basic data quality rules.

    Returns a report containing validation results.
    """
    errors = []
    warnings = []

    if dataframe.empty:
        errors.append("Dataset is empty.")

    missing_columns = [
        column for column in required_columns
        if column not in dataframe.columns
    ]

    if missing_columns:
        errors.append(f"Missing required columns: {missing_columns}")

    if not missing_columns and not dataframe.empty:
        missing_values = dataframe[list(required_columns)].isnull().sum()
        missing_values = missing_values[missing_values > 0]

        if not missing_values.empty:
            warnings.append(
                f"Missing values detected: {missing_values.to_dict()}"
            )

    duplicate_count = 0

    if unique_columns and all(
        column in dataframe.columns for column in unique_columns
    ):
        duplicate_count = int(
            dataframe.duplicated(subset=list(unique_columns)).sum()
        )

        if duplicate_count:
            errors.append(
                f"Found {duplicate_count} duplicate records."
            )

    report = {
        "status": "FAILED" if errors else "PASSED",
        "row_count": len(dataframe),
        "column_count": len(dataframe.columns),
        "errors": errors,
        "warnings": warnings,
        "duplicate_count": duplicate_count,
    }

    if errors:
        logger.error("Data validation failed: %s", errors)
    else:
        logger.info("Data validation passed.")

    return report
