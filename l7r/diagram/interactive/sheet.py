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
`compound/`. THE PAGE IS RUST since feature 449 T150 (the engine port's step 2): `rust/mode_a/src/sheet/page.rs` regroups the
sheet into pieces and writes the page (`rust/mode_a/src/page.rs`), and `write_sheet_page` below is the one call the six
pool generators make, run as `scripts/gates/l7r-gate.sh mode-a sheet-page`.
"""

from __future__ import annotations

# LOCKSTEP (feature 449 T170, `ask:449-engine-order` condition 3): the reader here (`Node`, `parse`, `DEFS`, `element_kinds`) is ported to `rust/mode_a/src/sheet.rs`, which `make notes-census`
# runs; an edit here makes the same change there in the same commit, and `make rust-test CRATE=rust/mode_a` fails until it does
# (`parse/lockstep.rs` holds the two equal on every pool sheet).
# (T150) Its page half (`pieces`, `census`, `title_of` and the page's writing) is Rust alone, `rust/mode_a/src/sheet/page.rs`;
# `write_sheet_page` is a call to it.

import builtins
import importlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field

from .classes import FeatureClass

#: One token of the sheet: a comment, a tag, or the text between tags.
_TOKEN = re.compile(r"<!--.*?-->|<[^>]*>|[^<]+", re.S)
_NAME = re.compile(r"</?\s*([A-Za-z][\w:.-]*)")
_KIND = re.compile(r'\sdata-kind="([^"]*)"')
_PART_OF = re.compile(r'\sdata-part-of="([^"]*)"')

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

    @property
    def part_of(self) -> str | None:
        """The kind this element is a PART of though drawn outside its group - for paint order (feature 264: the
        genkan is drawn after the garden so the garden does not cover it, and is still the residence's)."""
        m = _PART_OF.search(self.open)
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


#: The tree this module is in: its launcher builds and runs the Mode A engine (`scripts/gates/l7r-gate.sh mode-a`).
_TREE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def _raised(kind: str, message: str) -> BaseException:
    """The exception the Python writer raised for the engine's refusal `kind: message` - its class by name (a builtin, or a dotted
    one such as `l7r.diagram._census.RenderedInATest`), so a generator's traceback ends on the line it ended on; a class that cannot
    be built from a message alone is stood in for by one of the same name."""
    module, _, name = kind.rpartition(".")
    try:
        cls = getattr(importlib.import_module(module) if module else builtins, name)
        return cls(message)
    except (ImportError, AttributeError, TypeError):
        return type(name, (Exception,), {"__module__": module or "builtins"})(message)


def write_sheet_page(svg_path: str, registry: dict[str, FeatureClass], with_raster: bool | None = None, svg: str | None = None) -> Census:
    """`<map>.html` beside `<map>.svg`, from the sheet's own tags - and the sheet's census, for the caller to report. Written by
    the Mode A engine (`l7r-mode-a sheet-page`, feature 449 T150): `with_raster` defaults there to the render condition every
    other page uses (feature 208: no picture when `DIAGRAM_SKIP_RENDER=1`), and the map's `<map>.notes.md` "Map notes" block is
    read from the output path, as for a hamlet. `svg` is the sheet's text when it is not the file's - a hand sheet's with its
    captions placed (feature 286, `labels.hand_sheet.placed`), handed on stdin; the page is still written beside, and named for,
    `svg_path`. `registry` is the engine's own, read from the same modal files (`compound_kinds`); every caller passes
    `COMPOUND_CLASSES`.

    THE READS ARE OPENED HERE (feature 449 T150): the generation cache learns a generator's data files by spying on `open()`
    (`gencache.record`, spec 187 D3), which cannot see the engine's process, so each file the engine read is opened for reading
    here - a stylesheet or question edit still re-keys the sheet."""
    del registry  # the engine reads the same registry from the tree (`l7r_gate_registry::about::compound_classes`)
    argv = [os.path.join(_TREE, "scripts", "gates", "l7r-gate.sh"), "mode-a", "sheet-page", svg_path]
    if with_raster is not None:
        argv.append("--with-raster" if with_raster else "--no-raster")
    if svg is not None:
        argv.append("--stdin")
    run = subprocess.run(argv, input=(svg or "").encode("utf-8"), capture_output=True, check=False)
    said = run.stderr.decode("utf-8", "replace")
    try:
        out = json.loads(run.stdout)
    except ValueError:
        raise RuntimeError(f"l7r-mode-a sheet-page exited {run.returncode}: {said}") from None
    # the engine's warnings (resvg absent: the page carries no picture) reach the generator's stderr as the Python writer's did; a
    # refusal's own last line is the exception raised below, not printed twice
    if "error" in out:
        kind = out["error"]["kind"]
        at = said.rfind("\n" + kind) + 1 if not said.startswith(kind) else 0  # the refusal's text, its message of any length
        sys.stderr.write(said[:at])
        raise _raised(kind, out["error"]["message"])
    sys.stderr.write(said)
    for path in out["reads"]:
        with open(path, "rb"):
            pass
    return Census(dict(out["counts"]), out["unclassed"], out["unregistered"])
