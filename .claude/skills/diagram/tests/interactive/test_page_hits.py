"""The page's hover layer - the invisible regions and widened copies that take the pointer (split from test_page.py
when it passed the 1,000-line bar, feature 266 follow-up)."""

from __future__ import annotations

import pytest

from l7r.diagram.interactive.classes import NOT_HIGHLIGHTED
from l7r.diagram.interactive.page import (
    hit_copies,
    hit_regions,
    marks_region,
    render_page,
    wrap,
)
from l7r.diagram.interactive.tags import Split

pytestmark = pytest.mark.renders  # tests OF the page's raster / the plates: they render tiny synthetic pictures on purpose (feature 213)

RECT = '<rect x="1" y="2" width="3" height="4" fill="#abc" stroke="#123"/>'


def test_hit_regions_come_from_the_recorded_footprints_of_present_classes_only() -> None:
    m = {
        "commons": [{"role": "grazing", "poly": [[0, 0], [10, 0], [10, 10]]}, {"role": "woodland", "poly": [[20, 0], [30, 0], [30, 10]]}],
        "bamboo_stands": [{"role": "homestead", "poly": [[0, 20], [5, 20], [5, 25]]}],
        "marshes": [{"role": "toe", "poly": [[40, 40], [50, 40], [50, 50]]}],
    }
    out = hit_regions(m, {"scrub and rough grazing", "homestead bamboo", "marsh"})
    assert out.count("<polygon") == 3 and 'data-k="woodland commons"' not in out, "the absent class gets no region"
    assert 'fill="none" style="pointer-events: fill"' in out and 'class="hit"' in out
    assert hit_regions(None, {"marsh"}) == "" and hit_regions({"marshes": [{"role": "toe"}]}, {"marsh"}) == ""


def test_the_page_puts_the_hit_regions_right_above_the_sheet() -> None:
    strings = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">', '<rect width="10" height="10" fill="#EFE3C2"/>', RECT, "</svg>"]
    tags = [None, "-", "marsh", None]
    page = render_page(strings, tags, "T", {"ftpx": 1.0}, {"marshes": [{"role": "toe", "poly": [[0, 0], [9, 0], [9, 9]]}]})
    sheet = page.index('fill="#EFE3C2"')
    hit = page.index('class="hit"')
    ink = page.index(RECT)
    assert sheet < hit < ink


def test_thin_marks_get_a_fat_invisible_hit_copy() -> None:
    lane = '<path d="M1,1 L9,9" fill="none" stroke="#C9AE79" stroke-width="5.0"/>'
    out = hit_copies(lane)
    assert out == '<path d="M1,1 L9,9" fill="none" class="hit" style="pointer-events: stroke; stroke-width: 20.0px"/>'
    bead = '<g opacity="0.85"><circle cx="10" cy="20" r="1.4" fill="#2F6B35"/></g>'
    assert hit_copies(bead) == '<circle cx="10" cy="20" r="4.2" fill="none" class="hit" style="pointer-events: fill"/>'
    blades = '<g stroke="#A7A860" stroke-width="0.8"><line x1="1" y1="2" x2="3" y2="4"/></g>'
    assert 'stroke-width: 6.0px' in hit_copies(blades), "the floor: four times 0.8 is under 6 px"
    assert hit_copies('<polygon points="0,0 1,0 1,1" fill="#abc"/>') == "", "a filled shape already takes the pointer"


def test_widened_classes_carry_their_hit_copies_and_others_do_not() -> None:
    lane = '<path d="M1,1 L9,9" fill="none" stroke="#C9AE79" stroke-width="5.0"/>'
    assert 'class="hit"' in wrap(lane, "village lane") and 'class="hit"' not in wrap(lane, "pond")
    paddy = '<polygon points="0,0 9,0 9,9" fill="#A6C398" stroke="#7A5A30" stroke-width="1.4"/>'
    out = wrap(paddy, Split("paddy", "bund"))
    assert out.count('class="hit"') == 1 and out.index('class="hit"') > out.index('data-k="bund"'), "the bund's box rides in the bund group, above the paddy fill"


def test_the_marks_region_covers_only_cells_that_hold_a_mark() -> None:
    rects = marks_region(['<g><line x1="5" y1="5" x2="6" y2="6"/><line x1="30" y1="5" x2="31" y2="6"/><circle cx="100" cy="100" r="2"/></g>'], cell=24.0, grow=0)
    assert rects == '<rect x="0" y="0" width="48" height="24" fill="none"/><rect x="96" y="96" width="24" height="24" fill="none"/>'
    assert marks_region([]) == ""


def test_the_hit_widths_are_per_class_as_the_gm_tuned_them() -> None:
    """Bunds and beans twice the first cut, channels and the stream widened, lanes unchanged (GM 2026-08-28)."""
    bund = '<polygon points="0,0 9,0 9,9" fill="none" stroke="#7A5A30" stroke-width="1.4"/>'
    assert "stroke-width: 12.0px" in wrap(bund, Split("paddy", "bund")), "1.4 * 8 = 11.2 -> the 12 px floor"
    bead = '<circle cx="10" cy="20" r="1.4" fill="#2F6B35"/>'
    assert 'r="8.4"' in wrap(bead, "bund beans")
    ditch = '<path d="M1,1 L9,9" fill="none" stroke="#6C9CBE" stroke-width="2.5"/>'
    assert "stroke-width: 15.0px" in wrap(ditch, "irrigation ditch")
    stream = '<path d="M1,1 L9,9" fill="none" stroke="#9CB4C8" stroke-width="7"/>'
    assert "stroke-width: 12.0px" in wrap(stream, "stream")
    lane = '<path d="M1,1 L9,9" fill="none" stroke="#C9AE79" stroke-width="5.0"/>'
    assert "stroke-width: 20.0px" in wrap(lane, "village lane")


def test_the_hit_layer_sits_above_the_ink_it_widens() -> None:
    """One layer for every widened box, emitted after the drawn record and before `</svg>`."""
    strings = ['<svg viewBox="0 0 20 20">', '<line x1="1" y1="1" x2="9" y2="9" stroke="#37637F" stroke-width="2.4"/>', "</svg>"]
    tags = [NOT_HIGHLIGHTED, "pond sluice", None]
    page = render_page(strings, tags, "t")
    assert page.index('class="hit"') > page.index('stroke-width="2.4"')
    assert page.index('class="hit"') < page.index("</svg>")


def test_a_woods_outline_lies_above_the_scrubs_grown_cells() -> None:
    """GM 2026-09-27: a gap between two trees inside the windbreak stopped lighting the windbreak, because the scrub's
    grown mark cells were stacked above the belt's own outline. The recorded footprints now ride above the marks'
    regions, so inside the belt the pointer finds the belt."""
    blades = '<g stroke="#A7A860" stroke-width="0.8"><line x1="50" y1="50" x2="51" y2="52"/></g>'
    crown = '<circle cx="60" cy="60" r="5" fill="#4E7A3A"/>'
    strings = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">', '<rect width="200" height="200" fill="#EFE3C2"/>', blades, crown, "</svg>"]
    tags = [None, "-", "scrub and rough grazing", "windbreak", None]
    manifest = {
        "commons": [{"role": "grazing", "poly": [[0, 0], [200, 0], [200, 200], [0, 200]]}],
        "village_groves": [{"role": "windbreak", "poly": [[40, 40], [120, 40], [120, 120], [40, 120]]}],
    }
    page = render_page(strings, tags, "T", {"ftpx": 1.0}, manifest)
    scrub = page.index('data-k="scrub and rough grazing"><g class="hit"')
    belt = page.index('data-k="windbreak"><polygon class="hit"')
    assert scrub < belt, "the belt's outline is drawn after - so above - the scrub's cells"
