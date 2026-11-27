import streamlit as st
import pandas as pd

st.set_page_config(page_title="Worklist", page_icon="📋", layout="wide")
st.title("Care Coordinator Worklist")
st.caption("AI-prioritized follow-up queue • clinician approval required")

if "patient_frame" not in st.session_state:
    st.info("Open the main dashboard once to populate the worklist.")
    st.stop()

frame = st.session_state["patient_frame"].copy()

risk_filter = st.segmented_control("Risk tier", ["All", "High", "Moderate", "Low"], default="All")
if risk_filter == "High":
    frame = frame[frame["risk"] >= 70]
elif risk_filter == "Moderate":
    frame = frame[(frame["risk"] >= 40) & (frame["risk"] < 70)]
elif risk_filter == "Low":
    frame = frame[frame["risk"] < 40]

frame = frame.sort_values("risk", ascending=False)

for _, row in frame.iterrows():
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns([1.2, 1.2, 2.8, 1.4])
        c1.markdown(f"**{row['name']}**\n<small>{row['patient_id']} • {row['department']}</small>", unsafe_allow_html=True)
        c2.markdown(f"### {row['risk']}%\n<small>Readmission risk</small>", unsafe_allow_html=True)
        c3.markdown(
            "**Top driver:** " + str(row["drivers"][0]) + "\n\n"
            "**Plan:** " + "; ".join([str(x) for x in row["drivers"][:2]])
        )
        c4.selectbox(
            "Follow-up status",
            ["Not started", "Scheduled", "In progress", "Completed"],
            index=0,
            key=f"status-{row['patient_id']}",
        )