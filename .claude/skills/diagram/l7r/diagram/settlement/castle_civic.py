"""Split from settlement.py by feature 025 - see settlement/CLAUDE.md for the index."""

import math
import random
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, cast

from ..labels import Subject
from ..labels.geom import rect
from ._geom import (
    GOVERNOR_CAPTION_FS,
    Poly,
    Pt,
    organic_bbox,
    organic_poly,
    point_in_poly,
    seg_closest,
    seg_dist,
    segments_cross,
    smooth_closed,
    smooth_points,
    torii_halfbox,
)

if TYPE_CHECKING:
    from .core import Settlement


class CastleCivicMixin:
    # ---- the DAIMYO'S CASTLE (feature 019) ---------------------------------------------------

    def castle(  # type: ignore[misc]
        self: Settlement,
        x: float,
        y: float,
        w: float,
        h: float,
        label: str = "Castle",
        gate_dir: str = "south",
        moat_gap: float | None = None,
        moat_width: float | None = None,
        baileys: bool = False,
        bailey_fracs: tuple[float, ...] = (0.64, 0.34),
        label_xy: Pt | None = None,
        karamete_dir: str | None = None,
    ) -> Any:
        """A domain capital's castle, drawn as an ENCEINTE and BLANK INSIDE.

        THE INTERIOR IS EMPTY AND THAT IS NOT A SIMPLIFICATION TO BE FIXED LATER (GM 2026-08-08).
        No building may ever be drawn in here - not the tenshu, not the goten, not the granary or
        the armory - because the castle is the subject of its own Mode A sheet, and ANY interior
        detail on this map becomes a constraint that sheet must later match, with nothing enforcing
        the match. The two would drift silently and the map would end up asserting something the
        compound plan contradicts. In the GM's words: "I'd rather nothing be shown than the WRONG
        thing be shown." An empty court asserts nothing and can never be wrong. The same doctrine
        governs `manor` and `governor_mansion`; see research/cities/capitals.html, "Why is the castle drawn blank inside?".

        WHAT IS DRAWN, AND WHY THE KEEP IS NOT AMONG IT. A castle reads as a castle from its WORKS,
        never from its keep: at a capital's 3 ft/px a tenshu footprint is just another building box
        (Hirosaki's is ~0.6 ha - 1.2% of its castle), so drawing it would be both illegible and a
        sync liability. What carries the read is the enceinte, its moat, the bailey divisions and
        the dogleg gate approach.

        BAILEYS AND MASUGATA ARE OFF BY DEFAULT - the GM's experiment was RUN AND ANSWERED
        (`baileys=`, GM 2026-08-08: "let's try adding the bailey walls and masugata dogleg gate
        approaches and whatnot and then see how that looks, and we can remove them if needed").

        THE VERDICT, from two rendered attempts: they do not make a 50 ha enclosure read as a
        castle, and the reason generalizes. The first cut drew the wards CONCENTRIC and it read as
        a bullseye. The second offset them toward the far side from the ote-mon, varied the wall
        weights and enlarged the masugata until it was visible - a real improvement, and still
        nested rectangles. **Rectangles inside rectangles read as ABSTRACTION however they are
        arranged**: what makes a castle read is irregular ward outlines, substantial water between
        the wards, and corner yagura, none of which survive being drawn walls-only at 3 ft/px.
        So the internal works buy nothing and cost a Mode A sync surface, and the blank rule wins
        on its own terms. The knob stays because the finding is about THIS drawing vocabulary, not
        a law - a future castle with irregular wards could revisit it.

        What DID survive the experiment is the ISHIGAKI DOUBLING on the outer enceinte (below):
        a battered stone rampart drawn as a doubled line reads as mass where a single stroke reads
        as a fence. That is the outer wall, so it adds no sync surface the wall did not already
        have.

        `bailey_fracs` are the inner enclosures as a fraction of the enceinte, outermost first
        (default: ninomaru at 0.64, honmaru at 0.34). Each bailey's gate turns 90 degrees from its
        parent's, which IS the dogleg: an attacker through the ote-mon must turn twice under fire
        rather than run straight at the keep. A `masugata` box stands outside the main gate - the
        square barbican that makes the first of those turns.

        RESERVES ITS GROUND IN BOTH REGISTRIES, deliberately (see CLAUDE.md, "DRAW ORDER" and
        "CENTER vs FOOTPRINT"): `block_polys` is CENTER-tested by the urban packs, `placed` is
        distance-tested. An enclosure this size - roughly 85% of an entire provincial city - has to
        stop a wide building hanging half its roof over the rampart, and only the second registry
        does that. Records M['castle']."""
        hw, hh = w / 2, h / 2
        wall = "#2D2A24"
        gap = self.px(60) if moat_gap is None else moat_gap  # a castle moat stands ~60 ft off the wall foot
        mw = self.px(80) if moat_width is None else moat_width  # ~80 ft: wider than the city's own ~66 ft moat
        ww = max(self.px(6), 3.0)  # an ishigaki rampart is far heavier than a manor's ~2 ft dobei
        gg = max(self.px(22) / 2, 3.0)  # the ote-mon passes ~22 real ft - a formal castle gate
        gp = max(self.px(4), 3.0)

        def ring(rx: float, ry: float) -> list[Pt]:
            return [(x - rx, y - ry), (x + rx, y - ry), (x + rx, y + ry), (x - rx, y + ry)]

        # 1. THE MOAT, routed through the shared water groups so a feeder merges into it cleanly
        mo = ring(hw + gap, hh + gap)
        dd = "M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in mo) + " Z"
        self._water(
            f'<path d="{dd}" fill="none" stroke="#9CB4C8" stroke-width="{mw:.0f}" stroke-linejoin="round"/>',
            {},
            sheen=f'<path d="{dd}" fill="none" stroke="#B6CAD8" stroke-width="{mw * 0.4:.0f}" stroke-linejoin="round"/>',
        )

        def walled_rect(cx: float, cy: float, rx: float, ry: float, gdir: str, weight: float = 1.0, gdir2: str | None = None) -> Pt:
            """One enclosure: four wall runs with a gap in the `gdir` side (and in `gdir2`, when
            the enclosure keeps a rear gate). Returns the main gate center.

            Takes its own CENTER, because a castle's wards are OFFSET rather than concentric - see
            the bailey block below for why that is the whole difference between a fortress and a
            bullseye."""
            sw = ww * weight
            open_dirs = {gdir} | ({gdir2} if gdir2 else set())
            sides = {
                "north": ((cx - rx, cy - ry), (cx + rx, cy - ry), (cx, cy - ry)),
                "south": ((cx - rx, cy + ry), (cx + rx, cy + ry), (cx, cy + ry)),
                "west": ((cx - rx, cy - ry), (cx - rx, cy + ry), (cx - rx, cy)),
                "east": ((cx + rx, cy - ry), (cx + rx, cy + ry), (cx + rx, cy)),
            }
            for name, (pa, pb, (gx, gy)) in sides.items():
                if name not in open_dirs:
                    self.add_wall(f'<line x1="{pa[0]:.0f}" y1="{pa[1]:.0f}" x2="{pb[0]:.0f}" y2="{pb[1]:.0f}" stroke="{wall}" stroke-width="{sw:.1f}"/>')
                elif name in ("west", "east"):
                    self.add_wall(f'<line x1="{pa[0]:.0f}" y1="{pa[1]:.0f}" x2="{pa[0]:.0f}" y2="{gy - gg:.1f}" stroke="{wall}" stroke-width="{sw:.1f}"/>')
                    self.add_wall(f'<line x1="{pb[0]:.0f}" y1="{gy + gg:.1f}" x2="{pb[0]:.0f}" y2="{pb[1]:.0f}" stroke="{wall}" stroke-width="{sw:.1f}"/>')
                    for py in (gy - gg, gy + gg):
                        self.add_wall(f'<rect x="{gx - gp / 2:.1f}" y="{py - gp / 2:.1f}" width="{gp:.1f}" height="{gp:.1f}" fill="{wall}"/>')
                else:
                    self.add_wall(f'<line x1="{pa[0]:.0f}" y1="{pa[1]:.0f}" x2="{gx - gg:.1f}" y2="{pa[1]:.0f}" stroke="{wall}" stroke-width="{sw:.1f}"/>')
                    self.add_wall(f'<line x1="{gx + gg:.1f}" y1="{pb[1]:.0f}" x2="{pb[0]:.0f}" y2="{pb[1]:.0f}" stroke="{wall}" stroke-width="{sw:.1f}"/>')
                    for px_ in (gx - gg, gx + gg):
                        self.add_wall(f'<rect x="{px_ - gp / 2:.1f}" y="{gy - gp / 2:.1f}" width="{gp:.1f}" height="{gp:.1f}" fill="{wall}"/>')
            return sides[gdir][2]

        # 2. the court ground, then the enceinte. The ISHIGAKI draws as a DOUBLED line - a battered
        # stone rampart reads as mass, where a single stroke reads as a fence.
        self.add(f'<rect x="{x - hw:.0f}" y="{y - hh:.0f}" width="{w:.0f}" height="{h:.0f}" fill="#E3D6B2"/>')
        inb = ww * 1.9
        self.add(f'<rect x="{x - hw + inb:.0f}" y="{y - hh + inb:.0f}" width="{w - 2 * inb:.0f}" height="{h - 2 * inb:.0f}" fill="none" stroke="{wall}" stroke-width="{ww * 0.32:.1f}" opacity="0.5"/>')
        gate = walled_rect(x, y, hw, hh, gate_dir, gdir2=karamete_dir)

        # CORNER YAGURA. The city rampart carries a mural tower every bowshot; a castle drawn with a
        # bare unarticulated line therefore asserts that the daimyo's fortress is the WEAKER work,
        # which is the biggest single reason a blank enceinte reads as a picture frame rather than a
        # fortress (settlement-review, 2026-08-09). These are OUTER-wall furniture, in exactly the
        # position the ishigaki doubling occupies: they add no Mode A sync surface the wall did not
        # already have, which is why they survive the bailey verdict that removed the internal works.
        yw, yh = self.px(62), self.px(40)
        for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            tx, ty = x + sx * (hw - yw / 2), y + sy * (hh - yh / 2)
            self.add_wall(f'<rect x="{tx - yw / 2:.1f}" y="{ty - yh / 2:.1f}" width="{yw:.1f}" height="{yh:.1f}" fill="#B9A882" stroke="{wall}" stroke-width="{ww * 0.6:.1f}"/>')
            self.M.setdefault("castle_towers", []).append({"x": round(tx, 1), "y": round(ty, 1), "w": round(yw, 1), "h": round(yh, 1), "kind": "yagura"})
        # A GATE TOWER MUST READ AS A GATE (GM 2026-08-10: "I would have expected to just see
        # gates at the castle keep... these look kind of like guard towers"). It IS a gate - a
        # YAGURA-MON, the gatehouse with a turret built over its passage, which is the standard
        # Japanese castle gate; the corner works are sumi-yagura, and the ishigaki carries a
        # walkway behind its hei parapet, which is why a castle needs far fewer towers than a
        # European curtain wall. The DRAWING was the problem: a gate tower was the same plain
        # rectangle as a corner turret, so nothing said "you pass through here". It now carries
        # the passage - a gap in the tower's footprint on the wall's axis, with the jambs drawn
        # heavier - so the eye reads a gatehouse straddling an opening.
        gtw, gth = self.px(88), self.px(52)
        _gx0, _gy0 = gate[0] - gtw / 2, gate[1] - gth / 2
        _horiz = abs(gate[1] - y) > abs(gate[0] - x)  # a gate on the N or S face: passage runs in y
        self.add_wall(f'<rect x="{_gx0:.1f}" y="{_gy0:.1f}" width="{gtw:.1f}" height="{gth:.1f}" fill="#B9A882" stroke="{wall}" stroke-width="{ww * 0.75:.1f}"/>')
        _pw = (gtw if _horiz else gth) * 0.34  # the passage, a third of the gatehouse's span
        if _horiz:
            self.add_wall(f'<rect x="{gate[0] - _pw / 2:.1f}" y="{_gy0:.1f}" width="{_pw:.1f}" height="{gth:.1f}" fill="#E3D6B2" stroke="{wall}" stroke-width="{ww * 0.5:.1f}"/>')
        else:
            self.add_wall(f'<rect x="{_gx0:.1f}" y="{gate[1] - _pw / 2:.1f}" width="{gtw:.1f}" height="{_pw:.1f}" fill="#E3D6B2" stroke="{wall}" stroke-width="{ww * 0.5:.1f}"/>')
        self.M.setdefault("castle_towers", []).append({"x": round(gate[0], 1), "y": round(gate[1], 1), "w": round(gtw, 1), "h": round(gth, 1), "kind": "gate_tower"})
        # THE KARAMETE-MON (GM 2026-08-09, researched): the ote-mon/karamete-mon pair is the
        # STANDARD gate program - main gate south by aspect divination, rear gate opposite - and
        # the pairing is military doctrine: the garrison sorties from the rear gate to trap an
        # attacker held at the front. Its tower draws a size down from the ote-mon's, as a rear
        # gate should. research/cities/capitals.html, "A castle has TWO gates".
        karamete: Pt | None = None
        if karamete_dir:
            karamete = {"north": (x, y - hh), "south": (x, y + hh), "west": (x - hw, y), "east": (x + hw, y)}[karamete_dir]
            ktw, kth = self.px(64), self.px(40)
            if karamete_dir in ("west", "east"):
                ktw, kth = kth, ktw
            self.add_wall(f'<rect x="{karamete[0] - ktw / 2:.1f}" y="{karamete[1] - kth / 2:.1f}" width="{ktw:.1f}" height="{kth:.1f}" fill="#B9A882" stroke="{wall}" stroke-width="{ww * 0.75:.1f}"/>')
            self.M.setdefault("castle_towers", []).append({"x": round(karamete[0], 1), "y": round(karamete[1], 1), "w": round(ktw, 1), "h": round(kth, 1), "kind": "gate_tower"})

        # 3. THE BAILEYS - provisional, and OFFSET rather than concentric, which is the entire
        # difference between a castle and a bullseye. The first cut drew them centered and
        # axis-shared and it read as a target symbol; real wards are asymmetric, and the honmaru
        # sits at the FAR side from the ote-mon so an attacker crosses the whole works under fire.
        # Each ward's gate also turns off its parent's, so the route doglegs at every wall.
        turn = {"south": "east", "east": "north", "north": "west", "west": "south"}
        away = {"south": (0.0, -1.0), "north": (0.0, 1.0), "east": (-1.0, 0.0), "west": (1.0, 0.0)}[gate_dir]
        rings: list[list[Pt]] = []
        gates: list[Pt] = [(round(gate[0], 1), round(gate[1], 1))]
        cx_, cy_, prx, pry = x, y, hw, hh
        if baileys:
            gdir = gate_dir
            for k, frac in enumerate(bailey_fracs):
                gdir = turn[gdir]
                rx_, ry_ = hw * frac, hh * frac
                jog = 0.13 * (1 if k % 2 == 0 else -1)
                cx_ = x + away[0] * (prx - rx_) * 0.72 + (jog * hw if away[0] == 0 else 0.0)
                cy_ = y + away[1] * (pry - ry_) * 0.72 + (jog * hh if away[1] == 0 else 0.0)
                rings.append([(cx_ - rx_, cy_ - ry_), (cx_ + rx_, cy_ - ry_), (cx_ + rx_, cy_ + ry_), (cx_ - rx_, cy_ + ry_)])
                g_ = walled_rect(cx_, cy_, rx_, ry_, gdir, weight=0.85 if k == 0 else 0.72)
                gates.append((round(g_[0], 1), round(g_[1], 1)))
                prx, pry = rx_, ry_
            # 4. the INNER moat, hugging the honmaru at its own offset center
            ir = gap * 0.42
            inner = [(cx_ - prx - ir, cy_ - pry - ir), (cx_ + prx + ir, cy_ - pry - ir), (cx_ + prx + ir, cy_ + pry + ir), (cx_ - prx - ir, cy_ + pry + ir)]
            idd = "M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in inner) + " Z"
            self._water(f'<path d="{idd}" fill="none" stroke="#9CB4C8" stroke-width="{mw * 0.5:.0f}" stroke-linejoin="round"/>', {})
            # 5. THE MASUGATA - the square barbican that makes the first turn. Sized to READ: the
            # first cut was ~2.4 gate-widths and vanished at map scale, which is the same mistake as
            # drawing a keep footprint - a feature nobody can see is not a feature.
            ux, uy = {"south": (0.0, 1.0), "north": (0.0, -1.0), "east": (1.0, 0.0), "west": (-1.0, 0.0)}[gate_dir]
            bs = gg * 4.2
            bx, by = gate[0] + ux * bs, gate[1] + uy * bs
            bc = [(bx - bs, by - bs), (bx + bs, by - bs), (bx + bs, by + bs), (bx - bs, by + bs)]
            open_side = 1 if ux == 0 else 0  # one flank stays open: the way out turns ACROSS the approach
            for i in range(4):
                if i == open_side:
                    continue
                a_, b_ = bc[i], bc[(i + 1) % 4]
                self.add_wall(f'<line x1="{a_[0]:.0f}" y1="{a_[1]:.0f}" x2="{b_[0]:.0f}" y2="{b_[1]:.0f}" stroke="{wall}" stroke-width="{ww * 0.85:.1f}"/>')

        # RECORDED AS A LIST, not a bare dict. `every_feature_classified_for_overlap` enumerates
        # manifest keys whose value is a non-empty LIST of dicts, so a dict-shaped record is skipped
        # silently - which left the largest structure this project draws invisible to the overlap
        # matrix, to solid_structs(), and to every hazard row. That is how the Imperial road came to
        # run straight through this castle with a green gate (settlement-review, 2026-08-09).
        rec = {
            "x": x,
            "y": y,
            "w": w,
            "h": h,
            "label": label,
            "gate": list(gate),
            "gate_dir": gate_dir,
            "gates": [list(g) for g in gates],
            "moat": [[round(px, 1), round(py, 1)] for px, py in mo],
            "moat_width": round(mw, 1),
            "baileys": [[[round(px, 1), round(py, 1)] for px, py in r] for r in rings],
            "wall_w": round(ww, 2),
            "gate_w": round(2 * gg, 2),
        }
        if karamete is not None and karamete_dir:  # karamete exists only when karamete_dir was given (above); the second test is the narrowing a checker can see
            rec["karamete"] = [round(karamete[0], 1), round(karamete[1], 1)]
            rec["karamete_dir"] = karamete_dir
        # BOTH registries - see the docstring. The reservation covers the MOAT too: nothing builds
        # on the water, and the packs must flow around the whole works rather than the wall alone.
        m = gap + mw / 2 + max(36 * self.bscale, 26)
        self.block_polys.append([(x - hw - m, y - hh - m), (x + hw + m, y - hh - m), (x + hw + m, y + hh + m), (x - hw - m, y + hh + m)])
        self.placed.append((x, y, w + 2 * m, h + 2 * m))
        if label:
            lx, ly = label_xy if label_xy else (x, y)
            self.label(lx, ly, label, GOVERNOR_CAPTION_FS + 2, weight="bold")
        self.M.setdefault("castles", []).append(rec)
        return rec

    def ministry(self: Settlement, x: float, y: float, name: str, w: Any = None, h: Any = None, label_below: bool | None = None, label_inside: bool = False) -> None:  # type: ignore[misc]
        """A provincial ministry office (one of the SIX). Records to M['ministries'] with its
        `name`; exactly one city-wide must be the Ministry of Rites (sited in the temple
        neighborhood). Official violet roof so it reads apart from housing/commerce."""
        if w is None:
            w, h = self.px(224), self.px(148)  # a ministry office compound ~224x148 ft (was 88px at the 0.42-grain city)
        self.add(f'<rect x="{x - w / 2:.0f}" y="{y - h / 2:.0f}" width="{w}" height="{h}" rx="2" fill="#BCA6C4" stroke="#463653" stroke-width="2"/>')
        self.add(f'<rect x="{x - w / 2:.0f}" y="{y - h / 2:.0f}" width="{w}" height="9" fill="#6A4A78"/>')
        self.add(f'<line x1="{x - w * 0.3:.0f}" y1="{y:.0f}" x2="{x + w * 0.3:.0f}" y2="{y:.0f}" stroke="#463653" stroke-width="0.7" opacity="0.6"/>')
        self.M["ministries"].append({"x": x, "y": y, "w": w, "h": h, "name": name})
        self.placed.append((x, y, w, h))
        bm = max(30 * self.bscale, 26)  # a building-half margin at the map's grain, floored so a dwelling's corner keeps the 14px office-abut clearance
        self.block_polys.append([(x - w / 2 - bm, y - h / 2 - bm), (x + w / 2 + bm, y - h / 2 - bm), (x + w / 2 + bm, y + h / 2 + bm), (x - w / 2 - bm, y + h / 2 + bm)])
        if label_inside:
            # THE CAPITAL'S MINISTRY CAPTIONS SIT ON THE GLYPH (GM 2026-08-09) - the estate rule
            # applied to the state offices: the capital's 224x148 ft compound has the room, where
            # a provincial city's tighter fabric keeps the caption beside the box. Two stacked
            # lines, because "Ministry of Retainers" cannot fit the width in one: the shared
            # "Ministry of" runs small above the department's own name. Near-black for
            # legibility on the violet, per the GM.
            dept = name.removeprefix("Ministry of ").strip()
            if dept != name:
                self.label(x, y - h * 0.10, "Ministry of", 6.5, italic=True, color="#2D2A24")
                self.label(x, y + h * 0.18, dept, max(7.0, min(9.5, (w * 0.8) / (max(len(dept), 1) * 0.55))), weight="bold", color="#2D2A24")
            else:
                self.label(x, y + h * 0.05, name, max(6.5, min(9.0, (w * 0.8) / (max(len(name), 1) * 0.55))), weight="bold", color="#2D2A24")
        else:
            if label_below is None:
                label_below = self._label_hits(x, y - h / 2 - 9, name, 9) > self._label_hits(x, y + h / 2 + 11, name, 9)
            self.label(x, y + h / 2 + 11 if label_below else y - h / 2 - 9, name, 9, italic=True, color="#463653")

    # ---- martial training: the state hall and the private dojos (GM 2026-07-25) ---------------
    # A DOJO IS A CITY INSTITUTION. The county tier draws a practice ground and no dojo at all
    # (buildings.md, "A dojo is a city institution; county training is courtyard keiko"): a county
    # town holds ~20 resident samurai, which is no student body and no living for a sensei, and the
    # rural anchors agree - an Edo daikansho/jin'ya had no bugeijo in its program and a Chinese
    # county yamen had no training hall at all. The PROVINCIAL CITY is the first tier that supports
    # one, and it supports two KINDS, which is why there are two glyphs here:
    #
    #   martial_hall  the STATE institution - the martial wing of the provincial school, where the
    #                 province's samurai youth are schooled and the officer cohort drills. Exactly
    #                 ONE per provincial city, always. Historically the hanko's bugeijo, and hanko
    #                 were built IN CASTLE TOWNS for the domain's own retainers - so the tier that
    #                 seats a governor and ~225 working samurai is the tier that seats the hall.
    #   dojo          a PRIVATE machi-dojo, a retired sensei or noted duelist teaching a named
    #                 style out of a hall in the samurai quarter. COUNT ROLLS from the samurai
    #                 cohort (see `dojos`).
    #
    # The two share a FORM (a long plank-floored hall with a kamiza head + a training yard with
    # striking posts) and split on COLOR: state violet, the same family as the ministries, vs the
    # ordinary building tan of a private establishment in a residential quarter.
    DOJO_SAMURAI_FRAC = 0.10  # a provincial city is ~10% samurai (budgets.md: ~300 of ~3,000)
    DOJO_PER_SAMURAI = (
        200  # GM formula 2026-07-25: 1 private dojo per 200 samurai + a remainder roll (research/cities/government.html "Martial training is an urban institution" - the roll wins over the rough read)
    )

    def _dojo_hall(self: Settlement, g: list[str], x0: float, y0: float, w: float, h: float, fill: str, edge: str, head: str) -> None:  # type: ignore[misc]
        """The shared DOJO HALL glyph: a long rectangle with a plank-floor grain running lengthwise
        and the KAMIZA (the head of the hall, where the shrine alcove sits and students bow in)
        marked as a band across the short end. The plank grain is what says 'sprung wooden floor'
        rather than 'another shophouse' at a glance - the one interior feature a top-down dojo has."""
        g.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{h:.1f}" rx="1.5" fill="{fill}" stroke="{edge}" stroke-width="1.6"/>')
        g.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{max(w * 0.13, 2.6):.1f}" height="{h:.1f}" fill="{head}" opacity="0.9"/>')  # the kamiza end
        for pi in range(1, 4):  # the plank-floor grain, lengthwise
            py = y0 + h * pi / 4
            g.append(f'<line x1="{x0 + 1.2:.1f}" y1="{py:.1f}" x2="{x0 + w - 1.2:.1f}" y2="{py:.1f}" stroke="{edge}" stroke-width="0.55" opacity="0.5"/>')

    def _keiko_gear(self: Settlement, g: list[str], rack: tuple[float, float], posts: Sequence[tuple[float, float]], edge: str) -> None:  # type: ignore[misc]
        """The training yard's durable equipment - a WEAPON RACK and the kenjutsu striking posts
        (tategi). Both are sub-glyph at city scale (a rack is ~8x2 real ft = under 3px at 3 ft/px),
        so they follow the Mode A stroke convention and draw as LOCATION MARKERS at a fixed legible
        size rather than to scale. What makes a training ground read as ESTABLISHED is the gear
        practice leaves behind, so the markers carry more meaning than their footprint does."""
        g.append(f'<line x1="{rack[0]:.1f}" y1="{rack[1]:.1f}" x2="{rack[0] + 5.0:.1f}" y2="{rack[1]:.1f}" stroke="{edge}" stroke-width="2.0" stroke-linecap="round"/>')
        for px_, py_ in posts:
            g.append(f'<circle cx="{px_:.1f}" cy="{py_:.1f}" r="1.7" fill="none" stroke="{edge}" stroke-width="1.1"/>')

    def martial_hall(self: Settlement, x: float, y: float, rot: float = 0.0, label: str = "martial hall", label_below: bool | None = None, label_xy: Pt | None = None) -> None:  # type: ignore[misc]
        """The PROVINCIAL MARTIAL HALL - the state training institution, one per provincial city.

        REAL FEET (the sizes are researched, not chosen for legibility - see research/cities/government.html 'Martial training is an urban institution'
        "Historical grounding: martial training in a provincial city"). The compound is sized to its
        PROGRAM rather than rounded up: the lane sets the width and the hall-plus-lane sets the
        depth, and everything else is circulation.
          - the hall              60 x 36 ft = 2,160 sqft = 120 tatami (a mat is 3 x 6 ft). At the
                                  ~90-135 sqft per drilling samurai that buildings.md already
                                  established for the county practice ground, that floor holds
                                  ~20 pairs at once - the officer cohort plus a school class
          - the sensei's house    40 x 24 ft, a modest samurai dwelling (compare the 56 x 40 ft
                                  junior samurai city house)
          - the archery lane      100 x 26 ft of swept ground with an AZUCHI (earthen butt) at the
                                  far end. 100 ft covers the kyudo standard 28 m / 92 ft shooting
                                  distance - the same ~90 ft clear lane the Mode A azuchi uses
          - the walled compound   130 x 100 ft (13,000 sqft, ~0.30 acre) = lane + butt + wall
                                  margins across, hall + lane + circulation deep. Well BELOW a
                                  ministry office compound (224 x 148 ft), which is right: a
                                  ministry is a bureau of clerks and archives, this is one hall and
                                  a yard
        The lane is INSIDE the compound wall: the hall's whole point is that the province's youth
        train in one enclosed place, and an unwalled shooting lane in a city street is a hazard.
        Records M['martial_halls'] with its lane length in real feet (city_has_martial_hall,
        city_martial_hall_has_archery_range)."""
        f = self.px
        cw, ch = f(130) / 2, f(100) / 2
        g = [f'<g transform="translate({x:.0f},{y:.0f}) rotate({rot:.1f})">']
        g.append(f'<rect x="{-cw:.1f}" y="{-ch:.1f}" width="{cw * 2:.1f}" height="{ch * 2:.1f}" rx="2" fill="#E7E1EC" stroke="#463653" stroke-width="1.7"/>')
        ly0, ly1 = f(12), f(38)  # the archery lane's south band
        lx0, lx1 = -cw + f(7), -cw + f(107)
        g.append(f'<rect x="{lx0:.1f}" y="{ly0:.1f}" width="{lx1 - lx0:.1f}" height="{ly1 - ly0:.1f}" fill="#E3D9BE" stroke="#B9A57C" stroke-width="0.8"/>')
        g.append(f'<line x1="{lx0 + f(6):.1f}" y1="{ly0:.1f}" x2="{lx0 + f(6):.1f}" y2="{ly1:.1f}" stroke="#8A7448" stroke-width="0.8"/>')  # the shooting line
        g.append(f'<rect x="{lx1:.1f}" y="{ly0:.1f}" width="{f(10):.1f}" height="{ly1 - ly0:.1f}" rx="1" fill="#A98C58" stroke="#6B5228" stroke-width="1.1"/>')  # the azuchi butt
        self._dojo_hall(g, -cw + f(7), -ch + f(6), f(60), f(36), "#CDBBD6", "#463653", "#6A4A78")
        g.append(f'<rect x="{f(10):.1f}" y="{-ch + f(6):.1f}" width="{f(40):.1f}" height="{f(24):.1f}" rx="1.5" fill="#DDB87A" stroke="#5A3F1E" stroke-width="1.4"/>')  # the sensei's house
        self._keiko_gear(g, (-cw + f(10), 0.0), [(-cw + f(32), f(3)), (-cw + f(44), f(3))], "#463653")
        g.append('</g>')
        self.add(''.join(g))
        self.M.setdefault("martial_halls", []).append(
            {"x": round(x, 1), "y": round(y, 1), "w": round(f(130), 1), "h": round(f(100), 1), "rot": round(rot, 1), "label": label, "range_ft": round((lx1 - lx0) * self.ftpx, 1)}
        )
        self.placed.append((x, y, f(130), f(100)))
        # a modest stand-clear apron (14px, the office-abut clearance), NOT the ministries' 26: the
        # hall is not a government office for city_government_offices_dont_abut, and a samurai ward
        # is packed tightly enough that every px of apron costs a house it must not spend
        bm = max(30 * self.bscale, 14)
        self.block_polys.append([(x - cw - bm, y - ch - bm), (x + cw + bm, y - ch - bm), (x + cw + bm, y + ch + bm), (x - cw - bm, y + ch + bm)])
        # THE CAPTION IS WHAT BINDS, not the compound. "martial hall" is ~70px of italic text
        # against a 43x33px footprint at the city rung, so in a ward packed to its space budget the
        # hall very often fits somewhere its caption does not. Two escapes, in order: auto-pick the
        # emptier SIDE the way s.ministry does (a below-caption on a hall seated beside the yamen
        # lands squarely on the governor's mansion), and if neither side is clear, let the gen hand
        # the caption a `label_xy` in a nearby pocket - the same move Tango makes for the governor's
        # own caption. Either way the band the caption takes is reserved so a later pack cannot
        # slide a house under the text (labels_clear_of_other_buildings).
        if label_below is None:
            label_below = self._label_hits(x, y - ch - 9, label, 9) > self._label_hits(x, y + ch + 11, label, 9)
        lx_, ly_ = label_xy if label_xy else (x, y + ch + 11 if label_below else y - ch - 9)
        bw_ = max(cw + bm, 2.9 * len(label) + 10)
        by_ = ly_ - 11 if label_xy else (y + ch if label_below else y - ch - 26)
        self.block_polys.append([(lx_ - bw_, by_), (lx_ + bw_, by_), (lx_ + bw_, by_ + 26), (lx_ - bw_, by_ + 26)])
        self.label(lx_, ly_, label, 9, italic=True, color="#463653")

    def hanko(  # type: ignore[misc]
        self: Settlement, x: float, y: float, rot: float = 0.0, label: str = "Domain School", label_below: bool | None = None, label_xy: Pt | None = None, w_ft: float = 400, h_ft: float = 260
    ) -> None:
        """THE DOMAIN SCHOOL (hanko) - the capital's state school, and the parent institution of
        the provincial martial hall (GM asked 2026-08-09 which glyph the school takes; the answer
        is both-in-one, because that is what a hanko WAS).

        WHY THIS GLYPH AND NOT A MINISTRY BOX. The hanko is not a bureau of clerks - it is the
        school samurai families across the domain send their children to, and the historical
        hanko was a school of LETTERS with a martial wing (bugeijo) on the same grounds: Aizu's
        Nisshinkan, Mito's Kodokan and Kagoshima's Zoshikan all pair lecture halls with fencing
        floors and a shooting range. The provincial martial hall this engine already draws IS
        that martial wing at the tier below (cities/government.md, "Historical grounding: martial
        training"); the capital shows the whole institution. So the compound takes the
        martial-hall vocabulary - state violet, hall + kamiza, archery lane - plus the civil
        lecture hall that outranks them.

        REAL FEET (GM size audit 2026-08-09): compound 400 x 260 ft = ~1 ha (~3,000 tsubo) -
        the attested hanko band runs from Choshu's FIRST Meirinkan at 940 tsubo (0.31 ha, 1718)
        to Aizu's Nisshinkan at 2.65 ha and the rebuilt Meirinkan's 5 ha, so ~1 ha is a solid
        mid-band school for a ~200k-koku-class domain whose capital is the schooling magnet
        (research/cities/capitals.html) without claiming Nisshinkan's fame. Inside: civil lecture hall 76 x 44 ft
        (the LARGER wing - a hanko is first a school of letters); bugeijo 60 x 36 ft with kamiza
        and plank grain (the provincial hall's own 120-tatami floor); a 100 ft archery lane with
        azuchi along the south band (the kyudo 92 ft shot); the rest courts and circulation -
        a school's ground is mostly yard, exactly like a yamen's. Records M['martial_halls']
        with kind='hanko' - the same family the checks read - and blocks placement with the
        government-office apron."""
        f = self.px
        cw, ch = f(w_ft) / 2, f(h_ft) / 2
        g = [f'<g transform="translate({x:.0f},{y:.0f}) rotate({rot:.1f})">']
        g.append(f'<rect x="{-cw:.1f}" y="{-ch:.1f}" width="{cw * 2:.1f}" height="{ch * 2:.1f}" rx="2" fill="#E7E1EC" stroke="#463653" stroke-width="1.7"/>')
        # INTERIOR BLANK (GM 2026-08-09): a real hanko is building-DENSE - Aizu's Nisshinkan
        # packed lecture halls, dormitories, a swimming pond and an observatory into 2.6 ha -
        # so a faithful interior is a dozen buildings, and that belongs to the school's own
        # Mode A sheet. The earlier two-hall-and-lane sketch was neither honest nor blank; the
        # same sync doctrine as the castle and the estates applies (nothing shown beats the
        # wrong thing shown), and the caption moves inside the court like an estate's.
        g.append("</g>")
        self.add("".join(g))
        self.M.setdefault("martial_halls", []).append({"x": round(x, 1), "y": round(y, 1), "w": round(f(w_ft), 1), "h": round(f(h_ft), 1), "rot": round(rot, 1), "label": label, "kind": "hanko"})
        self.placed.append((x, y, f(w_ft), f(h_ft)))
        bm = max(30 * self.bscale, 26)  # a government school keeps the full office apron, unlike the packed-ward hall
        self.block_polys.append([(x - cw - bm, y - ch - bm), (x + cw + bm, y - ch - bm), (x + cw + bm, y + ch + bm), (x - cw - bm, y + ch + bm)])
        # the caption sits INSIDE the blank court, two lines, like an estate's
        _hw2 = str(label).split()
        if len(_hw2) >= 2:
            _htop, _hbot = " ".join(_hw2[:-1]), _hw2[-1]
            _hfs = max(7.0, min(12.0, (cw * 2 * 0.8) / (max(len(_htop), len(_hbot), 1) * 0.55)))
            self.label(x, y - ch * 0.22, _htop, _hfs, weight="bold", color="#463653")
            self.label(x, y + ch * 0.30, _hbot, _hfs, weight="bold", color="#463653")
        else:
            self.label(x, y, label, 10, weight="bold", color="#463653")

    def dojo(self: Settlement, x: float, y: float, rot: float = 0.0, label: str = "dojo") -> None:  # type: ignore[misc]
        """A PRIVATE DOJO (machi-dojo) in the samurai quarter.

        REAL FEET: the lot is 76 x 44 ft (~3,300 sqft) - a walled establishment about the size of a
        senior samurai's house - holding a 44 x 24 ft hall (1,056 sqft = ~59 tatami) and a training
        yard with a weapon rack and two striking posts. 59 mats is the LOW end of the Edo town-dojo
        band on purpose: the famous commercial dojos were a bakumatsu, million-person-city
        phenomenon, and a provincial seat of ~3,000 has not had that boom. NO archery lane - there
        is no room for a 92 ft shot on a 76 ft lot, and the butt is the state hall's to keep.
        Records M['dojos'] (city_dojo_count_follows_samurai, city_dojos_among_samurai)."""
        f = self.px
        lw, lh = f(76) / 2, f(44) / 2
        g = [f'<g transform="translate({x:.0f},{y:.0f}) rotate({rot:.1f})">']
        g.append(f'<rect x="{-lw:.1f}" y="{-lh:.1f}" width="{lw * 2:.1f}" height="{lh * 2:.1f}" rx="1.5" fill="#EFE7D2" stroke="#5A4326" stroke-width="1.3"/>')
        self._dojo_hall(g, -lw + f(3), -lh + f(3), f(44), f(24), "#D9C8A4", "#5A4326", "#8A6B42")
        self._keiko_gear(g, (-lw + f(6), lh - f(6)), [(f(14), f(2)), (f(24), f(2))], "#5A4326")
        g.append('</g>')
        self.add(''.join(g))
        self._trade_record("dojos", x, y, f(76), f(44), rot, label)

    def dojos(self: Settlement, seats: Sequence[tuple[float, float]], count: int | None = None) -> int:  # type: ignore[misc]
        """Place the city's PRIVATE dojos, COUNT ROLLED FROM THE SAMURAI COHORT (GM formula
        2026-07-25, the bathhouse pattern applied to a samurai-driven institution): ONE dojo per
        full 200 samurai, plus a chance of one EXTRA equal to the remainder fraction. A provincial
        city of 3,000 is ~10% samurai = ~300, so it keeps 1 guaranteed + a 50% roll; a 4,000 seat
        (~400 samurai) keeps exactly 2. Floored at 1 - the private tail is never empty at this tier.

        WHY THE SAMURAI COUNT AND NOT THE POPULATION: a dojo serves samurai and nobody else, so the
        cohort is the causal driver; the city's total population only matters through it. (The
        divisor works out to 1 per 2,000 inhabitants, which coincides with the bathhouse divisor by
        arithmetic accident, not by design - if a city's samurai share is ever declared away from
        10%, this follows the samurai and the bathhouses do not.) The countryside cohort is
        deliberately NOT counted: a provincial city's size already scales with the countryside that
        feeds it, so asking about it twice would double-count (GM 2026-07-25).

        Seats are hand-vetted (x, y) candidates, first n drawn - provide 2 so any roll can land;
        `count=` pins the roll. Recorded as meta['dojo_roll'] and gated by
        city_dojo_count_follows_samurai, so a stale hand count can never ship. The roll consumes NO
        main-stream RNG (dedicated Random on the map seed): a map rolling its old count stays
        byte-identical."""
        samurai = round(int(self.M.get("meta", {}).get("population") or 3000) * self.DOJO_SAMURAI_FRAC)
        rolled = max(1, samurai // self.DOJO_PER_SAMURAI + (1 if random.Random(self.seed * 2777 + 91).random() < (samurai % self.DOJO_PER_SAMURAI) / self.DOJO_PER_SAMURAI else 0))
        n = int(count) if count is not None else rolled
        if n > len(seats):
            raise ValueError(f"dojos rolled {n} but only {len(seats)} vetted seats were provided - add candidates (the samurai band can ask for up to 2)")
        for dx_, dy_ in seats[:n]:
            self.dojo(dx_, dy_)
        self.M["meta"]["dojo_roll"] = n
        return n

    def place_caption(  # type: ignore[misc]
        self: Settlement,
        text: str,
        box: Sequence[float] | None,
        size: float = 9,
        italic: bool = True,
        weight: str = "normal",
        color: str = "#5A4326",
        rot: float = 0.0,
    ) -> None:
        """Caption the feature occupying `box` - seated in the label phase by the ONE placer (feature 266) as a POINT
        subject: the feature's box turned by `rot`, the caption beside it at the standard's first free ranked position.
        Use this instead of a hand-picked `s.label(x, y, ...)` whenever the caption names a specific feature. Records the
        subject box on the label so `label_hugs_its_referent` can measure the finished gap.

        `box` accepts None so `s.frontage_box` can be passed straight through; a None means the row placed nothing, and
        captioning an empty row is a gen-script bug, not something to draw.

        DEFERRED to the label phase: seating a caption at call time judges it against half a map (Tango's north gate
        market caption took the flank that later filled with the execution ground)."""
        if box is None:
            raise ValueError(f"place_caption({text!r}) got no subject box - the feature it names placed nothing")
        x0, y0, x1, y1 = (float(v) for v in box)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        subject = Subject("point", tuple(rect(cx, cy, (x1 - x0) / 2, (y1 - y0) / 2, rot)), angle=rot)
        self._captions.append((text, subject, size, italic, weight, color))

    def _label_hits(self: Settlement, lx: float, ly: float, text: str, size: float, pad: float = 4.0, linepad: float = 6.0) -> int:  # type: ignore[misc]
        """How many already-placed footprints (buildings/houses + homestead groves) a label at
        (lx, ly) would cover. The cheap scorer behind auto label placement: prefer a label spot
        in EMPTY ground; when every spot overlaps something, take the least (GM label doctrine,
        2026-07). AABB against self.placed + grove_rects - a few thousand float compares, so it
        stays render-cheap.

        `pad`/`linepad` are the anti-touching margins - a label that CLEARS by a hair still reads
        as touching - and the DEFAULTS ARE LOAD-BEARING: every shipped map's ministry label sides
        and deferred road label were decided on these numbers, so changing them reflows the pool.
        The standoff ladder (`_best_label_spot`) passes 0 for both, because it enforces its own
        LABEL_MIN_AIR against the subject and would otherwise double-count: with the defaults a
        12px road caption could never come closer than ~29px of true air, which is most of the
        drift the GM caught. Even at 0 the box stays ~13% wider than the one `_record_label`
        writes (0.31/char here against 0.275), which is the slack that keeps glyphs off a
        neighbor's edge."""
        hw, hh = len(text) * size * 0.31 + pad, size * 0.75 + pad
        corners: Poly = [(lx - hw, ly - hh), (lx + hw, ly - hh), (lx + hw, ly + hh), (lx - hw, ly + hh)]
        probes: Poly = [*corners, (lx, ly)]  # the LINE tests below sample the corners + center
        # LEVEL ONLY SINCE FEATURE 266: the one placer (`l7r/diagram/labels/`) seats every searched caption, tilted ones
        # included, and its own index measures their true quads; this scorer is left serving the hand-seated ministry and
        # martial-hall side choices of the unscripted tiers (spec D8), which are level.

        def covers(bx: float, by: float, bw: float, bh: float) -> bool:
            """Does the caption cover this rect? The AABB test - exact for a level caption."""
            return abs(bx - lx) < hw + bw / 2 and abs(by - ly) < hh + bh / 2

        n = 0
        for px, py, pw, ph, *_ in self.placed:
            if covers(px, py, pw, ph):
                n += 1
        for gx, gy, gw, gh in self.grove_rects:
            if covers(gx, gy, gw, gh):
                n += 1
        # THE RAMPART IS AN OBSTACLE TOO (GM 2026-08-10): a caption laid across the wall or the
        # moat is swallowed by their ink and reads as naming the defenses. The ladder scored
        # only footprints, so an auto-placed caption beside a wall-hugging feature drifted onto
        # the wall - Hirameki's monastery and fire-tower captions both crossed it by a hair
        # (captions_clear_of_the_defenses). Counted like any other hit, so the ladder simply
        # prefers a clear rung.
        for _wpts, _whw in ([(list(self.M["wall"]) + [self.M["wall"][0]], 9.0)] if len(self.M.get("wall") or []) >= 3 else []) + (
            [(list(self.M["moat"]) + [self.M["moat"][0]], float(self.M.get("moat_width", 22)) / 2)] if self.M.get("moat") else []
        ):
            _c4 = corners
            if any(seg_dist(_qx, _qy, _wpts[_i], _wpts[_i + 1]) < _whw for _qx, _qy in _c4 for _i in range(len(_wpts) - 1)) or any(
                segments_cross(_c4[_e], _c4[(_e + 1) % 4], _wpts[_i], _wpts[_i + 1]) for _e in range(4) for _i in range(len(_wpts) - 1)
            ):
                n += 1
        for gs in self.M.get("gate_structs", []) + self.M.get("wall_towers", []):
            if covers(gs["x"], gs["y"], gs["w"], gs["h"]):
                n += 1
        # TORII ARCHES count too (GM 2026-07-27: an arch is "never covered by the 'temple of X'
        # label"). Without this the standoff ladder is blind to a sando - it cannot avoid what it
        # cannot see - and Tango's theater-stage caption, seated by that ladder, walked straight onto
        # Benten's arch the moment _avenue_at_threshold brought it in to the hall.
        _txh, _tyu, _tyd = torii_halfbox(self.ftpx)
        for _t in self.M.get("torii", []):
            # the arch's box is asymmetric about its anchor (uprights below, lintel above), so it
            # is re-centered here rather than passed as a half-extent - identical arithmetic
            if covers(_t[0], _t[1] + (_tyd - _tyu) / 2, 2 * _txh, _tyu + _tyd):
                n += 1
        # ...and WELLHEADS, for the same reason: a well is a caption victim in check_village's
        # _LABEL_GROUP (a drawn glyph a caption can bury) but has no w/h, so it is in none of the
        # registries above and the ladder could not see it - which is how Tango's cremation-ground
        # caption came to sit on one. Its drawn extent is the marker radius `vr`.
        for _w in self.M.get("wells", []):
            _vr = float(_w.get("vr") or _w.get("r") or 0)
            if covers(_w["x"], _w["y"], 2 * _vr, 2 * _vr):
                n += 1
        # the LINE features a label must not straddle: the rampart, the moat, the road itself,
        # and open water - tested as stroke-vs-label-box distance on the box's corner/center points
        lines: list[Any] = []
        if self.M.get("wall"):
            lines.append((self.M["wall"], 7))
        if self.M.get("moat_layer") or self.M.get("moat"):
            lines.append((self.M.get("moat_layer") or self.M.get("moat"), self.M.get("moat_width", 22) / 2))
        if self.M.get("road"):
            lines.append((self.M["road"], self.M.get("road_width", 30) / 2))
        for st in self.M.get("streams", []):
            lines.append((st["poly"], st.get("w", 9) / 2))
        for pts, half in lines:
            hit = False
            for k in range(len(pts) - 1):
                for qx, qy in probes:
                    px2, py2 = seg_closest(qx, qy, pts[k], pts[k + 1])
                    if abs(px2 - lx) < hw + half and abs(py2 - ly) < hh + half and math.hypot(px2 - qx, py2 - qy) < half + linepad:
                        n += 1
                        hit = True
                        break
                if hit:
                    break
            if hit:
                continue
        return n

    def forest_patch(self: Settlement, base: Any, label: Any = None, label_xy: Any = None) -> None:  # type: ignore[misc]
        """A bounded copse (organic polygon), as opposed to forest() which fills to the canvas edge.
        Same stand of INDIVIDUAL TREES (see _tree_stand), just a closed one - so it is framed whole,
        because unlike a canvas-filling wood its SHAPE is the feature. Blocks houses; deterministic."""
        # SCOPED (2026-08-08): the copse OUTLINE is stream-drawn (organic_poly), and its SHAPE is the
        # feature - so an upstream change reshaped the wood and moved every tree in it. Keyed on the
        # base polygon the GM placed it on, which is the thing that should decide how it looks.
        with self.rng_scope("forest_patch", len(base), base[0][0], base[0][1]):
            outline = organic_poly(base, 22)
            sm = smooth_points(outline)
            xs = [p[0] for p in sm]
            ys = [p[1] for p in sm]
            # the litter floor shrinks toward the copse's center by a crown's width, so its edge sits
            # under the canopy (see _tree_stand: the crowns are what the copse's outline is made of)
            ccx, ccy = sum(xs) / len(xs), sum(ys) / len(ys)
            apo = min(math.hypot(x - ccx, y - ccy) for x, y in sm)
            k = max(0.35, 1 - self.px(self.CANOPY_R_FT) / max(apo, 1.0))
            self._tree_stand(sm, seed=12, floor=[(ccx + (x - ccx) * k, ccy + (y - ccy) * k) for x, y in sm])
            self.block_polys.append(sm)
            self.M["forest_patches"].append([[round(x, 1), round(y, 1)] for x, y in sm])
            if label:
                lx, ly = label_xy if label_xy else ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2)
                self.label(lx, ly, label, 12, italic=True, weight="bold", color="#3E5631")

    def wall(self: Settlement, pts: Any, gate: Any = None, label: Any = None, guardtower: bool = True) -> None:  # type: ignore[misc]
        """An irregular town rampart (thick polyline; may be an open arc anchored to a
        hill). gate=(x,y): a gap with posts, a guard station, and an optional guardtower.
        Recorded so the gate can check the wall and gate exist. No-build corridor."""
        wc = '#3A352C'
        # the rampart renders in the WALL layer (over the ground lanes - a street running into it passes
        # UNDER it), with a genuine gap at the gate so the road shows through the opening
        dd = self._gapped_ring(pts, [gate] if gate else [], 36, closed=False)
        ww = self.M["wall_stroke"] = 10.0  # recorded for the same reason as the city rampart's (see city_wall)
        self.M["wall_z"] = self.add_wall(f'<path d="{dd}" fill="none" stroke="{wc}" stroke-width="{ww:g}" stroke-linejoin="round" stroke-linecap="round"/>')
        self.add_wall(f'<path d="{dd}" fill="none" stroke="#6B5A3A" stroke-width="3" stroke-linejoin="round" opacity="0.5"/>')
        if gate:
            gx, gy = gate
            self.add_wall(f'<rect x="{gx - 42:.0f}" y="{gy - 24:.0f}" width="14" height="48" fill="{wc}"/>')  # gateposts (frame the opening)
            self.add_wall(f'<rect x="{gx + 28:.0f}" y="{gy - 24:.0f}" width="14" height="48" fill="{wc}"/>')
            # the gatehouse (guard station + tower) goes in the TOP layer: a street running
            # through the gate passes UNDER it, not over it
            gz = self.add_top(f'<rect x="{gx - 48:.0f}" y="{gy + 26:.0f}" width="96" height="46" rx="2" fill="#C9A57A" stroke="#5A4326" stroke-width="1.6"/>')  # guard station
            self.add_top(f'<line x1="{gx - 48:.0f}" y1="{gy + 49:.0f}" x2="{gx + 48:.0f}" y2="{gy + 49:.0f}" stroke="#5A4326" stroke-width="0.8"/>')
            self.M["gate_structs"] = [{"x": gx, "y": gy + 49, "w": 96, "h": 46, "z": gz}]  # guard station
            if guardtower:
                tz = self.add_top(f'<rect x="{gx + 50:.0f}" y="{gy - 44:.0f}" width="40" height="40" fill="#9C8A66" stroke="{wc}" stroke-width="2.4"/>')  # guardtower
                self.add_top(f'<rect x="{gx + 58:.0f}" y="{gy - 36:.0f}" width="24" height="24" fill="#6B5A3A"/>')
                self.M["gate_structs"].append({"x": gx + 70, "y": gy - 24, "w": 40, "h": 40, "z": tz})
            # block the guard station / tower from placement (rect + a building-half margin)
            for gs in self.M["gate_structs"]:
                bm = 32
                self.block_polys.append(
                    [
                        (gs["x"] - gs["w"] / 2 - bm, gs["y"] - gs["h"] / 2 - bm),
                        (gs["x"] + gs["w"] / 2 + bm, gs["y"] - gs["h"] / 2 - bm),
                        (gs["x"] + gs["w"] / 2 + bm, gs["y"] + gs["h"] / 2 + bm),
                        (gs["x"] - gs["w"] / 2 - bm, gs["y"] + gs["h"] / 2 + bm),
                    ]
                )
            self.M["gate"] = [gx, gy]
        self.M["wall"] = [[x, y] for x, y in pts]
        # no-build clearance kept wide enough that even a large building's CORNER (not
        # just its center) stays off the rampart stroke (half-diagonal of a 60x40 ~36)
        self.corridors.append(([(x, y) for x, y in pts], 46))
        if label:
            self.label(pts[0][0], pts[0][1] - 16, label, 12, italic=True, weight="bold", color=wc)

    def flower_field(self: Settlement, shape: Any, label: Any = None, amp: float = 30, label_xy: Any = None, kind: str = "chrysanthemum", flat_west: bool = False) -> None:  # type: ignore[misc]
        """An ornamental flower field (e.g. chrysanthemums - the Imperial flower).
        Organic outline like a paddy, but rows of gold blooms instead of rice.
        flat_west keeps the west edge straight so it can run flush against a town wall."""
        outline = (
            organic_bbox(shape, amp, flat_edges=cast("tuple[int, ...]", {3} if flat_west else ())) if len(shape) == 4 and all(isinstance(v, (int, float)) for v in shape) else organic_poly(shape, amp)
        )
        sm = smooth_points(outline)
        d = smooth_closed(outline)
        cid = self._cid('flower')
        self.add(f'<clipPath id="{cid}"><path d="{d}"/></clipPath>')
        self.add(f'<g clip-path="url(#{cid})">')
        self.add(
            f'<rect x="{min(p[0] for p in sm):.0f}" y="{min(p[1] for p in sm):.0f}" '
            f'width="{max(p[0] for p in sm) - min(p[0] for p in sm):.0f}" height="{max(p[1] for p in sm) - min(p[1] for p in sm):.0f}" fill="#B7C089"/>'
        )
        xs, ys = [p[0] for p in sm], [p[1] for p in sm]
        st = random.getstate()
        random.seed(17)
        yy = min(ys) + 12
        while yy < max(ys):
            xx = min(xs) + 12
            while xx < max(xs):
                fx, fy = xx + random.uniform(-4, 4), yy + random.uniform(-4, 4)
                if point_in_poly(fx, fy, sm):
                    self.add(f'<circle cx="{fx:.0f}" cy="{fy:.0f}" r="3.4" fill="#E8C84C" stroke="#B89A2E" stroke-width="0.5"/>')
                    self.add(f'<circle cx="{fx:.0f}" cy="{fy:.0f}" r="1.2" fill="#FBF2C4"/>')
                xx += 15
            yy += 15
        self.add('</g>')
        random.setstate(st)
        self.add(f'<path d="{d}" fill="none" stroke="#8A8A4A" stroke-width="2.5"/>')
        self.field_polys.append(sm)
        self.M["flower_fields"].append({"kind": kind, "outline": [[round(p[0], 1), round(p[1], 1)] for p in sm]})
        if label:
            lx, ly = label_xy if label_xy else ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2)
            self.label(lx, ly, label, 11, italic=True, weight="bold", color="#7A6A1A")
