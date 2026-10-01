"""Build (or check) the record's site from its per-entry fragments (features 258 and 301).

`make record` writes the site under `research/site/` (`record/site.py`): a page per question and per registry entry,
a page per part, the home page and the single page. Nothing it writes is committed (feature 301, GM 2026-10-01:
*"we should definitely stop checking the assembled files into source control"*); render-sync builds it on the main
checkout. `CHECK=1` builds the whole site in memory and writes nothing: it exits 1 when the record does not build
cleanly - a link that lands nowhere, an id used twice, a note nothing cites, a cited work with no write-up - naming
each one (spec FR-011). `SPLIT=<name>` performs the one-time split of a page that is still whole and refuses to leave
it behind unless it assembles back to the same bytes.

Where this runs at the gate and at the push, and why both: `specs/258-*/contracts/record-cli.md`; the build in main:
`pipeline/render_cache.py`.
"""

from __future__ import annotations

import argparse
import os
import sys

from l7r.diagram.interactive.record import site
from l7r.diagram.interactive.record.store import RecordError, split_originals, write_fragments
from l7r.diagram.interactive.sources import RESEARCH_DIR


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="build the record's site from its per-entry fragments")
    ap.add_argument("--check", action="store_true", help="build in memory and exit 1 on any refusal; writes nothing")
    ap.add_argument("--split", default="", help="the one-time split of a page that is still whole")
    ap.add_argument("--research-dir", default=RESEARCH_DIR, help=argparse.SUPPRESS)
    ap.add_argument("--out", default="", help=argparse.SUPPRESS)
    args = ap.parse_args(argv)
    try:
        if args.split:
            return _split(args.split, args.research_dir)
        return _build(args.research_dir, args.out or os.path.join(args.research_dir, site.SITE), check=args.check)
    except RecordError as refusal:
        print(f"record: {refusal}", file=sys.stderr)
        return 1


def _split(name: str, research_dir: str) -> int:
    page_rel = _page_rel(name)
    written = write_fragments(page_rel, research_dir)
    print(f"record: split {page_rel} into {len(written)} fragment(s); it assembles back to the same bytes")
    return 0


def _build(research_dir: str, out: str, *, check: bool) -> int:
    inline = split_originals(research_dir, write=not check)
    if check and inline:
        print("record: an original is still inline - `make record` moves it:\n  " + "\n  ".join(inline), file=sys.stderr)
        return 1
    if inline:
        print(f"record: moved the originals of {len(inline)} notes file(s) into their .originals.html (feature 292)")
    files = site.build(research_dir)
    pages = sum(1 for f in files if f.endswith(".html"))
    if check:
        print(f"record: builds cleanly ({pages} page(s))")
        return 0
    site.write(files, out)
    print(f"record: wrote the site, {pages} page(s), to {os.path.relpath(out)}/ - open {os.path.relpath(os.path.join(out, 'index.html'))}")
    return 0


def _page_rel(name: str) -> str:
    """`ways` -> `ways.html`; `sources` -> `SOURCES.html`, which is the page that directory holds."""
    if name in ("sources", "SOURCES"):
        return "SOURCES.html"
    return name if name.endswith(".html") else f"{name}.html"


if __name__ == "__main__":
    raise SystemExit(main())
