#!/usr/bin/env python3
"""Fail a function past 100 statements, or a suppression of that cap that does not say why (feature 370).

WHY (the GM, 2026-10-08, closing feature 111: *"we've replaced 'decompose for readability' with a mechanical cap on
function length and file length"* - only the file cap existed). Constitution Principle X clause 12 caps a function's
size; this holds it. The cap is ruff's statement rule, PLR0915, at `max-statements = 100` in `pyproject.toml` - the GM's
number (2026-10-10), the second most common value on GitHub in the survey of 1,209 repositories and the most common one
chosen over the default 50 (`specs/370-function-length-gate/research.md` R1).

WHAT IT CHECKS, over the five trees the cap holds (`TREES`; the legacy pool and `specs/` are write-once history):

  1. every function over the cap, by ruff with the ROOT config pinned (`--config pyproject.toml`), so no `ruff.toml`
     beside the code can lift it - and ruff lints a named path even where `extend-exclude` fences it out of the rest of
     the lint, which is how `scripts/`, `pool/` and `tests/hooks/` are held by this rule alone;
  2. every suppression of it, read from COMMENT tokens (a `# noqa` in a string is not one): the escape is clause 12's -
     on the `def` line, saying why the body must remain one (`MIN_WORDS` words at least). A bare `# noqa` on a `def`
     line silences the cap with no rule named, and a file-level `# ruff: noqa` / `# flake8: noqa` that is bare or names
     the rule exempts a whole file - both refused;
  3. `pyproject.toml`: no ruff `*ignore*` key may name the rule or a prefix of it.

Every refusal prints the way out. Invoked first in `make static` and `make quick` (so this message, not ruff's bare
one, is what a session reads) and by `scripts/sync-with-main.sh` before every push - a push of `tests/` or `scripts/`
alone takes the DIRECT route and runs no gate.

    check-function-cap.py [root]      check a tree (default: this repository)
    check-function-cap.py --selftest  plant each case in a scratch tree and prove each fires or passes
"""

from __future__ import annotations

import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import tokenize
import tomllib
from pathlib import Path

sys.dont_write_bytecode = True  # the push runs this inside the tree it is about to push

REPO = Path(__file__).resolve().parents[2]
RULE = "PLR0915"
TREES = ("l7r", "tests", "scripts", "pool", "tests/hooks")
MIN_WORDS = 3

WAYS_OUT = f"""
  Each function above is past the 100-statement cap (constitution Principle X clause 12; ruff {RULE}). Two ways out:
    - split it into parts at module or class level (a nested function counts in its parent, so it does not help), or
    - if the body must stay one, put `# noqa: {RULE} <why the body must remain one>` on its `def` line - a reason of
      {MIN_WORDS} words or more.
  Why 100: specs/370-function-length-gate/research.md R1.
"""

_CODES = r"[A-Z]+[0-9]*(?:\s*,\s*[A-Z]+[0-9]*)*"
_INLINE = re.compile(rf"#\s*noqa(?::\s*(?P<codes>{_CODES}))?(?P<rest>.*)$", re.I)
_FILE = re.compile(rf"#\s*(?:ruff|flake8)\s*:\s*noqa(?::\s*(?P<codes>{_CODES}))?", re.I)
_DEF = re.compile(r"^\s*(?:async\s+)?def\s")


def _names_rule(codes: str | None) -> bool:
    """Does a code list name the rule, or a prefix of it (`PLR09`, `PL`, `ALL`)?"""
    return any(c == "ALL" or (c and RULE.startswith(c)) for c in re.split(r"\s*,\s*", (codes or "").strip().upper()))


def held_files(root: Path) -> list[Path]:
    """Every `.py` under the held trees, once each (`tests/hooks` sits inside `tests`)."""
    found = {p for t in TREES if (root / t).is_dir() for p in (root / t).rglob("*.py") if "__pycache__" not in p.parts}
    return sorted(found)


def over_cap(root: Path, config: Path = REPO / "pyproject.toml") -> list[tuple[str, int, str]]:
    """(file relative to root, line, ruff's message) for every function over the cap, under `config`."""
    trees = [t for t in TREES if (root / t).is_dir()]
    if not trees or not config.is_file():  # a tree with no config sets no cap (the push's own fixtures)
        return []
    r = subprocess.run(
        [*_ruff(), "check", "--no-cache", "--config", str(config), "--select", RULE, "--output-format", "json", *trees],
        capture_output=True,
        text=True,
        check=False,
        cwd=root,
    )
    try:  # a ruff that did not run answers in stderr, not JSON - never read that as "nothing over the cap"
        found = json.loads(r.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(f"ruff did not run ({r.returncode}): {r.stderr.strip()[:300]}") from None
    rows = {(str(Path(f["filename"]).resolve().relative_to(root.resolve())), f["location"]["row"], f["message"]) for f in found}
    return sorted(rows)


def _ruff() -> list[str]:
    """The ruff on PATH, else the interpreter's module: the push's fixtures run with HOME moved, which hides a per-user
    install from `python3 -m ruff` while its binary stays on PATH."""
    exe = shutil.which("ruff")
    return [exe] if exe else [sys.executable, "-m", "ruff"]


def _comments(text: str) -> list[tuple[int, str]]:
    """(line, comment text) for every comment token; a file that does not tokenize has none we can read."""
    try:
        return [(t.start[0], t.string) for t in tokenize.generate_tokens(io.StringIO(text).readline) if t.type == tokenize.COMMENT]
    except tokenize.TokenError, SyntaxError:
        return []


def suppression_problems(path: Path) -> list[tuple[int, str]]:
    """(line, what is wrong) for every suppression of the cap in one file that clause 12 does not allow."""
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    out: list[tuple[int, str]] = []
    for n, comment in _comments(text):
        f = _FILE.search(comment)
        if f and (f.group("codes") is None or _names_rule(f.group("codes"))):
            out.append((n, f"a file-level `# ruff: noqa` / `# flake8: noqa` that is bare or names {RULE} exempts every function in the file - remove it"))
            continue
        m = _INLINE.search(comment)
        if not m:
            continue
        on_def = bool(_DEF.match(lines[n - 1])) if n - 1 < len(lines) else False
        if m.group("codes") is None:
            if on_def:
                out.append((n, f"a bare `# noqa` on a `def` line silences the cap with no rule named - name {RULE} and say why the body must remain one"))
            continue
        if not _names_rule(m.group("codes")):
            continue
        if not on_def:
            out.append((n, f"`# noqa: {RULE}` belongs only on the `def` line of the one function it keeps whole"))
        elif len(re.findall(r"[A-Za-z]{2,}", m.group("rest"))) < MIN_WORDS:
            out.append((n, f"say why the body must remain one, in {MIN_WORDS} words or more after `# noqa: {RULE}` (constitution X clause 12), or split it"))
    return out


def config_ignores(toml_text: str) -> list[str]:
    """Every ruff `*ignore*` setting in a pyproject that names the rule or a prefix of it."""
    ruff = tomllib.loads(toml_text).get("tool", {}).get("ruff", {})
    found: list[str] = []

    def walk(node: object, key: str, under_ignore: bool) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                walk(v, f"{key}.{k}", under_ignore or "ignore" in k)
        elif isinstance(node, list):
            for v in node:
                walk(v, key, under_ignore)
        elif under_ignore and isinstance(node, str) and _names_rule(node):
            found.append(f"{key} = {node!r}")

    walk(ruff, "tool.ruff", False)
    return found


def _file_facts(root: Path) -> object | None:
    """Feature 383 (the GM 2026-10-12): each file's suppression problems kept by its content (`record_cache.FileFacts`) -
    tokenizing every held file was nearly all of this check's 1.5 s; ruff, the other half, is 0.07 s. None where the cache
    module is not beside this script (a fixture copy)."""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "record"))
        import record_cache  # noqa: PLC0415
    except ImportError:
        return None
    return record_cache.FileFacts(root, "function-cap", Path(__file__))


def check(root: Path, config: Path = REPO / "pyproject.toml") -> list[str]:
    """Every refusal, as the lines to print; empty when the tree is under the cap."""
    msgs = [f"  {f}:{n}  {msg}" for f, n, msg in over_cap(root, config)]
    files = held_files(root)
    rel = {p: p.relative_to(root).as_posix() for p in files}
    facts = _file_facts(root)
    found = facts.facts([rel[p] for p in files], lambda r: suppression_problems(root / r)) if facts is not None else {rel[p]: suppression_problems(p) for p in files}  # type: ignore[attr-defined]
    problems = [f"  {p.relative_to(root)}:{n}  {why}" for p in files for n, why in found[rel[p]]]
    pyproject = root / "pyproject.toml"
    ignores = config_ignores(pyproject.read_text()) if pyproject.is_file() else []
    out: list[str] = []
    if msgs:
        out += [f"check-function-cap: {len(msgs)} function(s) over the 100-statement cap", *msgs, WAYS_OUT]
    if problems:
        out += [f"check-function-cap: {len(problems)} suppression(s) of the cap that clause 12 does not allow", *problems, ""]
    if ignores:
        out += ["check-function-cap: pyproject.toml switches the cap off for whole files - remove these:", *(f"  {i}" for i in ignores), ""]
    return out


def _body(n: int, suffix: str = "") -> str:
    return f"def f() -> None:{suffix}\n" + "".join(f"    x{i} = {i}\n" for i in range(n))


def selftest() -> int:
    """Plant each case and prove the verdict: over the cap fires in a fenced-out tree, each bad suppression fires, a
    reasoned one passes, a `# noqa` in a string is not read, and a config ignore fires."""
    cases = {
        "scripts/long.py": (_body(101), True),
        "l7r/ok.py": (_body(100), False),
        "l7r/kept.py": (_body(101, f"  # noqa: {RULE} - one ordered pass whose steps share every local"), False),
        "l7r/thin.py": (_body(3, f"  # noqa: {RULE} - long"), True),
        "l7r/bare.py": (_body(3, "  # noqa"), True),
        "l7r/file.py": ("# flake8: noqa\n" + _body(3), True),
        "l7r/stray.py": (f"x = 1  # noqa: {RULE} - a reason in enough words\n", True),
        "l7r/string.py": (f'S = "def g():  # noqa: {RULE}"\n', False),
    }
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        for rel, (text, _) in cases.items():
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text(text)
        # its own config, so the selftest proves the check anywhere - the push's fixture trees carry no pyproject.toml
        config = Path(td) / "selftest-ruff.toml"
        config.write_text('[lint]\nselect = ["PLR0915"]\n[lint.pylint]\nmax-statements = 100\n')
        report = "\n".join(check(root, config))
        wrong = [rel for rel, (_, fires) in cases.items() if (f"{rel}:" in report) is not fires]
    bad_config = config_ignores('[tool.ruff.lint.per-file-ignores]\n"x.py" = ["PLR09"]\n') == []
    if wrong or bad_config:
        print(f"check-function-cap SELFTEST FAILED: wrong verdict on {wrong}{' and the config ignore' if bad_config else ''}", file=sys.stderr)
        return 1
    print("check-function-cap: selftest ok (the cap fires in a fenced-out tree, each bad suppression fires, a reasoned one passes)")
    return 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["--selftest"]:
        return selftest()
    root = Path(argv[0]) if argv else REPO
    out = check(root)
    if out:
        print("\n".join(out), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / "hooks" / "lib"))
    import usage_log  # noqa: E402 - feature 406 T03 (D162): every refusing check records its run

    sys.exit(usage_log.exited("check-function-cap", main(sys.argv[1:])))
