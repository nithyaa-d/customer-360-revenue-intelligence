
"""Safe natural-language analytics query engine."""

from pathlib import Path

import duckdb
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATABASE_FILE = PROJECT_ROOT / "customer_360_analytics.duckdb"

PREDICTIONS_FILE = (
    PROJECT_ROOT / "data" / "processed" / "churn_predictions.csv"
)


def execute_query(sql: str) -> pd.DataFrame:
    """Execute a read-only analytical query against DuckDB."""

    if not DATABASE_FILE.exists():
        raise FileNotFoundError("DuckDB database not found.")

    connection = duckdb.connect(
        str(DATABASE_FILE),
        read_only=True,
    )

    try:
        return connection.execute(sql).fetchdf()
    finally:
        connection.close()


def answer_question(question: str) -> dict:
    """
    Map supported natural-language questions to safe SQL templates.

    Arbitrary SQL supplied by users is never executed.
    """

    question = question.lower().strip()

    if not question:
        return {
            "answer": "Please enter a business question.",
            "data": pd.DataFrame(),
        }

    # -------------------------------------------------
    # 1. Total customers
    # -------------------------------------------------

    if "how many customers" in question or "total customers" in question:

        result = execute_query("""
            SELECT COUNT(*) AS total_customers
            FROM main.dim_customer_360
        """)

        count = int(result.iloc[0]["total_customers"])

        return {
            "answer": f"The platform contains {count:,} customers.",
            "data": result,
        }

    # -------------------------------------------------
    # 2. Highest revenue country
    # -------------------------------------------------

    if (
        "highest revenue country" in question
        or "top country" in question
        or "revenue by country" in question
    ):

        result = execute_query("""
            SELECT
                country,
                COUNT(DISTINCT customer_id) AS customers,
                SUM(annual_revenue) AS total_revenue
            FROM main.dim_customer_360
            GROUP BY country
            ORDER BY total_revenue DESC
        """)

        top_country = result.iloc[0]

        return {
            "answer": (
                f"{top_country['country']} generates the highest "
                f"annual customer revenue at "
                f"${top_country['total_revenue']:,.0f}."
            ),
            "data": result,
        }

    # -------------------------------------------------
    # 3. Highest revenue industry
    # -------------------------------------------------

    if "industry" in question and (
        "highest" in question
        or "top" in question
        or "revenue" in question
    ):

        result = execute_query("""
            SELECT
                industry,
                COUNT(DISTINCT customer_id) AS customers,
                SUM(annual_revenue) AS total_revenue,
                ROUND(AVG(annual_revenue), 2) AS average_revenue
            FROM main.dim_customer_360
            GROUP BY industry
            ORDER BY total_revenue DESC
        """)

        top_industry = result.iloc[0]

        return {
            "answer": (
                f"{top_industry['industry']} has the highest "
                f"total annual customer revenue at "
                f"${top_industry['total_revenue']:,.0f}."
            ),
            "data": result,
        }

    # -------------------------------------------------
    # 4. Acquisition channel performance
    # -------------------------------------------------

    if "acquisition channel" in question or "marketing channel" in question:

        result = execute_query("""
            SELECT
                acquisition_channel,
                COUNT(DISTINCT customer_id) AS customers,
                SUM(annual_revenue) AS total_revenue,
                ROUND(AVG(annual_revenue), 2) AS average_revenue
            FROM main.dim_customer_360
            GROUP BY acquisition_channel
            ORDER BY total_revenue DESC
        """)

        return {
            "answer": (
                "Here is the revenue and customer performance "
                "for each acquisition channel."
            ),
            "data": result,
        }

    # -------------------------------------------------
    # 5. Customer account status
    # -------------------------------------------------

    if "customer status" in question or "account status" in question:

        result = execute_query("""
            SELECT
                account_status,
                COUNT(*) AS customer_count
            FROM main.dim_customer_360
            GROUP BY account_status
            ORDER BY customer_count DESC
        """)

        return {
            "answer": "Here is the customer distribution by account status.",
            "data": result,
        }

    # -------------------------------------------------
    # 6. Customer churn risk predictions
    # -------------------------------------------------

    if "churn risk" in question or "high risk" in question:

        if not PREDICTIONS_FILE.exists():
            return {
                "answer": (
                    "Churn predictions are unavailable. "
                    "Run the churn scoring pipeline first."
                ),
                "data": pd.DataFrame(),
            }

        predictions = pd.read_csv(PREDICTIONS_FILE)

        high_risk = predictions[
            predictions["risk_category"] == "High"
        ]

        count = len(high_risk)

        return {
            "answer": (
                f"{count:,} customers are currently classified "
                "as high churn risk by the demonstration model."
            ),
            "data": high_risk.sort_values(
                "churn_probability",
                ascending=False,
            ).head(10),
        }

    # -------------------------------------------------
    # 7. Top customers by revenue
    # -------------------------------------------------

    if "top customers" in question or "highest paying customers" in question:

        result = execute_query("""
            SELECT
                customer_id,
                customer_name,
                country,
                industry,
                annual_revenue,
                account_status
            FROM main.dim_customer_360
            ORDER BY annual_revenue DESC
            LIMIT 10
        """)

        return {
            "answer": "Here are the top 10 customers by annual revenue.",
            "data": result,
        }

    # -------------------------------------------------
    # Unsupported questions
    # -------------------------------------------------

    return {
        "answer": (
            "I couldn't match that question to a supported analysis yet. "
            "Try asking about total customers, country revenue, "
            "industry performance, acquisition channels, customer status, "
            "churn risk or top customers."
        ),
        "data": pd.DataFrame(),
    }
