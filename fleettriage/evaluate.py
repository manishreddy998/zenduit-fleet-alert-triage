import json, time
from pathlib import Path
from .data import generate
from .model import Triage, is_safety_critical


def main():
    rows = generate()
    train, test = rows[:4000], rows[4000:]
    m = Triage().fit(train)
    t0 = time.perf_counter()
    curve = []
    for th in [0.2, 0.25, 0.3, 0.35, 0.4, 0.5, 0.6]:
        m.threshold = th
        dec = [m.decide(a) for a in test]
        shown = [d["action"] != "suppress" for d in dec]
        act = [a["actionable"] for a in test]
        tp = sum(s and y for s, y in zip(shown, act))
        curve.append({"threshold": th, "alerts_shown": sum(shown), "share_suppressed": round(1 - sum(shown) / len(test), 3),
                      "actionable_recall": round(tp / sum(act), 3), "precision_of_shown": round(tp / max(1, sum(shown)), 3)})
    ms = (time.perf_counter() - t0) * 1000 / (len(test) * 7)
    m.threshold = 0.2
    crit = [a for a in test if is_safety_critical(a)]
    missed_crit = sum(m.decide(a)["action"] != "escalate" for a in crit)
    base_prec = round(sum(a["actionable"] for a in test) / len(test), 3)
    out = {"train": len(train), "test": len(test), "baseline_show_everything": {"alerts_shown": len(test), "precision_of_shown": base_prec},
           "curve": curve, "safety_critical_in_test": len(crit), "safety_critical_missed": missed_crit, "ms_per_alert": round(ms, 3)}
    Path("results.json").write_text(json.dumps(out, indent=2))
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6.5, 3.5))
    ax.plot([c["share_suppressed"] for c in curve], [c["actionable_recall"] for c in curve], "o-", color="#2563eb")
    for c in curve: ax.annotate(str(c["threshold"]), (c["share_suppressed"], c["actionable_recall"]), fontsize=8, xytext=(3, 3), textcoords="offset points")
    ax.set_xlabel("share of alerts suppressed"); ax.set_ylabel("recall of actionable alerts"); ax.set_title("Noise cut vs actionable recall (labels = threshold)")
    ax.grid(alpha=.3); fig.tight_layout(); fig.savefig("docs/results.png", dpi=130)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
