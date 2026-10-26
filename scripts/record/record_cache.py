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


def _codeid():  # noqa: ANN202 - the module, loaded by path
    """`l7r/diagram/pipeline/codeid.py`, loaded by PATH (stdlib only, as `gate-stamp.py` loads it): this script does not
    import the engine package."""
    import importlib.util  # noqa: PLC0415
    import sys  # noqa: PLC0415

    cached = sys.modules.get("l7r_codeid")
    if cached is not None:
        return cached
    path = pathlib.Path(__file__).resolve().parents[2] / "l7r" / "diagram" / "pipeline" / "codeid.py"
    spec = importlib.util.spec_from_file_location("l7r_codeid", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["l7r_codeid"] = mod
    spec.loader.exec_module(mod)
    return mod


def code_sha(*paths: pathlib.Path) -> str:
    """The version of the code a cache serves: its source files' contents - Python by what runs (feature 426, the audit: an
    extractor's docstring or comment does not change what it extracts), anything else by its bytes."""
    h = hashlib.sha256()
    for p in paths:
        data = p.read_bytes()
        h.update(_codeid().semantic_bytes(data, p.name) if p.suffix == ".py" else data)
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
    dirs = [path.parent, *(path.parent / d for d in ("../hooks/lib", "../reviews", "../record", "../measure", "../gates"))]
    for name in _import_names(path, repo):
        parts = name.split(".")
        candidates = [d / f"{name}.py" for d in dirs if len(parts) == 1]
        candidates += [repo.joinpath(*parts).with_suffix(".py"), repo.joinpath(*parts, "__init__.py")]
        for c in candidates:
            if c.is_file() and repo.resolve() in c.resolve().parents:
                imported_files(c, repo, seen)
                break
    return seen


_NAMES: dict[str, list] = {}  # {path: [mtime_ns, size, names]}, the imports index below, loaded once per process
_NAMES_DIRTY: list[bool] = [False]


def _names_file(repo: pathlib.Path) -> pathlib.Path | None:
    d = None if off() else common_dir(repo)
    return d / CACHE_DIR / "imports.json" if d is not None else None


def _import_names(path: pathlib.Path, repo: pathlib.Path) -> list[str]:
    """The names a module imports, kept by its mtime and size (feature 383): the code key parsed every module of a tool's
    import graph on every run - 0.4 s of a check bundle, 75 modules - though they change far less often than it runs."""
    if not _NAMES and not _NAMES_DIRTY[0]:
        import json  # noqa: PLC0415

        f = _names_file(repo)
        try:
            loaded = json.loads(f.read_text(encoding="utf-8")) if f is not None and f.is_file() else {}
        except (OSError, ValueError):
            loaded = {}
        _NAMES.update(loaded if isinstance(loaded, dict) else {})
    st = path.stat()
    kept = _NAMES.get(str(path))
    if isinstance(kept, list) and kept[:2] == [st.st_mtime_ns, st.st_size]:
        return kept[2]
    import ast  # noqa: PLC0415

    names: list[str] = []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        tree = None
    for node in ast.walk(tree) if tree is not None else ():
        if isinstance(node, ast.Import):
            names += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            names += [node.module, *(f"{node.module}.{a.name}" for a in node.names)]
    _NAMES[str(path)] = [st.st_mtime_ns, st.st_size, names]
    _NAMES_DIRTY[0] = True
    return names


def _save_names(repo: pathlib.Path) -> None:
    f = _names_file(repo)
    if not _NAMES_DIRTY[0] or f is None:
        return
    import json  # noqa: PLC0415

    try:
        f.parent.mkdir(parents=True, exist_ok=True)
        tmp = f.with_suffix(f".{os.getpid()}.tmp")
        tmp.write_text(json.dumps(_NAMES), encoding="utf-8")
        os.replace(tmp, f)
        _NAMES_DIRTY[0] = False
    except OSError:
        pass


def code_sha_of(repo: pathlib.Path, *paths: pathlib.Path) -> str:
    """`code_sha` over `paths` and every project module they import, transitively, in a stable order."""
    files: set[pathlib.Path] = set()
    for p in paths:
        imported_files(p, repo, files)
    _save_names(repo)
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


# ---- feature 383 (the GM 2026-10-12): a check's work kept by the CONTENT it read ----------------------------------------------
#: "we can compute a hash of the file within a tiny fraction of a second ... a cache that stores the previous values extracted
#: from a file and the hash of the file at the time that they were extracted" (the GM). A clean tracked file's content id is
#: its index blob id - git has already hashed it, so the whole repository's ids are one `ls-files -s` (0.02 s); only a file the
#: work tree changed is read and hashed here.


def _git_z(root: pathlib.Path, *args: str) -> list[str]:
    p = subprocess.run(["git", "-C", str(root), *args], capture_output=True, check=False)
    return [s for s in p.stdout.decode("utf-8", errors="surrogateescape").split("\0") if s] if p.returncode == 0 else []


def _hash_file(path: pathlib.Path) -> str:
    """A file's id as git would give it (its blob id), so the same bytes have the same id whether the index holds them or the
    work tree does - in a clone and in its worktree alike (feature 383 amendment 1)."""
    try:
        data = path.read_bytes()
    except OSError:
        return "gone"
    return hashlib.sha1(b"blob %d\x00" % len(data) + data, usedforsecurity=False).hexdigest()


def content_ids(root: pathlib.Path, prefixes: Sequence[str] = (), *, untracked: bool = False) -> dict[str, str]:
    """{path: content id} for every tracked file (under `prefixes`, when given): its index blob id, or - where the work tree
    changed it, or (with `untracked`) git does not track it and does not ignore it - a hash of its bytes. Two or three git
    processes, never one per file."""
    scope = ["--", *prefixes] if prefixes else []
    ids: dict[str, str] = {}
    for rec in _git_z(root, "ls-files", "-s", "-z", *scope):
        meta, _, path = rec.partition("\t")
        parts = meta.split()
        if len(parts) == 3 and path:
            ids[path] = parts[1]
    for path in _git_z(root, "diff", "--name-only", "-z", *scope):
        ids[path] = _hash_file(root / path)
    if untracked:
        for path in _git_z(root, "ls-files", "--others", "--exclude-standard", "-z", *scope):
            ids[path] = _hash_file(root / path)
    return ids


class FileFacts:
    """What an extractor found in each file, kept by the file's content id and the extractor's code (`ParseCache.at`'s name
    carries the sha of `code` and every project module it imports - pass a data file the extraction depends on, such as a
    config, among `code` too). `facts(paths, extract)` extracts only the files not kept; `facts_batch(paths, extract_many)`
    hands the misses over together, for an extractor that is one subprocess over many files."""

    def __init__(self, root: pathlib.Path, name: str, *code: pathlib.Path, ids: dict[str, str] | None = None) -> None:
        self.root = root
        self.cache = ParseCache.at(root, f"facts-{name}", *code)
        self.ids = ids

    def _key(self, path: str) -> str:
        if self.ids is None:
            self.ids = content_ids(self.root)
        cid = self.ids.get(path) or _hash_file(self.root / path)
        return text_key(path, cid)

    def _ids_for(self, paths: Sequence[str]) -> None:
        """The content ids of the directories `paths` sit in, listed once - not the whole repository's, for a check that
        reads one corner of it."""
        if self.ids is None and paths:
            dirs = sorted({p.rsplit("/", 1)[0] if "/" in p else "." for p in paths})
            self.ids = content_ids(self.root, () if "." in dirs or len(dirs) > 64 else dirs)

    def fact(self, key_text: str, make: Callable[[], Any]) -> Any:  # noqa: ANN401 - the caller's own value
        """One value kept by the text it was made from - for an engine reader handed this object as its memo (feature 383:
        the record store's `MEMO`); `save()` writes what the run added."""
        return self.cache.get(text_key(key_text), make)

    def save(self) -> None:
        self.cache.save()

    def facts(self, paths: Sequence[str], extract: Callable[[str], Any]) -> dict[str, Any]:
        self._ids_for(paths)
        out = {p: self.cache.get(self._key(p), lambda p=p: extract(p)) for p in paths}
        self.cache.save()
        return out

    def facts_batch(self, paths: Sequence[str], extract_many: Callable[[list[str]], dict[str, Any]]) -> dict[str, Any]:
        self._ids_for(paths)
        keys = {p: self._key(p) for p in paths}
        misses = [p for p in paths if keys[p] not in self.cache.data]
        found = extract_many(misses) if misses else {}
        out = {}
        for p in paths:
            out[p] = self.cache.get(keys[p], lambda p=p: found.get(p))
        self.cache.save()
        return out


class ResultMemo:
    """A check's whole answer, kept for a run that PASSED, by the content of every file under its input trees (tracked and
    untracked, the ignored excepted), its code and the interpreter's version. `hit()` is the kept (stdout, stderr) while
    nothing it read changed; `keep(out, err)` records a pass. A failing run is never kept: a refusal is always computed."""

    def __init__(self, root: pathlib.Path, name: str, inputs: Sequence[str], *code: pathlib.Path, argv: Sequence[str] = ()) -> None:
        import sys  # noqa: PLC0415

        ids = content_ids(root, inputs, untracked=True)
        repo = pathlib.Path(__file__).resolve().parents[2]
        self.key = text_key(name, *argv, sys.version, code_sha_of(repo, *code) if code else "", *(f"{p}\x1e{i}" for p, i in sorted(ids.items())))
        d = common_dir(root)
        self.path = None if off() or d is None else d / CACHE_DIR / f"memo-{name}.json"

    def hit(self) -> tuple[str, str] | None:
        if self.path is None:
            return None
        try:
            import json  # noqa: PLC0415

            kept = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
        return (kept.get("out", ""), kept.get("err", "")) if isinstance(kept, dict) and kept.get("key") == self.key else None

    def keep(self, out: str, err: str) -> None:
        if self.path is None:
            return
        import json  # noqa: PLC0415

        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp = tempfile.mkstemp(dir=self.path.parent, suffix=".tmp")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump({"key": self.key, "out": out, "err": err}, f)
            os.replace(tmp, self.path)
        except OSError:
            pass
