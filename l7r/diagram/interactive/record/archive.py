"""The source archive, as the record build sees it (feature 309).

The GM, 2026-10-02: download a copy of every source the record cites - *"every webpage we cite and every pdf of every
academic paper"*, *"even things which seem at low risk of going away, like wikipedia pages"* - into the PRIVATE repository
`EliAndrewC/diagram-research`, as a hedge against pages going offline or moving, with *"backup links to the Github where
we check these in"*. A citation quotes a passage verbatim from a page the reader can open; a page that dies or is edited
under its quote leaves the footnote uncheckable, so a cited page with no archived copy is a defect the build refuses.

WHAT IS CITED is derived, never listed: every URL in a registry entry, its HTML comments included - a comment there is
where a session recorded the page it actually read the passage from (`READ <date> at <url>`, the `_pdf` behind a J-STAGE
article page, the PMC copy behind a DOI: 23 entries, plan review 2026-10-02) - and every URL a footnote in
`questions/*.notes.html` links, its comments excluded (there they are search trails and pages read and NOT cited). The
registry is not the whole list: spec-fidelity round 1 found about a dozen footnote URLs no entry carries. `scripts/record/archive.py`, which takes the copies, asks THIS module
what is cited and what a URL's id is, so the build and the archiver agree by construction.

THE MANIFEST is one JSON file per URL, `research/archive/<id[:2]>/<id>.json` (one file each, so two sessions archiving
different URLs never touch the same file - plan D3), holding the outcome and where the copy lies in the archive
repository. A source's page in the built site shows its archived-copy link from it (spec FR-010).
"""

from __future__ import annotations

import datetime
import glob
import hashlib
import html
import json
import os
import re
from dataclasses import dataclass, field

from l7r.diagram.interactive.record import store
from l7r.diagram.interactive.sources import QUESTIONS

#: Where the manifest lives, under the record.
ARCHIVE_DIR = "archive"
#: The FR-012 match of the GM's downloaded files to the keys they copy, beside the manifest.
GM_COPIES = "gm-copies.json"
#: A row's file, `<id[:2]>/<id>.json`: sharded by the id's first two hex digits so no directory holds more than a few
#: hundred rows as the manifest grows past 5,000 (GitHub lists only the first 1,000 entries of a directory - the GM asked
#: for a layout that stays browsable, 2026-10-02). The archive repository is sharded the same way.
ROW_GLOB = "[0-9a-f][0-9a-f]/[0-9a-f]*.json"
#: The archive repository. PRIVATE (the GM, 2026-10-02: *"for now I just want an archive"* - much of it is
#: copyrighted), so its links open for the GM and no one else.
REPO = "https://github.com/EliAndrewC/diagram-research"
#: A capture that could not be pushed counts as covered for this long, then the build refuses it (plan D5: the
#: same week as the page cache's age rule, `scripts/record/sources.py:MAX_AGE_DAYS`, so one feature's write-then-check
#: cycle never trips it and a host that never comes back does not hide a missing copy for long).
PENDING_DAYS = 7

#: Every outcome a row can carry (spec FR-001). The first three hold a copy; `partial` holds what the site served.
ARCHIVED = ("archived", "archived-earlier-snapshot", "archived-gm-copy")
OUTCOMES = (*ARCHIVED, "partial", "unreachable", "pending-upload")

_COMMENT = re.compile(r"<!--.*?-->", re.S)
_URL = re.compile(r"https?://[^\s<>\"']+")
_ENTRY = re.compile(r'<h3 id="([a-z0-9][a-z0-9-]*)">.*?</h3>\s*(.*?)(?=<h3 id=|<h2 id=|</main>|\Z)', re.S)


def clean(url: str) -> str:
    """A URL as it is cited: entity-unescaped (the record is HTML - `&amp;` in a query is `&`), its fragment dropped, and
    the punctuation a sentence puts after it trimmed - a closing parenthesis only where the URL did not open one, since
    `(https://.../Edo)` wraps a URL and `町屋_(商家)` is part of one (the rule of `scripts/record/check_bundle.py:url_of`)."""
    url = html.unescape(url).split("#")[0]
    while url.endswith((".", ",", ";", ":")) or (url.endswith(")") and url.count(")") > url.count("(")):
        url = url[:-1]
    return url


def url_id(url: str) -> str:
    """A cited URL's manifest id: the first 12 hex of the SHA-256 of the URL as cited (`clean`)."""
    return hashlib.sha256(clean(url).encode("utf-8")).hexdigest()[:12]


def urls_in(markup: str, comments: bool = False) -> list[str]:
    """Every URL in `markup`, in order and once each - those inside HTML comments only where `comments` is set."""
    out: list[str] = []
    for found in _URL.findall(markup if comments else _COMMENT.sub("", markup)):
        url = clean(found)
        if url not in out:
            out.append(url)
    return out


@dataclass
class Cited:
    """Who cites one URL: the registry keys and the notes files."""

    keys: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def cited(research_dir: str) -> dict[str, Cited]:
    """Every URL the record cites (spec FR-001), registry entries first, then the footnotes' own links."""
    out: dict[str, Cited] = {}
    for key, body in _ENTRY.findall(store.registry_html(research_dir)):
        for url in urls_in(body, comments=True):
            out.setdefault(url, Cited()).keys.append(key)
    for path in sorted(glob.glob(os.path.join(research_dir, QUESTIONS, "*.notes.html"))):
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        for url in urls_in(text):
            out.setdefault(url, Cited()).notes.append(os.path.basename(path))
    return out


def load(research_dir: str) -> dict[str, dict]:
    """The manifest: id -> row. Empty when the record has no `archive/` (a test's small record)."""
    rows = {}
    for path in sorted(glob.glob(os.path.join(research_dir, ARCHIVE_DIR, ROW_GLOB))):
        with open(path, encoding="utf-8") as fh:
            rows[os.path.basename(path)[:-5]] = json.load(fh)
    return rows


def covered(row: dict, today: datetime.date) -> bool:
    """A row answers for its URL: any outcome but a pending upload older than `PENDING_DAYS`."""
    if row.get("outcome") != "pending-upload":
        return row.get("outcome") in OUTCOMES
    return (today - datetime.date.fromisoformat(row["captured"][:10])).days <= PENDING_DAYS


def refusals(research_dir: str, today: datetime.date | None = None) -> list[str]:
    """One refusal per cited URL with no covering row (spec FR-007), each naming the command that archives it. A record
    with no `archive/` directory has no archive to hold it to (a test's small record); the real one always has it."""
    if not os.path.isdir(os.path.join(research_dir, ARCHIVE_DIR)):
        return []
    today = today or datetime.datetime.now(datetime.UTC).date()
    rows = load(research_dir)
    out = []
    for url, who in cited(research_dir).items():
        row = rows.get(url_id(url))
        if row is None or not covered(row, today):
            where = ", ".join(who.keys or who.notes)
            state = "no archived copy" if row is None else f"its upload pending since {row['captured'][:10]}"
            out.append(f"archive: {url} ({where}) has {state} - `make archive URL='{url}'` archives it (feature 309)")
    return out


def copy_link(row: dict) -> str:
    """Where a row's copy opens in the archive repository."""
    return f"{REPO}/tree/main/{row['path']}"


def entry_line(entry: str, rows: dict[str, dict]) -> str:
    """The archived-copy line under a registry entry's citation line, for every URL the entry cites (spec FR-010), its
    comments' included: a link to each copy with its capture date, the GM's downloaded copy where there is one, or a note
    that no copy could be archived. Empty where the entry cites no URL or the manifest holds none of them."""
    parts = []
    gm_seen: set[str] = set()
    for url in urls_in(entry, comments=True):
        row = rows.get(url_id(url))
        if row is None:
            continue
        date = row.get("captured", "")[:10]
        if row["outcome"] in (*ARCHIVED, "partial", "pending-upload") and row.get("path"):
            label = "partial copy" if row["outcome"] == "partial" else "copy"
            parts.append(f'<a href="{html.escape(copy_link(row))}" target="_blank" rel="noopener">archived {label}, {date}</a>')
        else:
            parts.append(f"no copy could be archived ({html.escape(row.get('reason', 'unreachable'))}, {date})")
        for gm in row.get("gm_copies", []):
            if gm in gm_seen:
                continue
            gm_seen.add(gm)
            parts.append(f'<a href="{html.escape(REPO)}/blob/main/{html.escape(gm)}" target="_blank" rel="noopener">the GM\'s downloaded copy</a>')
    if not parts:
        return ""
    return '<p class="archived"><em>Archived:</em> ' + "; ".join(parts) + " (private)</p>\n"
