"""A quotation's ORIGINAL-language text, stored apart from its translation (feature 292).

The GM, 2026-09-29: *"when we include translated text, and then also include the original text in whatever language
... can we store the original text separately as well? ... other than that, I don't think that there is any reason for
other subagent checks to read both the translation and the original text ... the original text should be collapsed by
default."*

A note quotes a foreign passage as `「English」 (translated; original: 「原文」)`
(feature 202). The notes fragment a session edits and a check reads keeps the translation and, where the original
stood, a PLACEHOLDER - `<span class="orig" data-orig="<key>#<n>"></span>`; the original itself lives in the question's
`.originals.html` beside it, one `<li data-orig="<key>#<n>">original: 「原文」</li>` per unit. The assembly puts each
original back, wrapped - `<span class="orig">original: 「原文」</span>` - so the pages a reader opens, and every script
that reads them with the tags stripped, meet the note's text exactly as before; `record.js` collapses the wrapped span
behind a click.

A UNIT is `original: 「...」` with any originals joined to it in one run (`original: 「O1」 and 「O2」`, `...; original:
「O2」`): one placeholder per run keeps the bytes between the originals, so restoring is exact. Brackets nest
(`「...「...」...」`), so a unit closes at depth zero.
"""

from __future__ import annotations

import re

ORIGINALS_SUFFIX = ".originals.html"
_START = re.compile(r"original:\s*「")
#: What may stand between two originals of one run: a joiner, and perhaps a repeated `original:`.
_JOIN = re.compile(r"\s*(?:and|/|,|;)?\s*(?:original:\s*)?(?=「)")
_NOTE = re.compile(r'(<li data-note="([^"]+)">)(.*?)(</li>)', re.S)
_TOKEN = re.compile(r'<span class="orig" data-orig="([^"]+)"></span>')
_STORED = re.compile(r'<li data-orig="([^"]+)">(.*?)</li>\n?', re.S)


def _close(text: str, at: int) -> int:
    """The index just past the `」` that closes the `「` at `at`, bracket depth counted; -1 when it never closes."""
    depth = 0
    for i in range(at, len(text)):
        if text[i] in "「｢":  # the half-width forms too: a source's own nested `｢...｣` inside a quotation (water/620)
            depth += 1
        elif text[i] in "」｣":
            depth -= 1
            if depth == 0:
                return i + 1
    return -1


def units(text: str) -> list[tuple[int, int]]:
    """The [start, end) of every original run in one note's text."""
    out: list[tuple[int, int]] = []
    pos = 0
    while (m := _START.search(text, pos)) is not None:
        end = _close(text, m.end() - 1)
        if end < 0:
            break
        while (j := _JOIN.match(text, end)) is not None and (nxt := _close(text, j.end())) > 0:
            end = nxt
        out.append((m.start(), end))
        pos = end
    return out


def split(notes_html: str, originals_html: str = "") -> tuple[str, str]:
    """(the notes with a placeholder for each original run still written inline, the originals file with those runs
    appended). A run already moved is left where it is, and a new one in the same note is numbered after the note's
    highest - so a session writes a note the natural way, original inline, and `make record` moves it. Notes with no
    inline original are unchanged."""
    stored = {ref.rsplit("#", 1)[0]: 0 for ref, _ in _STORED.findall(originals_html)}
    for ref, _ in _STORED.findall(originals_html):
        key, n = ref.rsplit("#", 1)
        stored[key] = max(stored[key], int(n))
    added: list[str] = []

    def one(m: re.Match[str]) -> str:
        key, body = m.group(2), m.group(3)
        n = max([stored.get(key, 0)] + [int(r.rsplit("#", 1)[1]) for r in _TOKEN.findall(body)])
        parts, last = [], 0
        for a, b in units(body):
            n += 1
            ref = f"{key}#{n}"
            added.append(f'<li data-orig="{ref}">{body[a:b]}</li>\n')
            parts += [body[last:a], f'<span class="orig" data-orig="{ref}"></span>']
            last = b
        return m.group(1) + "".join(parts) + body[last:] + m.group(4)

    return _NOTE.sub(one, notes_html), originals_html + "".join(added)


def has_placeholder(notes_html: str) -> bool:
    """Does this notes text hold a placeholder, which needs its originals file?"""
    return _TOKEN.search(notes_html) is not None


def restore(notes_html: str, originals_html: str, *, wrapped: bool = True) -> str:
    """The notes with each placeholder replaced by its original - wrapped in `<span class="orig">` for the pages a
    reader opens, or bare (`wrapped=False`) to reproduce the text as it was before the split. A placeholder with no
    stored original is a refusal: the original would silently vanish from the page."""
    table = dict(_STORED.findall(originals_html))

    def one(m: re.Match[str]) -> str:
        ref = m.group(1)
        if ref not in table:
            raise KeyError(f"no original stored for `{ref}` - its `.originals.html` lacks `<li data-orig=\"{ref}\">`")
        return f'<span class="orig">{table[ref]}</span>' if wrapped else table[ref]

    return _TOKEN.sub(one, notes_html)
