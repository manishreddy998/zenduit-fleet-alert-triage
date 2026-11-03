"""Hybrid triage on real sensor alerts. A hard safety rule first (very hard braking or
acceleration is always shown), then a logistic ranker decides which other alerts a fleet
manager sees. The model can never hide an alert that the safety rule escalates."""
import numpy as np
from sklearn.linear_model import LogisticRegression

HARD_ACC = 4.0  # m/s^2, about 0.4 g


def is_safety_critical(a):
    return a["acc_xy"] >= HARD_ACC


def features(a):
    return [a["acc_xy"], a["acc_z"], a["gyro_z"], a["gyro_xy"], np.log1p(a["duration"])]


class Triage:
    def __init__(self, threshold=0.3):
        self.threshold = threshold; self.lr = LogisticRegression(max_iter=1000, class_weight="balanced")

    def fit(self, rows):
        self.lr.fit(np.array([features(a) for a in rows]), [a["actionable"] for a in rows]); return self

    def score(self, a):
        return float(self.lr.predict_proba(np.array([features(a)]))[0, 1])

    def decide(self, a):
        s = self.score(a)
        if is_safety_critical(a):
            return {"action": "escalate", "score": s, "why": "hard acceleration rule"}
        return {"action": "notify" if s >= self.threshold else "suppress", "score": s, "why": "ranker"}
