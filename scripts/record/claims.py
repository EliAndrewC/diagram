#!/usr/bin/env python3
"""The claims INDEX: per research claim of the engine and the Mode A procedures, what the last check found (feature 316).

WHY (GM 2026-10-02): *"having an index of which things our sub-agent checks have shown to be valid and which ones are known to
not be valid ... there would always be an up-to-date index"*, and *"when the implementation changes then our tooling knows
which specific functions need to be fed to subagents to kind of redo the checks"*. A claim is a `Research:` line in a docstring
(`l7r/diagram/tools/claims.py` reads them, and fingerprints each unit's CODE); this script fingerprints the RESEARCH each claim
cites, keeps the committed index (`dev/claims-index.json`), and answers every question asked of it:

    claims.py owed                          every unit with no row or a stale one, and why; the bundle command per module
    claims.py bundle (--owed | --module P | --units K,K) [--out DIR] [--reason WHY]
                                             the files `impl-drift` reads, copied out of the repository (a unit not owed: REASON)
    claims.py record --bundle DIR --reply FILE
                                             the check's `VERDICT` and `UNCLAIMED` lines into the index, at what it read
    claims.py triage [--out DIR]           the claims owed only a TRIAGE: their pages' new or changed blocks, for one agent
    claims.py triaged --bundle DIR --reply FILE
                                             clear every claim the triage did not name; a named one is owed `impl-drift`
    claims.py backfill                      give rows checked at today's research the pages they were checked at
    claims.py report                        counts by verdict, then every finding and every UNRESEARCHED claim
    claims.py gate                          what the push refuses (owed, or a finding the delta introduced) and warns

THE RESEARCH FINGERPRINT (spec FR-004 b): a cited question's heading and the words of its blocks less its intro - the reading
`_entry_owed.findings` and feature 311 make, so an intro, a comment or a re-wrap owes nothing. GUESS, UNRESEARCHED, CONVENTION
and NONE cite nothing and have none.

A RE-CHECK IS SCOPED TO WHAT A CLAIM RESTS ON (feature 318, FR-016; the GM 2026-10-04, on 370 claims re-owed by a few edits to
one page: *"fix that ... to ensure the rechecks are appropriately scoped"*). The bundle numbers every block of the cited
questions and each verdict names the blocks it rests on (`[§3, §12]`); its row keeps those blocks' digests (`rests`) and the
pages it was checked at (`pages`, each snapshotted in `dev/claims-pages.json`). When a cited page moves, a claim is owed
`impl-drift` only if a block it rests on is gone (`rests changed`); otherwise it is owed only a TRIAGE - one agent shown the
page's new or changed blocks and every claim citing it names the few a change bears on, and the rest are cleared. A row with
no `pages` (checked before this) is owed in full, as before (`research changed`).

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
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True  # the push runs this in fixture trees whose `git status` must stay clean
import record_units as ru  # noqa: E402

INDEX = "dev/claims-index.json"
# GUARD_EDIT_OK: feature 328 amendment 8 (the GM 2026-10-07) - a finding in code only the legacy hand-authored villages, towns
# and cities run is DEFERRED, not DRIFTED: those checks go when the settlements convert, so they are not worth fixing now.
DEFERRED = "dev/claims-deferred.json"
STORE = "dev/claims-pages.json"  # the page snapshots each row's pages name (feature 318, FR-016)
QUESTIONS = "research/questions"
FINDINGS = ("DRIFTED", "NEEDS-RESEARCH", "MISLABELED", "UNCLAIMED", "CANNOT-TELL")
VERDICTS = ("IN-STEP", *FINDINGS)
DEFAULT_OUT = Path("/tmp/l7r-check")
#: What the base read needs: the engine, the procedure documents and the questions.
BASE_PATHS = ("l7r", "docs/buildings.md", "docs/buildings", QUESTIONS)
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


def page_blocks(name: str, qdir: Path, memo: dict[str, Any] | None = None) -> tuple[str, list[tuple[str, str]]]:
    """A cited question's findings digest and its non-intro blocks as (digest, words), in order - what a claim can rest on
    (feature 318, FR-016). A missing file is `missing` with no blocks."""
    memo = {} if memo is None else memo
    if name not in memo:
        f = qdir / name
        if not f.is_file():
            memo[name] = ("missing", [])
        else:
            text = f.read_text(encoding="utf-8")
            page = ru.read_page(text)
            memo[name] = (
                findings_of(text),
                [(ru.digest([b.words]), b.words) for b in page.blocks if not b.intro],
            )
    return memo[name]


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
    cl = engine(Path(__file__).resolve().parents[2])
    qdir = qdir if qdir is not None else skill / "research" / "questions"
    memo: dict[str, str] = {}
    out: dict[str, Row] = {}
    for unit, _errors in cl.all_units(skill):
        for claim in unit.claims:
            key = unit.key(claim)
            out[key] = Row(
                key,
                unit,
                claim,
                unit.code(claim),
                research_fp(claim.pointers, qdir, memo),
            )
    return out


def load_index(path: Path) -> dict[str, dict[str, str]]:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def save_index(path: Path, rows: dict[str, dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(dict(sorted(rows.items())), indent=1, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def load_store(path: Path) -> dict[str, list[str]]:
    """The page snapshots: a question's findings digest -> its blocks' digests at a check (feature 318, FR-016)."""
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def save_store(path: Path, store: Mapping[str, list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(dict(sorted(store.items())), indent=0, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def standing(pointers: Sequence[str], qdir: Path, memo: dict[str, Any]) -> set[str]:
    """`page:digest` for every block now standing on the questions `pointers` cite."""
    out: set[str] = set()
    for ptr in pointers:
        name = ptr.rsplit("/", 1)[1]
        out.update(f"{name}:{d}" for d, _w in page_blocks(name, qdir, memo)[1])
    return out


def research_why(
    row: Row,
    was: Mapping[str, Any],
    qdir: Path,
    store: Mapping[str, list[str]],
    memo: dict[str, Any],
) -> str:
    """Why a claim whose cited research moved is owed (feature 318, FR-016): a full re-check when a block it rested on is gone
    (`rests changed`) or its row predates the snapshots (`research changed`); else only the TRIAGE of what changed on its pages."""
    pages = was.get("pages")
    if not isinstance(pages, dict) or any(d not in store for d in pages.values()):
        return "research changed"
    rests = was.get("rests")
    if isinstance(rests, list) and not set(rests) <= standing(row.claim.pointers, qdir, memo):
        return "rests changed"
    return "triage"


def owed(
    cur: dict[str, Row],
    index: Mapping[str, Mapping[str, Any]],
    qdir: Path | None = None,
    store: Mapping[str, list[str]] | None = None,
) -> list[tuple[str, str]]:
    """(key, why) for every claim with no row, whose code moved, or whose research moved
    (FR-016: `rests changed` / `research changed` owe `impl-drift`; `triage` owes only the triage of the changed blocks)."""
    out: list[tuple[str, str]] = []
    memo: dict[str, Any] = {}
    for key, row in sorted(cur.items()):
        was = index.get(key)
        if was is None:
            out.append((key, "new"))
        elif was.get("code") != row.code:
            out.append((key, "code changed"))
        elif was.get("triage") == "touched":
            out.append((key, "triage touched"))
        elif was.get("research") != row.research:
            out.append(
                (
                    key,
                    research_why(row, was, qdir, store or {}, memo) if qdir is not None else "research changed",
                )
            )
    return out


def judged(due: Sequence[tuple[str, str]]) -> list[str]:
    """The owed keys `impl-drift` must judge: every owed key but those owed only a triage."""
    return [k for k, why in due if why != "triage"]


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
        "END EVERY VERDICT NOTE with the blocks of the cited questions it rests on, as numbered in the question files: "
        "`[§3, §12]`, or `[§]` when the questions are silent on the claim. A later edit to a page re-checks a claim only "
        "when a block it rests on changes (feature 318), so name every block your verdict reads.\n",
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
    numbered: dict[str, str] = {}  # §N -> page:digest, numbered across the whole bundle (FR-016)
    snapshots: dict[str, list[str]] = {}
    memo: dict[str, Any] = {}
    for name in cited:
        page = ru.read_page((qdir / name).read_text(encoding="utf-8"))
        fp, blocks = page_blocks(name, qdir, memo)
        snapshots[fp] = [d for d, _w in blocks]
        lines = []
        for b in page.blocks:
            if b.intro:
                lines.append("[intro] " + b.words)
                continue
            numbered[f"§{len(numbered) + 1}"] = f"{name}:{ru.digest([b.words])}"
            lines.append(f"[§{len(numbered)}] {b.words}")
        (out / "questions" / f"{name}.txt").write_text(
            f"# {page.heading}\n({QUESTIONS}/{name})\n\n" + "\n\n".join(lines) + "\n",
            encoding="utf-8",
        )
        parts.append(f"- `questions/{name}.txt` - {page.heading}")
    (out / "MANIFEST.md").write_text("\n".join(parts) + "\n", encoding="utf-8")
    units = {
        k: {
            "code": cur[k].code,
            "core": cur[k].unit.core,
            "research": cur[k].research,
            "uid": cur[k].uid,
            "pages": {ptr.rsplit("/", 1)[1]: page_blocks(ptr.rsplit("/", 1)[1], qdir, memo)[0] for ptr in cur[k].claim.pointers},
        }
        for k in keys
    }
    (out / "units.json").write_text(json.dumps(units, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    (out / "blocks.json").write_text(
        json.dumps({"numbered": numbered, "snapshots": snapshots}, indent=1, sort_keys=True) + "\n",
        encoding="utf-8",
    )
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


_RESTS = re.compile(r"\[(§[^\]]*)\]\s*$")


_ELIDED = re.compile(r"\b(\d{4})-[\w-]*\.\.\.?[\w-]*?((?:\.drawing)?\.html)")


def unelide(reply: str, stems: list[str]) -> str:
    """The reply with each pointer a check wrote shortened (`0236-...-home-plot.drawing.html`) given its full file name, so a
    verdict note written into the index never fails `check-research-pointers.py` (feature 319: four did, and the index had to
    be hand-repaired). `stems` are the question stems (`0236-shrine-...`); a number with no question, or with more than one
    stem, is left as written for a person to see."""

    def full(m: re.Match[str]) -> str:
        hits = [s for s in stems if s.startswith(m.group(1) + "-")]
        return f"{hits[0]}{m.group(2)}" if len(hits) == 1 else m.group(0)

    return _ELIDED.sub(full, reply)


def rests_of(note: str, numbered: Mapping[str, str]) -> tuple[str, list[str] | None]:
    """A verdict note without its closing `[§3, §12]`, and the `page:digest` of each block it names (feature 318, FR-016): `[§]`
    is an empty list (the questions are silent on the claim), no tag at all None (either way any change on its pages is
    triaged); a number the bundle does not hold is dropped."""
    m = _RESTS.search(note)
    if not m:
        return note, None
    names = [x.strip() for x in m.group(1).split(",")]
    return note[: m.start()].rstrip(), sorted({numbered[n] for n in names if n in numbered})


def record(
    index: dict[str, dict[str, Any]],
    units: dict[str, dict[str, Any]],
    reply: str,
    today: str,
    numbered: Mapping[str, str] | None = None,
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    """The index with a check's reply applied, and the messages for the session (spec FR-009). A key not in the bundle is
    refused; a bundle key the reply gives no verdict stays owed; an UNCLAIMED finding is a row of its own, and a unit's earlier
    UNCLAIMED rows are dropped when this check of its claims does not report them again. Each row keeps the pages it was checked
    at and the blocks its verdict rests on (feature 318, FR-016)."""
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
        note, rests = rests_of(note, numbered or {})
        # ...ONLY ON ITS OWN PAGES (feature 328 wave 95): an agent re-sent a fresh bundle cited the section numbers of the bundle it
        # first read, and claims came to rest on blocks of pages they do not cite, so an edit to their own pages no longer
        # re-owed them. A foreign rest is dropped and named; with none of its own left the claim triages any change on its pages
        if rests and "pages" in fp:
            foreign = [r for r in rests if r.rsplit(":", 1)[0] not in fp["pages"]]
            if foreign:
                msgs.append(f"`{key}`: rests on {', '.join(sorted({r.rsplit(':', 1)[0] for r in foreign}))}, a page it does not cite - dropped (was the reply judged against another bundle's numbering?)")
                rests = [r for r in rests if r not in foreign] or None
        row: dict[str, Any] = {
            "verdict": verdict,
            "code": fp["code"],
            "core": fp["core"],
            "research": fp["research"],
            "date": today,
            "note": note,
        }
        if "pages" in fp:
            row["pages"] = fp["pages"]
        if rests is not None:
            row["rests"] = rests
        out[key] = row
    cores = {u["uid"]: u["core"] for u in units.values()}
    for uid, decision in unclaimed:
        if uid not in cores:
            msgs.append(f"refused: UNCLAIMED `{uid}` is not a unit of this bundle")
            continue
        out[f"{uid}#{decision}"] = {
            "verdict": "UNCLAIMED",
            "code": cores[uid],
            "core": cores[uid],
            "research": "",
            "date": today,
            "note": decision,
        }
        msgs.append(f"UNCLAIMED {uid} - {decision}: write a claim for it, then check it")
    return out, msgs


# ---- the triage (feature 318, FR-016) ------------------------------------------------------------------------------

_TOUCHES = re.compile(r"^TOUCHES\s+(\S.*?)\s+-\s+(.*)$")


#: The page texts a snapshot was taken of, kept as git blobs in the clone (feature 375 T04): `{findings digest: blob sha}`.
BLOBS = "claims-page-blobs.json"


def _blob_map(qdir: Path) -> Path | None:
    common = (_git(qdir, "rev-parse", "--path-format=absolute", "--git-common-dir") or "").strip()
    return Path(common) / BLOBS if common else None


def keep_texts(qdir: Path, units: Mapping[str, Mapping[str, Any]]) -> int:
    """Keep, as a git blob, the text of every page a recorded snapshot was taken of (`units`' `pages`), while the page still
    stands at that snapshot. WHY (feature 375 T04, measured on 372's wave 108): a block drafted and withdrawn before any commit
    is in no version of the page's history, so `removed_words` could not show it, and every claim citing the page was owed in
    full (`forced`) - "3 of 3 sent on to impl-drift" from a triage reply that named none. The blob is the snapshot's own text,
    so the removed words are always there to show."""
    path = _blob_map(qdir)
    pages = {name: fp for u in units.values() for name, fp in dict(u.get("pages") or {}).items()}
    if path is None or not pages:
        return 0
    blobs = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    kept = 0
    for name, fp in sorted(pages.items()):
        f = qdir / name
        if fp in blobs or not f.is_file() or findings_of(text := f.read_text(encoding="utf-8")) != fp:
            continue
        run = subprocess.run(["git", "-C", str(qdir), "hash-object", "-w", "--stdin"], input=text, capture_output=True, text=True, check=False)
        if run.returncode == 0:
            blobs[fp] = run.stdout.strip()
            kept += 1
    if kept:
        path.write_text(json.dumps(blobs, indent=0, sort_keys=True) + "\n", encoding="utf-8")
    return kept


def kept_text(qdir: Path, fp: str) -> str:
    """The text of the page snapshot `fp`, from the clone's kept blobs, or ''."""
    path = _blob_map(qdir)
    blob = json.loads(path.read_text(encoding="utf-8")).get(fp, "") if path is not None and path.is_file() else ""
    return (_git(qdir, "cat-file", "-p", blob) or "") if blob else ""


def removed_words(qdir: Path, name: str, digests: set[str], depth: int = 60, snapshot: str = "") -> dict[str, str]:
    """The words of the blocks `digests` of the question `name` that no longer stand, read back from the snapshot's kept text
    (`keep_texts`) and then the page's own git history (newest first, at most `depth` versions): the snapshots keep digests
    only, and the triage must SHOW a removed block. A block nothing yields is absent from the answer."""
    found: dict[str, str] = {}
    texts = ([kept_text(qdir, snapshot)] if snapshot else []) + [
        _git(qdir, "show", f"{sha}:./{name}") or "" for sha in (_git(qdir, "log", "--format=%H", f"-{depth}", "--", name) or "").split()
    ]
    for text in texts:
        for b in ru.read_page(text).blocks:
            d = ru.digest([b.words])
            if d in digests and not b.intro:
                found.setdefault(d, b.words)
        if len(found) == len(digests):
            break
    return found


def triage_bundle(
    cur: dict[str, Row],
    index: Mapping[str, Mapping[str, Any]],
    store: Mapping[str, list[str]],
    keys: Sequence[str],
    qdir: Path,
    out: Path,
) -> Path:
    """The triage bundle for `keys` (claims owed only a triage): per cited page, the blocks new, changed or REMOVED since each
    claim's check (a removed block is shown too: a row with no `rests` may have rested on it, and a deleted caveat bears on a
    claim that did not name it), and the claims citing it with their last verdict. A removed block whose words its page's history
    no longer yields makes every claim citing that page owed in full (`forced`). Writes MANIFEST.md and triage.json (each claim's
    fingerprints now, today's snapshots, the forced claims)."""
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    memo: dict[str, Any] = {}
    by_page: dict[str, list[str]] = {}
    changed: dict[str, list[str]] = {}
    gone: dict[str, list[str]] = {}
    lost: dict[tuple[str, str], bool] = {}
    forced: set[str] = set()
    for key in keys:
        for name, old in index[key]["pages"].items():
            fp, blocks = page_blocks(name, qdir, memo)
            if fp == old:
                continue
            before, now = set(store.get(old, [])), {d for d, _w in blocks}
            fresh = [w for d, w in blocks if d not in before]
            if (name, old) not in lost:
                missing = before - now
                words = removed_words(qdir, name, missing, snapshot=old) if missing else {}
                gone[f"{name}|{old}"] = [words[d] for d in sorted(missing) if d in words]
                lost[(name, old)] = len(words) < len(missing)
            if lost[(name, old)]:
                forced.add(key)
            if fresh or gone[f"{name}|{old}"]:
                changed[name] = fresh
                gone[name] = sorted(set(gone.get(name, [])) | set(gone[f"{name}|{old}"]))
                by_page.setdefault(name, []).append(key)
    parts = [
        "# Triage of claim re-checks (feature 318)\n",
        "owed-checks: claims-triage\n",
        "Each page below changed since the claims under it were last judged; it lists ONLY its new, changed and REMOVED blocks. "
        "For each claim, decide whether any of those blocks - a block added or reworded, or one taken away - could change its verdict - a figure, rule, form, order, exception or recorded "
        "deviation that bears on what the claim says the code does. Reply one `TOUCHES <key> - <which block, a few words>` line per "
        "such claim, and nothing for the rest: a claim you do not name is cleared without a re-check. When unsure, name it.\n",
    ]
    for name, ks in sorted(by_page.items()):
        parts.append(f"## {QUESTIONS}/{name}\n\nNew or changed blocks:\n")
        parts += [f"> {w}\n" for w in changed[name]] or ["(none)\n"]
        if gone.get(name):
            parts.append("Removed blocks (no longer on the page):\n")
            parts += [f"> {w}\n" for w in gone[name]]
        parts.append("Claims citing it:\n")
        for k in sorted(ks):
            parts.append(f"- KEY `{k}`: `{cur[k].claim.line}` - last verdict {index[k].get('verdict')}: {index[k].get('note', '')}")
        parts.append("")
    (out / "MANIFEST.md").write_text("\n".join(parts) + "\n", encoding="utf-8")
    units = {
        k: {
            "research": cur[k].research,
            "pages": {ptr.rsplit("/", 1)[1]: page_blocks(ptr.rsplit("/", 1)[1], qdir, memo)[0] for ptr in cur[k].claim.pointers},
        }
        for k in keys
    }
    snaps = {fp: [d for d, _w in blocks] for fp, blocks in memo.values()}
    (out / "triage.json").write_text(
        json.dumps({"units": units, "snapshots": snaps, "forced": sorted(forced)}, indent=1, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return out / "MANIFEST.md"


def record_triage(
    index: dict[str, dict[str, Any]],
    units: Mapping[str, Mapping[str, Any]],
    reply: str,
    today: str,
    forced: Sequence[str] = (),
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    """The index with a triage reply applied: a named claim is owed `impl-drift` (`triage: touched`), and so is a `forced` one (a
    block removed from its page whose words the history no longer yields); every other claim of the bundle keeps its verdict and
    the blocks it rests on, recorded at the pages as they stand now."""
    touched = {m.group(1).strip("`"): m.group(2) for raw in reply.split("\n") if (m := _TOUCHES.match(raw.strip().strip("`")))}
    msgs = [f"refused: `{k}` is not a claim of this triage" for k in sorted(set(touched) - set(units))]
    touched |= {k: "a removed block the history no longer shows" for k in forced if k in units and k not in touched}
    out = dict(index)
    for key, fp in sorted(units.items()):
        row = dict(out[key])
        if key in touched:
            row["triage"] = "touched"
            msgs.append(f"touched: {key} - {touched[key]}")
        else:
            row.update(research=fp["research"], pages=dict(fp["pages"]), triaged=today)
            row.pop("triage", None)
        out[key] = row
    return out, msgs


def backfill(
    cur: dict[str, Row],
    index: dict[str, dict[str, Any]],
    qdir: Path,
    store: dict[str, list[str]],
) -> int:
    """Give every row checked at today's research (its fingerprint matches) the pages it was checked at, and snapshot those pages,
    so the next edit to them is triaged rather than re-judged in full (FR-016). A row whose research moved is left owed in full."""
    memo: dict[str, Any] = {}
    n = 0
    for key, row in cur.items():
        was = index.get(key)
        if was is None or "pages" in was or was.get("research") != row.research or not row.claim.pointers:
            continue
        pages = {}
        for ptr in row.claim.pointers:
            name = ptr.rsplit("/", 1)[1]
            fp, blocks = page_blocks(name, qdir, memo)
            pages[name] = fp
            store[fp] = [d for d, _w in blocks]
        was["pages"] = pages
        n += 1
    return n


# ---- the report and the gate ---------------------------------------------------------------------------------------


def load_deferred(path: Path) -> frozenset[str]:
    """The units (`units`, `path::qualname`) and single claims (`keys`, `path::qualname#label`) whose findings are DEFERRED
    (`dev/claims-deferred.json`), or none."""
    if not path.is_file():
        return frozenset()
    doc = json.loads(path.read_text(encoding="utf-8"))
    return frozenset(doc.get("units", [])) | frozenset(doc.get("keys", []))


def shown(key: str, verdict: str, deferred: frozenset[str]) -> str:
    """A finding's verdict as the report shows it: DEFERRED where its unit is deferred, else its own."""
    return "DEFERRED" if verdict in FINDINGS and (key in deferred or key.rsplit("#", 1)[0] in deferred) else verdict


def report(
    cur: dict[str, Row],
    index: dict[str, dict[str, str]],
    qdir: Path | None = None,
    store: Mapping[str, list[str]] | None = None,
    deferred: frozenset[str] = frozenset(),
) -> str:
    """Counts by verdict, the owed count, then every finding and every UNRESEARCHED claim (spec FR-011); a finding in a
    deferred unit (`load_deferred`) is shown and counted DEFERRED."""
    rows = live_rows(cur, index)
    due = owed(cur, index, qdir, store)
    counts = Counter(shown(k, v["verdict"], deferred) for k, v in rows.items())
    tally = ", ".join(f"{v} {counts[v]}" for v in (*VERDICTS, "DEFERRED") if counts[v]) or "no verdicts yet"
    lines = [f"claims: {len(cur)} in scope; {tally}; owed {len(due)}"]
    for key, v in sorted(rows.items()):
        if v["verdict"] != "IN-STEP":
            lines.append(f"  {shown(key, v['verdict'], deferred):<14} {key} - {v.get('note', '')}")
    unres = sorted(k for k, r in cur.items() if r.claim.backing == "UNRESEARCHED")
    if unres:
        lines.append(f"UNRESEARCHED claims (the open research): {len(unres)}")
        lines += [f"  {k}" for k in unres]
    return "\n".join(lines)


def base_tree(root: Path, base: str, into: Path) -> Path:
    """The engine, procedures and questions at `base`, extracted under `into`; returns the skill directory there."""
    archive = subprocess.run(
        ["git", "-C", str(root), "archive", "--format=tar", base, "--", *BASE_PATHS],
        capture_output=True,
        check=False,
    )
    if archive.returncode == 0:
        tar = into / "base.tar"
        tar.write_bytes(archive.stdout)
        with tarfile.open(tar) as t:
            t.extractall(into, filter="data")
    (into / "l7r" / "diagram" / "hamletgen").mkdir(parents=True, exist_ok=True)
    return into


def base_cores(skill: Path) -> dict[str, str]:
    """uid -> core for EVERY unit at a tree, claimed or not: the base the push compares with may hold no claims at all (this
    feature's own landing, where main has none), and a unit's code is the same whatever its claims say."""
    cl = engine(Path(__file__).resolve().parents[2])
    return {f"{u.path}::{u.qualname}": u.core for u, _errors in cl.all_units(skill, every_module_unit=True)}


def classify(
    cur: dict[str, Row],
    index: dict[str, dict[str, str]],
    base_index: dict[str, dict[str, str]],
    cores: dict[str, str],
    base_qdir: Path,
    deferred: frozenset[str] = frozenset(),
) -> tuple[list[str], list[str]]:
    """(introduced, pre-existing) finding lines (spec FR-010). `cores` is every unit's core at the merge base (`base_cores`),
    `base_qdir` the base's questions: a first finding is introduced only when its unit's code matches no base unit's (its own
    key's, or one gone at the head - a rename or a move) or its claim's cited findings differ from the base's."""
    head_uids = {r.uid for r in cur.values()}
    gone_cores = {core for uid, core in cores.items() if uid not in head_uids}
    memo: dict[str, str] = {}
    intro: list[str] = []
    pre: list[str] = []
    for key, v in sorted(live_rows(cur, index).items()):
        if v["verdict"] not in FINDINGS or shown(key, v["verdict"], deferred) == "DEFERRED":
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


def split_keys(text: str, known: Mapping[str, Any]) -> list[str]:
    """The claim keys a comma-separated `text` names. A key's label may hold a comma of its own (`#the track out, the field spur
    and a row street stay whole`), so the pieces are joined back into the LONGEST run that is a `known` key; a piece no run
    makes known is returned alone, for the caller to name as unknown. Split on every comma, the feature-317 batches could not
    name 8 of their 387 owed keys."""
    parts = text.split(",")
    keys: list[str] = []
    i = 0
    while i < len(parts):
        j = next(
            (j for j in range(len(parts), i, -1) if ",".join(parts[i:j]).strip() in known),
            i + 1,
        )
        key = ",".join(parts[i:j]).strip()
        if key:
            keys.append(key)
        i = j
    return keys


def gate(root: Path) -> tuple[list[str], list[str]]:
    """(refusals, warnings) for the push: owed units, introduced findings; pre-existing findings warn."""
    skill = root
    cur = current(skill)
    index = load_index(root / INDEX)
    due = owed(cur, index, skill / "research" / "questions", load_store(root / STORE))
    refuse = [f"owed ({why}): {key}" for key, why in due]
    mb = (_git(root, "merge-base", "HEAD", "origin/main") or _git(root, "rev-parse", "HEAD") or "").strip()
    base_index = json.loads(_git(root, "show", f"{mb}:{INDEX}") or "{}") if mb else {}
    with tempfile.TemporaryDirectory() as tmp:
        bskill = base_tree(root, mb, Path(tmp)) if mb else Path(tmp)
        cores = base_cores(bskill) if mb else {}
        intro, pre = classify(cur, index, base_index, cores, bskill / "research" / "questions", load_deferred(root / DEFERRED))
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
    tr = sub.add_parser("triage")
    tr.add_argument("--out", default="")
    td = sub.add_parser("triaged")
    td.add_argument("--bundle", required=True)
    td.add_argument("--reply", required=True)
    sub.add_parser("backfill")
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
        cl = engine(root)
        qs = {p.name for p in (root / QUESTIONS).glob("*.html")}
        probs = [x for x in cl.coverage(cl.all_units(root), qs) if args.path in x.split(" ", 1)[0]]
        print("\n".join(probs) if probs else f"claims-coverage: every unit{' under ' + args.path if args.path else ''} carries a claim")
        if probs:
            print(f"claims-coverage: {len(probs)} problem(s). The form: {cl.GRAMMAR}")
        return 1 if probs else 0
    cur = current(root)
    index = load_index(root / INDEX)
    qdir, store = root / QUESTIONS, load_store(root / STORE)
    if args.cmd == "owed":
        due = owed(cur, index, qdir, store)
        if not due:
            print("claims-owed: no claim is owed")
            return 0
        full = judged(due)
        mods = Counter(cur[k].unit.path for k in full)
        for key, why in due:
            print(f"{why:<16} {key}")
        if full:
            print(f"claims-owed: {len(full)} claim(s) in {len(mods)} file(s) owe impl-drift; bundle per file with `make claims-bundle MODULE=<path>`, or OWED=1 for all")
        if len(due) > len(full):
            print(f"claims-owed: {len(due) - len(full)} claim(s) owe only a TRIAGE of the blocks that changed on their pages - `make claims-triage` first; it sends on only the claims a change bears on")
        return 0
    if args.cmd == "backfill":
        n = backfill(cur, index, qdir, store)
        save_index(root / INDEX, live_rows(cur, index))
        save_store(root / STORE, store)
        print(f"claims-backfill: {n} row(s) given the pages they were checked at")
        return 0
    if args.cmd == "triage":
        keys = [k for k, why in owed(cur, index, qdir, store) if why == "triage"]
        if not keys:
            print("claims-triage: no claim is owed a triage")
            return 0
        print(
            triage_bundle(
                cur,
                index,
                store,
                keys,
                qdir,
                Path(args.out) if args.out else DEFAULT_OUT / "claims-triage",
            )
        )
        print(f"claims-triage: {len(keys)} claim(s); dispatch one ad-hoc agent (model opus) on the MANIFEST, save its reply, then `make claims-triaged BUNDLE=<dir> REPLY=<file>`")
        return 0
    if args.cmd == "triaged":
        data = json.loads((Path(args.bundle) / "triage.json").read_text(encoding="utf-8"))
        new, msgs = record_triage(
            index,
            data["units"],
            Path(args.reply).read_text(encoding="utf-8"),
            datetime.date.today().isoformat(),
            data.get("forced", []),
        )
        save_index(root / INDEX, live_rows(cur, new))
        save_store(root / STORE, {**store, **data["snapshots"]})
        keep_texts(qdir, data["units"])
        for m in msgs:
            print(f"claims-triaged: {m}")
        named = sum(1 for m in msgs if m.startswith("touched") and " - a removed block the history no longer shows" not in m)
        forced = sum(1 for m in msgs if m.startswith("touched")) - named
        print(f"claims-triaged: {named + forced} of {len(data['units'])} sent on to impl-drift ({named} named by the reply"
              + (f", {forced} owed in full: a removed block's words could not be shown" if forced else "")
              + "); the rest cleared")
        return 0
    if args.cmd == "report":
        print(report(cur, index, qdir, store, load_deferred(root / DEFERRED)))
        return 0
    if args.cmd == "bundle":
        due_all = owed(cur, index, qdir, store)
        due = {k: why for k, why in due_all if why != "triage"}
        if args.owed:
            keys = sorted(due)
        elif args.module:
            keys = sorted(k for k, row in cur.items() if row.unit.path == args.module or row.unit.path.endswith("/" + args.module))
        else:
            keys = split_keys(args.units, cur)
        unknown = [k for k in keys if k not in cur]
        if unknown or not keys:
            print(
                f"claims-bundle: no such claim(s): {', '.join(unknown) or '(none selected)'}",
                file=sys.stderr,
            )
            return 2
        not_owed = [k for k in keys if k not in due]
        if not_owed and len(args.reason.split()) < 2:
            print(
                f'claims-bundle: {len(not_owed)} of these claims are not owed (first: {not_owed[0]}); a re-check needs REASON="<why>"',
                file=sys.stderr,
            )
            return 3
        slug = re.sub(
            r"[^a-z0-9]+",
            "-",
            (args.module or ("owed" if args.owed else keys[0])).lower(),
        ).strip("-")[-60:]
        out = Path(args.out) if args.out else DEFAULT_OUT / f"claims-{slug}"
        print(bundle(root, cur, keys, out))
        if not_owed:
            print(f"claims-bundle: re-check of {len(not_owed)} claim(s) not owed, because: {args.reason}")
        return 0
    units = json.loads((Path(args.bundle) / "units.json").read_text(encoding="utf-8"))
    stems = sorted({p.name.split(".")[0] for p in (root / QUESTIONS).glob("[0-9][0-9][0-9][0-9]-*.html")})
    reply = unelide(Path(args.reply).read_text(encoding="utf-8"), stems)
    blocks_file = Path(args.bundle) / "blocks.json"
    blocks = json.loads(blocks_file.read_text(encoding="utf-8")) if blocks_file.is_file() else {"numbered": {}, "snapshots": {}}
    new, msgs = record(index, units, reply, datetime.date.today().isoformat(), blocks["numbered"])
    save_index(root / INDEX, live_rows(cur, new))
    save_store(root / STORE, {**store, **blocks["snapshots"]})
    keep_texts(qdir, units)
    for m in msgs:
        print(f"claims-checked: {m}")
    print(f"claims-checked: {sum(1 for k in units if k in new and new[k].get('code') == units[k]['code'])} of {len(units)} recorded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
