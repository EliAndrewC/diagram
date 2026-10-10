"""File, don't fix (feature 375, FR-006): a check's finding on words the change did not write is filed as a row, not fixed.

In feature 372 a check proposed small fixes to blocks a wave never touched, and each fix re-owed a round. A check bundle now
says which blocks and notes the delta wrote (`changed_section`), the page checks put a finding on anything else under
`OUTSIDE THE CHANGE`, and `make record-checked REPLY=` files those lines as open rows of the active feature.
"""

from __future__ import annotations

import json
import pathlib
import subprocess

from tests.tooling.test_modal_checks import _load

cb = _load("check_bundle")
ro = _load("record_owed")

PAGE = '<h2 id="wells">Wells</h2>\n<p>A well stands by the door.</p>\n<p>Its curb is stone.</p>\n'
NOTES = '<li data-note="a">A note.</li>\n<li data-note="b">B note.</li>\n'


def _git(root: pathlib.Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), "-c", "user.email=t@t", "-c", "user.name=t", *args], check=True, capture_output=True)


def test_the_bundle_names_the_blocks_and_notes_the_change_wrote(tmp_path: pathlib.Path) -> None:
    q = tmp_path / "research" / "questions"
    q.mkdir(parents=True)
    (q / "0105-wells.html").write_text(PAGE)
    (q / "0105-wells.notes.html").write_text(NOTES)
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "base")
    rels = ["research/questions/0105-wells.html", "research/questions/0105-wells.notes.html"]
    assert "(none - every block and note predates this change" in cb.changed_section(tmp_path, rels)
    (q / "0105-wells.html").write_text(PAGE.replace("by the door", "by the kitchen"))
    (q / "0105-wells.notes.html").write_text(NOTES.replace("B note.", "B note, rewritten."))
    text = cb.changed_section(tmp_path, rels)
    assert "changed-block: research/questions/0105-wells.html | A well stands by the kitchen." in text
    assert "curb" not in text and "changed-note: research/questions/0105-wells.notes.html | b" in text and "| a\n" not in text
    assert "OUTSIDE THE CHANGE" in text


REPLY = """quote-check: 0105 - READABLE 2/2, VERBATIM 2/2

1. the kitchen sentence: fine.

## OUTSIDE THE CHANGE

- `research/questions/0105-wells.html` | Its curb is stone | no footnote for the stone curb
- research/questions/0105-wells.notes.html | note a | the page number is missing
not a row
## later heading
- x | y | z
"""


def test_a_reply_s_outside_findings_are_filed_as_open_rows(tmp_path: pathlib.Path) -> None:
    assert ro.outside("no section here") == []
    rows = ro.outside(REPLY)
    assert rows == [("research/questions/0105-wells.html", "Its curb is stone", "no footnote for the stone curb"), ("research/questions/0105-wells.notes.html", "note a", "the page number is missing")]
    (tmp_path / ".specify").mkdir()
    (tmp_path / ".specify" / "feature.json").write_text('{"feature_directory": "specs/375-x"}')
    filed = ro.file_outside(tmp_path, "quote-check", REPLY)
    found = [json.loads(line) for line in (tmp_path / "specs/375-x/found.jsonl").read_text().splitlines()]
    assert found == filed and {r["status"] for r in found} == {"open"} and found[0]["check"] == "quote-check"
    assert ro.file_outside(tmp_path, "quote-check", "nothing outside") == []
    (tmp_path / ".specify" / "feature.json").write_text("not json")
    ro.file_outside(tmp_path, "record-format", REPLY)
    assert (tmp_path / "specs/_unfiled/found.jsonl").is_file(), "no active feature: still filed, never dropped"
