#!/usr/bin/env python3
"""No bundle for a check nothing owes, and the `intro-check` bundle - `check_bundle.py`'s owed half (feature 311, plan D4, D9).

WHY (GM 2026-10-02): *"I do worry about a future session making some extremely minor formatting tweak or something and then
having that literally rerun every subagent check for all 2,000 something of our resources"*. A check costs its tokens when it
is DISPATCHED, and it is dispatched on a bundle; so the bundle is where "is this owed?" is asked. A bundle for a check and a
subject the delta does not owe (`record_owed.py`) is refused with the owed list. The escapes, each a reason of two words or
more recorded in the MANIFEST: `NOT_OWED_OK` (a backfill, an audit the GM asked for, a source's numbers about to reach a map
or a rule) and, for a source-reader's whole-page read, `NEW` - a read for a claim not yet in the record, which nothing can owe
yet because the note it will support does not exist.

Every question or source bundle's MANIFEST carries `owed-checks:` (what `check-bundle-hooks.sh` lets be dispatched on it) and
one `unit: <slug> <fingerprint>` line per unit it carries, at the content copied (what `make record-checked BUNDLE=` records).
"""

from __future__ import annotations

import functools
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path[1:1] = [str((pathlib.Path(__file__).resolve().parent / _d).resolve()) for _d in ('../hooks/lib',)]  # the moved scripts it imports (2026-10-08)
import record_owed as ro  # noqa: E402
import record_units as ru  # noqa: E402

#: the checks a question bundle is owed for; `record-style` is owed by a declared sweep (feature 292), never by a delta
GATED = ("intro-check", "record-format", "quote-check", "translation-check", "entry-drift")
MODAL_DIRS = ("l7r/diagram/interactive/classes", "l7r/diagram/interactive/compound_kinds")


def reason_ok(text: str) -> bool:
    import hm_escape as _hm_escape  # noqa: PLC0415

    return _hm_escape.reason_is_enough(text)


def question_of(q: str) -> str:
    m = re.match(r"(\d{1,4})", q)
    return m.group(1).zfill(4) if m else q


def owed_for_question(root: pathlib.Path, q: str, for_: str, not_owed_ok: str, every: list[ru.Unit] | None = None) -> tuple[list[ru.Unit], str, str]:
    """(the units the bundle carries, the `owed-checks:` value, a refusal or ""), for `make check-bundle Q= FOR=`; `every`
    is the delta's units when the caller already has them (a batch asks once, not once per question)."""
    if for_ == "record-style":
        return [], "record-style", ""
    qn = question_of(q)
    every = ro.units(root) if every is None else every
    units = [u for u in every if ru.question(u.subject) == qn or (u.check == "entry-drift" and for_ in ("entry-drift", "all"))]
    if q.endswith(".html"):  # ONE page (feature 303): its units only - feature 319 recorded a research page's bundle as
        drawing = ".drawing." in q  # answering the drawing page's units, which that bundle never carried
        units = [u for u in units if "#" not in u.subject or (".drawing" in u.subject.partition("#")[0]) == drawing]
    if for_ != "all":
        units = [u for u in units if u.check == for_]
    if units:
        return units, " ".join(dict.fromkeys(u.check for u in units)), ""
    if not_owed_ok:
        if not reason_ok(not_owed_ok):
            return [], "", "NOT_OWED_OK needs a REASON - two words and eight characters - so the audit says why"
        checks = GATED[:-1] if for_ == "all" else (for_,)
        return tree_units(root, qn, checks), " ".join(checks), ""
    listing = "\n".join(f"    {u.slug}" for u in every) or "    (nothing: no record check is owed by this delta)"
    return [], "", (
        f"no {for_ if for_ != 'all' else 'record'} check is owed on question {qn} by this delta - a bundle for it would "
        f"re-run a check on words it already passed. What IS owed:\n{listing}\n"
        "A check the GM asked for, or a backfill: NOT_OWED_OK=\"<why>\" on the same command."
    )


def tree_units(root: pathlib.Path, q: str, checks: tuple[str, ...]) -> list[ru.Unit]:
    """The units a NOT_OWED_OK bundle carries: every unit of those checks on the question, at today's content."""
    rec = ro.read_at(root, None, set())
    slugs = []
    for check in checks:
        if check in ("intro-check", "record-format"):
            slugs.append(f"{check}:{q}")
        elif check == "quote-check":
            for stem in (q, f"{q}.drawing"):
                slugs += [f"quote-check:{stem}#{k}" for k in rec.notes.get(stem, {})] + [f"quote-check:{stem}#unfootnoted"]
    return [ru.Unit(s, "not owed - a stated reason", ru.fingerprint(rec, s)) for s in slugs]


def owed_for_key(root: pathlib.Path, key: str, whole: bool, not_owed_ok: str, new: str) -> tuple[list[ru.Unit], str, str]:
    """(units, owed-checks, refusal) for `make check-bundle KEY= [WHOLE=1]`: the write-up check is owed when the write-up's
    words changed; a source-reader's whole read when a note citing the key changed, or when declared for a NEW claim."""
    every = ro.units(root)
    if whole:
        now = ro.read_at(root, None, set())
        units = [u for u in every if u.check == "source-reader" and key in now.cites.get(u.subject.partition("#")[0], {}).get(u.subject.partition("#")[2], ())]
        check = "source-reader"
    else:
        units = [u for u in every if u.check == "source-applicability" and u.subject == key]
        check = "source-applicability"
    if units:
        return units, check, ""
    for name, value in (("NEW", new if whole else ""), ("NOT_OWED_OK", not_owed_ok)):
        if value:
            return ([], check, "") if reason_ok(value) else ([], "", f"{name} needs a REASON - two words and eight characters - so the audit says why")
    hint = 'NEW="<the claim, in a few words>" for a read before its note is written; ' if whole else ""
    return [], "", (
        f"no {check} is owed on `{key}` by this delta - its {'notes' if whole else 'write-up'} did not change. "
        f"{hint}NOT_OWED_OK=\"<why>\" for anything else (a source's numbers about to reach a map or a rule)."
    )


def manifest_lines(units: list[ru.Unit], owed_checks: str, escape: str = "") -> str:
    """The lines the dispatch hook and `make record-checked` read from a MANIFEST."""
    lines = ["## Owed (feature 311)", "", f"owed-checks: {owed_checks}"]
    if escape:
        lines.append(f"not-owed: {escape}")
    lines += [f"unit: {u.slug} {u.fingerprint}" for u in units]
    return "\n".join(lines) + "\n"


def batch_units(units: list[ru.Unit], batch: frozenset[str]) -> list[ru.Unit]:
    """The owed units ONE quote-check batch can answer: its own notes', and the unfootnoted reading every batch carries.
    Feature 317: each batch carried every owed unit, so the batch holding none of the changed notes answered them all."""
    return [u for u in units if u.subject.partition("#")[2] in batch or u.subject.partition("#")[2] == "unfootnoted"]


def kind_units(units: list[ru.Unit], key: str) -> list[ru.Unit]:
    """The owed units ONE modal's entry-drift bundle can answer: that modal's own. Feature 319 (G4): every KIND= bundle
    carried every owed entry-drift unit, so the byre's answer recorded the windbreak's, which no agent had read."""
    return [u for u in units if u.check != "entry-drift" or u.subject == key]


def unfootnoted_owed(units: list[ru.Unit]) -> bool:
    """Is a quote-check of the page's unfootnoted blocks among the owed units (`quote-check:<stem>#unfootnoted`)?"""
    return any(u.check == "quote-check" and u.subject.partition("#")[2] == "unfootnoted" for u in units)


def owed_notes(units: list[ru.Unit]) -> frozenset[str]:
    """The notes a `FOR=quote-check` bundle with no NOTES= is cut to - none (the whole question) only when the unfootnoted
    reading is ALL that is owed. Beside owed notes it is the excerpt's `bare` blocks (feature 314), not the whole question:
    319 H2 found one changed note and one unmarked block of 0059 batched as the whole question's 140 notes, five agents."""
    keys = {u.subject.partition("#")[2] for u in units if u.check == "quote-check"}
    return frozenset(keys - {"unfootnoted"})


# --- the intro-check bundle (plan D4) --------------------------------------------------------------------------------------


@functools.cache
def _modal_docs(root: pathlib.Path) -> tuple[tuple[str, str], ...]:
    """(class name, docstring) of every modal, parsed once a run - a batch of 24 questions parsed them 24 times."""
    import modal_owed as mo  # noqa: PLC0415 - feature 319 (plan D12): a modal's text is its own file

    return tuple((m.cls.split(".", 1)[1], m.doc) for m in mo.modals_now(root, about_only=False))


def modals_for(root: pathlib.Path, page: str) -> list[str]:
    """The `Name:` of every modal whose `Entry:` names this question page - what the map draws from it (the class-level
    `Label:` went with the old form, feature 319)."""
    out = []
    for cls, doc in _modal_docs(root):
        if re.search(rf"^\s*Entry:.*\b{re.escape(page)}", doc, re.M):
            name = re.search(r"^\s*Name:\s*(.+)$", doc, re.M)
            out.append(f"- {name.group(1).strip() if name else cls}")
    return out


def page_text(text: str) -> str:
    """A page as its reader meets it, one block a line, the intro flagged - comments stripped, markup gone."""
    p = ru.read_page(text)
    return "\n".join([f"# {p.heading}", *((("[INTRO] " if b.intro else "") + b.words) for b in p.blocks)])


def intro_bundle_text(root: pathlib.Path, q: str) -> str:
    """One question's part of an intro-check bundle: its research page whole (the check confirms an intro adds no claim the
    body does not carry), its drawing page, and the map elements written from it."""
    qdir = root / ru.QUESTIONS
    research = sorted(p for p in qdir.glob(f"{question_of(q)}-*.html") if ru._STEM.match(p.name) and ".drawing." not in p.name)
    if not research:
        return ""
    page = research[0]
    drawing = page.with_name(page.name[: -len(".html")] + ".drawing.html")
    parts = [f"=== QUESTION {question_of(q)} - origin `{ru.QUESTIONS}/{page.name}`", "", "--- the research page", page_text(page.read_text(encoding="utf-8"))]
    if drawing.is_file():
        parts += ["", "--- how our maps draw it (its drawing page)", page_text(drawing.read_text(encoding="utf-8"))]
    modals = modals_for(root, page.name)
    parts += ["", "--- the map elements written from it", *(modals or ["- (none: no modal's Entry names this question)"]), ""]
    return "\n".join(parts)
