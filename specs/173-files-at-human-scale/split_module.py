#!/usr/bin/env python3
"""One-shot mover for feature 173: the nine oversize modules become packages.

Lineage: `024-human-scale-files/split_package.py` (verbatim contiguous line ranges, synthesized
imports, a hard failure on a forward cross-module reference) and `025-human-scale-splits/
split_settlement.py` (mixin ranges, `self: "Settlement"` annotation, symtable free reads). This
generalizes both so one tool does all nine instead of a thirteenth hand-written splitter.

    python3 split_module.py --analyze <path>          # names, spans, and the reference graph
    python3 split_module.py --plan <path>             # the proposed cuts, with cross-module edges
    python3 split_module.py --apply <path>            # write the package, delete the monolith

TWO SHAPES.

- `module`: top-level defs partition into submodules by contiguous line ranges. Functions call each
  other directly, so cross-module edges are real imports and a CYCLE IS FATAL - the tool refuses
  rather than emitting a package that cannot import. `--plan` exists to find the cuts that avoid it.
- `mixin`: one Mixin class whose methods partition into sub-mixins, composed back into the original
  class name in `__init__.py` (the `settlement/structures/` pattern, feature 114). Methods reach
  each other through `self.` on the composed Settlement, so a cross-submodule call needs NO import
  and the partition can be re-cut later without touching core.py. Module-level helpers in the same
  file go to one leading submodule that the sub-mixins import from.

Contiguity is what preserves the record: a statement owns the lines from the previous statement's
end through its own, so a banner comment travels with the code it introduces and no source line is
lost. Concatenating the emitted body regions in file order reproduces the monolith exactly, which
`--apply` asserts before it writes anything.

Retired the moment the nine land - the packages are then the hand-maintained truth.
"""

from __future__ import annotations

import argparse
import ast
import os
import re
import subprocess
import symtable
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SKILL = os.path.join(REPO, ".claude", "skills", "diagram")


# ---- the cut table -------------------------------------------------------------------------------
# Each entry: kind, and CUTS as (marquee name that OPENS the submodule, module name, "look here
# when" line). The first cut's marquee must be the file's first partitioned statement. Filled in
# per file after `--plan` shows the reference graph; see specs/173/cuts.md for the reasoning.
PLANS: dict[str, dict] = {}


def _load_cuts() -> None:
    """Cut tables live beside this script in cuts.py so the tool stays reviewable."""
    path = os.path.join(HERE, "cuts.py")
    if os.path.exists(path):
        ns: dict = {}
        with open(path) as fh:
            exec(compile(fh.read(), path, "exec"), ns)   # noqa: S102 - our own file, one-shot tool
        PLANS.update(ns["PLANS"])


# ---- name analysis -------------------------------------------------------------------------------
def toplevel_names(node: ast.stmt) -> list[str]:
    """Every module-level name this statement binds."""
    out: list[str] = []
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        out.append(node.name)
    elif isinstance(node, ast.Assign):
        for t in node.targets:
            for el in t.elts if isinstance(t, (ast.Tuple, ast.List)) else [t]:
                if isinstance(el, ast.Name):
                    out.append(el.id)
    elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        out.append(node.target.id)
    elif isinstance(node, ast.TypeAlias) and isinstance(node.name, ast.Name):
        out.append(node.name.id)
    return out


def free_reads(src: str) -> set[str]:
    """Names a source fragment reads without binding, via symtable (scope-aware)."""
    table = symtable.symtable(src, "<mod>", "exec")
    out: set[str] = set()

    def walk(t: symtable.SymbolTable) -> None:
        for s in t.get_symbols():
            if s.is_referenced() and not (s.is_local() and t.get_type() != "module"):
                out.add(s.get_name())
        for c in t.get_children():
            walk(c)

    walk(table)
    return out


def annotation_names(src: str) -> set[str]:
    """Py3.14 lazy annotations keep annotation-only names out of symtable - walk them by hand."""
    out: set[str] = set()
    for node in ast.walk(ast.parse(src)):
        anns: list[ast.expr] = []
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = node.args
            for a in [*args.args, *args.posonlyargs, *args.kwonlyargs, args.vararg, args.kwarg]:
                if a is not None and a.annotation is not None:
                    anns.append(a.annotation)
            if node.returns is not None:
                anns.append(node.returns)
        elif isinstance(node, ast.AnnAssign):
            anns.append(node.annotation)
        elif isinstance(node, ast.TypeAlias):
            anns.append(node.value)
        for a in anns:
            out |= {s.id for s in ast.walk(a) if isinstance(s, ast.Name)}
            out |= {s.value.id for s in ast.walk(a) if isinstance(s, ast.Attribute) and isinstance(s.value, ast.Name)}
    return out


def reads_of(src: str, wrap: bool = False) -> set[str]:
    body = "class _M:\n" + src if wrap else src
    return free_reads(body) | annotation_names(body)


# ---- the source, sliced --------------------------------------------------------------------------
class Source:
    def __init__(self, path: str) -> None:
        self.path = path
        with open(path) as fh:
            self.text = fh.read()
        self.lines = self.text.splitlines(keepends=True)
        self.tree = ast.parse(self.text)
        self.doc = self.tree.body[0] if isinstance(self.tree.body[0], ast.Expr) else None
        self.imports = [n for n in self.tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
        self.import_binds: dict[str, str] = {}
        for n in self.imports:
            seg = ast.get_source_segment(self.text, n) or ""
            for a in n.names:
                self.import_binds[(a.asname or a.name).split(".")[0]] = seg
        self.header_end = max((n.end_lineno or 0) for n in ([self.doc] if self.doc else []) + self.imports)

    def docstring(self) -> str:
        if self.doc is None:
            return ""
        return "".join(self.lines[self.doc.lineno - 1 : self.doc.end_lineno or 0])

    def contiguous(self, nodes: list[ast.stmt], start: int) -> list[tuple[ast.stmt, str]]:
        """Each node owns lines (previous end, its own end] - so banners travel with their code."""
        out: list[tuple[ast.stmt, str]] = []
        prev = start
        for n in nodes:
            out.append((n, "".join(self.lines[prev : n.end_lineno or 0])))
            prev = n.end_lineno or 0
        return out

    def body_nodes(self) -> list[ast.stmt]:
        skip = set(id(n) for n in self.imports) | ({id(self.doc)} if self.doc else set())
        return [n for n in self.tree.body if id(n) not in skip]


def reference_graph(src: Source, nodes: list[ast.stmt]) -> tuple[dict[str, int], list[tuple[int, int, str]]]:
    """(name -> statement index, [(from index, to index, name)]) over the module's own top level."""
    home: dict[str, int] = {}
    for i, n in enumerate(nodes):
        for nm in toplevel_names(n):
            home.setdefault(nm, i)
    edges: list[tuple[int, int, str]] = []
    for i, n in enumerate(nodes):
        seg = ast.get_source_segment(src.text, n) or ""
        for nm in sorted(reads_of(seg)):
            j = home.get(nm)
            if j is not None and j != i:
                edges.append((i, j, nm))
    return home, edges


# ---- reporting -----------------------------------------------------------------------------------
def cmd_analyze(path: str) -> int:
    src = Source(path)
    nodes = src.body_nodes()
    home, edges = reference_graph(src, nodes)
    print(f"{path}: {len(src.lines)} lines, {len(nodes)} top-level statements, header ends line {src.header_end}")
    prev = src.header_end
    for i, n in enumerate(nodes):
        span = (n.end_lineno or 0) - prev
        names = ", ".join(toplevel_names(n)) or "<statement>"
        out = sorted({nm for a, _, nm in edges if a == i})
        print(f"  [{i:3d}] {n.lineno:5d}-{n.end_lineno:<5d} ({span:4d}) {names[:60]:<60} -> {', '.join(out)[:70]}")
        prev = n.end_lineno or 0
    return 0


def cmd_plan(path: str) -> int:
    src = Source(path)
    plan = PLANS[rel(path)]
    if plan["kind"] == "mixin":
        return _plan_mixin(src, plan)
    nodes = src.body_nodes()
    SOURCE_TEXT[0] = src.text
    home, edges = reference_graph(src, nodes)
    if plan["kind"] == "names":
        owner = assign_by_name(nodes, plan["modules"])
        order = [m for m, _, _ in plan["modules"]]
    elif plan["kind"] == "lines":
        owner = assign_by_line(nodes, plan["cuts"])
        order = [m for _, m, _ in sorted(plan["cuts"])]
    else:
        owner = assign_modules(nodes, plan["cuts"])
        order = [m for _, m, _ in plan["cuts"]]
    sizes = {m: 0 for m in order}
    prev = src.header_end
    for i, n in enumerate(nodes):
        sizes[owner[i]] += (n.end_lineno or 0) - prev
        prev = n.end_lineno or 0
    cross: dict[tuple[str, str], set[str]] = {}
    for a, b, nm in edges:
        if owner[a] != owner[b]:
            cross.setdefault((owner[a], owner[b]), set()).add(nm)
    bad = [(u, v) for (u, v) in cross if order.index(v) > order.index(u)]
    # A LINEAR SCRIPT'S SECOND BINDING IS INVISIBLE ACROSS A CUT. `shiro-daika.gen.py` executes 346
    # drawing statements at module level and rebinds six short-lived names (`_qnx`, `_MKB`, ...).
    # Imports resolve to the module that defines a name FIRST, so if the two bindings land either
    # side of a cut, a later part silently reads the stale one - and the map draws wrong rather than
    # failing. Refuse instead: move the cut so both bindings stay together.
    # ...but a REBIND is only a hazard if the second part READS the name before rebinding it. When
    # the rebind comes first, the module owns the name locally, the import is never synthesized (the
    # emitter excludes locally-bound names) and nothing stale is reachable. `shiro-daika.gen.py`'s
    # `_qnx`/`_qny` are exactly that shape - a scratch normal vector recomputed in a later section -
    # so the check reports them and passes. What it refuses is a part that reads the old value and
    # then replaces it, which is the one arrangement that draws a wrong map in silence.
    straddle: list[str] = []
    fatal: list[str] = []
    bound: dict[str, dict[str, int]] = {}
    for i, n in enumerate(nodes):
        for nm in toplevel_names(n):
            bound.setdefault(nm, {}).setdefault(owner[i], n.lineno)
    first_read: dict[tuple[str, str], int] = {}
    for i, n in enumerate(nodes):
        seg = ast.get_source_segment(src.text, n) or ""
        for nm in reads_of(seg):
            first_read.setdefault((owner[i], nm), n.lineno)
    for nm, mods in sorted(bound.items()):
        if len(mods) < 2:
            continue
        where = ", ".join(sorted(mods))
        late = [m for m, ln in mods.items() if first_read.get((m, nm), 10**9) < ln]
        if late:
            fatal.append(f"{nm} - {', '.join(sorted(late))} READS it before rebinding it")
        else:
            straddle.append(f"{nm} ({where}; each part rebinds before use, so nothing stale is reachable)")
    for m in order:
        print(f"  {sizes[m]:5d}  {m}.py")
    print(f"  {sum(sizes.values()):5d}  total (monolith body)")
    for (u, v), names in sorted(cross.items()):
        arrow = "FORWARD" if order.index(v) > order.index(u) else "back"
        print(f"    {u} -> {v} [{arrow}]: {', '.join(sorted(names))[:100]}")
    if straddle:
        print(f"    REBOUND ACROSS A CUT: {'; '.join(straddle)}")
    if bad:
        print(f"\n  {len(bad)} FORWARD edge(s) - these are import cycles; move the cut.")
        return 1
    if fatal:
        print("    STALE-READ HAZARD: " + "; ".join(fatal))
        print(f"\n  {len(fatal)} name(s) read from an earlier part and then rebound - move the cut.")
        return 1
    over = [m for m in order if sizes[m] > 1000]
    if over:
        print(f"\n  still over the bar: {', '.join(over)}")
        return 1
    patched = patched_through_module(src.path, set(home))
    for name, where in sorted(patched.items()):
        print(f"    MONKEYPATCHED through the module: {name} (in {', '.join(sorted(set(where)))}) - the patch target moves with it")
    print("\n  acyclic, every module under the bar")
    return 0


def _plan_mixin(src: Source, plan: dict) -> int:
    cls = next(n for n in src.tree.body if isinstance(n, ast.ClassDef) and n.name == plan["class"])
    methods = [n for n in cls.body if isinstance(n, ast.FunctionDef)]
    owner = assign_modules(methods, plan["cuts"])
    order = [m for _, m, _ in plan["cuts"]]
    sizes = {m: 0 for m in order}
    prev = cls.body[0].end_lineno if isinstance(cls.body[0], ast.Expr) else cls.lineno
    for i, n in enumerate(methods):
        sizes[owner[i]] += (n.end_lineno or 0) - (prev or 0)
        prev = n.end_lineno or 0
    helpers = sum(1 for n in src.body_nodes() if n is not cls)
    pre = (cls.lineno - 1) - src.header_end
    print(f"  {pre:5d}  {plan.get('helpers', '_helpers')}.py   ({helpers} module-level helpers before the class)")
    for m in order:
        print(f"  {sizes[m]:5d}  {m}.py")
    over = [m for m in order if sizes[m] > 1000]
    if over:
        print(f"\n  still over the bar: {', '.join(over)}")
        return 1
    print("\n  methods reach each other through self. - no cross-module imports to cycle")
    return 0


def assign_by_line(nodes: list[ast.stmt], cuts: list[tuple[int, str, str]]) -> list[str]:
    """Statement index -> module, by the LINE each section starts at.

    `wip/shiro-daika.gen.py` needs this: its sections open with a drawing call, which binds no name,
    so there is no marquee to cut on - but the file carries a banner comment above every one of
    them, and those banners are what a reader navigates by.
    """
    starts = sorted(cuts, key=lambda c: c[0])
    owner: list[str] = []
    for n in nodes:
        here = starts[0][1]
        for line, module, _ in starts:
            if n.lineno >= line:
                here = module
        owner.append(here)
    return owner


def assign_modules(nodes: list[ast.stmt], cuts: list[tuple[str, str, str]]) -> list[str]:
    """Statement index -> module name, by contiguous ranges opened by each cut's marquee name."""
    starts = {}
    for marquee, module, _ in cuts:
        starts[marquee] = module
    owner: list[str] = []
    current: str | None = None
    for n in nodes:
        for nm in toplevel_names(n):
            if nm in starts:
                current = starts.pop(nm)
                break
        if current is None:
            raise SystemExit(f"the first cut's marquee is not the first statement: {toplevel_names(n)}")
        owner.append(current)
    if starts:
        raise SystemExit(f"marquee names never seen: {', '.join(starts)}")
    return owner



def assign_by_name(nodes: list[ast.stmt], modules: list[tuple[str, list[str], str]]) -> list[str]:
    """Statement index -> module, for a file whose SOURCE ORDER IS NOT ITS DEPENDENCY ORDER.

    `hamletgen/ways.py` is the case that forced this: its two stage entry points stand at the top
    and every primitive they call stands below, so contiguous cuts in source order are ALL forward
    edges. Grouping by subject and emitting the layers bottom-up is the only cut that produces an
    importable package - and a slice still carries the banner comment above it, so a moved function
    arrives with its own commentary.

    Only functions and classes are listed by hand. Everything else places itself:

    - a bare string-literal statement is the DOCSTRING OF THE CONSTANT ABOVE IT (this file's own
      convention, e.g. `_BRIDGE_DETOUR = 2.0` followed by 15 lines explaining the number), so it
      follows its neighbor and never travels alone;
    - any other unlisted statement - a constant - lands in the EARLIEST emitted module that reads
      it, which is the only placement that keeps every edge pointing backwards. A constant nothing
      reads stays with the module it was declared beside.
    """
    order = [m for m, _, _ in modules]
    home: dict[str, str] = {}
    for module, names, _ in modules:
        for nm in names:
            if nm in home:
                raise SystemExit(f"{nm} listed twice ({home[nm]} and {module})")
            home[nm] = module
    listed = set(home)

    defines: list[list[str]] = [toplevel_names(n) for n in nodes]
    known = {nm for names in defines for nm in names}
    unlisted = [i for i, names in enumerate(defines) if names and not (set(names) & listed)]
    missing = listed - known
    if missing:
        raise SystemExit(f"named but not defined in the file: {', '.join(sorted(missing))}")

    owner: list[str | None] = [None] * len(nodes)
    for i, names in enumerate(defines):
        for nm in names:
            if nm in home:
                owner[i] = home[nm]
                break

    # A constant goes where it is first NEEDED - and that is a FIXED POINT, not one pass. A constant
    # read only by ANOTHER unplaced constant has no owned reader on the first sweep, so a single
    # pass leaves it to fall through to its neighbor's module, which is how `pack_audit.py`'s
    # `WALL_STROKE` (read by `_WALL_GROUP_RE`, itself unplaced) landed in `checks` while `parse`
    # read it - one forward edge, caught by `--plan`. Iterate until nothing moves.
    segs = [ast.get_source_segment(SOURCE_TEXT[0], n) or "" for n in nodes]
    reads = [reads_of(s) for s in segs]
    while True:
        readers: dict[str, set[str]] = {}
        for i in range(len(nodes)):
            if owner[i] is None:
                continue
            for nm in reads[i]:
                readers.setdefault(nm, set()).add(owner[i])
        moved = False
        for i in unlisted:
            for nm in defines[i]:
                users = readers.get(nm, set())
                if not users:
                    continue
                want = min(users, key=order.index)
                # a constant may only move EARLIER, and must be free to: `WALL_STROKE` is read by a
                # regex constant that is itself unplaced on the first sweep, so pass 1 sees only its
                # `checks` reader and pass 2 discovers the earlier `parse` one. Freezing after the
                # first placement leaves the forward edge in place.
                if owner[i] is None or order.index(want) < order.index(owner[i]):
                    owner[i] = want
                    moved = True
                break
        if not moved:
            break
    # bare-string docstrings follow the statement above them; anything still unplaced does too
    for i, n in enumerate(nodes):
        if owner[i] is None:
            owner[i] = owner[i - 1] if i else order[0]
    return [o for o in owner if o is not None]


SOURCE_TEXT = [""]   # set by cmd_plan/cmd_apply before assign_by_name runs


def rel(path: str) -> str:
    return os.path.relpath(os.path.abspath(path), SKILL)



# ---- the consumed surface, DERIVED ---------------------------------------------------------------
def consumed_surface(module_path: str, own_names: set[str]) -> set[str]:
    """Names the REST of the tree reads from this module - so `__init__.py` re-exports exactly them.

    Derived by grep rather than declared, per constitution clause 14: a hand-written re-export
    roster restates what the importers already say. Two forms are counted, and one is deliberately
    over-broad: `from x.y.mod import a, b` names its names, while `mod.NAME` attribute access
    anywhere in the tree contributes NAME if this module defines it - which can over-export (a
    same-named attribute on an unrelated object) but never under-export silently.
    """
    stem = os.path.basename(module_path)[:-3]
    want: set[str] = set()
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", ".clones", "legacy-hand-authored-pool", "specs"}]
        for fn in files:
            if not fn.endswith(".py"):
                continue
            here = os.path.join(root, fn)
            if os.path.abspath(here) == os.path.abspath(module_path):
                continue
            try:
                body = open(here).read()
            except OSError:
                continue
            if stem not in body:
                continue
            for m in re.finditer(rf"from\s+[.\w]*\b{re.escape(stem)}\s+import\s+\(?([^)\n]+)\)?", body):
                for piece in m.group(1).split(","):
                    name = piece.strip().split(" as ")[0].strip()
                    if name and name != "*":
                        want.add(name)
            # AN ALIAS DEFEATS A BARE-STEM GREP. `tests/tools/test_pack_audit.py` reads
            # `from l7r.diagram.tools import pack_audit as pa` and then says `pa._luma` 91 times, so
            # a search for `pack_audit.` finds nothing and fourteen private names silently leave the
            # surface. Resolve every alias the importer gave this module and search those too.
            names = {stem} | set(re.findall(rf"import\s+{re.escape(stem)}\s+as\s+(\w+)", body))
            for alias in names:
                for m in re.finditer(rf"\b{re.escape(alias)}\.(\w+)", body):
                    want.add(m.group(1))
    return want & own_names


def patched_through_module(module_path: str, own_names: set[str]) -> dict[str, list[str]]:
    """Names something MONKEYPATCHES through the module object - the split's quietest hazard.

    `monkeypatch.setattr(hinterland, "WOODLAND_BBOX_FLOOR", 1.01)` works on a monolith because the
    reader and the patch target are the same namespace. After a split the reader holds its own bound
    copy in a submodule, the patch lands on the package, and the test goes green-to-red for a reason
    that has nothing to do with the code. Reported by `--plan` so the cut is made knowing it.
    """
    stem = os.path.basename(module_path)[:-3]
    out: dict[str, list[str]] = {}
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", ".clones", "legacy-hand-authored-pool", "specs"}]
        for fn in files:
            if not fn.endswith(".py") or os.path.abspath(os.path.join(root, fn)) == os.path.abspath(module_path):
                continue
            try:
                body = open(os.path.join(root, fn)).read()
            except OSError:
                continue
            if stem not in body:
                continue
            aliases = {stem} | set(re.findall(rf"import\s+{re.escape(stem)}\s+as\s+(\w+)", body))
            for alias in aliases:
                for m in re.finditer(rf"setattr\(\s*{re.escape(alias)}\s*,\s*[\"'](\w+)[\"']", body):
                    if m.group(1) in own_names:
                        out.setdefault(m.group(1), []).append(os.path.relpath(os.path.join(root, fn), REPO))
    return out


# ---- emission ------------------------------------------------------------------------------------
def _deepen(stmt: str) -> str:
    """A package is one level deeper than the module it replaces, so every relative import gains a dot.

    This is the silent half of a split: `from ._geom import Poly` still PARSES at the new depth and
    resolves to a module that does not exist, and the failure arrives as an ImportError at run time
    rather than as anything the mover noticed.
    """
    return re.sub(r"^([ \t]*from\s+)(\.)", r"\1..", stmt, flags=re.M)



def _one_name_import(stmt: str, name: str) -> str:
    """`from x import a, b, c` -> `from x import <name> as <name>`; `import x` -> itself.

    The explicit `as` form is what pyrefly's no-implicit-reexport rule requires of a re-export.
    """
    m = re.match(r"^\s*from\s+([.\w]+)\s+import\b", stmt)
    if m:
        return f"from {m.group(1)} import {name} as {name}"
    return stmt.strip()


def _synth_imports(body: str, src: "Source", local: set[str], earlier: dict[str, str], wrap: bool, self_type: str | None, plan_core: str = "from ..core import Settlement") -> str:
    reads = reads_of(body, wrap=wrap) - local
    blocks: list[str] = []
    std = sorted({_deepen(src.import_binds[n]) for n in reads if n in src.import_binds})
    if std:
        blocks.append("\n".join(std))
    by_mod: dict[str, list[str]] = {}
    for n in sorted(reads):
        mod = earlier.get(n)
        if mod is not None:
            by_mod.setdefault(mod, []).append(n)
    for mod, names in sorted(by_mod.items()):
        blocks.append(f"from .{mod} import {', '.join(sorted(names))}")
    if self_type and (self_type in reads or wrap):
        # `from typing import TYPE_CHECKING` may already have come across on a copied std import
        # (the monolith writes `from typing import TYPE_CHECKING, Any, cast`); a second one is a
        # redefinition ruff will not merge.
        have = any("TYPE_CHECKING" in b for b in blocks)
        lead = "" if have else "from typing import TYPE_CHECKING\n\n"
        blocks.append(f"{lead}if TYPE_CHECKING:\n    {plan_core}")
    return "\n".join(b for b in blocks if b)


def _annotate_self(seg: str, self_type: str) -> str:
    out = re.sub(r'(\n    def \w+\(\s*self)([,)])', rf'\1: "{self_type}"\2', "\n" + seg)[1:]
    return re.sub(r'(\n    def \w+\([^\n]*self: "' + self_type + r'"[^\n]*)', r'\1  # type: ignore[misc]', "\n" + out)[1:]


def cmd_apply(path: str) -> int:
    src = Source(path)
    plan = PLANS[rel(path)]
    pkg = plan.get("pkg", path[:-3])
    order = [m for m, _, _ in plan["modules"]] if plan["kind"] == "names" else [m for _, m, _ in (sorted(plan["cuts"]) if plan["kind"] == "lines" else plan["cuts"])]
    hdr_doc = plan["doc"]
    os.makedirs(pkg, exist_ok=True)
    written: dict[str, int] = {}

    def write(name: str, text: str) -> None:
        if not text.endswith("\n"):
            text += "\n"
        with open(os.path.join(pkg, name + ".py"), "w") as fh:
            fh.write(text)
        written[name] = text.count("\n")

    if plan["kind"] == "mixin":
        cls = next(n for n in src.tree.body if isinstance(n, ast.ClassDef) and n.name == plan["class"])
        helpers_mod = plan.get("helpers", "_helpers")
        pre = [n for n in src.body_nodes() if n is not cls]
        assert all((n.end_lineno or 0) < cls.lineno for n in pre), "statements after the class are not handled"
        helper_entries = src.contiguous(pre, src.header_end)
        helper_body = "".join(seg for _, seg in helper_entries)
        helper_names = {nm for n in pre for nm in toplevel_names(n)}
        write(helpers_mod, hdr_doc + _synth_imports(_deepen(helper_body), src, helper_names, {}, False, plan["self"], plan["self_import"]) + "\n\n" + _deepen(helper_body).lstrip("\n"))
        earlier = dict.fromkeys(helper_names, helpers_mod)

        methods = [n for n in cls.body if isinstance(n, ast.FunctionDef)]
        has_doc = isinstance(cls.body[0], ast.Expr)
        entries = src.contiguous(methods, (cls.body[0].end_lineno or 0) if has_doc else cls.lineno)
        owner = assign_modules(methods, plan["cuts"])
        groups: dict[str, list[str]] = {m: [] for m in order}
        for (_, seg), m in zip(entries, owner, strict=True):
            groups[m].append(seg)
        classes: list[tuple[str, str]] = []
        for _marquee, m, _look in plan["cuts"]:
            sub = plan["classes"][m]
            classes.append((m, sub))
            body = _deepen(_annotate_self("".join(groups[m]), plan["self"]))
            text = hdr_doc + _synth_imports(body, src, set(), earlier, True, plan["self"], plan["self_import"]) + "\n\n\nclass " + sub + ":\n" + body.lstrip("\n")
            write(m, text)
        # THE MODULE-LEVEL HELPERS ARE PART OF THE SURFACE TOO. `water_ways.fan_rival` and
        # `fixtures.pick_caption_seat` are exactly the functions the project's own rule lifted OUT of
        # closures so they could be unit-tested (GM 2026-08-28), so the tests import them by name -
        # and a package that re-exported only the mixin class would break every one of them.
        consumed = consumed_surface(path, helper_names | set(src.import_binds))
        surface = sorted({n for n in helper_names if not n.startswith("_")} | (consumed & helper_names))
        passthrough = sorted(consumed & set(src.import_binds))
        init = (
            src.docstring().rstrip("\n") + "\n\n"
            + "\n".join(f"from .{m} import {c}" for m, c in classes) + "\n"
            + (f"from .{helpers_mod} import " + ", ".join(f"{n} as {n}" for n in surface) + "\n" if surface else "")
            + ("".join(_deepen(_one_name_import(src.import_binds[n], n)) + "\n" for n in passthrough))
            + "\n\n"
            + f"class {plan['class']}(\n" + "".join(f"    {c},\n" for _, c in classes) + "):\n"
            + f'    """The composed surface. No members of its own - see this package\'s CLAUDE.md."""\n'
        )
        with open(os.path.join(pkg, "__init__.py"), "w") as fh:
            fh.write(init)
    else:
        nodes = src.body_nodes()
        SOURCE_TEXT[0] = src.text
        entries = src.contiguous(nodes, src.header_end)
        owner = (
            assign_by_name(nodes, plan["modules"]) if plan["kind"] == "names"
            else assign_by_line(nodes, plan["cuts"]) if plan["kind"] == "lines"
            else assign_modules(nodes, plan["cuts"])
        )
        groups: dict[str, list[str]] = {m: [] for m in order}
        names_of: dict[str, set[str]] = {m: set() for m in order}
        for n, (_, seg), m in zip(nodes, entries, owner, strict=True):
            groups[m].append(seg)
            names_of[m] |= set(toplevel_names(n))
        joined = "".join("".join(groups[m]) for m in order)
        whole = "".join(seg for _, seg in entries)
        if plan["kind"] in ("names", "lines"):
            # a by-name split REORDERS the layers, so the bodies are a permutation of the monolith's
            # slices rather than a concatenation of them - assert the multiset instead, which still
            # proves no source line was dropped or duplicated
            assert sorted(seg for _, seg in entries) == sorted(s for m in order for s in groups[m]), "a slice was lost or duplicated"
        else:
            assert joined == whole, "contiguous slices did not reproduce the body"
        earlier: dict[str, str] = {}
        for m in order:
            # A DEFERRED IMPORT INSIDE A FUNCTION BODY IS A RELATIVE IMPORT TOO. `place_wells` holds
            # `from .hinterland import belt_polygon` deliberately (a later stage; module-level would
            # invert the pipeline's reading order), and moving the body one level down breaks it -
            # as a ModuleNotFoundError at CALL time, not import time, so nothing catches it until
            # that branch runs.
            body = _deepen("".join(groups[m]))
            text = hdr_doc + _synth_imports(body, src, names_of[m], earlier, False, None) + "\n\n" + body.lstrip("\n")
            write(m, text)
            earlier.update(dict.fromkeys(names_of[m], m))
        own = set(earlier)
        consumed = consumed_surface(path, own | set(src.import_binds))
        # THE PACKAGE MUST REPRODUCE THE MODULE NAMESPACE, not just the names someone imports by
        # name. Two consumers proved it on `hamletgen/ways.py`: `hamletgen/__init__.py` does
        # `from .ways import *`, which re-exports every PUBLIC name whether or not anything is
        # recorded as importing it; and the tests read `hg.ways.seg_dist` and `hg.ways.WEB_REACH_FT`
        # - names the monolith IMPORTED rather than defined, which were in its namespace all the
        # same. Export both, or the split is silently narrowing a public surface.
        surface = {n for n in own if not n.startswith("_")} | (consumed & own)
        imported = sorted(consumed & set(src.import_binds))
        by_mod: dict[str, list[str]] = {}
        for n in sorted(surface):
            by_mod.setdefault(earlier[n], []).append(n)
        passthrough = "\n".join(_deepen(_one_name_import(src.import_binds[n], n)) for n in imported)
        if plan.get("chain"):
            # A LINEAR SCRIPT, so importing a part EXECUTES it. Each part already imports names from
            # the one before, which forces the order by itself; naming them here in order as well
            # makes that contract readable instead of emergent, and guarantees it for a part that
            # happens to read nothing from its predecessor.
            init = (
                src.docstring().rstrip("\n") + "\n\n"
                + "# Importing this package DRAWS THE MAP: each part executes at import, in this order,\n"
                + "# and each imports from the one above it, so the order is enforced by Python itself\n"
                + "# rather than by this list. See CLAUDE.md in this directory for what each part holds.\n"
                + "".join(f"from . import {m} as {m}  # noqa: F401\n" for m in order)
            )
        else:
            init = (
                src.docstring().rstrip("\n") + "\n\n"
                + "\n".join(f"from .{m} import " + ", ".join(f"{n} as {n}" for n in sorted(ns)) for m, ns in sorted(by_mod.items()))
                + ("\n" + passthrough if passthrough else "")
                + "\n"
            )
        with open(os.path.join(pkg, "__init__.py"), "w") as fh:
            fh.write(init)

    os.remove(path)
    apkg = os.path.abspath(pkg)
    subprocess.run([sys.executable, "-m", "ruff", "check", "--fix", "-q", apkg], cwd=SKILL, check=False)
    subprocess.run([sys.executable, "-m", "ruff", "format", "-q", apkg], cwd=SKILL, check=False)
    for name, n in sorted(written.items(), key=lambda kv: -kv[1]):
        print(f"{n:6d}  {os.path.basename(pkg)}/{name}.py")
    return 0


def main(argv: list[str] | None = None) -> int:
    _load_cuts()
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--analyze", metavar="PATH")
    ap.add_argument("--plan", metavar="PATH")
    ap.add_argument("--apply", metavar="PATH")
    a = ap.parse_args(argv)
    if a.analyze:
        return cmd_analyze(a.analyze)
    if a.plan:
        return cmd_plan(a.plan)
    if a.apply:
        return cmd_apply(a.apply)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
