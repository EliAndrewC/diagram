#!/usr/bin/env python3
"""Fail when a live file names the project's old location (feature 329, FR-007).

WHY. Feature 329 moved the project from the skill directory under `.claude/skills/` to the repository root. A pointer
to the old place is a pointer to nothing - and the clones that were mid-feature when it landed carry commits written
against it, so the old prefix will keep arriving for a while after the move. This check turns each arrival into a
refusal naming the new path, at the gate (`make static`) and at the push (`sync-with-main.sh`).

LIVE is every tracked file except the verbatim records, which quote what happened and are not rewritten: the feature
history `specs/`, the recorded commands the hook suite replays (`scripts/fixtures/`), the run, perf, idle and bypass
records (`dev/*-log/`), and the review ledger's rows written before this check existed - LINE BY LINE (plan review
round 1): a ledger line naming the old path passes only if it stands verbatim in the ledger at the commit that added
this file, so a row written after the move is held like any other line. Run `--selftest` first (the Makefile does).

    check-old-layout.py [<repo root>]    # default: the current directory
    check-old-layout.py --selftest
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

OLD = ".claude/skills/" + "diagram"  # split so this file is not its own finding
EXEMPT = re.compile(r"^(specs/|scripts/fixtures/|dev/[a-z]+-log/|scripts/check-old-layout\.py$)")  # the last: it names the forms it looks for
LEDGER = "docs/review-ledger.md"


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True).stdout


def old_ledger_lines(root: Path) -> set[str]:
    """The ledger as of the commit that added this check (HEAD's, before that commit exists)."""
    added = _git(root, "log", "--diff-filter=A", "--format=%H", "--", "scripts/check-old-layout.py").split()
    ref = added[-1] if added else "HEAD"
    return set(_git(root, "show", f"{ref}:{LEDGER}").splitlines())


# The path as code also spells it: split into Path or os.path.join parts, or with its dots escaped in a regex. Each one
# was found in the tree the day this check was written, past the literal search.
FORMS = (re.escape(OLD), r'"\.claude",\s*"skills",\s*"diagram"', r'"\.claude"\s*/\s*"skills"\s*/\s*"diagram"', r"\\\.claude/skills/diagram")


def findings(root: Path) -> list[str]:
    out = _git(root, "grep", "-n", "-I", "-P", "|".join(FORMS), "--", ".")
    old_rows: set[str] | None = None
    rows = []
    for line in out.splitlines():
        path, _, rest = line.partition(":")
        if EXEMPT.match(path):
            continue
        if path == LEDGER:
            if old_rows is None:
                old_rows = old_ledger_lines(root)
            if rest.partition(":")[2] in old_rows:
                continue
        rows.append(line)
    return rows


def report(rows: list[str]) -> int:
    if not rows:
        return 0
    print(f"OLD LAYOUT: {len(rows)} line(s) name {OLD}/, which feature 329 moved to the repository root.")
    print(f"Drop the prefix - `{OLD}/dev/loop.md` is now `dev/loop.md`, and a command that cd'd there runs at the root:")
    for r in rows[:40]:
        path, rest = r.split(":", 1)
        print(f"  {path}:{rest[:200].replace(OLD + '/', '')}")
    if len(rows) > 40:
        print(f"  ... and {len(rows) - 40} more")
    return 1


def selftest() -> int:
    with tempfile.TemporaryDirectory() as t:
        root = Path(t)
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        (root / "docs").mkdir()
        (root / "specs" / "001-x").mkdir(parents=True)
        (root / "docs" / "a.md").write_text(f"see {OLD}/dev/loop.md\n")
        (root / "docs" / "b.py").write_text('R = os.path.join(".claude", "skills", "diag' + 'ram", "research")\n')
        (root / "specs" / "001-x" / "plan.md").write_text(f"history: {OLD}/dev/loop.md\n")
        (root / LEDGER).write_text(f"| old row | {OLD}/pool |\n")
        subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(root), "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "a"], check=True)
        with (root / LEDGER).open("a") as f:
            f.write(f"| new row | {OLD}/dev |\n")
        subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
        rows = findings(root)
        got = sorted((r.split(":", 1)[0], "new row" in r) for r in rows)
        if got != [("docs/a.md", False), ("docs/b.py", False), (LEDGER, True)]:
            print(f"selftest: expected docs/a.md and the NEW ledger row only, got {rows}")
            return 1
    print("check-old-layout selftest: ok")
    return 0


def main(argv: list[str]) -> int:
    if argv[1:2] == ["--selftest"]:
        return selftest()
    root = Path(argv[1]) if len(argv) > 1 else Path(".")
    return report(findings(root))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
