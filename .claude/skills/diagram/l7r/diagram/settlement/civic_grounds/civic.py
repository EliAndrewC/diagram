"""Institutional and commercial works: what a domain builds because it administers and trades,
as opposed to what its inhabitants build in order to live.

Split from settlement/civic_grounds.py by feature 115 - see settlement/civic_grounds/CLAUDE.md for the index.

Research: plumbing - NONE
"""

import math
import random
from typing import TYPE_CHECKING, Any

from .._geom import (
    Pt,
    point_in_poly,
    rects_overlap,
    rot_rect,
    seg_dist,
    segments_cross,
)

if TYPE_CHECKING:
    from ..core import Settlement


class CivicWorksMixin:
    def precinct_interior(self: Settlement, x: float, y: float, w: float | None = None, h: float | None = None, rear: str = "north", graveyard: bool = True) -> None:  # type: ignore[misc]
        """A SOVEREIGN TEMPLE PRECINCT's interior (feature 021, research item 7): the head-house
        program - abbot's residence, order administration, library/sutra hall, two monk
        dormitories, kitchen/refectory - drawn INSIDE the ground the 020 reservation held,
        densest toward the hall axis with the dormitories rearward (the shared Zen/Chinese
        seven-halls plan; the 390x300 ft reservation was sized for exactly this). `rear` names
        the side AWAY from the sando (the torii face), where the service program gathers; the
        front third stays open for the approach. Also claims the reservation itself: records
        M['precincts'] and holds both placement registries, replacing the hand-rolled 020
        reserve, and (graveyard=True) draws the parish burial plot that closes the temple's
        020 `graveyard` claim. Map-scale glyphs are footprint boxes in the religious palette,
        labeled never - the hall's own caption names the complex (caption-loudness).

        Research:
            head-house program - research/questions/0227-city-temples-the-precinct-its-halls-bell-tower-and-pagoda-garan.drawing.html: residence, kitchen, two dormitories, library, administration
            program seats - research/questions/0227-city-temples-the-precinct-its-halls-bell-tower-and-pagoda-garan.drawing.html: kuri and monks' quarters to one side, abbot's behind the hall; hand-set, dormitories on axis at the rear, residence to one side
            program sizes - UNRESEARCHED: hand-set footprints
            precinct size - research/questions/0227-city-temples-the-precinct-its-halls-bell-tower-and-pagoda-garan.drawing.html: about 73,000 sq ft, 310 x 235 ft by default, or the caller's w x h
            parish burial plot in the precinct - research/questions/0237-burial-grounds-of-towns-and-cities-and-paupers-grounds-yizhong.drawing.html, research/questions/0235-village-burial-grounds-bochi.drawing.html: a ruled plot; 24 x 16 px (about 0.08 acre at 3 ft/px)
            glyph - CONVENTION: footprint boxes, no captions
        """
        w, h = (self.px(310) if w is None else w), (self.px(235) if h is None else h)  # a sovereign precinct about 73,000 sq ft (0227)
        self.M.setdefault("precincts", []).append({"x": round(x, 1), "y": round(y, 1), "w": w, "h": h, "rear": rear, "graveyard": graveyard})
        self.block_polys.append([(x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2)])
        self.placed.append((x, y, w, h))
        sgn = -1.0 if rear == "north" else 1.0  # rear-edge offsets flip with the sando side
        ye = y + sgn * h / 2
        # (dx, dy-from-rear-edge, w-ft, h-ft, kind) - hand-set so nothing clips the 150x100 ft hall
        prog = [
            (-44, 12, 48, 30, "residence"),
            (-45, 30, 36, 24, "kitchen"),
            (-8, 10, 57, 21, "dormitory"),
            (14, 22, 57, 21, "dormitory"),
            (52, None, 33, 24, "library"),
            (-54, None, 42, 27, "administration"),
        ]
        g = []
        for dx, dy, wf, hf, kind in prog:
            bw, bh = wf / self.ftpx, hf / self.ftpx
            bx = x + dx
            by = (y + sgn * 2) if dy is None else (ye - sgn * dy)
            g.append(f'<rect x="{bx - bw / 2:.1f}" y="{by - bh / 2:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="1.2" fill="#E6DCC4" stroke="#6E5B3A" stroke-width="1.1"/>')
            self.M.setdefault("precinct_halls", []).append({"x": round(bx, 1), "y": round(by, 1), "w": round(bw, 1), "h": round(bh, 1), "kind": kind, "precinct": [round(x, 1), round(y, 1)]})
        self.add_top("".join(g))
        if graveyard:
            self.cemetery(x + 44, ye - sgn * 14, 24, 16, parish=True)

    def district(self: Settlement, name: str, kind: str, poly: Any, rank_band: str | None = None) -> None:  # type: ignore[misc]
        """A declared fabric DISTRICT (feature 021): a named placement region for the housing
        packs and the ground truth for capital_rank_gradient. A declarative overlay like
        quarter() - draws nothing and reserves nothing; the packs it names do the drawing.
        Records M['districts'] {name, kind, poly, rank_band?}; kinds: yashiki, detached,
        terrace, machi, monzen, entertainment.

        Research: district overlay - NONE: draws and reserves nothing
        """
        rec: dict[str, Any] = {"name": name, "kind": kind, "poly": [list(p) for p in poly]}
        if rank_band is not None:
            rec["rank_band"] = rank_band
        self.M.setdefault("districts", []).append(rec)

    def terrace(self: Settlement, x: float, y: float, units: int = 8, rot: float = 0.0, frontage_ft: float = 18.0, depth_ft: float = 24.0) -> int:  # type: ignore[misc]
        """A RETAINER TERRACE range (feature 021): ONE roof over `units` single-file household
        cells divided by party walls - the kumi-yashiki/nagaya form. Research (021 item 2):
        cells of 4.5-8 tatami behind an earth-floored entry, ~18 ft frontage each, ~21 ft
        deep (Shibata's 8-cell 143 x 21 ft range is the anchor); detached cottages were the
        Kanazawa EXCEPTION, so the glyph is a continuous roof with drawn seams, not houses at
        row pitch. In Rokugan these house junior SAMURAI (Ranks 1-4) - ashigaru are peasants
        and have no capital quarter (GM 2026-08-08). Records M['terraces']
        {x, y, w, h, rot, units, z}; classified SOLID in the keep-clear contract.

        Research:
            one roof over the cells - research/questions/0140-where-a-capitals-samurai-live-lineage-compounds-walled-estates-and-retainer-terraces-bukeyashiki.drawing.html, research/questions/0140-where-a-capitals-samurai-live-lineage-compounds-walled-estates-and-retainer-terraces-bukeyashiki.html: a continuous range with drawn seams
            cell frontage - research/questions/0140-where-a-capitals-samurai-live-lineage-compounds-walled-estates-and-retainer-terraces-bukeyashiki.html: 18 ft
            range depth - research/questions/0140-where-a-capitals-samurai-live-lineage-compounds-walled-estates-and-retainer-terraces-bukeyashiki.html: 24 ft, Shibata's 7.3 m
            cell count - research/questions/0140-where-a-capitals-samurai-live-lineage-compounds-walled-estates-and-retainer-terraces-bukeyashiki.html: eight households under one roof at Shibata; the caller's units, default 8
        """
        w, h = units * frontage_ft / self.ftpx, depth_ft / self.ftpx
        g = [f'<g transform="translate({x:.1f},{y:.1f}) rotate({rot:.1f})">']
        g.append(f'<rect x="{-w / 2:.1f}" y="{-h / 2:.1f}" width="{w:.1f}" height="{h:.1f}" rx="1.5" fill="#C9B892" stroke="#6E5B3A" stroke-width="1.4"/>')
        step = w / units
        for i in range(1, units):
            sx = -w / 2 + i * step
            g.append(f'<line x1="{sx:.1f}" y1="{-h / 2:.1f}" x2="{sx:.1f}" y2="{h / 2:.1f}" stroke="#6E5B3A" stroke-width="0.9" opacity="0.8"/>')
        g.append("</g>")
        z = self.add_top("".join(g))
        self.M.setdefault("terraces", []).append({"x": round(x, 1), "y": round(y, 1), "w": round(w, 1), "h": round(h, 1), "rot": round(rot, 1), "units": units, "z": z})
        # reserve the AXIS-ALIGNED BBOX of the rotated range, not the unrotated w x h: a rot=90
        # file reserves a wide/short phantom otherwise, and place_wells seated a wellhead ON the
        # Shiro Daika gate terraces through exactly that gap (found 2026-08-10, feature 021)
        ta = math.radians(rot)
        self.placed.append((x, y, abs(w * math.cos(ta)) + abs(h * math.sin(ta)), abs(w * math.sin(ta)) + abs(h * math.cos(ta))))
        return z

    def granary(self: Settlement, x: float, y: float, n: int = 1, w: Any = None, h: Any = None, gap: float = 14, label: str = "granary", append: bool = False, rot: float = 0.0) -> list[Any]:  # type: ignore[misc]
        """A short row of fireproof storehouses (kura) - the tax-rice granary of a rice-TRANSIT
        town, where grain from many counties is gathered and forwarded up the kick-up chain.
        White-walled with a dark hip roof. Opt-in (meta(granary=True)): a standard county seat
        keeps its grain inside the magistrate's yamen, so it is NOT drawn separately. Records to
        M['granary'] (gated by town_has_granary) and blocks houses, like the manor.
        append=True records each store into the M['granaries'] LIST instead and leaves the legacy
        dict untouched: a capital holds its grain in TWO places for two reasons (the domain's
        working stipend rice at the wharf, the Emperor's stores beside it - and the siege stock
        inside the castle, never drawn), and a second call on the dict would silently clobber the
        first. Per-store records, so the overlap matrix can see each one (feature 019's lesson).
        `rot` turns the whole row (degrees) so a riverside complex can stand parallel to its bank
        (GM 2026-08-09: the wharf granaries belong ON the wharf, aligned with the water they
        serve); the rot=0 path is byte-identical to the old drawing for every existing map.

        Research:
            tax-rice granary at a transit town - research/questions/0098-storehouses-for-the-tax-rice.drawing.html: opt-in, a county seat keeps its grain in the yamen
            store size and count - research/questions/0098-storehouses-for-the-tax-rice.drawing.html: the caller's n x w x h, by default the office's single store of about 45 x 25 ft
            the capital's granaries - research/questions/0142-rice-storehouses-and-the-rice-brokers-in-a-capital-kura-fudasashi.drawing.html: append, turned to the bank
            white walls and dark hip roof - research/questions/0098-storehouses-for-the-tax-rice.drawing.html: the form a knob (takakura or kura); always the earth-walled kura, not rolled
            store fills and roof band - CONVENTION
            gap between stores - UNRESEARCHED: 14 px, fixed in pixels
            keep-clear margin - UNRESEARCHED: 30 px, 60 px added when turned
            caption - CONVENTION
        """
        w, h = (self.px(45) if w is None else w), (self.px(25) if h is None else h)  # one office store about 45 x 25 ft (0098)
        stores: list[Any] = []
        ga = math.radians(rot)
        gca, gsa = math.cos(ga), math.sin(ga)
        x0 = x - (n * w + (n - 1) * gap) / 2
        for i in range(n):
            cx = x0 + i * (w + gap) + w / 2
            if rot:
                rcx, rcy = x + (cx - x) * gca, y + (cx - x) * gsa  # the store's seat along the turned row axis
                gg_ = [f'<g transform="translate({rcx:.1f},{rcy:.1f}) rotate({rot:.1f})">']
                gg_.append(f'<rect x="{-w / 2:.0f}" y="{-h / 2:.0f}" width="{w}" height="{h}" rx="2" fill="#E8E0CE" stroke="#6B5A3C" stroke-width="2"/>')
                gg_.append(f'<rect x="{-w / 2:.0f}" y="{-h / 2:.0f}" width="{w}" height="9" fill="#5A4A30"/>')
                gg_.append(f'<line x1="0" y1="{-h / 2 + 9:.0f}" x2="0" y2="{h / 2:.0f}" stroke="#6B5A3C" stroke-width="0.7"/>')
                gg_.append("</g>")
                self.add("".join(gg_))
                stores.append({"x": round(rcx, 1), "y": round(rcy, 1), "w": w, "h": h, "rot": rot})
                self.block_polys.append([(round(qx, 1), round(qy, 1)) for qx, qy in rot_rect(rcx, rcy, w + 60, h + 60, rot)])
                continue
            self.add(f'<rect x="{cx - w / 2:.0f}" y="{y - h / 2:.0f}" width="{w}" height="{h}" rx="2" fill="#E8E0CE" stroke="#6B5A3C" stroke-width="2"/>')
            self.add(f'<rect x="{cx - w / 2:.0f}" y="{y - h / 2:.0f}" width="{w}" height="9" fill="#5A4A30"/>')  # dark fireproof hip roof
            self.add(f'<line x1="{cx:.0f}" y1="{y - h / 2 + 9:.0f}" x2="{cx:.0f}" y2="{y + h / 2:.0f}" stroke="#6B5A3C" stroke-width="0.7"/>')
            stores.append({"x": cx, "y": y, "w": w, "h": h, "rot": 0})
            bm = 30  # block a RECT + a building-half margin so dwellings keep clear, like the manor
            self.block_polys.append([(cx - w / 2 - bm, y - h / 2 - bm), (cx + w / 2 + bm, y - h / 2 - bm), (cx + w / 2 + bm, y + h / 2 + bm), (cx - w / 2 - bm, y + h / 2 + bm)])
        if append:
            self.M.setdefault("granaries", []).extend({**st, "label": label} for st in stores)
        else:
            self.M["granary"] = {"x": x, "y": y, "n": n, "stores": stores, "label": label}
        if label:
            if rot:
                loff = h / 2 + 12  # seat the caption off the row's upslope flank, clear of the turned roofs
                # the caption lies ALONG the row at its full tilt (GM 2026-08-09: linear
                # subjects may carry the whole angle - linear_tilt_full - where the old clamp
                # would have gone level past 45 deg, and label_tilt's building fold would have
                # laid perpendicular text ACROSS the kura)
                self.label(
                    x + gsa * loff,
                    y - gca * loff,
                    label,
                    11,
                    italic=True,
                    color="#6B5A3C",
                    ref=(min(s["x"] - s["w"] / 2 for s in stores), min(s["y"] - s["h"] / 2 for s in stores), max(s["x"] + s["w"] / 2 for s in stores), max(s["y"] + s["h"] / 2 for s in stores)),
                    rot=rot,
                    linear=True,
                    full_tilt=True,
                )
            else:
                self.label(
                    x,
                    y - h / 2 - 10,
                    label,
                    11,
                    italic=True,
                    color="#6B5A3C",
                    ref=(min(s["x"] - s["w"] / 2 for s in stores), min(s["y"] - s["h"] / 2 for s in stores), max(s["x"] + s["w"] / 2 for s in stores), max(s["y"] + s["h"] / 2 for s in stores)),
                )
        return stores

    def merchant_storehouses(self: Settlement, count: int = 6, kw: Any = None, kh: Any = None) -> int:  # type: ignore[misc]
        """Attach a small fireproof storehouse (kura) to the BACK of several merchant houses.
        Because most Rokugani farmers are TENANTS, the rent-rice and bulk goods of their (often
        absentee) landlords are kept in town - over and above the ordinary inventory storeroom a
        shop already has - so a noticeable MINORITY of businesses run a deep lot with a kura
        behind the shopfront (the classic narrow-front / deep-lot merchant compound). The kura
        is drawn as an annex behind the building (opposite its street-facing awning), like the
        farmhouse shed: part of the premises, not a separately-sited structure, so it needs no
        open ground in the packed quarter. Records to M['storehouses']; call AFTER the
        businesses are placed. Returns the number attached.

        Research:
            a kura behind the shop - research/questions/0155-rich-merchants-walled-houses-and-their-fireproof-storehouses-kura.html: an annex opposite the awning
            a minority of shops - research/questions/0155-rich-merchants-walled-houses-and-their-fireproof-storehouses-kura.drawing.html: the drawing page's GUESS, a large merchant house one or two, an ordinary shop-house none; the caller's count, default 6, of kinds merchant and shop
            kura size - research/questions/0155-rich-merchants-walled-houses-and-their-fireproof-storehouses-kura.drawing.html: 14 to 20 ft square, drawn 17 ft square
            off the street bed and the neighbor's lot - NONE: overlap rules
        """
        if kw is None:
            kw = kh = self.px(17)  # a kura 14 to 20 ft square (0155), drawn at the middle
        biz = [b for b in self.M["buildings"] if b["kind"] in ("merchant", "shop")]
        st = random.getstate()  # spread the picks across the quarter without perturbing
        random.seed(7)  # the main placement RNG (saved/restored, like forest())
        random.shuffle(biz)
        random.setstate(st)
        placed = 0
        for b in biz:
            if placed >= count:
                break
            th = math.radians(b["rot"])
            bx, by = math.sin(th), -math.cos(th)  # the building's BACK direction (awning faces -back)
            off = b["h"] / 2 + kh / 2 - 2  # tuck the kura just behind the shopfront
            ox, oy = b["x"] + bx * off, b["y"] + by * off
            # never let a kura sit ON a street/alley bed (the broad corridor test would veto
            # every candidate at city scale, where the shop rows legitimately sit inside the
            # corridor clearance of the street they front)
            beds = [(st["pts"], st.get("w", 18) / 2) for st in self.M.get("town_streets", [])]
            beds += [(al["pts"], al.get("w", 10) / 2) for al in self.M.get("alleys", [])]
            if self.M.get("road"):
                beds.append((self.M["road"], self.M.get("road_width", 30) / 2))
            if any(seg_dist(ox, oy, pts[k], pts[k + 1]) < half + max(kw, kh) / 2 + 3 for pts, half in beds for k in range(len(pts) - 1)):
                continue
            # ...and never ACROSS A NEIGHBOR. The kura is an annex of its OWN shop - that is what
            # makes its overlap legitimate - so a kura tucked behind a narrow shopfront that happens
            # to back onto the next lot's larger house is a defect, not an annex. The overlap matrix
            # (feature 017) found exactly that twice, because the old blanket storehouse exemption
            # could only say "a kura may overlap a building", never "its own".
            kq = rot_rect(ox, oy, kw, kh, b["rot"])
            if any(other is not b and rects_overlap(kq, rot_rect(other["x"], other["y"], other["w"], other["h"], other.get("rot", 0))) for other in self.M["buildings"]):
                continue
            self.add(
                f'<g transform="translate({ox:.0f},{oy:.0f}) rotate({b["rot"]:.0f})">'
                f'<rect x="{-kw / 2:.0f}" y="{-kh / 2:.0f}" width="{kw}" height="{kh}" rx="1.5" fill="#E8E0CE" stroke="#6B5A3C" stroke-width="1.4"/>'
                f'<rect x="{-kw / 2:.0f}" y="{-kh / 2:.0f}" width="{kw}" height="4.5" fill="#5A4A30"/></g>'
            )  # dark fireproof roof
            # RECORD THE ROTATION. The kura is DRAWN at its shopfront's angle and was recorded without
            # one, so every manifest reader rebuilt it as an axis-aligned box a couple of px wider than
            # the thing on the page - placement cleared a merchant_large by 0.37px and the overlap
            # matrix, reading the un-rotated record, reported a 0.6px collision (Tango, 2026-07-27).
            # Placement and its check must read the same geometry; here they could not, because the
            # manifest did not carry it.
            self.M["storehouses"].append({"x": ox, "y": oy, "w": kw, "h": kh, "rot": b["rot"], "of": [b["x"], b["y"]]})
            self.placed.append((ox, oy, kw, kh))  # later packs (the city terraces) must flow around the annex
            placed += 1
        return placed

    def merchant_residences(self: Settlement, count: int = 10, depth_margin: float = 14, spread: float = 120) -> int:  # type: ignore[misc]
        """Place a few RICH merchant RESIDENCES (kind 'merchant_large') directly BEHIND the shopfront band,
        each ALIGNED to (same rotation as) the storefront it sits behind - the merchant family lives over/
        behind its own shop. Derived from the ACTUAL placed shops (not fixed coords), so it stays correct
        under any seed: each home is set one step DEEPER than the deepest shop (clearing the storefront band),
        parallel to it. Call AFTER the frontage but BEFORE the laborer packs (which then set back further,
        leaving the merchant-band -> gap -> warren order). Uses a true RECTANGULAR overlap test (the circle
        _fits is far too conservative for a large home in a tight band). Returns count placed.

        Research:
            the merchant family lives behind its shop - research/questions/0154-merchants-townhouses-machiya.html, research/questions/0155-rich-merchants-walled-houses-and-their-fireproof-storehouses-kura.drawing.html: one step behind the shopfront band, aligned to it
            how many - research/questions/0155-rich-merchants-walled-houses-and-their-fireproof-storehouses-kura.drawing.html: a dozen or so very rich merchant families in a city of about 3,000; the caller's count, default 10
            spread along the band - UNRESEARCHED: 120 px apart
            band margin - UNRESEARCHED: 14 px
        """
        rd = self.M.get("road")
        biz = [b for b in self.M["buildings"] if b["kind"] in ("merchant", "shop")]
        if not (rd and biz):
            return 0

        def droad(x: float, y: float) -> float:
            return min(seg_dist(x, y, rd[k], rd[k + 1]) for k in range(len(rd) - 1))  # pyrefly: ignore[unsupported-operation, bad-argument-type]  # dict.get(k, Any-default) typed Any|None by pyrefly, Any by mypy - research 142 R5

        def corners(cx: float, cy: float, rw: float, rh: float, rot: float = 0.0) -> list[Pt]:
            th = math.radians(rot)
            c, sn = math.cos(th), math.sin(th)
            return [(cx + dx * c - dy * sn, cy + dx * sn + dy * c) for dx, dy in ((-rw / 2, -rh / 2), (rw / 2, -rh / 2), (rw / 2, rh / 2), (-rw / 2, rh / 2))]

        def overlap(ca: Any, cb: Any) -> bool:
            return (
                any(point_in_poly(px, py, cb) for px, py in ca)
                or any(point_in_poly(px, py, ca) for px, py in cb)
                or any(segments_cross(ca[i], ca[(i + 1) % 4], cb[j], cb[(j + 1) % 4]) for i in range(4) for j in range(4))
            )

        bandmax = max(droad(b["x"], b["y"]) for b in biz)  # depth of the deepest storefront
        w, h = self._dims("merchant_large")
        st = random.getstate()  # spread the picks without perturbing the main placement RNG
        random.seed(11)
        random.shuffle(biz)
        random.setstate(st)
        placed = 0
        used: list[Pt] = []
        for b in biz:
            if placed >= count:
                break
            th = math.radians(b["rot"])
            backx, backy = math.sin(th), -math.cos(th)  # the shop's BACK (inland, away from the road)
            step = bandmax - droad(b["x"], b["y"]) + h / 2 + depth_margin  # land just behind the WHOLE band
            ox, oy = b["x"] + backx * step, b["y"] + backy * step
            if ox < 55 or ox > self.W - 55 or oy < 88 or oy > self.H - 26:
                continue
            if self.bound and not point_in_poly(ox, oy, self.bound):
                continue
            if self._in_blocked(ox, oy) or self._near_corridor(ox, oy):
                continue
            mc = corners(ox, oy, w, h, b["rot"])  # (_in_blocked above already keeps it off the paddies)
            if any(overlap(mc, corners(px, py, pw, ph)) for (px, py, pw, ph, *_) in self.placed if abs(px - ox) + abs(py - oy) <= 150):  # rectangular, not circular: clears the tight band
                continue
            if any(math.hypot(ox - ux, oy - uy) < spread for ux, uy in used):
                continue  # keep the rich homes spread along the band
            self.building(ox, oy, w, h, "merchant_large", rot=b["rot"])
            used.append((ox, oy))
            placed += 1
        return placed
