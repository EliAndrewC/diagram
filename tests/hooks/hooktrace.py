#!/usr/bin/env python3
"""A guard suite's inputs by what it READ the last time it went green (feature 383 amendment 3, plan D27).

`hookdeps.py` derives a suite's inputs from the names its files mention, and two suites - sync-with-main and gate-stamp,
whose fixtures copy the whole of `scripts/` and run the push in it - are held to the whole tree: they re-ran on 42 of 44
tooling landings (2026-10-03 to 10-17). Here each suite runs under the preloaded C-library recorder
(`tests/tooling/_deps_site/l7r_file_log.c`): every file it opens, stats or lists under the repository - a fixture's copy of a
script standing for the repository's file of that name, a fixture's `cp` not counted - is kept by content when the suite goes
green, and the suite is skipped while every one of those reads is unchanged. A suite that read the repository's own git
directory (a clone of the real repository: its content comes through git, which the recorder does not follow), or a file git
ignores, is not traced: it keeps `hookdeps.py`'s key.

    hooktrace.py shim <gitdir>                      the recorder, built once per version of its source; its path, or nothing
    hooktrace.py stamp <gitdir> <guard> <log> <root>  keep a green suite's reads (none kept where it cannot be traced)
    hooktrace.py fresh <gitdir> <root> <guard>...   print the guards whose kept reads are all unchanged
"""

from __future__ import annotations

import hashlib
import json
import os
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
SRC = REPO / "tests" / "tooling" / "_deps_site" / "l7r_file_log.c"
sys.path.insert(0, str(REPO / "scripts" / "record"))
import record_cache  # noqa: E402 - the content ids every reuse here compares by

SKIP = (".git/l7r-cache/", ".git/hooks-test/")  # content caches and the stamps themselves


def shim(gitdir: pathlib.Path) -> str:
    if not SRC.is_file():
        return ""
    so = gitdir / "l7r-cache" / f"l7r_file_log-{hashlib.sha256(SRC.read_bytes()).hexdigest()[:12]}.so"
    if so.is_file():
        return str(so)
    so.parent.mkdir(parents=True, exist_ok=True)
    tmp = so.with_suffix(f".{os.getpid()}.tmp")
    try:
        ok = subprocess.run(["gcc", "-shared", "-fPIC", "-O2", "-o", str(tmp), str(SRC), "-ldl"], capture_output=True, check=False).returncode == 0
    except OSError:
        ok = False
    if not ok:
        tmp.unlink(missing_ok=True)
        return ""
    tmp.replace(so)
    return str(so)


def recorder_version() -> str:
    return hashlib.sha256(SRC.read_bytes()).hexdigest()[:12] if SRC.is_file() else ""


def _rel(path: str, root: pathlib.Path) -> str:
    rel = os.path.relpath(path, root).replace(os.sep, "/")
    if "/__pycache__/" in f"/{rel}" and rel.endswith(".pyc"):
        head, _, name = rel.rpartition("__pycache__/")
        rel = head + name.split(".", 1)[0] + ".py"
    return "" if rel == "." else rel


def _ids(root: pathlib.Path) -> tuple[dict[str, str], dict[str, list[str]]]:
    ids = record_cache.content_ids(root, untracked=True)
    entries: dict[str, set[str]] = {}
    for rel in ids:
        parts = rel.split("/")
        for i in range(len(parts)):
            entries.setdefault("/".join(parts[:i]), set()).add(parts[i])
    return ids, {d: sorted(e) for d, e in entries.items()}


def _state(kind: str, rel: str, root: pathlib.Path, ids: dict[str, str], entries: dict[str, list[str]]) -> str:
    if kind == "dir":
        return json.dumps(entries.get(rel, []))
    return ids.get(rel) or ("absent" if not (root / rel).exists() else ("dir" if (root / rel).is_dir() else "ignored"))


def reads(log: pathlib.Path, root: pathlib.Path) -> dict[str, set[str]] | None:
    """{'file': rels, 'dir': rels} from a suite's log, or None where it cannot be traced (git read the repository)."""
    out: dict[str, set[str]] = {"file": set(), "dir": set()}
    if not log.is_file():
        return out
    for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
        _f, _, rest = line.partition("\t")
        kind, _, path = rest.partition("\t")
        if kind == "c-git":
            return None
        rel = _rel(path, root)
        if rel and not rel.startswith(SKIP) and rel != ".git" and kind in ("c-file", "c-dir"):
            out[kind[2:]].add(rel)
    return out


def trace_file(gitdir: pathlib.Path, guard: str) -> pathlib.Path:
    return gitdir / "hooks-test" / f"{guard}.trace.json"


def stamp(gitdir: pathlib.Path, guard: str, log: pathlib.Path, root: pathlib.Path) -> int:
    target = trace_file(gitdir, guard)
    r = reads(log, root)
    target.unlink(missing_ok=True)
    if r is None or not r["file"]:
        return 0  # not traced (or a run without the recorder): the suite keeps hookdeps' key
    ids, entries = _ids(root)
    files = {rel: _state("file", rel, root, ids, entries) for rel in sorted(r["file"])}
    if "ignored" in files.values():
        return 0  # it read a file git ignores: not known by content
    dirs = {rel: _state("dir", rel, root, ids, entries) for rel in sorted(r["dir"])}
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({"py": sys.version, "recorder": recorder_version(), "files": files, "dirs": dirs}), encoding="utf-8")
    return 0


def fresh(gitdir: pathlib.Path, root: pathlib.Path, guards: list[str]) -> list[str]:
    kept = {g: json.loads(trace_file(gitdir, g).read_text(encoding="utf-8")) for g in guards if trace_file(gitdir, g).is_file()}
    if not kept:
        return []
    ids, entries = _ids(root)
    return [
        g
        for g, k in kept.items()
        if k.get("py") == sys.version
        and k.get("recorder") == recorder_version()  # a trace by an older recorder may lack what this one sees
        and all(_state("file", rel, root, ids, entries) == was for rel, was in k["files"].items())
        and all(_state("dir", rel, root, ids, entries) == was for rel, was in k["dirs"].items())
    ]


def main(argv: list[str]) -> int:
    if len(argv) >= 2 and argv[0] == "shim":
        print(shim(pathlib.Path(argv[1])))
        return 0
    if len(argv) == 5 and argv[0] == "stamp":
        return stamp(pathlib.Path(argv[1]), argv[2], pathlib.Path(argv[3]), pathlib.Path(argv[4]))
    if len(argv) >= 3 and argv[0] == "fresh":
        print("\n".join(fresh(pathlib.Path(argv[1]), pathlib.Path(argv[2]), argv[3:])))
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
