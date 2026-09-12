#!/usr/bin/env python3
"""The four things a review round kept finding in a spec that a script can find for nothing.

Feature 236, the GM's item 5. Twenty `spec-fidelity` rounds over two features cost 91 minutes, and at
least eight of their findings were mechanical (`specs/236-catch-mistakes-early-and-cheaply/research.md`
R1): a figure stated with no method behind it, a withdrawn measurement still standing somewhere else, a
requirement no success criterion covers, a task list citing an id the spec no longer has. A reviewer
finding those is a reviewer not spending the round on what only a reader can judge.

    1. A MEASURED FIGURE WITH NO RESEARCH POINTER. A paragraph in Summary, Functional requirements,
       Success criteria or Decisions recorded that states a number with a UNIT must also point at the
       research - `R<k>` or `research.md`. A count with no unit ("20 rounds", "FR-001") is not a
       measurement and is not asked for one. Review history and Out of scope narrate, and are exempt.
    2. A WITHDRAWN FIGURE STILL STANDING. `research.md` may mark superseded text `WITHDRAWN: <text>`;
       that text may not then appear anywhere under `specs/` except in a Decisions recorded or Review
       history section, which exist to narrate a reversal. The marked text must be at least twelve
       characters and contain a letter, so a bare number can never be banned. What this CANNOT reach
       is the rest of the tree, where feature 234's own withdrawn measurement survived in five places
       (spec D5, `research.md` R5): reaching that is a different mechanism.
    3. AN ORPHANED REQUIREMENT. Every `FR-` must be named by at least one success criterion, and every
       `SC-` must name an FR or declare itself `(spec-wide)`. An id is three digits and an optional
       lower-case letter, so `FR-007a` is its own id and not a mention of `FR-007`.
    4. A STALE TASK LIST. Every FR or SC id `tasks.md` cites must exist in the spec.

CHECKS 1, 3 AND 4 NEED A `tasks.md` (FR-010a). A freshly claimed spec has none, and the root CLAUDE.md
protects two pushes that carry exactly that shape - the number claim and the mid-feature milestone
push - so a lint that fired on them would refuse the protocol the project requires.
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys

UNITS = ("ft", "m", "km", "ha", "mu", "sq ft", "%", "ms", "s", "min", "minute", "minutes",
         "h", "MB", "MiB", "GiB", "px")
_UNIT_ALT = "|".join(sorted((re.escape(u) for u in UNITS), key=len, reverse=True))
_FIGURE = re.compile(rf"(?<![\w.])\d[\d,]*(?:\.\d+)?\s*(?:{_UNIT_ALT})(?![\w-])")
_POINTER = re.compile(r"\bR\d+\b|research\.md")
_ID = re.compile(r"\b(FR|SC)-(\d{3}[a-z]?)\b")
_DEF = re.compile(r"^\*\*(FR|SC)-(\d{3}[a-z]?)\*\*", re.M)
_HEADING = re.compile(r"^##+\s+(.*?)\s*$", re.M)
_WITHDRAWN = re.compile(r"WITHDRAWN:\s*(.+?)\s*$", re.M)

FIGURE_SECTIONS = ("summary", "functional requirements", "success criteria", "decisions recorded")
NARRATING_SECTIONS = ("decisions recorded", "review history")


def sections(text: str) -> list[tuple[str, int, str]]:
    """(heading in lower case, 1-based line of the first body line, body) for each `##` section."""
    out, marks = [], list(_HEADING.finditer(text))
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        out.append((m.group(1).lower(), text[:m.end()].count("\n") + 1, text[m.end():end]))
    return out


def check_figures(spec: pathlib.Path) -> list[str]:
    """Check 1 - a measured figure whose method the reader cannot reach."""
    bad = []
    for name, start, body in sections(spec.read_text()):
        if not any(name.startswith(s) for s in FIGURE_SECTIONS):
            continue
        line = start
        for para in body.split("\n\n"):
            found = _FIGURE.search(para)
            if found and not _POINTER.search(para):
                n = line + para[:found.start()].count("\n")
                bad.append(f"{spec}:{n}: the figure {found.group(0).strip()!r} states a measurement "
                           f"with no pointer to the research (`R<k>` or `research.md`) in its paragraph")
            line += para.count("\n") + 2
    return bad


def _exempt_spans(text: str) -> list[tuple[int, int]]:
    """Character ranges of the sections that exist to narrate a reversal."""
    spans, marks = [], list(_HEADING.finditer(text))
    for i, m in enumerate(marks):
        if any(m.group(1).lower().startswith(s) for s in NARRATING_SECTIONS):
            spans.append((m.start(), marks[i + 1].start() if i + 1 < len(marks) else len(text)))
    return spans


def check_withdrawn(spec_dir: pathlib.Path, specs_root: pathlib.Path) -> list[str]:
    """Check 2 - text this feature withdrew, still standing somewhere under `specs/`."""
    research = spec_dir / "research.md"
    if not research.is_file():
        return []
    bad, marked = [], []
    for m in _WITHDRAWN.finditer(research.read_text()):
        text = m.group(1).strip().strip("`\"'")
        n = research.read_text()[:m.start()].count("\n") + 1
        if len(text) < 12 or not re.search(r"[A-Za-z]", text):
            bad.append(f"{research}:{n}: `WITHDRAWN:` needs at least twelve characters and a letter - "
                       f"{text!r} would ban a bare figure from the whole record")
            continue
        marked.append((text, str(research), n))
    for text, where, n in marked:
        for path in sorted(specs_root.rglob("*.md")):
            if path == research:
                continue
            body = path.read_text(errors="replace")
            spans = _exempt_spans(body)
            for hit in re.finditer(re.escape(text), body):
                if any(a <= hit.start() < b for a, b in spans):
                    continue                 # narrated in Decisions recorded or Review history
                line = body[:hit.start()].count("\n") + 1
                bad.append(f"{path}:{line}: withdrawn text still standing here - {where}:{n} marks "
                           f"{text!r} as superseded")
    return bad


def check_orphans(spec: pathlib.Path) -> list[str]:
    """Check 3 - a requirement no criterion covers, or a criterion covering nothing."""
    text = spec.read_text()
    frs = {m.group(0)[2:-2] for m in _DEF.finditer(text) if m.group(1) == "FR"}
    bad, covered = [], set()
    for name, start, body in sections(text):
        if not name.startswith("success criteria"):
            continue
        line = start
        for para in body.split("\n\n"):
            for sc in re.finditer(r"^\*\*(SC-\d{3}[a-z]?)\*\*(.*)$", para, re.M):
                named = {f"{k}-{v}" for k, v in _ID.findall(sc.group(2)) if k == "FR"}
                covered |= named
                if not named and "(spec-wide)" not in sc.group(2):
                    n = line + para[:sc.start()].count("\n")
                    bad.append(f"{spec}:{n}: {sc.group(1)} names no FR and is not marked `(spec-wide)`")
            line += para.count("\n") + 2
    for fr in sorted(frs - covered):
        n = next(m.start() for m in _DEF.finditer(text) if m.group(0)[2:-2] == fr)
        bad.append(f"{spec}:{text[:n].count(chr(10)) + 1}: {fr} is named by no success criterion")
    return bad


def check_stale_tasks(spec: pathlib.Path, tasks: pathlib.Path) -> list[str]:
    """Check 4 - a task list citing an id the spec does not have."""
    have = {m.group(0)[2:-2] for m in _DEF.finditer(spec.read_text())}
    body, bad = tasks.read_text(), []
    for m in _ID.finditer(body):
        if m.group(0) not in have:
            bad.append(f"{tasks}:{body[:m.start()].count(chr(10)) + 1}: cites {m.group(0)}, which "
                       f"{spec.name} does not define")
    return bad


def lint(spec_dir: pathlib.Path, specs_root: pathlib.Path | None = None) -> list[str]:
    """Every complaint about one `specs/NNN-*/` directory."""
    spec_dir = pathlib.Path(spec_dir)
    specs_root = specs_root or spec_dir.parent
    spec = spec_dir / "spec.md"
    if not spec.is_file():
        return []
    tasks = spec_dir / "tasks.md"
    bad = check_withdrawn(spec_dir, specs_root)      # check 2 needs no tasks.md
    if tasks.is_file():
        bad += check_figures(spec) + check_orphans(spec) + check_stale_tasks(spec, tasks)
    return bad


def touched_spec_dirs(root: pathlib.Path) -> list[pathlib.Path]:
    """Every `specs/NNN-*/` the delta against the merge base touches, plus untracked ones."""
    root = pathlib.Path(root).resolve()
    try:
        base = subprocess.run(["git", "-C", str(root), "merge-base", "HEAD", "origin/main"],
                              capture_output=True, text=True, timeout=20).stdout.strip()
        names = subprocess.run(["git", "-C", str(root), "diff", "--name-only", base or "HEAD"],
                               capture_output=True, text=True, timeout=20).stdout.split()
        names += subprocess.run(["git", "-C", str(root), "ls-files", "--others", "--exclude-standard"],
                                capture_output=True, text=True, timeout=20).stdout.split()
    except Exception:
        return []
    out = []
    for name in names:
        parts = pathlib.Path(name).parts
        if len(parts) >= 2 and parts[0] == "specs" and (root / "specs" / parts[1]).is_dir():
            d = root / "specs" / parts[1]
            if d not in out:
                out.append(d)
    return out


def selftest() -> None:
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        specs = pathlib.Path(td) / "specs"
        d = specs / "999-a-feature"
        d.mkdir(parents=True)
        (d / "tasks.md").write_text("- [ ] T01 do the thing (FR-001)\n")
        good = ("# x\n\n## Summary\n\nIt took 91 min, measured in `research.md` R1.\n\n"
                "## Functional requirements\n\n**FR-001** A thing.\n\n**FR-001a** Another.\n\n"
                "## Success criteria\n\n**SC-001** (FR-001, FR-001a) Both hold.\n"
                "**SC-002** (spec-wide) The gate is green.\n\n"
                "## Decisions recorded\n\n**D1** We kept the 22 ft figure out of the rule (`research.md` R2).\n\n"
                "## Review history\n\nRound 1 said 6.7 m and we withdrew it.\n")
        (d / "spec.md").write_text(good)
        assert lint(d) == [], lint(d)
        # 1: a figure with no pointer
        (d / "spec.md").write_text(good.replace("It took 91 min, measured in `research.md` R1.", "It took 91 min."))
        assert any("no pointer" in x for x in lint(d)), lint(d)
        # 1: a count with no unit is not a figure
        (d / "spec.md").write_text(good.replace("It took 91 min, measured in `research.md` R1.", "It took 20 rounds."))
        assert lint(d) == [], lint(d)
        # 3: an FR no SC names, and an SC that names none
        (d / "spec.md").write_text(good.replace("**SC-001** (FR-001, FR-001a) Both hold.", "**SC-001** (FR-001) One holds."))
        assert any("FR-001a is named by no success criterion" in x for x in lint(d)), lint(d)
        (d / "spec.md").write_text(good.replace("**SC-002** (spec-wide) The gate is green.", "**SC-002** The gate is green."))
        assert any("names no FR" in x for x in lint(d)), lint(d)
        # 4: a task citing an id that is gone
        (d / "spec.md").write_text(good)
        (d / "tasks.md").write_text("- [ ] T01 do the thing (FR-404)\n")
        assert any("FR-404" in x for x in lint(d)), lint(d)
        (d / "tasks.md").write_text("- [ ] T01 do the thing (FR-001)\n")
        # 2: withdrawn text still standing, and the narrating sections that may carry it
        (d / "research.md").write_text("WITHDRAWN: the 22 ft figure\n")
        (d / "spec.md").write_text(good)
        assert lint(d) == [], "Decisions recorded and Review history may narrate a reversal"
        (d / "spec.md").write_text(good.replace("**FR-001** A thing.", "**FR-001** Keep the 22 ft figure."))
        assert any("withdrawn text still standing" in x for x in lint(d)), lint(d)
        # 2: a marker too short to be safe is itself the complaint
        (d / "research.md").write_text("WITHDRAWN: 22 ft\n")
        (d / "spec.md").write_text(good)
        assert any("twelve characters" in x for x in lint(d)), lint(d)
        # FR-010a: a freshly claimed spec, with no tasks.md, passes checks 1, 3 and 4
        (d / "research.md").unlink()
        (d / "tasks.md").unlink()
        (d / "spec.md").write_text("# x\n\n## Summary\n\nIt took 91 min.\n\n## Functional requirements\n\n**FR-001** A thing.\n")
        assert lint(d) == [], lint(d)
    print("spec-lint selftest ok")


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        selftest()
        return 0
    args = [a for a in argv if not a.startswith("--")]
    if "--delta" in argv:
        root = pathlib.Path(args[0] if args else ".")
        dirs = touched_spec_dirs(root)
    else:
        dirs = [pathlib.Path(a) for a in args]
    if not dirs:
        return 0
    bad: list[str] = []
    for d in dirs:
        bad += lint(d)
    if not bad:
        return 0
    print("\n".join(bad))
    print("\nspec-lint: " + str(len(bad)) + " finding(s). Each is a thing a review round would "
          "otherwise spend itself on (feature 236, the GM: mistakes caught early and cheaply).")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
