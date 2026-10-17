#!/usr/bin/env python3
"""The pop-up triage - a drawing or question page's edit owes a pop-up's checks only where it bears on that pop-up (feature
375, FR-001, plan D1).

WHY. Measured on feature 372 (2026-10-10): about twelve `modal-depiction` runs came back clean, owed only because 0100's or
0105's drawing page changed somewhere the pop-up never read - `modal_owed.py` owed every kind whose `Drawing:` or `Entry:`
names a moved page, whatever moved. `make claims-triage` already answered the same question for claims with one cheap agent
over the changed blocks (feature 318); this is that triage for the pop-ups.

THE RULE. A modal unit owed ONLY because a page it names moved (`modal_owed.owed`'s "a page its ... names moved") is owed a
triage first. `make modal-triage` writes one bundle: per moved page, the blocks new, changed or removed since the unit was
last answered - the page as that check read it, kept as a blob by `make modal-bundle` (`page:` lines in its MANIFEST), else
the merge base - and each kind naming the page with its About and Depiction. One ad-hoc agent (model opus) replies one
`TOUCHES <uid> @ <page file name> - <which block>` line per (kind, page) a change bears on; `make modal-triaged BUNDLE= REPLY=`
answers every other unit at its current fingerprint (result `triage: untouched` - cleared on the record) and marks touched only
the units whose check READS a named page - a question page owes the research checks, a drawing page `modal-depiction` (feature
375 amendment 1: 343's triage owed 11 of 61 units for pages their checks never read); a line naming no page owes them all. `make modal-bundle` refuses a unit owed only a triage until that triage has named it.

    modal_triage.py bundle [--out DIR]               the triage bundle for every unit owed only a triage
    modal_triage.py record --bundle DIR --reply F    apply a triage reply
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys
from collections.abc import Mapping, Sequence

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True
import modal_owed as mo  # noqa: E402
import record_owed as ro  # noqa: E402
import record_units as ru  # noqa: E402

DEFAULT_OUT = pathlib.Path("/tmp/l7r-check/modal-triage")
#: in the record-checks store: {slug: fingerprint} of the units a triage named, owed the full check at that fingerprint
TOUCHED = "modal-triage-touched.json"
#: `TOUCHES <uid> [@ <page file name>] - <block>` (feature 375 amendment 1, FR-015: the page scopes which of the pop-up's checks
#: are owed - a question page its research checks, a drawing page its `modal-depiction`; a line naming no page owes them all)
_TOUCHES = re.compile(r"^TOUCHES\s+`?(\S+?)`?(?:\s+@\s+`?(\S+?)`?)?\s+-\s+(.*)$")


def triage_only(why: str) -> bool:
    """Whether `modal_owed.owed` owes the unit only because a page it names moved (its own words unchanged)."""
    return why.startswith("a page its ")


def touched(store: pathlib.Path) -> dict[str, str]:
    f = store / TOUCHED
    return json.loads(f.read_text(encoding="utf-8")) if f.is_file() else {}


def pending(root: pathlib.Path, base: str, store: pathlib.Path, owed: Sequence[tuple[str, str, str]] | None = None) -> list[tuple[str, str, str]]:
    """(slug, why, fingerprint) of every unit owed only a triage: unanswered at its fingerprint and not named by a triage.
    `owed` is the pop-ups' owed rows when the caller has them already (`modal_bundle`, feature 375 amendment 3 plan D27)."""
    named = touched(store)
    return [(slug, why, fp) for slug, why, fp in (owed if owed is not None else mo.owed(root, base)) if triage_only(why) and not ro.answered(store, slug, fp) and named.get(slug) != fp]


def keep(root: pathlib.Path, path: str) -> str:
    """The page at `path` written into the clone's object store as it stands; its blob id, or '' (no such file)."""
    f = root / path
    if not f.is_file():
        return ""
    run = subprocess.run(["git", "-C", str(root), "hash-object", "-w", "--", path], capture_output=True, text=True, check=False)
    return run.stdout.strip() if run.returncode == 0 else ""


def _blob(root: pathlib.Path, blob: str) -> str:
    run = subprocess.run(["git", "-C", str(root), "cat-file", "-p", blob], capture_output=True, text=True, check=False)
    return run.stdout if run.returncode == 0 else ""


def before(root: pathlib.Path, store: pathlib.Path, slug: str, path: str, base: str) -> str:
    """The page `path` as the unit's last answer read it (its kept blob), else as the merge base holds it."""
    blob = dict(ro._read(store, slug).get("pages") or {}).get(path, "")
    return (_blob(root, blob) if blob else "") or (mo._read_at(root, base)(path) or "" if base else "")


def baseline(store: pathlib.Path, slug: str, path: str) -> str:
    """Which version of `path` a unit's triage diffs against: the blob its last answer kept, or "" for the merge base."""
    return str(dict(ro._read(store, slug).get("pages") or {}).get(path, ""))


def changed_blocks(old: str, new: str) -> tuple[list[str], list[str]]:
    """(blocks new or changed, blocks removed) between two versions of a page, by their words."""
    was = [b.words for b in ru.read_page(old).blocks]
    now = [b.words for b in ru.read_page(new).blocks]
    return [w for w in now if w not in was], [w for w in was if w not in now]


def _pages_of(m: mo.Modal, check: str) -> list[str]:
    return m.drawing_files() if check == mo.DEPICTION_CHECK else m.entry_files()


def bundle(root: pathlib.Path, out: pathlib.Path, base: str = "") -> tuple[pathlib.Path | None, int]:
    """Write the triage bundle (MANIFEST.md, triage.json); (its MANIFEST, how many units it carries). `base` defaults to the
    merge base; the SC-001 replay passes a commit's parent."""
    base = base or ro.merge_base(root)
    store = ro.store(root)
    units = pending(root, base, store)
    if not units:
        return None, 0
    modals = {m.uid: m for m in mo.modals_now(root, about_only=False)}
    # ...GROUPED BY BASELINE (feature 385 T02, plan D11): a page's changed blocks are listed once for every unit diffing against
    # the SAME version of it - the blob its last check read, or the merge base - never one union for all; one unit on the merge
    # base made every unit of T01's triage show two new bullets the others had already been checked against
    by_page: dict[tuple[str, str], dict[str, set[str]]] = {}
    blocks: dict[tuple[str, str], tuple[list[str], list[str]]] = {}
    reads: dict[str, list[str]] = {}  # slug -> the moved pages its check reads (FR-015: a reply line owes only the units reading its page)
    blobs: dict[str, dict[str, str]] = {}  # slug -> {page: the blob this triage showed it} - kept with its answer (D11)
    for slug, why, _fp in units:
        check, uid = slug.split(":", 1)
        m = modals.get(uid)
        if m is None:
            continue
        for path in _pages_of(m, check):
            if pathlib.Path(path).name not in why:
                continue
            now = (root / path).read_text(encoding="utf-8") if (root / path).is_file() else ""
            key = (path, baseline(store, slug, path))
            if key not in blocks:
                blocks[key] = changed_blocks(before(root, store, slug, path, base), now)
            by_page.setdefault(key, {}).setdefault(uid, set()).add(check)
            reads.setdefault(slug, []).append(path)
            blobs.setdefault(slug, {})[path] = keep(root, path)
    if out.exists():
        for f in out.iterdir():
            f.unlink()
    out.mkdir(parents=True, exist_ok=True)
    parts = [
        "# Triage of pop-up checks (feature 375, FR-001)\n",
        "owed-checks: modal-triage\n",
        # what to decide and how to reply is the `modal-triage` agent's contract, its system prompt, read from the prompt cache
        # by every dispatch; here it followed the unique prompt and was written fresh each time (feature 383 amendment 6, D36)
        "For the `modal-triage` agent: rule on each pop-up below as your contract says, and reply in its form.\n",
    ]
    for key in sorted(by_page):
        path, base_blob = key
        fresh, gone = blocks[key]
        against = "against the version these pop-ups' last check read" if base_blob else "against the merge base (no check has read it yet)"
        parts.append(f"## {path}\n\n({against})\n\nNew or changed blocks:\n")
        parts += [f"> {w}\n" for w in fresh] or ["(none)\n"]
        if gone:
            parts.append("Removed blocks (no longer on the page):\n")
            parts += [f"> {w}\n" for w in gone]
        parts.append("Pop-ups naming it:\n")
        for uid in sorted(by_page[key]):
            m = modals[uid]
            parts.append(
                f"- UID `{uid}` ({', '.join(sorted(by_page[key][uid]))}): About - {m.tags.get('About', '')[:400]}"
                + (f" | Depiction - {m.tags.get('Depiction', '')[:400]}" if m.tags.get("Depiction") else "")
            )
        parts.append("")
    (out / "MANIFEST.md").write_text("\n".join(parts) + "\n", encoding="utf-8")
    (out / "triage.json").write_text(json.dumps({"units": {s: fp for s, _w, fp in units}, "pages": reads, "blobs": blobs}, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return out / "MANIFEST.md", len(units)


def _reads(page: str, unit_pages: Sequence[str]) -> bool:
    """Does a unit whose checks read `unit_pages` read the page a reply line named (by its file name, or its stem)?"""
    name = pathlib.Path(page).name
    return any(pathlib.Path(p).name in (name, name + ".html") for p in unit_pages)


def record(
    store: pathlib.Path, units: Mapping[str, str], reply: str, pages: Mapping[str, Sequence[str]] | None = None, blobs: Mapping[str, Mapping[str, str]] | None = None
) -> list[str]:
    """Apply a triage reply: a unit is marked touched (owed its full check at this fingerprint) when a line names its pop-up AT
    one of the pages the unit's check reads (`pages`, from triage.json - FR-015), or names its pop-up with no page (owing all of
    its units, failing toward checking); every other unit is answered at its fingerprint, `triage: untouched`. Only lines that
    OPEN with `TOUCHES ` name anything."""
    named: dict[str, list[tuple[str, str]]] = {}
    for raw in reply.split("\n"):
        if m := _TOUCHES.match(raw.strip().strip("`")):
            named.setdefault(m.group(1).strip("`"), []).append((m.group(2) or "", m.group(3)))
    uids = {s.split(":", 1)[1] for s in units}
    msgs = [f"refused: `{u}` is not a pop-up of this triage" for u in sorted(set(named) - uids)]
    mark = touched(store)
    for slug, fp in sorted(units.items()):
        uid = slug.split(":", 1)[1]
        lines = named.get(uid, [])
        known = [p for ps in (pages or {}).values() for p in ps]
        # a page the bundle never showed (misnamed, bare, unchanged) is read as no page: it owes all, never clears (plan review)
        hit = [why for page, why in lines if not page or pages is None or slug not in pages or not _reads(page, known) or _reads(page, pages[slug])]
        if hit:
            mark[slug] = fp
            msgs.append(f"touched: {slug} - {hit[0]}")
        else:
            # ...KEEPING THE PAGES THE TRIAGE SHOWED IT (feature 385 T02, plan D11): an untouched answer written with none erased the
            # blob the check before it kept, and every later triage of the unit fell back to the merge base
            kept = {**dict(ro._read(store, slug).get("pages") or {}), **dict((blobs or {}).get(slug) or {})}
            ro.write_answer(store, slug, fp, "triage: untouched", kept or None)
    store.mkdir(parents=True, exist_ok=True)
    (store / TOUCHED).write_text(json.dumps(mark, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return msgs


def refusal(root: pathlib.Path, m: mo.Modal, check: str, owed: Sequence[tuple[str, str, str]] | None = None) -> str:
    """Why `make modal-bundle` may not bundle `check` on `m` yet: a unit of it owed only a triage that has not named it."""
    base = ro.merge_base(root)
    store = ro.store(root)
    slugs = {f"{c}:{m.uid}" for c in ((check,) if check != mo.RESEARCH_AGENT else mo.RESEARCH_CHECKS)}
    waiting = [s for s, _w, _fp in pending(root, base, store, owed) if s in slugs]
    return (
        (f"{', '.join(sorted(waiting))} owe(s) only a TRIAGE (a page it names moved, its own words did not) - `make modal-triage` first; it sends on only the pop-ups a change bears on")
        if waiting
        else ""
    )


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("bundle")
    b.add_argument("--out", default="")
    r = sub.add_parser("record")
    r.add_argument("--bundle", required=True)
    r.add_argument("--reply", required=True)
    ap.add_argument("--root", default=".")
    a = ap.parse_args(argv)
    root = pathlib.Path(a.root).resolve()
    if a.cmd == "bundle":
        manifest, n = bundle(root, pathlib.Path(a.out) if a.out else DEFAULT_OUT)
        if manifest is None:
            print("modal-triage: no pop-up is owed a triage")
            return 0
        print(manifest)
        print(
            f"modal-triage: {n} unit(s); dispatch the `modal-triage` agent on the MANIFEST (a session started before 2026-10-17's amendment 6 landed: restart to load it), save its reply, then "
            "`make modal-triaged BUNDLE=<dir> REPLY=<file>`"
        )
        return 0
    data = json.loads((pathlib.Path(a.bundle) / "triage.json").read_text(encoding="utf-8"))
    msgs = record(ro.store(root), data["units"], pathlib.Path(a.reply).read_text(encoding="utf-8"), data.get("pages"), data.get("blobs"))
    for msg in msgs:
        print(f"modal-triaged: {msg}")
    n = sum(1 for msg in msgs if msg.startswith("touched"))
    print(f"modal-triaged: {n} of {len(data['units'])} unit(s) sent on to their checks; the rest answered `triage: untouched`")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
