"""The drawing pages still stating a changed constant's OLD figure (feature 385 T62, plan D81).

WHY. The round arbiter on `ask:t10-findings-at-landing` (2026-10-18): T10 made the dike-pond inset derived per map, and three
drawing pages (0022, 0025, 0027) still said the pond stood 23 ft in from its parcel's edge - found by a claims round at landing,
not at the edit. So `make claims-owed` now names them at the edit.

THE RULE. A claimed module-level constant (a `Research:` docstring under it) whose value or claim differs between the merge base
with origin/main and the working tree is CHANGED. Its OLD figures are the numbers in its base value, written as a page writes them
(`23.0` as `23`); 0 and 1 are left out, since every page states them. Each drawing page that states one as a whole number (not a
digit of a longer one, whatever unit follows) and IS, or links, a question the constant's claim cites is named. A FLAG, never a
refusal: a page that restates the figure in words ("six in ten") is not found - measured on 0024, which links no question the
claim cites either - and the claims rounds still read the pages.
"""

from __future__ import annotations

import ast
import re
import subprocess
from pathlib import Path

QUESTIONS = "research/questions"
CITED = re.compile(r"research/questions/(\d{4})-")


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=False).stdout


def constants(source: str) -> dict[str, tuple[str, str, ast.expr]]:
    """name -> (its value dumped, its docstring, its value) for each module-level assignment of one name."""
    try:
        body = ast.parse(source).body
    except SyntaxError:
        return {}
    out: dict[str, tuple[str, str, ast.expr]] = {}
    for i, st in enumerate(body):
        if isinstance(st, ast.Assign) and len(st.targets) == 1 and isinstance(st.targets[0], ast.Name):
            name, val = st.targets[0].id, st.value
        elif isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name) and st.value is not None:
            name, val = st.target.id, st.value
        else:
            continue
        nxt = body[i + 1] if i + 1 < len(body) else None
        doc = nxt.value.value if isinstance(nxt, ast.Expr) and isinstance(nxt.value, ast.Constant) and isinstance(nxt.value.value, str) else ""
        out[name] = (ast.dump(val), doc, val)
    return out


def figures(val: ast.expr) -> list[str]:
    """The numbers of a value as a page writes them: a whole float without its `.0`; 0 and 1 left out."""
    nums = {n.value for n in ast.walk(val) if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) and not isinstance(n.value, bool)}
    return sorted({str(int(v)) if float(v).is_integer() else repr(v) for v in nums if v not in (0, 1)})


def stale(root: Path, base: str = "") -> list[str]:
    """One line per drawing page still stating a changed constant's old figure."""
    base = base or _git(root, "merge-base", "HEAD", "origin/main").strip()
    if not base:
        return []
    pages = sorted((root / QUESTIONS).glob("*.drawing.html"))
    texts = {p: p.read_text(encoding="utf-8", errors="replace") for p in pages}
    out: list[str] = []
    for path in _git(root, "diff", "--name-only", base, "--", "l7r").split():
        if not path.endswith(".py") or not (root / path).is_file():
            continue
        head = constants((root / path).read_text(encoding="utf-8"))
        for name, (dump, doc, val) in constants(_git(root, "show", f"{base}:{path}")).items():
            now = head.get(name)
            if now is None or (now[0], now[1]) == (dump, doc) or "Research:" not in doc + now[1]:
                continue
            cited = set(CITED.findall(doc + now[1]))
            for fig in figures(val):
                pat = re.compile(rf"(?<![\d.]){re.escape(fig)}(?!\d|\.\d)")
                for p, text in texts.items():
                    if (p.name[:4] in cited or any(re.search(rf"\b{q}-[a-z]", text) for q in cited)) and pat.search(text):
                        out.append(f"stale figure: {p.relative_to(root)} states {fig} ({name} was {ast.unparse(val)} in {path}) - reword it, or check it still holds")
    return out
