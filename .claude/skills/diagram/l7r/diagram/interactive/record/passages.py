"""A footnote that quotes several passages, shown as a list (feature 292).

The GM, 2026-09-29: *"anytime we are citing multiple things from a source instead of one thing, we should display this as
a bulleted list within the footnote"* - flat when the passages are siblings, nested when one passage introduces others
(*"from a 1750 document of the Kawai papers, which the paper glosses:"* followed by the glosses).

The notes a session writes do not change: a note is still one line, its passages joined by `; `. The assembly writes the
list - `<span class="pass">` per passage (`pass sub` for one a colon introduced) inside `<span class="passages">` - and
keeps every separator it replaces, in a `<span class="sep">` the stylesheet hides. So the text of the page, tags
stripped, is exactly what it was: every reader of the citations pages (the quote-verbatim script, the tests) meets the
same words, and only the reader sees a list. Spans, not list items, because a note is itself an `<li>` and every reader
of the notes matches `<li ...>(.*?)</li>` lazily.

A split is made only at depth zero - outside brackets 「」, parentheses, double quotes, and HTML tags and comments - and
only where the next thing is a passage: a quotation mark, or the key link of another source.
"""

from __future__ import annotations

import re

_KEY_HEAD = re.compile(r'^(\s*<a href="[^"]*"(?: [^>]*)?><code>[a-z0-9][a-z0-9-]*</code></a>)( - )')
_STARTS = ("「", '"', "“", "<a href=")


def _depth0_marks(text: str) -> list[tuple[int, str]]:
    """(index, kind) of each `;`, `/` and `:` at depth zero, kind being the character (`/` joins two passages in some
    notes: `"..." / "..."`)."""
    marks = []
    depth, in_quote, i = 0, False, 0
    while i < len(text):
        c = text[i]
        if c == "<":
            # a tag, a comment and a collapsed original (originals.py) are each one unit - never split inside them; an
            # unclosed one ends the scan (a `find` of -1 must not send the scan backwards)
            closer = "</span>" if text.startswith('<span class="orig">', i) else "-->" if text.startswith("<!--", i) else ">"
            at = text.find(closer, i + 1)
            if at < 0:
                break
            i = at + len(closer)
            continue
        if c in "「(（":
            depth += 1
        elif c in "」)）" and depth:
            depth -= 1
        elif c == '"':
            in_quote = not in_quote
        elif c in ";:/" and depth == 0 and not in_quote:
            marks.append((i, c))
        i += 1
    return marks


def _next_is_passage(text: str, at: int) -> int:
    """The index where a passage starts after the separator at `at`, or -1 when what follows is not a passage."""
    j = at + 1
    while j < len(text) and text[j] == " ":
        j += 1
    return j if text.startswith(_STARTS, j) else -1


def bulleted(body: str) -> str:
    """One note's body with its passages as a list, when it quotes more than one; unchanged otherwise."""
    head = _KEY_HEAD.match(body)
    if head is None:
        return body
    rest = body[head.end() :]
    cuts: list[tuple[int, int, str]] = []  # (end of this piece, start of the next, the separator's kind)
    for at, kind in _depth0_marks(rest):
        start = _next_is_passage(rest, at)
        if start >= 0:
            end = at + 1 if kind == ":" else len(rest[:at].rstrip(" "))  # ` ; ` and ` / `: the space before goes with the separator
            cuts.append((end, start, kind))
    if not cuts:
        return body
    pieces, seps, kinds, last = [], [], [], 0
    for end, start, kind in cuts:
        pieces.append(rest[last:end])
        seps.append(rest[end:start])
        kinds.append(kind)
        last = start
    tail = rest[last:]
    trailing = tail[len(tail.rstrip()) :]  # whitespace ending the note stays outside the list, where a reader trims it
    pieces.append(tail[: len(tail) - len(trailing)])
    nested = False
    out = [head.group(1), f'<span class="sep">{head.group(2)}</span><span class="passages">']
    for n, piece in enumerate(pieces):
        cls = "pass sub" if nested else "pass"
        out.append(f'<span class="{cls}">{piece}</span>')
        if n < len(seps):
            out.append(f'<span class="sep">{seps[n]}</span>')
            nested = nested or kinds[n] == ":"
    out.append("</span>" + trailing)
    return "".join(out)


_NOTE = re.compile(r'(<li data-note="[^"]+">)(.*?)(</li>)', re.S)


def bulleted_notes(notes_html: str) -> str:
    """Every note of a notes file, each with its passages listed when it has several."""
    return _NOTE.sub(lambda m: m.group(1) + bulleted(m.group(2)) + m.group(3), notes_html)
