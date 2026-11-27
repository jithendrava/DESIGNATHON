"""JSON-backed demo workflow state. Replace with an authenticated database in production."""
import json
from pathlib import Path
from threading import Lock
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / "data" / "demo_workflow.json"
_LOCK = Lock()

def _load():
    if not STORE.exists():
        return {}
    try:
        return json.loads(STORE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

def _save(data):
    STORE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STORE.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    tmp.replace(STORE)

def get_patient_state(patient_id):
    with _LOCK:
        return _load().get(patient_id, {
            "review_status": "Pending",
            "decision": None,
            "clinical_note": "",
            "follow_up_status": "Not started",
            "follow_up_due": None,
            "updated_at": None,
        })

def update_patient_state(patient_id, updates):
    with _LOCK:
        data = _load()
        current = data.get(patient_id, {
            "review_status": "Pending",
            "decision": None,
            "clinical_note": "",
            "follow_up_status": "Not started",
            "follow_up_due": None,
            "updated_at": None,
        })
        current.update(updates)
        current["updated_at"] = datetime.now(timezone.utc).isoformat()
        data[patient_id] = current
        _save(data)
        return current
