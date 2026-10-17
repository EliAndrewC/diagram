#!/usr/bin/env python3
"""Text every dispatch of a check shares, written into the check's agent file (feature 383 amendment 6, FR-032, plan D35).

An agent file is the agent's system prompt, the first thing in every dispatch, so it is read from the prompt cache by every
dispatch of its type after the first; a bundle is read after the prompt, which differs per unit, so every copy of a text in a
bundle is written to the cache fresh. The three modal checks' bundles each carried the modal guidelines, 15-17k characters,
339 times between 2026-10-10 and 10-17 (research R13). The GM, 2026-10-17: *"any context that subagents share in common is put
either into their system prompt, ideally, or ... at the very beginning of the prompt"*.

    agent_sync.py           write each agent file's generated sections from their sources
    agent_sync.py --check   list the agent files whose sections differ from their sources; exit 1 if any (the test runs it)

A section is the source's text between `<!-- generated: <source> ... -->` and `<!-- /generated: <source> -->`; everything
else in the agent file is the agent's own and is left as it is. Edit the source (`dev/modals.md`), never the copy.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
_MODALS = ("dev/modals.md", "dev/modals-particular.md")
#: agent file -> the sources it carries, in order
SYNC: dict[str, tuple[str, ...]] = {
    ".claude/agents/modal-form.md": _MODALS,
    ".claude/agents/modal-depiction.md": _MODALS,
    ".claude/agents/modal-research.md": _MODALS,
}
HEAD = "## The guidelines (generated - `make agent-sync` writes them from their sources; edit the source, not this copy)"


def _section(source: str, text: str) -> str:
    return f"<!-- generated: {source} -->\n{text.rstrip()}\n<!-- /generated: {source} -->\n"


def render(agent_text: str, sources: dict[str, str]) -> str:
    """The agent file with its generated part (HEAD and the sections after it) written from `sources`, in their order."""
    own = agent_text.split("\n" + HEAD, 1)[0].rstrip()
    own = re.sub(r"\n<!-- generated: [^>]*-->.*?<!-- /generated: [^>]*-->\n?", "\n", own, flags=re.S).rstrip()
    return own + "\n\n" + HEAD + "\n\n" + "\n".join(_section(s, t) for s, t in sources.items())


def stale(root: pathlib.Path = ROOT) -> list[str]:
    out = []
    for agent, sources in SYNC.items():
        path = root / agent
        want = render(path.read_text(encoding="utf-8"), {s: (root / s).read_text(encoding="utf-8") for s in sources})
        if path.read_text(encoding="utf-8") != want:
            out.append(agent)
    return out


def write(root: pathlib.Path = ROOT) -> list[str]:
    changed = stale(root)
    for agent in changed:
        path = root / agent
        path.write_text(render(path.read_text(encoding="utf-8"), {s: (root / s).read_text(encoding="utf-8") for s in SYNC[agent]}), encoding="utf-8")
    return changed


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    if a.check:
        bad = stale()
        for agent in bad:
            print(f"agent-sync: {agent} differs from {', '.join(SYNC[agent])} - run `make agent-sync` and commit the agent file")
        return 1 if bad else 0
    changed = write()
    print(f"agent-sync: {len(changed)} agent file(s) written" + (f": {', '.join(changed)}" if changed else " - all in step"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
