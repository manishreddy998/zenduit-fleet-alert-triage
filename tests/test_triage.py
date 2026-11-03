from fleettriage.data import all_alerts, all_events
from fleettriage.model import Triage, is_safety_critical


def test_real_data_loads():
    A, E = all_alerts(), all_events()
    assert len(E) == 69 and sum(e["aggressive"] for e in E) == 55 and len(A) > 100


def test_safety_rule_never_suppressed():
    A = all_alerts(); m = Triage(threshold=0.99).fit(A)
    for a in A:
        if is_safety_critical(a):
            assert m.decide(a)["action"] == "escalate"


def test_ranker_suppresses_some():
    A = all_alerts(); m = Triage(0.5).fit(A)
    assert any(m.decide(a)["action"] == "suppress" for a in A)
