#!/usr/bin/env python3
"""Does this text carry an unresolved merge conflict? The ONE detector, shared (feature 241).

Shared on purpose, the way `_hm_make.recipe_comment_hazards` is shared between the recipe-comment guard
and its gate-phase backstop: two copies of a detector drift, and the copy in the backstop is the one
nobody reads until it is wrong.

WHAT COUNTS. The TRIPLE `git merge` leaves, in order, each at the start of a line: seven `<`, then a line
of exactly seven `=`, then seven `>`. Any ONE of them alone is not a conflict and must not be treated as
one - a line of seven `=` is an ordinary Markdown underline, and a session writing about merges types the
other two. Requiring all three in order is what makes the rule safe to refuse on.

WHAT IS PROSE. A marker inside a fenced block (``` or ~~~), inside an indented block (four spaces or a
tab), or inside a backtick span is text ABOUT a conflict - this feature's own spec, research and suite all
carry examples, and so does any doc explaining a merge. Those lines are skipped before the triple is
looked for, which is the same "match invocations not mentions" rule every guard here follows.

The markers are BUILT rather than written, so this file does not trip its own detector when the backstop
scans the tree.
"""

from __future__ import annotations

import pathlib
import subprocess
import sys

OPEN, MID, CLOSE = "<" * 7, "=" * 7, ">" * 7


def _live_lines(text: str) -> list[str]:
    """The lines a reader would execute rather than read: fenced and indented blocks dropped."""
    out, fence = [], ""
    for raw in text.splitlines():
        stripped = raw.lstrip()
        if fence:
            if stripped.startswith(fence):
                fence = ""
            continue
        if stripped.startswith("```") or stripped.startswith("~~~"):
            fence = stripped[:3]
            continue
        if raw.startswith("    ") or raw.startswith("\t"):
            continue  # an indented block: prose showing a marker, not a marker
        out.append(raw)
    return out


def has_conflict(text: str) -> bool:
    """The triple, in order, on lines that are not prose."""
    state = 0
    for line in _live_lines(text):
        if state == 0 and line.startswith(OPEN):
            state = 1
        elif state == 1 and line.rstrip() == MID:
            state = 2
        elif state == 2 and line.startswith(CLOSE):
            return True
    return False


def conflicted(paths: list[str] | tuple[str, ...]) -> list[str]:
    """Which of these paths carry a conflict. Anything unreadable as text is SKIPPED, never guessed at:
    a binary file, a path that is a directory, a file deleted between the command and this check."""
    bad = []
    for p in paths:
        f = pathlib.Path(p)
        try:
            if not f.is_file():
                continue
            text = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if has_conflict(text):
            bad.append(str(p))
    return sorted(bad)


def tracked_files(root: str) -> list[str]:
    """Every tracked file, from git rather than from a walk - the backstop's subject."""
    r = subprocess.run(["git", "-C", root, "ls-files", "-z"], capture_output=True, text=True, check=False)
    return [str(pathlib.Path(root) / n) for n in r.stdout.split("\0") if n]


def main(argv: list[str]) -> int:
    if not argv or argv[0] != "--tracked":
        print("usage: _hm_conflict.py --tracked <root>   # the gate backstop; exits 1 naming any file with a conflict", file=sys.stderr)
        return 2
    root = argv[1] if len(argv) > 1 else "."
    bad = conflicted(tracked_files(root))
    if not bad:
        print(f"conflict-markers: none in {len(tracked_files(root))} tracked file(s)")
        return 0
    print("\nCONFLICT MARKERS IN TRACKED FILES - a merge was committed unresolved:", file=sys.stderr)
    for p in bad:
        print(f"  {p}", file=sys.stderr)
    print("\nResolve each one and commit the resolution. The history here is never rewritten, so the markers", file=sys.stderr)
    print("cannot be amended away - the fix is a commit on top (feature 241; twice on 2026-09-12/13).\n", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
