#!/usr/bin/env python3
"""Fail when a Python file has grown past ~1,000 raw lines without a written justification.

WHY (GM 2026-08-31, feature 173): *"This project has a set of guidelines that revolve around not
letting files grow too large, but it looks like we have allowed that to drift ... if any of them are
too large, which is to say over one thousand lines of code, then we fail the gate with a message
that explains that the clone responsible for this work must split up the file in the manner
prescribed in our project guidelines."* Ten files were over the bar when they asked, one of them at
4,369 lines. The rule is constitution Principle X clause 13 and it has existed since 2026-08-15;
what did not exist was anything that stopped a file crossing it, because - by the clause's own
design - no single edit crosses the line, so the line has to be CHECKED rather than felt.

This closes half of the constitution's own v1.6.1 deferred TODO: *"Automated file-length check
(flags source files past the threshold lacking a justification header)"*. The other half, clause
12's expression-counting check on FUNCTIONS, is still owed and is deliberately not attempted here.

RAW LINES, deliberately - clause 13 says so, "deliberately unlike clause 12's logic units - because
the motivating cost is token economy: a session that needs one function from a file pays
context-window tokens for the whole file, and that cost scales with text, not logic". Blank lines,
comments and docstrings all count, which is also what the GM's own `nl -b a` census counted.

THE JUSTIFICATION HEADER (clause 13's ordered-data carve-out, which survives): a file may stay large
if it is one cohesive ordered dataset whose row order IS the execution contract. It says so in its
own first 40 lines, with `FILE_SIZE_OK:` and a reason of at least 40 characters - a file-level
exemption is argued, not tokenized (feature 170: an escape must say why; that guard's floor is eight
characters, and a whole-file exemption deserves a sentence). `--list` prints every file taking it, so
the carve-outs stay enumerable; a carve-out nobody can count is a carve-out nobody revisits.

Note what this canNOT check: whether the file really IS ordered data. No character count tests that.
What holds the line is that the reason is in the file, in git history, and in `make audit`.

Scanned: every tracked `*.py` in the repository except the four exclusions in SKIP_PARTS -
`legacy-hand-authored-pool/` (frozen write-once exhibits, already outside ruff, coverage and every
re-run since feature 161 - three of them are over the bar and must stay untouched), `.clones/`
(other sessions' trees, which this one does not judge), `specs/` (the feature record, including
fourteen retired one-shot splitters kept as history - a record of past work is not code a session
loads), and `.git`/`__pycache__`.

Run `--selftest` first (the Makefile's `lint` and sync-with-main.sh both do): it plants an oversize
file and verifies the checker fires, plants a justified one and verifies it passes, and plants one
whose marker carries no real reason and verifies THAT fires - a checker that cannot prove it still
bites is the failure mode the whole guard exists to prevent. A run that scans ZERO files also fails
loudly, for the reason check-duplicate-defs.py records: wrong root beats silent success.

Invoked by: the diagram Makefile's `lint` phase (which `make done` runs first, so an oversize file
is reported before the map roll is paid for) and scripts/sync-with-main.sh before EVERY push - the
push guard is the point, because a docs-or-tests-only delta takes the DIRECT route and never runs a
gate at all.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

MAX_LINES = 1000
MARKER = "FILE_SIZE_OK:"
MIN_REASON = 40
HEADER_LINES = 40
SKIP_PARTS = {"legacy-hand-authored-pool", ".clones", "specs", ".git", "__pycache__", "node_modules"}

GUIDANCE = f"""
  Each file above is past the ~{MAX_LINES:,}-line bar of constitution Principle X clause 13. The clone
  doing this work splits it before the work can merge - that is the rule the GM gated on
  2026-08-31, and it is not deferrable to a later pass.

  THE PRESCRIBED SHAPE: the file becomes a DIRECTORY-MODULE - `hamletgen/ways.py` becomes
  `hamletgen/ways/` with sub-modules - carrying a CLAUDE.md that indexes them with a
  "look here when" line each, so a future session loads only the part it needs.

  Read, in this order:
    - .specify/memory/constitution.md, Principle X clause 13 (the rule and both carve-outs)
    - CLAUDE.md, "Files stay at human scale" (the operational mirror)
    - .claude/skills/diagram/l7r/diagram/settlement/structures/ - a worked exemplar: its
      __init__.py composes the sub-mixins back into the one class its caller imports, and its
      CLAUDE.md is the index format. Seventeen more packages in this tree follow it.

  TWO CARVE-OUTS, before you split:
    - ORDERED DATA (clause 13): one cohesive ordered dataset whose row order IS the execution
      contract may stay large - say so in the first {HEADER_LINES} lines with `{MARKER} <reason>`,
      at least {MIN_REASON} characters. `make audit` lists every file that takes this.
    - A DERIVED ROSTER (clause 14): if the bulk restates what code elsewhere already declares,
      splitting is the WRONG fix - duplicated information does not shrink by being divided.
      Derive the surface instead (feature 027 took 3,148 lines to 63 that way).
"""


def raw_lines(path: Path) -> int:
    """Raw lines, counted as `wc -l` and `nl -b a` count them - which is what clause 13 means."""
    with path.open("rb") as fh:
        return sum(1 for _ in fh)


def justification(path: Path) -> str | None:
    """The stated reason from a `FILE_SIZE_OK:` marker in the file's first lines, if there is one."""
    with path.open(encoding="utf-8", errors="replace") as fh:
        for i, line in enumerate(fh):
            if i >= HEADER_LINES:
                break
            if MARKER in line:
                return line.split(MARKER, 1)[1].strip()
    return None


def scan(root: str = ".") -> list[Path]:
    """Every candidate `.py` under root - tracked files when this is a git tree, else a walk.

    Asking git is what honors "any path already ignored by git" without a per-file call: one
    `ls-files` names exactly the tracked set. The walk is the fallback the selftest runs on, since
    a temp directory is not a repository.
    """
    base = Path(root)
    try:
        out = subprocess.run(
            # --cached AND --others --exclude-standard: tracked files PLUS untracked ones git is
            # not ignoring, which is exactly "every file in the tree that is not gitignored". Two
            # halves matter: a file split into a package mid-feature is untracked until `git add`,
            # and a file DELETED but not yet committed is still --cached while gone from disk -
            # hence the is_file() filter, without which the first run inside this very feature's
            # clone died on its own half-finished split.
            ["git", "-C", str(base), "ls-files", "-z", "--cached", "--others", "--exclude-standard", "*.py"],
            capture_output=True, text=True, check=True, timeout=30,
        ).stdout
        paths = [base / p for p in out.split("\0") if p]
    except (subprocess.SubprocessError, OSError):
        paths = sorted(base.rglob("*.py"))
    seen = set()
    return sorted(
        p for p in paths
        if p.is_file()
        and not SKIP_PARTS.intersection(p.relative_to(base).parts)
        and not (p in seen or seen.add(p))
    )


def run(root: str = ".") -> tuple[list[tuple[Path, int]], list[tuple[Path, int, str]], int]:
    """(over the bar, justified, scanned) - the two lists are disjoint and both are reportable."""
    over: list[tuple[Path, int]] = []
    justified: list[tuple[Path, int, str]] = []
    scanned = 0
    for p in scan(root):
        scanned += 1
        n = raw_lines(p)
        if n <= MAX_LINES:
            continue
        reason = justification(p)
        if reason is not None and len(reason) >= MIN_REASON:
            justified.append((p, n, reason))
        else:
            over.append((p, n))
    return over, justified, scanned


def selftest() -> int:
    """Prove the checker bites: oversize fires, justified passes, a token without a reason fires."""
    import tempfile

    body = "x = 1\n"
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "big.py").write_text(body * (MAX_LINES + 1))
        (d / "edge.py").write_text(body * MAX_LINES)   # exactly at the bar PASSES
        (d / "ok.py").write_text(
            f"# {MARKER} an ordered registry whose row order is the execution contract\n"
            + body * (MAX_LINES + 1)
        )
        (d / "thin.py").write_text(f"# {MARKER} ordered\n" + body * (MAX_LINES + 1))
        (d / "late.py").write_text(   # the marker must be in the HEADER, not buried
            body * (HEADER_LINES + 1) + f"# {MARKER} an ordered registry whose rows are the contract\n" + body * MAX_LINES
        )
        over, justified, scanned = run(str(d))
        names = sorted(p.name for p, _ in over)
        if names != ["big.py", "late.py", "thin.py"] or len(justified) != 1 or scanned != 5:
            print(
                "check-file-scale SELFTEST FAILED: expected big/late/thin over the bar, ok.py "
                f"justified and edge.py passing over 5 files; got {names}, "
                f"{[p.name for p, _, _ in justified]} over {scanned}",
                file=sys.stderr,
            )
            return 1
    print("check-file-scale: selftest ok (oversize fires, a justified file passes, a bare marker fires)")
    return 0


def main(argv: list[str]) -> int:
    if argv and argv[0] == "--selftest":
        return selftest()
    listing = bool(argv) and argv[0] == "--list"
    root = argv[1] if listing and len(argv) > 1 else (argv[0] if argv and not listing else ".")
    over, justified, scanned = run(root)
    if listing:
        for p, n in sorted(over, key=lambda r: -r[1]):
            print(f"  {n:5d}  {p}")
        for p, n, why in sorted(justified, key=lambda r: -r[1]):
            print(f"  {n:5d}  {p}   JUSTIFIED: {why}")
        if not over and not justified:
            print(f"  every one of {scanned} Python files is at or under {MAX_LINES:,} lines")
        return 0
    if scanned == 0:
        print(
            f"check-file-scale: scanned ZERO files under {root!r} - wrong root? failing loudly",
            file=sys.stderr,
        )
        return 1
    if over:
        print(f"\ncheck-file-scale: {len(over)} file(s) past the {MAX_LINES:,}-line bar\n", file=sys.stderr)
        for p, n in sorted(over, key=lambda r: -r[1]):
            print(f"  {n:5d} lines ({n - MAX_LINES:+d})  {p}", file=sys.stderr)
        print(GUIDANCE, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
