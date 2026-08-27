"""The tripwire's expected-failure pin (feature 133 T91, the GM's waiver)."""

from l7r.diagram.tools import mapcheck as mc


def test_tripwire_verdict_reads_the_pin_like_the_cohort_baseline(monkeypatch):
    monkeypatch.setattr(mc, "TRIPWIRE_EXPECTED", {33: frozenset({"village_windbreak_is_continuous"})})
    assert mc.tripwire_verdict(41, []) == ("ok", False)
    mark, bad = mc.tripwire_verdict(33, ["village_windbreak_is_continuous[belt]"])
    assert not bad and "expected" in mark
    mark, bad = mc.tripwire_verdict(33, ["village_windbreak_is_continuous", "lanes_form_one_network"])
    assert bad and "REGRESSION" in mark and "lanes_form_one_network" in mark
    mark, bad = mc.tripwire_verdict(33, [])
    assert bad and "STALE PIN" in mark, "a pinned seed that comes up clean must make someone drop the pin"
    mark, bad = mc.tripwire_verdict(41, ["a", "b", "c", "d"])
    assert bad and mark == "a, b, c"
