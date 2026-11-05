"""Generate revenue and customer analytics from the Gold dataset."""

import logging
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT / "data" / "processed" / "customer_360.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "analytics"


def validate_customer_data(dataframe: pd.DataFrame) -> None:
    """Validate the columns required for revenue analytics."""

    required_columns = [
        "customer_id",
        "country",
        "industry",
        "acquisition_channel",
        "annual_revenue",
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
        raise ValueError("Customer dataset is empty.")

    if dataframe["customer_id"].duplicated().any():
        raise ValueError("Duplicate customer IDs detected.")


def build_revenue_analysis(
    dataframe: pd.DataFrame,
    dimension: str,
) -> pd.DataFrame:
    """Summarise customer revenue by a selected business dimension."""

    validate_customer_data(dataframe)

    allowed_dimensions = [
        "country",
        "industry",
        "acquisition_channel",
    ]

    if dimension not in allowed_dimensions:
        raise ValueError(
            f"Unsupported dimension: {dimension}"
        )

    summary = (
        dataframe.groupby(dimension, dropna=False)
        .agg(
            customer_count=("customer_id", "nunique"),
            total_annual_revenue=("annual_revenue", "sum"),
            average_annual_revenue=("annual_revenue", "mean"),
        )
        .reset_index()
    )

    summary["average_annual_revenue"] = (
        summary["average_annual_revenue"].round(2)
    )

    return summary.sort_values(
        "total_annual_revenue",
        ascending=False,
    ).reset_index(drop=True)


def build_customer_kpis(dataframe: pd.DataFrame) -> dict:
    """Calculate high-level customer and revenue KPIs."""

    validate_customer_data(dataframe)

    total_customers = int(dataframe["customer_id"].nunique())

    churned_customers = int(
        dataframe["is_churned"].astype(bool).sum()
    )

    total_annual_revenue = float(
        dataframe["annual_revenue"].sum()
    )

    return {
        "total_customers": total_customers,
        "active_customers": int(
            (dataframe["account_status"] == "Active").sum()
        ),
        "at_risk_customers": int(
            (dataframe["account_status"] == "At Risk").sum()
        ),
        "churned_customers": churned_customers,
        "churn_rate_pct": round(
            churned_customers / total_customers * 100, 2
        ),
        "total_annual_customer_revenue": round(
            total_annual_revenue, 2
        ),
        "average_annual_revenue_per_customer": round(
            total_annual_revenue / total_customers, 2
        ),
    }


def run_revenue_analysis() -> None:
    """Generate and save all revenue analytics outputs."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    logger = logging.getLogger(__name__)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Customer 360 dataset not found: {INPUT_FILE}"
        )

    logger.info("Reading Gold Customer 360 dataset.")

    dataframe = pd.read_csv(INPUT_FILE)

    validate_customer_data(dataframe)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Revenue analysis by business dimensions
    for dimension in [
        "country",
        "industry",
        "acquisition_channel",
    ]:
        summary = build_revenue_analysis(dataframe, dimension)

        output_file = OUTPUT_DIR / f"revenue_by_{dimension}.csv"

        summary.to_csv(output_file, index=False)

        logger.info("Generated revenue analysis: %s", output_file)

    # Customer KPI summary
    kpis = build_customer_kpis(dataframe)

    kpi_dataframe = pd.DataFrame(
        list(kpis.items()),
        columns=["metric", "value"],
    )

    kpi_file = OUTPUT_DIR / "customer_kpis.csv"

    kpi_dataframe.to_csv(kpi_file, index=False)

    logger.info("Generated customer KPI report: %s", kpi_file)

    logger.info("Revenue analytics completed successfully.")
    logger.info("Customer KPIs: %s", kpis)


if __name__ == "__main__":
    run_revenue_analysis()
