from fleettriage.data import generate
from fleettriage.model import Triage


def test_collision_always_escalates_even_at_max_threshold():
    rows = generate(2000)
    m = Triage(threshold=0.99).fit(rows)
    for a in rows:
        if a["type"] == "collision":
            assert m.decide(a)["action"] == "escalate"


def test_ranker_suppresses_some_noise():
    rows = generate(3000)
    m = Triage().fit(rows[:2000])
    assert any(m.decide(a)["action"] == "suppress" for a in rows[2000:])


def test_data_deterministic():
    assert generate(100) == generate(100)
