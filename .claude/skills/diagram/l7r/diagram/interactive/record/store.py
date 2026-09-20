"""The fragments on disk: writing them once, and reading them back into a page (feature 258).

`split.py` and `assemble.py` know nothing about the filesystem - they are the property the tests hold.
This is where a `Page` meets a directory: what a fragment is called, which names are legal in a page
directory, and every refusal in `contracts/fragment-format.md`.

Nothing here guesses. A file it does not recognize is a refusal, not something skipped: a skipped
fragment is a lost entry of the record, and it would be lost silently.
"""

from __future__ import annotations

import os

from l7r.diagram.interactive.record import fragments as frag
from l7r.diagram.interactive.record.assemble import assemble
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
    """The page as its fragments make it."""
    return assemble(read_fragments(page_rel, record_dir))


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
    """Every page whose committed bytes differ from what its fragments would make, as messages."""
    stale = []
    for page_rel in record_pages(record_dir):
        if not os.path.isdir(os.path.join(record_dir, frag.page_dir(page_rel))):
            continue  # not split yet - a stage that has not landed
        with open(os.path.join(record_dir, page_rel), encoding="utf-8") as fh:
            committed = fh.read()
        if committed != read_page(page_rel, record_dir):
            stale.append(page_rel)
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
    known = {frag.FRONT, frag.TAIL, frag.CITATIONS_FRONT, frag.CITATIONS_WORKS, frag.CITATIONS_TAIL}
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
