"""The research claims of the Rust phases, read from their doc comments (feature 444 T17, `dev/rust-tooling.md` "research claims").

WHY: a rebuilt phase's `Research:` section moves from a docstring to its `///` doc comment, and the claims index, its gate, the
bundles and the triage read UNITS (`claims.Unit`) - so this reader turns a `.rs` file into the same units the Python reader
writes, and the process downstream is unchanged. A unit is an item - `fn`, `struct`, `enum`, `trait`, `const`, `static`, `type`
- or a method of an `impl` block (`Type.method`); its claims are the `Research:` section of the `///` lines above it (attributes
between them skipped), else the file's `//!` module doc's, inherited; its core is the item's comment-free tokens
(`codeid.rust_tokens`), so a doc-comment edit is wording and any change to what runs moves the core. A Python reader of the
Rust source rather than the `syn` parser the inventory first named: the units need an item's span and doc, which a brace
scan that skips strings, chars and comments gives, and the reader stays in the process that builds the index (a deliberate
deviation, recorded in the inventory).
"""

from __future__ import annotations

import importlib.util
import pathlib
import re

from l7r.diagram.tools.claims import Unit, _sha, claims_of

_ITEM = re.compile(
    r"^\s*(?:pub(?:\([^)]*\))?\s+)?(?:(?:const|async|unsafe|extern\s+\"C\")\s+)*"
    r"(fn|struct|enum|trait|impl|const|static|type|mod)\b\s*(?:<[^>]*>\s*)?([A-Za-z_][A-Za-z0-9_]*)?"
)
_ROOT = pathlib.Path(__file__).resolve().parents[3]


def _codeid():  # noqa: ANN202 - scripts/gates/codeid.py by path: the one definition of "what runs" for a `.rs` file
    spec = importlib.util.spec_from_file_location("codeid", _ROOT / "scripts" / "gates" / "codeid.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _end(text: str, start: int) -> int:
    """The offset just past the item that opens at `start`: its matching `}`, or the `;` that ends a body-less item - strings,
    chars and comments skipped."""
    i, n, depth = start, len(text), 0
    while i < n:
        c = text[i]
        if text.startswith("//", i):
            j = text.find("\n", i)
            i = n if j < 0 else j
            continue
        if text.startswith("/*", i):
            j = text.find("*/", i + 2)
            i = n if j < 0 else j + 2
            continue
        if c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            i = j + 1
            continue
        if c == "'" and i + 2 < n and (text[i + 2] == "'" or text[i + 1] == "\\"):
            j = text.find("'", i + 2)
            i = n if j < 0 else j + 1
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i + 1
        elif c == ";" and depth == 0:
            return i + 1
        i += 1
    return n


def _items(text: str, base_line: int, prefix: str, in_impl: bool) -> list[tuple[str, str, int, int, str, str]]:
    """(qualname, kind, first line, last line, doc, item text) for each item in `text`, an `impl` block's methods inside it."""
    out: list[tuple[str, str, int, int, str, str]] = []
    lines = text.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    doc: list[str] = []
    k = 0
    while k < len(lines):
        stripped = lines[k].strip()
        if stripped.startswith("///"):
            doc.append(stripped[3:].removeprefix(" "))
            k += 1
            continue
        if stripped.startswith("#[") or stripped.startswith("#!["):
            k += 1
            continue
        m = _ITEM.match(lines[k])
        if not m:
            if stripped and not stripped.startswith("//"):
                doc = []
            k += 1
            continue
        start = offsets[k]
        end = _end(text, start)
        last = next(i for i in range(k, len(lines)) if offsets[i + 1] >= end)
        body = text[start:end]
        word, name = m.group(1), m.group(2) or ""
        if word == "impl":
            target = re.search(r"\bfor\s+([A-Za-z_][A-Za-z0-9_]*)", body.split("{", 1)[0]) or re.search(r"impl\s*(?:<[^>]*>\s*)?([A-Za-z_][A-Za-z0-9_]*)", body)
            inner = body.find("{")
            if target and inner >= 0:
                head_lines = body[: inner + 1].count("\n")
                out += _items(body[inner + 1 : -1], base_line + k + head_lines, f"{prefix}{target.group(1)}.", True)
        elif word != "mod" and name:
            kind = ("method" if in_impl else "function") if word == "fn" else "constant" if word in ("const", "static") else "class"
            out.append((prefix + name, kind, base_line + k + 1, base_line + last + 1, "\n".join(doc), body))
        doc = []
        k = last + 1
    return out


def rust_units(source: str, path: str) -> tuple[list[str], list[Unit]]:
    """(the file's errors, its units) for one `.rs` source text: each item's own claims, else the `//!` module doc's, inherited."""
    module_doc = "\n".join(line.strip()[3:].removeprefix(" ") for line in source.splitlines() if line.strip().startswith("//!"))
    mod_claims, mod_errors = claims_of(module_doc or None)
    tokens = _codeid().rust_tokens
    units: list[Unit] = []
    for qual, kind, first, last, doc, body in _items(source, 0, "", False):
        claims, errors = claims_of(doc or None)
        inherited = not claims and not errors
        units.append(Unit(path, qual, kind, first, last, claims or (mod_claims if inherited else []), inherited, _sha(tokens(body.encode()).decode()), errors))
    return mod_errors, units


def all_rust_units(root: pathlib.Path, repo_prefix: str = "") -> list[tuple[Unit, list[str]]]:
    """Every unit of every `.rs` under `rust/` (`target/` pruned), with its file's errors - the Rust phases are all in the
    hamlet scope, so every unit owes a claim, own or inherited, as the scope's Python does."""
    out: list[tuple[Unit, list[str]]] = []
    base = root / "rust"
    for p in sorted(base.rglob("*.rs")) if base.is_dir() else []:
        if "target" in p.relative_to(base).parts:
            continue
        errors, units = rust_units(p.read_text(encoding="utf-8"), repo_prefix + p.relative_to(root).as_posix())
        out += [(u, errors) for u in units]
    return out


class RustItem:
    """A Rust item a `Steps:` line names as `<path>.rs::<qualname>` (`tools/placement_stages.py`): its doc comment as its
    `__doc__`, so the page reads a Rust step as it reads a Python one (`dev/rust-tooling.md` "the placement-stages page"),
    its unit for the claims under it."""

    def __init__(self, unit: Unit, doc: str) -> None:
        self.unit = unit
        self.__doc__ = doc
        self.__qualname__ = unit.qualname
        self.__name__ = unit.qualname.rsplit(".", 1)[-1]


def resolve(root: pathlib.Path, ref: str) -> RustItem:
    """The item `ref` (`rust/phases/src/field.rs::Basin.area`) names, or LookupError."""
    path, _sep, qual = ref.partition("::")
    source = (root / path).read_text(encoding="utf-8")
    _errors, units = rust_units(source, path)
    docs = {q: d for q, _k, _f, _l, d, _b in _items(source, 0, "", False)}
    for u in units:
        if u.qualname == qual:
            return RustItem(u, docs[qual])
    raise LookupError(ref)
