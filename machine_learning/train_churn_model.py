
"""Train a machine learning model to predict customer churn."""

import logging
from pathlib import Path

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT / "data" / "processed" / "customer_360.csv"
)

MODEL_DIR = PROJECT_ROOT / "models"
MODEL_FILE = MODEL_DIR / "churn_model.joblib"

RANDOM_STATE = 42


def load_customer_data() -> pd.DataFrame:
    """Load and validate the Customer 360 dataset."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Customer dataset not found: {INPUT_FILE}. "
            "Run the data pipelines first."
        )

    dataframe = pd.read_csv(INPUT_FILE)

    if dataframe.empty:
        raise ValueError("Customer dataset is empty.")

    return dataframe


def prepare_features(dataframe: pd.DataFrame):
    """Separate model features from the churn target."""

    target = "is_churned"

    excluded_columns = [
        "customer_id",
        "customer_name",
        "email",
        "signup_date",
        "last_activity_date",
        "account_status",
        "is_churned",
    ]

    if target not in dataframe.columns:
        raise ValueError("Churn target column is missing.")

    y = dataframe[target].astype(int)

    X = dataframe.drop(
        columns=excluded_columns,
        errors="ignore",
    )

    return X, y


def build_model(X: pd.DataFrame) -> Pipeline:
    """Build a preprocessing and Random Forest pipeline."""

    categorical_features = X.select_dtypes(
        include=["object", "string"]
    ).columns.tolist()

    numerical_features = X.select_dtypes(
        include=["number", "bool"]
    ).columns.tolist()

    numerical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "encoder",
                OneHotEncoder(handle_unknown="ignore"),
            ),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numerical_pipeline, numerical_features),
            ("categorical", categorical_pipeline, categorical_features),
        ]
    )

    classifier = RandomForestClassifier(
        n_estimators=300,
        max_depth=8,
        min_samples_split=10,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=RANDOM_STATE,
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", classifier),
        ]
    )


def main() -> None:
    """Train, evaluate and save the churn prediction model."""

    logging.basicConfig(level=logging.INFO)

    logger = logging.getLogger(__name__)

    logger.info("Loading Customer 360 dataset.")

    dataframe = load_customer_data()

    X, y = prepare_features(dataframe)

    logger.info("Feature count: %d", X.shape[1])
    logger.info("Customer count: %d", len(X))

    if y.nunique() != 2:
        raise ValueError(
            "Churn modelling requires both churn and non-churn customers."
        )

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    logger.info("Training Random Forest model.")

    model = build_model(X_train)

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    probabilities = model.predict_proba(X_test)[:, 1]

    logger.info(
        "Classification report:\n%s",
        classification_report(y_test, predictions),
    )

    logger.info(
        "Confusion matrix:\n%s",
        confusion_matrix(y_test, predictions),
    )

    roc_auc = roc_auc_score(y_test, probabilities)

    logger.info("ROC-AUC: %.4f", roc_auc)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, MODEL_FILE)

    logger.info("Model saved to: %s", MODEL_FILE)


if __name__ == "__main__":
    main()
