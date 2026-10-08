"""Feature 235 (GM 2026-09-12): the census counts the record's footnotes BY KIND, and only ABSENT is a backlog.

The GM's reason for the tool: *"if we're counting things that are not actually problems in a category that is
meant to denote problems, then we're just gonna keep getting confused."* So what this file holds is that the
number the tool prints is the number in the files - a hand-built table was wrong three times while feature 232
ran, which is the whole argument for counting mechanically. Since feature 303 the rows are the record's sections.
"""

from __future__ import annotations

import collections
import re

from l7r.diagram.interactive.citations import footnote_form
from l7r.diagram.interactive.record import store
from l7r.diagram.interactive.sources import RESEARCH_DIR, canon_keys
from l7r.diagram.tools import footnote_census as fc


def real_form() -> fc.Classifier:
    canon = canon_keys()
    return lambda body: footnote_form(body, canon)


def test_the_four_kinds_are_counted_and_a_settled_absence_is_not_a_backlog() -> None:
    bodies = [
        '<a href="https://x.y/z"><code>k-1</code></a> - 「twelve characters here」',
        "no publicly readable source (searched 2026-09-12: nothing readable)",
        "no publicly readable source (searched 2026-09-12: nothing; searched again, settled 2026-09-12)",
        "no source is owed: measured on our own maps",
        "something else entirely",
    ]
    assert fc.kinds_of(bodies, real_form()) == collections.Counter({"citation": 1, "absence": 1, "settled": 1, "grounds": 1, "malformed": 1})


def test_the_census_numbers_are_the_numbers_in_the_files() -> None:
    """Counted a second way, from the raw notes files, so a classifier change cannot move the total quietly; and every
    row is a section of one half."""
    per = fc.census(real_form())
    record = store.load(RESEARCH_DIR)
    root = f"{RESEARCH_DIR}/questions"
    notes = 0
    for page in record.pages():
        try:
            with open(f"{root}/{page.notes_file}", encoding="utf-8") as fh:
                notes += len(re.findall(r'<li data-note="', fh.read()))
        except OSError:
            continue
    total = per["TOTAL"]
    assert sum(total.values()) == notes and notes > 3000, "every note of every page falls in exactly one column"
    assert not total["malformed"], f"{total['malformed']} note(s) match no form - the gate names them"
    for kind in fc.KINDS:
        assert sum(c[kind] for name, c in per.items() if name != "TOTAL") == total[kind]
    assert all(name == "TOTAL" or name.startswith(("research: ", "drawing: ")) for name in per)


def test_the_report_names_the_backlog_and_says_when_a_note_is_malformed() -> None:
    per = {
        "research: Water": collections.Counter({"citation": 3, "absence": 1}),
        "research: Cities / Urban fabric": collections.Counter({"grounds": 1, "settled": 2, "malformed": 1}),
        "TOTAL": collections.Counter({"citation": 3, "absence": 1, "grounds": 1, "settled": 2, "malformed": 1}),
    }
    out = fc.render(per)
    assert "The backlog is ABSENT: 1." in out
    assert "MALFORMED: 1 footnote(s)" in out
    assert "Cities / Urban fabric" in out and out.splitlines()[0].startswith("section")


def test_the_report_is_clean_when_nothing_is_malformed() -> None:
    out = fc.render({"research: Water": collections.Counter({"citation": 1}), "TOTAL": collections.Counter({"citation": 1})})
    assert "MALFORMED" not in out and "The backlog is ABSENT: 0." in out


def test_the_tool_runs_and_prints_the_record_s_own_census(capsys) -> None:  # noqa: ANN001
    assert fc.main([]) == 0
    out = capsys.readouterr().out
    assert "The backlog is ABSENT:" in out and "TOTAL" in out
