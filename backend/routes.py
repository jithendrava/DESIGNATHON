from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.ml.predict import predict
from backend.services.genai_service import GenAIService

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


_genai = GenAIService()


@router.get("/health")
def health():
    return {"status": "ok", "model": "readmission-logistic-regression-v1"}


@router.get("/patients")
def patients():
    rows = [
        {"id": "UCI-1001", "name": "John Carter", "department": "Cardiology", "risk": 84, "status": "Pending"},
        {"id": "UCI-1002", "name": "Maria Garcia", "department": "Internal Medicine", "risk": 69, "status": "In review"},
        {"id": "UCI-1003", "name": "David Wilson", "department": "Neurology", "risk": 76, "status": "Pending"},
        {"id": "UCI-1004", "name": "Aisha Khan", "department": "Internal Medicine", "risk": 43, "status": "Approved"},
        {"id": "UCI-1005", "name": "Robert Brown", "department": "Cardiology", "risk": 81, "status": "Pending"},
        {"id": "UCI-1006", "name": "Emma Davis", "department": "Orthopedics", "risk": 28, "status": "Approved"},
    ]
    return {"patients": rows}


@router.post("/predict")
def score_patient(request: PatientScoreRequest):
    result = predict(request.model_dump())
    return result


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