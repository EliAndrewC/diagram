"""The citations behind an explanation, read from the research record itself (feature 134, GM
2026-08-28: "all of the things that say that there is no reference for them should at this point
have a reference").

A class names the research entry it was written FROM (`FeatureClass.entry`: a file and one or more
quoted headings). The entry's `**Sources:**` line names keys in `research/SOURCES.md`, and the
registry there carries the citation and what each source was used for. Both are parsed here at page
write time, so a citation pass over the research (another session's, 2026-08-28) reaches every
modal without anyone re-typing keys into `classes.py` - whose own `sources` tuple is only the
fallback for an entry the parser cannot find.
"""

from __future__ import annotations

import os
import re
from functools import cache

_HERE = os.path.dirname(os.path.abspath(__file__))
RESEARCH_DIR = os.path.normpath(os.path.join(_HERE, "..", "..", "..", "research"))

_KEY = re.compile(r"`([a-z0-9][a-z0-9-]*)`")
_ENTRY_FILE = re.compile(r"research/([a-z-]+\.md)")
# A heading is quoted 'like this', and "like this" when the heading itself contains an apostrophe -
# the single-quote form cannot carry "A reservoir's shore is reeded". Both are read (settlement-review
# 2026-08-29): with only the first form the marsh entry lost `mineta-2007-tameike` from the modal AND
# swallowed the heading after it, because the run of characters between the two double quotes matched
# as one giant "heading" that no section is named.
_ENTRY_HEADING = re.compile(r"'((?:[^']|'(?=[A-Za-z]))+)'|\"([^\"]+)\"")


@cache
def _sections(path: str) -> list[tuple[str, str]]:
    """(heading, body) for every `##`/`###` section of a research file."""
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except OSError:
        return []
    out: list[tuple[str, str]] = []
    heading = ""
    body: list[str] = []
    for line in text.splitlines():
        if line.startswith("## ") or line.startswith("### "):
            if heading:
                out.append((heading, "\n".join(body)))
            heading = line.lstrip("#").strip()
            body = []
        else:
            body.append(line)
    if heading:
        out.append((heading, "\n".join(body)))
    return out


def section_sources(body: str) -> list[str]:
    """The SOURCES.md keys a section's `**Sources:**` line names (in order, deduplicated)."""
    m = re.search(r"^\*\*Sources:\*\*(.*)$", body, re.M)
    if not m:
        return []
    keys: list[str] = []
    for k in _KEY.findall(m.group(1)):
        if k not in keys:
            keys.append(k)
    return keys


def research_sources(entry: str, research_dir: str = RESEARCH_DIR) -> list[str]:
    """Every key the research entries named in `entry` cite. A quoted heading matches a section whose
    heading STARTS with it (the registry quotes headings shortened at a dash)."""
    files = _ENTRY_FILE.findall(entry)
    # a heading is the OUTERMOST quoted text of each "; "-separated segment - a title may itself
    # carry an apostrophe ("The garden's sun"), so a simple quote-to-quote match cuts it short
    # a quoted heading; a quote followed by a letter is an apostrophe INSIDE a title ("The garden's
    # sun"), any other quote closes it
    headings = [m.group(1) or m.group(2) for m in _ENTRY_HEADING.finditer(entry)]
    keys: list[str] = []
    for fname in files:
        for heading, body in _sections(os.path.join(research_dir, fname)):
            if any(heading.startswith(h) or h.startswith(heading) for h in headings):
                for k in section_sources(body):
                    if k not in keys:
                        keys.append(k)
    return keys


@cache
def registry(research_dir: str = RESEARCH_DIR) -> dict[str, str]:
    """key -> the SOURCES.md entry text (citation and its 'Used for' line), markdown stripped lightly."""
    out: dict[str, str] = {}
    for heading, body in _sections(os.path.join(research_dir, "SOURCES.md")):
        m = re.fullmatch(r"`([a-z0-9][a-z0-9-]*)`", heading.strip())
        if not m:
            continue
        text = re.sub(r"\s*\n\s*\n\s*", " | ", body.strip())
        text = re.sub(r"\*(Used for:)\*", r"\1", text).replace("*", "")
        out[m.group(1)] = text
    return out


_URL = re.compile(r"https?://[^\s)\]>]+")


def urls_of(text: str) -> list[str]:
    """Every URL a SOURCES.md entry carries (GM 2026-08-28: the references link to where the source
    can be read); the trailing punctuation a sentence leaves on a URL is trimmed."""
    out: list[str] = []
    for u in _URL.findall(text):
        u = u.rstrip(".,;:")
        if u not in out:
            out.append(u)
    return out


def citations(keys: list[str], research_dir: str = RESEARCH_DIR) -> dict[str, dict[str, object]]:
    """key -> {"text": the registry entry, "urls": its URLs} for the references modal."""
    reg = registry(research_dir)
    return {k: {"text": reg.get(k, "(not in research/SOURCES.md)"), "urls": urls_of(reg.get(k, ""))} for k in keys}
