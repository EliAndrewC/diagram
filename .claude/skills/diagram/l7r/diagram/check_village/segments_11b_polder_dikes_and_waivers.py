"""Gate segments (polder dikes and waivers; keys 0581-0594) - bodies verbatim, registry order preserved."""

import math
from typing import Any

from .common_01_geometry import point_in_poly, seg_dist
from .common_03_capacity import _UNBOUND, WAIVER_META_CHECKS, WAIVER_MIN_REASON, _kept

# A polder's PERIMETER DIKE is an irregular hand-piled EARTHWORK, not a ruled line (GM 2026-07-22,
# researched: the wei-tian / dike-pond dike was dredged pond-mud heaped and packed, planted and
# breach-repaired, and the OUTER dike followed the natural water edge - the 'fish-scale polder' 鱼鳞圩
# form; the dead-straight uniform-width rectangle is a post-1949 industrial shape). So a polder /
# dike-pond map must record an `s.perimeter_dike` band (M['dikes']) whose width VARIES along its length
# (w_max >= ~1.4x w_min) - a reverted uniform-width stroke, or no dike at all, fires. Grounding:
# settlements.md 'Perimeter dike'.


def _seg_0581__polder_dike_is_earthwork(
    *,
    M: Any = _UNBOUND,
    _a: Any = _UNBOUND,
    _b: Any = _UNBOUND,
    _dgaps: Any = _UNBOUND,
    _dike_densify: Any = _UNBOUND,
    _dol: Any = _UNBOUND,
    _fl: Any = _UNBOUND,
    _flvals: Any = _UNBOUND,
    _i: Any = _UNBOUND,
    _inband: Any = _UNBOUND,
    _k: Any = _UNBOUND,
    _leaves: Any = _UNBOUND,
    _ln: Any = _UNBOUND,
    _ring: Any = _UNBOUND,
    _stray: Any = _UNBOUND,
    _ungapped: Any = _UNBOUND,
    _waters: Any = _UNBOUND,
    _wax: Any = _UNBOUND,
    _way: Any = _UNBOUND,
    _wdd: Any = _UNBOUND,
    _wdev: Any = _UNBOUND,
    _wfrac: Any = _UNBOUND,
    _wi: Any = _UNBOUND,
    _wl: Any = _UNBOUND,
    _woff: Any = _UNBOUND,
    _wol: Any = _UNBOUND,
    _wox: Any = _UNBOUND,
    _woy: Any = _UNBOUND,
    _wpoly: Any = _UNBOUND,
    _wtot: Any = _UNBOUND,
    band: Any = _UNBOUND,
    bx: Any = _UNBOUND,
    by: Any = _UNBOUND,
    c: Any = _UNBOUND,
    ch: Any = _UNBOUND,
    check: Any = _UNBOUND,
    cx: Any = _UNBOUND,
    cy: Any = _UNBOUND,
    d: Any = _UNBOUND,
    dk: Any = _UNBOUND,
    dks: Any = _UNBOUND,
    fields: Any = _UNBOUND,
    fx: Any = _UNBOUND,
    fy: Any = _UNBOUND,
    g: Any = _UNBOUND,
    gx: Any = _UNBOUND,
    gy: Any = _UNBOUND,
    h: Any = _UNBOUND,
    hh: Any = _UNBOUND,
    hw: Any = _UNBOUND,
    i: Any = _UNBOUND,
    in_dike: Any = _UNBOUND,
    meta: Any = _UNBOUND,
    on_dike: Any = _UNBOUND,
    out: Any = _UNBOUND,
    poly: Any = _UNBOUND,
    px: Any = _UNBOUND,
    py: Any = _UNBOUND,
    rp: Any = _UNBOUND,
    s: Any = _UNBOUND,
    step: Any = _UNBOUND,
    sx: Any = _UNBOUND,
    sy: Any = _UNBOUND,
    wmn: Any = _UNBOUND,
    wmx: Any = _UNBOUND,
    x: Any = _UNBOUND,
    y: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 581 (polder_channels_clear_of_dike, polder_dike_gapped_at_sluices, polder_dike_is_earthwork, polder_edges_wander, polder_floor_is_ring_interior, structures_clear_of_dike) - body verbatim from the legacy gate() (feature 022)."""
    if meta.get("field_archetype") in ("polder_grid", "mulberry_dike_fishpond"):
        dks = M.get("dikes") or []
        dk = dks[0] if dks else None
        wmn, wmx = (dk.get("w_min", 0.0), dk.get("w_max", 0.0)) if dk else (0.0, 0.0)
        check(
            "polder_dike_is_earthwork",
            bool(dk) and wmx >= 1.4 * max(1.0, wmn),
            f"a polder's perimeter dike must be an irregular earthwork band of VARYING width (drawn present: {bool(dk)}; width {wmn:.0f}-{wmx:.0f} px, want max >= 1.4x min) - a uniform-width or missing dike reads as a post-1949 ruled rectangle, not a hand-piled fish-scale polder",
        )

        # THE DIKES WANDER - NOT A MACHINE-PERFECT RECTANGLE (GM 2026-07-22, issue 4): a hand-dug wei-tian dike
        # followed the old water edge, so it runs at a slight ANGLE and gently CHANGES direction with the ground
        # (the 'fish-scale polder' 鱼鳞圩 read); a dead-straight axis-aligned block is the post-1949 land-
        # consolidation shape. Teeth: in the down-slope frame, most of the field OUTLINE must run OFF both axes -
        # a pure rectangle scores 0 (every edge axis-aligned) and fires, while the edge-wander block clears the
        # floor comfortably. Grounding: build_polder 'EDGE WANDER' + settlements.md 'Polder edge wander'.
        _wdd = math.radians(meta.get("down_deg", 90))
        _wox, _woy = math.cos(_wdd), math.sin(_wdd)
        _wol = fields[0]["outline"] if fields else []
        _wtot = _woff = 0.0
        for _wi in range(len(_wol) - 1):
            _wax, _way = _wol[_wi + 1][0] - _wol[_wi][0], _wol[_wi + 1][1] - _wol[_wi][1]
            _wl = math.hypot(_wax, _way)
            if _wl < 1:
                continue
            _wdev = min(abs(_wax * _wox + _way * _woy), abs(_wax * _woy - _way * _wox)) / _wl  # 0 = on an axis
            _wtot += _wl
            if _wdev > 0.05:  # > ~3 deg off the nearer axis
                _woff += _wl
        _wfrac = _woff / _wtot if _wtot else 0.0
        check(
            "polder_edges_wander",
            bool(fields) and _wfrac >= 0.30,
            f"a polder's dikes must WANDER, not run axis-perfect - only {_wfrac:.0%} of the field outline runs off-axis (want >=30%); a dead-straight rectangle is the post-1949 consolidation shape, not a hand-dug fish-scale polder",
        )

        # THE GREEN FLOOR IS THE RING-CANAL INTERIOR, not the dike-boundary envelope (GM 2026-07-22): the
        # greenery must be bounded by the OUTERMOST irrigated channels (the feeder/drain/toe ring), so it
        # follows the wavering ring instead of a separate envelope rectangle that drifts in and out of it.
        # Teeth: every recorded field-floor vertex must lie within ~8 px of a ring channel centerline; the
        # pre-fix envelope floor sat ~9-22 px out at the dike boundary and fires. Grounding: build_polder's
        # `floor` (the concatenated ring sides) + comb_base_fill + settlements.md 'Polder edge wander'.
        _ring = [d["poly"] for d in M.get("field_ditches", []) if d.get("seg") in ("feeder", "drain", "e_toe", "w_toe")]
        _flvals = list(M.get("comb_floors", {}).values())
        if _ring and _flvals:
            _fl = _flvals[0]
            _stray = [(round(fx), round(fy)) for fx, fy in _fl if min(seg_dist(fx, fy, rp[i], rp[i + 1]) for rp in _ring for i in range(len(rp) - 1)) > 8]
            check(
                "polder_floor_is_ring_interior",
                not _stray,
                f"the polder's green field floor must be the INTERIOR of the ring canal (bounded by the outermost channels), but {len(_stray)} floor vertex/vertices sit >8 px off the ring at {_stray[:3]} - a floor drawn to the dike-boundary envelope drifts in and out of the wavering ring",
            )

        # THE RING CANAL RUNS ON THE INNER TOE, CLEAR OF THE DIKE (GM 2026-07-22, researched: the trunk
        # irrigation/drainage canal rings the block on the INSIDE toe of the perimeter dike, on the field
        # side - "一河围田 / one river surrounds the field"; outside the dike is the wild water it holds back,
        # so no channel runs out there, and water crosses the dike ONLY at gated sluices at the inlet +
        # outfall). So an irrigation channel buried in the dike earthwork is wrong. Teeth: count field-ditch
        # vertices falling inside the recorded dike band; a couple (the inlet/outfall sluice crossings) are
        # fine, but a trunk running along inside the dike (the old s=+-12 feeder, ~36 pts in the band) fires.
        if dk:
            band = dk["outline"]
            in_dike = sum(1 for ch in M.get("field_ditches", []) for x, y in ch["poly"] if point_in_poly(x, y, band))
            check(
                "polder_channels_clear_of_dike",
                in_dike <= 4,
                f"{in_dike} irrigation-channel point(s) run through the dike earthwork (want <= 4, the inlet/outfall sluice crossings) - the polder RING CANAL runs on the INNER TOE of the dike (field side), not buried in the dike body; water crosses the dike only at the sluices",
            )

            # WATER CROSSES THE DIKE ONLY THROUGH A DUG GAP (GM 2026-07-22, issue 1): the inlet + outfall sluices
            # pass THROUGH a notch cut in the earthwork, not OVER the top of the unbroken bank (which read as the
            # water running uphill onto the dike and back down). Teeth: a THROUGH-CROSSER - a water line with a
            # densified point inside the dike band AND a vertex outside the field outline (so it genuinely runs
            # from the field, through the dike, to the far / off-map side) - must have a recorded gap within
            # ~26 px of where it enters the band. The pre-fix dike recorded NO gaps, so every crosser fires. The
            # incidental ring-canal clipping the inner toe at a concave bend is NOT a crosser (it never leaves the
            # field), so it is not required to have a gap. Grounding: perimeter_dike gaps + settlements.md.
            _dgaps = dk.get("gaps", [])
            _dol = fields[0]["outline"] if fields else []

            def _dike_densify(poly: Any, step: float = 4.0) -> list[tuple[float, float]]:
                out: list[tuple[float, float]] = []
                for _i in range(len(poly) - 1):
                    _a, _b = poly[_i], poly[_i + 1]
                    _ln = math.hypot(_b[0] - _a[0], _b[1] - _a[1])
                    _steps = max(1, int(_ln / step))
                    for _k in range(_steps):
                        out.append((_a[0] + (_b[0] - _a[0]) * _k / _steps, _a[1] + (_b[1] - _a[1]) * _k / _steps))
                if poly:
                    out.append((poly[-1][0], poly[-1][1]))
                return out

            _waters = [c["poly"] for c in M.get("field_ditches", [])] + [s["poly"] for s in M.get("streams", [])] + [c["poly"] for c in M.get("channels", [])]
            _ungapped: list[tuple[int, int]] = []  # type: ignore[no-redef]
            for _wpoly in _waters:
                _inband = [(x, y) for x, y in _dike_densify(_wpoly) if point_in_poly(x, y, band)]
                _leaves = bool(_dol) and any(not point_in_poly(px, py, _dol) for px, py in _wpoly)
                if _inband and _leaves and not any(math.hypot(bx - gx, by - gy) <= 26 for bx, by in _inband for gx, gy in _dgaps):
                    _ungapped.append((round(_inband[0][0]), round(_inband[0][1])))
            check(
                "polder_dike_gapped_at_sluices",
                not _ungapped,
                f"{len(_ungapped)} channel(s) cross the dike with no dug gap at {_ungapped[:4]} - a polder's inlet/outfall sluice passes THROUGH a notch cut in the earthwork bank, not over the top of it; every through-crossing needs a recorded dike gap",
            )

            # STRUCTURES + WINDBREAK KEEP OFF THE DIKE (GM 2026-07-22): the dike is a raised earthwork bank,
            # not building ground, so no farmhouse footprint and no windbreak grove clump may sit ON it (the
            # bank carries only its own soil-binding trees). perimeter_dike registers the band as a placement
            # keep-out; this verifies it. A house corner or a grove clump center inside the dike band fires.
            on_dike = []
            _keep = dk.get("keepout") or band  # the crest's few chords the placer kept off (feature 140); the band for an older manifest
            for h in M.get("houses", []):
                if h.get("on_dike"):
                    continue  # a dike_top_houses house LIVES on the bank (settlement_form 'dike_top') - dike_top_houses_on_the_dike verifies it instead
                hw, hh = h.get("w", 40) / 2, h.get("h", 26) / 2
                if any(point_in_poly(h["x"] + sx * hw, h["y"] + sy * hh, _keep) for sx in (-1, 1) for sy in (-1, 1)):
                    on_dike.append(("house", round(h["x"]), round(h["y"])))
            for g in M.get("village_groves", []):
                on_dike += [("grove", round(cx), round(cy)) for cx, cy in g.get("clumps", []) if point_in_poly(cx, cy, band)]
            check(
                "structures_clear_of_dike",
                not on_dike,
                f"structure(s)/windbreak clump(s) sitting ON the perimeter dike earthwork: {on_dike[:4]} - the dike is a raised bank, not building ground; houses and the windbreak keep off it",
            )
    return _kept(
        locals(),
        (
            '_dgaps',
            '_dike_densify',
            '_dol',
            '_fl',
            '_flvals',
            '_inband',
            '_leaves',
            '_ring',
            '_stray',
            '_ungapped',
            '_waters',
            '_wax',
            '_way',
            '_wdd',
            '_wdev',
            '_wfrac',
            '_wi',
            '_wl',
            '_woff',
            '_wol',
            '_wox',
            '_woy',
            '_wpoly',
            '_wtot',
            'band',
            'bx',
            'by',
            'c',
            'ch',
            'cx',
            'cy',
            'd',
            'dk',
            'dks',
            'fx',
            'fy',
            'g',
            'gx',
            'gy',
            'h',
            'hh',
            'hw',
            'i',
            'in_dike',
            'on_dike',
            'out',
            'px',
            'py',
            'rp',
            's',
            'sx',
            'sy',
            'wmn',
            'wmx',
            'x',
            'y',
        ),
    )


# DIKE-TOP HOUSES REALLY SIT ON THE DIKE (GM 2026-07-24, settlements.md 'Polder siting Q&A'): a house
# tagged `on_dike` (placed by dike_top_houses, settlement_form 'dike_top') is exempt from
# structures_clear_of_dike - so the tag must not be a free pass. Every tagged house's center must lie
# ON the recorded dike band (or within the small platform slack - the widened-crest house pad bulges
# the band a touch). A tagged house floating off the bank, or tagged houses on a map with no dike at
# all, fires.


# THE WATERWARD FLANKS ARE WET (GM 2026-07-24, settlements.md 'Polder siting Q&A'): outside a polder's
# dike is the FLUCTUATING WATER it was reclaimed from - lake, creek, reed marsh, mudflat - except on a
# landward flank where the polder abuts the natural shore (the margin-polder case; reclamation advanced
# FROM the shore). A map declares its water-facing flanks in meta.waterward (compass letters, frame
# axes); each declared flank must then actually READ wet - sampled just outside the dike band's extreme
# on that side, most points must land in recorded wet cover (a waterside/toe marsh poly or the header
# pond). Undeclared maps skip (a non-polder map has no dike to face water).


# A polder's PARCEL fabric must VARY (researched 2026-07-21; grounding in build_polder's docstring).
# The surveyed chessboard was the CANAL grid; the parcels inside were a private-tenure patchwork
# (Buck 1929-33: mean parcel ~1 mu, several scattered per farm; dike-ponds accreted 挖塘培基,
# household by household). Identical uniform cells are the 20th-century consolidation look (hojo
# seibi 30x100m), so a block of them - the original Kuwabata/Enokida render - must fire. Applies to
# both polder-geometry archetypes; measured from the manifest's per-plot [along, cross] spans, and a
# polder manifest that records NO parcel geometry fails rather than passes by omission.


# A RIBBON-VALLEY field (feature 005 US4) is LONG and NARROW - a thin strip strung down a confined valley -
# so its extent ALONG the fall is much greater than its extent ACROSS it. That aspect is the archetype's
# teeth: a ribbon reads as a winding valley strip, not a broad fan/block.


# SOFT ADVISORY (default-on; a map opts out with meta(crop_advisory=False)): a single feature that could
# be moved to free a significantly tighter crop. NOT a failure - it never enters `fails` or gates the map;
# it just prints a hint. (Unlike a hard invariant, e.g. houses-clear-of-moats, this is a default we accept.)


# ---- the waiver hatch audits itself (GM 2026-07-27; the "why" is at WAIVER_MIN_REASON) ------
# Runs LAST, because it can only judge the waivers once every check has had its chance to fire.


def _seg_0590___wv_thin(*, _waivers: Any = _UNBOUND, k: Any = _UNBOUND, v: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 590 (_wv_thin, k, v) - body verbatim from the legacy gate() (feature 022)."""
    _wv_thin = sorted(k for k, v in _waivers.items() if not isinstance(v, str) or len(v.strip()) < WAIVER_MIN_REASON)
    return _kept(locals(), ('_wv_thin', 'k', 'v'))


def _seg_0591__waivers_are_documented(*, _wv_thin: Any = _UNBOUND, check: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 591 (waivers_are_documented) - body verbatim from the legacy gate() (feature 022)."""
    check(
        "waivers_are_documented",
        not _wv_thin,
        f"waiver(s) with no real explanation: {_wv_thin} - a waiver's value is the REASON this particular place "
        f"overrides the rule ({WAIVER_MIN_REASON}+ chars of it), and it is the only record that the map broke the "
        f"rule on purpose. Write the history ('the Emperor lies southeast, so the samurai quarter...'), not 'by design'",
    )
    return _kept(locals(), ())


def _seg_0592___wv_stale(*, _waived: Any = _UNBOUND, _waivers: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 592 (_wv_stale) - body verbatim from the legacy gate() (feature 022)."""
    _wv_stale = sorted(set(_waivers) - set(_waived) - WAIVER_META_CHECKS)
    return _kept(locals(), ('_wv_stale',))



def _seg_0594_500__waterward_strips_run_off_the_frame(
    *,
    M: Any = _UNBOUND,
    check: Any = _UNBOUND,
    meta: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    waterward_strips_run_off_the_frame_bad: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 0594_500 (waterward_strips_run_off_the_frame) - a polder's waterward reed strip is wild
    water CONTINUING, so its outer edge must lie outside the rendered view.

    The strip is not a feature with an edge: outside the dike is the fluctuating lake or creek the polder
    was reclaimed from, and it goes on past the sheet (`settlements/archetypes.md`, "Polder waterward
    fringe"). It used to be drawn to the canvas edge, which made that true by construction and wasted the
    scatter - on Kuwabata the crop kept 74 px of the 1,880 px drawn, and the discarded reeds cost 18 s of
    a 40 s gen. Feature 139 T55 cut it to a `WATERWARD_DEPTH` band off the dike face, and a band CAN stop
    inside the frame: then the reader sees a straight line where wild water stops being wild. Nothing
    checked that, which is this engine's standing failure shape ("a rule that cannot fire looks exactly
    like a rule that passes"), so the check is the guard - measured per DECLARED flank (`meta.waterward`),
    against the drawn view, on the map that has one. TEETH: a strip that ends inside the view fails.
    Grounding: `hamletgen.stage_waterward`, `consts.WATERWARD_DEPTH`; caught by settlement-review
    2026-08-29."""
    if scale in ("hamlet", "village", "town"):
        waterward_strips_run_off_the_frame_bad = []
        _wwf = meta.get("waterward") or []
        _wwv = meta.get("view")
        _wws = [m for m in M.get("marshes", []) if m.get("role") == "waterside" and m.get("poly")]
        if _wwf and _wwv and _wws:
            _vx0, _vy0, _vw, _vh = (float(v) for v in _wwv)
            for _wwm in _wws:
                _wxs = [float(q[0]) for q in _wwm["poly"]]
                _wys = [float(q[1]) for q in _wwm["poly"]]
                # the strip belongs to the flank its OUTER edge faces; each flank's edge must clear the view
                _reach = {"W": min(_wxs) <= _vx0, "E": max(_wxs) >= _vx0 + _vw, "N": min(_wys) <= _vy0, "S": max(_wys) >= _vy0 + _vh}
                if not any(_reach[_f] for _f in _wwf if _f in _reach):
                    waterward_strips_run_off_the_frame_bad.append((round(min(_wxs)), round(min(_wys))))
        check(
            "waterward_strips_run_off_the_frame",
            not waterward_strips_run_off_the_frame_bad,
            f"waterward reed strip(s) at {waterward_strips_run_off_the_frame_bad[:3]} STOP inside the drawn view - the un-reclaimed water outside a dike goes on past the sheet, so a strip that ends in frame draws a straight line where wild water stops being wild; widen `WATERWARD_DEPTH` (hamletgen/consts.py) until every declared flank's strip clears the view",
        )
    return _kept(locals(), ("waterward_strips_run_off_the_frame_bad",))

def _seg_0593__waivers_are_live(*, _ran: Any = _UNBOUND, _wv_stale: Any = _UNBOUND, check: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 593 (waivers_are_live) - body verbatim from the legacy gate() (feature 022)."""
    check(
        "waivers_are_live",
        not _wv_stale,
        f"stale waiver(s): {_wv_stale} - each names a check that did NOT fail on this map (it now passes, this "
        f"scale never runs it, or the name is a typo/renamed). Delete it: a waiver kept past the defect it "
        f"excused is how a map ends up exempt from rules nobody remembers it was breaking. "
        f"Checks that ran: {len(_ran)}",
    )
    return _kept(locals(), ())
