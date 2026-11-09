"""The docstring-blind code id: what a piece of Python DOES, without what it says about itself (feature 426, D2).
# TOOL_RECORD: its main is asked only by the Rust gate, once a run, and the gate reports its failure (feature 449 T062)

A `.py` file's id is its AST with every docstring dropped and no line or column attributes (`ast.dump`'s default), so a
comment, a docstring, a constant's claim string, a blank line or reformatting leaves it alone, and any token that runs moves
it. One definition, read three ways:

- `semantic_bytes` - a whole file, what the Rust gate's stamp hashes for `make done` (asked by `rust/gate/src/codeid.rs`, stdlib
  only, because it runs inside the guards and must not import the engine package) and `ci/delta.py` through it; the engine's
  keys read it through `l7r/diagram/pipeline/codeid.py`, a shim that loads this file;
- `split_ids` - a module's top level and each function, what the roll and map key (`gencache.split_sources`) hashes per
  executed function;
- `strip_docstrings` - the rule itself, for a caller holding a tree.

WHY (GM 2026-08-26, feature 133 T11; feature 426): a record-the-why comment is REQUIRED at the point of change in this project
and the research claims live in docstrings, so a key that counted them re-ran the gate (until 133) and re-rolled every seed
through an edited function (until 426: feature 417's claims rounds re-rolled 54 seeds a relabel). Bytecode was priced and
declined: `co_consts` carries docstrings and the line table every comment's line shift. A file that does not parse is hashed as
its bytes - unparseable is still content.

What is CONTENT is not stripped here but by the caller choosing bytes: the interactive class registry's docstrings are the
modal text (`interactive/classes/_base.py` returns `cls.__doc__`), so `gencache` and `render_cache` key `interactive/` on its
bytes, as `gate-stamp`'s `RAW_AREAS` do.

Research: hashing plumbing - NONE
"""

from __future__ import annotations

import ast
import copy
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
from pathlib import Path

_FUNCS = (ast.FunctionDef, ast.AsyncFunctionDef)
#: THE ENGINE PATHS of a landing - a delta with one owes the landing cohort (`l7r.diagram.ci.delta.is_engine`'s list, feature 132
#: FR-008). One definition, read by `scripts/land.py` and by the cohort's counter-only test (`cohort_known.counter_only`, feature
#: 446), so the two can never disagree about what a counter-only delta may leave unchecked
ENGINE = re.compile(r"^(l7r/.*\.py|pool/.*\.gen\.py|pool/.*\.json|rust/.*\.rs|rust/(?:.*/)?Cargo\.(?:toml|lock))$")  # rust/: 444 T17


def strip_docstrings(tree: ast.AST, keep_module_docstring: bool = False) -> ast.AST:
    """`tree` with EVERY bare string statement removed, in place: a body's docstring and the claim string after a constant's
    assignment alike (feature 385 T57, the round arbiter's fix on hour:385-approach-checklist@20) - Python evaluates a bare
    string statement and discards it; no token of it runs. `keep_module_docstring` keeps a module's own docstring, for a
    script that prints it as its usage (feature 426: `ci/state.tooling_hash`)."""
    head = tree.body[0] if keep_module_docstring and isinstance(tree, ast.Module) and tree.body else None
    for node in ast.walk(tree):
        for field in ("body", "orelse", "finalbody"):
            stmts = getattr(node, field, None)
            if isinstance(stmts, list):
                stmts[:] = [s for s in stmts if s is head or not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and isinstance(s.value.value, str))]
    return tree


def rust_tokens(data: bytes) -> bytes:
    """What runs, for a `.rs` file: its tokens with every comment dropped - line, block (nested) and doc comments alike, so a
    `///` claim or `Steps:` edit is wording, as a docstring is - and whitespace between tokens collapsed; string, raw-string,
    byte-string and char literals kept whole, a lifetime (`'a`) a token (feature 444 T17, `dev/rust-tooling.md` "the docstring-
    blind code id"). A file that is not UTF-8 is its bytes verbatim."""
    try:
        s = data.decode("utf-8")
    except UnicodeDecodeError:
        return data
    out: list[str] = []
    cur: list[str] = []
    i, n = 0, len(s)

    def flush() -> None:
        if cur:
            out.append("".join(cur))
            cur.clear()

    while i < n:
        c = s[i]
        if s.startswith("//", i):
            flush()
            j = s.find("\n", i)
            i = n if j < 0 else j
        elif s.startswith("/*", i):
            flush()
            depth, i = 1, i + 2
            while i < n and depth:
                if s.startswith("/*", i):
                    depth, i = depth + 1, i + 2
                elif s.startswith("*/", i):
                    depth, i = depth - 1, i + 2
                else:
                    i += 1
        elif c in "rb" and (m := _RAW.match(s, i)):
            flush()
            end = s.find('"' + m.group(1), m.end())
            end = n if end < 0 else end + 1 + len(m.group(1))
            out.append(s[i:end])
            i = end
        elif c == '"' or (c == "b" and s.startswith('b"', i)):
            flush()
            j = i + (2 if c == "b" else 1)
            while j < n and s[j] != '"':
                j += 2 if s[j] == "\\" else 1
            out.append(s[i : j + 1])
            i = j + 1
        elif c == "'":
            flush()
            if i + 1 < n and s[i + 1] == "\\":
                j = s.find("'", i + 2)
            elif i + 2 < n and s[i + 2] == "'":
                j = i + 2
            else:  # a lifetime or a label: `'a`
                j = i
                while j + 1 < n and (s[j + 1].isalnum() or s[j + 1] == "_"):
                    j += 1
                out.append(s[i : j + 1])
                i = j + 1
                continue
            j = n - 1 if j < 0 else j
            out.append(s[i : j + 1])
            i = j + 1
        elif c.isspace():
            flush()
            i += 1
        elif c.isalnum() or c == "_":
            cur.append(c)
            i += 1
        else:
            flush()
            out.append(c)
            i += 1
    flush()
    return "\x00".join(out).encode()


_RAW = re.compile(r'b?r(#*)"')


def semantic_bytes(data: bytes, name: str, keep_module_docstring: bool = False) -> bytes:
    """What runs, for a `.py` file: its docstring-free AST dumped without attributes (its own module docstring kept with
    `keep_module_docstring`); for a `.rs` file, its comment-free tokens (`rust_tokens`); any other file, or one that does not
    parse, its bytes verbatim."""
    if name.endswith(".rs"):
        return rust_tokens(data)
    if not name.endswith(".py"):
        return data
    try:
        tree = ast.parse(data)
    except SyntaxError, ValueError:
        return data
    return ast.dump(strip_docstrings(tree, keep_module_docstring)).encode()


def _plain(v: ast.expr) -> bool:
    """A name, or an attribute chain on one (`self.ring`): read, never called."""
    return isinstance(v, ast.Name) or (isinstance(v, ast.Attribute) and _plain(v.value))


def _counter_value(v: ast.expr) -> bool:
    """A counter's increment, in the forms feature 446's FR-001 defines: a literal, a name,
    `len(<name or attribute>)`, `<name>.size`, `max(len(<name>) - <literal>, <literal>)`, or a product of these - nothing that
    calls engine code, so the block can do no more than add to a counter."""
    if isinstance(v, ast.Constant) or isinstance(v, ast.Name):
        return True
    if isinstance(v, ast.Attribute) and v.attr == "size" and isinstance(v.value, ast.Name):
        return True
    if isinstance(v, ast.BinOp) and isinstance(v.op, ast.Mult):
        return _counter_value(v.left) and _counter_value(v.right)
    if isinstance(v, ast.Call) and isinstance(v.func, ast.Name) and not v.keywords:
        if v.func.id == "len" and len(v.args) == 1:
            return _plain(v.args[0])
        if v.func.id == "max" and len(v.args) == 2 and isinstance(v.args[1], ast.Constant):
            d = v.args[0]
            return isinstance(d, ast.BinOp) and isinstance(d.op, ast.Sub) and isinstance(d.right, ast.Constant) and isinstance(d.left, ast.Call) and _counter_value(d.left)
    return False


def is_counter_block(s: ast.stmt) -> bool:
    """A COUNTER BLOCK (feature 446, FR-001): `if __debug__:` with no `else`, its body nothing but `OPS["<str>"] += / -= <value>`
    (`_counter_value`). Any other `if __debug__:` - an `else`, a call, a write elsewhere - is code: a cohort rolls without `-O`, so
    its body runs, and only a write to the counters is provably inert."""
    if not (isinstance(s, ast.If) and isinstance(s.test, ast.Name) and s.test.id == "__debug__" and not s.orelse and s.body):
        return False
    for b in s.body:
        if not (isinstance(b, ast.AugAssign) and isinstance(b.op, (ast.Add, ast.Sub)) and isinstance(b.target, ast.Subscript)):
            return False
        tgt = b.target
        if not (isinstance(tgt.value, ast.Name) and tgt.value.id == "OPS" and isinstance(tgt.slice, ast.Constant) and isinstance(tgt.slice.value, str)):
            return False
        if not _counter_value(b.value):
            return False
    return True


def strip_counters(tree: ast.AST) -> ast.AST:
    """`tree` with every counter block removed, in place (`is_counter_block`)."""
    for node in ast.walk(tree):
        for field in ("body", "orelse", "finalbody"):
            stmts = getattr(node, field, None)
            if isinstance(stmts, list):
                stmts[:] = [s for s in stmts if not is_counter_block(s)]
    return tree


def debug_free_bytes(data: bytes, name: str) -> bytes:
    """A `.py` file's semantic bytes (`semantic_bytes`) with every counter block removed; any other file, or one that does not
    parse, its bytes. Two versions are COUNTER-ONLY-EQUAL when these are equal (feature 446, FR-001)."""
    if not name.endswith(".py"):
        return data
    try:
        tree = ast.parse(data)
    except SyntaxError, ValueError:
        return data
    return ast.dump(strip_counters(strip_docstrings(tree))).encode()


# THE CONTENT ID AND ITS KEPT CACHE (feature 449 T063, slice 1; moved from `gate-stamp.py`, the round arbiter's `ask:449-T063-slices`): the one Python library for the callers phases 3 and 4 port.

_CACHE_NAME = "semantic-id-cache-2.json"  # -2: feature 385 T57 changed the rule, so the old entries are not reused


def git_blob_id(data: bytes) -> str:
    """The id git gives these bytes as a blob: sha1 over the 'blob <len>\\0' header + bytes. Computed
    here so a caller with contents in hand gets the same key `git ls-tree` and `git hash-object` print."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()  # noqa: S324 - an identity, not a security hash


def content_id(data: bytes, name: str, root: Path | None = None) -> str:
    """sha256 of `semantic_bytes(data, name)`, memoized per repository under `.git/` by the sha of
    the RAW bytes. Parsing and dumping ~280 files cost 13 s per check (measured 2026-08-26: the
    `already verified` answer went from 1 s to 14 s), and the raw sha -> semantic id map is a pure
    function, so it is computed once per distinct file content and read back forever after. Without a
    repository root the id is computed directly - correctness never depends on the cache."""
    raw = git_blob_id(data)  # the cache is keyed by GIT's own blob id, so `ls-tree`/`hash-object` answer a hit without reading the file (T27)
    if not name.endswith((".py", ".rs")):  # `.rs`: its comment-free tokens (feature 444 T17)
        return raw
    table = _cache_table(root)
    if raw in table:
        return table[raw]
    sem = hashlib.sha256(semantic_bytes(data, name)).hexdigest()
    table[raw] = sem
    _cache_dirty.add(id(table))
    _flush_cache(root)
    return sem


# THE CACHE IS LOADED ONCE PER PROCESS AND WRITTEN ONCE PER MISS, not read and rewritten per file:
# the first cut re-parsed the 27 KB JSON for each of ~280 files, and a warm hash pass still cost
# 2.7 s (measured 2026-08-26 in tests/tooling/ci/test_state.py). Keyed by the cache path so two roots in one
# process (the tests' fixture repos) never share a table.
_cache_tables: dict[Path, dict[str, str]] = {}
_cache_dirty: set[int] = set()


def _git_dir(root: Path) -> Path | None:
    """The directory to keep this repository's gate state in, or None if it cannot be determined.

    NOT `root / ".git"`. **In a git WORKTREE, `.git` is a FILE**, not a directory - it contains a
    single `gitdir: /path/to/real/.git/worktrees/<name>` line - so writing a path underneath it
    raises `NotADirectoryError`. That matters here rather than being a curiosity, because
    constitution Principle XIII MANDATES a detached worktree for the regression baseline
    (`git worktree add --detach`), so `make done` in the very tree the procedure tells you to
    create used to crash this module once per area (measured 2026-08-30, feature 161: the gate ran
    and passed, only the recording failed, and it failed noisily-but-non-fatally - the shape that
    gets scrolled past).

    `git rev-parse --git-common-dir` resolves to the SHARED git directory in both a plain checkout
    and a worktree, which is the right place for a stamp: it is keyed on content, and a worktree
    and its parent checking out the same content deserve the same answer.

    The `.is_dir()` guard that used to be inline here was doing half of this job already - it
    recognized that `.git` might not be a directory and simply gave up on the cache - which is why
    only the STAMP path crashed and the cache path did not.
    """
    # GUARD_EDIT_OK: fixing a slow path found while working (2026-09-28) - ASKED ONCE PER ROOT, NOT PER FILE.
    # `content_id` reaches this through `_cache_table` for every file hashed (and `_flush_cache` again per
    # miss), so one `make quick` status record ran `git rev-parse` 302 times: 0.66 s of its 0.85 s. Only a
    # FOUND directory is remembered - a root with none is asked again, since a test may `git init` it later.
    if root in _git_dirs and _git_dirs[root].is_dir():
        return _git_dirs[root]
    out = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--git-common-dir"],
        capture_output=True,
        text=True,
    )
    if out.returncode != 0:
        return None
    d = Path(out.stdout.strip())
    if not d.is_absolute():
        d = root / d
    if not d.is_dir():
        return None
    _git_dirs[root] = d
    return d


_git_dirs: dict[Path, Path] = {}


def _cache_path(root: Path | None) -> Path | None:
    if root is None:
        return None
    d = _git_dir(root)
    return (d / _CACHE_NAME) if d is not None else None


def _cache_table(root: Path | None) -> dict[str, str]:
    path = _cache_path(root)
    if path is None:
        return {}
    if path not in _cache_tables:
        table: dict[str, str] = {}
        if path.is_file():
            try:
                table = json.loads(path.read_text(encoding="utf-8"))
            except ValueError:
                table = {}
        _cache_tables[path] = table
    return _cache_tables[path]


def _flush_cache(root: Path | None) -> None:
    path = _cache_path(root)
    if path is not None and id(_cache_tables.get(path)) in _cache_dirty:
        # ATOMIC, AND MERGED WITH WHAT ANOTHER WRITER KEPT (feature 449 T062): the Rust gate writes this file too
        try:
            on_disk = json.loads(path.read_text(encoding="utf-8"))
        except OSError, ValueError:
            on_disk = {}
        merged = {**(on_disk if isinstance(on_disk, dict) else {}), **_cache_tables[path]}
        tmp = path.with_suffix(f".{os.getpid()}.tmp")
        tmp.write_text(json.dumps(merged), encoding="utf-8")
        tmp.replace(path)
        _cache_dirty.discard(id(_cache_tables[path]))


def ids_main(paths: list[str]) -> int:
    """`codeid.py --ids <file>...`: each file's id, one a line, in order (the Rust gate's one question of a run, the round arbiter's `ask:449-T062-py-id`)."""
    for name in paths:
        print(hashlib.sha256(semantic_bytes(pathlib.Path(name).read_bytes(), name)).hexdigest())
    return 0


def semantic_main(args: list[str]) -> int:
    """`--semantic keep|strip <path>...`: each file's semantic bytes as `<length>\\n<bytes>`, for the Rust gate's tooling and config hashes (feature 449 T72)."""
    keep, out = args[0] == "keep", sys.stdout.buffer
    for name in args[1:]:
        data = semantic_bytes(pathlib.Path(name).read_bytes(), name, keep_module_docstring=keep)
        out.write(f"{len(data)}\n".encode())
        out.write(data)
    return 0


def debug_free_equal_main(args: list[str]) -> int:
    """`--debug-free-equal <a> <b> [<a> <b> ...]`: exit 0 when each pair is the same but for counter blocks (feature 446), for the Rust gate."""
    read = lambda name: debug_free_bytes(pathlib.Path(name).read_bytes(), name)  # noqa: E731
    return 0 if all(read(a) == read(b) for a, b in zip(args[::2], args[1::2], strict=True)) else 1


def missing_main(args: list[str]) -> int:
    """`--missing <data> <path>...`: each file's unrun lines, comma-separated, a line a file, for the Rust gate's coverage report (feature 449 T72); only coverage.py can say."""
    import coverage  # noqa: PLC0415 - absent from the gate's ordinary path, and needed only when a file is exempt

    cov = coverage.Coverage(data_file=args[0])
    cov.load()
    measured = set(cov.get_data().measured_files())
    for name in args[1:]:
        print(",".join(str(n) for n in (cov.analysis2(name)[3] if name in measured else [])))
    return 0


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def split_ids(src: bytes) -> tuple[str, dict[str, str], set[str]] | None:
    """(the module's top-level id, {function qualname: its id}, {class qualnames}) for `src`, or None when it does not parse.

    A function's id is its own node's (decorators, signature and body, nested definitions included); the top level is the
    module with every function taken out, so a changed constant, import, class attribute or decorator-free class line moves it
    and a changed function body moves only that function - the split `gencache` always made, now blind to docstrings and
    comments."""
    try:
        tree = ast.parse(src)
    except SyntaxError, ValueError:
        return None
    strip_docstrings(tree)
    funcs: dict[str, str] = {}
    classes: set[str] = set()

    def walk(node: ast.AST, prefix: str) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, _FUNCS):
                qual = f"{prefix}{child.name}"
                funcs[qual] = _sha(ast.dump(child).encode())
                walk(child, f"{qual}.")  # nested defs get their own entry AND stay in their parent's id
            elif isinstance(child, ast.ClassDef):
                classes.add(f"{prefix}{child.name}")
                walk(child, f"{prefix}{child.name}.")
            else:
                walk(child, prefix)

    walk(tree, "")
    top = copy.deepcopy(tree)
    for node in ast.walk(top):
        for field in ("body", "orelse", "finalbody"):
            stmts = getattr(node, field, None)
            if isinstance(stmts, list):
                stmts[:] = [s for s in stmts if not isinstance(s, _FUNCS)]
    return _sha(ast.dump(top).encode()), funcs, classes


if __name__ == "__main__":
    verbs = {"--ids": ids_main, "--semantic": semantic_main, "--missing": missing_main, "--debug-free-equal": debug_free_equal_main}
    sys.exit(verbs[sys.argv[1]](sys.argv[2:]) if sys.argv[1:2] and sys.argv[1] in verbs else 2)
