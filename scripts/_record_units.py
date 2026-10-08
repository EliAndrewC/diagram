#!/usr/bin/env python3
"""The record checks a delta owes, decided over plain text - the pure half of `_record_owed.py` (feature 311).

WHY (GM 2026-10-02). Asked whether an edit re-runs every check: *"it would be a waste of time and tokens for us to add the
kind of paragraph that I just explained and then rerun all of the other subagent checks for things like whether the research
accurately characterizes its source or... whether our quotations match word for word"*, and *"not just do the correct thing,
to kind of enforce us doing the correct thing"*. So what each check is owed is a function of what changed, and of nothing
else, and this module is that function - tested with strings, no repository (`tests/tooling/test_record_owed.py`).

WHAT COUNTS AS CHANGED (spec FR-004). A heading, a block or a note is changed only when its WORDS change - its text with HTML
comments, markup and whitespace normalized away and each note mark kept as a `[^key]` token - and only when those words stand
nowhere in the record at the base. A comment, a tag marker, a bold or a re-wrap changes no words; a move, a renumbering or a
merge leaves the words standing somewhere, so it owes nothing (`_translation_owed.py` judges a translated pair the same way).

WHAT IS OWED, row by row (spec FR-004):

    a research page's heading changed                -> intro-check
    an intro added, changed or removed               -> intro-check, record-format
    a note changed                                   -> source-reader and quote-check on that note, record-format
    a block carrying note marks changed              -> quote-check on each mark it carries (SUPPORTS), record-format
    a block with no mark, not an intro, changed      -> quote-check's unfootnoted reading of its page, record-format
    a source write-up's visible words changed        -> source-applicability

The two `quote-check` rows on blocks go beyond the proposal the GM accepted (spec Decisions Recorded: rewording an assertion can
make a faithful quotation stop supporting it, and new uncited prose may carry a historical claim). The intro is MARKED
(`<p class="intro">`) so that it alone is spared every source-reading check: it is *"definitionally something that is not
citing any research"*. `translation-check` and `entry-drift` keep their own scripts; `_record_owed.py` folds them in.

A UNIT is `<check>:<subject>`: the subject is a question (`0094`), a page and a note (`0094#kyakhta`, `0094.drawing#k`), a
page's unfootnoted prose (`0094#unfootnoted`) or a source key. Its FINGERPRINT hashes exactly the words its check reads, so an
answer recorded for a unit stays good until those words move.
"""

from __future__ import annotations

import hashlib
import html
import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field

RECORD = "research"
QUESTIONS = f"{RECORD}/questions"
SOURCES = f"{RECORD}/sources/010-works-cited"

_COMMENT = re.compile(r"<!--.*?-->", re.S)
_MARK = re.compile(r'<sup class="fn" data-note="([^"]+)"></sup>')
_TAG = re.compile(r"<[^>]+>")
_BREAK = re.compile(r"<br\s*/?>", re.I)
_SPACE = re.compile(r"\s+")
_HEADING = re.compile(r"<h[23][^>]*>(.*?)</h[23]>", re.S)
# the blocks a reader meets, as `_check_bundle.py` reads them: an unclosed block ends where the next one opens
_BLOCK = re.compile(r"<(p|li|blockquote|td|dd)\b([^>]*)>(.*?)(?:</\1>|(?=<(?:p|li|blockquote|td|dd)\b)|\Z)", re.S)
_NOTE = re.compile(r'<li data-note="([^"]+)">(.*?)</li>', re.S)
_ORIG_TOKEN = re.compile(r'<span class="orig" data-orig="([^"]+)"></span>')
_ORIG_STORED = re.compile(r'<li data-orig="([^"]+)">(.*?)</li>', re.S)
_STEM = re.compile(r"^(\d{4})-([^.]+)(\.drawing)?\.html$")
_INTRO = re.compile(r'\bclass="intro"')
#: a cited key is LINKED (`<a href=...><code>key</code></a>`, "a key is never bare"): a bare `<code>` in a note is a symbol
#: kept out of the glossary's tooltips - Sugiura's table letters `be`, `mo` - and named no source (feature 319, G4)
_CODE = re.compile(r'<a href="[^"]*"(?: [^>]*)?>\s*<code>([a-z0-9][a-z0-9-]*)</code>\s*</a>')

#: the checks this module decides, in the order a report lists them
CHECKS = ("intro-check", "record-format", "source-reader", "quote-check", "source-applicability")


def words(text: str) -> str:
    """A fragment's WORDS: comments and markup gone, entities decoded, whitespace collapsed, each note mark a `[^key]`."""
    text = _COMMENT.sub("", text)
    text = _MARK.sub(lambda m: f" [^{m.group(1)}]", text)
    text = _BREAK.sub(" ", text)  # a lead line and its body are two runs of words, not one
    return _SPACE.sub(" ", html.unescape(_TAG.sub("", text))).strip()


def digest(parts: Iterable[str]) -> str:
    return hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()[:16]


@dataclass(frozen=True)
class Block:
    words: str
    marks: tuple[str, ...]
    intro: bool = False


@dataclass
class Page:
    heading: str = ""
    blocks: list[Block] = field(default_factory=list)

    @property
    def intro(self) -> str:
        return next((b.words for b in self.blocks if b.intro), "")


def read_page(text: str) -> Page:
    """A question page as its reader meets it: the heading, then every block in order, the intro flagged."""
    body = _COMMENT.sub("", text)
    head = _HEADING.search(body)
    blocks = []
    for m in _BLOCK.finditer(body):
        w = words(m.group(3))
        if w:
            blocks.append(Block(w, tuple(dict.fromkeys(_MARK.findall(m.group(3)))), m.group(1) == "p" and bool(_INTRO.search(m.group(2)))))
    return Page(words(head.group(1)) if head else "", blocks)


def read_notes(notes: str, originals: str = "") -> dict[str, str]:
    """key -> the note's words, with its originals put back (a changed original is a changed note: quote-check reads it)."""
    table = dict(_ORIG_STORED.findall(originals))
    restored = _ORIG_TOKEN.sub(lambda m: table.get(m.group(1), ""), notes)
    return {k: words(body) for k, body in _NOTE.findall(restored)}


@dataclass
class Record:
    """The record as the checks read it: pages by their stem (`0094`, `0094.drawing`), notes by stem, write-ups by key."""

    pages: dict[str, Page]
    notes: dict[str, dict[str, str]]
    slugs: dict[str, str]
    sources: dict[str, str]
    #: stem -> note -> the registry keys the note links (`<code>key</code>`): which notes a source-reader read is for
    cites: dict[str, dict[str, tuple[str, ...]]] = field(default_factory=dict)

    @classmethod
    def of(cls, files: Mapping[str, str], sources: Mapping[str, str]) -> Record:
        """`files`: a question file's name -> its text (pages, notes, originals); `sources`: a key -> its write-up's text."""
        pages: dict[str, Page] = {}
        notes: dict[str, dict[str, str]] = {}
        slugs: dict[str, str] = {}
        cites: dict[str, dict[str, tuple[str, ...]]] = {}
        for name, text in files.items():
            if name.endswith(".notes.html"):
                page = name[: -len(".notes.html")] + ".html"
                m = _STEM.match(page)
                if m:
                    notes[_subject(m)] = read_notes(text, files.get(name[: -len(".notes.html")] + ".originals.html", ""))
                    cites[_subject(m)] = {k: tuple(dict.fromkeys(_CODE.findall(body))) for k, body in _NOTE.findall(text)}
                continue
            m = _STEM.match(name)
            if m:
                pages[_subject(m)] = read_page(text)
                slugs[_subject(m)] = m.group(2)
        return cls(pages, notes, slugs, {k: words(v) for k, v in sources.items()}, cites)

    def index(self) -> Index:
        ix = Index()
        for page in self.pages.values():
            ix.headings.add(page.heading)
            ix.blocks.update(b.words for b in page.blocks)
        for notes in self.notes.values():
            ix.notes.update(notes.values())
        return ix


@dataclass
class Index:
    """Every heading, block and note's words in a record - what "stands nowhere at the base" is asked of."""

    headings: set[str] = field(default_factory=set)
    blocks: set[str] = field(default_factory=set)
    notes: set[str] = field(default_factory=set)


def _subject(m: re.Match[str]) -> str:
    return m.group(1) + (".drawing" if m.group(3) else "")


def question(subject: str) -> str:
    """The question a subject belongs to: `0094.drawing#k` -> `0094`."""
    return subject.split("#", 1)[0].split(".", 1)[0]


@dataclass(frozen=True)
class Unit:
    slug: str
    occasion: str
    fingerprint: str = ""

    @property
    def check(self) -> str:
        return self.slug.split(":", 1)[0]

    @property
    def subject(self) -> str:
        return self.slug.split(":", 1)[1]


def owed(now: Record, base: Record) -> list[Unit]:
    """THE DECISION (spec FR-004): every unit `now` owes against `base`, each with its occasion and fingerprint."""
    ix = base.index()
    out: dict[str, str] = {}

    def owe(slug: str, why: str) -> None:
        out.setdefault(slug, why)

    for stem, page in now.pages.items():
        q, research = question(stem), not stem.endswith(".drawing")
        if research and page.heading not in ix.headings:
            owe(f"intro-check:{q}", "the heading is new or changed")
        for b in page.blocks:
            if b.words in ix.blocks:
                continue
            owe(f"record-format:{q}", "visible words new or changed")
            if b.intro:
                owe(f"intro-check:{q}", "the intro is new or changed")
            elif b.marks:
                for k in b.marks:
                    owe(f"quote-check:{stem}#{k}", "a block carrying this note changed (SUPPORTS)")
            else:
                owe(f"quote-check:{stem}#unfootnoted", "a block with no note mark changed (an uncited claim?)")
        for k, w in now.notes.get(stem, {}).items():
            if w not in ix.notes:
                owe(f"source-reader:{stem}#{k}", "the note is new or changed")
                owe(f"quote-check:{stem}#{k}", "the note is new or changed")
                owe(f"record-format:{q}", "visible words new or changed")
    # an intro removed: its words are gone, and the question it stood on is still here under its slug
    held = {now.slugs[s]: s for s in now.pages if not s.endswith(".drawing")}
    for stem, page in base.pages.items():
        if not stem.endswith(".drawing") and page.intro and base.slugs[stem] in held:
            if now.pages[held[base.slugs[stem]]].intro != page.intro:
                owe(f"intro-check:{question(held[base.slugs[stem]])}", "the intro is removed or changed")
    for key, w in now.sources.items():
        if base.sources.get(key) != w:
            owe(f"source-applicability:{key}", "the write-up is new or its visible words changed")
    return [Unit(slug, why, fingerprint(now, slug)) for slug, why in sorted(out.items())]


def fingerprint(rec: Record, slug: str) -> str:
    """A hash of exactly the words the unit's check reads (plan D1)."""
    check, subject = slug.split(":", 1)
    stem, _, note = subject.partition("#")
    q = question(subject)
    if check == "intro-check":
        page = rec.pages.get(q, Page())
        return digest([page.heading, page.intro])
    if check == "record-format":
        parts = []
        for s in (q, f"{q}.drawing"):
            page = rec.pages.get(s, Page())
            parts += [page.heading, *(b.words for b in page.blocks), *(f"{k}={v}" for k, v in sorted(rec.notes.get(s, {}).items()))]
        return digest(parts)
    if check == "source-applicability":
        return digest([rec.sources.get(subject, "")])
    page, notes = rec.pages.get(stem, Page()), rec.notes.get(stem, {})
    if check == "source-reader":
        return digest([notes.get(note, "")])
    if note == "unfootnoted":
        return digest(b.words for b in page.blocks if not b.marks and not b.intro)
    return digest([notes.get(note, ""), *(b.words for b in page.blocks if note in b.marks)])
