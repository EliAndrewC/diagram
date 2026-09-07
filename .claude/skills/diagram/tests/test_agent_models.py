"""Every subagent check runs on Opus (GM 2026-09-07: *"our subagent checks should all specifically use the Opus model, regardless of what the main claude code session uses"*).

The model is pinned in each agent file's frontmatter rather than inherited, so the session's own model never
leaks into a check; this test derives the roster from the directory, so a new agent owes the pin the day it lands.
"""

from __future__ import annotations

import pathlib
import re

AGENTS = pathlib.Path(__file__).resolve().parents[4] / ".claude" / "agents"


def _frontmatter(path: pathlib.Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    assert m, f"{path.name}: no YAML frontmatter"
    return {k.strip(): v.strip() for k, v in (line.split(":", 1) for line in m.group(1).splitlines() if ":" in line)}


def test_every_agent_pins_opus() -> None:
    files = sorted(AGENTS.glob("*.md"))
    assert len(files) >= 7, "the agents directory was found (non-vacuity)"
    wrong = {p.name: _frontmatter(p).get("model", "<missing>") for p in files if _frontmatter(p).get("model") != "opus"}
    assert not wrong, f"agents not pinned to Opus (GM 2026-09-07): {wrong}"
