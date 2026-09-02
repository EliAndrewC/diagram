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

from l7r.diagram.interactive.classes import CLASSES, NOT_HIGHLIGHTED, PLACE
from l7r.diagram.interactive.glossary import GLOSSARY
from l7r.diagram.interactive.notes import EMPTY, MapNotes
from l7r.diagram.interactive.page import (
    CAVEAT_LEAD,
    explanations,
    glossary_for,
    hit_copies,
    hit_layer,
    hit_regions,
    ink_census,
    marks_region,
    merge_primitives,
    present_classes,
    render_page,
    unregistered_classes,
    wrap,
)
from l7r.diagram.interactive.sources import citations, registry, research_sources, section_sources, urls_of
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
    assert data["windbreak"]["siblings"] == ["copse"], "woodland commons is absent from this map, so it is not claimed; siblings are link keys now"
    assert data["farmhouse"]["siblings"] == [], "storage shed and byre are absent"
    # the presumption of accuracy (feature 156): an accurate class announces nothing, and the liberty
    # its record discloses rides in `caveat` instead, to be shown after the what and the why
    assert data["windbreak"]["label"] == "accurate", "the classification is still recorded (constitution XII)"
    assert data["windbreak"]["lead"] == "", "an accurate class leads with what the feature is, not with a claim"
    # the windbreak is one of the seven whose record discloses no liberty, so it shows no caveat at
    # all (settlement-review, 2026-08-29); the copse beside it on this map does have one
    assert data["windbreak"]["caveat"] == "", "the windbreak discloses no liberty - see test_classes"
    assert data["copse"]["caveat"] == CAVEAT_LEAD + CLASSES["copse"].caveat and CLASSES["copse"].caveat
    assert data["windbreak"]["sources"] == research_sources(CLASSES["windbreak"].entry) and "forests-2020" in data["windbreak"]["sources"]
    assert len(data["windbreak"]["refs"]["forests-2020"]["text"]) > 20


def test_the_wet_paddy_is_explained_apart_from_the_paddy_and_only_when_present() -> None:
    """Feature 158 (GM 2026-08-29): the blue plots are "its own type of thing, and it deserves its own
    explanation". Both classes on one map means two entries and a link each way; a map with no blue
    plot must show neither the class nor a sibling paragraph claiming a distinction from an absent one."""
    both = explanations({"paddy", "wet paddy"})
    assert set(both) == {"paddy", "wet paddy"}
    assert both["paddy"]["what"] != both["wet paddy"]["what"], "two kinds, two explanations"
    assert both["wet paddy"]["siblings"] == ["paddy"] and "wet paddy" in both["paddy"]["siblings"]
    # the disclosure the GM's reader needs: on a comb field the tint marks a SHARE of the wet ground.
    # It rides in the caveat, so the modal leads with what the plot is (feature 156).
    assert both["wet paddy"]["caveat"], "the drawing liberty reaches the modal"
    green_only = explanations({"paddy"})
    assert set(green_only) == {"paddy"}
    assert "wet paddy" not in green_only["paddy"]["siblings"], "a map with no blue plot claims no distinction"


def test_a_blue_plot_and_a_green_one_carry_different_classes_on_the_same_polygon_shape() -> None:
    """The fill half of the Split is what changes; the bund stroke is the same class either way
    (spec FR-003), so hovering a bund still lights every bund in the field."""
    blue = wrap(RECT, Split("wet paddy", "bund"))
    green = wrap(RECT, Split("paddy", "bund"))
    assert 'data-k="wet paddy"' in blue and 'data-k="paddy"' in green
    assert blue.count('data-k="bund"') == green.count('data-k="bund"') == 1


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


def _css_token(css: str, name: str) -> str:
    m = re.search(rf"{re.escape(name)}:\s*(#[0-9A-Fa-f]{{6}})\s*;", css)
    assert m, f"{name} is not defined as a hex color in page.css"
    return m.group(1)


def _luminance(hex_color: str) -> float:
    """WCAG relative luminance of an sRGB hex color."""

    def channel(v: int) -> float:
        c = v / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (int(hex_color[i : i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def contrast_ratio(a: str, b: str) -> float:
    la, lb = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def test_the_placard_name_keeps_a_readable_color_when_the_card_is_lit() -> None:
    """Feature 176 (GM 2026-09-02): "I should be able to see and read the name of the hamlet while the
    title card is highlighted ... whatever color has changed to must have decent contrast with the
    highlighted background color." The card and the name share the class `place`, so the gold fill rule
    would paint both; a later rule keeps the name in the map's ink. "Decent" is the WCAG AA bar for
    normal text, 4.5:1, read from the two colors the stylesheet actually declares."""
    page = _page()
    css = re.search(r"<style>(.*?)</style>", page, re.S)
    assert css, "the stylesheet is inlined"
    rule = re.search(r"g\.f\.on\.f-place text\s*\{\s*fill:\s*var\(--ink\)\s*!important;\s*\}", css.group(1))
    assert rule, "the lit placard's name keeps --ink (page.css)"
    gold_fill = re.search(r"g\.f\.on:not\(\[fill=\"none\"\]\).*?\{ fill: var\(--hl\)", css.group(1))
    assert gold_fill and gold_fill.start() < rule.start(), "the name's rule comes AFTER the gold fill rule (and is more specific), so it wins"
    ratio = contrast_ratio(_css_token(css.group(1), "--ink"), _css_token(css.group(1), "--hl"))
    assert ratio >= 4.5, f"ink on the highlight is {ratio:.1f}:1, under the 4.5:1 AA bar"


def test_the_page_embeds_only_the_present_classes() -> None:
    page = _page()
    blob = re.search(r'<script id="classes" type="application/json">(.*?)</script>', page, re.S)
    assert blob
    payload = json.loads(blob.group(1).replace("<\\/", "</"))
    data = payload["classes"]
    assert set(data) == {"farmhouse", "paddy", "bund"}
    assert data["paddy"]["siblings"] == [] and data["bund"]["siblings"] == [], "bund beans are not on this page"
    assert any(g["term"] == "bund" for g in payload["glossary"]), "the glossary carries the terms the present explanations use"


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
    assert 'class="hit"' in wrap(lane, "village lane") and 'class="hit"' not in wrap(lane, "pond")
    paddy = '<polygon points="0,0 9,0 9,9" fill="#A6C398" stroke="#7A5A30" stroke-width="1.4"/>'
    out = wrap(paddy, Split("paddy", "bund"))
    assert out.count('class="hit"') == 1 and out.index('class="hit"') > out.index('data-k="bund"'), "the bund's box rides in the bund group, above the paddy fill"


def test_the_marks_region_covers_only_cells_that_hold_a_mark() -> None:
    rects = marks_region(['<g><line x1="5" y1="5" x2="6" y2="6"/><line x1="30" y1="5" x2="31" y2="6"/><circle cx="100" cy="100" r="2"/></g>'], cell=24.0, grow=0)
    assert rects == '<rect x="0" y="0" width="48" height="24" fill="none"/><rect x="96" y="96" width="24" height="24" fill="none"/>'
    assert marks_region([]) == ""


def test_the_region_grows_a_cell_around_each_mark_but_stays_inside_the_footprint() -> None:
    one = ['<line x1="36" y1="36" x2="37" y2="37"/>']  # the cell (1, 1)
    grown = marks_region(one, cell=24.0, grow=1)
    assert grown.count("<rect") == 3 and 'x="0" y="0" width="72"' in grown, "the eight neighbors are in: three rows of three"
    clipped = marks_region(one, cell=24.0, grow=1, within=[[[0, 0], [48, 0], [48, 48], [0, 48]]])
    assert clipped.count("<rect") == 2 and 'width="48"' in clipped and 'y="48"' not in clipped, "the growth stops at the footprint; the marked cell itself always counts"


def test_the_scrub_region_comes_from_its_marks_not_its_polygon() -> None:
    strings = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300">',
        '<rect width="300" height="300" fill="#EFE3C2"/>',
        '<g stroke="#A7A860" stroke-width="0.8"><line x1="5" y1="5" x2="6" y2="9"/></g>',
        "</svg>",
    ]
    tags = [None, "-", "scrub and rough grazing", None]
    page = render_page(strings, tags, "T", {"ftpx": 1.0}, {"commons": [{"role": "grazing", "poly": [[0, 0], [300, 0], [300, 300], [0, 300]]}]})
    assert "<rect x=\"0\" y=\"0\" width=\"48\" height=\"24\" fill=\"none\"/>" in page and 'polygon class="hit"' not in page


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


def test_the_citations_come_from_the_research_entries() -> None:
    """GM 2026-08-28: the references behind a modal are the entry's own Sources line, read from the record."""
    keys = research_sources("research/vegetation.md - 'The fengshui forest - real scale, and why ours is honest'")
    assert "forests-2020" in keys
    reg = registry()
    assert len(reg) > 200 and "sugiura-1973-fuzoku" in reg and "Used for:" in reg["sugiura-1973-fuzoku"]
    assert citations(["forests-2020", "no-such-key"])["no-such-key"]["text"] == "(not in research/SOURCES.md)"
    assert urls_of("Saitama City (https://www.city.saitama.lg.jp/p077111.html; READ). See https://example.org/a).") == ["https://www.city.saitama.lg.jp/p077111.html", "https://example.org/a"]
    assert section_sources("**Sources:** `a-1`, [`b-2`](SOURCES.md#b-2) and `a-1` again") == ["a-1", "b-2"]
    assert research_sources("nothing here") == []


def test_every_class_cites_what_its_entry_cites_and_the_uncited_are_the_known_five() -> None:
    uncited = sorted(k for k, fc in CLASSES.items() if not research_sources(fc.entry))
    assert uncited == ["fallow", "field pond", "field rock", "footbridge", "grave island"], "an entry the citation pass left without keys (report.md lists them)"
    for k, fc in CLASSES.items():
        for key in research_sources(fc.entry):
            assert key in registry(), f"{k} cites {key}, which SOURCES.md does not register"


def test_the_glossary_is_well_formed_and_used() -> None:
    for term, (variants, definition) in GLOSSARY.items():
        assert variants and len(definition) > 30 and "\u2014" not in definition, term
    used = {g["term"] for g in glossary_for(explanations(set(CLASSES)))}
    assert {"bund", "coppice", "iriai", "tameike", "yashikirin", "kosatsuba", "hokora"} <= used
    unused = set(GLOSSARY) - used
    assert not unused, f"glossary terms no explanation uses: {sorted(unused)}"


def test_every_registered_source_carries_a_link_or_says_why_not() -> None:
    """Constitution v2.13.0 (GM 2026-08-28): a SOURCES.md key records the URL where the source can be
    read, or an explicit `URL: none - <why>`; the references modal links to it."""
    bare = sorted(k for k, text in registry().items() if not urls_of(text) and "URL: none" not in text)
    assert bare == [], f"sources with neither a link nor a stated reason: {bare}"


def test_merge_primitives_folds_a_run_of_unfilled_circles() -> None:
    from l7r.diagram.interactive.page import merge_primitives

    run = '<circle cx="1" cy="1" r="2" stroke="#000"/><circle cx="5" cy="5" r="2" stroke="#000"/>'
    out = merge_primitives(run)
    assert out.count("<circle") == 0 and "<path" in out


def test_research_sections_of_a_missing_file_are_empty_not_an_error() -> None:
    """Feature 146: a research pointer naming a file that is not there yields no sections - the interactive
    page loses that entry's citations rather than failing to build."""
    from l7r.diagram.interactive.sources import _sections

    assert _sections("research/no-such-file-at-all.md") == []


# ---- feature 148: the merge gathers what is SEPARATED, without moving the picture ----------------


def test_same_styled_primitives_merge_even_when_something_sits_between_them() -> None:
    """The defect feature 148 exists for: `merge_primitives` took only CONSECUTIVE runs, and a map whose
    glyphs interleave has almost none. Kuwabata's mulberry dike draws trunk, shadow and foliage per tree -
    a mean run of 2.4 elements - so 2,975 circles carrying three styles collapsed to nothing."""
    from l7r.diagram.interactive.page import merge_primitives

    s = (
        '<circle cx="10" cy="10" r="2" fill="#0a0"/>'
        '<path d="M100 100 L110 110" stroke="#333"/>'  # in the way, and nowhere near the circles
        '<circle cx="40" cy="40" r="2" fill="#0a0"/>'
    )
    out = merge_primitives(s)
    assert out.count("<circle") == 0, out
    assert out.count("<path") == 2, "the two circles became one path, and the intervening path is untouched"
    assert 'fill="#0a0"' in out


def test_a_primitive_is_not_moved_past_something_it_overlaps() -> None:
    """FR-002. The reorder is only invisible where the extents do not touch - otherwise the thing in
    between would change which of the two paints on top."""
    from l7r.diagram.interactive.page import merge_primitives

    s = (
        '<circle cx="10" cy="10" r="5" fill="#0a0"/>'
        '<path d="M8 8 L60 60" stroke="#333"/>'  # crosses BOTH circles
        '<circle cx="40" cy="40" r="5" fill="#0a0"/>'
    )
    assert merge_primitives(s).count("<circle") == 2, "neither circle may jump the path it lies under"


def test_a_translucent_shape_does_not_merge_with_one_it_overlaps() -> None:
    """Two blobs at opacity 0.85 stack DARKER where they cross; the same two as subpaths of one path are
    a single 0.85 fill and the crossing goes light. Measured on the reference hamlet before this guard
    existed: the page differed from its own SVG on 14.5% of pixels."""
    from l7r.diagram.interactive.page import merge_primitives

    over = '<circle cx="10" cy="10" r="6" fill="#0a0" opacity="0.85"/><circle cx="14" cy="10" r="6" fill="#0a0" opacity="0.85"/>'
    assert merge_primitives(over).count("<circle") == 2, "overlapping translucent shapes keep their own stacking"
    apart = '<circle cx="10" cy="10" r="2" fill="#0a0" opacity="0.85"/><circle cx="90" cy="90" r="2" fill="#0a0" opacity="0.85"/>'
    assert merge_primitives(apart).count("<circle") == 0, "translucent shapes that do NOT overlap still merge"


def test_ellipses_merge_like_circles() -> None:
    """FR-003 - the marsh is 1,656 ellipses on the reference hamlet and the pass ignored them entirely."""
    from l7r.diagram.interactive.page import merge_primitives

    s = '<ellipse cx="10" cy="10" rx="3" ry="2" fill="#456"/><ellipse cx="80" cy="80" rx="3" ry="2" fill="#456"/>'
    out = merge_primitives(s)
    assert out.count("<ellipse") == 0 and out.count("<path") == 1, out
    assert "a3,2 " in out, "an ellipse becomes two elliptical arcs, not a circle's"


def test_an_unreadable_extent_blocks_the_reorder_rather_than_risking_it() -> None:
    """An element whose box cannot be computed counts as being in the way. Too careful, never wrong."""
    from l7r.diagram.interactive.page import merge_primitives

    s = '<circle cx="10" cy="10" r="2" fill="#0a0"/><path d="M"/><circle cx="90" cy="90" r="2" fill="#0a0"/>'
    assert merge_primitives(s).count("<circle") == 2


def test_a_planted_tag_marks_the_group_and_a_plain_one_does_not() -> None:
    """Feature 153: the crowns on a crop dike carry the DIKE's class - hovering either lights both - so
    the only thing separating them is a token on the group, which the stylesheet paints in its own
    tone. A plain `str` tag must emit exactly what it emitted before the token existed."""
    from l7r.diagram.interactive.tags import Planted

    lit = wrap(RECT, Planted("mulberry dike"))
    assert lit.startswith('<g class="f f-mulberry-dike planted" data-k="mulberry dike">'), lit
    assert wrap(RECT, "mulberry dike") == f'<g class="f f-mulberry-dike" data-k="mulberry dike">{RECT}</g>'


def test_a_planted_tag_is_a_str_and_so_takes_every_str_path() -> None:
    """`Planted` subclasses `str` on purpose: the census, the hit boxes, `present_classes` and every
    `isinstance(tag, str)` branch keep working with no knowledge of it."""
    from l7r.diagram.interactive.tags import Planted

    tag = Planted("mulberry dike")
    assert isinstance(tag, str) and tag == "mulberry dike"
    assert ink_census([RECT], [tag])[0]["mulberry dike"] == 1


def test_a_pond_sluice_gets_the_field_ditchs_widening() -> None:
    """The GM, 2026-08-29: the sluices are "really hard to click on ... a larger highlight box, similar
    to what we are doing with the field ditches". Same factors; the sluice's mark being thinner, the
    box comes out smaller in absolute terms and larger relative to the ink, which is the point."""
    from l7r.diagram.interactive.page import HIT_WIDEN

    assert HIT_WIDEN["pond sluice"] == HIT_WIDEN["field ditch"]
    sluice = '<line x1="10" y1="10" x2="30" y2="10" stroke="#37637F" stroke-width="2.4"/>'
    out = hit_layer([sluice], ["pond sluice"])
    widths = [float(w) for w in re.findall(r'class="hit"[^>]*stroke-width: ([\d.]+)px', out)]
    assert widths == [14.4], f"one invisible copy, six times the drawn 2.4 px: {out}"


def test_outlined_shapes_that_overlap_keep_their_own_paint_order() -> None:
    """Feature 153, measured on Kuwabata. One <path> paints every subpath's FILL and only then its
    stroke, so an earlier crown's outline that a later crown's fill used to cover comes back over it -
    the woodland read as a heap of glass rings. Same style, apart: still merged."""
    over = '<circle cx="10" cy="10" r="6" fill="#4F6E33" stroke="#3C5526" stroke-width="0.8"/><circle cx="14" cy="10" r="6" fill="#4F6E33" stroke="#3C5526" stroke-width="0.8"/>'
    assert merge_primitives(over).count("<circle") == 2, "overlapping outlined shapes keep their order"
    apart = '<circle cx="10" cy="10" r="2" fill="#4F6E33" stroke="#3C5526" stroke-width="0.8"/><circle cx="90" cy="90" r="2" fill="#4F6E33" stroke="#3C5526" stroke-width="0.8"/>'
    assert merge_primitives(apart).count("<circle") == 0, "outlined shapes that do not touch still merge"


def test_a_line_is_never_outlined_however_the_scatter_is_written() -> None:
    """A line has no fill area, whatever `fill` says or leaves unsaid - and the scatters ARE lines, one
    per blade, sharing a root. Reading them as outlined cost 4,336 elements on Kuwabata's scrub alone
    (5,536 unmerged blades where 1,200 paths had been), which is the whole point of the merge pass."""
    tuft = '<line x1="10" y1="20" x2="11" y2="14" stroke="#6E9377" stroke-width="0.8"/><line x1="10" y1="20" x2="9" y2="15" stroke="#6E9377" stroke-width="0.8"/>'
    assert merge_primitives(tuft).count("<line") == 0, "two blades of one tuft still become one path"


def test_two_circles_whose_boxes_overlap_but_whose_edges_do_not_still_merge() -> None:
    """A box lies most about a round blob: two crowns can share a box corner and not touch at all. The
    overlap test reads a circle AS a circle for exactly this case."""
    corner = '<circle cx="0" cy="0" r="10" fill="#4F6E33" stroke="#3C5526" stroke-width="0.5"/><circle cx="18" cy="18" r="10" fill="#4F6E33" stroke="#3C5526" stroke-width="0.5"/>'
    assert merge_primitives(corner).count("<circle") == 0, "boxes overlap, circles do not - so they merge"
    touching = '<circle cx="0" cy="0" r="10" fill="#4F6E33" stroke="#3C5526" stroke-width="0.5"/><circle cx="12" cy="12" r="10" fill="#4F6E33" stroke="#3C5526" stroke-width="0.5"/>'
    assert merge_primitives(touching).count("<circle") == 2, "circles that really do touch keep their order"


def test_a_member_may_not_jump_back_past_anything_skipped_since_the_buckets_FIRST_member() -> None:
    """Feature 148 cleared a bucket's skipped extents whenever a member joined, which proves only that
    THAT member cleared them. A third member is emitted at the FIRST member's position too, so it has to
    clear everything skipped since the bucket opened (feature 153)."""
    a = '<circle cx="10" cy="10" r="2" fill="#0a0"/>'
    blocker = '<circle cx="60" cy="60" r="6" fill="#a00"/>'
    b = '<circle cx="200" cy="200" r="2" fill="#0a0"/>'
    c = '<circle cx="61" cy="61" r="2" fill="#0a0"/>'
    out = merge_primitives(a + blocker + b + c)
    assert out.count("<circle") >= 2, f"the third member overlaps what the second cleared: {out}"
    assert '<circle cx="61" cy="61" r="2" fill="#0a0"/>' in out, "it stays where it was drawn"


def test_a_fill_only_shape_is_not_outlined_and_still_merges_where_it_overlaps() -> None:
    """Only a shape painting BOTH has a paint order to lose. Two overlapping opaque fills of one color
    are the same ink whether they are two elements or two subpaths, so they merge."""
    from l7r.diagram.interactive.page import _outlined

    assert not _outlined("circle", {"fill": "#4F6E33"})
    assert not _outlined("circle", {"fill": "none", "stroke": "#3C5526"})
    assert not _outlined("circle", {"fill": "#4F6E33", "stroke": "#3C5526", "stroke-width": "0"})
    assert _outlined("circle", {"fill": "#4F6E33", "stroke": "#3C5526"})
    over = '<circle cx="10" cy="10" r="6" fill="#4F6E33"/><circle cx="14" cy="10" r="6" fill="#4F6E33"/>'
    assert merge_primitives(over).count("<circle") == 0


def test_only_the_lifted_class_leaves_its_own_group() -> None:
    """Feature 153. A pond sluice is a gate IN a watercourse, so 49 of Kuwabata's 52 are drawn on top of
    a field ditch - and while every box rode inside its own class group, the ditch's group came later
    and its 14.4 px box took the pointer from the sluice's own 2.4 px line (the sluice won 42.4% of its
    own box; `settlement-review` measured it at 125,173 points, worst sluice 10.3%). Lifting the sluice
    alone fixes it - 88.6%, worst 75.8% - and lifting EVERY box does not: above the ink the bund's 12 px
    box stops being buried and takes 5,112 sample points off the dikes, the vegetable ground and the
    paddy. So the layer holds exactly `HIT_ON_TOP`, and everything else stays where the GM tuned it."""
    from l7r.diagram.interactive.page import HIT_ON_TOP

    ditch = '<line x1="0" y1="10" x2="100" y2="10" stroke="#6E93A8" stroke-width="3.5"/>'
    sluice = '<line x1="48" y1="10" x2="52" y2="10" stroke="#37637F" stroke-width="2.4"/>'
    assert frozenset({"pond sluice"}) == HIT_ON_TOP
    assert 'class="hit"' not in wrap(sluice, "pond sluice"), "the lifted class leaves nothing behind"
    assert 'class="hit"' in wrap(ditch, "field ditch"), "every other widened class keeps its box inline"
    layer = hit_layer([ditch, sluice], ["field ditch", "pond sluice"])
    assert 'data-k="pond sluice"' in layer and 'data-k="field ditch"' not in layer


def test_the_hit_layer_sits_above_the_ink_it_widens() -> None:
    """One layer for every widened box, emitted after the drawn record and before `</svg>`."""
    strings = ['<svg viewBox="0 0 20 20">', '<line x1="1" y1="1" x2="9" y2="9" stroke="#37637F" stroke-width="2.4"/>', "</svg>"]
    tags = [NOT_HIGHLIGHTED, "pond sluice", None]
    page = render_page(strings, tags, "t")
    assert page.index('class="hit"') > page.index('stroke-width="2.4"')
    assert page.index('class="hit"') < page.index("</svg>")


def test_a_lifted_box_gives_up_the_ground_a_structure_stands_on() -> None:
    """Feature 153, settlement-review round 2. Lifting the sluice above the ink broke the rule the lift
    is allowed under: its 14.4 px box swallowed 88.4% of one pig sty's own footprint and 42.8% of a duck
    pen's - the sty's center sits 4.67 px from a lifted line whose half-width is 7.2. The layer is
    clipped against every recorded structure, so it keeps the open ground and gives up the glyph."""
    from l7r.diagram.interactive.page import hit_layer

    sluice = '<line x1="90" y1="100" x2="110" y2="100" stroke="#37637F" stroke-width="2.4"/>'
    manifest = {"pig_sties": [{"x": 100.0, "y": 100.0, "w": 10.0, "h": 8.0, "rot": 0}]}
    out = hit_layer([sluice], ["pond sluice"], manifest)
    assert 'clip-path="url(#hit-keep-clear)"' in out, out
    assert 'clip-rule="evenodd"' in out and "M94.9,95.9h10.2v8.2h-10.2Z" in out, "a hole over the sty, padded the tenth of a pixel the coordinates round to"
    assert "clip-path" not in hit_layer([sluice], ["pond sluice"], {}), "no structures, no clip"
    junk = {"pig_sties": ["not a record", {"x": 1.0}, {"x": 100.0, "y": 100.0, "w": 10.0, "h": 8.0, "rot": 0}]}
    assert hit_layer([sluice], ["pond sluice"], junk).count("M94.9,95.9") == 1, "a record it cannot read is skipped, not fatal"


def test_a_rotated_footprint_is_held_clear_by_its_whole_box() -> None:
    """The hole is the axis-aligned box of the ROTATED glyph - a superset, so it is never smaller than
    the thing it protects."""
    from l7r.diagram.interactive.page import hit_layer

    sluice = '<line x1="90" y1="100" x2="110" y2="100" stroke="#37637F" stroke-width="2.4"/>'
    out = hit_layer([sluice], ["pond sluice"], {"byres": [{"x": 100.0, "y": 100.0, "w": 10.0, "h": 10.0, "rot": 45}]})
    assert "h14.3v14.3" in out, f"10 x 10 turned 45 degrees needs a 14.14 px box, plus the 0.2 pad: {out}"


def test_a_lifted_class_the_priority_list_forgets_still_wins() -> None:
    """The list ranks the lifted classes against each other; a class lifted BECAUSE it cannot otherwise
    be hit must not land in the weakest place because someone forgot to add it (the first version's
    `-1` fallback did exactly that)."""
    from l7r.diagram.interactive import page as pg

    ditch = '<line x1="0" y1="10" x2="100" y2="10" stroke="#6E93A8" stroke-width="3.5"/>'
    sluice = '<line x1="48" y1="10" x2="52" y2="10" stroke="#37637F" stroke-width="2.4"/>'
    lifted = pg.HIT_ON_TOP | {"field ditch"}
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(pg, "HIT_ON_TOP", lifted)
        mp.setattr(pg, "HIT_PRIORITY", ("field ditch",))  # the sluice is the forgotten one
        out = pg.hit_layer([ditch, sluice], ["field ditch", "pond sluice"])
    assert out.index('data-k="field ditch"') < out.index('data-k="pond sluice"'), out


def test_every_keep_clear_key_makes_its_holes() -> None:
    """`HIT_KEEP_CLEAR` names manifest keys, and a key whose records carry some other shape - a well's
    `x,y,r`, a footbridge's `span`, a sluice gate's bare `x,y,rot` - yields NO hole and NO error
    (settlement-review round 3). So the count is asserted against a real manifest: one hole per record,
    plus one per auxiliary polygon (a duck pen's `wet` apron), plus the canvas rectangle."""
    import json
    from pathlib import Path

    from l7r.diagram.interactive.page import HIT_KEEP_CLEAR, _keep_clear_clip

    man = json.loads((Path(__file__).resolve().parents[2] / "pool/hamlets/kuwabata/kuwabata.json").read_text())
    for k in HIT_KEEP_CLEAR:
        assert man.get(k), f"{k} records nothing on this map, so the count below cannot see it go wrong"
    recs = [r for k in HIT_KEEP_CLEAR for r in man.get(k) or []]
    aprons = sum(1 for r in recs for e in ("wet", "poly") if isinstance(r.get(e), list) and len(r[e]) > 2)
    clip, _ = _keep_clear_clip(man)
    assert recs, "the reference dike-pond map records structures"
    assert clip.count("M") == 1 + len(recs) + aprons, f"{len(recs)} records + {aprons} aprons + the canvas"


# --- the notes block and the place card reach the page (feature 156) ---


def test_an_annotation_reaches_only_the_class_its_notes_name() -> None:
    notes = MapNotes(place={}, features={"windbreak": "Unusually deep on this map.", "flying castle": "dropped", "pond": "absent from this map"})
    data = explanations({"windbreak", "copse"}, notes)
    assert data["windbreak"]["on_this_map"] == "Unusually deep on this map."
    assert data["copse"]["on_this_map"] == "", "a class the notes do not annotate carries nothing"
    assert "flying castle" not in data, "a key the registry does not know is dropped, silently"
    assert "pond" not in data, "a class absent from this map is dropped, silently"


def test_with_no_notes_no_class_claims_anything_local() -> None:
    data = explanations({"windbreak", "copse"})
    assert all(d["on_this_map"] == "" for d in data.values())


def _render(tags: list, meta: dict, notes: MapNotes = EMPTY) -> dict:
    strings = ['<svg viewBox="0 0 9 9">'] + [RECT] * len(tags) + ["</svg>"]
    page = render_page(strings, ["-", *tags, None], "Inashiro", meta, {"houses": [{}] * 15}, notes)
    return json.loads(re.search(r'<script id="classes" type="application/json">(.*?)</script>', page, re.S).group(1).replace("<\\/", "</"))["classes"]


def test_the_placard_opens_the_place_card() -> None:
    notes = MapNotes(place={"district": "Hoshigaoka", "district direction": "east"}, features={})
    data = _render([PLACE, "paddy", "village lane"], {"scale": "hamlet", "name": "Inashiro", "households": 15}, notes)
    card = data[PLACE]
    assert card["name"] == "Inashiro" and "is a hamlet of 15 farmhouses, population ~75" in card["what"]
    assert "village district of Hoshigaoka, which lies east" in card["why"]
    assert card["lead"] == "" and card["caveat"], "no accuracy claim; the basis is stated (FR-001, FR-008a)"


def test_the_lane_default_names_the_village_the_notes_name() -> None:
    notes = MapNotes(place={"district": "Hoshigaoka", "district direction": "east"}, features={})
    data = _render([PLACE, "village lane"], {"scale": "hamlet", "name": "Inashiro", "households": 15}, notes)
    assert (
        data["village lane"]["on_this_map"]
        == "The connector track leads out of the hamlet toward Hoshigaoka, the main village of the district it belongs to; the lanes between the farmsteads feed it."
    )


def test_an_authored_lane_annotation_beats_the_default() -> None:
    notes = MapNotes(place={"district": "Hoshigaoka"}, features={"village lane": "This one climbs the spur first."})
    data = _render([PLACE, "village lane"], {"scale": "hamlet", "name": "Inashiro", "households": 15}, notes)
    assert data["village lane"]["on_this_map"] == "This one climbs the spur first."


def test_a_tier_the_vocabulary_does_not_describe_gets_no_card() -> None:
    data = _render([PLACE, "paddy"], {"scale": "megalopolis", "name": "Nowhere"})
    assert PLACE not in data, "the placard simply has nothing to open, exactly as before"


def test_the_reserved_place_key_is_never_reported_as_unruled() -> None:
    assert unregistered_classes({PLACE: 3, "paddy": 1}) == []
    assert unregistered_classes({"flying castle": 1}) == ["flying castle"]


def test_no_rendered_page_tells_a_reader_a_feature_is_historically_accurate() -> None:
    """Spec SC-001, at the page level: the phrase and its paraphrases are gone from what is rendered."""
    page = _page()
    assert "historically accurate" not in page
    data = json.loads(re.search(r'<script id="classes" type="application/json">(.*?)</script>', page, re.S).group(1).replace("<\\/", "</"))["classes"]
    for key, d in data.items():
        if d["label"] == "accurate":
            assert d["lead"] == "", key
            assert not re.search(r"\bare read\b|\bis read\b|\bat its true\b|\btrue size\b", d["caveat"]), key


def test_an_element_with_no_extent_is_treated_as_touching_everything() -> None:
    """`_hits` decides whether two drawn elements merge into one hover group. An extent of `None` means
    the emitter recorded no geometry for that element, and the safe answer is YES: refusing to merge
    would split one feature into two hover groups on the sheet, which the reader sees, while merging
    slightly too eagerly costs nothing visible. Boxes and circles both go through here, and a circle
    is tested AS a circle - two crowns whose boxes overlap at a corner do not actually touch."""
    from l7r.diagram.interactive.page import _hits

    assert _hits(None, (0.0, 0.0, 5.0)) is True
    assert _hits((0.0, 0.0, 5.0), None) is True
    assert _hits(None, None) is True
    # circles: touching exactly at the rims counts, a hair further apart does not
    assert _hits((0.0, 0.0, 5.0), (10.0, 0.0, 5.0)) is True
    assert _hits((0.0, 0.0, 5.0), (10.1, 0.0, 5.0)) is False
