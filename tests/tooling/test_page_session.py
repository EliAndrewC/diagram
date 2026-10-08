"""`scripts/_page_session_runner.py` (feature 250 D7, D11): each brief in a fresh headless session, in order.

WHAT THESE PROVE. Every brief gets its own session id, log directory and command, in the order given; the command
names the session like the clone (so the clone-sync hooks route it), carries the chosen id (so its transcript is
known before it starts), runs headless in bypass mode and passes the caller's extra arguments through. Nothing here
starts a session: `plan` is the part with logic, and the detached loop is four lines the first page runs exercised.
"""

from __future__ import annotations

import importlib.util
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]


def _load():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("_page_session_runner", REPO / "scripts" / "_page_session_runner.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ps = _load()
BRIEF = "# Brief\n\n## Your items\n- B1 one question\n"


def test_each_brief_is_its_own_session_in_order(tmp_path: pathlib.Path, capsys) -> None:
    briefs = [tmp_path / "veg-1.md", tmp_path / "veg-2.md"]
    for b in briefs:
        b.write_text(BRIEF, encoding="utf-8")
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


def test_a_page_session_starts_from_the_lower_floor(tmp_path: pathlib.Path) -> None:
    """R3, recommendation 1: only research's tools, no MCP servers, no skill listing - and in a clone, not the
    mirror's root CLAUDE.md, which sits above every clone (a probe: first turn 40,280 -> 21,267 tokens). Feature 274
    (SC-003): nor the clone's own root CLAUDE.md, and the slim rules file is appended after the standing authorization."""
    flags = ps.floor_flags("/diagram/.clones/diagram-research")
    assert "--disable-slash-commands" in flags and "--strict-mcp-config" in flags
    assert flags[flags.index("--tools") + 1] == "Bash,Read,Edit,Write,Grep,Glob,Agent,WebFetch,WebSearch"
    assert '"claudeMdExcludes": ["/diagram/CLAUDE.md", "/diagram/.clones/diagram-research/CLAUDE.md"]' in flags[flags.index("--settings") + 1]
    assert '"claudeMdExcludes": ["/diagram/CLAUDE.md"]' in ps.floor_flags("/diagram")[ps.floor_flags("/diagram").index("--settings") + 1]
    assert "--append-system-prompt" not in ps.floor_flags(str(tmp_path)), "nothing to append, no flag"
    (tmp_path / "container-scripts").mkdir()
    for f, text in zip(ps.PROMPT_FILES, ("STANDING AUTHORIZATION", "SLIM RULES"), strict=True):
        (tmp_path / f).write_text(text + "\n", encoding="utf-8")
    flags = ps.floor_flags(str(tmp_path))
    assert flags.count("--append-system-prompt") == 1 and flags[flags.index("--append-system-prompt") + 1] == "STANDING AUTHORIZATION\n\nSLIM RULES"
    real = ps.floor_flags(str(REPO))
    appended = real[real.index("--append-system-prompt") + 1]
    assert "Standing authorizations" in appended and appended.index("Standing authorizations") < appended.index("Rules for a headless research page session")


def test_the_real_rules_file_is_the_one_appended() -> None:
    assert (REPO / ps.PROMPT_FILES[1]).is_file() and (REPO / ps.PROMPT_FILES[0]).is_file()


def test_a_then_step_queues_the_briefs_it_prints(tmp_path: pathlib.Path, monkeypatch) -> None:
    """The check sessions are planned when the write session has ended, from its handoff (R3, recommendation 2)."""
    (tmp_path / ".git" / "page-sessions").mkdir(parents=True)
    a, b = str(tmp_path / "veg-2a.md"), str(tmp_path / "veg-2b.md")
    for f in (a, b):
        pathlib.Path(f).write_text("<!-- page-load: kind=check -->\n**Your questions:** Q=0071\n", encoding="utf-8")
    step = tmp_path / "checks.sh"
    step.write_text("#!/bin/sh\n", encoding="utf-8")
    step.chmod(0o755)
    ran: list[str] = []
    monkeypatch.setattr(
        ps.subprocess,
        "run",
        lambda cmd, **kw: (
            ran.append(cmd[0] if cmd[0] != "claude" else cmd[2].split("Read ")[1].split(" first")[0]),
            ps.subprocess.CompletedProcess(cmd, 0, stdout=f"{a}\n{b}\n" if cmd[0] == str(step) else ""),
        )[1],
    )
    run_log = tmp_path / "run.log"
    ps.work(str(tmp_path), "n", [], [{"then": str(step)}], str(run_log))
    assert ran == [str(step), a, b], ran
    lines = run_log.read_text(encoding="utf-8").splitlines()
    assert lines[0].startswith("planned 2") and lines[-1] == "ALL DONE", lines
    assert [ln.split()[0] for ln in lines[1:-1]] == ["started", "ended", "started", "ended"], "a line as each session starts and ends"
    index = (tmp_path / ".git" / "page-sessions" / "index.txt").read_text(encoding="utf-8").splitlines()
    assert [ln.split()[1] for ln in index] == [a, b]


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
    # 319 (2026-10-04): a finished page session's claim is newer than the dispatcher's; the caller's own id wins
    os.utime(claims / "sid-dispatcher", (time.time() - 3600, time.time() - 3600))
    (claims / "sid-finished-page-session").write_text(str(root), encoding="utf-8")
    assert ps.dispatcher(str(root)) == "sid-finished-page-session", "without the caller's id, the newest claim"
    assert ps.dispatcher(str(root), "sid-dispatcher") == "sid-dispatcher"
    assert ps.dispatcher(str(root), "sid-elsewhere") == "sid-finished-page-session", "a caller claiming another clone is not it"
    (claims / "sid-finished-page-session").unlink()
    os.utime(claims / "sid-dispatcher", None)
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
    for f in ("a.md", "b.md"):
        (tmp_path / f).write_text(BRIEF, encoding="utf-8")
    queue = ps.plan(str(tmp_path), "n", "/p", [], [str(tmp_path / "a.md"), str(tmp_path / "b.md")])
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
    assert slept == [ps.RETRY_EVERY], "the reset is an hour off, but the retry comes after 15 minutes at most"
    kinds = [ln.split()[0] for ln in run_log.read_text(encoding="utf-8").splitlines()]
    assert kinds == ["started", "failed", "ended", "started", "ended", "ALL"], kinds


def test_every_retry_sleep_is_capped_at_15_minutes_and_the_reach_stays_about_11_hours(tmp_path: pathlib.Path, monkeypatch) -> None:
    """Feature 280 (2026-09-28): a limit the GM resets early must not leave the queue idle for the rest of a six-hour
    wait. Every sleep is at most RETRY_EVERY, and RETRIES x RETRY_EVERY keeps the ~11 hour reach."""
    (tmp_path / "a.md").write_text(BRIEF, encoding="utf-8")
    queue = ps.plan(str(tmp_path), "n", "/p", [], [str(tmp_path / "a.md")])
    outcomes = iter([(1, '{"is_error": true, "result": "limit reached - resets 3am"}')] * 3 + [(0, '{"subtype": "success"}')])

    def fake_run(cmd, **kw):  # noqa: ANN001, ANN003, ANN202
        rc, out = next(outcomes)
        kw["stdout"].write(out)
        return ps.subprocess.CompletedProcess(cmd, rc)

    slept: list[float] = []
    monkeypatch.setattr(ps.subprocess, "run", fake_run)
    monkeypatch.setattr(ps.time, "sleep", slept.append)
    monkeypatch.setattr(ps.time, "time", lambda: 1_900_000_000.0)  # 17:46 UTC, so 3am is over five hours off
    run_log = tmp_path / "run.log"
    ps.work(str(tmp_path), "n", [], queue, str(run_log))
    assert slept == [ps.RETRY_EVERY] * 3 and ps.RETRY_EVERY == 900, slept
    assert "waiting 15 min (reset in" in run_log.read_text(encoding="utf-8")
    assert 10.5 * 3600 <= ps.RETRIES * ps.RETRY_EVERY <= 11.5 * 3600, "the reach stays about 11 hours"


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
    brief.write_text(BRIEF, encoding="utf-8")
    sid = "f6b577d1-4b97-4962-a643-e735d51727da"
    (tmp_path / ".git" / "page-sessions" / sid).mkdir(parents=True)
    queue = ps.plan(str(tmp_path), "diagram-research-1", "/p", [], [f"resume:{sid}:{brief}", str(brief)])
    first, second = queue
    assert first["sid"] == sid and first["log"].endswith(sid)
    assert "--resume" in first["cmd"] and first["cmd"][first["cmd"].index("--resume") + 1] == sid and "--session-id" not in first["cmd"]
    assert first["cmd"][first["cmd"].index("-p") + 1] == ps.RESUME
    assert second["sid"] != sid and "--session-id" in second["cmd"]


# Feature 274: the write cap (D2), the continuation (D3) and the key cap's variable (D4), SC-001.

OVER = "# Brief\n\n**Do not edit:** 0005, 0006, 0007, 0008, 0009, 0010, 0011, 0012, 0013, 0014, 0015, 0017, 0231\n\n## Your items\n" + "".join(f"- B{n} question {n}\n" for n in range(10, 15))


def test_an_over_cap_brief_is_refused_at_launch_before_anything_starts(tmp_path: pathlib.Path, capsys, monkeypatch) -> None:
    monkeypatch.delenv("WRITE_CAP_OK", raising=False)
    ok, big, empty = tmp_path / "g1-write.md", tmp_path / "g2-write.md", tmp_path / "g3.md"
    ok.write_text(BRIEF, encoding="utf-8")
    big.write_text(OVER, encoding="utf-8")
    empty.write_text("# a brief that assigns nothing\n", encoding="utf-8")
    started: list[object] = []
    monkeypatch.setattr(ps.subprocess, "Popen", lambda *a, **k: started.append(a))
    assert ps.main([str(tmp_path), "n", "/p", "--", str(ok), str(big)]) == 2
    err = capsys.readouterr().err
    assert "REFUSED, nothing started" in err and "assigns 5 questions" in err and "g2a-write.md, g2b-write.md" in err and "WRITE_CAP_OK" in err
    assert not started and not (tmp_path / ".git" / "page-sessions").exists(), "nothing detached, no session made"
    assert ps.main([str(tmp_path), "n", "/p", "--", str(empty)]) == 2 and "assigns nothing" in capsys.readouterr().err
    assert ps.main([str(tmp_path), "n", "/p", "--", str(tmp_path / "gone.md")]) == 2 and "no such brief" in capsys.readouterr().err


def test_write_cap_ok_with_a_reason_lets_a_brief_through_and_is_logged(tmp_path: pathlib.Path, monkeypatch, capsys) -> None:
    import json

    big = tmp_path / "g2-write.md"
    big.write_text(OVER, encoding="utf-8")
    monkeypatch.setenv("GUARD_LOG_DIR", str(tmp_path / "log"))
    monkeypatch.setenv("WRITE_CAP_OK", "ok")
    with pytest.raises(ps.Refused, match="needs a REASON"):
        ps.plan(str(tmp_path), "n", "/p", [], [str(big)])
    monkeypatch.setenv("WRITE_CAP_OK", "one question split into five small parts")
    (item,) = ps.plan(str(tmp_path), "n", "/p", [], [str(big)])
    assert item["write"] is True
    entries = [json.loads(f.read_text(encoding="utf-8")) for f in sorted((tmp_path / "log").glob("*.json"))]
    assert [(e["guard"], e["event"], e["rule"]) for e in entries] == [("page-session", "blocked", "WRITE_CAP_OK-no-reason"), ("page-session", "escaped", "write-cap")]
    assert entries[1]["detail"] == "one question split into five small parts" and entries[1]["context"]["brief"] == str(big)


def test_every_exempt_kind_runs_and_only_a_write_session_is_told_the_key_cap(tmp_path: pathlib.Path, monkeypatch) -> None:
    briefs = []
    for kind in ps._brief_load.KINDS:
        b = tmp_path / f"{kind}.md"
        b.write_text(f"<!-- page-load: kind={kind} -->\n{OVER}", encoding="utf-8")
        briefs.append(str(b))
    (tmp_path / "w.md").write_text(BRIEF, encoding="utf-8")
    queue = ps.plan(str(tmp_path), "n", "/p", [], [*briefs, str(tmp_path / "w.md")])
    assert [q["write"] for q in queue] == [False, False, False, False, True]
    envs: list[dict] = []
    monkeypatch.setattr(ps.subprocess, "run", lambda cmd, **kw: (envs.append(kw["env"]), ps.subprocess.CompletedProcess(cmd, 0))[1])
    monkeypatch.setenv("L7R_KEY_CAP", "99")
    sids = [q["sid"] for q in queue]
    ps.work(str(tmp_path), "n", [], queue, str(tmp_path / "run.log"))
    assert [e.get("L7R_KEY_CAP") for e in envs] == [None, None, None, None, str(ps.KEY_CAP)], "a check session is not capped"
    assert [e["L7R_PAGE_SESSION"] for e in envs] == sids
    assert all(e["L7R_CONTINUE"] == str(tmp_path / ".git" / "page-sessions" / s / "continue.md") for e, s in zip(envs, sids, strict=True))


def test_a_then_step_printing_an_over_cap_brief_stops_the_queue(tmp_path: pathlib.Path, monkeypatch) -> None:
    (tmp_path / ".git" / "page-sessions").mkdir(parents=True)
    big = tmp_path / "late-write.md"
    big.write_text(OVER, encoding="utf-8")
    step = tmp_path / "plan.sh"
    ran: list[str] = []
    monkeypatch.setattr(ps.subprocess, "run", lambda cmd, **kw: (ran.append(cmd[0]), ps.subprocess.CompletedProcess(cmd, 0, stdout=f"{big}\n"))[1])
    monkeypatch.delenv("WRITE_CAP_OK", raising=False)
    later = ps.new_item(str(tmp_path), "n", [], str(big), True)
    run_log = tmp_path / "run.log"
    ps.work(str(tmp_path), "n", [], [{"then": str(step)}, later], str(run_log))
    lines = run_log.read_text(encoding="utf-8").splitlines()
    assert ran == [str(step)], "nothing after the refusal runs"
    assert lines[0].startswith("STOPPED late-write.md: it assigns 5 questions") and lines[-1] == "ALL DONE", lines


def test_a_continuation_a_session_leaves_is_queued_next_before_the_checks(tmp_path: pathlib.Path, monkeypatch) -> None:
    """D3: a write session that hits the key cap writes its unreached items to $L7R_CONTINUE and stops; the runner
    queues that brief next - before the group's `then:` checks step - counted like any brief, still a write session."""
    w = tmp_path / "g1-write.md"
    w.write_text(BRIEF, encoding="utf-8")
    step = tmp_path / "checks.sh"
    (first,) = ps.plan(str(tmp_path), "n", "/p", [], [str(w)])
    order: list[str] = []

    def fake_run(cmd, **kw):  # noqa: ANN001, ANN003, ANN202
        if cmd[0] == str(step):
            order.append("then")
            return ps.subprocess.CompletedProcess(cmd, 0, stdout="")
        env = kw["env"]
        order.append(env["L7R_PAGE_SESSION"])
        if env["L7R_PAGE_SESSION"] == first["sid"]:
            pathlib.Path(env["L7R_CONTINUE"]).write_text("# Brief (continued)\n\n## Your items\n- B2 the one not reached\n", encoding="utf-8")
        assert env["L7R_KEY_CAP"] == str(ps.KEY_CAP), "a continuation of a write session is capped too"
        return ps.subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(ps.subprocess, "run", fake_run)
    run_log = tmp_path / "run.log"
    ps.work(str(tmp_path), "n", [], [first, {"then": str(step)}], str(run_log))
    assert len(order) == 3 and order[0] == first["sid"] and order[2] == "then", order
    log = run_log.read_text(encoding="utf-8")
    assert f"continued {first['sid']} -> {order[1]}" in log
    index = (tmp_path / ".git" / "page-sessions" / "index.txt").read_text(encoding="utf-8")
    assert f"{order[1]} {tmp_path}/.git/page-sessions/{first['sid']}/continue.md" in index


def test_a_continuation_over_the_cap_stops_the_queue(tmp_path: pathlib.Path, monkeypatch) -> None:
    monkeypatch.delenv("WRITE_CAP_OK", raising=False)
    w = tmp_path / "g1-write.md"
    w.write_text(BRIEF, encoding="utf-8")
    (first,) = ps.plan(str(tmp_path), "n", "/p", [], [str(w)])
    monkeypatch.setattr(ps.subprocess, "run", lambda cmd, **kw: (pathlib.Path(kw["env"]["L7R_CONTINUE"]).write_text(OVER, encoding="utf-8"), ps.subprocess.CompletedProcess(cmd, 0))[1])
    run_log = tmp_path / "run.log"
    ps.work(str(tmp_path), "n", [], [first, {"then": "/never/run"}], str(run_log))
    lines = run_log.read_text(encoding="utf-8").splitlines()
    assert lines[-2].startswith("STOPPED continue.md: it assigns 5") and lines[-1] == "ALL DONE", lines


def _run_sh(tmp_path: pathlib.Path, *args: str) -> tuple[int, list[str], str]:
    """page-session.sh with a fake `claude` and a fake `python3` on PATH: the fake python records the runner's argv."""
    import subprocess

    bin_ = tmp_path / "bin"
    bin_.mkdir(parents=True)
    (bin_ / "claude").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    argv_file = tmp_path / "argv.json"
    (bin_ / "python3").write_text(
        f"#!/usr/bin/env -S {pathlib.Path(__import__('sys').executable)}\nimport json, sys\nopen({str(argv_file)!r}, 'w').write(json.dumps(sys.argv[1:]))\n", encoding="utf-8"
    )
    for f in bin_.iterdir():
        f.chmod(0o755)
    brief = tmp_path / "brief.md"
    brief.write_text(BRIEF, encoding="utf-8")
    env = {"PATH": f"{bin_}:/usr/bin:/bin", "HOME": str(tmp_path)}
    r = subprocess.run(["bash", str(REPO / "scripts" / "page-session.sh"), str(brief), *args], cwd=REPO, env=env, capture_output=True, text=True, check=False)
    argv = __import__("json").loads(argv_file.read_text()) if argv_file.exists() else []
    return r.returncode, argv, r.stderr


def test_effort_and_agents_reach_every_session_and_unset_they_change_nothing(tmp_path: pathlib.Path) -> None:
    """Feature 293 (research R1 D2, FR-003): the effort experiment runs each page session at its arm's effort and with the
    pinned ad-hoc judge; unset, the runner's argv is what it was."""
    code, plain, _ = _run_sh(tmp_path / "a", "diagram-x", "opus")
    assert code == 0 and "--effort" not in plain and "--agents" not in plain
    extra = plain[plain.index("--model") : plain.index("--")]
    assert extra == ["--model", "opus"], "unset EFFORT and AGENTS add nothing"
    agents = tmp_path / "agents.json"
    agents.write_text('{"adhoc-judge": {"model": "opus", "effort": "high"}}', encoding="utf-8")
    code, argv, _ = _run_sh(tmp_path / "b", "diagram-x", "", "xhigh", str(agents))
    extra = argv[4 : argv.index("--")]  # the runner script, root, name, projects, then the extra flags
    assert code == 0 and extra == ["--effort", "xhigh", "--agents", agents.read_text()]


def test_a_missing_agents_file_is_refused_before_anything_starts(tmp_path: pathlib.Path) -> None:
    code, argv, err = _run_sh(tmp_path, "diagram-x", "", "medium", str(tmp_path / "nope.json"))
    assert code == 2 and argv == [] and "no agents file" in err


# ---- feature 295 item 3: a headless session that has gone quiet is resumed ------------------------------------------


def test_a_session_s_last_activity_is_its_newest_transcript_or_subagent_write(tmp_path: pathlib.Path) -> None:
    import os

    assert ps.last_activity(str(tmp_path), "sid") is None, "nothing written yet"
    (tmp_path / "sid.jsonl").write_text("{}", encoding="utf-8")
    os.utime(tmp_path / "sid.jsonl", (1000, 1000))
    assert ps.last_activity(str(tmp_path), "sid") == 1000
    sub = tmp_path / "sid" / "subagents"
    sub.mkdir(parents=True)
    (sub / "agent-a.jsonl").write_text("{}", encoding="utf-8")
    os.utime(sub / "agent-a.jsonl", (5000, 5000))
    assert ps.last_activity(str(tmp_path), "sid") == 5000, "a subagent still writing is the session still working"


def test_the_projects_directory_is_the_one_page_session_sh_names(monkeypatch) -> None:
    monkeypatch.setenv("HOME", "/h")
    assert ps.projects_dir("/diagram/.clones/diagram-x") == "/h/.claude/projects/-diagram--clones-diagram-x"


def _fake_claude(tmp_path: pathlib.Path, sid: str):  # noqa: ANN202
    """A live process whose argv is a session's: a copy of bash named `claude`, `--session-id <sid>` among its args."""
    import shutil
    import subprocess

    exe = tmp_path / "claude"
    shutil.copy(shutil.which("bash") or "/bin/bash", exe)
    return subprocess.Popen([str(exe), "-c", "sleep 30; :", "--session-id", sid], stdin=subprocess.DEVNULL)


def test_session_pids_finds_the_session_by_its_argument_and_nothing_else(tmp_path: pathlib.Path) -> None:
    proc = _fake_claude(tmp_path, "sid-295")
    try:
        assert ps.session_pids("sid-295") == [proc.pid]
        assert ps.session_pids("sid-other") == []
    finally:
        proc.kill()
        proc.wait()


def test_the_watch_ends_a_silent_session_and_leaves_a_writing_one(tmp_path: pathlib.Path) -> None:
    """Silence past the threshold with the process alive ends it; a fresh write keeps it; no process, nothing to end."""
    import os
    import time

    proc = _fake_claude(tmp_path, "sid-quiet")
    try:
        (tmp_path / "sid-quiet.jsonl").write_text("{}", encoding="utf-8")
        os.utime(tmp_path / "sid-quiet.jsonl", (time.time() - 3600, time.time() - 3600))
        busy = ps.StallWatch(str(tmp_path), "sid-quiet", check=0.05, after=5)
        busy.start()
        time.sleep(0.3)
        busy.stop()
        assert not busy.stalled, "silence is counted from the watch's start, never from before it (a resume's old transcript)"
        watch = ps.StallWatch(str(tmp_path), "sid-quiet", check=0.05, after=0.2)
        watch.start()
        assert proc.wait(timeout=10) != 0, "the silent session's process was ended"
        watch.join(timeout=5)
        assert watch.stalled and watch.idle >= 0
    finally:
        proc.kill()
        proc.wait()
    gone = ps.StallWatch(str(tmp_path), "sid-none", check=0.05, after=0.0)
    gone.start()
    time.sleep(0.3)
    gone.stop()
    assert not gone.stalled, "no live process for the session: nothing is ended"


def test_a_stalled_session_is_resumed_at_once_and_capped(tmp_path: pathlib.Path, monkeypatch) -> None:
    """The R12 incident: a stall is resumed with no usage-limit wait; past STALL_RESUMES the queue moves on."""
    (tmp_path / "a.md").write_text(BRIEF, encoding="utf-8")
    (tmp_path / "b.md").write_text(BRIEF, encoding="utf-8")
    queue = ps.plan(str(tmp_path), "n", "/p", [], [str(tmp_path / "a.md"), str(tmp_path / "b.md")])
    first = queue[0]["sid"]
    stalls = iter([True] * (ps.STALL_RESUMES + 1) + [False] * 5)

    class FakeWatch:
        def __init__(self, projects: str, sid: str) -> None:
            self.sid, self.stalled, self.idle = sid, False, 0

        def start(self) -> None:
            self.stalled = self.sid == first and next(stalls)
            self.idle = 1200 if self.stalled else 0

        def stop(self) -> None:
            pass

    calls: list[list[str]] = []

    def fake_run(cmd, **kw):  # noqa: ANN001, ANN003, ANN202
        calls.append(cmd)
        kw["stdout"].write('{"subtype": "success"}')
        return ps.subprocess.CompletedProcess(cmd, 0)

    slept: list[float] = []
    monkeypatch.setattr(ps, "StallWatch", FakeWatch)
    monkeypatch.setattr(ps.subprocess, "run", fake_run)
    monkeypatch.setattr(ps.time, "sleep", slept.append)
    run_log = tmp_path / "run.log"
    ps.work(str(tmp_path), "n", [], queue, str(run_log))
    lines = run_log.read_text(encoding="utf-8").splitlines()
    assert slept == [], "a stall owes no usage-limit wait"
    assert sum(ln.startswith("stalled ") and "resuming it" in ln for ln in lines) == ps.STALL_RESUMES
    assert f"stalled {first} - idle 20 min, resumed {ps.STALL_RESUMES} times already; moving on" in lines
    assert all("--resume" in c for c in calls[1 : ps.STALL_RESUMES + 1]), "each stall resumes the SAME session"
    assert "--session-id" in calls[-1] and lines[-1] == "ALL DONE", "then the next brief runs"


# Feature 317: a resumed session is handed what its agents returned (R1's check session dispatched its eight checks twice).


def _transcript(path: pathlib.Path, rows: list[dict]) -> None:
    import json

    path.write_text("".join(json.dumps(r) + "\n" for r in rows) + "not json\n", encoding="utf-8")


def _note(name: str) -> dict:
    return {
        "type": "queue-operation",
        "operation": "enqueue",
        "content": f"<task-notification>\n<summary>Agent \"{name}\" finished</summary>\n<result>{name}: 1 IN-STEP</result>\n</task-notification>",
    }


def _turn(stop: str) -> dict:
    return {"type": "assistant", "message": {"stop_reason": stop, "content": [{"type": "text", "text": "..."}]}}


DEQ = {"type": "queue-operation", "operation": "dequeue"}


def test_the_reports_a_headless_session_never_took_up_are_those_queued_since_its_last_dequeue(tmp_path: pathlib.Path) -> None:
    """The R1 check session's transcript, in small: a prompt taken up, then eight reports queued and never taken up; after
    the resume the notice of unfinished agents and the prompt are taken up, and only what is queued after counts."""
    _transcript(tmp_path / "sid.jsonl", [{"type": "queue-operation", "operation": "enqueue", "content": "the brief"}, DEQ, _turn("end_turn"), _note("quote-check"), _note("record-format")])
    got = ps.undelivered(str(tmp_path), "sid")
    assert len(got) == 2 and "quote-check: 1 IN-STEP" in got[0] and "record-format" in got[1]
    _transcript(tmp_path / "sid.jsonl", [_note("quote-check"), DEQ, _turn("tool_use")])
    assert ps.undelivered(str(tmp_path), "sid") == [] and ps.undelivered(str(tmp_path), "none") == []


def test_a_turn_has_ended_only_when_the_last_assistant_entry_stopped_at_end_turn(tmp_path: pathlib.Path) -> None:
    _transcript(tmp_path / "a.jsonl", [_turn("tool_use"), _turn("end_turn"), _note("x")])
    _transcript(tmp_path / "b.jsonl", [_turn("end_turn"), _turn("tool_use")])
    assert ps.turn_ended(str(tmp_path), "a") and not ps.turn_ended(str(tmp_path), "b") and not ps.turn_ended(str(tmp_path), "none")


def test_a_resume_names_the_file_of_reports_and_a_resume_item_carries_them(tmp_path: pathlib.Path) -> None:
    """The reports are written beside the session's log and the resume's prompt names the file; with none, no file and the
    plain continue. A `resume:` item is planned with them, and a stall of it resumes it again rather than failing (its
    command has no `--session-id` left to replace)."""
    assert ps.returned_file(str(tmp_path), []) is None and not (tmp_path / "returned.md").exists()
    path = ps.returned_file(str(tmp_path), ["<task-notification>a</task-notification>", "<task-notification>b</task-notification>"])
    assert path == str(tmp_path / "returned.md") and (tmp_path / "returned.md").read_text(encoding="utf-8").count("<task-notification>") == 2
    base = ["claude", "-p", "brief", "--session-id", "s1"]
    assert ps.resume_command(base, "s1")[2] == ps.RESUME
    told = ps.resume_command(base, "s1", path)
    assert told[2].startswith(ps.RESUME) and path in told[2] and "do not dispatch them again" in told[2] and told[3:] == ["--resume", "s1"]
    assert ps.resume_command(told, "s1") == [*told[:2], ps.RESUME, "--resume", "s1"], "a resumed command resumed again"
    brief = tmp_path / "r1-check.md"
    brief.write_text(BRIEF, encoding="utf-8")
    sid = "46661922-2c8c-4c0d-9ba3-d357b196b81b"
    projects = tmp_path / "projects"
    projects.mkdir()
    _transcript(projects / f"{sid}.jsonl", [DEQ, _turn("end_turn"), _note("entry-drift CartYard")])
    (item,) = ps.plan(str(tmp_path), "n", str(projects), [], [f"resume:{sid}:{brief}"])
    returned = pathlib.Path(item["log"], "returned.md")
    assert returned.exists() and "entry-drift CartYard" in returned.read_text(encoding="utf-8")
    assert str(returned) in item["cmd"][item["cmd"].index("-p") + 1]


def test_a_session_whose_turn_ended_with_reports_waiting_is_resumed_before_the_long_stall(tmp_path: pathlib.Path) -> None:
    """Quiet past RETURNED_AFTER, its turn ended and reports queued: ended well short of STALL_AFTER. Quiet as long but still
    in a tool call (its turn not ended), or with nothing queued, it is left to the long stall."""
    import os
    import time

    def watch(rows: list[dict], sid: str) -> bool:
        proc = _fake_claude(tmp_path, sid)
        try:
            _transcript(tmp_path / f"{sid}.jsonl", rows)
            os.utime(tmp_path / f"{sid}.jsonl", (time.time() - 3600, time.time() - 3600))
            w = ps.StallWatch(str(tmp_path), sid, check=0.05, after=600, returned=0.2)
            w.start()
            time.sleep(0.6)
            w.stop()
            return w.stalled
        finally:
            proc.kill()
            proc.wait()

    assert watch([DEQ, _turn("end_turn"), _note("quote-check")], "sid-back"), "the reports are back: resumed now"
    assert not watch([DEQ, _turn("tool_use"), _note("quote-check")], "sid-busy"), "still in a tool call: left alone"
    assert not watch([DEQ, _turn("end_turn")], "sid-idle"), "nothing queued: left to the long stall"
