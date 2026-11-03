import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
import streamlit as st, pandas as pd
from fleettriage.data import all_alerts, TRIPS
from fleettriage.model import Triage

st.set_page_config(page_title="Fleet alert triage", layout="wide")
st.title("Fleet alert triage")
st.caption("Real phone sensor alerts from 4 car trips (Driver Behavior Dataset, Ferreira et al. 2017). "
           "A hard braking rule escalates first, a ranker trained on the other trips decides the rest.")
A = all_alerts()
trip = st.selectbox("Held out trip", TRIPS, index=0)
thr = st.slider("Ranker threshold", 0.1, 0.9, 0.5, 0.05)
m = Triage(thr).fit([a for a in A if a["trip"] != trip])
rows = [a for a in A if a["trip"] == trip]; d = [m.decide(a) for a in rows]
df = pd.DataFrame(rows); df["action"] = [x["action"] for x in d]; df["score"] = [round(x["score"], 2) for x in d]
c1, c2, c3, c4 = st.columns(4)
c1.metric("Device alerts", len(df)); c2.metric("Escalated", int((df.action == "escalate").sum()))
c3.metric("Notified", int((df.action == "notify").sum())); c4.metric("Suppressed", int((df.action == "suppress").sum()))
st.dataframe(df[["start", "duration", "acc_xy", "gyro_z", "event", "actionable", "action", "score"]].sort_values("score", ascending=False),
             use_container_width=True, height=420)
