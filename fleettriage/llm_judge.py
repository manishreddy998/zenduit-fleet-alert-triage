"""Zero shot Qwen judge: given one alert's sensor peaks, decide whether a fleet manager
should see it. Compared against the same baselines. Replays from data/llm_cache.json."""
import json
from .llm import get_backend
from .data import all_alerts, all_events
from .evaluate import metrics, OUT

SYS = ("You triage telematics alerts from a phone mounted in a car. Linear acceleration is in m/s^2 "
       "(horizontal = braking/accelerating/cornering, about 9.8 = 1 g), yaw rate in rad/s. "
       "Normal city driving rarely passes 3 m/s^2 or 0.5 rad/s. Reply JSON {\"show\": true|false, \"reason\": \"short\"}.")


def prompt(a):
    return (f"Alert lasting {a['duration']} s. Peak horizontal accel {a['acc_xy']:.2f} m/s^2, vertical {a['acc_z']:.2f} m/s^2, "
            f"peak yaw rate {a['gyro_z']:.2f} rad/s, peak pitch/roll rate {a['gyro_xy']:.2f} rad/s. "
            "Is this aggressive driving the fleet manager should see?")


def judge(a, be):
    try:
        return bool(be.complete_json(SYS, prompt(a), 48).get("show"))
    except KeyError:
        raise
    except Exception:
        return True  # parse failure: fail open, show the alert


if __name__ == "__main__":
    A, E, be = all_alerts(), all_events(), get_backend()
    shown = [judge(a, be) for a in A]
    r = {"qwen2.5-3b judge": metrics(A, E, shown)}
    p = OUT / "results.json"; d = json.loads(p.read_text()); d.update(r); p.write_text(json.dumps(d, indent=2)); print(r)
