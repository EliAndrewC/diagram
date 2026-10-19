#!/usr/bin/env python3
"""The claims TRIAGE - one cheap agent over what changed, so a claim is re-judged only when a change bears on it (feature 318,
FR-016; feature 375, FR-002). Split out of `claims.py` (feature 375 T09) when the section triage would have taken that file
past the 1,000-line bar; `claims.py` imports everything here, so `make claims-triage` / `claims-triaged` are unchanged.

A claim citing questions is triaged when a page it cites changed without touching a block its verdict rests on; a claim of a
Mode A PROCEDURE SECTION is triaged when its section changed and its own line did not (feature 375, FR-002 - `tools/claims.py`
fingerprints a section claim by its line alone). The bundle shows the blocks new, changed or removed since each claim's check;
the reply names the claims a change bears on, and every other claim is cleared.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any

import record_units as ru

if TYPE_CHECKING:  # the row type `claims.py` defines; it imports this module, so only the type checker imports it back
    from claims import Row

QUESTIONS = "research/questions"


def _git(root: Path, *args: str) -> str | None:
    p = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=False)
    return p.stdout if p.returncode == 0 else None


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
    texts = ([kept_text(qdir, snapshot)] if snapshot else []) + [_git(qdir, "show", f"{sha}:./{name}") or "" for sha in (_git(qdir, "log", "--format=%H", f"-{depth}", "--", name) or "").split()]
    for text in texts:
        for b in ru.read_page(text).blocks:
            d = ru.digest([b.words])
            if d in digests and not b.intro:
                found.setdefault(d, b.words)
        if len(found) == len(digests):
            break
    return found


def section_words(root: Path, path: str, title: str, digests: set[str], depth: int = 60) -> dict[str, str]:
    """The words of the blocks `digests` of the procedure section `title` of `path` that no longer stand, read back from the
    document's git history (newest first, at most `depth` versions) - as `removed_words` does for a page."""
    from l7r.diagram.tools import claims as engine_claims  # noqa: PLC0415 - the engine's own section reader, one rule

    found: dict[str, str] = {}
    for sha in (_git(root, "log", "--format=%H", f"-{depth}", "--", path) or "").split():
        text = _git(root, "show", f"{sha}:{path}") or ""
        # a claimed dictionary's entries are read from the module as it stood (feature 385 T83), a section's from its document
        units = engine_claims.module_units(text, path)[2] if path.endswith(".py") else engine_claims.doc_units(text, path, None)
        for unit in units:
            if unit.qualname == title:
                for b in unit.blocks:
                    if (d := ru.digest([b])) in digests:
                        found.setdefault(d, b)
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
    by_page: dict[tuple[str, str], list[str]] = {}  # (page, the version its claims were checked at) - feature 385 plan D11
    changed: dict[str, list[str]] = {}
    gone: dict[str, list[str]] = {}
    lost: dict[tuple[str, str], bool] = {}
    forced: set[str] = set()
    sections: dict[str, tuple[list[str], list[str], list[str]]] = {}  # "path::title" -> (fresh, gone, keys) - feature 375 FR-002
    for key in keys:
        unit = cur[key].unit
        if unit.line_keyed and index[key].get("section") not in (None, unit.core):
            before = set(store.get(index[key]["section"], []))
            fresh = [b for b in unit.blocks if ru.digest([b]) not in before]
            now = {ru.digest([b]) for b in unit.blocks}
            missing = before - now
            words = section_words(qdir.parents[1], unit.path, unit.qualname, missing) if missing else {}
            if len(words) < len(missing):
                forced.add(key)
            got = sections.setdefault(f"{unit.path}::{unit.qualname}", ([], [], []))
            got[0].extend(w for w in fresh if w not in got[0])
            got[1].extend(w for d, w in sorted(words.items()) if w not in got[1])
            got[2].append(key)
        for name, old in dict(index[key].get("pages") or {}).items():
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
                # ...GROUPED BY THE VERSION EACH CLAIM WAS CHECKED AT (feature 385 T02, plan D11): one page's blocks were one
                # union for every claim citing it, so claims checked at different versions each saw the others' changes
                changed[f"{name}|{old}"] = fresh
                by_page.setdefault((name, old), []).append(key)
    # ...AND A CLAIM THE TRIAGE HAS NOTHING TO SHOW IS OWED IN FULL (feature 385 T03): a claim relabeled to cite a page its
    # last check never read had no changed block to show, so the bundle listed nothing and the agent could clear nothing
    shown = {k for ks in by_page.values() for k in ks} | {k for _f, _l, ks in sections.values() for k in ks}
    forced |= {k for k in keys if k not in shown}
    parts = [
        "# Triage of claim re-checks (feature 318)\n",
        "owed-checks: claims-triage\n",
        # what to decide and how to reply is the `claims-triage` agent's contract, its system prompt, read from the prompt cache
        # by every dispatch; here it followed the unique prompt and was written fresh each time (feature 383 amendment 6, D36)
        "For the `claims-triage` agent: rule on each claim below as your contract says, and reply in its form.\n",
    ]
    for where, (fresh, lost, ks) in sorted(sections.items()):  # `lost`, never `gone`: the pages' loop below reads `gone` (374)
        parts.append(f"## {where} (a procedure section; the claims' own lines did not change)\n\nNew or changed blocks:\n")
        parts += [f"> {w}\n" for w in fresh] or ["(none)\n"]
        if lost:
            parts.append("Removed blocks (no longer in the section):\n")
            parts += [f"> {w}\n" for w in lost]
        parts.append("Claims in it:\n")
        for k in sorted(ks):
            parts.append(f"- KEY `{k}`: `{cur[k].claim.line}` - last verdict {index[k].get('verdict')}: {index[k].get('note', '')}")
        parts.append("")
    for (name, old), ks in sorted(by_page.items()):
        parts.append(f"## {QUESTIONS}/{name}\n\n(against the version these claims were last checked at, {old[:12]})\n\nNew or changed blocks:\n")
        parts += [f"> {w}\n" for w in changed[f"{name}|{old}"]] or ["(none)\n"]
        if gone.get(f"{name}|{old}"):
            parts.append("Removed blocks (no longer on the page):\n")
            parts += [f"> {w}\n" for w in gone[f"{name}|{old}"]]
        parts.append("Claims citing it:\n")
        for k in sorted(ks):
            parts.append(f"- KEY `{k}`: `{cur[k].claim.line}` - last verdict {index[k].get('verdict')}: {index[k].get('note', '')}")
        parts.append("")
    (out / "MANIFEST.md").write_text("\n".join(parts) + "\n", encoding="utf-8")
    units = {
        k: {
            "research": cur[k].research,
            "pages": {ptr.rsplit("/", 1)[1]: page_blocks(ptr.rsplit("/", 1)[1], qdir, memo)[0] for ptr in cur[k].claim.pointers},
            **({"section": cur[k].unit.core} if cur[k].unit.line_keyed else {}),
        }
        for k in keys
    }
    snaps = {fp: [d for d, _w in blocks] for fp, blocks in memo.values()}
    snaps |= {cur[k].unit.core: [ru.digest([b]) for b in cur[k].unit.blocks] for k in keys if cur[k].unit.line_keyed}
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
            if "section" in fp:
                row["section"] = fp["section"]
            row.pop("triage", None)
        out[key] = row
    return out, msgs
