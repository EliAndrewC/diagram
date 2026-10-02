"""The record on disk, read for a reader (features 258, 303).

Since feature 303 the record holds two kinds of thing. The QUESTIONS are one stem each in `questions/`
(`record/questions.py` reads and checks them); a question page is shown as its fragment says, with the cross-link to its
other half and its *Not to be confused with:* list written in (`page_html`), and with its own notes (`page_notes`). The
REGISTRY is still a page of fragments - `sources/`, its front matter, its groups and their entries - assembled as
feature 258 assembled every page (`read_fragments`, `registry_html`).

A note's key is unique within its PAGE (a research page, or a drawing page), and a reference resolves in that page's own
notes file only (spec 303 research R3): a note two questions cite is in both notes files.

Nothing here guesses. A file it does not recognize is a refusal, not something skipped: a skipped fragment is a lost
entry of the record, and it would be lost silently.
"""

from __future__ import annotations

import os
import re

from l7r.diagram.interactive.record import absence, confusables, originals, passages, xref
from l7r.diagram.interactive.record import fragments as frag
from l7r.diagram.interactive.record import questions as qs
from l7r.diagram.interactive.record.assemble import assemble
from l7r.diagram.interactive.record.notes import NoteError, merge, notes_of
from l7r.diagram.interactive.record.split import Entry, Page, Section
from l7r.diagram.interactive.sources import RESEARCH_DIR

#: The registry is the one page whose sections hold entries of their own.
REGISTRY = "SOURCES.html"
REGISTRY_DIR = "sources"
ENTRY_LEVEL = 3


class RecordError(Exception):
    """A refusal. Its message names the file, always, and never only a count."""


def entry_level(page_rel: str) -> int | None:
    """Which heading level is an ENTRY on this page, if any. Only the registry has them."""
    return ENTRY_LEVEL if page_rel == REGISTRY else None


def load(record_dir: str = RESEARCH_DIR) -> qs.Record:
    """Every question, tagged and homed; a refusal as a `RecordError` naming every file at fault."""
    try:
        return qs.load(record_dir)
    except (qs.QuestionError, qs.ct.ContentsError) as e:
        raise RecordError(str(e)) from None


# ------------------------------------------------------------------------------------------------- the registry


def read_fragments(page_rel: str = REGISTRY, record_dir: str = RESEARCH_DIR) -> Page:
    """The `Page` the registry's directory of fragments holds, in prefix order, with every refusal checked."""
    where = frag.page_dir(page_rel)
    root = os.path.join(record_dir, where)
    if not os.path.isdir(root):
        raise RecordError(f"{where}/: no fragment directory for {page_rel}")
    names = os.listdir(root)
    front, tail = _required(where, root, names)
    sections = []
    for name in _ordered_sections(where, root, names):
        sections.append(Section(id=_id_of(name), text=_read(os.path.join(root, name)) or "", entries=_entries(where, root, name)))
    return Page(front=front, sections=tuple(sections), tail=tail)


def registry_html(record_dir: str = RESEARCH_DIR) -> str:
    """The registry as one page."""
    return assemble(read_fragments(REGISTRY, record_dir))


def _required(where: str, root: str, names: list[str]) -> tuple[str, str]:
    missing = [n for n in (frag.FRONT, frag.TAIL) if n not in names]
    if missing:
        raise RecordError(f"{where}/: {' and '.join(missing)} missing - a page's front matter and its closing are fragments like any other, and the assembly will not invent them")
    return _read(os.path.join(root, frag.FRONT)) or "", _read(os.path.join(root, frag.TAIL)) or ""


def _ordered_sections(where: str, root: str, names: list[str]) -> list[str]:
    ordered = frag.ordered(names)
    for name in names:
        if name in (frag.FRONT, frag.TAIL) or name in ordered:
            continue
        if os.path.isdir(os.path.join(root, name)):
            continue  # an entries directory, checked with its section
        raise RecordError(f"{where}/{name}: not a fragment name. A page directory holds {frag.FRONT}, {frag.TAIL} and <prefix>-<heading id>.html, and nothing else")
    seen: dict[int, str] = {}
    for name in ordered:
        at = frag.position_of(name)
        if at in seen:
            raise RecordError(f"{where}/: {seen[at]} and {name} both claim prefix {at:0{frag.SECTION_DIGITS}d} - the assembly will not choose between them")
        seen[at] = name
    return ordered


def _entries(where: str, root: str, section_name: str) -> tuple[Entry, ...]:
    sub = section_name[: -len(".html")]
    path = os.path.join(root, sub)
    if not os.path.isdir(path):
        return ()
    out = []
    for name in _ordered_sections(f"{where}/{sub}", path, os.listdir(path)):
        text = _read(os.path.join(path, name)) or ""
        heading = _heading_id(text)
        if frag.key_of(heading) != frag.key_of(_id_of(name)):
            raise RecordError(f"{where}/{sub}/{name}: its filename says `{frag.key_of(_id_of(name))}` and its heading registers `{frag.key_of(heading)}` - one of the two is wrong")
        out.append(Entry(id=heading, text=text))
    return tuple(out)


def _id_of(name: str) -> str:
    """The heading id a fragment's name carries: `010-how-deep.html` -> `how-deep`."""
    return name.split("-", 1)[1][: -len(".html")]


def _heading_id(text: str) -> str:
    from l7r.diagram.interactive.record.split import heading_id  # noqa: PLC0415 - one call, no cycle at import

    return heading_id(text, 0)


# ------------------------------------------------------------------------------------------------- a question's page


_NOTE_BODY = re.compile(r'(<li data-note="[^"]+">)(.*?)(</li>)', re.S)


def page_notes(file: str, record_dir: str = RESEARCH_DIR) -> dict[str, str]:
    """{key: body} of one page's notes, as its reader sees them: originals put back, a note of several passages as a
    list, an absence note's words (feature 292). A page with no notes file has none."""
    root = os.path.join(record_dir, qs.QUESTIONS)
    base = file[: -len(".html")]
    notes_name, orig_name = base + qs.NOTES, base + qs.ORIGINALS
    text = _read(os.path.join(root, notes_name))
    if text is None:
        return {}
    stored = _read(os.path.join(root, orig_name))
    if stored is not None:
        try:
            text = originals.restore(text, stored)
        except KeyError as e:
            raise RecordError(f"{qs.QUESTIONS}/{notes_name}: {e.args[0]}") from None
    elif originals.has_placeholder(text):
        raise RecordError(f"{qs.QUESTIONS}/{notes_name}: a note holds an original's placeholder and {orig_name} is missing")
    text = passages.bulleted_notes(text)
    text = _NOTE_BODY.sub(lambda m: m.group(1) + absence.render(m.group(2)) + m.group(3), text)
    try:
        return merge([(f"{qs.QUESTIONS}/{notes_name}", notes_of(text, f"{qs.QUESTIONS}/{notes_name}"))])
    except NoteError as e:
        raise RecordError(str(e)) from None


def page_html(record: qs.Record, page: qs.Page, record_dir: str = RESEARCH_DIR) -> str:
    """A question page as its reader sees it, before its links are written for a site page: the cross-link to its
    other half (feature 292, `xref.py`) and its *Not to be confused with:* list (`confusables.py`) written in."""
    html = xref.link(page.text, page, xref.pairs(record))
    pairs = confusables.load(record_dir)
    bad = confusables.unresolved(pairs, record)
    if bad:
        raise RecordError(f"{confusables.DATA} names a section that does not exist:\n  " + "\n  ".join(bad))
    return confusables.write(html, page.file, pairs, record)


def split_originals(record_dir: str = RESEARCH_DIR, *, write: bool = True) -> list[str]:
    """Move every original still written inline in a page's notes into its `.originals.html` (feature 292,
    `originals.py`); returns the notes files that had one. With `write=False` it only reports - the check."""
    moved = []
    root = os.path.join(record_dir, qs.QUESTIONS)
    for name in sorted(os.listdir(root)) if os.path.isdir(root) else []:
        if not name.endswith(qs.NOTES):
            continue
        notes_path = os.path.join(root, name)
        orig_path = notes_path[: -len(qs.NOTES)] + qs.ORIGINALS
        text, stored = _read(notes_path) or "", _read(orig_path) or ""
        new_text, new_stored = originals.split(text, stored)
        if new_text == text:
            continue
        moved.append(f"{qs.QUESTIONS}/{name}")
        if write:
            _overwrite(notes_path, new_text)
            _overwrite(orig_path, new_stored)
    return moved


def _overwrite(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def _read(path: str) -> str | None:
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None
