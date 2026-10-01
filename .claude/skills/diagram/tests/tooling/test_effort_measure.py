"""`scripts/_effort_measure.py` (feature 293, FR-006/FR-007): a run's cost and rework, read from its transcripts and logs.

WHAT THESE PROVE. Usage is folded per message id as the per-field maximum and agrees with `_agent_census.py`'s fold; main
and subagent tokens are kept apart; an ad-hoc dispatch is listed with its model and description and counted as judging on
opus or on a judging word (R1 D3); every rework signal of research R4 is counted from its own source; a still-running run
is refused, a killed one is void, and a task R run's claim is released (R6 D5).
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess

import pytest

REPO = pathlib.Path(__file__).resolve().parents[5]


def _load(name: str):  # noqa: ANN202
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


em = _load("_effort_measure")
census = _load("_agent_census")
FEATURE = "specs/293-effort-level-experiment"


def _asst(mid: str, ts: str, blocks: list[dict], out: int, inp: int = 10, cr: int = 100, cw: int = 5, effort: str = "xhigh") -> dict:
    return {
        "type": "assistant",
        "timestamp": ts,
        "effort": effort,
        "message": {"id": mid, "model": "claude-opus-5-5", "content": blocks, "usage": {"input_tokens": inp, "output_tokens": out, "cache_read_input_tokens": cr, "cache_creation_input_tokens": cw}},
    }


def _result(tid: str, text: str, ts: str) -> dict:
    return {"type": "user", "timestamp": ts, "message": {"content": [{"type": "tool_result", "tool_use_id": tid, "content": text}]}}


def _write(path: pathlib.Path, recs: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r) for r in recs) + "\nnot json\n", encoding="utf-8")


MAIN = [
    _asst("m1", "2026-10-01T10:00:00Z", [{"type": "text", "text": "starting"}], out=3),
    _asst("m1", "2026-10-01T10:00:01Z", [{"type": "tool_use", "id": "t1", "name": "Bash", "input": {"command": "make quick"}}], out=40),
    _result("t1", "1 failed, 20 passed\nmake: *** Error 1", "2026-10-01T10:01:00Z"),
    _asst("m2", "2026-10-01T10:02:00Z", [{"type": "tool_use", "id": "t2", "name": "Bash", "input": {"command": "make quick"}}], out=7),
    _result("t2", "21 passed", "2026-10-01T10:03:00Z"),
    _asst(
        "m3",
        "2026-10-01T10:04:00Z",
        [
            {"type": "tool_use", "id": "t3", "name": "Agent", "input": {"subagent_type": "general-purpose", "model": "opus", "description": "weigh the two routes"}},
            {"type": "tool_use", "id": "t4", "name": "Agent", "input": {"subagent_type": "Explore", "model": "sonnet", "description": "review the lane tests"}},
            {"type": "tool_use", "id": "t5", "name": "Agent", "input": {"subagent_type": "Explore", "model": "sonnet", "description": "find burial.py"}},
            {"type": "tool_use", "id": "t6", "name": "Agent", "input": {"subagent_type": "adhoc-judge", "description": "judge"}},
            {"type": "tool_use", "id": "t7", "name": "Agent", "input": {"subagent_type": "quote-check", "description": "q"}},
        ],
        out=9,
    ),
    _asst("m4", "2026-10-01T11:00:00Z", [{"type": "text", "text": "Which width should the path be?"}], out=2),
]
SUB = [
    _asst("s1", "2026-10-01T10:30:00Z", [{"type": "tool_use", "id": "u1", "name": "WebFetch", "input": {}}], out=5),
    _asst("s2", "2026-10-01T10:31:00Z", [{"type": "text", "text": "CHANGES REQUIRED - 2 notes not verbatim"}], out=6, effort="high"),
]


def test_the_fold_takes_each_message_s_maximum_and_agrees_with_the_census() -> None:
    folded = em.fold(MAIN)
    assert folded["output_tokens"] == 40 + 7 + 9 + 2, "m1's two records count once, at their maximum"
    ours = em.fold(MAIN)
    theirs = census.fold_usage(MAIN)
    assert theirs["fresh"] == ours["input_tokens"] + ours["cache_creation_input_tokens"]
    assert theirs["cached"] == ours["cache_read_input_tokens"] and theirs["output"] == ours["output_tokens"]


def test_verdicts_and_failed_runs_are_read_from_their_words() -> None:
    assert em.verdict_of("**Verdict: FAITHFUL.** all resolved") == "pass"
    assert em.verdict_of("BLOCKED on two items") == "not-pass"
    assert em.verdict_of("nothing to say") == "unclear"
    assert em.failed_make_runs(MAIN) == ["make quick"], "the failure before the green run of the same target"
    assert em.last_text([]) == ""


def _world(tmp: pathlib.Path, task: str = "I") -> dict:
    clone = tmp / "clones" / "diagram-exp-e1"
    projects = tmp / "projects"
    project = projects / str(clone).replace("/", "-").replace(".", "-")
    _write(project / "sid-1.jsonl", MAIN)
    _write(project / "sid-1" / "subagents" / "agent-a1.jsonl", SUB)
    (project / "sid-1" / "subagents" / "agent-a1.meta.json").write_text(json.dumps({"agentType": "quote-check"}))
    _write(project / "sid-1" / "subagents" / "agent-a2.jsonl", [_asst("s3", "2026-10-01T10:40:00Z", [{"type": "text", "text": "KEEP 2, CUT 1"}], out=1)])
    (project / "sid-1" / "subagents" / "agent-a2.meta.json").write_text(json.dumps({"agentType": "escalation-check"}))
    guard = tmp / "guard-log"
    guard.mkdir()
    for i, e in enumerate(
        [
            {"session": "sid-1", "cwd": "/x", "guard": "batching", "event": "blocked", "rule": "recon"},
            {"session": "other", "cwd": str(clone) + "/sub", "guard": "house-style", "event": "rewrote", "rule": "dash"},
            {"session": "other", "cwd": "/elsewhere", "guard": "batching", "event": "blocked", "rule": "recon"},
        ]
    ):
        (guard / f"{i}.json").write_text(json.dumps(e))
    (guard / "bad.json").write_text("{")
    run = {"run_id": "e1", "task": task, "clone": str(clone), "pauses": [["2026-10-01T10:10:00Z", "2026-10-01T10:20:00Z"]]}
    return {"run": run, "projects": projects, "guard": guard, "clone": clone}


def test_a_run_is_measured_from_every_source(tmp_path: pathlib.Path) -> None:
    w = _world(tmp_path)
    m = em.measure(w["run"], w["projects"], w["guard"], {"quote-check", "escalation-check", "adhoc-judge"}, ["293 I: the path", "fix the spur width", "round-2 changes", "Revert the web edit"])
    assert m["tokens"]["main"]["output_tokens"] == 58 and m["tokens"]["subagents"]["output_tokens"] == 12
    assert m["tokens"]["total"]["cache_read_input_tokens"] == 100 * 4 + 100 * 3
    assert m["wall_clock_s"] == 3600 - 600, "first to last event, less the logged pause"
    assert m["tool_calls"]["main"] == {"Bash": 2, "Agent": 5} and m["tool_calls"]["subagents"] == {"WebFetch": 1}
    assert m["effort"]["main"] == {"xhigh": 4}, "counted per message, m1's two records once"
    assert m["effort"]["subagents"] == {"quote-check": {"xhigh": 1, "high": 1}, "escalation-check": {"xhigh": 1}}
    assert em.efforts([{"type": "assistant", "uuid": "u"}]) == {"unrecorded": 1}
    assert m["dispatches"]["general-purpose@opus"] == 1 and m["dispatches"]["adhoc-judge@inherit"] == 1
    assert [a["type"] for a in m["adhoc_dispatches"]] == ["general-purpose", "Explore", "Explore"]
    assert m["adhoc_judging_at_session_effort"] == 2, "opus, or a judging word on sonnet ('review the lane tests')"
    rw = m["rework"]
    assert rw["guard"] == {"batching:blocked:recon": 1, "house-style:rewrote:dash": 1}
    assert rw["verdicts"] == {"quote-check": {"not-pass": 1}, "escalation-check": {"pass": 1}}
    assert rw["failed_make_runs"] == ["make quick"] and len(rw["fix_commits"]) == 3
    assert rw["escalations"] == 2, "one escalation-check, one final turn ending in a question"


def test_an_empty_project_measures_zero(tmp_path: pathlib.Path) -> None:
    run = {"run_id": "e9", "task": "I", "clone": str(tmp_path / "none"), "pauses": []}
    m = em.measure(run, tmp_path, tmp_path / "no-log", set(), [])
    assert m["wall_clock_s"] == 0 and m["tokens"]["total"]["output_tokens"] == 0 and m["rework"]["guard"] == {}


def _git(*args: str, cwd: pathlib.Path) -> str:
    return subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


def _repo(tmp: pathlib.Path, w: dict, task: str, logs: list[pathlib.Path]) -> pathlib.Path:
    """A session repository holding the run record and experiment.json, and the run clone with a commit since start."""
    clone = w["clone"]
    clone.mkdir(parents=True, exist_ok=True)
    _git("init", "-q", "-b", "main", cwd=clone)
    (clone / ".claude" / "agents").mkdir(parents=True)
    (clone / ".claude" / "agents" / "quote-check.md").write_text("x")
    _git("add", "-A", cwd=clone)
    _git("commit", "-qm", "start", cwd=clone)
    start = _git("rev-parse", "HEAD", cwd=clone)
    (clone / "research" / "sources").mkdir(parents=True)
    (clone / "research" / "sources" / "0042-k.html").write_text("k")
    _git("add", "-A", cwd=clone)
    _git("commit", "-qm", "fix the source", cwd=clone)
    repo = tmp / "session"
    fdir = repo / FEATURE
    (fdir / "runs").mkdir(parents=True)
    snap = tmp / "snap"
    snap.mkdir()
    (snap / "sources-consulted.jsonl").write_text("a\n")
    copy = tmp / "copy"
    copy.mkdir()
    (copy / "sources-consulted.jsonl").write_text("a\nb\nc\n")
    (fdir / "experiment.json").write_text(json.dumps({"sources_snapshot": str(snap)}))
    run = w["run"] | {"task": task, "start_commit": start, "shared_state": {}, "env": {"L7R_SOURCES_HOME": str(copy)}, "sessions": [{"log": str(p)} for p in logs], "ended": None}
    (fdir / "runs" / "e1.json").write_text(json.dumps(run))
    _git("init", "-q", "-b", "main", cwd=repo)
    return repo


def _main(w: dict, repo: pathlib.Path, claims: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> int:
    monkeypatch.chdir(repo)
    return em.main(["--run", "e1", "--projects", str(w["projects"]), "--guard-log", str(w["guard"]), "--claims", str(claims)])


def test_the_command_refuses_a_running_run_then_measures_it(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    w = _world(tmp_path)
    log = tmp_path / "log"
    log.mkdir()
    repo = _repo(tmp_path, w, "I", [log])
    claims = tmp_path / "claims.md"
    assert _main(w, repo, claims, monkeypatch) == 2 and "still running" in capsys.readouterr().err
    (log / "result.json").write_text('{"type": "result"}')
    assert _main(w, repo, claims, monkeypatch) == 0
    run = json.loads((repo / FEATURE / "runs" / "e1.json").read_text())
    assert run["status"] == "valid" and run["ended"] and not claims.exists(), "task I releases no claim"
    assert run["shared_state"]["ledger_lines_appended"] == 2
    assert run["shared_state"]["prefixes_reserved"] == ["research/sources/0042-k.html"]
    m = json.loads((repo / FEATURE / "measurements" / "e1.json").read_text())
    assert m["rework"]["fix_commits"] == ["fix the source"] and "tokens in" in capsys.readouterr().out


def test_a_killed_task_r_run_is_void_and_its_claim_released(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    w = _world(tmp_path, task="R")
    pages = w["clone"] / ".git" / "page-sessions"
    repo = _repo(tmp_path, w, "R", [])
    (pages / "sid-1").mkdir(parents=True)
    (pages / "sid-1" / "stderr.txt").write_text("Killed\n")
    claims = tmp_path / "claims.md"
    assert _main(w, repo, claims, monkeypatch) == 0
    run = json.loads((repo / FEATURE / "runs" / "e1.json").read_text())
    assert run["status"] == "void" and "137" in run["void_reason"]
    assert "run e1 ended - claim released" in claims.read_text() == run["shared_state"]["claims_release_line"] + "\n"
    assert em.void_reason(tmp_path / "nothing") == ""


def test_the_session_can_void_a_run_for_an_environment_reason(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    w = _world(tmp_path)
    log = tmp_path / "log"
    log.mkdir()
    (log / "result.json").write_text('{"type": "result"}')
    repo = _repo(tmp_path, w, "I", [log])
    monkeypatch.chdir(repo)
    assert em.main(["--run", "e1", "--projects", str(w["projects"]), "--guard-log", str(w["guard"]), "--claims", str(tmp_path / "c.md"), "--void", "the launcher leaked the arm"]) == 0
    run = json.loads((repo / FEATURE / "runs" / "e1.json").read_text())
    assert run["status"] == "void" and "leaked the arm" in run["void_reason"]


def test_a_resumed_session_is_finished_by_its_newest_result(tmp_path: pathlib.Path) -> None:
    import os
    import time as _t

    log = tmp_path / "log"
    log.mkdir()
    (log / "result.json").write_text("")
    assert not em.finished(log)
    (log / "result-0.json").write_text('{"type": "result"}')
    later = _t.time() + 5
    os.utime(log / "result-0.json", (later, later))
    assert em.finished(log) and em.latest(log, "result", ".json").name == "result-0.json"
    (log / "stderr-0.txt").write_text("Killed\n")
    os.utime(log / "stderr-0.txt", (later, later))
    assert "137" in em.void_reason(log)


def test_a_run_that_never_started_can_be_voided(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    w = _world(tmp_path)
    log = tmp_path / "log"
    log.mkdir()
    (log / "result.json").write_text("")
    (log / "stderr.txt").write_text("Error: No messages returned from query\n")
    repo = _repo(tmp_path, w, "I", [log])
    monkeypatch.chdir(repo)
    assert em.main(["--run", "e1", "--projects", str(w["projects"]), "--guard-log", str(w["guard"]), "--claims", str(tmp_path / "c.md"), "--void", "it failed at launch"]) == 0
    assert json.loads((repo / FEATURE / "runs" / "e1.json").read_text())["status"] == "void"
