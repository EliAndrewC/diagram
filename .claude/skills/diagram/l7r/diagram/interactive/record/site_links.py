"""Where a link in the record goes once the record is a site (feature 301).

A fragment's links were written for the PAGE it assembled into: `water.html#reservoir-ponds-tameike` from
`fields.html`, `../SOURCES.html#key` from a citations page, `assets/record.css`. The site splits every page into
small pages and also joins them all into one, so the same `href` has to land in two places: the small page of the
question that holds the anchor, and the anchor itself on the single page. Nothing is guessed: every `id` in the
record is indexed once, an `href` is resolved against the page it was written for, and one that resolves to nothing
is a refusal naming the fragment (spec FR-006). A link in a session note (an HTML comment) is not a link and is left
alone.
"""

from __future__ import annotations

import os
import posixpath
import re
from dataclasses import dataclass

#: The registry's page and its fragment directory.
REGISTRY = "SOURCES.html"
REGISTRY_DIR = "sources"
#: An id anywhere in a fragment, and a link or an image source in its markup.
_ID = re.compile(r'\bid="([^"]+)"')
_ATTR = re.compile(r'(<(?:a|img)\b[^>]*?\s(?:href|src)=")([^"]*)(")', re.S)
_COMMENT = re.compile(r"<!--.*?-->", re.S)
_SCHEME = re.compile(r"^[a-z][a-z0-9+.-]*:", re.I)
_FRAGMENT_NAME = re.compile(r"^\d{3,4}-(.+)\.html$")


class LinkError(Exception):
    """A link that lands nowhere. Its message names where it was written and what it pointed at."""


@dataclass(frozen=True)
class Loc:
    """Where an anchor lives in the site: the part (a page's directory), the small page holding it (a question's or a
    registry entry's id, or None for the part's own page), and the anchor itself (None for the top of the page)."""

    part: str
    page: str | None
    anchor: str | None = None


def ids_in(html: str) -> list[str]:
    """Every id in a piece of markup, outside session notes."""
    return _ID.findall(_COMMENT.sub("", html))


class Index:
    """Every id in the record, mapped to where it lives - built once, asked per link."""

    def __init__(self) -> None:
        self.ids: dict[tuple[str, str], Loc] = {}
        self.parts: dict[str, str] = {}  # page_rel -> part dir
        self.pages: dict[tuple[str, str], str] = {}  # (part dir, small page id) -> its file name in the site
        self.part_ids: dict[str, str] = {}  # part dir -> the id of its title (the single page's anchor for it)

    def add_part(self, page_rel: str, part: str, title_id: str) -> None:
        self.parts[page_rel] = part
        self.part_ids[part] = title_id
        self.ids[(page_rel, title_id)] = Loc(part, None)

    def add(self, page_rel: str, part: str, page: str | None, html: str) -> None:
        """Index every id in `html` as living on `page` of `part` (None: on the part's own page)."""
        for found in ids_in(html):
            self.ids.setdefault((page_rel, found), Loc(part, page, None if found == page else found))
        if page is not None:
            self.pages[(part, page)] = f"{page}.html"

    def resolve(self, href: str, from_dir: str) -> Loc | str | None:
        """What `href`, written in a page that sat in `from_dir` (relative to the record), points at: a `Loc` in the
        record; a path relative to the record for a file that is not a page (an asset); or None for a link that leaves
        the record untouched (a URL with a scheme, `//host`). Raises `LinkError` for a link into the record that lands
        nowhere."""
        if not href or _SCHEME.match(href) or href.startswith("//"):
            return None
        path, _, anchor = href.partition("#")
        if not path:
            raise LinkError(f"`{href}` - an in-page anchor, which the caller resolves against its own page")
        target = posixpath.normpath(posixpath.join(from_dir, path))
        if target.startswith("citations/"):
            return self._citations(target[len("citations/") :], anchor, href)
        if target in self.parts:
            return self._on_page(target, anchor, href)
        part = posixpath.dirname(target)
        named = _FRAGMENT_NAME.match(posixpath.basename(target))
        if named and part in self.part_ids:
            return self._fragment(part, named.group(1), anchor, href)
        return target + (f"#{anchor}" if anchor else "")

    def anchor(self, page_rel: str, anchor: str, href: str) -> Loc:
        """An in-page anchor (`#x`) written in `page_rel`."""
        return self._on_page(page_rel, anchor, href)

    def _on_page(self, page_rel: str, anchor: str, href: str) -> Loc:
        if not anchor:
            return Loc(self.parts[page_rel], None)
        loc = self.ids.get((page_rel, anchor))
        if loc is None:
            raise LinkError(f"`{href}` - no id `{anchor}` on {page_rel}")
        return loc

    def _citations(self, page_rel: str, anchor: str, href: str) -> Loc:
        """A citations page is not a page of the site: its works entries are the registry's entries, and the page
        itself is its research page's part."""
        if page_rel not in self.parts:
            raise LinkError(f"`{href}` - no research page {page_rel} behind this citations page")
        if anchor.startswith("work-"):
            return self._on_page(REGISTRY, anchor[len("work-") :], href)
        if anchor:
            raise LinkError(f"`{href}` - a citations page's note is not addressable in the site; link its question")
        return Loc(self.parts[page_rel], None)

    def _fragment(self, part: str, page_id: str, anchor: str, href: str) -> Loc:
        if (part, page_id) not in self.pages:
            raise LinkError(f"`{href}` - no question `{page_id}` in {part}/")
        return Loc(part, page_id, anchor or None)


def site_href(loc: Loc, here: str) -> str:
    """The link from the site file `here` (relative to the site root) to `loc` on the multi-page site."""
    file = f"{loc.part}/{loc.page}.html" if loc.page is not None else f"{loc.part}/index.html"
    rel = posixpath.relpath(file, posixpath.dirname(here) or ".")
    return rel + (f"#{loc.anchor}" if loc.anchor else "")


def single_href(loc: Loc, index: Index) -> str:
    """The same link on the single page, where every page is an anchor."""
    if loc.anchor:
        return f"#{loc.anchor}"
    return f"#{loc.page}" if loc.page is not None else f"#{index.part_ids[loc.part]}"


def asset_href(target: str, here: str, site_dir: str = "site") -> str:
    """A file of the record that is not a page (`assets/record.css`), from the site file `here`."""
    path, _, anchor = target.partition("#")
    rel = posixpath.relpath(path, posixpath.dirname(posixpath.join(site_dir, here)))
    return rel + (f"#{anchor}" if anchor else "")


def rewrite(html: str, *, page_rel: str, from_dir: str, index: Index, here: str, single: bool, where: str) -> tuple[str, list[str]]:
    """`html` with every link rewritten for one form: the small pages (`single=False`, `here` the file it is written
    to) or the single page. Returns the markup and the refusals, each naming `where` - the fragment the link is in.
    `page_rel` is the page an in-page anchor (`#x`) belongs to; `from_dir` is the directory the markup was written
    for (a citations page's notes were written one level down, in `citations/`)."""
    errors: list[str] = []
    hidden = [(m.start(), m.end()) for m in _COMMENT.finditer(html)]

    def one(m: re.Match[str]) -> str:
        if any(a <= m.start() < b for a, b in hidden):
            return m.group(0)
        href = m.group(2)
        try:
            target = index.anchor(page_rel, href[1:], href) if href.startswith("#") else index.resolve(href, from_dir)
        except LinkError as e:
            errors.append(f"{where}: {e}")
            return m.group(0)
        if target is None:
            return m.group(0)
        return m.group(1) + _href_for(target, index, here, single) + m.group(3)

    return _ATTR.sub(one, html), errors


def _href_for(target: Loc | str, index: Index, here: str, single: bool) -> str:
    """A resolved target as an `href` in one form: an asset is rebased; a place in the record is its small page, or its
    anchor on the single page."""
    if isinstance(target, str):
        return asset_href(target, "all.html" if single else here)
    return single_href(target, index) if single else site_href(target, here)


def part_dir(page_rel: str) -> str:
    """The site directory of a page - its fragment directory (`fields`, `cities/fabric`, `sources`)."""
    return REGISTRY_DIR if page_rel == REGISTRY else os.path.splitext(page_rel)[0]
