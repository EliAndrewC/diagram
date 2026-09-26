"""A hand-drawn sheet as an interactive page: the SVG's own `data-kind` tags are the class side list (feature 262).

The GM, 2026-09-26, asking for clickable magistracy maps: *"the main important thing is that the labels and the
features on the building diagram for each magistracy have a common source, such that changing that source in one
place is enough to change it downstream."* A hamlet's page gets its (string, class) pairs from the generator that
drew it; a hand-drawn Mode A sheet has no generator, so the pairs are read back out of the drawing itself. Every
element or group carries `data-kind="<key>"` - the nearest one wins - and `data-kind="-"` is the not-highlighted
ruling. The label drawn inside a feature's group is that feature's ink, so relabeling a building is one edit to the
sheet and nothing else; what a KIND is lives once, in `compound/`'s registry.

THE READER KEEPS THE SHEET'S BYTES. It tokenizes rather than parsing as XML, because an XML round trip rewrites
attributes, namespaces and entities, and the page is meant to be a second serialization of the same drawing. A
subtree with no differently-tagged descendant is one fragment, verbatim. A group that holds a differently-tagged
descendant is descended into, and each piece is emitted inside COPIES of its ancestors' opening tags, so a
`transform` or an inherited `fill` still applies; the pieces stay in document order, so the paint order is the
sheet's. Comments are dropped (they are the author's notes, not ink).

Look here when: an element of a magistracy page lights with the wrong kind (its tag, or its nearest tagged
ancestor's), the census names ink with no kind, or a new Mode A sheet needs a page. The registry is
`compound/`; the page itself is `page.py`, shared with the hamlets.
"""

from __future__ import annotations

import os
import re
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, field

from .classes import NOT_HIGHLIGHTED, FeatureClass
from .content import content
from .page import ink_census, unregistered_classes, write_html
from .tags import ClsTag

#: One token of the sheet: a comment, a tag, or the text between tags.
_TOKEN = re.compile(r"<!--.*?-->|<[^>]*>|[^<]+", re.S)
_NAME = re.compile(r"</?\s*([A-Za-z][\w:.-]*)")
_KIND = re.compile(r'\sdata-kind="([^"]*)"')
_ID = re.compile(r'\sid="[^"]*"')

#: What a Mode A caveat opens with (feature 262, building-review): "On the drawing:", the hamlet lead, labeled every
#: caveat as a drawing note, and a compound's caveats are as often a rule of the setting or a gap in the research.
CAVEAT_LEAD: str = content("page-text.json")["compound_caveat_lead"]

#: The element whose content is never ink: patterns, gradients and clip paths are referenced, not drawn.
DEFS = "defs"


@dataclass
class Node:
    """One element of the sheet: its opening tag verbatim, its children, its closing tag verbatim (empty for a
    self-closing element). `text` holds a text or whitespace run instead, and then there is no element."""

    open: str = ""
    name: str = ""
    children: list[Node] = field(default_factory=list)
    close: str = ""
    text: str = ""
    start: int = -1  # the byte offset of the opening tag in the sheet - what the pack audit's labels are keyed by

    @property
    def kind(self) -> str | None:
        m = _KIND.search(self.open)
        return m.group(1) if m else None

    def source(self) -> str:
        """The element's own bytes, reassembled - comments inside it are dropped, nothing else changes."""
        if not self.name:
            return self.text
        return self.open + "".join(c.source() for c in self.children) + self.close

    def tagged_below(self) -> bool:
        """Whether any descendant carries a kind of its own - the one reason to descend rather than emit whole."""
        return any(c.name and (c.kind is not None or c.tagged_below()) for c in self.children)


def parse(svg: str) -> Node:
    """The sheet as a tree rooted at its `<svg>` element. Whatever precedes the root (an XML declaration, a
    comment) is not part of the drawing; a sheet with no `<svg>` element, or one that never closes it, is refused."""
    stack: list[Node] = [Node(name="#document")]
    for m in _TOKEN.finditer(svg):
        tok = m.group(0)
        if tok.startswith("<!--") or tok.startswith("<?") or tok.startswith("<!"):
            continue
        if not tok.startswith("<"):
            stack[-1].children.append(Node(text=tok))
            continue
        nm = _NAME.match(tok)
        name = nm.group(1) if nm else ""
        if tok.startswith("</"):
            if len(stack) < 2 or stack[-1].name != name:
                raise ValueError(f"unbalanced </{name}> in the sheet (open: {stack[-1].name})")
            stack[-1].close = tok
            stack.pop()
            continue
        node = Node(open=tok, name=name, start=m.start())
        stack[-1].children.append(node)
        if not tok.endswith("/>"):
            stack.append(node)
    if len(stack) != 1:
        raise ValueError(f"the sheet ends inside <{stack[-1].name}>")
    roots = [c for c in stack[0].children if c.name == "svg"]
    if not roots:
        raise ValueError("no <svg> element in the sheet")
    return roots[0]


def _tag(kind: str | None) -> ClsTag:
    return NOT_HIGHLIGHTED if kind == NOT_HIGHLIGHTED else kind


def _walk(node: Node, chain: list[Node], inherited: str | None, seen_ids: set[str]) -> Iterator[tuple[str, ClsTag]]:
    """(fragment, kind) for `node` in document order - whole when nothing below it is tagged otherwise, else
    piece by piece inside copies of its ancestors. `chain` is the untagged-or-tagged ancestors being re-opened."""
    if not node.name:
        if node.text.strip():
            yield _wrapped(node.text, chain, seen_ids), _tag(inherited)
        return
    kind = node.kind if node.kind is not None else inherited
    if node.name == DEFS:
        yield _wrapped(node.source(), chain, seen_ids), NOT_HIGHLIGHTED
        return
    if node.children and node.tagged_below():
        for child in node.children:
            yield from _walk(child, [*chain, node], kind, seen_ids)
        return
    yield _wrapped(node.source(), chain, seen_ids), _tag(kind)


def _wrapped(s: str, chain: Sequence[Node], seen_ids: set[str]) -> str:
    """`s` inside copies of its ancestors' opening tags. An ancestor's `id` rides on its FIRST copy only, so the
    page never carries an id twice because of the reader."""
    opens: list[str] = []
    for a in chain:
        tag = a.open
        m = _ID.search(tag)
        if m:
            if m.group(0) in seen_ids:
                tag = tag.replace(m.group(0), "", 1)
            else:
                seen_ids.add(m.group(0))
        opens.append(tag)
    closes = "".join(a.close for a in reversed(chain))
    return "".join(opens) + s + closes


def flatten(svg: str) -> tuple[list[str], list[ClsTag]]:
    """The sheet as the page's two parallel lists: the drawn strings in paint order and each one's kind. The
    `<svg>` opening tag comes first and its closing last, both ruled not-highlighted - `render_page` reads the
    viewBox from the first string and inserts its layers before the string holding `</svg>`."""
    root = parse(svg)
    strings: list[str] = [root.open]
    tags: list[ClsTag] = [NOT_HIGHLIGHTED]
    seen: set[str] = set()
    for child in root.children:
        for s, t in _walk(child, [], None, seen):
            strings.append(s)
            tags.append(t)
    strings.append(root.close)
    tags.append(NOT_HIGHLIGHTED)
    return strings, tags


def element_kinds(svg: str) -> dict[int, str]:
    """The kind of every tagged-or-inheriting element, keyed by the byte offset of its opening tag - how the pack
    audit, which reads the sheet with its own regexes, learns what each label it found belongs to (feature 262,
    FR-003a: the audit finds a program item by its tag, not by a pattern over its label). Untagged elements are
    absent; `<defs>` content is absent."""
    out: dict[int, str] = {}

    def visit(node: Node, inherited: str | None) -> None:
        if not node.name or node.name == DEFS:
            return
        kind = node.kind if node.kind is not None else inherited
        if kind is not None:
            out[node.start] = kind
        for c in node.children:
            visit(c, kind)

    visit(parse(svg), None)
    return out


@dataclass(frozen=True)
class Census:
    """What a sheet's tags amount to: drawn elements per kind, the ink with no kind (capped, as the hamlet census
    is), and the kinds the registry does not know."""

    counts: dict[str, int]
    unclassed: list[str]
    unregistered: list[str]


def census(svg: str, registry: dict[str, FeatureClass]) -> Census:
    """The completeness facts the pool test holds every magistracy to (spec FR-006)."""
    strings, tags = flatten(svg)
    counts, unclassed = ink_census(strings, tags)
    return Census(counts, unclassed, unregistered_classes(counts, registry))


def title_of(path: str) -> str:
    """`ochiba-magistracy.svg` -> `Ochiba Magistracy` - the page's browser-tab title; the sheet's own title is drawn."""
    return os.path.basename(path).rsplit(".", 1)[0].replace("-", " ").title()


def write_sheet_page(svg_path: str, registry: dict[str, FeatureClass], with_raster: bool | None = None) -> Census:
    """`<map>.html` beside `<map>.svg`, from the sheet's own tags - and the sheet's census, for the caller to
    report. `with_raster` defaults to the render condition every other page uses (feature 208): no picture when
    `DIAGRAM_SKIP_RENDER=1`. The map's `<map>.notes.md` "Map notes" block is read by `write_html` from the
    output path, as for a hamlet."""
    if with_raster is None:
        with_raster = os.environ.get("DIAGRAM_SKIP_RENDER") != "1"
    with open(svg_path, encoding="utf-8") as fh:
        svg = fh.read()
    strings, tags = flatten(svg)
    write_html(svg_path[: -len(".svg")] + ".html", strings, tags, name=title_of(svg_path), with_raster=with_raster, registry=registry, caveat_lead=CAVEAT_LEAD)
    counts, unclassed = ink_census(strings, tags)
    return Census(counts, unclassed, unregistered_classes(counts, registry))
