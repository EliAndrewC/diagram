#!/usr/bin/env python3
"""Feature 329, T07: move the documents the Markdown audit relocates, and every pointer with them (plan D12).

For every LIVE tracked text file (not specs/, scripts/fixtures/, dev/*-log/, the review ledger):
  1. a repo-relative mention of a moved path (`dev/reviews.md`, `buildings/programs.md#x`) -> its new path;
  2. a RELATIVE link or path (`../dev/reviews.md`, `programs.md`) that resolves, from the file's own place, to a moved
     path -> the relative form from the file's place to the new path;
  3. in a file that itself moved, every relative link is re-resolved from its OLD place and rewritten from its new one.
Bare basenames that resolve to nothing are left alone and listed for a hand look.

    python3 specs/329-unskill-the-repo/move_docs.py   (after the `git mv`s; reads MOVES below)
"""

from __future__ import annotations

import os
import re
import subprocess
import sys

MOVES = {
    "buildings.md": "docs/buildings.md",
    "buildings/programs.md": "docs/buildings/programs.md",
    "migration-plan.md": "docs/migration-plan.md",
    "timings.md": "dev/timings.md",
    "dev/skill-boundary.md": "docs/package-boundary.md",
    "dev/reviews.md": "docs/reviews.md",
    "dev/switches.md": "docs/switches.md",
}
BACK = {v: k for k, v in MOVES.items()}
EXEMPT = re.compile(r"^(specs/|scripts/fixtures/|dev/[a-z]+-log/|docs/review-ledger\.md$)")
# a path-like token: letters, digits, dots, dashes, slashes; ends in .md, optionally followed by an #anchor
TOKEN = re.compile(r"(?<![\w./-])((?:\.\./|\./)*[\w.-]+(?:/[\w.-]+)*\.md)(?=[#)\s`'\"\],;:|>]|$)")


def norm(p: str) -> str:
    return os.path.normpath(p).replace(os.sep, "/")


def rewrite(f: str, text: str) -> tuple[str, list[str]]:
    here_new = os.path.dirname(f)
    here_old = os.path.dirname(BACK.get(f, f))
    log: list[str] = []

    def sub(m: re.Match[str]) -> str:
        tok = m.group(1)
        # (1) a repo-relative mention
        if tok in MOVES:
            log.append(f"{f}: {tok} -> {MOVES[tok]}")
            return MOVES[tok]
        # (2)/(3) a relative token, resolved from where the file WAS
        target = norm(os.path.join(here_old, tok))
        new_target = MOVES.get(target, target)
        if target in MOVES or f in BACK:
            if not os.path.exists(new_target) and target not in MOVES:
                return tok  # does not resolve (a prose mention, or a path relative to something else): left alone
            rel = os.path.relpath(new_target, here_new or ".").replace(os.sep, "/")
            if rel != tok:
                log.append(f"{f}: {tok} -> {rel}")
            return rel
        return tok

    return TOKEN.sub(sub, text), log


def main() -> int:
    files = subprocess.run(["git", "ls-files", "-z"], capture_output=True, text=True, check=True).stdout.split("\0")
    out: list[str] = []
    for f in filter(None, files):
        if EXEMPT.match(f) or not os.path.isfile(f):
            continue
        try:
            text = open(f, encoding="utf-8").read()
        except UnicodeDecodeError:
            continue
        if ".md" not in text:
            continue
        new, log = rewrite(f, text)
        if new != text:
            open(f, "w", encoding="utf-8").write(new)
            out += log
    print("\n".join(out))
    print(f"move-docs: {len(out)} rewrite(s)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
