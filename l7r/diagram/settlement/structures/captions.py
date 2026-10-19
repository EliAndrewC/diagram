"""The primitives a siter uses to ask whether a caption fits, and whether a footprint would land under one.

Split from settlement/structures.py by feature 114 - see settlement/structures/CLAUDE.md for the index.

Research: caption placement - CONVENTION: where and how a map caption is seated, and what it keeps clear of
"""

import math
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from l7r.diagram.interactive.tags import ClsTag
from l7r.diagram.overlap.taxonomy import _LABEL_GROUP

from ...labels import CIVIC_GROUPS, Obstacle, ObstacleIndex, Placement, Subject, Way, circle_obstacle, place, referent_box
from ...labels.geom import rect
from ...labels.standard import WEIGHT_OBSTACLE
from .._geom import (
    LAND,
    Poly,
    Pt,
    label_quad,
    label_tilt,
    linear_tilt,
    linear_tilt_full,
    torii_halfbox,
)
from ..finish import caption_record_box

# Ground cover and land parcels a caption may stand on - not blockers (see `label_blocker_quads`).
CAPTION_FEATURE_GAP = 4.0
"""How much bare ground a CAPTION owes any solid feature it is not naming, in px.

Four feet, the figure every other "these two inked things must read as separate" rule on these maps uses
(`_TOUCH_GAP` for a lane against a plot boundary, `FOOTPATH_FABRIC_GAP` for a tread against a fence). It is
not a structural clearance - nothing collides - it is a READING distance: two inked things a hair apart are
one object to a reader, and a caption that touches a roof names the roof.

MEASURED, on Kuwabata, 2026-09-12 (settlement-review): "notice board" came to rest with its lower corner
**0.02 px** above a byre's top edge and 38.7 ft from the board it names, and every check in the tree passed
it. Three separate tests had to be wrong at once for that, and they were, all in the same way - each asked
for an OVERLAP where the thing that matters is a DISTANCE: the seat probe (`boards.py` `_blocked`), the seat
picker's fallback when every seat is blocked (`_helpers.pick_caption_seat`), and - the one that actually
placed it - `pull_caption_toward`, which moves a caption half way toward its subject AFTER the seat has
been judged and refused the move only on `rects_overlap`. A pull is the last thing that touches the
position, so it is the one that had to hold the margin.
"""


LABEL_GROUND_KEYS = frozenset(
    {
        "commons",
        "marshes",
        "village_groves",
        "bamboo_stands",
        "groves",
        "pastures",
        "fields",
        "dry_plots",
        "wet_plots",
        "fallow_patches",
        "forest_patches",
        "flower_fields",
        "quarters",
        "districts",
        "clearings",
        "taxfree",
    }
)


def stroke_quad(a: Pt, b: Pt, half: float) -> Poly:
    """The drawn band of a stroke from `a` to `b` of half-width `half`, as a quad (a wall or moat run)."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / n * half, dx / n * half
    return [(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny), (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)]


def subject_ref(subject: Subject, p: Placement) -> tuple[float, float, float, float]:
    """The referent box a caption records (element [6]): the subject's box, or for a LINE subject the drawn road across
    from where the caption landed - the box `label_hugs_its_referent` measures the gap against. The placer's own
    `referent_box`, the one the hug is held to (feature 287, labels L10)."""
    return referent_box(subject, p.block)


def tree_crown_discs(M: Any) -> list[tuple[float, float, float]]:
    """Every DRAWN tree crown as (x, y, r): `tree_crowns`, the flat list the drawer writes as it paints, or - for a
    manifest with none recorded - the grove clumps at their nominal radius (see `fixtures.siting.canopy_index`, which
    files the same list for the board's siting)."""
    flat = M.get("tree_crowns") or []
    items = [(float(flat[i]), float(flat[i + 1]), float(flat[i + 2])) for i in range(0, len(flat) - 2, 3)]
    if not items:
        items = [(float(c[0]), float(c[1]), float(g.get("r") or 0.0)) for g in (M.get("village_groves") or []) if isinstance(g, dict) for c in (g.get("clumps") or [])]
    return items


def pending_caption_quad(payload: Sequence[Any]) -> Poly:
    """The drawn quad of a queued `text` caption (`label()`'s own payload), from the arithmetic `label()` will draw it by:
    its record box (`caption_record_box`, its fixed lines or the one line) turned by its tilt (feature 287, labels L4: a
    probe made at siting time sees every caption the label phase will draw before this one)."""
    x, y, text, size, anchor, _it, _wt, _co, _ref, rot, linear, full_tilt, _wrap, _cls, lines, angle = payload
    tilt = angle if angle is not None else ((linear_tilt_full(rot) if full_tilt else linear_tilt(rot)) if linear else label_tilt(rot))
    box = caption_record_box(text, list(lines) if lines else [text], x, y, size, anchor)
    return label_quad([*box, 0, text, None, tilt])


if TYPE_CHECKING:
    from ..core import Settlement


class CaptionProbesMixin:
    def label_blocker_quads(self: Settlement, skip_key: str | None = None) -> list[Poly]:  # type: ignore[misc]
        """Every FOOTPRINT a caption must miss, as its true rotated quad (the corner ring the glyph
        is drawn with) - the boxes, and what the wrap rule (`_caption_lines`,
        feature 133 T39) tests against, because a caption that clears a tilted house by a few feet
        clears the house, not its bounding box.

        GROUND IS NOT A BLOCKER (found under T39). The derived walk takes every recorded list of
        dicts with w/h, and on a hamlet that includes the scrub `commons` strips and the marsh - a
        canvas-sized rectangle each - so every caption on the sheet "overlapped" something, the wrap
        rule never fired, and every seat probe built on this list had been reporting blocked ground
        wherever the scrub is drawn, i.e. everywhere. A caption stands on scrub, grass, a grove or a
        paddy the way a name stands on a map; it must miss the BUILT things."""
        quads: list[Poly] = []
        for key, recs in self.M.items():
            if key == skip_key or key in LABEL_GROUND_KEYS or not isinstance(recs, list):
                continue
            for o in recs:
                if not (isinstance(o, dict) and all(isinstance(o.get(f), (int, float)) for f in ("x", "y", "w", "h"))):
                    continue
                a = math.radians(o.get("rot", 0) or 0)
                ca, sa = math.cos(a), math.sin(a)
                hw2, hh2 = o["w"] / 2, o["h"] / 2
                cs = ((-hw2, -hh2), (hw2, -hh2), (hw2, hh2), (-hw2, hh2))
                quads.append([(o["x"] + dx * ca - dy * sa, o["y"] + dx * sa + dy * ca) for dx, dy in cs])
        return quads

    def place_labels(self: Settlement) -> None:  # type: ignore[misc]
        """THE LABEL PHASE - the last phase of a settlement's generation (feature 157, GM 2026-08-29).

        *"add a phase at the very end of every settlement creation process, which is putting down the
        labels for things. Thus, after the final map feature is added, which on a hamlet is the notice
        board, there is a final phase in which we add labels for whatever map features get labels. This
        is because how we place labels will always depend on what else is on the map."*

        Nothing draws a caption before this runs: `label()` queues, and this drains. A `text` request is a
        caption whose seat its feature already computed (the unscripted tiers' hand seats, feature 266 D8);
        every other kind is SEATED here by the one placer (`l7r.diagram.labels`, feature 266), because the
        seat must see the finished map. A new labeled feature adds a row to `_PLACERS`, not a branch here.

        THE DRAIN ORDER is the queue's own call order, then the deferred `place_caption` seats, then
        the road caption - which is today's relative order preserved exactly, and it keeps the rule
        `finish()` used to state inline: the most-constrained caption is seated first and the road,
        which has by far the most room to move, yields last.

        PRIORITY IS DELIBERATELY NOT HERE. The GM described it and then ruled it out for this map:
        *"When we begin putting labels on maps that have many labels, we can assign a priority to each
        type of thing ... However, that will not apply here."* When a map does have competing labels,
        priority becomes one more key in front of the call-order sort in this function. That sentence
        is the extension point; building the scheme now would be building what was not asked for.

        IDEMPOTENT. The hamlet pipeline runs this as `stage_labels`; `finish()` runs it too, as the
        last thing it does, so a hand-authored gen with no stage pipeline gets the same phase with no
        change to the script. Whichever runs first drains the queue and the other does nothing."""
        if not self._labels_pending:
            return
        self._labels_pending = False  # ...so `label()` below reaches its body instead of re-queuing
        self._label_index: ObstacleIndex | None = None  # built on the first seated caption, from the map as it then stands
        queued, self._label_queue = self._label_queue, []
        for kind, payload in queued:
            getattr(self, self._PLACERS[kind])(*payload)
        for _tx, _subject, _sz, _it, _wt, _co in self._captions:
            self._draw_seated_caption(_tx, _subject, _sz, _it, _wt, _co, None)
        self._captions = []
        if getattr(self, "_road_label", None):
            self._finish_road_label()  # feature 145: the Imperial-road caption, a town/city feature, lives in structures/ground.py
            self._road_label: Any = None  # declared Any at structures/ground.py; re-declared for the checker (the attribute is conditional)

    # WHICH METHOD DRAWS EACH QUEUED KIND. An ordered-data row rather than a derived one (clause 14's
    # carve-out): it states a DECISION - that a kosatsuba's seat is searched in the phase while a
    # `text` caption's was fixed by its feature - which no introspection could recover.
    _PLACERS = {"text": "_draw_queued_label", "kosatsuba": "_draw_board_caption", "field_name": "_draw_field_name_label"}

    def _draw_seated_caption(  # type: ignore[misc]
        self: Settlement, text: str, subject: Subject, size: float, italic: bool, weight: str, color: str, cls: ClsTag, markup: bool = False
    ) -> Placement:
        """Seat one caption by the ONE placer (feature 266) and draw it, with its leader if it has one.

        The obstacle index is built once per phase, on the first seated caption, and each caption drawn is added to
        it so the next one keeps off it (FR-009). `markup` draws the field-name form (letter-spaced, a heavier halo)
        in place of `label()`'s; it is placed exactly the same way."""
        if self._label_index is None:
            self._label_index = self.label_obstacles()
        view = self.M["meta"].get("view")
        frame = (view[0], view[1], view[0] + view[2], view[1] + view[3]) if view else None
        return self._draw_placement(text, subject, place(text, size, subject, self._label_index, frame), size, italic, weight, color, cls, markup)

    def _draw_placement(  # type: ignore[misc]
        self: Settlement, text: str, subject: Subject, p: Placement, size: float, italic: bool, weight: str, color: str, cls: ClsTag, markup: bool = False
    ) -> Placement:
        """Draw one caption where the placer put it - its words and its leader - and add it to the phase's index.
        A caption whose seat was PROVED before the phase (the notice board's, labels L4) is drawn here verbatim."""
        if self._label_index is None:
            self._label_index = self.label_obstacles()
        ref = subject_ref(subject, p)
        if markup:
            z = self.add_label(
                f'<text x="{p.x:.0f}" y="{p.y:.0f}" text-anchor="middle" font-size="{size:g}" font-weight="bold" fill="#33301E" letter-spacing="1.5" paint-order="stroke" stroke="{LAND}" stroke-width="3.5">{text}</text>'
            )
            self._record_label(p.x, p.y, text, size, "middle", z, ref)
        else:
            self.label(p.x, p.y, text, size, italic=italic, weight=weight, color=color, ref=ref, cls=cls, lines=p.lines, angle=p.angle)
        if p.leader is not None:
            (x1, y1), (x2, y2) = p.leader
            self.add_label(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{max(0.6, 0.08 * size):.2f}" stroke-linecap="round"/>', cls=cls)
            self.M.setdefault("caption_leaders", []).append([round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1), text])
        self._label_index.add(Obstacle(p.block, WEIGHT_OBSTACLE))
        return p

    def label_obstacles(self: Settlement) -> ObstacleIndex:  # type: ignore[misc]
        """Everything on the finished map a caption is scored against (feature 266, FR-006, FR-014), indexed once.

        OBSTACLES (1,000): every built record (any manifest list of dicts with x, y, w, h - DERIVED, never hand-listed,
        because a hand-kept list goes stale - ground excepted), every radius fixture (a well, a persimmon), every torii
        arch, the wall and the moat, every caption already drawn and the title placard. Each built record carries its
        caption group (the overlap taxonomy's `_LABEL_GROUP`; a `buildings` record its own `kind` word) so a caption
        naming that group may lie on it, and a civic record with a name of its own is marked `named` (FR-014). WAYS
        (500 each): the lanes, the road, the streams and the drawn channels, at their drawn half-widths. Ground cover,
        fields and land parcels are free space and are not indexed at all."""
        obstacles: list[Obstacle] = []
        for key, recs in self.M.items():
            if key in LABEL_GROUND_KEYS or key == "labels" or not isinstance(recs, list):
                continue
            for o in recs:
                if not isinstance(o, dict) or not all(isinstance(o.get(f), (int, float)) for f in ("x", "y")):
                    continue
                if all(isinstance(o.get(f), (int, float)) for f in ("w", "h")):
                    w, h = float(o.get("vw") or o["w"]), float(o.get("vh") or o["h"])
                    poly = rect(float(o["x"]), float(o["y"]), w / 2, h / 2, float(o.get("rot") or 0.0))
                elif isinstance(o.get("vr") or o.get("r"), (int, float)):
                    r = float(o.get("vr") or o.get("r") or 0.0)
                    poly = rect(float(o["x"]), float(o["y"]), r, r)
                else:
                    continue
                group = _LABEL_GROUP.get(key) or (str(o.get("kind") or "").split("_")[0] or None if key == "buildings" else None)
                named = group in CIVIC_GROUPS and bool(o.get("name") or o.get("label"))
                obstacles.append(Obstacle(tuple(poly), WEIGHT_OBSTACLE, group, named))
        txh, tyu, tyd = torii_halfbox(self.ftpx)
        for t in self.M.get("torii") or []:
            obstacles.append(Obstacle(tuple(rect(float(t[0]), float(t[1]) + (tyd - tyu) / 2, txh, (tyu + tyd) / 2)), WEIGHT_OBSTACLE, "torii"))
        for ring_pts, half in self._defense_lines():
            for a, b in zip(ring_pts, ring_pts[1:], strict=False):
                obstacles.append(Obstacle(tuple(stroke_quad(a, b, half)), WEIGHT_OBSTACLE))
        obstacles += [Obstacle(tuple(label_quad(lb)), WEIGHT_OBSTACLE) for lb in self.M["labels"] if len(lb) > 3]
        # EVERY DRAWN TREE CROWN (feature 287, labels L7): a caption's halo biting a crown was judged only AFTER the placer
        # had chosen (`board_caption_level`), so the probed seat and the drawn one could differ. A crown is an obstacle
        # like a roof; a caption naming trees may lie on its own kind (the `grove` group)
        obstacles += [circle_obstacle(x, y, r, WEIGHT_OBSTACLE, "grove") for x, y, r in tree_crown_discs(self.M)]
        # ...AND EVERY CAPTION STILL QUEUED (feature 287, labels L4): a probe made before the label phase - the board's
        # siter - sees the fixed-seat captions and the proved board captions the phase will draw, so the seat it proves is
        # the seat the phase can draw. During the phase the queue has been drained into it, so this adds nothing there.
        for kind, payload in getattr(self, "_label_queue", []):
            if kind == "text":
                obstacles.append(Obstacle(tuple(pending_caption_quad(payload)), WEIGHT_OBSTACLE))
            elif kind == "kosatsuba" and len(payload) > 6 and payload[6] is not None:
                obstacles.append(Obstacle(payload[6].block, WEIGHT_OBSTACLE))
        if self.M.get("title"):
            x0, y0, x1, y1 = self.M["title"]["bbox"]
            obstacles.append(Obstacle(((x0, y0), (x1, y0), (x1, y1), (x0, y1)), WEIGHT_OBSTACLE))
        ways = [Way(tuple((float(a), float(b)) for a, b in ln["pts"]), float(ln.get("w") or 3) / 2) for ln in self.M.get("lanes") or [] if len(ln.get("pts") or []) >= 2]
        if len(self.M.get("road") or []) >= 2:
            ways.append(Way(tuple((float(p[0]), float(p[1])) for p in self.M["road"]), float(self.M.get("road_width") or 26) / 2))
        for st in self.M.get("streams") or []:
            if len(st.get("poly") or []) >= 2:
                ways.append(Way(tuple((float(p[0]), float(p[1])) for p in st["poly"]), float(st.get("w") or 9) / 2))
        for ch in self.M.get("drawn_channels") or []:
            if len(ch.get("pts") or []) >= 2:
                ways.append(Way(tuple((float(p[0]), float(p[1])) for p in ch["pts"]), float(ch.get("w") or 3) / 2))
        return ObstacleIndex(obstacles, ways)

    def _defense_lines(self: Settlement) -> list[tuple[list[Pt], float]]:  # type: ignore[misc]
        """The rampart and the moat as closed polylines with their drawn half-widths - obstacles a caption must not lie
        across (GM 2026-08-10: a caption on the wall reads as naming the defenses)."""
        out: list[tuple[list[Pt], float]] = []
        wall = self.M.get("wall") or []
        if len(wall) >= 3:
            out.append(([(float(p[0]), float(p[1])) for p in wall] + [(float(wall[0][0]), float(wall[0][1]))], 4.5))
        moat = self.M.get("moat") or []
        if len(moat) >= 3:
            out.append(([(float(p[0]), float(p[1])) for p in moat] + [(float(moat[0][0]), float(moat[0][1]))], float(self.M.get("moat_width", 22)) / 2))
        return out

    def field_name_label(self: Settlement, label: str, box: tuple[float, float, float, float]) -> None:  # type: ignore[misc]
        """Queue a FIELD-NAME caption - the big letter-spaced name a `water_field`
        lays across its own body (feature 157).

        It has its own `kind` because it is one of the two captions in the engine that do NOT go
        through `label()`: the markup carries `letter-spacing` and a 3.5 px halo that the caption
        primitive has no parameters for, and inventing them to route two dormant call sites through it
        would be changing the primitive to suit a caller. Queuing the exact markup instead keeps the
        phase's coverage STRUCTURAL - no caption is drawn outside it - without touching how these two
        would look if a map ever asked for them. The field is an AREA subject (feature 266): its name lies inside it,
        over its middle when that is free, placed by the one placer."""
        self._label_queue.append(("field_name", (label, box)))

    def _draw_field_name_label(self: Settlement, label: str, box: tuple[float, float, float, float]) -> None:  # type: ignore[misc]
        """Draw one queued field-name caption - the markup the field drawers used to emit inline, seated by the placer."""
        x0, y0, x1, y1 = box
        self._draw_seated_caption(label, Subject("area", ((x0, y0), (x1, y0), (x1, y1), (x0, y1))), 15, False, "bold", "#33301E", None, markup=True)

    def _draw_queued_label(  # type: ignore[misc]
        self: Settlement,
        x: float,
        y: float,
        text: str,
        size: float,
        anchor: str,
        italic: bool,
        weight: str,
        color: str,
        ref: Sequence[float],
        rot: float,
        linear: bool,
        full_tilt: bool,
        wrap: bool,
        cls: ClsTag,
        lines: Sequence[str] | None = None,
        angle: float | None = None,
    ) -> None:
        """Draw one queued `text` caption - `label()`'s own arguments, replayed with the phase open. A hand-seated
        caption changes the map under the placer's index, so the index is rebuilt at the next seated caption."""
        self._label_index: ObstacleIndex | None = None
        self.label(x, y, text, size, anchor, italic, weight, color, ref=ref, rot=rot, linear=linear, full_tilt=full_tilt, wrap=wrap, cls=cls, lines=lines, angle=angle)

    def discard_queued_label(self: Settlement, kind: str) -> None:  # type: ignore[misc]
        """Drop the most recent queued caption of `kind` - the UNDO for a feature that was placed and
        then withdrawn (feature 157).

        `hamletgen.stage_notice` re-seats a board the frame cannot hold, and it used to have to pop the
        board's record, blank its glyph, hunt the finished caption out of `M['labels']` by its text and
        blank that too. With the caption still queued there is nothing drawn to hunt: the request is
        dropped and the re-seated board queues its own. That simplification is the phase paying for
        itself - the orphan-caption bug it replaces (feature 133 T48) could not have existed."""
        for i in range(len(self._label_queue) - 1, -1, -1):
            if self._label_queue[i][0] == kind:
                del self._label_queue[i]
                return
