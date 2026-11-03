"""Leave one trip out evaluation on the real Driver Behavior Dataset.
Baselines: show every device alert, and a single stricter threshold rule.
Metrics: alerts shown, precision, and event recall (share of the 55 labelled aggressive
events with at least one shown alert)."""
import json
from pathlib import Path
from .data import all_alerts, all_events, TRIPS
from .model import Triage, is_safety_critical

OUT = Path(__file__).resolve().parent.parent / "docs"


def metrics(A, E, shown):
    S = [a for a, s in zip(A, shown) if s]
    agg = [e for e in E if e["aggressive"]]
    hit = sum(any(a["trip"] == e["trip"] and a["start"] < e["end"] and a["end"] > e["start"] for a in S) for e in agg)
    return {"alerts_shown": len(S), "precision": round(sum(a["actionable"] for a in S) / max(len(S), 1), 3),
            "event_recall": round(hit / len(agg), 3), "events_missed": len(agg) - hit}


def run(threshold=0.5):
    A, E = all_alerts(), all_events(); res = {}
    res["show_all"] = metrics(A, E, [True] * len(A))
    res["strict_rule (acc>=3 or gyro>=0.6)"] = metrics(A, E, [a["acc_xy"] >= 3 or a["gyro_z"] >= 0.6 for a in A])
    dec = [None] * len(A)
    for t in TRIPS:
        m = Triage(threshold).fit([a for a in A if a["trip"] != t])
        for i, a in enumerate(A):
            if a["trip"] == t: dec[i] = m.decide(a)
    res[f"hybrid (rule + ranker, thr {threshold})"] = metrics(A, E, [d["action"] != "suppress" for d in dec])
    res["_counts"] = {"alerts": len(A), "actionable": sum(a["actionable"] for a in A), "events": len(E),
                      "aggressive_events": sum(e["aggressive"] for e in E), "safety_rule_hits": sum(map(is_safety_critical, A))}
    return res, A, dec


if __name__ == "__main__":
    out = {}
    for thr in (0.3, 0.5, 0.7):
        r, A, dec = run(thr); out.update(r)
    OUT.mkdir(exist_ok=True); (OUT / "results.json").write_text(json.dumps(out, indent=2)); print(json.dumps(out, indent=2))
