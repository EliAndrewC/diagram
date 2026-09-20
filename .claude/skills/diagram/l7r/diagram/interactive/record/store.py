"""The fragments on disk: writing them once, and reading them back into a page (feature 258).

`split.py` and `assemble.py` know nothing about the filesystem - they are the property the tests hold.
This is where a `Page` meets a directory: what a fragment is called, which names are legal in a page
directory, and every refusal in `contracts/fragment-format.md`.

Nothing here guesses. A file it does not recognize is a refusal, not something skipped: a skipped
fragment is a lost entry of the record, and it would be lost silently.
"""

from __future__ import annotations

import os
import re

from l7r.diagram.interactive.record import citations_side as cite
from l7r.diagram.interactive.record import fragments as frag
from l7r.diagram.interactive.record.assemble import assemble
from l7r.diagram.interactive.record.notes import allocate, merge, notes_of, number_references
from l7r.diagram.interactive.record.split import Entry, Page, Section, split
from l7r.diagram.interactive.sources import RESEARCH_DIR

#: The registry is the one page whose sections hold entries of their own - 920 of them.
REGISTRY = "SOURCES.html"
ENTRY_LEVEL = 3


class RecordError(Exception):
    """A refusal. Its message names the file, always, and never only a count."""


def record_pages(record_dir: str = RESEARCH_DIR) -> list[str]:
    """Every hand-authored page, as a path relative to the record: the registry, the research pages,
    and the `cities/` ones. The citations pages are not here - they are assembled beside their
    research page, from the same directory (stage 3)."""
    top = sorted(f for f in os.listdir(record_dir) if f.endswith(".html"))
    cities_dir = os.path.join(record_dir, "cities")
    cities = sorted(f"cities/{f}" for f in os.listdir(cities_dir) if f.endswith(".html")) if os.path.isdir(cities_dir) else []
    return top + cities


def entry_level(page_rel: str) -> int | None:
    """Which heading level is an ENTRY on this page, if any. Only the registry has them."""
    return ENTRY_LEVEL if page_rel == REGISTRY else None


def write_fragments(page_rel: str, record_dir: str = RESEARCH_DIR) -> list[str]:
    """Split a page that is still whole and write its fragments. Returns the paths written, relative
    to the record. Refuses to leave a split behind that does not assemble back to the same bytes."""
    with open(os.path.join(record_dir, page_rel), encoding="utf-8") as fh:
        text = fh.read()
    page = split(text, entry_level=entry_level(page_rel))
    where = frag.page_dir(page_rel)
    os.makedirs(os.path.join(record_dir, where), exist_ok=True)
    written = [_write(record_dir, where, frag.FRONT, page.front)]
    for position, section in enumerate(page.sections, start=1):
        name = frag.section_file(position, section.id)
        written.append(_write(record_dir, where, name, section.text))
        for at, entry in enumerate(section.entries, start=1):
            sub = os.path.join(where, name[: -len(".html")])
            os.makedirs(os.path.join(record_dir, sub), exist_ok=True)
            written.append(_write(record_dir, sub, frag.entry_file(at, entry.id), entry.text))
    written.append(_write(record_dir, where, frag.TAIL, page.tail))
    rebuilt = read_page(page_rel, record_dir)
    if rebuilt != text:
        raise RecordError(
            f"{page_rel}: the split does not assemble back to the same bytes "
            f"({_first_difference(text, rebuilt)}) - nothing has been removed, but the "
            f"fragments in {where}/ are wrong and must not be committed"
        )
    return written


def read_page(page_rel: str, record_dir: str = RESEARCH_DIR) -> str:
    """The research page as its fragments make it, numbered where its notes have moved (stage 3)."""
    return assemble_pages(page_rel, record_dir)[0]


def read_fragments(page_rel: str, record_dir: str = RESEARCH_DIR) -> Page:
    """The `Page` a directory of fragments holds, in prefix order, with every refusal checked."""
    where = frag.page_dir(page_rel)
    root = os.path.join(record_dir, where)
    if not os.path.isdir(root):
        raise RecordError(f"{where}/: no fragment directory for {page_rel} - run `make record SPLIT={where}`")
    names = os.listdir(root)
    front, tail = _required(where, root, names)
    sections = []
    for name in _ordered_sections(where, names):
        with open(os.path.join(root, name), encoding="utf-8") as fh:
            text = fh.read()
        sections.append(Section(id=_id_of(name), text=text, entries=_entries(where, root, name)))
    return Page(front=front, sections=tuple(sections), tail=tail)


def check(record_dir: str = RESEARCH_DIR) -> list[str]:
    """Every committed file whose bytes differ from what the fragments would make.

    The citations page is compared carrying the works region it already has: that region is
    `make citations`' to derive and `tests/interactive/test_citations.py`'s to hold equal to its
    source, and re-deriving it here would mean writing a page to disk, which a check does not do.
    """
    stale = []
    for page_rel in record_pages(record_dir):
        if not os.path.isdir(os.path.join(record_dir, frag.page_dir(page_rel))):
            continue  # not split yet - a stage that has not landed
        research, citations = assemble_pages(page_rel, record_dir)
        if _read(os.path.join(record_dir, page_rel)) != research:
            stale.append(page_rel)
        if citations is not None and _read(os.path.join(record_dir, cite.citations_rel(page_rel))) != citations:
            stale.append(cite.citations_rel(page_rel))
    return stale


def _write(record_dir: str, where: str, name: str, text: str) -> str:
    with open(os.path.join(record_dir, where, name), "w", encoding="utf-8") as fh:
        fh.write(text)
    return os.path.join(where, name)


def _required(where: str, root: str, names: list[str]) -> tuple[str, str]:
    missing = [n for n in (frag.FRONT, frag.TAIL) if n not in names]
    if missing:
        raise RecordError(f"{where}/: {' and '.join(missing)} missing - a page's front matter and its closing are fragments like any other, and the assembly will not invent them")
    out = []
    for name in (frag.FRONT, frag.TAIL):
        with open(os.path.join(root, name), encoding="utf-8") as fh:
            out.append(fh.read())
    return out[0], out[1]


def _ordered_sections(where: str, names: list[str]) -> list[str]:
    known = {frag.FRONT, frag.TAIL, frag.CITATIONS_FRONT, frag.CITATIONS_MID, frag.CITATIONS_TAIL}
    ordered = frag.ordered(names)
    for name in names:
        if name in known or name in ordered or name.endswith(frag.NOTES_SUFFIX):
            continue
        if os.path.isdir(os.path.join(where, name)) or not name.endswith(".html"):
            continue  # an entries directory, checked with its section
        raise RecordError(f"{where}/{name}: not a fragment name. A page directory holds {frag.FRONT}, {frag.TAIL}, <prefix>-<heading id>.html and their .notes.html, and nothing else")
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
    for name in _ordered_sections(os.path.join(where, sub), os.listdir(path)):
        with open(os.path.join(path, name), encoding="utf-8") as fh:
            text = fh.read()
        entry = Entry(id=_id_of(name), text=text)
        if frag.key_of(_heading_id(text)) != frag.key_of(entry.id):
            raise RecordError(f"{where}/{sub}/{name}: its filename says `{frag.key_of(entry.id)}` and its heading registers `{frag.key_of(_heading_id(text))}` - one of the two is wrong")
        out.append(Entry(id=_heading_id(text), text=text))
    return tuple(out)


def _id_of(name: str) -> str:
    """The heading id a fragment's name carries: `010-how-deep.html` -> `how-deep`."""
    return name.split("-", 1)[1][: -len(".html")]


def _heading_id(text: str) -> str:
    from l7r.diagram.interactive.record.split import heading_id  # noqa: PLC0415 - one call, no cycle at import

    return heading_id(text, 0)


def _first_difference(want: str, got: str) -> str:
    for at, (a, b) in enumerate(zip(want, got, strict=False)):
        if a != b:
            return f"first difference at byte {at}: {want[at : at + 40]!r} against {got[at : at + 40]!r}"
    return f"one is {len(want)} characters and the other {len(got)}"


# ---------------------------------------------------------------- stage 3: the notes


def has_notes(page_rel: str, record_dir: str = RESEARCH_DIR) -> bool:
    """Has this page's citations side been moved into fragments yet? A stage that has not landed is
    not a failure, so every reader below asks first."""
    return os.path.isfile(os.path.join(record_dir, frag.page_dir(page_rel), frag.CITATIONS_FRONT))


def read_notes(page_rel: str, record_dir: str = RESEARCH_DIR) -> dict[str, str]:
    """{key: body} for the whole page, gathered from its questions' notes files in question order."""
    where = frag.page_dir(page_rel)
    root = os.path.join(record_dir, where)
    per_question = []
    for name in frag.ordered(os.listdir(root)):
        notes_path = os.path.join(root, frag.notes_file(name))
        if not os.path.isfile(notes_path):
            continue
        with open(notes_path, encoding="utf-8") as fh:
            per_question.append((f"{where}/{frag.notes_file(name)}", notes_of(fh.read(), f"{where}/{name}")))
    return merge(per_question)


def assemble_pages(page_rel: str, record_dir: str = RESEARCH_DIR) -> tuple[str, str | None]:
    """(the research page, the citations page) as the fragments make them.

    The citations page carries the works region the committed page carries; `write_pages` is what
    re-derives it, because the derivation reads a page from disk and this function writes nothing.
    """
    research = assemble(read_fragments(page_rel, record_dir))
    if not has_notes(page_rel, record_dir):
        return research, None
    stripped, placed = allocate(research, read_notes(page_rel, record_dir), page_rel)
    research = number_references(research, placed, cite.citations_href(page_rel))
    where = os.path.join(record_dir, frag.page_dir(page_rel))
    parts = []
    for name in (frag.CITATIONS_FRONT, frag.CITATIONS_MID, frag.CITATIONS_TAIL):
        with open(os.path.join(where, name), encoding="utf-8") as fh:
            parts.append(fh.read())
    committed = _read(os.path.join(record_dir, cite.citations_rel(page_rel))) or ""
    page = cite.assemble_citations(parts[0], cite.works_region(committed), parts[1], placed, parts[2], cite.page_href(page_rel))
    return research, page


def write_pages(page_rel: str, record_dir: str = RESEARCH_DIR) -> int:
    """Write both of a page's committed files, re-deriving the works block from the assembled page.

    Two passes, in this order, so that `citations.py` reads a PAGE and never a fragment (FR-029):
    the citations page goes to disk with the works region as it stands, `derive()` reads it there,
    and the page is written again with the region filled - along with the hover script beside it.
    """
    from l7r.diagram.interactive.citations import derive, script_path  # noqa: PLC0415 - one call site

    research, citations = assemble_pages(page_rel, record_dir)
    written = _write_if_changed(os.path.join(record_dir, page_rel), research)
    if citations is None:
        return written
    written += _write_if_changed(os.path.join(record_dir, cite.citations_rel(page_rel)), citations)
    js, html, _ = derive(page_rel, record_dir)
    written += _write_if_changed(os.path.join(record_dir, cite.citations_rel(page_rel)), html)
    written += _write_if_changed(os.path.join(record_dir, script_path(page_rel)), js)
    return written


def _write_if_changed(path: str, text: str) -> int:
    if _read(path) == text:
        return 0
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return 1


def _read(path: str) -> str | None:
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def write_notes_fragments(page_rel: str, record_dir: str = RESEARCH_DIR) -> list[str]:
    """The one-time move of a page's notes beside the questions that cite them (stage 3).

    Each note goes to the question where it is FIRST referenced, in the order that question cites it,
    and takes a key derived from its own leading source key (research R5). The question fragments are
    rewritten from numbers to keys, and the citations page's three hand-authored regions become
    fragments of their own. Refuses to leave the move behind unless what assembles back carries the
    same assertions with the same notes.
    """
    where = frag.page_dir(page_rel)
    root = os.path.join(record_dir, where)
    if has_notes(page_rel, record_dir):
        raise RecordError(f"{page_rel}: its notes have already moved - the migration runs once, and running it again on key-form references would find no numbered ones")
    committed_citations = _read(os.path.join(record_dir, cite.citations_rel(page_rel)))
    if committed_citations is None:
        raise RecordError(f"{page_rel}: no citations page beside it - nothing to move")
    notes = cite.old_notes(committed_citations)
    names = frag.ordered(os.listdir(root))
    bodies = {name: _read(os.path.join(root, name)) or "" for name in names}

    slug_of: dict[int, str] = {}
    for name in names:
        for found in cite.OLD_REFERENCE.finditer(bodies[name]):
            slug_of.setdefault(int(found.group(1)), name.split("-", 1)[1][: -len(".html")])
    keys = cite.keys_for("".join(bodies[name] for name in names), notes, slug_of)
    missing = sorted(set(notes) - set(keys))
    if missing:
        raise RecordError(f"{cite.citations_rel(page_rel)}: note(s) {missing} that no reference on {page_rel} names - the move will not drop them, and cannot place them")

    written = []
    for name in names:
        first_here = [n for n in dict.fromkeys(int(m.group(1)) for m in cite.OLD_REFERENCE.finditer(bodies[name])) if slug_of.get(n) == name.split("-", 1)[1][: -len(".html")]]
        written.append(_write(record_dir, where, name, cite.to_key_form(bodies[name], keys)))
        if first_here:
            fragment = cite.notes_fragment([(keys[n], notes[n]) for n in first_here])
            written.append(_write(record_dir, where, frag.notes_file(name), fragment))
    front, mid, tail = cite.split_regions(committed_citations)
    for name, text in ((frag.CITATIONS_FRONT, front), (frag.CITATIONS_MID, mid), (frag.CITATIONS_TAIL, tail)):
        written.append(_write(record_dir, where, name, text))

    research, citations = assemble_pages(page_rel, record_dir)
    _refuse_a_move_that_changed_the_record(page_rel, research, citations, notes, record_dir)
    return written


def _refuse_a_move_that_changed_the_record(page_rel: str, research: str, citations: str | None, notes: dict[int, str], record_dir: str) -> None:
    """What stage 3 is allowed to change, and nothing else (spec SC-003).

    The research page may differ from the committed one ONLY in its footnote numbers and the ids that
    carry them; the citations page's notes may be reordered, but the same note bodies must be there,
    all of them.
    """
    committed = _read(os.path.join(record_dir, page_rel)) or ""
    if _numberless(committed) != _numberless(research):
        raise RecordError(f"{page_rel}: the move changed more than the footnote numbers - with every number and reference id stripped, the page is not the page it was")
    if citations is not None:
        was, now = sorted(notes.values()), sorted(cite.old_notes(citations).values())
        if was != now:
            raise RecordError(f"{cite.citations_rel(page_rel)}: {len(was)} notes went in and {len(now)} came out, or their text changed - the move carries every note verbatim")


def _numberless(page_html: str) -> str:
    """A page with every footnote number and reference id removed, for comparing across a renumbering."""
    out = re.sub(r'<sup class="fn"><a (?:id="fnref-[0-9a-z-]+" )?href="([^"]*)#fn-\d+">\d+</a></sup>', r'<sup class="fn"><a href="\1"></a></sup>', page_html)
    return out
