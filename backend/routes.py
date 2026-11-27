from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Literal

from backend.ml.predict import predict
from backend.services.genai_service import GenAIService
from backend.services.intervention_engine import recommend
from backend.services.workflow_store import get_patient_state, update_patient_state

router = APIRouter()

class PatientScoreRequest(BaseModel):
    age: int = Field(default=65, ge=18, le=100)
    prior_admissions: int = Field(default=1, ge=0, le=20)
    length_of_stay: int = Field(default=4, ge=1, le=14)
    medications: int = Field(default=5, ge=0, le=30)
    number_emergency: int = Field(default=0, ge=0, le=20)

class GenAIRequest(BaseModel):
    task: str = Field(default="discharge_summary")
    name: str = Field(default="Patient")
    language: str = Field(default="English")
    risk: int = Field(default=0, ge=0, le=100)
    drivers: list[str] = Field(default_factory=list)
    interventions: list[str] = Field(default_factory=list)

class ReviewRequest(BaseModel):
    decision: Literal["Approve plan", "Modify plan", "Defer to later"]
    clinical_note: str = Field(default="", max_length=4000)

class FollowUpRequest(BaseModel):
    status: Literal["Not started", "Scheduled", "In progress", "Completed"]
    due_date: str | None = None

_genai = GenAIService()

# Synthetic demonstration records. Risk is calculated by the shipped model,
# not copied from presentation-only hardcoded percentages.
DEMO_PATIENTS = [
    {"id":"UCI-1001","name":"John Carter","department":"Cardiology","age":72,"prior_admissions":4,"length_of_stay":8,"medications":18,"number_emergency":3},
    {"id":"UCI-1002","name":"Maria Garcia","department":"Internal Medicine","age":68,"prior_admissions":2,"length_of_stay":6,"medications":12,"number_emergency":1},
    {"id":"UCI-1003","name":"David Wilson","department":"Neurology","age":81,"prior_admissions":3,"length_of_stay":7,"medications":15,"number_emergency":2},
    {"id":"UCI-1004","name":"Aisha Khan","department":"Internal Medicine","age":55,"prior_admissions":1,"length_of_stay":3,"medications":8,"number_emergency":0},
    {"id":"UCI-1005","name":"Robert Brown","department":"Cardiology","age":76,"prior_admissions":5,"length_of_stay":9,"medications":20,"number_emergency":4},
    {"id":"UCI-1006","name":"Emma Davis","department":"Orthopedics","age":63,"prior_admissions":0,"length_of_stay":2,"medications":5,"number_emergency":0},
]

def _tier(risk):
    return "High" if risk >= 70 else "Moderate" if risk >= 40 else "Low"

def _scored_patient(patient):
    result = predict(patient)
    state = get_patient_state(patient["id"])
    return {
        **{k: patient[k] for k in ("id","name","department","age")},
        "risk": result["risk"],
        "probability": result["probability"],
        "tier": _tier(result["risk"]),
        "drivers": result["drivers"],
        "interventions": recommend(result["risk"], result["drivers"]),
        **state,
        "model_version": result.get("model_version"),
    }

@router.get("/health")
def health():
    return {"status": "ok", "model": "readmission-logistic-regression-v1"}

@router.get("/patients")
def patients():
    try:
        rows = [_scored_patient(p) for p in DEMO_PATIENTS]
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    return {"patients": sorted(rows, key=lambda p: p["risk"], reverse=True),
            "source": "synthetic demonstration records scored by the local model"}

@router.get("/patients/{patient_id}")
def patient_detail(patient_id: str):
    patient = next((p for p in DEMO_PATIENTS if p["id"] == patient_id), None)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return _scored_patient(patient)

@router.post("/patients/{patient_id}/review")
def submit_review(patient_id: str, request: ReviewRequest):
    if not any(p["id"] == patient_id for p in DEMO_PATIENTS):
        raise HTTPException(status_code=404, detail="Patient not found")
    status = "Approved" if request.decision == "Approve plan" else (
        "Modified" if request.decision == "Modify plan" else "Deferred"
    )
    state = update_patient_state(patient_id, {
        "review_status": status,
        "decision": request.decision,
        "clinical_note": request.clinical_note,
    })
    return {"patient_id": patient_id, **state}

@router.patch("/patients/{patient_id}/follow-up")
def update_follow_up(patient_id: str, request: FollowUpRequest):
    if not any(p["id"] == patient_id for p in DEMO_PATIENTS):
        raise HTTPException(status_code=404, detail="Patient not found")
    state = update_patient_state(patient_id, {
        "follow_up_status": request.status,
        "follow_up_due": request.due_date,
    })
    return {"patient_id": patient_id, **state}

@router.post("/predict")
def score_patient(request: PatientScoreRequest):
    result = predict(request.model_dump())
    return {**result, "tier": _tier(result["risk"]),
            "interventions": recommend(result["risk"], result["drivers"]),
            "clinician_review_required": True}

@router.post("/genai/generate")
def generate_language_content(request: GenAIRequest):
    allowed_tasks = {"discharge_summary", "clinician_note", "reminder"}
    task = request.task if request.task in allowed_tasks else "discharge_summary"
    return _genai.generate(task, request.model_dump())

@router.get("/genai/status")
def genai_status():
    return {
        "configured": _genai.is_configured(),
        "provider": "azure-openai" if _genai.is_configured() else "offline-safe-fallback",
        "clinician_review_required": True,
    }
