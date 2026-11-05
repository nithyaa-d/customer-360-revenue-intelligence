
"""Extract data from source CSV files."""

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def extract_csv(file_path: str | Path) -> pd.DataFrame:
    """
    Read a CSV file and return its contents as a DataFrame.

    Args:
        file_path: Path to the source CSV file.

    Returns:
        A pandas DataFrame containing the extracted data.
    """
    source_path = Path(file_path)

    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {source_path}")

    if source_path.suffix.lower() != ".csv":
        raise ValueError("Only CSV files are supported.")

    logger.info("Extracting data from %s", source_path)

    try:
        dataframe = pd.read_csv(source_path)
        logger.info(
            "Successfully extracted %d rows and %d columns",
            len(dataframe),
            len(dataframe.columns),
        )
        return dataframe

    except pd.errors.EmptyDataError as exc:
        raise ValueError(f"Source file is empty: {source_path}") from exc

    except pd.errors.ParserError as exc:
        raise ValueError(f"Unable to parse CSV: {source_path}") from exc
