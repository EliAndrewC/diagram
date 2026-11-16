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

WHAT IS LEFT HERE (feature 449 T145, phase 4's S2; the plan review's FR-003 ruling, ONE LIVE WRITER per shared file): the ledger's
and the cache's commands are `l7r-gate record sources ...` (`rust/gate/crates/record/src/record/sources.rs`), the ledger's half the
guard's `shared::consulted`, the cache the `research` crate's `pages`. What stays is what `archive.py`, `uncited.py` and
`uncited_imports.py` still import until S3a and S3b port them: the READS (`norm`, `home`, `read`, `cached`, ...), which
`ask:449-T81-slices` lets stay half-ported, and `put`, the cache's one write they make, a forwarder to `l7r-gate record sources
put` (`ask:449-T86-door`), so the Rust is the cache's one writer. An edit of a read here makes the same change in the Rust.
"""

from __future__ import annotations

import builtins
import contextlib
import datetime
import fcntl
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import time
import urllib.parse
from collections.abc import Iterator

HERE = pathlib.Path(__file__).resolve().parent
GATE = HERE.parent / "gates" / "l7r-gate.sh"
LEDGER = "sources-consulted.jsonl"
LOCK = "sources-consulted.lock"
CACHE = "page-cache"

#: THE AGE RULE. A cached page older than this is fetched again (REFRESH=1 fetches it at once). WHY SEVEN DAYS
#: (research.md R1, observed 2026-09-29): the saving is nearly all in the first day - 5,236 repeats came within an
#: hour of the read before and only 174 more than a day after - so a longer age buys almost nothing more, while
#: what an age COSTS is a page edited after it was saved (a Wikipedia sentence rewritten under a quote). A week
#: spans a feature's write-then-check cycle, so one feature never fetches a page twice, and bounds how stale a
#: verbatim check can be. Chosen by the session for feature 288; the brief asked for one stated age.
MAX_AGE_DAYS = 7

_URL = re.compile(r"https?://[^\s<\"']+")


def norm(u: str) -> str:
    """The normalization of feature 288's measurement, so the ledger's URLs and the
    measurement's are one set: scheme, `www.`, the mobile host, a fragment and a trailing slash dropped;
    percent-decoded; lower-cased, except a Wikipedia path, whose case is the article's name."""
    u = u.strip().strip("'\"<>),.;:")  # a colon too: prose after a URL in parentheses, "(https://...): 「...」" (feature 312)
    u = urllib.parse.unquote(u)
    u = u.split("#")[0]
    u = re.sub(r"^https?://", "", u)
    u = re.sub(r"^www\.", "", u)
    u = re.sub(r"^([a-z]{2,3})\.m\.wikipedia", r"\1.wikipedia", u)
    u = re.sub(r"^m\.", "", u)
    u = u.rstrip("/")
    if "wikipedia" not in u:
        return u.lower()
    return u[: u.find("/")].lower() + u[u.find("/") :] if "/" in u else u.lower()


def _blocked():  # noqa: ANN202 - the record's module, imported on first use so this file stays importable alone
    """`l7r/diagram/interactive/record/blocked.py` (feature 312 FR-001 - FR-003): the one decision on what no route may
    read or store - this ledger, this cache and every fetch through `CachedPages` ask it."""
    skill = str(HERE.parents[1])  # the repository root, where l7r/ is
    if skill not in sys.path:
        sys.path.insert(0, skill)
    from l7r.diagram.interactive.record import blocked  # noqa: PLC0415

    return blocked


def _attempts_mod():  # noqa: ANN202 - the attempts log (feature 312), which imports this module: imported on use
    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))
    import attempts  # noqa: PLC0415

    return attempts


def now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


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


@contextlib.contextmanager
def locked(where: pathlib.Path, timeout: float = 30.0) -> Iterator[None]:
    """`flock` on the ledger's lock file, polled so a hung holder is an error rather than a hang (as `make reserve`)."""
    where.mkdir(parents=True, exist_ok=True)
    fd = os.open(where / LOCK, os.O_RDWR | os.O_CREAT, 0o644)
    deadline = time.monotonic() + timeout
    try:
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise TimeoutError(f"could not take {where / LOCK} within {timeout:g}s") from None
                time.sleep(0.02)
        yield
    finally:
        os.close(fd)  # closing the descriptor releases the lock


def read(where: pathlib.Path) -> list[dict]:
    path = where / LEDGER
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines() if path.is_file() else []:
        with contextlib.suppress(json.JSONDecodeError):
            rows.append(json.loads(line))
    return rows


def entry_dir(where: pathlib.Path, url: str) -> pathlib.Path:
    h = hashlib.sha256(norm(url).encode("utf-8")).hexdigest()
    return where / CACHE / h[:2] / h


def cached(where: pathlib.Path, url: str, max_age_days: float = MAX_AGE_DAYS, exact: bool = False) -> dict | None:
    """The cached page of `url`, or None: absent, older than the age, or - where `exact` - an imported copy whose
    text is the saved form and not the page as fetched (quote-verbatim compares characters)."""
    d = entry_dir(where, url)
    try:
        meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
        text = (d / "text.txt").read_text(encoding="utf-8")
    except (OSError, json.JSONDecodeError):
        return None
    age = datetime.datetime.now(datetime.timezone.utc) - datetime.datetime.fromisoformat(meta["fetched"])
    if age > datetime.timedelta(days=max_age_days) or (exact and not meta.get("exact", False)):
        return None
    files = sorted((p.name for p in d.glob("page*.txt")), key=lambda n: int(m.group(1)) if (m := re.search(r"\.p(\d+)\.txt$", n)) else 0)
    return {**meta, "text": text, "dir": d, "files": files}


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


def put(where: pathlib.Path, url: str, text: str, fetched: str | None = None, exact: bool = True, origin: str = "fetch") -> dict:
    """Store one page through the Rust, the cache's one writer (`l7r-gate record sources put`, feature 449 T145): its text,
    its saved form in parts, and `meta.json` last; the stored page as `cached` reads it. Run from this repository, so a URL is
    checked against its blocked list as before."""
    cmd = [str(GATE), "record", "sources", "put", "--home", os.path.abspath(where), "--url", url, "--origin", origin]
    cmd += ["--fetched", fetched] if fetched else []
    cmd += [] if exact else ["--inexact"]
    done = subprocess.run(cmd, input=text.encode("utf-8"), capture_output=True, cwd=HERE, check=False)
    if done.returncode:
        raise raised(done.stderr.decode("utf-8", "replace"))
    got = json.loads(done.stdout)
    d, files = pathlib.Path(got.pop("dir")), got.pop("files")
    return {**got, "text": text, "dir": d, "files": files}
