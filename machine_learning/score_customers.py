
"""Generate customer-level churn risk predictions."""

import logging
from pathlib import Path

import joblib
import pandas as pd

from machine_learning.train_churn_model import (
    MODEL_FILE,
    load_customer_data,
    prepare_features,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent

OUTPUT_FILE = (
    PROJECT_ROOT / "data" / "processed" / "churn_predictions.csv"
)


def assign_risk_category(probability: float) -> str:
    """Assign a customer risk category based on churn probability."""

    if probability >= 0.70:
        return "High"
    elif probability >= 0.40:
        return "Medium"
    else:
        return "Low"


def score_customers() -> pd.DataFrame:
    """Load the trained model and score all customers."""

    if not MODEL_FILE.exists():
        raise FileNotFoundError(
            f"Trained model not found: {MODEL_FILE}. "
            "Train the churn model first."
        )

    dataframe = load_customer_data()

    X, _ = prepare_features(dataframe)

    model = joblib.load(MODEL_FILE)

    probabilities = model.predict_proba(X)[:, 1]
    predictions = model.predict(X)

    # Keep useful customer information for business users
    output_columns = [
        "customer_id",
        "country",
        "industry",
        "annual_revenue",
        "days_since_last_activity",
    ]

    results = dataframe[output_columns].copy()

    results["churn_probability"] = probabilities.round(4)
    results["predicted_churn"] = predictions.astype(bool)

    results["risk_category"] = [
        assign_risk_category(probability)
        for probability in probabilities
    ]

    results = results.sort_values(
        "churn_probability",
        ascending=False,
    ).reset_index(drop=True)

    return results


def main() -> None:
    """Generate and save customer churn predictions."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    logger = logging.getLogger(__name__)

    logger.info("Starting customer churn scoring.")

    results = score_customers()

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    results.to_csv(OUTPUT_FILE, index=False)

    logger.info("Scored %d customers.", len(results))

    logger.info(
        "Risk distribution:\n%s",
        results["risk_category"].value_counts(),
    )

    logger.info("Predictions saved to: %s", OUTPUT_FILE)


if __name__ == "__main__":
    main()
