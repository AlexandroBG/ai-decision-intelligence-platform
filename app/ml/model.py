import pandas as pd
from sklearn.ensemble import IsolationForest

from app.ml.errors import MLInputError
from app.ml.features import FEATURE_COLUMNS


def train_isolation_forest(
    dataframe: pd.DataFrame,
    contamination: float = 0.08,
    random_state: int = 42,
) -> IsolationForest:
    missing_columns = set(FEATURE_COLUMNS) - set(dataframe.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))

        raise MLInputError(f"Missing required columns for model training: {missing}")

    if dataframe.empty:
        raise MLInputError("Training dataframe must not be empty.")

    if not 0 < contamination <= 0.5:
        raise MLInputError(
            "contamination must be greater than 0 and less than or equal to 0.5."
        )

    features = dataframe[FEATURE_COLUMNS]

    model = IsolationForest(
        contamination=contamination,
        random_state=random_state,
    )

    model.fit(features)

    return model


def score_isolation_forest(
    model: IsolationForest,
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    missing_columns = set(FEATURE_COLUMNS) - set(dataframe.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))

        raise MLInputError(f"Missing required columns for model scoring: {missing}")

    if dataframe.empty:
        raise MLInputError("Scoring dataframe must not be empty.")

    result = dataframe.copy()

    features = result[FEATURE_COLUMNS]

    result["anomaly_score"] = -model.decision_function(features)

    predictions = model.predict(features)

    result["is_anomaly"] = predictions == -1

    return result
