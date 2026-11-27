# ReadmissionAI implementation notes

## Changes in this update
- Replaced the API's presentation-only patient percentages with scores computed by the repository's trained model for synthetic demo encounters.
- Added patient detail, clinician review submission, and follow-up status endpoints.
- Added a small JSON-backed workflow store so demo review/follow-up state survives API restarts.
- Added risk tier and intervention output to the prediction endpoint.

## Run locally
```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
```
API docs: http://127.0.0.1:8000/docs

## API endpoints
- `GET /api/health`
- `GET /api/patients`
- `GET /api/patients/{patient_id}`
- `POST /api/predict`
- `POST /api/patients/{patient_id}/review`
- `PATCH /api/patients/{patient_id}/follow-up`
- `POST /api/genai/generate`
- `GET /api/genai/status`

Example review:
```json
{"decision":"Approve plan","clinical_note":"Reviewed with patient and care team."}
```

Example follow-up:
```json
{"status":"Scheduled","due_date":"2026-12-01"}
```

## Important limitations
- Demo names and encounter inputs are synthetic. They are not real patient records.
- The supplied UCI diabetes readmission model is a research/demo model, not clinically validated. Its saved test ROC-AUC is approximately 0.666 and its positive-class precision is approximately 0.170 at the saved threshold; do not present its score as a clinical probability without calibration and external validation.
- The React frontend still contains seed records and needs to be wired to these API endpoints before its pages reflect persistent backend state.
- JSON storage is for a local hackathon demo only. Production requires authenticated access, role-based authorization, audit logging, encrypted storage, a managed database, and privacy/compliance review.
- AI-generated text is a draft and must be reviewed by a qualified clinician.
