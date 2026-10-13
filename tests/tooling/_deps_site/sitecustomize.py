"""What a Python process started by a tooling test reads (feature 383 amendment 1, FR-013; `tests/tooling/_test_deps.py`).

Put on PYTHONPATH by the tooling tree's plugin while it records: every Python process a test starts imports this first, and
- while `L7R_TEST_DEP_LOG` names a log - notes each file it opens and each directory it lists under the repository
(`L7R_TEST_DEP_ROOT`), and each other program it starts there, as lines `<test file>\t<kind>\t<path>`, each written as it is first seen. The
system's own sitecustomize, which this one shadows, is run first.
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
for _d in sys.path:
    _f = os.path.join(_d or ".", "sitecustomize.py")
    if os.path.abspath(_d or ".") != _HERE and os.path.isfile(_f):
        try:
            with open(_f, encoding="utf-8") as _fh:
                exec(compile(_fh.read(), _f, "exec"), {"__name__": "sitecustomize_system", "__file__": _f})  # noqa: S102
        except Exception:  # noqa: BLE001, S110 - the system's hook failing must not fail the test's process
            pass
        break

_LOG = os.environ.get("L7R_TEST_DEP_LOG")
# only a process a test started: the test workers themselves inherit the log with no test named, and record in-process
if _LOG and os.environ.get("L7R_TEST_DEP_FILE"):
    _ROOT = os.environ.get("L7R_TEST_DEP_ROOT", "")
    _FILE = os.environ.get("L7R_TEST_DEP_FILE", "")
    _SEEN: set[tuple[str, str]] = set()
    _LOCATION = {"--show-toplevel", "--git-dir", "--git-common-dir", "--absolute-git-dir", "--show-prefix", "--show-cdup",
                 "--is-inside-work-tree", "--path-format=absolute", "--path-format=relative"}  # _test_deps.LOCATION

    def _under(path: object) -> str:
        try:
            p = os.path.abspath(os.fsdecode(path))  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return ""
        return p if _ROOT and (p == _ROOT or p.startswith(_ROOT + os.sep)) else ""

    def _hook(event: str, args: tuple) -> None:
        if event == "open" and args and isinstance(args[0], (str, bytes)):
            mode = args[1] if len(args) > 1 else "r"
            if isinstance(mode, str) and any(c in mode for c in "wax+"):
                return
            p = _under(args[0])
            if p:
                _note("file", p)
        elif event in ("os.listdir", "os.scandir") and args:
            p = _under(args[0] if args[0] is not None else ".")
            if p:
                _note("dir", p)
        elif event == "subprocess.Popen" and args:
            exe, argv, cwd = args[0], args[1], args[2] if len(args) > 2 else None
            env = args[3] if len(args) > 3 else None
            name = os.path.basename(os.fsdecode(exe if exe else (argv[0] if argv else ""))) if (exe or argv) else ""
            flags = {os.fsdecode(a) for a in (argv or [])[1:3] if isinstance(a, (str, bytes))}
            recorded = env is None or (env.get("L7R_TEST_DEP_LOG") and _HERE in str(env.get("PYTHONPATH", "")))
            if name.startswith("python") and recorded and not flags & {"-I", "-S", "-E", "-IS", "-ISE"}:
                return  # a Python child records its own reads through this module
            if name.startswith("python"):
                _note("opaque", name)  # isolated, or its environment drops this module: what it reads is not known
                return
            words = [os.fsdecode(a) for a in (argv or []) if isinstance(a, (str, bytes))]
            where = next((words[i + 1] for i, w in enumerate(words[:-1]) if w == "-C"), None)
            paths = [w for w in words[1:] if os.path.isabs(w) and w != where]
            sub = next((w for w in words[1:] if not w.startswith("-") and w != where and "=" not in w), "")
            if name in ("sleep", "true", "false", "echo"):
                hit = False  # reads no file of the repository
            elif name == "git" and sub == "rev-parse" and words[words.index("rev-parse") + 1:] and all(w in _LOCATION for w in words[words.index("rev-parse") + 1:]):
                hit = False  # asks only where the repository is
            elif name == "git" and where is None and sub in ("init", "clone") and paths:
                hit = any(_under(w) for w in paths)  # init and clone read nothing where they run: the paths they name
            else:
                hit = bool(_under(where or cwd or os.getcwd())) or any(_under(w) for w in paths)
            if hit:
                _note("opaque", name)  # the same rule as tests/tooling/_test_deps.py's against_repo

    try:
        _OUT = open(_LOG, "a", encoding="utf-8", buffering=1)  # noqa: SIM115 - written as each read is first seen
    except OSError:
        _OUT = None

    def _note(kind: str, path: str) -> None:
        # each read written as it is first seen, never only at exit: a child that ends by os._exit or a signal would leave
        # its reads unrecorded, and a test file reused on a record missing them would be reused unsafely
        if (kind, path) not in _SEEN and _OUT is not None:
            _SEEN.add((kind, path))
            try:
                _OUT.write(f"{_FILE}\t{kind}\t{path}\n")
            except (OSError, ValueError):
                pass

    sys.addaudithook(_hook)
