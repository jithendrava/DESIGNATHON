import requests

BASE = "http://127.0.0.1:8000/api"

def main():
    health = requests.get(f"{BASE}/health", timeout=10)
    health.raise_for_status()
    print("health:", health.json())

    patients = requests.get(f"{BASE}/patients", timeout=30)
    patients.raise_for_status()
    rows = patients.json()["patients"]
    assert rows, "No demo patients returned"
    assert all("risk" in p and "drivers" in p and "interventions" in p for p in rows)
    print(f"patients: {len(rows)}; highest risk: {rows[0]['risk']}%")

    pid = rows[0]["id"]
    review = requests.post(f"{BASE}/patients/{pid}/review", json={
        "decision": "Approve plan", "clinical_note": "Demo review"
    }, timeout=10)
    review.raise_for_status()
    followup = requests.patch(f"{BASE}/patients/{pid}/follow-up", json={
        "status": "Scheduled", "due_date": "2026-12-01"
    }, timeout=10)
    followup.raise_for_status()
    print("review and follow-up endpoints: OK")

if __name__ == "__main__":
    main()
