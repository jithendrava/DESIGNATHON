import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "diabetes_readmission" / "diabetic_data.csv"
MODEL_PATH = ROOT / "readmission_model.joblib"
METRICS_PATH = ROOT / "readmission_metrics.json"

# Numeric and categorical fields available before discharge.
NUMERIC_FEATURES = [
    "time_in_hospital",
    "num_lab_procedures",
    "num_procedures",
    "num_medications",
    "number_outpatient",
    "number_emergency",
    "number_inpatient",
]

CATEGORICAL_FEATURES = [
    "race",
    "gender",
    "age",
    "admission_type_id",
    "discharge_disposition_id",
    "admission_source_id",
    "medical_specialty",
    "payer_code",
    "diag_1",
    "diag_2",
    "diag_3",
    "max_glu_serum",
    "A1Cresult",
    "change",
    "diabetesMed",
]

FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def load_and_prepare():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"UCI dataset not found at {DATA_PATH}")

    data = pd.read_csv(DATA_PATH, na_values=["?", "Unknown/Invalid"])
    data["target"] = (data["readmitted"] == "<30").astype(int)

    # Split by patient rather than encounter to reduce repeated-patient leakage.
    unique_patients = data["patient_nbr"].drop_duplicates().tolist()
    train_patients, test_patients = train_test_split(
        unique_patients, test_size=0.20, random_state=42
    )

    train = data[data["patient_nbr"].isin(train_patients)].copy()
    test = data[data["patient_nbr"].isin(test_patients)].copy()

    return train, test


def build_pipeline():
    numeric = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    categorical = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=True)),
    ])

    preprocessing = ColumnTransformer([
        ("numeric", numeric, NUMERIC_FEATURES),
        ("categorical", categorical, CATEGORICAL_FEATURES),
    ])

    classifier = LogisticRegression(
        class_weight="balanced",
        max_iter=300,
        solver="lbfgs",
        random_state=42,
    )

    return Pipeline([
        ("preprocessing", preprocessing),
        ("classifier", classifier),
    ])


def train():
    train, test = load_and_prepare()
    pipeline = build_pipeline()

    pipeline.fit(train[FEATURES], train["target"])
    probabilities = pipeline.predict_proba(test[FEATURES])[:, 1]
    predictions = (probabilities >= 0.50).astype(int)

    metrics = {
        "model": "balanced logistic regression",
        "dataset": str(DATA_PATH.name),
        "train_encounters": len(train),
        "test_encounters": len(test),
        "train_patients": int(train["patient_nbr"].nunique()),
        "test_patients": int(test["patient_nbr"].nunique()),
        "positive_rate": round(float(test["target"].mean()), 4),
        "roc_auc": round(float(roc_auc_score(test["target"], probabilities)), 4),
        "average_precision": round(float(average_precision_score(test["target"], probabilities)), 4),
        "confusion_matrix": confusion_matrix(test["target"], predictions).tolist(),
        "classification_report": classification_report(
            test["target"], predictions, output_dict=True
        ),
    }

    joblib.dump({
        "pipeline": pipeline,
        "features": FEATURES,
        "numeric_features": NUMERIC_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "threshold": 0.50,
        "model_version": "1.0.0",
    }, MODEL_PATH)

    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print(json.dumps(metrics, indent=2))
    print(f"Saved model to {MODEL_PATH}")


if __name__ == "__main__":
    train()