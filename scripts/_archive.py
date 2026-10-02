#!/usr/bin/env python3
"""Archive every source the record cites into the private repository EliAndrewC/diagram-research (feature 309).

WHY (the GM, 2026-10-02, `specs/309-source-archive/request.md`): a hedge against *"websites going offline, failing to be
maintained"* or *"changing URLs in a website redesign"* - *"backup copies of all of the content we are referencing"*, every
web page and every PDF, *"even things which seem at low risk of going away, like wikipedia pages"*, and for a web page
*"the whole webpage with images and css and such and not just the html content"*. The repository is PRIVATE on purpose:
much of it is copyrighted, and *"for now I just want an archive"*.

WHAT A CAPTURE HOLDS (spec FR-002), in `<id[:2]>/<id>/<UTC time>/` of the archive - sharded by the URL id's first two hex
digits, so no directory holds more than a few hundred entries (GitHub lists only the first 1,000 of a directory; the GM
asked for the layout to stay browsable as the archive grows past 5,000 URLs, 2026-10-02) - with who cites it in `capture.json`:
  served.<ext>  the bytes the site served, unaltered (an HTML document, a PDF, an image)
  page.mhtml    a web page whole, as Chromium rendered it - its text, images, stylesheets and fonts - in one file that any
                Chromium browser opens offline (plan D1: SingleFile fails on this host's Node, monolith runs no scripts)
  text.txt      its readable text
  capture.json  the URL cited and the URL fetched, the time, the status, the type, the SHA-256, the keys and notes that
                cite it, and a MediaWiki page's revision (plan D7)
A file past `PART` bytes is written in parts with the whole file's SHA-256 beside them (GitHub refuses one past 100 MB).

THE ORDER (plan D2): the live fetch first. A DEAD page (gone, failing, answered by the front page) then takes the newest
Wayback snapshot, then the GM's downloaded copy, else it is `unreachable` with the page cache's text kept; a REFUSED page
(a bot wall, or a page that rendered no text) takes the GM's copy first, then a snapshot, else it is `partial` - what the
site served, the page cache's text beside it (`capture`). And
IN ADDITION, every file of `/host-l7r-repo/academic-sources/` that `research/archive/gm-copies.json` matches to a key is
copied to `gm-copies/<file>` (FR-012), whatever the live fetch did.

ONE WORKING COPY on the host (the GM: *"you can just push directly to it without each of our diagram .clones/ having its
own copy"*): `<mirror>/.specify/source-archive/`, written under `<mirror>/.specify/source-archive.lock`, pushed straight to
GitHub. The PAT reaches git as `GIT_CONFIG_*` environment entries, never on a command line, in a file or in a log (FR-011).

THE MANIFEST, one row per cited URL in this repository (`research/archive/<id>.json`), is what the record build reads
(`l7r/diagram/interactive/record/archive.py`, which also says what is cited - this script asks it, so they agree).

    _archive.py url <u> [--key K]          archive one URL now (`make archive URL=`; `make reserve ... URL=` calls it)
    _archive.py backfill [--workers N]     archive every cited URL with no row, resumably (`make archive-sources`)
    _archive.py report                     the coverage table, fetching nothing (`make archive-sources REPORT=1`)
    _archive.py gm-copies                  the GM's matched files copied in, their rows told (`make archive-sources GM=1`)
"""

from __future__ import annotations

import argparse
import base64
import contextlib
import dataclasses
import datetime
import fcntl
import hashlib
import html
import json
import mimetypes
import multiprocessing
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.parse
from collections.abc import Iterator

HERE = pathlib.Path(__file__).resolve().parent
SKILL = HERE.parent / ".claude" / "skills" / "diagram"
for _p in (str(HERE), str(SKILL)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import _sources as src  # noqa: E402

from l7r.diagram.interactive.record import archive as rec  # noqa: E402
from l7r.diagram.interactive.record import blocked  # noqa: E402

REMOTE = rec.REPO + ".git"
WORKDIR = "source-archive"
LOCK = "source-archive.lock"
UNPUSHED = "source-archive.unpushed"
GM_DIR = pathlib.Path(
    os.environ.get("L7R_GM_SOURCES", "/host-l7r-repo/academic-sources")
)
MANIFEST = pathlib.Path(".claude/skills/diagram/research") / rec.ARCHIVE_DIR
#: A file past this is stored in parts: GitHub refuses a file past 100 MB, and 95 leaves room.
PART = 95 * 2**20
#: The backfill pushes once this much is committed and unpushed (plan D9: far under GitHub's 2 GB push limit, and a
#: stopped run loses at most one batch's push - the captures stay in the working copy for the next run).
PUSH_EVERY = 200 * 2**20
#: A backfill lane starts a fresh browser this often, so a lane's memory stays bounded: the containers share a 10 GB cap,
#: and two lanes' browsers had grown to 1.8 GB (one renderer 0.7 GB) partway through the first backfill (observed
#: 2026-10-02 at the host's low-memory warning).
RECYCLE_EVERY = 25
#: Politeness (plan D8): one request at a time per host, this long between them; a 429 or 503 waits RETRY_WAIT once.
HOST_GAP_S = 1.0
RETRY_WAIT_S = 30.0
#: The page cache's text is a fallback copy at any age - an old copy of a dead page beats none (a timedelta, so finite).
CACHE_ANY_AGE_DAYS = 365 * 100
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
WAYBACK = "https://archive.org/wayback/available?url="
_REVISION = re.compile(rb'"wgRevisionId"\s*:\s*(\d+)')
_SNAPSHOT_TS = re.compile(r"^(https?://web\.archive\.org/web/)(\d{14})/")


# ---- one fetch ---------------------------------------------------------------------------------------------------


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


def ext_of(content_type: str, url: str) -> str:
    """The served file's extension, from its type and then its URL."""
    kind = content_type.split(";")[0].strip().lower()
    if "html" in kind:
        return ".html"
    guessed = mimetypes.guess_extension(kind) if kind else None
    if guessed:
        return {".jpe": ".jpg", ".htm": ".html"}.get(guessed, guessed)
    suffix = pathlib.PurePosixPath(urllib.parse.urlparse(url).path).suffix.lower()
    return suffix if re.fullmatch(r"\.[a-z0-9]{1,5}", suffix) else ".bin"


def pdf_text(body: bytes) -> str:
    """A PDF's text, by `pdftotext` (poppler); empty where it has none or the tool fails."""
    with tempfile.TemporaryDirectory() as tmp:
        path = pathlib.Path(tmp) / "f.pdf"
        path.write_bytes(body)
        done = subprocess.run(
            ["pdftotext", "-layout", str(path), "-"], capture_output=True, check=False
        )
    return done.stdout.decode("utf-8", "replace") if done.returncode == 0 else ""


_TAGS = re.compile(r"<(script|style|noscript)\b.*?</\1>|<[^>]+>", re.S | re.I)


def served_text(body: bytes) -> str:
    """A served HTML document's text without a browser - the text of a page that would not render whole."""
    return re.sub(
        r"\s+\n",
        "\n",
        re.sub(
            r"[ \t]+",
            " ",
            html.unescape(_TAGS.sub(" ", body.decode("utf-8", "replace"))),
        ),
    ).strip()


def revision(body: bytes) -> str:
    """A MediaWiki page's revision id, from its page config (plan D7); empty for any other page."""
    m = _REVISION.search(body)
    return m.group(1).decode() if m else ""


#: The statuses that mean the site is THERE but refuses an automated reader (a bot wall, a login, a rate limit), as
#: against gone: a refused page takes the GM's downloaded copy before a Wayback snapshot, a dead one the reverse (plan D2).
REFUSING = (401, 403, 406, 429, 451)


def failure(cited: str, got: Fetched) -> tuple[str, str]:
    """('', '') where a live fetch brought the page back; else ('dead' | 'refused', why) (plan D10). Dead: a network
    error, a missing page or a server failure, an empty body, or a redirect from a deeper path to the site's root (a moved
    page answered by its front page). Refused: a `REFUSING` status, or a web page that rendered no text."""
    if got.error:
        return "dead", got.error
    if got.status in REFUSING:
        return "refused", f"HTTP {got.status}"
    if got.status is None or got.status >= 400:
        return "dead", f"HTTP {got.status}"
    if not got.body:
        return "dead", "an empty response"
    deep = urllib.parse.urlparse(cited).path.strip("/")
    landed = urllib.parse.urlparse(got.final_url or cited).path.strip("/")
    if deep and not landed:
        return "dead", f"redirected to the site's front page ({got.final_url})"
    if got.is_html and not got.text.strip():
        return "refused", "the page showed no text"
    return "", ""


def snapshot_raw(url: str) -> str:
    """A Wayback snapshot's URL for the bytes as archived (`id_`), without the archive's toolbar."""
    return _SNAPSHOT_TS.sub(lambda m: f"{m.group(1)}{m.group(2)}id_/", url, count=1)


class Browser:
    """Fetches through Playwright's Chromium: the bytes with a request, then - for a web page - the page rendered, its
    MHTML snapshot and its visible text. One per process; `get` and `render` are the seams a test replaces."""

    def __init__(self) -> None:
        from playwright.sync_api import sync_playwright  # noqa: PLC0415 - only a real run needs a browser

        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch()
        self._ctx = self._browser.new_context(user_agent=UA, ignore_https_errors=True)
        self._last: dict[str, float] = {}

    def close(self) -> None:
        self._browser.close()
        self._pw.stop()

    def _wait(self, url: str) -> None:
        host = urllib.parse.urlparse(url).netloc
        gap = HOST_GAP_S - (time.monotonic() - self._last.get(host, 0.0))
        if gap > 0:
            time.sleep(gap)
        self._last[host] = time.monotonic()

    def get(self, url: str) -> Fetched:
        for attempt in (1, 2):
            self._wait(url)
            try:
                r = self._ctx.request.get(
                    url,
                    timeout=60_000,
                    headers={
                        "Accept": "*/*",
                        "Accept-Language": "en,ja;q=0.8,zh;q=0.6",
                    },
                    max_redirects=10,
                )
            except Exception as e:  # noqa: BLE001 - every failure of the transport is an outcome, recorded with its reason
                return Fetched(url, error=str(e).splitlines()[0][:200])
            if r.status in (429, 503) and attempt == 1:
                time.sleep(RETRY_WAIT_S)
                continue
            return Fetched(
                url, r.status, r.url, r.headers.get("content-type", ""), r.body()
            )
        raise AssertionError(
            "unreachable"
        )  # pragma: no cover - the loop returns on its second pass

    def render(self, url: str) -> tuple[str, str]:
        """The page's MHTML and visible text, as Chromium shows it; ('', '') where it will not render. Tried twice: in
        the first backfill 5 of ~1,150 pages failed to render under load and rendered at once when tried again (observed
        2026-10-02, method: the failed URLs rendered alone by the same Browser)."""
        for _attempt in (1, 2):
            self._wait(url)
            page = self._ctx.new_page()
            try:
                page.goto(url, wait_until="load", timeout=60_000)
                with contextlib.suppress(Exception):
                    page.wait_for_load_state("networkidle", timeout=10_000)
                mhtml = page.context.new_cdp_session(page).send(
                    "Page.captureSnapshot", {"format": "mhtml"}
                )["data"]
                return mhtml, page.inner_text("body")
            except Exception:  # noqa: BLE001, S112 - a page that will not render keeps its served bytes; the outcome says so
                continue
            finally:
                page.close()
        return "", ""


def fetch(browser, url: str) -> Fetched:  # noqa: ANN001 - a Browser, or a test's stand-in with get and render
    """One URL's bytes, and for a web page its render; a PDF's text from the PDF, a text file's from itself. A URL on a
    blocked domain is refused before any request (feature 312 FR-002)."""
    blocked.check(url, "an archive fetch")
    got = browser.get(url)
    if got.error or got.status is None or got.status >= 400:
        return got
    if got.is_html:
        got.mhtml, got.text = browser.render(got.final_url or url)
        if not got.mhtml:
            got.text = served_text(got.body)
    elif "pdf" in got.content_type or got.body[:5] == b"%PDF-":
        got.text = pdf_text(got.body)
    elif got.content_type.startswith("text/"):
        got.text = got.body.decode("utf-8", "replace")
    return got


def wayback(browser, url: str) -> tuple[str, str] | None:  # noqa: ANN001
    """The newest snapshot the Wayback Machine holds of `url`: (its URL, its 14-digit time), or None."""
    got = browser.get(WAYBACK + urllib.parse.quote(url, safe=""))
    if got.error or got.status != 200:
        return None
    try:
        closest = (
            json.loads(got.body.decode("utf-8"))
            .get("archived_snapshots", {})
            .get("closest", {})
        )
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    if not closest.get("available") or not closest.get("url"):
        return None
    return closest["url"].replace("http://", "https://", 1), closest.get(
        "timestamp", ""
    )


# ---- one capture -------------------------------------------------------------------------------------------------


@dataclasses.dataclass
class Capture:
    """One URL's outcome and the files that go in the archive for it."""

    outcome: str
    files: dict[str, bytes]
    record: dict
    reason: str = ""


def files_of(got: Fetched) -> dict[str, bytes]:
    out = {"served" + ext_of(got.content_type, got.final_url or got.url): got.body}
    if got.mhtml:
        out["page.mhtml"] = got.mhtml.encode("utf-8")
    if got.text:
        out["text.txt"] = got.text.encode("utf-8")
    return out


def record_of(url: str, got: Fetched, origin: str) -> dict:
    return {
        "url": url,
        "fetched_url": got.url,
        "final_url": got.final_url or got.url,
        "status": got.status,
        "content_type": got.content_type,
        "sha256": hashlib.sha256(got.body).hexdigest(),
        "bytes": len(got.body),
        "revision": revision(got.body) if got.is_html else "",
        "origin": origin,
        "whole_page": bool(got.mhtml),
    }


def from_snapshot(browser, url: str, reason: str) -> Capture | None:  # noqa: ANN001
    """The newest Wayback snapshot of `url` captured, or None where there is none or it will not fetch."""
    snap = wayback(browser, url)
    if snap is None:
        return None
    old = fetch(browser, snapshot_raw(snap[0]))
    if failure(snap[0], old)[0] == "dead":
        return None
    if old.is_html:
        old.mhtml, shown = browser.render(snap[0])
        old.text = shown or old.text
    return Capture(
        "archived-earlier-snapshot",
        files_of(old),
        {**record_of(url, old, f"wayback {snap[1]}"), "live_failure": reason},
        reason,
    )


def capture(browser, url: str, has_gm_copy: bool, cache_text: str = "") -> Capture:  # noqa: ANN001
    """One cited URL captured in the order of plan D2: the live fetch first. A DEAD page then takes a Wayback snapshot,
    then the GM's copy, else it is `unreachable` (the page cache's text kept where the cache holds it - spec US1
    scenario 3). A REFUSED page (a bot wall, or a page that rendered no text) takes the GM's copy first, then a snapshot,
    else it is `partial`: what the site served, with the page cache's text beside it (the spec's Edge Cases)."""
    live = fetch(browser, url)
    kind, reason = failure(url, live)
    if not kind and live.is_html and not live.mhtml:
        return Capture(
            "partial",
            files_of(live),
            record_of(url, live, "live"),
            "the page would not render whole: its served HTML and text are kept",
        )
    if not kind:
        return Capture("archived", files_of(live), record_of(url, live, "live"))
    served = files_of(live) if live.body else {}
    cached = {"page-cache-text.txt": cache_text.encode("utf-8")} if cache_text else {}
    base = (
        {**record_of(url, live, "live"), "live_failure": reason}
        if live.body
        else {"url": url, "live_failure": reason}
    )
    gm = (
        Capture(
            "archived-gm-copy",
            served,
            {**base, "origin": "the GM's downloaded copy"},
            reason,
        )
        if has_gm_copy
        else None
    )
    if kind == "refused":
        found = gm or from_snapshot(browser, url, reason)
        return found or Capture("partial", {**served, **cached}, base, reason)
    found = from_snapshot(browser, url, reason) or gm
    return found or Capture("unreachable", cached, base, reason)


def split_large(
    files: dict[str, bytes], part: int = PART
) -> tuple[dict[str, bytes], dict[str, dict]]:
    """Files past `part` bytes cut into `<name>.partN`, with each whole file's SHA-256 and part count to join it by."""
    out: dict[str, bytes] = {}
    parts: dict[str, dict] = {}
    for name, body in files.items():
        if len(body) <= part:
            out[name] = body
            continue
        pieces = [body[i : i + part] for i in range(0, len(body), part)]
        for n, piece in enumerate(pieces, 1):
            out[f"{name}.part{n}"] = piece
        parts[name] = {
            "parts": len(pieces),
            "sha256": hashlib.sha256(body).hexdigest(),
            "bytes": len(body),
        }
    return out, parts


# ---- the working copy --------------------------------------------------------------------------------------------


def mirror(root: pathlib.Path) -> pathlib.Path:
    """The mirror: a clone's grandparent under `.clones/`, else the repository itself."""
    return root.parent.parent if root.parent.name == ".clones" else root


def git_env(token: str) -> dict[str, str]:
    """The environment that authenticates git to GitHub with the PAT as an extra header (FR-011)."""
    basic = base64.b64encode(f"x-access-token:{token}".encode()).decode()
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_CONFIG_")}
    env.update(
        {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "http.https://github.com/.extraheader",
            "GIT_CONFIG_VALUE_0": f"AUTHORIZATION: basic {basic}",
            "GIT_TERMINAL_PROMPT": "0",
        }
    )
    return env


def token(root: pathlib.Path) -> str:
    from l7r.diagram.ci.config import load_secrets  # noqa: PLC0415 - only a push needs the secrets

    return load_secrets(mirror(root)).github_pat


class Archive:
    """The host's one working copy of the archive repository, written and pushed under the host-wide lock."""

    def __init__(
        self,
        home: pathlib.Path,
        remote: str = REMOTE,
        env: dict[str, str] | None = None,
    ) -> None:
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
                        raise TimeoutError(
                            f"could not take {self.home / LOCK} within {timeout:g}s"
                        ) from None
                    time.sleep(0.05)
            yield
        finally:
            os.close(fd)

    def git(self, *args: str, check: bool = True) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["git", "-C", str(self.dir), *args],
            env=self.env,
            capture_output=True,
            text=True,
            check=check,
        )

    def ensure(self) -> None:
        """Clone the repository once; an empty one is initialized on `main` with its remote."""
        if (self.dir / ".git").is_dir():
            return
        self.dir.parent.mkdir(parents=True, exist_ok=True)
        done = subprocess.run(
            ["git", "clone", "-q", self.remote, str(self.dir)],
            env=self.env,
            capture_output=True,
            text=True,
            check=False,
        )
        if done.returncode != 0:
            raise RuntimeError(
                f"could not clone the archive: {done.stderr.strip()[:300]}"
            )
        if self.git("rev-parse", "--verify", "-q", "HEAD", check=False).returncode != 0:
            self.git("checkout", "-q", "-b", "main")
        self.git("config", "user.name", "diagram source archive")
        self.git("config", "user.email", "noreply@anthropic.com")

    def unpushed(self) -> int:
        try:
            return int((self.home / UNPUSHED).read_text())
        except (OSError, ValueError):
            return 0

    def _count(self, n: int) -> None:
        (self.home / UNPUSHED).write_text(str(n))

    def put(self, rel: str, files: dict[str, bytes], message: str) -> str:
        """Write `files` under `rel` and commit them (call under the lock); returns the directory used - `rel`, or
        `rel-2`, `rel-3` ... where a capture in the same second already holds it (FR-009: never over an earlier one)."""
        used, n = rel, 1
        while (self.dir / used).exists():
            n += 1
            used = f"{rel}-{n}"
        d = self.dir / used
        d.mkdir(parents=True)
        for name, body in files.items():
            (d / name).write_bytes(body)
        self.git("add", "--", used)
        self.git("commit", "-q", "-m", message)
        self._count(self.unpushed() + sum(len(b) for b in files.values()))
        return used

    def copy_in(self, rel: str, source: pathlib.Path) -> bool:
        """Copy the GM's file or folder to `rel` once (call under the lock); False where it is already there."""
        dest = self.dir / rel
        if dest.exists():
            return False
        dest.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, dest)
        else:
            shutil.copy2(source, dest)
        self.git("add", "--", rel)
        self.git("commit", "-q", "-m", f"the GM's downloaded copy: {rel}")
        self._count(
            self.unpushed()
            + sum(
                p.stat().st_size
                for p in ([dest] if dest.is_file() else dest.rglob("*"))
                if p.is_file()
            )
        )
        return True

    def put_file(self, rel: str, body: bytes, message: str) -> None:
        """Write and commit one file at `rel` (call under the lock), where nothing is yet."""
        if (self.dir / rel).exists():
            return
        (self.dir / rel).parent.mkdir(parents=True, exist_ok=True)
        (self.dir / rel).write_bytes(body)
        self.git("add", "--", rel)
        self.git("commit", "-q", "-m", message)
        self._count(self.unpushed() + len(body))

    def push(self) -> str:
        """Push `main` (call under the lock); '' on success or with nothing committed yet, else git's complaint."""
        if self.git("rev-parse", "--verify", "-q", "HEAD", check=False).returncode != 0:
            return ""
        done = self.git("push", "-q", "origin", "HEAD:main", check=False)
        if done.returncode != 0:
            return done.stderr.strip()[:300] or f"git push exited {done.returncode}"
        self._count(0)
        return ""


# ---- the manifest ------------------------------------------------------------------------------------------------


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


def read_row(root: pathlib.Path, url: str) -> dict | None:
    try:
        return json.loads(row_path(root, url).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def write_row(root: pathlib.Path, url: str, row: dict) -> None:
    path = row_path(root, url)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(
        json.dumps(row, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(tmp, path)


def gm_table(root: pathlib.Path) -> dict[str, dict]:
    """The GM's files, by name: each one's keys and, once copied, where it is in the archive (`archived`). No table, no
    files; a table that will not parse is an error, never an empty table - the first backfill ran on a malformed one and
    copied none of the GM's files while every row looked normal (2026-10-02)."""
    path = root / MANIFEST / rec.GM_COPIES
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))["files"]


def gm_copies(root: pathlib.Path) -> dict[str, list[str]]:
    """key -> the GM's files that copy it (FR-012), from `research/archive/gm-copies.json`."""
    out: dict[str, list[str]] = {}
    for name, entry in sorted(gm_table(root).items()):
        for key in entry.get("keys", []):
            out.setdefault(key, []).append(name)
    return out


GM_DEST = "gm-copies"


def place_gm(store: Archive, name: str, entry: dict) -> str:
    """The GM's file `name` in the archive (call under the lock): copied from the inbox to `gm-copies/<name>` once, its
    text beside a PDF as `<name>.txt` so `make archive-find` reads it; returns its archive path, or '' where it is
    neither in the archive nor in the inbox. A file the table already places (`archived`) is looked for there."""
    dest = entry.get("archived") or f"{GM_DEST}/{name}"
    source = GM_DIR / name
    if not (store.dir / dest).exists() and source.exists():
        store.copy_in(dest, source)
        if (
            source.is_file()
            and source.suffix.lower() == ".pdf"
            and (text := pdf_text(source.read_bytes()))
        ):
            store.put_file(f"{dest}.txt", text.encode("utf-8"), f"the text of {dest}")
    return dest if (store.dir / dest).exists() else ""


def stamp() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def home_of(root: pathlib.Path) -> pathlib.Path:
    """Where the working copy and its lock live: beside the page cache, `_sources.home` (the tests' seam moves both)."""
    return src.home(root)


def archive_url(
    root: pathlib.Path,
    url: str,
    who: rec.Cited,
    browser,
    store: Archive,
    push: bool = True,
) -> dict:  # noqa: ANN001
    """Archive one cited URL, copy its keys' GM files, write its manifest row, and push when asked. Returns the row."""
    url = rec.clean(url)
    blocked.check(url, "the archive")
    copies, table = gm_copies(root), gm_table(root)
    mine = sorted({n for k in who.keys for n in copies.get(k, [])})
    cache = src.cached(src.home(root), url, max_age_days=CACHE_ANY_AGE_DAYS)
    got = capture(browser, url, bool(mine), cache["text"] if cache else "")
    files, parts = split_large(got.files)
    when = stamp()
    rel = f"{capture_base(url)}/{when}"
    record = {
        **got.record,
        "captured": when,
        "keys": who.keys,
        "notes": who.notes,
        "outcome": got.outcome,
        "parts": parts,
    }
    gm_paths = []
    with store.locked():
        store.ensure()
        if files:
            rel = store.put(
                rel,
                {
                    **files,
                    "capture.json": (
                        json.dumps(record, ensure_ascii=False, indent=1) + "\n"
                    ).encode(),
                },
                f"{got.outcome}: {url}",
            )
        gm_paths = [p for name in mine if (p := place_gm(store, name, table[name]))]
        failure = store.push() if push else ""
    old = read_row(root, url) or {}
    row = {
        "url": url,
        "keys": who.keys,
        "notes": who.notes,
        "outcome": got.outcome,
        "path": rel if files else old.get("path", ""),
        "first": old.get("first") or (rel if files else ""),
        "captured": datetime.datetime.now(datetime.timezone.utc).isoformat(
            timespec="seconds"
        ),
        "sha256": got.record.get("sha256", ""),
        "revision": got.record.get("revision", ""),
        "final_url": got.record.get("final_url", ""),
        "reason": got.reason,
        "gm_copies": sorted(set(gm_paths) | set(old.get("gm_copies", []))),
    }
    if failure:
        row["held"], row["outcome"], row["reason"] = (
            row["outcome"],
            "pending-upload",
            f"push failed: {failure}",
        )
    write_row(root, url, row)
    return row


def sync_gm_copies(root: pathlib.Path, store: Archive) -> int:
    """Every GM file `gm-copies.json` matches copied into the archive, and every row of its key told so - without fetching
    anything (FR-012). A row the live fetch left `partial` or `unreachable` becomes `archived-gm-copy` (plan D2: the GM's
    copy stands in where the live page failed). Returns the rows changed."""
    copies, table = gm_copies(root), gm_table(root)
    rows = {p: json.loads(p.read_text(encoding="utf-8")) for p in row_files(root)}
    changed = 0
    with store.locked():
        store.ensure()
        for key, names in copies.items():
            paths = [p for name in names if (p := place_gm(store, name, table[name]))]
            for row in rows.values():
                if key not in row.get("keys", []) or not paths:
                    continue
                before = dict(row)
                row["gm_copies"] = sorted(set(row.get("gm_copies", [])) | set(paths))
                if row["outcome"] in ("partial", "unreachable"):
                    row["outcome"] = "archived-gm-copy"
                if row != before:
                    write_row(root, row["url"], row)
                    changed += 1
        failure = store.push()
    if failure:
        raise RuntimeError(
            f"the GM's copies are committed but the push failed: {failure}"
        )
    return changed


def owed(root: pathlib.Path) -> dict[str, rec.Cited]:
    """Every cited URL with no row, or a row still waiting on its upload."""
    rows = rec.load(str(root / ".claude/skills/diagram/research"))
    return {
        u: w
        for u, w in rec.cited(str(root / ".claude/skills/diagram/research")).items()
        if rows.get(rec.url_id(u), {}).get("outcome") in (None, "pending-upload")
    }


# ---- the backfill ------------------------------------------------------------------------------------------------


def lanes(urls: list[str], n: int) -> list[list[str]]:
    """`urls` dealt into `n` lanes, every URL of one host in one lane (plan D8: never two requests to a host at once)."""
    by_host: dict[str, list[str]] = {}
    for u in urls:
        by_host.setdefault(urllib.parse.urlparse(u).netloc, []).append(u)
    out: list[list[str]] = [[] for _ in range(max(1, n))]
    for host_urls in sorted(by_host.values(), key=len, reverse=True):
        min(out, key=len).extend(host_urls)
    return [lane for lane in out if lane]


def _lane(
    args: tuple[str, list[str], str],
) -> list[
    dict
]:  # pragma: no cover - one worker process with a live browser; its parts are tested
    root_s, urls, home_s = args
    root = pathlib.Path(root_s)
    store = Archive(pathlib.Path(home_s), env=git_env(token(root)))
    who = rec.cited(str(root / ".claude/skills/diagram/research"))
    browser = Browser()
    out = []
    try:
        for n, url in enumerate(urls, 1):
            if (
                n % RECYCLE_EVERY == 0
            ):  # a long-lived browser grows: two lanes held 1.8 GB after ~600 pages (2026-10-02)
                browser.close()
                browser = Browser()
            row = archive_url(
                root, url, who.get(url, rec.Cited()), browser, store, push=False
            )
            out.append(row)
            print(f"{row['outcome']:26} {url}", flush=True)
            if store.unpushed() >= PUSH_EVERY:
                with store.locked():
                    if store.unpushed() >= PUSH_EVERY and (failure := store.push()):
                        print(f"push failed: {failure}", flush=True)
    finally:
        browser.close()
    return out


def backfill(
    root: pathlib.Path, workers: int
) -> (
    int
):  # pragma: no cover - the live run; `lanes`, `archive_url` and `report` are tested
    todo = owed(root)
    print(
        f"archive: {len(todo)} cited URL(s) owed a copy, in up to {workers} lane(s)",
        flush=True,
    )
    home = home_of(root)
    store = Archive(home, env=git_env(token(root)))
    with store.locked():
        store.ensure()
    jobs = [(str(root), lane, str(home)) for lane in lanes(sorted(todo), workers)]
    with multiprocessing.get_context("spawn").Pool(len(jobs) or 1) as pool:
        for _ in pool.imap_unordered(_lane, jobs):
            pass
    with store.locked():
        failure = store.push()
    if failure:
        print(
            f"archive: the final push failed - {failure}; the captures wait in {store.dir}",
            file=sys.stderr,
        )
        return 1
    settle(root)
    return report(root)


def settle(root: pathlib.Path) -> int:
    """Rows waiting on an upload, once a push has gone through, get their real outcome back."""
    n = 0
    for path in row_files(root):
        row = json.loads(path.read_text(encoding="utf-8"))
        if row.get("outcome") == "pending-upload" and row.get("held"):
            row["outcome"], row["reason"] = row.pop("held"), ""
            write_row(root, row["url"], row)
            n += 1
    return n


def report(root: pathlib.Path, out=sys.stdout) -> int:  # noqa: ANN001
    """The coverage table (spec FR-004): counts per outcome, every URL with none, and every unreachable one's reason."""
    research = str(root / ".claude/skills/diagram/research")
    rows = rec.load(research)
    counts: dict[str, int] = {}
    missing, failed = [], []
    for url in rec.cited(research):
        row = rows.get(rec.url_id(url))
        outcome = row["outcome"] if row else "(none)"
        counts[outcome] = counts.get(outcome, 0) + 1
        if row is None:
            missing.append(url)
        elif outcome in ("unreachable", "partial"):
            failed.append(f"{outcome:11} {url} - {row.get('reason', '')}")
    total = sum(counts.values())
    print(f"archive coverage: {total} cited URL(s)", file=out)
    for outcome in (*rec.OUTCOMES, "(none)"):
        if counts.get(outcome):
            print(f"  {outcome:26} {counts[outcome]:5}", file=out)
    for line in failed:
        print(f"  {line}", file=out)
    for url in missing[:50]:
        print(f"  no row: {url}", file=out)
    return 1 if missing else 0


def main(
    argv: list[str] | None = None,
) -> int:  # pragma: no cover - argument plumbing over the tested functions
    ap = argparse.ArgumentParser(
        description="archive the record's cited sources (feature 309)"
    )
    sub = ap.add_subparsers(dest="cmd", required=True)
    one = sub.add_parser("url")
    one.add_argument("url")
    one.add_argument("--key", default="")
    back = sub.add_parser("backfill")
    back.add_argument("--workers", type=int, default=4)
    sub.add_parser("report")
    sub.add_parser("gm-copies")
    args = ap.parse_args(argv)
    root = src.repo_root()
    if args.cmd == "report":
        return report(root)
    if args.cmd == "gm-copies":
        print(
            f"archive: {sync_gm_copies(root, Archive(home_of(root), env=git_env(token(root))))} row(s) given the GM's copies"
        )
        return 0
    if args.cmd == "backfill":
        return backfill(root, args.workers)
    return archive_one(root, args.url, args.key)


def archive_one(
    root: pathlib.Path, url: str, key: str = ""
) -> int:  # pragma: no cover - the live path `make archive` and `make reserve` take
    """Archive one URL now, as the census sees it (a KEY names a registry entry not yet written)."""
    who = rec.cited(str(root / ".claude/skills/diagram/research")).get(
        rec.clean(url), rec.Cited()
    )
    if key and key not in who.keys:
        who.keys.insert(0, key)
    browser = Browser()
    try:
        row = archive_url(
            root, url, who, browser, Archive(home_of(root), env=git_env(token(root)))
        )
    finally:
        browser.close()
    src._attempts_mod().add(root, url, "unknown", f"archived{' for ' + key if key else ''} (make archive)", route="archive", key=key)
    print(
        f"archive: {row['outcome']} - {url}"
        + (f" ({row['reason']})" if row["reason"] else "")
        + (f"\n  {rec.copy_link(row)}" if row["path"] else "")
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
