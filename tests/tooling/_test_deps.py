"""A tooling test file the clone passed is not run again on identical inputs (feature 383 amendment 1, FR-013).

The GM, 2026-10-13: *"Yes please we should definitely skip suites the clone already passed."* `make land-tooling` re-ran the
whole tooling tree (1,784 tests, about 40 s) in a fresh worktree on every landing, though the clone had passed it on the same
files minutes before. The guard suites already reuse a pass keyed by what they read (`make hooks-test`); this does the same
for each tooling test FILE.

RECORD (`L7R_TEST_DEPS=record`, which `make test-file` and the gate's tooling run set). While a tooling test file runs, everything it reads under the
repository is noted - each file it opens and each directory it lists, in its own process (an audit hook) and in every Python
process it starts (`_deps_site/sitecustomize.py`, put on PYTHONPATH) - and each other program it starts against the
repository. When every test of the file passed, its reads are kept by their content (git blob ids; a directory by its
entries) in `<git common dir>/l7r-cache/tooling-test-passes.json`. A failure keeps nothing; a run filtered by `-k` or a node
id keeps nothing.

REUSE (`L7R_TEST_DEPS=reuse`, which `make land-tooling` sets; it records what it runs as well). A test file whose kept reads are all unchanged - same content,
same entries - and that started no other program against the repository is deselected, and the run says how many. What is
not known is run: a file never recorded, one that started `git` or `make` in the repository, a Python child run isolated or
with the recording dropped from its environment. `L7R_CACHE_OFF=1` reuses nothing.
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import tempfile

import pytest

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SITE = HERE / "_deps_site"
TREE = "tests/tooling/"
MODE = os.environ.get("L7R_TEST_DEPS", "")
STORE_NAME = "tooling-test-passes.json"

_current: list[str] = [""]
_reads: dict[str, dict[str, set[str]]] = {}
_failed: set[str] = set()
_ran: dict[str, int] = {}
_deselected: set[str] = set()


def pytest_deselected(items: list[pytest.Item]) -> None:
    """A file any of whose tests was deselected - by `-k`, a marker, or a reuse - did not run whole: its pass is not kept."""
    _deselected.update(_rel(i.nodeid) for i in items)


def _rel(nodeid: str) -> str:
    return nodeid.split("::", 1)[0]


def _store() -> pathlib.Path | None:
    p = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--path-format=absolute", "--git-common-dir"], capture_output=True, text=True)
    return pathlib.Path(p.stdout.strip()) / "l7r-cache" / STORE_NAME if p.returncode == 0 and p.stdout.strip() else None


def _under(path: object) -> str:
    try:
        p = os.path.abspath(os.fsdecode(path))  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return ""
    root = str(ROOT)
    return p if p == root or p.startswith(root + os.sep) else ""


def _hook(event: str, args: tuple) -> None:
    f = _current[0]
    if not f:
        return
    if event == "open" and args and isinstance(args[0], (str, bytes)):
        mode = args[1] if len(args) > 1 else "r"
        if isinstance(mode, str) and any(c in mode for c in "wax+"):
            return
        p = _under(args[0])
        if p:
            _reads.setdefault(f, {}).setdefault("file", set()).add(p)
    elif event in ("os.listdir", "os.scandir") and args:
        p = _under(args[0] if args[0] is not None else ".")
        if p:
            _reads.setdefault(f, {}).setdefault("dir", set()).add(p)
    elif event == "subprocess.Popen" and args:
        why = opaque_child(args, str(SITE))
        if why:
            _reads.setdefault(f, {}).setdefault("opaque", set()).add(why)


def opaque_child(args: tuple, site: str) -> str:
    """The name of a program a test started whose reads are not known (`subprocess.Popen`'s audit arguments: executable, argv,
    cwd, env), or "": a Python child that records itself is known; any other program run in or on the repository is not, nor
    a Python child run isolated or with the recording dropped from its environment."""
    exe, argv = args[0], args[1]
    cwd = args[2] if len(args) > 2 else None
    env = args[3] if len(args) > 3 else None
    try:
        name = os.path.basename(os.fsdecode(exe if exe else (argv[0] if argv else "")))
    except (TypeError, IndexError):
        name = ""
    if name.startswith("python"):
        flags = {os.fsdecode(a) for a in list(argv or [])[1:3] if isinstance(a, (str, bytes))}
        recorded = env is None or (env.get("L7R_TEST_DEP_LOG") and site in str(env.get("PYTHONPATH", "")))
        return "" if recorded and not flags & {"-I", "-S", "-E", "-IS", "-ISE"} else name
    words = [os.fsdecode(a) for a in (argv or []) if isinstance(a, (str, bytes))]
    # where the program works: `git -C <dir>` and `make -C <dir>` name it, else its cwd (a test's git in its own tmp repo is not
    # the repository - 64 of the first recording's 74 unknown files were that)
    return name if against_repo(name, words, cwd, _under) else ""


def against_repo(name: str, words: list[str], cwd: object, under) -> bool:  # noqa: ANN001 - under: a path test
    """Does a program work in or on the repository? Unless both its working directory (and any `-C`) are outside it and no
    argument names a path inside it, yes - the plan review's rule (a `git worktree add /tmp/x HEAD` run in the repository
    names an outside path and reads the repository). Two git forms read nothing where they run: `git init <dir>` and
    `git clone <src> <dst>`, judged by the paths they name."""
    where = next((words[i + 1] for i, w in enumerate(words[:-1]) if w == "-C"), None)
    paths = [w for w in words[1:] if os.path.isabs(w) and w != where]
    sub = next((w for w in words[1:] if not w.startswith("-") and w != where and "=" not in w), "")
    if name in READ_NOTHING:
        return False
    if name == "git" and sub == "rev-parse" and _location_only(words):
        return False
    if name == "git" and where is None and sub in ("init", "clone") and paths:
        return any(under(w) for w in paths)
    return bool(under(where or cwd or os.getcwd())) or any(under(w) for w in paths)


#: programs that read no file of the repository wherever they run
READ_NOTHING = frozenset({"sleep", "true", "false", "echo"})
#: `git rev-parse` asking only WHERE the repository is: its answer depends on the checkout's place, not on its content (the
#: commonest unknown in the first recordings - `record_cache.common_dir`, `--show-toplevel`)
LOCATION = frozenset({"--show-toplevel", "--git-dir", "--git-common-dir", "--absolute-git-dir", "--show-prefix", "--show-cdup",
                      "--is-inside-work-tree", "--path-format=absolute", "--path-format=relative"})


def _location_only(words: list[str]) -> bool:
    rest = words[words.index("rev-parse") + 1:]
    return bool(rest) and all(w in LOCATION for w in rest)


def _ids() -> tuple[dict[str, str], dict[str, list[str]]]:
    """({repository-relative path: content id}, {directory: its entries}) - tracked and untracked files, the ignored aside."""
    sys.path.insert(0, str(ROOT / "scripts" / "record"))
    import record_cache  # noqa: PLC0415

    ids = record_cache.content_ids(ROOT, untracked=True)
    entries: dict[str, set[str]] = {}
    for rel in ids:
        parts = rel.split("/")
        for i in range(len(parts)):
            entries.setdefault("/".join(parts[:i]), set()).add(parts[i])
    return ids, {d: sorted(e) for d, e in entries.items()}


def _rel_path(path: str) -> str:
    """A read's path relative to the repository; a module's bytecode (`x/__pycache__/y.cpython-314.pyc`) stands for its source
    (`x/y.py`), which the import compared it against."""
    rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
    rel = "" if rel == "." else rel
    if "/__pycache__/" in f"/{rel}" and rel.endswith(".pyc"):
        head, _, name = rel.rpartition("__pycache__/")
        rel = head + name.split(".", 1)[0] + ".py"
    return rel


#: reads that cannot change a result: the content caches (`record_cache`), whose every entry is keyed by what it holds
CACHE_READS = (".git/l7r-cache/",)


def _state(kind: str, rel: str, ids: dict[str, str], entries: dict[str, list[str]]) -> str:
    """What a read found, as content: a file's id (`absent` where there is none), a directory's entries. A file git ignores
    has no id here - `ignored`, which no kept pass accepts (what it held is not known)."""
    if kind == "file":
        return ids.get(rel) or ("absent" if not (ROOT / rel).exists() else "ignored")
    return json.dumps(entries.get(rel, []))


def pytest_configure(config: pytest.Config) -> None:
    if MODE not in ("record", "reuse") or os.environ.get("L7R_CACHE_OFF", "") not in ("", "0"):
        return
    config._l7r_deps = True  # type: ignore[attr-defined]  # reuse records too: a landing's run keeps what it ran for the next
    if not hasattr(config, "workerinput"):  # the controller (or a run with no workers): the shared log and the children's path
        d = tempfile.mkdtemp(prefix="l7r-test-deps-")
        os.environ["L7R_TEST_DEP_DIR"] = d
        os.environ["L7R_TEST_DEP_ROOT"] = str(ROOT)
        os.environ["PYTHONPATH"] = os.pathsep.join([str(SITE), *([os.environ["PYTHONPATH"]] if os.environ.get("PYTHONPATH") else [])])
    worker = getattr(config, "workerinput", {}).get("workerid", "main")
    os.environ["L7R_TEST_DEP_LOG"] = os.path.join(os.environ.get("L7R_TEST_DEP_DIR", tempfile.gettempdir()), f"children-{worker}.log")
    sys.addaudithook(_hook)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item: pytest.Item, nextitem: pytest.Item | None):  # noqa: ANN201, ARG001
    rel = _rel(item.nodeid)
    tracked = getattr(item.config, "_l7r_deps", False) and rel.startswith(TREE)
    if tracked:
        _current[0] = rel
        os.environ["L7R_TEST_DEP_FILE"] = rel
    yield
    if tracked:
        _current[0] = ""
        os.environ["L7R_TEST_DEP_FILE"] = ""
        _ran[rel] = _ran.get(rel, 0) + 1


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    if report.failed:
        _failed.add(_rel(report.nodeid))


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:  # noqa: ARG001
    config = session.config
    if not getattr(config, "_l7r_deps", False):
        return
    d = os.environ.get("L7R_TEST_DEP_DIR", "")
    worker = getattr(config, "workerinput", {}).get("workerid", "main")
    if d:
        with open(os.path.join(d, f"worker-{worker}.json"), "w", encoding="utf-8") as fh:
            json.dump({"reads": {f: {k: sorted(v) for k, v in r.items()} for f, r in _reads.items()}, "failed": sorted(_failed),
                       "ran": _ran, "deselected": sorted(_deselected)}, fh)
    if hasattr(config, "workerinput") or not d:
        return
    if any("::" in a for a in config.args):
        return  # a run of named tests: a file's other tests did not run, so its pass is not the file's
    _keep(pathlib.Path(d))


def _keep(d: pathlib.Path) -> None:
    """Merge the workers' and the children's reads and keep each passed file's, by content."""
    reads: dict[str, dict[str, set[str]]] = {}
    failed: set[str] = set()
    ran: dict[str, int] = {}
    for w in d.glob("worker-*.json"):
        data = json.loads(w.read_text(encoding="utf-8"))
        for f, r in data["reads"].items():
            for k, v in r.items():
                reads.setdefault(f, {}).setdefault(k, set()).update(v)
        failed.update(data["failed"])
        failed.update(data.get("deselected", []))  # not run whole (the plan review: checked, never trusted to a marker)
        for f, n in data["ran"].items():
            ran[f] = ran.get(f, 0) + n
    for log in d.glob("children-*.log"):
        for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
            f, _, rest = line.partition("\t")
            kind, _, path = rest.partition("\t")
            if f and kind:
                reads.setdefault(f, {}).setdefault(kind, set()).add(path)
    store = _store()
    if store is None:
        return
    ids, entries = _ids()
    try:
        kept = json.loads(store.read_text(encoding="utf-8")) if store.is_file() else {}
    except (OSError, ValueError):
        kept = {}
    for f in ran:
        if f in failed:
            kept.pop(f, None)
            continue
        r = reads.get(f, {})
        opened = {_rel_path(p) for p in r.get("file", set())}
        opened = {p for p in opened if not p.startswith(CACHE_READS)}
        files = {p for p in opened if not (ROOT / p).is_dir()}
        dirs = {_rel_path(p) for p in r.get("dir", set())} | {p for p in opened if (ROOT / p).is_dir() and not p.startswith(".git")}
        if any(p == ".git" or p.startswith(".git/") for p in opened if (ROOT / p).is_dir()):
            files.add(".git")  # the repository's own git state was read: not known by content, so never reused
        kept[f] = {"py": sys.version, "opaque": sorted(r.get("opaque", set())),
                   "files": {p: _state("file", p, ids, entries) for p in sorted(files)},
                   "dirs": {p: _state("dir", p, ids, entries) for p in sorted(dirs)}}
    store.parent.mkdir(parents=True, exist_ok=True)
    tmp = store.with_suffix(f".{os.getpid()}.tmp")
    tmp.write_text(json.dumps(kept), encoding="utf-8")
    tmp.replace(store)


def reusable(kept: dict, ids: dict[str, str], entries: dict[str, list[str]]) -> bool:
    """Is a kept pass still good: the same interpreter, no other program run against the repository, no read of a file git
    ignores, and every read unchanged? Reads are kept relative to the repository, so a worktree compares with its clone."""
    if kept.get("py") != sys.version or kept.get("opaque"):
        return False
    files, dirs = kept.get("files", {}), kept.get("dirs", {})
    if "ignored" in files.values():
        return False
    return all(_state("file", p, ids, entries) == was for p, was in files.items()) and \
        all(_state("dir", p, ids, entries) == was for p, was in dirs.items())


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if MODE != "reuse" or not getattr(config, "_l7r_deps", False):
        return
    store = _store()
    try:
        kept = json.loads(store.read_text(encoding="utf-8")) if store and store.is_file() else {}
    except (OSError, ValueError):
        kept = {}
    files = {_rel(i.nodeid) for i in items if _rel(i.nodeid).startswith(TREE)}
    if not kept or not files:
        return
    ids, entries = _ids()
    skip = {f for f in files if f in kept and reusable(kept[f], ids, entries)}
    if not skip:
        return
    gone = [i for i in items if _rel(i.nodeid) in skip]
    items[:] = [i for i in items if _rel(i.nodeid) not in skip]
    config.hook.pytest_deselected(items=gone)
    if not hasattr(config, "workerinput"):
        config._l7r_reused = (len(skip), len(gone))  # type: ignore[attr-defined]


def pytest_terminal_summary(terminalreporter, config: pytest.Config) -> None:  # noqa: ANN001
    reused = getattr(config, "_l7r_reused", None)
    if reused:
        terminalreporter.write_line(f"reused the clone's passes: {reused[0]} tooling test file(s), {reused[1]} test(s), on identical inputs (feature 383 FR-013)")
