"""Feature 210 FR-005: the child rolls the same hamlet the worker would have. Two real rolls of one small spec,
so it lives in the full tree."""

from __future__ import annotations

import json

import pytest

from l7r.diagram.hamletgen import HamletSpec
from l7r.diagram.pipeline import rollcache


@pytest.mark.rolls_map
def test_the_child_rolls_the_same_hamlet_as_the_worker_would() -> None:
    spec = HamletSpec(name="Childroll", seed=3, households=10)
    direct = rollcache._roll_payload(spec)
    (plan, manifest, rep), deps = rollcache._hamlet_in_child(spec)
    assert rep.line() == direct[2].line() and rep.manifest is not None, "the same report, and it carries its manifest (feature 213)"
    assert json.dumps(manifest, sort_keys=True) == json.dumps(direct[1], sort_keys=True), "the same manifest, byte for byte as JSON"
    assert (plan.spec, plan.W, plan.H) == (direct[0].spec, direct[0].W, direct[0].H), "the same plan (its objects' reprs carry addresses, so the fields are compared)"
    assert deps["functions"] and deps["files"] is not None, "the child recorded what the roll executed"
    assert any("hamletgen" in str(f) for f in deps["functions"]), "the record names the engine functions the roll ran"
