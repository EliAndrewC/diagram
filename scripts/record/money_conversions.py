#!/usr/bin/env python3
"""The record's copy of gm-assistant's money conversion table (feature 413, diagram#14, FR-001).

gm-assistant generates `webapp/l7r/money/data/conversions.json` (`python3 -m l7r.money export`): per era and per coin, what
one unit was worth in silver, goods dollars, wage dollars and Rokugani sen. The record's build converts each marked amount
from a COPY of it, `research/assets/money-conversions.json`, so the build needs neither the network nor the mount. This
copies it, byte for byte, from gm-assistant's main checkout, read only (no git runs there).

    money_conversions.py           copy it                       `make money-conversions`
    money_conversions.py --check   exit 1 while the copy differs `make money-conversions CHECK=1`

A container without gm-assistant mounted checks nothing and says so (exit 0): the copy is what the build reads.
"""

from __future__ import annotations

import argparse
import os
import sys

SOURCE = "/host-l7r-repo/gm-assistant/webapp/l7r/money/data/conversions.json"
COPY = os.path.join("research", "assets", "money-conversions.json")


def main(argv: list[str] | None = None, source: str = SOURCE, root: str = ".") -> int:
    ap = argparse.ArgumentParser(description="copy gm-assistant's money conversion table into the record")
    ap.add_argument("--check", action="store_true", help="write nothing; exit 1 while the copy differs")
    args = ap.parse_args(argv)
    copy = os.path.join(root, COPY)
    try:
        with open(source, "rb") as fh:
            fresh = fh.read()
    except FileNotFoundError:
        print(f"money-conversions: gm-assistant's table is not here ({source}) - nothing to compare; the record builds from {COPY}")
        return 0
    try:
        with open(copy, "rb") as fh:
            held: bytes | None = fh.read()
    except FileNotFoundError:
        held = None
    if held == fresh:
        print(f"money-conversions: {COPY} is current")
        return 0
    if args.check:
        print(f"money-conversions: {COPY} differs from gm-assistant's {source} - run `make money-conversions` and commit the copy", file=sys.stderr)
        return 1
    with open(copy, "wb") as fh:
        fh.write(fresh)
    print(f"money-conversions: {COPY} refreshed from {source}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
