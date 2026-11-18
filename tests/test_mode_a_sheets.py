"""THE SWEEP (feature 254, spec FR-004): every Mode A sheet in the live pool, through every registered
check that applies to its declared type - the shared layer and the type's own.

WHY IT IS HERE AND NOT IN `gate/`. It parses a few small SVGs: milliseconds, no roll, no tooling, so
by `tests/CLAUDE.md`'s rule it is a quick-tree test and `make quick` sweeps the pool on every change -
which is what the GM asked for when they said a hand-authored diagram should still have "automated
checks that we run on them". Before this test the audit ran only when a session remembered to run it,
and the pool had never been swept: the drafts had no scale bar and drew their walls where the checks
could not read them, and one hand-drawn sheet sat below a band the record itself called "in-band".

A failure names the sheet, the check and the compliant fix, in that order, because that is what the
session fixing it needs first. A sheet whose tier has no declaration is NOT swept silently: the pool
classifier's ratchet in `test_villages.py` refuses it as `unknown` first.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from l7r.diagram.buildings import types as bt
from l7r.diagram.pipeline import poolmaps
from l7r.diagram.tools import pack_audit as pa
from l7r.diagram.tools.pack_audit import mapmatch, onmap, size_marks
from l7r.diagram.tools.pack_audit import registry as R
from tests import _sheets

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _sheet(b: poolmaps.MapBundle) -> str:
    """The bundle's svg, a declared generated exception's regenerated when it is absent OR stale (`tests/_sheets.py`:
    a draft's svg is gitignored, and a copy older than the engine once failed here as if it were a regression)."""
    btype = bt.by_tier(b.tier)
    return _sheets.fresh(b.path(".svg"), b.gen, btype is not None and b.stem in btype.generated_exceptions)


def _bundles() -> list[poolmaps.MapBundle]:
    return [b for b in poolmaps.bundles(trees=(poolmaps.LIVE_TREE,), kinds={"compound"}, skill_dir=SKILL) if b.tier in bt.tiers()]


@pytest.mark.parametrize("bundle", _bundles(), ids=lambda b: b.stem)
def test_every_mode_a_sheet_passes_its_checks(bundle: poolmaps.MapBundle) -> None:
    svg = _sheet(bundle)
    assert os.path.isfile(svg), f"{bundle.tier}/{bundle.stem}: no svg on disk and it is not a declared generated exception"
    with open(svg, encoding="utf-8") as fh:
        text = fh.read()
    ctx = R.Context(pa.parse_svg(text), text, bt.by_tier(bundle.tier), pa.read_form(svg), pa.read_on_map(svg))
    failures = [f"{bundle.stem}: {ch.name}: {f} - fix: {ch.fix}" for ch, found in R.run_checks(ctx, bundle.tier) for f in found]
    assert not failures, "\n".join(failures)


def test_the_sweep_covers_every_declared_tier_that_has_a_sheet() -> None:
    """A declared tier with a folder is swept; a declared tier with no folder yet is the exemplar's to fill."""
    swept = {b.tier for b in _bundles()}
    live = os.path.join(SKILL, "pool")
    for tier in bt.tiers():
        if os.path.isdir(os.path.join(live, tier)):
            assert tier in swept, f"{tier} has a pool folder but no bundle reached the sweep"
    assert "magistracies" in swept


def test_a_generated_sheet_is_regenerated_when_missing_or_stale_and_a_hand_drawn_one_never(tmp_path: Path) -> None:
    """The stale-copy failure of 2026-09-26: a sheet older than its generator or the engine is written again."""
    svg, gen = tmp_path / "a.svg", tmp_path / "a.gen.py"
    gen.write_text("", encoding="utf-8")
    ran: list[list[str]] = []

    def run(cmd: list[str], **_kw: object) -> None:
        ran.append(cmd)
        svg.write_text("<svg/>", encoding="utf-8")

    assert _sheets.fresh(str(svg), str(gen), False, 0.0, run) == str(svg) and ran == [], "hand-drawn: never run"
    _sheets.fresh(str(svg), str(gen), True, 0.0, run)
    assert len(ran) == 1 and ran[0][-1] == str(gen), "missing: generated"
    _sheets.fresh(str(svg), str(gen), True, 0.0, run)
    assert len(ran) == 1, "fresh: left alone"
    os.utime(svg, (1, 1))
    _sheets.fresh(str(svg), str(gen), True, 0.0, run)
    assert len(ran) == 2, "older than its generator: generated again"
    assert _sheets.is_stale(str(svg), str(gen), os.path.getmtime(svg) + 10), "older than the engine is stale"
    assert _sheets.newest_engine_mtime() > 0


def _notes(bundle: poolmaps.MapBundle) -> str:
    path = bundle.path(".notes.md")
    if not os.path.isfile(path):
        return ""
    with open(path, encoding="utf-8") as fh:
        return fh.read()


@pytest.mark.parametrize("bundle", _bundles(), ids=lambda b: b.stem)
def test_a_sheet_whose_subject_a_map_records_says_so(bundle: poolmaps.MapBundle) -> None:
    """Feature 294 B24 (US5's home for plan-sheet agreement): where a pool or legacy map records a subject of the sheet's
    tier at its place (`<place>-<type>`, under the tier's key), the notes carry the `**On map**:` declaration - so the
    map check holds the sheet to the map - or opt out of it in so many words, `**On map**: none - <why>`."""
    maps = mapmatch.maps_recording(bundle.stem, bundle.tier)
    if maps:
        assert onmap.declares(_notes(bundle)), (
            f"{bundle.stem}: {', '.join(maps)} records its subject under {mapmatch.TIER_KEYS[bundle.tier]} and the notes carry no "
            f"`**On map**:` line - declare it (`{onmap.GRAMMAR}`) or opt out (`{onmap.OPT_OUT}`)"
        )


def test_the_map_record_rule_finds_the_sheets_it_is_for() -> None:
    """Non-vacuity: the two sheets whose places a map records are found, the two no map records are not."""
    assert mapmatch.maps_recording("hoshigaoka-shrine", "country-shrines") == ["legacy-hand-authored-pool/villages/hoshigaoka/hoshigaoka.json"]
    assert mapmatch.maps_recording("ubame-magistracy", "magistracies") == ["legacy-hand-authored-pool/towns/ubame/ubame.json"]
    assert mapmatch.maps_recording("ochiba-magistracy", "magistracies") == [] and mapmatch.maps_recording("hayakawa-magistracy", "magistracies") == []


# Feature 294 B15b's sweep (a count of tubs, privies or wells typed in the notes' current prose agrees with what the sheet draws) moved
# to the Mode A engine crate with the Python it called (feature 449 T170): `rust/mode_a/src/census/pool_check.rs`, `make rust-test`.


@pytest.mark.parametrize("bundle", _bundles(), ids=lambda b: b.stem)
def test_the_size_table_lists_every_tagged_kind(bundle: poolmaps.MapBundle) -> None:
    """Feature 294 B15c (the audit's Z5 row): every kind the sheet tags is sized by a row - a rect's, or a circle's, path's
    or line's (`size_marks.mark_rows`) - so `size-audit` enumerates every sized feature from the table."""
    svg = _sheet(bundle)
    with open(svg, encoding="utf-8") as fh:
        missing = size_marks.untabled_kinds(fh.read())
    assert not missing, f"{bundle.stem}: tagged kinds no size-table row carries (a kind on a caption alone): {missing} - tag the drawn element with the kind, or the caption with the kind it names"


# --- the draft's tub seat (feature 449 T182): pinned here, the kept test file the placer's sheets are swept in -------------


def test_a_tub_seat_by_a_door_is_tried_nearest_first_across_the_faces() -> None:
    """The by-the-door search tried the faces N, S, E, W in turn: a door on the east face near the north-east corner took a
    north-face seat 4.5 ft from it before the east-face seat 2.5 ft from it."""
    from l7r.diagram.compound_model import BuildingSpec, Placed
    from l7r.diagram.compound_parts import seats_within_reach

    hut = Placed(BuildingSpec("hall", "lord", 20.0, 10.0, "inner", "N", feature="office hall"), 0.0, 0.0)
    seats = seats_within_reach(hut, [(20.0, 2.0)])
    assert seats[0] == ("E", 0.2), seats[:3]


def test_a_door_kind_with_no_door_takes_no_tub_and_a_bath_takes_its_court_face() -> None:
    """A door-kind building whose door found no seat fell to the doorless seats and took a court-face tub with no door drawn;
    it takes none, and the bath (no door kind) keeps the court face."""
    from l7r.diagram.compound_model import BuildingSpec, Placed
    from l7r.diagram.compound_parts import doored_tub_seats

    karo = Placed(BuildingSpec("karo's house", "lord", 37.0, 23.0, "inner", "divider", feature="karo's house"), 0.0, 0.0)
    bath = Placed(BuildingSpec("bath", "service", 10.0, 8.0, "inner", "N"), 0.0, 0.0)
    assert doored_tub_seats(karo, []) == []
    assert doored_tub_seats(karo, [(18.0, 0.0)])
    assert doored_tub_seats(bath, []) is None


def test_touching_corridor_pieces_are_one_passage_with_one_unbroken_outline() -> None:
    """The round-trip's three corridor pieces were three closed dotted rects, read as three rooms (the corridor's glyph-check);
    a stepped run's union is now one ring with no edge between the pieces and no pen-up move (the hand-sheet reader joins a
    path's vertices in order, and a jump read as a stroke across the passage that set its caption outside the house)."""
    from l7r.diagram.compound import _touching_groups, _union_outline

    pieces = [(0.0, 26.0, 36.0, 6.0), (36.0, 26.0, 29.0, 6.0), (62.0, 29.0, 28.0, 6.0), (0.0, 60.0, 5.0, 5.0)]
    assert sorted(map(sorted, _touching_groups(pieces))) == [[0, 1, 2], [3]]
    assert _union_outline(pieces[:3], 0.0, 0.0) == ["M 0 78 L 195 78 L 195 87 L 270 87 L 270 105 L 186 105 L 186 96 L 0 96 L 0 78 Z"]
    corner = _union_outline([(0.0, 0.0, 1.0, 1.0), (1.0, 1.0, 1.0, 1.0)], 0.0, 0.0)  # pieces meeting at one corner: rings, never a jump
    assert all(d.count("M") == 1 for d in corner)
    assert sum(d.count("L") for d in corner) == 8


def test_the_round_trips_corridor_is_drawn_as_one_passage() -> None:
    """The emitter, not only its helpers: the round-trip's three corridor pieces keep a fill each, tagged for the checks,
    with no outline of their own; one dotted ring round them and one caption."""
    import re

    (bundle,) = [b for b in _bundles() if b.stem == "ochiba-roundtrip-test"]
    with open(_sheet(bundle), encoding="utf-8") as fh:
        svg = fh.read()
    pieces = re.findall(r'<rect [^>]*data-kind="residence corridor"[^>]*/>', svg)
    assert len(pieces) == 3 and all('stroke="none"' in r for r in pieces), pieces
    dotted = re.findall(r'<(\w+) [^>]*stroke-dasharray="1 2"[^>]*>', svg)
    assert dotted == ["path"], dotted
    ring = re.search(r'<path d="([^"]*)"[^>]*stroke-dasharray="1 2"', svg)
    assert ring is not None and ring.group(1).count("M") == 1, ring
    assert len(re.findall(r">corridor</text>", svg)) == 1
