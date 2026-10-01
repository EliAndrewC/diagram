"""Feature 294: what the settlement-review used to catch by eye, as rules over the shipped maps (plan B; research R3).

The GM (2026-10-01): *"if our settlement review is checking for anything which a properly implemented placement algorithm
would make impossible, then we should fix the placement algorithm and then stop checking for that thing in the settlement
review."* Each rule here is one of the review's recorded finding classes (`specs/294-settlement-review-rethink/research.md`
R1, R3), proved RED on a seeded fault of its recorded case first (the `test_*_fires_*` cases, plain inputs) and then held over
every shipped hamlet (the `test_*_pool` cases). The predicates are module-level so the seeded cases call them directly.

Thresholds and their sources (plan D11): footbridges 60 ft apart (GUESS; the placer spaces them 300 ft); house bearings
within +-33.75 deg of the common bearing (research homesteads/240: 87% of houses within the commonest compass point and the
two either side) with no pile-up at the limit; the brook crosses the view in one piece (map drawing convention); the wood shed
nearer its own house than any other building and turned with it (research homesteads/212 and 720; "nearest its own" a GUESS).
"""

from __future__ import annotations

import glob
import json
import os
from collections.abc import Mapping, Sequence
from typing import Any

import pytest
from shapely.geometry import LineString, Point, box
from shapely.strtree import STRtree

_SKILL = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_HAMLETS = sorted(glob.glob(os.path.join(_SKILL, "pool", "hamlets", "*", "*.gen.py")))

FOOTBRIDGE_GAP_FT = 60.0  # GUESS (plan D11): the recorded case was two decks side by side (feature 269, rounds 1-2)
BEARING_BAND_DEG = 33.75  # research homesteads/240: the commonest compass point and the two either side
PILE_AT_LIMIT = 2  # no more than two houses within a degree of the widest turn (the 9-of-16 pile, 269 E round 1)
PILE_FLOOR_DEG = 5.0  # a turn this small is the common bearing itself, not a clamp
SHED_TURN_TOL_DEG = 2.0


def _manifest(gen: str) -> dict[str, Any]:
    from tests.gate import _pool

    with open(_pool.obtain(gen), encoding="utf-8") as fh:
        return json.load(fh)


def _ftpx(M: Mapping[str, Any]) -> float:
    return float((M.get("meta") or {}).get("ftpx") or 1.0)


# ---- B8: no two footbridges side by side ------------------------------------------------------------------


def bridges_too_close(bridges: Sequence[Mapping[str, Any]], ftpx: float, gap_ft: float = FOOTBRIDGE_GAP_FT) -> list[tuple[int, int, float]]:
    """(i, j, ft) for every pair of bridge decks closer than `gap_ft`, found through one STRtree over the deck centers."""
    pts = [Point(b["x"], b["y"]) for b in bridges]
    tree = STRtree(pts)
    out = []
    for i, p in enumerate(pts):
        for j in tree.query(p.buffer(gap_ft / ftpx)):
            j = int(j)
            if j > i and p.distance(pts[j]) * ftpx < gap_ft:
                out.append((i, j, round(p.distance(pts[j]) * ftpx, 1)))
    return out


def test_two_decks_side_by_side_fire() -> None:
    """Seeded: the recorded case, a second deck laid 15 ft along the same ditch."""
    assert bridges_too_close([{"x": 0, "y": 0}, {"x": 15, "y": 0}, {"x": 400, "y": 0}], 1.0) == [(0, 1, 15.0)]


# ---- B11: house bearings within the band, no pile at its limit --------------------------------------------


def _turn(rot: float, bearing: float) -> float:
    return (rot - bearing + 180.0) % 360.0 - 180.0


def bearing_faults(houses: Sequence[Mapping[str, Any]], bearing: float) -> list[str]:
    """Each way the houses' turns break the band: a house outside +-`BEARING_BAND_DEG`, or a pile of more than
    `PILE_AT_LIMIT` houses within a degree of the widest turn (a clamp, not a spread)."""
    turns = [_turn(float(h.get("rot") or 0.0), bearing) for h in houses]
    out = [f"house {i} turned {t:.1f} deg" for i, t in enumerate(turns) if abs(t) > BEARING_BAND_DEG]
    if turns:
        widest = max(abs(t) for t in turns)
        piled = sum(1 for t in turns if abs(abs(t) - widest) <= 1.0)
        if widest > PILE_FLOOR_DEG and piled > PILE_AT_LIMIT:
            out.append(f"{piled} houses piled at {widest:.1f} deg")
    return out


def test_a_pile_at_the_clamp_and_a_house_out_of_the_band_fire() -> None:
    """Seeded: Sawada's recorded case, 9 of 16 houses at +-30 deg; and one house turned 40 deg."""
    assert bearing_faults([{"rot": 30.0}] * 9 + [{"rot": 3.0}] * 7, 0.0) == ["9 houses piled at 30.0 deg"]
    assert bearing_faults([{"rot": 40.0}, {"rot": 0.0}], 0.0) == ["house 0 turned 40.0 deg"]
    assert bearing_faults([{"rot": 0.0}] * 10, 0.0) == [], "every house on the common bearing is no pile"


# ---- B12: the brook crosses the view as one piece ---------------------------------------------------------


def brook_pieces_in_view(stream: Mapping[str, Any], view: Sequence[float]) -> int:
    """How many separate runs of the brook's course lie inside the view (`meta.view` = x, y, w, h)."""
    x, y, w, h = view
    inside = LineString(stream["poly"]).intersection(box(x, y, x + w, y + h))
    return 0 if inside.is_empty else len(getattr(inside, "geoms", [inside]))


def test_a_brook_leaving_and_re_entering_the_view_fires() -> None:
    """Seeded: the recorded case (230 pass 3, Sawada's brook off the frame and back): out of the view and in again."""
    course = {"poly": [[-10, 50], [50, 50], [50, 150], [80, 150], [80, 50], [150, 50]]}
    assert brook_pieces_in_view(course, [0, 0, 100, 100]) == 2
    assert brook_pieces_in_view({"poly": [[-10, 50], [150, 50]]}, [0, 0, 100, 100]) == 1


# ---- B3: the wood shed on its own household's ground, turned with its house --------------------------------


def shed_faults(M: Mapping[str, Any]) -> list[str]:
    """Each wood shed (`farm_fixtures` kind `woodpile`) nearer another household's house than its own (`of`), or turned
    off its house's rake. Its own household's byre, shed or retirement house beside it is not a neighbor's gable."""
    houses = list(M.get("houses") or [])
    centers = [Point(h["x"], h["y"]) for h in houses]
    tree = STRtree(centers)
    out = []
    for f in M.get("farm_fixtures") or []:
        if f.get("kind") != "woodpile":
            continue
        here, own = Point(f["x"], f["y"]), Point(*f["of"])
        nearest = centers[int(tree.nearest(here))]
        if nearest.distance(own) > 1.0 and here.distance(nearest) < here.distance(own) - 1e-6:
            out.append(f"the shed at ({f['x']}, {f['y']}) stands nearer another household's house than its own")
        house = min(houses, key=lambda h: own.distance(Point(h["x"], h["y"])))
        off = abs(_turn(float(f.get("rot") or 0.0), float(house.get("rot") or 0.0))) % 90.0
        if min(off, 90.0 - off) > SHED_TURN_TOL_DEG:  # a quarter turn is the same rake
            out.append(f"the shed at ({f['x']}, {f['y']}) is turned off its house")
    return out


def test_a_shed_on_a_neighbors_gable_or_turned_off_its_house_fires() -> None:
    """Seeded: the recorded case (feature 269, a woodpile on the neighbor's gable), and a shed turned 45 deg."""
    houses = [{"x": 0, "y": 0, "rot": 0}, {"x": 60, "y": 0, "rot": 0}]
    on_gable = {"houses": houses, "farm_fixtures": [{"kind": "woodpile", "x": 50, "y": 0, "rot": 0, "of": [0, 0]}]}
    assert shed_faults(on_gable) and "nearer another household" in shed_faults(on_gable)[0]
    turned = {"houses": houses, "farm_fixtures": [{"kind": "woodpile", "x": 0, "y": 20, "rot": 45, "of": [0, 0]}]}
    assert shed_faults(turned) == ["the shed at (0, 20) is turned off its house"]


# ---- the shipped hamlets ----------------------------------------------------------------------------------


@pytest.mark.parametrize("gen", _HAMLETS, ids=os.path.basename)
def test_the_shipped_hamlets_keep_the_rules_the_review_used_to_judge(gen: str) -> None:
    from l7r.diagram.hamletgen.ways import law

    M = _manifest(gen)
    meta = M.get("meta") or {}
    assert bridges_too_close(M.get("bridges") or [], _ftpx(M)) == [], "B8: two footbridges side by side"
    if meta.get("house_bearing_deg") is not None:
        assert bearing_faults(M.get("houses") or [], float(meta["house_bearing_deg"])) == [], "B11: house bearings"
    for stream in M.get("streams") or []:
        assert brook_pieces_in_view(stream, meta["view"]) <= 1, "B12: the brook leaves and re-enters the view"
    assert shed_faults(M) == [], "B3: wood shed seating"
    # B13: the lane law the placer guarantees, proved on what shipped
    assert law.needle_ends(M.get("lanes") or []) == [], "B13: a needle join"
    assert law.needle_loops(M) == [], "B13: a needle loop"
    assert law.lanes_that_kink(M) == [], "B13: a lane that doubles back or kinks"


# ---- B15: every map folder carries its notes --------------------------------------------------------------


def folders_without_notes(root: str) -> list[str]:
    """Every map or sheet folder of both pool trees with no non-empty `<name>.notes.md`."""
    out = []
    for tree in ("pool", "legacy-hand-authored-pool"):
        for d in sorted(glob.glob(os.path.join(root, tree, "*", "*"))):
            name = os.path.basename(d)
            if not os.path.isdir(d) or not any(os.path.isfile(os.path.join(d, f"{name}{ext}")) for ext in (".gen.py", ".json", ".svg")):
                continue
            notes = os.path.join(d, f"{name}.notes.md")
            if not os.path.isfile(notes) or not open(notes, encoding="utf-8").read().strip():
                out.append(name)
    return out


def test_a_map_folder_with_no_notes_fires(tmp_path: Any) -> None:
    d = tmp_path / "pool" / "hamlets" / "bare"
    d.mkdir(parents=True)
    (d / "bare.gen.py").write_text("")
    assert folders_without_notes(str(tmp_path)) == ["bare"]
    (d / "bare.notes.md").write_text("# bare\n")
    assert folders_without_notes(str(tmp_path)) == []


def test_every_pool_and_legacy_map_folder_carries_its_notes() -> None:
    assert folders_without_notes(_SKILL) == []
