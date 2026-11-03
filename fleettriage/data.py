"""REAL data: Driver Behavior Dataset (Ferreira et al., PLOS ONE 2017,
github.com/jair-jr/driverBehaviorDataset). 4 real car trips of about 13 to 21 minutes with a
windshield mounted phone, linear acceleration and gyroscope at 50 to 200 Hz, and 69 video
labelled driving events (aggressive braking, acceleration, turns, lane changes, non aggressive).

A device style rule raises an alert for every second where acceleration or yaw rate passes a
threshold, the way a telematics unit does. Consecutive alert seconds merge into one alert.
An alert is actionable when it overlaps an aggressive event."""
import csv, json
from pathlib import Path
import numpy as np

D = Path(__file__).resolve().parent.parent / "data" / "driverBehavior"
TRIPS = ["16", "17", "20", "21"]
ACC_T, GYR_T = 2.0, 0.35  # m/s^2 and rad/s, device style thresholds


def _sensor(trip, name, t0):
    rows = list(csv.reader((D / trip / name).open()))[1:]
    t = np.array([(int(r[1]) - t0) / 1e9 for r in rows]); v = np.array([[float(x) for x in r[2:5]] for r in rows])
    return t, v


def events(trip):
    out = []
    for r in list(csv.reader((D / trip / "groundTruth.csv").open()))[1:]:
        out.append({"type": r[0].strip(), "start": float(r[1]), "end": float(r[2]), "aggressive": r[0].strip() != "evento_nao_agressivo"})
    return out


def alerts(trip):
    t0 = json.loads((D / trip / "viagem.json").read_text())["firstCollectionUptimeNanos"]
    ta, a = _sensor(trip, "aceleracaoLinear_terra.csv", t0); tg, g = _sensor(trip, "giroscopio_terra.csv", t0)
    secs = int(max(ta.max(), tg.max())) + 1
    feats = []
    for s in range(secs):
        ma, mg = (ta >= s) & (ta < s + 1), (tg >= s) & (tg < s + 1)
        if not ma.any() or not mg.any():
            feats.append(None); continue
        A, G = a[ma], g[mg]
        feats.append({"acc_xy": float(np.abs(A[:, :2]).max()), "acc_z": float(np.abs(A[:, 2]).max()),
                      "gyro_z": float(np.abs(G[:, 2]).max()), "gyro_xy": float(np.abs(G[:, :2]).max())})
    out, cur = [], None
    for s, f in enumerate(feats):
        hit = f and (max(f["acc_xy"], f["acc_z"]) >= ACC_T or f["gyro_z"] >= GYR_T)
        if hit:
            if cur and s == cur["end"]:
                cur["end"] = s + 1; cur["secs"].append(f)
            else:
                cur = {"trip": trip, "start": s, "end": s + 1, "secs": [f]}; out.append(cur)
    ev = events(trip)
    for al in out:
        S = al.pop("secs")
        al.update({k: max(x[k] for x in S) for k in S[0]}); al["duration"] = al["end"] - al["start"]
        ov = [e for e in ev if e["start"] < al["end"] and e["end"] > al["start"]]
        al["actionable"] = any(e["aggressive"] for e in ov)
        al["event"] = ov[0]["type"] if ov else "none"
    return out


def all_alerts():
    return [a for t in TRIPS for a in alerts(t)]


def all_events():
    return [dict(e, trip=t) for t in TRIPS for e in events(t)]
