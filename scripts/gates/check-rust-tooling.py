#!/usr/bin/env python3
"""`make rust-tooling` - no Python-only check without its row in `dev/rust-tooling.md` (feature 443 T07, FR-011, plan D13).

WHY (the design the GM approved on 2026-10-28, `specs/443-work-budget-tooling/request.md` section 7, "Nothing forgotten,
mechanically"): when phases move to Rust, a check that reads Python's syntax tree or `.py` files silently stops checking the moved
code. So every such check says, in the inventory, what happens to it under Rust - and a new one cannot be added without saying.

WHAT IS READ: every tracked file (`git ls-files`) outside `specs/`, `research/`, `dev/` and the pools, `.py` or `.sh`, that imports
`ast`, `tokenize`, `inspect` or `symtable`, calls the builtin `compile(`, or reads `.py` files (`"*.py"`, `endswith(".py")`,
`suffix == ".py"`, `-name '*.py'`); and every Makefile target whose recipe runs ruff, pyrefly, pytest, coverage, testmon or vulture
or globs `*.py`. Each must be named by a row's KEYS - a path, a glob (`fnmatch`, so `*` crosses `/`) or `make <target>`; the
check fails naming each one that is not, and the row to add.

    check-rust-tooling.py [--root <repo>]
"""

from __future__ import annotations

import argparse
import fnmatch
import re
import subprocess
import sys
from pathlib import Path

INVENTORY = "dev/rust-tooling.md"
SKIP = ("specs/", "research/", "dev/", "pool/", "legacy-hand-authored-pool/")
SYNTAX = re.compile(r"^\s*(?:import\s+(?:ast|tokenize|inspect|symtable)\b|from\s+(?:ast|tokenize|inspect|symtable)\s+import\b)", re.M)
PY_FILES = re.compile(r"""["']\*\.py["']|endswith\(\s*["']\.py["']|suffix\s*==\s*["']\.py["']|-name\s+['"]\*\.py['"]|(?<![.\w])compile\(""")
# ...AND A READER OF THE RUST PHASES' SOURCE (feature 444 T17, the row "this inventory's check"): a tool reading `.rs` files is as
# much a part of the Rust tooling as one reading `.py`, and goes unlisted the same silent way
RS_FILES = re.compile(r"""["']\*\.rs["']|endswith\(\s*["']\.rs["']|suffix\s*==\s*["']\.rs["']|-name\s+['"]\*\.rs['"]""")
TOOLS = re.compile(r"\b(?:ruff|pyrefly|pytest|coverage|testmon|vulture|rust_checks|cargo|clippy|rustfmt|llvm-cov)\b|[\"']\*\.py[\"']|-name\s+['\"]\*\.py['\"]")
_TARGET = re.compile(r"^([a-z][\w-]*)\s*:(?!=)")
_KEY = re.compile(r"`([^`]+)`")


def readers(root: Path, files: list[str]) -> list[str]:
    """The tracked files that read Python's syntax tree or `.py` files."""
    out = []
    for f in files:
        if f.startswith(SKIP) or not f.endswith((".py", ".sh")):
            continue
        try:
            text = (root / f).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if SYNTAX.search(text) or PY_FILES.search(text) or RS_FILES.search(text):
            out.append(f)
    return out


def tool_targets(makefile: str) -> list[str]:
    """The Makefile targets whose recipe runs a Python-only tool or globs `*.py`."""
    recipes: dict[str, str] = {}
    cur = None
    for line in makefile.splitlines():
        if not line.startswith("\t") and (m := _TARGET.match(line)):
            cur = m.group(1)
            recipes.setdefault(cur, "")
        elif line.startswith("\t") and cur:
            recipes[cur] += line + "\n"
    return sorted(t for t, r in recipes.items() if TOOLS.search(r))


def keys(inventory: str) -> list[str]:
    """Every key of the inventory's rows: the backticked items of each row's last cell."""
    out: list[str] = []
    for line in inventory.splitlines():
        if line.startswith("| ") and not line.startswith(("| check |", "|---")):
            out += _KEY.findall(line.rstrip().rstrip("|").rsplit("|", 1)[-1])
    return out


#: THE FATES A ROW IS PROVEN FOR before a Rust phase lands (feature 444 FR-011, T17's step 1); "dropped" and "unchanged" owe none
PROVEN_FATES = ("one for one", "partial", "rewritten", "replaced")


def unproven(inventory: str) -> list[str]:
    """The inventory's rows of a PROVEN_FATES fate that the "Proven on the fixture" table does not name exactly - a name with a
    qualifier (`dead closure (its private half)`) proves part of a row, not the row."""
    rows: list[str] = []
    proven: set[str] = set()
    table = ""
    for line in inventory.splitlines():
        if line.startswith("| check |"):
            table = "inventory"
        elif line.startswith("| row |"):
            table = "proven"
        elif line.startswith("| ") and not line.startswith("|---"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if table == "inventory" and len(cells) >= 5 and cells[3].startswith(PROVEN_FATES):
                rows.append(cells[0])
            elif table == "proven":
                proven.add(cells[0])
    return [r for r in rows if r not in proven]


def problems(root: Path) -> list[str]:
    files = subprocess.run(["git", "-C", str(root), "ls-files"], capture_output=True, text=True, check=True).stdout.split()
    have = keys((root / INVENTORY).read_text(encoding="utf-8")) if (root / INVENTORY).is_file() else []
    paths = [k for k in have if not k.startswith("make ")]
    targets = {k.removeprefix("make ").strip() for k in have if k.startswith("make ")}
    out = [f"{f}: reads Python's syntax tree, or .py or .rs files, and no row of {INVENTORY} names it" for f in readers(root, files) if not any(fnmatch.fnmatch(f, k) for k in paths)]
    # ...AND NO RUST PHASE LANDS WITH A ROW UNPROVEN (feature 444 FR-011, the round arbiter's ruling on
    # ask:444-T17-rows-need-a-phase: Route A defers four rows to T19's port only because this refuses its landing until they
    # are marked proven - without it the deferral would be a waiver)
    if any(f.startswith("rust/") and f.endswith(".rs") for f in files) and (root / INVENTORY).is_file():
        out += [
            f"a Rust phase is in the tree, and the row `{r}` of {INVENTORY} is not proven - prove it on the phase (its check refuses a copy written to break it), then name it in the \"Proven on the fixture\" table"
            for r in unproven((root / INVENTORY).read_text(encoding="utf-8"))
        ]
    mk = root / "Makefile"
    if mk.is_file():
        out += [f"make {t}: its recipe runs a Python-only or Rust tool, and no row of {INVENTORY} names it" for t in tool_targets(mk.read_text(encoding="utf-8")) if t not in targets]
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="check-rust-tooling.py")
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[2]))
    root = Path(ap.parse_args(argv).root)
    bad = problems(root)
    if not bad:
        print(f"rust-tooling: every Python-only check has its row in {INVENTORY}")
        return 0
    print("\n".join(f"rust-tooling: {b}" for b in bad), file=sys.stderr)
    print(
        f"rust-tooling: add a row to {INVENTORY} - | check | today (Python) | in the Rust phases | fate (one for one, partial, rewritten, "
        "replaced, dropped or unchanged) | keys (`<path or glob>` or `make <target>`) | - or name it in an existing row's keys",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hooks" / "lib"))
    sys.dont_write_bytecode = True  # a record leaves no __pycache__ in the worktree (feature 406)
    import usage_log  # noqa: E402 - feature 406 T05 (D162): every refusing check records its run

    sys.exit(usage_log.exited("check-rust-tooling", main(sys.argv[1:])))
