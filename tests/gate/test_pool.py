"""`tests/gate/_pool.py` (feature 215): a shipped spec is read from the pool's map, any other goes to the roll cache.
Feature 219: the gate rolls no spec of its own, so the roll-cache branches are proved on stubs here."""

from __future__ import annotations

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.pipeline import rollcache
from tests import rolls
from tests.gate import _pool


def test_a_spec_the_pool_does_not_carry_goes_to_the_roll_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    spec = hg.HamletSpec(name="Probe", seed=3, households=10)
    assert _pool.gen_of(spec) is None and _pool.gen_of(rolls.REFERENCE) is not None
    monkeypatch.setattr(rollcache, "hamlet", lambda s: ("plan", {"M": s.seed}))
    monkeypatch.setattr(rollcache, "report", lambda s: ("report", "HIT"))
    assert _pool.rolled_map(spec) == ("plan", {"M": 3})
    assert _pool.rolled_report(spec) == "report"


def test_a_pool_map_read_twice_by_one_test_is_obtained_once(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 417 T44 (the round arbiter's tooling fix on ask:417-T31-C2-regression): `rolled_map` then `rolled_report` read a
    stale pool map twice in one test, and each read regenerated it - the roll census then refused an otherwise-green landing.
    The second read is served what the first obtained."""
    calls: list[str] = []
    monkeypatch.setattr(_pool.gencache, "gate_obtain", lambda g: (calls.append(g), (f"/tmp/{g}.json", "REGENERATED", 1.0))[1])
    monkeypatch.setattr(_pool, "refresh_census", lambda m: False)
    first = _pool.obtain_full("pool/x/x.gen.py")
    again = _pool.obtain_full("pool/x/x.gen.py")
    assert calls == ["pool/x/x.gen.py"], "the map is rolled once"
    assert first[0] == again[0] and again[1] == "CACHED"
