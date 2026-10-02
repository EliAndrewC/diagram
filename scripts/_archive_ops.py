#!/usr/bin/env python3
"""The source archive's housekeeping and lookups (feature 309, Amendment 1) - beside `_archive.py`, which captures.

THE INBOX (FR-013; the GM, 2026-10-02: use the download directory *"as a queue of sorts ... once something has been
added to the diagram research repository and then pushed, then we can delete it from the academic sources directory"*).
Every file or saved-page folder in `/host-l7r-repo/academic-sources/` but the GM's two lists is copied to
`gm-copies/<name>` of the archive once its keys are known (a new download waits until the session matches it: MATCH= or
NONE=), the push is CONFIRMED on GitHub (the path is in `origin/main`'s tree), and only then
is it deleted from the inbox. `research/archive/gm-copies.json` keeps each processed file's name, keys and archive path,
so a copy is still found after its file is gone; a file that copies no cited source is archived all the same (*"store
sources which we ourselves do not end up citing"*), its keys `[]`.

EVERY PAGE READ (FR-014). `make source-pages` archives what it reads (`_source_pages.py`); `consulted` archives every
URL on the sources-consulted ledger with no row yet - a whole live capture where the page answers, else the page cache's
saved text (`partial`), else `unreachable` (the GM chose every page read, the earlier ~4,900 included).

THE LOOKUP (FR-015, FR-016; the GM: *"first check to see if we already have something, rather than going out and trying
to find it on the internet"*): `find` answers by URL, key or words in the archived text, naming each copy's local path.

THE RELAYOUT (one time): the first ~1,700 captures were filed `<key>/<id>/`, `notes/<id>/` and `<key>/gm-copy/<name>`;
the GM asked for a layout that stays browsable past 5,000 (2026-10-02), so they move to `<id[:2]>/<id>/` and
`gm-copies/<name>` (git renames), and the manifest's rows to `research/archive/<id[:2]>/<id>.json`.

    _archive_ops.py inbox                 `make archive-inbox`
    _archive_ops.py consulted [--limit N] `make archive-sources CONSULTED=1`
    _archive_ops.py find [--url U] [--key K] [--terms "a|b"]   `make archive-find`
    _archive_ops.py relayout              one time
    _archive_ops.py urls <u> ...          the pages just read, archived where they have no row (`make source-pages`,
                                          `make source-outcome` call it)
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import _archive as ar  # noqa: E402

rec, src = ar.rec, ar.src
#: The GM's own notes in the inbox, never processed: they are lists of what to fetch, not sources.
GM_LISTS = ("TO-DOWNLOAD.md", "for-the-gm-fetch-list.md")


def write_table(root: pathlib.Path, table: dict[str, dict]) -> None:
    path = root / ar.MANIFEST / rec.GM_COPIES
    doc = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {"_about": "Feature 309: the GM's downloaded files."}
    doc["files"] = {k: table[k] for k in sorted(table)}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def on_github(store: ar.Archive, rel: str) -> bool:
    """Whether `rel` is in the tree of `origin/main` as this copy last pushed or fetched it."""
    done = store.git("ls-tree", "--name-only", "origin/main", "--", rel, check=False)
    return done.returncode == 0 and bool(done.stdout.strip())


def process_inbox(root: pathlib.Path, store: ar.Archive, inbox: pathlib.Path | None = None, match: dict[str, list[str]] | None = None) -> tuple[dict[str, str], list[str]]:
    """Archive every inbox entry the table places, confirm the push, then delete it (FR-013). Returns (name -> its archive
    path, the names left waiting). An entry is deleted only where its path is confirmed in `origin/main`, so a failed push
    deletes nothing. A NEW entry - not in `gm-copies.json` - is processed only once `match` gives its keys (`[]` for one
    judged to copy no cited source, `make archive-inbox NONE=<file>`): FR-012 matches every GM file to its key, and a file
    archived keyless and deleted would never be matched (plan review, Amendment 1). Until then it waits in the inbox."""
    inbox = inbox or ar.GM_DIR
    table = ar.gm_table(root)
    for name, keys in (match or {}).items():
        table.setdefault(name, {"evidence": "matched by the session at the inbox (feature 309 FR-012)"})["keys"] = keys
    names = [n for n in sorted(os.listdir(inbox)) if n not in GM_LISTS and not n.startswith(".")] if inbox.is_dir() else []
    placed: dict[str, str] = {}
    waiting = [n for n in names if n not in table]
    names = [n for n in names if n in table]
    if not names:
        return placed, waiting
    with store.locked():
        store.ensure()
        for name in names:
            entry = table[name]
            dest = ar.place_gm(store, name, entry)
            if dest:
                entry["archived"] = dest
                placed[name] = dest
        failure = store.push()
    write_table(root, table)
    if failure:
        raise RuntimeError(f"the inbox is archived locally but the push failed, so nothing was deleted: {failure}")
    for name, dest in placed.items():
        if on_github(store, dest):
            target = inbox / name
            shutil.rmtree(target) if target.is_dir() else target.unlink()
    return placed, waiting


def consulted_urls(root: pathlib.Path) -> list[str]:
    """Every URL a session has read (the sources-consulted ledger, the page cache's own URLs first) with no row yet."""
    home = src.home(root)
    have = {json.loads(p.read_text(encoding="utf-8"))["url"] for p in ar.row_files(root)}
    seen_norm = {src.norm(u) for u in have}
    urls: dict[str, str] = {}
    for meta in sorted((home / src.CACHE).glob("*/*/meta.json")):
        with open(meta, encoding="utf-8") as fh:
            url = json.load(fh).get("url", "")
        if url.startswith("http"):
            urls.setdefault(src.norm(url), rec.clean(url))
    for row in src.read(home):
        n = row.get("url", "")
        if n:
            urls.setdefault(n, "https://" + n)
    return sorted(u for n, u in urls.items() if n not in seen_norm)


def consulted(root: pathlib.Path, limit: int = 0) -> int:  # pragma: no cover - the live run; `consulted_urls` and `archive_url` are tested
    todo = consulted_urls(root)
    todo = todo[:limit] if limit else todo
    print(f"archive: {len(todo)} consulted URL(s) with no copy yet", flush=True)
    store = ar.Archive(ar.home_of(root), env=ar.git_env(ar.token(root)))
    browser = ar.Browser()
    try:
        for n, url in enumerate(todo, 1):
            if n % ar.RECYCLE_EVERY == 0:
                browser.close()
                browser = ar.Browser()
            row = ar.archive_url(root, url, rec.Cited(), browser, store, push=False)
            print(f"{row['outcome']:26} {url}", flush=True)
            if store.unpushed() >= ar.PUSH_EVERY:
                with store.locked():
                    store.push()
    finally:
        browser.close()
    with store.locked():
        failure = store.push()
    ar.settle(root)
    return 1 if failure else 0


def unarchived(root: pathlib.Path, urls: list[str]) -> list[str]:
    """The URLs, cleaned, that have no archive row yet - a page read again is not captured again (FR-014)."""
    have = {src.norm(json.loads(p.read_text(encoding="utf-8"))["url"]) for p in ar.row_files(root)}
    out = []
    for url in (rec.clean(u) for u in urls):
        if url.startswith("http") and src.norm(url) not in have and url not in out:
            out.append(url)
    return out


def archive_urls(root: pathlib.Path, urls: list[str]) -> int:  # pragma: no cover - the live path the ledger's writers take; `unarchived` and `archive_url` are tested
    """Archive the pages just read that have no row (FR-014): one browser, one push."""
    todo = unarchived(root, urls)
    if not todo:
        return 0
    who = rec.cited(str(root / ar.MANIFEST.parent))
    store = ar.Archive(ar.home_of(root), env=ar.git_env(ar.token(root)))
    browser = ar.Browser()
    try:
        for url in todo:
            row = ar.archive_url(root, url, who.get(url, rec.Cited()), browser, store)
            print(f"archive: {row['outcome']} - {url}", file=sys.stderr)
    finally:
        browser.close()
    return 0


def find(root: pathlib.Path, store: ar.Archive, url: str = "", key: str = "", terms: str = "", out=sys.stdout) -> int:  # noqa: ANN001
    """What the archive already holds (FR-015): rows by URL or key, and archived texts holding every term; each with its
    local path. Exit 0 with hits, 1 with none - so a session knows to go to the web."""
    hits = 0
    rows = [json.loads(p.read_text(encoding="utf-8")) for p in ar.row_files(root)]
    want = src.norm(url) if url else ""
    for row in rows:
        if (want and src.norm(row["url"]) == want) or (key and key in row.get("keys", [])):
            hits += 1
            local = store.dir / row["path"] if row.get("path") else None
            print(f"{row['outcome']:26} {row['url']}\n  local: {local or '(no copy)'}\n  keys: {', '.join(row.get('keys', [])) or '-'}", file=out)
            for gm in row.get("gm_copies", []):
                print(f"  the GM's copy: {store.dir / gm}", file=out)
    if key:
        for name, entry in sorted(ar.gm_table(root).items()):
            if key in entry.get("keys", []) and entry.get("archived"):
                hits += 1
                print(f"the GM's copy of {key}: {store.dir / entry['archived']}", file=out)
    words = [t.strip() for t in terms.split("|") if t.strip()]
    if words and store.dir.is_dir():
        found = None
        for word in words:
            done = subprocess.run(["grep", "-rlIiF", "--include=text.txt", "--include=*.pdf.txt", "--include=*.txt", "--", word, str(store.dir)], capture_output=True, text=True, check=False)
            files = {f for f in done.stdout.splitlines() if "/.git/" not in f}
            found = files if found is None else found & files
        by_dir = {str(pathlib.Path(f).parent): f for f in sorted(found or ())}
        url_of = {str(store.dir / r["path"]): r["url"] for r in rows if r.get("path")}
        for d, f in sorted(by_dir.items()):
            hits += 1
            print(f"text holds {' + '.join(words)}: {f}" + (f"\n  url: {url_of[d]}" if d in url_of else ""), file=out)
    if not hits:
        print("archive: nothing held - search the web (and archive what you read: `make source-pages` does)", file=out)
    return 0 if hits else 1


def relayout(root: pathlib.Path, store: ar.Archive) -> int:
    """Move the first captures to the sharded layout (git renames), and the manifest's rows with them. Returns rows moved."""
    moved = 0
    with store.locked():
        store.ensure()
        table = ar.gm_table(root)
        renames: dict[str, str] = {}
        for name, entry in table.items():
            for key in entry.get("keys", []):
                old = f"{key}/gm-copy/{name}"
                if (store.dir / old).exists():
                    renames[old] = f"{ar.GM_DEST}/{name}"
            entry.pop("archived", None)
        flat = sorted((root / ar.MANIFEST).glob("[0-9a-f]*.json"))
        for path in flat:
            row = json.loads(path.read_text(encoding="utf-8"))
            base = ar.capture_base(row["url"])
            for field in ("path", "first"):
                old = row.get(field, "")
                if old and not old.startswith(base + "/"):
                    renames.setdefault(os.path.dirname(old), base)
                    row[field] = f"{base}/{os.path.basename(old)}"
            row["gm_copies"] = sorted({renames.get(g, g) for g in row.get("gm_copies", [])})
            ar.write_row(root, row["url"], row)
            path.unlink()
            moved += 1
        for old, new in sorted(renames.items()):
            if (store.dir / old).exists() and old != new:
                if new.endswith("/" + os.path.basename(old)) or new.startswith(ar.GM_DEST + "/"):
                    (store.dir / new).parent.mkdir(parents=True, exist_ok=True)
                    store.git("mv", "-k", old, new)
                else:
                    (store.dir / new).mkdir(parents=True, exist_ok=True)
                    for child in sorted((store.dir / old).iterdir()):
                        store.git("mv", "-k", str(child.relative_to(store.dir)), f"{new}/{child.name}")
        for old in sorted({o.split("/")[0] for o in renames}):
            for d in sorted((p for p in (store.dir / old).rglob("*") if p.is_dir()), key=lambda p: -len(p.parts)) if (store.dir / old).is_dir() else []:
                if not any(d.iterdir()):
                    d.rmdir()
            if (store.dir / old).is_dir() and not any((store.dir / old).iterdir()):
                (store.dir / old).rmdir()
        for name, entry in table.items():
            if (store.dir / ar.GM_DEST / name).exists():
                entry["archived"] = f"{ar.GM_DEST}/{name}"
        store.git("commit", "-q", "-m", "relayout: captures sharded by the URL id's first two hex digits, the GM's copies under gm-copies/", check=False)
        failure = store.push()
    write_table(root, table)
    if failure:
        raise RuntimeError(f"relayout committed but not pushed: {failure}")
    return moved


def main(argv: list[str] | None = None) -> int:  # pragma: no cover - argument plumbing over the tested functions
    ap = argparse.ArgumentParser(description="the source archive's housekeeping and lookups (feature 309)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("inbox")
    i.add_argument("--match", action="append", default=[], help="<file>=<key>[,<key>] - a new download's keys")
    i.add_argument("--none", action="append", default=[], help="<file> - a new download that copies no cited source")
    c = sub.add_parser("consulted")
    c.add_argument("--limit", type=int, default=0)
    f = sub.add_parser("find")
    f.add_argument("--url", default="")
    f.add_argument("--key", default="")
    f.add_argument("--terms", default="")
    sub.add_parser("relayout")
    u = sub.add_parser("urls")
    u.add_argument("urls", nargs="+")
    args = ap.parse_args(argv)
    root = src.repo_root()
    if args.cmd == "urls":
        return archive_urls(root, args.urls)
    store = ar.Archive(ar.home_of(root), env=ar.git_env(ar.token(root)))
    if args.cmd == "find":
        return find(root, store, args.url, args.key, args.terms)
    if args.cmd == "consulted":
        return consulted(root, args.limit)
    if args.cmd == "relayout":
        print(f"archive: {relayout(root, store)} row(s) moved to the sharded layout")
        return 0
    match = {m.split("=", 1)[0]: [k for k in m.split("=", 1)[1].split(",") if k] for m in args.match if "=" in m}
    match.update({n: [] for n in args.none})
    placed, waiting = process_inbox(root, store, match=match)
    print(f"archive: {len(placed)} inbox file(s) archived, pushed and removed from {ar.GM_DIR}")
    for name, dest in placed.items():
        print(f"  {name} -> {dest}")
    for name in waiting:
        print(f"  WAITING {name}: a new download - read its first page, find the source it copies, then `make archive-inbox MATCH='{name}=<key>'` (or NONE='{name}' if it copies no cited source)")
    ar.sync_gm_copies(root, store)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
