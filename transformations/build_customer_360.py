"""Build the Gold-layer Customer 360 dataset."""

import logging
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT / "data" / "processed" / "customers_silver.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT / "data" / "processed" / "customer_360.csv"
)


def build_customer_360(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Enrich Silver customer data with business segments."""

    required_columns = [
        "customer_id",
        "annual_revenue",
        "customer_tenure_days",
        "days_since_last_activity",
        "account_status",
        "is_churned",
    ]

    missing_columns = [
        column for column in required_columns
        if column not in dataframe.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    if dataframe.empty:
        raise ValueError("Cannot build Customer 360 from empty data.")

    gold = dataframe.copy()

    # Segment customers based on annual revenue
    gold["revenue_segment"] = pd.cut(
        gold["annual_revenue"],
        bins=[-1, 50000, 200000, float("inf")],
        labels=["SMB", "Mid-Market", "Enterprise"],
    ).astype("string")

    # Segment customers based on recent activity
    gold["engagement_segment"] = pd.cut(
        gold["days_since_last_activity"],
        bins=[-1, 30, 90, float("inf")],
        labels=[
            "Highly Engaged",
            "Moderately Engaged",
            "Low Engagement",
        ],
    ).astype("string")

    # Classify customer lifecycle stage
    gold["customer_lifecycle_stage"] = pd.cut(
        gold["customer_tenure_days"],
        bins=[-1, 90, 365, float("inf")],
        labels=["New", "Established", "Mature"],
    ).astype("string")

    # Classify customer value using revenue thresholds
    gold["customer_value_segment"] = pd.cut(
        gold["annual_revenue"],
        bins=[-1, 50000, 200000, float("inf")],
        labels=["Low Value", "Medium Value", "High Value"],
    ).astype("string")

    return gold.reset_index(drop=True)


def run_customer_360() -> None:
    """Read Silver data and generate the Gold Customer 360 dataset."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    logger = logging.getLogger(__name__)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Silver dataset not found: {INPUT_FILE}. "
            "Run the Silver transformation first."
        )

    logger.info("Reading Silver customer dataset.")
    dataframe = pd.read_csv(INPUT_FILE)

    logger.info("Building Customer 360 dataset.")
    gold_dataframe = build_customer_360(dataframe)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    gold_dataframe.to_csv(OUTPUT_FILE, index=False)

    logger.info(
        "Customer 360 completed: %d customers and %d columns.",
        len(gold_dataframe),
        len(gold_dataframe.columns),
    )

    logger.info("Gold dataset saved at: %s", OUTPUT_FILE)


if __name__ == "__main__":
    run_customer_360()
