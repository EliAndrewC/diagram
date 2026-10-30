"""The combined search (feature 447 amendment 3): both searches run, their hits merged by source, each source printed once, what
was shown under a key never shown again - with the semantic index's stand-in model, so no test loads the real one."""

from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "record"))
sys.path.insert(0, str(REPO / "tests" / "tooling"))
import research_search as rs  # noqa: E402
import semantic_index as si  # noqa: E402
from test_semantic_index import Fake, Store  # noqa: E402

pytestmark = pytest.mark.tooling


def _corpus(tmp: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path]:
    archive, root = tmp / "archive", tmp / "repo"
    for cap, body in {
        "ab/x1/t1": "the paddy field lay below the intake, one tan to a plot",
        "ab/x2/t1": "a temple roof of cypress bark",
        "cd/y1/t1": "一枚の田 one plot of paddy measured three se",
    }.items():
        (archive / cap).mkdir(parents=True)
        (archive / cap / "text.txt").write_text(body)
    (archive / "gm-copies").mkdir()
    (archive / "gm-copies" / "book.pdf.txt").write_text("paddy plot sizes in the survey registers, paddy and plot again")
    (archive / ".git").mkdir()
    (archive / ".git" / "x.txt").write_text("paddy plot never read")
    q = root / si.QUESTIONS
    q.mkdir(parents=True)
    (q / "0005-rice-paddies.html").write_text("<h2>Rice paddies</h2><p>a paddy plot of one tan</p>")
    (q / "0005-rice-paddies.originals.html").write_text("<p>paddy plot never indexed</p>")
    return archive, root


def test_a_source_is_a_capture_a_gm_copy_or_a_record_page() -> None:
    assert rs.source_of("ab/x1/t1/text.txt") == "ab/x1"
    assert rs.source_of("gm-copies/book.pdf.txt") == "gm-copies/book.pdf.txt"
    assert rs.source_of("research/questions/0005-rice-paddies.html") == "record 0005"


def test_both_searches_merge_by_source_and_each_source_is_printed_once(tmp_path: pathlib.Path) -> None:
    archive, root = _corpus(tmp_path)
    si.build(archive, root, Fake(), log=lambda _s: None)
    rows, found, held = rs.search(archive, root, tmp_path / "home", ["paddy plot"], [["paddy", "plot"], ["cypress"]], Fake())
    sources = [r["source"] for r in rows]
    assert len(sources) == len(set(sources)) == found and held == 0, "one row a source"
    by = {r["source"]: r["by"] for r in rows}
    assert by["gm-copies/book.pdf.txt"] == {"index", "text"} and by["ab/x2"] >= {"text"}, "what found it is kept"
    assert "record 0005" in by and not any(".git" in s for s in sources), "the record is searched, git never"
    assert sources[0] in {"gm-copies/book.pdf.txt", "record 0005", "ab/x1"}, "a source both find rises"
    assert "[index+text]" in "\n".join(rs.render(archive, root, rows))


def test_under_a_key_a_later_call_prints_only_new_sources(tmp_path: pathlib.Path) -> None:
    archive, root = _corpus(tmp_path)
    si.build(archive, root, Fake(), log=lambda _s: None)
    home = tmp_path / "home"
    first, _found, held = rs.search(archive, root, home, [], [["paddy"]], Fake(), key="field size", limit=2)
    assert [r["source"] for r in first][0] == "record 0005" and len(first) == 3, "the record's page apart, then two sources"
    assert held == 0 and rs.seen_path(home, "field size").name == "field-size.json"
    again, found, held = rs.search(archive, root, home, [], [["paddy"]], Fake(), key="field size", limit=2)
    assert held == 3 and len(again) == 1 and not {r["source"] for r in first} & {r["source"] for r in again} and found == 4
    import os  # noqa: PLC0415

    os.utime(rs.seen_path(home, "field size"), (0, 0))
    stale, _f, held = rs.search(archive, root, home, [], [["paddy"]], Fake(), key="field size", limit=2)
    assert held == 0 and len(stale) == 3, "a key's memory is forgotten after a day"
    lines = rs.render(archive, root, first)
    assert lines[0].startswith("-- the record's pages") and lines[2].startswith("-- the archive's sources")


def test_a_term_search_needs_no_index_and_a_question_with_no_index_finds_nothing(tmp_path: pathlib.Path) -> None:
    archive, root = _corpus(tmp_path)
    assert rs.meaning(rs.load_index(tmp_path / "none"), ["paddy"], Fake()) == [[]]
    rows, _f, _h = rs.search(archive, root, tmp_path / "home", [], [["cypress"]], Fake())
    assert [r["source"] for r in rows] == ["ab/x2"]
    assert rs.text(tmp_path / "missing", tmp_path / "missing", [["x"]]) == [[]]


def test_main_asks_for_something_says_when_there_is_no_index_and_prints_the_merge(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    import archive as ar  # noqa: PLC0415

    store = Store(tmp_path)
    root = tmp_path / "repo"
    (root / si.QUESTIONS).mkdir(parents=True)
    monkeypatch.setattr(ar.src, "repo_root", lambda: root)
    monkeypatch.setattr(ar, "home_of", lambda _r: tmp_path / "home")
    assert rs.main(["--terms", "|"], embed=Fake(), store=store) == 2
    assert rs.main(["--q", "paddy"], embed=Fake(), store=store) == 1
    assert "no index yet" in capsys.readouterr().err
    (store.dir / "ab" / "x").mkdir(parents=True)
    (store.dir / "ab" / "x" / "text.txt").write_text("the paddy field lay below the intake")
    si.build(store.dir, root, Fake(), log=lambda _s: None)
    assert rs.main(["--q", "paddy intake", "--terms", "paddy", "--key", "k", "--limit", "5"], embed=Fake(), store=store) == 0
    assert rs.main(["--terms", "intake"], store=store) == 0, "a term search loads no model"
    out = capsys.readouterr().out
    assert "1 of 1 source(s), 0 already shown under key 'k'" in out and "ab/x  [index+text]" in out and "the paddy field" in out
    (store.dir / "ab" / "y").mkdir(parents=True)
    (store.dir / "ab" / "y" / "text.txt").write_text("another intake")
    assert rs.main(["--terms", "intake", "--limit", "1"], store=store) == 0
    assert "1 more not printed" in capsys.readouterr().out
