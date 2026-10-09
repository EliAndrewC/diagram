"""`scripts/record/attempts.py` - what each source was tried for, and what came of it (feature 312, FR-015 - FR-018).

WHAT THESE PROVE. A line carries the URL normalized, the question, what was sought and one of the spec's outcomes, and a
blocked URL is never written; the seed maps every ledger row - a stem kept, an old id through `moved-303.json` or kept as
`old:`, a free-text entry taken as what was sought, a row with no question `unknown` - with each ledger outcome mapped,
and runs once; a URL's report names its attempts and the filter's verdict (not kept, or kept as an uncited entry); a key's
and a question's reports find theirs; the command line adds and shows. NO NETWORK.
"""

from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import sys

import pytest
from tests._scripts import script

REPO = pathlib.Path(__file__).resolve().parents[5]


def _load(name: str):  # noqa: ANN202
    spec = importlib.util.spec_from_file_location(name, script(name))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = sys.modules[name.lstrip("_")] = mod  # the old name and the one a sibling imports it by (2026-10-08)
    spec.loader.exec_module(mod)
    return mod


at = _load("_attempts")


def _home() -> pathlib.Path:
    return pathlib.Path(os.environ["L7R_SOURCES_HOME"])


@pytest.fixture(autouse=True)
def _attempts_here(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The conftest's seam pointed at this test's own tree, so a test's log is the tree it builds."""
    monkeypatch.setenv("L7R_ATTEMPTS_ROOT", str(tmp_path))


def _root(tmp_path: pathlib.Path) -> pathlib.Path:
    (tmp_path / ".git").mkdir()
    r = tmp_path / at.RESEARCH
    r.mkdir(parents=True)
    (r / "moved-303.json").write_text(json.dumps({"numbers": {"cities/government 230": "0150"}}), encoding="utf-8")
    return tmp_path


def test_a_line_is_normalized_and_its_outcome_checked(tmp_path: pathlib.Path) -> None:
    root = _root(tmp_path)
    x = at.add(root, "https://www.example.org/a/", "0012", "the dike width", feature="312", route="source-pages")
    assert (x["url"], x["raw"], x["question"], x["outcome"], x["feature"]) == ("example.org/a", "https://www.example.org/a/", "0012", "unknown", "312")
    assert at.read(root) == [x]
    with pytest.raises(ValueError, match="pending"):
        at.line("https://example.org", "0012", "x", "pending")


def test_an_empty_question_is_unknown_and_nothing_is_written_for_no_lines(tmp_path: pathlib.Path) -> None:
    root = _root(tmp_path)
    assert at.line("https://example.org", "", "x")["question"] == "unknown"
    at.write(root, [])
    assert not (root / at.LOG).exists()


def test_a_blocked_url_is_never_written(tmp_path: pathlib.Path) -> None:
    root = _root(tmp_path)
    with pytest.raises(Exception, match="the attempts log refused"):
        at.add(root, "https://grokipedia.com/page/X", "0012", "anything")


def test_the_seed_maps_every_ledger_row_once(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture) -> None:
    root = _root(tmp_path)
    rows = [
        {"url": "a.org/1", "raw": "https://a.org/1", "utc": "2026-09-01T00:00:00+00:00", "feature": "288", "questions": ["0042"], "outcome": "cited:a-key"},
        {"url": "a.org/2", "raw": "https://a.org/2", "utc": "2026-09-02T00:00:00+00:00", "feature": "290", "questions": ["cities/government/230", "ways/100"], "outcome": "nothing-found"},
        {"url": "a.org/3", "utc": "2026-09-03T00:00:00+00:00", "questions": ["What does it say about torii?"], "outcome": "rejected: modern"},
        {"url": "a.org/4", "utc": "2026-09-04T00:00:00+00:00", "questions": [], "outcome": "unknown-outcome"},
        {"url": "a.org/5", "questions": [], "outcome": "unreadable"},
        {"url": "grokipedia.com/page/x", "questions": [], "outcome": "pending"},
        {"raw": "no url"},
    ]
    with open(_home() / "sources-consulted.jsonl", "w", encoding="utf-8") as fh:
        fh.writelines(json.dumps(r) + "\n" for r in rows)
    assert at.seed(root, _home()) == 6
    got = [(x["url"], x["question"], x["outcome"], x["key"], x["sought"]) for x in at.read(root)]
    assert got == [
        ("a.org/1", "0042", "found", "a-key", at.UNKNOWN_SOUGHT),
        ("a.org/2", "0150", "not-found", "", at.UNKNOWN_SOUGHT),
        ("a.org/2", "old:ways/100", "not-found", "", at.UNKNOWN_SOUGHT),
        ("a.org/3", "unknown", "not-applicable", "", "What does it say about torii? (rejected: modern)"),
        ("a.org/4", "unknown", "unknown", "", at.UNKNOWN_SOUGHT),
        ("a.org/5", "unknown", "unreadable", "", at.UNKNOWN_SOUGHT),
    ]
    assert all(x["seed"] == at.SEED and x["route"] == "ledger" for x in at.read(root))
    assert at.read(root)[0]["date"] == "2026-09-01"
    assert at.seed(root, _home()) == 0
    assert "nothing written" in capsys.readouterr().err
    with open(_home() / "sources-consulted.jsonl", "a", encoding="utf-8") as fh:  # a read by a session on code without the log
        fh.write(json.dumps({"url": "a.org/9", "utc": "2026-10-02T21:57:16+00:00", "feature": "315", "questions": [], "outcome": "pending"}) + "\n")
    assert at.seed(root, _home()) == 1, "a re-run catches up the rows written since"
    assert at.read(root)[-1]["url"] == "a.org/9" and at.seed(root, _home()) == 0


def test_the_log_lives_in_the_clone_unless_the_seam_moves_it(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("L7R_ATTEMPTS_ROOT")
    assert at.base(tmp_path) == tmp_path


def test_no_moved_file_maps_nothing(tmp_path: pathlib.Path) -> None:
    (tmp_path / at.RESEARCH).mkdir(parents=True)
    assert at.old_ids(tmp_path) == {}


def test_a_report_names_the_attempts_and_the_filters_verdict(tmp_path: pathlib.Path) -> None:
    root = _root(tmp_path)
    at.add(root, "https://a.org/1", "0042", "the dike width", "not-found", key="a-key")
    at.add(root, "https://b.org/2", "0042", "the dike width", "found")
    with open(root / at.NOT_KEPT, "w", encoding="utf-8") as fh:
        fh.write(json.dumps({"url": "a.org/1", "reasons": ["modern-only"], "note": "mechanized", "date": "2026-10-02"}) + "\n")
        fh.write("not json\n")
    (root / at.UNCITED).mkdir(parents=True)
    (root / at.UNCITED / "0100-b-key.html").write_text("<p>B (https://b.org/2)</p>", encoding="utf-8")
    out = at.report(root, url="http://a.org/1/")
    assert out[0] == "attempts: http://a.org/1/ - 1 earlier attempt(s):"
    assert out[1] == "  filter verdict: NOT KEPT 2026-10-02 (modern-only - mechanized)"
    assert "Q 0042: not-found - the dike width" in out[2]
    assert at.report(root, url="https://b.org/2")[1] == "  filter verdict: KEPT, uncited: 0100-b-key.html"
    assert at.report(root, url="https://c.org/") == ["attempts: https://c.org/ - no earlier attempt"]
    assert at.report(root, key="a-key")[0] == "attempts: key a-key - 1 attempt(s)"
    q = at.report(root, q="0042")
    assert q[0] == "attempts: question 0042 - 2 attempt(s)" and "https://b.org/2" in q[2]


def test_the_command_line_adds_and_shows(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture) -> None:
    root = _root(tmp_path)
    monkeypatch.chdir(root)
    assert at.main(["add", "--url", "https://a.org/1", "--q", "0042", "--sought", "width", "--outcome", "found", "--route", "cli"]) == 0
    assert at.main(["show", "--url", "https://a.org/1"]) == 0
    assert "Q 0042: found - width" in capsys.readouterr().out
    assert at.main(["seed"]) == 0


def test_an_outcome_carries_what_its_read_sought(tmp_path: pathlib.Path) -> None:
    root = _root(tmp_path)
    at.add(root, "https://a.org/1", "0042", "the dike width")
    assert at.outcome(root, "https://a.org/1", "0042", "rejected: modern")["sought"] == "the dike width (rejected: modern)"
    x = at.outcome(root, "https://a.org/1", "0042", "cited:a-key", "a new aim")
    assert (x["outcome"], x["key"], x["sought"], x["route"]) == ("found", "a-key", "a new aim", "source-outcome")
    assert at.outcome(root, "https://z.org", "", "pending")["sought"] == at.UNKNOWN_SOUGHT
