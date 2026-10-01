"""The record's questions, one stem each, in one flat directory (feature 303).

The GM, 2026-10-01: *"considering that they are all like individual files now, are we actually getting anything out of
having a directory called cities?"* - no. Every question lives in `research/questions/` under one stem,
`NNNN-<slug>`: its research page `NNNN-<slug>.html`, its drawing page `NNNN-<slug>.drawing.html` (how our maps draw
it), and beside each its `.notes.html` and `.originals.html`. `NNNN` is the question's identity across the record and
never its order; `<slug>` is the heading id of the stem's research page (of its drawing page where it has none), so a
glob on the heading id finds the file.

A research page states its tags on the line after its heading (`contents.py`); a drawing page in the same stem inherits
them. A drawing page alone in its stem is either a second drawing page of another stem's question - it says so,
`<!-- about: NNNN-<slug> -->`, and inherits that question's tags - or a drawing-only question that states its own.

Nothing here guesses. A file it does not recognize is a refusal naming it, and a run gathers every refusal.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field

from l7r.diagram.interactive.record import contents as ct

QUESTIONS = "questions"
NOTES = ".notes.html"
ORIGINALS = ".originals.html"
DRAWING = ".drawing"
#: A file of the questions directory: number, slug, drawing or not, and notes / originals or the page itself.
_NAME = re.compile(r"^(\d{4})-([^./\s]+)(\.drawing)?(\.notes|\.originals)?\.html$")
#: A page's heading: the first `<h2>`.
_HEADING = re.compile(r'<h2 id="([^"]+)">(.*?)</h2>', re.S)
ABOUT = re.compile(r"<!-- about: (\d{4}-[^\s]+) -->")
_TAG = re.compile(r"<[^>]+>")
_XREF = re.compile(r'<span class="xref">.*?</span>', re.S)


class QuestionError(Exception):
    """A refusal about the questions directory. Its message names every file at fault."""


@dataclass
class Page:
    """One page of a question: its research page or its drawing page."""

    stem: str
    number: int
    drawing: bool
    file: str  # the file name in `questions/`
    heading_id: str
    title: str
    text: str

    @property
    def notes_file(self) -> str:
        return self.file[: -len(".html")] + NOTES

    @property
    def originals_file(self) -> str:
        return self.file[: -len(".html")] + ORIGINALS

    @property
    def half(self) -> str:
        return "drawing" if self.drawing else "research"


@dataclass
class Question:
    number: int
    stem: str
    research: Page | None = None
    drawing: Page | None = None
    about: str | None = None  # the stem a lone drawing page is about
    tags: ct.Tags | None = None
    home: ct.Section | None = None

    def pages(self) -> list[Page]:
        return [p for p in (self.research, self.drawing) if p is not None]


@dataclass
class Record:
    """Every question, the vocabulary and the contents, read and checked."""

    questions: list[Question]
    vocab: ct.Vocabulary
    sections: list[ct.Section]
    by_file: dict[str, Page] = field(default_factory=dict)
    by_id: dict[str, Page] = field(default_factory=dict)
    by_stem: dict[str, Question] = field(default_factory=dict)

    def pages(self, half: str | None = None) -> list[Page]:
        return [p for q in self.questions for p in q.pages() if half is None or p.half == half]

    def question_of(self, page: Page) -> Question:
        return self.by_stem[page.stem]

    def ordered(self, pages: list[Page]) -> list[Page]:
        """Pages in presentation order: level, then identity number, then research before drawing (spec FR-011)."""

        def key(p: Page) -> tuple[int, int, int]:
            tags = self.question_of(p).tags
            assert tags is not None  # every question is tagged once `load` returns
            return (self.vocab.level_rank(tags.level), p.number, int(p.drawing))

        return sorted(pages, key=key)

    def in_section(self, section: ct.Section, half: str) -> list[Page]:
        """The pages of one half whose question lives in exactly this section, in order."""
        return self.ordered([p for p in self.pages(half) if self.question_of(p).home is section])

    def holds(self, section: ct.Section, half: str) -> bool:
        """Does this section, or a subsection, home a page of this half? An empty section is omitted (FR-013)."""
        return bool(self.in_section(section, half)) or any(self.holds(s, half) for s in section.sections)


def text_of(markup: str) -> str:
    return re.sub(r"\s+", " ", _TAG.sub("", _XREF.sub("", markup))).strip()


def heading(text: str) -> tuple[str, str] | None:
    """(heading id, heading text) of a page, or None."""
    m = _HEADING.search(re.sub(r"<!--.*?-->", "", text, flags=re.S))
    return (m.group(1), m.group(2)) if m else None


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _gather(record_dir: str, errors: list[str]) -> dict[str, Question]:
    """Every stem in the directory, its pages read; a name that is not a question's file is a refusal."""
    root = os.path.join(record_dir, QUESTIONS)
    stems: dict[str, Question] = {}
    numbers: dict[int, str] = {}
    companions: list[tuple[str, str]] = []
    for name in sorted(os.listdir(root)) if os.path.isdir(root) else []:
        m = _NAME.match(name)
        if m is None:
            errors.append(f"{QUESTIONS}/{name}: not a question's file - NNNN-<slug>.html, .drawing.html, and their .notes.html and .originals.html")
            continue
        number, slug, drawing, companion = int(m.group(1)), m.group(2), bool(m.group(3)), m.group(4)
        stem = f"{m.group(1)}-{slug}"
        if numbers.setdefault(number, stem) != stem:
            errors.append(f"{QUESTIONS}/{name}: number {m.group(1)} is already {numbers[number]} - a number names one question")
            continue
        q = stems.setdefault(stem, Question(number, stem))
        if companion:
            companions.append((stem, name))
            continue
        text = _read(os.path.join(root, name))
        found = heading(text)
        if found is None:
            errors.append(f"{QUESTIONS}/{name}: no `<h2 id=...>` heading")
            continue
        page = Page(stem, number, drawing, name, found[0], text_of(found[1]), text)
        if drawing:
            q.drawing = page
        else:
            q.research = page
    for stem, name in companions:
        page_file = re.sub(r"\.(notes|originals)\.html$", ".html", name)
        if not any(p.file == page_file for p in stems[stem].pages()):
            errors.append(f"{QUESTIONS}/{name}: beside no page - {page_file} does not exist")
    return stems


def _check_slug(q: Question, errors: list[str]) -> None:
    owner = q.research or q.drawing
    if owner is not None and q.stem.split("-", 1)[1] != owner.heading_id:
        errors.append(f"{QUESTIONS}/{owner.file}: its name says `{q.stem.split('-', 1)[1]}` and its heading is `{owner.heading_id}` - the slug is the heading id")


def _tags(q: Question, record_dir: str, vocab: ct.Vocabulary, errors: list[str]) -> None:
    """A question's stated tags and `about:`, with the refusals of spec FR-007."""
    for page in q.pages():
        where = f"{QUESTIONS}/{page.file}"
        try:
            stated = ct.parse_tags(page.text, where, vocab)
        except ct.ContentsError as e:
            errors.append(str(e))
            continue
        about = ABOUT.search(page.text)
        if not page.drawing:
            if about:
                errors.append(f"{where}: an `about:` on a research page - only a lone drawing page names the question it is about")
            if stated is None:
                errors.append(f"{where}: no tags - a research page states `{ct.Tags(('<subject>',), ('<setting>',), '<level>').marker()}` on the line after its heading")
            q.tags = stated
        elif q.research is not None:
            if stated is not None or about:
                errors.append(f"{where}: states {'tags' if stated else 'an about:'} - a drawing page beside its research page inherits its tags")
        elif about and stated:
            errors.append(f"{where}: states both tags and an `about:` - it inherits from the question it is about, or is a question of its own")
        elif about:
            q.about = about.group(1)
        elif stated is None:
            errors.append(f"{where}: no tags and no `about:` - a drawing page alone in its stem says which question it draws, or states its own tags")
        else:
            q.tags = stated


def load(record_dir: str) -> Record:
    """Every question, tagged and homed, or a `QuestionError` naming every refusal (spec FR-007, FR-010)."""
    vocab = ct.load_vocabulary(record_dir)
    sections = ct.load_contents(record_dir, vocab)
    errors: list[str] = []
    stems = _gather(record_dir, errors)
    record = Record(sorted(stems.values(), key=lambda q: q.number), vocab, sections, by_stem=stems)
    for q in record.questions:
        _check_slug(q, errors)
        _tags(q, record_dir, vocab, errors)
        for page in q.pages():
            if page.heading_id in record.by_id:
                errors.append(f"{QUESTIONS}/{page.file}: heading id `{page.heading_id}` is also {record.by_id[page.heading_id].file}'s")
            record.by_id.setdefault(page.heading_id, page)
            record.by_file[page.file] = page
    for q in record.questions:
        if q.about is not None:
            target = stems.get(q.about)
            if target is None or target.research is None:
                errors.append(f"{QUESTIONS}/{q.drawing.file if q.drawing else q.stem}: `about: {q.about}` names no research question")
            else:
                q.tags = target.tags
    for q in record.questions:
        if q.tags is None:
            continue
        q.home = ct.home(sections, q.tags)
        if q.home is None:
            errors.append(f"{QUESTIONS}/{q.stem}: tags {q.tags.marker()} - no section of {ct.CONTENTS} takes them")
    if not errors:
        errors += ct.idle_rules(sections, [q.tags for q in record.questions if q.tags is not None])
    if errors:
        raise QuestionError("\n  ".join([f"the questions do not load ({len(errors)} refusal(s)):", *errors]))
    return record
