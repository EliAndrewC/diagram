"""The web settles itself - `Lawful`, the one question asked before a tree lane is drawn, and `corridor_on_lawful_ground`. Split from `ways/settle.py` at the 1,000-line bar (feature 405 T54, under T53's rule); the package docstring (`settle/__init__.py`) is the whole account.

Research: settle plumbing - NONE"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

from l7r.diagram.settlement import rot_rect
from l7r.diagram.settlement._knobs import bridge_crossed_waters
from l7r.diagram.settlement.city.bridges import flooded_ground

from ...consts import WEB_FABRIC_GAP, Poly, Pt
from .. import law
from ..corridors import (
    ACCESS_WIDTH,
    MEET_REACH_FT,
    GroundIndex,
    _box,
    _poly_box,
    building_quads,
    open_ground_rings,
    through_a_building,
)
from ..fabric import lane_fabric as _fabric
from ..geom import lane_owner, memo_ground, worked_ground
from ..squaring import (
    _pts,
    square_run,
    square_waters,
)
from ..sweeps import _DOUBLED_DEG, along_tail
from .shapes import _crossing_fault, _rounded, fouled_segment

# ---- step 4b: the reach the web owes - a corridor, a way target, the field ----------------------------------------------


class Lawful:
    """Would a run, drawn as a new lane of a given width, keep every per-lane rule of the law - no kink or hook, no crossing
    fault, no foul of the fabric, no field, dry plot or marsh underfoot (`open_ground_rings`) - and meet the ways it comes near
    as the law asks: no needle, fold or hairpin at either end, no tail doubled along a way, either way round - and, for a
    TREE lane (`tree`), no household's way out left crossing the brook twice (`law.adds_a_way_out_crossing`)? The ONE
    question the web asks before it adds a tree lane, since a tree lane is never cut afterwards. The map's fabric, water
    and wet ground are read once, when it is built, for every run a step asks about. The way-out clause is the tree's
    alone: an ordinary lane re-laid by a repair is cut by step 3 if it carries such a way out, and the route it asks costs
    two walks of the whole web a run (measured 30-60 ms on cohort seeds 3 and 12, most of the settle's time when every
    re-laid end asked it).

    Research: the lane law asked of a new lane - NONE: each clause claimed at `on_lawful_ground` and `__call__`"""

    def __init__(self, s: Any, tree: bool = False) -> None:
        self.M = s.M
        self.tree = tree
        self.wet = flooded_ground(s.M)
        self.yards, self.houses = _fabric(s)
        self.solid = law.solid_boxes(s.M)
        self.fixtures = law.fixture_quads(s.M)
        self.buildings = building_quads(s.M)
        self.ground = memo_ground(s, "worked", worked_ground)
        self._index: GroundIndex | None = None
        # ...AND WHOSE OWN WAY A RUN IS (405 T18): a caller drawing a household's own way sets it on a copy (`copy.copy`), and that
        # household's yards and gardens are exempt from the fence gap (`theirs`); None - every other run - exempts none
        self.owner: Pt | None = None

    @property
    def index(self) -> GroundIndex:
        """The ground `on_lawful_ground` reads, indexed on first use (`corridors.GroundIndex`): the waters a crossing fault
        or the squaring reads, the outlines a run may not cross (`open_ground_rings`), and the fabric the foul tests read."""
        if self._index is None:
            M = self.M
            waters = [*law._brooks(M), *law.water_courses(M, "channel"), *(w for w, _ww in bridge_crossed_waters(M)), *(c for c, _h in square_waters(M))]
            houses = [(h, _poly_box(rot_rect(float(h["x"]), float(h["y"]), float(h["w"]), float(h["h"]), float(h.get("rot", 0.0))))) for h in self.houses]
            self._index = GroundIndex(
                waters,
                open_ground_rings(M),
                {
                    "houses": houses,
                    "yards": [(y, _poly_box(y[0])) for y in self.yards if y[0]],
                    "solid": [(b, b) for b in self.solid],
                    "fixtures": [(q, _poly_box(q)) for q in self.fixtures],
                    "buildings": [(q, _poly_box(q)) for q in self.buildings],
                },
            )
            self._square_pad = max((h for _c, h in square_waters(M)), default=0.0) + 1.0
        return self._index

    def blocked(self, a: Pt, b: Pt, width: float) -> bool:
        """Is the straight way `a`-`b` not lawful ground - `forced`'s question (feature 385 plan D2), asked of this map's
        own ground, so a run's turns and meetings are judged forced or not exactly as the law judges them? A two-point
        chord has no turn of its own, so this never asks itself again.

        Research: a forced turn is lawful - research/questions/0081-village-lanes.drawing.html: "A turn the ground forces is drawn as walked" - the straighter way blocked where it is not lawful ground"""
        return math.dist(a, b) > 1e-6 and not self.on_lawful_ground([a, b], width)

    def squared(self, run: Poly) -> Poly:
        """`square_run(self.M, run)`, skipped where no water the squaring reads comes within its reach of the run - there it
        changes nothing (no crossing to square, no vertex within a water's half-width to drop)."""
        return square_run(self.M, run) if self.index.water_near(run, self._square_pad) else list(run)

    def on_lawful_ground(self, run: Poly, width: float, owner: Pt | None = None) -> bool:
        """`ground_fault` found none: the run is on lawful ground."""
        return self.ground_fault(run, width, owner) is None

    def ground_fault(self, run: Poly, width: float, owner: Pt | None = None) -> str | None:
        """The first rule of the ground half a run breaks, by name, or None (feature 385 T03, plan D16: a refusal says which
        rule turned each run down, so the ground is looked at where it refused). THE GROUND HALF - what a run keeps whatever lanes the web draws beside it: no kink or hook, no crossing fault (a
        brook crossed off a ford or twice, a crossing off square, one no deck seats), no foul of a farmhouse, another
        household's yard or garden, a building or a farmstead fixture, no field, dry plot or marsh underfoot. The seating asks
        this of a corridor before it admits a house (`corridor_on_lawful_ground`), so the web can always draw what it
        reserved.

        Research:
            bends like a path - research/questions/0081-village-lanes.drawing.html: no kink or hook
            crossings - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: `_crossing_fault`
            nothing built on a lane - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: no foul of house, yard, building, fixture
            off crop and marsh - research/questions/0081-village-lanes.drawing.html: no field, dry plot or marsh underfoot"""
        if len(run) < 2:
            return "too short"
        if law.hook_faults(run, width, self.blocked) or law.kink_faults(run, width, self.blocked):
            return "bends"
        # every test below reads only what stands near the run (`index`, `GroundIndex`): a crossing fault needs a crossing,
        # and each foul a part within its own reach of the run - so the parts beyond it are left out, not the verdict
        ix = self.index
        houses = ix.near("houses", run, max(width / 2.0 + 2.0, law.DOORSTEP_FT) + 1.0)  # ...the doorstep's reach: `theirs` reads it
        fouled = fouled_segment(
            run, width, houses, ix.near("yards", run, WEB_FABRIC_GAP + 1.0), ix.near("solid", run, 1.0), ix.near("fixtures", run, width / 2.0 + law.FIXTURE_PAD_FT + 1.0), self.M, owner or self.owner
        )
        if fouled is not None:
            return "fabric"
        if not ix.open_ground(run):
            return "off open ground"
        if through_a_building(run, ix.near("buildings", run, 1.0)):
            return "through a building"
        # ...AND THE CROSSING LAST, the one test that solves a deck (feature 328, the perf-audit of wave 10: the field way's
        # search judged 242 candidates on 20 households seed 4, each solving its crossing first; every test here is pure, so
        # the order changes no verdict - 8.8 s -> 7.9 s, the output identical)
        crossing = ix.water_near(run, 1.0) and _crossing_fault({**self.M, "lanes": [{"pts": _rounded(run), "w": width}]}, 0, run, self.wet) is not None
        return "crossing" if crossing else None

    def __call__(self, run: Poly, width: float, skip: int | None = None) -> bool:
        """`fault` found none. `skip`: the lane `run` would replace, left out of what it is asked to meet."""
        return self.fault(run, width, skip) is None

    def fault(self, run: Poly, width: float, skip: int | None = None) -> str | None:
        """The first rule a run breaks as a new lane, by name, or None (feature 385 T03, plan D16).

        Research:
            lanes meet as a T - research/questions/0081-village-lanes.drawing.html: no needle, fold or hairpin at either end
            an end reaches something seen - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: no dangling end
            no doubled tail - research/questions/0081-village-lanes.drawing.html: an end running back along another way under 20 degrees, either way round; asked here at 15 (`_DOUBLED_DEG`) - a known gap, carried to feature 385 T12 (the side-by-side family)
            no way out over and back - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: tree lanes"""
        M = self.M
        # ...a run that replaces a lane (`skip`) is that lane's: its household's own way where the lane is one (405 T18)
        owner = self.owner or (lane_owner((M.get("lanes") or [])[skip]) if skip is not None and skip < len(M.get("lanes") or []) else None)
        if why := self.ground_fault(run, width, owner):
            return why
        lanes = [ln for k, ln in enumerate(M.get("lanes") or []) if k != skip]
        x0, y0, x1, y1 = _box(run, MEET_REACH_FT)
        near = [ln for ln in lanes if len(ln.get("pts") or []) >= 2 and not ((b := _box(_pts(ln), 0.0))[2] < x0 or b[0] > x1 or b[3] < y0 or b[1] > y1)]
        tl, k = [*near, {"pts": run, "w": width}], len(near)
        if any(k in (n, m) for n, _e, m, _u, _v in law.needle_ends(tl, self.blocked)):
            return "needle_joins"
        if any(k in (a, b) for a, _ea, b, _eb in law.folded_joint_pairs(tl, self.blocked)):
            return "folded_joints"
        if any(n == k for _c, n, _e in law.connector_hairpin_ends(tl, self.blocked)):
            return "connector_hairpins"
        # ...AND EACH END SERVES SOMETHING (the lane law's `dangling_lane_ends`): a tree lane is never trimmed afterwards, so an
        # end it would leave in open ground is refused here
        trial = {**M, "lanes": tl}
        if any(n == k for n, _e in law.dangling_lane_ends(trial, self.ground)):
            return "dangling_lane_ends"
        if any(along_tail(p, q, deg=_DOUBLED_DEG) is not None for o in (_pts(ln) for ln in near) for p, q in ((run, o), (run[::-1], o), (o, run), (o[::-1], run))):
            return "doubled_tails"
        # ...AND IT HANDS NO HOUSEHOLD A WAY OUT OVER THE BROOK AND BACK (ways W08): a way out is a route through the whole
        # web, so it is asked last, of the lanes the run would join - a tree lane is never cut for it afterwards
        return "way_out_over_and_back" if self.tree and law.adds_a_way_out_crossing(M, run, width, lanes) else None


def corridor_on_lawful_ground(M: Mapping[str, Any], run: Poly, width: float = ACCESS_WIDTH, lawful: Lawful | None = None) -> bool:
    """THE SEATING'S QUESTION (feature 287, plan M3): would a corridor along `run`, squared at its water crossings
    (`square_run`), stand on lawful ground (`Lawful.on_lawful_ground`) on the manifest as it stands? One predicate, asked by
    the seating before it admits a house and by the web before it draws the corridor. A caller asking many runs of one manifest
    hands in its `Lawful(SimpleNamespace(M=M))`, indexed once (feature 314: 145 runs, each indexing it again, 3.0 of 5.8 s).

    Research: the seating's corridor - NONE: the ground half of `Lawful`, claimed there"""
    import types

    ix = lawful or Lawful(types.SimpleNamespace(M=M))
    return ix.on_lawful_ground(ix.squared(run), width)  # `squared`: `square_run`, skipped where no water comes near the run
