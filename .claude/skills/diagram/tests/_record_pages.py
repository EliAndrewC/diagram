"""The record's pages as the tests read them - read from the fragments, never from a built file (features 301, 303).

The site is built (`make record`) and not committed, so a test that opened a built page would read nothing in a fresh
clone, or a stale copy in an old one. Every test over the record reads it here instead, through `sources.record_text`
- the same reading the engine does. `RecordPath` is a path to where a page IS (`research/questions/<file>`, or the
registry's `SOURCES.html`), so a test keeps its path arithmetic (`relative_to`, `.name`, `/`); its text is a
question page as its reader sees it - with its cross-link and its *Not to be confused with:* list - and `numbered`
gives the same page with its references numbered from 1 and its notes by number, as its small page carries them.
"""

from __future__ import annotations

import functools
import os
import pathlib

from l7r.diagram.interactive.record import site_notes, store
from l7r.diagram.interactive.sources import RESEARCH_DIR, record_text


@functools.cache
def _real_record() -> store.qs.Record:
    return store.load(RESEARCH_DIR)


@functools.cache
def text_of(rel: str) -> str:
    """`rel` as `sources.record_text` reads it, with the real record LOADED ONCE per test process (2026-10-04).

    `record_text` caches each page's text, but a miss on a question page calls `store.load` - the whole record, ~90 ms -
    so the tests that read every page loaded the record 475 times: 42 s of a 44 s test, measured by cProfile, and
    three such tests were a quarter of a full `make quick`. A question page is the same two calls the engine makes
    (`store.load`, then `store.page_html`) on one record; anything else goes through `record_text` as before."""
    if rel.startswith("questions/"):
        record = _real_record()
        name = rel[len("questions/") :]
        if name in record.by_file:
            return store.page_html(record, record.by_file[name], RESEARCH_DIR)
    return record_text(rel)


class RecordPath(pathlib.PosixPath):
    """A page of the record by its path; its text is read from its fragments."""

    def _rel(self) -> str:
        return os.path.relpath(self, RESEARCH_DIR).replace(os.sep, "/")

    def read_text(self, encoding: str | None = "utf-8", errors: str | None = None, newline: str | None = None) -> str:  # noqa: ARG002 - pathlib's signature
        return text_of(self._rel())

    def exists(self, *, follow_symlinks: bool = True) -> bool:  # noqa: ARG002 - pathlib's signature
        return bool(text_of(self._rel()))


def page(rel: str) -> RecordPath:
    """`questions/<file>` or `SOURCES.html`."""
    return RecordPath(RESEARCH_DIR, rel)


def question_pages() -> list[RecordPath]:
    """Every question page of both halves, in number order."""
    return [page(f"questions/{p.file}") for p in store.load(RESEARCH_DIR).pages()]


def all_pages() -> list[RecordPath]:
    """Every page a reader opens: the registry and every question page."""
    return [page("SOURCES.html"), *question_pages()]


def numbered(path: pathlib.Path) -> tuple[str, dict[str, str]]:
    """A question page with its references numbered from 1, as its small page carries them, and {number: note body}."""
    body, placed = site_notes.small_page(path.read_text(encoding="utf-8"), store.page_notes(path.name), str(path.name))
    return body, {str(p.number): p.body for p in placed}


def notes_text(path: pathlib.Path) -> str:
    """A question page's notes as its reader sees them - originals put back - one `<li>` each; empty for the registry
    and for a page with no notes."""
    if path.name == "SOURCES.html":
        return ""
    return "".join(f"<li>{body}</li>\n" for body in store.page_notes(path.name).values())
