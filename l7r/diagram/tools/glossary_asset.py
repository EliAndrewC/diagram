"""Assemble (or check) the glossary from its per-term files (features 209, 259 and 301).

`make glossary` assembles `interactive/assets/glossary.json` - the ONE glossary the map's modals and the record share -
from its per-term files; `--check` exits 1 when the committed JSON differs from them. The record's copy, the script
`glossary.js`, is DERIVED from it into the site by `make record` (feature 301: built, never committed), so there is no
committed script to check; `--path` writes the script somewhere on request.
"""

from __future__ import annotations

import argparse
import importlib
import sys

from l7r.diagram.interactive import glossary
from l7r.diagram.interactive import glossary_source as source


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="assemble interactive/assets/glossary.json, then write research/assets/glossary.js")
    ap.add_argument("--check", action="store_true", help="exit 1 when the committed glossary.json differs from its term files")
    ap.add_argument("--split", action="store_true", help="the one-time split of glossary.json into per-term files")
    ap.add_argument("--path", default="", help="also write the record's glossary script here")
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
        print(f"glossary.json: STALE against its per-term files - run `make glossary` ({', '.join(stale)})", file=sys.stderr)
        return 1
    if not args.check:
        if source.write_source():
            importlib.reload(glossary)
        source.write_index()

    if args.check:
        print(f"glossary: in sync ({len(glossary.GLOSSARY)} terms)")
        return 0
    if args.path:
        with open(args.path, "w", encoding="utf-8") as fh:
            fh.write(glossary.record_glossary_js())
        print(f"wrote {args.path} ({len(glossary.GLOSSARY)} terms)")
    else:
        print(f"glossary: assembled ({len(glossary.GLOSSARY)} terms) - `make record` derives the site's script from it")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
