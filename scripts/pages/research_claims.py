#!/usr/bin/env python3
"""The research claims sign-up sheet, claimed and asked through one tool - never opened by hand (feature 376).

    research_claims.py claim <questions> --feature N [--status S] [--release OWNER --why W]   `make research-claim`
    research_claims.py query <questions>                                                     `make research-claims`
    research_claims.py sweep                                       release every live claim of a closed feature, one line each

WHY (the GM, 2026-10-10, specs/376-research-group-fixed-costs/request.md): *"any time we have a process that requires
editing a potentially large file, then we should use tooling to edit the file ... the same sensibility that is why we
have a make target for doing a task tick"*. Parallel research sessions share `/diagram/.clones/RESEARCH-CLAIMS.md`: a
session says which questions it is working on and checks that nobody else holds them. By 2026-10-10 the sheet was 1,138
lines (170 KB), and a check by page name (`make lines KEY=<page>`) returned a median of 4,147 characters, carried on
every later turn - about 16 M tokens across the research groups after feature 274 (376's spec).

A LINE keeps the sheet's own shape, `<owner> | <feature> | <item> | <status> | <date>`; a new one names its questions
as `Q=0060,0246`. A line names a question by any 4-digit number in its item, or by an old `<page>/<NNN>` or
`<page> <NNN>` (`PAGE=<page> SECTION=<NNN>` too) mapped through `research/moved-303.json`.

A claim is LIVE while it is the latest line of its owner naming that question and that line carries none of `done`,
`released`, `landed`, `complete` or `withdrawn` after its owner (the spec: "an old line counts as live unless a later line
for the same owner and item says it is done" - old lines put the word in the item or a sixth field, so the whole line
is read). A forgotten claim is released by a later line: by name with a reason, or by `sweep`, which writes one release
line for each live claim whose feature `make speckit-todo` reads as closed (plan review of 376, which ruled an implicit
retirement by the feature's state outside the spec).

The OWNER is the clone's directory name, so a session cannot claim as another; another owner's stale claim is released
only by name and with a reason (`--release OWNER --why`), which the line records. A claim is read, checked and appended
under a lock on `<sheet>.lock`. Output is one line per live claim the questions touch, and one summary line.
"""

from __future__ import annotations

import argparse
import contextlib
import datetime
import fcntl
import importlib.util
import json
import os
import pathlib
import re
import subprocess
import sys

SHEET = pathlib.Path(os.environ.get("L7R_CLAIMS_SHEET", "/diagram/.clones/RESEARCH-CLAIMS.md"))
RELEASED = re.compile(r"\b(done|released|landed|complete|withdrawn)\b", re.I)
QNUM = re.compile(r"(?<![\d.])(\d{4})(?![\d])")
# an old page name and the RUN of three-digit section numbers after it - `<page> 050 110 145`, `<page>/090 080`, or
# the PAGE= / SECTION= arguments (plan review: 27 of 300 owner-question pairs sat after the first number of a run)
OLD = re.compile(r"(?:PAGE=)?([a-z][a-z-]*(?:/[a-z][a-z-]*)?)((?:(?:/|\s+SECTION=|\s*,?\s+(?:and\s+)?)\d{3}(?![\d]))+)")


def root() -> pathlib.Path:
    return pathlib.Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False).stdout.strip() or ".")


def mirror(top: pathlib.Path) -> pathlib.Path:
    return top.parent.parent if top.parent.name == ".clones" else top


def old_map(top: pathlib.Path) -> dict[tuple[str, int], str]:
    """(old page, old section number) -> the question's number, from feature 303's move record."""
    try:
        files = json.loads((top / "research" / "moved-303.json").read_text(encoding="utf-8")).get("files", {})
    except (OSError, ValueError):
        return {}
    out = {}
    for old, new in files.items():
        m, n = re.match(r"(.+)/(\d{3})-", old), re.search(r"questions/(\d{4})-", new)
        if m and n:
            out[(m.group(1), int(m.group(2)))] = n.group(1)
    return out


def questions_of(item: str, olds: dict[tuple[str, int], str]) -> set[str]:
    found = set(QNUM.findall(item))
    for page, run in OLD.findall(item):
        for num in re.findall(r"\d{3}", run):
            q = olds.get((page, int(num)))
            if q:
                found.add(q)
    return found


def parse(line: str) -> dict | None:
    parts = [p.strip() for p in line.split("|")]
    if len(parts) < 3 or line.lstrip().startswith("#"):
        return None
    return {"owner": parts[0], "feature": parts[1], "item": parts[2], "status": parts[3] if len(parts) > 3 else "",
            "date": parts[4] if len(parts) > 4 else "", "line": line.rstrip("\n")}


def _todo(top: pathlib.Path):  # noqa: ANN202 - scripts/speckit-todo.py, imported by path (its name has a hyphen)
    spec = importlib.util.spec_from_file_location("speckit_todo", top / "scripts" / "speckit-todo.py")
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    sys.modules.setdefault("speckit_todo", mod)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def settled_features(top: pathlib.Path) -> set[str]:
    """Every feature number `make speckit-todo` reads as closed in the mirror's specs/ (and this clone's)."""
    out: set[str] = set()
    try:
        todo = _todo(top)
        vocab = todo.vocabulary(top)
    except Exception:  # noqa: BLE001 - a missing speckit-todo retires nothing; the status rule still holds
        return out
    for specs in {mirror(top) / "specs", top / "specs"}:
        for d in specs.glob("[0-9][0-9][0-9]-*") if specs.is_dir() else []:
            with contextlib.suppress(Exception):
                if todo.feature(d, vocab).state in ("closed", "done - GM review pending"):
                    out.add(d.name.split("-", 1)[0])
    return out


def live(lines: list[str], top: pathlib.Path) -> dict[str, list[dict]]:
    """question -> the live claims on it (the latest line of each owner naming it, carrying no released word)."""
    olds = old_map(top)
    latest: dict[tuple[str, str], dict] = {}
    for line in lines:
        row = parse(line)
        if row is None:
            continue
        for q in questions_of(row["item"], olds):
            latest[(row["owner"], q)] = row
    out: dict[str, list[dict]] = {}
    for (_owner, q), row in latest.items():
        if RELEASED.search(row["line"].split("|", 1)[-1]):
            continue
        out.setdefault(q, []).append(row)
    return out


def sweep(top: pathlib.Path, sheet: pathlib.Path = SHEET, today: str = "") -> tuple[int, str]:
    """One release line for each live claim whose feature `make speckit-todo` reads as closed - the later line the spec
    asks for, written once, not a rule applied silently on every read."""
    today = today or datetime.date.today().isoformat()
    done = settled_features(top)
    with locked(sheet):
        held = live(read_lines(sheet), top)
        by_owner: dict[tuple[str, str], set[str]] = {}
        for q, rows in held.items():
            for r in rows:
                feat = (re.search(r"\d{3}", r["feature"]) or [""])[0]  # type: ignore[index]
                if feat and feat in done:
                    by_owner.setdefault((r["owner"], feat), set()).add(q)
        lines = [f"{o} | {f} | Q={','.join(sorted(qs))} | released by {top.name}: feature {f} is closed (make speckit-todo) | {today}"
                 for (o, f), qs in sorted(by_owner.items())]
        with open(sheet, "a", encoding="utf-8") as fh:
            fh.writelines(line + "\n" for line in lines)
    return 0, f"research-claims sweep: {len(lines)} release line(s) for {sum(len(q) for q in by_owner.values())} claim(s) of closed features"


@contextlib.contextmanager
def locked(sheet: pathlib.Path):  # noqa: ANN201
    sheet.parent.mkdir(parents=True, exist_ok=True)
    with open(f"{sheet}.lock", "a+") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


def asked(spec: str) -> list[str]:
    qs = sorted(set(re.findall(r"\d{4}", spec)))
    if not qs:
        raise SystemExit("research-claims: Q= names no question - give their numbers, e.g. Q=\"0060 0246\"")
    return qs


def show(row: dict) -> str:
    return f"  {row['owner']} | {row['feature']} | {row['item']} | {row['status']} | {row['date']}"


def read_lines(sheet: pathlib.Path) -> list[str]:
    return sheet.read_text(encoding="utf-8", errors="replace").splitlines() if sheet.is_file() else []


def query(qs: list[str], top: pathlib.Path, sheet: pathlib.Path = SHEET) -> tuple[int, str]:
    held = live(read_lines(sheet), top)
    rows = list({r["line"]: r for q in qs for r in held.get(q, [])}.values())
    if not rows:
        return 0, f"research-claims: no live claim on {' '.join(qs)}"
    return 1, "\n".join([f"research-claims: {len(rows)} live claim(s) on {' '.join(qs)}:", *map(show, rows)])


def claim(qs: list[str], feature: str, status: str, top: pathlib.Path, sheet: pathlib.Path = SHEET,
          release: str = "", why: str = "", today: str = "") -> tuple[int, str]:
    owner = top.name
    today = today or datetime.date.today().isoformat()
    with locked(sheet):
        held = live(read_lines(sheet), top)
        if release:
            if not why:
                return 2, "research-claim: RELEASE=<owner> needs WHY=\"<why the claim is stale>\" - it is written on the line"
            line = f"{release} | {feature} | Q={','.join(qs)} | released by {owner}: {why} | {today}"
        else:
            others = list({r["line"]: r for q in qs for r in held.get(q, []) if r["owner"] != owner}.values())
            if others and not RELEASED.match(status):
                return 1, "\n".join([f"research-claim: REFUSED - another session holds {len(others)} of these:", *map(show, others),
                                     "  if a claim is stale (its session gone), release it: make research-claim Q=<n> FEATURE=<f> RELEASE=<owner> WHY=\"<why>\""])
            line = f"{owner} | {feature} | Q={','.join(qs)} | {status} | {today}"
        with open(sheet, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    return 0, f"research-claim: recorded - {line}"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("op", choices=["claim", "query", "sweep"])
    ap.add_argument("questions", nargs="?", default="")
    ap.add_argument("--feature", default="")
    ap.add_argument("--status", default="in progress")
    ap.add_argument("--release", default="")
    ap.add_argument("--why", default="")
    a = ap.parse_args(argv)
    if a.op == "sweep":
        print(sweep(root())[1])
        return 0
    qs, top = asked(a.questions), root()
    if a.op == "query":
        _code, text = query(qs, top)
        print(text)
        return 0
    if not re.search(r"\d{3}", a.feature):
        print("research-claim: FEATURE=<number> is required - the feature the work belongs to", file=sys.stderr)
        return 2
    code, text = claim(qs, a.feature, a.status, top, release=a.release, why=a.why)
    print(text, file=sys.stderr if code else sys.stdout)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
