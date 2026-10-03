#!/usr/bin/env python3
"""The claims INDEX: per research claim of the engine and the Mode A procedures, what the last check found (feature 316).

WHY (GM 2026-10-02): *"having an index of which things our sub-agent checks have shown to be valid and which ones are known to
not be valid ... there would always be an up-to-date index"*, and *"when the implementation changes then our tooling knows
which specific functions need to be fed to subagents to kind of redo the checks"*. A claim is a `Research:` line in a docstring
(`l7r/diagram/tools/claims.py` reads them, and fingerprints each unit's CODE); this script fingerprints the RESEARCH each claim
cites, keeps the committed index (`dev/claims-index.json`), and answers every question asked of it:

    _claims.py owed                          every unit with no row or a stale one, and why; the bundle command per module
    _claims.py bundle (--owed | --module P | --units K,K) [--out DIR] [--reason WHY]
                                             the files `impl-drift` reads, copied out of the repository (a unit not owed: REASON)
    _claims.py record --bundle DIR --reply FILE
                                             the check's `VERDICT` and `UNCLAIMED` lines into the index, at what it read
    _claims.py report                        counts by verdict, then every finding and every UNRESEARCHED claim
    _claims.py gate                          what the push refuses (owed, or a finding the delta introduced) and warns

THE RESEARCH FINGERPRINT (spec FR-004 b): a cited question's heading and the words of its blocks less its intro - the reading
`_entry_owed.findings` and feature 311 make, so an intro, a comment or a re-wrap owes nothing. GUESS, UNRESEARCHED, CONVENTION
and NONE cite nothing and have none.

INTRODUCED OR PRE-EXISTING (spec FR-010, plan D7). A finding at the head is INTRODUCED when the merge base's index held its unit
IN-STEP, or held no row AND the delta changed the unit's code or a cited question's findings. The code is asked ACROSS KEYS: a
unit's core carries no name of its own, so a unit renamed or moved with its code intact matches a base unit that no longer
exists at the head. A finding at both ends is pre-existing whatever changed; a pre-existing finding is a warning.
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True  # the push runs this in fixture trees whose `git status` must stay clean
import _record_units as ru  # noqa: E402

SKILL = ".claude/skills/diagram"
INDEX = f"{SKILL}/dev/claims-index.json"
QUESTIONS = f"{SKILL}/research/questions"
FINDINGS = ("DRIFTED", "NEEDS-RESEARCH", "MISLABELED", "UNCLAIMED", "CANNOT-TELL")
VERDICTS = ("IN-STEP", *FINDINGS)
DEFAULT_OUT = Path("/tmp/l7r-check")
#: What the base read needs: the engine, the procedure documents and the questions.
BASE_PATHS = (f"{SKILL}/l7r", f"{SKILL}/buildings.md", f"{SKILL}/buildings", QUESTIONS)
_VERDICT = re.compile(r"^VERDICT\s+(\S.*?)\s+(" + "|".join(VERDICTS) + r")\s+-\s+(.*)$")
_UNCLAIMED = re.compile(r"^UNCLAIMED\s+(\S+?::\S.*?)\s+-\s+(.*)$")


def _git(root: Path, *args: str) -> str | None:
    p = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=False)
    return p.stdout if p.returncode == 0 else None


def engine(skill: Path) -> Any:  # noqa: ANN401 - the engine's claims reader, imported from the tree asked about
    if str(skill) not in sys.path:
        sys.path.insert(0, str(skill))
    from l7r.diagram.tools import claims  # noqa: PLC0415

    return claims


def findings_of(page_text: str) -> str:
    """The digest of what a claim is checked against: a question's heading and its non-intro blocks' words."""
    page = ru.read_page(page_text)
    return ru.digest([page.heading, *(b.words for b in page.blocks if not b.intro)])


def research_fp(pointers: Sequence[str], qdir: Path, memo: dict[str, str] | None = None) -> str:
    """The research fingerprint of one claim's pointers (empty for a class claim); a missing file is `missing`."""
    if not pointers:
        return ""
    memo = {} if memo is None else memo
    parts = []
    for ptr in pointers:
        name = ptr.rsplit("/", 1)[1]
        if name not in memo:
            f = qdir / name
            memo[name] = findings_of(f.read_text(encoding="utf-8")) if f.is_file() else "missing"
        parts.append(memo[name])
    return ru.digest(parts)


@dataclass
class Row:
    """One unit as the tree holds it now: its key, the unit, its claim (None for an UNCLAIMED row), and its fingerprints."""

    key: str
    unit: Any
    claim: Any
    code: str
    research: str

    @property
    def uid(self) -> str:
        return f"{self.unit.path}::{self.unit.qualname}"


def current(skill: Path, qdir: Path | None = None) -> dict[str, Row]:
    """key -> Row for every claim of every unit in scope, at the tree under `skill` (its questions under `qdir`)."""
    cl = engine(Path(__file__).resolve().parents[1] / SKILL)
    qdir = qdir if qdir is not None else skill / "research" / "questions"
    memo: dict[str, str] = {}
    out: dict[str, Row] = {}
    for unit, _errors in cl.all_units(skill):
        for claim in unit.claims:
            key = unit.key(claim)
            out[key] = Row(key, unit, claim, unit.code(claim), research_fp(claim.pointers, qdir, memo))
    return out


def load_index(path: Path) -> dict[str, dict[str, str]]:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def save_index(path: Path, rows: dict[str, dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(sorted(rows.items())), indent=1, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def owed(cur: dict[str, Row], index: dict[str, dict[str, str]]) -> list[tuple[str, str]]:
    """(key, why) for every claim with no row or whose code or research moved since its row (spec FR-006)."""
    out: list[tuple[str, str]] = []
    for key, row in sorted(cur.items()):
        was = index.get(key)
        if was is None:
            out.append((key, "new"))
        elif was.get("code") != row.code:
            out.append((key, "code changed"))
        elif was.get("research") != row.research:
            out.append((key, "research changed"))
    return out


def live_rows(cur: dict[str, Row], index: dict[str, dict[str, str]]) -> dict[str, dict[str, str]]:
    """The index rows that still speak of something: a claim in scope, or an UNCLAIMED row whose unit still exists."""
    uids = {r.uid for r in cur.values()}
    return {k: v for k, v in index.items() if k in cur or (v.get("verdict") == "UNCLAIMED" and k.rsplit("#", 1)[0] in uids)}


# ---- the bundle --------------------------------------------------------------------------------------------------


def _source(root: Path, unit: Any) -> str:  # noqa: ANN401
    """A unit's lines, with the comment block directly above it (a constant's why lives there)."""
    lines = (root / unit.path).read_text(encoding="utf-8").split("\n")
    start = unit.lineno - 1
    while start > 0 and lines[start - 1].lstrip().startswith(("#", "@")):
        start -= 1
    end = unit.end_lineno
    if unit.kind == "class":  # its own statements only: each method is a unit of its own, shown under its own heading
        indent = len(lines[unit.lineno - 1]) - len(lines[unit.lineno - 1].lstrip())
        for k in range(unit.lineno, unit.end_lineno):
            st = lines[k].lstrip()
            if st.startswith(("def ", "async def ", "class ", "@")) and len(lines[k]) - len(st) > indent:
                end = k
                break
    if unit.kind == "constant" and end < len(lines) and lines[end].lstrip().startswith(('"""', "'''", '"', "'")):
        while end < len(lines) and lines[end].strip():  # the claim literal after it
            end += 1
    return "\n".join(lines[start:end])


def bundle(root: Path, cur: dict[str, Row], keys: Sequence[str], out: Path) -> Path:
    """Write the bundle for `keys` (rows of `cur`) under `out`: MANIFEST.md with every source and question inline, and
    units.json with the fingerprints the check reads - what `record` writes into the index (spec FR-007)."""
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    by_uid: dict[str, list[Row]] = {}
    for k in keys:
        by_uid.setdefault(cur[k].uid, []).append(cur[k])
    qdir = root / QUESTIONS
    cited: list[str] = []
    parts = [
        "# Bundle for impl-drift (feature 316)\n",
        "owed-checks: impl-drift\n",
        "Each UNIT below is a function, method, class, constant or procedure section with its CLAIMS. Judge each claim against "
        "the questions it cites (inline at the end) and report one `VERDICT <key> <IN-STEP|DRIFTED|NEEDS-RESEARCH|MISLABELED|"
        "CANNOT-TELL> - <note>` line per KEY, plus `UNCLAIMED <path>::<qualname> - <decision>` for a physical decision in a "
        "unit's code that no claim covers.\n",
    ]
    for uid, rows in by_uid.items():
        unit = rows[0].unit
        lang = "markdown" if unit.kind == "section" else "python"
        parts.append(f"## UNIT {uid} ({unit.kind}, {unit.path}:{unit.lineno})\n")
        for r in rows:
            parts.append(f"- KEY `{r.key}`: `{r.claim.line}`" + (" (inherited from the module docstring)" if unit.inherited else ""))
        if unit.names:
            parts.append("- constants it reads: " + "; ".join(f"`{n}`" for n in unit.names))
        parts.append(f"\n```{lang}\n{_source(root, unit)}\n```\n")
        # every page ANY claim of the unit cites, owed or not: an UNRESEARCHED or GUESS claim cites nothing, and its check
        # can only see a page that answers it if the unit's other claims bring it (the torii re-check, 2026-10-03)
        for c in unit.claims:
            for ptr in c.pointers:
                name = ptr.rsplit("/", 1)[1]
                if name not in cited and (qdir / name).is_file():
                    cited.append(name)
    # THE QUESTIONS ARE FILES BESIDE THE MANIFEST, as their reader meets them (heading and blocks, intro marked, no markup),
    # each once however many units cite it: inline whole pages made the audit's per-file bundles 23 MB (measured 2026-10-03)
    (out / "questions").mkdir()
    parts.append("# The cited questions\n\nEach is a file under `questions/` beside this MANIFEST - read each one a unit cites, once:\n")
    for name in cited:
        page = ru.read_page((qdir / name).read_text(encoding="utf-8"))
        body = "\n\n".join(("[intro] " if b.intro else "") + b.words for b in page.blocks)
        (out / "questions" / f"{name}.txt").write_text(f"# {page.heading}\n({QUESTIONS}/{name})\n\n{body}\n", encoding="utf-8")
        parts.append(f"- `questions/{name}.txt` - {page.heading}")
    (out / "MANIFEST.md").write_text("\n".join(parts) + "\n", encoding="utf-8")
    units = {k: {"code": cur[k].code, "core": cur[k].unit.core, "research": cur[k].research, "uid": cur[k].uid} for k in keys}
    (out / "units.json").write_text(json.dumps(units, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return out / "MANIFEST.md"


# ---- recording a verdict -------------------------------------------------------------------------------------------


def parse_reply(text: str) -> tuple[dict[str, tuple[str, str]], list[tuple[str, str]]]:
    """({key: (verdict, note)}, [(uid, decision)]) from a check's reply."""
    verdicts: dict[str, tuple[str, str]] = {}
    unclaimed: list[tuple[str, str]] = []
    for raw in text.split("\n"):
        line = raw.strip().strip("`")
        if m := _VERDICT.match(line):
            verdicts[m.group(1).strip("`")] = (m.group(2), m.group(3).strip())
        elif m := _UNCLAIMED.match(line):
            unclaimed.append((m.group(1).strip("`"), m.group(2).strip()))
    return verdicts, unclaimed


def record(index: dict[str, dict[str, str]], units: dict[str, dict[str, str]], reply: str, today: str) -> tuple[dict[str, dict[str, str]], list[str]]:
    """The index with a check's reply applied, and the messages for the session (spec FR-009). A key not in the bundle is
    refused; a bundle key the reply gives no verdict stays owed; an UNCLAIMED finding is a row of its own, and a unit's earlier
    UNCLAIMED rows are dropped when this check of its claims does not report them again."""
    verdicts, unclaimed = parse_reply(reply)
    msgs: list[str] = []
    out = dict(index)
    for key in sorted(set(verdicts) - set(units)):
        msgs.append(f"refused: `{key}` is not a unit of this bundle")
    uids_checked = {u["uid"] for u in units.values()}
    for key in [k for k, v in out.items() if v.get("verdict") == "UNCLAIMED" and k.rsplit("#", 1)[0] in uids_checked]:
        del out[key]
    for key, fp in sorted(units.items()):
        if key not in verdicts:
            msgs.append(f"no verdict for `{key}` - it stays owed")
            continue
        verdict, note = verdicts[key]
        out[key] = {"verdict": verdict, "code": fp["code"], "core": fp["core"], "research": fp["research"], "date": today, "note": note}
    cores = {u["uid"]: u["core"] for u in units.values()}
    for uid, decision in unclaimed:
        if uid not in cores:
            msgs.append(f"refused: UNCLAIMED `{uid}` is not a unit of this bundle")
            continue
        out[f"{uid}#{decision}"] = {"verdict": "UNCLAIMED", "code": cores[uid], "core": cores[uid], "research": "", "date": today, "note": decision}
        msgs.append(f"UNCLAIMED {uid} - {decision}: write a claim for it, then check it")
    return out, msgs


# ---- the report and the gate ---------------------------------------------------------------------------------------


def split_units(text: str) -> list[str]:
    """UNITS="<key>,<key>" as keys. A claim's name may hold a comma ("walls, gate and empty court"), so a comma
    splits only where the next piece starts a new key (it holds the `::` of a path)."""
    return [k.strip() for k in re.split(r",(?=[^,]*::)", text.strip().rstrip(",")) if k.strip()]


def report(cur: dict[str, Row], index: dict[str, dict[str, str]]) -> str:
    """Counts by verdict, the owed count, then every finding and every UNRESEARCHED claim (spec FR-011)."""
    rows = live_rows(cur, index)
    due = owed(cur, index)
    counts = Counter(v["verdict"] for v in rows.values())
    tally = ", ".join(f"{v} {counts[v]}" for v in VERDICTS if counts[v]) or "no verdicts yet"
    lines = [f"claims: {len(cur)} in scope; {tally}; owed {len(due)}"]
    for key, v in sorted(rows.items()):
        if v["verdict"] != "IN-STEP":
            lines.append(f"  {v['verdict']:<14} {key} - {v.get('note', '')}")
    unres = sorted(k for k, r in cur.items() if r.claim.backing == "UNRESEARCHED")
    if unres:
        lines.append(f"UNRESEARCHED claims (the open research): {len(unres)}")
        lines += [f"  {k}" for k in unres]
    return "\n".join(lines)


def base_tree(root: Path, base: str, into: Path) -> Path:
    """The engine, procedures and questions at `base`, extracted under `into`; returns the skill directory there."""
    archive = subprocess.run(["git", "-C", str(root), "archive", "--format=tar", base, "--", *BASE_PATHS], capture_output=True, check=False)
    if archive.returncode == 0:
        tar = into / "base.tar"
        tar.write_bytes(archive.stdout)
        with tarfile.open(tar) as t:
            t.extractall(into, filter="data")
    (into / SKILL / "l7r" / "diagram" / "hamletgen").mkdir(parents=True, exist_ok=True)
    return into / SKILL


def base_cores(skill: Path) -> dict[str, str]:
    """uid -> core for EVERY unit at a tree, claimed or not: the base the push compares with may hold no claims at all (this
    feature's own landing, where main has none), and a unit's code is the same whatever its claims say."""
    cl = engine(Path(__file__).resolve().parents[1] / SKILL)
    return {f"{u.path}::{u.qualname}": u.core for u, _errors in cl.all_units(skill, every_module_unit=True)}


def classify(cur: dict[str, Row], index: dict[str, dict[str, str]], base_index: dict[str, dict[str, str]], cores: dict[str, str], base_qdir: Path) -> tuple[list[str], list[str]]:
    """(introduced, pre-existing) finding lines (spec FR-010). `cores` is every unit's core at the merge base (`base_cores`),
    `base_qdir` the base's questions: a first finding is introduced only when its unit's code matches no base unit's (its own
    key's, or one gone at the head - a rename or a move) or its claim's cited findings differ from the base's."""
    head_uids = {r.uid for r in cur.values()}
    gone_cores = {core for uid, core in cores.items() if uid not in head_uids}
    memo: dict[str, str] = {}
    intro: list[str] = []
    pre: list[str] = []
    for key, v in sorted(live_rows(cur, index).items()):
        if v["verdict"] not in FINDINGS:
            continue
        was = base_index.get(key)
        line = f"{v['verdict']:<14} {key} - {v.get('note', '')}"
        if was is not None:
            (pre if was.get("verdict") in FINDINGS else intro).append(line)
            continue
        uid, core = key.rsplit("#", 1)[0], v.get("core", "")
        code_changed = not (cores.get(uid) == core or core in gone_cores)
        research_changed = key in cur and research_fp(cur[key].claim.pointers, base_qdir, memo) != cur[key].research
        (intro if code_changed or research_changed else pre).append(line)
    return intro, pre


def gate(root: Path) -> tuple[list[str], list[str]]:
    """(refusals, warnings) for the push: owed units, introduced findings; pre-existing findings warn."""
    skill = root / SKILL
    cur = current(skill)
    index = load_index(root / INDEX)
    due = owed(cur, index)
    refuse = [f"owed ({why}): {key}" for key, why in due]
    mb = (_git(root, "merge-base", "HEAD", "origin/main") or _git(root, "rev-parse", "HEAD") or "").strip()
    base_index = json.loads(_git(root, "show", f"{mb}:{INDEX}") or "{}") if mb else {}
    with tempfile.TemporaryDirectory() as tmp:
        bskill = base_tree(root, mb, Path(tmp)) if mb else Path(tmp)
        cores = base_cores(bskill) if mb else {}
        intro, pre = classify(cur, index, base_index, cores, bskill / "research" / "questions")
    return refuse + [f"introduced: {x}" for x in intro], [f"pre-existing: {x}" for x in pre]


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("owed")
    b = sub.add_parser("bundle")
    b.add_argument("--owed", action="store_true")
    b.add_argument("--module", default="")
    b.add_argument("--units", default="")
    b.add_argument("--out", default="")
    b.add_argument("--reason", default="")
    r = sub.add_parser("record")
    r.add_argument("--bundle", required=True)
    r.add_argument("--reply", required=True)
    sub.add_parser("report")
    sub.add_parser("gate")
    cv = sub.add_parser("coverage")
    cv.add_argument("--path", default="", help="only units whose file path contains this")
    ap.add_argument("--root", default=".")
    args = ap.parse_args(argv)
    root = Path((_git(Path(args.root), "rev-parse", "--show-toplevel") or args.root).strip())
    if args.cmd == "gate":
        refuse, warn = gate(root)
        for w in warn:
            print(f"claims-gate: {w}")
        for x in refuse:
            print(f"claims-gate: REFUSED {x}")
        return 1 if refuse else 0
    if args.cmd == "coverage":
        cl = engine(root / SKILL)
        qs = {p.name for p in (root / QUESTIONS).glob("*.html")}
        probs = [x for x in cl.coverage(cl.all_units(root / SKILL), qs) if args.path in x.split(" ", 1)[0]]
        print("\n".join(probs) if probs else f"claims-coverage: every unit{' under ' + args.path if args.path else ''} carries a claim")
        if probs:
            print(f"claims-coverage: {len(probs)} problem(s). The form: {cl.GRAMMAR}")
        return 1 if probs else 0
    cur = current(root / SKILL)
    index = load_index(root / INDEX)
    if args.cmd == "owed":
        due = owed(cur, index)
        if not due:
            print("claims-owed: no claim is owed")
            return 0
        mods = Counter(cur[k].unit.path for k, _w in due)
        for key, why in due:
            print(f"{why:<16} {key}")
        print(f"claims-owed: {len(due)} claim(s) in {len(mods)} file(s); bundle per file with `make claims-bundle MODULE=<path>`, or OWED=1 for all")
        return 0
    if args.cmd == "report":
        print(report(cur, index))
        return 0
    if args.cmd == "bundle":
        due = dict(owed(cur, index))
        if args.owed:
            keys = sorted(due)
        elif args.module:
            keys = sorted(k for k, row in cur.items() if row.unit.path == args.module or row.unit.path.endswith("/" + args.module))
        else:
            keys = split_units(args.units)
        unknown = [k for k in keys if k not in cur]
        if unknown or not keys:
            print(f"claims-bundle: no such claim(s): {', '.join(unknown) or '(none selected)'}", file=sys.stderr)
            return 2
        not_owed = [k for k in keys if k not in due]
        if not_owed and len(args.reason.split()) < 2:
            print(f"claims-bundle: {len(not_owed)} of these claims are not owed (first: {not_owed[0]}); a re-check needs REASON=\"<why>\"", file=sys.stderr)
            return 3
        slug = re.sub(r"[^a-z0-9]+", "-", (args.module or ("owed" if args.owed else keys[0])).lower()).strip("-")[-60:]
        out = Path(args.out) if args.out else DEFAULT_OUT / f"claims-{slug}"
        print(bundle(root, cur, keys, out))
        if not_owed:
            print(f"claims-bundle: re-check of {len(not_owed)} claim(s) not owed, because: {args.reason}")
        return 0
    units = json.loads((Path(args.bundle) / "units.json").read_text(encoding="utf-8"))
    reply = Path(args.reply).read_text(encoding="utf-8")
    new, msgs = record(index, units, reply, datetime.date.today().isoformat())
    save_index(root / INDEX, live_rows(cur, new))
    for m in msgs:
        print(f"claims-checked: {m}")
    print(f"claims-checked: {sum(1 for k in units if k in new and new[k].get('code') == units[k]['code'])} of {len(units)} recorded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
