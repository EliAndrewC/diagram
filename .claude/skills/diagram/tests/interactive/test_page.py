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
from l7r.diagram.interactive.page import explanations, ink_census, present_classes, render_page, unregistered_classes, wrap
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
