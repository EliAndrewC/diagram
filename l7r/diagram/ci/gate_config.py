"""What decides HOW the gate's tests run - the incremental planner's reason to run everything (feature 415, T02, D3/D4).

WHY (the GM, 2026-10-24: "I thought that our landing was efficient in terms of only running tests on things that were
changed"). The planner planned FULL whenever `state.tooling_hash` moved - a hash built to decide when the TOOLING tests rerun,
over `scripts/`, the whole Makefile and `pyproject.toml` too. Tooling lands several times a day, so most landings ran all
10,376 tests: feature 405 T26's two engine files reached 143 of 11,890 baseline tests, and its gate ran everything because
`scripts/` had moved (feature 415 `research.md` R1). `tooling_hash` stays as it is for the tooling tests; the planner reads
this instead:

- `config_hash`: the gate's own machinery (`l7r/diagram/ci/`, `l7r/diagram/pipeline/`, `l7r/diagram/switches.py`,
  `l7r/diagram/_invocation.py`, `tests/conftest.py`, `tests/_scope.py`), the pinned lockfiles, `pyproject.toml`'s pytest and
  coverage tables, and the Makefile's TEST CONFIGURATION - the recipes of `test` and `test-full` and every variable they
  reference, closed over the variables those reference, with each `##` help comment stripped. A change to any of these plans
  FULL; a Makefile help line, a new target or a `requirements*.in` does not.
- `scripts_readers` / `tooling_modules`: what a `scripts/` change selects - every test module under `tests/tooling/` and
  `tests/hooks/` (reused on their recorded reads where unchanged, `tests/tooling/_test_deps.py`), and every other test module
  whose source, or the source of a `tests/` module it imports (transitively), contains the substring `scripts` (spec FR-001,
  read loosely: `tests/test_building_types.py` reaches it as `os.path.join(REPO, "scripts")`; a substring, so
  `tests._scripts` matches too).
"""

from __future__ import annotations

import ast
import hashlib
import re
from pathlib import Path

#: the gate's own machinery - every one already in `state.TOOLING_PATHS` (feature 415 plan D3)
MACHINERY = ("l7r/diagram/ci", "l7r/diagram/pipeline", "l7r/diagram/switches.py", "l7r/diagram/_invocation.py", "tests/conftest.py", "tests/_scope.py")
#: the pinned lockfiles (`requirements.txt`: "Locked ... Re-lock: pip-compile"); the `.in` sources are not (spec round 1)
LOCKFILES = ("requirements.txt", "requirements-dev.txt", "requirements-ci.txt")
#: the Makefile targets whose recipes run the gate's test phase
TEST_TARGETS = ("test", "test-full")
#: the trees whose test modules a `scripts/` change selects whole (their tests reused on recorded reads where unchanged)
TOOLING_TREES = ("tests/tooling/", "tests/hooks/")

_VAR_DEF = re.compile(r"^(?:[\w.-]+:\s*)?(?:export\s+|override\s+)?([A-Z_][A-Z0-9_]*)\s*(?::=|\?=|\+=|=)")
_VAR_REF = re.compile(r"\$[({]([A-Z_][A-Z0-9_]*)[)}]")


def _help_stripped(line: str) -> str:
    return line.split("##", 1)[0].rstrip() if "##" in line else line


def makefile_test_config(text: str) -> str:
    """The Makefile's test configuration: each line of the test targets' recipes, then every definition of every variable
    they reference, closed over the variables those reference, in file order, with `##` help comments stripped."""
    lines = text.splitlines()
    kept: list[str] = []
    i = 0
    while i < len(lines):
        target = re.match(r"^([\w.-]+)\s*:(?!=)", lines[i])
        if target and target.group(1) in TEST_TARGETS and not _VAR_DEF.match(lines[i]):
            kept.append(_help_stripped(lines[i]))
            i += 1
            while i < len(lines) and (lines[i].startswith("\t") or lines[i].startswith("##")):
                if lines[i].startswith("\t"):
                    kept.append(lines[i])
                i += 1
            continue
        i += 1
    defs: dict[str, list[str]] = {}
    for line in lines:
        m = _VAR_DEF.match(line)
        if m:
            defs.setdefault(m.group(1), []).append(_help_stripped(line))
    seen: set[str] = set()
    todo = sorted({v for line in kept for v in _VAR_REF.findall(line)})
    while todo:
        name = todo.pop()
        if name in seen:
            continue
        seen.add(name)
        for line in defs.get(name, []):
            todo += [v for v in _VAR_REF.findall(line) if v not in seen]
    return "\n".join(kept + [line for line in lines if (m := _VAR_DEF.match(line)) and m.group(1) in seen and _help_stripped(line)])


def pyproject_test_config(text: str) -> str:
    """`pyproject.toml`'s `[tool.pytest...]` and `[tool.coverage...]` tables, each with its lines."""
    out: list[str] = []
    keep = False
    for line in text.splitlines():
        head = re.match(r"^\s*\[+\s*([^\]]+?)\s*\]+", line)
        if head:
            keep = head.group(1).startswith(("tool.pytest", "tool.coverage"))
        if keep:
            out.append(line)
    return "\n".join(out)


def config_hash(root: Path) -> str:
    """A content hash over what decides how the gate's tests run (the module docstring); a missing file counts as empty."""
    h = hashlib.sha256()
    files: list[Path] = []
    for rel in (*MACHINERY, *LOCKFILES):
        p = root / rel
        files += sorted(p.rglob("*")) if p.is_dir() else [p]
    for f in files:
        if f.is_file() and "__pycache__" not in f.parts:
            h.update(str(f.relative_to(root)).encode())
            h.update(f.read_bytes())
    for name, extract in (("Makefile", makefile_test_config), ("pyproject.toml", pyproject_test_config)):
        p = root / name
        h.update(name.encode())
        h.update(extract(p.read_text(encoding="utf-8")).encode() if p.is_file() else b"")
    return h.hexdigest()


def _imports(path: Path, root: Path) -> set[str]:
    """The modules under `tests/` that `path` imports, as repository-relative file paths."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except OSError, SyntaxError, ValueError:
        return set()
    pkg = path.parent.relative_to(root).parts
    out: set[str] = set()
    for node in ast.walk(tree):
        names: list[tuple[str, ...]] = []
        if isinstance(node, ast.Import):
            names = [tuple(a.name.split(".")) for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            base = tuple((node.module or "").split(".")) if node.module else ()
            if node.level:
                base = pkg[: len(pkg) - node.level + 1] + base
            names = [base] + [(*base, a.name) for a in node.names]
        for parts in names:
            if not parts or parts[0] != "tests":
                continue
            for cand in (root.joinpath(*parts).with_suffix(".py"), root.joinpath(*parts) / "__init__.py"):
                if cand.is_file():
                    out.add(str(cand.relative_to(root)))
    return out


def scripts_readers(root: Path) -> list[str]:
    """Every test module outside the tooling trees whose source, or a `tests/` module it imports (transitively), contains
    the substring `scripts` - repository-relative, sorted."""
    files = sorted(str(p.relative_to(root)) for p in (root / "tests").rglob("*.py") if "__pycache__" not in p.parts)
    names = {f: (root / f).read_text(encoding="utf-8", errors="replace") for f in files}
    reads = {f for f, src in names.items() if "scripts" in src}
    deps = {f: _imports(root / f, root) for f in files}
    changed = True
    while changed:
        changed = False
        for f in files:
            if f not in reads and deps[f] & reads:
                reads.add(f)
                changed = True
    return sorted(f for f in reads if Path(f).name.startswith("test_") and not f.startswith(TOOLING_TREES))


def tooling_modules(root: Path) -> list[str]:
    """Every test module under the tooling trees, repository-relative, sorted."""
    return sorted(str(p.relative_to(root)) for tree in TOOLING_TREES for p in (root / tree).rglob("test_*.py") if "__pycache__" not in p.parts)
