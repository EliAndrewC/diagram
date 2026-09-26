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
    runs = ps.plan(str(tmp_path), "diagram-research", "/p", ["--model", "opus"], [str(b) for b in briefs])
    assert len(runs) == 2 and runs[0][0] != runs[1][0], "two sessions, two ids"
    for (sid, log, *cmd), brief in zip(runs, briefs, strict=True):
        assert pathlib.Path(log).is_dir() and log.endswith(sid)
        assert cmd[:2] == ["claude", "-p"] and str(brief) in cmd[2], "the prompt names its own brief"
        assert cmd[cmd.index("-n") + 1] == "diagram-research" and cmd[cmd.index("--session-id") + 1] == sid
        assert "bypassPermissions" in cmd and cmd[-2:] == ["--output-format", "json"] and "--model" in cmd
    out = capsys.readouterr().out
    assert out.index("veg-1.md") < out.index("veg-2.md") and f"/p/{runs[0][0]}.jsonl" in out
