"""The record's pages as the tests read them - assembled in memory, never from a file (feature 301).

The pages are built (`make record`, `record/site.py`) and no longer committed, so a test that opened
`research/<page>.html` would read nothing in a fresh clone, or a stale copy in an old one. Every test over the record
reads it here instead, through `sources.record_text` - the same in-memory assembly the engine reads. `RecordPath` is a
path to where a page WOULD be, so a test keeps its path arithmetic (`relative_to`, `.name`, `/`); only its contents
come from the fragments.
"""

from __future__ import annotations

import os
import pathlib

from l7r.diagram.interactive.citations import citations_page
from l7r.diagram.interactive.record.store import record_pages
from l7r.diagram.interactive.sources import RESEARCH_DIR, record_text


class RecordPath(pathlib.PosixPath):
    """A page of the record (or a citations page) by its path; its text is the in-memory assembly."""

    def _rel(self) -> str:
        return os.path.relpath(self, RESEARCH_DIR).replace(os.sep, "/")

    def read_text(self, encoding: str | None = "utf-8", errors: str | None = None, newline: str | None = None) -> str:  # noqa: ARG002 - pathlib's signature
        return record_text(self._rel())

    def exists(self, *, follow_symlinks: bool = True) -> bool:  # noqa: ARG002 - pathlib's signature
        return bool(record_text(self._rel()))


def page(rel: str) -> RecordPath:
    """`fields.html`, `cities/fabric.html`, `SOURCES.html`, `citations/fields.html`."""
    return RecordPath(RESEARCH_DIR, rel)


def research_pages() -> list[RecordPath]:
    """Every research page (the registry excepted), in the record's order."""
    return [page(p) for p in record_pages() if p != "SOURCES.html"]


def all_pages() -> list[RecordPath]:
    """Every page a reader of the per-page record would open: the registry, the research pages, their citations pages."""
    research = research_pages()
    return [page("SOURCES.html"), *research, *(citations_of(p) for p in research)]


def citations_of(path: pathlib.Path) -> RecordPath:
    """The citations page of a research page."""
    return page(citations_page(os.path.relpath(path, RESEARCH_DIR).replace(os.sep, "/")))
