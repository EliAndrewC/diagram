"""How a caption may be cut into lines (feature 266; the cutting rule is feature 133 T39's, lifted here unchanged).

The GM's wrap rule (research/presentation, "Why does a caption sometimes break across two lines?"): one line if that
clears the sheet, else the first of two or three lines that does. The placer asks it at every seat, one line first.
"""

from __future__ import annotations

import itertools


def cut(words: list[str], n: int) -> list[str] | None:
    """The best way to set `words` on `n` lines, or None when there is none.

    Words are never broken; a cut is a split of the word list into contiguous lines. Among the splits into `n` lines
    the one with the SHORTEST longest line wins (the block is as narrow as it can be), ties broken toward even
    lengths. A line that is only one short word - three letters or fewer - is refused whenever there are more words
    than lines, so "Shrine of Benten" is cut as "Shrine of / Benten" or "Shrine / of Benten", never with "of" alone."""
    best: tuple[tuple[int, int], list[str]] | None = None
    for cuts in itertools.combinations(range(1, len(words)), n - 1):
        bounds = (0, *cuts, len(words))
        lines = [" ".join(words[a:b]) for a, b in zip(bounds, bounds[1:], strict=False)]
        if len(words) > n and any(len(ln) <= 3 for ln in lines):
            continue  # a short word never stands alone
        score = (max(len(ln) for ln in lines), max(len(ln) for ln in lines) - min(len(ln) for ln in lines))
        if best is None or score < best[0]:
            best = (score, lines)
    return best[1] if best else None


def layouts(text: str) -> list[list[str]]:
    """Every layout a caption may take, in the order the wrap rule tries them: one line, then two, then three
    (three only for three words or more)."""
    words = text.split()
    out = [[text]]
    for n in (2, 3):
        if len(words) >= n:
            lines = cut(words, n)
            if lines is not None:
                out.append(lines)
    return out
