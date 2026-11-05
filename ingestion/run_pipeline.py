"""Run the end-to-end CRM data ingestion pipeline."""

import logging
from pathlib import Path

from ingestion.extract import extract_csv
from ingestion.validate import validate_dataframe
from ingestion.load import load_csv


# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Input and output locations
INPUT_FILE = PROJECT_ROOT / "data" / "raw" / "customers.csv"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "customers.csv"

# Required customer dataset columns
REQUIRED_COLUMNS = [
    "customer_id",
    "email",
    "signup_date",
    "country",
    "industry",
    "annual_revenue",
    "acquisition_channel",
    "account_status",
]


def run_pipeline() -> None:
    """Execute extraction, validation, and loading."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    logger = logging.getLogger(__name__)

    logger.info("Starting CRM data ingestion pipeline.")

    # Step 1: Extract
    dataframe = extract_csv(INPUT_FILE)

    # Step 2: Validate
    validation_report = validate_dataframe(
        dataframe=dataframe,
        required_columns=REQUIRED_COLUMNS,
        unique_columns=["customer_id"],
    )

    logger.info("Validation report: %s", validation_report)

    if validation_report["status"] != "PASSED":
        raise ValueError("Pipeline stopped because data validation failed.")

    # Step 3: Load
    output_path = load_csv(
        dataframe=dataframe,
        output_path=OUTPUT_FILE,
        validation_report=validation_report,
    )

    logger.info("Pipeline completed successfully.")
    logger.info("Processed dataset saved at: %s", output_path)


if __name__ == "__main__":
    run_pipeline()
