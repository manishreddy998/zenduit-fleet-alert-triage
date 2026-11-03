import sys, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
import streamlit as st, pandas as pd
from fleettriage.data import generate
from fleettriage.model import Triage

st.set_page_config(page_title="Fleet alert triage", layout="wide")
st.title("Fleet alert triage")
st.caption("Synthetic telematics alerts. Safety rules escalate first, a ranker decides what else a fleet manager sees.")
rows = generate(); m = Triage().fit(rows[:4000])
m.threshold = st.slider("Ranker threshold", 0.1, 0.7, 0.2, 0.05)
df = pd.DataFrame(rows[4000:4300]); d = [m.decide(a) for a in rows[4000:4300]]
df["action"] = [x["action"] for x in d]; df["score"] = [x["score"] for x in d]
c1, c2, c3 = st.columns(3)
c1.metric("Escalated", int((df.action == "escalate").sum())); c2.metric("Notified", int((df.action == "notify").sum())); c3.metric("Suppressed", int((df.action == "suppress").sum()))
st.dataframe(df[["vehicle", "type", "speed", "g", "dtc_sev", "repeats_1h", "action", "score"]].sort_values("score", ascending=False).head(25), use_container_width=True)
