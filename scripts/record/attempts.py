#!/usr/bin/env python3
"""The attempts log: what each source was tried for, and what came of it (feature 312, FR-015 - FR-018).

WHY (the GM, 2026-10-02): *"it might make sense for efficiency purposes to have a separate file in which we record all of
the things that we have tried to use a source for. and found it wanting ... if we ever do another pass on a research topic,
then we can have a procedure by which we first check to see if we have tried to answer this specific question already using
this source"* - and the same for cited sources, *"because we do often cite the same source multiple times for multiple
different questions"*. The sources-consulted ledger (feature 288) records READS, host-local; this records ATTEMPTS, committed
beside the record: `research/source-attempts.jsonl`, one JSON line per attempt, union-merged (`.gitattributes`) so every
clone appends without a conflict.

A LINE: `{"url": <normalized>, "raw", "key", "question": NNNN | "old:<page>/<NNN>" | "unknown", "sought", "outcome",
"date", "feature", "route"}`. OUTCOMES (spec FR-015): `found`, `partial`, `not-found`, `not-applicable`, `unreadable`,
`unknown` - a read just begun is written `unknown`, and `make source-outcome` appends its outcome as a later line. What a cited source WAS used for is derived from its footnotes and
never copied here.

THE SEED (FR-016): every ledger row becomes a line - its question mapped to the current stem through `moved-303.json`, a
free-text "question" (the seed import of feature 288 kept the reading prompt there) taken as what was sought, an id that
cannot be mapped kept as `old:<id>`, none as `unknown`; what was sought, where nothing says, is
`unknown - recorded before feature 312` (the GM: *"it is of course okay in any case to mark that we don't know why something
was consulted originally"*).

WHAT IS LEFT HERE (feature 449 T145, phase 4's S2; the plan review's FR-003 ruling, ONE LIVE WRITER per shared file): the log's
commands are `l7r-gate record attempts ...`, the log the guard's `shared::attempts`. What stays is what `archive.py`, `uncited.py`
and `uncited_imports.py` still import until S3a and S3b port them: `base`, `read` and `today` (reads, `ask:449-T81-slices`);
`add`, the log's one write they make, a forwarder to `l7r-gate record attempts add` (`ask:449-T86-door`), so the Rust is the log's
one writer; and `write`, for the uncited filter's own lists (`not-kept.jsonl`, the kept and misfiled lists), which only that
Python writes - it refuses the attempts log itself. An edit of a read here makes the same change in the Rust.
"""

from __future__ import annotations

import datetime
import json
import os
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import sources as src  # noqa: E402

GATE = HERE.parent / "gates" / "l7r-gate.sh"
RESEARCH = pathlib.Path("research")
LOG = RESEARCH / "source-attempts.jsonl"
NOT_KEPT = RESEARCH / "not-kept.jsonl"
UNCITED = RESEARCH / "sources" / "040-uncited-works"
OUTCOMES = ("found", "partial", "not-found", "not-applicable", "unreadable", "unknown")


def base(root: pathlib.Path) -> pathlib.Path:
    """The tree whose `research/` holds the log: the clone, or `L7R_ATTEMPTS_ROOT` - the tests' seam, as
    `L7R_SOURCES_HOME` moves the ledger (`tests/tooling/conftest.py`); no session sets it."""
    return pathlib.Path(os.environ.get("L7R_ATTEMPTS_ROOT") or root)


def today() -> str:
    return datetime.date.today().isoformat()


def read(root: pathlib.Path, rel: pathlib.Path = LOG) -> list[dict]:
    path = base(root) / rel
    out = []
    for raw in path.read_text(encoding="utf-8").splitlines() if path.is_file() else []:
        try:
            out.append(json.loads(raw))
        except json.JSONDecodeError:
            continue
    return out


def write(root: pathlib.Path, lines: list[dict], rel: pathlib.Path) -> None:
    """Append to one of the uncited filter's own lists under the ledger's kind of lock: two agents of one session never
    interleave half lines. The attempts log is `add`'s, the Rust's one writer (feature 449 T145)."""
    if rel == LOG:
        raise ValueError("the attempts log is written by `add` (l7r-gate record attempts add), its one writer")
    if not lines:
        return
    for line in lines:
        src._blocked().check(line.get("raw") or line["url"], "the attempts log")
    path = base(root) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    with src.locked(src.home(root), timeout=30.0), open(path, "a", encoding="utf-8") as fh:
        fh.writelines(json.dumps(x, ensure_ascii=False) + "\n" for x in lines)


def add(root: pathlib.Path, url: str, question: str, sought: str, outcome: str = "unknown", *, route: str = "", key: str = "") -> dict:
    """One attempt on the log, through the Rust, its one writer (`l7r-gate record attempts add`, feature 449 T145): the line
    written, as the log holds it."""
    if outcome not in OUTCOMES:
        raise ValueError(f"outcome {outcome!r} is not one of {', '.join(OUTCOMES)}")
    cmd = [str(GATE), "record", "attempts", "add", "--root", os.path.abspath(root), "--url", url, "--q", question or "unknown",
           "--sought", sought, "--outcome", outcome, "--route", route, "--key", key, "--print"]
    done = subprocess.run(cmd, capture_output=True, text=True, cwd=HERE, check=False)
    if done.returncode:
        raise src.raised(done.stderr)
    return json.loads(done.stdout)
