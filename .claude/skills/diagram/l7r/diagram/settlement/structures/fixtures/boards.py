"""Split from settlement/structures/fixtures.py by feature 173 - see this package's CLAUDE.md for the index."""

from typing import TYPE_CHECKING

from ....labels import Subject
from ....labels.geom import rect
from ..._geom import label_tilt, tilt_caption_seat
from ..._knobs import KOSATSUBA_MARKER_MIN_PX

if TYPE_CHECKING:
    from ...core import Settlement


class BoardsMixin:
    def fire_tower(self: Settlement, x: float, y: float, tw: float | None = None, rot: float = 0.0, label: str = "fire tower") -> int:  # type: ignore[misc]
        """A HINOMI-YAGURA (fire-watch tower): a tall, slender braced-timber tower with a lookout
        platform and an alarm bell (hansho), standing in the dense COMMONER quarter of a walled
        town or city where packed wooden rooftops make fire catastrophic. It is a CIVILIAN interior
        structure - the magistrate's fire-watch - distinct from a wall guard tower (military, on the
        rampart): drawn as an OPEN braced frame (not the guard tower's solid block) with a red bell.
        The watchman strikes the bell in a cadence that tells the town how near the fire is. Records
        M['fire_towers'] (an overlap-checked struct: it must stand clear of the wall, roads, and
        buildings) and reserves a small no-build block (it needs clear sightlines). Place it among the
        laborer/merchant blocks. See the research/cities/fabric.html 'How did a dense wooden city watch for fire?' historical grounding."""
        if tw is None:
            tw = self.px(26)  # a real hinomi-yagura frame is ~26 ft square (town-calibrated glyph)
        h = tw / 2
        g = [f'<g transform="translate({x:.0f},{y:.0f}) rotate({rot:.1f})">']
        g.append(f'<rect x="{-h - 2:.0f}" y="{-h - 5:.0f}" width="{tw + 4}" height="5" rx="1" fill="#7A5A30"/>')  # the little roof cap over the lookout platform
        g.append(f'<rect x="{-h:.0f}" y="{-h:.0f}" width="{tw}" height="{tw}" fill="#EFE6CC" fill-opacity="0.45" stroke="#7A5A30" stroke-width="2"/>')  # the open braced-timber frame
        g.append(f'<line x1="{-h:.0f}" y1="{-h:.0f}" x2="{h:.0f}" y2="{h:.0f}" stroke="#7A5A30" stroke-width="1.1"/>')  # cross-braces (an X)
        g.append(f'<line x1="{h:.0f}" y1="{-h:.0f}" x2="{-h:.0f}" y2="{h:.0f}" stroke="#7A5A30" stroke-width="1.1"/>')
        g.append(f'<circle cx="0" cy="0" r="{tw * 0.2:.1f}" fill="#B0462F" stroke="#5A3F1E" stroke-width="0.8"/>')  # the alarm bell (hansho)
        g.append('</g>')
        z = self.add_top(''.join(g))
        self.M["fire_towers"].append({"x": round(x, 1), "y": round(y, 1), "w": tw, "h": tw, "rot": round(rot, 1), "z": z, "label": label})
        self.placed.append((x, y, tw, tw))
        bm = 16
        self.block_polys.append([(x - h - bm, y - h - bm), (x + h + bm, y - h - bm), (x + h + bm, y + h + bm), (x - h - bm, y + h + bm)])
        if label:
            _t = label_tilt(rot)
            _lx, _ly = tilt_caption_seat(x, y, rot, _t, h, h, 14) if _t else (x, y + h + 14)
            self.label(_lx, _ly, label, 9, italic=True, color="#7A5A30", rot=_t)
        return z

    def kosatsuba(self: Settlement, x: float, y: float, rot: float = 0.0, label: str = "notice board") -> int:  # type: ignore[misc]
        """The KOSATSUBA - the settlement's official notice board: a small roofed frame posting
        the state's STANDING LAW (edicts, porter/packhorse rate tables, ban lists). Sited at the
        most TRAFFICKED public point - the highway frontage, the main street by the gate, a
        bridgehead or market corner - because it is the state talking at everyone who passes
        (Edo's principal board stood at Nihonbashi, the bridgehead). NEVER defaulted to the
        magistrate's manor gate: the manor's own board (Mode A program, buildings.md) posts the
        bench's OUTPUT (verdicts, bounties) for people who come to court, and the manor sits at
        the settlement edge where feet do not pass. True size ~12x5 ft (a 7x3 ft board under a
        small roof); the label carries the read.

        `rot` IS THE ROAD'S BEARING, not a free choice. The glyph's long axis is the board's
        FACE, so a board must stand square to the way it fronts - broadside to the traffic that
        reads it. Turned perpendicular, the face goes edge-on to everyone approaching and the
        institution fails while the siting checks stay green (that is exactly how Nagahara's
        third board shipped, GM 2026-07-27). Hand placements must pass the fronted route's
        bearing; `place_kosatsuba` derives it. Held by `kosatsuba_faces_the_road`. Records M['kosatsuba'] (an overlap-checked
        struct). WHY: research/urban-features.html 'The notice board (kosatsuba) - siting is a traffic decision'. Place LAST, on a clear verge
        beside the road, like the fire tower.

        The DRAWN glyph is a LOCATION MARKER at the coarse tiers (GM call 2026-07-24, taking the
        escape research/urban-features.html 'The notice board (kosatsuba)' documents): the true 12x5 ft frame draws 6x2.5 px at village grain
        and 4x1.7 px at city grain - at city scale, rotated upright, that is a 1.7 px sliver that
        reads as gate hardware, not a feature (Nagahara: two of its three boards were invisible
        until the GM went looking, and the one that read did so only by its label). So the glyph
        is floored at KOSATSUBA_MARKER_MIN_PX on its long axis with the 12:5 aspect preserved -
        the wells' doctrine exactly (SKILL.md 'to scale'): the marker denotes the board's
        TO-SCALE LOCATION with legible pixels that are not themselves claimed to be to scale. The
        floor NEVER shrinks a board, so hamlets and towns (1 ft/px) still draw the true 12x5 px;
        only village and city grain lift. The manifest keeps the TRUE w/h (so a size audit reads
        real feet) and records the drawn box as vw/vh, which is what the overlap checks and the
        placement reservation use - the pixels that can actually collide."""
        w, h = self.px(12), self.px(5)
        k = max(1.0, KOSATSUBA_MARKER_MIN_PX / w)  # marker floor, aspect preserved
        vw, vh = w * k, h * k
        hw, hh = vw / 2, vh / 2
        g = [f'<g transform="translate({x:.0f},{y:.0f}) rotate({rot:.1f})">']
        g.append(f'<rect x="{-hw:.1f}" y="{-hh:.1f}" width="{vw:.1f}" height="{vh:.1f}" rx="1" fill="#7A5A30" stroke="#5A3F1E" stroke-width="0.8"/>')  # the little tiled roof, seen from above
        g.append(f'<line x1="{-hw:.1f}" y1="0" x2="{hw:.1f}" y2="0" stroke="#EFE6CC" stroke-width="0.9"/>')  # the ridge
        g.append('</g>')
        z = self.add_top(''.join(g), cls="notice board")
        self.M["kosatsuba"].append({"x": round(x, 1), "y": round(y, 1), "w": w, "h": h, "vw": round(vw, 1), "vh": round(vh, 1), "rot": round(rot, 1), "z": z, "label": label})
        self.placed.append((x, y, vw, vh))
        bm = 6
        self.block_polys.append([(x - hw - bm, y - hh - bm), (x + hw + bm, y - hh - bm), (x + hw + bm, y + hh + bm), (x - hw - bm, y + hh + bm)])
        if label:
            # THE BOARD IS PLACED HERE; ITS CAPTION IS SEATED IN THE LABEL PHASE (feature 157, GM
            # 2026-08-29: *"moving label placement so that the notice board itself is placed during a
            # separate phase than the labels for the map are placed"*). Unlike a `text` caption, whose
            # feature has already chosen its seat, a board's seat is SEARCHED - so the search has to
            # run when the map is finished, not when the plank goes in.
            self._label_queue.append(("kosatsuba", (x, y, rot, vw, vh, label)))
        return z

    def _draw_board_caption(self: Settlement, x: float, y: float, rot: float, vw: float, vh: float, label: str) -> None:  # type: ignore[misc]
        """Seat and draw one notice board's caption, in the LABEL PHASE (feature 157), by the ONE placer (feature 266).

        The board is a POINT subject: its drawn, rotated footprint and its angle. Everything else - the ranked side,
        the preferred gap off the board's edge, the angle (the board's own, upright; the GM's 2026-08-27 ruling), the
        line breaks, and a leader if the caption cannot stand directly beside it - is the cartographic standard's,
        decided in `l7r.diagram.labels` (research/presentation, "Where does a caption sit"). The 560-line search that
        stood here, with its own annulus, ladder, lane target and half-way pull, is gone with the hand-built rules it
        encoded."""
        subject = Subject("point", tuple(rect(x, y, vw / 2, vh / 2, rot)), angle=rot)
        self._draw_seated_caption(label, subject, 8, True, "normal", "#7A5A30", "notice board")  # the caption shares the board's class (feature 134 FR-006)
