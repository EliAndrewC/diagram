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


_ITEM4 = re.compile(r"^4\. \*\*.*?(?=^\d+\. \*\*|^#|\Z)", re.M | re.S)
_SPAN = re.compile(r"`([^`\n]*)`")
_NOT_A_FIGURE = re.compile(
    r"\b\d{4}-\d\d-\d\d(?:T\d\d:\d\d(?::\d\d)?Z?)?\b|\b\d\d:\d\d(?::\d\d)?Z?\b|\b(?:FR|SC)-\d+[a-z]?\b|\b[TDA]\d+[a-z]?\b|\b0\d{3}\b"
)
#: a number that names a thing rather than measures it: "round 1", "seed 45", "hour 22", "amendment 6", "item 4"
_NAMED = re.compile(r"(?i)\b(?:round|rounds|seed|seeds|hour|amendment|item|items|change|wave|batch|step|task|feature|proposal|part|tier|version|line|group)\s+\d+(?:\s*(?:-|and|to)\s*\d+)?\b")
_LABEL = re.compile(r"(?is)(?=.*\bmeasured\b)(?=.*\b20\d\d-\d\d-\d\d\b)(?=.*\()|\bm:[\w.-]+")


def unlabeled_figure(section: str) -> str:
    """The first figure Approach item 4 states whose own sentence carries no `measured <date> (<method>)` or `m:<key>`, or ''
    (feature 385 T86, plan D107; T81's "4.4 s (measured)" came back unreviewable). A code span holding a path, a key or a command
    is set aside; one holding a value is read as prose; dates, clock times and ids are no figures."""
    m = _ITEM4.search(section)
    if not m:
        return ""
    item = _SPAN.sub(lambda s: " " if re.search(r"/|::|=|\bmake ", s.group(1)) else s.group(1), m.group(0))
    for sentence in re.split(r"(?<=\.)\s+|\n(?=\S)", item):
        bare = _NOT_A_FIGURE.sub(" ", re.sub(r"^\s*4\.", " ", sentence))
        bare = _NAMED.sub(" ", bare)
        if re.search(r"(?<![\w-])\d[\d,.]*(?![\w-])", bare) and not _LABEL.search(sentence):
            return sentence.strip()[:160]
    return ""


def refusal(spec_dir: pathlib.Path, section: str) -> str:
    """Why `make decide` refuses this section, or ''."""
    req = (spec_dir / "request.md").read_text(encoding="utf-8") if (spec_dir / "request.md").is_file() else ""
    if missing := gm_quotes_missing(section, req):
        return ("the section quotes the GM with words request.md does not hold - add the GM's words to request.md verbatim, or "
                "correct the quote (feature 385 T84):\n  " + "\n  ".join(f'"{q.strip()[:160]}"' for q in missing))
    if fig := unlabeled_figure(section):
        return ("Approach item 4 states a figure whose sentence carries no `measured <YYYY-MM-DD> (<method>)` or `m:<key>` - label "
                f"it where it stands (feature 385 T86):\n  {fig}")
    return ""
