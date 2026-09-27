"""`scripts/_page_session_runner.py` (feature 250 D7, D11): each brief in a fresh headless session, in order.

WHAT THESE PROVE. Every brief gets its own session id, log directory and command, in the order given; the command
names the session like the clone (so the clone-sync hooks route it), carries the chosen id (so its transcript is
known before it starts), runs headless in bypass mode and passes the caller's extra arguments through. Nothing here
starts a session: `plan` is the part with logic, and the detached loop is four lines the first page runs exercised.
"""

from __future__ import annotations

import importlib.util
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[5]


def _load():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("_page_session_runner", REPO / "scripts" / "_page_session_runner.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ps = _load()


def test_each_brief_is_its_own_session_in_order(tmp_path: pathlib.Path, capsys) -> None:
    briefs = [tmp_path / "veg-1.md", tmp_path / "veg-2.md"]
    for b in briefs:
        b.write_text("brief", encoding="utf-8")
    queue = ps.plan(str(tmp_path), "diagram-research", "/p", ["--model", "opus"], [str(b) for b in briefs])
    runs = [[q["sid"], q["log"], *q["cmd"]] for q in queue]
    assert len(runs) == 2 and runs[0][0] != runs[1][0], "two sessions, two ids"
    for (sid, log, *cmd), brief in zip(runs, briefs, strict=True):
        assert pathlib.Path(log).is_dir() and log.endswith(sid)
        assert cmd[:2] == ["claude", "-p"] and str(brief) in cmd[2], "the prompt names its own brief"
        assert cmd[cmd.index("-n") + 1] == "diagram-research" and cmd[cmd.index("--session-id") + 1] == sid
        assert "bypassPermissions" in cmd and cmd[-2:] == ["--output-format", "json"] and "--model" in cmd
    out = capsys.readouterr().out
    assert out.index("veg-1.md") < out.index("veg-2.md") and f"/p/{runs[0][0]}.jsonl" in out


def test_a_page_session_starts_from_the_lower_floor() -> None:
    """R3, recommendation 1: only research's tools, no MCP servers, no skill listing - and in a clone, not the
    mirror's root CLAUDE.md, which sits above every clone (a probe: first turn 40,280 -> 21,267 tokens)."""
    flags = ps.floor_flags("/diagram/.clones/diagram-research")
    assert "--disable-slash-commands" in flags and "--strict-mcp-config" in flags
    assert flags[flags.index("--tools") + 1] == "Bash,Read,Edit,Write,Grep,Glob,Agent,WebFetch,WebSearch"
    assert '"claudeMdExcludes": ["/diagram/CLAUDE.md"]' in flags[flags.index("--settings") + 1]
    assert "--settings" not in ps.floor_flags("/diagram"), "the mirror keeps its own CLAUDE.md"


def test_a_then_step_queues_the_briefs_it_prints(tmp_path: pathlib.Path, monkeypatch) -> None:
    """The check sessions are planned when the write session has ended, from its handoff (R3, recommendation 2)."""
    (tmp_path / ".git" / "page-sessions").mkdir(parents=True)
    step = tmp_path / "checks.sh"
    step.write_text("#!/bin/sh\necho /b/veg-2a.md\necho /b/veg-2b.md\n", encoding="utf-8")
    step.chmod(0o755)
    ran: list[str] = []
    monkeypatch.setattr(
        ps.subprocess,
        "run",
        lambda cmd, **kw: (
            ran.append(cmd[0] if cmd[0] != "claude" else cmd[2].split("Read ")[1].split(" first")[0]),
            ps.subprocess.CompletedProcess(cmd, 0, stdout="/b/veg-2a.md\n/b/veg-2b.md\n" if cmd[0] == str(step) else ""),
        )[1],
    )
    run_log = tmp_path / "run.log"
    ps.work(str(tmp_path), "n", [], [{"then": str(step)}], str(run_log))
    assert ran == [str(step), "/b/veg-2a.md", "/b/veg-2b.md"], ran
    lines = run_log.read_text(encoding="utf-8").splitlines()
    assert lines[0].startswith("planned 2") and lines[-1] == "ALL DONE", lines
    assert [ln.split()[0] for ln in lines[1:-1]] == ["started", "ended", "started", "ended"], "a line as each session starts and ends"
    index = (tmp_path / ".git" / "page-sessions" / "index.txt").read_text(encoding="utf-8").splitlines()
    assert [ln.split()[1] for ln in index] == ["/b/veg-2a.md", "/b/veg-2b.md"]


def test_each_session_is_told_its_dispatcher_the_one_claimant_the_clone_guard_lets_through(tmp_path: pathlib.Path, monkeypatch) -> None:
    """D14: a queued session was refused by the clone guard while its live dispatcher's tree was clean."""
    import os
    import time

    root = tmp_path / ".clones" / "diagram-research"
    (root / ".git" / "page-sessions").mkdir(parents=True)
    claims = tmp_path / ".clones" / ".session-clones"
    claims.mkdir()
    (claims / "sid-old").write_text(str(root), encoding="utf-8")
    os.utime(claims / "sid-old", (time.time() - 60, time.time() - 60))
    (claims / "sid-dispatcher").write_text(str(root), encoding="utf-8")
    (claims / "sid-elsewhere").write_text(str(tmp_path / ".clones" / "other"), encoding="utf-8")
    assert ps.dispatcher(str(root)) == "sid-dispatcher"
    assert ps.dispatcher(str(tmp_path / "not-a-clone")) == ""
    assert ps.dispatcher(str(tmp_path / ".clones" / "unclaimed")) == ""
    seen: list[str] = []
    monkeypatch.setattr(ps.subprocess, "run", lambda cmd, **kw: (seen.append(kw["env"]["L7R_DISPATCHER"]), ps.subprocess.CompletedProcess(cmd, 0))[1])
    log = root / ".git" / "page-sessions" / "s1"
    log.mkdir()
    ps.work(str(root), "n", [], [{"sid": "s1", "log": str(log), "brief": "/b/x.md", "cmd": ["claude"]}], str(tmp_path / "run.log"))
    assert seen == ["sid-dispatcher"]


def test_a_queued_session_does_not_inherit_the_dispatcher_s_tmux_pane() -> None:
    """2026-09-27: a headless session carrying TMUX registered itself in the GM's pane and retitled the GM's tab."""
    env = ps.headless_env({"TMUX": "/tmp/tmux-1000/default,10,0", "TMUX_PANE": "%0", "HOME": "/h"}, "sid-d")
    assert env == {"HOME": "/h", "L7R_DISPATCHER": "sid-d"}


def test_a_session_the_usage_limit_ends_is_resumed_after_the_wait_not_skipped(tmp_path: pathlib.Path, monkeypatch) -> None:
    """The GM, 2026-09-27: overnight, a spent five-hour window must not burn the rest of the queue - the failed session
    waits for the reset and RESUMES, and the next brief starts only after it succeeds."""
    queue = ps.plan(str(tmp_path), "n", "/p", [], [str(tmp_path / "a.md"), str(tmp_path / "b.md")])
    (tmp_path / "a.md").write_text("x", encoding="utf-8")
    calls: list[list[str]] = []
    outcomes = iter([(1, '{"is_error": true, "result": "Claude AI usage limit reached|1900000000"}'), (0, '{"subtype": "success", "is_error": false}'), (0, '{"subtype": "success"}')])

    def fake_run(cmd, **kw):  # noqa: ANN001, ANN003, ANN202
        calls.append(cmd)
        rc, out = next(outcomes)
        kw["stdout"].write(out)
        return ps.subprocess.CompletedProcess(cmd, rc)

    slept: list[float] = []
    monkeypatch.setattr(ps.subprocess, "run", fake_run)
    monkeypatch.setattr(ps.time, "sleep", slept.append)
    monkeypatch.setattr(ps.time, "time", lambda: 1_900_000_000 - 3600)
    run_log = tmp_path / "run.log"
    first = queue[0]["sid"]  # `work` consumes the queue
    ps.work(str(tmp_path), "n", [], queue, str(run_log))
    assert len(calls) == 3, "a, a resumed, then b"
    assert calls[1][calls[1].index("--resume") + 1] == first and "--session-id" not in calls[1]
    assert calls[1][calls[1].index("-p") + 1] == ps.RESUME and "--session-id" in calls[2], "the next brief is a fresh session"
    assert slept == [3600 + 120], "until two minutes past the reset the message names"
    kinds = [ln.split()[0] for ln in run_log.read_text(encoding="utf-8").splitlines()]
    assert kinds == ["started", "failed", "ended", "started", "ended", "ALL"], kinds


def test_the_wait_reads_the_reset_or_backs_off() -> None:
    now = 1_900_000_000.0  # 2030-03-17 17:46:40 UTC
    assert ps.wait_for("limit reached|1900000600", 0, now) == 600 + 120
    assert ps.wait_for("5-hour limit reached - resets 7pm", 0, now) == (19 * 3600) - (17 * 3600 + 46 * 60 + 40) + 120
    assert ps.wait_for("resets 3am", 0, now) <= 6 * 3600, "never over six hours"
    assert [ps.wait_for("overloaded", n, now) for n in (0, 1, 2, 9)] == [900, 1800, 3600, 3600]
    assert ps.failed(0, '{"is_error": false, "subtype": "success"}') is False
    assert ps.failed(0, '{"subtype": "error_during_execution"}') and ps.failed(1, "") and not ps.failed(0, "not json")
    assert ps.first_line("\n  hello\nworld") == "hello" and ps.first_line("") == "no output"


def test_a_resume_item_continues_the_same_session_in_its_own_log(tmp_path: pathlib.Path) -> None:
    """Feature 271: a runner that died with its dispatcher left a session mid-brief; `resume:<sid>:<brief>` resumes
    that very session (`--resume`, a continue prompt) in its existing log directory, and briefs after it still queue."""
    brief = tmp_path / "v1-write.md"
    brief.write_text("brief", encoding="utf-8")
    sid = "f6b577d1-4b97-4962-a643-e735d51727da"
    (tmp_path / ".git" / "page-sessions" / sid).mkdir(parents=True)
    queue = ps.plan(str(tmp_path), "diagram-research-1", "/p", [], [f"resume:{sid}:{brief}", str(brief)])
    first, second = queue
    assert first["sid"] == sid and first["log"].endswith(sid)
    assert "--resume" in first["cmd"] and first["cmd"][first["cmd"].index("--resume") + 1] == sid and "--session-id" not in first["cmd"]
    assert first["cmd"][first["cmd"].index("-p") + 1] == ps.RESUME
    assert second["sid"] != sid and "--session-id" in second["cmd"]
