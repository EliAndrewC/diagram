#!/usr/bin/env python3
"""Apply the ready-made edits a check agent's report ends its findings with (feature 250 D15, research R6).

WHY. On the last three measured pages the largest single cost was the APPLY step of a check session: 12 to 27
turns a group, each re-reading a context of 60,000 to 90,000 tokens, most of them spent reading a file so that
`Edit` would accept it and then typing the replacement the report had already worded (R6). `quote-check` and
`record-format` now end every finding they can word with an EDIT block, and this applies a whole report in one
command; the session's turns go to the findings that need judgment.

THE BLOCKS, as the two contracts write them:

    EDIT <origin path>
    <<<
    the exact text now in the file
    ===
    the text that replaces it
    >>>

    GLOSSARY <term> | <variant>, <variant> | <definition>

A block is applied only when its old text occurs EXACTLY ONCE in its file - never a guess at which occurrence was
meant - and only under the record (`research/`) or a modal's class file (`interactive/classes/`, D17); anything else is REFUSED with the reason, and the session applies
it by hand. A glossary term already on file is skipped. `--skip 2,5` leaves those blocks alone (the session
disagrees with them); `--dry-run` reports without writing. The input is the agent's reply saved as text, or its
transcript (`.jsonl`, or the `.output` link the dispatch names), whose last reply is read.

THE ROUND SETTLES (feature 335's round arbiter, 2026-10-11, rulings `round:record-format|q:0104@3` and
`ask:f335-garden-modal-depiction`). Applying a round's own blocks used to re-owe the unit it answered - its words had moved -
so the next round read the check's own words back, found nothing new, and the round cap fired on a loop the tooling made. Now
the owed units of the reply's check (its counts line names it) are fingerprinted before and after the blocks go in, and a
unit whose content moved by them alone settles with its round's answer (`record_owed.settle`: at once when the answer is
recorded at the content before them, else when `make record-checked` records it). A record-format unit whose prepass now
raises a word the round never ruled on stays owed, and so does any unit changed in any other way.

AND THE CHECKS BEFORE IT (feature 375 amendment 3, FR-019). A pop-up's checks run in order - form, research, depiction
(`modal_owed.ORDER`) - and a round's blocks also settle each check BEFORE the replying one in that order, where its answer
already stands at the words before them: research's fixes do not owe form again, depiction's owe neither. Never pending for
those: an answer recorded later would answer words that check never read. A check after the replying one reads the edited
words next, so nothing of it settles.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

# A block may sit indented under a numbered finding, every line of it carrying the same indent; the indent is
# the list's, not the file's, and is taken off each line of the old and new text. record-format wrote its first
# cities/fabric 140 report that way and the unindented pattern found no block in it at all (feature 250 T55).
EDIT = re.compile(
    r"^(?P<ind>[ \t]*)EDIT[ \t]+`?(?P<path>[^\n`]+?)`?[ \t]*\n(?P=ind)<<<\n(?P<old>.*?)\n(?P=ind)===\n(?:(?P<new>.*?)\n)??(?P=ind)>>>[ \t]*$",
    re.S | re.M,
)
GLOSSARY = re.compile(r"^[ \t]*GLOSSARY[ \t]+(?P<term>[^|\n]+?)[ \t]*\|[ \t]*(?P<variants>[^|\n]*?)[ \t]*\|[ \t]*(?P<def>[^\n]+?)[ \t]*$", re.M)
RECORD = "research/"
# D17 (R8, recommendation 1): a drifted modal's prose is its Kind class's docstring - thirteen hand edits on `fields`
MODALS = "l7r/diagram/interactive/classes/"
# feature 262's building-plan sheets keep their modal prose in compound_kinds/, which entry-drift checks the same way
# (feature 265: 58 owed pairs there, and every EDIT for them was refused until this)
SHEET_MODALS = "l7r/diagram/interactive/compound_kinds/"
# feature 319 (plan D12): a modal's text is its own file now, one per kind - the EDIT target every modal check names
MODAL_FILES = "l7r/diagram/interactive/assets/modals/"
ROOTS = (RECORD, MODALS, SHEET_MODALS, MODAL_FILES)
TERMS = "l7r/diagram/interactive/assets/glossary/"


def unescaped(text: str) -> str:
    """A report saved inside a task notification has its markup escaped - `&lt;&lt;&lt;` for `<<<` - and every block in it
    read as no block at all (feature 319: a session's returned-reports file). Unescaped only when its markers are, so a
    report that quotes `&amp;` from a record file keeps it."""
    if "&lt;&lt;&lt;" in text and "\n<<<" not in text:
        import html  # noqa: PLC0415

        return html.unescape(text)
    return text


def reply_of(path: pathlib.Path) -> str:
    """The report's text: the file itself, or the last assistant reply in a transcript."""
    text = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix not in (".jsonl", ".output"):
        return unescaped(text)
    last = ""
    for line in text.splitlines():
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        msg = rec.get("message") or {}
        if rec.get("type") == "assistant" and isinstance(msg.get("content"), list):
            said = "".join(c.get("text", "") for c in msg["content"] if c.get("type") == "text")
            last = said or last
    return last


def dedent(text: str, indent: str) -> str:
    """The block's text without the indent of the list it sat in."""
    return "\n".join(line.removeprefix(indent) for line in text.split("\n")) if indent else text


def blocks(report: str) -> list[dict]:
    """Every EDIT and GLOSSARY block, in the report's order, numbered from 1."""
    # A LONE EMPTY LINE IS A PARAGRAPH BREAK, NO LINE IS A DELETION (feature 385 T60, the round arbiter on
    # hour:385-approach-checklist@22): `===` then `>>>` deletes; `===`, one empty line, `>>>` breaks. Both used to parse as no text,
    # so a split paragraph was deleted instead, and T10's check session finished two pop-ups by hand.
    found = [
        (m.start(), {"kind": "edit", "path": m["path"].strip(), "old": dedent(m["old"], m["ind"]), "new": dedent(m["new"] or "", m["ind"]), "brk": m["new"] == ""})
        for m in EDIT.finditer(report)
    ]
    found += [
        (m.start(), {"kind": "glossary", "term": m["term"].strip(), "variants": [v.strip() for v in m["variants"].split(",") if v.strip() not in ("", "-")], "def": m["def"].strip()})
        for m in GLOSSARY.finditer(report)
    ]
    return [{"n": n, **b} for n, (_, b) in enumerate(sorted(found, key=lambda f: f[0]), 1)]


def resolve(root: pathlib.Path, path: str) -> pathlib.Path | None:
    """The origin file, if it lies under the record; a path elsewhere is not this script's to write."""
    p = pathlib.Path(path)
    p = (p if p.is_absolute() else root / p).resolve()
    return p if any(p.is_relative_to(root / r) for r in ROOTS) else None


def held_dropped(root: pathlib.Path, b: dict) -> str:
    """For a modal-form reply's EDIT on a pop-up: the research-fixed wording (`modal_bundle.research_held`) its old text holds
    and its new text drops, else ''. A form round only rewords; the facts are research's (343's border-court ruling)."""
    m = re.search(r"modals/(\w+)/([^/]+)\.md$", b["path"])
    target = resolve(root, b["path"])
    if not m or target is None or not target.is_file():
        return ""
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import modal_bundle  # noqa: PLC0415

    held = modal_bundle.research_held(root, f"{m.group(1)}/{m.group(2)}", target.read_text(encoding="utf-8"))
    return next((h for h in held if h in b["old"] and h not in b["new"]), "")


def apply_edit(root: pathlib.Path, b: dict, dry: bool, form: bool = False) -> str:
    if form and (h := held_dropped(root, b)):
        return f"REFUSED - a modal-form EDIT drops wording a research round fixed ({h[:80]!r}); reword around it, or put the fact to modal-research"
    target = resolve(root, b["path"])
    if target is None:
        return f"REFUSED - {b['path']} is not under {RECORD}, {MODAL_FILES}, {MODALS} or {SHEET_MODALS}"
    if not target.is_file():
        return f"REFUSED - no file {b['path']}"
    text = target.read_text(encoding="utf-8")
    count = text.count(b["old"])
    # ALREADY APPLIED: a block whose new text holds its old text still finds the old text once it is in, so a second run
    # applied it again (feature 374 wave 154: a re-run doubled a pop-up's `Entry:` path). Its new text standing where the
    # old text stands is the block applied: skipped, never written twice.
    if b["old"] and b["old"] in b["new"] and b["new"] in text and text.count(b["new"]) >= count:
        return f"already applied to {target.name}"
    if count != 1:
        return f"REFUSED - the old text occurs {count} times in {target.name}, not once"
    if not dry:
        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "hooks" / "lib"))
        from hm_house import americanize  # noqa: PLC0415 - feature 385 T78: an agent's new text in the house style

        target.write_text(replaced(text, {**b, "new": americanize(b["new"])}), encoding="utf-8")
    return f"applied to {target.name}"


def replaced(text: str, b: dict) -> str:
    """The file with the block's one occurrence replaced (T60): a break is a blank line where the old text was whole lines,
    two newlines inside a line; an empty replacement of whole lines takes their newline with them, leaving no blank line."""
    i = text.index(b["old"])
    j = i + len(b["old"])
    whole = (i == 0 or text[i - 1] == "\n") and (j == len(text) or text[j] == "\n")
    if b.get("brk"):
        new = "" if whole else "\n\n"
    elif not b["new"] and whole:
        new = ""
        j += j < len(text)  # the emptied line's own newline
    else:
        new = b["new"]
    return text[:i] + new + text[j:]


def slug(term: str) -> str:
    """The glossary's own filename rule, restated exactly (`glossary_source._encode`): the term as it is,
    case and spaces kept, with only `%` and `/` percent-encoded. A hyphenated lowercase slug wrote
    `7960-trunk-street.json` for `trunk street`, and `make glossary` refused it (feature 250)."""
    return term.replace("%", "%25").replace("/", "%2F")


def apply_term(root: pathlib.Path, b: dict, dry: bool) -> str:
    d = root / TERMS
    have = {json.loads(f.read_text(encoding="utf-8")).get("term", "").lower() for f in d.glob("*.json")}
    if b["term"].lower() in have:
        return f"skipped - '{b['term']}' is already a glossary term"
    # the term is always its own first variant: matching reads only `variants`, and a term given only its
    # plural (kidoban -> "kidobans", cities/fabric 2b) never matched the bare word and failed the record test
    entry = {"term": b["term"], "def": b["def"], "variants": [b["term"], *(v for v in b["variants"] if v != b["term"])]}
    if dry:
        return f"would add a file for {b['term']!r}"
    # the prefix is RESERVED under the host-wide lock (feature 265 FR-010): two queues adding terms at once never
    # take the same one; the reservation writes the file, here with its full text as the stub
    # a key another clone is already defining is REFUSED like an edit, never a traceback: the traceback stopped the
    # run mid-report and left the blocks after it unapplied (271 T3 check-b, `Kinki` held by 267)
    reserve = _reserve()
    try:
        path = reserve.reserve("glossary", b["term"], root, stub=json.dumps(entry, ensure_ascii=False, indent=1) + "\n")
    except reserve.Refusal as e:
        return f"REFUSED - {e}"
    return f"added {path.name}"


def _reserve():  # noqa: ANN202
    import importlib.util  # noqa: PLC0415

    spec = importlib.util.spec_from_file_location("reserve_prefix", pathlib.Path(__file__).resolve().parent / "reserve-prefix.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _sibling(name: str):  # noqa: ANN202
    """A record script beside this one, imported flat (`record_owed`, `record_prepass`)."""
    import importlib  # noqa: PLC0415

    here = str(pathlib.Path(__file__).resolve().parent)
    if here not in sys.path:
        sys.path.insert(0, here)
    return importlib.import_module(name)


_QUESTION = re.compile(r"(?:^|/)research/questions/(\d{4})-[^/]*\.html$")


def touched_questions(found: list[dict]) -> set[str]:
    """The question numbers whose files the report's EDIT blocks name."""
    return {m.group(1) for b in found if b["kind"] == "edit" and (m := _QUESTION.search(b["path"]))}


def prepass_words(root: pathlib.Path, q: str) -> set[str]:
    """Every word `make record-prepass` hands record-format to rule on for question `q` (its candidate lines and its rare
    words), over the question's pages as they stand now. The prepass memoizes the corpus; it is cleared so that words the
    edit just wrote are counted."""
    rp = _sibling("record_prepass")
    for f in vars(rp).values():
        if callable(getattr(f, "cache_clear", None)):
            f.cache_clear()
    qdir = root / RECORD / "questions"
    pages = [p for p in sorted(qdir.glob(f"{q}-*.html")) if not p.name.endswith((".notes.html", ".originals.html"))]
    gloss = root / rp.GLOSSARY
    glossary = json.loads(gloss.read_text(encoding="utf-8")) if gloss.is_file() else {}
    listing = rp.prepass("\n".join(p.read_text(encoding="utf-8") for p in pages), glossary, str(root / rp.RESEARCH))
    return {i["match"] for s in listing for i in s["items"]} | {w for s in listing for w, _n in s["rare"]}


def is_repo(root: pathlib.Path) -> bool:
    """`root` is a clone's top level - where the record checks' units and answers are (a bare record tree has none)."""
    import subprocess  # noqa: PLC0415

    p = subprocess.run(["git", "-C", str(root), "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False)
    return p.returncode == 0 and pathlib.Path(p.stdout.strip()).resolve() == root.resolve()


class Round:
    """What `settle` needs from BEFORE the blocks are applied: the owed fingerprints of the reply's own checks, and for a
    record-format reply the prepass words of each question it edits (feature 335's round arbiter, 2026-10-11)."""

    def __init__(self, root: pathlib.Path, report: str, found: list[dict]) -> None:
        self.root, self.ro = root, _sibling("record_owed")
        self.checks = self.ro.reply_checks(report)
        # feature 375 amendment 3 (FR-019b): a pop-up check's blocks also settle the checks BEFORE it in the order
        self.earlier = _sibling("modal_owed").earlier_units(self.checks) if self.checks else ()
        self.before = self.ro.fingerprints(root, (*self.checks, *self.earlier)) if self.checks else {}
        rf = "record-format" in self.checks
        self.words = {q: prepass_words(root, q) for q in touched_questions(found)} if rf else {}
        # feature 399 (the GM 2026-10-19): ANOTHER check's blocks settle a quote-check note they moved only outside its
        # quotation and its claim - kind C. Read before the blocks: each note's words, quotation key, and whether it was owed
        self.quotes = self.quote_notes(touched_questions(found)) if self.checks and "quote-check" not in self.checks else {}
        self.quote_owed = set(self.ro.fingerprints(root, ("quote-check",))) if self.quotes else set()

    def quote_notes(self, questions: set[str]) -> dict[str, tuple[str, str]]:
        """{quote-check slug: (fingerprint, quotation key)} of every note of `questions`, in the working tree now."""
        ru = self.ro.ru
        rec = self.ro.read_at(self.root, None, set())
        slugs = [f"quote-check:{stem}#{k}" for stem, notes in rec.notes.items() if ru.question(stem) in questions for k in notes]
        return {s: (ru.fingerprint(rec, s), ru.quotation_key(rec, s)) for s in slugs}

    def settle_quotes(self) -> list[str]:
        """Each quote-check note this run's blocks moved: settled where its quotation and claim stand as before and its answer
        stood at the words before (or it was not owed then, its words main's); else said to be owed, with why."""
        out, store = [], self.ro.store(self.root)
        after = self.quote_notes({self.ro.ru.question(s.split(":", 1)[1]) for s in self.quotes})
        why = f"{self.ro.FIXED}: the {'/'.join(self.checks)} round's EDIT blocks"
        for slug, (fp, key) in sorted(self.quotes.items()):
            fp2, key2 = after.get(slug, ("", ""))
            if not fp2 or fp2 == fp:
                continue
            if key2 != key:
                out.append(f"  {slug}: still owed - its quotation or its claim changed")
            elif slug in self.quote_owed and not self.ro.answered(store, slug, fp):
                out.append(f"  {slug}: still owed - not answered at the words before these blocks")
            else:
                was = self.ro._read(store, slug)
                self.ro.write_answer(store, slug, fp2, f"{why}; was: {was.get('result', 'unchanged since main')}", was.get("pages"))
                self.ro.keep_reading(store, slug, key2, "qkeys")
                out.append(f"  {slug}: settled - another check's fix, outside its quotation and its claim")
        return out

    def settle(self) -> list[str]:
        """Each owed unit of the reply's checks whose content moved by this run's blocks alone: answered where the round's
        answer already stands at the content before them, pending where it is not recorded yet; a record-format unit whose
        prepass now raises a word the round never ruled on stays owed. Any unit changed some other way stays owed."""
        out = []
        after = self.ro.fingerprints(self.root, (*self.checks, *self.earlier)) if self.checks else {}
        store = self.ro.store(self.root)
        for slug, fp in sorted(after.items()):
            before = self.before.get(slug, "")
            if not before or before == fp:
                continue
            if slug.split(":", 1)[0] in self.earlier:
                # an EARLIER check settles only where its answer already stands at the words before these blocks - never
                # pending: an answer recorded later would answer words that check never read (plan D26)
                if self.ro.answered(store, slug, before):
                    self.ro.settle(store, slug, before, fp)
                    out.append(f"  {slug}: settled with its answer - the {'/'.join(self.checks)} round's blocks alone moved it (it runs before them)")
                else:
                    out.append(f"  {slug}: still owed - not answered at the words before these blocks")
                continue
            q = slug.split(":", 1)[1]
            if slug.startswith("record-format:") and q in self.words and (new := sorted(prepass_words(self.root, q) - self.words[q])):
                out.append(f"  {slug}: still owed - its prepass now raises {', '.join(new[:8])}, which the round never ruled on")
                continue
            said = self.ro.settle(store, slug, before, fp)
            out.append(f"  {slug}: {'settled with its answered round' if said == 'answered' else 'settles when `make record-checked` records this round'}")
        return out + (self.settle_quotes() if self.quotes else [])


def settle_round(root: pathlib.Path, report: str, found: list[dict], apply) -> int:  # noqa: ANN001
    """Run `apply` (the blocks, written) inside the settling: fingerprints before, then after (feature 335's round arbiter).
    The settling never stops the edits: a failure is reported, and the round is answered as before."""
    rnd = None
    if is_repo(root):
        try:
            rnd = Round(root, report, found)
        except Exception as e:  # noqa: BLE001 - the edits go in regardless; the unit stays owed, as it did before this
            print(f"apply-edits: could not read the round's units ({type(e).__name__}: {e}) - its units stay owed")
    applied = apply()
    if rnd is not None and rnd.checks and applied:
        try:
            lines = rnd.settle()
        except Exception as e:  # noqa: BLE001
            lines = [f"  could not settle ({type(e).__name__}: {e}) - its units stay owed"]
        if lines:
            print(f"apply-edits: the {'/'.join(rnd.checks)} round's own EDITs, applied verbatim:")
            print("\n".join(lines))
    elif rnd is not None and applied:
        # feature 385 T10: a reply saved without its counts line applied every block and settled nothing, without a word -
        # three pop-ups stayed owed a form round they had passed
        print(
            "apply-edits: the reply names no check, so the units it answered stay owed - put the agent's counts line "
            "(`modal-form: <name> - 2 findings`, `quote-check: ...`) at the top of the reply file and run this again; "
            "the blocks already in are settled, not applied twice"
        )
    return applied


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("report", help="the agent's reply saved as text, or its transcript (.jsonl / .output)")
    ap.add_argument("--root", default=".", help="the clone root")
    ap.add_argument("--skip", default="", help="block numbers to leave alone, e.g. 2,5")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    root = pathlib.Path(args.root).resolve()
    report = reply_of(pathlib.Path(args.report))
    found = blocks(report)
    form = next((ln.strip() for ln in report.splitlines() if ln.strip()), "").startswith("modal-form:")  # its counts line
    if not found:
        print("apply-edits: the report carries no EDIT or GLOSSARY block - apply its findings by hand", file=sys.stderr)
        return 2
    skip = {int(s) for s in args.skip.split(",") if s.strip()}
    refused = terms = 0

    def apply() -> int:
        nonlocal refused, terms
        edited = 0
        for b in found:
            if b["n"] in skip:
                print(f"  {b['n']}. skipped (--skip)")
                continue
            said = apply_edit(root, b, args.dry_run, form) if b["kind"] == "edit" else apply_term(root, b, args.dry_run)
            refused += said.startswith("REFUSED")
            terms += said.startswith("added")
            edited += said.startswith("applied")
            print(f"  {b['n']}. {said}   ({b.get('path') or 'GLOSSARY ' + b['term']})")
        return edited

    # AN EDIT ALREADY APPLIED BY HAND SETTLES TOO (feature 385 T21; the round arbiter's fix on ask:t05-lane-popup-round3 and
    # its plan review: the test is the diff matching the EDIT line for line, not how it got there). A block whose new text
    # stands once in its file and whose old text is gone is put back to its old text here, so the settling below sees the
    # round's own blocks move the unit, and re-applies it: the file ends as it was, the unit settles as if applied here.
    if not args.dry_run:
        for b in found:
            if b["kind"] != "edit" or b["n"] in skip or not b["old"] or b["old"] in b["new"]:
                continue
            target = resolve(root, b["path"])
            text = target.read_text(encoding="utf-8") if target is not None and target.is_file() else ""
            if text and text.count(b["old"]) == 0 and text.count(b["new"]) == 1:
                target.write_text(text.replace(b["new"], b["old"], 1), encoding="utf-8")
                print(f"  {b['n']}. found applied by hand - settled through its reply   ({b['path']})")
    # a dry run writes nothing, so it settles nothing; a reply with no EDIT block changes no unit's words
    if args.dry_run or not any(b["kind"] == "edit" for b in found):
        apply()
    else:
        settle_round(root, report, found, apply)
    tail = " - then `make glossary`" if terms else ""
    print(f"apply-edits: {len(found)} block(s), {refused} refused{' (dry run, nothing written)' if args.dry_run else ''}{tail}")
    return 1 if refused else 0


if __name__ == "__main__":
    sys.exit(main())
