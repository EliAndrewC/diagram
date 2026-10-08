"""The HTML target's string layer (feature 134): wrapping, the ink census, and the page's contents.

What the browser test cannot cheaply prove per string is proved here: each tag shape wraps the way
`page.wrap` promises (a `Split` becomes a fill-only and a stroke-only copy; `Parts` wrap piece by
piece with the unclassed wrapper tags left bare), the census counts ink and only ink and reports
only what nobody ruled on, and the page embeds only the classes present and only the sibling
paragraphs whose other class is present (spec US4 scenario 4).
"""

from __future__ import annotations

import json
import random
import re

import pytest

from l7r.diagram.interactive import conditions
from l7r.diagram.interactive.classes import CLASSES, PLACE
from l7r.diagram.interactive.notes import EMPTY, MapNotes
from l7r.diagram.interactive.page import (
    PLAIN_CURSOR,
    explanations,
    hit_layer,
    ink_census,
    merge_primitives,
    present_classes,
    render_page,
    unregistered_classes,
    wrap,
)
from l7r.diagram.interactive.sources import (
    SITE_PAGES,
    github_anchor,
    question_text,
    registry,
    research_questions,
    research_sources,
    section_sources,
    urls_of,
)
from l7r.diagram.interactive.tags import Split

pytestmark = pytest.mark.renders  # tests OF the page's raster / the plates: they render tiny synthetic pictures on purpose (feature 213)

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


def test_the_broad_kinds_keep_the_arrow_and_every_other_kind_gets_the_hand() -> None:
    """GM 2026-09-26: the cursor stays normal over grassland, marshland, paddies, copses, windbreak forests and
    woodland commons, and turns into the link hand over every other feature. Every name on the list is a class
    the registry knows - a renamed key would otherwise drop off the list with no test failing."""
    assert {"scrub and rough grazing", "marsh", "paddy", "wet paddy", "copse", "windbreak", "woodland commons"} == PLAIN_CURSOR
    assert set(CLASSES) >= PLAIN_CURSOR
    data = explanations(set(CLASSES))
    assert {k for k, d in data.items() if d["plain"]} == PLAIN_CURSOR
    assert not explanations({"flying castle"})["flying castle"].get("plain"), "an unregistered stub is still clickable"


def test_explanations_hold_only_present_classes_and_present_siblings() -> None:
    data = explanations({"windbreak", "copse", "farmhouse", "notice board"})
    assert set(data) == {"windbreak", "copse", "farmhouse", "notice board"}
    assert data["windbreak"]["siblings"] == ["copse"], "woodland commons is absent from this map, so it is not claimed; siblings are link keys now"
    assert data["farmhouse"]["siblings"] == [], "storage shed and byre are absent"
    # feature 319: no feature-level label, lead or caveat rides on the page - the classification is per statement
    assert not {"label", "lead", "caveat", "what", "why"} & set(data["copse"]) and data["copse"]["about"]
    assert data["windbreak"]["guesses"], "the windbreak's guesses are bullets of their own"
    # the references are QUESTIONS (feature 180): the sections the entry names, linked to the local page; the
    # cited keys, the citation text and the entry pointer no longer ride on the page at all
    # a map recording no knobs lists no knob-conditioned question (FR-015): the windbreak's 0031 rests on a nucleated-only guess
    assert data["windbreak"]["questions"] == research_questions(conditions.shown_entry(CLASSES["windbreak"].entry, {}))
    assert any(
        q["text"].startswith("Groves around a southern Chinese village") and q["url"].startswith(SITE_PAGES + "q/groves-around-a-southern-chinese-village") for q in data["windbreak"]["questions"]
    )
    assert not {"sources", "refs", "entry"} & set(data["windbreak"]), "dropped from the page data (spec FR-011)"


def test_a_question_link_is_github_s_own_anchor() -> None:
    """Feature 180, spec FR-006 / D7: the anchor rule is REPRODUCED, and these seven were read off the live
    GitHub rendering on 2026-09-05 - a `?`, parentheses, an apostrophe, ` - `, CJK characters, emphasis.
    A divergence from GitHub's rule fails HERE, with the expected string in the assertion, rather than
    as a silently broken link on every page."""
    live = {
        "How close does a farmhouse stand to the paddy? Up against it - but never on the bund (researched 2026-08-27, feature 133 T41)": "how-close-does-a-farmhouse-stand-to-the-paddy-up-against-it---but-never-on-the-bund-researched-2026-08-27-feature-133-t41",
        "May a byre stand beside a wellhead? (researched 2026-08-18)": "may-a-byre-stand-beside-a-wellhead-researched-2026-08-18",
        "DISPERSED (散村 *sankyoson*) - decisive, and our terrain is its terrain": "dispersed-散村-sankyoson---decisive-and-our-terrain-is-its-terrain",
        "The farmstead's fixtures - privy, woodpile, manure heap, bath, coop, household shrine, persimmon (researched 2026-08-27, feature 133 T53-T59)": "the-farmsteads-fixtures---privy-woodpile-manure-heap-bath-coop-household-shrine-persimmon-researched-2026-08-27-feature-133-t53-t59",
        "Homestead groves (yashikirin) - the real scale and prevalence": "homestead-groves-yashikirin---the-real-scale-and-prevalence",
        "The ring canal runs on the INNER toe - 一河围田": "the-ring-canal-runs-on-the-inner-toe---一河围田",
        "Why rape (油菜) was tried and removed": "why-rape-油菜-was-tried-and-removed",
    }
    for heading, anchor in live.items():
        assert github_anchor(heading) == anchor, heading
    # a heading repeated within one file is numbered in order of appearance, as GitHub numbers it
    seen: dict[str, int] = {}
    assert [github_anchor("Citing", seen), github_anchor("Citing", seen), github_anchor("Other", seen), github_anchor("Citing", seen)] == ["citing", "citing-1", "other", "citing-2"]
    # underscores and combining marks survive; other punctuation does not
    assert github_anchor("a_b: ć") == "a_b-ć"


def test_a_question_s_text_drops_the_dated_bookkeeping_and_nothing_else() -> None:
    """Spec FR-005 / D2: "(researched 2026-08-27, feature 133 T41)" is for the project, not the reader."""
    assert question_text("How does a village lane bend? (researched 2026-08-27, feature 133 T32)") == "How does a village lane bend?"
    assert question_text("The muck heap that reads as the neighbor's (accepted 2026-08-29, feature 152)") == "The muck heap that reads as the neighbor's"
    assert question_text("What a settlement IS, and what the place card may say about it (feature 156, 2026-08-29)") == "What a settlement IS, and what the place card may say about it"
    assert question_text("DISPERSED (散村 *sankyoson*) - decisive, and our terrain is its terrain") == "DISPERSED (散村 sankyoson) - decisive, and our terrain is its terrain", (
        "an undated parenthetical is part of the question; emphasis markers are not"
    )
    assert question_text("Why rape (油菜) was tried and removed") == "Why rape (油菜) was tried and removed"


def test_the_questions_come_in_the_entry_s_order_and_every_class_that_names_a_section_has_some() -> None:
    """Spec FR-004 / D4: the class author's primary question first, not file order; FR-002: the one entry
    that resolved to nothing was `fallow`, whose link was hidden already - until feature 269 (K1) wrote it from
    0013, so now every class names a findable section."""
    qs = research_questions(CLASSES["farmhouse"].entry)
    # feature 319 rewrote the farmhouse's Entry to exactly what its About rests on (dev/modals.md M14): 0029 first, then 0028
    # and 0004, though 0004 sorts first by file - the entry's order wins
    assert [q["text"][:30] for q in qs][:3] == ["Farmhouses (minka)", "The farmstead and what stood o", "Households: how many live in a"], qs
    # feature 301: a question links its own small page in the record's site
    assert all(q["url"].startswith(SITE_PAGES + "q/") for q in qs), "flat, whatever section the question is in (feature 303)"
    assert qs[2]["url"] == SITE_PAGES + "q/households-how-many-live-in-a-house-and-under-how-many-roofs-ie.html"
    assert qs[0]["url"].endswith("/farmhouses-minka.html")
    # file order would put the farmstead topic before the farmhouse topic; the entry's order wins (the lane entry moved to the ways page in the feature 292 sweep)
    assert [q["url"] for q in research_questions(CLASSES["farmhouse"].entry)] == [q["url"] for q in qs], "deterministic"
    unresolved = sorted(k for k, fc in CLASSES.items() if not research_questions(fc.entry))
    assert unresolved == [], "every class's entry names at least one findable section"
    assert research_questions("nothing here") == []
    for k, fc in CLASSES.items():
        for q in research_questions(fc.entry):
            assert q["url"].startswith(SITE_PAGES) and q["url"].endswith(".html") and "#" not in q["url"] and q["text"], (k, q)
            assert "researched 20" not in q["text"] and "*" not in q["text"], (k, q)


def test_the_page_carries_the_questions_and_no_record_line() -> None:
    """Spec FR-001 (no `Record:` footer), FR-008 (the lead-in), FR-009 (the button is set by the script),
    FR-011 (the JSON shape)."""
    html_text = render_page([RECT], ["farmhouse"], "T")
    # the MARKUP, before the data and the script (the script's comments name the old footer to say it is gone)
    markup = html_text.split('<script id="classes"')[0]
    assert "x-entry" not in markup and "Record:" not in markup
    assert "x-entry" not in html_text.split("<script>")[1], "and the script touches no such element"
    # the References tab opens on its links alone (the GM, 2026-10-05: "the links are self-explanatory")
    assert 'id="r-intro"' not in html_text and "Topics we researched" not in html_text
    blob = json.loads(re.search(r'<script id="classes" type="application/json">(.*?)</script>', html_text, re.S).group(1).replace("<\\/", "</"))
    farmhouse = blob["classes"]["farmhouse"]
    assert farmhouse["questions"] and set(farmhouse["questions"][0]) == {"text", "url"}
    assert not {"sources", "refs", "entry"} & set(farmhouse)
    # feature 319: the modal is TABS - About, Guesses, References - in one dialog; the references dialog, its return button
    # and the "See references (N)" link are gone (they were features 180 and 181's), and a tab with nothing to show is hidden
    assert '<nav id="x-tabs" role="tablist">' in markup and all(f'id="t-{t}"' in markup for t in ("about", "guesses", "depict", "refs"))
    assert [m for m in re.findall(r'role="tab" id="t-\w+" data-tab="\w+" aria-controls="p-\w+">(\w+)<', markup)] == ["About", "Guesses", "Depiction", "References"]
    assert 'id="references"' not in markup and "r-close" not in html_text and "See references" not in html_text
    assert "behind" not in html_text.split("<style>")[1].split("</style>")[0], "no stylesheet rule hides the explanation any more"
    assert 'document.getElementById("t-guesses").hidden = !(d.guesses && d.guesses.length)' in html_text
    assert 'document.getElementById("t-refs").hidden = !d.questions.length' in html_text
    # feature 182: the glossary tooltip is ONE element outside the dialog, placed by the script
    assert '<div id="tip" role="tooltip" hidden></div>' in markup and markup.index('id="tip"') > markup.index('id="explain"')
    assert ".gl:hover::after" not in html_text and "#tip { position: fixed;" in html_text


def test_the_wet_paddy_is_explained_apart_from_the_paddy_and_only_when_present() -> None:
    """Feature 158 (GM 2026-08-29): the blue plots are "its own type of thing, and it deserves its own
    explanation". Both classes on one map means two entries and a link each way; a map with no blue
    plot must show neither the class nor a sibling paragraph claiming a distinction from an absent one."""
    both = explanations({"paddy", "wet paddy"})
    assert set(both) == {"paddy", "wet paddy"}
    assert both["paddy"]["about"] != both["wet paddy"]["about"], "two kinds, two explanations"
    assert both["wet paddy"]["siblings"] == ["paddy"] and "wet paddy" in both["paddy"]["siblings"]
    # the disclosure the GM's reader needs - how the map tints the wet ground - is the Depiction tab's (feature 319)
    assert both["wet paddy"]["depiction"], "the drawing liberty reaches the modal"
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
    assert "no entry" in data["flying castle"]["about"][0] and "label" not in data["flying castle"]


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


def test_the_scrub_region_is_the_shape_its_tile_fills_not_its_polygon() -> None:
    """Feature 298: the scrub's hit region is its recorded cover - the ground its grass tile fills, holes bare - not the
    whole commons polygon (the GM: "if my mouse is just in the middle of the village, over blank space where there is
    deliberately no scrubland, then I don't think that the scrubland should be highlighted"); a scrub zone whose tile filled
    nothing has no region; a marsh keeps its polygon."""
    strings = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300">',
        '<rect width="300" height="300" fill="#EFE3C2"/>',
        '<path d="M0,0L300,0L300,300Z" fill="url(#cover-grass-1)" style="pointer-events: none"/>',
        '<path d="M0,0L10,0L10,10Z" fill="url(#cover-reed-1)" style="pointer-events: none"/>',
        "</svg>",
    ]
    tags = [None, "-", "scrub and rough grazing", "marsh", None]
    cover = [[[0, 0], [300, 0], [300, 300]], [[100, 50], [150, 50], [150, 100]]]
    manifest = {
        "commons": [{"role": "grazing", "poly": [[0, 0], [300, 0], [300, 300], [0, 300]], "cover": cover}, {"role": "grazing", "poly": [[0, 0], [9, 0], [9, 9]]}],
        "marshes": [{"role": "toe", "poly": [[0, 0], [10, 0], [10, 10]]}],
    }
    page = render_page(strings, tags, "T", {"ftpx": 1.0}, manifest)
    assert page.count('class="hit" d="M0.0,0.0L300.0,0.0L300.0,300.0ZM100.0,50.0') == 1, "the scrub's region is its cover, hole and all"
    assert page.count('class="hit" d="M0.0,0.0L9.0') == 0, "a scrub zone with no cover has no region"
    assert page.count('class="hit" d="M0.0,0.0L10.0,0.0L10.0,10.0Z"') == 1, "the marsh keeps its polygon"


def test_the_citations_come_from_the_research_entries() -> None:
    """GM 2026-08-28: the references behind a modal are the entry's own Sources line, read from the record."""
    keys = research_sources("research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.html")
    assert "sugiura-1973-fuzoku" in keys
    reg = registry()
    assert len(reg) > 200 and "sugiura-1973-fuzoku" in reg and "Used for:" in reg["sugiura-1973-fuzoku"]
    assert urls_of("Saitama City (https://www.city.saitama.lg.jp/p077111.html; READ). See https://example.org/a).") == ["https://www.city.saitama.lg.jp/p077111.html", "https://example.org/a"]
    assert section_sources('<p><strong>Sources:</strong> <code>a-1</code>, <a href="SOURCES.html#b-2"><code>b-2</code></a> and <code>a-1</code> again</p>') == ["a-1", "b-2"]
    assert research_sources("nothing here") == []


def test_every_class_cites_what_its_entry_cites_and_the_uncited_are_the_known_four() -> None:
    """No entry is left without a key. `fallow` was the last, its section recording a silence, until feature 269 (K1)
    wrote it from 0013 (the resting paddy basin). The
    in-field-features section of `fields.html` (field pond, field rock, grave island) was cited in feature 242. `copse` and `windbreak` were uncited for a day: their
    fengshui-forest entry rested on two MDPI papers mdpi.com would not serve to this container, until the GM
    downloaded them (2026-09-07) and the passages were read from the copies - the Fujian paper supports the
    two-groves-per-village figure and reads AGAINST the record's grove areas, which are labeled GUESS now.

    `stream` and `footbridge` left this list in feature 232. The water-width ladder had rested on the Chinese
    design standard GB 50288, which is not readable anywhere and so could not be cited (feature 195, GM
    2026-09-06); the pass found the Jiangsu provincial standard that DEFERS to it by number and is served
    openly, so the ladder is cited from that and from an open design report. GB 50288 itself stays on the
    list of documents only a person could reach."""
    uncited = sorted(k for k, fc in CLASSES.items() if not research_sources(fc.entry))
    assert uncited == [], "an entry without a cited key - see the docstring"
    for k, fc in CLASSES.items():
        for key in research_sources(fc.entry):
            assert key in registry(), f"{k} cites {key}, which SOURCES.md does not register"


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
    """Feature 146: a research pointer naming a file that is not there yields nothing - the interactive page loses that
    entry's references rather than failing to build (`scripts/gates/check-entry-headings.py` refuses it at the push)."""
    assert research_questions("research/questions/0999-no-such-question.html") == []
    assert research_sources("research/questions/0999-no-such-question.html") == []


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


@pytest.fixture
def lifted_sluice(monkeypatch: pytest.MonkeyPatch) -> None:
    """A stand-in lifted class for the on-top hit layer (feature 153): the pond sluice it was built for is retired (feature
    280 M57), so `HIT_ON_TOP` is empty and these tests lift a 'pond sluice' mark of their own, widened as a ditch is."""
    from l7r.diagram.interactive import page as pg

    monkeypatch.setattr(pg, "HIT_ON_TOP", frozenset({"pond sluice"}))
    monkeypatch.setattr(pg, "HIT_WIDEN", {**pg.HIT_WIDEN, "pond sluice": pg.HIT_WIDEN["irrigation ditch"]})
    monkeypatch.setattr(pg, "HIT_PRIORITY", (*pg.HIT_PRIORITY, "pond sluice"))


def test_only_the_lifted_class_leaves_its_own_group(lifted_sluice: None) -> None:
    """Feature 153. A pond sluice is a gate IN a watercourse, so 49 of Kuwabata's 52 are drawn on top of
    a field ditch - and while every box rode inside its own class group, the ditch's group came later
    and its 14.4 px box took the pointer from the sluice's own 2.4 px line (the sluice won 42.4% of its
    own box; `settlement-review` measured it at 125,173 points, worst sluice 10.3%). Lifting the sluice
    alone fixes it - 88.6%, worst 75.8% - and lifting EVERY box does not: above the ink the bund's 12 px
    box stops being buried and takes 5,112 sample points off the dikes, the vegetable ground and the
    paddy. So the layer holds exactly `HIT_ON_TOP`, and everything else stays where the GM tuned it."""
    from l7r.diagram.interactive import page as pg

    ditch = '<line x1="0" y1="10" x2="100" y2="10" stroke="#6E93A8" stroke-width="3.5"/>'
    sluice = '<line x1="48" y1="10" x2="52" y2="10" stroke="#37637F" stroke-width="2.4"/>'
    assert frozenset({"pond sluice"}) == pg.HIT_ON_TOP, "the stand-in, lifted alone"
    assert 'class="hit"' not in wrap(sluice, "pond sluice"), "the lifted class leaves nothing behind"
    assert 'class="hit"' in wrap(ditch, "irrigation ditch"), "every other widened class keeps its box inline"
    layer = hit_layer([ditch, sluice], ["irrigation ditch", "pond sluice"])
    assert 'data-k="pond sluice"' in layer and 'data-k="irrigation ditch"' not in layer


def test_a_lifted_box_gives_up_the_ground_a_structure_stands_on(lifted_sluice: None) -> None:
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


def test_a_record_s_auxiliary_polygon_is_held_clear_by_its_box(lifted_sluice: None) -> None:
    """A glyph drawn outside its own `w` x `h` (a `poly` on the record) punches a second hole, its bounding box
    padded the tenth of a pixel the coordinates round to; a `poly` of two points is no polygon and adds none."""
    from l7r.diagram.interactive.page import hit_layer

    sluice = '<line x1="90" y1="100" x2="110" y2="100" stroke="#37637F" stroke-width="2.4"/>'
    rec = {"x": 100.0, "y": 100.0, "w": 10.0, "h": 8.0, "rot": 0, "poly": [[100.0, 104.0], [106.0, 104.0], [106.0, 110.0]]}
    out = hit_layer([sluice], ["pond sluice"], {"pig_sties": [rec]})
    assert "M99.9,103.9h6.2v6.2h-6.2Z" in out, out
    two = {**rec, "poly": [[100.0, 104.0], [106.0, 104.0]]}
    assert hit_layer([sluice], ["pond sluice"], {"pig_sties": [two]}).count("h6.2v6.2") == 0


def test_a_rotated_footprint_is_held_clear_by_its_whole_box(lifted_sluice: None) -> None:
    """The hole is the axis-aligned box of the ROTATED glyph - a superset, so it is never smaller than
    the thing it protects."""
    from l7r.diagram.interactive.page import hit_layer

    sluice = '<line x1="90" y1="100" x2="110" y2="100" stroke="#37637F" stroke-width="2.4"/>'
    out = hit_layer([sluice], ["pond sluice"], {"byres": [{"x": 100.0, "y": 100.0, "w": 10.0, "h": 10.0, "rot": 45}]})
    assert "h14.3v14.3" in out, f"10 x 10 turned 45 degrees needs a 14.14 px box, plus the 0.2 pad: {out}"


def test_a_lifted_class_the_priority_list_forgets_still_wins(lifted_sluice: None) -> None:
    """The list ranks the lifted classes against each other; a class lifted BECAUSE it cannot otherwise
    be hit must not land in the weakest place because someone forgot to add it (the first version's
    `-1` fallback did exactly that)."""
    from l7r.diagram.interactive import page as pg

    ditch = '<line x1="0" y1="10" x2="100" y2="10" stroke="#6E93A8" stroke-width="3.5"/>'
    sluice = '<line x1="48" y1="10" x2="52" y2="10" stroke="#37637F" stroke-width="2.4"/>'
    lifted = pg.HIT_ON_TOP | {"irrigation ditch"}
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(pg, "HIT_ON_TOP", lifted)
        mp.setattr(pg, "HIT_PRIORITY", ("irrigation ditch",))  # the sluice is the forgotten one
        out = pg.hit_layer([ditch, sluice], ["irrigation ditch", "pond sluice"])
    assert out.index('data-k="irrigation ditch"') < out.index('data-k="pond sluice"'), out


def test_every_keep_clear_key_makes_its_holes() -> None:
    """`HIT_KEEP_CLEAR` names manifest keys, and a key whose records carry some other shape - a well's
    `x,y,r`, a footbridge's `span`, a sluice gate's bare `x,y,rot` - yields NO hole and NO error
    (settlement-review round 3). So the count is asserted against a real manifest: one hole per record,
    plus one per auxiliary polygon (a `poly` apron; the duck pen's `wet` retired with it, 269 E9), plus the canvas rectangle."""
    import json
    from pathlib import Path

    from l7r.diagram.interactive.page import HIT_KEEP_CLEAR, _keep_clear_clip

    man = json.loads((Path(__file__).resolve().parents[2] / "pool/hamlets/kuwabata/kuwabata.json").read_text())
    for k in HIT_KEEP_CLEAR:
        assert man.get(k), f"{k} records nothing on this map, so the count below cannot see it go wrong"
    recs = [r for k in HIT_KEEP_CLEAR for r in man.get(k) or []]
    aprons = sum(1 for r in recs if isinstance(r.get("poly"), list) and len(r["poly"]) > 2)
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
    assert "lead" not in card and "label" not in card and card["basis"], "no accuracy claim; the basis is stated (FR-001, FR-008a)"


def test_the_lane_default_names_the_village_the_notes_name() -> None:
    notes = MapNotes(place={"district": "Hoshigaoka", "district direction": "east"}, features={})
    data = _render([PLACE, "village lane"], {"scale": "hamlet", "name": "Inashiro", "households": 15}, notes)
    # feature 319 (plan D10): a hamlet's own sentence is the title card's, never the lane modal's
    assert data["village lane"]["on_this_map"] == ""
    assert "The connector track leads out of the hamlet toward Hoshigaoka, the main village of the district it belongs to; the lanes between the farmsteads feed it." in data[PLACE]["facts"]


def test_an_authored_lane_annotation_beats_the_default() -> None:
    notes = MapNotes(place={"district": "Hoshigaoka"}, features={"village lane": "This one climbs the spur first."})
    data = _render([PLACE, "village lane"], {"scale": "hamlet", "name": "Inashiro", "households": 15}, notes)
    assert data["village lane"]["on_this_map"] == "", "feature 319: a hamlet reads no `### Features`"
    town = _render([PLACE, "village lane"], {"scale": "town", "name": "Ubame", "households": 400}, notes)
    assert town["village lane"]["on_this_map"] == "This one climbs the spur first.", "a tier not yet standardized keeps its notes"


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
        assert "lead" not in d and "label" not in d, key  # feature 319: nothing class-level is announced


def test_an_element_with_no_extent_is_treated_as_touching_everything() -> None:
    """`_hits` decides whether two drawn elements merge into one hover group. An extent of `None` means
    the emitter recorded no geometry for that element, and the safe answer is YES: refusing to merge
    would split one feature into two hover groups on the sheet, which the reader sees, while merging
    slightly too eagerly costs nothing visible. Boxes and circles both go through here, and a circle
    is tested AS a circle - two crowns whose boxes overlap at a corner do not actually touch."""
    from l7r.diagram.interactive.extents import _hits

    assert _hits(None, (0.0, 0.0, 5.0)) is True
    assert _hits((0.0, 0.0, 5.0), None) is True
    assert _hits(None, None) is True
    # circles: touching exactly at the rims counts, a hair further apart does not
    assert _hits((0.0, 0.0, 5.0), (10.0, 0.0, 5.0)) is True
    assert _hits((0.0, 0.0, 5.0), (10.1, 0.0, 5.0)) is False


# ---- feature 199: a merged scatter is written as one path per cell (GM 2026-09-07) -----------------


def _blades(n: int, cells: list[tuple[int, int]], style: str = 'stroke="#000"') -> str:
    """`n` same-styled lines, the i-th anchored in `cells[i % len(cells)]` (TILE px cells), interleaved
    so every cell's members are separated by the others' - the shape a scatter actually has."""
    from l7r.diagram.interactive.page import TILE

    out = []
    for i in range(n):
        cx, cy = cells[i % len(cells)]
        x = cx * TILE + 10 + (i % 37) * 10
        y = cy * TILE + 10 + (i % 29) * 10
        out.append(f'<line x1="{x:g}" y1="{y:g}" x2="{x + 2:g}" y2="{y + 3:g}" {style}/>')
    return "".join(out)


def _anchor_cells(d: str) -> list[tuple[int, int]]:
    """The TILE cells of a merged path's subpath anchors, in order of first appearance. A line subpath
    starts at its anchor; an arc subpath (a circle or ellipse) starts at `cx - rx`, so its anchor - the
    center - is that plus the first arc radius."""
    import math

    from l7r.diagram.interactive.page import TILE

    cells: list[tuple[int, int]] = []
    for m in re.finditer(r"M(-?[\d.]+),(-?[\d.]+)(a(-?[\d.]+))?", d):
        x, y = float(m.group(1)), float(m.group(2))
        if m.group(3):
            x += float(m.group(4))
        c = (math.floor(x / TILE), math.floor(y / TILE))
        if c not in cells:
            cells.append(c)
    return cells


def test_a_large_merged_scatter_is_one_path_per_cell() -> None:
    """FR-001: a bucket of TILE_MIN+ members is written as one path per cell of its anchors, the cells
    in order of first appearance, every subpath kept, the style and the line's `fill="none"` on each."""
    from l7r.diagram.interactive.page import TILE_MIN, merge_primitives

    n = 2 * TILE_MIN + 50
    out = merge_primitives(_blades(n, [(0, 0), (1, 0), (0, 1)]))
    paths = re.findall(r'<path d="([^"]*)"([^>]*)/>', out)
    assert out.count("<line") == 0 and len(paths) == 3, out[:300]
    assert sum(d.count("M") for d, _ in paths) == n, "every blade is still drawn"
    assert [_anchor_cells(d) for d, _ in paths] == [[(0, 0)], [(1, 0)], [(0, 1)]], "one cell per path, first-appearance order"
    assert all('stroke="#000"' in a and 'fill="none"' in a for _, a in paths), "each tile carries the whole style"


def test_a_small_merged_scatter_stays_one_path() -> None:
    """FR-001's threshold: under TILE_MIN members the bucket is one path exactly as before, whatever it spans."""
    from l7r.diagram.interactive.page import TILE_MIN, merge_primitives

    out = merge_primitives(_blades(TILE_MIN - 1, [(0, 0), (1, 0), (0, 1)]))
    paths = re.findall(r'<path d="([^"]*)"', out)
    assert len(paths) == 1 and paths[0].count("M") == TILE_MIN - 1
    assert len(_anchor_cells(paths[0])) == 3, "the one path spans three cells, untiled"


def test_tiling_leaves_the_other_buckets_alone() -> None:
    """FR-006: a run that mixes a tiled bucket with a small one leaves the small one as it was, in its place."""
    from l7r.diagram.interactive.page import TILE, TILE_MIN, merge_primitives

    far = 5 * TILE + 20
    crowns = "".join(f'<circle cx="{far + i * 30:g}" cy="{far:g}" r="4" fill="#0a0"/>' for i in range(3))
    out = merge_primitives(_blades(TILE_MIN + 50, [(0, 0), (1, 0)]) + crowns)
    paths = re.findall(r'<path d="([^"]*)"([^>]*)/>', out)
    assert len(paths) == 3 and out.count("<circle") == 0
    assert [_anchor_cells(d) for d, _ in paths[:2]] == [[(0, 0)], [(1, 0)]]
    assert paths[2][0].count("M") == 3 and "a4,4" in paths[2][0] and 'fill="#0a0"' in paths[2][1], "the crowns are one path, after the blades"


def test_a_round_marks_cell_is_its_centers_not_where_its_arc_starts() -> None:
    """FR-001 / D6: the anchor of a circle or ellipse is its CENTER. Its subpath starts a radius to the
    left, which can sit in the neighboring cell."""
    from l7r.diagram.interactive.page import TILE, _cell

    assert _cell("circle", {"cx": f"{TILE + 2:g}", "cy": "10", "r": "5"}) == (1, 0)
    assert _cell("ellipse", {"cx": f"{TILE - 1:g}", "cy": f"{TILE:g}", "rx": "5", "ry": "3"}) == (0, 1)
    assert _cell("line", {"x1": "-1", "y1": "0", "x2": "5", "y2": "5"}) == (-1, 0)


def test_a_page_without_its_raster_never_calls_the_encoder_and_is_the_vector_only_form(monkeypatch) -> None:
    """Feature 208 FR-001 (GM 2026-09-07: "not write it at all for test rolls where it is not needed"): with
    `with_raster=False` neither the picture nor the id map is made - the encoder would raise if it were called -
    and the page is the vector-only form (`"r": 0`, no image element) a host without resvg gets; with the
    default the same strings get their picture."""
    from l7r.diagram.interactive import page as page_mod
    from l7r.diagram.interactive import raster

    strings = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">', RECT, "</svg>"]
    tags = [None, "farmhouse", None]

    def boom(*_a, **_kw):
        raise AssertionError("the raster was made for a page that asked for none")

    monkeypatch.setattr(raster, "picture", boom)
    monkeypatch.setattr(raster, "id_map", boom)
    plain = render_page(strings, tags, "T", with_raster=False)
    assert '"raster": {"r": 0}' in plain and 'id="raster"' not in plain
    assert page_mod.raster_wanted(False, (0.0, 0.0, 40.0, 40.0)) is False
    assert page_mod.raster_wanted(True, None) is False, "no viewBox, no picture - as before"
    assert page_mod.raster_wanted(True, (0.0, 0.0, 40.0, 40.0)) is True
    monkeypatch.undo()
    full = render_page(strings, tags, "T")
    assert 'id="raster"' in full and '"r": 0' not in full


def test_merge_primitives_returns_a_string_with_under_two_elements_untouched_without_scanning() -> None:
    """Feature 225 FR-005: the C-speed count runs before the element scan; one element is never merged."""
    one = '<circle cx="1" cy="2" r="3" fill="#2F6B35"/>'
    assert merge_primitives(one) is one and merge_primitives("") == "" and merge_primitives("<g></g>") == "<g></g>"
    two_uses = '<use href="#a"/><use href="#b"/>'  # two self-closing elements, neither a primitive: past the count, nothing to merge
    assert merge_primitives(two_uses) is two_uses


def test_the_windbreak_pop_up_names_its_side_and_an_authored_note_beats_it() -> None:
    """Feature 261: the windbreak's `on_this_map` says which side the belt is on and why, unless the notes say."""
    meta = {"scale": "hamlet", "name": "Kashikawa", "households": 20, "windward": "NW", "wind_source": "regional"}
    data = _render([PLACE, "windbreak"], meta)
    # feature 319 (plan D10): the side and its reason are the title card's fact, and a hamlet reads no `### Features`
    assert data["windbreak"]["on_this_map"] == "" and any(f.startswith("Here the belt stands toward the northwest of the houses") for f in data[PLACE]["facts"])
    notes = MapNotes(place={}, features={"windbreak": "This one is planted on the old dike."})
    assert _render([PLACE, "windbreak"], meta, notes)["windbreak"]["on_this_map"] == "", "a hamlet's modal is the same on every map"


def test_the_merges_bucket_grids_change_no_byte(monkeypatch):
    """Feature 278 (FR-011): `_refused` asks a grid of each bucket's extents instead of walking them. Over a dense,
    interleaved scatter - lines and circles in several styles, some translucent, some outlined, some wider than the
    grid's big-box bound - the merged page is byte-identical to the one the whole-list walk wrote (the grid forced to
    return everything it holds)."""

    from l7r.diagram.interactive import page as pg

    rng = random.Random(278)
    parts = []
    for _ in range(3000):
        k = rng.random()
        if k < 0.45:
            x, y = rng.uniform(0, 1500), rng.uniform(0, 1500)
            parts.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x + rng.uniform(-9, 9):.1f}" y2="{y + rng.uniform(-9, 9):.1f}" stroke="#{rng.choice(["6a7", "8b5"])}" stroke-width="1"/>')
        elif k < 0.9:
            style = rng.choice(['fill="#2a4"', 'fill="#2a4" opacity="0.8"', 'fill="#475" stroke="#123" stroke-width="0.5"'])
            parts.append(f'<circle cx="{rng.uniform(0, 1500):.1f}" cy="{rng.uniform(0, 1500):.1f}" r="{rng.uniform(1, 14):.1f}" {style}/>')
        elif k < 0.97:
            x, y = rng.uniform(0, 1500), rng.uniform(0, 1500)
            parts.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x + rng.uniform(-1600, 1600):.1f}" y2="{y + rng.uniform(-1600, 1600):.1f}" stroke="#6a7" stroke-width="1"/>')
        else:
            parts.append(f'<rect x="{rng.uniform(0, 1500):.1f}" y="{rng.uniform(0, 1500):.1f}" width="30" height="20" fill="#999"/>')
    svg = "<g>" + "".join(parts) + "</g>"
    indexed = pg.merge_primitives(svg)

    def everything(self, e):
        return list(self.big) + [x for b in self.cells.values() for x in b]

    monkeypatch.setattr(pg._BoxGrid, "near", everything)
    assert pg.merge_primitives(svg) == indexed
    assert indexed.count("<path") > 5 and len(indexed) < len(svg), "non-vacuity: the scatter merged"


def test_an_unreadable_extent_is_refused_by_any_bucket_holding_something():
    """Feature 278: with the bucket grids, an element whose extent cannot be read still touches everything - a bucket
    that skipped anything refuses it, an empty one does not - and a member with no extent marks a translucent bucket as
    touching every newcomer."""
    from l7r.diagram.interactive.extents import _BoxGrid, _file_extent, _refused

    def bucket(translucent=False):
        return {"blocked": False, "translucent": translucent, "outlined": False, "extents": [], "skip": [], "ext_grid": _BoxGrid(), "ext_none": False, "skip_grid": _BoxGrid()}

    b = bucket()
    assert _refused(b, None) is False
    b["skip"].append((0.0, 0.0, 5.0, 5.0))
    b["skip_grid"].add((0.0, 0.0, 5.0, 5.0))
    assert _refused(b, None) is True
    t = bucket(translucent=True)
    _file_extent(t, None)
    assert t["ext_none"] is True and _refused(t, (500.0, 500.0, 2.0)) is True


def test_a_hamlet_card_states_its_grove_sides_as_a_choice_not_a_fact() -> None:
    """Feature 319 (plan D10): the farm grove's sides are a CHOICE on the title card (`choices.json` `grove_sides`), so the
    card's facts never repeat them as a sentence."""
    from l7r.diagram.interactive.place import homestead_grove_default

    meta = {"scale": "hamlet", "name": "Kashikawa", "households": 20, "grove_sides": 3, "settlement_form": "dispersed"}
    sentence = homestead_grove_default(meta)
    data = _render([PLACE, "homestead grove"], meta)
    assert sentence and sentence not in data[PLACE]["facts"]
    assert data["homestead grove"]["on_this_map"] == ""


def test_a_village_map_keeps_its_grove_sides_sentence_on_the_grove_modal() -> None:
    """Feature 319: only a HAMLET's card carries its choices; a tier not yet standardized (a village) keeps the farm grove's
    sides as the grove modal's own sentence (feature 291, FR-009)."""
    from l7r.diagram.interactive.place import homestead_grove_default

    meta = {"scale": "village", "name": "V", "households": 40, "grove_sides": 3, "settlement_form": "dispersed"}
    data = _render(["homestead grove"], meta)
    assert data["homestead grove"]["on_this_map"] == homestead_grove_default(meta) != ""
