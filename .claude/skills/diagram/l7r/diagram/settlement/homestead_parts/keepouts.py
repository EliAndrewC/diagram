"""Split from settlement/homestead_parts.py by feature 173 - see this package's CLAUDE.md for the index."""

import math
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from .._geom import boxed_seg_hit, seg_dist

if TYPE_CHECKING:
    from ..core import Settlement


class KeepoutsMixin:
    def _corridor_buffers(self: Settlement, extra: float = 0) -> list[Any]:  # type: ignore[misc]
        """Lane / town-street / road centerlines with their (half-width + `extra`) keep-out - the corridors that
        trees, scrub, and other vegetation must not be drawn ON. Returns [(polyline, buffer), ...]."""
        corr = [([tuple(p) for p in ln["pts"]], ln.get("w", 6) / 2 + extra) for ln in self.M.get("lanes", [])]
        corr += [([tuple(p) for p in s["pts"]], s.get("w", 10) / 2 + extra) for s in self.M.get("town_streets", [])]
        # alleys + the city ring road are ways too (GM 2026-07-24: yard furniture kept off "roads"
        # must mean EVERY tread - a rail tip on an alley is the same defect as one on the road)
        corr += [([tuple(p) for p in a["pts"]], a.get("w", 4) / 2 + extra) for a in self.M.get("alleys", [])]
        if self.M.get("ring_road"):
            corr.append(([tuple(p) for p in self.M["ring_road"]], self.M.get("ring_road_width", 20) / 2 + extra))
        if self.M.get("road"):
            corr.append(([tuple(p) for p in self.M["road"]], self.M.get("road_width", 30) / 2 + extra))
        return corr

    def _watercourse_segs(self: Settlement, pad: float = 2.0, channel_margin: float = 0.0) -> list[tuple[Any, float]]:  # type: ignore[misc]
        """Every drawn watercourse as (polyline, half-width + pad) pairs in boxed_segs shape: streams,
        channels, and the comb laterals' drawn truth (M['drawn_channels'] - added 2026-08-16, GM,
        Inashiro: grass tufts stood ON the head-race, because the scatter knew only the hairline
        topology record in M['channels'], w 2.5, while the drawn lateral ran ~14 wide on its own
        filleted post-clip polyline - the "same manifest source" trap, settlements.md 'PLANK
        BRIDGES'). A tapered lateral is split by `waterfields.taper_pieces` - ONE piece per SEGMENT
        at its arc-correct width, the very same call `field_channel` inks it with, so the corridor
        and the stroke it protects cannot disagree. Factored so the per-point test (_on_watercourse) and the
        ground-cover scatters' pre-boxed grids provably test the same geometry. `channel_margin`
        widens the IRRIGATION courses only (channels + drawn laterals, never streams) - the commons
        scatter passes the cut-bank margin here (_BANK_MARGIN_FT says why banks are bare and why a
        natural stream bank is not)."""
        out: list[tuple[Any, float]] = [(wc["poly"], wc.get("w", 6) / 2 + pad) for wc in self.M.get("streams", [])]
        out += [(wc["poly"], wc.get("w", 6) / 2 + pad + channel_margin) for wc in self.M.get("channels", [])]
        for ch in self.M.get("drawn_channels", []):
            p, w0, w1 = ch["pts"], ch["w0"], ch["w1"]
            if len(p) < 2:
                continue
            if abs(w1 - w0) < 0.2:  # drawn as ONE stroke at w0 (field_channel's uniform branch)
                out.append((p, w0 / 2 + pad + channel_margin))
            else:  # drawn per SEGMENT at its arc-correct width - the SAME ladder field_channel inks
                from l7r.diagram.waterfields import taper_pieces  # local: the engine packages are peers, imported lazily

                for piece, wk in taper_pieces(p, w0, w1):
                    out.append((piece, wk / 2 + pad + channel_margin))
        return out

    def _on_watercourse(self: Settlement, px: float, py: float, pad: float = 2.0, near: Any = None) -> bool:  # type: ignore[misc]
        """True if (px, py) lies ON a drawn watercourse - a stream, an irrigation channel, or a comb
        lateral (within its drawn half-width + `pad`; _watercourse_segs says which registries and
        why). Decorative ground-cover (scrub, reeds) skips it: vegetation never draws OVER open
        water, the same reason it skips the lane tread and the pond. `near` is an optional
        pre-boxed accessor (boxed_grid(boxed_segs(self._watercourse_segs())).near) for callers that
        test per scatter POINT - the same hoist-the-invariant discipline as their other keep-outs
        (fld_b / cor_b); verdicts are identical either way (the grid prunes, it never decides)."""
        if near is not None:
            if boxed_seg_hit(px, py, near(px, py)):
                return True
        else:
            for p, half in self._watercourse_segs(pad):
                if any(seg_dist(px, py, p[i], p[i + 1]) < half for i in range(len(p) - 1)):
                    return True
        # ... and the fengshui crescent pond's open water (found 2026-07-21: scrub tufts drew ON the
        # half-moon pond - the skip knew M['pond'] and the linear courses but not this water body)
        return any(math.hypot(px - cp["cx"], py - cp["cy"]) < cp["r"] + pad for cp in self.M.get("crescent_ponds", []))

    # THE URBAN-CLEARANCE HALO (GM 2026-07-21, Hoshizora): loose ground-cover (scrub, reeds) stays out of
    # the swept/trodden ground AROUND every occupied structure, not merely off its footprint. WHY: the daily
    # foot traffic, sweeping, and fuel/fodder-gathering pressure of the residents strips brush from the
    # ground nearest the dwellings first - dooryards are packed earth, the alleys between packed town houses
    # are walked bare, and a settlement's whole built-up fabric reads CLEARED; scrub survives only past this
    # halo, on the outskirts. 30 ft around structures (a working dooryard's depth; also closes the gaps in
    # packed districts, whose ~40-48 ft house spacing leaves no strip wider than two halos), 20 ft around a
    # wellhead (the most-trodden, spill-puddled ground in any settlement), 8 ft around tended ground plots
    # (a garden's or threshing yard's maintained edge). Constants are REAL FEET, converted at the map grain.
    _CROP_MARGIN_FT = 6.0
    # CROP MARGIN (GM 2026-08-15: scrub was overlapping dry crop plots and crowding crop edges).
    # Scrub stands OFF the crops: the scatter skips every paddy AND dry plot, plus this margin of
    # real feet around every crop edge. WHY 6 ft - the bund plus one cut swath: a paddy levee
    # (keihan/aze; Chinese tian'geng) is a ~1-2 ft earthen ridge (~3 ft where it carries a footpath,
    # azemichi), and the levee grass and the strip beside the crop were CUT several times a season
    # for fodder/green manure, so woody scrub never establishes within about a scythe's swath
    # (~1-2 m) of the field edge - the same ~1 m clean strip that separates crop from boundary
    # vegetation in traditional field-margin practice. Land hunger keeps East Asian margins NARROW,
    # so 6 ft (~1.8 m) total, not a wide verge. Tall glyphs (scraggly pines, woodland crowns) add
    # their own drawn reach on top so no tip leans over the crop. Grass-tuft blade TIPS are the
    # deliberate exception (settlement-review, 2026-08-16): a blade is 2.4-4.2*bs px, so at the
    # coarser tiers a tip can lean up to a few real feet over the margin line - accepted, because
    # grass leaning over a bund is real; bases and tall-glyph reach are what the rule enforces.
    # Full grounding: settlements/vegetation.md "Scrub stands off the crops".
    _BANK_MARGIN_FT = 6.0
    # CUT-BANK MARGIN (GM 2026-08-16, Inashiro second pass: tufts seeded in the 10-16 ft berm
    # strip between the dry hem plots and the supply channels - legal under the drawn-width water
    # skip + the crop margin, which between them left a bare sliver mid-strip). The commons scatter
    # stands its bases this many real feet off the drawn water EDGE of every IRRIGATION channel
    # (M['channels'] + M['drawn_channels']). WHY 6 ft, and why channels only: a supply channel's
    # bank is MAINTAINED ground - walked for sluice work and bund upkeep, and its grass scythed for
    # fodder on the same rotation as the field margins - so established scrub tufts/brush there are
    # as wrong as on a bund; one scythe swath (~1.8 m) is the same figure the crop margin rests on
    # (_CROP_MARGIN_FT above). STREAMS and the reed marsh deliberately take NO margin: a natural
    # bank is vegetated to the water's edge, and the 2026-08-16 settlement-review pass explicitly
    # praised the absence of a sterile halo on the brooks. Full grounding:
    # research/vegetation.md "The cut bank".
    _HALO_STRUCT_FT = 30.0
    _HALO_WELL_FT = 20.0
    _HALO_PLOT_FT = 8.0
    # occupied structures (people live/work in them: full dooryard halo) vs tended ground plots (kept clear
    # to their edge, but nobody sweeps a 30 ft apron around a vegetable bed)
    _HALO_STRUCT_KEYS = ("houses", "buildings", "storehouses", "flophouses", "byres", "farm_sheds", "religious", "shrines", "manors", "ministries", "inspection_stations", "theater_stage")
    # `theater_stage` added 2026-07-26: hinterland scrub was drawn ON the stage's roof, and it took an
    # independent reviewer's eye to see it because SCRUB IS NOT RECORDED IN THE MANIFEST - no gate check
    # and no manifest audit can reach this class of defect at all. (This halo is deliberately NARROWER
    # than the canopy rule below: it sweeps a 30 ft dooryard apron, so every key added here also strips
    # ground cover for 30 ft around it and moves `town_margins_clothed`. Roofed civic/trade premises are
    # therefore NOT bulk-added here - they are handled by the canopy contract, which is about ink on a
    # roof rather than about how much of the sheet reads as worked.)
    _HALO_PLOT_KEYS = ("gardens", "threshing_yards")
    # NO TREE IS DRAWN ON A ROOF OR A WELLHEAD (GM 2026-07-25). Every ROOFED structure on the map,
    # plus the wellheads - the keep-out that every canopy crown is tested against (_crown_covers).
    # Open-air work grounds (threshing yards, kitchen gardens, tanning/dye yards, cremation grounds)
    # are deliberately NOT here: they have their own sun-corridor and clearance rules, and a tree
    # overhanging the CORNER of a yard is a real thing, while a tree drawn on a roof is just a
    # building you can no longer see.
    # OPEN-AIR WORKING GROUND - deliberately NOT a canopy keep-out. These records are a patch of
    # ground, not a roof: a tree overhanging the corner of a yard is a real thing, and each of these
    # has its own clearance and sun-corridor rules. Every OTHER solid feature is a keep-out by
    # default (below), so this tuple is the only place a new feature can legitimately opt out - and
    # `test_every_roofed_feature_is_a_canopy_keepout` fails if a key is in neither.
    _CANOPY_OPEN_AIR_KEYS = (
        "gardens",  # a dooryard bed; a bough over its edge is normal
        "threshing_yards",  # a swept work floor abutting its own farmhouse
        "tanning_yards",  # a pit yard on a bank - open ground by definition
        "dye_yards",  # drying racks in the open
        "lumber_yards",  # stacked timber in the open
        "charcoal_yards",  # a cart yard whose roofed sheds are interior detail, not the record
        "refining_forges",  # an open-sided works; the record is its whole working ground
        "cremation_grounds",  # open ground with a pyre platform
        "execution_grounds",  # bare, unfenced waste ground - the bareness IS the feature
        "punishment_spots",  # a patch of tamped earth on a verge
        "boundary_markers",  # a stone
        "ossuaries",  # a low earth mound
        "cemeteries",  # an open burial ground; trees among graves are correct
        "kosatsuba",  # a board on a post at the verge
    )
    # NO TREE IS DRAWN ON A ROOF OR A WELLHEAD (GM 2026-07-25; DERIVED 2026-07-26). Every roofed
    # structure plus the wellheads - the keep-out every canopy crown is tested against (_crown_covers).
    # This was a HAND LIST until a reviewer found scrub on a theater stage; the list is now the overlap
    # registry minus the open-air exemptions above, so a new roofed feature is covered by default and
    # forgetting is impossible. Same move that retired `ring_road_kept_clear`'s hand list.
    # Features that are not in check_village's _OVERLAP_STRUCTS at all (they are targets or exempt
    # there) but are still roofed things a crown must not cover.
    _CANOPY_EXTRA_KEYS = ("merchant_estates", "wall_towers", "gate_structs", "theater_stage")
    # Every ROOFED premises from the overlap registry. settlement.py cannot import check_village
    # (circular), so this tuple is written out - and
    # `test_every_roofed_feature_is_a_canopy_keepout` holds it against the real registry, failing
    # with the offending key by name if a new feature is in neither this nor _CANOPY_OPEN_AIR_KEYS.
    # The TEST is the ratchet; the tuple is just the data.
    _CANOPY_ROOFED_KEYS = (
        "farm_fixtures",  # the privy, bath shed and coop are roofed; the stack, heap and hokora are not, but none takes a tree (feature 133 T53-T59)
        "precinct_halls",  # the sovereign precinct program - roofed halls (021)
        "terraces",  # a retainer terrace is one continuous roof over its household cells
        "granaries",  # the capital's wharf granaries - kura rows, roofed like the town's dict-recorded one
        "mausoleums",
        "fire_towers",
        "drum_towers",
        "breweries",
        "oil_presses",
        "pawnshops",
        "bathhouses",
        "kilns",
        "farriers",
        "martial_halls",
        "dojos",
        "castles",  # a walled compound like a manor - its court is blank by doctrine, not open ground
        "castle_towers",  # yagura are roofed buildings
    )
    _CANOPY_STRUCT_KEYS = _HALO_STRUCT_KEYS + _CANOPY_EXTRA_KEYS + _CANOPY_ROOFED_KEYS

    def _canopy_keepouts(self: Settlement, bbox: tuple[float, float, float, float]) -> tuple[list[tuple[float, float, float, float]], list[tuple[float, float, float]]]:  # type: ignore[misc]
        """Every drawn BUILDING footprint (as x, y, half-w, half-h) and WELLHEAD (as x, y, r) near `bbox` -
        the keep-out a tree CROWN may not cover. Distinct from _urban_keepouts, the 30 ft swept halo the
        ground-cover scatters honor: a tree may stand hard against a wall (real groves hug the eaves), it
        may only not be DRAWN ON the roof - so the halo here is zero. A rotated structure is covered
        conservatively by its half-diagonal square. Prefiltered to `bbox`, since the caller tests every
        crown of a stand against this list."""
        bx0, by0, bx1, by1 = bbox
        rects: list[tuple[float, float, float, float]] = []
        for k in self._CANOPY_STRUCT_KEYS:
            for o in self._reclist(k):
                # the DRAWN box (a location marker like the kosatsuba draws at a legibility floor
                # above its true footprint, and overlap here is about drawn pixels - same reason the
                # wells use vr over r)
                hw, hh = o.get("vw", o["w"]) / 2, o.get("vh", o["h"]) / 2  # pyrefly: ignore[unsupported-operation]  # dict.get(k, Any-default) typed Any|None by pyrefly, Any by mypy - research 142 R5
                if o.get("rot"):
                    hw = hh = math.hypot(hw, hh)
                if o["x"] + hw >= bx0 and o["x"] - hw <= bx1 and o["y"] + hh >= by0 and o["y"] - hh <= by1:
                    rects.append((o["x"], o["y"], hw, hh))
        circles = [(o["x"], o["y"], o.get("vr", o["r"])) for o in self.M.get("wells", []) if bx0 <= o["x"] <= bx1 and by0 <= o["y"] <= by1]
        return rects, circles

    @staticmethod
    def _crown_covers(x: float, y: float, r: float, rects: Sequence[tuple[float, float, float, float]], circles: Sequence[tuple[float, float, float]], pad: float = 0.0) -> bool:
        """Whether a canopy crown of radius `r` centered at (x, y) would cover any keep-out from
        _canopy_keepouts - i.e. whether drawing this one tree would hide a building or a wellhead.
        `pad` is a placement-side margin ONLY: the manifest rounds crown coordinates to 0.1 px, so a
        crown drawn exactly TANGENT to a wall can round to a hair of overlap and fire the check that
        re-reads it. Drawing passes a small pad so a kept crown is unambiguously clear; the check
        itself stays exact (pad 0), which is what keeps its teeth."""
        for cx, cy, hw, hh in rects:
            dx, dy = max(abs(x - cx) - hw, 0.0), max(abs(y - cy) - hh, 0.0)
            if dx * dx + dy * dy < (r + pad) ** 2:
                return True
        return any((x - wx) ** 2 + (y - wy) ** 2 < (r + pad + wr) ** 2 for wx, wy, wr in circles)

    def _record_crowns(self: Settlement, crowns: Sequence[tuple[float, float, float]]) -> None:  # type: ignore[misc]
        """Record drawn canopy crowns as a flat [x, y, r, ...] run in M['tree_crowns'] - the manifest
        record of EVERY tree this map draws, which is what structures_clear_of_trees / wells_clear_of_trees
        test. Flat rather than per-tree dicts because a to-scale map draws thousands of them (see
        settlements.md, 'No tree is drawn on a roof')."""
        for x, y, r in crowns:
            self.M["tree_crowns"] += [round(x, 1), round(y, 1), round(r, 1)]

    def _reclist(self: Settlement, key: str) -> list[dict[str, Any]]:  # type: ignore[misc]
        """Records under `key`, whether the manifest stores a LIST of them or a single dict.

        A few features are singletons stored as a bare dict (`theater_stage`, `governor_mansion`) -
        which is why their keys are singular. Iterating one of those blindly yields its string KEYS,
        and `o["w"]` then raises `TypeError: string indices must be integers`. check_village has the
        same shape in `_OVERLAP_SINGLETONS`; this is the settlement-side counterpart.
        """
        rec = self.M.get(key)
        if isinstance(rec, dict):
            return [rec]
        return [r for r in (rec or []) if isinstance(r, dict)]

    def _urban_keepouts(self: Settlement, bbox: tuple[float, float, float, float]) -> tuple[list[tuple[float, float, float, float]], list[tuple[float, float, float]]]:  # type: ignore[misc]
        """Axis-aligned keep-out rects + wellhead keep-out circles for the urban-clearance halo (see the
        constants above), built from every structure/plot/well recorded in M so far. A rotated structure is
        covered conservatively by its half-diagonal square. Prefiltered to `bbox` (the cover poly's extent) -
        a keep-out that cannot touch the scatter region would only slow the per-point loop (a to-scale town
        carries ~200 structures and each cover poly samples thousands of points). Returned as (rects,
        circles) for the ground-cover scatters' per-point tests."""
        bx0, by0, bx1, by1 = bbox
        rects: list[tuple[float, float, float, float]] = []
        for keys, halo_ft in ((self._HALO_STRUCT_KEYS, self._HALO_STRUCT_FT), (self._HALO_PLOT_KEYS, self._HALO_PLOT_FT)):
            halo = halo_ft * self.bscale
            for k in keys:
                for o in self._reclist(k):
                    hw, hh = o["w"] / 2, o["h"] / 2
                    if o.get("rot"):
                        hw = hh = math.hypot(hw, hh)  # conservative: the rotated rect fits in its half-diagonal square
                    rx0, ry0, rx1, ry1 = o["x"] - hw - halo, o["y"] - hh - halo, o["x"] + hw + halo, o["y"] + hh + halo
                    if rx1 >= bx0 and rx0 <= bx1 and ry1 >= by0 and ry0 <= by1:
                        rects.append((rx0, ry0, rx1, ry1))
        wh = self._HALO_WELL_FT * self.bscale
        circles = [(o["x"], o["y"], o.get("vr", o["r"]) + wh) for o in self.M.get("wells", []) if bx0 - 40 <= o["x"] <= bx1 + 40 and by0 - 40 <= o["y"] <= by1 + 40]
        return rects, circles
