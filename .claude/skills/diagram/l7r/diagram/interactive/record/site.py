"""The record as a manual: a site with a navigation tree, and the whole record on one page (feature 301).

The GM, 2026-10-01: *"a single page version which gets automatically assembled and that single page version has all of
the research and all of the sources and all of the citations with a linkable table of contents at the very top. But
then it also gets assembled into a page structure where anything that would be a top-level table of contents entry
... will be its own separate parent section and then maybe each of our subsections are themselves individual pages
within the larger section, which are linked on the left"* - and the maps link *"to the smaller pages"*, with *"the one
giant page ... accessible ... in the navigation section to the left of the smaller individualized pages."*

What `make record` writes, under `research/site/` (gitignored; built on the main checkout by render-sync):

    index.html                   home: every part, grouped, and the single page
    <part>/index.html            a part (one page of the record): its opening, then its questions listed
    <part>/<heading id>.html     a small page: one question, its notes numbered from 1, the works they cite
    sources/<key>.html           one registry entry
    all.html                     the single page: contents, every part, the citations, the sources
    nav.js                       the navigation tree as data (`assets/site.js` draws it)
    assets/                      the record's stylesheets and scripts, and the derived glossary

Nothing is read back from what this writes, and nothing in the engine reads it: the fragments are the record. A link
that lands nowhere, an id used twice, a note nothing cites or a cited work with no write-up refuses the build, naming
the fragment (spec FR-006, FR-007).
"""

from __future__ import annotations

import html
import json
import os
import re
import shutil
import tempfile
from dataclasses import dataclass, field

from l7r.diagram.interactive.record import fragments as frag
from l7r.diagram.interactive.record import site_links as links
from l7r.diagram.interactive.record import site_notes as sn
from l7r.diagram.interactive.record.assemble import assemble
from l7r.diagram.interactive.record.notes import NoteError, Placed, render_note
from l7r.diagram.interactive.record.split import split
from l7r.diagram.interactive.record.store import RecordError, _cross_linked, entry_level, read_fragments, read_notes, record_pages
from l7r.diagram.interactive.sources import COLLECTIONS, RESEARCH_DIR, clear_caches, page_text, registry_entries

SITE = "site"
#: The assets the site carries, copied from `research/assets/` - the hand-written ones. The glossary is derived.
ASSETS = ("record.css", "record.js", "site.css", "site.js")
#: The groups the home page and the navigation list the parts in, by the collection a part belongs to.
GROUPS = (("", "Research"), ("cities", "Cities"), ("rendering", "How our maps draw it"), ("rendering/cities", "How our maps draw cities"))
REGISTRY_GROUP = "Sources"
TITLE = "The research record"
_H1 = re.compile(r'<h1 id="([^"]+)">(.*?)</h1>', re.S)
_HEAD = re.compile(r"<h([23]) id=\"([^\"]+)\">(.*?)</h\1>", re.S)
_MAIN = re.compile(r"<main>\s*", re.S)
_TRAILING_RULE = re.compile(r"\s*<hr>\s*$")
_P = re.compile(r"<p>(.*?)</p>", re.S)
_COMMENT = re.compile(r"<!--.*?-->", re.S)
_SENTENCE = re.compile(r"(.+?[.!?])(?:\s|$)", re.S)
#: What the assembly writes under a heading before the question's own opening: the "Not to be confused with:" list.
_CONFUSABLES = re.compile(r'<div class="confusables">.*?</div>', re.S)


@dataclass
class Item:
    """A question, or a registry entry: one small page."""

    id: str
    html: str
    title: str
    lead: str


@dataclass
class Group:
    """A section of the registry: its heading and opening, and its entries."""

    id: str
    html: str
    items: list[Item]


@dataclass
class Part:
    """One page of the record - a part of the manual."""

    page_rel: str
    dir: str
    title: str
    title_id: str
    intro: str
    items: list[Item] = field(default_factory=list)
    groups: list[Group] = field(default_factory=list)
    notes: dict[str, str] = field(default_factory=dict)

    @property
    def is_registry(self) -> bool:
        return self.page_rel == links.REGISTRY

    def all_items(self) -> list[Item]:
        return [i for g in self.groups for i in g.items] if self.is_registry else self.items


def _text(fragment: str) -> str:
    return page_text(_COMMENT.sub("", fragment))


def lead_of(section: str) -> str:
    """The first sentence of a section's first paragraph - the line a part's list shows under each question."""
    m = _P.search(_CONFUSABLES.sub("", _COMMENT.sub("", section)))
    if m is None:
        return ""
    text = _text(m.group(1))
    s = _SENTENCE.match(text)
    return s.group(1) if s else text


def _item(text: str, heading_id: str) -> Item:
    m = _HEAD.search(text)
    title = _text(re.sub(r'<span class="xref">.*?</span>', "", m.group(3), flags=re.S)) if m else heading_id
    return Item(id=heading_id, html=text, title=title, lead=lead_of(text))


def load_part(page_rel: str, record_dir: str) -> Part:
    """A page of the record, cross-linked as its assembly is, and taken apart into its small pages."""
    raw = _cross_linked(assemble(read_fragments(page_rel, record_dir)), page_rel, record_dir)
    page = split(raw, entry_level=entry_level(page_rel))
    front = page.front[_MAIN.search(page.front).end() :] if _MAIN.search(page.front) else page.front  # type: ignore[union-attr]
    h1 = _H1.search(front)
    if h1 is None:
        raise RecordError(f"{frag.page_dir(page_rel)}/{frag.FRONT}: no `<h1 id=...>` - a part needs its title")
    part = Part(
        page_rel=page_rel,
        dir=links.part_dir(page_rel),
        title=_text(h1.group(2)),
        title_id=h1.group(1),
        intro=_TRAILING_RULE.sub("", front[h1.end() :]).strip(),
        notes=read_notes(page_rel, record_dir),  # every question's notes file; none is an empty page of notes
    )
    for section in page.sections:
        if part.is_registry:
            part.groups.append(Group(id=section.id, html=section.text, items=[_item(e.text, e.id) for e in section.entries]))
        else:
            part.items.append(_item(section.text, section.id))
    return part


def load(record_dir: str = RESEARCH_DIR) -> list[Part]:
    """Every part, in the order the manual reads them: the research, the cities, how the maps draw it, the sources."""
    parts = [load_part(p, record_dir) for p in record_pages(record_dir)]
    order = {c: i for i, (c, _label) in enumerate(GROUPS)}

    def rank(p: Part) -> tuple[int, str]:
        if p.is_registry:
            return (len(GROUPS), p.dir)
        return (order[collection_of(p.page_rel)], p.dir)

    return sorted(parts, key=rank)


def collection_of(page_rel: str) -> str:
    """The collection a page is in: `` for a top-level page, `cities`, `rendering`, `rendering/cities`."""
    d = os.path.dirname(page_rel)
    return d if d in COLLECTIONS else ""


def build_index(parts: list[Part]) -> links.Index:
    """Every id in the record, and the ids the build refuses: a question's or entry's id used twice anywhere (FR-007),
    and any id used twice on the single page, which holds them all."""
    index = links.Index()
    seen: dict[str, str] = {}
    errors: list[str] = []

    def claim(found: str, where: str) -> None:
        if found in seen and seen[found] != where:
            errors.append(f"the id `{found}` is used in {seen[found]} and again in {where} - the single page holds both, and an id names one place")
        seen.setdefault(found, where)

    for part in parts:
        index.add_part(part.page_rel, part.dir, part.title_id)
        claim(part.title_id, f"{part.dir}/{frag.FRONT}")
        for found in links.ids_in(part.intro):
            claim(found, f"{part.dir}/{frag.FRONT}")
        index.add(part.page_rel, part.dir, None, part.intro)
        for group in part.groups:
            index.add(part.page_rel, part.dir, None, group.html)
            for found in links.ids_in(group.html):
                claim(found, f"{part.dir}/ group {group.id}")
        for item in part.all_items():
            index.add(part.page_rel, part.dir, item.id, item.html)
            for found in links.ids_in(item.html):
                claim(found, f"{part.dir}/ {item.id}")
    for reserved in ("contents", "citations", "record", "page-notes", "page-works"):
        if reserved in seen:
            errors.append(f"the id `{reserved}` (in {seen[reserved]}) is one the site's own pages use")
    if errors:
        raise RecordError("\n  ".join(["the record's ids collide:", *errors]))
    return index


# ------------------------------------------------------------------------------------------------- the page shell


def _root(here: str) -> str:
    """From a site file to the site root: `` for `index.html`, `../` for `fields/x.html`, `../../` deeper."""
    return "../" * here.count("/")


def shell(title: str, here: str, part: str, body: str, *, lazy_glossary: bool = False) -> str:
    """A site page: the head, the navigation the script draws, the content. `lazy_glossary` marks the single page, whose
    glossary hover `record.js` wraps a heading's run at a time as it nears the screen (research R8)."""
    root = _root(here)
    gl = f'<script src="{root}assets/glossary.js" defer></script>\n'
    return (
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{html.escape(title)}</title>\n"
        f'<link rel="stylesheet" href="{root}assets/record.css">\n<link rel="stylesheet" href="{root}assets/site.css">\n'
        f"{gl}"
        f'<script src="{root}nav.js" defer></script>\n<script src="{root}assets/site.js" defer></script>\n'
        f'<script src="{root}assets/record.js" defer></script>\n'
        "</head>\n"
        f'<body class="site" data-root="{root}" data-part="{html.escape(part)}" data-page="{html.escape(here)}"{" data-lazy-glossary" if lazy_glossary else ""}>\n'
        '<div class="layout">\n<nav id="sidebar" aria-label="Contents">'
        f'<noscript><p><a href="{root}index.html">Contents</a> - <a href="{root}all.html">the whole record on one page</a></p></noscript></nav>\n'
        f"<main>\n{body}\n</main>\n</div>\n</body>\n</html>\n"
    )


def _crumbs(part: Part, here: str) -> str:
    return f'<p class="crumbs"><a href="{_root(here)}index.html">{TITLE}</a> &rsaquo; <a href="index.html">{html.escape(part.title)}</a></p>\n'


def _as_title(item_html: str) -> str:
    """A question's own heading made the page's title: its first `<h2>`/`<h3>` becomes the `<h1>`."""
    m = _HEAD.search(item_html)
    if m is None:
        return item_html
    return item_html[: m.start()] + f'<h1 id="{m.group(2)}">{m.group(3)}</h1>' + item_html[m.end() :]


def _neighbors(items: list[Item], at: int) -> str:
    prev = f'<a rel="prev" href="{items[at - 1].id}.html">&lsaquo; {html.escape(items[at - 1].title)}</a>' if at > 0 else "<span></span>"
    nxt = f'<a rel="next" href="{items[at + 1].id}.html">{html.escape(items[at + 1].title)} &rsaquo;</a>' if at + 1 < len(items) else "<span></span>"
    return f'<nav class="pager">{prev}{nxt}</nav>\n'


# ------------------------------------------------------------------------------------------------- the build


class Build:
    """One build of the site: the files it writes, and every refusal it found, gathered so one run names them all."""

    def __init__(self, record_dir: str) -> None:
        self.record_dir = record_dir
        self.parts = load(record_dir)
        self.index = build_index(self.parts)
        self.entries = registry_entries(record_dir)
        self.files: dict[str, str] = {}
        self.errors: list[str] = []

    def rewrite(self, markup: str, part: Part, here: str, where: str, *, single: bool = False, from_dir: str | None = None) -> str:
        out, errs = links.rewrite(
            markup,
            page_rel=part.page_rel,
            from_dir=os.path.dirname(part.page_rel) if from_dir is None else from_dir,
            index=self.index,
            here=here,
            single=single,
            where=where,
        )
        self.errors += errs
        return out

    def run(self) -> dict[str, str]:
        for part in self.parts:
            self._part(part)
        self._home()
        self._single()
        self.files["nav.js"] = nav_js(self.parts)
        if self.errors:
            raise RecordError("\n  ".join([f"the site does not build ({len(self.errors)} refusal(s)):", *self.errors]))
        return self.files

    def _works(self, placed: list[Placed], part: Part, here: str, where: str) -> str:
        from l7r.diagram.interactive.citations import cited_keys, works_html  # noqa: PLC0415 - citations imports the record

        keys = cited_keys([(str(p.number), p.body) for p in placed])
        block, missing = works_html(keys, self.entries, "")
        self.errors += [f"{where}: cites `{k}`, whose registry entry has no write-up (`What it is:` and `Why it applies, and its limits:`)" for k in missing]
        return self.rewrite(block, part, here, where, from_dir="")

    def _notes_from(self, part: Part) -> str:
        """Where a page's notes were written: beside its citations page, one directory down (`../SOURCES.html#key`)."""
        return os.path.join("citations", os.path.dirname(part.page_rel)).rstrip("/")

    def _part(self, part: Part) -> None:
        """A part's small pages and its own page. The order matters: links are resolved while every `href` is still the
        record's (a numbered reference is an in-page `#fn-N`, and a key in a note becomes `#work-<key>`, neither of which
        is the record's), then the references are numbered, then the notes' keys turned to the works at the foot."""
        cited: set[str] = set()
        items = part.all_items()
        for at, item in enumerate(items):
            here = f"{part.dir}/{item.id}.html"
            where = f"{part.dir}/ {item.id}"
            try:
                body, placed = sn.small_page(self.rewrite(item.html, part, here, where), part.notes, where)
            except NoteError as e:
                self.errors.append(str(e))
                continue
            cited.update(p.key for p in placed)
            placed = [Placed(p.key, p.number, self.rewrite(p.body, part, here, where, from_dir=self._notes_from(part)), p.references) for p in placed]
            foot = sn.foot(placed, self._works(placed, part, here, where) if placed else "")
            content = _crumbs(part, here) + _as_title(body) + foot + _neighbors(items, at)
            self.files[here] = shell(f"{item.title} - {part.title}", here, part.dir, content)
        orphans = sorted(set(part.notes) - cited)
        if orphans:
            self.errors.append(f"{part.dir}/: {', '.join(orphans)} - defined as a note, referenced nowhere")
        here = f"{part.dir}/index.html"
        self.files[here] = shell(part.title, here, part.dir, self._part_page(part, here))

    def _listing(self, items: list[Item]) -> str:
        rows = []
        for item in items:
            lead = f' <span class="lead">{html.escape(item.lead)}</span>' if item.lead else ""
            rows.append(f'<li><a href="{item.id}.html">{html.escape(item.title)}</a>{lead}</li>')
        return '<ul class="questions">\n' + "\n".join(rows) + "\n</ul>\n"

    def _part_page(self, part: Part, here: str) -> str:
        top = f'<p class="crumbs"><a href="{_root(here)}index.html">{TITLE}</a></p>\n'
        intro = self.rewrite(part.intro, part, here, f"{part.dir}/{frag.FRONT}")
        body = f'{top}<h1 id="{part.title_id}">{html.escape(part.title)}</h1>\n{intro}\n'
        if part.is_registry:
            for group in part.groups:
                body += self.rewrite(group.html, part, here, f"{part.dir}/ group {group.id}") + self._listing(group.items)
        else:
            body += self._listing(part.items)
        return body

    def _home(self) -> None:
        body = [f'<h1 id="contents">{TITLE}</h1>', '<p><a href="all.html">The whole record on one page</a> - every question, every note and every source, under one table of contents.</p>']
        for label, parts in grouped(self.parts):
            body.append(f"<h2>{html.escape(label)}</h2>\n<ul>")
            body += [f'<li><a href="{p.dir}/index.html">{html.escape(p.title)}</a></li>' for p in parts]
            body.append("</ul>")
        self.files["index.html"] = shell(TITLE, "index.html", "", "\n".join(body))

    def _single(self) -> None:
        """The whole record on one page (FR-003, FR-005): contents, every part, the citations, the sources."""
        count = sn.Numbering()
        toc = ['<nav class="toc"><h2 id="contents">Contents</h2>\n<ul>']
        out: list[str] = []
        for label, parts in grouped(self.parts):
            toc.append(f"<li>{html.escape(label)}<ul>")
            for part in parts:
                toc.append(f'<li><a href="#{part.title_id}">{html.escape(part.title)}</a>')
                if not part.is_registry:
                    toc.append("<ul>" + "".join(f'<li><a href="#{i.id}">{html.escape(i.title)}</a></li>' for i in part.items) + "</ul>")
                toc.append("</li>")
                if part.is_registry:
                    continue
                out.append(f'<section class="part">\n<h1 id="{part.title_id}">{html.escape(part.title)}</h1>\n')
                out.append(self.rewrite(part.intro, part, "all.html", f"{part.dir}/{frag.FRONT}", single=True))
                for item in part.items:
                    where = f"{part.dir}/ {item.id}"
                    try:
                        out.append(count.number(self.rewrite(item.html, part, "all.html", where, single=True), part.page_rel, part.notes, where))
                    except NoteError as e:
                        self.errors.append(str(e))
                out.append("</section>\n")
            toc.append("</ul></li>")
        toc.append('<li><a href="#citations">Citations</a></li>')
        notes = []
        for page_rel, placed in count.placed:
            part = next(p for p in self.parts if p.page_rel == page_rel)
            body = self.rewrite(placed.body, part, "all.html", f"{part.dir}/ notes", single=True, from_dir=self._notes_from(part))
            notes.append(render_note(Placed(placed.key, placed.number, sn.keyed_to(body, "#"), 0), ""))
        out.append('<section class="part footnotes">\n<h1 id="citations">Citations</h1>\n<ol>\n' + "\n".join(notes) + "\n</ol></section>\n")
        registry = next((p for p in self.parts if p.is_registry), None)
        if registry is not None:
            toc.append(
                f'<li><a href="#{registry.title_id}">{html.escape(registry.title)}</a><ul>'
                + "".join(f'<li><a href="#{g.id}">{html.escape(_text(_HEAD.search(g.html).group(3)) if _HEAD.search(g.html) else g.id)}</a></li>' for g in registry.groups)
                + "</ul></li>"
            )
            out.append(f'<section class="part">\n<h1 id="{registry.title_id}">{html.escape(registry.title)}</h1>\n')
            out.append(self.rewrite(registry.intro, registry, "all.html", f"{registry.dir}/{frag.FRONT}", single=True))
            for group in registry.groups:
                out.append(self.rewrite(group.html, registry, "all.html", f"{registry.dir}/ group {group.id}", single=True))
                out += [self.rewrite(i.html, registry, "all.html", f"{registry.dir}/ {i.id}", single=True) for i in group.items]
            out.append("</section>\n")
        toc.append("</ul></nav>\n")
        head = f'<h1 id="record">{TITLE}</h1>\n<p><em>Every question the maps were researched from, every note behind them and every source they cite, on one page. The same record, a page per question: <a href="index.html">the contents</a>.</em></p>\n'
        self.files["all.html"] = shell(TITLE + " - the whole record", "all.html", "", head + "".join(toc) + "".join(out), lazy_glossary=True)


def grouped(parts: list[Part]) -> list[tuple[str, list[Part]]]:
    """The parts under the headings the home page and the navigation use, in the manual's order."""
    out: list[tuple[str, list[Part]]] = []
    for collection, label in GROUPS:
        mine = [p for p in parts if not p.is_registry and collection_of(p.page_rel) == collection]
        if mine:
            out.append((label, mine))
    registry = [p for p in parts if p.is_registry]
    if registry:
        out.append((REGISTRY_GROUP, registry))
    return out


def nav_js(parts: list[Part]) -> str:
    """The navigation tree, once, as data: every part with its small pages, read by `assets/site.js` on every page. A
    script rather than markup on each page because the registry alone has 920 entries (research R3), and a script
    rather than a fetch because the site is opened from disk (spec 211 D1's reason)."""
    tree = {
        "title": TITLE,
        "home": "index.html",
        "all": "all.html",
        "groups": [{"label": label, "parts": [{"dir": p.dir, "title": p.title, "items": [[i.title, f"{p.dir}/{i.id}.html"] for i in p.all_items()]} for p in mine]} for label, mine in grouped(parts)],
    }
    return "// DERIVED FILE - written by `make record` from the record's fragments (feature 301). Never edit here.\nwindow.RECORD_NAV = " + json.dumps(tree, ensure_ascii=False) + ";\n"


def build(record_dir: str = RESEARCH_DIR) -> dict[str, str]:
    """Every file of the site, by its path under `site/`. Raises `RecordError` naming every refusal."""
    from l7r.diagram.interactive.glossary import record_glossary_js  # noqa: PLC0415 - the glossary loads the map's assets

    clear_caches()
    files = Build(record_dir).run()
    files["assets/glossary.js"] = record_glossary_js()
    for name in ASSETS:
        with open(os.path.join(record_dir, "assets", name), encoding="utf-8") as fh:
            files[f"assets/{name}"] = fh.read()
    return files


def write(files: dict[str, str], out_dir: str) -> None:
    """Write the site to `out_dir` whole: built beside it and swapped in, so a reader never meets a half-written site
    and a page the record no longer has does not linger."""
    parent = os.path.dirname(os.path.abspath(out_dir))
    os.makedirs(parent, exist_ok=True)
    fresh = tempfile.mkdtemp(prefix=".site-", dir=parent)
    for rel, text in files.items():
        path = os.path.join(fresh, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
    os.chmod(fresh, 0o755)
    old = None
    if os.path.exists(out_dir):
        old = tempfile.mkdtemp(prefix=".site-old-", dir=parent)
        os.rmdir(old)
        os.replace(out_dir, old)
    os.replace(fresh, out_dir)
    if old is not None:
        shutil.rmtree(old)
