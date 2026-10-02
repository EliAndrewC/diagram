#!/usr/bin/env python3
"""The uncited pages, judged once: kept, or recorded as not kept with their reasons (feature 312, FR-006 - FR-011).

WHY (the GM, 2026-10-02): *"anything that we take the time to actually store a copy of should get a write-up"*, but blog
posts and dead ends *"feel like things that we should have a record of. So that we know not to check them next time. But
which we don't bother to store the full copy of"* - so *"part of our looking through the backlog of unsighted sources
should be applying a filter and that filter can be its own subagent check"*, its reasons *"a simple matter of tagging"*.

THE SET (FR-006) is computed, never listed: the ledger's and the page cache's URLs with no archive manifest row
(`_archive_ops.consulted_urls`), less any URL a registry entry carries (a cited URL under another spelling, or an uncited
entry already written), less any URL with a verdict, less a blocked domain; plus the manifest rows that no key and no
footnote cite (the three pages captured before the GM held the backfill - the GM: *"their disposition should just be
whatever the filter ends up saying"*). Re-run it after later research and it holds only the pages read since.

THE RULE (FR-007) decides what needs no judgment, with no agent: a search, listing, API or raw URL (`no-substance`); a
page whose text is the same as one already judged or cited (`duplicate`); a page no route can read - the cache, a live
fetch, the Wayback Machine - (`unreadable`, with its access state in feature 313's vocabulary).

THE FILTER (FR-008) is the `source-filter` agent over BUNDLES of whole pages (plan D5, plan review 2026-10-02: never a
front cut). A bundle closes at about 150,000 characters or 60,000 estimated tokens, whichever comes first - a CJK
character is about a token where a Latin one is about a quarter (research.md R3); a page over that goes alone, in parts of
20,000 estimated tokens, each a file the agent reads whole. The agent writes `verdicts.jsonl` beside the bundle's
`MANIFEST.md`; `apply` refuses a bundle whose verdicts miss an id, carry an unknown reason, or give a NOT-KEPT no reason.

WHERE A VERDICT GOES (FR-010, plan D7): a NOT-KEPT is a line of `research/not-kept.jsonl` (union-merged), and the page is
never archived; a KEEP is a line of this feature's `kept.jsonl` until its write-up exists, after which the registry entry
is the record. A pre-hold capture judged NOT-KEPT loses its manifest row; its copy stays in the archive's history.

    _uncited.py set [--write FILE]              the set's count (and the URLs, to FILE)
    _uncited.py rule                            the rule's verdicts on the set, written
    _uncited.py fetch [--workers N] [--limit N] the set's pages with no saved text fetched into the cache, or ruled unreadable
    _uncited.py bundle OUT [--limit N]          the set's remaining pages as filter bundles under OUT
    _uncited.py apply DIR [DIR ...]             a bundle's verdicts written
    _uncited.py score DIR ANSWERS               a calibration run scored against its labels
    _uncited.py report                          where the set stands
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import _archive as ar  # noqa: E402
import _archive_ops as ops  # noqa: E402
import _attempts as at  # noqa: E402
import _sources as src  # noqa: E402

NOT_KEPT = at.NOT_KEPT
KEPT = pathlib.Path("specs/312-uncited-source-catalog/kept.jsonl")
SOURCES = at.RESEARCH / "sources"
REASONS = ("off-topic", "modern-only", "unreliable-kind", "no-substance", "duplicate", "unreadable")
ACCESS = ("bot-refused", "down", "gone", "paywalled")
#: The no-substance rule: `prep.md`'s two regexes, measured over the ledger 2026-10-02, and the forms the plan review found
#: they missed - 44 MediaWiki search pages (`index.php?search=...&title=Special:...`) and a wiki category listing.
SEARCH = re.compile(
    r"duckduckgo|google\.[a-z.]+/search|bing\.com/search|baidu\.com/s\?|search\?|/search/|advancedsearch"
    r"|[?&](q|query|keyword|kw|wd|search)=|/results?\b|/wiki/(?:Category|Special|特別|特殊|Kategorie):|/wiki/カテゴリ:|/wiki/Category%3A",
    re.I,
)
API = re.compile(r"/api/|api\.php|action=raw|output=json|\.json\b", re.I)
#: The GM's own campaign notes are canon, never an uncited source (the GM, 2026-10-02: *"we should probably never do that,
#: just as a general rule"*): no page of theirs enters the set.
CANON = re.compile(r"^github\.com/eliandrewc/|^raw\.githubusercontent\.com/eliandrewc/", re.I)
#: A SHELL: saved text this thin is usually the page's frame, not the page (observed 2026-10-02: a Baidu Baike entry saved
#: as its five-character site name, an ADEAC municipal-history page as ~200 characters of navigation, a frameset's
#: "this page needs frames") - so the fetch reads it again, rendered; and a shell no route improves, under `EMPTY`
#: characters, is unreadable rather than judged.
SHELL_CHARS = 600
EMPTY = 100
BUNDLE_CHARS = 150_000
BUNDLE_TOKENS = 60_000
PART_TOKENS = 20_000
PART_CHARS = 50_000  # the Read tool returns about 60,000 characters of a file; a part longer was read in part (feature 312, 2026-10-02)
_CJK = re.compile(r"[　-鿿가-힯豈-﫿]")


def today() -> str:
    return datetime.date.today().isoformat()


def tokens(text: str) -> int:
    """An estimate: a CJK character about a token, anything else about a quarter of one (research.md R3)."""
    c = len(_CJK.findall(text))
    return c + (len(text) - c) // 4


# ---- the set ----


def judged(root: pathlib.Path) -> set[str]:
    return {x["url"] for x in at.read(root, NOT_KEPT)} | {x["url"] for x in at.read(root, KEPT)}


def registry_norms(root: pathlib.Path) -> set[str]:
    """Every URL any registry entry carries, cited or uncited, normalized."""
    out = set()
    for f in sorted((at.base(root) / SOURCES).glob("*/[0-9]*-*.html")):
        out |= {src.norm(u) for u in src._URL.findall(f.read_text(encoding="utf-8"))}
    return out


def prehold(root: pathlib.Path) -> list[str]:
    """The manifest rows nothing cites - no key, no footnote: the captures made before the GM held the backfill."""
    rows = [json.loads(p.read_text(encoding="utf-8")) for p in ar.row_files(root)]
    return [r["url"] for r in rows if not r.get("keys") and not r.get("notes")]


def cited_marks(root: pathlib.Path) -> set[str]:
    """The URLs the ledger marks `cited:<key>` whose key still has a registry entry: a page cited under another spelling
    of its URL (FR-022, research.md R4 - six of the eight, each covered by its key's archived copy). A mark whose key no
    entry holds is not a citation, and its page is judged like any other."""
    keys = {m.group(1) for f in (at.base(root) / SOURCES).glob("*/[0-9]*-*.html") if (m := re.fullmatch(r"\d+-(.+)\.html", f.name))}
    return {r["url"] for r in src.read(src.home(root)) if r.get("outcome", "").startswith("cited:") and r["outcome"][6:].strip() in keys}


_ZH_VARIANT = re.compile(r"^zh\.wikipedia\.org/(?:zh-(?:hans|hant|cn|tw|hk|sg|mo)|wiki)/")


def work(n: str) -> str:
    """One work under one key: a normalized URL with Chinese Wikipedia's script variants folded into `/wiki/` - the same
    article served as `/zh-hans/X`, `/zh-tw/X` and `/wiki/X` was judged and written up twice (Pingyao's wall, 2026-10-02)."""
    return _ZH_VARIANT.sub("zh.wikipedia.org/wiki/", n)


def uncited_set(root: pathlib.Path) -> list[str]:
    skip = {work(n) for n in judged(root) | registry_norms(root) | cited_marks(root)}
    blocked = src._blocked()
    out: dict[str, str] = {}
    for u in [*ops.consulted_urls(root), *prehold(root)]:
        n = work(src.norm(u))
        if n not in skip and not blocked.blocked(u) and not CANON.search(n):
            out.setdefault(n, u)
    return sorted(out.values())


def fingerprint(text: str | None) -> str:
    """The saved text of one revision, whatever URL reached it: two redirects to one article (杖刑 and 笞刑, 2026-10-02)
    save the same body. The head is skipped (the title a redirect may carry); a page too short to tell gives none."""
    body = re.sub(r"\s+", " ", text or "")
    return "" if len(body) < 1000 else hashlib.sha1(body[200:].encode()).hexdigest()


def duplicate_works(root: pathlib.Path) -> list[tuple[str, str]]:
    """Kept pages that are one work with a cited entry's URL or an earlier kept page - by URL under another spelling
    (`work`) or by the same saved text (`fingerprint`): each as (the kept page's raw URL, what it duplicates)."""
    seen: dict[str, str] = {}
    for f in sorted((at.base(root) / SOURCES).glob("*/[0-9]*-*.html")):
        if f.parent.name != at.UNCITED.name:
            for u in src._URL.findall(f.read_text(encoding="utf-8")):
                seen.setdefault(work(src.norm(u)), f.stem.split("-", 1)[1])
    where = src.home(root)
    out = []
    for x in at.read(root, KEPT):
        marks = [m for m in (work(x["url"]), fingerprint(text_of(where, x["raw"]))) if m]
        hit = next((seen[m] for m in marks if m in seen), None)
        if hit:
            out.append((x["raw"], hit))
        else:
            seen.update(dict.fromkeys(marks, x["raw"]))
    return out


# ---- the rule ----


#: Not a URL at all: a shell fragment the ledger's seed took from a command line (`https://kotobank.jp/word/${enc}`,
#: `...?title=$(python3`, `.../wiki/$u`, a regex `[^` - observed 2026-10-02).
_SHELL = re.compile(r"[$`{}\s]|\[\^")


def wellformed(url: str) -> bool:
    """A URL a fetch can be aimed at: it parses, has a dotted host, and is no shell fragment."""
    try:
        host = ar.urllib.parse.urlsplit(url).hostname or ""
    except ValueError:
        return False
    return "." in host and not _SHELL.search(url)


def no_substance(url: str) -> bool:
    return bool(SEARCH.search(url) or API.search(url))


def access_of(got: ar.Fetched) -> str:
    """A failed fetch's access state (feature 313's vocabulary)."""
    if got.status in (401, 402):
        return "paywalled"
    if got.status in (403, 406, 429, 451):
        return "bot-refused"
    if got.status in (404, 410):
        return "gone"
    return "down"


def line(url: str, reasons: list[str], basis: str, note: str = "", access: str = "") -> dict:
    bad = [r for r in reasons if r not in REASONS]
    if not reasons or bad:
        raise ValueError(f"{url}: reasons {reasons!r} - each one of {', '.join(REASONS)}, at least one")
    if access and access not in ACCESS:
        raise ValueError(f"{url}: access {access!r} is not one of {', '.join(ACCESS)}")
    x = {"url": src.norm(url), "raw": url, "reasons": reasons, "note": note, "basis": basis, "date": today(), "feature": "312"}
    return {**x, "access": access} if access else x


def not_kept(root: pathlib.Path, lines: list[dict]) -> None:
    """Written to `not-kept.jsonl` under the attempts log's lock; a blocked URL is refused there too."""
    at.write(root, lines, NOT_KEPT)
    for x in lines:  # FR-010: a pre-hold capture not kept loses its manifest row; its copy stays in the archive's history
        row = ar.row_path(root, x["raw"])
        if row.is_file() and not json.loads(row.read_text(encoding="utf-8")).get("keys"):
            row.unlink()


def kept(root: pathlib.Path, urls: list[str], basis: str) -> None:
    at.write(root, [{"url": src.norm(u), "raw": u, "basis": basis, "date": today(), "feature": "312"} for u in urls], KEPT)


def text_of(where: pathlib.Path, url: str) -> str | None:
    hit = src.cached(where, url, max_age_days=10_000)
    return hit["text"] if hit else None


def digest(text: str) -> str:
    return hashlib.sha256(re.sub(r"\s+", " ", text).strip().encode("utf-8")).hexdigest()


def rule(root: pathlib.Path, urls: list[str]) -> dict[str, int]:
    """The verdicts no agent is needed for: no-substance by URL; duplicate by the text of a cited page or of a page
    earlier in the set."""
    where = src.home(root)
    cited = {digest(t) for u in registry_norms(root) if (t := text_of(where, "https://" + u))}
    seen: dict[str, str] = {}
    out: list[dict] = []
    for u in urls:
        if no_substance(u):
            out.append(line(u, ["no-substance"], "rule", "a search, listing, API or raw URL"))
            continue
        if not wellformed(u):
            out.append(line(u, ["unreadable"], "rule", "a malformed URL no route can fetch (a fragment, or a shell variable)", "gone"))
            continue
        t = text_of(where, u)
        if t is None or not t.strip():
            continue
        d = digest(t)
        if d in cited:
            out.append(line(u, ["duplicate"], "rule", "the same text as a cited page"))
        elif d in seen:
            out.append(line(u, ["duplicate"], "rule", f"the same text as {seen[d]}"))
        else:
            seen[d] = u
    not_kept(root, out)
    return {"no-substance": sum(x["reasons"] == ["no-substance"] for x in out), "duplicate": sum(x["reasons"] == ["duplicate"] for x in out)}


def needs_fetch(where: pathlib.Path, url: str) -> bool:
    """No saved text, or a shell of one."""
    t = text_of(where, url)
    return t is None or len(t.strip()) < SHELL_CHARS


def fetch_one(browser, where: pathlib.Path, url: str) -> tuple[str, str]:  # noqa: ANN001
    """Read one page into the cache: live, then the Wayback Machine's newest snapshot. A read replaces saved text only
    when it is longer. Returns ("", "") when the page now has more than an empty shell, or (its access state, why)."""
    have = (text_of(where, url) or "").strip()
    got = ar.fetch(browser, url)
    text = got.text.strip() if got.text and not got.error and got.status and got.status < 400 else ""
    state, why = ("", "") if text else (access_of(got), got.error or f"HTTP {got.status}")
    origin = "fetch"
    if len(text) < SHELL_CHARS:
        snap = ar.wayback(browser, url)
        if snap:
            old = ar.fetch(browser, snap[0])
            if old.text and len(old.text.strip()) > len(text):
                text, origin = old.text.strip(), "wayback"
    if len(text) > len(have):
        src.put(where, url, text, origin=origin)
        have = text
    if len(have) >= EMPTY:
        return "", ""
    return state or "down", why or "an empty page"


def fetch(root: pathlib.Path, urls: list[str], browser) -> dict[str, int]:  # noqa: ANN001
    """FR-007: every page of the set with no saved text, or a shell of one, read or ruled unreadable."""
    where = src.home(root)
    counts = {"read": 0, "unreadable": 0}
    for n, u in enumerate(urls, 1):
        if no_substance(u) or not needs_fetch(where, u):
            continue
        if n % ar.RECYCLE_EVERY == 0 and hasattr(browser, "close"):
            browser.close()
            browser = ar.Browser()
        try:
            state, why = fetch_one(browser, where, u)
        except Exception as err:  # a browser that died under one page (Playwright "Event loop is closed!", 2026-10-02) ends
            # one page's read, not the lane: the page is left unjudged for the next run, and the lane gets a fresh browser
            print(f"{'error':22} {u} - {type(err).__name__}: {str(err)[:120]}", flush=True)
            counts["error"] = counts.get("error", 0) + 1
            if hasattr(browser, "close"):
                try:
                    browser.close()
                except Exception:  # noqa: BLE001, S110 - a dead browser may fail to close; the new one is what matters
                    pass
                browser = ar.Browser()
            continue
        at.add(root, u, "unknown", "feature 312's filter: is the page worth keeping", "unreadable" if state else "unknown", route="uncited-fetch")
        if state:
            not_kept(root, [line(u, ["unreadable"], "rule", why, state)])
            counts["unreadable"] += 1
        else:
            counts["read"] += 1
        print(f"{'unreadable ' + state if state else 'read':22} {u}", flush=True)
    return counts


def _lane(args: tuple[str, list[str]]) -> dict[str, int]:  # pragma: no cover - one worker with a live browser; `fetch` is tested
    root, urls = pathlib.Path(args[0]), args[1]
    browser = ar.Browser()
    try:
        return fetch(root, urls, browser)
    finally:
        browser.close()


def fetch_all(root: pathlib.Path, urls: list[str], workers: int) -> dict[str, int]:  # pragma: no cover - the live run
    """The fetch in lanes, every URL of one host in one lane (the archive's rule: never two requests to a host at once)."""
    jobs = [(str(root), lane) for lane in ar.lanes(urls, workers)]
    total = {"read": 0, "unreadable": 0, "error": 0}
    with ar.multiprocessing.get_context("spawn").Pool(len(jobs) or 1) as pool:
        for got in pool.imap_unordered(_lane, jobs):
            total = {k: total[k] + got.get(k, 0) for k in total}
    return total


# ---- the imported copies (research.md R5) ----

MISFILED = pathlib.Path("specs/312-uncited-source-catalog/import-check.jsonl")


def imported(where: pathlib.Path, url: str) -> str | None:
    """The page's saved text when it came from feature 288's one-time import of old saves, which filed some pages' text
    under another URL (observed 2026-10-02: `ja.wikipedia.org/wiki/村` held 砂利道's article) - else None."""
    hit = src.cached(where, url, max_age_days=10_000)
    return hit["text"] if hit and str(hit.get("origin", "")).startswith("import") else None


def grams(text: str, n: int = 4) -> set[str]:
    t = re.sub(r"\s+", " ", text)[:5000]
    return {t[i : i + n] for i in range(max(0, len(t) - n + 1))}


def same_page(a: str, b: str) -> bool:
    """Two texts of one page: their character 4-grams over the first 5,000 characters overlap by a third or more (a page
    re-fetched later differs by its edits and its navigation, never by its subject)."""
    ga, gb = grams(a), grams(b)
    return bool(ga and gb) and len(ga & gb) / len(ga | gb) >= 1 / 3


def verify(root: pathlib.Path, urls: list[str], browser) -> dict[str, int]:  # noqa: ANN001
    """Each URL whose saved text is an imported copy, read live: the copy replaced by the live text, and a line in
    `import-check.jsonl` saying whether the copy was this page (`same`), another page's (`misfiled`), or could not be
    told (`unread`). A misfiled page's verdict is then judged again from the live text."""
    where = src.home(root)
    counts = {"same": 0, "misfiled": 0, "unread": 0}
    for u in urls:
        old = imported(where, u)
        if old is None:
            continue
        got = ar.fetch(browser, u)
        live = got.text.strip() if got.text and not got.error and got.status and got.status < 400 else ""
        result = "unread" if len(live) < EMPTY else ("same" if same_page(old, live) else "misfiled")
        if live and result != "unread":
            src.put(where, u, live, origin="fetch")
        at.write(root, [{"url": src.norm(u), "raw": u, "result": result, "date": today()}], MISFILED)
        counts[result] += 1
        print(f"{result:10} {u}", flush=True)
    return counts


def _verify_lane(args: tuple[str, list[str]]) -> dict[str, int]:  # pragma: no cover - one worker with a live browser; `verify` is tested
    root, urls = pathlib.Path(args[0]), args[1]
    browser = ar.Browser()
    try:
        return verify(root, urls, browser)
    finally:
        browser.close()


def verify_all(root: pathlib.Path, urls: list[str], workers: int) -> dict[str, int]:  # pragma: no cover - the live run
    jobs = [(str(root), lane) for lane in ar.lanes(urls, workers)]
    total = {"same": 0, "misfiled": 0, "unread": 0}
    with ar.multiprocessing.get_context("spawn").Pool(len(jobs) or 1) as pool:
        for got in pool.imap_unordered(_verify_lane, jobs):
            total = {k: total[k] + got[k] for k in total}
    return total


def imported_urls(where: pathlib.Path) -> list[str]:
    """Every page-cache entry that came from the one-time import - cited and uncited alike (the defect is the cache's)."""
    out = []
    for meta in sorted(where.glob(f"{src.CACHE}/*/*/meta.json")):
        m = json.loads(meta.read_text(encoding="utf-8"))
        if str(m.get("origin", "")).startswith("import") and str(m.get("url", "")).startswith("http"):
            out.append(m["url"])
    return out


# ---- the bundles ----


def title_of(text: str) -> str:
    return next((x.strip()[:120] for x in text.splitlines() if x.strip()), "(no text)")


def split(text: str, limit: int = 0) -> list[str]:
    """A long page in parts of about `limit` (`PART_TOKENS`) estimated tokens and at most `PART_CHARS` characters, cut at a
    line where one falls."""
    limit = limit or PART_TOKENS
    parts, cur, n, c = [], [], 0, 0
    for ln in text.splitlines(keepends=True):
        t = tokens(ln)
        if cur and (n + t > limit or c + len(ln) > PART_CHARS):
            parts.append("".join(cur))
            cur, n, c = [], 0, 0
        while t > limit or len(ln) > PART_CHARS:  # one enormous line
            cut = max(1, min(len(ln) * limit // max(t, 1), PART_CHARS))
            parts.append(ln[:cut])
            ln, t = ln[cut:], tokens(ln[cut:])
        cur.append(ln)
        n, c = n + t, c + len(ln)
    return [*parts, "".join(cur)] if cur else parts


def groups(pages: list[tuple[str, str]]) -> list[list[tuple[str, str]]]:
    """Pages into bundles: each closes at `BUNDLE_CHARS` or `BUNDLE_TOKENS`; a page over either goes alone."""
    out, cur, chars, toks = [], [], 0, 0
    for url, text in pages:
        c, t = len(text), tokens(text)
        if c > BUNDLE_CHARS or t > BUNDLE_TOKENS:
            out.append([(url, text)])
            continue
        if cur and (chars + c > BUNDLE_CHARS or toks + t > BUNDLE_TOKENS):
            out.append(cur)
            cur, chars, toks = [], 0, 0
        cur.append((url, text))
        chars, toks = chars + c, toks + t
    return [*out, cur] if cur else out


MANIFEST_HEAD = """# source-filter bundle {name}

{n} page(s). Read EVERY file listed below, whole - a page in parts is every part - and judge each page as your contract
says. Write `verdicts.jsonl` in THIS directory, one JSON line per id, then reply with one count line.

"""


CONTRACT = HERE.parent / ".claude" / "agents" / "source-filter.md"


def contract_body() -> str:
    """The `source-filter` contract without its frontmatter, copied into every bundle as `CONTRACT.md`: a session that has
    not restarted since the agent file was added cannot dispatch it by name, and dispatches an ad-hoc Opus agent on the
    same contract instead (research.md R2) - which then reads nothing under the repository."""
    text = CONTRACT.read_text(encoding="utf-8")
    return text.split("\n---\n", 1)[1].lstrip() if text.startswith("---\n") else text


def write_bundle(d: pathlib.Path, pages: list[tuple[str, str, str]]) -> None:
    """`pages` is (id, url, text). Each page's text in its own files; the MANIFEST names them; the contract beside them."""
    d.mkdir(parents=True, exist_ok=True)
    (d / "CONTRACT.md").write_text(contract_body(), encoding="utf-8")
    body = [MANIFEST_HEAD.format(name=d.name, n=len(pages))]
    for pid, url, text in pages:
        parts = split(text)
        names = [f"{pid}.txt"] if len(parts) == 1 else [f"{pid}.part{k}.txt" for k in range(1, len(parts) + 1)]
        for name, part in zip(names, parts, strict=True):
            (d / name).write_text(part, encoding="utf-8")
        body.append(f"## {pid}\n\n- url: {url}\n- title: {title_of(text)}\n- size: {len(text):,} characters, about "
                    f"{tokens(text):,} tokens\n- files: {', '.join(names)}\n\n")
    (d / "MANIFEST.md").write_text("".join(body), encoding="utf-8")
    (d / "ids.json").write_text(json.dumps({pid: url for pid, url, _ in pages}, ensure_ascii=False, indent=1), encoding="utf-8")


def bundle(root: pathlib.Path, urls: list[str], out: pathlib.Path, start: int = 1) -> list[pathlib.Path]:
    where = src.home(root)
    pages = [(u, t) for u in urls if (t := text_of(where, u)) is not None and t.strip()]
    pages.sort(key=lambda p: (ar.urllib.parse.urlsplit(p[0]).netloc, p[0]))
    dirs, n = [], 0
    for k, group in enumerate(groups(pages), start):
        d = out / f"312-filter-{k:04d}"
        items = []
        for url, text in group:
            n += 1
            items.append((f"p{n:05d}", url, text))
        write_bundle(d, items)
        dirs.append(d)
    return dirs


# ---- the verdicts ----


def read_verdicts(d: pathlib.Path) -> tuple[dict[str, dict], list[str]]:
    """The bundle's verdicts by id, and every problem with them (FR-008's shape)."""
    ids = json.loads((d / "ids.json").read_text(encoding="utf-8"))
    path = d / "verdicts.jsonl"
    got: dict[str, dict] = {}
    problems = []
    for raw in path.read_text(encoding="utf-8").splitlines() if path.is_file() else []:
        if not raw.strip():
            continue
        try:
            v = json.loads(raw)
        except json.JSONDecodeError:
            problems.append(f"not JSON: {raw[:80]}")
            continue
        pid = v.get("id", "")
        if pid not in ids:
            problems.append(f"{pid!r} is not an id of this bundle")
        elif v.get("verdict") not in ("KEEP", "NOT-KEPT"):
            problems.append(f"{pid}: verdict {v.get('verdict')!r}")
        elif v["verdict"] == "NOT-KEPT" and (not v.get("reasons") or any(r not in REASONS for r in v["reasons"])):
            problems.append(f"{pid}: NOT-KEPT needs reasons from {', '.join(REASONS)} - got {v.get('reasons')!r}")
        else:
            got[pid] = v
    problems += [f"{pid}: no verdict" for pid in ids if pid not in got]
    return got, problems


def apply(root: pathlib.Path, d: pathlib.Path) -> dict[str, int]:
    got, problems = read_verdicts(d)
    if problems:
        raise ValueError(f"{d}: verdicts refused -\n  " + "\n  ".join(problems))
    ids = json.loads((d / "ids.json").read_text(encoding="utf-8"))
    nk = [line(ids[p], v["reasons"], "source-filter", (v.get("note") or "")[:200]) for p, v in got.items() if v["verdict"] == "NOT-KEPT"]
    keep = [ids[p] for p, v in got.items() if v["verdict"] == "KEEP"]
    not_kept(root, nk)
    kept(root, keep, "source-filter")
    proposed = sorted({v["propose_block"] for v in got.values() if v.get("propose_block")})
    for dom in proposed:
        print(f"uncited: {d.name} proposes blocking {dom} - for the GM; only the GM adds a domain (FR-001)")
    return {"kept": len(keep), "not-kept": len(nk), "proposed": len(proposed)}


def score(d: pathlib.Path, answers: dict[str, str]) -> dict[str, dict[str, int]]:
    """A calibration run against its labels (`answers`: id -> KEEP | NOT-KEPT): per leg, agreed of total."""
    got, problems = read_verdicts(d)
    if problems:
        raise ValueError(f"{d}: verdicts refused -\n  " + "\n  ".join(problems))
    out: dict[str, dict[str, int]] = {"KEEP": {"agreed": 0, "total": 0}, "NOT-KEPT": {"agreed": 0, "total": 0}}
    for pid, want in answers.items():
        out[want]["total"] += 1
        out[want]["agreed"] += got[pid]["verdict"] == want
    return out


# ---- the write-ups (FR-012, plan D9) ----

WRITEUP = HERE.parent / "specs" / "312-uncited-source-catalog" / "writeup-contract.md"
DRAFT_PAGES = 15
_KEY = re.compile(r"^[a-z0-9][a-z0-9-]*$")
#: A field's own label written into its text by the drafter (the pilot, 2026-10-02: "What it is: A database entry...") - the
#: entry writes the label itself, so a leading one is dropped rather than doubled.
_LABEL = re.compile(r"^(?:What it is|Why it applies, and its limits)\s*:\s*", re.I)


def vocabulary_block(root: pathlib.Path) -> str:
    """Every tag value with its explanation, from the record's own vocabulary (the source-applicability contract's form)."""
    st = sys.modules.get("_source_tags") or _load_source_tags()
    return st.contract_block(st.load_vocabulary(str(at.base(root) / at.RESEARCH)))


def _load_source_tags():  # noqa: ANN202
    import importlib.util  # noqa: PLC0415

    spec = importlib.util.spec_from_file_location("_source_tags", HERE.parent / ".claude/skills/diagram/l7r/diagram/interactive/record/source_tags.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def written(root: pathlib.Path) -> set[str]:
    """The kept URLs that already have an uncited entry."""
    d = at.base(root) / at.UNCITED
    return {src.norm(u) for f in (sorted(d.glob("*.html")) if d.is_dir() else []) for u in src._URL.findall(f.read_text(encoding="utf-8"))}


def registry_keys(root: pathlib.Path) -> set[str]:
    return {m.group(1) for f in (at.base(root) / SOURCES).glob("*/[0-9]*-*.html") if (m := re.fullmatch(r"\d+-(.+)\.html", f.name))}


DRAFT_HEAD = """# write-up draft bundle {name}

{n} kept page(s). Read CONTRACT.md, then EVERY file listed below, whole - a page in parts is every part - and draft each
page's registry write-up as the contract says. Write `entries.jsonl` in THIS directory, one JSON line per id, then reply
with one count line.

"""


def draft_bundles(root: pathlib.Path, out: pathlib.Path, start: int = 1) -> list[pathlib.Path]:
    """The kept pages with no entry yet, DRAFT_PAGES a bundle (within the token budget), each with the drafting contract."""
    where, done = src.home(root), written(root)
    todo = [(x["raw"], t) for x in at.read(root, KEPT) if x["url"] not in done and (t := text_of(where, x["raw"]))]
    contract = WRITEUP.read_text(encoding="utf-8") + vocabulary_block(root) + "\n"
    taken = registry_keys(root)
    dirs, n, k = [], 0, start
    for group in groups(todo):
        for i in range(0, len(group), DRAFT_PAGES):
            d = out / f"312-draft-{k:04d}"
            items = []
            for url, text in group[i : i + DRAFT_PAGES]:
                n += 1
                items.append((f"p{n:05d}", url, text))
            write_bundle(d, items)
            (d / "CONTRACT.md").write_text(contract, encoding="utf-8")
            head = MANIFEST_HEAD.format(name=d.name, n=len(items))
            (d / "MANIFEST.md").write_text(DRAFT_HEAD.format(name=d.name, n=len(items)) + (d / "MANIFEST.md").read_text(encoding="utf-8")[len(head):], encoding="utf-8")
            with open(d / "MANIFEST.md", "a", encoding="utf-8") as fh:
                fh.write(f"## Keys already taken - choose none of these\n\n{' '.join(sorted(taken))}\n")
            dirs.append(d)
            k += 1
    return dirs


def entry_html(key: str, citation: str, what: str, why: str, marker: str) -> str:
    return (f'<h3 id="{key}"><code>{key}</code></h3>\n<p><!-- WRITTEN {today()} from the page as saved, by feature 312\'s '
            f'write-up pass; KEPT by source-filter -->{citation}</p>\n<p><em>What it is:</em> {what}</p>\n'
            f"<p><em>Why it applies, and its limits:</em> {why}</p>\n{marker}\n")


def install(root: pathlib.Path, d: pathlib.Path, reserve) -> dict[str, int]:  # noqa: ANN001 - reserve-prefix's `reserve`, a seam
    """A draft bundle's entries reserved and written into `040-uncited-works/`. A line is refused (and counted) when it
    names no known id, has an empty field, a key that is not one, or tags the vocabulary refuses; a key already taken gets
    `-2`, `-3`... The citation must carry the page's URL exactly."""
    ids = json.loads((d / "ids.json").read_text(encoding="utf-8"))
    st = sys.modules.get("_source_tags") or _load_source_tags()
    vocab = st.load_vocabulary(str(at.base(root) / at.RESEARCH))
    taken = registry_keys(root)
    done = written(root)
    kept_now = {x["url"] for x in at.read(root, KEPT)}
    counts = {"written": 0, "refused": 0, "already": 0, "dropped": 0}
    for raw in (d / "entries.jsonl").read_text(encoding="utf-8").splitlines() if (d / "entries.jsonl").is_file() else []:
        try:
            e = json.loads(raw)
            url = ids[e["id"]]
            key, cite, what, why = (str(e[f]).strip() for f in ("key", "citation", "what", "why"))
            what, why = _LABEL.sub("", what), _LABEL.sub("", why)
            marker = st.parse(f"<!-- tags: {e['tags']} -->", e["id"], vocab).marker()
        except (json.JSONDecodeError, KeyError, TypeError, AttributeError, st.SourceTagError) as err:
            print(f"uncited: {d.name}: refused - {err}: {raw[:120]}", file=sys.stderr)
            counts["refused"] += 1
            continue
        if not (_KEY.match(key) and cite and what and why and url in cite):
            print(f"uncited: {d.name}: refused {e.get('id')} - a bad key, an empty field, or a citation without its URL", file=sys.stderr)
            counts["refused"] += 1
            continue
        if src.norm(url) in done:  # a bundle installed twice writes nothing twice
            counts["already"] += 1
            continue
        if src.norm(url) not in kept_now:  # retired since its bundle was drafted (`dedupe`, a merge): nothing to write
            counts["dropped"] += 1
            continue
        base, n = key, 1
        while True:
            while key in taken:
                n += 1
                key = f"{base}-{n}"
            try:
                path = reserve("uncited", key, root, url=url)
                break
            except Exception as err:  # reserve-prefix's Refusal: a key another clone holds is taken too
                if "already" not in str(err):
                    raise
                taken.add(key)
        path.write_text(entry_html(key, cite, what, why, marker), encoding="utf-8")
        taken.add(key)
        done.add(src.norm(url))
        counts["written"] += 1
    return counts


USED_FOR_PLACEHOLDER = '<p><em>Used for:</em> TODO (<a href="contents.json#SECTION">the section it serves</a>)</p>\n'


def cite(root: pathlib.Path, key: str) -> pathlib.Path:
    """FR-014, plan D11: an uncited entry moved to the works cited when a footnote first cites it, keeping its number,
    with a `Used for:` line placed before its tags marker that the build refuses until it names a real section."""
    d = at.base(root) / at.UNCITED
    found = [f for f in (d.glob(f"*-{key}.html") if d.is_dir() else []) if re.fullmatch(rf"\d+-{re.escape(key)}\.html", f.name)]
    if not found:
        raise ValueError(f"no uncited entry for {key!r} in {at.UNCITED}")
    src_file = found[0]
    dest = at.base(root) / SOURCES / "010-works-cited" / src_file.name
    text = src_file.read_text(encoding="utf-8")
    i = text.rfind("<!-- tags:")
    text = (text[:i] + USED_FOR_PLACEHOLDER + text[i:]) if i >= 0 else text + USED_FOR_PLACEHOLDER
    dest.write_text(text, encoding="utf-8")
    src_file.unlink()
    return dest


def merge(root: pathlib.Path, key: str, into: str) -> pathlib.Path:
    """Two entries for one work (a redirect and its target, a script variant): `key`'s uncited entry is retired and its
    page moves from the kept list to the not-kept list as a duplicate of `into` - an uncited or a cited entry - which stays."""
    def entry(k: str, where: str) -> list[pathlib.Path]:
        return [f for f in (at.base(root) / SOURCES).glob(f"{where}/*-{k}.html") if re.fullmatch(rf"\d+-{re.escape(k)}\.html", f.name)]

    for k, where in ((key, at.UNCITED.name), (into, "*")):
        if not entry(k, where):
            raise ValueError(f"no {'uncited ' if where != '*' else ''}entry for {k!r} under {SOURCES}")
    gone = entry(key, at.UNCITED.name)[0]
    text = gone.read_text(encoding="utf-8")
    kept = at.read(root, KEPT)
    mine = [x for x in kept if x["raw"] in text]
    if not mine:
        raise ValueError(f"{key!r}: no kept page's URL appears in {gone.name}")
    path = at.base(root) / KEPT
    drop = {x["raw"] for x in mine}
    with src.locked(src.home(root), timeout=30.0):
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        path.write_text("".join(s for s in lines if not any(json.dumps(r, ensure_ascii=False) in s for r in drop)), encoding="utf-8")
    at.write(root, [line(x["raw"], ["duplicate"], "source-applicability", f"the same work as {into}") for x in mine], NOT_KEPT)
    gone.unlink()
    return gone


def entry_holding(root: pathlib.Path, raw: str) -> str | None:
    """The key of the uncited entry whose citation carries this URL, if one was written."""
    d = at.base(root) / at.UNCITED
    for f in sorted(d.glob("[0-9]*-*.html") if d.is_dir() else []):
        if raw in f.read_text(encoding="utf-8"):
            return f.stem.split("-", 1)[1]
    return None


def dedupe(root: pathlib.Path, dry: bool = False) -> list[str]:
    """Every duplicate `duplicate_works` finds retired: a written entry by `merge`, an unwritten kept page by moving its
    line to the not-kept list. What it duplicates stays (a cited entry, or the first kept page)."""
    done = []
    for raw, into in duplicate_works(root):
        into_key = into if not into.startswith("http") else (entry_holding(root, into) or into)
        key = entry_holding(root, raw)
        if dry:
            pass
        elif key:
            merge(root, key, into_key)
        else:
            path = at.base(root) / KEPT
            q = json.dumps(raw, ensure_ascii=False)
            with src.locked(src.home(root), timeout=30.0):
                lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
                path.write_text("".join(s for s in lines if q not in s), encoding="utf-8")
            at.write(root, [line(raw, ["duplicate"], "rule", f"the same work as {into_key}")], NOT_KEPT)
        done.append(f"{key or raw} -> {into_key}")
    return done


def report(root: pathlib.Path) -> str:
    nk = at.read(root, NOT_KEPT)
    reasons: dict[str, int] = {}
    for x in nk:
        for r in x["reasons"]:
            reasons[r] = reasons.get(r, 0) + 1
    left = uncited_set(root)
    where = src.home(root)
    readable = sum(1 for u in left if text_of(where, u) is not None)
    return (f"uncited: {len(left)} page(s) not yet judged ({readable} with saved text); {len(at.read(root, KEPT))} kept, "
            f"{len(nk)} not kept ({', '.join(f'{k} {v}' for k, v in sorted(reasons.items()))})")


def main(argv: list[str] | None = None) -> int:  # pragma: no cover - argument plumbing over the tested functions
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("set")
    s.add_argument("--write", default="")
    sub.add_parser("rule")
    f = sub.add_parser("fetch")
    f.add_argument("--limit", type=int, default=0)
    f.add_argument("--workers", type=int, default=4)
    b = sub.add_parser("bundle")
    b.add_argument("out")
    b.add_argument("--limit", type=int, default=0)
    b.add_argument("--start", type=int, default=1)
    a = sub.add_parser("apply")
    a.add_argument("dirs", nargs="+")
    c = sub.add_parser("score")
    c.add_argument("dir")
    c.add_argument("answers")
    sub.add_parser("report")
    vf = sub.add_parser("verify")
    vf.add_argument("--limit", type=int, default=0)
    vf.add_argument("--sample", type=int, default=0)
    vf.add_argument("--all-imported", action="store_true", help="every imported cache entry, cited ones too (R5)")
    vf.add_argument("--workers", type=int, default=3)
    dr = sub.add_parser("draft")
    dr.add_argument("out")
    dr.add_argument("--start", type=int, default=1)
    ct = sub.add_parser("cite")
    ct.add_argument("key")
    ins = sub.add_parser("install")
    ins.add_argument("dirs", nargs="+")
    mg = sub.add_parser("merge")
    mg.add_argument("key")
    mg.add_argument("into")
    sub.add_parser("dedupe").add_argument("--dry", action="store_true")
    args = ap.parse_args(argv)
    root = src.repo_root()
    if args.cmd == "set":
        urls = uncited_set(root)
        if args.write:
            pathlib.Path(args.write).write_text("\n".join(urls) + "\n", encoding="utf-8")
        print(f"uncited: {len(urls)} page(s) in the set")
    elif args.cmd == "rule":
        print(f"uncited: the rule - {json.dumps(rule(root, uncited_set(root)))}")
    elif args.cmd == "fetch":
        urls = [u for u in uncited_set(root) if not no_substance(u) and wellformed(u) and needs_fetch(src.home(root), u)]
        urls = urls[: args.limit] if args.limit else urls
        print(f"uncited: fetching {len(urls)} page(s) in up to {args.workers} lane(s)", flush=True)
        print(f"uncited: {json.dumps(fetch_all(root, urls, args.workers))}")
    elif args.cmd == "bundle":
        urls = uncited_set(root)
        urls = urls[: args.limit] if args.limit else urls
        dirs = bundle(root, urls, pathlib.Path(args.out), args.start)
        print(f"uncited: {len(dirs)} bundle(s) under {args.out}")
    elif args.cmd == "apply":
        for d in args.dirs:
            print(f"uncited: {d} - {json.dumps(apply(root, pathlib.Path(d)))}")
    elif args.cmd == "score":
        print(json.dumps(score(pathlib.Path(args.dir), json.loads(pathlib.Path(args.answers).read_text(encoding="utf-8")))))
    elif args.cmd == "verify":
        import random  # noqa: PLC0415

        judged_urls = [x["raw"] for x in at.read(root, KEPT)] + [x["raw"] for x in at.read(root, NOT_KEPT) if x.get("basis") == "source-filter"]
        done = {x["url"] for x in at.read(root, MISFILED)}
        pool_urls = imported_urls(src.home(root)) if args.all_imported else judged_urls
        todo = [u for u in dict.fromkeys(pool_urls) if src.norm(u) not in done and imported(src.home(root), u) is not None and wellformed(u)]
        if args.sample:
            random.seed(312)
            todo = random.sample(todo, min(args.sample, len(todo)))
        todo = todo[: args.limit] if args.limit else todo
        print(f"uncited: verifying {len(todo)} imported cop(ies) in up to {args.workers} lane(s)", flush=True)
        print(f"uncited: {json.dumps(verify_all(root, todo, args.workers))}")
    elif args.cmd == "draft":
        print(f"uncited: {len(dedupe(root))} duplicate(s) retired first; {len(draft_bundles(root, pathlib.Path(args.out), args.start))} draft bundle(s) under {args.out}")
    elif args.cmd == "cite":
        dest = cite(root, args.key)
        print(f"uncited: {args.key} moved to {dest.relative_to(root)} - write its Used for: line (the build refuses the placeholder), then `git add -A` the move")
    elif args.cmd == "dedupe":
        done = dedupe(root, args.dry)
        print("\n".join(f"uncited: duplicate retired - {d}" for d in done) + f"\nuncited: {len(done)} duplicate(s) retired")
    elif args.cmd == "merge":
        gone = merge(root, args.key, args.into)
        print(f"uncited: {args.key} retired ({gone.name}) as a duplicate of {args.into}; its page is on the not-kept list")
    elif args.cmd == "install":
        import importlib.util  # noqa: PLC0415

        spec = importlib.util.spec_from_file_location("reserve_prefix", HERE / "reserve-prefix.py")
        assert spec and spec.loader
        rp = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(rp)
        for d in args.dirs:
            print(f"uncited: {d} - {json.dumps(install(root, pathlib.Path(d), rp.reserve))}")
    else:
        print(report(root))
    return 0


if __name__ == "__main__":
    sys.exit(main())
