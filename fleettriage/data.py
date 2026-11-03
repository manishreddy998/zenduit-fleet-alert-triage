"""Seeded SYNTHETIC telematics alert stream. No real fleet data.

Each alert has an event type, speed, g force, engine fault code severity, time of
day and driver history. The hidden label `actionable` says whether a fleet
manager would have needed to act. Labels are noisy on purpose.
"""
import random

TYPES = ["harsh_brake", "harsh_accel", "speeding", "idle", "dtc", "collision", "seatbelt", "geofence"]
BASE = {"harsh_brake": .25, "harsh_accel": .15, "speeding": .2, "idle": .05, "dtc": .3, "collision": .9, "seatbelt": .35, "geofence": .1}


def generate(n=6000, seed=3):
    rng = random.Random(seed)
    rows = []
    for i in range(n):
        t = rng.choices(TYPES, weights=[20, 12, 22, 25, 10, 1, 5, 5])[0]
        speed = max(0, rng.gauss(70 if t == "speeding" else 45, 18))
        g = abs(rng.gauss(0.45 if t in ("harsh_brake", "harsh_accel") else 0.15, 0.15)) + (rng.uniform(1.5, 4) if t == "collision" else 0)
        dtc_sev = rng.choice([0, 1, 2, 3]) if t == "dtc" else 0
        night = int(rng.random() < 0.25)
        prior = rng.randint(0, 6)
        repeats_1h = rng.randint(0, 8)
        p = BASE[t] + 0.08 * (speed > 100) + 0.15 * (g > 0.7) + 0.2 * (dtc_sev == 3) + 0.05 * night + 0.04 * prior - 0.03 * repeats_1h
        actionable = int(rng.random() < min(max(p, 0.01), 0.98))
        if t == "collision" or dtc_sev == 3:
            actionable = 1  # safety critical always needs a human
        rows.append(dict(id=i, vehicle=f"TRK-{rng.randint(1,120):03d}", type=t, speed=round(speed, 1), g=round(g, 2),
                         dtc_sev=dtc_sev, night=night, prior_events=prior, repeats_1h=repeats_1h, actionable=actionable))
    return rows
