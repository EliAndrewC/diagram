#!/usr/bin/env python3
"""Save the full visible text of named pages, for `source-reader` to grep (feature 255, FR-006).

WHY. The fetch tool hands an agent a small model's EXTRACT of a page, never the page, and the one passage every
cheaper tier kept missing in feature 251 was found the first time the page itself was read (research R8). But a
whole page re-read every turn cost two to eight times the recorded runs, and a fetcher AGENT wandered. This is the
narrower form R8 pointed at: a script that saves the named pointers' text - no model, no wandering - so the reader
can `Grep` the saved pages for a claim's terms and `Read` only around the hits.

WHAT IT DOES. Each URL is fetched by `_quote_verbatim.Pages` - one attempt per host, a timeout, the charset honored,
a PDF not attempted - and its visible text is written to `<out>/<nn>-<host>.txt`, wrapped at sentence ends so a
grep hit is a line and not a page. `<out>/MANIFEST.txt` lists every pointer as `pointer | file | state`; a pointer
the script could not reach is listed with its state and why, and is the reader's to fetch. It judges nothing.
"""

from __future__ import annotations

import argparse
import importlib.util
import pathlib
import re
import sys
import urllib.parse

HERE = pathlib.Path(__file__).resolve().parent


def _qv():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("_quote_verbatim", HERE / "_quote_verbatim.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


qv = _qv()


def file_for(index: int, url: str) -> str:
    host = re.sub(r"[^a-z0-9.-]+", "-", urllib.parse.urlsplit(url).netloc.lower()).strip("-") or "page"
    return f"{index:02d}-{host}.txt"


def wrapped(text: str) -> str:
    """One sentence to a line (Latin and CJK stops), so `Grep` returns a passage and `Read` can page around it."""
    return re.sub(r"(?<=[.!?。！？])\s*(?=\S)", "\n", text).strip() + "\n"


def save(urls: list[str], out: pathlib.Path, pages) -> list[dict]:  # noqa: ANN001
    out.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    for index, url in enumerate(dict.fromkeys(urls), 1):
        got = pages.get(url)
        row = {"pointer": url, "file": "-", "state": got["state"], "why": got.get("why", "")}
        if got["state"] == "FETCHED":
            row["file"] = file_for(index, url)
            (out / row["file"]).write_text(wrapped(got["text"]), encoding="utf-8")
            row["why"] = f"{len(got['text'])} chars"
        rows.append(row)
    manifest = "".join(f"{r['pointer']} | {r['file']} | {r['state']}{' - ' + r['why'] if r['why'] else ''}\n" for r in rows)
    (out / "MANIFEST.txt").write_text("pointer | file | state\n" + manifest, encoding="utf-8")
    return rows


def main(argv: list[str] | None = None, pages=None) -> int:  # noqa: ANN001
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("out", help="the directory the pages and MANIFEST.txt are written to")
    ap.add_argument("urls", nargs="*", help="the pointers to save")
    args = ap.parse_args(argv)
    if not args.urls:
        print("source-pages: no pointer given - URL=<u1> [URL=<u2> ...]", file=sys.stderr)
        return 2
    out = pathlib.Path(args.out)
    rows = save(args.urls, out, pages or qv.Pages())
    print((out / "MANIFEST.txt").read_text(encoding="utf-8"), end="")
    print(f"  saved {sum(r['state'] == 'FETCHED' for r in rows)} of {len(rows)} to {out} - hand source-reader the manifest")
    return 0


if __name__ == "__main__":
    sys.exit(main())
