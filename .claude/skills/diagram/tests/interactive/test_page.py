"""The HTML target's string layer (feature 134): wrapping, the ink census, and the page's contents.

What the browser test cannot cheaply prove per string is proved here: each tag shape wraps the way
`page.wrap` promises (a `Split` becomes a fill-only and a stroke-only copy; `Parts` wrap piece by
piece with the unclassed wrapper tags left bare), the census counts ink and only ink and reports
only what nobody ruled on, and the page embeds only the classes present and only the sibling
paragraphs whose other class is present (spec US4 scenario 4).
"""

from __future__ import annotations

import json
import re

import pytest

from l7r.diagram.interactive.classes import CLASSES
from l7r.diagram.interactive.page import explanations, hit_copies, hit_regions, ink_census, marks_region, merge_primitives, present_classes, render_page, unregistered_classes, wrap
from l7r.diagram.interactive.tags import Split

RECT = '<rect x="1" y="2" width="3" height="4" fill="#abc" stroke="#123"/>'


def test_wrap_of_a_plain_class() -> None:
    assert wrap(RECT, "farmhouse") == f'<g class="f f-farmhouse" data-k="farmhouse">{RECT}</g>'


def test_wrap_slugs_a_multiword_class_and_keeps_the_key_as_data() -> None:
    out = wrap(RECT, "storage shed")
    assert out.startswith('<g class="f f-storage-shed" data-k="storage shed">')


@pytest.mark.parametrize("tag", [None, "-"])
def test_unclassed_and_ruled_out_ink_is_left_bare(tag: str | None) -> None:
    assert wrap(RECT, tag) == RECT


def test_wrap_of_a_split_emits_a_fill_copy_and_a_stroke_copy() -> None:
    out = wrap(RECT, Split("paddy", "bund"))
    fill_copy, stroke_copy = out.split("</g>")[:2]
    assert 'data-k="paddy"' in fill_copy and 'fill="#abc"' in fill_copy and 'stroke="none"' in fill_copy
    assert 'data-k="bund"' in stroke_copy and 'stroke="#123"' in stroke_copy and 'fill="none"' in stroke_copy


def test_wrap_of_parts_wraps_each_piece_and_leaves_the_wrapper_tags_bare() -> None:
    parts = ((None, '<g transform="translate(1,2)">'), ("storage shed", RECT), ("farmhouse", RECT + RECT), (None, "</g>"))
    out = wrap("".join(s for _c, s in parts), parts)
    assert out.startswith('<g transform="translate(1,2)"><g class="f f-storage-shed"')
    assert out.endswith("</g></g>")
    assert out.count("<g class=") == 2


def test_census_counts_ink_per_class_and_reports_only_the_unruled() -> None:
    strings = [
        '<svg viewBox="0 0 1 1">',
        "<defs>",
        '<pattern id="p"><rect width="1" height="1"/></pattern>',
        "</defs>",
        RECT,
        RECT + RECT,
        '<clipPath id="c"><rect/></clipPath>',
        RECT,
        '<g opacity="0.5">',
        "</g>",
        "</svg>",
    ]
    tags = [None, None, None, None, "-", "farmhouse", None, None, None, None, None]
    counts, unclassed = ink_census(strings, tags)
    assert counts == {"-": 1, "farmhouse": 2}
    assert len(unclassed) == 1 and unclassed[0].startswith("<rect>")


def test_census_counts_a_split_once_and_parts_by_piece() -> None:
    strings = [RECT, RECT + RECT]
    tags = [Split("paddy", "bund"), (("storage shed", RECT), ("farmhouse", RECT))]
    counts, unclassed = ink_census(strings, tags)
    assert counts == {"paddy": 1, "storage shed": 1, "farmhouse": 1} and unclassed == []


def test_census_caps_the_unclassed_list_and_keeps_the_count() -> None:
    counts, unclassed = ink_census([RECT] * 25, [None] * 25)
    assert counts == {}
    assert len(unclassed) == 21 and unclassed[-1] == "... and 5 more"


def test_unregistered_classes_names_keys_the_registry_lacks() -> None:
    assert unregistered_classes({"farmhouse": 1, "-": 2, "flying castle": 3}) == ["flying castle"]


def test_present_classes_reads_every_tag_shape() -> None:
    tags = ["farmhouse", "-", None, Split("paddy", "bund"), ((None, "x"), ("byre", "y"))]
    assert present_classes(tags) == {"farmhouse", "paddy", "bund", "byre"}


def test_explanations_hold_only_present_classes_and_present_siblings() -> None:
    data = explanations({"windbreak", "copse", "farmhouse"})
    assert set(data) == {"windbreak", "copse", "farmhouse"}
    assert set(data["windbreak"]["siblings"]) == {"copse"}, "woodland commons is absent from this map, so it is not claimed"
    assert data["farmhouse"]["siblings"] == {}, "storage shed and byre are absent"
    assert data["windbreak"]["label_phrase"] == "historically accurate"
    assert data["windbreak"]["sources"] == list(CLASSES["windbreak"].sources)


def test_explanations_stub_an_unregistered_class_rather_than_dropping_it() -> None:
    data = explanations({"flying castle"})
    assert data["flying castle"]["label"] == "guess" and "no entry" in data["flying castle"]["what"]


def _page() -> str:
    strings = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">', RECT, RECT, RECT, "</svg>"]
    tags = [None, "farmhouse", Split("paddy", "bund"), "-", None]
    return render_page(strings, tags, "Testhamlet", {"ftpx": 1.0})


def test_the_page_is_self_contained() -> None:
    page = _page()
    assert "<!DOCTYPE html>" in page and "<title>Testhamlet - interactive map</title>" in page
    assert not re.search(r'(src|href)="(https?:)?//', page), "no external asset (spec FR-001)"
    assert "<style>" in page and "<script>" in page and 'id="map"' in page
    assert "<h1>" not in page and 'class="hint"' not in page, "no page header - the map carries its own placard (GM 2026-08-28)"


def test_the_page_embeds_only_the_present_classes() -> None:
    page = _page()
    blob = re.search(r'<script id="classes" type="application/json">(.*?)</script>', page, re.S)
    assert blob
    data = json.loads(blob.group(1).replace("<\\/", "</"))
    assert set(data) == {"farmhouse", "paddy", "bund"}
    assert set(data["paddy"]["siblings"]) == set() and set(data["bund"]["siblings"]) == set(), "bund beans are not on this page"


def test_the_page_escapes_a_closing_script_tag_inside_the_json() -> None:
    assert "</script>" not in json.dumps({"x": "</script>"}).replace("</", "<\\/")


def test_same_styled_lines_merge_into_one_path_and_keep_their_group_style() -> None:
    """The scrub's 225,000 blades are one <path> on the page (GM 2026-08-28, performance)."""
    g = '<g stroke="#A7A860" stroke-width="0.8"><line x1="1" y1="2" x2="3" y2="4"/><line x1="5" y1="6" x2="7" y2="8"/><line x1="9" y1="9" x2="9" y2="10"/></g>'
    assert merge_primitives(g) == '<g stroke="#A7A860" stroke-width="0.8"><path d="M1,2L3,4M5,6L7,8M9,9L9,10" fill="none"/></g>'


def test_same_styled_circles_merge_into_one_path_of_arcs() -> None:
    out = merge_primitives('<circle cx="10" cy="20" r="1.4" fill="#2F6B35"/><circle cx="30" cy="40" r="1.4" fill="#2F6B35"/>')
    assert out.startswith('<path d="M8.6,20a1.4,1.4 0 1 0 2.8,0a1.4,1.4 0 1 0 -2.8,0M28.6,40a') and out.endswith('fill="#2F6B35"/>')


def test_differently_styled_primitives_are_left_alone() -> None:
    lines = '<line x1="1" y1="2" x2="3" y2="4" stroke="#a" stroke-width="0.8"/><line x1="5" y1="6" x2="7" y2="8" stroke="#b" stroke-width="0.8"/>'
    assert merge_primitives(lines) == lines
    crowns = '<circle cx="1" cy="2" r="3" fill="#496733" stroke="#3C5526" stroke-width="0.8"/><circle cx="1" cy="2" r="1.2" fill="#364D22" opacity="0.55"/>'
    assert merge_primitives(crowns) == crowns


def test_the_merge_applies_to_classed_strings_only() -> None:
    lines = '<line x1="1" y1="2" x2="3" y2="4"/><line x1="5" y1="6" x2="7" y2="8"/>'
    assert "<path" in wrap(lines, "marsh")
    assert wrap(lines, None) == lines and wrap(lines, "-") == lines


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
    assert 'class="hit"' in wrap(lane, "village lane") and 'class="hit"' not in wrap(lane, "stream")
    paddy = '<polygon points="0,0 9,0 9,9" fill="#A6C398" stroke="#7A5A30" stroke-width="1.4"/>'
    out = wrap(paddy, Split("paddy", "bund"))
    assert out.count('class="hit"') == 1 and out.index('class="hit"') > out.index('data-k="bund"'), "the bund's hit copy rides in the bund group, above the paddy fill"


def test_the_marks_region_covers_only_cells_that_hold_a_mark() -> None:
    rects = marks_region(['<g><line x1="5" y1="5" x2="6" y2="6"/><line x1="30" y1="5" x2="31" y2="6"/><circle cx="100" cy="100" r="2"/></g>'], cell=24.0)
    assert rects == '<rect x="0" y="0" width="48" height="24"/><rect x="96" y="96" width="24" height="24"/>'
    assert marks_region([]) == ""


def test_the_scrub_region_comes_from_its_marks_not_its_polygon() -> None:
    strings = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300">',
        '<rect width="300" height="300" fill="#EFE3C2"/>',
        '<g stroke="#A7A860" stroke-width="0.8"><line x1="5" y1="5" x2="6" y2="9"/></g>',
        "</svg>",
    ]
    tags = [None, "-", "scrub and rough grazing", None]
    page = render_page(strings, tags, "T", {"ftpx": 1.0}, {"commons": [{"role": "grazing", "poly": [[0, 0], [300, 0], [300, 300], [0, 300]]}]})
    assert "<rect x=\"0\" y=\"0\" width=\"24\" height=\"24\"/>" in page and 'polygon class="hit"' not in page


def test_the_hit_widths_are_per_class_as_the_gm_tuned_them() -> None:
    """Bunds and beans twice the first cut, channels and the stream widened, lanes unchanged (GM 2026-08-28)."""
    bund = '<polygon points="0,0 9,0 9,9" fill="none" stroke="#7A5A30" stroke-width="1.4"/>'
    assert "stroke-width: 12.0px" in wrap(bund, Split("paddy", "bund")), "1.4 * 8 = 11.2 -> the 12 px floor"
    bead = '<circle cx="10" cy="20" r="1.4" fill="#2F6B35"/>'
    assert 'r="8.4"' in wrap(bead, "bund beans")
    ditch = '<path d="M1,1 L9,9" fill="none" stroke="#6C9CBE" stroke-width="2.5"/>'
    assert "stroke-width: 15.0px" in wrap(ditch, "field ditch")
    stream = '<path d="M1,1 L9,9" fill="none" stroke="#9CB4C8" stroke-width="7"/>'
    assert "stroke-width: 12.0px" in wrap(stream, "stream")
    lane = '<path d="M1,1 L9,9" fill="none" stroke="#C9AE79" stroke-width="5.0"/>'
    assert "stroke-width: 20.0px" in wrap(lane, "village lane")
