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
import json
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


PART = 20_000     # the most characters one saved file holds (D19): a longer page is saved as parts
LIMIT = 30_000    # a page longer than this, saved for a check that names its quotes, is saved as an EXCERPT (D19)
HEAD = 6_000      # an excerpt keeps the page's front: title, author, date, contents - what a source is judged by
WINDOW = 1_500    # and this much either side of each passage the record quotes from it


def parts(text: str, size: int = PART) -> list[str]:
    """`text` cut at line ends into pieces of at most `size` characters (a single longer line is cut where it must).

    WHY (feature 250 D19, research R10): one source was a whole book, and the checks that read its saved page read
    200,026 and 83,621 characters of it. A grep hit now leads to one part, never to the book."""
    out: list[str] = []
    cur = ""
    for line in text.splitlines(keepends=True):
        while len(line) > size:
            if cur:
                out.append(cur)
                cur = ""
            out.append(line[:size])
            line = line[size:]
        if len(cur) + len(line) > size:
            out.append(cur)
            cur = ""
        cur += line
    return [*out, cur] if cur else out


def excerpt(text: str, quotes: list[str], head: int = HEAD, window: int = WINDOW, limit: int = LIMIT) -> str:
    """A long page cut to its front and a window around each quoted passage found in it; a short page whole.

    WHY (D19): `source-applicability` judges what a source IS - its front matter - and how the record USES it - the
    passages it quotes - and on R10's book it read 200,026 characters of the whole to do so, 0.73 million tokens.
    What is left out is said, with its size, so an agent never takes the excerpt for the whole."""
    flat = " ".join(text.split())
    if len(flat) <= limit:
        return text
    spans = [(0, min(head, len(flat)))]
    for q in quotes:
        words = " ".join(q.split())
        # the passage's start, else a stretch from its middle - a quote's first words are where an ellipsis, a
        # reference marker or a line break most often sits between the record's copy and the page
        probes = [words[:40], words[len(words) // 2 - 15 : len(words) // 2 + 15], words[-30:]]
        at = next((flat.find(pr) for pr in probes if len(pr) >= 12 and flat.find(pr) >= 0), -1)
        if at >= 0:
            spans.append((max(0, at - window), min(len(flat), at + len(q) + window)))
    spans.sort()
    merged: list[list[int]] = []
    for a, b in spans:
        if merged and a <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    found = len(spans) - 1
    pieces, last = [], 0
    for a, b in merged:
        if a > last:
            pieces.append(f"\n[... {a - last:,} characters not copied ...]\n")
        pieces.append(wrapped(flat[a:b]))
        last = b
    if last < len(flat):
        pieces.append(f"\n[... {len(flat) - last:,} characters not copied ...]\n")
    note = f"[EXCERPT of a {len(flat):,}-character page: its first {head:,} characters and {window:,} either side of the {found} of {len(quotes)} quoted passage(s) found in it]\n"
    return note + "".join(pieces)


def saved_rows(out: pathlib.Path) -> list[dict]:
    """The rows an earlier save into `out` listed - kept, so a second save ADDS to the directory.

    WHY (feature 250 D15): a write session saved a second batch into the same directory and its files, numbered
    from 01 again, overwrote the first batch's; it re-saved everything, a turn and a fetch per page for nothing."""
    manifest = out / "MANIFEST.txt"
    if not manifest.is_file():
        return []
    rows = []
    for line in manifest.read_text(encoding="utf-8").splitlines()[1:]:
        pointer, file, state = (line.split(" | ", 2) + ["", ""])[:3]
        state, _, why = state.partition(" - ")
        rows.append({"pointer": pointer, "file": file, "state": state, "why": why})
    return rows


def save(urls: list[str], out: pathlib.Path, pages, quotes: list[str] | None = None) -> list[dict]:  # noqa: ANN001
    out.mkdir(parents=True, exist_ok=True)
    rows = saved_rows(out)
    # past every earlier file, so a new page never takes an old one's number. WHY the highest number and not the
    # row count (feature 271 V4): a retried failure's old row is dropped below, so after a retry the count fell
    # behind the numbers in use and a third save wrote over a page the second had saved.
    start = max([len(rows)] + [int(r["file"][:2]) for r in rows if r["file"][:2].isdigit()]) + 1
    have = {r["pointer"] for r in rows if r["state"] == "FETCHED"}
    rows = [r for r in rows if r["pointer"] in have or r["pointer"] not in urls]
    for index, url in enumerate((u for u in dict.fromkeys(urls) if u not in have), start):
        got = pages.get(url)
        row = {"pointer": url, "file": "-", "state": got["state"], "why": got.get("why", "")}
        if got["state"] == "FETCHED":
            name = file_for(index, url)
            text = wrapped(got["text"]) if quotes is None else excerpt(wrapped(got["text"]), quotes)
            pieces = parts(text)
            if len(pieces) == 1:
                (out / name).write_text(pieces[0], encoding="utf-8")
                row["file"] = name
            else:
                for k, piece in enumerate(pieces, 1):
                    (out / f"{name[:-4]}.p{k}.txt").write_text(piece, encoding="utf-8")
                row["file"] = f"{name[:-4]}.p1.txt ... .p{len(pieces)}.txt ({len(pieces)} parts - grep them all, read the part a hit is in)"
            row["why"] = f"{len(got['text'])} chars" + ("" if quotes is None or len(text) >= len(got["text"]) else f", saved as an excerpt of {len(text):,}")
        rows.append(row)
    manifest = "".join(f"{r['pointer']} | {r['file']} | {r['state']}{' - ' + r['why'] if r['why'] else ''}\n" for r in rows)
    (out / "MANIFEST.txt").write_text("pointer | file | state\n" + manifest, encoding="utf-8")
    return rows


def main(argv: list[str] | None = None, pages=None) -> int:  # noqa: ANN001
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("out", help="the directory the pages and MANIFEST.txt are written to")
    ap.add_argument("urls", nargs="*", help="the pointers to save")
    ap.add_argument("--quotes", default="", help="a JSON list of the passages the record quotes from these pages: a long page is saved as an excerpt around them (D19)")
    args = ap.parse_args(argv)
    if not args.urls:
        print("source-pages: no pointer given - URL=<u1> [URL=<u2> ...]", file=sys.stderr)
        return 2
    out = pathlib.Path(args.out)
    quotes = json.loads(pathlib.Path(args.quotes).read_text(encoding="utf-8")) if args.quotes else None
    rows = save(args.urls, out, pages or qv.Pages(), quotes)
    print((out / "MANIFEST.txt").read_text(encoding="utf-8"), end="")
    print(f"  saved {sum(r['state'] == 'FETCHED' for r in rows)} of {len(rows)} to {out} - hand source-reader the manifest")
    return 0


if __name__ == "__main__":
    sys.exit(main())
