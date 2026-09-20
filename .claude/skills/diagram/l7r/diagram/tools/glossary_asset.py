"""Write (or check) the research record's derived glossary asset (feature 209, GM 2026-09-07).

`make glossary` writes `research/assets/glossary.js` from `interactive/glossary.py`, the ONE glossary the map's
modals and the record's pages share; `--check` exits 1 when the committed file differs from the derivation,
which is what `tests/interactive/test_record_format.py` holds at the gate. A derived file is committed rather
than built on the fly because the record's pages are static, hand-authored HTML that a reader opens from disk.
"""

from __future__ import annotations

import argparse
import importlib
import os
import sys

from l7r.diagram.interactive import glossary
from l7r.diagram.interactive import glossary_source as source
from l7r.diagram.interactive.sources import RESEARCH_DIR

ASSET = os.path.join(RESEARCH_DIR, "assets", "glossary.js")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="assemble interactive/assets/glossary.json, then write research/assets/glossary.js")
    ap.add_argument("--check", action="store_true", help="exit 1 when either committed file differs from its source")
    ap.add_argument("--split", action="store_true", help="the one-time split of glossary.json into per-term files")
    ap.add_argument("--path", default=ASSET, help=argparse.SUPPRESS)
    args = ap.parse_args(argv)
    if args.split:
        written = source.write_term_files()
        print(f"glossary: split into {len(written)} term file(s); they assemble back to the same bytes")
        return 0

    # THE SOURCE IS ASSEMBLED FIRST, AND THE ASSET IS DERIVED FROM IT (feature 259). The order is not
    # a preference: `interactive/glossary.py` builds its GLOSSARY at import from `glossary.json`, so a
    # derivation taken before the assembly would be of the file as it stood one edit ago.
    stale = source.check()
    if args.check and stale:
        print(f"glossary.json: STALE against its per-term files - run `make glossary` ({', '.join(stale)})",
              file=sys.stderr)
        return 1
    if not args.check:
        if source.write_source():
            importlib.reload(glossary)
        source.write_index()

    want = glossary.record_glossary_js()
    try:
        with open(args.path, encoding="utf-8") as fh:
            have: str | None = fh.read()
    except OSError:
        have = None
    if args.check:
        if have == want:
            print(f"glossary: in sync ({len(glossary.GLOSSARY)} terms, json and js)")
            return 0
        print(f"glossary.js: STALE against interactive/glossary.py - run `make glossary` ({args.path})", file=sys.stderr)
        return 1
    with open(args.path, "w", encoding="utf-8") as fh:
        fh.write(want)
    print(f"wrote {args.path} ({len(glossary.GLOSSARY)} terms)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
