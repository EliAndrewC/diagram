"""Putting a page back together (feature 258).

Concatenation, byte for byte, with no separator, no re-indentation, no whitespace normalization and no
re-encoding: whatever a fragment holds is what the page gets. The only bytes the assembly WRITES rather
than copies are footnote numbers and the anchors that carry them, which `notes.py` owns.

That austerity is the point. A reader opens the assembled page from disk, the engine parses it, and
every test over the record reads it; if the assembly reformatted anything, the record's bytes would
become an output of a program rather than the thing a session wrote, and the GM's "identical to what we
have now" would be a claim nobody could check.
"""

from __future__ import annotations

from l7r.diagram.interactive.record.split import Page


def assemble(page: Page) -> str:
    """The page as a reader opens it: front, the sections in order with their entries, tail."""
    parts = [page.front]
    for section in page.sections:
        parts.append(section.text)
        parts.extend(entry.text for entry in section.entries)
    parts.append(page.tail)
    return "".join(parts)
