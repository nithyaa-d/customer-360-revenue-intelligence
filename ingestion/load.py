"""Load validated datasets into the processed data directory."""

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def load_csv(
    dataframe: pd.DataFrame,
    output_path: str | Path,
    validation_report: dict,
) -> Path:
    """
    Save a validated DataFrame as a CSV file.

    Args:
        dataframe: DataFrame to save.
        output_path: Destination CSV file path.
        validation_report: Report returned by validate_dataframe().

    Returns:
        Path to the saved CSV file.
    """
    if validation_report.get("status") != "PASSED":
        raise ValueError(
            "Data cannot be loaded because validation did not pass."
        )

    if dataframe.empty:
        raise ValueError("Cannot load an empty DataFrame.")

    destination = Path(output_path)

    if destination.suffix.lower() != ".csv":
        raise ValueError("Output file must have a .csv extension.")

    destination.parent.mkdir(parents=True, exist_ok=True)

    logger.info("Loading %d records into %s", len(dataframe), destination)

    dataframe.to_csv(destination, index=False)

    logger.info("Successfully saved data to %s", destination)

    return destination
