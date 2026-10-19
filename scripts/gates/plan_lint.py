"""What `make decide` refuses before a plan section reaches its review (feature 385 T84 and T86, plans D105 and D107).

WHY. The evening of 2026-10-18 sent 42 plan reviews; four came back unreviewable for what a script can see first - the GM's words
not in `request.md` (T70, T75 twice) and a figure with no date or method (T81) - and T64's first plan misquoted the GM.
"""

from __future__ import annotations

import pathlib
import re

_GM = re.compile(r"\bthe GM(?:'s)?\b", re.I)
_WORD = re.compile(r"[a-z0-9]+")


def _folded(text: str) -> str:
    return " " + " ".join(_WORD.findall(text.lower())) + " "


def gm_quotes(section: str) -> list[str]:
    """Each double-quoted span that follows "the GM" (any case, with or without 's) within the same sentence."""
    out: list[str] = []
    masked = re.sub(r"`[^`\n]*`", lambda c: " " * len(c.group(0)), section)  # a code span names words, it quotes no one
    for m in _GM.finditer(masked):
        if masked[masked.rfind("\n", 0, m.start()) + 1 : m.start()].count('"') % 2:
            continue  # "the GM" inside a quotation is a mention, not an attribution
        i, quoting, start = m.end(), False, 0
        while i < len(masked):
            ch = masked[i]
            if ch == '"':
                if quoting:
                    out.append(section[start:i])  # read from the text as written, code spans and all
                else:
                    start = i + 1
                quoting = not quoting
            elif not quoting and (ch == "\n" and masked[i + 1 : i + 2] in ("\n", "") or ch in ".!?" and masked[i + 1 : i + 2] in (" ", "\n", "")):
                break
            i += 1
    return list(dict.fromkeys(out))


def gm_quotes_missing(section: str, request: str) -> list[str]:
    """The GM quotes whose words, folded, are not a run in the request folded the same way (D105) - every length, no escape."""
    req = _folded(request)

    def found(q: str) -> bool:  # an elided quote is found when each piece between its ellipses is (the plan review's note)
        return all(_folded(p) in req for p in re.split(r"\.\.\.|\u2026", q) if _folded(p).strip())

    return [q for q in gm_quotes(section) if _folded(q).strip() and not found(q)]


def refusal(spec_dir: pathlib.Path, section: str) -> str:
    """Why `make decide` refuses this section, or ''."""
    req = (spec_dir / "request.md").read_text(encoding="utf-8") if (spec_dir / "request.md").is_file() else ""
    if missing := gm_quotes_missing(section, req):
        return ("the section quotes the GM with words request.md does not hold - add the GM's words to request.md verbatim, or "
                "correct the quote (feature 385 T84):\n  " + "\n  ".join(f'"{q.strip()[:160]}"' for q in missing))
    return ""
