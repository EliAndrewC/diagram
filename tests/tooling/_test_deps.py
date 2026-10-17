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

GATE (`L7R_TEST_DEPS=gate`, which the gate's coverage run sets unless forced full; amendment 5, plan D31). On a FULL plan only,
a tooling test is reused against the reads that produced the BASELINE's coverage of it (`<baseline>/tooling-reads.json`, not
the clone's store, which a later run may have re-recorded on other content), and only if the baseline holds it; the reused
node ids go to `tooling-reused.json`, whose coverage `incremental carry` copies in before the floors. What the run records
goes to `tooling-reads.json.next`, promoted with the baseline it produced.
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
sys.path.insert(0, str(SITE))
import l7r_dep_rules as rules  # noqa: E402 - beside the children's shim, which uses the same rules

TREE = "tests/tooling/"
MODE = os.environ.get("L7R_TEST_DEPS", "")
#: GATE (plan D31): the gate's coverage run, on a FULL plan, reuses a tooling test only against the reads that produced the
#: baseline's coverage of it - kept beside the baseline (`tooling-reads.json`, promoted by `incremental save-baseline`) - and
#: names what it reused (`tooling-reused.json`) so `incremental carry` copies that coverage into this run's data
GATE = os.environ.get("L7R_GATE_SELECT", "") if MODE == "gate" else ""
REUSING = MODE in ("reuse", "gate")
GATE_READS, GATE_REUSED = "tooling-reads.json", "tooling-reused.json"
STORE_NAME = "tooling-test-passes.json"
#: what a kept pass holds: 2 added the git questions' answers (amendment 2); 3 keeps a pass PER TEST, beside what each test's file and
#: the session read (amendment 5). A pass kept in another form is never reused - an older reader would misread it
STORE_VERSION = 3
SESSION = "<session>"  # the key session- and package-scoped fixtures record under: every test depends on it

_current: list[str] = [""]
_reads: dict[str, dict[str, set[str]]] = {}
_failed: set[str] = set()
_ran: set[str] = set()
_collected: dict[str, list[str]] = {}
_reused_ids: set[str] = set()


def _rel(nodeid: str) -> str:
    return nodeid.split("::", 1)[0]


def _store() -> pathlib.Path | None:
    if GATE:
        return pathlib.Path(GATE) / GATE_READS
    return _clone_store()


def _clone_store() -> pathlib.Path | None:
    """The clone's store, in its git common directory's cache - where the C recorder is built too, in either mode."""
    p = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--path-format=absolute", "--git-common-dir"], capture_output=True, text=True)
    return pathlib.Path(p.stdout.strip()) / "l7r-cache" / STORE_NAME if p.returncode == 0 and p.stdout.strip() else None


def _under(path: object) -> str:
    return rules.under(path, str(ROOT))


def _hook(event: str, args: tuple) -> None:
    f = _current[0]
    if not f:
        return
    if event == "open" and args and isinstance(args[0], (str, bytes)):
        mode = args[1] if len(args) > 1 else "r"
        if isinstance(mode, str) and any(c in mode for c in "wax+"):
            return
        if mode is None and len(args) > 2 and isinstance(args[2], int) and args[2] & os.O_ACCMODE != os.O_RDONLY:
            return  # an os.open for writing (its flags, not a mode string, say so): not a read
        if mode is None and not os.path.isabs(os.fsdecode(args[0])):
            return  # an os.open by name under a directory handle (shutil.rmtree of a temporary tree): not a path here
        p = _under(args[0])
        if p:
            _reads.setdefault(f, {}).setdefault("file", set()).add(p)
    elif event in ("os.listdir", "os.scandir") and args:
        p = _under(args[0] if args[0] is not None else ".")
        if p:
            _reads.setdefault(f, {}).setdefault("dir", set()).add(p)
    elif event == "subprocess.Popen" and args:
        kind, what = rules.judge(args, str(ROOT), str(SITE))
        if kind:
            _reads.setdefault(f, {}).setdefault(kind, set()).add(what)


def opaque_child(args: tuple, site: str) -> str:
    """The name of a program a test started whose reads are not known, or "" (`l7r_dep_rules.judge`: a git question is known -
    its answer is kept and asked again - and so is a Python child that records itself)."""
    kind, what = rules.judge(args, str(ROOT), site)
    return what if kind == "opaque" else ""


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


#: reads that cannot change a result: the content caches, whose every entry is keyed by what it holds - `record_cache`'s, the
#: gate stamp's semantic ids (a blob id to its id), and the translation pairs' `ParseCache` (amendment 2, FR-020)
CACHE_READS = (".git/l7r-cache/", ".git/semantic-id-cache.json", ".git/record-checks/translation-pairs.json")


def _state(kind: str, rel: str, ids: dict[str, str], entries: dict[str, list[str]]) -> str:
    """What a read found, as content: a file's id (`absent` where there is none), a directory's entries. A file git ignores
    has no id here - `ignored`, which no kept pass accepts (what it held is not known)."""
    if kind == "file" and rel.startswith(".git/"):
        return _git_file_state(rel[5:])
    if kind == "file":
        return ids.get(rel) or ("absent" if not (ROOT / rel).exists() else "ignored")
    return json.dumps(entries.get(rel, []))


_COMMON: list[pathlib.Path | None] = []


def _git_file_state(rest: str) -> str:
    """A file under `.git/` by its content in the git COMMON directory, which a worktree shares with its clone (amendment 3:
    ruff reads `.git/info/exclude`, and in a worktree `.git` is a file, so the path read as `absent` there). A file kept per
    checkout (HEAD, the index) differs between them, and so the file runs, as it should."""
    if not _COMMON:
        store = _store()
        _COMMON.append(store.parents[1] if store else None)
    common = _COMMON[0]
    path = common / rest if common else None
    if path is None or not path.is_file():
        return "absent"
    import hashlib  # noqa: PLC0415

    data = path.read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()  # noqa: S324 - an identity, as git computes it


def pytest_configure(config: pytest.Config) -> None:
    if MODE not in ("record", "reuse", "gate") or os.environ.get("L7R_CACHE_OFF", "") not in ("", "0"):
        return
    if MODE == "gate" and not gate_full(GATE):
        return  # an incremental plan selects by coverage; only a full plan's tooling tests are this plugin's (plan D31)
    config._l7r_deps = True  # type: ignore[attr-defined]  # reuse records too: a landing's run keeps what it ran for the next
    if not hasattr(config, "workerinput"):  # the controller (or a run with no workers): the shared log and the children's path
        d = tempfile.mkdtemp(prefix="l7r-test-deps-")
        os.environ["L7R_TEST_DEP_DIR"] = d
        os.environ["L7R_TEST_DEP_ROOT"] = str(ROOT)
        os.environ["PYTHONPATH"] = os.pathsep.join([str(SITE), *([os.environ["PYTHONPATH"]] if os.environ.get("PYTHONPATH") else [])])
        shim = build_shim()
        if shim:  # every process started from here on loads it; the workers too, which skip themselves (L7R_TEST_DEP_SELF)
            os.environ[rules.SHIM_ENV] = shim
            os.environ["LD_PRELOAD"] = " ".join([shim, *([os.environ["LD_PRELOAD"]] if os.environ.get("LD_PRELOAD") else [])])
            os.environ["UV_USE_IO_URING"] = "0"
    worker = getattr(config, "workerinput", {}).get("workerid", "main")
    os.environ["L7R_TEST_DEP_LOG"] = os.path.join(os.environ.get("L7R_TEST_DEP_DIR", tempfile.gettempdir()), f"children-{worker}.log")
    os.environ["L7R_TEST_DEP_SELF"] = str(os.getpid())
    sys.addaudithook(_hook)
    _monitor()


SHIM_SRC = SITE / "l7r_file_log.c"


def gate_full(bdir: str) -> bool:
    """Is the gate's plan in `bdir` a FULL one - the run whose tooling tests reuse (plan D31)?"""
    try:
        return bool(bdir) and json.loads((pathlib.Path(bdir) / "plan.json").read_text(encoding="utf-8")).get("mode") == "full"
    except OSError, ValueError:
        return False


def gate_baseline_tests(bdir: str) -> set[str] | None:
    """The node ids the gate's baseline holds coverage for (`tests.json`); None outside the gate. A test it does not hold has
    no coverage to carry, so it always runs (plan D31)."""
    if not bdir:
        return None
    try:
        return set(json.loads((pathlib.Path(bdir) / "tests.json").read_text(encoding="utf-8")))
    except OSError, ValueError:
        return set()


def build_shim() -> str:
    """The preloaded C-library recorder (plan D26), built once per version of its source into the git common directory's
    cache with gcc; "" where it cannot be built (no compiler) - every non-Python child then stays unknown, as before."""
    store = _clone_store()
    if store is None or not SHIM_SRC.is_file():
        return ""
    import hashlib  # noqa: PLC0415

    so = store.parent / f"l7r_file_log-{hashlib.sha256(SHIM_SRC.read_bytes()).hexdigest()[:12]}.so"
    if so.is_file():
        return str(so)
    so.parent.mkdir(parents=True, exist_ok=True)
    tmp = so.with_suffix(f".{os.getpid()}.tmp")
    try:
        ok = subprocess.run(["gcc", "-shared", "-fPIC", "-O2", "-o", str(tmp), str(SHIM_SRC), "-ldl"], capture_output=True, check=False).returncode == 0
    except OSError:
        ok = False
    if not ok:
        tmp.unlink(missing_ok=True)
        return ""
    tmp.replace(so)
    return str(so)


def _enter(key: str) -> str:
    prev = _current[0]
    _current[0] = key
    os.environ["L7R_TEST_DEP_FILE"] = key
    if _MONITORING[0]:
        sys.monitoring.restart_events()  # each code object's first run is seen again, under the new key
    return prev


#: the sys.monitoring tool id this records under: coverage takes 1, a profiler 2, the optimizer 5
MONITOR_ID = 3
_MONITORING = [False]


def _ran_code(code, offset: int):  # noqa: ANN001, ANN202, ARG001
    """A code object of the repository started running: its file is a read of the current key. WHY (found 2026-10-17, plan
    D32b): a module is opened once per worker, so a test that only CALLS a module another test imported first never opened
    it, and its pass was reused after that module changed (`ci/delta.py` edited: 36 tests ran, and `test_delta.py`'s
    others were reused). The run of its code is what a test depends on; each code object reports once per key and is then
    disabled until `_enter` restarts the events."""
    f = _current[0]
    if f:
        p = _under(code.co_filename)
        if p:
            _reads.setdefault(f, {}).setdefault("file", set()).add(p)
    return sys.monitoring.DISABLE


def _monitor() -> None:
    """Record the code each key runs (`_ran_code`); a no-op where the id is taken (a coverage run uses its own)."""
    mon = sys.monitoring
    try:
        mon.use_tool_id(MONITOR_ID, "l7r-test-deps")
    except ValueError:
        return
    mon.register_callback(MONITOR_ID, mon.events.PY_START, _ran_code)
    mon.set_events(MONITOR_ID, mon.events.PY_START)
    _MONITORING[0] = True


@pytest.hookimpl(hookwrapper=True)
def pytest_make_collect_report(collector: pytest.Collector):  # noqa: ANN201
    """What a test file reads while it is imported and collected is its FILE's read: every test of it depends on it."""
    rel = _rel_path(str(collector.path)) if isinstance(collector, pytest.Module) else ""
    track = rel.startswith(TREE) and getattr(collector.config, "_l7r_deps", False)
    prev = _enter(rel) if track else ""
    yield
    if track:
        _enter(prev)


def fixture_key(baseid: str, scope: str, nodeid: str) -> str:
    """The key a fixture wider than one test records under: the test module that DEFINES it, at any scope, since only that
    module's tests can use it (plan D32b - a session fixture of `test_incremental_gate.py` made every test depend on
    `ci/delta.py`); else, for one from a conftest, the requesting file for a module- or class-scoped one, the session for a
    session- or package-scoped one."""
    home = baseid.split("::", 1)[0]
    if home.endswith(".py") and home.startswith(TREE):
        return home
    if home not in ("", "tests") and not (home + "/").startswith(TREE):
        return ""  # defined where no tooling test can use it (`tests/gate/conftest.py`): the gate's run sets those up too
    f = _rel(nodeid)
    return f if scope in ("module", "class") and f.startswith(TREE) else SESSION


@pytest.hookimpl(hookwrapper=True)
def pytest_fixture_setup(fixturedef, request):  # noqa: ANN001, ANN201
    """A fixture wider than one test is read for every test that may use it: a module- or class-scoped one for its file, a
    session- or package-scoped one for the session (amendment 5, plan D32)."""
    key = ""
    if getattr(request.config, "_l7r_deps", False) and fixturedef.scope != "function":
        key = fixture_key(fixturedef.baseid, fixturedef.scope, request.node.nodeid)
    prev = _enter(key) if key else ""
    yield
    if key:
        _enter(prev)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item: pytest.Item, nextitem: pytest.Item | None):  # noqa: ANN201, ARG001
    tracked = getattr(item.config, "_l7r_deps", False) and _rel(item.nodeid).startswith(TREE)
    prev = _enter(item.nodeid) if tracked else ""
    yield
    if tracked:
        _enter(prev)
        _ran.add(item.nodeid)


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    if report.failed:
        _failed.add(report.nodeid)


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:  # noqa: ARG001
    config = session.config
    if not getattr(config, "_l7r_deps", False):
        return
    d = os.environ.get("L7R_TEST_DEP_DIR", "")
    worker = getattr(config, "workerinput", {}).get("workerid", "main")
    if d:
        with open(os.path.join(d, f"worker-{worker}.json"), "w", encoding="utf-8") as fh:
            reused = list(getattr(config, "_l7r_reused", (0, 0)))
            json.dump({"reads": {k: {kk: sorted(v) for kk, v in r.items()} for k, r in _reads.items()}, "failed": sorted(_failed),
                       "ran": sorted(_ran), "collected": _collected, "reused": reused, "reused_ids": sorted(_reused_ids)}, fh)  # fmt: skip
    if hasattr(config, "workerinput") or not d:
        return
    # UNDER XDIST THE WORKERS DESELECT, the controller does not (383 amendment 2): the controller reports one worker's count
    counts = [json.loads(w.read_text(encoding="utf-8")).get("reused", [0, 0]) for w in pathlib.Path(d).glob("worker-*.json")]
    if not getattr(config, "_l7r_reused", None) and any(c[0] or c[1] for c in counts):
        config._l7r_reused = tuple(max(counts))  # type: ignore[attr-defined]
    _keep(pathlib.Path(d))


#: what every test of a file depends on besides what it read: the plugin's own code and the test configuration (amendment 5)
PLUGIN = ("tests/tooling/_test_deps.py", "tests/tooling/_deps_site/l7r_dep_rules.py", "tests/tooling/_deps_site/sitecustomize.py",
          "tests/tooling/_deps_site/l7r_file_log.c", "pyproject.toml")  # fmt: skip


def file_inputs(rel: str) -> set[str]:
    """The test file itself, the `conftest.py` files from its directory up to `tests/`, and `PLUGIN` - read by every test of it,
    whether or not the run saw them read (a conftest is imported before any test file is)."""
    out = {rel, *PLUGIN}
    parts = rel.split("/")[:-1]
    while parts and parts[0] == "tests":
        out.add("/".join([*parts, "conftest.py"]))
        parts = parts[:-1]
    return out


def _paths(r: dict[str, set[str]], extra: set[str] = frozenset()) -> tuple[set[str], set[str]]:  # noqa: B006
    """(the files, the directories) one read set names, relative to the repository."""
    opened = {_rel_path(p) for p in r.get("file", set())} | set(extra)
    opened = {p for p in opened if p and not (p + "/").startswith(CACHE_READS) and p != ".git"}  # `.git` itself: where, not what
    files = {p for p in opened if not (ROOT / p).is_dir()}
    dirs = {_rel_path(p) for p in r.get("dir", set())} | {p for p in opened if (ROOT / p).is_dir() and not p.startswith(".git")}
    if any(p == ".git" or p.startswith(".git/") for p in opened if (ROOT / p).is_dir()):
        files.add(".git")  # the repository's own git state was read: not known by content, so never reused
    return files, dirs


def _entry(r: dict[str, set[str]], answers: dict[str, str], extra: set[str] = frozenset()) -> dict:  # noqa: B006
    """One kept read set: the paths it read (their contents in the store's one table, `states`), its git questions' answers and
    the programs not known."""
    files, dirs = _paths(r, extra)
    return {"opaque": sorted(r.get("opaque", set())), "files": sorted(files), "dirs": sorted(dirs),
            "git": {q: answer(q, answers) for q in sorted(r.get("git", set()))}}  # fmt: skip


def _named(e: dict) -> set[str]:
    return {"f:" + p for p in e.get("files", [])} | {"d:" + p for p in e.get("dirs", [])}


def _now(key: str, ids: dict[str, str], entries: dict[str, list[str]]) -> str:
    """A table key's content here: `f:<path>` a file's, `d:<path>` a directory's entries."""
    return _state("file" if key[0] == "f" else "dir", key[2:], ids, entries)


def _keep(d: pathlib.Path) -> None:
    """Merge the workers' and the children's reads, and keep each passed TEST's, its file's and the session's (amendment 5)."""
    reads: dict[str, dict[str, set[str]]] = {}
    failed: set[str] = set()
    ran: set[str] = set()
    collected: dict[str, list[str]] = {}
    reused_ids: set[str] = set()
    for w in d.glob("worker-*.json"):
        data = json.loads(w.read_text(encoding="utf-8"))
        for k, r in data["reads"].items():
            for kk, v in r.items():
                reads.setdefault(k, {}).setdefault(kk, set()).update(v)
        failed.update(data["failed"])
        ran.update(data["ran"])
        reused_ids.update(data.get("reused_ids", []))
        for f, ns in data.get("collected", {}).items():
            collected[f] = sorted(set(collected.get(f, [])) | set(ns))
    for log in d.glob("children-*.log"):
        for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
            k, _, rest = line.partition("\t")
            kind, _, path = rest.partition("\t")
            if k and kind:
                reads.setdefault(k, {}).setdefault(kind, set()).add(path)
    gaps = shim_gaps(reads)
    for r in reads.values():  # the C recorder's reads join Python's; its children are known only where it saw all Python saw
        r.setdefault("file", set()).update(r.pop("c-file", set()), r.pop("py-file", set()))
        r.setdefault("dir", set()).update(r.pop("c-dir", set()))
        known = r.pop("c", set())
        if gaps:
            r.setdefault("opaque", set()).update(known)
    if gaps:
        (d / "shim-gaps.json").write_text(json.dumps({f: sorted(g)[:20] for f, g in gaps.items()}), encoding="utf-8")
    store = _store()
    if store is None:
        return
    if GATE:  # what this run reused, for `incremental carry`; the reads go to `.next`, promoted only with a green baseline
        (pathlib.Path(GATE) / GATE_REUSED).write_text(json.dumps(sorted(reused_ids)), encoding="utf-8")
    out = store.with_name(store.name + ".next") if GATE else store
    ids, entries = _ids()
    answers: dict[str, str] = {}
    try:
        kept = json.loads(store.read_text(encoding="utf-8")) if store.is_file() else {}
    except OSError, ValueError:
        kept = {}
    if kept.get("v") != STORE_VERSION or kept.get("py") != sys.version or "states" not in kept:
        kept = {"v": STORE_VERSION, "py": sys.version, "states": {}, "session": {}, "files": {}, "tests": {}}
    states: dict[str, str] = kept["states"]
    new_tests: dict[str, dict] = {}
    for n in ran - failed:
        new_tests[n] = _entry(reads.get(n, {}), answers)
    new_files = {f: {"nodeids": ns, "entry": _entry(reads.get(f, {}), answers, file_inputs(f))} for f, ns in collected.items()}
    # THE SESSION'S READS ARE KEPT AS A UNION: a run that reused every test needing a session fixture never ran it
    old = kept.get("session", {})
    session = {k: set(v) for k, v in reads.get(SESSION, {}).items()}
    session.setdefault("git", set()).update(old.get("git", {}))
    session.setdefault("opaque", set()).update(old.get("opaque", []))
    new_session = _entry(session, answers)  # the old entry's paths are already relative: merged after, never re-resolved
    new_session["files"] = sorted(set(new_session["files"]) | set(old.get("files", [])))
    new_session["dirs"] = sorted(set(new_session["dirs"]) | set(old.get("dirs", [])))
    # EACH READ'S CONTENT IS KEPT ONCE (plan D32a), taken now; an entry kept earlier against a content that moved is dropped, so
    # no entry is ever judged against a content it did not see
    recorded = set().union(*(_named(e) for e in [*new_tests.values(), *(v["entry"] for v in new_files.values()), new_session]))
    now = {k: _now(k, ids, entries) for k in recorded}
    moved = {k for k, v in now.items() if k in states and states[k] != v}
    # a test kept earlier stood on its file's and the session's reads as they were then: where those moved, it is dropped too
    session_moved = bool((_named(old) | _named(new_session)) & moved)
    files_moved = {f for f, v in new_files.items() if _named(v["entry"]) & moved}
    for n, e in list(kept["tests"].items()):
        stale = n not in new_tests and (bool(_named(e) & moved) or session_moved or _rel(n) in files_moved)
        if n in failed or stale:
            del kept["tests"][n]
    for f, v in list(kept["files"].items()):
        if f not in new_files and (_named(v["entry"]) & moved or session_moved):
            del kept["files"][f]
    kept["tests"].update(new_tests)
    kept["files"].update(new_files)
    kept["session"] = new_session
    states.update(now)
    named = set().union(_named(kept["session"]), *(_named(e) for e in kept["tests"].values()), *(_named(v["entry"]) for v in kept["files"].values()))
    kept["states"] = {k: v for k, v in states.items() if k in named}
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(f".{os.getpid()}.tmp")
    tmp.write_text(json.dumps(kept), encoding="utf-8")
    tmp.replace(out)


def shim_gaps(reads: dict[str, dict[str, set[str]]]) -> dict[str, set[str]]:
    """Per test file, the files a Python child opened (Python's own recorder) that the preloaded C recorder did not see - the
    run's check of the C recorder (plan D26): every Python child carries both. Any gap and nothing is reused on the C recorder."""
    out: dict[str, set[str]] = {}
    for f, r in reads.items():
        c_saw = r.get("c-file", set()) | r.get("c-dir", set())
        if not c_saw and not r.get("c"):
            continue  # no child this run was the C recorder's to check
        missed = {p for p in r.get("py-file", set()) if p not in c_saw and not _rel_path(p).startswith(CACHE_READS)}
        if missed:
            out[f] = missed
    return out


def entry_ok(e: dict, states: dict[str, str], ids: dict[str, str], entries: dict[str, list[str]], answers: dict[str, str] | None = None, memo: dict[str, str] | None = None) -> bool:
    """Is one kept read set still what it was: no program not known, no read of a file git ignores, every path it names as the
    store's table holds it, every git answer the same? Reads are kept relative to the repository, so a worktree compares with
    its clone."""
    if e.get("opaque") or "error" in e.get("git", {}).values():
        return False
    memo = {} if memo is None else memo
    for k in _named(e):
        was = states.get(k)
        if was is None or was == "ignored":
            return False
        if k not in memo:
            memo[k] = _now(k, ids, entries)
        if memo[k] != was:
            return False
    return all(answer(q, answers if answers is not None else {}) == was for q, was in e.get("git", {}).items())


def reusable_tests(kept: dict, ids: dict[str, str], entries: dict[str, list[str]], answers: dict[str, str], allowed: set[str] | None = None) -> tuple[set[str], dict[str, int]]:
    """(the node ids whose own reads, their file's and the session's are all unchanged; {file: its test count} for each file
    every recorded test of which is among them - such a file is not collected at all)."""
    states, memo = kept.get("states", {}), {}
    if "states" not in kept or kept.get("v") != STORE_VERSION or kept.get("py") != sys.version or not entry_ok(kept.get("session", {}), states, ids, entries, answers, memo):
        return set(), {}
    file_ok = {f: entry_ok(e["entry"], states, ids, entries, answers, memo) for f, e in kept.get("files", {}).items() if f.startswith(TREE)}
    tests = {n for n, e in kept.get("tests", {}).items() if file_ok.get(_rel(n)) and (allowed is None or n in allowed) and entry_ok(e, states, ids, entries, answers, memo)}
    whole = {f: len(e["nodeids"]) for f, e in kept.get("files", {}).items() if file_ok.get(f) and e["nodeids"] and set(e["nodeids"]) <= tests}
    return tests, whole


def answer(question: str, answers: dict[str, str]) -> str:
    """A git question's answer here (`l7r_dep_rules.ask`), asked once per run however many test files asked it."""
    if question not in answers:
        answers[question] = rules.ask(question, str(ROOT))
    return answers[question]


def reuse_set(config: pytest.Config) -> tuple[set[str], dict[str, int]]:
    """What this run reuses, decided once per process before collection (amendment 3 plan D25; per test since amendment 5)."""
    cached = getattr(config, "_l7r_reuse_set", None)
    if cached is not None:
        return cached
    out: tuple[set[str], dict[str, int]] = (set(), {})
    if REUSING and getattr(config, "_l7r_deps", False):
        store = _store()
        try:
            kept = json.loads(store.read_text(encoding="utf-8")) if store and store.is_file() else {}
        except OSError, ValueError:
            kept = {}
        if kept:
            ids, entries = _ids()
            out = reusable_tests(kept, ids, entries, {}, gate_baseline_tests(GATE))
    config._l7r_reuse_set = out  # type: ignore[attr-defined]
    return out


def pytest_ignore_collect(collection_path: pathlib.Path, config: pytest.Config) -> bool | None:
    """A test file every test of which is reused is not collected: its module is never imported (FR-022)."""
    if not REUSING or not getattr(config, "_l7r_deps", False) or collection_path.suffix != ".py":
        return None
    rel = _rel_path(str(collection_path))
    _tests, whole = reuse_set(config)
    if rel not in whole:
        return None
    config.__dict__.setdefault("_l7r_skipped", {})[rel] = whole[rel]
    return True


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Every collected test of the tree is noted by its file (before any deselection), and in a reuse run each reused test is
    deselected."""
    if not getattr(config, "_l7r_deps", False):
        return
    for i in items:
        if _rel(i.nodeid).startswith(TREE):
            _collected.setdefault(_rel(i.nodeid), []).append(i.nodeid)
    if not REUSING:
        return
    tests, _whole = reuse_set(config)
    gone = [i for i in items if i.nodeid in tests]
    if gone:
        items[:] = [i for i in items if i.nodeid not in tests]
        config.hook.pytest_deselected(items=gone)
    skipped = config.__dict__.get("_l7r_skipped", {})
    _reused_ids.update(i.nodeid for i in gone)
    _reused_ids.update(n for n in tests if _rel(n) in skipped)
    config._l7r_reused = (len(skipped), sum(skipped.values()) + len(gone))  # type: ignore[attr-defined]


def pytest_terminal_summary(terminalreporter, config: pytest.Config) -> None:  # noqa: ANN001
    reused = getattr(config, "_l7r_reused", None)
    if reused and (reused[0] or reused[1]):
        terminalreporter.write_line(
            f"reused the clone's passes: {reused[1]} tooling test(s), {reused[0]} file(s) of them not even collected, on identical inputs (feature 383 FR-013, per test since amendment 5)"
        )
