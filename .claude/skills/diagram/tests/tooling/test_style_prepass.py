"""`scripts/_style_prepass.py` - the mechanical half of the style guide, handed to `record-style` (feature 292)."""

from __future__ import annotations

import importlib.util
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[5]


def _load(name: str):  # noqa: ANN202
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


sp = _load("_style_prepass")


def test_a_metric_figure_in_our_own_prose_owes_its_conversion_and_a_quotation_never_does() -> None:
    """GM 2026-09-29: *"any time we expressed something in meters, then we also convert it to feet ... this rule about
    units only applies to text that we ourselves write"* - so the source's own words, in corner brackets, a `<q>` or a
    comment, are never listed, and a figure already carrying `(~N ft)` or `(~N in)` is not."""
    html = (
        "<p>Trees 11 to 28 m tall, about 15 m (~49 ft) on average, trunks 10 cm (~4 in) across, a hall 12 m wide."
        "<!-- 30 m in a comment --> Its source: 「28 m」 and <q>5 m</q>.</p>"
    )
    found = sp.unconverted(html)
    assert [f.split(" - ")[0] for f in found] == ["11 to 28 m", "12 m"], found
    assert sp.unconverted("<p>a 5 min walk, 8.5 ft of crown</p>") == [], "minutes and feet are not metric figures"
    assert sp.unconverted("<p>2 ha (~5 acres) and 3 km (~2 miles)</p>") == []


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
    assert out.count("  none") == 5, "020's metric list, both GM lists and both empty lead-line lists say none"


def test_a_visible_gm_ruling_is_listed_and_one_in_a_comment_is_not() -> None:
    """GM 2026-09-29: a ruling is kept for later sessions in an HTML comment and never shown - so every visible "GM"
    is listed, a quoted ruling included, and a comment's is not."""
    html = "<p>The GM ruled on 2026-09-29: <q>two sides is the minimum</q>. <!-- the GM's words: ... --> A GMT clock.</p>"
    found = sp.gm_mentions(html)
    assert len(found) == 1 and "GM ruled" in found[0], found


def test_the_command_reads_a_page_s_question_and_refuses_one_that_matches_nothing(capsys) -> None:  # noqa: ANN001
    assert sp.main(["homesteads", "--root", str(REPO), "--section", "010"]) == 0
    assert "== 010-" in capsys.readouterr().out
    assert sp.main(["homesteads", "--root", str(REPO), "--section", "no-such-question-anywhere"]) == 2
