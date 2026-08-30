"""Captions, and the one board a hamlet posts (feature 166).

Carries six rules the retired battery re-measured on every finished map: `caption_stands_beside_its_referent`,
`label_hugs_its_referent`, `labels_align_with_their_referent`, `captions_clear_the_ways_they_stand_on`,
`kosatsuba_by_the_road` and `kosatsuba_faces_the_road`.

A CAPTION IS NOT A FEATURE; IT IS A FINGER POINTING AT ONE. Everything here follows from that. It stands
beside its subject rather than on top of it, near enough that the reader does not have to guess which
feature it names, turned to match the thing it labels, and off the ways somebody has to read THROUGH -
a caption lying across a lane notches the lane, and the reader sees a path with a bite out of it.

THE LABEL PHASE IS THE LAST STAGE OF ALL, WHICH IS WHY THESE ARE PLACER RULES AND NOT AUDIT RULES. Every
caption is seated in `stage_labels`, against the finished map, because (GM, feature 157) "how we place
labels will always depend on what else is on the map". So the seat search has the whole page in front of
it and there is nothing downstream to undo its work - exactly the condition under which a post-hoc audit
can only ever re-measure what the placer already decided.

THE KOSATSUBA IS THE STATE SPEAKING. A notice board carries the standing law - the edicts on the five
human relationships, on Christianity, on absconding - and it is posted where the traffic is, at the
entrance to the settlement, turned to face the people walking past. A board set back from the way, or
turned side-on to it, is a proclamation nobody reads, which is the one thing a proclamation cannot be.
"""

from __future__ import annotations

import math

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.pipeline import rollcache

SPEC = hg.HamletSpec(name="Inashiro", seed=4, households=15, down_deg=90, water_sink="pond")

HUG_PX = 120.0
"""How far a caption may sit from the feature it names before the reader has to guess. The standoff
ladder tries progressively further seats; past this it has run out and the subject wants moving instead."""

NOTCH_CLEARANCE = 2.0
"""How near a caption's box may come to a lane's drawn tread. Closer than this and the caption's halo
eats the path."""

BOARD_TO_WAY_PX = 90.0
"""How near the notice board must stand to a way. It is posted where the traffic is."""

FACING_DEG = 45.0
"""How square the board must be to the way it faces. Past this it is side-on and unreadable to somebody
walking past."""


def _seg_dist(px: float, py: float, a, b) -> float:
    ax, ay, bx, by = a[0], a[1], b[0], b[1]
    vx, vy = bx - ax, by - ay
    L2 = vx * vx + vy * vy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / L2))
    return math.hypot(px - (ax + t * vx), py - (ay + t * vy))


def _ways(M):
    out = [[(float(x), float(y)) for x, y in (ln.get("pts") or [])] for ln in (M.get("lanes") or [])]
    lane = M.get("lane")
    if lane and len(lane) >= 2:
        out.append([(float(p[0]), float(p[1])) for p in lane])
    return [p for p in out if len(p) >= 2]


def _box_gap(a, b) -> float:
    dx = max(a[0] - b[2], b[0] - a[2], 0.0)
    dy = max(a[1] - b[3], b[1] - a[3], 0.0)
    return math.hypot(dx, dy)


@pytest.fixture(scope="module")
def rolled():
    return rollcache.hamlet(SPEC)


@pytest.fixture(scope="module")
def labels(rolled):
    """The seated captions, with the assertion that there ARE some. A map that captions nothing would
    satisfy every rule below without drawing a single label."""
    _plan, M = rolled
    L = [lab for lab in (M.get("labels") or []) if len(lab) >= 6]
    assert L, "the roll seated no caption, so every rule in this module would pass on nothing"
    return M, L


def test_every_caption_records_the_feature_it_names(labels) -> None:
    """`caption_stands_beside_its_referent`. A caption must record WHICH feature it points at, not merely
    sit somewhere near one. Without the referent box the map has a piece of text and a reader's guess, and
    every rule below - the hug, the alignment - has nothing to measure against."""
    _M, L = labels
    unanchored = [lab[5] for lab in L if len(lab) < 7 or not lab[6]]
    assert not unanchored, f"caption(s) record no referent: {unanchored[:4]}"


def test_every_caption_hugs_what_it_names(labels) -> None:
    """`label_hugs_its_referent`. A caption floating away from its subject makes the reader pair them by
    proximity, and on a dense sheet proximity is ambiguous. When the standoff ladder cannot seat a caption
    near its subject, the answer is to move the SUBJECT - the caption is not the thing with a reason to be
    where it is."""
    _M, L = labels
    adrift = []
    for lab in L:
        if len(lab) < 7 or not lab[6]:
            continue
        box = (float(lab[0]), float(lab[1]), float(lab[2]), float(lab[3]))
        ref = (float(lab[6][0]), float(lab[6][1]), float(lab[6][2]), float(lab[6][3]))
        gap = _box_gap(box, ref)
        if gap > HUG_PX:
            adrift.append((lab[5], round(gap)))
    assert not adrift, f"caption(s) float too far from what they name (name, px): {adrift}"


def test_every_caption_is_turned_to_match_its_subject(labels) -> None:
    """`labels_align_with_their_referent`. A caption on a rotated feature reads as belonging to it only
    when it shares its angle; set square to the page beside a feature lying at 40 degrees, it reads as
    naming something else. Alignment is modulo 180 because a label reads the same way up either way."""
    _M, L = labels
    misaligned = []
    for lab in L:
        if len(lab) < 8 or lab[7] is None:
            continue
        rot = float(lab[7])
        # the subject's own rotation, matched by the referent box's center
        ref = lab[6]
        if not ref:
            continue
        cx, cy = (float(ref[0]) + float(ref[2])) / 2, (float(ref[1]) + float(ref[3])) / 2
        subj = None
        for key, val in _M.items():
            if key == "labels" or not isinstance(val, list):
                continue
            for f in val:
                if isinstance(f, dict) and f.get("rot") and abs(float(f.get("x", 1e9)) - cx) <= 3.0 and abs(float(f.get("y", 1e9)) - cy) <= 3.0:
                    subj = float(f["rot"])
        if subj is None:
            continue
        off = abs((rot - subj + 90.0) % 180.0 - 90.0)
        if off > 12.0:
            misaligned.append((lab[5], round(off, 1)))
    assert not misaligned, f"caption(s) not turned to match their subject (name, deg off): {misaligned}"


def test_no_caption_lies_across_a_way(labels) -> None:
    """`captions_clear_the_ways_they_stand_on`. A caption's box carries a halo that paints out what is
    under it, so one lying on a lane notches the lane and the reader sees a path with a bite taken out of
    it. The caption has the whole page to sit in; the lane does not."""
    M, L = labels
    ways = _ways(M)
    assert ways, "the roll drew no way, so this rule would judge nothing"
    notched = []
    for lab in L:
        x0, y0, x1, y1 = (float(lab[0]), float(lab[1]), float(lab[2]), float(lab[3]))
        corners = ((x0, y0), (x1, y0), (x0, y1), (x1, y1), ((x0 + x1) / 2, (y0 + y1) / 2))
        for ln in M.get("lanes") or []:
            pts = [(float(a), float(b)) for a, b in (ln.get("pts") or [])]
            half = float(ln.get("w") or 3) / 2.0
            if len(pts) < 2:
                continue
            if any(_seg_dist(cx, cy, pts[i], pts[i + 1]) - half < NOTCH_CLEARANCE for cx, cy in corners for i in range(len(pts) - 1)):
                notched.append((lab[5], round(x0), round(y0)))
                break
    assert not notched, f"caption(s) lie across a lane: {notched[:4]}"


def test_the_notice_board_stands_by_the_way(rolled) -> None:
    """`kosatsuba_by_the_road`. The state's standing law is posted where the traffic is - at the entrance,
    on the way in. A board set back in a field is a proclamation nobody reads, and a proclamation nobody
    reads is not one."""
    _plan, M = rolled
    boards = M.get("kosatsuba") or []
    assert boards, "the roll posted no notice board, so this rule would judge nothing"
    ways = _ways(M)
    assert ways, "the roll drew no way for a board to stand by"
    stray = []
    for b in boards:
        d = min(min(_seg_dist(float(b["x"]), float(b["y"]), p[i], p[i + 1]) for i in range(len(p) - 1)) for p in ways)
        if d > BOARD_TO_WAY_PX:
            stray.append((round(float(b["x"])), round(float(b["y"])), round(d)))
    assert not stray, f"notice board(s) stand away from every way: {stray}"


def test_the_notice_board_faces_the_way(rolled) -> None:
    """`kosatsuba_faces_the_road`. Standing beside the way is not enough - the board must be turned to
    face the people walking past. Side-on it is a plank, and the edicts on it are unreadable to exactly
    the traffic it was posted for."""
    _plan, M = rolled
    boards = M.get("kosatsuba") or []
    assert boards, "the roll posted no notice board"
    ways = _ways(M)
    assert ways, "the roll drew no way for a board to face"
    turned = []
    for b in boards:
        bx, by = float(b["x"]), float(b["y"])
        best, bearing = 1e9, 0.0
        for p in ways:
            for i in range(len(p) - 1):
                d = _seg_dist(bx, by, p[i], p[i + 1])
                if d < best:
                    best = d
                    bearing = math.degrees(math.atan2(p[i + 1][1] - p[i][1], p[i + 1][0] - p[i][0]))
        # MEASURED, NOT GUESSED. `rot` is the board's LONG AXIS (w=12, h=5 - a wide, shallow plank), and
        # the face is normal to it, so the board faces the way when its rotation is PARALLEL to the way's
        # bearing. On the reference roll: rot -95.2, nearest way bearing -95.2, parallel offset 0.0.
        # My first draft asserted the perpendicular and read 90 deg off - a sign convention guessed is a
        # sign convention that will be guessed again, so the measurement is recorded here.
        off = abs((float(b.get("rot") or 0.0) - bearing + 90.0) % 180.0 - 90.0)
        if off > FACING_DEG:
            turned.append((round(bx), round(by), round(off)))
    assert not turned, f"notice board(s) stand side-on to the way they should face (x, y, deg off): {turned}"
