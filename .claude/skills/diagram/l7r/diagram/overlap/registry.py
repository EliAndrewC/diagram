"""The registry of what stands - the overlap matrix refused at record time (feature 287 M8, water W53).

WHY THIS EXISTS. The matrix (`matrix_policy` and the conditional permissions in `pair_permitted`) was read by one test
and no placer: a finished map was judged after the fact, and a feature a later stage drew over ground an earlier stage
had claimed was the shape that got through (R1, group 3). The plan's M8: "every footprint is recorded through one
indexed registry that answers 'may this kind lie on what is already here' by the matrix, and a placer offers only
candidates it admits."

SO EVERY FOOTPRINT IS RECORDED HERE, AND BY CONSTRUCTION RATHER THAN BY CALL SITE. The engine appends to the manifest
from some two hundred places (`s.M["houses"].append`, `s.M.setdefault("lanes", []).append`, a rebind of a filtered
copy); a registry each of them had to remember to call would be the per-site list that falls behind. The manifest is a
`StandingManifest` instead, and every list under a key the matrix tests is a `StandingList`: an append, an insert, an
item set or a rebind RECORDS, and a removal FORGETS. A record the matrix forbids on what already stands raises
`OverlapRefused` by name, before it is in the list - the backstop, so no violation is ever drawn. A placer asks
`admits(key, record)` first, so the raise does not fire in practice (`s.admits` on the settlement).

ONE PREDICATE. `element_extents` is the extractor `matrix_extents` reads a finished map with, per record, and
`pair_forbidden` is the pair test `matrix_violations` asks; the registry calls the same two. So the finished-map verdict
and the record-time verdict cannot disagree about a pair both see.

INDEXED, NEVER WALKED (the root CLAUDE.md's rule for an overlap check against the features already on the map). Each
extent is binned once, when it is recorded, in a uniform grid of `CELL` px; a question walks only the cells its own
extents cover, and the exact test (the separating axes) runs only on the pairs whose boxes meet.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Iterator, Mapping, Sequence
from typing import Any, SupportsIndex

from l7r.diagram.settlement._geom.indexes import Indexed
from l7r.diagram.settlement._geom.overlap import sat_overlap
from l7r.diagram.settlement._geom.walls import torii_halfbox

from .reserved import Reservations
from .taxonomy import (
    _MATRIX_PARENT_FIELD,
    _MATRIX_PERMISSIVE,
    _MX_FIXTURE_BOX,
    _MX_LINE_W,
    _MX_NOT_GEOMETRY,
    OVERLAP_CLASS,
    _mx_rect,
    _mx_same,
    _mx_stroke,
    matrix_policy,
)

Extent = tuple[str, list[tuple[float, float]], Any, Any]  # (key, drawn polygon, own id, parent id)
Box = tuple[float, float, float, float]

# Keys whose manifest value is ONE geometry rather than a list of records: the pond's ellipse, the road's polyline, the
# rampart's. A list under one of these keys is a polyline, so it is recorded whole and never element by element.
WHOLE_VALUE_KEYS = frozenset({"pond", "road", "moat", "ring_road", "wall", "lane"})

CELL = 120.0  # the index's cell, px - the grain `matrix_violations` has binned the finished map at since feature 017


def tested(key: str) -> bool:
    """Does the matrix test records under `key`? A permissive class (cover, vegetation, overlays, records), an
    unclassified key and bookkeeping that is not geometry are never extracted, so they are never recorded."""
    cls = OVERLAP_CLASS.get(key)
    return cls is not None and cls not in _MATRIX_PERMISSIVE and key not in _MX_NOT_GEOMETRY


def elements(key: str, value: Any) -> list[Any]:
    """The records under `key` the extractor reads one at a time: the whole value for a one-geometry key, the value itself
    for a single record stored as a dict, else the list's items."""
    if key in WHOLE_VALUE_KEYS:
        return [value] if value else []
    if isinstance(value, dict) and "x" in value:
        return [value]
    return list(value) if isinstance(value, list) else []


def element_extents(k: str, o: Any, M: Mapping[str, Any]) -> list[Extent]:
    """Every DRAWN extent of ONE record `o` under key `k`, as (key, polygon, own id, parent id).

    DRAWN, not recorded. Several features store an ENVELOPE far larger than the ink inside it - a paddy field's smoothed
    `outline` bows well outside its plots, a grove's `poly` is a belt outline whose ink is its clumps, a commons `poly`
    surrounds a sparse grass scatter. A survey that compared envelopes reported 101 overlapping pairs pool-wide, roughly
    half of them artifacts of exactly that; a matrix built on envelopes would inherit those, cry wolf, and be switched
    off. So this reads what is actually inked, and permissive classes are not extracted at all (`tested`). `M` supplies
    the widths a record does not carry (the road's, the moat's) and the scale a torii's box is drawn at."""
    out: list[Extent] = []
    pfield = _MATRIX_PARENT_FIELD.get(k)
    if k == "wards":
        # the fence LINE at a hair's width: a fence is thin, and a generous stroke would manufacture defects out of
        # houses that merely front it
        for q in _mx_stroke(o.get("boundary") or [], 2.5):
            out.append((k, q, None, None))
    elif k == "kido":
        # THE FULL DRAWN FOOTPRINT, AND IT IS TWO DIFFERENT THINGS (GM 2026-07-27: "in general we always want overlap
        # checks to use full footprints"). A ward gate is a roofed bar + two posts + a guard box standing off to ONE
        # flank, so no single centered w/h rect describes it - and, carrying no w/h at all, it fell through every branch
        # here and was extracted as NOTHING: a notice board came to rest squarely on Nagahara's guard box with the gate
        # green. The gateway (roof + posts) is a FIXTURE on the fence: the gate IS the opening, so it may stand on the
        # ward line and on the way it bars. The GUARD BOX is a small building on the verge beside it, extracted as
        # `kido_guard_box`, classed SOLID (the GM, same day: "ward gates seem to sometimes overlap with neighborhood
        # walls"). `parts` is each drawn rect's ROTATED corner quad, so this is the ink and not a bounding box. All parts
        # share ONE object id, carried as own-id and parent-id, so the annex-on-its-own-parent test stops the pieces of
        # one gate accusing each other; the key-tagged 3-tuple cannot collide with another key's (x, y) id.
        oid = (k, round(float(o.get("x", 0)), 1), round(float(o.get("y", 0)), 1))
        gq = [(round(float(q[0]), 1), round(float(q[1]), 1)) for q in (o.get("guard") or [])]
        for qd in o.get("parts") or []:
            if len(qd) > 2:
                poly = [(float(q[0]), float(q[1])) for q in qd]
                is_guard = gq and [(round(a, 1), round(b, 1)) for a, b in poly] == gq
                out.append(("kido_guard_box" if is_guard else k, poly, oid, oid))
    elif k in _MX_FIXTURE_BOX:
        # fixtures record their extent in their own vocabulary (a bridge stores span x deck-w, a jetty a length, a
        # sluice nothing at all), so each says how to read its drawn box
        bw, bh = _MX_FIXTURE_BOX[k](o)
        out.append((k, _mx_rect({"x": o["x"], "y": o["y"], "w": bw, "h": bh, "rot": o.get("rot", 0)}), (round(o["x"], 1), round(o["y"], 1)), None))
    elif k == "wells":
        r_ = float(o.get("vr") or o.get("r") or 8.0)
        out.append((k, [(o["x"] + r_ * math.cos(i * math.pi / 6), o["y"] + r_ * math.sin(i * math.pi / 6)) for i in range(12)], (round(o["x"], 1), round(o["y"], 1)), None))
    elif k == "pond":
        out.append((k, [(o[0] + o[2] * math.cos(a_), o[1] + o[3] * math.sin(a_)) for a_ in [i * math.pi / 8 for i in range(16)]], None, None))
    elif k in ("road", "moat", "ring_road", "wall", "lane"):
        _w = {"road": float(M.get("road_width") or 30.0), "moat": float(M.get("moat_width") or 22.0), "ring_road": 20.0, "wall": 10.0, "lane": 6.0}[k]
        for q in _mx_stroke(o or [], _w / 2):
            out.append((k, q, None, None))
    elif k == "torii":
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            hw_, up_, dn_ = torii_halfbox(float((M.get("meta") or {}).get("ftpx") or 1))
            tx_, ty_ = float(o[0]), float(o[1])
            out.append((k, [(tx_ - hw_, ty_ - up_), (tx_ + hw_, ty_ - up_), (tx_ + hw_, ty_ + dn_), (tx_ - hw_, ty_ + dn_)], None, None))
    elif k in _MX_LINE_W:
        pl2 = o.get("poly") or o.get("pts")
        if pl2:
            par = o.get(pfield) if pfield else None
            for q in _mx_stroke(pl2, float(o.get("w") or _MX_LINE_W[k]) / 2):
                out.append((k, q, None, par))
    elif isinstance(o, dict):
        par = o.get(pfield) if pfield else None
        pid = tuple(par) if isinstance(par, list) else par
        if "x" in o and (o.get("w") or o.get("vw")):
            out.append((k, _mx_rect(o), (round(o["x"], 1), round(o["y"], 1)), pid))
        elif len(o.get("poly") or o.get("outline") or ()) > 2:
            # POLYGON-ONLY records - a dry hatake plot stores `poly`/`crop`/`theta` and no x/w at all. An earlier cut of
            # this extractor required x+w and so skipped every one of them SILENTLY, which made the very defect this
            # feature exists to catch (a dry crop plot in a watercourse) disappear from its own dry run. `outline` is
            # the same shape under another name (a flower bed's ring), and it cost exactly that silence until 2026-07-27.
            out.append((k, [(q[0], q[1]) for q in (o.get("poly") or o["outline"])], None, pid))
    return out


def private_well(o: Any) -> tuple[float, float] | None:
    """A trade work's private well's id (it stands inside its own court), else None."""
    if isinstance(o, dict) and o.get("private") and "x" in o:
        return (round(o["x"], 1), round(o["y"], 1))
    return None


def pair_permitted(a: Extent, b: Extent, priv: Iterable[Any] | set[Any]) -> bool:
    """May the extents `a` and `b` overlap? The class policy (`matrix_policy`) and the permissions that depend on the two
    RECORDS rather than on their classes alone: an annex may lie on its own parent (and only its own), two annexes of
    one household may abut, and a trade work's private well stands inside its own court (`priv`, the private wells'
    ids). A channel reaching the field it feeds is a parent permission too (`field_ditches` names its field)."""
    ki, _pi, idi, pari = a
    kj, _pj, idj, parj = b
    if matrix_policy(ki, kj):
        return True
    if _mx_same(pari, idj) or _mx_same(parj, idi):
        return True  # an annex on its OWN parent
    if OVERLAP_CLASS.get(ki) == "ANNEX" and OVERLAP_CLASS.get(kj) == "ANNEX" and _mx_same(pari, parj):
        return True  # two annexes of one household
    return "wells" in (ki, kj) and (idi in priv or idj in priv)  # a trade work's own private well, inside its own court


def box_of(poly: Sequence[Sequence[float]]) -> Box:
    return (min(q[0] for q in poly), min(q[1] for q in poly), max(q[0] for q in poly), max(q[1] for q in poly))


def pair_forbidden(a: Extent, b: Extent, priv: Iterable[Any] | set[Any], box_a: Box | None = None, box_b: Box | None = None) -> bool:
    """THE predicate: do `a` and `b` overlap where the matrix forbids it? Permission first (cheap), then the boxes, then
    the separating axes (touching edges do not count)."""
    if pair_permitted(a, b, priv):
        return False
    ba = box_a or box_of(a[1])
    bb = box_b or box_of(b[1])
    if ba[2] < bb[0] or ba[0] > bb[2] or ba[3] < bb[1] or ba[1] > bb[3]:
        return False
    return sat_overlap(a[1], b[1])


class OverlapRefused(ValueError):
    """A record the matrix forbids on what already stands. The backstop: a placer asks `admits` first, so this names a
    placer that did not - the key being recorded, the key it would lie on, and where."""

    def __init__(self, key: str, other: str, at: tuple[float, float]) -> None:
        super().__init__(f"{key} would be recorded on a {other} at ({at[0]:.0f}, {at[1]:.0f}), which the overlap matrix forbids")
        self.key = key
        self.other = other
        self.at = at

    def __reduce__(self) -> tuple[Any, ...]:
        """Pickled by its three fields: a roll in a worker process raises it across the pool (`cohort`)."""
        return (OverlapRefused, (self.key, self.other, self.at))


class Standing:
    """What stands on the map, indexed as it is recorded: `record`, `forget`, and the one question `conflicts` (with
    `admits`, its yes/no). `M` is the manifest whose widths and scale the extractor reads (`element_extents`)."""

    def __init__(self, M: Mapping[str, Any], W: float = 4000.0, H: float = 4000.0) -> None:
        self.M = M
        self.W, self.H = float(W), float(H)
        self._bins: dict[tuple[int, int], list[int]] = {}
        self._ext: dict[int, tuple[Extent, Box, Box]] = {}  # entry id -> (extent, its box, its box clamped to the canvas)
        # (key, id(record)) -> (the record, its entry ids): held, so an id is never reused while it stands. Keyed by the key
        # too, because one object may stand under two keys (a shrine's hall is recorded under `religious` and `shrines`)
        self._held: dict[tuple[str, int], tuple[Any, list[int]]] = {}
        self.priv: set[Any] = set()
        self.strict = False  # raise on a forbidden record (`refuse`); the hamlet driver sets it
        self.reserved = Reservations()  # the corridors and wood seats the seating reserved (`reserved.py`)
        self._holds: set[tuple[str, int]] = set()  # parts held before they are drawn (`hold`): standing, though on no list
        self._next = 0

    def __len__(self) -> int:
        return len(self._held)

    # CLAMP THE INDEX BOX TO THE CANVAS (kept from `matrix_violations`, feature 017). A bin per 120 px of a feature
    # reaching far off-map costs a dict entry per cell in BOTH axes; a fixture planting a wall vertex at 9,000,000 on a
    # 3,200 px canvas was ~5.6 billion cells. The index only prunes, so clamping changes no verdict on the map.
    def _clamp(self, b: Box) -> Box:
        return (max(b[0], -self.W), max(b[1], -self.H), min(b[2], self.W * 2), min(b[3], self.H * 2))

    def _cells(self, cb: Box) -> Iterator[tuple[int, int]]:
        for gx in range(int(cb[0] // CELL), int(cb[2] // CELL) + 1):
            for gy in range(int(cb[1] // CELL), int(cb[3] // CELL) + 1):
                yield (gx, gy)

    def extents(self, key: str, o: Any) -> list[Extent]:
        return element_extents(key, o, self.M)

    def conflicts(self, key: str, o: Any, ignore: Any = None) -> list[tuple[str, str, float, float]]:
        """Every forbidden overlap recording `o` under `key` would make: (key, the standing key, x, y), empty when the
        matrix admits it. `ignore` is a record whose own extents do not count (the one `o` replaces)."""
        own = self.extents(key, o)
        if not own:
            return []
        priv = self.priv | ({pw} if (pw := private_well(o) if key == "wells" else None) else set())
        skip = set(self._held[(key, id(ignore))][1]) if ignore is not None and (key, id(ignore)) in self._held else set()
        out: list[tuple[str, str, float, float]] = []
        boxes = [box_of(e[1]) for e in own]
        for i, e in enumerate(own):
            b = boxes[i]
            for j in range(i + 1, len(own)):  # the record's own pieces against each other: the same rule as any pair
                if pair_forbidden(e, own[j], priv, b, boxes[j]):
                    out.append((key, own[j][0], *_center(e[1])))
            cb = self._clamp(b)
            if cb[2] < cb[0] or cb[3] < cb[1]:
                continue  # wholly off the canvas - nothing on the map can meet it
            seen: set[int] = set()
            for cell in self._cells(cb):
                for n in self._bins.get(cell, ()):
                    if n in seen or n in skip:
                        continue
                    seen.add(n)
                    other, ob, _ocb = self._ext[n]
                    if pair_forbidden(e, other, priv, b, ob):
                        out.append((e[0], other[0], *_center(e[1])))
        return out + self.reserved.conflicts(key, o, own)  # ...and the ground the seating reserved (`reserved.py`)

    def hold(self, key: str, rec: Any) -> Any:
        """Stand `rec` under `key` before it is drawn - a part the seating laid that a later stage draws (a household's well
        pocket, its fixtures), held so every way laid in between keeps off it as off a drawn one. Raises as `record`.
        `release` takes it down when the part itself is recorded."""
        self.record(key, rec)
        self._holds.add((key, id(rec)))
        return rec

    def release(self, key: str, rec: Any) -> None:
        self._holds.discard((key, id(rec)))
        self.forget(key, rec)

    def forbidding(self, key: str) -> list[Extent]:
        """Every standing extent the matrix forbids a record of `key` - one naming no parent - to lie on: the walls a
        router threads a new way between, read from the same predicate a record is refused by (`pair_permitted`)."""
        probe: Extent = (key, [], None, None)
        out = [e for e, _b, _cb in self._ext.values() if not pair_permitted(probe, e, self.priv)]
        if key == "lanes":  # ...and the reserved wood seats a way keeps its buffer off (`Reservations.seat_walls`)
            out += [("wood seat", w, None, None) for w in self.reserved.seat_walls()]
        return out

    def admits(self, key: str, o: Any, ignore: Any = None) -> bool:
        """May `o` be recorded under `key` on what already stands? The question every placer asks of its candidate."""
        return not self.conflicts(key, o, ignore)

    def record(self, key: str, o: Any) -> None:
        """Record `o` under `key`; raise `OverlapRefused` where the matrix forbids it on what already stands."""
        bad = self.conflicts(key, o)
        if bad:
            self.refuse(bad)
        self._add(key, o)

    def refuse(self, bad: Sequence[tuple[str, str, float, float]]) -> None:
        """Raise `OverlapRefused` for the first of `bad` - on a STRICT registry (`strict`), which a generator whose every
        placer asks the registry declares (the scripted hamlet, `hamletgen/driver.build`). Elsewhere the record stands as
        it always did: the town and city tiers' frozen hand-authored generators predate the registry and lay what the
        matrix forbids by design of their exhibits (the legacy pool's Kikuta, four such pairs), and their unit tests build
        those scenes; they are indexed all the same, so a placer there that asks `admits` is answered."""
        if not self.strict:
            return
        k, other, x, y = bad[0]
        raise OverlapRefused(k, other, (x, y))

    def kept(self, key: str, rec: Mapping[str, Any]) -> Kept:
        """`rec` as a record that keeps itself recorded: a later write to one of its drawn fields asks the registry first."""
        return Kept(self, key, rec)

    def _add(self, key: str, o: Any) -> None:
        ids: list[int] = []
        for e in self.extents(key, o):
            b = box_of(e[1])
            cb = self._clamp(b)
            n = self._next
            self._next += 1
            self._ext[n] = (e, b, cb)
            ids.append(n)
            if cb[2] < cb[0] or cb[3] < cb[1]:
                continue
            for cell in self._cells(cb):
                self._bins.setdefault(cell, []).append(n)
        prev = self._held.get((key, id(o)))
        self._held[(key, id(o))] = (o, (prev[1] if prev else []) + ids)
        if key == "wells" and (pw := private_well(o)):
            self.priv.add(pw)

    def forget(self, key: str, o: Any) -> None:
        """Take `o` off the map (a removal, a rebind, a record replaced)."""
        held = self._held.pop((key, id(o)), None)
        if held is None:
            return
        for n in held[1]:
            _e, _b, cb = self._ext.pop(n)
            if cb[2] < cb[0] or cb[3] < cb[1]:
                continue
            for cell in self._cells(cb):
                lst = self._bins.get(cell)
                if lst is not None:
                    lst.remove(n)
        if key == "wells" and (pw := private_well(o)):
            self.priv.discard(pw)

    def rerecord(self, key: str, o: Any) -> None:
        """`o` was reshaped in place: forget what it was and record what it is (the raise as `record`)."""
        held = self._held.get((key, id(o)))
        if held is not None and [self._ext[n][0] for n in held[1]] == self.extents(key, o):
            return  # nothing it covers moved
        self.forget(key, o)
        self.record(key, o)

    def resync(self) -> None:
        """THE BACKSTOP FOR A RECORD RESHAPED IN PLACE (a lane's `pts` rewritten, a brook's course rounded). A record held here
        is recorded as it stood when it landed; a stage that rewrites one without asking (`rerecord`) leaves the index
        stale. So at every stage's end (`hamletgen/driver.py`) and before a manifest is written (`finish`), every record on
        the manifest is compared with what is held: a record whose drawn extents moved is recorded again - and raises where
        the matrix forbids what it now covers - one no longer on the manifest is forgotten, and one that reached it by a
        list the manifest does not hold is recorded."""
        live: set[tuple[str, int]] = set()
        M = self.M
        for key in list(M.keys()):
            if not tested(key):
                continue
            for o in elements(key, M.get(key)):
                live.add((key, id(o)))
                self.rerecord(key, o)
        for k in [k for k in self._held if k not in live and k not in self._holds]:
            self.forget(k[0], self._held[k][0])


def _center(poly: Sequence[Sequence[float]]) -> tuple[float, float]:
    return (round(sum(q[0] for q in poly) / len(poly)), round(sum(q[1] for q in poly) / len(poly)))


#: How much wider than it will be drawn a stroked candidate is asked of the registry, in px: a placer stricter by a hair,
#: because the record rounds its points to 0.1 px after the question is asked (the `BAR_MARGIN_PX` convention of the seats).
PLACER_MARGIN_PX = 0.2


def forbidden_segment(M: Any, key: str, pts: Sequence[Sequence[float]], width: float, margin: float = PLACER_MARGIN_PX) -> int | None:
    """THE ONE QUESTION A LINEAR PLACER ASKS (a lane, a path): the first segment of a run along `pts`, drawn `width` wide
    under `key`, that the overlap matrix forbids on what stands on `M` (the settlement's `StandingManifest`); None where it
    admits every one, or where `M` carries no registry (a bare manifest)."""
    st = getattr(M, "standing", None)
    if st is None:
        return None
    for k in range(len(pts) - 1):
        seg = [[round(float(q[0]), 1), round(float(q[1]), 1)] for q in (pts[k], pts[k + 1])]
        if st.conflicts(key, {"pts": seg, "w": width + 2.0 * margin}):
            return k
    return None


class Kept(dict):  # type: ignore[type-arg]
    """A record that keeps itself recorded (`Standing.kept`): a write to a field its drawn extent is read from (`pts`,
    `poly`, `w`, ...) is asked of the registry first - the record as it would become, its own old extent aside - and
    refused by `OverlapRefused` where the matrix forbids it, leaving the record as it was; admitted, it is recorded again.
    So a stage that reshapes a lane in place is held at the write, not at the stage's end. A placer asks first:
    `s.admits(key, {**rec, "pts": new}, ignore=rec)`."""

    __slots__ = ("_key", "_standing")

    def __init__(self, standing: Standing, key: str, rec: Mapping[str, Any]) -> None:
        super().__init__(rec)
        self._standing = standing
        self._key = key

    def __reduce__(self) -> tuple[Any, ...]:
        return (dict, (dict(self),))

    def _held(self) -> bool:
        return (self._key, id(self)) in self._standing._held

    def __setitem__(self, k: str, v: Any) -> None:
        if k not in GEOMETRY_FIELDS or not self._held():
            super().__setitem__(k, v)
            return
        bad = self._standing.conflicts(self._key, {**self, k: v}, ignore=self)
        if bad:
            self._standing.refuse(bad)
        super().__setitem__(k, v)
        self._standing.forget(self._key, self)
        self._standing._add(self._key, self)

    def update(self, *args: Any, **kw: Any) -> None:  # type: ignore[override]
        for k, v in dict(*args, **kw).items():
            self[k] = v


#: The fields a record's drawn extent is read from (`element_extents`): a write to one moves what the record covers.
GEOMETRY_FIELDS = frozenset({"pts", "poly", "outline", "w", "h", "vw", "vh", "x", "y", "rot", "r", "vr", "parts", "boundary", "span", "len", "of", "field", "private"})


class StandingList(Indexed):
    """A manifest list whose every added record is recorded in the registry and every removed one forgotten. An
    `Indexed`, so the fit rules' versioned indexes keep working over it."""

    __slots__ = ("key", "standing")

    def __init__(self, standing: Standing, key: str, items: Iterable[Any] = ()) -> None:
        super().__init__()
        self.standing = standing
        self.key = key
        for it in items:
            self.append(it)

    def __reduce__(self) -> tuple[Any, ...]:
        """Pickled and copied as a plain `Indexed` over the same records: a registry is the live map's, never a copy's."""
        return (Indexed, (list(self),))

    def append(self, item: Any) -> None:
        self.standing.record(self.key, item)
        super().append(item)

    def extend(self, items: Any) -> None:
        for it in list(items):
            self.append(it)

    def insert(self, i: SupportsIndex, item: Any) -> None:
        self.standing.record(self.key, item)
        super().insert(i, item)

    def remove(self, item: Any) -> None:
        super().remove(item)
        self.standing.forget(self.key, item)

    def pop(self, i: SupportsIndex = -1) -> Any:
        item = super().pop(i)
        self.standing.forget(self.key, item)
        return item

    def clear(self) -> None:
        for it in self:
            self.standing.forget(self.key, it)
        super().clear()

    def __setitem__(self, i: Any, v: Any) -> None:
        old = self[i]
        olds = old if isinstance(i, slice) else [old]
        news = list(v) if isinstance(i, slice) else [v]
        for it in olds:
            self.standing.forget(self.key, it)
        done: list[Any] = []
        try:
            for it in news:
                self.standing.record(self.key, it)
                done.append(it)
        except OverlapRefused:
            for it in done:
                self.standing.forget(self.key, it)
            for it in olds:
                self.standing._add(self.key, it)
            raise
        super().__setitem__(i, news if isinstance(i, slice) else v)

    def __delitem__(self, i: Any) -> None:
        old = self[i]
        super().__delitem__(i)
        for it in old if isinstance(i, slice) else [old]:
            self.standing.forget(self.key, it)

    def __iadd__(self, other: Any) -> Any:  # type: ignore[misc]  # an in-place op on a subclass (see Indexed.__iadd__)
        self.extend(other)
        return self

    def __imul__(self, n: Any) -> Any:  # type: ignore[misc]  # see Indexed.__imul__
        self.extend(list(self) * (int(n) - 1) if int(n) > 0 else [])
        if int(n) <= 0:
            self.clear()
        return self


class StandingManifest(dict):  # type: ignore[type-arg]
    """The settlement's manifest with the registry under it: a value set under a key the matrix tests is recorded (a
    list becomes a `StandingList`, a one-geometry value is recorded whole), and the value it replaces is forgotten."""

    def __init__(self, standing: Standing, items: Mapping[str, Any] | None = None) -> None:
        super().__init__()
        self.standing = standing
        for k, v in (items or {}).items():
            self[k] = v

    def __reduce__(self) -> tuple[Any, ...]:
        """Pickled and copied as a plain dict: the registry is the live map's, never a copy's."""
        return (dict, (dict(self),))

    def _wrap(self, key: str, value: Any) -> Any:
        if not tested(key):
            return value
        if key in WHOLE_VALUE_KEYS:
            if value:
                self.standing.record(key, value)
            return value
        if isinstance(value, list) and not isinstance(value, StandingList):
            return StandingList(self.standing, key, value)
        if isinstance(value, dict) and "x" in value:
            self.standing.record(key, value)
        return value

    def _unwrap(self, key: str) -> None:
        if not tested(key) or key not in self:
            return
        for o in elements(key, dict.__getitem__(self, key)):
            self.standing.forget(key, o)

    def __setitem__(self, key: str, value: Any) -> None:
        old = self.get(key)
        self._unwrap(key)
        try:
            new = self._wrap(key, value)
        except OverlapRefused:
            if old is not None:
                for o in elements(key, old):
                    self.standing._add(key, o)
            raise
        super().__setitem__(key, new)

    def setdefault(self, key: str, default: Any = None) -> Any:
        if key not in self:
            self[key] = default
        return self[key]

    def update(self, *args: Any, **kw: Any) -> None:
        for k, v in dict(*args, **kw).items():
            self[k] = v

    def __delitem__(self, key: str) -> None:
        self._unwrap(key)
        super().__delitem__(key)

    def pop(self, key: str, *default: Any) -> Any:
        if key in self:
            self._unwrap(key)
        return super().pop(key, *default)
