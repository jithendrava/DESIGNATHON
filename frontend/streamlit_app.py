import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.ml.predict import predict
from backend.services.intervention_engine import recommend

st.set_page_config(page_title="ReadmissionAI", page_icon="🏥", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #f5f7fb; }
[data-testid="stSidebar"] { background: #102a43; }
[data-testid="stSidebar"] * { color: #f8fafc; }
.block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

DATA_PATH = ROOT / "data" / "diabetes_readmission" / "diabetic_data.csv"
METRICS_PATH = ROOT / "readmission_metrics.json"

@st.cache_data(ttl=3600)
def load_demo_patients():
    data = pd.read_csv(DATA_PATH)
    sample = data.head(12).copy()
    names = [
        "John Carter", "Maria Garcia", "David Wilson", "Aisha Khan",
        "Robert Brown", "Emma Davis", "Michael Smith", "Linda Nguyen",
        "James Lee", "Patricia Moore", "William Taylor", "Susan Clark",
    ]
    departments = ["Cardiology", "Internal Medicine", "Neurology", "Internal Medicine"]
    sample.insert(0, "name", names)
    sample.insert(1, "department", [departments[i % len(departments)] for i in range(len(sample))])
    sample.insert(2, "patient_id", [f"UCI-{i+1001}" for i in range(len(sample))])
    sample.insert(3, "status", ["Pending" if i % 3 else "In Review" for i in range(len(sample))])
    return sample

@st.cache_resource
def load_metrics():
    if METRICS_PATH.exists():
        return json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    return None

with st.sidebar:
    st.title("🏥 ReadmissionAI")
    st.caption("Care Coordination Assistant")
    st.divider()
    metrics = load_metrics()
    if metrics:
        st.metric("Model ROC-AUC", f"{metrics['roc_auc']:.3f}")
        st.caption("Balanced logistic regression • Patient-separated test")
    st.divider()
    st.success("Clinician review required")

st.title("30-Day Readmission Risk Overview")
st.caption("UCI hospital encounter model • AI scores require clinician review")

patients = load_demo_patients()

# A 12-row demo worklist is useful for immediate interaction.
scored = []
for _, row in patients.iterrows():
    result = predict(row.to_dict())
    scored.append({
        "patient_id": row["patient_id"],
        "name": row["name"],
        "department": row["department"],
        "risk": result["risk"],
        "drivers": result["drivers"],
        "status": row["status"],
    })

patient_frame = pd.DataFrame(scored)
st.session_state["patient_frame"] = patient_frame

high = int((patient_frame["risk"] >= 70).sum())
moderate = int(((patient_frame["risk"] >= 40) & (patient_frame["risk"] < 70)).sum())
pending = int((patient_frame["status"] == "Pending").sum())

c1, c2, c3, c4 = st.columns(4)
c1.metric("High-risk encounters", high)
c2.metric("Moderate-risk encounters", moderate)
c3.metric("Pending clinician review", pending)
c4.metric("Demo encounters", len(patient_frame))

st.divider()
left, right = st.columns([1.8, 1])

with left:
    st.subheader("Priority Worklist")
    display = patient_frame.sort_values("risk", ascending=False).copy()
    display["Risk"] = display["risk"].astype(str) + "%"
    display["Primary driver"] = display["drivers"].apply(lambda values: values[0])
    st.dataframe(
        display[["patient_id", "name", "department", "Risk", "Primary driver", "status"]],
        use_container_width=True,
        hide_index=True,
    )

with right:
    st.subheader("Risk Distribution")
    counts = pd.Series({
        "High": high,
        "Moderate": moderate,
        "Low": int((patient_frame["risk"] < 40).sum()),
    })
    st.bar_chart(counts, color="#1769aa")

st.divider()
st.subheader("Score a patient")
with st.form("patient_form", clear_on_submit=False):
    f1, f2, f3 = st.columns(3)
    with f1:
        age = st.number_input("Age", 18, 100, 72)
        department = st.selectbox("Department", ["Cardiology", "Internal Medicine", "Neurology", "Orthopedics"])
    with f2:
        prior = st.number_input("Prior inpatient admissions", 0, 20, 2)
        emergency = st.number_input("Prior emergency visits", 0, 20, 1)
    with f3:
        stay = st.number_input("Length of stay (days)", 1, 14, 6)
        meds = st.number_input("Medication count", 0, 30, 10)

    submitted = st.form_submit_button("Calculate readmission risk", use_container_width=True)

    if submitted:
        result = predict({
            "age": age,
            "prior_admissions": prior,
            "length_of_stay": stay,
            "medications": meds,
            "number_emergency": emergency,
        })
        tier = "High" if result["risk"] >= 70 else "Moderate" if result["risk"] >= 40 else "Low"
        st.success(f"Risk score: {result['risk']}% — {tier} risk")
        st.write("**Top risk drivers**")
        for driver in result["drivers"]:
            st.write(f"• {driver}")
        st.write("**Suggested interventions**")
        for action in recommend(result["risk"], result["drivers"]):
            st.write(f"✓ {action}")

st.caption("This is clinical decision support for demonstration only. It is not a medical device.")