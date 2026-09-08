"""Write (or check) what the record's citations pages derive (feature 211, GM 2026-09-07).

`make citations` writes, for every research page, the derived script `research/citations/<name>.js` its hover
reads, and the works section between the markers at the top of `research/citations/<name>.html`, from the notes
on that page and the write-ups in `SOURCES.html`; `--check` exits 1 when a committed script or works section
differs from its derivation, or when a cited key has no write-up - which is what `tests/interactive/test_citations.py`
holds at the gate. Derived files are committed rather than built on the fly because the record's pages are static,
hand-authored HTML a reader opens from disk (the glossary asset's reason, feature 209).
"""

from __future__ import annotations

import argparse
import os
import sys

from l7r.diagram.interactive.citations import citations_page, derive, research_pages, script_path
from l7r.diagram.interactive.sources import RESEARCH_DIR


def _read(path: str) -> str | None:
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="write research/citations/<name>.js and each citations page's works section")
    ap.add_argument("--check", action="store_true", help="exit 1 when a committed derivation differs, or a cited key has no write-up")
    ap.add_argument("--research-dir", default=RESEARCH_DIR, help=argparse.SUPPRESS)
    args = ap.parse_args(argv)
    stale: list[str] = []
    missing: dict[str, list[str]] = {}
    written = 0
    for page in research_pages(args.research_dir):
        cpath = os.path.join(args.research_dir, citations_page(page))
        if _read(cpath) is None:
            stale.append(f"{citations_page(page)}: no citations page")
            continue
        js, html, lacking = derive(page, args.research_dir)
        if lacking:
            missing[page] = lacking
        spath = os.path.join(args.research_dir, script_path(page))
        for path, want in ((spath, js), (cpath, html)):
            if _read(path) == want:
                continue
            if args.check:
                stale.append(os.path.relpath(path, args.research_dir))
            else:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(want)
                written += 1
    for page, keys in missing.items():
        print(f"{page}: cited keys with no write-up in SOURCES.html ({WHAT} / {WHY}): {', '.join(keys)}", file=sys.stderr)
    if args.check:
        if stale:
            print("citations: STALE - run `make citations`:\n  " + "\n  ".join(stale), file=sys.stderr)
        elif not missing:
            print("citations: in sync")
        return 1 if stale or missing else 0
    print(f"citations: wrote {written} file(s)")
    return 1 if missing else 0


WHAT = "What it is:"
WHY = "Why it applies, and its limits:"

if __name__ == "__main__":
    raise SystemExit(main())
