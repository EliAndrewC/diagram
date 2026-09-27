"""`scripts/_canon.py` and `scripts/_hm_canon.py` (feature 250 D16): the canon searched for every term at once.

WHAT THESE PROVE. `make canon` reports every term's hits with the heading each sits under, caps a term's rows,
says so when a term has none, and refuses an empty TERMS; the guard's decision names a direct read of a canon file
(absolute path, `cd` then relative, the Read and Grep tools) and passes a mention or a read of anything else; a
`make canon` within three tool calls of another is a repeat unless it names every earlier term (the fold).
"""

from __future__ import annotations

import importlib.util
import json
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[5]


def _load(name: str):  # noqa: ANN202
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


canon = _load("_canon")
hm = _load("_hm_canon")


def test_every_term_is_answered_with_its_heading(tmp_path, capsys) -> None:
    f = tmp_path / "budgets.md"
    f.write_text("# Roads\nThe Imperial road is kept by the treasury.\n## Cities\nMerchants are a quarter.\n" + "road\n" * 20, encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text("Imperial road", encoding="utf-8")
    files = canon.canon_files((tmp_path, tmp_path / "missing"))
    assert files == [f], "CLAUDE.md is not canon, and a missing root is skipped"
    assert canon.main(["Imperial road|merchant|ogre"], files=files) == 0
    out = capsys.readouterr().out
    assert "== Imperial road: 1 hit(s)" in out and "[Roads] The Imperial road is kept" in out
    assert "[Cities] Merchants are a quarter." in out and "== ogre: 0 hit(s)" in out
    assert canon.main(["road"], files=files) == 0
    assert "the first 15 shown" in capsys.readouterr().out
    assert canon.main([" | "], files=files) == 2
    assert "every term of the claim" in capsys.readouterr().err


def _payload(tool: str, ti: dict, transcript: pathlib.Path | None = None) -> dict:
    return {"tool_name": tool, "tool_input": ti, "tool_use_id": "now", "transcript_path": str(transcript or "")}


def test_a_direct_read_is_named_and_a_mention_is_not() -> None:
    direct = [
        ("Bash", {"command": "grep -n road /host-l7r-repo/setting/budgets.md"}),
        ("Bash", {"command": "cd /host-l7r-repo && sed -n 1,9p gm-assistant/setting/economics.md"}),
        ("Read", {"file_path": "/host-l7r-repo/setting/l7r.md"}),
        ("Grep", {"pattern": "x", "path": "/host-l7r-repo/gm-assistant/setting"}),
    ]
    for tool, ti in direct:
        assert hm.decide(_payload(tool, ti)) == "direct", ti
    passing = [
        ("Bash", {"command": "echo /host-l7r-repo/setting/budgets.md"}),
        ("Bash", {"command": "grep -rn road research/"}),
        ("Read", {"file_path": "/diagram/research/x.html"}),
        ("Edit", {"file_path": "/host-l7r-repo/setting/l7r.md"}),
        ("Bash", {"command": "make canon TERMS=road | grep -c road"}),
    ]
    for tool, ti in passing:
        assert hm.decide(_payload(tool, ti)) == "pass", ti


def test_a_repeat_is_refused_unless_it_folds(tmp_path) -> None:
    t = tmp_path / "t.jsonl"

    def earlier(*cmds: str) -> None:
        rows = [json.dumps({"type": "assistant", "message": {"content": [{"type": "tool_use", "id": f"t{i}", "input": {"command": c}}]}}) for i, c in enumerate(cmds)]
        rows.insert(0, "not json")
        rows.append(json.dumps({"type": "assistant", "isSidechain": True, "message": {"content": [{"type": "tool_use", "id": "side", "input": {"command": "make canon TERMS=x"}}]}}))
        t.write_text("\n".join(rows), encoding="utf-8")

    earlier("ls", "make canon TERMS='road|merchant'")
    assert hm.decide(_payload("Bash", {"command": 'make canon TERMS="artisan"'}, t)) == "repeat"
    assert hm.decide(_payload("Bash", {"command": 'make canon TERMS="Road|merchant|artisan"'}, t)) == "pass"
    earlier("make canon TERMS=road", "ls", "ls", "ls")
    assert hm.decide(_payload("Bash", {"command": "make canon TERMS=artisan"}, t)) == "pass", "outside the window"
    assert hm.decide(_payload("Bash", {"command": "make canon TERMS=artisan"}, tmp_path / "missing.jsonl")) == "pass"
    assert hm.recent_commands(str(t), "now", window=2) == ["ls", "ls"]
