#!/usr/bin/env python3
"""The source archive's Python door, until S4 ports the Python that imports it (feature 449 T146, phase 4's S3a; cut by T147, S3b).

`archive.py` archived every source the record cites into the PRIVATE repository EliAndrewC/diagram-research (feature 309). Its
commands are `l7r-gate record archive url|backfill|report|gm-copies|inbox|consulted|find|urls|relayout` now
(`rust/gate/crates/archive/`), its browser the one browser crate (`rust/browser/`, `l7r-browser`, `ask:449-phase4-slices` Q4), and
every write it made has ONE writer, the Rust (FR-003): the archive's working copy, its manifest rows, the backfill's lanes.

WHAT IS LEFT HERE is what S4's `research_search.py` and `semantic_index.py` still reach (observed 2026-11-16, method: each importer's
uses of `ar.` read): `src` (for `repo_root`), `home_of`, `git_env`, `token`, and `Archive`'s `dir`, its lock and its `git` - reads,
half-ported as `ask:449-T81-slices` lets them stay - and `Archive.push`, a forwarder to `l7r-gate record archive push`
(`ask:449-T86-door`), which runs while the caller holds `Archive.locked()`, so the Rust takes no lock for it. A failed write raises
the exception the Python raised, by the kind on the Rust's last line (`sources.raised`). T147 (S3b) deleted the rest with
`uncited.py`, `uncited_imports.py` and `archive_ops.py`, its last importers. An edit of a read here makes the same change in the Rust
in the same commit (`ask:449-phase4-slices`).
"""

from __future__ import annotations

import base64
import contextlib
import fcntl
import os
import pathlib
import subprocess
import sys
import time
from collections.abc import Iterator

HERE = pathlib.Path(__file__).resolve().parent
for _p in (str(HERE), str(HERE.parents[1])):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import sources as src  # noqa: E402

from l7r.diagram.interactive.record import archive as rec  # noqa: E402

GATE = HERE.parent / "gates" / "l7r-gate.sh"
REMOTE = rec.REPO + ".git"
WORKDIR = "source-archive"
LOCK = "source-archive.lock"


def _gate(args: list[str], *, env: dict[str, str] | None = None) -> str:
    """`l7r-gate record archive <args>`: its stdout; a refusal raises what the Python raised, by kind."""
    done = subprocess.run([str(GATE), "record", "archive", *args], input=b"", env=env, check=False, capture_output=True)
    if done.returncode:
        raise src.raised(done.stderr.decode("utf-8", "replace"))
    return done.stdout.decode("utf-8")


def mirror(root: pathlib.Path) -> pathlib.Path:
    """The mirror: a clone's grandparent under `.clones/`, else the repository itself."""
    return root.parent.parent if root.parent.name == ".clones" else root


def git_env(token: str) -> dict[str, str]:
    """The environment that authenticates git to GitHub with the PAT as an extra header (FR-011)."""
    basic = base64.b64encode(f"x-access-token:{token}".encode()).decode()
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_CONFIG_")}
    env.update({"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "http.https://github.com/.extraheader",
                "GIT_CONFIG_VALUE_0": f"AUTHORIZATION: basic {basic}", "GIT_TERMINAL_PROMPT": "0"})
    return env


def token(root: pathlib.Path) -> str:
    # only a push needs the secrets; the one reader is the Rust gate's (feature 449 T064)
    return subprocess.run([str(GATE), "github-token"], cwd=mirror(root), capture_output=True, text=True, check=False).stdout.strip()


class Archive:
    """The host's one working copy of the archive repository: its lock and its `git` read here, its push the Rust's."""

    def __init__(self, home: pathlib.Path, remote: str = REMOTE, env: dict[str, str] | None = None) -> None:
        self.home, self.remote, self.env = home, remote, env
        self.dir = home / WORKDIR

    @contextlib.contextmanager
    def locked(self, timeout: float = 600.0) -> Iterator[None]:
        self.home.mkdir(parents=True, exist_ok=True)
        fd = os.open(self.home / LOCK, os.O_RDWR | os.O_CREAT, 0o644)
        deadline = time.monotonic() + timeout
        try:
            while True:
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    if time.monotonic() >= deadline:
                        raise TimeoutError(f"could not take {self.home / LOCK} within {timeout:g}s") from None
                    time.sleep(0.05)
            yield
        finally:
            os.close(fd)

    def git(self, *args: str, check: bool = True) -> subprocess.CompletedProcess:
        return subprocess.run(["git", "-C", str(self.dir), *args], env=self.env, capture_output=True, text=True, check=check)

    def push(self) -> str:
        """Push `main` (call under the lock): '' on success or with nothing committed yet, else git's complaint (the Rust's)."""
        return _gate(["push", "--home", os.path.abspath(self.home)], env=self.env).rstrip("\n")


def home_of(root: pathlib.Path) -> pathlib.Path:
    """Where the working copy and its lock live: beside the page cache, `sources.home` (the tests' seam moves both)."""
    return src.home(root)
