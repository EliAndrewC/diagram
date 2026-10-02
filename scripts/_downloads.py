#!/usr/bin/env python3
"""The canonical download list, the GM's marked copy, ingest and sync (feature 313).

WHY (the GM, 2026-10-02, `specs/313-download-list/request.md`): the list of sources only the GM can fetch *"deserves to be
in source control somewhere"*, and the GM's working file *"should be an actual copy and not the canonical source"*. Per
entry, *"a space that is already set aside, where I can either check a box (i.e. turning `[ ]` into `[x]`)"*; the GM marks
the copy, says "ingest", and the marks are recorded here; the GM says "sync", and the copy is replaced from here.

THE FILES (plan D1). The canonical list is `research/to-download.md`; what was last imported, synced and ingested is
`research/to-download.state.json`; the GM's copy is `/host-l7r-repo/academic-sources/TO-DOWNLOAD.md`, written by `sync`
alone (`download-copy-hooks.sh` refuses a session's own write to it).

AN ENTRY (plan D2) is a `### <id>. <title>` heading - a number, or `H<n>` in the high-risk section - and the lines up to the
next heading. Directly under the heading stand a blank line and the three MARK LINES, then once marks are recorded a
`- Marks recorded <date>` line; the rest is the entry's BODY. The GM's copy is the canonical list's bytes at the last sync,
so the copy is proven lossless by comparing fingerprints, not by re-rendering.

INGEST is three-way (plan D4): the base is the canonical list at the commit last synced, so a body the GM changed is told
from a body a session changed (a pointer `make fragment-move` rewrote); a GM text edit is never recorded or dropped without
`KEEP=` or `DROP=`. SYNC refuses while the copy holds anything not ingested (plan D5). ADD takes the next number under a
host-wide lock that sees every clone (plan D6), and `check` holds the list append-only at the push (plan D11).

    _downloads.py import --gm <file> --high-risk <file>      once: the canonical list from the GM's file and 312's
    _downloads.py ingest [--keep IDS] [--drop IDS]           `make downloads-ingest`
    _downloads.py sync                                       `make downloads-sync`
    _downloads.py add <draft.md>                             `make download-add FILE=`
    _downloads.py check [--base REF]                         at the push; --selftest
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime
import difflib
import hashlib
import importlib.util
import json
import os
import pathlib
import re
import subprocess
import sys
from collections.abc import Iterable

SKILL = ".claude/skills/diagram"
CANON = f"{SKILL}/research/to-download.md"
STATE = f"{SKILL}/research/to-download.state.json"
#: The GM's copy, in the inbox `_archive.GM_DIR` names (the same environment variable moves both, for a test).
GM_COPY = pathlib.Path(os.environ.get("L7R_GM_SOURCES", "/host-l7r-repo/academic-sources")) / "TO-DOWNLOAD.md"
HIGH_RISK = "specs/312-uncited-source-catalog/high-risk-sources.md"
#: The host-wide lock and ledger an added entry's number is taken under, beside `make reserve`'s in the mirror's .specify/.
LOCK, LEDGER = "download-ids.lock", "download-ids.jsonl"

HEAD = re.compile(r"^### (H?\d+)\. ")
ANY_HEADING = re.compile(r"^#{1,3} ")
_BOX = r"\[\s*([xX]?)\s*\]"
MARK1 = re.compile(rf"^- Mark: {_BOX} downloaded \| {_BOX} partial \(abstract or excerpt\) \| {_BOX} paywalled \| {_BOX} not found\s*$")
MARK2 = re.compile(rf"^- {_BOX} Found elsewhere \(only with downloaded or partial\) - where:(.*)$")
MARK3 = re.compile(r"^- Saved as \(optional, the file's name\):(.*)$")
RECORDED = re.compile(r"^- Marks recorded (\d{4}-\d{2}-\d{2})\b.*$")
#: The section markers the import writes, so the import's sources can be re-derived from the list (SC-001).
HR_BEGIN, HR_END = "<!-- high-risk: imported from specs/312-uncited-source-catalog/high-risk-sources.md -->", "<!-- high-risk: end -->"
GM_BEGIN = "<!-- imported: the GM's TO-DOWNLOAD.md from here to the end, entries given their mark lines -->"


class Refusal(Exception):
    """A refusal the command prints and exits 1 on; its message carries the fix."""


@dataclasses.dataclass(frozen=True)
class Marks:
    downloaded: bool = False
    partial: bool = False
    paywalled: bool = False
    not_found: bool = False
    elsewhere: bool = False
    where: str = ""
    saved: str = ""

    def lines(self) -> list[str]:
        b = lambda v: "x" if v else " "  # noqa: E731
        return [
            f"- Mark: [{b(self.downloaded)}] downloaded | [{b(self.partial)}] partial (abstract or excerpt) | [{b(self.paywalled)}] paywalled | [{b(self.not_found)}] not found",
            f"- [{b(self.elsewhere)}] Found elsewhere (only with downloaded or partial) - where:" + (f" {self.where}" if self.where else ""),
            "- Saved as (optional, the file's name):" + (f" {self.saved}" if self.saved else ""),
        ]

    def any(self) -> bool:
        return self.downloaded or self.partial or self.paywalled or self.not_found or self.elsewhere

    def problem(self) -> str:
        """Why these marks contradict themselves (spec FR-005), else ""."""
        if self.elsewhere and not (self.downloaded or self.partial):
            return "found elsewhere is ticked without downloaded or partial - it says where a copy you have came from"
        if self.not_found and (self.downloaded or self.partial or self.paywalled):
            return "not found is ticked with downloaded, partial or paywalled - it means nothing was found"
        return ""


def parse_marks(lines: list[str]) -> Marks | None:
    """The three mark lines, or None where they are not there in their form."""
    if len(lines) < 3:
        return None
    m1, m2, m3 = MARK1.match(lines[0]), MARK2.match(lines[1]), MARK3.match(lines[2])
    if not (m1 and m2 and m3):
        return None
    d, p, w, n = (bool(g) for g in m1.groups())
    return Marks(d, p, w, n, bool(m2.group(1)), m2.group(2).strip(), m3.group(1).strip())


@dataclasses.dataclass
class Entry:
    id: str
    heading: str
    marks: Marks | None
    recorded: str | None
    body: list[str]

    def lines(self) -> list[str]:
        if self.marks is None:
            return [self.heading, *self.body]
        return [self.heading, "", *self.marks.lines(), *([self.recorded] if self.recorded else []), *self.body]

    def body_text(self) -> str:
        return "\n".join(self.body)


Block = str | Entry


def parse(text: str) -> list[Block]:
    """The list as text runs and entries, in order; `render(parse(t)) == t` for any text."""
    blocks: list[Block] = []
    run: list[str] = []
    entry: list[str] | None = None

    def close() -> None:
        nonlocal entry
        if entry is not None:
            blocks.append(_entry(entry))
            entry = None

    for line in text.split("\n"):
        if HEAD.match(line):
            close()
            if run:
                blocks.append("\n".join(run))
                run = []
            entry = [line]
        elif entry is not None and ANY_HEADING.match(line):
            close()
            run = [line]
        elif entry is not None:
            entry.append(line)
        else:
            run.append(line)
    close()
    if run:
        blocks.append("\n".join(run))
    return blocks


def _entry(lines: list[str]) -> Entry:
    eid = HEAD.match(lines[0]).group(1)  # type: ignore[union-attr]
    marks = parse_marks(lines[2:5]) if len(lines) >= 5 and lines[1] == "" else None
    if marks is None:
        return Entry(eid, lines[0], None, None, lines[1:])
    rest = lines[5:]
    recorded = rest[0] if rest and RECORDED.match(rest[0]) else None
    return Entry(eid, lines[0], marks, recorded, rest[1:] if recorded else rest)


def render(blocks: Iterable[Block]) -> str:
    return "\n".join(b if isinstance(b, str) else "\n".join(b.lines()) for b in blocks)


def entries(blocks: Iterable[Block]) -> list[Entry]:
    return [b for b in blocks if isinstance(b, Entry)]


def by_id(blocks: Iterable[Block]) -> dict[str, Entry]:
    return {e.id: e for e in entries(blocks)}


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def today() -> str:
    return datetime.date.today().isoformat()


# --- the import -----------------------------------------------------------------------------------------------------

HEADER = """
**This is the canonical list, kept in the diagram repository (feature 313).** Your file in `academic-sources/` is a copy of
it. Mark the copy as you go; nothing else in it needs editing.

**Marking an entry.** Under each heading are three lines. Turn `[ ]` into `[x]` for what happened:

- **downloaded** - you have the whole work, saved in `academic-sources/`.
- **partial** - you have only part of it, such as the abstract or an excerpt.
- **paywalled** - it needs a paid or institutional login. It can be ticked with partial, when the abstract was free.
- **not found** - you could not find it anywhere. Tick it alone.
- **Found elsewhere** - tick it with downloaded or partial when what you have came from somewhere other than the links
  given, and write where after `where:`.
- **Saved as** is optional: the file's name, if you want to save the session matching your download to its entry.

**When you are ready, say "ingest".** The session records your marks here, archives the files you saved, and tells you
about anything it could not settle. **Say "sync"** to have your copy replaced by this list, with the entries added since
your last sync. Sync refuses while your copy holds marks that have not been ingested, so nothing you mark is lost.

New entries are only ever added at the very end of the file, never in between, so once you have worked to the end of a
part, that part stays done.
"""


def import_list(gm_text: str, high_risk_text: str) -> str:
    """The canonical list from the GM's file and 312's high-risk list (plan D3): the GM's title, the new header, the
    high-risk section (312's file with its title demoted), then the GM's file from its second line. Every entry gets its
    mark lines; entries the GM's 2026-09-13 status table settled are ticked from it (spec FR-004)."""
    gm_title, _, gm_rest = gm_text.partition("\n")
    hr_title, _, hr_rest = high_risk_text.partition("\n")
    hr_heading = "## " + hr_title.removeprefix("# ")
    text = "\n".join([gm_title, HEADER, "---", "", HR_BEGIN, hr_heading, hr_rest.rstrip("\n"), HR_END, "", "---", "", GM_BEGIN, gm_rest])
    blocks = parse(text)
    for e in entries(blocks):
        e.marks = Marks()
        if e.id in STATUS_2026_09_13:
            e.marks = STATUS_2026_09_13[e.id]
            e.recorded = "- Marks recorded 2026-09-13 (from the GM's status table at the top of Part 1)"
    return render(blocks)


#: What the GM's file itself records of the GM's 2026-09-13 pass over Part 1 (its STATUS table, and entry 16's "You
#: already saved a PDF"): the files saved are downloaded; "CLOSED - unavailable" and "genuinely closed" are not found,
#: the GM having said everything missing was simply unavailable to them. Nothing else is ticked (spec FR-004).
STATUS_2026_09_13: dict[str, Marks] = {
    **{i: Marks(downloaded=True) for i in ("1", "2", "3", "4", "5", "6", "8", "12", "13", "14", "15", "16")},
    **{i: Marks(not_found=True) for i in ("7", "9", "10", "11")},
}


def unimport(canon_text: str) -> tuple[str, str]:
    """The GM's file and 312's file as the import read them, re-derived from a just-imported list (SC-001's test)."""
    blocks = parse(canon_text)
    for e in entries(blocks):
        e.marks, e.recorded = None, None
    text = render(blocks)
    title, _, rest = text.partition("\n")
    hr = rest.split(HR_BEGIN + "\n", 1)[1].split("\n" + HR_END, 1)[0]
    hr_title, _, hr_body = hr.partition("\n")
    gm = rest.split(GM_BEGIN + "\n", 1)[1]
    return title + "\n" + gm, "# " + hr_title.removeprefix("## ") + "\n" + hr_body + "\n"


# --- the state, git ----------------------------------------------------------------------------------------------------


def load_state(root: pathlib.Path) -> dict:
    path = root / STATE
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def save_state(root: pathlib.Path, state: dict) -> None:
    (root / STATE).write_text(json.dumps(state, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def git(root: pathlib.Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)


def at_commit(root: pathlib.Path, commit: str) -> str:
    done = git(root, "show", f"{commit}:{CANON}")
    if done.returncode:
        raise Refusal(f"the canonical list at {commit} cannot be read ({done.stderr.strip()}) - is the clone synced in? scripts/sync-with-main.sh sync-in")
    return done.stdout


# --- ingest --------------------------------------------------------------------------------------------------------------


@dataclasses.dataclass
class IngestResult:
    recorded: list[str] = dataclasses.field(default_factory=list)
    refused: dict[str, str] = dataclasses.field(default_factory=dict)
    pending: dict[str, str] = dataclasses.field(default_factory=dict)
    kept: list[str] = dataclasses.field(default_factory=list)
    dropped: list[str] = dataclasses.field(default_factory=list)
    unknown: list[str] = dataclasses.field(default_factory=list)
    saved: dict[str, str] = dataclasses.field(default_factory=dict)

    def clean(self) -> bool:
        return not (self.pending or self.unknown or self.refused)


def merge(canon_text: str, copy_text: str, base_text: str, date: str, keep: set[str], drop: set[str]) -> tuple[str, IngestResult]:
    """Ingest's comparison over plain texts (plan D4): the canonical list with the copy's marks recorded and the bodies
    the session was told to keep, and what happened to each entry."""
    canon_blocks = parse(canon_text)
    canon, base, copy = by_id(canon_blocks), by_id(parse(base_text)), by_id(parse(copy_text))
    out = IngestResult()
    for eid, c in copy.items():
        mine = canon.get(eid)
        if mine is None:
            out.unknown.append(eid)
            continue
        if c.marks is not None and c.marks != mine.marks:
            why = c.marks.problem()
            if why:
                out.refused[eid] = why
            else:
                mine.marks, mine.recorded = c.marks, f"- Marks recorded {date}"
                out.recorded.append(eid)
        if c.marks is not None and c.marks.saved:
            out.saved[eid] = c.marks.saved
        was = base.get(eid)
        old = (was.heading + "\n" + was.body_text()) if was else None
        if old == c.heading + "\n" + c.body_text():
            continue
        if eid in drop:
            out.dropped.append(eid)
            continue
        if eid in keep:
            mine.heading, mine.body = c.heading, c.body
            out.kept.append(eid)
            continue
        session_changed = old is not None and mine.heading + "\n" + mine.body_text() != old
        diff = "\n".join(
            difflib.unified_diff(
                (old or "").split("\n"), (c.heading + "\n" + c.body_text()).split("\n"), "at the last sync", "your copy", lineterm="", n=1
            )
        )
        out.pending[eid] = ("CONFLICT - a session changed this entry too; the canonical text is kept unless KEEP=\n" if session_changed else "") + diff
    return render(canon_blocks), out


def ingest(root: pathlib.Path, copy: pathlib.Path, keep: set[str], drop: set[str], date: str | None = None) -> IngestResult:
    state = load_state(root)
    if "synced" not in state:
        raise Refusal("the GM's copy has never been synced, so it holds no mark lines to read - run `make downloads-sync` first (on the GM's word)")
    copy_text = copy.read_text(encoding="utf-8")
    canon_path = root / CANON
    text, out = merge(canon_path.read_text(encoding="utf-8"), copy_text, at_commit(root, state["synced"]["commit"]), date or today(), keep, drop)
    canon_path.write_text(text, encoding="utf-8")
    if out.clean():
        state["ingested"] = {"sha256": sha(copy_text), "date": date or today()}
        save_state(root, state)
    return out


# --- sync -----------------------------------------------------------------------------------------------------------------


def sync(root: pathlib.Path, copy: pathlib.Path, date: str | None = None) -> str:
    """Write the canonical list over the GM's copy (plan D5); returns the commit recorded as the base."""
    state = load_state(root)
    canon_text = (root / CANON).read_text(encoding="utf-8")
    if copy.exists():
        have = sha(copy.read_text(encoding="utf-8"))
        known = {state.get(k, {}).get("sha256") for k in ("imported", "synced", "ingested")} - {None}
        if have not in known:
            raise Refusal(changed_message(copy.read_text(encoding="utf-8"), root, state))
    if git(root, "diff", "--quiet", "HEAD", "--", CANON).returncode or git(root, "ls-files", "--error-unmatch", CANON).returncode:
        raise Refusal(f"{CANON} has uncommitted changes - commit it first, so the base the next ingest compares against is a commit")
    commit = git(root, "rev-parse", "HEAD").stdout.strip()
    copy.write_text(canon_text, encoding="utf-8")
    state["synced"] = {"sha256": sha(canon_text), "date": date or today(), "commit": commit}
    save_state(root, state)
    return commit


def changed_message(copy_text: str, root: pathlib.Path, state: dict) -> str:
    """Name what the copy holds that is not in the canonical list, and how to bring it in."""
    canon = by_id(parse((root / CANON).read_text(encoding="utf-8")))
    names: list[str] = []
    for e in entries(parse(copy_text)):
        mine = canon.get(e.id)
        if mine is None:
            names.append(f"{e.id} (not in the canonical list - add it with `make download-add FILE=<draft>`, or by hand at the end if it keeps its number)")
        elif (e.marks is not None and e.marks != mine.marks) or e.body_text() != mine.body_text() or e.heading != mine.heading:
            names.append(e.id)
    first = "synced" not in state
    lead = "the GM's copy changed since the import, before any sync" if first else "the GM's copy holds changes not yet ingested"
    fix = (
        "bring each named entry into the canonical list (an added one with `make download-add`, a changed one by hand), then sync"
        if first
        else "run `make downloads-ingest` first (KEEP=/DROP= for text edits), then sync"
    )
    return f"{lead}: {', '.join(names) or 'text outside any entry'} - {fix}"


# --- add ---------------------------------------------------------------------------------------------------------------------

NEW_HEAD = re.compile(r"^### NEW\. (.+)$")
POINTER = re.compile(r"research/(?:questions/[0-9]{4}-[a-z0-9-]+(?:\.drawing)?\.html|contents\.json#[a-z0-9-]+)")


def drafts(text: str, record: pathlib.Path) -> list[tuple[str, list[str]]]:
    """The draft's entries as (title, body lines), each checked for its parts (plan D6); refuses naming what is missing."""
    out: list[tuple[str, list[str]]] = []
    for chunk in re.split(r"(?m)^(?=### NEW\. )", text):
        if not chunk.strip():
            continue
        lines = chunk.rstrip("\n").split("\n")
        m = NEW_HEAD.match(lines[0])
        if not m:
            raise Refusal("a draft entry is headed `### NEW. <the work>` - the number is given when it is appended")
        body = "\n".join(lines[1:])
        missing = [
            what
            for what, ok in (
                ("a link line `- **[...](https://...)**`", re.search(r"^- \*\*\[[^\]]+\]\(https?://", body, re.M)),
                ("`- Fallback:` with a link", re.search(r"^- Fallback: .*\]\(https?://", body, re.M)),
                ("`- **Rests on it:**`", re.search(r"^- \*\*Rests on it:\*\*", body, re.M)),
                ("`- Blocked by:`", re.search(r"^- Blocked by: \S", body, re.M)),
            )
            if not ok
        ]
        pointers = POINTER.findall(body)
        if not pointers:
            missing.append("a pointer in Rests on it (`research/questions/NNNN-<id>.html` or `research/contents.json#<section>`)")
        gone = [p for p in pointers if p.startswith("research/questions/") and not (record / p.removeprefix("research/")).is_file()]
        if gone:
            missing.append("pointers that exist (" + ", ".join(gone) + " - none such)")
        if missing:
            raise Refusal(f"draft entry {m.group(1)!r} lacks: " + "; ".join(missing))
        out.append((m.group(1), lines[1:]))
    if not out:
        raise Refusal("the draft holds no `### NEW. <the work>` entry")
    return out


def numbers_in(text: str) -> list[int]:
    return [int(e.id) for e in entries(parse(text)) if not e.id.startswith("H")]


def append(canon_text: str, new: list[Entry]) -> str:
    """The list with `new` appended at its end - the one place a new entry goes (spec FR-008)."""
    return canon_text.rstrip("\n") + "\n\n" + "\n\n".join("\n".join(e.lines()) for e in new) + "\n"


def _reserve_module():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("reserve_prefix", pathlib.Path(__file__).with_name("reserve-prefix.py"))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def add(root: pathlib.Path, draft: str, timeout: float = 30.0) -> list[str]:
    """Append the draft's entries under the next numbers, taken under the host-wide lock (plan D6); returns the ids."""
    rp = _reserve_module()
    items = drafts(draft, root / SKILL / "research")
    mirror = rp.mirror_of(root.resolve())
    ledger = mirror / ".specify" / LEDGER
    with rp.Lock(mirror / ".specify" / LOCK, timeout):
        held: list[int] = []
        clones = mirror / ".clones"
        for p in [mirror / CANON, root / CANON, *([c / CANON for c in clones.iterdir()] if clones.is_dir() else [])]:
            if p.is_file():
                held += numbers_in(p.read_text(encoding="utf-8"))
        held += [int(json.loads(line)["n"]) for line in (ledger.read_text(encoding="utf-8").splitlines() if ledger.is_file() else []) if line.strip()]
        n = max(held, default=0)
        new: list[Entry] = []
        with ledger.open("a", encoding="utf-8") as fh:
            for title, body in items:
                n += 1
                new.append(Entry(str(n), f"### {n}. {title}", Marks(), None, body))
                fh.write(json.dumps({"n": n, "clone": str(root), "utc": datetime.datetime.now(datetime.UTC).isoformat()}) + "\n")
        path = root / CANON
        path.write_text(append(path.read_text(encoding="utf-8"), new), encoding="utf-8")
    return [e.id for e in new]


# --- the push check ---------------------------------------------------------------------------------------------------------


def problems(old_text: str | None, new_text: str) -> list[str]:
    """What the push refuses in the canonical list against main's (plan D11), each naming its entry and the fix."""
    new = entries(parse(new_text))
    out: list[str] = []
    ids = [e.id for e in new]
    for eid in sorted({i for i in ids if ids.count(i) > 1}):
        out.append(f"entry {eid} appears twice - an id is never reused; give the second its own with `make download-add`")
    for e in new:
        if e.marks is None:
            out.append(f"entry {e.id} has no mark lines under its heading - the GM ticks them; `make download-add` writes them, or copy them from any entry")
    if old_text is None:
        return out
    old_ids = [e.id for e in entries(parse(old_text))]
    lost = [i for i in old_ids if i not in ids]
    if lost:
        out.append(f"entries {', '.join(lost)} are gone - an entry is never removed; the GM's marks say when one is done")
    kept = [i for i in ids if i in set(old_ids)]
    if kept != [i for i in old_ids if i in set(ids)]:
        out.append("entries are reordered against main - nothing is moved; new entries go at the end")
    old = set(old_ids)
    added = [i for i in ids if i not in old]
    tail_start = max((k for k, i in enumerate(ids) if i in old), default=-1)
    top = max((int(i) for i in old_ids if not i.startswith("H")), default=0)
    for i in added:
        if i.startswith("H") or ids.index(i) < tail_start or int(i) <= top:
            out.append(f"entry {i} is not appended at the end under a new number - `make download-add FILE=<draft>` appends it")
    return out


def check(root: pathlib.Path, base: str = "origin/main") -> list[str]:
    path = root / CANON
    if not path.is_file():
        return []
    done = git(root, "show", f"{base}:{CANON}")
    return problems(done.stdout if done.returncode == 0 else None, path.read_text(encoding="utf-8"))


def selftest() -> None:
    e = "\n".join
    one = e(["# T", "", "### 1. A", "", *Marks().lines(), "", "- body", ""])
    two = one + e(["### 2. B", "", *Marks().lines(), "", "- b", ""])
    assert render(parse(two)) == two, "parse and render are an identity"
    assert problems(one, two) == [], "an entry appended at the end passes"
    assert any("gone" in p for p in problems(two, one)), "a removed entry is refused"
    swapped = e(["# T", "", "### 2. B", "", *Marks().lines(), "", "- b", "", "### 1. A", "", *Marks().lines(), "", "- body", ""])
    assert any("reordered" in p for p in problems(two, swapped)), "a reorder is refused"
    assert any("no mark lines" in p for p in problems(one, one + "### 3. C\n\n- c\n")), "an entry without marks is refused"
    assert Marks(elsewhere=True).problem() and Marks(not_found=True, paywalled=True).problem() and not Marks(partial=True, paywalled=True).problem()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    im = sub.add_parser("import")
    im.add_argument("--gm", default=str(GM_COPY))
    im.add_argument("--high-risk", default=HIGH_RISK)
    ing = sub.add_parser("ingest")
    ing.add_argument("--keep", default="")
    ing.add_argument("--drop", default="")
    sub.add_parser("sync")
    ad = sub.add_parser("add")
    ad.add_argument("draft")
    ch = sub.add_parser("check")
    ch.add_argument("--base", default="origin/main")
    sub.add_parser("selftest")
    a = ap.parse_args(argv)
    root = pathlib.Path(git(pathlib.Path.cwd(), "rev-parse", "--show-toplevel").stdout.strip() or ".")
    try:
        return _run(a, root)
    except Refusal as r:
        print(f"downloads: REFUSED - {r}", file=sys.stderr)
        return 1


def _run(a: argparse.Namespace, root: pathlib.Path) -> int:
    if a.cmd == "selftest":
        selftest()
        return 0
    if a.cmd == "import":
        gm_text = pathlib.Path(a.gm).read_text(encoding="utf-8")
        if (root / CANON).exists():
            raise Refusal(f"{CANON} exists - the import runs once")
        (root / CANON).write_text(import_list(gm_text, (root / a.high_risk).read_text(encoding="utf-8")), encoding="utf-8")
        save_state(root, {"imported": {"sha256": sha(gm_text), "date": today()}})
        print(f"downloads: imported {len(entries(parse((root / CANON).read_text(encoding='utf-8'))))} entries into {CANON}")
        return 0
    if a.cmd == "sync":
        commit = sync(root, GM_COPY)
        print(f"downloads: the GM's copy replaced from {CANON} at {commit[:12]}; commit {STATE}")
        return 0
    if a.cmd == "add":
        draft = pathlib.Path(a.draft)
        if not draft.is_absolute() and not draft.exists():
            draft = root / a.draft
        ids = add(root, draft.read_text(encoding="utf-8"))
        print(f"downloads: appended {', '.join(ids)} to {CANON} - commit it; the GM sees it at the next sync")
        return 0
    if a.cmd == "check":
        found = check(root, a.base)
        for p in found:
            print(f"downloads: {p}", file=sys.stderr)
        return 1 if found else 0
    out = ingest(root, GM_COPY, set(a.keep.split()), set(a.drop.split()))
    code = report_ingest(out, root)
    inbox = [f"--match={name}={eid}" for eid, name in inbox_matches(out.saved, GM_COPY.parent).items()]
    done = subprocess.run([sys.executable, str(pathlib.Path(__file__).with_name("_archive_ops.py")), "inbox", *inbox], cwd=root)
    return code or done.returncode


def inbox_matches(saved: dict[str, str], inbox: pathlib.Path) -> dict[str, str]:
    """entry id -> the file its saved-as line names, for the files present in the inbox (plan D7): the GM's naming
    matches a download to its entry without a question. A name that is not there is left for the session."""
    return {eid: name for eid, name in saved.items() if name and "/" not in name and (inbox / name).exists()}


def report_ingest(out: IngestResult, root: pathlib.Path) -> int:
    print(f"downloads: ingest - marks recorded on {len(out.recorded)} entries" + (f" ({', '.join(out.recorded)})" if out.recorded else ""))
    for eid, why in out.refused.items():
        print(f"  NOT RECORDED {eid}: {why} - ask the GM which they meant")
    for eid in out.unknown:
        print(f"  NOT IN THE LIST {eid}: the GM's copy has an entry the canonical list lacks - bring it in by hand at the end")
    for eid, diff in out.pending.items():
        print(f"  TEXT EDIT {eid} - pending; KEEP={eid} records it, DROP={eid} discards it:\n{diff}")
    if out.kept or out.dropped:
        print(f"  text kept: {', '.join(out.kept) or '-'}; dropped: {', '.join(out.dropped) or '-'}")
    if out.saved:
        print("  saved-as files named: " + ", ".join(f"{k}={v}" for k, v in out.saved.items()))
    print(f"  commit {CANON} and {STATE}" + ("" if out.clean() else "; sync stays refused until nothing is pending"))
    return 0 if out.clean() else 1


if __name__ == "__main__":
    sys.exit(main())
