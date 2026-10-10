"""`scripts/pages/claims.py` (feature 376 FR-001): the research claims sheet, claimed and asked through one tool.

WHAT THESE PROVE (SC-001): on a sheet the size of the real one (1,138 lines on 2026-10-10), a claim and a query print
at most five lines; another session's live claim refuses an overlapping claim and is named alone; a release frees it;
an old free-text line is matched by its old page and number; a claim whose feature is settled is not live; a stale
claim is released by name only with a reason; and two claims race through the lock.
"""

from __future__ import annotations

import importlib.util
import pathlib
import threading

REPO = pathlib.Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("claims", REPO / "scripts/pages/claims.py")
assert _spec and _spec.loader
claims = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(claims)


def _top(tmp: pathlib.Path, name: str = "clone-a") -> pathlib.Path:
    """A clone named `name` under a mirror with one closed feature (300) and one open (376), and an old-page map."""
    mirror = tmp / "mirror"
    for d, status in (("300-done-thing", "Done 2026-10-01"), ("376-open-thing", "In progress")):
        (mirror / "specs" / d).mkdir(parents=True, exist_ok=True)
        (mirror / "specs" / d / "spec.md").write_text(f"# {d}\n\n**Status**: {status}\n")
    top = mirror / ".clones" / name
    (top / "research").mkdir(parents=True, exist_ok=True)
    (top / "research" / "moved-303.json").write_text('{"files": {"homesteads/060-the-byre.html": "questions/0071-the-byre.html"}}')
    (top / "scripts").mkdir(exist_ok=True)
    (top / "scripts" / "speckit-todo.py").write_text((REPO / "scripts" / "speckit-todo.py").read_text())
    (top / ".specify").mkdir(exist_ok=True)
    (top / ".specify" / "affects.json").write_text((REPO / ".specify" / "affects.json").read_text())
    return top


def _sheet(tmp: pathlib.Path, rows: list[str], filler: int = 0) -> pathlib.Path:
    sheet = tmp / "CLAIMS.md"
    pad = [f"old-session-{i} | 2{i % 50:02d} | Q={1000 + i} | in progress | 2026-09-27" for i in range(filler)]
    sheet.write_text("# Research claims\n\n" + "\n".join(pad + rows) + "\n")
    return sheet


def test_a_claim_on_free_questions_is_recorded_and_prints_one_line(tmp_path: pathlib.Path) -> None:
    top, sheet = _top(tmp_path), _sheet(tmp_path, [], filler=1138)
    code, text = claims.claim(["0060", "0246"], "376", "in progress", top, sheet, today="2026-10-10")
    assert code == 0 and text.count("\n") == 0 and "clone-a | 376 | Q=0060,0246 | in progress | 2026-10-10" in text
    assert sheet.read_text().splitlines()[-1] == "clone-a | 376 | Q=0060,0246 | in progress | 2026-10-10"
    code, text = claims.query(["0060"], top, sheet)
    assert code == 1 and len(text.splitlines()) <= 5 and "clone-a" in text


def test_another_sessions_live_claim_refuses_naming_only_it_and_a_release_frees_it(tmp_path: pathlib.Path) -> None:
    sheet = _sheet(tmp_path, ["clone-b | 376 | Q=0246 | in progress | 2026-10-10"], filler=1138)
    top = _top(tmp_path)
    before = sheet.read_text()
    code, text = claims.claim(["0060", "0246"], "376", "in progress", top, sheet)
    assert code == 1 and "REFUSED" in text and "clone-b | 376 | Q=0246" in text and len(text.splitlines()) <= 5
    assert sheet.read_text() == before, "a refused claim records nothing"
    top_b = _top(tmp_path, "clone-b")
    assert claims.claim(["0246"], "376", "done", top_b, sheet)[0] == 0
    assert claims.query(["0246"], top, sheet) == (0, "research-claims: no live claim on 0246")
    assert claims.claim(["0060", "0246"], "376", "in progress", top, sheet)[0] == 0


def test_an_old_free_text_line_is_matched_by_its_old_page_and_number(tmp_path: pathlib.Path) -> None:
    sheet = _sheet(tmp_path, ["Diagram shrines | 376 | homesteads/060 and homesteads 060, the byre | in progress"])
    code, text = claims.query(["0071"], _top(tmp_path), sheet)
    assert code == 1 and "Diagram shrines" in text


def test_a_claim_whose_feature_is_settled_is_not_live(tmp_path: pathlib.Path) -> None:
    sheet = _sheet(tmp_path, ["clone-b | 300 | Q=0060 | in progress | 2026-09-27"])
    assert claims.query(["0060"], _top(tmp_path), sheet)[0] == 0, "feature 300 is Done, so its forgotten claim is retired"


def test_a_stale_claim_is_released_by_name_only_with_a_reason(tmp_path: pathlib.Path) -> None:
    sheet = _sheet(tmp_path, ["clone-b | 376 | Q=0060 | in progress | 2026-10-01"])
    top = _top(tmp_path)
    assert claims.claim(["0060"], "376", "in progress", top, sheet, release="clone-b")[0] == 2
    code, text = claims.claim(["0060"], "376", "in progress", top, sheet, release="clone-b", why="its session ended 2026-10-01")
    assert code == 0 and "released by clone-a: its session ended 2026-10-01" in sheet.read_text().splitlines()[-1]
    assert claims.query(["0060"], top, sheet)[0] == 0


def test_two_claims_at_once_go_through_the_lock_and_one_is_refused(tmp_path: pathlib.Path) -> None:
    sheet = _sheet(tmp_path, [])
    results: list[int] = []
    tops = [_top(tmp_path, "clone-a"), _top(tmp_path, "clone-b")]
    threads = [threading.Thread(target=lambda t=t: results.append(claims.claim(["0500"], "376", "in progress", t, sheet)[0])) for t in tops]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert sorted(results) == [0, 1]


def test_a_query_naming_no_question_is_refused_with_the_form(tmp_path: pathlib.Path) -> None:
    try:
        claims.asked("the byre")
    except SystemExit as e:
        assert 'Q="0060 0246"' in str(e)
    else:
        raise AssertionError("a query naming no number must be refused")
