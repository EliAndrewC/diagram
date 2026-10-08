"""`scripts/record/style_prepass.py` - the mechanical half of the style guide, handed to `record-style` (feature 292)."""

from __future__ import annotations

import importlib.util
import pathlib
import sys

from tests._scripts import script

REPO = pathlib.Path(__file__).resolve().parents[2]


def _load(name: str):  # noqa: ANN202
    spec = importlib.util.spec_from_file_location(name, script(name))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = sys.modules[name.lstrip("_")] = mod  # the old name and the one a sibling imports it by (2026-10-08)
    spec.loader.exec_module(mod)
    return mod


sp = _load("_style_prepass")


def test_a_metric_figure_in_our_own_prose_owes_its_conversion_and_a_quotation_never_does() -> None:
    """GM 2026-09-29: *"any time we expressed something in meters, then we also convert it to feet ... this rule about
    units only applies to text that we ourselves write"* - so the source's own words, in corner brackets, a `<q>` or a
    comment, are never listed, and a figure already carrying `(~N ft)` or `(~N in)` is not."""
    html = "<p>Trees 11 to 28 m tall, about 15 m (~49 ft) on average, trunks 10 cm (~4 in) across, a hall 12 m wide.<!-- 30 m in a comment --> Its source: 「28 m」 and <q>5 m</q>.</p>"
    found = sp.unconverted(html)
    assert [f.split(" - ")[0] for f in found] == ["11 to 28 m", "12 m"], found
    assert sp.unconverted("<p>a 5 min walk, 8.5 ft of crown</p>") == [], "minutes and feet are not metric figures"
    assert sp.unconverted("<p>2 ha (~5 acres) and 3 km (~2 miles)</p>") == []
    assert sp.unconverted("<p>a mat of 90 x 180 cm (~3 x 6 ft)</p>") == [], "a dimension converts as a dimension"


def test_every_lead_line_is_listed_as_a_question_or_a_statement_with_its_body() -> None:
    """STYLE.md 3: the agent rules on each lead line - statement or question - so every one is listed, marked."""
    html = (
        "<ul><li><strong>How tall were they?</strong><br>11 to 28 m.</li>"
        "<li><strong>Farming communities have had these groves for centuries.</strong><br>The Kaga domain...<ul><li>x</li></ul></li></ul>"
    )
    assert sp.lead_lines(html) == ["Q  How tall were they?  |  11 to 28 m.", "S  Farming communities have had these groves for centuries.  |  The Kaga domain..."]


def test_the_report_names_each_fragment_and_says_none_when_clean(tmp_path: pathlib.Path) -> None:
    out = sp.report({"010-x.html": "<p>12 m wide</p>", "020-y.html": "<p>clean</p>"})
    assert "== 010-x.html" in out and "METRIC WITHOUT A CONVERSION (1)" in out and "12 m" in out
    assert out.count("  none") == 15, "every empty list of both questions says none"


def test_a_visible_gm_ruling_is_listed_and_one_in_a_comment_is_not() -> None:
    """GM 2026-09-29: a ruling is kept for later sessions in an HTML comment and never shown - so every visible "GM"
    is listed, a quoted ruling included, and a comment's is not."""
    html = "<p>The GM ruled on 2026-09-29: <q>two sides is the minimum</q>. <!-- the GM's words: ... --> A GMT clock.</p>"
    found = sp.gm_mentions(html)
    assert len(found) == 1 and "GM ruled" in found[0], found


def test_a_paragraph_or_a_bullet_over_the_bar_is_listed_and_footnotes_and_comments_do_not_count() -> None:
    """GM 2026-09-29: the opening paragraphs (133 and 68 words) are fine and the 364-word rule paragraph is not - a
    mechanical bar between them. A bullet's own text is a paragraph; its nested list is counted item by item."""
    ok = " ".join(["word"] * sp.MAX_WORDS)
    over = " ".join(["word"] * (sp.MAX_WORDS + 1))
    sup = '<sup class="fn" data-note="k"></sup>' * 40
    html = f"<p>{ok}{sup}<!-- {over} --></p><ul><li><strong>Lead.</strong><br>{over}<ul><li>{ok}</li></ul></li></ul><p class=\"spec\">{over}</p>"
    found = sp.long_paragraphs(html)
    assert [f.split(" words")[0] for f in found] == [str(sp.MAX_WORDS + 2), str(sp.MAX_WORDS + 1)], found


def test_a_year_in_a_lead_line_is_listed_with_whether_the_glossary_defines_it() -> None:
    """GM 2026-09-29: a skimmer reads one bullet alone, so a year its lead line leans on is explained there or is a
    tooltip - the prepass lists each, and says which."""
    html = "<ul><li><strong>Were the groves as large before 1868?</strong><br>x</li><li><strong>What stood in 1603?</strong><br>y</li><li><strong>Plain.</strong><br>z</li></ul>"
    assert sp.lead_line_years(html, {"1868"}) == [
        "1868 (a glossary tooltip) - Were the groves as large before 1868?",
        "1603 (NOT in the glossary) - What stood in 1603?",
    ]
    assert "YEARS IN LEAD LINES (2)" in sp.report({"x.html": html}, {"1868"})


def test_an_old_form_absence_note_and_foreign_script_in_our_words_are_listed() -> None:
    """GM 2026-09-29: the search goes in a comment, the findings are visible; and 屋敷林 in our own words is translated -
    a quotation, an original and a comment keep their own script."""
    notes = (
        '<li data-note="a">no publicly readable source (searched 2026-09-28: 屋敷林 江戸時代; read ja.wikipedia 屋敷林)</li>\n'
        '<li data-note="b">no publicly readable source<!-- searched 2026-09-29: 築地松 --> None counts them.</li>\n'
        '<li data-note="c"><a href="x"><code>k</code></a> - 「A」 (translated; <span class="orig" data-orig="c#1"></span>)</li>\n'
    )
    assert sp.old_absence(notes) == ["a"]
    found = sp.foreign_in_own_text(notes)
    assert [f.split(" - ")[0] for f in found] == ["屋敷林", "江戸時代", "屋敷林"], "the old note's visible search, not the comment's"
    assert sp.foreign_in_own_text('<p>written 垣根 in its documents; 「引用」 <!-- 註 --><span class="orig">original: 「原文」</span></p>')[0].startswith("垣根 - ")
    out = sp.report({"q.html": "<p>x</p>"}, set(), {"q.html": notes})
    assert "ABSENCE NOTE IN THE OLD FORM (1)" in out and "KANJI WITHOUT ITS GLOSS (3)" in out


def test_kanji_in_our_words_passes_only_with_its_reading_and_meaning() -> None:
    """GM 2026-09-30: *"a transliteration is not a translation"* - one format, `漢字 (romaji, "meaning")`, which a script
    can hold; the meaning is then the translation-check's to judge."""
    ok = '<p>written 垣根 (kakine, "hedge") in its documents</p>'
    assert sp.foreign_in_own_text(ok) == [] and sp.glosses(ok) == [("垣根", "kakine", "hedge")]
    assert sp.foreign_in_own_text('<p>a class (無屋敷登録人, muyashiki torokunin)</p>')[0].startswith("無屋敷登録人 - "), "a reading alone is not a gloss"
    assert sp.glosses('<p>垣根 (kakine, &quot;hedge&quot;) and "a quoted aside"</p>') == [("垣根", "kakine", "hedge")]


def test_a_sentence_resting_on_an_absence_note_is_listed_for_a_ruling() -> None:
    """GM 2026-09-30: a sentence saying what an unread page contains "looks very suspicious" - every sentence whose
    footnote is an absence note is listed, for the check to rule it a silence, a guess, or a claim to cut."""
    notes = '<li data-note="a">no publicly readable source<!-- searched 2026-09-30: x --> The page did not load.</li>\n<li data-note="b"><a href="x"><code>k</code></a> - "q"</li>\n'
    prose = '<p>A yard at Kodaira is 70 tsubo, from a page we could not read.<sup class="fn" data-note="a"></sup> Mats covered it.<sup class="fn" data-note="b"></sup></p>'
    assert sp.absence_sentences(prose, notes) == ["[a] A yard at Kodaira is 70 tsubo, from a page we could not read."]
    assert "SENTENCES RESTING ON AN ABSENCE NOTE (1)" in sp.report({"q.html": prose}, set(), {"q.html": notes})


def test_the_hook_helper_and_the_engine_name_the_same_questions_directory() -> None:
    """`hm_record.py` restates the record's questions directory because a hook helper imports nothing from the engine
    (feature 303: the sub-collections it restated before are gone)."""
    from l7r.diagram.interactive.record.questions import QUESTIONS

    assert _load("_hm_record").QUESTIONS == QUESTIONS


def test_the_command_reads_a_question_and_refuses_one_that_matches_nothing(capsys) -> None:  # noqa: ANN001
    assert sp.main(["0041", "--root", str(REPO)]) == 0
    assert "== 0041-" in capsys.readouterr().out
    assert sp.main(["9999", "--root", str(REPO)]) == 2
    assert "make style-prepass Q=" in capsys.readouterr().err
