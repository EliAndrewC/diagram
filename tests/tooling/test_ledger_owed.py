"""A ledger row for every pass of every check (feature 371).

The GM, 2026-10-10: *"a log of when our subagent checks find something that needs to be changed and when they don't, so that
we can see how often they are paying off"*. Every check's pass is logged when it returns, with its cost cells; a pass is
answered by a measured-table row carrying its check and those cells. These build a fixture log and ledger.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

from tests._scripts import script

_spec = importlib.util.spec_from_file_location("ledger_owed", script("ledger_owed.py"))
assert _spec is not None and _spec.loader is not None
lo = importlib.util.module_from_spec(_spec)
sys.modules["ledger_owed"] = lo
_spec.loader.exec_module(lo)

_lint = importlib.util.spec_from_file_location("ledger_lint_for_owed", script("ledger_lint.py"))
assert _lint is not None and _lint.loader is not None
ll = importlib.util.module_from_spec(_lint)
_lint.loader.exec_module(ll)

HEAD = f"# ledger\n\n{ll.MEASURED_HEADING}\n\nprose\n\n| {' | '.join(ll.COLUMNS)} |\n|{'---|' * len(ll.COLUMNS)}\n"


def _clean_env() -> dict[str, str]:
    """The environment without the outer make's variables: a test run under `make arbiter-fix-done LAND=...` inherits LAND= through
    MAKEFLAGS, and a `make` the test runs would then land tooling for real (found 2026-10-18, T20's landing)."""
    import os

    params = {"LAND", "TICK", "F", "T", "ID", "NOTE", "TEST", "ENGINE", "WRITE", "ARBITER", "FILE", "AS", "BLOCKS", "TASK"}
    return {k: v for k, v in os.environ.items() if k not in ("MAKEFLAGS", "MFLAGS", "MAKELEVEL", "MAKEOVERRIDES") and k not in params}


def _pass(check: str = "glyph-check", wall: str = "80 s", tokens: str = "244k in (199k cached) / 7.8k out", subject: str = "copse on inashiro") -> dict[str, str]:
    return {"date": "2026-10-10", "check": check, "subject": subject, "agent": "a1", "wall": wall, "tokens": tokens}


def _row(check: str = "glyph-check", wall: str = "80 s", tokens: str = "244k in (199k cached) / 7.8k out") -> str:
    return f"| 2026-10-10 | {check} | copse on inashiro | PASS | caught nothing | nothing | - | nothing | {wall} | {tokens} |\n"


def test_a_pass_with_no_row_is_owed_and_one_with_its_row_is_not() -> None:
    """SC-001 / SC-002: the row answers by its check and its cost cells."""
    p = _pass()
    assert lo.unanswered([p], HEAD) == [p]
    assert lo.unanswered([p], HEAD + _row()) == []
    assert lo.unanswered([p], HEAD + _row(check="size-audit")) == [p], "another check's row with the same cells does not answer"


def test_two_same_day_rounds_are_told_apart_by_their_cells() -> None:
    """SC-003 / FR-005: one row cannot answer both rounds."""
    r1, r2 = _pass(wall="80 s"), _pass(wall="95 s", tokens="250k in (199k cached) / 8.1k out")
    assert lo.unanswered([r1, r2], HEAD + _row()) == [r2]


def test_the_cells_match_whatever_the_spacing() -> None:
    assert lo.unanswered([_pass()], HEAD + _row(tokens="244k in (199k cached)  /  7.8k out")) == []


def test_the_printed_row_carries_what_is_measured_and_leaves_the_judgment() -> None:
    """SC-004 / FR-003: date, check, subject and cost filled; the five judgment cells for the session."""
    row = lo.row_for(_pass())
    assert row == "| 2026-10-10 | glyph-check | copse on inashiro | ? | ? | ? | ? | ? | 80 s | 244k in (199k cached) / 7.8k out |"
    assert len(row.strip("|").split("|")) == len(ll.COLUMNS)


def test_the_log_is_read_line_by_line_and_a_bad_line_is_skipped(tmp_path: Path) -> None:
    log = tmp_path / "check-passes.jsonl"
    log.write_text(json.dumps(_pass()) + "\nnot json\n" + json.dumps(_pass(wall="95 s")) + "\n")
    assert [p["wall"] for p in lo.load_passes(log)] == ["80 s", "95 s"]
    assert lo.load_passes(tmp_path / "absent.jsonl") == []


@pytest.mark.parametrize(("ledger", "refuse", "rc"), [("", False, 0), ("", True, 1), ("row", True, 0)])
def test_the_command_reports_and_refuses_only_when_asked(tmp_path: Path, ledger: str, refuse: bool, rc: int) -> None:
    """FR-004: a report never fails; `--refuse` fails while a pass is unanswered, and names the row to add."""
    log, led = tmp_path / "check-passes.jsonl", tmp_path / "review-ledger.md"
    log.write_text(json.dumps(_pass()) + "\n")
    led.write_text(HEAD + (_row() if ledger else ""))
    r = subprocess.run([sys.executable, str(script("ledger_owed.py")), "--log", str(log), "--ledger", str(led), *(["--refuse"] if refuse else [])], capture_output=True, text=True, check=False)
    assert r.returncode == rc, r.stderr + r.stdout
    if not ledger:
        assert "| 2026-10-10 | glyph-check | copse on inashiro | ? |" in r.stdout + r.stderr
        assert "LEDGER_ROWS_OK" in r.stdout + r.stderr


def test_each_return_of_a_resumed_check_is_a_pass_and_a_repeat_is_one() -> None:
    """Plan review 2: a check resumed after it returned has two passes, each answered only by its own row; the same return
    seen by two events (a foreground check) is one pass."""
    first, later = _pass(wall="80 s"), _pass(wall="40 s", tokens="90k in (80k cached) / 2.0k out")
    passes = lo.distinct([first, later, dict(later)])
    assert passes == [first, later]
    assert lo.unanswered(passes, HEAD + _row()) == [later]
    assert lo.unanswered(passes, HEAD + _row() + _row(wall="40 s", tokens="90k in (80k cached) / 2.0k out")) == []


def test_the_printed_row_keeps_its_ten_cells_whatever_its_subject() -> None:
    """FR-003: a subject with a pipe or a newline is made safe, so the row keeps the table's ten cells; filled in, it lints."""
    row = lo.row_for(_pass(subject="MODE 2 | review\nfeature 371"))
    filled = row.replace("| ? | ? | ? | ? | ? |", "| PASS | caught nothing | nothing | - | nothing |")
    assert ll.problems(HEAD + filled + "\n") == [], ll.problems(HEAD + filled + "\n")


def _call(stamp: str, rid: str, out: int) -> str:
    return (
        json.dumps(
            {
                "timestamp": stamp,
                "requestId": rid,
                "message": {"role": "assistant", "content": [], "usage": {"input_tokens": 1000, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0, "output_tokens": out}},
            }
        )
        + "\n"
    )


def test_a_pass_is_settled_from_the_finished_transcript_not_the_cells_logged_at_the_stop(tmp_path: Path) -> None:
    """Measured 2026-10-10: at SubagentStop the agent's last call was not yet on disk, so a 13 s check was logged as 4 s and no
    row copied from `make review-cost` could ever answer it. The finished transcript decides; the logged cells stand only
    where it is gone."""
    sub = tmp_path / "proj" / "sess" / "subagents"
    sub.mkdir(parents=True)
    prompt = json.dumps({"timestamp": "2026-10-10T10:00:00Z", "message": {"role": "user", "content": "check it"}}) + "\n"
    (sub / "agent-a1.jsonl").write_text(prompt + _call("2026-10-10T10:00:04Z", "r1", 100) + _call("2026-10-10T10:00:13Z", "r2", 900))
    (sub / "agent-a2.jsonl").write_text(prompt + _call("2026-10-10T10:00:20Z", "r1", 100))
    early = {**_pass(wall="4 s", tokens="1k in (0k cached) / 0.1k out"), "segment": "0"}
    old = {**_pass(wall="1 s", tokens="x"), "agent": "a2"}  # logged before the segment was
    gone = {**_pass(wall="7 s", tokens="y"), "agent": "a9", "segment": "0"}
    a1, a2, a9 = lo.settled([early, old, gone], tmp_path)
    assert (a1["wall"], a1["tokens"]) == ("13 s", "2k in (0k cached) / 1.0k out")
    assert a2["wall"] == "20 s", "an agent that returned once has one return to settle by"
    assert (a9["wall"], a9["tokens"]) == ("7 s", "y"), "no transcript: the logged cells stand"
    assert a1["logged"] == "4 s | 1k in (0k cached) / 0.1k out", "the cells logged at the stop are kept beside"
    # a row written from those logged cells before the recompute still answers its pass (2026-10-11: 131 answered passes
    # read as owed again the day the recompute landed); a row with the recomputed cells answers it too
    assert lo.unanswered([a1], HEAD + _row(wall="4 s", tokens="1k in (0k cached) / 0.1k out")) == []
    assert lo.unanswered([a1], HEAD + _row(wall="13 s", tokens="2k in (0k cached) / 1.0k out")) == []
    assert lo.unanswered([a1], HEAD + _row(wall="5 s", tokens="1k in (0k cached) / 0.1k out")) == [a1]


def test_a_page_session_s_passes_get_rows_written_from_their_replies(tmp_path: Path) -> None:
    """2026-10-11: headless page sessions wrote no ledger rows, and 343's and 368's owed 124 at landing. `--write` fills each
    owed pass's row from the agent's own reply; `--session` keeps it to the session that ended."""
    for n, (sid, aid, reply) in enumerate((("s1", "a1", "COVERAGE 0 findings; TRUTH 0; LINKS 0"), ("s1", "a2", "1. the lantern is on no drawing page"), ("s2", "a3", "x"))):
        sub = tmp_path / "proj" / sid / "subagents"
        sub.mkdir(parents=True, exist_ok=True)
        prompt = json.dumps({"timestamp": "2026-10-10T10:00:00Z", "message": {"role": "user", "content": "Check the bundle at /tmp/l7r-check/modal-sheet-garden/MANIFEST.md"}}) + "\n"
        said = (
            json.dumps(
                {
                    "timestamp": "2026-10-10T10:00:09Z",
                    "requestId": "r2",
                    "message": {
                        "role": "assistant",
                        "content": [{"type": "text", "text": reply}],
                        "usage": {"input_tokens": 1000, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0, "output_tokens": 100 * (n + 1)},
                    },
                }
            )
            + "\n"
        )
        (sub / f"agent-{aid}.jsonl").write_text(prompt + said)
    log = tmp_path / "passes.jsonl"
    subject = "Check the bundle at /tmp/l7r-check/modal-sheet-garden/MANIFEST.md"
    log.write_text("".join(json.dumps({**_pass(check="modal-depiction", subject=subject), "agent": a, "segment": "0"}) + "\n" for a in ("a1", "a2", "a3")))
    ledger = tmp_path / "ledger.md"
    ledger.write_text(HEAD)
    args = ["--log", str(log), "--ledger", str(ledger), "--transcripts", str(tmp_path), "--write", "specs/343-x/briefs/'s checks file"]
    assert lo.main([*args, "--session", "s1"]) == 0
    rows = ledger.read_text().splitlines()[-2:]
    assert "| modal-sheet-garden | clean | COVERAGE 0 findings; TRUTH 0; LINKS 0 | nothing |" in rows[0]
    assert "| findings | 1. the lantern is on no drawing page | judgment | - | applied or filed as specs/343-x/briefs/'s checks file records |" in rows[1]
    assert ll.problems(ledger.read_text()) == [], "the written rows pass the ledger's lint"
    assert len(lo.unanswered(lo.distinct(lo.settled(lo.load_passes(log), tmp_path)), ledger.read_text())) == 1, "s2's pass is left for s2"


def test_the_refusal_names_the_command_that_writes_each_row(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Feature 385 amendment 5 (FR-019): rows were typed by hand, about 2 min a task; `make ledger-owed WRITE=` writes them from
    each agent's reply (the page sessions' form), and the refusal names it."""
    log = tmp_path / "passes.jsonl"
    log.write_text(json.dumps({"agent": "a1", "check": "spec-fidelity", "date": "2026-10-18", "subject": "s", "wall": "60 s", "tokens": "9k in / 1k out"}) + "\n")
    ledger = tmp_path / "ledger.md"
    ledger.write_text("")
    assert lo.main(["--log", str(log), "--ledger", str(ledger), "--transcripts", str(tmp_path)]) == 0
    assert 'make ledger-owed WRITE="<where you recorded what you did>"' in capsys.readouterr().out
    repo = Path(__file__).resolve().parents[2]
    dry = subprocess.run(["make", "-n", "-C", str(repo), "ledger-owed", "WRITE=the plan records"], capture_output=True, text=True, check=False, env=_clean_env()).stdout
    assert '--write "the plan records"' in dry


def test_a_plan_review_that_recorded_its_verdict_gets_its_row_and_others_do_not(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 385 T72 (plan D92): 81 plan reviews' rows were written by hand on 2026-10-18, each naming the plan-verdict record."""
    replies = {"a1": "plan-verdict: CLEAR recorded for 385-x T72 (3 decision(s))", "a2": "I could not record it", "a3": "BLOCKED recorded for 385-x"}
    monkeypatch.setattr(lo.review_cost, "transcript", lambda agent, root=None: tmp_path / agent)
    sys.path.insert(0, str(script("ledger_owed.py").parent.parent / "hooks" / "lib"))
    import hm_checks  # noqa: PLC0415

    monkeypatch.setattr(hm_checks, "_reply_of", lambda path, default: replies[Path(path).name])
    monkeypatch.setattr(lo, "filled_row", lambda p, where, root=None: f"| {p['agent']} | {where} |")
    owed = [dict(_pass("spec-fidelity", subject="MODE 4: PLAN REVIEW of T72"), agent=a) for a in ("a1", "a2", "a3")]
    owed.append(_pass("glyph-check"))  # another check's pass: still the session's to answer
    assert lo.plan_review_rows(owed, tmp_path) == ["| a1 | the plan-verdict record (make plan-verdict) |", "| a3 | the plan-verdict record (make plan-verdict) |"]
