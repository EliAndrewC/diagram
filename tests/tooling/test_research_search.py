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
    assert lines[0].startswith("-- the record's pages") and "-- the archive's sources --" in lines[3:]


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


# THE CASES THE MEASURE PASSAGE EXISTS FOR (feature 447 amendment 4, `specs/447-semantic-index/research/t05-why.md`): each run was
# shown a passage without the size and passed over the source. Their answering sentences, verbatim from the archive, each set among
# a distractor the real page also holds - the test fails if the answer is not among the measures printed.
CASES = [
    (
        "Hattori 97/97f6d769ce72",
        "おおよそ約2万㎡の広さに及びます。" + "水田跡の周辺。" * 30 + "畦によって区切られた水田の広さは、小さいもので10㎡ほど、大きいもので180㎡程度で、全体に小さな区画の水田でした。",
        ["水田"],
        "10㎡ほど",
    ),
    ("Ofuro 10/100916836bb9", "国土づくりの歴史 大きな第一歩であった。" + "水田の誕生。" * 30 + "御布呂遺跡から発見された古墳期の水田(左〕は、1区画3-5㎡で、インドネシアの", ["水田", "区画"], "3-5㎡"),
    (
        "Huizhou 04/04c46c135344",
        "其名下佃种的土地总计5号，共2.872亩。" + "鱼鳞图册的记载。" * 30 + "鳞册开载项守之等额田柒分壹厘伍毫，四户分庄共少柒丝肆忽。共积壹百陆拾步壹分陆厘",
        ["田", "亩"],
        "柒分壹厘伍毫",
    ),
    (
        "Bray 3c/3cf980c9fd08",
        "rice was domesticated 10,000 years ago in marshy areas. "
        + "the water supply was regulated. " * 30
        + "paddies were usually small by Western standards: a field twenty yards square would be considered large",
        ["field", "paddy"],
        "twenty yards",
    ),
]


@pytest.mark.parametrize(("name", "body", "terms", "answer"), CASES, ids=[c[0] for c in CASES])
def test_the_measures_printed_hold_the_answer_the_runs_passed_over(name: str, body: str, terms: list[str], answer: str) -> None:
    spans = rs.measure_passages(body, terms)
    assert len(spans) <= rs.PASSAGES and any(answer in body[s:e] for s, e in spans), f"{name}: {[body[s:e] for s, e in spans]}"


def test_measures_do_not_overlap_and_a_text_without_one_has_none() -> None:
    body = "3 se and 4 se of paddy. " + "x" * 600 + " 5 tan of paddy plot."
    spans = rs.measure_passages(body, ["paddy", "plot"])
    assert len(spans) == 2 and spans[0][1] <= spans[1][0] or spans[1][1] <= spans[0][0]
    assert rs.measure_passages("no numbers here", ["paddy"]) == []
    assert rs.MEASURE.search("31 by 40 feet") and rs.MEASURE.search("0.39 hectares") and rs.MEASURE.search("half an acre")


def test_render_adds_the_measure_line_only_when_the_shown_passages_lack_it(tmp_path: pathlib.Path) -> None:
    archive, root = tmp_path / "archive", tmp_path / "repo"
    (archive / "ab" / "x1" / "t").mkdir(parents=True)
    (root / si.QUESTIONS).mkdir(parents=True)
    body = "the paddy floor was cracked and uneven. " * 30 + "each plot of paddy measured 18 m2 at most."
    (archive / "ab" / "x1" / "t" / "text.txt").write_text(body)
    row = {"source": "ab/x1", "by": {"index"}, "passages": {"index": [("ab/x1/t/text.txt", 0, 900)]}}
    lines = rs.render(archive, root, [row], ["plot", "paddy"])
    assert any(line.lstrip().startswith("measure:") and "18 m2" in line for line in lines)
    near = {"source": "ab/x1", "by": {"index"}, "passages": {"index": [("ab/x1/t/text.txt", len(body) - 100, len(body))]}}
    assert not any("measure:" in line for line in rs.render(archive, root, [near], ["plot"])), "already shown, not repeated"
