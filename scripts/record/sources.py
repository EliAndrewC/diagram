#!/usr/bin/env python3
"""The sources-consulted ledger and the saved-page cache keyed by URL (feature 288).

WHY (specs/288-sources-ledger-and-page-cache/research.md R1, observed 2026-09-29). Nothing recorded that a page was
read and NOT cited: 208 uncited pages were read again in a later session, 144 of them under another feature, and the
later reader never knew the page had already been judged. And the pages `make source-pages` saved were filed per run
under `/tmp/l7r-check/<run>/`, so a page saved once was never found again. The GM asked for both cheap fixes:

THE LEDGER, `<mirror>/.specify/sources-consulted.jsonl`, host-wide beside `make claim`'s and `make reserve`'s ledgers
and appended under their kind of lock: one JSON line per read - the normalized URL, the UTC time, the feature, clone,
session and question(s), and the outcome (`cited:<key>`, `rejected:<why>`, `nothing-found`, `unreadable`, `pending`;
the one-time seed writes `unknown-outcome`). `make source-pages` prints a URL's earlier lines BEFORE it fetches, and
appends `pending` for each page it saves; `make source-outcome` records the judgment; a registry entry marks its URL
`cited:<key>` (`make reserve ... URL=`, or the fill pass `make record` and `make sources-consulted` run).

THE CACHE, `<mirror>/.specify/page-cache/<h2>/<h>/`, `<h>` the SHA-256 of the normalized URL: `meta.json`, the page's
visible text as fetched (`text.txt`) and its saved form in parts as `make source-pages` writes it (`page.txt`, or
`page.p1.txt` ...). Every tool that fetches a source page reads it through the cache (the `research` crate's `CachedPages`),
so a page is fetched once.

NO GUARD (R1: the saving is too small for a refusal): the tooling prints what is known where it matters.

WHAT IS LEFT HERE (feature 449 T145, phase 4's S2; cut by T147, S3b): the ledger's and the cache's commands are `l7r-gate record
sources ...` (`rust/gate/crates/record/src/record/sources.rs`), the ledger's half the guard's `shared::consulted`, the cache the
`research` crate's `pages`, and the uncited filter that read and stored pages through this file is the `uncited` crate. What stays is
what `archive.py` - a door for S4's `research_search.py` and `semantic_index.py` - still imports: `repo_root` and `home` (reads,
`ask:449-T81-slices`) and `raised`, by which its push forwarder raises the Rust's refusal. An edit of a read here makes the same
change in the Rust (`shared::consulted`).
"""

from __future__ import annotations

import builtins
import contextlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent


def _blocked():  # noqa: ANN202 - the record's module, imported on first use so this file stays importable alone
    """`l7r/diagram/interactive/record/blocked.py` (feature 312 FR-001 - FR-003): its exceptions, which `raised` names."""
    skill = str(HERE.parents[1])  # the repository root, where l7r/ is
    if skill not in sys.path:
        sys.path.insert(0, skill)
    from l7r.diagram.interactive.record import blocked  # noqa: PLC0415

    return blocked


def repo_root(start: pathlib.Path | None = None) -> pathlib.Path:
    """The repository this runs in: the nearest directory above `start` holding `.git`."""
    root = (start or pathlib.Path.cwd()).resolve()
    while not (root / ".git").exists() and root != root.parent:
        root = root.parent
    return root


def home(root: pathlib.Path | None = None) -> pathlib.Path:
    """Where the ledger and the cache live: the MIRROR's `.specify/` (a clone's grandparent when its parent is
    `.clones`), which is the host volume every clone sees. `L7R_SOURCES_HOME` moves it - the tests' seam."""
    if os.environ.get("L7R_SOURCES_HOME"):
        return pathlib.Path(os.environ["L7R_SOURCES_HOME"])
    root = repo_root() if root is None else root
    mirror = root.parent.parent if root.parent.name == ".clones" else root
    return mirror / ".specify"


def raised(stderr: str) -> Exception:
    """What a forwarder raises for a write the Rust refused (feature 449 T145): the exception the Python raised there - the blocked
    list's own (`Blocked`, `BlockedListError`) or a built-in one, by the kind on the Rust's last line, `<Kind>: <message>` - so a
    caller that catches it by kind still does; a kind with no such exception is a `RuntimeError` with the Rust's words."""
    last = stderr.strip().splitlines()[-1] if stderr.strip() else ""
    kind, _, message = last.partition(": ")
    cls = getattr(_blocked(), kind, None) if kind in ("Blocked", "BlockedListError") else getattr(builtins, kind, None)
    if isinstance(cls, type) and issubclass(cls, Exception):
        with contextlib.suppress(TypeError):  # an exception whose constructor takes more than words (`UnicodeDecodeError`)
            return cls(message)
    return RuntimeError(stderr.strip())
