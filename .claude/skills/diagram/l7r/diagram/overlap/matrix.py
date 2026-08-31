"""The overlap MATRIX (was: shared gate helpers, overlap policy): matrix_violations, check_ring_road_clear, matrix_extents, GridIndex, forest_reveal_x, torii_halfbox, FOREST_REVEAL_FT, CANOPY_STRUCT_KEYS, ... - bodies verbatim from check_village.py (feature 024 package split; SCC-packed, see split_package.py)."""

import math
from collections.abc import Mapping
from typing import Any

from l7r.diagram.settlement import sat_overlap

from .taxonomy import (
    _MATRIX_PARENT_FIELD,
    _MATRIX_PERMISSIVE,
    _MX_FIXTURE_BOX,
    _MX_LINE_W,
    OVERLAP_CLASS,
    Poly,
    _mx_rect,
    _mx_same,
    _mx_stroke,
    matrix_policy,
    point_in_poly,
    poly_dist,
    seg_dist,
    segments_cross,
)


def matrix_violations(M: Mapping[str, Any]) -> list[tuple[str, str, float, float]]:
    """Every FORBIDDEN overlap on the map, as (key_a, key_b, x, y).

    The conditional permissions live here rather than in `matrix_policy`, because each depends on
    the two RECORDS rather than on their classes alone: an annex may lie on its own parent (and only
    its own), two annexes of one household may abut, a supply channel may reach the field it feeds,
    and a trade work's private well stands inside its own court."""
    ext = matrix_extents(M)
    if not ext:
        return []  # pragma: no cover - every real map draws something
    priv = {(round(w_["x"], 1), round(w_["y"], 1)) for w_ in M.get("wells", []) or [] if w_.get("private")}
    polys = [p for _k, p, _i, _pa in ext]
    boxes = [(min(q[0] for q in p), min(q[1] for q in p), max(q[0] for q in p), max(q[1] for q in p)) for p in polys]
    # CLAMP THE INDEX BOX TO THE CANVAS. GridIndex.add inserts under every cell an item's bbox
    # touches, so one feature reaching far off-map costs a dict entry per 120 px in BOTH axes. A
    # malformed map is not hypothetical - `city_geometry_within_canvas` is checked with a fixture
    # planting a wall vertex at 9,000,000 on a 3,200 px canvas, which is ~5.6 BILLION cells and
    # gigabytes of RAM (found the hard way, 2026-07-26: the run had to be killed by hand). The index
    # only PRUNES - every surviving pair is still tested against the real polygons - so clamping the
    # indexed extent changes no verdict for anything actually on the map. Two features BOTH off the
    # canvas may no longer be compared, which is the right division of labour: geometry that is not
    # on the map is `city_geometry_within_canvas`'s business, not the overlap matrix's.
    _mx_w = float(M.get("meta", {}).get("W") or 4000)
    _mx_h = float(M.get("meta", {}).get("H") or 4000)

    def _mx_clamp(b: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
        return (max(b[0], -_mx_w), max(b[1], -_mx_h), min(b[2], _mx_w * 2), min(b[3], _mx_h * 2))

    # Clamp for BOTH insert and query: `near_rect` walks the cells of the box it is GIVEN, so
    # querying with the unclamped extent costs exactly as much as inserting with it did.
    cboxes = [_mx_clamp(b) for b in boxes]
    gi = GridIndex(120)
    for idx, cb in enumerate(cboxes):
        if cb[2] < cb[0] or cb[3] < cb[1]:
            continue  # wholly off the canvas - nothing on the map can meet it
        gi.add(cb[0], cb[1], cb[2], cb[3], idx)
    seen: set[tuple[int, int]] = set()
    out: list[tuple[str, str, float, float]] = []
    for i, (ki, _pi, idi, pari) in enumerate(ext):
        del _pi
        bi = boxes[i]
        cbi = cboxes[i]
        if cbi[2] < cbi[0] or cbi[3] < cbi[1]:
            continue
        for j in gi.near_rect(*cbi):
            if j <= i or (i, j) in seen:
                continue
            seen.add((i, j))
            kj, _pj, idj, parj = ext[j]
            del _pj
            if matrix_policy(ki, kj):
                continue
            bj = boxes[j]
            if bi[2] < bj[0] or bi[0] > bj[2] or bi[3] < bj[1] or bi[1] > bj[3]:
                continue
            if _mx_same(pari, idj) or _mx_same(parj, idi):
                continue  # an annex on its OWN parent
            if OVERLAP_CLASS.get(ki) == "ANNEX" and OVERLAP_CLASS.get(kj) == "ANNEX" and _mx_same(pari, parj):
                continue  # two annexes of one household
            if "wells" in (ki, kj) and ((idi in priv) or (idj in priv)):
                continue  # a trade work's own private well, inside its own court
            if sat_overlap(polys[i], polys[j]):
                cx = sum(q[0] for q in polys[i]) / len(polys[i])
                cy = sum(q[1] for q in polys[i]) / len(polys[i])
                out.append((ki, kj, round(cx), round(cy)))
    return out


def matrix_extents(M: Mapping[str, Any]) -> list[tuple[str, list[tuple[float, float]], Any, Any]]:
    """Every DRAWN extent as (key, polygon, own_id, parent_id).

    DRAWN, not recorded. Several features store an ENVELOPE far larger than the ink inside it - a
    paddy field's smoothed `outline` bows well outside its plots, a grove's `poly` is a belt outline
    whose ink is its clumps, a commons `poly` surrounds a sparse grass scatter. A survey that
    compared envelopes reported 101 overlapping pairs pool-wide, roughly half of them artifacts of
    exactly that; a matrix built on envelopes would inherit those, cry wolf, and be switched off.
    So this reads what is actually inked, and permissive classes are not extracted at all.
    """
    out: list[tuple[str, list[tuple[float, float]], Any, Any]] = []
    for k, cls in OVERLAP_CLASS.items():
        if cls in _MATRIX_PERMISSIVE:
            continue
        rec = M.get(k)
        recs: list[Any] = [rec] if isinstance(rec, dict) and "x" in rec else (rec if isinstance(rec, list) else [])
        pfield = _MATRIX_PARENT_FIELD.get(k)
        if k == "wards":
            # the fence LINE at a hair's width: a fence is thin, and a generous stroke would
            # manufacture defects out of houses that merely front it
            for wd in recs:
                for q in _mx_stroke(wd.get("boundary") or [], 2.5):
                    out.append((k, q, None, None))
        elif k == "kido":
            # THE FULL DRAWN FOOTPRINT, AND IT IS TWO DIFFERENT THINGS (GM 2026-07-27: "in general
            # we always want overlap checks to use full footprints"). A ward gate is a roofed bar +
            # two posts + a guard box standing off to ONE flank, so no single centered w/h rect
            # describes it - and, carrying no w/h at all, it fell through every branch here and was
            # extracted as NOTHING. Classified, mounted, and completely invisible: a notice board
            # came to rest squarely on Nagahara's guard box with the gate green. That is the failure
            # _FIXTURE_MOUNTS was written to end, one level down - a mount list cannot help a
            # feature the extractor never reaches.
            #
            # The parts are then NOT interchangeable. The gateway (roof + posts) is a genuine
            # FIXTURE on the fence: the gate IS the opening, so it may stand on the ward line and on
            # the way it bars. The GUARD BOX is a small building on the verge beside it, and rides
            # no such permission - it is extracted as `kido_guard_box`, classed SOLID, so the matrix
            # forbids it against the fence, the roadbed and everything built. The GM's second
            # observation, same day: "ward gates seem to sometimes overlap with neighborhood walls".
            # They did - on oblique crossings, where the box sits along the lane and the fence does
            # not - and both cases were invisible because the whole gate rode the gateway's mount.
            #
            # `parts` is each drawn rect's ROTATED corner quad, recorded by the glyph itself, so
            # this is the ink and not a bounding box (the record also keeps `bbox`, which for a gate
            # at 45 degrees claims ~2x the ground the gate covers). All parts share ONE object id,
            # carried as both own-id and parent-id, so the existing annex-on-its-own-parent test
            # stops the pieces of one gate accusing each other; the key-tagged 3-tuple cannot
            # collide with another key's 2-tuple (x, y) id, so it excuses nothing but its own glyph.
            for o_ in recs:
                oid = (k, round(float(o_.get("x", 0)), 1), round(float(o_.get("y", 0)), 1))
                gq = [(round(float(q[0]), 1), round(float(q[1]), 1)) for q in (o_.get("guard") or [])]
                for qd in o_.get("parts") or []:
                    if len(qd) > 2:
                        poly = [(float(q[0]), float(q[1])) for q in qd]
                        is_guard = gq and [(round(a, 1), round(b, 1)) for a, b in poly] == gq
                        out.append(("kido_guard_box" if is_guard else k, poly, oid, oid))
        elif k in _MX_FIXTURE_BOX:
            # fixtures record their extent in their own vocabulary (a bridge stores span x deck-w, a
            # jetty a length, a sluice nothing at all), so each says how to read its drawn box
            for o_ in recs:
                bw, bh = _MX_FIXTURE_BOX[k](o_)
                out.append((k, _mx_rect({"x": o_["x"], "y": o_["y"], "w": bw, "h": bh, "rot": o_.get("rot", 0)}), (round(o_["x"], 1), round(o_["y"], 1)), None))
        elif k == "wells":
            for w_ in recs:
                r_ = float(w_.get("vr") or w_.get("r") or 8.0)
                out.append((k, [(w_["x"] + r_ * math.cos(i * math.pi / 6), w_["y"] + r_ * math.sin(i * math.pi / 6)) for i in range(12)], (round(w_["x"], 1), round(w_["y"], 1)), None))
        elif k == "pond":
            p_ = M.get("pond")
            if p_:
                out.append((k, [(p_[0] + p_[2] * math.cos(a_), p_[1] + p_[3] * math.sin(a_)) for a_ in [i * math.pi / 8 for i in range(16)]], None, None))
        elif k in ("road", "moat", "ring_road", "wall", "lane"):
            _w = {"road": float(M.get("road_width") or 30.0), "moat": float(M.get("moat_width") or 22.0), "ring_road": 20.0, "wall": 10.0, "lane": 6.0}[k]
            for q in _mx_stroke(M.get(k) or [], _w / 2):
                out.append((k, q, None, None))
        elif k == "torii":
            hw_, up_, dn_ = torii_halfbox(float(M.get("meta", {}).get("ftpx") or 1))
            for t_ in recs:
                if isinstance(t_, (list, tuple)) and len(t_) >= 2:
                    tx_, ty_ = float(t_[0]), float(t_[1])
                    out.append((k, [(tx_ - hw_, ty_ - up_), (tx_ + hw_, ty_ - up_), (tx_ + hw_, ty_ + dn_), (tx_ - hw_, ty_ + dn_)], None, None))
        elif k in _MX_LINE_W:
            for r2_ in recs:
                pl2 = r2_.get("poly") or r2_.get("pts")
                if not pl2:
                    continue  # pragma: no cover - defensive: every linear record carries a path
                par = r2_.get(pfield) if pfield else None
                for q in _mx_stroke(pl2, float(r2_.get("w") or _MX_LINE_W[k]) / 2):
                    out.append((k, q, None, par))
        else:
            for o_ in recs:
                if not isinstance(o_, dict):
                    continue  # pragma: no cover - defensive: classified keys store dicts
                par = o_.get(pfield) if pfield else None
                pid = tuple(par) if isinstance(par, list) else par
                if "x" in o_ and (o_.get("w") or o_.get("vw")):
                    out.append((k, _mx_rect(o_), (round(o_["x"], 1), round(o_["y"], 1)), pid))
                elif len(o_.get("poly") or o_.get("outline") or ()) > 2:
                    # POLYGON-ONLY records - a dry hatake plot stores `poly`/`crop`/`theta` and no
                    # x/w at all. An earlier cut of this extractor required x+w and so skipped every
                    # one of them SILENTLY, which made the very defect this feature exists to catch
                    # (a dry crop plot in a watercourse) disappear from its own dry run. A feature
                    # that is never extracted looks exactly like a feature with nothing wrong.
                    # `outline` is the same shape under another name (a flower bed's ring), and it
                    # cost exactly that silence until 2026-07-27.
                    out.append((k, [(q[0], q[1]) for q in (o_.get("poly") or o_["outline"])], None, pid))
    return out


class GridIndex:
    """A uniform-grid spatial index for the "what is near here?" queries several checks make
    THOUSANDS of times against the same features. Each item is inserted under every cell its
    influence bbox touches; a query returns only the items in the queried cell(s), which is a
    superset of the true neighbors, so the caller still runs its exact test - the index prunes,
    it never decides.

    WHY (profiled 2026-07-25, after a feature spent an hour and the gate was suspected): the
    naive form is a full scan per query, and two checks were doing exactly that.
    `city_fan_heads_quilted` tested each of ~3,000 canal-side sample points against EVERY plot
    polygon and ditch on the map - 14M segment-distance calls, ~58% of Tango's 17s gate.
    `structures_clear_of_trees` tested every structure against every drawn crown - 1,049 x 7,440
    on Tango. Both are point-vs-local-geometry questions, so pruning to the local cell is a pure
    constant-factor win with identical verdicts (the gate's whole regression corpus is replayed
    against the pre-index results to prove that).

    Cell size is the one tuning knob: too small wastes memory on cell lists, too large stops
    pruning. Pick it near the size of the features being indexed."""

    __slots__ = ("cell", "bins")

    def __init__(self, cell: float) -> None:
        self.cell = max(float(cell), 1.0)
        self.bins: dict[tuple[int, int], list[Any]] = {}

    def add(self, x0: float, y0: float, x1: float, y1: float, payload: Any) -> None:
        """Index `payload` under every cell its influence bbox touches."""
        c = self.cell
        for gx in range(int(x0 // c), int(x1 // c) + 1):
            for gy in range(int(y0 // c), int(y1 // c) + 1):
                self.bins.setdefault((gx, gy), []).append(payload)

    def near(self, x: float, y: float) -> list[Any]:
        """Candidates whose influence bbox may reach (x, y). Empty list when nothing is close."""
        return self.bins.get((int(x // self.cell), int(y // self.cell)), [])

    def near_rect(self, x0: float, y0: float, x1: float, y1: float) -> list[Any]:
        """Candidates near any part of a rect, de-duplicated by identity (an item spanning several
        of the queried cells is returned once)."""
        c = self.cell
        seen: dict[int, Any] = {}
        for gx in range(int(x0 // c), int(x1 // c) + 1):
            for gy in range(int(y0 // c), int(y1 // c) + 1):
                for it in self.bins.get((gx, gy), ()):
                    seen[id(it)] = it
        return list(seen.values())


def forest_reveal_x(forest: Poly, edge: Any, reveal: float, w: float) -> list[float]:
    """Mirror of settlement.forest_reveal_x (keep in sync): the x-values a canvas-filling FOREST
    contributes to the frame. The wood is drawn to the canvas edge, but the crop reveals only the
    tree line plus `reveal` px of canopy behind it - deeper in it is identical crowns, and holding
    the frame open for them is wasted image. This is the crop rule, so crop_hugs_content (which
    gates how tight the crop is) has to measure by exactly the same rule."""
    if not edge:
        return [min(max(p[0], 0), w) for p in forest]
    ex = [min(max(p[0], 0), w) for p in edge]
    return ex + [min(x + reveal, w) for x in ex]


def torii_halfbox(ftpx: float, span_ft: float = 16.0) -> tuple[float, float, float]:
    """Mirror of settlement.torii_halfbox (keep in sync): the true drawn half-extents (x half-width, y-up,
    y-down) of a torii glyph at scale `ftpx`, plus a small stroke pad. Replaces the legacy fixed x+/-19 /
    y-10..+18 box (the pre-true-scale 38px glyph, ~5x oversized), used to check torii sit within the frame."""
    s2 = (span_ft / ftpx) / 2
    pad = 2.0
    return s2 + pad, s2 * 7.0 / 19.0 + pad, s2 * 17.0 / 19.0 + pad


FOREST_REVEAL_FT = 110.0  # mirrors settlement.FOREST_REVEAL_FT - how deep the crop reveals a canvas-filling wood

# Mirrors settlement._CANOPY_STRUCT_KEYS (keep in sync): every ROOFED structure a tree may not be drawn on.
CANOPY_STRUCT_KEYS = (
    "houses",
    "farm_fixtures",
    "buildings",
    "storehouses",
    "flophouses",
    "byres",
    "farm_sheds",
    "religious",
    "shrines",
    "manors",
    "ministries",
    "inspection_stations",
    "merchant_estates",
    "fire_towers",
    "drum_towers",
    "breweries",
    "pawnshops",
    "bathhouses",
    "oil_presses",
    "kilns",
    "farriers",
    "mausoleums",
    "gate_structs",
    "wall_towers",
    "martial_halls",
    "dojos",
)

# Martial training in a provincial city (GM 2026-07-25). The first two mirror
# settlement.DOJO_SAMURAI_FRAC / DOJO_PER_SAMURAI - keep in sync, they are the roll the gate holds
# the map to. RANGE_FT is the kyudo standard 28 m shot (92 ft), rounded down to the ~90 ft clear
# lane the Mode A azuchi already uses. QUARTER_PX is "in or against the samurai neighborhood" at the
# city rung (3 ft/px -> ~780 real ft, about a quarter's width), not a precise siting rule.
DOJO_SAMURAI_FRAC = 0.10

DOJO_PER_SAMURAI = 200

DOJO_RANGE_FT = 90.0

DOJO_QUARTER_PX = 260.0


def poly_gap(a: Poly, b: Poly) -> float:
    """Minimum distance between two polygons; 0.0 if they overlap, touch, or one contains the other."""
    na, nb = len(a), len(b)
    if any(point_in_poly(x, y, b) for x, y in a) or any(point_in_poly(x, y, a) for x, y in b):
        return 0.0
    if any(segments_cross(a[i], a[(i + 1) % na], b[j], b[(j + 1) % nb]) for i in range(na) for j in range(nb)):
        return 0.0
    return min(min(poly_dist(x, y, b) for x, y in a), min(poly_dist(x, y, a) for x, y in b))


def edge_dist(px: float, py: float, poly: Poly) -> float:
    return min(seg_dist(px, py, poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly)))


def polyline_len(poly: Poly) -> float:
    return sum(math.hypot(poly[i + 1][0] - poly[i][0], poly[i + 1][1] - poly[i][1]) for i in range(len(poly) - 1))
