"""Write (or check) the research record's derived glossary asset (feature 209, GM 2026-09-07).

`make glossary` writes `research/assets/glossary.js` from `interactive/glossary.py`, the ONE glossary the map's
modals and the record's pages share; `--check` exits 1 when the committed file differs from the derivation,
which is what `tests/interactive/test_record_format.py` holds at the gate. A derived file is committed rather
than built on the fly because the record's pages are static, hand-authored HTML that a reader opens from disk.
"""

from __future__ import annotations

import argparse
import os
import sys

from l7r.diagram.interactive.glossary import GLOSSARY, record_glossary_js
from l7r.diagram.interactive.sources import RESEARCH_DIR

ASSET = os.path.join(RESEARCH_DIR, "assets", "glossary.js")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="write research/assets/glossary.js from interactive/glossary.py")
    ap.add_argument("--check", action="store_true", help="exit 1 when the committed asset differs from the derivation")
    ap.add_argument("--path", default=ASSET, help=argparse.SUPPRESS)
    args = ap.parse_args(argv)
    want = record_glossary_js()
    try:
        with open(args.path, encoding="utf-8") as fh:
            have: str | None = fh.read()
    except OSError:
        have = None
    if args.check:
        if have == want:
            print(f"glossary.js: in sync ({len(GLOSSARY)} terms)")
            return 0
        print(f"glossary.js: STALE against interactive/glossary.py - run `make glossary` ({args.path})", file=sys.stderr)
        return 1
    with open(args.path, "w", encoding="utf-8") as fh:
        fh.write(want)
    print(f"wrote {args.path} ({len(GLOSSARY)} terms)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
