#!/usr/bin/env python3
"""Run a check, or replay its last PASS while nothing it reads has changed (feature 383, plan D2).

WHY (the GM 2026-10-12: *"if we made use of a caching layer, then I feel like it would not take nearly five seconds"*). The
record's build check (`make record CHECK=1`, 6.4 s) and the glossary's run at every push and every gate's preflight, and
nearly every push leaves their inputs untouched. What they read is measured, not guessed (specs/383 research R1): an audit
hook on `open` saw `research/`, the engine's glossary assets, the modules the build imports and the standard library. So a
pass is kept by the content of every file under the input trees (`record_cache.ResultMemo`), the code sha of the module run
and every project module it imports, and the interpreter's version, and replayed - its output and exit 0 - until one of
them changes. A FAILING run is never kept: a refusal is always computed afresh.

A miss runs the check IN THIS PROCESS when it is `python3 -m <module> ...`, and `--facts <module>:<attr>` hands that module
a per-file memo (`record_cache.FileFacts`) as `<attr>`, so a run that must rebuild still reuses each file's parse whose
content did not change (the record store's `MEMO`, a page's notes).

    memo_check.py <name> --inputs <tree> ... [--code <file> ...] [--facts <module>:<attr>] -- <command ...>
    memo_check.py record | glossary          the two presets (`PRESETS`), the Makefile's and the push's one statement

`L7R_CACHE_OFF=1` always runs the command, and keeps nothing.
"""

from __future__ import annotations

import contextlib
import importlib
import io
import runpy
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # the push runs this in the tree it is about to push
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "record"))
import record_cache  # noqa: E402


def _in_process(root: Path, module: str, args: list[str], facts: str) -> tuple[int, str, str]:
    """`python3 -m <module> <args>` in this interpreter, its output captured; with `facts`, the per-file memo installed."""
    memo = None
    if facts:
        mod_name, _, attr = facts.partition(":")
        target = importlib.import_module(mod_name)
        memo = record_cache.FileFacts(root, f"memo-{mod_name.rsplit('.', 1)[-1]}", Path(target.__file__ or ""))
        setattr(target, attr, memo)
    out, err, saved = io.StringIO(), io.StringIO(), sys.argv[:]
    sys.argv = [module, *args]
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                runpy.run_module(module, run_name="__main__", alter_sys=False)
                code = 0
            except SystemExit as stop:
                code = stop.code if isinstance(stop.code, int) else (0 if stop.code is None else 1)
                if stop.code is not None and not isinstance(stop.code, int):
                    print(stop.code, file=sys.stderr)
    finally:
        sys.argv = saved
        if memo is not None:
            memo.save()
    return code, out.getvalue(), err.getvalue()


def run(root: Path, name: str, inputs: list[str], command: list[str], code: list[Path] = (), facts: str = "") -> int:  # type: ignore[assignment]
    memo = record_cache.ResultMemo(root, name, inputs, Path(__file__), *code, argv=command)
    kept = memo.hit()
    if kept is not None:
        sys.stdout.write(kept[0])
        sys.stderr.write(kept[1])
        return 0
    if command[:2] in (["python3", "-m"], [sys.executable, "-m"]) and len(command) > 2:
        rc, out, err = _in_process(root, command[2], command[3:], facts)
    else:
        p = subprocess.run(command, cwd=root, capture_output=True, text=True, check=False)
        rc, out, err = p.returncode, p.stdout, p.stderr
    sys.stdout.write(out)
    sys.stderr.write(err)
    if rc == 0:
        memo.keep(out, err)
    return rc


#: the checks this runs by name - the ONE statement of what each reads, for the Makefile's CHECK branches and the push's runner
#: alike: (input trees, code, the per-file memo it is handed, the command). Measured in specs/383 research R1.
PRESETS: dict[str, tuple[list[str], list[str], str, list[str]]] = {
    "record": (["research", "l7r/diagram/interactive/assets"], ["l7r/diagram/tools/record_asset.py"], "l7r.diagram.interactive.record.store:MEMO",
               ["python3", "-m", "l7r.diagram.tools.record_asset", "--check"]),
    "glossary": (["research", "l7r/diagram/interactive/assets"], ["l7r/diagram/tools/glossary_asset.py"], "",
                 ["python3", "-m", "l7r.diagram.tools.glossary_asset", "--check"]),
}


def parse(args: list[str]) -> tuple[str, list[str], list[str], str, list[str]] | None:
    """(name, inputs, code, facts, command), or None when the arguments do not say all of name, inputs and command. A
    preset's name alone says all of them."""
    if len(args) == 1 and args[0] in PRESETS:
        return (args[0], *PRESETS[args[0]])
    if "--" not in args or not args or args[0].startswith("--"):
        return None
    cut = args.index("--")
    head, command = args[1:cut], args[cut + 1 :]
    lists: dict[str, list[str]] = {"--inputs": [], "--code": [], "--facts": []}
    current = None
    for a in head:
        if a in lists:
            current = a
        elif current is None:
            return None
        else:
            lists[current].append(a)
    if not lists["--inputs"] or not command or len(lists["--facts"]) > 1:
        return None
    return args[0], lists["--inputs"], lists["--code"], (lists["--facts"] or [""])[0], command


def main(argv: list[str] | None = None) -> int:
    parsed = parse(list(sys.argv[1:] if argv is None else argv))
    if parsed is None:
        print("usage: memo_check.py record|glossary, or <name> --inputs <tree> ... [--code <file> ...] [--facts <module>:<attr>] -- <command ...>", file=sys.stderr)
        return 2
    name, inputs, code, facts, command = parsed
    top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False).stdout.strip()
    root = Path(top or ".").resolve()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))  # `-m l7r...` run in this process resolves from the repository root, as python3 -m does
    return run(root, name, inputs, command, [root / c for c in code], facts)


if __name__ == "__main__":
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / "hooks" / "lib"))
    sys.dont_write_bytecode = True  # a record leaves no __pycache__ in the worktree (feature 406)
    import usage_log  # noqa: E402 - feature 406 T03 (D162): every refusing check records its run

    sys.exit(usage_log.exited("memo_check", main()))
