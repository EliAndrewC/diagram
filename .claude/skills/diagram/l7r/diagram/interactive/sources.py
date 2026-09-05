"""What a modal's references rest on, read from the research record itself.

A class names the research entry it was written FROM (`FeatureClass.entry`: a file and one or more
quoted headings). Two things are read out of that pointer at page-write time, so a change to the
record reaches every modal without anyone re-typing anything into `classes.py`:

- **the QUESTIONS** (feature 180, GM 2026-09-05) - the headings of the sections the entry names, each
  with a link to that section on the public GitHub rendering of the research file. This is what the
  references modal shows: *"instead of listing individual sources on the references modal, we will
  list the questions which we asked and researched - those pages are themselves sourced with links,
  so a user who wants to follow through and read the original sources can do so."* The audience is
  a casual RPG enthusiast curious why the settlement looks the way it does, and they are not to be
  met with a wall of third-party works; the sources are one click further out, on the page that
  answers the question.
- **the SOURCES** (feature 134, GM 2026-08-28: "all of the things that say that there is no reference
  for them should at this point have a reference") - the `**Sources:**` keys those sections cite and
  the `research/SOURCES.md` registry behind them. The page no longer shows these; the tests over the
  record still read them, to prove every entry cites and every source carries a URL where it can be
  read (constitution v2.13.0).
"""

from __future__ import annotations

import os
import re
import unicodedata
from functools import cache

_HERE = os.path.dirname(os.path.abspath(__file__))
RESEARCH_DIR = os.path.normpath(os.path.join(_HERE, "..", "..", "..", "research"))

#: WHERE A QUESTION LINKS (feature 180). The GM's own example URL, less the file: the research tree as
#: GitHub renders it, on `main`. `main` rather than a commit is a recorded decision (spec D1): a reader
#: gets the CURRENT answer, including a correction made after their map was rendered; the cost - a
#: renamed heading breaks the anchor on a page rendered before the rename - is accepted because
#: `research/README.md` rules anchors stable and every pool page re-renders at each landing.
RESEARCH_URL = "https://github.com/EliAndrewC/diagram/blob/main/.claude/skills/diagram/research/"

_KEY = re.compile(r"`([a-z0-9][a-z0-9-]*)`")
#: A research file the entry names - `research/water.md`, or one level down, `research/cities/fabric.md`.
#: The one-level form was added in feature 180 (spec FR-012a): the pattern could not match a
#: subdirectory, so an entry naming a `cities/` file would have resolved to no sources and no questions,
#: silently. No class did that on the day it was fixed; the URL above is built from this same match, so
#: the silent miss would have become a silent broken link.
_ENTRY_FILE = re.compile(r"research/((?:[a-z-]+/)?[a-z-]+\.md)")
# A heading is quoted 'like this', and "like this" when the heading itself contains an apostrophe -
# the single-quote form cannot carry "A reservoir's shore is reeded". Both are read (settlement-review
# 2026-08-29): with only the first form the marsh entry lost `mineta-2007-tameike` from the modal AND
# swallowed the heading after it, because the run of characters between the two double quotes matched
# as one giant "heading" that no section is named.
_ENTRY_HEADING = re.compile(r"'((?:[^']|'(?=[A-Za-z]))+)'|\"([^\"]+)\"")
_HEADING_LINE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
#: The bookkeeping a heading carries for the project, not for the reader: a trailing parenthetical with
#: a date in it - "(researched 2026-08-27, feature 133 T41)", "(accepted 2026-08-29, feature 152)",
#: "(feature 156, 2026-08-29)". Stripped from the question TEXT only (spec FR-005, D2); the anchor is
#: computed from the full heading, so the link still lands.
_DATED_TAIL = re.compile(r"\s*\([^()]*\b\d{4}-\d{2}-\d{2}\b[^()]*\)\s*$")
#: Markdown emphasis and code markers, which GitHub renders away before it slugs the heading.
_MARKUP = re.compile(r"[*`]")


def heading_text(heading: str) -> str:
    """The rendered text of a markdown heading - what a reader sees and what GitHub slugs."""
    return _MARKUP.sub("", heading).strip()


def github_anchor(heading: str, seen: dict[str, int] | None = None) -> str:
    """GitHub's anchor for a heading (spec FR-006): the rendered text lowercased; every character that
    is not a letter, a digit, a combining mark, a space, a hyphen or an underscore dropped; spaces
    replaced by hyphens (so " - " becomes "---"); and, when `seen` is passed, a heading repeated within
    one file suffixed "-1", "-2", ... in order of appearance.

    The rule is REPRODUCED here rather than fetched, and it was checked against the live site before
    it shipped (2026-09-05, spec D7): seven headings with a `?`, parentheses, an apostrophe, ` - `, CJK
    characters and emphasis markers all carry exactly the anchor this predicts. `test_page.py` pins
    those seven, so a future divergence from GitHub's rule shows up as a failing test that states the
    expected string, not as a silently broken link."""
    kept: list[str] = []
    for ch in heading_text(heading).lower():
        if ch == " ":
            kept.append("-")
        elif ch in "-_" or ch.isalnum() or unicodedata.category(ch).startswith("M"):
            kept.append(ch)
    slug = "".join(kept)
    if seen is not None:
        n = seen.get(slug, 0)
        seen[slug] = n + 1
        if n:
            slug = f"{slug}-{n}"
    return slug


def question_text(heading: str) -> str:
    """The heading as the references modal shows it: the rendered text, less the dated bookkeeping."""
    return _DATED_TAIL.sub("", heading_text(heading)).strip()


@cache
def _parsed(path: str) -> list[tuple[str, str, str]]:
    """(heading, body, anchor) for every `##`/`###` section of a research file, in file order.

    The ANCHOR COUNTER WALKS EVERY HEADING LEVEL, because GitHub's does: a `####` between two sections
    takes part in the "-1" numbering of a repeated slug even though it opens no section here (fields.md
    carries several). Headings inside a fenced code block are skipped, as GitHub skips them - the
    README's entry-format example is one such."""
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except OSError:
        return []
    out: list[tuple[str, str, str]] = []
    seen: dict[str, int] = {}
    heading = anchor = ""
    body: list[str] = []
    fenced = False
    for line in text.splitlines():
        if line.startswith("```"):
            fenced = not fenced
        m = None if fenced else _HEADING_LINE.match(line)
        if m:
            a = github_anchor(m.group(2), seen)
            if len(m.group(1)) in (2, 3):
                if heading:
                    out.append((heading, "\n".join(body), anchor))
                heading, anchor = m.group(2), a
                body = []
                continue
        body.append(line)
    if heading:
        out.append((heading, "\n".join(body), anchor))
    return out


def _sections(path: str) -> list[tuple[str, str]]:
    """(heading, body) for every `##`/`###` section of a research file."""
    return [(h, b) for h, b, _a in _parsed(path)]


def _names(heading: str, quoted: str) -> bool:
    """Does a quoted heading from an entry name this section? The registry quotes headings shortened at
    a dash, so a match is a prefix either way."""
    return heading.startswith(quoted) or quoted.startswith(heading)


def _entry_headings(entry: str) -> list[str]:
    # a heading is the OUTERMOST quoted text of each "; "-separated segment - a title may itself
    # carry an apostrophe ("The garden's sun"), so a simple quote-to-quote match cuts it short
    # a quoted heading; a quote followed by a letter is an apostrophe INSIDE a title ("The garden's
    # sun"), any other quote closes it
    return [m.group(1) or m.group(2) for m in _ENTRY_HEADING.finditer(entry)]


def section_sources(body: str) -> list[str]:
    """The SOURCES.md keys a section's `**Sources:**` line names (in order, deduplicated)."""
    # THE LINE WRAPS, AND THE KEYS AFTER THE WRAP COUNT (2026-08-29). Matching to end-of-LINE read only
    # the first physical line of a `**Sources:**` entry, so a section citing more keys than fit in one
    # 100-column line silently lost the rest - and lost them INVISIBLY, since the modal still showed a
    # plausible list. Measured on research/water.md "A reservoir's shore is reeded": the line names seven
    # keys over two lines and only the first four reached the page, dropping `nies-tameike`,
    # `inamino-tameike-museum` and `ohmi-yoshi`. The entry runs to the blank line that ends the paragraph.
    m = re.search(r"^\*\*Sources:\*\*((?:.*(?:\n(?!\s*$).*)*))", body, re.M)
    if not m:
        return []
    keys: list[str] = []
    for k in _KEY.findall(m.group(1)):
        if k not in keys:
            keys.append(k)
    return keys


def research_sources(entry: str, research_dir: str = RESEARCH_DIR) -> list[str]:
    """Every key the research entries named in `entry` cite, in file order."""
    headings = _entry_headings(entry)
    keys: list[str] = []
    for fname in _ENTRY_FILE.findall(entry):
        for heading, body in _sections(os.path.join(research_dir, fname)):
            if any(_names(heading, h) for h in headings):
                for k in section_sources(body):
                    if k not in keys:
                        keys.append(k)
    return keys


def research_questions(entry: str, research_dir: str = RESEARCH_DIR) -> list[dict[str, str]]:
    """The QUESTIONS behind a modal (feature 180): `{"text", "url"}` for every research section the
    entry names, in the order the ENTRY quotes them rather than file order (spec D4 - the class author
    put the primary question first), deduplicated. `text` is the heading less its dated bookkeeping;
    `url` is the section's anchor on the public GitHub rendering of the file."""
    files = _ENTRY_FILE.findall(entry)
    out: list[dict[str, str]] = []
    urls: set[str] = set()
    for quoted in _entry_headings(entry):
        for fname in files:
            for heading, _body, anchor in _parsed(os.path.join(research_dir, fname)):
                url = f"{RESEARCH_URL}{fname}#{anchor}"
                if _names(heading, quoted) and url not in urls:
                    urls.add(url)
                    out.append({"text": question_text(heading), "url": url})
    return out


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
    """Every URL a SOURCES.md entry carries (GM 2026-08-28: a source records where it can be read);
    the trailing punctuation a sentence leaves on a URL is trimmed."""
    out: list[str] = []
    for u in _URL.findall(text):
        u = u.rstrip(".,;:")
        if u not in out:
            out.append(u)
    return out
