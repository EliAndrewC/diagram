"""What a program a tooling test starts reads, judged the same way in the test's process and in every Python process it starts
(feature 383 amendments 1 and 2; `tests/tooling/_test_deps.py`, `sitecustomize.py` beside this file). Standard library only:
every Python child imports it.

A child is one of three things:
- KNOWN: it reads nothing of the repository (`against_repo` says no), or it is a Python process that records its own reads;
- a GIT QUESTION (amendment 2, FR-015): a read-only git command asked of the repository, kept with a digest of its answer and
  asked again at reuse (`ask`) - the same answer is the same input;
- OPAQUE: anything else run against the repository - what it read is not known, so its test file always runs.

A Python child given a fresh environment (`env={...}` without the recording) is ADOPTED (FR-016): the recording's variables
are put into that environment before the child starts, so it records itself. One run isolated (`-I`, `-E`, `-S`) ignores them
and stays opaque.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess

#: programs that read no file of the repository wherever they run
READ_NOTHING = frozenset({"sleep", "true", "false", "echo"})
#: `git rev-parse` asking only WHERE the repository is: its answer depends on the checkout's place, not on its content
LOCATION = frozenset(
    {"--show-toplevel", "--git-dir", "--git-common-dir", "--absolute-git-dir", "--show-prefix", "--show-cdup", "--is-inside-work-tree", "--path-format=absolute", "--path-format=relative"}
)
#: git commands that answer from the repository and change nothing a test could read back (a `status` may refresh the index's
#: stat cache, which no answer shows)
READ_ONLY_GIT = frozenset(
    {
        "ls-files",
        "ls-tree",
        "show",
        "diff",
        "log",
        "rev-parse",
        "merge-base",
        "cat-file",
        "status",
        "rev-list",
        "diff-tree",
        "diff-index",
        "for-each-ref",
        "show-ref",
        "grep",
        "blame",
        "describe",
        "name-rev",
        "check-ignore",
        "hash-object",
    }
)
#: words that make a read-only command read its standard input or a file of its own (`blame --contents`), or write a file: its
#: answer cannot be asked again
NOT_REPLAYABLE = ("--stdin", "--batch", "--output", "--contents", "-w", "--write", "--ext-diff", "--textconv")
ISOLATED = frozenset({"-I", "-S", "-E", "-IS", "-ISE"})
RECORDING = ("L7R_TEST_DEP_LOG", "L7R_TEST_DEP_FILE", "L7R_TEST_DEP_ROOT")
#: what a non-Python child needs to be recorded by the C library (amendment 3, plan D26): the preloaded recorder, and libuv's
#: io_uring off, whose file calls would pass the library by
SHIM_ENV = "L7R_TEST_DEP_SHIM"
ROOT_MARK = "{ROOT}"
#: git variables that steer which repository, index or objects a command reads: a question asked under one names a place the
#: replay would not see. The configuration variables (`GIT_CONFIG_COUNT`, set for every session here) are kept: the replay runs
#: under the same environment, and an answer they change differs, so the file runs
STEERING = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_COMMON_DIR", "GIT_NAMESPACE")


def under(path: object, root: str) -> str:
    """The absolute path when it is the repository or inside it, else ""."""
    try:
        p = os.path.abspath(os.fsdecode(path))  # type: ignore[arg-type]
    except TypeError, ValueError:
        return ""
    return p if root and (p == root or p.startswith(root + os.sep)) else ""


def _where(words: list[str]) -> str | None:
    return next((words[i + 1] for i, w in enumerate(words[:-1]) if w == "-C"), None)


def _sub(words: list[str], where: str | None) -> str:
    skip = False
    for w in words[1:]:
        if skip:
            skip = False
            continue
        if w in ("-C", "-c"):
            skip = True
            continue
        if not w.startswith("-") and w != where and "=" not in w:
            return w
    return ""


def location_only(words: list[str]) -> bool:
    rest = words[words.index("rev-parse") + 1 :] if "rev-parse" in words else []
    return bool(rest) and all(w in LOCATION for w in rest)


def against_repo(name: str, words: list[str], cwd: object, root: str) -> bool:
    """Does a program work in or on the repository? Unless both its working directory (and any `-C`) are outside it and no
    argument names a path inside it, yes - the plan review's rule (a `git worktree add /tmp/x HEAD` run in the repository
    names an outside path and reads the repository). Two git forms read nothing where they run: `git init <dir>` and
    `git clone <src> <dst>`, judged by the paths they name."""
    where = _where(words)
    paths = [w for w in words[1:] if os.path.isabs(w) and w != where]
    sub = _sub(words, where)
    if name in READ_NOTHING:
        return False
    if name == "git" and sub == "rev-parse" and location_only(words):
        return False
    if name == "git" and where is None and sub in ("init", "clone") and paths:
        return any(under(w, root) for w in paths)
    return bool(under(where or cwd or os.getcwd(), root)) or any(under(w, root) for w in paths)


def git_question(words: list[str], cwd: object, env: object, root: str) -> str:
    """A read-only git command as a question that can be asked again in another checkout: `[working dir, argv...]` with the
    repository's path written `{ROOT}`, as JSON; "" when it cannot be asked again - a command that may write, one reading its
    standard input, or one steered by a `STEERING` variable."""
    where = _where(words)
    sub = _sub(words, where)
    if sub not in READ_ONLY_GIT or any(w.startswith(NOT_REPLAYABLE) for w in words[1:]):
        return ""
    if sub == "hash-object" and "-w" in words:
        return ""
    environ = env if isinstance(env, dict) else os.environ
    if any(str(k) in STEERING for k in environ):
        return ""
    here = os.path.abspath(os.fsdecode(cwd)) if cwd else os.getcwd()
    return json.dumps([_mark(here, root), *[_mark(w, root) for w in words[1:]]])


def _mark(word: str, root: str) -> str:
    return word.replace(root, ROOT_MARK) if root else word


def ask(question: str, root: str) -> str:
    """The digest of a git question's answer in the checkout at `root`: its exit status, its output and its errors, the
    checkout's path written `{ROOT}` so a worktree's answer compares with its clone's. "error" when it cannot be asked."""
    try:
        cwd, *argv = (w.replace(ROOT_MARK, root) for w in json.loads(question))
        env = {**{k: v for k, v in os.environ.items() if k not in STEERING}, "GIT_OPTIONAL_LOCKS": "0"}  # a `status` leaves the index be
        p = subprocess.run(["git", *argv], cwd=cwd, capture_output=True, env=env, timeout=60, check=False)
    except OSError, ValueError, subprocess.TimeoutExpired:
        return "error"
    h = hashlib.sha256()
    h.update(str(p.returncode).encode())
    for part in (p.stdout, p.stderr):
        h.update(b"\0" + part.replace(root.encode(), ROOT_MARK.encode()))
    return h.hexdigest()


def adopt(name: str, argv: list[str], env: object, values: dict[str, str], site: str) -> bool:
    """Is a Python child recorded? A child that inherits this process's environment is; one given its own environment is
    ADOPTED - the recording's variables put into that environment, in place, before it starts (FR-016) - unless it runs
    isolated, which ignores them."""
    if not name.startswith("python") or set(argv[1:3]) & ISOLATED:
        return False
    if env is None:
        return True
    if not isinstance(env, dict):  # a mapping passed whole (`env=os.environ`): recorded when it carries the recording
        return bool(getattr(env, "get", None) and env.get("L7R_TEST_DEP_LOG") and site in str(env.get("PYTHONPATH", "")))  # type: ignore[union-attr]
    for k in RECORDING:
        if values.get(k):
            env.setdefault(k, values[k])
    if site not in str(env.get("PYTHONPATH", "")):
        env["PYTHONPATH"] = os.pathsep.join([site, *([env["PYTHONPATH"]] if env.get("PYTHONPATH") else [])])
    return bool(env.get("L7R_TEST_DEP_LOG"))


def preload(env: object, shim: str, values: dict[str, str]) -> bool:
    """Is a non-Python child recorded by the preloaded C-library recorder? A child inheriting this process's environment is
    when the recorder is in it; one given its own environment has the recorder, io_uring's switch and the recording's variables
    put into it in place (plan D26)."""
    if not shim:
        return False
    if env is None:
        return shim in os.environ.get("LD_PRELOAD", "")
    if not isinstance(env, dict):
        return bool(getattr(env, "get", None) and shim in str(env.get("LD_PRELOAD", "")))  # type: ignore[union-attr]
    for k in RECORDING:
        if values.get(k):
            env.setdefault(k, values[k])
    if shim not in str(env.get("LD_PRELOAD", "")):
        env["LD_PRELOAD"] = " ".join([shim, *([env["LD_PRELOAD"]] if env.get("LD_PRELOAD") else [])])
    env.setdefault("UV_USE_IO_URING", "0")
    return bool(env.get("L7R_TEST_DEP_LOG"))


def judge(args: tuple, root: str, site: str) -> tuple[str, str]:
    """Judge one `subprocess.Popen` audit event (executable, argv, cwd, env): ("", "") known, ("git", question), ("c", the
    program's name) - known by the preloaded recorder, trusted only where the run's check of it holds - or ("opaque", the
    program's name)."""
    exe, argv = args[0], args[1]
    cwd = args[2] if len(args) > 2 else None
    env = args[3] if len(args) > 3 else None
    try:
        name = os.path.basename(os.fsdecode(exe if exe else (argv[0] if argv else "")))
    except TypeError, IndexError:
        name = ""
    words = [os.fsdecode(a) for a in (argv or []) if isinstance(a, (str, bytes))]
    if name.startswith("python"):
        values = {k: os.environ.get(k, "") for k in RECORDING}
        return ("", "") if adopt(name, words, env, values, site) else ("opaque", name)
    if not against_repo(name, words, cwd, root):
        return ("", "")
    if name == "git":
        q = git_question(words, cwd, env, root)
        if q:
            return ("git", q)
        return ("opaque", name)
    values = {k: os.environ.get(k, "") for k in RECORDING}
    return ("c", name) if preload(env, os.environ.get(SHIM_ENV, ""), values) else ("opaque", name)
