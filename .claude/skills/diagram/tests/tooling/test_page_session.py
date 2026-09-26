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
