
"""Run the complete Customer 360 analytics pipeline."""

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def run_step(description, command):

    print("\n" + "=" * 70)
    print(f"STEP: {description}")
    print("=" * 70)

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Pipeline failed during: {description}"
        )

    print(f"\nSUCCESS: {description}")


def main():

    python = sys.executable

    steps = [
        (
            "Generate synthetic customer data",
            [
                python,
                "data/generate_data.py",
            ],
        ),
        (
            "Ingest and validate customer data",
            [
                python,
                "-m",
                "ingestion.run_pipeline",
            ],
        ),
        (
            "Run data transformations",
            [
                python,
                "-m",
                "transformations.run_transformations",
            ],
        ),
        (
            "Build Customer 360",
            [
                python,
                "-m",
                "transformations.build_customer_360",
            ],
        ),
        (
            "Generate revenue analytics",
            [
                python,
                "-m",
                "analytics.revenue_analysis",
            ],
        ),
        (
            "Build dbt models",
            [
                python,
                "-m",
                "dbt.cli.main",
                "run",
                "--project-dir",
                "dbt_project",
                "--profiles-dir",
                "dbt_project",
            ],
        ),
        (
            "Run dbt data quality tests",
            [
                python,
                "-m",
                "dbt.cli.main",
                "test",
                "--project-dir",
                "dbt_project",
                "--profiles-dir",
                "dbt_project",
            ],
        ),
        (
            "Verify dbt outputs",
            [
                python,
                "analytics/verify_dbt_outputs.py",
            ],
        ),
        (
            "Train churn prediction model",
            [
                python,
                "-m",
                "machine_learning.train_churn_model",
            ],
        ),
        (
            "Score customers for churn risk",
            [
                python,
                "-m",
                "machine_learning.score_customers",
            ],
        ),
    ]

    print("\nCUSTOMER 360 | REVENUE INTELLIGENCE")
    print("Starting complete analytics pipeline...")

    try:

        for description, command in steps:
            run_step(description, command)

    except RuntimeError as error:

        print(f"\nPIPELINE FAILED: {error}")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 70)

    print("\nGenerated outputs:")
    print("- data/raw/customers.csv")
    print("- data/processed/customers_silver.csv")
    print("- data/processed/customer_360.csv")
    print("- data/processed/analytics/")
    print("- customer_360_analytics.duckdb")
    print("- models/churn_model.joblib")
    print("- data/processed/churn_predictions.csv")

    print("\nYou can now launch the dashboard using:")
    print("python -m streamlit run dashboard/app.py")


if __name__ == "__main__":
    main()

