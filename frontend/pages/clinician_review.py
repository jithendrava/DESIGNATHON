import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.services.discharge_summary import summary
from backend.services.intervention_engine import recommend

st.set_page_config(page_title="Clinician Review", page_icon="🩺", layout="wide")
st.title("Clinician Review")
st.caption("Required review before any intervention plan is released")

st.warning("Clinical decision support only — approve, modify, or defer every high-risk AI flag.")

if "patient_frame" not in st.session_state:
    st.info("Open the main dashboard once to load a patient for review.")
    st.stop()

frame = st.session_state["patient_frame"]
patient_options = frame.sort_values("risk", ascending=False)["patient_id"].tolist()
selected_id = st.selectbox("Patient", patient_options)
patient = frame[frame["patient_id"] == selected_id].iloc[0]

left, right = st.columns([1.45, 1])

with left:
    st.subheader(f"Patient: {patient['name']} • {patient['patient_id']}")
    m1, m2, m3 = st.columns(3)
    m1.metric("Readmission risk", f"{patient['risk']}%")
    m2.metric("Department", patient["department"])
    m3.metric("Review status", patient["status"])

    st.markdown("**Top model risk drivers**")
    for index, driver in enumerate(patient["drivers"][:3], start=1):
        st.write(f"{index}. {driver}")

with right:
    st.subheader("Recommended intervention plan")
    actions = recommend(int(patient["risk"]), patient["drivers"])
    selected_actions = {}
    for action in actions:
        selected_actions[action] = st.checkbox(action, value=True)

    clinician = st.text_input("Clinician name")
    decision = st.radio("Clinical decision", ["Approve plan", "Modify plan", "Defer to later"])
    note = st.text_area("Clinical note", placeholder="Document rationale or modifications…")

    if st.button("Submit review", type="primary", use_container_width=True):
        if not clinician:
            st.error("Enter clinician name before submitting.")
        elif decision != "Defer to later" and not any(selected_actions.values()):
            st.error("Select at least one intervention or choose Defer to later.")
        else:
            st.success(f"Review recorded for {clinician}: {decision}")

st.divider()
st.subheader("Patient-friendly discharge summary")
language = st.selectbox("Language", ["English", "Hindi"])
st.info(summary(patient["name"], language))