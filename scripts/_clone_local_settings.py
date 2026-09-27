#!/usr/bin/env python3
"""Keep a clone's untracked `.claude/settings.local.json` excluding the MIRROR's root CLAUDE.md (feature 250).

WHY. Every clone lives inside the mirror (`/diagram/.clones/<name>`), so a session working in one loads the root
CLAUDE.md twice - the mirror's, because it sits above the clone, and the clone's own copy. Measured on a probe,
2026-09-26: excluding the mirror's copy took a session's first turn from 28,590 tokens to 21,267, and every turn
carries it (feature 250 research R4, recommendation 4). The page sessions got the fix as a launch flag; this gives
it to EVERY session in a clone, the GM's own included, through the local settings file git ignores. It takes
effect the next time a session starts there.

    _clone_local_settings.py <clone>     writes or merges the setting; prints one line when it changed anything

Only in a clone (a path under `.clones/`); the mirror keeps its own CLAUDE.md, which is its only copy. Other keys
in the file are kept; a file that is not JSON is left alone and reported, never overwritten.
"""

from __future__ import annotations

import json
import pathlib
import sys

KEY = "claudeMdExcludes"


def mirror_claude_md(clone: pathlib.Path) -> str | None:
    parts = clone.resolve().parts
    if ".clones" not in parts:
        return None
    return str(pathlib.Path(*parts[: parts.index(".clones")]) / "CLAUDE.md")


def ensure(clone: pathlib.Path) -> str:
    """What was done, as one line - empty when nothing needed doing."""
    target = mirror_claude_md(clone)
    if target is None:
        return ""
    path = clone / ".claude" / "settings.local.json"
    data: dict = {}
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8") or "{}")
        except ValueError:
            return f"clone-settings: {path} is not JSON - left alone; add \"{KEY}\": [\"{target}\"] by hand"
    excludes = data.get(KEY) or []
    if target in excludes:
        return ""
    data[KEY] = [*excludes, target]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return (f"clone-settings: {path} now excludes the mirror's {target}, which every session in this clone loaded "
            "beside the clone's own copy (about 7,000 tokens a turn) - it takes effect at the next session start")


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: _clone_local_settings.py <clone>", file=sys.stderr)
        return 2
    said = ensure(pathlib.Path(argv[0]))
    if said:
        print(said)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
