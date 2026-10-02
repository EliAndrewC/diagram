"""What a modal's references rest on, read from the research record itself.

A class names the research entry it was written FROM (`FeatureClass.entry`: a file and one or more
quoted headings). Two things are read out of that pointer at page-write time, so a change to the
record reaches every modal without anyone re-typing anything into `classes.py`:

- **the QUESTIONS** (feature 180, GM 2026-09-05) - the headings of the sections the entry names, each
  with a link to that section of the research PAGE - since feature 194 (GM 2026-09-06) the record is HTML
  under `research/` and the link is local and relative, not GitHub. This is what the
  references modal shows: *"instead of listing individual sources on the references modal, we will
  list the questions which we asked and researched - those pages are themselves sourced with links,
  so a user who wants to follow through and read the original sources can do so."* The audience is
  a casual RPG enthusiast curious why the settlement looks the way it does, and they are not to be
  met with a wall of third-party works; the sources are one click further out, on the page that
  answers the question.
- **the SOURCES** (feature 134, GM 2026-08-28: "all of the things that say that there is no reference
  for them should at this point have a reference") - the `**Sources:**` keys those sections cite and
  the registry behind them (`research/sources/`). The page no longer shows these; the tests over the
  record still read them, to prove every entry cites and every source carries a URL where it can be
  read (constitution v2.13.0).
"""

from __future__ import annotations

import html
import os
import re
import unicodedata
from functools import cache

_HERE = os.path.dirname(os.path.abspath(__file__))
RESEARCH_DIR = os.path.normpath(os.path.join(_HERE, "..", "..", "..", "research"))

#: WHERE A QUESTION LINKS (feature 194, GM 2026-09-06: *"make the links on our HTML maps link to the files
#: locally rather than linking to the markdown on GitHub since the markdown on GitHub will no longer exist as
#: it has been replaced with HTML"*). Relative to the MAP's own page: every map and every legacy exhibit is
#: `pool/<tier>/<name>/<name>.html` (or `legacy-hand-authored-pool/...`), three levels under the skill root,
#: and `research/` is one level under it. Feature 180's GitHub URL (`RESEARCH_URL`) is retired with the
#: Markdown; a renamed heading still breaks an anchor on a page rendered before the rename (spec 180 D1),
#: and every pool page re-renders at each landing.
#: Since feature 301 (GM 2026-10-01: *"the links to our research from the interactive HTML maps should link to the
#: smaller pages, not link to the one giant page"*) a question links its own small page in the record's site, and since
#: feature 303 that page is `research/site/q/<heading id>.html` whatever section the question sits in, so a regrouping of
#: the record moves no map's link.
SITE_PAGES = "../../../research/site/"
#: Where a question's small page is, under `SITE_PAGES`.
QUESTION_PAGES = "q/"
#: Where the questions are, in the record (feature 303: one flat directory, one stem per question).
QUESTIONS = "questions"


def record_text(rel: str, research_dir: str = RESEARCH_DIR) -> str:
    """A page of the record as a reader would open it, read from its fragments (features 301, 303). `rel` is
    `SOURCES.html` (the registry, assembled) or `questions/<file>` (a question page, with its cross-link and its
    *Not to be confused with:* list written in). Nothing assembled is on disk, so every reader asks here. A name that is
    neither is read from its file, which is what a test's fixture record is; one that is not there is empty."""
    return _record_text(os.path.normpath(research_dir), rel)


@cache
def _record_text(research_dir: str, rel: str) -> str:
    from l7r.diagram.interactive.record import store  # noqa: PLC0415 - the record imports this module

    if rel == "SOURCES.html" and os.path.isdir(os.path.join(research_dir, store.REGISTRY_DIR)):
        return store.registry_html(research_dir)
    if rel.startswith(QUESTIONS + "/") and os.path.isfile(os.path.join(research_dir, rel)):
        record = store.load(research_dir)
        return store.page_html(record, record.by_file[rel[len(QUESTIONS) + 1 :]], research_dir)
    try:
        with open(os.path.join(research_dir, rel), encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return ""


def clear_caches() -> None:
    """Forget every page read so far - what a build calls first, so a fragment edited since the last read in this
    process is read again (a long-lived process, or a test that edits and builds twice)."""
    for f in (_record_text, _page_notes, registry, registry_entries):
        f.cache_clear()


_KEY = re.compile(r"`([a-z0-9][a-z0-9-]*)`")
#: A research question an entry names: its FRAGMENT (feature 301, GM 2026-10-01: a pointer names *"the source which
#: is fed into and used to generate that HTML page, because that is the canonical location of the research"*) -
#: since feature 303 `research/questions/NNNN-<slug>.html`, or `NNNN-<slug>.drawing.html` for how our maps draw it.
#: A path either names a fragment or does not.
ENTRY_FRAGMENT = re.compile(r"research/questions/(\d{4}-[^\s/,;)\"'`<>]+?(?:\.drawing)?\.html)")
#: A heading in a research PAGE (feature 194): its level, its id (the record's anchor) and its inner HTML.
_HEADING_TAG = re.compile(r"<h([1-6])(?:\s+id=\"([^\"]*)\")?[^>]*>(.*?)</h\1>", re.S)
_TAG = re.compile(r"<[^>]+>")
_CODE_KEY = re.compile(r"<code>([a-z0-9][a-z0-9-]*)</code>")
#: The bookkeeping a heading carries for the project, not for the reader: a trailing parenthetical with
#: a date in it - "(researched 2026-08-27, feature 133 T41)", "(accepted 2026-08-29, feature 152)",
#: "(feature 156, 2026-08-29)". Stripped from the question TEXT only (spec FR-005, D2); the anchor is
#: computed from the full heading, so the link still lands.
_DATED_TAIL = re.compile(r"\s*\([^()]*\b\d{4}-\d{2}-\d{2}\b[^()]*\)\s*$")
#: Markdown emphasis and code markers - what the record's headings carried before feature 194, and what a
#: class entry may still quote; the page's heading TEXT has none, so stripping them keeps the two comparable.
_MARKUP = re.compile(r"[*`]")


#: The link the assembly writes into a heading to its research or rendering counterpart (feature 292, `record/xref.py`)
#: - a way out of the section, not part of its title, so every reading of a heading's text drops it.
_XREF = re.compile(r'<span class="xref">.*?</span>', re.S)


def heading_text(heading: str) -> str:
    """The rendered text of a heading - what a reader sees and what the anchor rule slugs."""
    return _MARKUP.sub("", _XREF.sub("", heading)).strip()


def page_text(fragment: str) -> str:
    """The text of an HTML fragment: tags dropped, entities decoded, whitespace collapsed."""
    return re.sub(r"\s+", " ", html.unescape(_TAG.sub("", _XREF.sub("", fragment)))).strip()


def github_anchor(heading: str, seen: dict[str, int] | None = None) -> str:
    """THE RECORD'S ANCHOR for a heading - GitHub's rule (feature 180, spec FR-006), kept as the id rule when
    the record converted to HTML (feature 194) so every pointer that landed on GitHub lands on the page: the
    rendered text lowercased; every character that
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


def parse_sections(page: str) -> list[tuple[str, str, str]]:
    """(heading text, body html, id) for every `<h2>`/`<h3>` section of a research page's HTML, in page order (feature
    191: the record is HTML). The id is the page's own - `tests/interactive/test_record.py` proves it equals
    `github_anchor` of the text; a `<code>` span in a heading (the registry's keys) reads as its text, as GitHub's
    slugger read the backticks. A body runs to the next heading of ANY level; a `####` opens no section."""
    out: list[tuple[str, str, str]] = []
    heads = list(_HEADING_TAG.finditer(page))
    for i, m in enumerate(heads):
        if m.group(1) not in ("2", "3"):
            continue
        end = heads[i + 1].start() if i + 1 < len(heads) else len(page)
        out.append((page_text(m.group(3)), page[m.end() : end], m.group(2) or ""))
    return out


def section_sources(body: str) -> list[str]:
    """The SOURCES keys a section's `<p><strong>Sources:</strong> ...</p>` roster names (in order, deduplicated).
    Feature 194: the roster is one `<p>`, so the wrap that once lost keys (2026-08-29: a `**Sources:**` line read
    to end-of-LINE dropped every key past the first physical line) cannot recur."""
    m = re.search(r"<p><strong>Sources:</strong>(.*?)</p>", body, re.S)
    if not m:
        return []
    keys: list[str] = []
    for k in _CODE_KEY.findall(m.group(1)):
        if k not in keys:
            keys.append(k)
    return keys


_REFERENCE = re.compile(r'<sup class="fn" data-note="([^"]*)"></sup>')
_NOTE_KEY = re.compile(r'<a href="[^"]*"><code>([a-z0-9][a-z0-9-]*)</code></a>')


@cache
def _page_notes(research_dir: str, file: str) -> dict[str, str]:
    """note key -> note HTML for one question page (`record/store.page_notes`)."""
    from l7r.diagram.interactive.record.store import page_notes  # noqa: PLC0415 - the record imports this module

    return page_notes(file, research_dir)


def footnote_sources(fragment: str, file: str, research_dir: str = RESEARCH_DIR) -> list[str]:
    """The keys a question page's FOOTNOTES cite, in order of first citation, once each - the question's sources once it
    carries no `Sources:` roster (feature 292: the roster is retired from a restyled section, and every key it named
    had to be quoted by one of these footnotes anyway). A reference names its note by key, in the page's own notes."""
    notes = _page_notes(os.path.normpath(research_dir), file)
    keys: list[str] = []
    for ref in _REFERENCE.findall(fragment):
        for k in _NOTE_KEY.findall(notes.get(ref, "")):
            if k not in keys:
                keys.append(k)
    return keys


def entry_fragments(entry: str) -> list[str]:
    """The file name of every question page an entry names, in the order it names them (spec 180 D4: the class author
    puts the primary question first), once each."""
    out: list[str] = []
    for m in ENTRY_FRAGMENT.finditer(entry):
        if m.group(1) not in out:
            out.append(m.group(1))
    return out


def _fragment(research_dir: str, file: str) -> str | None:
    try:
        with open(os.path.join(research_dir, QUESTIONS, file), encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def research_sources(entry: str, research_dir: str = RESEARCH_DIR) -> list[str]:
    """Every key the research questions named in `entry` cite, in entry order: a section's roster where it has one,
    else the keys its footnotes cite."""
    keys: list[str] = []
    for file in entry_fragments(entry):
        text = _fragment(research_dir, file)
        if text is None:
            continue
        for k in section_sources(text) or footnote_sources(text, file, research_dir):
            if k not in keys:
                keys.append(k)
    return keys


def research_questions(entry: str, research_dir: str = RESEARCH_DIR) -> list[dict[str, str]]:
    """The QUESTIONS behind a modal (feature 180): `{"text", "url"}` for every research question the entry names, in
    the order the ENTRY names them. `text` is the heading less its dated bookkeeping; `url` is the question's small
    page in the record's site (features 301, 303). A path that names no fragment yields nothing - which
    `scripts/check-entry-headings.py` refuses at the push."""
    out: list[dict[str, str]] = []
    for file in entry_fragments(entry):
        text = _fragment(research_dir, file)
        m = _HEADING_TAG.search(re.sub(r"<!--.*?-->", "", text or "", flags=re.S))
        if m is None:
            continue
        heading_id = m.group(2) or ""
        out.append({"text": question_text(page_text(m.group(3))), "url": f"{SITE_PAGES}{QUESTION_PAGES}{heading_id}.html"})
    return out


@cache
def registry(research_dir: str = RESEARCH_DIR) -> dict[str, str]:
    """key -> the SOURCES.html entry text (the citation line and its 'Used for' line, as text)."""
    out: dict[str, str] = {}
    for heading, body, _id in parse_sections(record_text("SOURCES.html", research_dir)):
        m = re.fullmatch(r"[a-z0-9][a-z0-9-]*", heading.strip())
        if not m:
            continue
        paras = [page_text(p) for p in re.findall(r"<p>(.*?)</p>", body, re.S)]
        out[m.group(0)] = " | ".join(p for p in paras if p)
    return out


_URL = re.compile(r"https?://[^\s)\]>]+")

# ---- feature 190: where a key LINKS - the classifier, one body (feature 211 moved it here from
# tests/interactive/test_sources.py, because `make citations` derives the works section of every citations page
# with it and a tool under l7r/ does not import from tests/; the test imports these three from here) ----------
#: A registry entry: its key and everything up to the next entry.
_ENTRY_BLOCK = re.compile(r'<h3 id="([a-z0-9][a-z0-9-]*)">.*?</h3>\s*(.*?)(?=<h3 id=|<h2 id=|</main>)', re.S)
_FIRST_P = re.compile(r"<p>(.*?)</p>", re.S)
_CITE_URL = re.compile(r"https?://[^\s<>\"]+")
_COMMENT = re.compile(r"<!--(.*?)-->", re.S)
#: The two write-ups a registry entry carries since feature 211 (GM 2026-09-07: what the work is, and why it is a
#: good and valid source for what we look up in it, with its honest limitations), as `<p><em>label</em> ...</p>`.
WHAT_LABEL = "What it is:"
WHY_LABEL = "Why it applies, and its limits:"
USED_LABEL = "Used for:"


def _line_text(fragment: str) -> str:
    """The citation line's text WITH its comments' text: since feature 209 the verification markers the classifier
    reads (READ, SUMMARY-ONLY, unfetched, the feature and task) live in an HTML comment inside the citation
    paragraph, hidden from the reader (GM 2026-09-07: a note for a session is an HTML comment) and still the rule's
    input here. The first URL on the line still governs, and a READ-at comment placed first carries it."""
    return html.unescape(_TAG.sub("", _COMMENT.sub(r" \1 ", fragment)))


def citation_lines(sources_html: str) -> dict[str, str]:
    """key -> the entry's citation line (its first paragraph, as text)."""
    return {m.group(1): _line_text(_FIRST_P.search(m.group(2)).group(1)) for m in _ENTRY_BLOCK.finditer(sources_html) if _FIRST_P.search(m.group(2))}


def not_read(cite: str) -> bool:
    """The record says the document was NOT read: SUMMARY-ONLY, `URL: none`, or the URL recorded as
    unfetched with no READ beside it (feature 143's re-sourcing pass recorded addresses it did not fetch).
    Where a line says both (`artic-pigsty-latrine`: the text READ through the museum's API, the page
    itself unfetched) the READ governs - the GM's qualifier is "which we were able to read"."""
    if "SUMMARY-ONLY" in cite or "URL: none" in cite:
        return True
    return bool(re.search(r"unfetched|not fetched", cite)) and "READ" not in cite


def link_target(key: str, cite: str, rel: str) -> str:
    """Where a citation of `key` links: the document's URL (the FIRST on the citation line, spec 190 D2; a URL that
    carries parentheses keeps them - the defect of 2026-09-06) when it was read, else the registry entry that
    says it was not (`rel` is '' from research/, '../' from cities/ and citations/, '../../' from citations/cities/)."""
    m = _CITE_URL.search(cite)
    if not_read(cite) or m is None:
        return f"{rel}SOURCES.html#{key}"
    u = m.group(0).rstrip(".,;:")
    while u.endswith(")") and u.count(")") > u.count("("):
        u = u[:-1]
    return u


#: Where a bare URL may stand in a fragment of markup: outside every tag and comment, and outside a link's text.
_MARKUP_PART = re.compile(r"(<!--.*?-->|<a\b[^>]*>.*?</a>|<[^>]+>)", re.S)


def _url_end(u: str) -> str:
    """A URL as a sentence leaves it, trimmed of the punctuation after it and of a closing parenthesis it did not open
    (the rule `link_target` follows)."""
    u = u.rstrip(".,;:")
    while u.endswith(")") and u.count(")") > u.count("("):
        u = u[:-1].rstrip(".,;:")
    return u


def linkify(fragment: str) -> str:
    """Every bare URL in `fragment` made a link to itself that opens in a new tab (feature 307, GM 2026-10-02: *"when we
    display a URL, it should become a link ... that would open the source in a new tab"*), done by the build so nothing
    is typed into the registry. A URL already inside a link, a tag or a comment is left as it is."""

    def text(part: str) -> str:
        out, at = [], 0
        for m in _CITE_URL.finditer(part):
            u = _url_end(m.group(0))
            out.append(part[at : m.start()] + f'<a href="{u}" target="_blank" rel="noopener">{u}</a>')
            at = m.start() + len(u)
        return "".join(out) + part[at:]

    return "".join(p if i % 2 else text(p) for i, p in enumerate(_MARKUP_PART.split(fragment)))


def _labeled(body: str, label: str) -> str:
    """The inner HTML of the entry's `<p><em>label</em> ...</p>` paragraph, '' when it has none."""
    m = re.search(r"<p><em>" + re.escape(label) + r"</em>\s*(.*?)</p>", body, re.S)
    return m.group(1).strip() if m else ""


@cache
def registry_entries(research_dir: str = RESEARCH_DIR) -> dict[str, dict[str, str]]:
    """key -> the parts of its SOURCES.html entry (feature 211): `cite` (the citation line's inner HTML, comments
    dropped - the reader's line, naming the work and its authors), `line` (the same as text WITH comment text, the
    classifier's input), `what` and `why` (the two write-ups' inner HTML, '' when not yet written), `used`."""
    src = record_text("SOURCES.html", research_dir)
    out: dict[str, dict[str, str]] = {}
    for m in _ENTRY_BLOCK.finditer(src):
        body = m.group(2)
        first = _FIRST_P.search(body)
        cite = first.group(1) if first else ""
        out[m.group(1)] = {
            "cite": re.sub(r"\s+", " ", _COMMENT.sub("", cite)).strip(),
            "line": _line_text(cite),
            "what": _labeled(body, WHAT_LABEL),
            "why": _labeled(body, WHY_LABEL),
            "used": _labeled(body, USED_LABEL),
        }
    return out


#: A registry entry's key and its first paragraph - the citation line, which says what the work is.
_ENTRY_HEAD = re.compile(r'<h3 id="([a-z0-9][a-z0-9-]*)">.*?</h3>\s*<p>(.*?)</p>', re.S)
#: The GM's own campaign notes, named on a citation line. Canon rather than evidence, so a footnote citing one
#: links the registry entry instead of a public page - the GM's ruling of 2026-09-07 ("it is correct to make L7R
#: setting notes an exception to the citation rule"). DERIVED from the registry rather than listed, so a new
#: canon key is covered the day it lands.
_CANON_FILE = re.compile(r"\bl7r\.md\b|\bbudgets\.md\b")


def registry_keys(research_dir: str = RESEARCH_DIR) -> set[str]:
    """Every key the registry defines."""
    return set(re.findall(r'<h3 id="([a-z0-9][a-z0-9-]*)"', record_text("SOURCES.html", research_dir)))


def canon_keys(research_dir: str = RESEARCH_DIR) -> set[str]:
    """The keys whose source is the GM's own campaign notes."""
    src = record_text("SOURCES.html", research_dir)
    return {m.group(1) for m in _ENTRY_HEAD.finditer(src) if _CANON_FILE.search(m.group(2))}


def urls_of(text: str) -> list[str]:
    """Every URL a SOURCES.html entry carries (GM 2026-08-28: a source records where it can be read);
    the trailing punctuation a sentence leaves on a URL is trimmed."""
    out: list[str] = []
    for u in _URL.findall(text):
        u = u.rstrip(".,;:")
        if u not in out:
            out.append(u)
    return out
