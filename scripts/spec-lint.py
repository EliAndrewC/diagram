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
    2. A WITHDRAWN FIGURE STILL STANDING. A `research.md` may mark superseded text with a line opening
       `WITHDRAWN: <text>`; that text may not then appear ANYWHERE IN THE TREE except in a Decisions
       recorded or Review history section, which exist to narrate a reversal, or in a verbatim record
       (`scripts/fixtures/`, `dev/*-log/`), which is history rather than a claim. The marked text must
       be at least twelve characters and contain a letter, so a bare number can never be banned. The
       reach was `specs/` alone at first and every one of the five survivals that motivated the check
       was outside it (spec D5, `research.md` R5).
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
# GUARD_EDIT_OK: the pattern recognized only `**FR-001**`, the id bolded alone, and five of the nine
# specs in this repository write `**FR-001 Its title.**` instead - three of them already on main. On
# those the linter saw NO requirements at all, so check 4 reported every id their tasks.md cites as
# undefined (46 findings on a correct tree, blocking every push) and check 3 silently checked nothing,
# which is the worse half. The id is still the first thing in the bold span; a title may follow it, the
# span may wrap a line, and the declaration may be a list item - all three shapes are in the record.
_DEF = re.compile(r"^(?:[-*+]\s+)?\*\*(FR|SC)-(\d{3}[a-z]?)(?=\*\*|[ .:])[^*]*\*\*", re.M)
_HEADING = re.compile(r"^##+\s+(.*?)\s*$", re.M)
# The marker OPENS a line (a list bullet may stand in front of it). Unanchored, the sentence that
# DESCRIBES the marker - "a research.md may mark superseded text `WITHDRAWN: <text>`" - declared one,
# which mattered little while the scan reached one directory and matters a great deal now that it
# reaches the tree.
_WITHDRAWN = re.compile(r"^\s*(?:[-*+]\s+)?WITHDRAWN:\s*(.+?)\s*$", re.M)
# A VERBATIM RECORD IS NOT A CLAIM. `scripts/fixtures/` holds corpora of commands that really ran and
# `dev/*-log/` the records of runs that really happened; a withdrawn figure inside one is history, not
# an assertion still standing. Same ground as the house-style rules' own fixture exemption (spec D8).
_RECORDS = re.compile(r"(^|/)(scripts/fixtures|dev/[\w-]*-log)/")

def _def_id(m: re.Match[str]) -> str:
    """The id a `_DEF` match declares - `**FR-001**` and `**FR-001 Its title.**` alike."""
    return f"{m.group(1)}-{m.group(2)}"


# What the withdrawn-figure scan does NOT read: a binary is judged by its bytes below, and these are
# the extensions that are always binary here, so the scan opens nothing it cannot use. An
# EXTENSIONLESS file is read - `Makefile` is where this project writes operative prose and figures,
# and a suffix roster that quietly dropped it was the amendment review's finding.
BINARY_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".pdf", ".gif", ".ico", ".woff", ".woff2",
                   ".ttf", ".zip", ".gz", ".prof", ".pyc", ".svg"}

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


def scanned_files(tree_root: pathlib.Path) -> list[pathlib.Path]:
    """Every text file in the tree a withdrawn figure could be standing in.

    `git ls-files` plus the untracked files git would keep, so the scan sees a file written this
    session and never descends into `.clones/` or a build artifact. Off a git tree - a test fixture -
    it walks instead, which is the same set for a directory that has no ignores.
    """
    try:
        out = subprocess.run(["git", "-C", str(tree_root), "ls-files", "--cached", "--others",
                              "--exclude-standard"], capture_output=True, text=True, timeout=60)
        names = out.stdout.split("\n") if out.returncode == 0 else []
    except Exception:
        names = []
    paths = [tree_root / n for n in names if n] if names else [
        p for p in tree_root.rglob("*") if p.is_file() and ".clones" not in p.parts]
    return [p for p in paths if p.suffix.lower() not in BINARY_SUFFIXES
            and not _RECORDS.search(str(p)) and p.is_file()]


def check_withdrawn(spec_dir: pathlib.Path, specs_root: pathlib.Path,
                    tree_root: pathlib.Path | None = None) -> list[str]:
    """Check 2 - text this feature withdrew, still standing anywhere in the tree.

    The reach is the WHOLE tree since feature 236's amendment (the GM 2026-09-12: *"You should do the
    tree wide scan instead of leaving this half done"*). It was `specs/` alone at first, and the limit
    was recorded rather than solved - while all five of the survivals that motivated the check were
    outside `specs/`: two skill `CLAUDE.md` files, the root guard table, a script docstring and a
    research page (spec D5, `research.md` R5).
    """
    research = spec_dir / "research.md"
    if not research.is_file():
        return []
    tree_root = tree_root or specs_root.parent
    bad, marked = [], []
    for m in _WITHDRAWN.finditer(research.read_text()):
        text = m.group(1).strip().strip("`\"'")
        n = research.read_text()[:m.start()].count("\n") + 1
        if len(text) < 12 or not re.search(r"[A-Za-z]", text):
            bad.append(f"{research}:{n}: `WITHDRAWN:` needs at least twelve characters and a letter - "
                       f"{text!r} would ban a bare figure from the whole record")
            continue
        marked.append((text, str(research), n))
    files = [p for p in scanned_files(tree_root) if p != research] if marked else []
    # ONE read per file, every marker asked of it - the scan reads the whole tree now, and reading it
    # again per marker made the cost of a second `WITHDRAWN:` line the cost of the first.
    for path in files:
        try:
            body = path.read_text(errors="replace")
        except OSError:
            continue
        if "\x00" in body[:8192]:              # a binary the extension did not announce
            continue
        spans = None
        for text, where, n in marked:
            for hit in re.finditer(re.escape(text), body):
                if spans is None:
                    spans = _exempt_spans(body)
                if any(a <= hit.start() < b for a, b in spans):
                    continue                   # narrated in Decisions recorded or Review history
                line = body[:hit.start()].count("\n") + 1
                bad.append(f"{path}:{line}: withdrawn text still standing here - {where}:{n} marks "
                           f"{text!r} as superseded")
    return sorted(bad)


def check_orphans(spec: pathlib.Path) -> list[str]:
    """Check 3 - a requirement no criterion covers, or a criterion covering nothing."""
    text = spec.read_text()
    frs = {_def_id(m) for m in _DEF.finditer(text) if m.group(1) == "FR"}
    bad, covered = [], set()
    for name, start, body in sections(text):
        if not name.startswith("success criteria"):
            continue
        line = start
        for para in body.split("\n\n"):
            for sc in re.finditer(r"^(?:[-*+]\s+)?\*\*(SC-\d{3}[a-z]?)(?=\*\*|[ .:])[^*]*\*\*(.*)$", para, re.M):
                named = {f"{k}-{v}" for k, v in _ID.findall(sc.group(2)) if k == "FR"}
                covered |= named
                if not named and "(spec-wide)" not in sc.group(2):
                    n = line + para[:sc.start()].count("\n")
                    bad.append(f"{spec}:{n}: {sc.group(1)} names no FR and is not marked `(spec-wide)`")
            line += para.count("\n") + 2
    for fr in sorted(frs - covered):
        n = next(m.start() for m in _DEF.finditer(text) if _def_id(m) == fr)
        bad.append(f"{spec}:{text[:n].count(chr(10)) + 1}: {fr} is named by no success criterion")
    return bad


def check_stale_tasks(spec: pathlib.Path, tasks: pathlib.Path) -> list[str]:
    """Check 4 - a task list citing an id the spec does not have."""
    have = {_def_id(m) for m in _DEF.finditer(spec.read_text())}
    body, bad = tasks.read_text(), []
    for m in _ID.finditer(body):
        if m.group(0) not in have:
            bad.append(f"{tasks}:{body[:m.start()].count(chr(10)) + 1}: cites {m.group(0)}, which "
                       f"{spec.name} does not define")
    return bad


def lint(spec_dir: pathlib.Path, specs_root: pathlib.Path | None = None,
         tree_root: pathlib.Path | None = None) -> list[str]:
    """Every complaint about one `specs/NNN-*/` directory.

    `tree_root` is what check 2 scans - the repository, not the spec directory - and defaults to the
    parent of `specs/`.
    """
    spec_dir = pathlib.Path(spec_dir)
    specs_root = specs_root or spec_dir.parent
    spec = spec_dir / "spec.md"
    if not spec.is_file():
        return []
    tasks = spec_dir / "tasks.md"
    bad = check_withdrawn(spec_dir, specs_root, tree_root)   # check 2 needs no tasks.md
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
        # a requirement declared as `**FR-001 Its title.**` is the same declaration
        titled = good.replace("**FR-001** A thing.", "**FR-001 A thing.** With a title in the bold span.")
        (d / "spec.md").write_text(titled)
        assert lint(d) == [], lint(d)
        (d / "spec.md").write_text(titled.replace("**SC-001** (FR-001, FR-001a) Both hold.", "**SC-001** (FR-001) One holds."))
        assert any("FR-001a is named by no success criterion" in x for x in lint(d)), "the titled form must still be checked for orphans"
        (d / "spec.md").write_text(good)
        # a declaration may be a LIST ITEM and its bold span may wrap a line
        listed = good.replace("**SC-001** (FR-001, FR-001a) Both hold.", "- **SC-001 Both hold.** (FR-001, FR-001a)")
        listed = listed.replace("**SC-002** (spec-wide) The gate is green.", "- **SC-002** (spec-wide) The gate is green.")
        (d / "spec.md").write_text(listed)
        assert lint(d) == [], lint(d)
        wrapped = good.replace("**FR-001a** Another.", "**FR-001a A title that\nwraps a line.** Another.")
        (d / "spec.md").write_text(wrapped)
        assert lint(d) == [], lint(d)
        (d / "spec.md").write_text(good)
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
        bad += lint(d, tree_root=pathlib.Path(dirs[0]).resolve().parents[1])
    if not bad:
        return 0
    print("\n".join(bad))
    print("\nspec-lint: " + str(len(bad)) + " finding(s). Each is a thing a review round would "
          "otherwise spend itself on (feature 236, the GM: mistakes caught early and cheaply).")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
