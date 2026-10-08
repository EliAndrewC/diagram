"""Every hook `.claude/settings.json` registers runs a script that EXISTS where the command looks for it (feature 250 D16).

WHY. Hooks run the MIRROR's copy (`/diagram/scripts/...`) so a fix reaches every session at once and no clone can
weaken a guard by editing its own copy (docs/session-clones.md). But a guard added in a feature is not in the mirror
until the feature lands, and a hook whose script is missing fails without blocking anything: `check-bundle-hooks.sh`
(feature 250 D8) and `canon-read-hooks.sh` (D16) were registered and never ran - found by the D16 plan review, which
measured zero guard-log entries for the first. So a guard not yet on main is registered with the fallback form
(`h=/diagram/scripts/X; [ -x "$h" ] || h="$CLAUDE_PROJECT_DIR/scripts/X"; exec "$h" ...`), and this fails on a bare
mirror path whose script the mirror does not have.
"""

from __future__ import annotations

import json
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[5]
MIRROR = pathlib.Path("/diagram/scripts")
BARE = re.compile(r"^/diagram/scripts/([\w.-]+)")
FALLBACK = re.compile(r'^h=/diagram/scripts/([\w.-]+); \[ -x "\$h" \] \|\| h="\$CLAUDE_PROJECT_DIR/scripts/\1"; exec "\$h" ')


def _commands() -> list[str]:
    hooks = json.loads((REPO / ".claude" / "settings.json").read_text(encoding="utf-8")).get("hooks", {})
    return [h["command"] for entries in hooks.values() for e in entries for h in e.get("hooks", []) if "command" in h]


def test_every_registered_hook_script_exists_where_its_command_looks() -> None:
    commands = _commands()
    assert len(commands) > 20, "the census found the hooks"
    missing = []
    for cmd in commands:
        fb = FALLBACK.match(cmd)
        if fb:
            assert (REPO / "scripts" / fb.group(1)).is_file(), f"{fb.group(1)}: not in this checkout's scripts/"
            continue
        bare = BARE.match(cmd)
        if bare and MIRROR.is_dir() and not (MIRROR / bare.group(1)).is_file():
            missing.append(bare.group(1))
    assert not missing, f"registered by the mirror path, but not in the mirror (it never runs until it lands): {missing} - register it with the fallback form"
