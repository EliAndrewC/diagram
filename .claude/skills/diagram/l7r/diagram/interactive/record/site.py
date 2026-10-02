"""The record as a manual: a site with a navigation tree, and the whole record on one page (features 301, 303).

The GM, 2026-10-01 (feature 301): *"a single page version which gets automatically assembled and that single page
version has all of the research and all of the sources and all of the citations with a linkable table of contents at
the very top"*, and a page structure with the sections *"linked on the left"*. And (feature 303) the sections are not
the directories the questions happened to sit in: they are `research/contents.json`, the questions are homed and
ordered by their tags (`record/contents.py`, `record/questions.py`), and the research and how our maps draw it are two
halves with the one structure.

What `make record` writes, under `research/site/` (gitignored; built on the main checkout by render-sync), is listed in
`site_pages.py`. Nothing is read back from what this writes, and nothing in the engine reads it: the fragments are the
record. A link that lands nowhere, an id used twice, a note nothing cites, a cited work with no write-up or a work whose
tags are missing or no section takes refuses the build, naming the fragment. The works stand under the sections their
tags put them in, each with its labels (feature 305, `source_tags.py`).
"""

from __future__ import annotations

import html
import os
import re
import shutil
import tempfile

from l7r.diagram.interactive.record import contents as ct
from l7r.diagram.interactive.record import questions as qs
from l7r.diagram.interactive.record import site_links as links
from l7r.diagram.interactive.record import site_notes as sn
from l7r.diagram.interactive.record import site_pages as sp
from l7r.diagram.interactive.record import source_tags as st
from l7r.diagram.interactive.record import store
from l7r.diagram.interactive.record.notes import NoteError, Placed, render_note
from l7r.diagram.interactive.record.split import split
from l7r.diagram.interactive.record.store import RecordError
from l7r.diagram.interactive.sources import RESEARCH_DIR, canon_keys, clear_caches, linkify, page_text, registry_entries

SITE = "site"
#: The assets the site carries, copied from `research/assets/` - the hand-written ones. The glossary is derived.
ASSETS = ("record.css", "record.js", "site.css", "site.js", "theme.js")
TITLE = sp.TITLE
_H1 = re.compile(r'<h1 id="([^"]+)">(.*?)</h1>', re.S)
_HEAD = re.compile(r"<h([23]) id=\"([^\"]+)\">(.*?)</h\1>", re.S)
#: A registry entry's heading, which the one-page record sets a level below its works section's.
_ENTRY_H3 = re.compile(r"<h3( id=\"[^\"]+\">.*?)</h3>", re.S)
_HEADING_END = re.compile(r"</h[1-4]>")
_FIRST_P = re.compile(r"<p>.*?</p>", re.S)
_MAIN = re.compile(r"<main>\s*", re.S)
_TRAILING_RULE = re.compile(r"\s*<hr>\s*$")
_P = re.compile(r"<p>(.*?)</p>", re.S)
_COMMENT = re.compile(r"<!--.*?-->", re.S)
_SENTENCE = re.compile(r"(.+?[.!?])(?:\s|$)", re.S)
#: What the assembly writes under a heading before the question's own opening: the "Not to be confused with:" list.
_CONFUSABLES = re.compile(r'<div class="confusables">.*?</div>', re.S)
#: A citation line of the GM's campaign notes - its lead, then the sections and URLs, then its session note - and in it
#: each parenthesized URL, and the comma or `and` that joins one section to the next (`canon_list`).
_CANON_LINE = re.compile(r"<p>(The GM's campaign notes, <code>[^<]+</code>), (.*?)(<!--.*?-->)?</p>", re.S)
_PAREN_URL = re.compile(r"\((https?://[^\s()]+)\)")
_JOIN = re.compile(r"^\s*(?:,\s*)?(?:and\s+)?")
#: Ids the site's own pages use, which no fragment may.
RESERVED = ("contents", "citations", "record", "page-notes", "page-works", "tags", *(h for h, _ in sp.HALVES))


def _text(fragment: str) -> str:
    return page_text(_COMMENT.sub("", fragment))


def lead_of(section: str) -> str:
    """The first sentence of a section's first paragraph - the line a listing shows under each question."""
    m = _P.search(_CONFUSABLES.sub("", _COMMENT.sub("", section)))
    if m is None:
        return ""
    text = _text(m.group(1))
    s = _SENTENCE.match(text)
    return s.group(1) if s else text


def canon_list(line: str) -> str:
    """A citation line naming two or more sections of the GM's campaign notes, as a bulleted list (GM 2026-10-02: *"when
    my campaign notes include a list of different sections ... then it should be listed as a bulleted list, for
    legibility"*): the line's lead and the whole file's URL, then a bullet per section with its URL. The registry keeps the
    one line - `The GM's campaign notes, <code>file</code>, "Heading" (url), ... and "Heading" (url) (file url)` - and the
    build lists it, so every entry written in that form is listed. Any other line, or one naming a single section, is
    returned as it is."""
    m = _CANON_LINE.fullmatch(line.strip())
    if m is None:
        return line
    lead, rest, comment = m.group(1), m.group(2), m.group(3) or ""
    items: list[str] = []
    whole = ""
    at = 0
    for u in _PAREN_URL.finditer(rest):
        name = _JOIN.sub("", rest[at : u.start()]).strip()
        if name:
            items.append(f"{name} ({u.group(1)})")
        else:
            whole = u.group(1)
        at = u.end()
    if rest[at:].strip() or len(items) < 2:
        return line
    head = f"<p>{lead}" + (f" ({whole})" if whole else "") + f":{comment}</p>"
    return head + '\n<ul class="canon-sections">\n' + "".join(f"<li>{i}</li>\n" for i in items) + "</ul>"


def _item(text: str, heading_id: str, page: qs.Page | None = None) -> sp.Item:
    m = _HEAD.search(text)
    title = _text(re.sub(r'<span class="xref">.*?</span>', "", m.group(3), flags=re.S)) if m else heading_id
    return sp.Item(id=heading_id, html=text, title=title, lead=lead_of(text), page=page)


class Registry:
    """The registry, taken apart into its groups and their entries."""

    def __init__(self, record_dir: str) -> None:
        page = split(store.registry_html(record_dir), entry_level=store.ENTRY_LEVEL)
        front = page.front[_MAIN.search(page.front).end() :] if _MAIN.search(page.front) else page.front  # type: ignore[union-attr]
        h1 = _H1.search(front)
        if h1 is None:
            raise RecordError(f"{store.REGISTRY_DIR}/_front.html: no `<h1 id=...>` - the registry needs its title")
        self.title, self.title_id = _text(h1.group(2)), h1.group(1)
        self.intro = _TRAILING_RULE.sub("", front[h1.end() :]).strip()
        self.groups = [(s.id, s.text, [_item(e.text, e.id) for e in s.entries]) for s in page.sections]

    def items(self) -> list[sp.Item]:
        return [i for _g, _h, items in self.groups for i in items]


def build_index(items: dict[str, sp.Item], registry: Registry, section_ids: tuple[str, ...] = ()) -> links.Index:
    """Every id in the record, and the ids the build refuses: one used twice anywhere, because the single page holds
    them all (feature 301 FR-007), or one the site's own pages use."""
    index = links.Index()
    seen: dict[str, str] = {}
    errors: list[str] = []

    def claim(found: str, where: str) -> None:
        if found in seen and seen[found] != where:
            errors.append(f"the id `{found}` is used in {seen[found]} and again in {where} - the single page holds both, and an id names one place")
        seen.setdefault(found, where)

    for file, item in items.items():
        index.add_page(file, item.id, item.html)
        for found in [item.id, *links.ids_in(item.html)]:
            claim(found, f"{qs.QUESTIONS}/{file}")
    index.add_registry(None, registry.intro)
    claim(registry.title_id, f"{store.REGISTRY_DIR}/_front.html")
    for gid, ghtml, gitems in registry.groups:
        index.add_registry(None, ghtml)
        for found in links.ids_in(ghtml):
            claim(found, f"{store.REGISTRY_DIR}/ group {gid}")
        for item in gitems:
            index.add_registry(item.id, item.html)
            for found in [item.id, *links.ids_in(item.html)]:
                claim(found, f"{store.REGISTRY_DIR}/ {item.id}")
    for sid in section_ids:
        claim(sid, st.SECTIONS)
    for reserved in RESERVED:
        if reserved in seen:
            errors.append(f"the id `{reserved}` (in {seen[reserved]}) is one the site's own pages use")
    if errors:
        raise RecordError("\n  ".join(["the record's ids collide:", *errors]))
    return index


def _as_title(item_html: str) -> str:
    """A question's own heading made the page's title: its first `<h2>`/`<h3>` becomes the `<h1>`."""
    m = _HEAD.search(item_html)
    if m is None:
        return item_html
    return item_html[: m.start()] + f'<h1 id="{m.group(2)}">{m.group(3)}</h1>' + item_html[m.end() :]


class Build:
    """One build of the site: the files it writes, and every refusal it found, gathered so one run names them all."""

    def __init__(self, record_dir: str) -> None:
        self.record_dir = record_dir
        self.record = store.load(record_dir)
        self.items = {p.file: _item(store.page_html(self.record, p, record_dir), p.heading_id, p) for p in self.record.pages()}
        self.registry = Registry(record_dir)
        try:
            self.catalog = st.Catalog(record_dir, {i.id: i.html for i in self.registry.items()}, canon_keys(record_dir), store.REGISTRY_DIR)
        except st.SourceTagError as e:
            raise RecordError(str(e)) from None
        self.index = build_index(self.items, self.registry, tuple(self.catalog.anchors()))
        for half, _ in sp.HALVES:
            for section in ct.walk(self.record.sections):
                if self.record.holds(section, half):
                    self.index.add_section(section.id, half)
        self.entries = registry_entries(record_dir)
        self.notes: dict[str, dict[str, str]] = {}
        self.files: dict[str, str] = {}
        self.errors: list[str] = list(self.catalog.errors)

    def rewrite(self, markup: str, own: str | None, here: str, where: str, *, single: bool = False) -> str:
        out, errs = links.rewrite(markup, own=own, index=self.index, here=here, single=single, where=where, registry_title=self.registry.title_id)
        self.errors += errs
        return out

    def notes_of(self, page: qs.Page) -> dict[str, str]:
        if page.file not in self.notes:
            try:
                self.notes[page.file] = store.page_notes(page.file, self.record_dir)
            except RecordError as e:
                self.errors.append(str(e))
                self.notes[page.file] = {}
        return self.notes[page.file]

    def run(self) -> dict[str, str]:
        for half, _label in sp.HALVES:
            for section in ct.walk(self.record.sections):
                if self.record.holds(section, half):
                    self._section(half, section)
        self._tags()
        self._registry()
        self._home()
        self._single()
        self.files["nav.js"] = sp.nav_js(sp.nav_tree(self.record, self.items, self.source_nodes()))
        if self.errors:
            raise RecordError("\n  ".join([f"the site does not build ({len(self.errors)} refusal(s)):", *self.errors]))
        return self.files

    def section_items(self, section: ct.Section, half: str) -> list[sp.Item]:
        return [self.items[p.file] for p in self.record.in_section(section, half)]

    def _works(self, placed: list[Placed], here: str, where: str) -> str:
        from l7r.diagram.interactive.citations import cited_keys, works_html  # noqa: PLC0415 - citations imports the record

        keys = cited_keys([(str(p.number), p.body) for p in placed])
        block, missing = works_html(keys, self.entries, "", self.catalog)
        self.errors += [f"{where}: cites `{k}`, whose registry entry has no write-up (`What it is:` and `Why it applies, and its limits:`)" for k in missing]
        return self.rewrite(block, None, here, where)

    def _question(self, item: sp.Item, half: str, section: ct.Section, run: list[sp.Item], at: int) -> None:
        """A question's small page. Links are resolved while every `href` is still the record's, then the references
        are numbered, then the notes' keys turned to the works at the foot."""
        page = item.page
        assert page is not None
        here = f"{links.QUESTION_DIR}/{item.id}.html"
        where = f"{qs.QUESTIONS}/{page.file}"
        notes = self.notes_of(page)
        try:
            body, placed = sn.small_page(self.rewrite(item.html, page.file, here, where), notes, where)
        except NoteError as e:
            self.errors.append(str(e))
            return
        orphans = sorted(set(notes) - {p.key for p in placed})
        if orphans:
            self.errors.append(f"{qs.QUESTIONS}/{page.notes_file}: {', '.join(orphans)} - defined as a note, referenced nowhere")
        placed = [Placed(p.key, p.number, self.rewrite(p.body, page.file, here, where), p.references) for p in placed]
        foot = sn.foot(placed, self._works(placed, here, where) if placed else "")
        tags = self.record.question_of(page).tags
        assert tags is not None
        content = sp.crumbs(here, [(sp.half_title(half), f"index.html#{half}"), *sp.section_trail(half, section)])
        content += _as_title(body) + sp.tags_line(tags, self.record.vocab, here) + foot + sp.pager(run, at, here, links.QUESTION_DIR)
        self.files[here] = sp.shell(f"{item.title} - {section.title}", here, sp.open_keys(half, section), content)

    def _section(self, half: str, section: ct.Section) -> None:
        """A section's page in one half - its description, its subsections, its questions - and its questions' pages."""
        here = sp.section_file(half, section)
        run = self.section_items(section, half)
        for at, item in enumerate(run):
            self._question(item, half, section, run, at)
        trail = [(sp.half_title(half), f"index.html#{half}"), *sp.section_trail(half, section)[:-1]]
        body = sp.crumbs(here, trail) + f"<h1>{html.escape(section.title)}</h1>\n{sp.description(section, half)}\n"
        subs = [s for s in section.sections if self.record.holds(s, half)]
        if subs:
            body += '<ul class="sections">\n' + "".join(f'<li><a href="../{sp.section_file(half, s)}">{html.escape(s.title)}</a></li>\n' for s in subs) + "</ul>\n"
        if run:
            body += sp.listing(run, here)
        self.files[here] = sp.shell(f"{section.title} - {sp.half_title(half)}", here, sp.open_keys(half, section), body)

    def _tags(self) -> None:
        """Every tag's page: exactly the questions carrying it, in the order a section lists them (spec 303 FR-014)."""
        vocab = self.record.vocab
        research_first = [q for q in self.record.questions if q.tags is not None]
        for facet in ct.FACETS:
            for tag in sp.facet_tags(vocab, facet):
                here = sp.tag_file(facet, tag.id)
                carrying = [q for q in research_first if (facet, tag.id) in q.tags.all()]  # type: ignore[union-attr]
                pages = self.record.ordered([p for q in carrying for p in q.pages()])
                rows = []
                for p in pages:
                    item = self.items[p.file]
                    rows.append(f'<li><a href="../{links.QUESTION_DIR}/{item.id}.html">{html.escape(item.title)}</a> <span class="lead">({sp.half_title(p.half)})</span></li>')
                body = sp.crumbs(here, [(sp.TAGS_GROUP, "index.html#tags")]) + f"<h1>{sp.FACET_NAMES[facet]}: {html.escape(tag.name)}</h1>\n<p><em>{html.escape(tag.description)}</em></p>\n"
                body += '<ul class="questions">\n' + "\n".join(rows) + "\n</ul>\n" if rows else "<p>No question carries this tag yet.</p>\n"
                self.files[here] = sp.shell(f"{sp.FACET_NAMES[facet]}: {tag.name}", here, f"tags/{facet}", body)

    def grouped(self, items: list[sp.Item]) -> list[tuple[st.Section | None, list[sp.Item]]]:
        """A registry group's entries under their works sections, in the sections' order and the registry's within
        each; an entry the catalog refused (already a build error) follows, under no section."""
        by_key = {i.id: i for i in items}
        out: list[tuple[st.Section | None, list[sp.Item]]] = [(s, [by_key[k] for k in keys]) for s, keys in self.catalog.grouped(list(by_key))]
        refused = [i for i in items if i.id not in self.catalog.section]
        return out + ([(None, refused)] if refused else [])

    def shelves(self, items: list[sp.Item]) -> list[tuple[st.Section | None, list[tuple[st.Label | None, list[sp.Item]]]]]:
        """A registry group's entries by works section, then by primary kind (feature 307, GM 2026-10-02: *"'Sources' as a
        top-level section, and then 'Setting canon' as a subsection of that ... and then in cases where we have other tags
        ... such as 'Reference' vs 'Scholarship' then we could have sub subsections for those"*). The canon, untagged,
        stands under no kind; an entry the catalog refused stands under no section."""
        out: list[tuple[st.Section | None, list[tuple[st.Label | None, list[sp.Item]]]]] = []
        for section, entries in self.grouped(items):
            by_key = {i.id: i for i in entries}
            kinds = [(None, entries)] if section is None else [(lab, [by_key[k] for k in keys]) for lab, keys in self.catalog.by_kind(list(by_key))]
            out.append((section, kinds))
        return out

    def registry_run(self) -> list[sp.Item]:
        """Every registry entry in the order its pages are chained and listed: group by group, section by section, kind
        by kind."""
        return [i for _g, _h, items in self.registry.groups for _s, kinds in self.shelves(items) for _k, run in kinds for i in run]

    def open_keys_of(self, key: str) -> str:
        """The sidebar nodes a source's own page opens: its section's and its kind's."""
        section, tags = self.catalog.section.get(key), self.catalog.tags.get(key)
        if section is None:
            return "sources"
        return f"sources/{section.id}" + (f" sources/{section.id}/{tags.primary('kind')}" if tags is not None else "")

    def source_nodes(self) -> list[dict]:
        """The Sources group of the sidebar: each works section, its kinds beneath it, the works beneath those - each node
        linking its place on the sources index (feature 307 FR-001..FR-003)."""
        index = f"{links.REGISTRY_DIR}/index.html"
        nodes = []
        for _g, _h, items in self.registry.groups:
            for section, kinds in self.shelves(items):
                if section is None:
                    continue
                subs = [
                    {"key": f"sources/{section.id}/{lab.id}", "title": lab.name, "href": f"{index}#{st.kind_anchor(section, lab)}", "sections": [], "items": [_nav_row(i) for i in run]}
                    for lab, run in kinds
                    if lab is not None
                ]
                direct = [_nav_row(i) for lab, run in kinds if lab is None for i in run]
                nodes.append({"key": f"sources/{section.id}", "title": section.title, "href": f"{index}#{section.id}", "sections": subs, "items": direct})
        return nodes

    def entry_html(self, item: sp.Item) -> str:
        """A registry entry as the reader sees it: its marker gone, its labels under its heading, and the URLs of its
        citation line - the paragraph after the heading - made links (feature 307 FR-006)."""
        text = st.strip_marker(item.html)
        m = _HEADING_END.search(text)
        return text if m is None else text[: m.end()] + "\n" + self.catalog.labels(item.id) + _FIRST_P.sub(lambda p: linkify(canon_list(p.group(0))), text[m.end() :], count=1)

    def _registry(self) -> None:
        reg = self.registry
        run = self.registry_run()
        for at, item in enumerate(run):
            here = f"{links.REGISTRY_DIR}/{item.id}.html"
            body = self.rewrite(self.entry_html(item), None, here, f"{store.REGISTRY_DIR}/ {item.id}")
            content = sp.crumbs(here, [(reg.title, f"{links.REGISTRY_DIR}/index.html")]) + _as_title(body) + sp.pager(run, at, here, links.REGISTRY_DIR)
            self.files[here] = sp.shell(f"{item.title} - {reg.title}", here, self.open_keys_of(item.id), content)
        here = f"{links.REGISTRY_DIR}/index.html"
        body = sp.crumbs(here, []) + f'<h1 id="{reg.title_id}">{html.escape(reg.title)}</h1>\n' + self.rewrite(reg.intro, None, here, f"{store.REGISTRY_DIR}/_front.html") + "\n"
        for gid, ghtml, items in reg.groups:
            body += self.rewrite(ghtml, None, here, f"{store.REGISTRY_DIR}/ group {gid}")
            for section, kinds in self.shelves(items):
                if section is not None:
                    body += st.section_heading(section, 3, section.id) + "\n"
                for lab, entries in kinds:
                    if section is not None and lab is not None:
                        body += st.kind_heading(section, lab, 4) + "\n"
                    body += '<ul class="questions">\n' + "\n".join(f'<li><a href="{i.id}.html">{html.escape(i.title)}</a></li>' for i in entries) + "\n</ul>\n"
        self.files[here] = sp.shell(reg.title, here, "sources", body)

    def _home(self) -> None:
        body = [f'<h1 id="contents">{TITLE}</h1>', '<p><a href="all.html">The whole record on one page</a> - every question, every note and every source, under one table of contents.</p>']

        def tree(half: str, sections: list[ct.Section]) -> str:
            rows = []
            for s in sections:
                if self.record.holds(s, half):
                    sub = tree(half, s.sections)
                    rows.append(f'<li><a href="{sp.section_file(half, s)}">{html.escape(s.title)}</a>{sub}</li>')
            return "<ul>" + "".join(rows) + "</ul>" if rows else ""

        for half, label in sp.HALVES:
            body.append(f'<h2 id="{half}">{html.escape(label)}</h2>\n{tree(half, self.record.sections)}')
        body.append(f'<h2 id="tags">{sp.TAGS_GROUP}</h2>')
        for facet in ct.FACETS:
            tags = ", ".join(f'<a href="{sp.tag_file(facet, t.id)}">{html.escape(t.name)}</a>' for t in sp.facet_tags(self.record.vocab, facet))
            body.append(f"<p><em>{sp.FACET_NAMES[facet]}:</em> {tags}</p>")
        sources = "".join(_home_source(n) for n in self.source_nodes())
        body.append(f'<h2><a href="{links.REGISTRY_DIR}/index.html">{sp.REGISTRY_GROUP}</a></h2>\n<ul>{sources}</ul>')
        self.files["index.html"] = sp.shell(TITLE, "index.html", "", "\n".join(body))

    def _single(self) -> None:
        """The whole record on one page: contents, both halves in table-of-contents order, the citations, the sources."""
        count = sn.Numbering()
        toc = ['<nav class="toc"><h2 id="contents">Contents</h2>\n<ul>']
        out: list[str] = []

        def walk(half: str, sections: list[ct.Section]) -> None:
            for s in sections:
                if not self.record.holds(s, half):
                    continue
                anchor = f"{half}-{s.id}"
                run = self.section_items(s, half)
                toc.append(f'<li><a href="#{anchor}">{html.escape(s.title)}</a><ul>' + "".join(f'<li><a href="#{i.id}">{html.escape(i.title)}</a></li>' for i in run))
                out.append(f'<section class="part">\n<h1 id="{anchor}">{html.escape(s.title)}</h1>\n{sp.description(s, half)}\n')
                for item in run:
                    page = item.page
                    assert page is not None
                    where = f"{qs.QUESTIONS}/{page.file}"
                    try:
                        out.append(count.number(self.rewrite(item.html, page.file, "all.html", where, single=True), page.file, self.notes_of(page), where))
                    except NoteError as e:
                        self.errors.append(str(e))
                out.append("</section>\n")
                walk(half, s.sections)
                toc.append("</ul></li>")

        for half, label in sp.HALVES:
            toc.append(f'<li><a href="#{half}">{html.escape(label)}</a><ul>')
            out.append(f'<h1 id="{half}" class="half">{html.escape(label)}</h1>\n')
            walk(half, self.record.sections)
            toc.append("</ul></li>")
        toc.append('<li><a href="#citations">Citations</a></li>')
        notes = []
        for file, placed in count.placed:
            body = self.rewrite(placed.body, file, "all.html", f"{qs.QUESTIONS}/{file} notes", single=True)
            notes.append(render_note(Placed(placed.key, placed.number, sn.keyed_to(body, "#"), 0), ""))
        out.append('<section class="part footnotes">\n<h1 id="citations">Citations</h1>\n<ol>\n' + "\n".join(notes) + "\n</ol></section>\n")
        reg = self.registry
        toc.append(
            f'<li><a href="#{reg.title_id}">{html.escape(reg.title)}</a><ul>'
            + "".join(
                f'<li><a href="#{gid}">{html.escape(_text(_HEAD.search(gh).group(3)) if _HEAD.search(gh) else gid)}</a>'
                + ("<ul>" + "".join(_toc_section(s, kinds) for s, kinds in self.shelves(gi) if s is not None) + "</ul>" if gi else "")
                + "</li>"
                for gid, gh, gi in reg.groups
            )
            + "</ul></li>"
        )
        out.append(f'<section class="part">\n<h1 id="{reg.title_id}">{html.escape(reg.title)}</h1>\n')
        out.append(self.rewrite(reg.intro, None, "all.html", f"{store.REGISTRY_DIR}/_front.html", single=True))
        for gid, ghtml, items in reg.groups:
            out.append(self.rewrite(ghtml, None, "all.html", f"{store.REGISTRY_DIR}/ group {gid}", single=True))
            for section, kinds in self.shelves(items):
                if section is not None:
                    out.append(st.section_heading(section, 3, section.id) + "\n")
                for lab, entries in kinds:
                    if section is not None and lab is not None:
                        out.append(st.kind_heading(section, lab, 4) + "\n")
                    out += [_ENTRY_H3.sub(r"<h5\1</h5>", self.rewrite(self.entry_html(i), None, "all.html", f"{store.REGISTRY_DIR}/ {i.id}", single=True), count=1) for i in entries]
        out.append("</section>\n")
        toc.append("</ul></nav>\n")
        head = f'<h1 id="record">{TITLE}</h1>\n<p><em>Every question the maps were researched from, every note behind them and every source they cite, on one page. The same record, a page per question: <a href="index.html">the contents</a>.</em></p>\n'
        self.files["all.html"] = sp.shell(TITLE + " - the whole record", "all.html", "", head + "".join(toc) + "".join(out), lazy_glossary=True)


def _nav_row(item: sp.Item) -> list[str]:
    """A source as the sidebar lists it: its key and its page."""
    return [item.title, f"{links.REGISTRY_DIR}/{item.id}.html"]


def _works_list(items: list[sp.Item], href: str) -> str:
    """Works as a contents list: each its key, linking `href` with the key in place of `{}`."""
    return "<ul>" + "".join(f'<li><a href="{href.format(i.id)}">{html.escape(i.title)}</a></li>' for i in items) + "</ul>" if items else ""


def _toc_section(section: st.Section, kinds: list[tuple[st.Label | None, list[sp.Item]]]) -> str:
    """A works section's line in the one-page record's contents: its kinds nested beneath it, and the works beneath each
    kind - or beneath the section, for the canon (feature 307 FR-004)."""
    subs = "".join(f'<li><a href="#{st.kind_anchor(section, lab)}">{html.escape(lab.name)}</a>{_works_list(run, "#{}")}</li>' for lab, run in kinds if lab is not None)
    direct = [i for lab, run in kinds if lab is None for i in run]
    return f'<li><a href="#{section.id}">{html.escape(section.title)}</a>' + _works_list(direct, "#{}") + (f"<ul>{subs}</ul>" if subs else "") + "</li>"


def _home_source(node: dict) -> str:
    """A works section on the home page: its kinds and their works beneath it, each in a block that opens on a click, so
    the contents stay readable with two thousand works under them (feature 307 FR-004)."""

    def works(rows: list[list[str]]) -> str:
        return "<ul>" + "".join(f'<li><a href="{href}">{html.escape(title)}</a></li>' for title, href in rows) + "</ul>" if rows else ""

    kinds = "".join(f'<li><details><summary><a href="{k["href"]}">{html.escape(k["title"])}</a></summary>{works(k["items"])}</details></li>' for k in node["sections"])
    return f'<li><details><summary><a href="{node["href"]}">{html.escape(node["title"])}</a></summary>{works(node["items"])}' + (f"<ul>{kinds}</ul>" if kinds else "") + "</details></li>"


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
