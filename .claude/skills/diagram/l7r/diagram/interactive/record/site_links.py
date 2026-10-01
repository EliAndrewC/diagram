"""Where a link in the record goes once the record is a site (features 301, 303).

A question's fragment, notes and originals are written in `questions/` and link from there (spec 303, plan D4):
another question's page as its file name (`0412-village-shrines.html#the-hall`, `0412-village-shrines.drawing.html`), an
id on the same page as `#id`, the registry as `../SOURCES.html#<key>`, an asset as `../assets/...`. The registry's own
fragments were written for `SOURCES.html` at the record's root. The site writes every page twice - its own small page,
and its anchor on the single page - so each `href` is resolved once, against the page it was written in, and written
for both. Nothing is guessed: every `id` is indexed, and a link that lands nowhere is a refusal naming the fragment
(spec 301 FR-006). A link in a session note (an HTML comment) is not a link and is left alone.
"""

from __future__ import annotations

import posixpath
import re
from dataclasses import dataclass

#: The registry's page, as a link names it, and its site directory.
REGISTRY = "SOURCES.html"
REGISTRY_DIR = "sources"
QUESTIONS = "questions"
#: Where a question's small page is, in the site - flat, so a regrouping moves no URL (spec 303 FR-004).
QUESTION_DIR = "q"
#: An id anywhere in a fragment, and a link or an image source in its markup.
_ID = re.compile(r'\bid="([^"]+)"')
_ATTR = re.compile(r'(<(?:a|img)\b[^>]*?\s(?:href|src)=")([^"]*)(")', re.S)
_COMMENT = re.compile(r"<!--.*?-->", re.S)
_SCHEME = re.compile(r"^[a-z][a-z0-9+.-]*:", re.I)


class LinkError(Exception):
    """A link that lands nowhere. Its message names where it was written and what it pointed at."""


@dataclass(frozen=True)
class Loc:
    """Where an anchor lives in the site: a question page (`kind` "q", `page` its heading id) or the registry (`kind`
    "source", `page` an entry's key, or None for the registry's own page), and the anchor (None for the top)."""

    kind: str
    page: str | None
    anchor: str | None = None


def ids_in(html: str) -> list[str]:
    """Every id in a piece of markup, outside session notes."""
    return _ID.findall(_COMMENT.sub("", html))


class Index:
    """Every id in the record, mapped to where it lives - built once, asked per link."""

    def __init__(self) -> None:
        self.files: dict[str, str] = {}  # question file name -> its page's heading id
        self.ids: dict[str, set[str]] = {}  # question file name -> the ids on its page
        self.registry: dict[str, str | None] = {}  # id on the registry -> the entry holding it (None: its own page)

    def add_page(self, file: str, heading_id: str, html: str) -> None:
        self.files[file] = heading_id
        self.ids[file] = set(ids_in(html)) | {heading_id}

    def add_registry(self, entry: str | None, html: str) -> None:
        for found in ids_in(html):
            self.registry.setdefault(found, entry)
        if entry is not None:
            self.registry[entry] = entry

    def resolve(self, href: str, own: str | None) -> Loc | str | None:
        """What `href` points at, written in the question page `own` (or, with `own` None, in the registry): a `Loc`; a
        path relative to the record for a file that is not a page (an asset); or None for a link that leaves the record
        (a URL with a scheme, `//host`). Raises `LinkError` for a link into the record that lands nowhere."""
        if not href or _SCHEME.match(href) or href.startswith("//"):
            return None
        path, _, anchor = href.partition("#")
        if not path:
            return self._registry(anchor, href) if own is None else self._question(own, anchor, href)
        target = posixpath.normpath(posixpath.join(QUESTIONS if own is not None else "", path))
        if target == REGISTRY:
            return self._registry(anchor, href)
        if target.startswith(QUESTIONS + "/"):
            return self._question(target[len(QUESTIONS) + 1 :], anchor, href)
        if target.endswith(".html"):
            raise LinkError(f"`{href}` - no such page in the record")
        return target + (f"#{anchor}" if anchor else "")

    def _question(self, file: str, anchor: str, href: str) -> Loc:
        if file not in self.files:
            raise LinkError(f"`{href}` - no question page {file}")
        heading = self.files[file]
        if anchor and anchor not in self.ids[file]:
            raise LinkError(f"`{href}` - no id `{anchor}` on {file}")
        return Loc("q", heading, anchor if anchor and anchor != heading else None)

    def _registry(self, anchor: str, href: str) -> Loc:
        if not anchor:
            return Loc("source", None)
        if anchor not in self.registry:
            raise LinkError(f"`{href}` - no id `{anchor}` on the registry")
        entry = self.registry[anchor]
        return Loc("source", entry, anchor if anchor != entry else None)


def site_file(loc: Loc) -> str:
    """The site file a place in the record is on."""
    if loc.kind == "q":
        return f"{QUESTION_DIR}/{loc.page}.html"
    return f"{REGISTRY_DIR}/{loc.page}.html" if loc.page is not None else f"{REGISTRY_DIR}/index.html"


def site_href(loc: Loc, here: str) -> str:
    """The link from the site file `here` (relative to the site root) to `loc` on the multi-page site."""
    rel = posixpath.relpath(site_file(loc), posixpath.dirname(here) or ".")
    return rel + (f"#{loc.anchor}" if loc.anchor else "")


def single_href(loc: Loc, registry_title: str) -> str:
    """The same link on the single page, where every page is an anchor."""
    return f"#{loc.anchor or loc.page or registry_title}"


def asset_href(target: str, here: str, site_dir: str = "site") -> str:
    """A file of the record that is not a page (`assets/record.css`), from the site file `here`."""
    path, _, anchor = target.partition("#")
    rel = posixpath.relpath(path, posixpath.dirname(posixpath.join(site_dir, here)))
    return rel + (f"#{anchor}" if anchor else "")


def rewrite(html: str, *, own: str | None, index: Index, here: str, single: bool, where: str, registry_title: str = "") -> tuple[str, list[str]]:
    """`html` with every link rewritten for one form: the small pages (`single=False`, `here` the file it is written
    to) or the single page. Returns the markup and the refusals, each naming `where` - the fragment the link is in.
    `own` is the question page the markup belongs to (None: the registry)."""
    errors: list[str] = []
    hidden = [(m.start(), m.end()) for m in _COMMENT.finditer(html)]

    def one(m: re.Match[str]) -> str:
        if any(a <= m.start() < b for a, b in hidden):
            return m.group(0)
        try:
            target = index.resolve(m.group(2), own)
        except LinkError as e:
            errors.append(f"{where}: {e}")
            return m.group(0)
        if target is None:
            return m.group(0)
        if isinstance(target, str):
            return m.group(1) + asset_href(target, "all.html" if single else here) + m.group(3)
        return m.group(1) + (single_href(target, registry_title) if single else site_href(target, here)) + m.group(3)

    return _ATTR.sub(one, html), errors
