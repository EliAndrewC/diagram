#!/usr/bin/env python3
"""The push's Python checks, run in ONE interpreter (feature 383, plan D8 and D9).

WHY (the GM 2026-10-12: *"Although I agree that the combining all the different checks into one is lower impact, it does
still seem worth doing"*). `sync-with-main.sh`'s push ran about 35 Python processes in a row, each paying an interpreter's
start and its imports again. Here each check runs as it would alone - `runpy.run_path(script, run_name="__main__")` with its
own `sys.argv`, its `SystemExit` caught - so its output and its exit are what `python3 <script> <args>` gives, and the
first refusal prints the line the shell's `die` printed and ends the run with exit 1.

A SELF-TEST RUNS ONCE PER VERSION OF ITS CODE (FR-007): a passing self-test is kept under the code sha of its script and every
project module the script imports (`record_cache.code_sha_of`), and skipped while that is unchanged. A failing one is never
kept; `L7R_CACHE_OFF=1` runs them all.

    push_checks.py <root> [--skip <name> ...] [--list]

Left to the shell, each for the reason at its call: the shell gates (`entry-gate.sh`, `claims-gate.sh`, `review-gate.sh`,
`plan-gate.sh`), which are no Python checks; and the steps after the fetch whose answers the shell's own branches read (the
features in progress, the closing check, the performance flag, the remote merge).
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import runpy
import sys
import traceback
from pathlib import Path

sys.dont_write_bytecode = True  # the push runs this in the tree it is about to push

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "record"))
import record_cache  # noqa: E402

#: (name, script relative to scripts/, arguments - `{root}` is the clone -, the refusal `die` printed, is it a self-test, the
#: path under the clone it needs: a check of something the tree does not hold is not run, as the shell's `if [ -d ... ]` did)
CHECKS: tuple[tuple[str, str, tuple[str, ...], str, bool, str], ...] = (
    ("duplicate-defs selftest", "gates/check-duplicate-defs.py", ("--selftest",), "check-duplicate-defs selftest failed - the guard itself is broken; fix scripts/gates/check-duplicate-defs.py before pushing", True, ""),
    ("duplicate-defs", "gates/check-duplicate-defs.py", ("{root}",), "duplicate top-level definitions (above) - a later def silently shadows the earlier; fix before pushing", False, ""),
    ("file-scale selftest", "gates/check-file-scale.py", ("--selftest",), "check-file-scale selftest failed - the guard itself is broken; fix scripts/gates/check-file-scale.py before pushing", True, ""),
    ("stale-dirs selftest", "gates/check-stale-dirs.py", ("--selftest",), "check-stale-dirs selftest failed - the guard itself is broken; fix scripts/gates/check-stale-dirs.py before pushing", True, ""),
    ("stale-dirs", "gates/check-stale-dirs.py", ("{root}",), "a directory in an importable tree has nothing left but __pycache__ (above) - it is still an importable namespace package, so this clone passes what a fresh clone fails", False, ""),
    ("file-scale", "gates/check-file-scale.py", ("{root}",), "a Python file is past the ~1,000-line bar (above) - constitution Principle X clause 13, gated since feature 173", False, ""),
    ("function-cap selftest", "gates/check-function-cap.py", ("--selftest",), "check-function-cap selftest failed - fix scripts/gates/check-function-cap.py before pushing", True, ""),
    ("function-cap", "gates/check-function-cap.py", ("{root}",), "a function is past the 100-statement cap, or a suppression of it says not why (above) - feature 370", False, ""),
    # feature 385 amendment 5 (FR-017): the gate's test_make_docs, on every route - T13 landed a target by the direct route, which
    # runs no gate, and the stale page failed T16's land-tooling a task later
    ("make-docs", "make-docs.py", ("{root}", "--check"), "docs/make-targets.html is stale against the Makefile (above) - run `make docs` and commit the page; feature 385 FR-017", False, "docs/make-targets.html"),
    ("ledger-owed", "reviews/ledger_owed.py", ("--ledger", "{root}/dev/review-ledger.md", "--refuse"), "a check's pass has no row in dev/review-ledger.md (above) - write each from its reply: make ledger-owed WRITE=\"<where you recorded what you did>\" (or add the row printed, its ?s filled); features 371, 385 FR-019", False, ""),
    ("entry-headings selftest", "gates/check-entry-headings.py", ("--selftest",), "check-entry-headings selftest failed - the guard itself is broken; fix scripts/gates/check-entry-headings.py before pushing", True, ""),
    ("entry-headings", "gates/check-entry-headings.py", ("{root}",), "a class entry names a research heading that no longer resolves (above) - a rename owes its inbound links, feature 234", False, ""),
    ("research-pointers selftest", "gates/check-research-pointers.py", ("--selftest",), "check-research-pointers selftest failed - the guard itself is broken; fix scripts/gates/check-research-pointers.py before pushing", True, ""),
    ("research-pointers", "gates/check-research-pointers.py", ("{root}",), "a pointer to the research does not resolve, or names a built page (above) - feature 301; `make fragment-move` moves a fragment with its pointers", False, ""),
    ("partial-citations", "gates/check-partial-citations.py", ("{root}",), "a footnote cites a source no one can wholly read with no confirmed passage (above) - feature 312 FR-020; confirm the passage (quote-check) and record it in research/partial-confirmations.jsonl, or make the note an absence note", False, ""),
    ("downloads selftest", "record/downloads.py", ("selftest",), "the download-list check's selftest failed - the guard itself is broken; fix scripts/record/downloads.py before pushing", True, ""),
    ("downloads", "record/downloads.py", ("check",), "the canonical download list is not append-only against main (above) - feature 313; `make download-add FILE=<draft.md>` appends an entry", False, ""),
    ("spec-lint selftest", "gates/spec-lint.py", ("--selftest",), "spec-lint selftest failed - the guard itself is broken; fix scripts/gates/spec-lint.py before pushing", True, ""),
    ("spec-lint", "gates/spec-lint.py", ("--delta", "{root}"), "spec-lint found something a review round would otherwise spend itself on (above) - feature 236, the GM: mistakes caught early and cheaply", False, ""),
    ("speckit-todo check", "speckit-todo.py", ("--root", "{root}", "--check"), "an open feature does not say what it affects (above): add its **Affects** line - make speckit-todo CHECK=1 re-checks", False, ""),
    ("conflict selftest", "hooks/lib/hm_conflict.py", ("--selftest",), "_hm_conflict selftest failed - the guard itself is broken; fix scripts/hooks/lib/hm_conflict.py before pushing", True, ""),
    ("conflict", "hooks/lib/hm_conflict.py", ("--tracked", "{root}"), "a tracked file still carries an unresolved merge conflict (above) - the history here is never rewritten, so resolve it before it lands, feature 241", False, ""),
    # the record's build and the glossary - the presets `make record CHECK=1` and `make glossary CHECK=1` run (memo_check.py)
    ("record", "gates/memo_check.py", ("record",), "the record does not build cleanly (above; `make record CHECK=1` at the repository root names each refusal) - features 258 and 301", False, "research/sources"),
    ("glossary", "gates/memo_check.py", ("glossary",), "the committed glossary differs from its per-term files (run `make glossary` at the repository root, then commit) - feature 259, spec FR-006", False, "research/sources"),
    # the green-gate guard; under GATE_STAMP_OK the shell logs the escape and passes `--skip gate-stamp selftest --skip gate-stamp`
    ("gate-stamp selftest", "gates/gate-stamp.py", ("--selftest",), "gate-stamp selftest failed - the guard itself is broken; fix scripts/gates/gate-stamp.py before pushing", True, ""),
    ("gate-stamp", "gates/gate-stamp.py", ("--check", "origin/main"), "push refused by the green-gate guard (above)", False, ""),
    # a touched feature that reads closed carries its report and its carried keys (feature 375 FR-009/FR-014); under a CLOSE_OK
    # with its reason the shell logs the escape and passes `--skip closing`
    ("closing", "gates/close_check.py", ("--push", "origin/main...HEAD"), "REFUSED: a feature this push closes owes what closing owes (feature 375) - the reasons above; a case that is genuinely exempt: CLOSE_OK=\"<reason>\" (recorded)", False, ""),
)
#: a refusal the guard log records, as the shell recorded it (`guard_log sync-with-main blocked <what> <rule>`)
LOGGED = {"closing": ("closing", "closing-owes")}
STAMPS = "selftests.json"


def run_one(script: Path, args: list[str], cwd: Path, quiet: bool = False) -> int:
    """`python3 <script> <args>` in this interpreter: its exit status, its output where it would go (stdout dropped when
    `quiet`, as the shell's `>/dev/null`). The working directory, `sys.argv` and `sys.path` are put back after."""
    saved_argv, saved_path, here = sys.argv[:], sys.path[:], os.getcwd()
    sys.argv = [str(script), *args]
    sys.path.insert(0, str(script.parent))
    sink = contextlib.redirect_stdout(io.StringIO()) if quiet else contextlib.nullcontext()
    try:
        os.chdir(cwd)
        with sink:
            runpy.run_path(str(script), run_name="__main__")
        code = 0
    except SystemExit as stop:
        code = stop.code if isinstance(stop.code, int) else (0 if stop.code is None else 1)
        if stop.code is not None and not isinstance(stop.code, int):
            print(stop.code, file=sys.stderr)
    except Exception:  # noqa: BLE001 - a crashing check refuses, as its process's traceback and exit 1 did
        traceback.print_exc()
        code = 1
    finally:
        os.chdir(here)
        sys.argv, sys.path[:] = saved_argv, saved_path
        sys.stdout.flush()
        sys.stderr.flush()
    return code


def _guard_log(what: str, rule: str) -> None:
    """The firing, recorded by the guard log's one writer (`hooks/lib/guardlog.sh`), as the shell's own call did."""
    import subprocess  # noqa: PLC0415

    lib = HERE.parent / "hooks" / "lib" / "guardlog.sh"
    subprocess.run(["bash", "-c", '. "$0" && guard_log sync-with-main blocked "$1" "$2"', str(lib), what, rule], check=False, capture_output=True)


def _stamps_file(root: Path) -> Path | None:
    d = None if record_cache.off() else record_cache.common_dir(root)
    return d / record_cache.CACHE_DIR / STAMPS if d is not None else None


def _load_stamps(path: Path | None) -> dict[str, str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8")) if path is not None and path.is_file() else {}
    except (OSError, ValueError):
        data = {}
    return data if isinstance(data, dict) else {}


def run(root: Path, skip: set[str]) -> int:
    scripts = HERE.parent
    stamps_at = _stamps_file(root)
    stamps, changed = _load_stamps(stamps_at), False
    for name, rel, argv, refusal, selftest, needs in CHECKS:
        if name in skip or (needs and not (root / needs).exists()):
            continue
        script = scripts / rel
        version = record_cache.code_sha_of(scripts.parent, script) if selftest else ""
        if selftest and stamps.get(rel) == version:
            continue  # FR-007: passed on this version of its code and every module it imports
        code = run_one(script, [a.replace("{root}", str(root)) for a in argv], root, quiet=selftest)
        if code != 0:
            print(f"sync-with-main: {refusal}", file=sys.stderr)
            if name in LOGGED:
                _guard_log(*LOGGED[name])
            return 1
        if selftest:
            stamps[rel], changed = version, True
    if changed and stamps_at is not None:
        try:
            stamps_at.parent.mkdir(parents=True, exist_ok=True)
            tmp = stamps_at.with_suffix(f".{os.getpid()}.tmp")
            tmp.write_text(json.dumps(stamps, indent=1) + "\n", encoding="utf-8")
            tmp.replace(stamps_at)
        except OSError:
            pass  # an unwritten stamp costs the next push a self-test, never a check
    return 0


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args[:1] == ["--list"]:
        for name, *_ in CHECKS:
            print(name)
        return 0
    if not args:
        print("usage: push_checks.py <root> [--skip <name> ...] [--list]", file=sys.stderr)
        return 2
    root, skip, rest = Path(args[0]).resolve(), set(), args[1:]
    while rest:
        if rest[0] == "--skip" and len(rest) > 1:
            skip.add(rest[1])
            rest = rest[2:]
        else:
            print(f"push_checks: unknown argument {rest[0]!r}", file=sys.stderr)
            return 2
    unknown = skip - {c[0] for c in CHECKS}
    if unknown:
        print(f"push_checks: no check named {', '.join(sorted(unknown))} (--list names them)", file=sys.stderr)
        return 2
    return run(root, skip)


if __name__ == "__main__":
    sys.exit(main())
