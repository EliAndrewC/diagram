#!/usr/bin/env python3
"""A coordination file read and written by line - `make lines` and `make append` (feature 274 D5, FR-002).

    coord.py lines <file> <regex>     the matching lines, numbered, at most MAX, then how many were shown of how many
    coord.py append <file>            appends $LINE as one line (the file made if needed); prints only where

WHY (feature 274, research R1). The research sessions re-read their coordination files whole: 619 reads of the
cross-session claims file across 172 sessions (about 30 M tokens carried), 418 of a group's handoff across 254 sessions
(about 20 M, though the briefs said "read only your own lines") and 388 of a checks report across 183 sessions (about
12 M), mostly to append one line - about 60 M in all, 5%. Every read stays in the session's context and is paid for
again on every later turn. So a session reads only its own lines and appends without reading.

The line to append comes from the ENVIRONMENT (`make` exports its command-line variables to the recipe), not from an
argument pasted into the recipe, so quotes and `$` in it survive. A relative FILE is taken from the directory `make`
ran in, else from the repository root, so the same command works from the clone root or the skill directory.
"""

from __future__ import annotations

import os
import pathlib
import re
import subprocess
import sys

MAX = 80  # lines shown at most: a KEY that matches more is too wide, and the count says so
#: the gate's wrapper, which lints a ledger row and costs a review (`l7r-gate reviews ledger-lint`, `review-cost`, feature 449 T83)
GATE = pathlib.Path(__file__).resolve().parents[1] / "gates" / "l7r-gate.sh"
#: the review ledger's measured table, whose rows the lint judges
MEASURED_HEADING = "## Review checks, measured (feature 294 on)"


def resolve(name: str, cwd: pathlib.Path | None = None) -> pathlib.Path:
    """FILE as given: absolute; else under the directory make ran in if it (or its parent directory) is there; else
    under the repository root."""
    p = pathlib.Path(name)
    if p.is_absolute():
        return p
    here = (cwd or pathlib.Path.cwd()) / p
    if here.exists() or here.parent.is_dir():
        return here
    top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=cwd, capture_output=True, text=True, check=False).stdout.strip()
    return pathlib.Path(top) / p if top else here


def lines(path: pathlib.Path, key: str) -> list[str]:
    """The output of `make lines`: each matching line as `<number>: <text>`, then the count line."""
    text = path.read_text(encoding="utf-8", errors="replace").splitlines()
    rx = re.compile(key)
    hits = [f"{n}: {ln}" for n, ln in enumerate(text, 1) if rx.search(ln)]
    out = hits[:MAX] + [f"({min(len(hits), MAX)} of {len(text)} lines shown)"]
    if len(hits) > MAX:
        out.append(f"({len(hits) - MAX} more matched - narrow KEY)")
    return out


def append(path: pathlib.Path, line: str) -> None:
    """Append ONE line, never reading the file; a newline first only if the file does not already end with one."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "ab+") as fh:
        fh.seek(0, os.SEEK_END)
        lead = b""
        if fh.tell():
            fh.seek(-1, os.SEEK_END)
            lead = b"" if fh.read(1) == b"\n" else b"\n"
        fh.write(lead + line.rstrip("\n").encode("utf-8") + b"\n")


def ledger_row_problems(path: pathlib.Path, line: str) -> list[str]:
    """A review-ledger row judged by the ledger's own lint BEFORE it is appended (feature 383 amendment 2, a defect found on the
    way: `make append ... && git commit` in one command had the commit's ledger hook judge the ledger before the row existed,
    so a row with a wrong class word was committed and only a tooling test caught it). Any other file: nothing to judge."""
    if path.name != "review-ledger.md" or path.parent.name != "dev":
        return []
    import tempfile  # noqa: PLC0415

    # the one lint is the gate's `reviews ledger-lint` since feature 449 T83 (`ask:449-T83-scope`): the row is judged under the measured
    # table's heading in a scratch file, as `ledger_lint.problems` judged it in memory
    with tempfile.NamedTemporaryFile("w", suffix=".md", encoding="utf-8", delete=False) as fh:
        fh.write(f"{MEASURED_HEADING}\n{line}\n")
    try:
        out = subprocess.run([str(GATE), "reviews", "ledger-lint", fh.name], capture_output=True, text=True, check=False)
    finally:
        os.unlink(fh.name)
    return [p.split(": ", 1)[-1] for p in out.stdout.splitlines()]


def with_cost(line: str, cells: str) -> str:
    """A ledger row closed with its cost cells: `line` (its cells up to `acted on`) then `wall | tokens |`."""
    head = line.rstrip()
    return f"{head}{'' if head.endswith('|') else ' |'} {cells} |"


def agent_cells(agent: str) -> str:
    """The latest return's cost cells of review agent `agent`, from `l7r-gate reviews review-cost --last` (`review_cost.py`'s port,
    feature 449 T83) - the one place they are read.

    WHY (the round arbiter on hour:374-match-the-research-continued@1): a session composing the cells through a shell variable
    (`C=$(make review-cost ...)`, then `LINE="... $C |"`) had its row judged by the ledger hook before the shell expanded it -
    about fourteen refusals in a window, one taking the reply file written before it down too."""
    out = subprocess.run([str(GATE), "reviews", "review-cost", "--agent", agent, "--last"], capture_output=True, text=True, check=False)
    if out.returncode != 0 or not out.stdout.strip():
        raise ValueError(out.stderr.strip() or f"no cost for agent {agent}")
    return out.stdout.strip().splitlines()[-1]


def main(argv: list[str], env: dict[str, str] | None = None) -> int:
    env = dict(os.environ) if env is None else env
    if len(argv) == 3 and argv[0] == "lines":
        path = resolve(argv[1])
        if not path.is_file():
            print(f"make lines: no file {path}", file=sys.stderr)
            return 2
        try:
            print("\n".join(lines(path, argv[2])))
        except re.error as e:
            print(f"make lines: KEY is not a regular expression - {e}", file=sys.stderr)
            return 2
        return 0
    if len(argv) == 2 and argv[0] == "append":
        line = env.get("LINE", "")
        if not line.strip() or "\n" in line.strip("\n"):
            print("make append: LINE=<text> is required, and it is ONE line", file=sys.stderr)
            return 2
        path = resolve(argv[1])
        if env.get("AGENT"):  # `make append ... AGENT=<id>`: the row's cost cells filled from the agent's own transcript
            try:
                line = with_cost(line, agent_cells(env["AGENT"]))
            except ValueError as e:
                print(f"make append: AGENT={env['AGENT']} - {e}", file=sys.stderr)
                return 2
        bad = ledger_row_problems(path, line)
        if bad:
            print("make append: the ledger row was NOT appended - " + "; ".join(bad), file=sys.stderr)
            return 2
        append(path, line)
        print(f"appended to {path}")
        return 0
    print("usage: coord.py lines <file> <regex> | coord.py append <file>  (the line in $LINE)", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
