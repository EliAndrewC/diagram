#!/usr/bin/env python3
"""No tool without its record (feature 406 T05, FR-004, D164).

WHY (the GM 2026-10-19, feature 406's request): "there should at least be a way that it is notionally possible for us to see
how often a tool is used, right? Or how often it makes a difference". `make tool-yield` reads what each tool leaves behind; a
tool added later that leaves nothing would sit in its table as a blank row forever. This check, run by `make hooks-test`,
refuses that tool before it lands:

    a wired hook, or a refusing check (the set `tool_yield.check_paths` lists), whose file neither calls `guard_log` or the
        usage-log helper nor carries `# TOOL_RECORD: <where its runs are seen>`;
    a usage-log call naming a tool `scripts/tool-registry.json` lacks;
    a registry entry no code calls.

    check-tool-signals.py [--root <repo>]      exit 0 clean, 1 with each finding and its fix
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "measure"))
sys.dont_write_bytecode = True  # leaves no __pycache__ in the worktree
import tool_yield  # noqa: E402

RECORDS = ("guard_log", "usage_log", "# TOOL_RECORD:")
CALLS = (
    re.compile(r'\bexited\(\s*"([\w-]+)"'),  # usage_log.exited("<tool>", ...)
    re.compile(r'usage_log\.record\([^\n]*?,\s*"([\w-]+)"'),  # usage_log.record(root, "<tool>", ...) on one line
    re.compile(r'--tool[ =]"?([\w-]+)'),  # usage_log.py record --tool <tool>
)


def _text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def unrecorded(root: Path) -> list[str]:
    """The hooks and checks that leave no record, each with its fix."""
    out = []
    hooks = {root / "scripts" / "hooks" / f"{name}-hooks.sh" for name in tool_yield.hook_guards(root)}
    for path in sorted(hooks | tool_yield.check_paths(root)):
        if path.is_file() and not any(mark in _text(path) for mark in RECORDS):
            rel = path.relative_to(root)
            out.append(
                f"{rel}: records none of its runs. Wrap its exit in `usage_log.exited(\"{path.stem}\", ...)` (a check), call "
                f"`guard_log` (a hook), or add `# TOOL_RECORD: <where its runs are seen>` near its top, and register a "
                f"usage-log name in scripts/tool-registry.json"
            )
    return out


def called(root: Path) -> dict[str, str]:
    """Every tool name a usage-log call names -> the first file that names it."""
    out: dict[str, str] = {}
    files = [p for p in (root / "scripts").rglob("*") if p.suffix in (".py", ".sh") and "__pycache__" not in p.parts]
    for path in sorted([*files, root / "Makefile"]):
        text = _text(path)
        if "usage_log" not in text or path.name == "usage_log.py":
            continue
        for pattern in CALLS:
            for name in pattern.findall(text):
                out.setdefault(name, str(path.relative_to(root)))
    return out


def mismatched(root: Path) -> list[str]:
    """Calls the registry lacks, and registry entries nothing calls."""
    reg = tool_yield.registry(root)
    calls = called(root)
    out = [
        f"{where}: records `{name}`, which scripts/tool-registry.json lacks - add it with its kind and what it does"
        for name, where in sorted(calls.items())
        if name not in reg
    ]
    out += [
        f"scripts/tool-registry.json: `{name}` is registered but no code records it - remove the entry, or record its runs"
        for name in sorted(reg)
        if name not in calls
    ]
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="no tool without its record (feature 406)")
    ap.add_argument("--root", default=str(tool_yield.ROOT))
    root = Path(ap.parse_args(argv).root).resolve()
    findings = unrecorded(root) + mismatched(root)
    for line in findings:
        print(f"check-tool-signals: {line}", file=sys.stderr)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hooks" / "lib"))
    sys.dont_write_bytecode = True  # a record leaves no __pycache__ in the worktree (feature 406)
    import usage_log  # noqa: E402 - feature 406 T05 (D162): every refusing check records its run

    sys.exit(usage_log.exited("check-tool-signals", main(sys.argv[1:])))
