import json
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
METRICS_PATH = ROOT / "readmission_metrics.json"

st.set_page_config(page_title="Trends Dashboard", page_icon="📊", layout="wide")
st.title("Readmission Trends Dashboard")

metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8")) if METRICS_PATH.exists() else None

c1, c2, c3 = st.columns(3)
if metrics:
    c1.metric("Test ROC-AUC", f"{metrics['roc_auc']:.3f}")
    c2.metric("Test average precision", f"{metrics['average_precision']:.3f}")
    c3.metric("Test positive readmission rate", f"{metrics['positive_rate']:.1%}")
else:
    c1.metric("Test ROC-AUC", "Not trained")
    c2.metric("Test average precision", "Not trained")
    c3.metric("Test positive readmission rate", "Not trained")

st.subheader("Demo monthly trend")
trend = pd.DataFrame({
    "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
    "Readmissions": [14.2, 13.8, 13.1, 12.6, 11.9, 11.4],
})
st.line_chart(trend.set_index("Month"))

st.subheader("Demo rate by department")
dept = pd.DataFrame({
    "Department": ["Cardiology", "Internal Medicine", "Neurology", "Orthopedics", "Pulmonology"],
    "30-day readmission rate": [14.8, 13.2, 11.7, 9.4, 16.1],
})
st.bar_chart(dept.set_index("Department"), color="#e8590c")

st.info("ROC-AUC, average precision, and test positive rate are from the real UCI dataset. Monthly trends and department rates are clearly marked demo values.")

st.divider()