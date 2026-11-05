"""Run the Silver-layer customer transformation pipeline."""

import logging
from pathlib import Path

import pandas as pd

from transformations.clean_customers import clean_customers


PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "customers.csv"
OUTPUT_FILE = (
    PROJECT_ROOT / "data" / "processed" / "customers_silver.csv"
)


def run_transformations() -> None:
    """Read Bronze data, transform it and save the Silver dataset."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    logger = logging.getLogger(__name__)

    logger.info("Starting Silver transformation pipeline.")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Bronze dataset not found: {INPUT_FILE}. "
            "Run the ingestion pipeline first."
        )

    # Step 1: Read Bronze data
    logger.info("Reading Bronze dataset: %s", INPUT_FILE)
    dataframe = pd.read_csv(INPUT_FILE)

    # Step 2: Transform customer data
    logger.info("Transforming customer records.")
    silver_dataframe = clean_customers(dataframe)

    # Step 3: Save Silver data
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    silver_dataframe.to_csv(OUTPUT_FILE, index=False)

    logger.info(
        "Silver transformation completed successfully. "
        "Processed %d customers and generated %d columns.",
        len(silver_dataframe),
        len(silver_dataframe.columns),
    )

    logger.info("Silver dataset saved at: %s", OUTPUT_FILE)


if __name__ == "__main__":
    run_transformations()
