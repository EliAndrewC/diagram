#!/usr/bin/env python3
"""What the record tooling reads, read once (feature 375 amendment 3, FR-020; plan D27, D28).

WHY. Measured on 374's delta (specs/375-enforced-wave-process/research.md R1): `record-owed`, `check-bundle`, `modal-bundle`
and `claims-owed` each took 6 to 7 s, run hundreds of times a feature (59 min of 374's tool time). Most of it was the same work
on every call: the whole record parsed at the merge base and again at the working tree, though nearly every file is the same
at both and the same as the call before; and the pop-ups and the entry-drift classes read at the base one `git show` process
per file (299 and 177 of them).

TWO TOOLS, and neither may change an answer:

- `RevReader` - the files under some directories at a revision, read by ONE `git ls-tree -r` and ONE `git cat-file --batch`
  on the first read; a path outside them falls back to its own `git show`.
- `ParseCache` - a parse kept by the text it parsed (sha256) and by the parsing code itself: the cache file's name carries
  the sha of the module whose parse it holds, so a change to that code is a different file and nothing it parsed before
  is served. Held in memory for the run and on disk under `<git common dir>/l7r-cache/`, written atomically and only when
  the run added entries. A missing, corrupt or unreadable file is an empty cache.

`L7R_CACHE_OFF=1` turns the disk cache off (SC-013 compares every command's output with and without it).
"""

from __future__ import annotations

import hashlib
import os
import pathlib
import pickle
import subprocess
import tempfile
from collections.abc import Callable, Sequence
from typing import Any

CACHE_DIR = "l7r-cache"


def cat_blobs(root: pathlib.Path, objects: Sequence[str]) -> list[str]:
    """Each object's text (`<rev>:<path>`), by one `git cat-file --batch`; a missing one is empty."""
    if not objects:
        return []
    p = subprocess.run(["git", "-C", str(root), "cat-file", "--batch"], input=("\n".join(objects) + "\n").encode("utf-8"), capture_output=True, check=False)
    out, data, i = [], p.stdout, 0
    for _ in objects:
        nl = data.index(b"\n", i)
        head = data[i:nl].split()
        if len(head) < 3 or head[1] == b"missing":
            out.append("")
            i = nl + 1
            continue
        size = int(head[2])
        out.append(data[nl + 1 : nl + 1 + size].decode("utf-8", errors="replace"))
        i = nl + 1 + size + 1
    return out


class RevReader:
    """`read(path)` -> the file's text at `rev`, or None where it has none. The files under `dirs` come from one listing and
    one batch, on the first read; any other path is its own `git show`."""

    def __init__(self, root: pathlib.Path, rev: str, dirs: Sequence[str]) -> None:
        self.root, self.rev, self.dirs = root, rev, tuple(d.rstrip("/") for d in dirs)
        self._files: dict[str, str] | None = None

    def _load(self) -> dict[str, str]:
        if self._files is None:
            p = subprocess.run(["git", "-C", str(self.root), "ls-tree", "-r", "--name-only", self.rev, "--", *self.dirs], capture_output=True, text=True, check=False)
            names = [n for n in p.stdout.split("\n") if n] if p.returncode == 0 else []
            self._files = dict(zip(names, cat_blobs(self.root, [f"{self.rev}:{n}" for n in names]), strict=True))
        return self._files

    def names(self, directory: str) -> list[str]:
        """The files directly in `directory` (one of `dirs` or below one) at `rev`, as `git ls-tree --name-only` lists them."""
        d = directory.rstrip("/") + "/"
        return sorted(n for n in self._load() if n.startswith(d) and "/" not in n[len(d):])

    def inside(self, path: str) -> bool:
        return any(path == d or path.startswith(d + "/") for d in self.dirs)

    def read(self, path: str) -> str | None:
        if self.inside(path):
            return self._load().get(path)
        p = subprocess.run(["git", "-C", str(self.root), "show", f"{self.rev}:{path}"], capture_output=True, text=True, check=False)
        return p.stdout if p.returncode == 0 else None

    __call__ = read


def common_dir(root: pathlib.Path) -> pathlib.Path | None:
    p = subprocess.run(["git", "-C", str(root), "rev-parse", "--git-common-dir"], capture_output=True, text=True, check=False)
    if p.returncode != 0 or not p.stdout.strip():
        return None
    path = pathlib.Path(p.stdout.strip())
    return path if path.is_absolute() else root / path


def code_sha(*paths: pathlib.Path) -> str:
    """The version of the code a cache serves: its source files' contents."""
    h = hashlib.sha256()
    for p in paths:
        h.update(p.read_bytes())
    return h.hexdigest()[:16]


def imported_files(path: pathlib.Path, repo: pathlib.Path, seen: set[pathlib.Path] | None = None) -> set[pathlib.Path]:
    """`path` and every project file it imports, transitively: an `import x` / `from x import y` resolved to a file beside it,
    in a directory it puts on `sys.path` (the scripts' flat imports), or under the repository by its dotted name. The
    standard library and installed packages resolve to nothing here, and are not part of the key (feature 375 amendment 3,
    the spec review's item: a change to a helper the parser imports must miss)."""
    seen = set() if seen is None else seen
    path = path.resolve()
    if path in seen or not path.is_file():
        return seen
    seen.add(path)
    import ast  # noqa: PLC0415

    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return seen
    dirs = [path.parent, *(path.parent / d for d in ("../hooks/lib", "../reviews", "../record", "../measure", "../gates"))]
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            names += [node.module, *(f"{node.module}.{a.name}" for a in node.names)]
    for name in names:
        parts = name.split(".")
        candidates = [d / f"{name}.py" for d in dirs if len(parts) == 1]
        candidates += [repo.joinpath(*parts).with_suffix(".py"), repo.joinpath(*parts, "__init__.py")]
        for c in candidates:
            if c.is_file() and repo.resolve() in c.resolve().parents:
                imported_files(c, repo, seen)
                break
    return seen


def code_sha_of(repo: pathlib.Path, *paths: pathlib.Path) -> str:
    """`code_sha` over `paths` and every project module they import, transitively, in a stable order."""
    files: set[pathlib.Path] = set()
    for p in paths:
        imported_files(p, repo, files)
    return code_sha(*sorted(files))


def text_key(*parts: str) -> str:
    return hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()


def off() -> bool:
    return os.environ.get("L7R_CACHE_OFF", "") not in ("", "0")


class ParseCache:
    """A parse kept by its text and its code. `get(key, make)` returns the kept value, or makes, keeps and returns it."""

    def __init__(self, path: pathlib.Path | None) -> None:
        self.path = None if off() else path
        self.data: dict[str, Any] = {}
        self.used: set[str] = set()
        self.added = False
        if self.path is not None and self.path.is_file():
            try:
                with self.path.open("rb") as f:
                    loaded = pickle.load(f)  # noqa: S301 - the clone's own cache, written by save() below
                self.data = loaded if isinstance(loaded, dict) else {}
            except Exception:  # noqa: BLE001 - a corrupt cache is an empty one, never a failure
                self.data = {}

    @classmethod
    def at(cls, root: pathlib.Path, name: str, *code: pathlib.Path) -> ParseCache:
        """The cache `<name>-<code sha>.pickle` under the clone's common git dir (an in-memory one outside a clone); the sha
        covers `code` and every project module it imports, transitively."""
        d = common_dir(root)
        repo = pathlib.Path(__file__).resolve().parents[2]
        return cls(d / CACHE_DIR / f"{name}-{code_sha_of(repo, *code)}.pickle" if d is not None else None)

    def get(self, key: str, make: Callable[[], Any]) -> Any:  # noqa: ANN401 - the caller's own parse
        self.used.add(key)
        if key in self.data:
            return self.data[key]
        value = self.data[key] = make()
        self.added = True
        return value

    #: a cache holding this many times the entries a run used drops the rest when it is next written (old versions of files)
    PRUNE_AT = 4

    def save(self) -> None:
        """Write the cache when the run added to it, dropping what this run did not use once it has grown PRUNE_AT times over."""
        if self.path is None or not self.added:
            return
        if len(self.data) > self.PRUNE_AT * max(len(self.used), 1):
            self.data = {k: v for k, v in self.data.items() if k in self.used}
        tmp = ""
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            for stale in self.path.parent.glob(self.path.name.rsplit("-", 1)[0] + "-*.pickle"):
                if stale != self.path:  # another version of this code's cache: never read again
                    stale.unlink(missing_ok=True)
            fd, tmp = tempfile.mkstemp(dir=self.path.parent, suffix=".tmp")
            with os.fdopen(fd, "wb") as f:
                pickle.dump(self.data, f, protocol=pickle.HIGHEST_PROTOCOL)
            os.replace(tmp, self.path)
        except Exception:  # noqa: BLE001 - an unwritable cache costs the next run its speed, never its answer
            if tmp:
                pathlib.Path(tmp).unlink(missing_ok=True)
