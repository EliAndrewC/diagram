#!/usr/bin/env python3
"""Which record checks this delta owes, and which are still unanswered - the one scripted answer (feature 311).

WHY (GM 2026-10-02): *"I do worry about a future session making some extremely minor formatting tweak or something and then
having that literally rerun every subagent check for all 2,000 something of our resources just because like the tooling was
not preventing it or was too dumb to to flag what things actually needed to be rechecked"* - and an owed check skipped is the
other half of the same failure. So every record check is owed by what the delta touched (`_record_units.py` decides it from
the words), the push refuses an owed unit with no current answer (`scripts/entry-gate.sh`, the record gate), and a bundle or a
dispatch for a check nothing owes is refused (`_check_bundle.py`, `check-bundle-hooks.sh`).

THE UNITS. `_record_units.owed` for intro-check, record-format, source-reader, quote-check and source-applicability; the
translation pairs `_translation_owed.py` names (`translation-check:<page>#<note>`); the modals `_entry_owed.py` names
(`entry-drift:<modal key>`). Against the merge base with origin/main and the WORKING TREE (what the push will carry once
committed), or between two revisions (`--between A B`, the replay of spec SC-002; it omits entry-drift, which reads the engine).

THE ANSWER RECORD (plan D6). `--answer CHECK` writes, per unit, `<git common dir>/record-checks/<slug>.json` holding the unit's
fingerprint; the unit is answered while its fingerprint now equals the recorded one. From a bundle (`--bundle DIR`: the
fingerprints the bundle recorded when it was built, i.e. what the check read) or from the tree now (`--q`, `--notes`, `--key`,
`--kind`: `source-reader`, which reads before the note exists, and fixes that apply the check's own findings). In the clone
that pushes, as the review records are.

    _record_owed.py [--root DIR] [--q NNNN] [--unanswered] [--slugs]   the owed units, with the command that answers each
    _record_owed.py --between A B                                       a historical commit pair
    _record_owed.py --answer CHECK --result "<counts>" (--bundle DIR | --q NNNN [--notes k,k] | --key K | --kind K)
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
from collections.abc import Sequence

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
# no __pycache__ beside the scripts: the push runs this in fixture trees whose `git status` must stay clean
sys.dont_write_bytecode = True
import _record_units as ru  # noqa: E402

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
        names = _git(root, "diff", "--name-only", base, "--", ru.SOURCES).split() + _git(root, "ls-files", "--others", "--exclude-standard", "--", ru.SOURCES).split()
    else:
        names = _git(root, "diff", "--name-only", base, head, "--", ru.SOURCES).split()
    return {n.rsplit("/", 1)[1] for n in names}


def read_at(root: pathlib.Path, rev: str | None, sources: set[str] | None = None) -> ru.Record:
    """The record at `rev` (None: the working tree), read with ONE ls-tree and ONE cat-file batch (plan D2); of the source
    write-ups, only those named in `sources` (None: all)."""
    if rev is None:
        qdir, sdir = root / ru.QUESTIONS, root / ru.SOURCES
        files = {p.name: p.read_text(encoding="utf-8") for p in qdir.glob("*.html")} if qdir.is_dir() else {}
        src = {p.name: p.read_text(encoding="utf-8") for p in sdir.glob("*.html") if sources is None or p.name in sources} if sdir.is_dir() else {}
    else:
        names = _git(root, "ls-tree", "-r", "--name-only", rev, "--", ru.QUESTIONS, ru.SOURCES).split("\n")
        names = [n for n in names if n.endswith(".html") and (sources is None or not n.startswith(ru.SOURCES + "/") or n.rsplit("/", 1)[1] in sources)]
        blobs = _cat(root, [f"{rev}:{n}" for n in names])
        files = {n.rsplit("/", 1)[1]: b for n, b in zip(names, blobs, strict=True) if n.startswith(ru.QUESTIONS + "/")}
        src = {n.rsplit("/", 1)[1]: b for n, b in zip(names, blobs, strict=True) if n.startswith(ru.SOURCES + "/")}
    sources = {m.group(1): text for name, text in src.items() if (m := _SOURCE_FILE.match(name))}
    return ru.Record.of(files, sources)


def _cat(root: pathlib.Path, objects: list[str]) -> list[str]:
    """Each object's text, by one `git cat-file --batch` (a missing one is empty)."""
    if not objects:
        return []
    p = subprocess.run(["git", "-C", str(root), "cat-file", "--batch"], input=("\n".join(objects) + "\n").encode("utf-8"), capture_output=True, check=False)
    out, data, i = [], p.stdout, 0
    for _ in objects:
        nl = data.index(b"\n", i)
        head = data[i:nl].split()
        if len(head) < 3 or head[1] == b"missing":
            out.append("")
            i = nl + 1
            continue
        size = int(head[2])
        out.append(data[nl + 1 : nl + 1 + size].decode("utf-8"))
        i = nl + 1 + size + 1
    return out


def _translation_units(root: pathlib.Path, now: ru.Record) -> list[ru.Unit]:
    import _translation_owed as to  # noqa: PLC0415

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
    import _entry_owed as eo  # noqa: PLC0415
    import _modal_owed as mo  # noqa: PLC0415

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


def _modal_units(root: pathlib.Path, base: str) -> list[ru.Unit]:
    """The About-form modals' units (feature 319, plan D6): `modal-form`, and the three `modal-research` answers."""
    import _modal_owed as mo  # noqa: PLC0415

    return [ru.Unit(slug, why, fp) for slug, why, fp in mo.owed(root, base)]


def units(root: pathlib.Path, base: str | None = None, head: str | None = None) -> list[ru.Unit]:
    """Every owed unit, against the merge base and the working tree, or between two revisions."""
    base = base or merge_base(root)
    touched = changed_sources(root, base, head) if base else None
    now = read_at(root, head, touched)
    out = ru.owed(now, read_at(root, base, touched) if base else ru.Record({}, {}, {}, {}))
    if head is None:
        out += _translation_units(root, now) + _entry_units(root, now) + _modal_units(root, base)
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


def write_answer(store_dir: pathlib.Path, slug: str, fp: str, result: str) -> None:
    """Record an answer. Every fingerprint ever answered is kept: an answer is about WORDS, so content reverted to words a
    check already passed stays answered (an edit answered and then undone owed its unit again when only the last was kept)."""
    store_dir.mkdir(parents=True, exist_ok=True)
    seen = [f for f in _read(store_dir, slug).get("answered", []) if f != fp] + [fp]
    rec = {"unit": slug, "fingerprint": fp, "answered": seen, "result": result, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    _file(store_dir, slug).write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")


def answered(store_dir: pathlib.Path, slug: str, fp: str) -> bool:
    rec = _read(store_dir, slug)
    return fp == rec.get("fingerprint") or fp in rec.get("answered", [])


def unanswered(root: pathlib.Path) -> list[ru.Unit]:
    s = store(root)
    return [u for u in units(root) if not answered(s, u.slug, u.fingerprint)]


def command(u: ru.Unit, now: ru.Record | None = None) -> str:
    """What builds the bundle for a unit - named in every report and refusal, so a session never has to work it out."""
    q, check = ru.question(u.subject), u.check
    if check == "source-applicability":
        return f"make check-bundle KEY={u.subject}"
    if check == "source-reader":
        stem, _, note = u.subject.partition("#")
        keys = list(now.cites.get(stem, {}).get(note, ())) if now else []
        keys = keys or ["<the note's key>"]
        return " ; ".join(f"make check-bundle KEY={k} WHOLE=1" for k in dict.fromkeys(keys)) + f"  then  make record-checked CHECK=source-reader Q={q} NOTES={note}"
    if check.startswith("modal-"):  # feature 319: a modal's units; the three research units are one modal-research dispatch
        agent = "modal-form" if check == "modal-form" else "modal-research"
        return f"make modal-bundle KIND=\"{u.subject}\" FOR={agent}  then  make record-checked CHECK={check} BUNDLE=<its bundle> RESULT=..."
    if check == "entry-drift":  # its subject is the modal's key, not a question: the section it moved under is named in the occasion
        sec = re.search(r"\((\d{4})-", u.occasion)
        return f"make check-bundle Q={sec.group(1) if sec else '<its section>'} FOR=entry-drift KIND=<the class of {u.subject}>  then  make record-checked CHECK=entry-drift KIND=\"{u.subject}\" RESULT=..."
    return f"make check-bundle Q={q} FOR={check}"


def report(rows: Sequence[ru.Unit], now: ru.Record | None = None) -> str:
    if not rows:
        return "record-owed: no record check is owed\n"
    lines = [f"record-owed: {len(rows)} unit(s) owed"]
    for u in rows:
        lines.append(f"  {u.slug}  - {u.occasion}\n      {command(u, now)}")
    lines.append("Answer each with `make record-checked CHECK=<check> BUNDLE=<its bundle> RESULT=\"<counts>\"` when its check returns.")
    return "\n".join(lines) + "\n"


def bypass_log(root: pathlib.Path, target: str, why: str) -> None:
    """A stated reason, written where `make audit` reads every escape (`dev/bypass-log/`, as `entry-gate.sh` writes it)."""
    import secrets  # noqa: PLC0415

    bl = root / ".claude/skills/diagram/dev/bypass-log" / time.strftime("%Y-%m", time.gmtime())  # a month folder (2026-10-02)
    bl.mkdir(parents=True, exist_ok=True)
    head = _git(root, "rev-parse", "--short", "HEAD").strip()
    rec = {"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "target": target, "commit": head, "why": why}
    (bl / f"{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}-{secrets.token_hex(3)}.json").write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")


def bundle_less_refusal(check: str, notes: str, reason: str) -> str:
    """Why a record without a bundle is refused, or "" (plan D6): it records today's content, which no check may have read -
    so only `source-reader` on named notes (it reads before the note exists, so no bundle can carry it) or a stated reason."""
    import _hm_escape  # noqa: PLC0415

    if check == "source-reader" and notes:
        return ""
    if reason and _hm_escape.reason_is_enough(reason):
        return ""
    if reason:
        return "REASON needs two words and eight characters - it ships to dev/bypass-log/ for the audit"
    return (f"a {check} answer without BUNDLE= records today's content, which the check may never have read: pass the BUNDLE= "
            "it read, or REASON=\"<why>\" (written to dev/bypass-log/). A fix that applies a check's findings is owed its second round.")


def answer(root: pathlib.Path, check: str, result: str, bundle: str = "", q: str = "", notes: str = "", key: str = "", kind: str = "") -> list[str]:
    """Record the answer for every unit of `check` the bundle carried, or that the tree owes on the named subject."""
    s, done = store(root), []
    if bundle:
        manifest = pathlib.Path(bundle) / "MANIFEST.md"
        # the slug may hold a space - an entry-drift modal key such as "cart yard" - so the fingerprint is the LAST token
        for m in re.finditer(r"^unit: (.+) (\S+)$", manifest.read_text(encoding="utf-8") if manifest.is_file() else "", re.M):
            if m.group(1).split(":", 1)[0] == check:
                write_answer(s, m.group(1), m.group(2), result)
                done.append(m.group(1))
        return done
    wanted = {k for k in notes.split(",") if k}
    for u in units(root):
        if u.check != check:
            continue
        subject_note = u.subject.partition("#")[2]
        if (q and ru.question(u.subject) == q.zfill(4) and (not wanted or subject_note in wanted)) or (key and u.subject == key) or (kind and u.subject == kind):
            write_answer(s, u.slug, u.fingerprint, result)
            done.append(u.slug)
    return done


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
        print(report(rows, read_at(root, args.between[1] if args.between else None)), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
