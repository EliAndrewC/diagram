"""The record, written per entry and assembled into the pages a reader opens (feature 258).

The GM, 2026-09-20: *"split our questions into individual files and split our citations into individual
files so that they get assembled into documents that are identical to what we have now ... but where
when you have to make an edit, then you are opening a file which is relatively small."*

The saving is not the session's own editing - reads of the record are 0.56% of all tool output and 90%
of them already ask for a window (spec research R2). It is the CHECKING AGENTS: one research page was
23% to 98% of everything that entered a recorded agent's context, a median of 68% over 17 runs (R3),
and feature 251 measured input at 75-90% of an agent's cost. An agent sent to check one entry was
reading the other thirty.

What is here: `split` takes a page apart, `assemble` puts it back, and the two are inverses - which is
what lets one test hold the property over the real record rather than over a fixture.
"""

from __future__ import annotations

from l7r.diagram.interactive.record.assemble import assemble
from l7r.diagram.interactive.record.split import Entry, Page, Section, comments, headings, sections_of, split

__all__ = ["Entry", "Page", "Section", "assemble", "comments", "headings", "sections_of", "split"]
