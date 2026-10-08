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
