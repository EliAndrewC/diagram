#!/usr/bin/env python3
"""A research feature ends with its findings checked against the code (feature 378) - `make impl-check F=NNN`.

WHY (the GM, 2026-10-10, specs/378-research-findings-checked-against-code/request.md): every `research record` feature has
*"a task in which we look up whether or not our implementation conforms"* - the link added where the code should cite the
new page, a mismatch *"properly annotated so that a `make claims-report` will show this item"* - without fixing the code
unless the feature asked; and the task is *"a tracked must be there"*. The claims machinery already holds the answer
(feature 316): a `Research:` claim cites a question, `impl-drift` checks it, the index keeps the verdict, and
`make claims-report` lists every finding. This asks the one question that was never asked: did the feature connect its
findings to it?

WHAT IS OWED by a feature tagged `research record`, for each question whose FINDINGS page (`research/questions/NNNN-<id>.html`,
not its `.notes`, `.drawing` or `.originals`) the feature's commits changed or created - its commits being those whose
message opens with its number (`Feature NNN` or `NNN:`), as this repository writes them:
  (a) at least one `Research:` claim, in the engine's code or the Mode A procedures, citing the question (its findings or
      its FINDINGS page - a claim on the drawing page alone is not re-owed by a rewritten finding), none of them owed - so the index holds a verdict for each, IN-STEP or a finding;
  (b) only for a question NO code decides (the thing is not built), a line in the feature's `implementation-check.md`:
      `- NNNN: no code implements it - <why>; searched: <the units and the grep that found none>`. Code that draws or
      decides the thing is case (a) whatever it does - its claim added, a mismatch the DRIFTED verdict the report shows.
A DRIFTED claim satisfies (a): the verdict is what the GM asked to see in the report, and fixing the code is the
feature's own business only if its spec says so.

    impl_check.py <feature dir>           what is owed and what is missing; exit 1 if anything is missing
The closing check (`scripts/gates/close_check.py`) asks `missing()` of every research-record feature at every close.
"""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TAG = "research record"
RECORD = "implementation-check.md"
#: the project's old place, before feature 329 moved it to the root - a commit from then names its pages under it (split, so
#: the old-layout check does not read this as a stale pointer)
_OLD_PREFIX = re.escape(".claude/skills/" + "diagram/")
FINDINGS_PAGE = re.compile(rf"^(?:{_OLD_PREFIX})?research/questions/(\d{{4}})-[a-z0-9-]+\.html$")
# a claim cites a question by its FINDINGS page only: a claim on the drawing page alone is fingerprinted on that page, so a
# rewritten finding never re-owes it and it would pass on a verdict reached before the change (plan review of 378)
CITED = re.compile(r"research/questions/(\d{4})-[a-z0-9-]+\.html$")
NONE_LINE = re.compile(r"^-\s*(\d{4}):\s*no code implements it\s*-\s*(\S.*)$", re.M)
#: case (b) says what was searched, or it is a reason without a search (spec FR-001, review round 1)
SEARCHED = re.compile(r";\s*searched:\s*\S")


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=False).stdout


def is_research_feature(d: Path) -> bool:
    try:
        text = (d / "spec.md").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    m = re.search(r"^\*\*Affects\*\*:?\s*(.+)$", text, re.M)
    return bool(m) and TAG in [t.strip().lower() for t in m.group(1).split(",")]


def changed_questions(root: Path, number: int) -> list[str]:
    """Every question whose findings page a commit of feature `number` changed or created."""
    pattern = rf"^(Feature )?0*{number}([: ]|$)"
    # the SUBJECT line opens with the number (git's --grep would also match a later line); a merge is no feature's
    rx = re.compile(pattern)
    shas = [ln.split(" ", 1)[0] for ln in _git(root, "log", "--no-merges", "--format=%H %s").splitlines() if rx.search(ln.split(" ", 1)[-1])]
    found: set[str] = set()
    for sha in shas:
        for name in _git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", "--root", sha).split():
            m = FINDINGS_PAGE.match(name)
            if m:
                found.add(m.group(1))
    return sorted(found)


def recorded_none(d: Path) -> dict[str, str]:
    try:
        return dict(NONE_LINE.findall((d / RECORD).read_text(encoding="utf-8", errors="replace")))
    except OSError:
        return {}


def _claims():  # noqa: ANN202 - scripts/record/claims.py, the claims index's one reader
    spec = importlib.util.spec_from_file_location("claims", Path(__file__).resolve().parent / "claims.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("claims", mod)
    spec.loader.exec_module(mod)
    return mod


def citing(root: Path) -> tuple[dict[str, list[str]], set[str], dict[str, str]]:
    """(question -> the claim keys citing it, the keys owed their check, key -> its index verdict)."""
    cl = _claims()
    cur = cl.current(root)
    index = cl.load_index(root / cl.INDEX)
    store = cl.load_store(root / cl.STORE)
    due = {k for k, _why in cl.owed(cur, index, root / cl.QUESTIONS, store)}
    by_q: dict[str, list[str]] = {}
    for key, row in cur.items():
        for p in row.claim.pointers if row.claim is not None else ():
            m = CITED.search(p)
            if m:
                by_q.setdefault(m.group(1), []).append(key)
    return by_q, due, {k: v.get("verdict", "") for k, v in index.items()}


def report(root: Path, d: Path, cites=None) -> tuple[list[str], list[str]]:  # noqa: ANN001 - citing()'s triple, for tests
    """(lines to print, what is missing) for feature directory `d`."""
    if not is_research_feature(d):
        return [f"impl-check: {d.name} is not tagged `{TAG}` - nothing is owed"], []
    number = int(d.name.split("-", 1)[0])
    qs = changed_questions(root, number)
    if not qs:
        return [f"impl-check: {d.name}'s commits changed no question's findings - nothing is owed"], []
    by_q, due, verdict = cites if cites is not None else citing(root)
    nones = recorded_none(d)
    lines, missing = [f"impl-check: {d.name} changed {len(qs)} question(s): {' '.join(qs)}"], []
    for q in qs:
        keys = sorted(by_q.get(q, []))
        if keys:
            owed = [k for k in keys if k in due]
            lines.append(f"  {q}: {len(keys)} claim(s) cite it" + (f", {len(owed)} owed the check" if owed else ""))
            lines += [f"      {verdict.get(k) or '-':<14} {k}" + ("  (owed)" if k in due else "") for k in keys]
            if owed:
                missing.append(f"{q}: {len(owed)} claim(s) citing it are owed their impl-drift check - `make claims-owed` names them")
        elif q in nones and SEARCHED.search(nones[q]):
            lines.append(f"  {q}: no code implements it - {nones[q]}")
        elif q in nones:
            lines.append(f"  {q}: no code implements it - {nones[q]}  (says nothing of what was searched)")
            missing.append(f"{q}: its line in {RECORD} must say what was searched - `; searched: <the units and the grep that found none>`")
        else:
            lines.append(f"  {q}: no claim cites it, and {RECORD} has no line for it")
            missing.append(f"{q}: cite it in the `Research:` claim of the code that decides it (then its impl-drift check), "
                           f"or, only if NO code decides it, add `- {q}: no code implements it - <why>; searched: <what>` to {d.name}/{RECORD}")
    lines.append(f"impl-check: {len(missing)} missing" if missing else "impl-check: nothing missing")
    return lines, missing


def missing(d: Path, root: Path = ROOT) -> list[str]:
    """What the closing check refuses on: every missing item, prefixed with the feature."""
    return [f"{d.name} owes its implementation check (feature 378): {m}" for m in report(root, d)[1]]


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__.strip().splitlines()[-2].strip(), file=sys.stderr)
        return 2
    d = Path(argv[0])
    d = d if d.is_dir() else next((ROOT / "specs").glob(f"{int(argv[0]):03d}-*"), d)
    lines, miss = report(ROOT, d)
    print("\n".join(lines))
    return 1 if miss else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
