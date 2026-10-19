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
import ast
import datetime
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tarfile
import textwrap
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True  # the push runs this in fixture trees whose `git status` must stay clean
import claims_carry  # noqa: E402
import claims_context  # noqa: E402
import claims_stale  # noqa: E402
import record_cache as rc  # noqa: E402
import record_units as ru  # noqa: E402
from claims_triage import (  # noqa: E402,F401 - the triage half, split out (feature 375 T09); re-exported
    BLOBS,
    findings_of,
    keep_texts,
    kept_text,
    page_blocks,
    record_triage,
    removed_words,
    triage_bundle,
)

INDEX = "dev/claims-index.json"
# GUARD_EDIT_OK: feature 328 amendment 8 (the GM 2026-10-07) - a finding in code only the legacy hand-authored villages, towns
# and cities run is DEFERRED, not DRIFTED: those checks go when the settlements convert, so they are not worth fixing now.
DEFERRED = "dev/claims-deferred.json"
STORE = "dev/claims-pages.json"  # the page snapshots each row's pages name (feature 318, FR-016), and each section's (375)
#: what a claim owed only a triage is owed for: a page it cites changed (feature 318), or its section did and its line did not (375)
SECTION_TRIAGE = "section triage"
TRIAGED = ("triage", SECTION_TRIAGE)
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


def units_of(skill: Path) -> list[Any]:
    """Every unit in scope at the tree under `skill`: `pairs_of` without the module errors."""
    return [u for u, _errors in pairs_of(skill)]


def form_problems(skill: Path, cl: Any = None) -> list[str]:
    """The gate's claim-form problems (`test_claims_coverage`) from the kept parse: a claim of the wrong form failed that
    tooling test at the gate, which `make quick` never runs (feature 374 batch 4), so `claims-owed` prints these first."""
    cl = cl or engine(skill)
    return cl.coverage(pairs_of(skill), {q.name for q in (skill / QUESTIONS).glob("*.html")})


def pairs_of(skill: Path) -> list[Any]:
    """Every unit in scope at the tree under `skill`, kept by what it is read from (feature 375 amendment 3, plan D29): every
    engine module and procedure document under `skill`, and the readers' own code - `scripts/record/claims.py` and every
    project module it imports, transitively (the engine's reader among them). Re-parsing the engine was 7.29 s a call on 374's
    delta (specs/375-enforced-wave-process/research.md R1); a key over the sources is read in a fraction of that. Only the
    newest key's file is kept."""
    cl = engine(Path(__file__).resolve().parents[2])
    h = hashlib.sha256(rc.code_sha_of(Path(__file__).resolve().parents[2], Path(__file__)).encode())
    for p in sorted((skill / "l7r" / "diagram").rglob("*.py")):
        if "__pycache__" not in p.parts:
            h.update(p.relative_to(skill).as_posix().encode() + b"\0" + p.read_bytes() + b"\0")
    for doc in cl.PROCEDURES:
        if (skill / doc).is_file():
            h.update(doc.encode() + b"\0" + (skill / doc).read_bytes() + b"\0")
    common = rc.common_dir(skill)
    cache = rc.ParseCache(common / rc.CACHE_DIR / f"claims-{h.hexdigest()[:16]}.pickle" if common is not None else None)
    # UNDER IT, EACH MODULE KEPT BY WHAT IT READS (feature 375 amendment 8, FR-035, plan D48): the key above moves with any
    # engine edit, and a comment cost 11.9 s against 1.0 warm (specs/375-enforced-wave-process/research.md R7) - so on its
    # miss each module's parse and units come from `claims-modules`, and only the edited modules are computed again
    # Named by the readers' code - this file, what it imports, and the engine's reader - so a change to `module_units` reads
    # nothing kept by the old one; and not `claims-...`: `save()` drops every other `<prefix>-*.pickle` as a stale version,
    # and the two caches deleted each other (measured 2026-10-12: every module missed after a one-line edit)
    reader = hashlib.sha256((rc.code_sha_of(Path(__file__).resolve().parents[2], Path(__file__)) + Path(cl.__file__).read_text(encoding="utf-8")).encode())
    memo = rc.ParseCache(common / rc.CACHE_DIR / f"claims_by_module-{reader.hexdigest()[:16]}.pickle" if common is not None else None)
    memo.PRUNE_AT = 1  # holds only what this run used, so the file does not grow with every edit
    # the units WITH their modules' errors, so the form check reads the same parse (feature 374 batch 4, `form_problems`)
    pairs = cache.get("pairs", lambda: list(cl.all_units(skill, memo=memo)))
    memo.save()
    cache.save()
    return pairs


def current(skill: Path, qdir: Path | None = None) -> dict[str, Row]:
    """key -> Row for every claim of every unit in scope, at the tree under `skill` (its questions under `qdir`)."""
    qdir = qdir if qdir is not None else skill / "research" / "questions"
    memo: dict[str, str] = {}
    out: dict[str, Row] = {}
    for unit in units_of(skill):
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
        elif was.get("code") != row.code and not (qdir is not None and relabeled_only(was, row, qdir.parent.parent)):
            out.append((key, "code changed"))
        elif was.get("triage") == "touched":
            out.append((key, "triage touched"))
        elif row.unit.kind == "section" and "section" in was and was["section"] != row.unit.core:
            out.append((key, SECTION_TRIAGE))  # feature 375 FR-002: its own line stands; the rest of its section moved
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
    return [k for k, why in due if why not in TRIAGED]


def live_rows(cur: dict[str, Row], index: dict[str, dict[str, str]]) -> dict[str, dict[str, str]]:
    """The index rows that still speak of something: a claim in scope, or an UNCLAIMED row whose unit still exists."""
    uids = {r.uid for r in cur.values()}
    return {k: v for k, v in index.items() if k in cur or (v.get("verdict") == "UNCLAIMED" and k.rsplit("#", 1)[0] in uids)}


# ---- the bundle --------------------------------------------------------------------------------------------------


_RESEARCH_BLOCK = re.compile(r"(?ms)^[ \t]*(?:\"\"\"|''')?Research:.*?(?=\"\"\"|'''|^[ \t]*$)")
"""A docstring's `Research:` section, from its `Research:` line to the docstring's close or a blank line."""


def body_of(root: Path, unit: Any) -> str:  # noqa: ANN401
    """A unit's source with its `Research:` section taken out, fingerprinted: what stays the same when only a claim's label
    or citation is rewritten (the round arbiter's tooling fix on ask:t01-claim-labels, feature 385 - three impl-drift rounds
    on T01's claims were about labels alone, each relabel re-owing every claim of its unit)."""
    try:
        text = _source(root, unit)
    except OSError:
        return ""
    return hashlib.sha256(_RESEARCH_BLOCK.sub("", text).encode("utf-8")).hexdigest()[:16]


def relabeled_only(was: Mapping[str, Any], row: Row, root: Path) -> bool:
    """Is a claim whose code fingerprint moved changed in its `Research:` lines alone - the unit's body as last judged - and
    either its own claim text unchanged (another claim of the unit was rewritten) or rewritten after a MISLABELED verdict (the
    relabel that verdict prescribed)? Then it owes no new round. A row recorded before bodies were kept owes one, as before."""
    if not was.get("body") or body_of(root, row.unit) != was["body"]:
        return False
    text = row.claim.normalized() if row.claim is not None else ""
    return was.get("claim") == text or was.get("verdict") == "MISLABELED"


def relabel_answered(was: Mapping[str, Any], row: Row, root: Path) -> bool:
    """A MISLABELED verdict answered by the relabel it prescribed - the claim's text rewritten since, the unit's body the one
    judged - so the gate does not refuse what `owed` no longer asks of it (385 T23, plan D45)."""
    text = row.claim.normalized() if row.claim is not None else ""
    return was.get("verdict") == "MISLABELED" and was.get("claim") not in (None, text) and relabeled_only(was, row, root)


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


def context_source(root: Path, ref: str) -> str:
    """The source of `path::qualname` - a function, method, class or module-level constant - shown in a bundle as context
    (feature 374: a CANNOT-TELL re-check asked for a helper's body, a constant or a caller the judged unit only names)."""
    path, _, qual = ref.partition("::")
    text = (root / path).read_text(encoding="utf-8")
    body: list[ast.stmt] = ast.parse(text).body
    node: ast.AST | None = None
    for name in qual.split("."):
        node = next(
            (
                n
                for n in body
                if (isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.name == name)
                or (isinstance(n, (ast.Assign, ast.AnnAssign)) and name in [t.id for t in (n.targets if isinstance(n, ast.Assign) else [n.target]) if isinstance(t, ast.Name)])
            ),
            None,
        )
        if node is None:
            raise ValueError(f"no `{qual}` in {path}")
        body = getattr(node, "body", [])
    return ast.get_source_segment(text, node) or ""


#: the most of its own module's functions a unit carries into its bundle as context (`callees`)
CALLEES_MAX = 6


def callees(root: Path, unit: Any, source: str) -> list[str]:
    """`path::name` of each of its own module's functions the unit calls (at most `CALLEES_MAX`; the arbiter's fix on
    ask:t03-claims-at-landing) and each module constant it reads, imported ones too (385 T25, `claims_context`)."""
    return claims_context.callees(root, unit, source, CALLEES_MAX)


def bundle(root: Path, cur: dict[str, Row], keys: Sequence[str], out: Path, context: Sequence[str] = (), pages: Sequence[str] = ()) -> Path:
    """Write the bundle for `keys` (rows of `cur`) under `out`: MANIFEST.md with every source and question inline, and
    units.json with the fingerprints the check reads - what `record` writes into the index (spec FR-007)."""
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    by_uid: dict[str, list[Row]] = {}
    for k in keys:
        by_uid.setdefault(cur[k].uid, []).append(cur[k])
    qdir = root / QUESTIONS
    index = load_index(root / INDEX)
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
        src = _source(root, unit)
        parts.append(f"\n```{lang}\n{src}\n```\n")
        if unit.kind != "section":  # ...the module's own functions it calls, and what a CANNOT-TELL asked for (385 T25, D47)
            asked = [n for r in rows for n in re.findall(r"`([A-Za-z_]\w*)", (index.get(r.key) or {}).get("note", "")) if (index.get(r.key) or {}).get("verdict") == "CANNOT-TELL"]
            far = claims_context.direct(root, unit, src, context_source) if any(claims_context.DISTANCE.search(r.claim.label) for r in rows) else []
            context = list(dict.fromkeys([*context, *callees(root, unit, src), *far, *claims_context.chase(root, unit.path, asked, context_source)]))
        # every page ANY claim of the unit cites, owed or not: an UNRESEARCHED or GUESS claim cites nothing, and its check
        # can only see a page that answers it if the unit's other claims bring it (the torii re-check, 2026-10-03)
        for c in unit.claims:
            for ptr in c.pointers:
                name = ptr.rsplit("/", 1)[1]
                if name not in cited and (qdir / name).is_file():
                    cited.append(name)
    if context:
        parts.append("# Context (read it; it is not judged)\n\nCode the units above call or read, shown so a verdict can see it:\n")
        for ref in context:
            parts.append(f"## CONTEXT {ref}\n\n```python\n{context_source(root, ref)}\n```\n")
    for p in (p.rsplit("/", 1)[-1] for p in pages):  # a path or a bare name; a page named and not found is an error, never
        if not (qdir / p).is_file():  # dropped (feature 374: a pointer-form path was skipped in silence)
            raise ValueError(f"PAGES: no question file {p} under {qdir}")
        cited += [p] if p not in cited else []
    # THE QUESTIONS ARE FILES BESIDE THE MANIFEST, as their reader meets them (heading and blocks, intro marked, no markup),
    # each once however many units cite it: inline whole pages made the audit's per-file bundles 23 MB (measured 2026-10-03)
    (out / "questions").mkdir()
    parts.append("# The cited questions\n\nEach is a file under `questions/` beside this MANIFEST - read each one a unit cites, once:\n")
    numbered: dict[str, str] = {}  # §N -> page:digest, numbered across the whole bundle (FR-016)
    snapshots: dict[str, list[str]] = {}
    memo: dict[str, Any] = {}
    for k in keys:  # a section claim's section, snapshot by its blocks: what a later section triage diffs (feature 375, FR-002)
        if cur[k].unit.kind == "section":
            snapshots[cur[k].unit.core] = [ru.digest([b]) for b in cur[k].unit.blocks]
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
            "body": body_of(root, cur[k].unit),
            "claim": cur[k].claim.normalized() if cur[k].claim is not None else "",
            "research": cur[k].research,
            "uid": cur[k].uid,
            "pages": {ptr.rsplit("/", 1)[1]: page_blocks(ptr.rsplit("/", 1)[1], qdir, memo)[0] for ptr in cur[k].claim.pointers},
            **({"section": cur[k].unit.core} if cur[k].unit.kind == "section" else {}),
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
    sys.path.insert(0, str(HERE.parent / "hooks" / "lib"))
    from hm_house import americanize  # noqa: PLC0415 - feature 385 T78: a note's words in the house style, its key as written

    verdicts: dict[str, tuple[str, str]] = {}
    unclaimed: list[tuple[str, str]] = []
    for raw in text.split("\n"):
        line = raw.strip().strip("`")
        if m := _VERDICT.match(line):
            verdicts[m.group(1).strip("`")] = (m.group(2), americanize(m.group(3).strip()))
        elif m := _UNCLAIMED.match(line):
            unclaimed.append((m.group(1).strip("`"), americanize(m.group(2).strip())))
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
                msgs.append(
                    f"`{key}`: rests on {', '.join(sorted({r.rsplit(':', 1)[0] for r in foreign}))}, a page it does not cite - dropped (was the reply judged against another bundle's numbering?)"
                )
                rests = [r for r in rests if r not in foreign] or None
        row: dict[str, Any] = {
            "verdict": verdict,
            "code": fp["code"],
            "core": fp["core"],
            **{f: fp[f] for f in ("body", "claim") if f in fp},
            "research": fp["research"],
            "date": today,
            "note": note,
        }
        if "pages" in fp:
            row["pages"] = fp["pages"]
        if "section" in fp:
            row["section"] = fp["section"]
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


def backfill_sections(cur: dict[str, Row], index: dict[str, dict[str, Any]], store: dict[str, list[str]]) -> int:
    """Re-key every procedure-section claim to the fingerprint of its own line (feature 375, FR-002) WITHOUT owing it: a row
    current under the old fingerprint (its section's core plus its line) gets the new `code` and its section's fingerprint and
    blocks; a row the old fingerprint already owed is left owed, since its new code cannot match. Run once, at the change."""
    cl = engine(Path(__file__).resolve().parents[2])
    n = 0
    for key, row in cur.items():
        was = index.get(key)
        if was is None or row.unit.kind != "section" or "section" in was:
            continue
        if was.get("code") == cl._sha(row.unit.core + "\x1f" + row.claim.normalized()):
            was.update(code=row.code, section=row.unit.core)
            store[row.unit.core] = [ru.digest([b]) for b in row.unit.blocks]
            n += 1
    return n


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
    # ONLY THE PATHS THE BASE HOLDS: `git archive` fails WHOLE on one missing pathspec, and an empty base tree made every
    # first finding read as introduced (found by feature 378, 2026-10-10: `docs/buildings/` is gone, so for some time the
    # gate compared every claim with nothing). A path the base lacks is skipped; a failure of the rest is raised.
    present = [p for p in BASE_PATHS if subprocess.run(["git", "-C", str(root), "cat-file", "-e", f"{base}:{p}"], capture_output=True, check=False).returncode == 0]
    archive = subprocess.run(
        ["git", "-C", str(root), "archive", "--format=tar", base, "--", *present],
        capture_output=True,
        check=False,
    )
    if present and archive.returncode != 0:
        raise RuntimeError(f"claims: the base tree could not be read at {base}: {archive.stderr.decode(errors='replace').strip()}")
    if present:
        tar = into / "base.tar"
        tar.write_bytes(archive.stdout)
        with tarfile.open(tar) as t:
            t.extractall(into, filter="data")
    (into / "l7r" / "diagram" / "hamletgen").mkdir(parents=True, exist_ok=True)
    return into


def base_cores(skill: Path, keep: Path | None = None) -> dict[str, str]:
    """uid -> core for EVERY unit at a tree, claimed or not: the base the push compares with may hold no claims at all (this
    feature's own landing, where main has none), and a unit's code is the same whatever its claims say.

    EACH MODULE KEPT BY WHAT IT READS, as `pairs_of` keeps the head's (feature 383 amendment 2, FR-019): with no memo every push
    parsed the whole base tree again - 8.5 of a landing's 16.7 s push (research R9) - though consecutive bases differ in a few
    modules. `keep` is the repository whose common git directory holds the memo; none keeps nothing."""
    cl = engine(Path(__file__).resolve().parents[2])
    common = rc.common_dir(keep) if keep is not None else None
    reader = hashlib.sha256((rc.code_sha_of(Path(__file__).resolve().parents[2], Path(__file__)) + Path(cl.__file__).read_text(encoding="utf-8")).encode())
    memo = rc.ParseCache(common / rc.CACHE_DIR / f"claims_base_by_module-{reader.hexdigest()[:16]}.pickle" if common is not None else None)
    memo.PRUNE_AT = 1  # holds only this base's modules; the next base shares nearly all of them
    cores = {f"{u.path}::{u.qualname}": u.core for u, _errors in cl.all_units(skill, every_module_unit=True, memo=memo)}
    memo.save()
    return cores


def classify(
    cur: dict[str, Row],
    index: dict[str, dict[str, str]],
    base_index: dict[str, dict[str, str]],
    cores: dict[str, str],
    base_qdir: Path,
    deferred: frozenset[str] = frozenset(),
    answered: frozenset[str] = frozenset(),
) -> tuple[list[str], list[str], list[tuple[str, str]]]:
    """(introduced, pre-existing, carried) findings (spec FR-010; carried: 385 FR-013, `claims_carry`). `cores`: every unit's core
    at the merge base, `base_qdir` its questions. CARRIED (key, line): its code and claim unchanged under the same key - its cited
    research moved, or it was only judged again (never a moved unit). Else a first finding is introduced when its code matches no base unit's (its own
    key's, or one gone at the head - a move) or its cited findings differ from the base's. `answered`: MISLABELED keys their
    prescribed relabel answered (`relabel_answered`), no finding at all."""
    head_uids = {r.uid for r in cur.values()}
    gone_cores = {core for uid, core in cores.items() if uid not in head_uids}
    memo: dict[str, str] = {}
    intro: list[str] = []
    pre: list[str] = []
    carried: list[tuple[str, str]] = []
    for key, v in sorted(live_rows(cur, index).items()):
        if v["verdict"] not in FINDINGS or key in answered or shown(key, v["verdict"], deferred) == "DEFERRED":
            continue
        was = base_index.get(key)
        line = f"{v['verdict']:<14} {key} - {v.get('note', '')}"
        if was is not None and was.get("verdict") in FINDINGS:
            pre.append(line)
            continue
        uid, core = key.rsplit("#", 1)[0], v.get("core", "")
        row = cur.get(key)
        if was is not None:
            if row is not None and was.get("code") == row.code:
                carried.append((key, line))
            else:
                intro.append(line)
            continue
        research_changed = row is not None and research_fp(row.claim.pointers, base_qdir, memo) != row.research
        if cores.get(uid) == core and research_changed:
            carried.append((key, line))
        else:
            code_changed = not (cores.get(uid) == core or core in gone_cores)
            (intro if code_changed or research_changed else pre).append(line)
    return intro, pre, carried


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
    """(refusals, warnings) for the push (`claims_carry.gate`)."""
    return claims_carry.gate(sys.modules[__name__], root)


def _parser() -> argparse.ArgumentParser:
    """The command line (lifted out of `main` by feature 370, the 100-statement cap)."""
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("owed")
    b = sub.add_parser("bundle")
    b.add_argument("--owed", action="store_true")
    b.add_argument("--module", default="")
    b.add_argument("--units", default="")
    b.add_argument("--out", default="")
    b.add_argument("--reason", default="")
    b.add_argument("--with", dest="context", default="", help="path::qualname,... shown as context, not judged")
    b.add_argument("--pages", default="", help="question files (NNNN-<id>[.drawing].html,...) added to the bundle")
    r = sub.add_parser("record")
    r.add_argument("--bundle", required=True)
    r.add_argument("--reply", required=True)
    tr = sub.add_parser("triage")
    tr.add_argument("--out", default="")
    td = sub.add_parser("triaged")
    td.add_argument("--bundle", required=True)
    td.add_argument("--reply", required=True)
    sub.add_parser("backfill")
    sub.add_parser("backfill-sections")
    sub.add_parser("report")
    sub.add_parser("gate")
    cc = sub.add_parser("carry")
    cc.add_argument("--feature", required=True)
    cc.add_argument("--task", default="")
    cc.add_argument("--keys", default="", help="findings a round-arbiter ruling carried, ';'-separated (with --ruling)")
    cc.add_argument("--ruling", default="", help="the arbiter.jsonl trigger that carried --keys")
    cv = sub.add_parser("coverage")
    cv.add_argument("--path", default="", help="only units whose file path contains this")
    ap.add_argument("--root", default=".")
    return ap


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    root = Path((_git(Path(args.root), "rev-parse", "--show-toplevel") or args.root).strip())
    if args.cmd == "gate":
        refuse, warn = gate(root)
        for w in warn:
            print(f"claims-gate: {w}")
        for x in refuse:
            print(f"claims-gate: REFUSED {x}")
        return 1 if refuse else 0
    if args.cmd == "carry":
        try:
            if bool(args.keys) != bool(args.ruling):
                raise ValueError("KEYS= and RULING= go together: the findings a round-arbiter ruling carried, and that ruling's trigger")
            keys = [k.strip() for k in args.keys.split(";") if k.strip()] if args.keys else [k for k, _ln in claims_carry.classified(sys.modules[__name__], root)[3] if k not in claims_carry.filed(root)]
            print(claims_carry.carry(root, args.feature, args.task, keys, ruling=args.ruling))
        except ValueError as e:
            print(f"claims-carry: {e}", file=sys.stderr)
            return 2
        return 0
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
        # THE GATE'S FORM CHECK, HERE TOO (feature 374 batch 4): a claim whose form is wrong (a GUESS naming the findings page,
        # not its drawing page) failed `test_claims_coverage` at the gate, a tooling test `make quick` never runs - a whole gate
        # for one word. Every session asks `claims-owed` after an edit, so it says so first.
        for x in form_problems(root):
            print(f"claims-form: {x} - the gate's test_claims_coverage fails on it")
        for x in claims_stale.stale(root):  # feature 385 T62: a changed constant's old figure, still on its research's pages
            print(x)
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
            print(
                f"claims-owed: {len(due) - len(full)} claim(s) owe only a TRIAGE of the blocks that changed on their pages - `make claims-triage` first; it sends on only the claims a change bears on"
            )
        return 0
    if args.cmd == "backfill-sections":
        n = backfill_sections(cur, index, store)
        save_index(root / INDEX, live_rows(cur, index))
        save_store(root / STORE, store)
        print(f"claims-backfill-sections: {n} section claim(s) re-keyed to their own line; none owed by it")
        return 0
    if args.cmd == "backfill":
        n = backfill(cur, index, qdir, store)
        save_index(root / INDEX, live_rows(cur, index))
        save_store(root / STORE, store)
        print(f"claims-backfill: {n} row(s) given the pages they were checked at")
        return 0
    if args.cmd == "triage":
        keys = [k for k, why in owed(cur, index, qdir, store) if why in TRIAGED]
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
        print(
            f"claims-triage: {len(keys)} claim(s); dispatch the `claims-triage` agent on the MANIFEST (a session started before 2026-10-17's amendment 6 landed: restart to load it), save its reply, then `make claims-triaged BUNDLE=<dir> REPLY=<file>`"
        )
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
        print(
            f"claims-triaged: {named + forced} of {len(data['units'])} sent on to impl-drift ({named} named by the reply"
            + (f", {forced} owed in full: a removed block's words could not be shown" if forced else "")
            + "); the rest cleared"
        )
        return 0
    if args.cmd == "report":
        print(report(cur, index, qdir, store, load_deferred(root / DEFERRED)))
        return 0
    if args.cmd == "bundle":
        due_all = owed(cur, index, qdir, store)
        due = {k: why for k, why in due_all if why not in TRIAGED}
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
        print(bundle(root, cur, keys, out, [c for c in args.context.split(",") if c], [p for p in args.pages.split(",") if p]))
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
    code = main()
    # THE EXIT, NOT THE WORK (feature 375 amendment 3, measured 2026-10-11 on 374's delta): with the units read through the
    # cache, the interpreter's final collection spent 3.2 s of a cold run walking the engine parse's objects before the
    # process ended. A command's heap dies with it; freezing it skips that walk. Only the command does this, never `main()`
    # called in-process (the gate's tests), where the objects must stay collectable.
    import gc

    gc.freeze()
    sys.exit(code)
