from pathlib import Path

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "readmission_model.joblib"


def _age_band(age):
    age = int(age)
    lower = max(0, (age // 10) * 10)
    upper = lower + 10
    if lower >= 100:
        return "[90-100)"
    return f"[{lower}-{upper})"


def _human_driver(feature_name):
    name = feature_name.replace("numeric__", "").replace("categorical__", "")

    mappings = {
        "number_inpatient": "Prior inpatient admissions",
        "number_emergency": "Emergency visits in the prior year",
        "number_outpatient": "Outpatient visits in the prior year",
        "time_in_hospital": "Extended hospital stay",
        "num_medications": "High medication count",
        "num_lab_procedures": "High number of laboratory procedures",
        "num_procedures": "Number of inpatient procedures",
        "age": "Older age group",
        "discharge_disposition_id": "Complex discharge disposition",
        "admission_source_id": "Admission source",
        "admission_type_id": "Admission type",
        "A1Cresult": "Abnormal or significant HbA1c result",
        "max_glu_serum": "Abnormal glucose serum result",
        "change": "Medication regimen changed during stay",
        "diabetesMed": "Active diabetes medication",
        "diag_1": "Primary diagnosis",
        "diag_2": "Secondary diagnosis",
        "diag_3": "Additional diagnosis",
    }

    for key, label in mappings.items():
        if name.startswith(key):
            return label
    if "race_" in name:
        return "Demographic risk factor"
    if "gender_" in name:
        return "Patient gender category"
    return name.replace("_", " ").title()


def predict(patient):
    """Score an encounter and return a 0-100 risk plus explainable drivers."""
    if not MODEL_PATH.exists():
        raise FileNotFoundError("The readmission model is not trained. Run backend/ml/train.py first.")

    artifact = joblib.load(MODEL_PATH)
    pipeline = artifact["pipeline"]
    features = artifact["features"]

    row = {}
    for feature in features:
        row[feature] = patient.get(feature)

    # Support the demo form's simpler field names.
    if "age" in patient and "age" not in row:
        row["age"] = _age_band(patient["age"])
    if "age" in row and isinstance(row["age"], (int, float)):
        row["age"] = _age_band(row["age"])
    if "prior_admissions" in patient:
        row["number_inpatient"] = patient["prior_admissions"]
    if "length_of_stay" in patient:
        row["time_in_hospital"] = patient["length_of_stay"]
    if "medications" in patient:
        row["num_medications"] = patient["medications"]

    frame = pd.DataFrame([row])
    probability = float(pipeline.predict_proba(frame[features])[:, 1][0])

    classifier = pipeline.named_steps["classifier"]
    preprocessing = pipeline.named_steps["preprocessing"]
    feature_names = preprocessing.get_feature_names_out(features)

    coefficients = classifier.coef_[0]
    transformed = preprocessing.transform(frame[features])
    contributions = transformed.toarray()[0] * coefficients if hasattr(transformed, "toarray") else transformed[0] * coefficients

    ranked = sorted(
        zip(feature_names, contributions),
        key=lambda item: abs(float(item[1])),
        reverse=True,
    )

    drivers = []
    seen = set()
    for feature_name, contribution in ranked:
        if float(contribution) <= 0:
            continue
        driver = _human_driver(feature_name)
        if driver not in seen:
            seen.add(driver)
            drivers.append(driver)
        if len(drivers) == 3:
            break

    if not drivers:
        drivers = ["No dominant model feature identified"]

    risk = round(min(max(probability * 100, 0), 99))
    return {
        "risk": risk,
        "probability": probability,
        "drivers": drivers,
        "model_version": artifact.get("model_version", "unknown"),
    }