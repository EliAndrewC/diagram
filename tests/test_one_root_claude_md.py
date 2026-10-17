"""A session loads the project's root instructions once (feature 383 amendment 6, FR-037, plan D40).

The GM, 2026-10-17: a session started in the checkout that works in its clone loaded CLAUDE.md twice - the checkout's at launch
and the clone's own copy, ~9k tokens, when it first touched a file there. `claudeMdExcludes` skips the clone's copy and leaves
its nested files to load where they are needed (specs/383 research R15).
"""

from __future__ import annotations

import fnmatch
import json
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[1]


def _excludes() -> list[str]:
    return json.loads((REPO / ".claude" / "settings.json").read_text(encoding="utf-8")).get("claudeMdExcludes", [])


def _excluded(path: str) -> bool:
    return any(_matches(path, p) for p in _excludes())


def _matches(path: str, pattern: str) -> bool:
    """A glob over absolute paths where `*` stays within one directory, as the settings' globs do."""
    return len(path.split("/")) == len(pattern.split("/")) and all(fnmatch.fnmatchcase(a, b) for a, b in zip(path.split("/"), pattern.split("/"), strict=True))


def test_the_clones_copy_of_the_root_claude_md_is_excluded() -> None:
    assert _excluded("/diagram/.clones/diagram-performance/CLAUDE.md"), "the clone's root CLAUDE.md loads beside the checkout's - add it to claudeMdExcludes"


def test_nothing_the_session_needs_once_is_excluded() -> None:
    for kept in ("/diagram/CLAUDE.md", "/diagram/.clones/x/tests/CLAUDE.md", "/diagram/.clones/x/l7r/diagram/CLAUDE.md", "/diagram/.clones/x/research/CLAUDE.md"):
        assert not _excluded(kept), f"{kept} is excluded, and only the clone's copy of the ROOT file is a duplicate"
