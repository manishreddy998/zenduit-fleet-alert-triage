"""Hybrid triage. Deterministic safety rules first, then a learned ranker for the rest.

Safety rules can never be overridden by the model, so a collision or critical
engine fault is always escalated no matter what the score says.
"""
import numpy as np
from sklearn.linear_model import LogisticRegression
from .data import TYPES


def is_safety_critical(a):
    return a["type"] == "collision" or a["dtc_sev"] == 3 or a["g"] >= 1.5


def features(a):
    onehot = [int(a["type"] == t) for t in TYPES]
    return onehot + [a["speed"] / 100, a["g"], a["dtc_sev"], a["night"], a["prior_events"], a["repeats_1h"]]


class Triage:
    def __init__(self, threshold=0.2):
        self.threshold = threshold
        self.clf = LogisticRegression(max_iter=1000)

    def fit(self, rows):
        X = np.array([features(r) for r in rows]); y = np.array([r["actionable"] for r in rows])
        self.clf.fit(X, y); return self

    def score(self, a):
        return float(self.clf.predict_proba(np.array([features(a)]))[0, 1])

    def decide(self, a):
        if is_safety_critical(a):
            return {"action": "escalate", "reason": "safety rule", "score": 1.0}
        s = self.score(a)
        return {"action": "notify" if s >= self.threshold else "suppress", "reason": "ranker", "score": round(s, 3)}
