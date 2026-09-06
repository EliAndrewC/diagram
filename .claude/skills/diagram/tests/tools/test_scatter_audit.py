"""Tests for scatter_audit.py (feature 108) - written RED-first against the contract in
specs/108-review-loop-efficiency/contracts/scatter-audit-cli.md.

Fixture strategy (research.md R5): parse/adjudication logic is fed SVG text + manifest dicts
directly (the pure-logic surface); the real engine renders a miniature settlement for the
integration case so the audit and the engine provably agree; `main` is exercised through tmp
files. The committed pool bytes are never touched."""

import json
import os
from pathlib import Path

import pytest

from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement._geom import CROWN_FILLS
from l7r.diagram.tools import scatter_audit as sa

HERE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))


def _mini_channel_settlement(seed: int = 1) -> Settlement:
    """A tiny real-engine map: one wide drawn lateral + commons scatter laid over its ground."""
    s = Settlement(600, 800, seed=seed)
    s.meta(name="A", scale="village", ftpx=1.0)  # ftpx recorded, as every real pool map records it
    s.field_channel([(300, 100), (310, 700)], "#6C9CBE", 14.0, 14.0)
    s.commons([(60, 60), (560, 60), (560, 760), (60, 760)], role="grazing")
    return s


def _manifest(**kw):
    m = {"meta": {"ftpx": 1.0}, "streams": [], "channels": [], "drawn_channels": [], "fields": [], "dry_plots": []}
    m.update(kw)
    return m


# ---- parsing ---------------------------------------------------------------------------------


def test_parse_counts_every_family_from_engine_emission():
    s = _mini_channel_settlement()
    fams = sa.parse_bases("".join(s.out))
    assert len(fams["blade"]) > 100  # grazing commons = tufts of 3 blades each
    assert len(fams["dot"]) > 0
    assert len(fams["pine"]) > 0  # role="grazing" draws scraggly pines
    assert fams["blade"] and all(isinstance(x, float) for x, _ in fams["blade"])


def test_parse_counts_one_base_per_blade_line_three_per_tuft():
    svg = '<g stroke="#A7A860" stroke-width="0.8"><line x1="10.0" y1="20.0" x2="10.5" y2="16.0"/><line x1="10.0" y1="20.0" x2="9.4" y2="16.2"/><line x1="10.0" y1="20.0" x2="10.1" y2="15.9"/></g>'
    fams = sa.parse_bases(svg)
    assert fams["blade"] == [(10.0, 20.0)] * 3  # one BasePoint per blade line, tips ignored


def test_parse_reeds_pine_trunks_and_crowns_but_not_companion_ink():
    """...and the CROWN fill is taken from the engine's own `CROWN_FILLS`, never written out here.

    This test used to hardcode `#7C9856` - a color the engine had stopped painting - which is
    exactly why the drift survived: the parser carried a stale copy of the palette and the test
    carried the SAME stale copy, so the two agreed with each other and disagreed with the map. The
    audit reported `crown=0 ... violations: 0` on maps recording thousands of crowns and this test
    stayed green throughout. A fixture built from the source of truth cannot pin a mistake."""
    svg = (
        '<g stroke="#6E9377" stroke-width="0.8"><line x1="5.0" y1="6.0" x2="5.0" y2="2.0"/></g>'
        '<line x1="40.0" y1="50.0" x2="40.0" y2="38.0" stroke="#7A6A48" stroke-width="1.1"/>'  # pine trunk
        '<line x1="40.0" y1="44.0" x2="37.0" y2="46.0" stroke="#6E8452" stroke-width="1.0"/>'  # branch: ignored
        f'<circle cx="80.0" cy="90.0" r="8.0" fill="{CROWN_FILLS[0]}" stroke="#4C6234" stroke-width="0.7"/>'  # crown - the fill comes from the ENGINE
        '<circle cx="77.4" cy="87.4" r="3.4" fill="#A6BA79" fill-opacity="0.55"/>'  # highlight: ignored
        '<ellipse cx="80.0" cy="92.0" rx="8.0" ry="5.8" fill="#59703E" fill-opacity="0.30"/>'  # shadow: ignored
        '<circle cx="60.0" cy="61.0" r="2.0" fill="#94A063" fill-opacity="0.85"/>'  # brush dot
    )
    fams = sa.parse_bases(svg)
    assert fams["reed"] == [(5.0, 6.0)]
    assert fams["pine"] == [(40.0, 50.0)]
    assert fams["crown"] == [(80.0, 90.0)]
    assert fams["dot"] == [(60.0, 61.0)]
    assert fams["blade"] == []


# ---- adjudication ----------------------------------------------------------------------------


def _one_dot_svg(x, y):
    return f'<circle cx="{x}" cy="{y}" r="2.0" fill="#94A063" fill-opacity="0.85"/>'


# ---- CLI -------------------------------------------------------------------------------------


def _write_map(tmp_path, svg_body, manifest):
    (tmp_path / "t.svg").write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 800">{svg_body}</svg>')
    (tmp_path / "t.json").write_text(json.dumps(manifest))
    return str(tmp_path / "t")


def test_crown_fills_covers_every_recorded_crown(pool_tier_glob):
    """`CROWN_FILLS` claims to be every color the engine paints a RECORDED crown with. That claim
    has rotted twice in one day - first the audit's own stale copy (0% coverage), then a
    replacement that missed every woodland-commons canopy (63%) while its comment asserted the old
    fills were unpainted. So the claim is TESTED against real ink rather than trusted: roll a map
    and compare crowns parsed against crowns recorded. A palette that loses a drawing site narrows
    the count, and this fails instead of quietly reporting a clean family."""
    import glob

    from l7r.diagram.pipeline import poolmaps

    checked = 0
    for gen in sorted(glob.glob(os.path.join(HERE, "pool", pool_tier_glob, "*.gen.py"))):  # the tier's own maps under --tier
        if poolmaps.classify(gen) != "scripted":
            continue  # frozen maps predate the palette and are never re-rendered
        stem = gen[: -len(".gen.py")]
        if not (os.path.isfile(stem + ".svg") and os.path.isfile(stem + ".json")):
            continue  # live renders are gitignored; a clean checkout simply has none
        recorded = len(json.loads(Path(stem + ".json").read_text()).get("tree_crowns") or []) // 3
        if not recorded:
            continue
        parsed = sa.parse_bases(Path(stem + ".svg").read_text(), families=("crown",))["crown"]  # crowns only: the guard is about CROWN_FILLS
        assert len(parsed) >= recorded, f"{os.path.basename(stem)}: parsed {len(parsed)} crowns against {recorded} recorded - CROWN_FILLS has lost a drawing site"
        # ...AND ON THE CANVAS, which counting cannot tell you. The count half of this guard passed
        # at 1446 >= 1446 for weeks while ~78% of the crown family was adjudicated at LOCAL
        # coordinates: `_draw_grove` emits its canopy inside `<g transform="translate(cx,cy)">`, and
        # `parse_bases` read `cx`/`cy` raw, so a crown at world (710.9, 1815.8) was judged at
        # (4.9, -14.2) and the audit reported 0 violations on a map that had 5 crown bases inside the
        # crop margin (settlement-review, Mizuguchi 2026-08-18). A family that sees the right NUMBER
        # of things somewhere else is exactly as blind as one that sees nothing.
        #
        # EVERY PARSED CROWN MUST SIT NEAR SOMETHING THE MANIFEST RECORDS, and finding an invariant
        # that actually separates a good parse from a broken one took two wrong tries, both recorded
        # because each looked obviously right:
        #   - comparing parsed bases to the recorded `tree_crowns` points fails, because that key
        #     records the tree STANDS' canopy while a grove clump records only its CENTRE in
        #     `village_groves[].clumps` - barely a fifth of parsed crowns coincide with a recorded
        #     one under ANY parser, broken or fixed;
        #   - an on-canvas test fails too, because a local offset is small (+-25 px) and so still
        #     lands inside a 2000 px canvas. Off-canvas is what it LOOKS like, not what it IS.
        # What a mis-parsed crown cannot do is land near a recorded ANCHOR - a stand crown or a clump
        # center - because its coordinates are an offset, not a position. Measured on the four
        # scripted hamlets: 0 orphans with the transform resolved, 1,503-2,387 without.
        _flat = json.loads(Path(stem + ".json").read_text()).get("tree_crowns") or []
        anchors = [(_flat[i], _flat[i + 1]) for i in range(0, len(_flat), 3)]
        for _g in json.loads(Path(stem + ".json").read_text()).get("village_groves") or []:
            anchors += [(c[0], c[1]) for c in _g["clumps"]]
        # ...and the DIKE-POND BANKS (feature 150): a mulberry_dike_fishpond map draws tens of
        # thousands of coppiced mulberry crowns along its recorded `dikeponds[].bank` rings, which
        # are crowns to `CROWN_FILLS` but stand on no `tree_crowns` or clump record - the bank
        # polygon is their anchor.
        for _dp in json.loads(Path(stem + ".json").read_text()).get("dikeponds") or []:
            anchors += [(float(q[0]), float(q[1])) for q in _dp.get("bank") or []]
        # ...and the PERIMETER DIKE, planted with willow and mulberry rows along its band
        # (`perimeter_dike`; research/archetypes.html "Why dikes were planted at all") - anchored on
        # the recorded `dikes[].outline`.
        for _dk in json.loads(Path(stem + ".json").read_text()).get("dikes") or []:
            anchors += [(float(q[0]), float(q[1])) for q in _dk.get("outline") or []]
        reach = 60.0
        buckets: dict[tuple[int, int], list[tuple[float, float]]] = {}
        for ax, ay in anchors:
            buckets.setdefault((int(ax // reach), int(ay // reach)), []).append((ax, ay))
        orphans = []
        for px, py in parsed:
            gx, gy = int(px // reach), int(py // reach)
            if not any((px - ax) ** 2 + (py - ay) ** 2 <= reach * reach for dx in (-1, 0, 1) for dy in (-1, 0, 1) for ax, ay in buckets.get((gx + dx, gy + dy), ())):
                orphans.append((px, py))
        assert not orphans, (
            f"{os.path.basename(stem)}: {len(orphans)} parsed crown bases sit near NOTHING the manifest records, e.g. {orphans[:3]} "
            f"- parse_bases is reading a family in LOCAL coordinates (an unresolved transform), so the audit is judging it in the wrong place"
        )
        checked += 1
    # A FRESH CLONE HAS NO LIVE RENDERS (gitignored; `make done` never draws one), so this used to
    # fail on every new checkout - the second of feature 131's two "known gitignored-artifact gap"
    # failures. A guard with nothing to check is SKIPPED, visibly, with the route to arming it.
    if not checked:
        pytest.skip("no live scripted map has both a .svg and a .json in this checkout - `make map` regenerates the reference hamlet with its render, then this guard has something to check")


def test_parse_bases_honours_the_families_filter_and_stops_before_the_crown_transform() -> None:
    """Feature 174: the `families` argument, which every caller so far leaves at its default.

    Its purpose is the comment's own: "a crown guard need not scan 220k blades". Three branches
    close together - the blade/reed skip, the dot and pine guards, and the early return before the
    crown transform resolution, which is the expensive half. Asserted by what comes back, so the
    test would fail if the filter simply stopped filtering.
    """
    # the REAL markers, copied from the module's own patterns (`_BLADE_GROUP`, `_DOT`) - an
    # invented colour parses as nothing, which would make this test pass by finding zero of everything
    svg = '<g stroke="#A7A860"><line x1="10" y1="20" x2="12" y2="16"/></g><circle cx="30" cy="40" r="1.1" fill="#94A063"/>'
    only_dots = sa.parse_bases(svg, families=("dot",))
    assert only_dots["dot"], "the family that was asked for is parsed"
    assert only_dots["blade"] == [], "and the ones that were not are left empty rather than scanned"
    assert only_dots["crown"] == [], "the crown transform pass is skipped entirely"

    everything = sa.parse_bases(svg)
    assert everything["dot"] and everything["blade"], "the default still parses every family"


def test_parse_bases_resolves_a_crowns_group_TRANSLATE_into_its_true_position() -> None:
    """Feature 174, and the defect the module's own docstring records (Mizuguchi, settlement-review
    2026-08-18): ~78% of the crown family was adjudicated in the wrong place while a count guard
    passed, because a crown drawn inside `<g transform="translate(tx,ty)">` records its coordinates
    relative to the group. The offset lookup is what resolves it.

    Both branches of that lookup: a crown INSIDE a translated span takes the offset, and one outside
    every span takes (0, 0). A test of the inside case alone would pass with the fallback broken.
    """
    from l7r.diagram.settlement._geom import CROWN_FILLS

    fill = CROWN_FILLS[0]
    svg = f'<circle cx="5" cy="7" r="9" fill="{fill}"/><g transform="translate(100,200)"><circle cx="5" cy="7" r="9" fill="{fill}"/></g>'
    crowns = sorted(sa.parse_bases(svg, families=("crown",))["crown"])
    assert crowns == [(5.0, 7.0), (105.0, 207.0)], "the untranslated crown keeps its own coordinates; the translated one is moved"
