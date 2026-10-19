#!/usr/bin/env python3
"""Which record checks this delta owes, and which are still unanswered - the one scripted answer (feature 311).

WHY (GM 2026-10-02): *"I do worry about a future session making some extremely minor formatting tweak or something and then
having that literally rerun every subagent check for all 2,000 something of our resources just because like the tooling was
not preventing it or was too dumb to to flag what things actually needed to be rechecked"* - and an owed check skipped is the
other half of the same failure. So every record check is owed by what the delta touched (`record_units.py` decides it from
the words), the push refuses an owed unit with no current answer (`scripts/gates/entry-gate.sh`, the record gate), and a bundle or a
dispatch for a check nothing owes is refused (`check_bundle.py`, `check-bundle-hooks.sh`).

THE UNITS. `_record_units.owed` for intro-check, record-format, source-reader, quote-check and source-applicability; the
translation pairs `translation_owed.py` names (`translation-check:<page>#<note>`); the modals `entry_owed.py` names
(`entry-drift:<modal key>`). Against the merge base with origin/main and the WORKING TREE (what the push will carry once
committed), or between two revisions (`--between A B`, the replay of spec SC-002; it omits entry-drift, which reads the engine).

THE ANSWER RECORD (plan D6). `--answer CHECK` writes, per unit, `<git common dir>/record-checks/<slug>.json` holding the unit's
fingerprint; the unit is answered while its fingerprint now equals the recorded one. From a bundle (`--bundle DIR`: the
fingerprints the bundle recorded when it was built, i.e. what the check read) or from the tree now (`--q`, `--notes`, `--key`,
`--kind`: `source-reader`, which reads before the note exists, and fixes that apply the check's own findings). In the clone
that pushes, as the review records are. A round's own EDIT blocks applied verbatim by `make apply-edits` SETTLE with that
round's answer instead of owing the unit again (`settle`; feature 335's round arbiter, 2026-10-11).

    record_owed.py [--root DIR] [--q NNNN] [--unanswered] [--slugs]   the owed units, with the command that answers each
    record_owed.py --between A B                                       a historical commit pair
    record_owed.py --answer CHECK --result "<counts>" (--bundle DIR | --q NNNN [--notes k,k] | --key K | --kind K)
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import subprocess
import sys
import time
import urllib.parse
from collections.abc import Collection, Mapping, Sequence
from typing import Any

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path[1:1] = [str((pathlib.Path(__file__).resolve().parent / _d).resolve()) for _d in ('../hooks/lib',)]  # the moved scripts it imports (2026-10-08)
# no __pycache__ beside the scripts: the push runs this in fixture trees whose `git status` must stay clean
sys.dont_write_bytecode = True
import record_cache as rc  # noqa: E402
import record_units as ru  # noqa: E402

_SOURCE_FILE = re.compile(r"^\d+-([a-z0-9-]+)\.html$")  # a write-up number runs past four digits (20500-...)


def _git(root: pathlib.Path, *args: str, stdin: str | None = None) -> str:
    p = subprocess.run(["git", "-C", str(root), *args], input=stdin, capture_output=True, text=True, check=False)
    return p.stdout if p.returncode == 0 else ""


def merge_base(root: pathlib.Path) -> str:
    if _git(root, "rev-parse", "--verify", "-q", "origin/main").strip():
        return _git(root, "merge-base", "HEAD", "origin/main").strip()
    return _git(root, "rev-parse", "--verify", "-q", "HEAD").strip()


def changed_sources(root: pathlib.Path, base: str, head: str | None) -> set[str]:
    """The write-ups that differ between `base` and `head` (None: the working tree, untracked files included) - the only
    ones a source-applicability unit can be owed on, so the other two thousand are never read (plan D2)."""
    if head is None:
        names = _git(root, "diff", "--name-only", base, "--", *ru.SOURCE_DIRS).split() + _git(root, "ls-files", "--others", "--exclude-standard", "--", *ru.SOURCE_DIRS).split()
    else:
        names = _git(root, "diff", "--name-only", base, head, "--", *ru.SOURCE_DIRS).split()
    return {n.rsplit("/", 1)[1] for n in names}


def read_at(root: pathlib.Path, rev: str | None, sources: set[str] | None = None) -> ru.Record:
    """The record at `rev` (None: the working tree), read with ONE ls-tree and ONE cat-file batch (plan D2); of the source
    write-ups, only those named in `sources` (None: all)."""
    if rev is None:
        qdir = root / ru.QUESTIONS
        files = {p.name: p.read_text(encoding="utf-8") for p in qdir.glob("*.html")} if qdir.is_dir() else {}
        src = {p.name: p.read_text(encoding="utf-8") for d in ru.SOURCE_DIRS for p in (root / d).glob("*.html") if sources is None or p.name in sources}
    else:
        names = _git(root, "ls-tree", "-r", "--name-only", rev, "--", ru.QUESTIONS, *ru.SOURCE_DIRS).split("\n")
        is_src = lambda n: n.startswith(tuple(d + "/" for d in ru.SOURCE_DIRS))  # noqa: E731
        names = [n for n in names if n.endswith(".html") and (sources is None or not is_src(n) or n.rsplit("/", 1)[1] in sources)]
        blobs = _blobs_at(root, rev, names)
        files = {n.rsplit("/", 1)[1]: b for n, b in zip(names, blobs, strict=True) if n.startswith(ru.QUESTIONS + "/")}
        src = {n.rsplit("/", 1)[1]: b for n, b in zip(names, blobs, strict=True) if is_src(n)}
    sources = {m.group(1): text for name, text in src.items() if (m := _SOURCE_FILE.match(name))}
    cache = parse_cache(root)
    record = ru.Record.of(files, sources, cache)
    cache.save()
    return record


_REV_FILES: dict[pathlib.Path, rc.ParseCache] = {}


def _blobs_at(root: pathlib.Path, rev: str, names: list[str]) -> list[str]:
    """The files `names` at commit `rev`, kept by the two (feature 383, plan D6): a commit never changes, and a bundle, the
    owed checks and the record gate each read the merge base's record again - 0.2 s a read, three reads a bundle."""
    if root not in _REV_FILES:
        _REV_FILES[root] = rc.ParseCache.at(root, "rev-files", HERE / "record_cache.py")
        _REV_FILES[root].PRUNE_AT = 2  # a revision's record is 5 MB: keep this run's revisions and as many again, no more
    cache = _REV_FILES[root]
    blobs = cache.get(rc.text_key(rev, *names), lambda: _cat(root, [f"{rev}:{n}" for n in names]))
    cache.save()
    return blobs


_CACHES: dict[pathlib.Path, rc.ParseCache] = {}


def parse_cache(root: pathlib.Path) -> rc.ParseCache:
    """The clone's record-parse cache, one per run (feature 375 amendment 3, plan D27): keyed by each file's text, and its
    file named by `record_units.py`'s own source, so a change to the parser never reads an older parse."""
    if root not in _CACHES:
        _CACHES[root] = rc.ParseCache.at(root, "record-parse", HERE / "record_units.py")
    return _CACHES[root]


_cat = rc.cat_blobs  # translation_owed imports it by this name


def _translation_units(root: pathlib.Path, now: ru.Record) -> list[ru.Unit]:
    import translation_owed as to  # noqa: PLC0415

    units = {}
    for notes_file, key, *_ in to.owed(root):
        m = ru._STEM.match(notes_file.rsplit("/", 1)[1].replace(".notes.html", ".html"))
        if m is None:
            continue
        stem = ru._subject(m)
        note = key if key != "a term's gloss" else "gloss"
        slug = f"translation-check:{stem}#{note}"
        fp = ru.digest([now.notes.get(stem, {}).get(key, ""), *(b.words for b in now.pages.get(stem, ru.Page()).blocks)] if note == "gloss" else [now.notes.get(stem, {}).get(key, "")])
        units[slug] = ru.Unit(slug, "a translated quotation is new or changed", fp)
    return list(units.values())


def _entry_units(root: pathlib.Path, now: ru.Record) -> list[ru.Unit]:
    import entry_owed as eo  # noqa: PLC0415
    import modal_owed as mo  # noqa: PLC0415

    _, lines = eo.owed(root)
    about = mo.about_keys(root)  # feature 319: an About-form modal owes modal-accuracy instead (plan D6)
    units = []
    for line in lines:
        key, _, rest = line.partition(" - ")
        if key in about:
            continue
        hits = rest.split(" - ", 1)[0].split()
        stems = [ru._subject(m) for h in hits if (m := ru._STEM.match(h))]
        fp = ru.digest([key, *(b.words for s in stems for b in now.pages.get(s, ru.Page()).blocks if not b.intro)])
        units.append(ru.Unit(f"entry-drift:{key}", f"its section's findings moved ({' '.join(hits)})", fp))
    return units


def _modal_units(root: pathlib.Path, base: str, uid: str = "") -> list[ru.Unit]:
    """The About-form modals' units (feature 319, plan D6): `modal-form`, and the three `modal-research` answers; `uid`
    scopes them to one pop-up."""
    import modal_owed as mo  # noqa: PLC0415

    return [ru.Unit(slug, why, fp) for slug, why, fp in mo.owed(root, base, uid)]


#: the families of owed units, each computed by its own reader: a bundle asks only for the ones it carries (feature 375
#: amendment 3, FR-020(d): a pop-up's bundle computed the whole delta to print one pop-up's lines)
FAMILIES = ("record", "translation", "entry-drift", "modal")


def units(root: pathlib.Path, base: str | None = None, head: str | None = None, families: Sequence[str] = FAMILIES, uid: str = "") -> list[ru.Unit]:
    """Every owed unit, against the merge base and the working tree, or between two revisions; `families` and, for the
    pop-ups, `uid` scope it to what a caller carries (the whole delta by default)."""
    base = base or merge_base(root)
    out: list[ru.Unit] = []
    now = None
    if "record" in families or "translation" in families or "entry-drift" in families:
        touched = changed_sources(root, base, head) if base else None
        now = read_at(root, head, touched)
        if "record" in families:
            out = ru.owed(now, read_at(root, base, touched) if base else ru.Record({}, {}, {}, {}))
    if head is None:
        if "translation" in families and now is not None:
            out += _translation_units(root, now)
        if "entry-drift" in families and now is not None:
            out += _entry_units(root, now)
        if "modal" in families:
            out += _modal_units(root, base, uid)
    return sorted(out, key=lambda u: u.slug)


def store(root: pathlib.Path) -> pathlib.Path:
    """Where the answer records live: the clone's git dir, or `RECORD_CHECKS_DIR` (a test's throwaway store)."""
    if os.environ.get("RECORD_CHECKS_DIR"):
        return pathlib.Path(os.environ["RECORD_CHECKS_DIR"])
    common = _git(root, "rev-parse", "--git-common-dir").strip() or ".git"
    path = pathlib.Path(common)
    return (path if path.is_absolute() else root / path) / "record-checks"


def _file(store_dir: pathlib.Path, slug: str) -> pathlib.Path:
    return store_dir / (urllib.parse.quote(slug, safe="") + ".json")


def _read(store_dir: pathlib.Path, slug: str) -> dict:
    try:
        return json.loads(_file(store_dir, slug).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def write_answer(store_dir: pathlib.Path, slug: str, fp: str, result: str, pages: dict[str, str] | None = None) -> None:
    """Record an answer. Every fingerprint ever answered is kept: an answer is about WORDS, so content reverted to words a
    check already passed stays answered (an edit answered and then undone owed its unit again when only the last was kept)."""
    store_dir.mkdir(parents=True, exist_ok=True)
    old = _read(store_dir, slug)
    seen = [f for f in old.get("answered", []) if f != fp] + [fp]
    settles = dict(old.get("settles", {}))
    if fp in settles:  # the round's own EDITs were applied before this answer was recorded: they settle with it (see settle)
        seen.append(settles.pop(fp))
    rec = {"unit": slug, "fingerprint": fp, "answered": seen, "result": result, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    if pages:  # feature 375 (plan D1): the pages this answer's check read, as blobs - what a later triage diffs against
        rec["pages"] = pages
    if settles:
        rec["settles"] = settles
    _file(store_dir, slug).write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")


#: what an answer settled by its round's own EDIT blocks records as its result
SETTLED = "settled - only its round's own EDIT blocks were applied, verbatim, since it was answered (make apply-edits)"


def settle(store_dir: pathlib.Path, slug: str, before: str, after: str) -> str:
    """A unit whose content moved from `before` to `after` by NOTHING but its last round's own EDIT blocks, applied verbatim
    by `make apply-edits`, is not owed that check again (feature 335's round arbiter, 2026-10-11, rulings
    `round:record-format|q:0104@3` and `ask:f335-garden-modal-depiction`: applying a round's own words re-owed the unit, the
    next round found nothing new, and the round cap fired on a loop of the tooling's making).

    Order-independent: if `before` is already answered, `after` is answered now ("answered"); if not (the reply applied
    before `make record-checked` records it - a frozen page's own order), `{before: after}` is kept pending and
    `write_answer` adds `after` when it records `before` ("pending"). Narrow: it fires only where `before` is EXACTLY the
    content the round answered, so any other change since that round - a hand edit, another reply - still owes the unit."""
    if not before or not after or before == after:
        return ""
    rec = _read(store_dir, slug)
    if answered(store_dir, slug, before):
        if after not in rec.get("answered", []):
            # the round's own counts are kept beside the note: a reader of `result` still sees what the check returned
            write_answer(store_dir, slug, after, f"{SETTLED}; was: {rec.get('result', '')}", rec.get("pages"))
        return "answered"
    store_dir.mkdir(parents=True, exist_ok=True)
    rec.setdefault("unit", slug)
    rec["settles"] = {**rec.get("settles", {}), before: after}
    _file(store_dir, slug).write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    return "pending"


#: a reply's counts line names its agent; modal-research answers three units
_AGENT_CHECKS = {"modal-research": ("modal-accuracy", "modal-references", "modal-gaps")}


#: the checks a reply's counts line may name - a BATCH reply (one agent, several pop-ups; feature 385 FR-009) opens with prose
#: and carries one counts line per unit (`modal-depiction: choice.well_siting--lane - COVERAGE 0 ...`)
BATCH_CHECKS = ("modal-depiction", "modal-form", "modal-research", "quote-check", "record-format", "intro-check", "entry-drift")


def reply_checks(reply: str) -> tuple[str, ...]:
    """The checks whose units a reply answers, from its FIRST line (`record-format: 33 of 33 ...`), else from the first counts
    line of a known check anywhere in it (a batch reply: the round arbiter's tooling fix on ask:t05-lane-popup-round3, where a
    batch's own verbatim EDIT, applied, re-owed a third round because its reply's first line named no check), else ()."""
    first = next((ln.strip() for ln in reply.splitlines() if ln.strip()), "")
    m = re.match(r"`?([a-z]+(?:-[a-z]+)+):", first)
    if not m:
        m = re.search(rf"^`?({'|'.join(BATCH_CHECKS)}): \S", reply, re.M)
    if not m:
        return ()
    return _AGENT_CHECKS.get(m.group(1), (m.group(1),))


def fingerprints(root: pathlib.Path, checks: Sequence[str]) -> dict[str, str]:
    """{slug: fingerprint} of every owed unit of `checks` in the working tree now."""
    return {u.slug: u.fingerprint for u in units(root) if u.check in checks}


def answered(store_dir: pathlib.Path, slug: str, fp: str, reading: str = "") -> bool:
    """`fp` answered - or, for a source-reader note, its `reading` (the pages and passages it reads) answered under another
    fingerprint: a note READ and then re-worded in English alone is not owed source-reader again (352, the arbiter's fix)."""
    rec = _read(store_dir, slug)
    return fp == rec.get("fingerprint") or fp in rec.get("answered", []) or bool(reading and reading in rec.get("readings", []))


def unanswered(root: pathlib.Path) -> list[ru.Unit]:
    s = store(root)
    return [u for u in units(root) if not answered(s, u.slug, u.fingerprint, u.reading) and not legacy_depiction_answered(root, s, u.slug)
            and not amendment1_depiction_answered(root, s, u.slug)]


def keep_reading(store_dir: pathlib.Path, slug: str, reading: str) -> None:
    """Add a source-reader answer's `reading` to its record (`answered` matches on it)."""
    rec = _read(store_dir, slug)
    if not reading or not rec or reading in rec.get("readings", []):
        return
    rec["readings"] = [*rec.get("readings", []), reading]
    _file(store_dir, slug).write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")


def _modal_then(root: pathlib.Path, m: Any, utc: str) -> Any:
    """The pop-up `m` as its file stood when an answer was recorded at `utc` (the last commit before it), or None - a pop-up
    in a `.py` docstring, or none committed by then."""
    import modal_owed as mo  # noqa: PLC0415

    path = m.origin.rsplit(":", 1)[0] if re.search(r":\d+$", m.origin) else m.origin
    rel = str(pathlib.Path(path).resolve().relative_to(root)) if pathlib.Path(path).is_absolute() else path
    then = _git(root, "rev-list", "-1", f"--before={utc}", "HEAD", "--", rel).strip()
    return mo.choice_modal(rel, _git(root, "show", f"{then}:{rel}")) if then and rel.endswith(".md") else None


def legacy_depiction_answered(root: pathlib.Path, store_dir: pathlib.Path, slug: str) -> bool:
    """A modal-depiction answer recorded under the fingerprint's OLD formula (before feature 375 amendment 1) still answers
    the words it read. The new formula covers what the check reads - About, Entry:, Depiction, Drawing: and its pages - and
    dropped Name, Guesses and Form; the old one covered all of those but Entry:. So an old-formula answer that matches today's
    content answers today's unit when the Entry: line is the one the modal carried when the answer was recorded. Without
    this, the formula change re-owed every depiction answer in every clone at once (343's sheet pop-ups and 368's hamlet
    pop-ups: 31 units, checked and answered, all owed again on the merge, 2026-10-11)."""
    if not slug.startswith("modal-depiction:"):
        return False
    import modal_owed as mo  # noqa: PLC0415

    rec = _read(store_dir, slug)
    m = mo.find(root, slug.split(":", 1)[1])
    if m is None or not rec.get("utc") or not answered(store_dir, slug, mo.legacy_depiction_fingerprint(root, m)):
        return False
    old = _modal_then(root, m, rec["utc"])
    return old is not None and old.entry == m.entry


def amendment1_depiction_answered(root: pathlib.Path, store_dir: pathlib.Path, slug: str) -> bool:
    """A modal-depiction answer recorded under amendment 1's formula (About in it) still answers its pop-up where what the check
    judges since amendment 6 (FR-028) - the Entry:, the Depiction tab, Drawing: and its pages - is unchanged since the answer:
    the pop-up as it stood then has the answer under amendment 1's formula, and the same fingerprint under today's as today.
    Without this, dropping About from the fingerprint owed every About-form pop-up's depiction once, in every clone."""
    if not slug.startswith("modal-depiction:"):
        return False
    import modal_owed as mo  # noqa: PLC0415

    rec = _read(store_dir, slug)
    m = mo.find(root, slug.split(":", 1)[1])
    old = _modal_then(root, m, rec["utc"]) if m is not None and rec.get("utc") else None
    return (
        old is not None
        and answered(store_dir, slug, mo.amendment1_depiction_fingerprint(root, old))
        and mo.depiction_fingerprint(root, old) == mo.depiction_fingerprint(root, m)
    )


def command(u: ru.Unit, now: ru.Record | None = None, triaged: Mapping[str, str] | None = None) -> str:
    """What builds the bundle for a unit - named in every report and refusal, so a session never has to work it out. `triaged`
    is the triage's touched marks ({slug: fingerprint}): a pop-up a triage sent on is bundled like any other (feature 385 T93)."""
    q, check = ru.question(u.subject), u.check
    if check == "source-applicability":
        return f"make check-bundle KEY={u.subject}"
    if check == "source-reader":
        stem, _, note = u.subject.partition("#")
        keys = list(now.cites.get(stem, {}).get(note, ())) if now else []
        keys = keys or ["<the note's key>"]
        return " ; ".join(f"make check-bundle KEY={k} WHOLE=1" for k in dict.fromkeys(keys)) + f"  then  make record-checked CHECK=source-reader Q={q} NOTES={note}"
    if check.startswith("modal-") and triage_first(u, triaged):  # feature 375 FR-001: owed only by a moved page, not yet triaged
        return "make modal-triage  then  make modal-triaged BUNDLE=<its bundle> REPLY=<the reply>  (a kind it names is then bundled as below)"
    if check.startswith("modal-"):  # feature 319: a modal's units; the three research units are one modal-research dispatch
        agent = check if check in ("modal-form", "modal-depiction") else "modal-research"
        return f"make modal-bundle KIND=\"{u.subject}\" FOR={agent}  then  make record-checked CHECK={check} BUNDLE=<its bundle> RESULT=..."
    if check == "entry-drift":
        found = re.search(r"\b(\d{4})-", u.occasion)  # the subject is a modal key ("threshing yard"), never a question
        kinds = modal_classes(u.subject) or [f"<the class of {u.subject}>"]
        qq = found.group(1) if found else "<its section>"
        return " ; ".join(f'make check-bundle Q={qq} FOR=entry-drift KIND="{k}"' for k in kinds) + \
            f'  then  make record-checked CHECK=entry-drift KIND="{u.subject}" BUNDLE=<its bundle> RESULT=<verdict>'
    return f"make check-bundle Q={q} FOR={check}"


_KINDS = pathlib.Path(__file__).resolve().parents[2] / "l7r/diagram/interactive"


def modal_classes(key: str, base: pathlib.Path = _KINDS) -> list[str]:
    """The modal class(es) whose `key` is this one, as `make check-bundle KIND=` takes them - module-qualified when the
    key lives in more than one module (the map's Well and the sheet's). A tip that left `<the class of ...>` for the
    session to look up sent it searching three files (2026-10-03)."""
    hits = []
    for path in sorted([*base.glob("classes/*.py"), *base.glob("compound_kinds/*.py")]):
        cls = ""
        for line in path.read_text(encoding="utf-8").splitlines():
            if m := re.match(r"class (\w+)\(", line):
                cls = m.group(1)
            elif cls and re.match(rf"\s+key = ['\"]{re.escape(key)}['\"]\s*$", line):
                hits.append((path.stem, cls))
    return [f"{mod}.{cls}" if len(hits) > 1 else cls for mod, cls in hits]


#: the batches `report` names, kept for the dispatch guard (feature 385 T81, plan D100/D101), in the clone's git directory
BATCHES = "modal-batches.json"


def triage_first(u: ru.Unit, triaged: Mapping[str, str] | None = None) -> bool:
    """Owed only by a moved page and not yet marked touched by `make modal-triaged` at its fingerprint (feature 385 T93, D115:
    T31's six pop-ups the triage sent on kept naming `make modal-triage` and stayed out of their batch)."""
    return u.occasion.startswith("a page its ") and (triaged or {}).get(u.slug) != u.fingerprint


def modal_batches(rows: Sequence[ru.Unit], answered_slugs: Collection[str] = (), triaged: Mapping[str, str] | None = None) -> dict[str, list[str]]:
    """{pop-up agent: [kinds]} for each agent two or more unanswered pop-ups owe (feature 385 T81, plan D100; the GM's approved
    change 1: T10's checks sent 90 single-pop-up agents because this listing named one `KIND=` per unit). A pop-up owed only by a
    moved page goes to `make modal-triage` first and joins a batch once the triage marks it touched (`triaged`, T93)."""
    out: dict[str, list[str]] = {}
    for u in rows:
        if u.slug in answered_slugs or not u.check.startswith("modal-") or triage_first(u, triaged):
            continue
        agent = u.check if u.check in ("modal-form", "modal-depiction") else "modal-research"
        if u.subject not in out.setdefault(agent, []):
            out[agent].append(u.subject)
    return {a: ks for a, ks in out.items() if len(ks) >= 2}


def keep_batches(root: pathlib.Path, batches: Mapping[str, list[str]]) -> None:
    gd = pathlib.Path(_git(root, "rev-parse", "--path-format=absolute", "--git-common-dir").strip() or root / ".git")
    (gd / BATCHES).write_text(json.dumps({"utc": time.time(), "batches": dict(batches)}) + "\n", encoding="utf-8")


def report(rows: Sequence[ru.Unit], now: ru.Record | None = None, answered_slugs: Collection[str] = (), triaged: Mapping[str, str] | None = None) -> str:
    """The listing. With `answered_slugs` (the default listing), each unit already answered is marked so and the header says
    how many are still unanswered: T01 of feature 385 read the full listing as owed and went looking for three more quote-check
    batches after one had answered (plan D12)."""
    if not rows:
        return "record-owed: no record check is owed\n"
    left = [u for u in rows if u.slug not in answered_slugs]
    head = f"record-owed: {len(rows)} unit(s) owed" + (f" by the delta, {len(left)} still unanswered" if answered_slugs else "")
    lines = [head]
    for u in rows:
        if u.slug in answered_slugs:
            lines.append(f"  [answered] {u.slug}  - {u.occasion}")
        else:
            lines.append(f"  {u.slug}  - {u.occasion}\n      {command(u, now, triaged)}")
    for agent, kinds in modal_batches(rows, answered_slugs, triaged).items():  # T81: one agent for the pop-ups one check owes
        lines.append(f"  batched: make modal-bundle KIND=\"{' '.join(kinds)}\" FOR={agent}  - ONE {agent} agent for these {len(kinds)} pop-ups")
    lines.append("Answer each with `make record-checked CHECK=<check> BUNDLE=<its bundle> RESULT=\"<counts>\"` when its check returns.")
    lines.append("Apply a round's own EDITs with `make apply-edits FROM=<the agent's reply or its transcript>` - its unit then settles, owing no "
                 "round to re-read its own words - the same command settles an EDIT you already applied by hand, word for word (feature 385 T21).")
    return "\n".join(lines) + "\n"


def bypass_log(root: pathlib.Path, target: str, why: str) -> None:
    """A stated reason, written where `make audit` reads every escape (`dev/bypass-log/`, as `entry-gate.sh` writes it)."""
    import secrets  # noqa: PLC0415

    bl = root / "dev/bypass-log" / time.strftime("%Y-%m", time.gmtime())  # a month folder (2026-10-02)
    bl.mkdir(parents=True, exist_ok=True)
    head = _git(root, "rev-parse", "--short", "HEAD").strip()
    rec = {"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "target": target, "commit": head, "why": why}
    (bl / f"{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}-{secrets.token_hex(3)}.json").write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")


def bundle_less_refusal(check: str, notes: str, reason: str) -> str:
    """Why a record without a bundle is refused, or "" (plan D6): it records today's content, which no check may have read -
    so only `source-reader` on named notes (it reads before the note exists, so no bundle can carry it) or a stated reason."""
    import hm_escape as _hm_escape  # noqa: PLC0415

    if check == "source-reader" and notes:
        return ""
    if reason and _hm_escape.reason_is_enough(reason):
        return ""
    if reason:
        return "REASON needs two words and eight characters - it ships to dev/bypass-log/ for the audit"
    return (f"a {check} answer without BUNDLE= records today's content, which the check may never have read: pass the BUNDLE= "
            "it read, or REASON=\"<why>\" (written to dev/bypass-log/). A fix that applies a check's findings is owed its second round.")


def answer(root: pathlib.Path, check: str, result: str, bundle: str = "", q: str = "", notes: str = "", key: str = "", kind: str = "") -> list[str]:
    """Record the answer for every unit of `check` the bundle carried, or that the tree owes on the named subject - and close
    that check's dispatches on those subjects in the clone's check state (feature 375, FR-003: an answered check no longer
    freezes its page)."""
    done = _answer(root, check, result, bundle, q, notes, key, kind)
    if check in ("source-reader", "quote-check") and done:  # the reading is the tree's now - a bundle's MANIFEST carries no reading
        s, now = store(root), {u.slug: u.reading for u in units(root) if u.check == check}
        for slug in done:
            keep_reading(s, slug, now.get(slug, ""))
    if done:
        import hm_checks  # noqa: PLC0415

        hm_checks.record_answer(root, check, done)
    return done


def _answer(root: pathlib.Path, check: str, result: str, bundle: str = "", q: str = "", notes: str = "", key: str = "", kind: str = "") -> list[str]:
    s, done = store(root), []
    checks = _AGENT_CHECKS.get(check, (check,))  # CHECK=modal-research answers its three units (the round arbiter on hour:397@3)
    if bundle:
        manifest = pathlib.Path(bundle) / "MANIFEST.md"
        text = manifest.read_text(encoding="utf-8") if manifest.is_file() else ""
        pages = dict(re.findall(r"^page: (\S+) ([0-9a-f]{40})$", text, re.M))
        # the slug may hold a space - an entry-drift modal key such as "cart yard" - so the fingerprint is the LAST token
        for m in re.finditer(r"^unit: (.+) (\S+)$", text, re.M):
            if m.group(1).split(":", 1)[0] in checks:
                write_answer(s, m.group(1), m.group(2), result, pages)
                done.append(m.group(1))
        return done
    wanted = {k for k in notes.split(",") if k}
    for u in units(root):
        if u.check not in checks:
            continue
        subject_note = u.subject.partition("#")[2]
        if (q and ru.question(u.subject) == q.zfill(4) and (not wanted or subject_note in wanted)) or (key and u.subject == key) or (kind and u.subject in kind.split(",")):
            write_answer(s, u.slug, u.fingerprint, result)
            done.append(u.slug)
    return done


_OUTSIDE = re.compile(r"^#*\s*\**OUTSIDE THE CHANGE\**\s*:?\s*$", re.M)
_ROW = re.compile(r"^\s*-\s*`?([^|`]+?)`?\s*\|\s*(.+?)\s*\|\s*(.+?)\s*$")


def outside(reply: str) -> list[tuple[str, str, str]]:
    """(file, block, finding) of every line under a reply's `OUTSIDE THE CHANGE` heading (feature 375, FR-006)."""
    m = _OUTSIDE.search(reply)
    if m is None:
        return []
    rows = []
    for line in reply[m.end():].splitlines():
        if line.startswith("#"):
            break
        r = _ROW.match(line)
        if r:
            rows.append((r.group(1).strip(), r.group(2), r.group(3)))
    return rows


def file_outside(root: pathlib.Path, check: str, reply: str) -> list[dict]:
    """Append a reply's OUTSIDE THE CHANGE findings to the active feature's `found.jsonl` as open rows: filed, never an edit
    owed by this change (feature 375, FR-006). Fixing one stays possible as that row's own change."""
    rows = [{"check": check, "file": f, "block": b, "finding": x, "status": "open",
             "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())} for f, b, x in outside(reply)]
    if not rows:
        return []
    import hm_arbiter  # the one reader of the active feature: a page session's own first (reading feature.json here filed 343's rows under 378)

    target = (hm_arbiter.feature_dir(root) or root / "specs/_unfiled") / "found.jsonl"
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as fh:
        fh.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
    return rows


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--q", default="", help="only this question's units (its number)")
    ap.add_argument("--unanswered", action="store_true", help="only the units with no current answer record")
    ap.add_argument("--slugs", action="store_true", help="print the unit slugs alone, one a line")
    ap.add_argument("--skip-check", default="", help="leave out this check's units (the gate, when ENTRY_DRIFT_OK discharged them)")
    ap.add_argument("--between", nargs=2, metavar=("A", "B"), help="the units B owes against A (no entry-drift, no answers)")
    ap.add_argument("--answer", default="", metavar="CHECK", help="record that CHECK returned on the named units")
    ap.add_argument("--result", default="", help="with --answer: the check's verdict counts")
    ap.add_argument("--bundle", default="")
    ap.add_argument("--notes", default="")
    ap.add_argument("--key", default="")
    ap.add_argument("--kind", default="")
    ap.add_argument("--reason", default="", help="with --answer and no --bundle: why today's content may be recorded (bypass log)")
    ap.add_argument("--reply", default="", help="with --answer: the check's reply, whose OUTSIDE THE CHANGE findings are filed (feature 375)")
    args = ap.parse_args(argv)
    top = _git(pathlib.Path(args.root), "rev-parse", "--show-toplevel").strip()
    if not top:
        print(f"_record_owed: {args.root} is not a git repository", file=sys.stderr)
        return 1
    root = pathlib.Path(top)
    if args.answer:
        if not args.result:
            print("_record_owed: --answer needs --result \"<the check's counts>\"", file=sys.stderr)
            return 2
        refusal = "" if args.bundle else bundle_less_refusal(args.answer, args.notes, args.reason)
        if refusal:
            print(f"record-checked: REFUSED - {refusal}", file=sys.stderr)
            return 2
        done = answer(root, args.answer, args.result, args.bundle, args.q, args.notes, args.key, args.kind)
        if args.reply:
            import apply_edits  # noqa: PLC0415 - a transcript's last reply, as `make apply-edits` reads one (hour 32: an .output read raw filed nothing)

            for row in file_outside(root, args.answer, apply_edits.reply_of(pathlib.Path(args.reply))):
                print(f"record-checked: filed, not fixed - {row['file']} | {row['block']} | {row['finding']}")
        if done and not args.bundle and args.reason:
            bypass_log(root, "record-checked", f"{args.answer} on {' '.join(done)}: {args.reason}")
        if not done:
            print(f"_record_owed: no owed {args.answer} unit matched - nothing recorded (`make record-owed` lists what is owed)", file=sys.stderr)
            return 3
        print(f"record-checked: {len(done)} unit(s) answered - " + " ".join(done))
        return 0
    rows = units(root, *args.between) if args.between else (unanswered(root) if args.unanswered else units(root))
    if args.q:
        rows = [u for u in rows if ru.question(u.subject) == args.q.zfill(4)]
    if args.skip_check:
        rows = [u for u in rows if u.check != args.skip_check]
    if args.slugs:
        print("".join(u.slug + "\n" for u in rows), end="")
    else:
        done = set() if args.unanswered or args.between else {u.slug for u in rows} - {u.slug for u in unanswered(root)}
        import modal_triage  # noqa: PLC0415 - it imports this module

        named = modal_triage.touched(store(root))
        print(report(rows, read_at(root, args.between[1] if args.between else None), done, named), end="")
        if not args.between:
            keep_batches(root, modal_batches(rows, done, named))
    return 0


if __name__ == "__main__":
    sys.exit(main())
