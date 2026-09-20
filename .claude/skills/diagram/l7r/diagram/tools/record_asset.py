"""Write (or check) the record's assembled pages from their per-entry fragments (feature 258).

`make record` writes every committed page of the record from the fragments under `research/<page>/`;
`CHECK=1` exits 1 when a committed page differs from its assembly, naming each one; `PAGE=<name>` does
one page; `SPLIT=<name>` performs the one-time split of a page that is still whole and refuses to leave
it behind unless it assembles back to the same bytes.

The shape is `make citations`' on purpose (`tools/citations_asset.py`): a derived, committed asset with
a `--check` mode. The pages are committed rather than built on the fly for the reason the glossary asset
is - a reader opens them from disk, and a browser will not fetch a sibling file from there.

Where this runs at the gate and at the push, and why both: `specs/258-*/contracts/record-cli.md`.
"""

from __future__ import annotations

import argparse
import sys

from l7r.diagram.interactive.record.store import RecordError, check, read_page, record_pages, write_fragments
from l7r.diagram.interactive.sources import RESEARCH_DIR


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="assemble the record's pages from their per-entry fragments")
    ap.add_argument("--check", action="store_true", help="exit 1 when a committed page differs from its assembly")
    ap.add_argument("--page", default="", help="one page: `ways`, `cities/defenses`, `sources`")
    ap.add_argument("--split", default="", help="the one-time split of a page that is still whole")
    ap.add_argument("--research-dir", default=RESEARCH_DIR, help=argparse.SUPPRESS)
    args = ap.parse_args(argv)
    try:
        if args.split:
            return _split(args.split, args.research_dir)
        if args.check:
            return _check(args.research_dir)
        return _write(args.page, args.research_dir)
    except RecordError as refusal:
        print(f"record: {refusal}", file=sys.stderr)
        return 1


def _split(name: str, research_dir: str) -> int:
    page_rel = _page_rel(name)
    written = write_fragments(page_rel, research_dir)
    print(f"record: split {page_rel} into {len(written)} fragment(s); it assembles back to the same bytes")
    return 0


def _check(research_dir: str) -> int:
    stale = check(research_dir)
    if stale:
        print("record: STALE - run `make record`:\n  " + "\n  ".join(stale), file=sys.stderr)
        return 1
    print(f"record: in sync ({len(record_pages(research_dir))} page(s))")
    return 0


def _write(page: str, research_dir: str) -> int:
    pages = [_page_rel(page)] if page else record_pages(research_dir)
    written = 0
    for page_rel in pages:
        want = read_page(page_rel, research_dir)
        path = f"{research_dir}/{page_rel}"
        if _read(path) == want:
            continue
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(want)
        written += 1
    print(f"record: wrote {written} page(s)")
    return 0


def _page_rel(name: str) -> str:
    """`ways` -> `ways.html`; `sources` -> `SOURCES.html`, which is the page that directory holds."""
    if name in ("sources", "SOURCES"):
        return "SOURCES.html"
    return name if name.endswith(".html") else f"{name}.html"


def _read(path: str) -> str | None:
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


if __name__ == "__main__":
    raise SystemExit(main())
