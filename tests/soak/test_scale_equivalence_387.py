"""Feature 387 (FR-007, SC-003): every changed placement site gives the old form's answer on every call of real rolls.

The reference spec at 15 households and at 40 (beyond the hamlet band, as the perf snapshot's scaling leg rolls it), seeds 4, 25,
39 and 47, rolled with each new function wrapped so every call also asks the old form - the oracles kept in the unit tests (and
the old `tree.admits` here) - and asserts the same answer. A soak test (`tests/soak/CLAUDE.md`): it rolls past the gate's floor
and cannot come from the roll cache, which serves a roll without executing it. Run by `make soak`.

It also measures how often a cell merge's neighbor search misses a live neighbor that a staircase split made after a merge
(plan D3's defect, reported, not fixed): written with the call counts, one file a roll, into the directory `$SOAK_387_OUT` when that is set."""

from __future__ import annotations

import copy
import json
import os
from collections.abc import Mapping
from typing import Any

import pytest

SEEDS = (4, 25, 39, 47)


def _old_admits(base: Any, M: Mapping[str, Any], run: Any, role: str, house: Any = None, yard: Any = None) -> bool:
    """`tree.admits` before feature 387: the whole tree rebuilt and judged for every candidate."""
    from l7r.diagram.hamletgen.ways import law
    from l7r.diagram.hamletgen.ways.tree import (
        _dedup,
        _pt,
        _root,
        _rounded,
        _trial,
        as_joined,
        chain_of,
        hosts,
        laid_run,
        lane_record,
        lanes_chain,
        tree_records,
        tree_shadows,
        walked_shadows,
        way_out_once,
    )

    recs = [*tree_records(M), {"role": role, "of": (float(house["x"]), float(house["y"])) if house is not None else None, "pts": _dedup([_pt(q) for q in run])}]
    root = _root(M)
    host = hosts(recs, root)
    k = len(recs) - 1
    if host[k] is None or len(recs[k]["pts"]) < 2:
        return False
    stub = [{"pts": root, "w": 6.0, "connector": True}] if root is not None else []
    houses = [*(M.get("houses") or []), *([house] if house is not None else [])]
    yards = [*(M.get("threshing_yards") or []), *([yard] if yard is not None else [])]
    view = _trial(M, houses=houses, threshing_yards=yards)
    law_ = copy.copy(base)
    law_.tree = False
    chain = chain_of(recs, host, k)
    whole = [*range(k), k]
    for ctx in (whole, [*reversed(chain[1:]), k]):
        drawn_of = {-1: root} if root is not None else {}  # `lanes_of` as it was, each run laid as the seating remembers it
        for i in ctx:
            drawn_of[i] = _rounded(laid_run(base, M, recs[i]["pts"]))
        lanes = [lane_record(recs[i], drawn_of[i], drawn_of.get(host[i]) if host[i] is not None else None) for i in ctx]
        new = lanes[-1]
        law_.M = _trial(view, lanes=[*lanes[:-1], *stub])
        if not law_(new["pts"], float(new["w"])):
            return False
        if ctx is whole:
            if law.needle_loops({"lanes": [*lanes, *stub]}):
                return False
            if law.needle_loops({"lanes": as_joined(_trial(view, lanes=[*lanes, *stub]), lanes)}):
                return False
            if any(len(ends) > law.DOORSTEP_MAX for ends in law.fronting_ends(_trial(view, lanes=[*lanes, *stub])).values()):
                return False
            if not way_out_once(M, [lanes_chain(recs, host, lanes, k)]):
                return False
            if tree_shadows([ln["pts"] for ln in lanes]) or walked_shadows(lanes):
                return False
    return True


@pytest.fixture
def shadowed(monkeypatch: pytest.MonkeyPatch) -> dict[str, int]:
    """Every changed site wrapped to ask its old form too; the calls compared, by site."""
    import l7r.diagram.waterfields.settle as settle  # the submodule itself, not through the package surface (its census, tests/waterfields/test_surface.py)
    from l7r.diagram.hamletgen.homesteads import bamboo, fixtures
    from l7r.diagram.hamletgen.ways import law, reach, tree, tree_base, web_counts
    from l7r.diagram.settlement import Settlement
    from tests.hamletgen.homesteads.test_strip_near_387 import _scan_blocked
    from tests.hamletgen.ways.test_corridors import _old_field_runs
    from tests.settlement.test_sun_keepouts_387 import _old as _old_sun
    from tests.waterfields.test_settle_neighbors_387 import _old_neighbors

    calls: dict[str, int] = {}

    def seen(site: str) -> None:
        calls[site] = calls.get(site, 0) + 1

    admits = tree.admits

    def admits_both(base: Any, M: Any, run: Any, role: str = tree.ACCESS_ROLE, house: Any = None, yard: Any = None) -> bool:
        got = admits(base, M, run, role, house, yard)
        assert got == _old_admits(base, M, run, role, house, yard), "tree.admits"
        seen("admits")
        return got

    monkeypatch.setattr(tree, "admits", admits_both)

    field_runs = reach.field_runs

    def field_runs_both(*a: Any, **k: Any) -> Any:
        got = field_runs(*a, **k)
        assert got == _old_field_runs(*a, **k), "field_runs"
        seen("field_runs")
        return got

    monkeypatch.setattr(reach, "field_runs", field_runs_both)

    needles_with = tree_base.Faces.needles_with

    def needles_both(self: Any, lanes: Any, changed: Any) -> int:
        got = needles_with(self, lanes, changed)
        assert got == len(law.needle_loops({"lanes": list(lanes)})), "Faces.needles_with"
        seen("needles")
        return got

    monkeypatch.setattr(tree_base.Faces, "needles_with", needles_both)

    p_trial = web_counts.Partners.trial

    def partners_both(self: Any, pair: Any, lanes: Any, tw: Any, ti: Any, edits: Any) -> int:
        got = p_trial(self, pair, lanes, tw, ti, edits)
        name = "doubled_tails" if self.kind == "doubled" else "shadows"
        assert got == pair.__self__.count(name, {"lanes": lanes}, tw, ti), "Partners.trial"
        seen("partners")
        return got

    monkeypatch.setattr(web_counts.Partners, "trial", partners_both)

    e_trial = web_counts.WebEnds.trial

    def ends_both(self: Any, M: Any, lanes: Any, ways: Any, tw: Any, edits: Any) -> int:
        got = e_trial(self, M, lanes, ways, tw, edits)
        assert got == len(law.doorstep_ends(M)), "WebEnds.trial"
        seen("web_ends")
        return got

    monkeypatch.setattr(web_counts.WebEnds, "trial", ends_both)

    neighbors = settle.Fabric.neighbors

    def neighbors_both(self: Any, i: int) -> list[int]:
        got = neighbors(self, i)
        assert got == _old_neighbors(self, i), "Fabric.neighbors"
        seen("neighbors")
        me = self.alive[i]  # plan D3's defect: a live neighbor the stale index cannot find (a split part)
        if any(j != i and j not in got and settle.shared_length(me, c) > 0.0 for j, c in self.alive.items()):
            seen("neighbors_missing_a_split_part")
        return got

    monkeypatch.setattr(settle.Fabric, "neighbors", neighbors_both)

    sun = Settlement._sun_keepouts

    def sun_both(self: Any, bbox: Any, reach_ft: Any = None) -> Any:
        got = sun(self, bbox) if reach_ft is None else sun(self, bbox, reach_ft)
        assert got == (_old_sun(self, bbox) if reach_ft is None else _old_sun(self, bbox, reach_ft)), "_sun_keepouts"
        seen("sun")
        return got

    monkeypatch.setattr(Settlement, "_sun_keepouts", sun_both)

    blocked = bamboo._strip_blocked

    def blocked_both(s: Any, *a: Any, near: Any, **k: Any) -> bool:
        got = blocked(s, *a, near=near, **k)
        assert got == _scan_blocked(s, *a, **k), "_strip_blocked"
        seen("strip")
        return got

    monkeypatch.setattr(bamboo, "_strip_blocked", blocked_both)
    monkeypatch.setattr(fixtures, "_strip_blocked", blocked_both)
    return calls


@pytest.mark.parametrize(("households", "seed"), [(15, 4), *((40, s) for s in SEEDS)])
def test_every_changed_site_answers_as_its_old_form(shadowed: dict[str, int], households: int, seed: int) -> None:
    from contextlib import ExitStack

    from l7r.diagram.hamletgen import HamletSpec
    from l7r.diagram.hamletgen.driver import generate
    from l7r.diagram.hamletgen.plan import beyond_the_band
    from l7r.diagram.tools.perf_snapshot import REFERENCE

    with ExitStack() as band:
        if households > 20:
            band.enter_context(beyond_the_band())
        report = generate(HamletSpec(seed=seed, **{**REFERENCE, "name": f"Soak387-{households}-{seed}", "households": households}), out_base=None, render=False)
    assert report.plan.placed == households
    for site in ("admits", "sun", "neighbors"):  # the strip check only where the roll keeps household bamboo (seed 47 at 40 keeps none)
        assert shadowed.get(site, 0) > 0, f"the roll never reached {site}"
    out = os.environ.get("SOAK_387_OUT")
    if out:  # a directory: one file a roll (the soak runs its tests in parallel)
        os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, f"{households}-{seed}.json"), "w") as fh:
            json.dump(dict(shadowed), fh, indent=1, sort_keys=True)
