"""City fixtures - the theater stage and the drum tower (feature 145: moved out of fixtures.py, whose kosatsuba the hamlet path executes)."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core import Settlement

import math
from typing import TYPE_CHECKING, Any


class UrbanFixturesMixin:
    def theater_stage(self: Settlement, cx: float, cy: float, w: Any = None, h: Any = None, rot: float = 0, label: Any = None, kind: str = "monzen") -> None:  # type: ignore[misc]
        """A public THEATER STAGE: a roofed raised stage facing an open viewing ground - the troupe-and-
        festival venue of a Rokugani town/city (the East Asian analog of a Greco-Roman amphitheater: a
        temple OPERA STAGE / shrine NOH-kagura stage). It belongs to a temple/monastery precinct, the
        audience gathering in the open ground between the stage and the hall. (cx,cy) is the center of the
        w x h viewing ground; the roofed stage sits at the -y (north) end facing +y into it; `rot` turns the
        whole feature (point it so the ground opens toward the temple). Records M['theater_stage'] - a LIST
        since 2026-08-10: the singleton dict write meant a second stage clobbered the first, so Shiro
        Daika's labeled entertainment-quarter theater existed as ink only, invisible to the overlap
        matrix in both directions (settlement-review). `kind` says which siting doctrine the stage owes:
        "monzen" (default) is a temple/shrine performance stage and must sit at its hall;
        "machi" is a commercial quarter theater and sits in the fabric. Reserves its footprint so
        packing avoids it."""
        if w is None:
            w, h = self.px(150), self.px(105)  # stage + viewing ground ~150x105 ft (town-calibrated)
        hw, hh = w / 2, h / 2
        sw, sh = w * 0.5, h * 0.26  # the roofed stage at the north end
        sy = -hh - sh * 0.5  # straddling the ground's north edge
        g = [f'<g transform="translate({cx:.1f},{cy:.1f}) rotate({rot:.1f})">']
        g.append(f'<rect x="{-hw:.0f}" y="{-hh:.0f}" width="{w:.0f}" height="{h:.0f}" rx="4" fill="#E4D6B0" stroke="#A98E54" stroke-width="1.5"/>')  # the swept earthen viewing ground
        g.append(f'<rect x="{-hw + 5:.0f}" y="{-hh + 5:.0f}" width="{w - 10:.0f}" height="{h - 10:.0f}" rx="3" fill="none" stroke="#C9B484" stroke-width="0.7" opacity="0.6"/>')
        for i in range(3):  # a few faint rows of standing crowd in the ground
            ry = -hh + h * (0.40 + 0.17 * i)
            for k in range(7):
                px = -hw + 14 + (w - 28) * (k + 0.5) / 7
                g.append(f'<circle cx="{px:.0f}" cy="{ry:.0f}" r="1.7" fill="#8A7A56" opacity="0.5"/>')
        g.append(f'<rect x="{-sw / 2:.0f}" y="{sy:.0f}" width="{sw:.0f}" height="{sh:.0f}" rx="2" fill="#C9A57A" stroke="#5A3F1E" stroke-width="1.8"/>')  # stage platform
        g.append(f'<rect x="{-sw / 2:.0f}" y="{sy:.0f}" width="{sw:.0f}" height="{sh * 0.36:.0f}" fill="#7A5A30"/>')  # its roof
        # NO painted-pine roundel. The kagami-ita's pine is painted on the VERTICAL back board, so a
        # plan view cannot see it at all - and drawn as a green disc it used the sheet's own
        # vegetation idiom and read as a bush growing on the stage (settlement-review, Ubame).
        g.append(f'<rect x="{-sw / 2:.0f}" y="{sy + sh - 2.5:.0f}" width="{sw:.0f}" height="2.5" fill="#5A3F1E" opacity="0.6"/>')  # stage-front lip onto the ground
        g.append('</g>')
        self.add(''.join(g))
        self.M.setdefault("theater_stage", []).append({"x": cx, "y": cy, "w": w, "h": h, "rot": rot, "kind": kind})
        R = math.hypot(hw, hh) + sh * 0.5  # rotation-safe covering radius (stage + ground)
        self.ellipses.append((cx, cy, R, R))
        if label:
            # Offset from the ROTATED extent, not the raw half-height. At rot=90 the ground's reach
            # along +y is hw, not hh, so the caption landed INSIDE the ground it names, with the
            # outline stroke running through the text (settlement-review, Ubame, 2026-07-26).
            # Identical to the old expression at rot=0, so unrotated stages are untouched.
            # Seat by the STANDOFF LADDER against the stage's ROTATED extent, hinted at the historical
            # spot. Two bugs, one fix: the old `cy + hh + 16` used the unrotated half-height, so a
            # rot=90 stage captioned INSIDE its own ground (Ubame); and a hand seat has no idea what
            # else is there, so simply correcting the reach dropped Tango's caption onto a monk house.
            # The hint keeps every UNROTATED stage exactly where it was whenever that seat is clear.
            _a = math.radians(rot)
            _rx = abs(hw * math.cos(_a)) + abs(hh * math.sin(_a))
            _ry = abs(hw * math.sin(_a)) + abs(hh * math.cos(_a))
            self.place_caption(label, (cx - _rx, cy - _ry, cx + _rx, cy + _ry), 11, italic=True, hint=(cx, cy + _ry + 16), rot=rot)

    def drum_tower(self: Settlement, x: float, y: float, tw: float | None = None, label: str = "drum tower") -> int:  # type: ignore[misc]
        """A combined BELL-AND-DRUM TOWER (zhonggulou) - the timekeeping/curfew institution of a
        WALLED seat (GM 2026-07-24). Morning bell, evening drum: dawn gate-opening, the dusk
        gate-closing that starts the street curfew, the five night watches, alarm and ceremony.
        Part of the standard county-seat kit (yamen, temples, drum tower); a county seat had ONE
        combined tower - the paired gulou/zhonglou on an axis is capital grammar (Pingyao, a
        wealthy county seat, has exactly one Market Tower, ~60 ft). Distinct from the fire towers:
        fire watch was a SEPARATE institution in both reference cultures (Song Kaifeng ran
        dedicated fire-lookout towers; Edo split the licensed toki-no-kane time bell from the
        hinomi-yagura). Drawn as a heavy masonry platform (county tier ~60-80 ft square) carrying
        a timber pavilion with the drum and the bell - visibly heavier-built than the skeletal
        braced-frame fire towers. Stands at the main street crossing, near (not inside) the yamen.
        Records M['drum_towers'] (an overlap-checked struct) and reserves a no-build block."""
        if tw is None:
            tw = self.px(
                36
            )  # county-tier footprint RE-VERIFIED (GM eye + research 2026-07-24): Pingyao's Market Tower - the wealthy-county showpiece - is ATTESTED at 133.4 m^2 plan (~38 ft square); these towers dominate by HEIGHT (50-60 ft), not plan, so ~36 ft = one rowhouse width reads correctly. The first-draft 70 ft was contaminated by garrison street-arch platforms (Dingbian 52 ft, Xingcheng 66 ft) - that variant is prefecture/garrison tier, never a 3,000-person seat
        h = tw / 2
        hi = tw * 0.31  # the pavilion atop the platform
        g = [f'<g transform="translate({x:.0f},{y:.0f})">']
        g.append(f'<rect x="{-h:.1f}" y="{-h:.1f}" width="{tw:.1f}" height="{tw:.1f}" rx="1.5" fill="#E3D7B8" stroke="#4A3318" stroke-width="2.4"/>')  # the masonry platform
        g.append(f'<rect x="{-hi:.1f}" y="{-hi:.1f}" width="{hi * 2:.1f}" height="{hi * 2:.1f}" rx="1" fill="#C9A57A" stroke="#4A3318" stroke-width="1.5"/>')  # the timber pavilion
        g.append(f'<line x1="{-hi:.1f}" y1="0" x2="{hi:.1f}" y2="0" stroke="#4A3318" stroke-width="0.9" opacity="0.7"/>')  # the pavilion roof ridge
        g.append(
            f'<circle cx="{-tw * 0.155:.1f}" cy="0" r="{max(tw * 0.105, 1.2):.1f}" fill="#8A4A2A" stroke="#4A3318" stroke-width="0.8"/>'
        )  # the great drum (radius floored - legible at the corrected 12px platform)
        g.append(f'<circle cx="{tw * 0.155:.1f}" cy="0" r="{max(tw * 0.08, 0.9):.1f}" fill="#6B5A3A" stroke="#4A3318" stroke-width="0.8"/>')  # the bell
        g.append('</g>')
        z = self.add_top(''.join(g))
        self.M.setdefault("drum_towers", []).append({"x": round(x, 1), "y": round(y, 1), "w": tw, "h": tw, "rot": 0.0, "z": z, "label": label})
        self.placed.append((x, y, tw, tw))
        bm = 12
        # the block reserves the caption band below too, AT THE CAPTION'S WIDTH - the corrected
        # 36 ft platform is narrower than the "drum tower" text, so a footprint-width band let
        # rowpack houses slide under the caption's ends (GM tower-resize ripple, 2026-07-24)
        self.block_polys.append([(x - h - bm, y - h - bm), (x + h + bm, y - h - bm), (x + h + bm, y + h + bm), (x - h - bm, y + h + bm)])
        cb_ = max(h + bm, 2.9 * len(label) + 10)
        self.block_polys.append([(x - cb_, y + h), (x + cb_, y + h), (x + cb_, y + h + 40), (x - cb_, y + h + 40)])
        # the caption is TWO LINES, "drum/bell" over "tower" (GM 2026-07-24): the county tower is
        # genuinely the combined zhonggulou - both instruments in one building, and both are drawn
        self.label(x, y + h + 12, "drum/bell", 9, italic=True, color="#4A3318")
        self.label(x, y + h + 24, "tower", 9, italic=True, color="#4A3318")
        return z
