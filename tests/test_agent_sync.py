"""The text every dispatch of a check shares lives in its agent file, in step with its source (feature 383 amendment 6, D35)."""

from __future__ import annotations

import importlib.util
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("agent_sync", REPO / "scripts/reviews/agent_sync.py")
assert spec and spec.loader
sync = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = sync
spec.loader.exec_module(sync)


def test_every_agent_file_carries_its_sources_as_they_are() -> None:
    assert sync.stale() == [], "an agent file's generated guidelines differ from their source - run `make agent-sync` and commit the agent file"


def test_render_replaces_the_generated_part_and_keeps_the_agents_own_text() -> None:
    own = "---\nname: x\n---\nThe agent's own contract."
    once = sync.render(own, {"dev/a.md": "rule one\n", "dev/b.md": "rule two\n"})
    assert once.startswith(own) and "<!-- generated: dev/a.md -->\nrule one\n<!-- /generated: dev/a.md -->" in once
    again = sync.render(once, {"dev/a.md": "rule one, revised\n", "dev/b.md": "rule two\n"})
    assert again.count(sync.HEAD) == 1 and "rule one, revised" in again and "rule one\n" not in again.split(sync.HEAD)[1].replace("rule one, revised", "")
    assert sync.render(again, {"dev/a.md": "rule one, revised\n", "dev/b.md": "rule two\n"}) == again, "idempotent"


def test_check_and_write_name_what_moved(tmp_path: pathlib.Path, monkeypatch, capsys) -> None:  # noqa: ANN001
    (tmp_path / "dev").mkdir()
    (tmp_path / ".claude" / "agents").mkdir(parents=True)
    (tmp_path / "dev" / "g.md").write_text("the rule\n", encoding="utf-8")
    (tmp_path / ".claude" / "agents" / "c.md").write_text("contract\n", encoding="utf-8")
    monkeypatch.setattr(sync, "SYNC", {".claude/agents/c.md": ("dev/g.md",)})
    monkeypatch.setattr(sync, "ROOT", tmp_path)
    monkeypatch.setattr(sync.stale, "__defaults__", (tmp_path,))
    monkeypatch.setattr(sync.write, "__defaults__", (tmp_path,))
    assert sync.main(["--check"]) == 1 and "run `make agent-sync`" in capsys.readouterr().out
    assert sync.main([]) == 0 and "1 agent file(s) written" in capsys.readouterr().out
    assert sync.main(["--check"]) == 0 and "the rule" in (tmp_path / ".claude" / "agents" / "c.md").read_text(encoding="utf-8")
    assert sync.main([]) == 0 and "all in step" in capsys.readouterr().out
