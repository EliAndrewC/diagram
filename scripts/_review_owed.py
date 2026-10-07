#!/usr/bin/env python3
"""Which review checks are OWED by this delta - the one scripted answer, keyed on OCCASIONS (feature 294).

WHY OCCASIONS (feature 294, GM 2026-10-01). Until this feature a `settlement-review` was owed for every pool map whose
manifest differed from main (feature 231), so one shared engine change owed a review of every map, every round, and every
fix moved the manifests again. The GM: *"as the number of settlements that we have in our pool grows ... This will become
quickly untenable"*; and, of the glyph review, *"something that would be run only when a new element is added to the map
and then not run it other times"* - *"a category of thing"*. So each judgment check is owed only on the occasion its answer
can change (`specs/294-settlement-review-rethink/research.md` R1 sorts every check), and "a manifest moved" owes nothing.

AN OWED UNIT is `<check>:<subject>`, reviewed on ONE map or sheet:

- `glyph-check:<class>` - an element new to a map or sheet, whatever its mark (detected: an ink class in a map's
  `ink_classes` that its manifest at the merge base lacks; a `data-kind` new to a sheet); or declared `glyph-redrawn:` /
  `placement-changed:` (the GM's tannery case: the same mark, placed by new rules). On a map NEW to the pool, only the
  classes new to the whole pool's legend are owed (spec Edge Cases).
- `settlement-review:<map>` - a map new to the pool (detected), or declared `new-form:` / `new-tier:`.
- `building-review:<sheet>` - a Mode A sheet new to the pool (detected), or declared `layout-revised:` / `new-program:`.
- `size-audit:<kind>` - a `data-kind` new to a sheet (detected), or declared `new-program:`.
- `fix-check:<map>` - declared `gm-fix:` (a feature closing a defect the GM reported by eye).

DECLARED OCCASIONS live in an `## Occasions` section of each active feature's `tasks.md`, one `- <kind>: <argument>` line
each, or `- none: <why>`. Whether a redraw or a rule change is SUBSTANTIAL is the feature's call to declare; a delta that
touches drawing or placement code with NO `## Occasions` section anywhere is refused (`--check-declared`, asked by
`review-gate.sh` at push) - an undeclared re-placement is exactly the silent case the tannery example rules out.

Usage: _review_owed.py [--root DIR] [--why | --units | --check-declared]
  prints one unit slug per line (empty when nothing is owed); `--why` the one-line ruling; `--units` a tab-separated line
  per unit (slug, check, subject, the map or sheet it is reviewed on, the occasion); `--check-declared` exits 1 naming the
  touched code when no active feature declares its occasions. Exit 1 when DIR is not a git repository.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

SKILL = ".claude/skills/diagram"
TREES = ("pool", "legacy-hand-authored-pool")
#: git pathspecs for every manifest in both pool trees (fnmatch without FNM_PATHNAME: `*` spans `/`)
MANIFESTS = tuple(f"{SKILL}/{tree}/*/*/*.json" for tree in TREES)
#: the checks an occasion can owe, in the order a session dispatches them
CHECKS = ("settlement-review", "building-review", "glyph-check", "size-audit", "fix-check")
#: the declarable occasions and the check each owes (`new-program` owes two)
DECLARED = {
    "glyph-redrawn": ("glyph-check",),
    "placement-changed": ("glyph-check",),
    "new-form": ("settlement-review",),
    "new-tier": ("settlement-review",),
    "layout-revised": ("building-review",),
    "new-program": ("building-review", "size-audit"),
    "gm-fix": ("fix-check",),
    "none": (),
}
#: ink-census keys that are not elements: unclassed ink and the place caption
NOT_ELEMENTS = frozenset({"-", "place"})
_DATA_KIND = re.compile(r'data-kind="([^"]+)"')
_OCCASION = re.compile(r"^\s*-\s*(?P<kind>[a-z-]+)\s*:\s*(?P<arg>.+?)\s*$")
#: drawing or placement code - a change here must declare its occasions (D2)
_CODE = re.compile(rf"^{re.escape(SKILL)}/(l7r/.+\.py|(pool|legacy-hand-authored-pool)/.+\.(gen\.py|svg))$")


@dataclass(frozen=True)
class Unit:
    check: str
    subject: str
    on: str  # the map or sheet the check looks at ("" when nothing draws the subject)
    occasion: str

    @property
    def slug(self) -> str:
        """The unit's file-safe name: the verdict record, the snapshot folder and the dispatch's `UNIT:` line use it."""
        return f"{self.check}--{re.sub(r'[^A-Za-z0-9]+', '-', self.subject).strip('-').lower()}"


def _git(root: Path, *args: str) -> str | None:
    """stdout of `git -C root args`, or None when git refused."""
    p = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=False)
    return p.stdout.strip() if p.returncode == 0 else None


def base_of(root: Path) -> tuple[str, str]:
    """(ref, description): the merge base of HEAD with origin/main; HEAD when there is no origin/main;
    '' for a repository with no commits (everything present is then new)."""
    head = _git(root, "rev-parse", "--verify", "-q", "HEAD")
    if not head:
        return "", "no commits yet"
    if _git(root, "rev-parse", "--verify", "-q", "origin/main"):
        mb = _git(root, "merge-base", "HEAD", "origin/main")
        if mb:
            return mb, f"origin/main (merge base {mb[:8]})"
    return head, f"HEAD ({head[:8]}; no origin/main)"


def pool_map_names(root: Path) -> list[str]:
    """Every map or sheet folder of both pool trees (feature 248 FR-001: a dispatch is counted against all of them)."""
    names: set[str] = set()
    for tree in TREES:
        for d in (root / SKILL / tree).glob("*/*"):
            if d.is_dir() and ((d / f"{d.name}.json").is_file() or (d / f"{d.name}.gen.py").is_file() or (d / f"{d.name}.svg").is_file()):
                names.add(d.name)
    return sorted(names)


def _folders(root: Path) -> list[Path]:
    """Every map/sheet folder, the live pool first (a check looks at a live map before a legacy one), then by name."""
    out: list[Path] = []
    for tree in TREES:
        out += sorted(d for d in (root / SKILL / tree).glob("*/*") if d.is_dir())
    return out


def is_sheet(folder: Path) -> bool:
    """A Mode A sheet: an SVG and no manifest (a Mode B map carries `<name>.json`)."""
    return not (folder / f"{folder.name}.json").is_file() and ((folder / f"{folder.name}.svg").is_file() or (folder / f"{folder.name}.gen.py").is_file())


def exempt(folder: Path) -> bool:
    """A hand-drawn Mode B map awaiting conversion owes no review; a Mode A sheet keeps its review wherever it lives (the GM's
    ruling of 2026-10-01, feature 294, quoted in `dev/reviews.md`): a folder in the legacy tree that is not a Mode A sheet."""
    return folder.parent.parent.name == TREES[1] and not is_sheet(folder)


def _rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _at_base(root: Path, base: str, path: Path) -> str | None:
    """The file's text at the merge base, or - for an untracked render (a generated sheet's gitignored SVG) - main's mirror
    copy beside `.clones/`; None when neither has it."""
    if base:
        text = _git(root, "show", f"{base}:{_rel(root, path)}")
        if text is not None:
            return text
    if ".clones" in root.parts:
        mirror = Path(*root.parts[: root.parts.index(".clones")]) / _rel(root, path)
        if mirror.is_file():
            return mirror.read_text(errors="replace")
    return None


def _existed(root: Path, base: str, folder: Path) -> bool:
    """Did this map/sheet folder exist at the merge base (any file of it tracked there)?"""
    return bool(base) and bool(_git(root, "ls-tree", "--name-only", base, f"{_rel(root, folder)}/"))


def ink_classes(text: str | None) -> set[str]:
    """The element classes a manifest's ink census names (`ink_classes`, feature 200's census), or none."""
    try:
        census = json.loads(text or "").get("ink_classes") or {}
    except (ValueError, AttributeError):
        return set()
    return {str(k) for k in census if str(k) not in NOT_ELEMENTS} if isinstance(census, dict) else set()


def sheet_kinds(text: str | None) -> set[str]:
    """The `data-kind`s a Mode A sheet's SVG tags."""
    return set(_DATA_KIND.findall(text or ""))


def legends(root: Path) -> dict[str, set[str]]:
    """Each folder's elements now (`<name>` -> classes or kinds)."""
    out: dict[str, set[str]] = {}
    for d in _folders(root):
        if exempt(d):
            continue
        if (d / f"{d.name}.json").is_file():
            out[d.name] = ink_classes((d / f"{d.name}.json").read_text(errors="replace"))
        elif (d / f"{d.name}.svg").is_file():
            out[d.name] = sheet_kinds((d / f"{d.name}.svg").read_text(errors="replace"))
    return out


def first_drawing(root: Path, element: str) -> str:
    """The first map or sheet (live pool first) whose legend has `element`, or ''."""
    for name, classes in legends(root).items():
        if element in classes:
            return name
    return ""


def detected(root: Path, base: str) -> list[Unit]:
    """The occasions the delta itself shows: maps and sheets new to the pool, and elements new to a map or sheet."""
    units: list[Unit] = []
    new_folders: list[Path] = []
    before: dict[str, set[str]] = {}
    for d in _folders(root):
        manifest, svg = d / f"{d.name}.json", d / f"{d.name}.svg"
        if exempt(d):
            continue
        if not (manifest.is_file() or svg.is_file() or (d / f"{d.name}.gen.py").is_file()):
            continue
        if not _existed(root, base, d):
            new_folders.append(d)
            continue
        if manifest.is_file():
            before[d.name] = ink_classes(_at_base(root, base, manifest))
        elif svg.is_file():
            before[d.name] = sheet_kinds(_at_base(root, base, svg))
    now = legends(root)
    pool_legend = set().union(*before.values()) if before else set()
    owed_elements: dict[str, tuple[str, str]] = {}
    for d in new_folders:
        sheet = is_sheet(d)
        units.append(Unit("building-review" if sheet else "settlement-review", d.name, d.name, f"a {'sheet' if sheet else 'map'} new to the pool"))
        for element in sorted(now.get(d.name, set()) - pool_legend):
            owed_elements.setdefault(element, (d.name, f"{element!r} is new to the pool's legend (on the new {'sheet' if sheet else 'map'} {d.name})"))
    for name, was in before.items():
        for element in sorted(now.get(name, set()) - was):
            owed_elements.setdefault(element, (name, f"{element!r} is new to {name}"))
    sheets = {d.name for d in _folders(root) if is_sheet(d)}
    for element, (on, why) in sorted(owed_elements.items()):
        units.append(Unit("glyph-check", element, on, why))
        if on in sheets:
            units.append(Unit("size-audit", element, on, why))
    return units


def active_features(root: Path, base: str) -> list[str]:
    """The feature directories this delta is the work of: the pointer in `.specify/feature.json`, plus every
    `specs/NNN-*/` the delta against `base` touches (committed, staged or unstaged) that has a `tasks.md`."""
    found: set[str] = set()
    try:
        pointer = str(json.loads((root / ".specify" / "feature.json").read_text()).get("feature_directory", "")).rstrip("/")
    except (OSError, ValueError):
        pointer = ""
    # THE POINTER ONLY WHILE ITS FEATURE IS OPEN: `.specify/feature.json` outlives the feature it names, and a landed
    # feature's `## Occasions` re-declared its units on every later delta (feature 294's own copse, owed again by a tweak)
    tasks = root / pointer / "tasks.md" if pointer else None
    if tasks is not None and tasks.is_file() and re.search(r"^- \[ \]", tasks.read_text(), re.M):
        found.add(pointer)
    touched = (_git(root, "diff", "--name-only", base, "--", "specs") or "") if base else ""
    for path in touched.splitlines():
        parts = Path(path).parts
        if len(parts) >= 2 and parts[0] == "specs" and (root / "specs" / parts[1] / "tasks.md").is_file():
            # ...BUT NOT A FEATURE THAT HAD LANDED AT THE BASE: its tasks.md there with every task ticked. Its occasions were
            # owed and judged when it landed; a later record written into its folder (a measurement answering a finding) is
            # not that feature's work again (the torii tweak re-owed feature 294's four glyph checks).
            was = _git(root, "show", f"{base}:specs/{parts[1]}/tasks.md")
            if was and "- [x]" in was and not re.search(r"^- \[ \]", was, re.M):
                continue
            found.add(f"specs/{parts[1]}")
    return sorted(found)


def occasions_section(tasks_text: str) -> list[tuple[str, str]] | None:
    """The `(kind, argument)` lines of a `tasks.md`'s `## Occasions` section, or None when it has no such section."""
    m = re.search(r"^## Occasions\s*$(?P<body>.*?)(?=^## |\Z)", tasks_text, re.M | re.S)
    if not m:
        return None
    return [(o["kind"], o["arg"]) for o in map(_OCCASION.match, m["body"].splitlines()) if o]


def commit_occasions(root: Path, base: str) -> list[tuple[str, str]]:
    """The `Occasion: <kind>: <argument>` lines of the delta's own commit messages - where a TWEAK declares, a change done
    directly with no spec-kit feature to carry a `tasks.md` (GM 2026-10-01: the household shrine's torii given its second
    crossbar). Scoped to the delta by construction: a landed commit is behind the base and is never read again."""
    log = (_git(root, "log", "--format=%B", f"{base}..HEAD") or "") if base else ""
    return [(o["kind"], o["arg"]) for line in log.splitlines() if (m := re.match(r"^Occasion:\s*(.*)$", line.strip())) and (o := _OCCASION.match(f"- {m[1]}"))]


def declared(root: Path, base: str) -> tuple[list[Unit], list[str], bool]:
    """(the units the active features declare, problems with the declarations, whether any feature declares at all)."""
    units: list[Unit] = []
    problems: list[str] = []
    any_section = False
    sources: list[tuple[str, list[tuple[str, str]] | None]] = []
    for feature in active_features(root, base):
        tasks = root / feature / "tasks.md"
        sources.append((feature, occasions_section(tasks.read_text()) if tasks.is_file() else None))
    if tweak := commit_occasions(root, base):
        sources.append(("the delta's commit messages", tweak))
    for feature, lines in sources:
        if lines is None:
            continue
        any_section = True
        for kind, arg in lines:
            checks = DECLARED.get(kind)
            if checks is None:
                problems.append(f"{feature}: unknown occasion {kind!r} (one of {', '.join(DECLARED)})")
                continue
            subject = arg.split(" - ")[0].strip()
            for check in checks:
                if check == "glyph-check":
                    # GUARD_EDIT_OK: feature 328 wave 5 - `<element> on <map>` names the map the change moved: the
                    # first map drawing the class was the only choice, and every way is inked `village lane`, so a
                    # row street re-placed on Kashikawa was owed a review of Inashiro's lanes, which had not moved
                    element, _, at = subject.partition(" on ")
                    element, at = element.strip(), at.strip()
                    if at:
                        on = at if element in legends(root).get(at, set()) else ""
                        if not on:
                            problems.append(f"{feature}: {kind}: {element!r} is not drawn on {at!r}")
                    else:
                        on = first_drawing(root, element)
                        if not on:
                            problems.append(f"{feature}: {kind}: {element!r} is drawn on no pool map or sheet")
                    units.append(Unit(check, element, on, f"declared {kind} ({feature})"))
                elif kind == "new-program":
                    program, _, sheet = subject.partition(" ")
                    units.append(Unit(check, sheet.strip() if check == "building-review" else program, sheet.strip(), f"declared {kind} {program} ({feature})"))
                else:
                    units.append(Unit(check, subject, subject, f"declared {kind} ({feature})"))
    return units, problems, any_section


def owed(root: Path) -> tuple[str, list[Unit], list[str]]:
    """(the base's description, the owed units - detected and declared, deduplicated, in dispatch order, problems)."""
    base, desc = base_of(root)
    units, problems, _ = declared(root, base)
    seen: dict[str, Unit] = {}
    for u in detected(root, base) + units:
        seen.setdefault(u.slug, u)
    ordered = sorted(seen.values(), key=lambda u: (CHECKS.index(u.check), u.subject))
    return desc, ordered, problems


def touched_code(root: Path, base: str) -> list[str]:
    """Drawing or placement code the delta touches (committed, staged or unstaged against the merge base)."""
    diff = (_git(root, "diff", "--name-only", base) or "") if base else ""
    untracked = _git(root, "ls-files", "--others", "--exclude-standard") or ""
    return sorted(p for p in {*diff.splitlines(), *untracked.splitlines()} if p and _CODE.match(p) and "/tests/" not in p)


def check_declared(root: Path) -> str | None:
    """The refusal when drawing or placement code moved and no active feature declares its occasions, else None."""
    base, _ = base_of(root)
    code = touched_code(root, base)
    if not code or declared(root, base)[2]:
        return None
    shown = ", ".join(code[:5]) + (f" and {len(code) - 5} more" if len(code) > 5 else "")
    return (
        f"drawing or placement code moved ({shown}) and no active feature's tasks.md has an `## Occasions` section, nor any commit "
        f"of the delta an `Occasion:` line. Declare what the change re-places or redraws - `- placement-changed: <class>` (or `<class> on <map>` for the map it moved), "
        f"`- glyph-redrawn: <class>`, ... or `- none: <why>` in the feature's tasks.md; a tweak with no feature puts "
        f"`Occasion: glyph-redrawn: <class> - <why>` in its commit message "
        f"(feature 294: whether a change is substantial is the feature's to declare, never silent)"
    )


def ruling(desc: str, units: Sequence[Unit], problems: Sequence[str] = ()) -> str:
    """The one-line answer a person or a guard message quotes."""
    head = f"no review owed against {desc}: no occasion in the delta" if not units else f"owed against {desc}: " + "; ".join(f"{u.check}:{u.subject} on {u.on or '?'} ({u.occasion})" for u in units)
    return head + ("" if not problems else " | PROBLEMS: " + "; ".join(problems))


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".", help="the clone (default: the cwd's repository)")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--why", action="store_true", help="print the one-line ruling instead of the slugs")
    mode.add_argument("--units", action="store_true", help="print slug, check, subject, map and occasion per unit")
    mode.add_argument("--check-declared", action="store_true", help="exit 1 when code moved and no feature declares its occasions")
    args = ap.parse_args(argv)
    top = _git(Path(args.root), "rev-parse", "--show-toplevel")
    if not top:
        print(f"_review_owed: {args.root} is not a git repository", file=sys.stderr)
        return 1
    root = Path(top)
    if args.check_declared:
        refusal = check_declared(root)
        if refusal:
            print(refusal)
            return 1
        return 0
    desc, units, problems = owed(root)
    if args.why:
        print(ruling(desc, units, problems))
    elif args.units:
        for u in units:
            print("\t".join((u.slug, u.check, u.subject, u.on, u.occasion)))
    else:
        for u in units:
            print(u.slug)
    return 0


if __name__ == "__main__":
    sys.exit(main())
