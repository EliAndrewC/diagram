"""`scripts/record/uncited_imports.py` - the page cache's imported copies, read live and checked (feature 312, research.md R5).

Split from `uncited.py` at the 1,000-line bar (2026-10-02): `verify` reads each imported copy live and records whether it
was this page, another page's text, or could not be told; `copy_verdicts` lists the filter verdicts that blamed a saved
copy on a page now read live, to read and then requeue or mark `stands`. Run through `make uncited DO=verify|copy-verdicts|stands`.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import archive as ar  # noqa: E402
import attempts as at  # noqa: E402
import sources as src  # noqa: E402
from uncited import EMPTY, NOT_KEPT, text_of, today  # noqa: E402

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


def garbled(text: str) -> bool:
    """Text decoded in the wrong charset: more than 1% replacement characters (U+FFFD)."""
    return len(text) >= EMPTY and text.count("�") > len(text) / 100


_CJK = re.compile(r"[぀-ヿ㐀-鿿]")


def worse_read(old: str, live: str) -> bool:
    """A live read that is less than the copy it would replace: under half its length (Adachi's page came back as a
    machine-translation notice), or a Chinese or Japanese page come back mostly in Latin script (Osaka Info's English
    edition) - observed 2026-10-02."""
    def cjk(t: str) -> float:
        return len(_CJK.findall(t)) / max(len(t), 1)

    return len(live) * 2 < len(old) or (cjk(old) > 0.2 and cjk(live) < cjk(old) / 4)


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
        live = "" if garbled(live) or worse_read(old, live) else live  # a mis-decoded, cut or translated read never replaces a copy (2026-10-02)
        result = "unread" if len(live) < EMPTY else ("same" if same_page(old, live) else "misfiled")
        if result == "misfiled":  # kept beside the live text: the 4-gram measure flags a skin change as readily as another page (R5), so a flag is confirmed by reading before `requeue`
            d = src.entry_dir(where, u)
            d.mkdir(parents=True, exist_ok=True)
            (d / "imported.txt").write_text(old, encoding="utf-8")
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


#: A not-kept note that blames the saved copy rather than the page (2026-10-02: two blogs ruled unreadable from mojibake
#: imports and a village page ruled no-substance from a title-only shell, each readable live).
COPY_FAULT = re.compile(r"mojibake|saved text|saved copy|title only|shell|encod|garbage|garbled|JavaScript|captcha|challenge|truncat", re.I)


def copy_verdicts(root: pathlib.Path) -> list[str]:
    """Pages to read and, if the page is readable, `requeue`: a filter verdict whose note blames the saved copy, on a page
    the import check has since read live into the cache readable (1,500 characters or more, not garbled)."""
    nk = {x["url"]: x for x in at.read(root, NOT_KEPT) if x.get("basis") == "source-filter"}
    rows = at.read(root, MISFILED)
    stood = {x["url"] for x in rows if x["result"] == "verdict-stands"}
    where, out = src.home(root), []
    for x in rows:
        v = None if x["url"] in stood else nk.get(x["url"])
        if not (v and x["result"] in ("same", "misfiled") and COPY_FAULT.search(v.get("note", ""))):
            continue
        text = text_of(where, x["raw"]) or ""
        if len(text) >= 1500 and not garbled(text):
            out.append(f"{x['raw']}  ({', '.join(v['reasons'])}: {v.get('note', '')[:90]})")
    return out


def stands(root: pathlib.Path, raw: str, note: str) -> None:
    """A page `copy_verdicts` listed, read, and its verdict found sound (the live page is as the verdict says): it leaves the list."""
    at.write(root, [{"url": src.norm(raw), "raw": raw, "result": "verdict-stands", "note": note, "date": today()}], MISFILED)
