"""The research CLAIMS of the engine's code and of the Mode A procedures - read from the source, never by running it.

WHY (feature 316, GM 2026-10-02): *"the code that generates a hamlet must have citations for anything that should be research
derived"*, and *"our tooling should be able to evaluate whether or not an annotated thing has been edited since the last time a
subagent check ran on it"*. A research pointer used to be a COMMENT beside the code: the gate checked that the question it
named existed, and nothing knew what it claimed or whether a check had ever compared the two. A claim is now a line of a
`Research:` section in a DOCSTRING (*"Docstrings would be preferable to comments since docstrings are introspectable"*), one
line per claim - the per-claim granularity the GM accepted - and this module reads them from the syntax tree, so neither the
gate nor the push imports the engine to ask.

THE GRAMMAR (`GRAMMAR`, which every refusal prints). A unit with one claim may write it on the header's own line:

    Research:
        dry-field share - research/questions/0033-row-villages-resson.html: rolled per settlement
        a near row keeps none - UNRESEARCHED
    Research: offset arithmetic - NONE

A constant has no docstring, so its claim is the string literal written directly after its assignment; a procedure section's
claim is a comment, `<!-- Research: <label> - <backing> -->`. A unit with no claim of its own takes its MODULE docstring's
`Research:` claims - a module of geometry helpers says NONE once, not on every helper - and each inherited claim is still a
unit of the index of its own (`scripts/record/claims.py`).

THE CODE FINGERPRINT (spec FR-004). A function's syntax tree with every docstring removed and no positions - so comments,
formatting and docstring prose change nothing, and a changed expression changes it - plus the dumped value of every in-scope
module-level constant it names (one level: a constant's own value is its own unit). That is the unit's `core`; a claim's
fingerprint is the core plus the claim line, its pointers reduced to their heading ids, so `make fragment-move` (which changes a
question's number and not its id) owes nothing. CALLEES ARE NOT FOLLOWED, the recorded limit: following them would owe nearly
every claim on any edit, and the callee's own claims are units of their own.

THE SCOPE (spec FR-002). Every engine module the hamlet generator imports, directly or through others, computed from the
import statements each time it is asked - so a module newly imported into hamlet generation comes into scope with it. 241
modules on 2026-10-02.
"""

from __future__ import annotations

import ast
import hashlib
import inspect
import re
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from pathlib import Path

#: The classes a backing may name besides question files (spec FR-001).
CLASSES = ("GUESS", "UNRESEARCHED", "CONVENTION", "DEVIATION", "CANON", "NONE")
#: A question file, as a claim names it (feature 303's flat directory).
POINTER = re.compile(r"research/questions/(\d{4})-([a-z0-9-]+?)(\.drawing)?\.html")
#: What every refusal prints, so the fix is in the message (the project's guard doctrine).
GRAMMAR = (
    "a claim is one line of a `Research:` docstring section: `<label> - <backing>[: <what the code does>]`, the backing being "
    "question files (`research/questions/NNNN-<id>.html` or `.drawing.html`, comma-separated), `GUESS [<drawing page>]` "
    "(searched, silent; the `.drawing.html` that records the guess), `UNRESEARCHED` (not yet searched), `CONVENTION`, "
    "`DEVIATION <question file>`, `CANON` (the GM's setting canon or ruling), or `NONE` (no physical decision); "
    "one claim may sit on the header line (`Research: <label> - <backing>`); a constant's claim is a string literal directly "
    "after its assignment; a module's claims are inherited by its units that carry none"
)
#: Where hamlet generation begins; the scope is everything it imports.
ROOT_PACKAGE = "l7r.diagram.hamletgen"
#: The Mode A procedure documents (spec FR-003, plan D9): None takes every section; a tuple takes those top sections and
#: every heading under them.
PROCEDURES: dict[str, tuple[str, ...] | None] = {
    "docs/buildings.md": None,
    "docs/building-programs.md": ("Magistrate's manor (county magistracy)", "Country shrine (a village district's shrine)"),
}
_SECTION_HEAD = re.compile(r"^Research:(.*)$")
_MARKER = re.compile(r"<!--\s*Research:\s*(.*?)\s*-->", re.S)
_COMMENT = re.compile(r"<!--.*?-->", re.S)
_HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
_CONST_NAME = re.compile(r"^_?[A-Z][A-Z0-9_]*$")


class ClaimError(ValueError):
    """A claim line that does not parse; the message carries the grammar."""


@dataclass(frozen=True)
class Claim:
    """One claim: what is decided, what backs it, and an optional account of what the code does."""

    label: str
    backing: str  # one of CLASSES, or "POINTER"
    pointers: tuple[str, ...]
    account: str
    line: str

    def normalized(self) -> str:
        """The claim line as it enters a fingerprint: whitespace collapsed, each pointer reduced to its heading id."""
        return POINTER.sub(lambda m: m.group(2) + (m.group(3) or ""), " ".join(self.line.split()))


def parse_claim(line: str) -> Claim:
    """One claim line, or ClaimError naming what is wrong and the grammar."""
    text = " ".join(line.split())
    label, sep, rest = text.partition(" - ")
    if not sep or not label.strip() or not rest.strip():
        raise ClaimError(f"`{text}` has no `<label> - <backing>`")
    backing, _, account = rest.partition(": ")
    backing = backing.strip()
    head = backing.split(" ", 1)[0]
    if head == "GUESS" and backing != head:  # a guess a drawing page records, named (feature 316, the audit's second round)
        parts = [p.strip() for p in backing[len("GUESS") :].split(",")]
        if not all((m := POINTER.fullmatch(p)) and m.group(3) for p in parts):
            raise ClaimError(f"`{text}`: `GUESS` names the drawing page that records it (`...drawing.html`), or nothing")
        return Claim(label.strip(), "GUESS", tuple(parts), account.strip(), text)
    if head in CLASSES and head != "DEVIATION":
        if backing != head:
            raise ClaimError(f"`{text}`: `{head}` takes no pointer")
        return Claim(label.strip(), head, (), account.strip(), text)
    kind, tail = ("DEVIATION", backing[len("DEVIATION") :].strip()) if head == "DEVIATION" else ("POINTER", backing)
    parts = [p.strip() for p in tail.split(",")]
    if not tail or not all(POINTER.fullmatch(p) for p in parts):
        raise ClaimError(f"`{text}`: the backing `{backing}` is not question files or a class")
    return Claim(label.strip(), kind, tuple(parts), account.strip(), text)


def _section_span(lines: list[str]) -> tuple[int, int, bool] | None:
    """(header index, end index, flat) of the `Research:` section in docstring lines, or None.

    Indented: each claim is a line indented under the header, and a blank or unindented line ends it. FLAT: a docstring whose
    FIRST line is the header is dedented whole by `inspect.cleandoc` (and by `ruff format`), so its claims stand at column 0
    under it - there the section runs to the first blank line (found by writer G11, feature 316)."""
    for i, raw in enumerate(lines):
        if not _SECTION_HEAD.match(raw):
            continue
        flat = i == 0 and len(lines) > 1 and bool(lines[1].strip()) and not lines[1].startswith(" ")
        end = i + 1
        while end < len(lines) and lines[end].strip() and (flat or lines[end].startswith(" ")):
            end += 1
        return i, end, flat
    return None


def section_lines(doc: str | None) -> list[str] | None:
    """The raw claim lines of a docstring's `Research:` section (continuations joined), or None when it has none.

    The section opens at a line `Research:` (or `Research: <one claim>`) at the docstring's own indentation; each claim is a
    line indented under it, a line indented deeper continues the claim above, and a blank line or an unindented line ends it.
    In a FLAT section (`_section_span`) a line with no ` - ` continues the claim above.
    """
    if not doc:
        return None
    lines = doc.expandtabs().split("\n")
    span = _section_span(lines)
    if span is None:
        return None
    i, end, flat = span
    head = _SECTION_HEAD.match(lines[i])
    out = [head.group(1).strip()] if head and head.group(1).strip() else []
    base: int | None = None
    for nxt in lines[i + 1 : end]:
        indent = len(nxt) - len(nxt.lstrip())
        if flat:
            if " - " in nxt or not out:
                out.append(nxt.strip())
            else:
                out[-1] += " " + nxt.strip()
        elif base is None or indent <= base:
            base = indent if base is None else base
            out.append(nxt.strip())
        else:
            out[-1] += " " + nxt.strip()
    return out


def strip_section(doc: str) -> str:
    """A docstring with its `Research:` section removed - what a page renders as prose (the walk-through)."""
    lines = doc.split("\n")
    span = _section_span(lines)
    if span is None:
        return doc.rstrip()
    i, end, _flat = span
    return "\n".join(lines[:i] + lines[end:]).rstrip()


def claims_of(doc: str | None) -> tuple[list[Claim], list[str]]:
    """(claims, errors) of one docstring; an error is a line that does not parse, with the grammar."""
    claims: list[Claim] = []
    errors: list[str] = []
    for line in section_lines(doc) or []:
        try:
            claims.append(parse_claim(line))
        except ClaimError as exc:
            errors.append(str(exc))
    if section_lines(doc) == []:
        errors.append("an empty `Research:` section")
    return claims, errors


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


@dataclass
class Unit:
    """A function, method, class, constant or procedure section, with its claims (own or inherited) and its code's core."""

    path: str
    qualname: str
    kind: str
    lineno: int
    end_lineno: int
    claims: list[Claim]
    inherited: bool
    core: str
    errors: list[str] = field(default_factory=list)
    names: tuple[str, ...] = ()

    def key(self, claim: Claim) -> str:
        """The index key of one claim of this unit."""
        return f"{self.path}::{self.qualname}#{claim.label}"

    def code(self, claim: Claim) -> str:
        """The code fingerprint of one claim: the core plus the normalized claim line."""
        return _sha(self.core + "\x1f" + claim.normalized())


def _strip_docstrings(tree: ast.AST) -> None:
    """Remove, IN PLACE, the docstring of every module, function and class in `tree` - once per parsed module, after the
    claims are read, so no unit's dump needs a copy (a copy per unit cost the whole scope 9 s; measured 2026-10-02)."""
    for sub in ast.walk(tree):
        if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)) and sub.body and _is_doc_literal(sub.body[0]):
            sub.body = sub.body[1:] or [ast.Pass()]


def _dump(node: ast.AST) -> str:
    return ast.dump(node, include_attributes=False)


def _is_doc_literal(stmt: ast.stmt | None) -> bool:
    return isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str)


def _const_target(stmt: ast.stmt) -> str | None:
    """The constant a module-level assignment binds, when it binds exactly one upper-case name."""
    if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name):
        name = stmt.targets[0].id
    elif isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name) and stmt.value is not None:
        name = stmt.target.id
    else:
        return None
    return name if _CONST_NAME.match(name) else None


def module_constants(tree: ast.Module) -> dict[str, str]:
    """name -> the dump of its value, for every module-level constant of one module."""
    out: dict[str, str] = {}
    for stmt in tree.body:
        name = _const_target(stmt)
        if name is not None:
            value = stmt.value  # type: ignore[union-attr]
            out[name] = _dump(value) if value is not None else ""
    return out


def import_table(tree: ast.Module, module: str, is_package: bool) -> dict[str, tuple[str, str]]:
    """local name -> (module, name) for every `from X import Y [as Z]` at any depth, relative imports resolved."""
    pkg = module if is_package else module.rsplit(".", 1)[0]
    out: dict[str, tuple[str, str]] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            src = resolve_from(pkg, node)
            for alias in node.names:
                out[alias.asname or alias.name] = (src, alias.name)
    return out


def resolve_from(pkg: str, node: ast.ImportFrom) -> str:
    """The absolute module a `from ... import` names, from the importing package."""
    if not node.level:
        return node.module or ""
    base = pkg.split(".")
    base = base[: len(base) - (node.level - 1)]
    return ".".join(base) + (f".{node.module}" if node.module else "")


def _own_statements(node: ast.AST) -> ast.AST:
    """A class as its own statements only (each method is a unit of its own); any other node as it is."""
    if not isinstance(node, ast.ClassDef):
        return node
    shell = ast.ClassDef(name=node.name, bases=node.bases, keywords=node.keywords, decorator_list=node.decorator_list, type_params=getattr(node, "type_params", []))
    shell.body = [s for s in node.body if not isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))] or [ast.Pass()]
    return shell


def nameless_dump(node: ast.AST) -> str:
    """A unit's syntax tree without its own NAME (and, for a class, without its methods), so a unit renamed or moved with
    its code intact keeps its core - the push matches it across keys (spec FR-010, plan D7). A constant is its value."""
    if isinstance(node, (ast.Assign, ast.AnnAssign)):
        return _dump(node.value) + ("" if isinstance(node, ast.Assign) else "\x1c" + _dump(node.annotation))  # type: ignore[arg-type]
    if isinstance(node, ast.Module):  # the module unit: its import-time calls
        return _dump(node)
    shell = _own_statements(node)
    name = shell.name  # type: ignore[attr-defined]
    shell.name = ""  # type: ignore[attr-defined]
    try:
        return _dump(shell)
    finally:
        shell.name = name  # type: ignore[attr-defined]


def _is_overload(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """An `@overload` (or `@typing.overload`) stub: found by the audit's batch 19, where `labels/placer.py`'s stubs of `place`
    took the implementation's key and its bundle showed a stub."""
    return any((isinstance(d, ast.Name) and d.id == "overload") or (isinstance(d, ast.Attribute) and d.attr == "overload") for d in fn.decorator_list)


def module_aliases(tree: ast.Module, table: dict[str, tuple[str, str]], modules: set[str]) -> dict[str, str]:
    """local name -> in-scope module, for `from pkg import mod [as m]` and `import pkg.mod as m` - so `m.NAME` is a read
    of that module's constant (36 such reads in `hamletgen/ways` alone, counted 2026-10-02)."""
    out = {local: f"{src}.{real}" for local, (src, real) in table.items() if f"{src}.{real}" in modules}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out |= {a.asname: a.name for a in node.names if a.asname and a.name in modules}
    return out


def module_units(
    source: str | ast.Module, path: str, module: str = "", is_package: bool = False, constants: dict[str, dict[str, str]] | None = None, every_module_unit: bool = False
) -> tuple[list[Claim], list[str], list[Unit]]:
    """(the module's claims, its errors, its units) for one Python source text (or its freshly parsed tree, which is
    consumed: its docstrings are stripped in place).

    `constants` maps an in-scope module to its constants (module_constants); a unit's core takes the value of every one it
    names, resolved through this module's own constants and its `from` imports. Without it, only the module's own."""
    tree = ast.parse(source) if isinstance(source, str) else source
    mod_claims, mod_errors = claims_of(ast.get_docstring(tree))
    constants = constants if constants is not None else {}
    own = module_constants(tree)
    table = import_table(tree, module, is_package) if module else {}
    # every unit and its docstring (and a constant's literal), read BEFORE the docstrings are stripped
    found: list[tuple[str, str, ast.AST, str | None]] = []

    def walk(body: list[ast.stmt], prefix: str, in_class: bool) -> None:
        for stmt in body:
            if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if _is_overload(stmt):  # a typing stub shares its implementation's name; the implementation is the unit
                    continue
                found.append((prefix + stmt.name, "method" if in_class else "function", stmt, ast.get_docstring(stmt)))
            elif isinstance(stmt, ast.ClassDef):
                found.append((prefix + stmt.name, "class", stmt, ast.get_docstring(stmt)))
                walk(stmt.body, f"{prefix}{stmt.name}.", True)

    walk(tree.body, "", False)
    for i, stmt in enumerate(tree.body):
        name = _const_target(stmt)
        if name is not None:
            nxt = tree.body[i + 1] if i + 1 < len(tree.body) else None
            found.append((name, "constant", stmt, inspect.cleandoc(nxt.value.value) if _is_doc_literal(nxt) else None))  # type: ignore[union-attr]
    # THE MODULE ITSELF IS A UNIT where its body CALLS something at import - a `register_knob(Knob(...))` table (found by
    # writer G11 on `settlement/_knobs.py`, feature 316): those statements belong to no function, class or constant, and a
    # module docstring's claims about them would otherwise fingerprint nothing. Its claims are the module's own.
    calls = [st for st in tree.body if isinstance(st, ast.Expr) and isinstance(st.value, ast.Call)]
    if calls and (mod_claims or every_module_unit):  # the push's base needs the core even where no claim stood yet
        shell = ast.Module(body=calls, type_ignores=[])
        found.append(("<module>", "module", shell, None))
        shell.lineno, shell.end_lineno = calls[0].lineno, calls[-1].end_lineno  # type: ignore[attr-defined]
    _strip_docstrings(tree)

    aliases = module_aliases(tree, table, set(constants))

    def values(node: ast.AST) -> tuple[str, tuple[str, ...]]:
        """`NAME=<value>` for each in-scope constant the node reads - by its own name, through a `from` import, or as
        `<module alias>.NAME` - keyed by the constant's NAME and not its module, so a file split that moves a constant
        owes nothing (plan review, 2026-10-02)."""
        hits: set[str] = set()
        for sub in ast.walk(node):
            if isinstance(sub, ast.Name):
                if sub.id in own:
                    hits.add(f"{sub.id}={own[sub.id]}")
                elif sub.id in table and table[sub.id][1] in constants.get(table[sub.id][0], {}):
                    src, real = table[sub.id]
                    hits.add(f"{real}={constants[src][real]}")
            elif isinstance(sub, ast.Attribute) and isinstance(sub.value, ast.Name) and sub.value.id in aliases:
                mod = aliases[sub.value.id]
                if sub.attr in constants.get(mod, {}):
                    hits.add(f"{sub.attr}={constants[mod][sub.attr]}")
        found_ = tuple(sorted(hits))
        return "\x1e".join(found_), found_

    units: list[Unit] = []
    for qual, kind, node, doc in found:
        claims, errors = claims_of(doc)
        inherited = not claims and not errors and kind != "module"
        if kind == "module":
            claims = list(mod_claims)
        read = node.value if isinstance(node, (ast.Assign, ast.AnnAssign)) and node.value is not None else _own_statements(node)  # a constant names itself only as its target
        dump, (vals, names) = nameless_dump(node), values(read)
        end = node.end_lineno or node.lineno  # type: ignore[attr-defined]
        units.append(Unit(path, qual, kind, node.lineno, end, claims or (mod_claims if inherited else []), inherited, _sha(dump + "\x1d" + vals), errors, names))  # type: ignore[attr-defined]
    units.sort(key=lambda u: u.lineno)
    return mod_claims, mod_errors, units


def doc_units(text: str, path: str, tops: tuple[str, ...] | None) -> list[Unit]:
    """The sections of one procedure document as units: every `##`-`####` heading, or only those under `tops`."""
    lines = text.split("\n")
    heads = [(i, len(m.group(1)), m.group(2)) for i, line in enumerate(lines) if (m := _HEADING.match(line))]
    units: list[Unit] = []
    taking: int | None = None  # the level of the top section being taken, when `tops` restricts
    for j, (i, level, title) in enumerate(heads):
        if tops is not None:
            if title in tops:
                taking = level
            elif taking is not None and level <= taking:
                taking = None
            if taking is None:
                continue
        elif level < 2 or level > 4:
            continue
        end = heads[j + 1][0] if j + 1 < len(heads) else len(lines)
        body = "\n".join(lines[i + 1 : end])
        claims: list[Claim] = []
        errors: list[str] = []
        for raw in _MARKER.findall(body):
            try:
                claims.append(parse_claim(raw))
            except ClaimError as exc:
                errors.append(str(exc))
        core = _sha(" ".join(_COMMENT.sub(" ", body).split()))
        units.append(Unit(path, title, "section", i + 1, end, claims, False, core, errors))
    return units


def reexported(constants: dict[str, dict[str, str]], tables: dict[str, dict[str, tuple[str, str]]]) -> dict[str, dict[str, str]]:
    """Each module's constants with those it RE-EXPORTS added (`from .other import NAME` of a constant), followed through any
    chain to the defining module - so a reader of a re-exported constant is owed when its value changes (22 such reads in
    scope, measured 2026-10-02: `hamletgen/plan` reads `GROVE_SIDES` through `hamletgen/consts`)."""
    out = {m: dict(c) for m, c in constants.items()}
    changed = True
    while changed:
        changed = False
        for mod, table in tables.items():
            for local, (src, real) in table.items():
                if real in out.get(src, {}) and local not in out.setdefault(mod, {}):
                    out[mod][local] = out[src][real]
                    changed = True
    return out


def _module_name(path: Path, skill: Path) -> tuple[str, bool]:
    rel = path.relative_to(skill).with_suffix("")
    parts = rel.parts
    if parts[-1] == "__init__":
        return ".".join(parts[:-1]), True
    return ".".join(parts), False


def engine_modules(skill: Path) -> dict[str, Path]:
    """module name -> file, for every module of the engine package under the skill root."""
    out: dict[str, Path] = {}
    for p in sorted((skill / "l7r" / "diagram").rglob("*.py")):
        if "__pycache__" not in p.parts:
            out[_module_name(p, skill)[0]] = p
    return out


def _imports_of(tree: ast.Module, module: str, is_package: bool, known: dict[str, Path]) -> set[str]:
    pkg = module if is_package else module.rsplit(".", 1)[0]
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            src = resolve_from(pkg, node)
            names.add(src)
            names.update(f"{src}.{a.name}" for a in node.names)
    out: set[str] = set()
    for name in names:
        while name and name not in known:
            name = name.rsplit(".", 1)[0] if "." in name else ""
        while name:  # importing a submodule runs every package above it
            if name in known:
                out.add(name)
            name = name.rsplit(".", 1)[0] if "." in name else ""
    return out


def scope(skill: Path, root: str = ROOT_PACKAGE) -> dict[str, Path]:
    """module -> file for the root package and every engine module it imports, directly or through others (FR-002)."""
    return {m: p for m, (p, _t) in _scope_trees(skill, root).items()}


def _scope_trees(skill: Path, root: str = ROOT_PACKAGE) -> dict[str, tuple[Path, ast.Module]]:
    known = engine_modules(skill)
    todo = [m for m in known if m == root or m.startswith(root + ".")]
    seen: dict[str, tuple[Path, ast.Module]] = {}
    while todo:
        mod = todo.pop()
        if mod in seen:
            continue
        tree = ast.parse(known[mod].read_text(encoding="utf-8"))
        seen[mod] = (known[mod], tree)
        todo += [m for m in _imports_of(tree, mod, known[mod].name == "__init__.py", known) if m not in seen]
    return dict(sorted(seen.items()))


def all_units(skill: Path, repo_prefix: str = "", every_module_unit: bool = False) -> Iterator[tuple[Unit, list[str]]]:
    """Every unit in scope with its module's errors: the code (FR-002), then the procedure sections (FR-003). Paths are
    repository-relative, as the index keys them."""
    mods = _scope_trees(skill)
    constants = reexported({m: module_constants(t) for m, (_p, t) in mods.items()}, {m: import_table(t, m, p.name == "__init__.py") for m, (p, t) in mods.items()})
    for mod, (p, tree) in mods.items():
        rel = repo_prefix + p.relative_to(skill).as_posix()
        _claims, errors, units = module_units(tree, rel, mod, p.name == "__init__.py", constants, every_module_unit)
        for unit in units:
            yield unit, errors
    for doc, tops in PROCEDURES.items():
        if not (skill / doc).is_file():  # a tree read at an older commit (the push's base) may predate a document
            continue
        text = (skill / doc).read_text(encoding="utf-8")
        for unit in doc_units(text, repo_prefix + doc, tops):
            yield unit, []


def coverage(units: Iterable[tuple[Unit, list[str]]], questions: set[str]) -> list[str]:
    """Every coverage failure (FR-002, FR-003): a unit with no claim own or inherited, a claim that does not parse, a pointer
    to a question file that does not exist (`questions` holds the file names). Each line names the unit and the fix."""
    problems: list[str] = []
    seen: set[tuple[str, str]] = set()
    for unit, module_errors in units:
        where = f"{unit.path}:{unit.lineno} {unit.qualname}"
        for err in module_errors:
            if (unit.path, err) not in seen:
                seen.add((unit.path, err))
                problems.append(f"{unit.path} module docstring: {err}")
        problems += [f"{where}: {err}" for err in unit.errors]
        if not unit.claims and not unit.errors:
            what = "a `<!-- Research: <label> - <backing> -->` comment" if unit.kind == "section" else "a `Research:` claim (own, or in its module docstring)"
            problems.append(f"{where}: no claim - add {what}")
        for claim in unit.claims:
            for ptr in claim.pointers:
                if ptr.rsplit("/", 1)[1] not in questions:
                    problems.append(f"{where}: `{ptr}` names no question file (find it with a glob on its heading id; `make fragment-move` renames)")
    return problems
