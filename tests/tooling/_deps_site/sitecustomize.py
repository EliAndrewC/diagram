"""What a Python process started by a tooling test reads (feature 383 amendment 1, FR-013; `tests/tooling/_test_deps.py`).

Put on PYTHONPATH by the tooling tree's plugin while it records: every Python process a test starts imports this first, and
- while `L7R_TEST_DEP_LOG` names a log - notes each file it opens and each directory it lists under the repository
(`L7R_TEST_DEP_ROOT`), and each other program it starts there, as lines `<test file>\t<kind>\t<path>`, each written as it is first seen. The
system's own sitecustomize, which this one shadows, is run first.
"""

import contextlib
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
    import l7r_dep_rules  # beside this file, on the same PYTHONPATH

    _SITE = os.path.dirname(os.path.abspath(__file__))

    def _hook(event: str, args: tuple) -> None:
        if event == "open" and args and isinstance(args[0], (str, bytes)):
            mode = args[1] if len(args) > 1 else "r"
            if isinstance(mode, str) and any(c in mode for c in "wax+"):
                return
            if mode is None and len(args) > 2 and isinstance(args[2], int) and args[2] & os.O_ACCMODE != os.O_RDONLY:
                return  # an os.open for writing (its flags, not a mode string, say so): not a read
            if mode is None and not os.path.isabs(os.fsdecode(args[0])):
                return  # an os.open by name under a directory handle (shutil.rmtree of a temporary tree): not a path here
            p = l7r_dep_rules.under(args[0], _ROOT)
            if p:
                _note("py-file", p)  # py-: a Python child's own record, which checks the C recorder (plan D26)
        elif event in ("os.listdir", "os.scandir") and args:
            p = l7r_dep_rules.under(args[0] if args[0] is not None else ".", _ROOT)
            if p:
                _note("dir", p)
        elif event == "subprocess.Popen" and args:
            kind, what = l7r_dep_rules.judge(args, _ROOT, _SITE)  # the same rule as the test's own process
            if kind:
                _note(kind, what)

    try:
        _OUT = open(_LOG, "a", encoding="utf-8", buffering=1)  # noqa: SIM115 - written as each read is first seen
    except OSError:
        _OUT = None

    def _note(kind: str, path: str) -> None:
        # each read written as it is first seen, never only at exit: a child that ends by os._exit or a signal would leave
        # its reads unrecorded, and a test file reused on a record missing them would be reused unsafely
        if (kind, path) not in _SEEN and _OUT is not None:
            _SEEN.add((kind, path))
            with contextlib.suppress(OSError, ValueError):
                _OUT.write(f"{_FILE}\t{kind}\t{path}\n")

    sys.addaudithook(_hook)
