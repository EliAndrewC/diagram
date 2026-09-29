"""What an ABSENCE note says to its reader (feature 292) - the ONE place its opening words are kept.

An absence note - a claim that stands, honestly labeled, because no public page could be found to cite for it (feature
195) - is written, and read by every script, as `no publicly readable source` followed by what was searched. The GM,
2026-09-29: *"Instead of 'no publicly available source' our standard wording should be 'Our research of
publicly-available sources couldn't find anything conclusive:' ... the replacement text ... should be stored in a single
place so that if we update it later we are updating a single line of text."* So the notes keep the short MARKER a script
classifies by, and the assembly shows `LEAD` in its place: the marker stays in the page inside a hidden span, so a reader
of the page's text still meets it first, and `unrender` gives any reader of the raw markup the note as it was written.

What was searched and when - the terms, the date - is for a later session, not the reader (GM, same day: *"the date we
searched and what the web searches were is not information the human reader needs to see"*): it is written in an HTML
comment after the marker, `no publicly readable source<!-- searched 2026-09-28: ... -->`, and what the search found is
the note's visible text, a list of `<span class="pass">` items (`pass sub` nested) where it is several things.
"""

from __future__ import annotations

import re

#: The words every absence note opens with, as its reader sees them. Change them here and `make record` re-renders
#: every absence note in the record.
LEAD = "Our research of publicly-available sources couldn't find anything conclusive:"
MARKER = "no publicly readable source"
_RENDERED = re.compile(rf'<span class="sep">{MARKER}</span><span class="absence-lead">[^<]*</span>')


def render(body: str) -> str:
    """A note's body as the page shows it: an absence note's marker hidden and `LEAD` shown; any other note unchanged."""
    stripped = body.lstrip()
    if not stripped.startswith(MARKER):
        return body
    at = len(body) - len(stripped)
    return body[:at] + f'<span class="sep">{MARKER}</span><span class="absence-lead">{LEAD}</span>' + body[at + len(MARKER) :]


def unrender(body: str) -> str:
    """The note as it was written - the marker bare - from a rendered page, for a reader that classifies raw markup."""
    return _RENDERED.sub(MARKER, body, count=1)
