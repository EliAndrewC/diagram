#!/usr/bin/env python3
"""The source archive's Python door, until S3b and S4 port the Python that imports it (feature 449 T146, phase 4's S3a).

`archive.py` archived every source the record cites into the PRIVATE repository EliAndrewC/diagram-research (feature 309). Its
commands are `l7r-gate record archive url|backfill|report|gm-copies` now (`rust/gate/crates/archive/`), its browser the one
browser crate (`rust/browser/`, `l7r-browser`, `ask:449-phase4-slices` Q4: never Playwright), and every write it made has ONE writer,
the Rust (FR-003): the archive's working copy, its manifest rows, the backfill's lanes.

WHAT IS LEFT HERE is what the Python still importing it reaches - `uncited.py`, `uncited_imports.py` and `archive_ops.py` (S3b),
`research_search.py` and `semantic_index.py` (S4):
  - the READS, half-ported as `ask:449-T81-slices` lets them stay: the constants, `Fetched`, `lanes`, `row_path`, `row_files`,
    `capture_base`, `gm_table`, `home_of`, `mirror`, `token`, `git_env`, and `Archive`'s lock, its `git` and `unpushed`;
  - FORWARDERS to `l7r-gate record archive <verb>` (`ask:449-T86-door`): `Archive.ensure` and `Archive.push`, `place_gm`,
    `archive_url`, `_lane`, `settle`, `sync_gm_copies`, `write_row`; and `Browser`, `fetch` and `wayback`, through one
    `l7r-gate record archive serve` a `Browser`. A failed write raises the exception the Python raised, by the kind on the Rust's
    last line (`sources.raised`).
`Archive.ensure`, `Archive.push` and `place_gm` run while the caller holds `Archive.locked()`, so the Rust takes no lock for them.
An edit of a read here makes the same change in the Rust in the same commit (`ask:449-phase4-slices`).
"""

from __future__ import annotations

import base64
import contextlib
import dataclasses
import fcntl
import json
import multiprocessing  # noqa: F401 - the importers' pools reach it as `ar.multiprocessing`
import os
import pathlib
import subprocess
import sys
import tempfile
import time
import urllib.parse
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
UNPUSHED = "source-archive.unpushed"
GM_DIR = pathlib.Path(os.environ.get("L7R_GM_SOURCES", "/host-l7r-repo/academic-sources"))
GM_DEST = "gm-copies"
MANIFEST = pathlib.Path("research") / rec.ARCHIVE_DIR
#: A backfill lane starts a fresh browser this often (the Rust's `backfill::RECYCLE_EVERY`, whose comment says why).
RECYCLE_EVERY = 25


def _gate(args: list[str], *, stdin: str = "", env: dict[str, str] | None = None, capture: bool = True) -> str:
    """`l7r-gate record archive <args>`: its stdout; a refusal raises what the Python raised, by kind."""
    done = subprocess.run([str(GATE), "record", "archive", *args], input=stdin.encode("utf-8"), env=env, check=False,
                          stdout=subprocess.PIPE if capture else None, stderr=subprocess.PIPE)
    if done.returncode:
        raise src.raised(done.stderr.decode("utf-8", "replace"))
    return done.stdout.decode("utf-8") if capture else ""


# ---- one fetch -------------------------------------------------------------------------------------------------------


@dataclasses.dataclass
class Fetched:
    """What one fetch of a URL brought back. `error` is set where nothing usable came."""

    url: str
    status: int | None = None
    final_url: str = ""
    content_type: str = ""
    body: bytes = b""
    mhtml: str = ""
    text: str = ""
    error: str = ""

    @property
    def is_html(self) -> bool:
        return "html" in self.content_type


class Browser:
    """The one browser crate behind `l7r-gate record archive serve`: a request, a render, a whole fetch and a Wayback lookup, each
    spaced and retried by the Rust as the Playwright `Browser` was. Started on first use, so a caller that only hands it to
    `archive_url` (which starts its own) starts no browser."""

    def __init__(self) -> None:
        self._p: subprocess.Popen | None = None
        self._tmp = tempfile.TemporaryDirectory()

    def _ask(self, op: str, url: str) -> dict:
        if self._p is None:
            self._p = subprocess.Popen([str(GATE), "record", "archive", "serve", "--root", str(src.repo_root())],
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            ready = json.loads(self._p.stdout.readline() or '{"raise": "RuntimeError", "message": "the browser did not start"}')
            if "raise" in ready:
                raise src.raised(f"{ready['raise']}: {ready['message']}")
        out = os.path.join(self._tmp.name, "body")
        self._p.stdin.write(json.dumps({"op": op, "url": url, "out": out}) + "\n")
        self._p.stdin.flush()
        got = json.loads(self._p.stdout.readline() or '{"raise": "RuntimeError", "message": "the browser has closed"}')
        if "raise" in got:
            raise src.raised(f"{got['raise']}: {got['message']}")
        if "url" in got:
            got["body"] = pathlib.Path(out).read_bytes() if os.path.exists(out) else b""
            with contextlib.suppress(OSError):
                os.remove(out)
        return got

    def _fetched(self, op: str, url: str) -> Fetched:
        got = self._ask(op, url)
        return Fetched(got["url"], got["status"], got["final_url"], got["content_type"], got["body"], got["mhtml"], got["text"],
                       got["error"])

    def get(self, url: str) -> Fetched:
        return self._fetched("get", url)

    def render(self, url: str) -> tuple[str, str]:
        got = self._ask("render", url)
        return got["mhtml"], got["text"]

    def close(self) -> None:
        if self._p is not None:
            with contextlib.suppress(OSError, ValueError):
                self._p.stdin.write(json.dumps({"op": "close"}) + "\n")
                self._p.stdin.close()
            self._p.wait()
            self._p = None
        self._tmp.cleanup()


def fetch(browser: Browser, url: str) -> Fetched:
    """One URL's bytes, and for a web page its render (the Rust's `fetch`; a blocked URL raises `Blocked`)."""
    return browser._fetched("fetch", url)  # noqa: SLF001 - the forwarder's own browser


def wayback(browser: Browser, url: str) -> tuple[str, str] | None:
    """The newest snapshot the Wayback Machine holds of `url`: (its URL, its 14-digit time), or None."""
    snap = browser._ask("wayback", url)["snapshot"]  # noqa: SLF001 - the forwarder's own browser
    return (snap[0], snap[1]) if snap else None


# ---- the working copy ------------------------------------------------------------------------------------------------


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
    """The host's one working copy of the archive repository: its lock, its `git` and its counter read here, its writes the Rust's."""

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

    def unpushed(self) -> int:
        try:
            return int((self.home / UNPUSHED).read_text())
        except (OSError, ValueError):
            return 0

    def ensure(self) -> None:
        """Clone the repository once (call under the lock): the Rust's `ensure`."""
        _gate(["ensure", "--home", os.path.abspath(self.home), "--remote", self.remote], env=self.env)

    def push(self) -> str:
        """Push `main` (call under the lock): '' on success or with nothing committed yet, else git's complaint (the Rust's)."""
        return _gate(["push", "--home", os.path.abspath(self.home)], env=self.env).rstrip("\n")


# ---- the manifest ----------------------------------------------------------------------------------------------------


def row_path(root: pathlib.Path, url: str) -> pathlib.Path:
    """A URL's manifest row, sharded as the archive is: `research/archive/<id[:2]>/<id>.json`."""
    uid = rec.url_id(url)
    return root / MANIFEST / uid[:2] / f"{uid}.json"


def row_files(root: pathlib.Path) -> list[pathlib.Path]:
    return sorted((root / MANIFEST).glob(rec.ROW_GLOB))


def capture_base(url: str) -> str:
    """Where a URL's captures go in the archive: `<id[:2]>/<id>`."""
    uid = rec.url_id(url)
    return f"{uid[:2]}/{uid}"


def write_row(root: pathlib.Path, url: str, row: dict) -> None:
    """The row written whole (the Rust's `write_row`, the manifest's one writer)."""
    _gate(["write-row", "--root", os.path.abspath(root), "--url", url], stdin=json.dumps(row, ensure_ascii=False))


def gm_table(root: pathlib.Path) -> dict[str, dict]:
    """The GM's files, by name; no table, no files; a table that will not parse is an error, never an empty table."""
    path = root / MANIFEST / rec.GM_COPIES
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))["files"]


def place_gm(store: Archive, name: str, entry: dict) -> str:
    """The GM's file `name` in the archive (call under the lock): its archive path, or '' (the Rust's `place_gm`)."""
    return _gate(["place-gm", "--home", os.path.abspath(store.home), "--name", name], stdin=json.dumps(entry, ensure_ascii=False),
                 env=store.env).rstrip("\n")


def home_of(root: pathlib.Path) -> pathlib.Path:
    """Where the working copy and its lock live: beside the page cache, `_sources.home` (the tests' seam moves both)."""
    return src.home(root)


def archive_url(root: pathlib.Path, url: str, who: rec.Cited, browser: Browser, store: Archive, push: bool = True) -> dict:  # noqa: ARG001 - the Rust starts its own browser
    """Archive one cited URL, copy its keys' GM files, write its manifest row, and push when asked (the Rust's `archive_url`)."""
    args = ["url-row", "--root", os.path.abspath(root), "--home", os.path.abspath(store.home), "--url", url]
    out = _gate([*args, *([] if push else ["--no-push"])], stdin=json.dumps({"keys": who.keys, "notes": who.notes}), env=store.env)
    return json.loads(out)


def sync_gm_copies(root: pathlib.Path, store: Archive) -> int:
    """Every GM file `gm-copies.json` matches copied in and every row of its key told so (the Rust's); the rows changed."""
    return int(_gate(["sync-gm", "--root", os.path.abspath(root), "--home", os.path.abspath(store.home)], env=store.env))


# ---- the backfill ----------------------------------------------------------------------------------------------------


def lanes(urls: list[str], n: int) -> list[list[str]]:
    """`urls` dealt into `n` lanes, every URL of one host in one lane (plan D8: never two requests to a host at once)."""
    by_host: dict[str, list[str]] = {}
    for u in urls:
        by_host.setdefault(urllib.parse.urlparse(u).netloc, []).append(u)
    out: list[list[str]] = [[] for _ in range(max(1, n))]
    for host_urls in sorted(by_host.values(), key=len, reverse=True):
        min(out, key=len).extend(host_urls)
    return [lane for lane in out if lane]


def _lane(args: tuple[str, list[str], str]) -> list[dict]:
    """One lane of a pool (the Rust's `lane`): each URL archived unpushed, its outcome line printed as it goes; its rows."""
    root_s, urls, home_s = args
    with tempfile.TemporaryDirectory() as tmp:
        rows = os.path.join(tmp, "rows.jsonl")
        _gate(["lane", "--root", root_s, "--home", home_s, "--rows", rows], stdin="\n".join(urls),
              env=git_env(token(pathlib.Path(root_s))), capture=False)
        with open(rows, encoding="utf-8") as fh:
            return [json.loads(line) for line in fh]


def settle(root: pathlib.Path) -> int:
    """Rows waiting on an upload, once a push has gone through, get their real outcome back (the Rust's)."""
    return int(_gate(["settle", "--root", os.path.abspath(root)]))

