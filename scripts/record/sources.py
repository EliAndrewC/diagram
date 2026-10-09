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
`page.p1.txt` ...). Every script that fetches a source page reads it through `CachedPages`, so a page is fetched once.

NO GUARD (R1: the saving is too small for a refusal): the tooling prints what is known where it matters.
"""

from __future__ import annotations

import argparse
import contextlib
import datetime
import fcntl
import hashlib
import html
import importlib.util
import json
import os
import pathlib
import re
import sys
import time
import urllib.parse
from collections.abc import Iterator

HERE = pathlib.Path(__file__).resolve().parent
LEDGER = "sources-consulted.jsonl"
LOCK = "sources-consulted.lock"
CACHE = "page-cache"
REGISTRY = pathlib.Path("research/sources/010-works-cited")

#: THE AGE RULE. A cached page older than this is fetched again (REFRESH=1 fetches it at once). WHY SEVEN DAYS
#: (research.md R1, observed 2026-09-29): the saving is nearly all in the first day - 5,236 repeats came within an
#: hour of the read before and only 174 more than a day after - so a longer age buys almost nothing more, while
#: what an age COSTS is a page edited after it was saved (a Wikipedia sentence rewritten under a quote). A week
#: spans a feature's write-then-check cycle, so one feature never fetches a page twice, and bounds how stale a
#: verbatim check can be. Chosen by the session for feature 288; the brief asked for one stated age.
MAX_AGE_DAYS = 7

OUTCOMES = "cited:<registry key> | rejected:<why> | nothing-found | unreadable | pending"
_OUTCOME = re.compile(r"cited:[a-z0-9][a-z0-9-]*|rejected:\s*\S.*|nothing-found|unreadable|pending")
_URL = re.compile(r"https?://[^\s<\"']+")


def norm(u: str) -> str:
    """The measurement's normalization (`specs/288-*/measurement/extract_norm.py`), so the ledger's URLs and the
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


def context(root: pathlib.Path) -> dict:
    """The feature, clone and session a ledger line is written under."""
    feature = os.environ.get("SPECIFY_FEATURE", "")
    pointer = root / ".specify" / "feature.json"
    if not feature and pointer.is_file():
        with contextlib.suppress(json.JSONDecodeError):
            feature = pathlib.Path(json.loads(pointer.read_text(encoding="utf-8")).get("feature_directory", "")).name
    session = os.environ.get("L7R_PAGE_SESSION") or os.environ.get("CLAUDE_CODE_SESSION_ID", "")
    return {"feature": feature.split("-")[0], "clone": root.name, "session": session}


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


# ---- the ledger ------------------------------------------------------------------------------------------------


def append(where: pathlib.Path, rows: list[dict]) -> None:
    if not rows:
        return
    for r in rows:
        _blocked().check(r.get("raw") or r.get("url", ""), "a sources-consulted ledger line")
    with locked(where), open(where / LEDGER, "a", encoding="utf-8") as f:
        f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)


def read(where: pathlib.Path) -> list[dict]:
    path = where / LEDGER
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines() if path.is_file() else []:
        with contextlib.suppress(json.JSONDecodeError):
            rows.append(json.loads(line))
    return rows


def line(ctx: dict, url: str, outcome: str, questions: list[str] | None = None) -> dict:
    return {"url": norm(url), "raw": url, "utc": now(), **ctx, "questions": questions or [], "outcome": outcome}


def archive_reads(root: pathlib.Path, urls: list[str], runner=None) -> int:  # noqa: ANN001 - the seam a test replaces
    """A page is archived when it is cited (feature 309 FR-014, Amendment 2: the uncited reads are feature 312's, whose
    filter decides which are kept): `archive_ops.py urls` captures each URL with no archive row yet, its report on stderr
    so this command's own output is unchanged. A failure never blocks the read. `L7R_ARCHIVE_READS=0` switches it off - the test suite's seam
    (`tests/tooling/conftest.py`), as `L7R_SOURCES_HOME` moves the ledger; no session sets it."""
    import subprocess  # noqa: PLC0415

    if not urls or os.environ.get("L7R_ARCHIVE_READS") == "0":
        return 0
    done = (runner or subprocess.run)([sys.executable, str(HERE / "archive_ops.py"), "urls", *urls], cwd=root, stdout=sys.stderr, stderr=sys.stderr, check=False)
    if done.returncode != 0:
        print(f"archive: archiving the pages read failed (exit {done.returncode}) - `make archive URL=<u>` retries one", file=sys.stderr)
    return done.returncode


def valid_outcome(outcome: str) -> bool:
    return bool(_OUTCOME.fullmatch(outcome.strip()))


def show(row: dict) -> str:
    """One ledger line as a reader wants it: when, who, what for, what came of it."""
    who = " ".join(p for p in (f"f{row['feature']}" if row.get("feature") else "", row.get("clone", ""),
                                f"s:{row['session'][:8]}" if row.get("session") else "") if p)
    reads = f" x{row['reads']}" if row.get("reads", 1) > 1 else ""
    qs = "; ".join(row.get("questions") or [])
    return f"  {row.get('utc', '')[:10]}  {who or '-'}{reads}  {row.get('outcome', '')}" + (f"  q: {qs[:240]}" if qs else "")


def earlier(where: pathlib.Path, url: str) -> list[dict]:
    key = norm(url)
    return [r for r in read(where) if r.get("url") == key]


def by_key(where: pathlib.Path, pattern: str) -> list[dict]:
    rx = re.compile(pattern)
    return [r for r in read(where) if str(r.get("outcome", "")).startswith("cited:") and rx.search(r["outcome"][6:])]


# ---- the registry ----------------------------------------------------------------------------------------------


def _check_bundle():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("_check_bundle", HERE / "check_bundle.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def registry(root: pathlib.Path) -> dict[str, str]:
    """Each registry entry's key -> the pointer it names (`_check_bundle.url_of`, the one reading of an entry)."""
    url_of = _check_bundle().url_of
    out = {}
    for f in sorted((root / REGISTRY).glob("[0-9]*-*.html")):
        m = re.fullmatch(r"\d+-(.+)\.html", f.name)
        url = url_of(f.read_text(encoding="utf-8")) if m else ""
        if m and url:
            out[m.group(1)] = url
    return out


def registry_urls(root: pathlib.Path) -> dict[str, str]:
    """Normalized URL -> the key of the entry that cites it: an entry's own pointer first, then any other URL in it
    (the measurement counted a URL cited if any registry entry carried it, R1)."""
    url_of = _check_bundle().url_of
    primary, other = {}, {}
    for f in sorted((root / REGISTRY).glob("[0-9]*-*.html")):
        m = re.fullmatch(r"\d+-(.+)\.html", f.name)
        if not m:
            continue
        text = f.read_text(encoding="utf-8")
        own = url_of(text)
        if own:
            primary.setdefault(norm(own), m.group(1))
        for u in _URL.findall(text):
            other.setdefault(norm(html.unescape(u)), m.group(1))
    return {**other, **primary}


def mark_filled(root: pathlib.Path, where: pathlib.Path) -> list[dict]:
    """A `cited:<key>` line for every filled registry entry whose URL the ledger does not already mark so - the
    "when the entry is filled" half of FR-005, run by `make record` and `make sources-consulted`."""
    have = {(r.get("url"), r.get("outcome")) for r in read(where)}
    ctx = context(root)
    rows = [line(ctx, url, f"cited:{key}") for key, url in registry(root).items() if (norm(url), f"cited:{key}") not in have]
    append(where, rows)
    return rows


# ---- the cache -------------------------------------------------------------------------------------------------


def wrapped(text: str) -> str:
    """One sentence to a line (Latin and CJK stops), so `Grep` returns a passage and `Read` can page around it.

    A Latin stop ends a sentence only before whitespace; a CJK stop needs none. WHY (feature 288 plan review): the
    rule broke after any stop, so "3.5 m" was saved as "3." and "5 m" on two lines, and a grep for the figure a
    claim names - the first thing source-reader greps for - missed the page's own sentence."""
    return re.sub(r"(?<=[.!?])\s+(?=\S)|(?<=[。！？])\s*(?=\S)", "\n", text).strip() + "\n"


PART = 20_000  # the most characters one saved file holds (feature 250 D19): a longer page is saved as parts


def parts(text: str, size: int = PART) -> list[str]:
    """`text` cut at line ends into pieces of at most `size` characters (a single longer line is cut where it must).

    WHY (feature 250 D19, research R10): one source was a whole book, and the checks that read its saved page read
    200,026 and 83,621 characters of it. A grep hit now leads to one part, never to the book."""
    out: list[str] = []
    cur = ""
    for ln in text.splitlines(keepends=True):
        while len(ln) > size:
            if cur:
                out.append(cur)
                cur = ""
            out.append(ln[:size])
            ln = ln[size:]
        if len(cur) + len(ln) > size:
            out.append(cur)
            cur = ""
        cur += ln
    return [*out, cur] if cur else out


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


def _write(path: pathlib.Path, text: str) -> None:
    """Written to a temporary name and renamed, so a reader never sees half a file."""
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def put(where: pathlib.Path, url: str, text: str, fetched: str | None = None, exact: bool = True, origin: str = "fetch") -> dict:
    """Store one page: its text, its saved form in parts, and `meta.json` last (a reader needs both)."""
    _blocked().check(url, "the page cache")
    d = entry_dir(where, url)
    d.mkdir(parents=True, exist_ok=True)
    pieces = parts(wrapped(text))
    with locked(where):
        for old in d.glob("page*.txt"):
            old.unlink()
        _write(d / "text.txt", text)
        names = ["page.txt"] if len(pieces) == 1 else [f"page.p{k}.txt" for k in range(1, len(pieces) + 1)]
        for name, piece in zip(names, pieces, strict=True):
            _write(d / name, piece)
        meta = {"url": url, "norm": norm(url), "fetched": fetched or now(), "chars": len(text), "exact": exact, "origin": origin}
        _write(d / "meta.json", json.dumps(meta, ensure_ascii=False, indent=1) + "\n")
    return {**meta, "text": text, "dir": d, "files": names}


def refresh_wanted() -> bool:
    """`REFRESH=1` on any make target that saves or checks a page: make exports a command-line variable to its
    recipes, so every script that fetches through the cache honors it without its own flag."""
    return os.environ.get("REFRESH", "") not in ("", "0")


class CachedPages:
    """A `_quote_verbatim.Pages` that asks the cache first and stores what it fetches (FR-008 - FR-010)."""

    def __init__(self, inner, where: pathlib.Path, refresh: bool = False, exact: bool = False, max_age_days: float = MAX_AGE_DAYS) -> None:  # noqa: ANN001
        self.inner, self.where, self.refresh, self.exact, self.max_age = inner, where, refresh, exact, max_age_days

    @property
    def refused(self) -> dict:
        """The hosts that refused this run - quote-verbatim's report names them (the inner fetcher's own record)."""
        return getattr(self.inner, "refused", {})

    def get(self, url: str) -> dict:
        """A blocked URL is never fetched (feature 312 FR-002): it comes back UNFETCHABLE with the refusal as its reason,
        so a run over many pointers reports it beside the rest instead of stopping."""
        rule = _blocked().blocked(url)
        if rule is not None:
            return {"state": "UNFETCHABLE", "why": _blocked().refusal(url, rule, "a fetch"), "blocked": True}
        hit = None if self.refresh else cached(self.where, url, self.max_age, self.exact)
        if hit is not None:
            return {"state": "FETCHED", "text": hit["text"], "cached": hit["fetched"]}
        got = self.inner.get(url)
        if got["state"] == "FETCHED":
            put(self.where, url, got["text"])
        return got


# ---- the one-time seed and import ------------------------------------------------------------------------------

SEED = "reread-2026-09-29"


def seed(per_url: pathlib.Path, root: pathlib.Path, where: pathlib.Path) -> int:
    """One line per URL, feature and session of the measurement's reads (FR-007): the first read's time, the reads'
    count, up to three of the questions asked of the page, and `cited:<key>` where a registry entry names the URL,
    else `unknown-outcome`. Run once: a ledger already holding the seed is left alone."""
    if any(r.get("seed") == SEED for r in read(where)):
        return 0
    cited = registry_urls(root)
    rows = []
    for url, events in json.loads(per_url.read_text(encoding="utf-8")).items():
        groups: dict[tuple[str, str], list[dict]] = {}
        for e in sorted(events, key=lambda e: e.get("ts", "")):
            groups.setdefault((str(e.get("feature") or ""), e.get("session", "")), []).append(e)
        for (feature, session), evs in groups.items():
            whys = list(dict.fromkeys(" ".join(str(e["why"]).split())[:200] for e in evs if e.get("why")))[:3]
            rows.append({"url": url, "raw": url, "utc": evs[0].get("ts", "")[:19] + "+00:00", "feature": feature, "clone": "",
                         "session": session, "questions": whys, "outcome": f"cited:{cited[url]}" if url in cited else "unknown-outcome",
                         "reads": len(evs), "seed": SEED})
    append(where, rows)
    return len(rows)


def import_saves(scratch: pathlib.Path, where: pathlib.Path) -> dict:
    """Each distinct page saved under `scratch` (`/tmp/l7r-check`) into the cache once (FR-012): the newest whole
    save of each normalized URL - an EXCERPT (feature 250 D19) is not the page and is skipped. Its text is the saved
    form, so it is marked `exact: false` and quote-verbatim, which compares characters, fetches the page afresh."""
    best: dict[str, tuple[float, str, pathlib.Path, list[pathlib.Path]]] = {}
    counts = {"manifests": 0, "rows": 0, "excerpts": 0, "missing": 0}
    for manifest in sorted(scratch.rglob("MANIFEST.txt")):
        counts["manifests"] += 1
        for row in manifest.read_text(encoding="utf-8", errors="replace").splitlines()[1:]:
            pointer, file, state = ([*row.split(" | ", 2), "", ""])[:3]
            if not state.startswith("FETCHED") or file in ("", "-") or not pointer.startswith("http"):
                continue
            counts["rows"] += 1
            if "excerpt" in state:
                counts["excerpts"] += 1
                continue
            stem = file.split(" ")[0].removesuffix(".txt").removesuffix(".p1")  # `NN-host.txt`, or `NN-host.p1.txt ... (N parts)`
            files = sorted(manifest.parent.glob(f"{stem}.p*.txt"), key=lambda p: int(p.name.rsplit(".p", 1)[1][:-4])) or [manifest.parent / f"{stem}.txt"]
            if not all(f.is_file() for f in files) or files[0].read_text(encoding="utf-8", errors="replace").startswith("[EXCERPT"):
                counts["missing" if not all(f.is_file() for f in files) else "excerpts"] += 1
                continue
            mtime = max(f.stat().st_mtime for f in files)
            key = norm(pointer)
            if key not in best or mtime > best[key][0]:
                best[key] = (mtime, pointer, manifest.parent, files)
    imported = kept = 0
    for key, (mtime, pointer, _dir, files) in sorted(best.items()):
        if cached(where, pointer, max_age_days=10_000) is not None:
            kept += 1
            continue
        text = "".join(f.read_text(encoding="utf-8", errors="replace") for f in files)
        fetched = datetime.datetime.fromtimestamp(mtime, datetime.timezone.utc).isoformat(timespec="seconds")
        put(where, pointer, text, fetched=fetched, exact=False, origin=f"import:{_dir}")
        imported += 1
    return {**counts, "distinct": len(best), "imported": imported, "already": kept}


# ---- the command line ------------------------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    o = sub.add_parser("outcome", help="record what came of reading a page")
    o.add_argument("url")
    o.add_argument("outcome")
    o.add_argument("--question", default="")
    o.add_argument("--sought", default="", help="what the read looked for (feature 312); else the latest attempt's")
    q = sub.add_parser("lookup", help="the ledger's lines for a URL, or for the registry keys a regex matches")
    q.add_argument("--url", default="")
    q.add_argument("--key", default="")
    sub.add_parser("mark-filled", help="mark every filled registry entry's URL cited")
    s = sub.add_parser("import", help="one time: seed the ledger from the measurement and import the saved pages")
    s.add_argument("--per-url", default="/diagram/.clones/.tools/logs/reread-2026-09-29/per_url.json")
    s.add_argument("--scratch", default="/tmp/l7r-check")
    args = ap.parse_args(argv)
    root, where = repo_root(), home()
    if args.cmd == "outcome":
        if not valid_outcome(args.outcome):
            print(f"source-outcome: OUTCOME={args.outcome!r} is not one of: {OUTCOMES}", file=sys.stderr)
            return 2
        row = line(context(root), args.url, args.outcome.strip(), [args.question] if args.question else [])
        append(where, [row])
        print(f"source-outcome: recorded{show(row)}")
        _attempts_mod().outcome(root, args.url, args.question, args.outcome.strip(), args.sought)
        if row["outcome"].startswith("cited:"):
            archive_reads(root, [args.url])
        return 0
    if args.cmd == "lookup":
        if not (args.url or args.key):
            print("sources-consulted: URL=<u> or KEY=<regex> is required", file=sys.stderr)
            return 2
        filled = mark_filled(root, where)
        rows = earlier(where, args.url) if args.url else by_key(where, args.key)
        print(f"sources-consulted: {len(rows)} line(s) for {norm(args.url) if args.url else 'keys matching ' + repr(args.key)}"
              + (f" ({len(filled)} newly filled registry entr{'y' if len(filled) == 1 else 'ies'} marked cited first)" if filled else ""))
        for r in rows:
            print((f"  {r['url']}\n  " if args.key else "") + show(r))
        return 0
    if args.cmd == "mark-filled":
        n = len(mark_filled(root, where))
        print(f"sources-consulted: {n} filled registry entr{'y' if n == 1 else 'ies'} marked cited")
        return 0
    per_url, scratch = pathlib.Path(args.per_url), pathlib.Path(args.scratch)
    seeded = seed(per_url, root, where) if per_url.is_file() else 0
    got = import_saves(scratch, where) if scratch.is_dir() else {}
    print(f"sources-import: seeded {seeded} ledger line(s) from {per_url} (0: already seeded, or no file)")
    print(f"sources-import: page cache {json.dumps(got)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
