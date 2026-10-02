"""Derive the source vocabulary into the `source-applicability` contract (feature 305 FR-012).

`make source-tags-contract` rewrites the block between the contract's `source-tags` markers from
`research/source-tags.json`, so the agent - which launches without the record's CLAUDE.md files - judges tags against
the same explanations the labels show. `--check` writes nothing and exits 1 while the block is stale; the test in
`tests/interactive/test_source_tags.py` holds it at the gate.
"""

from __future__ import annotations

import argparse
import os
import sys

from l7r.diagram.interactive.record import source_tags as st
from l7r.diagram.interactive.sources import RESEARCH_DIR

#: The contract, from the skill's research directory: `.claude/agents/` beside `.claude/skills/`.
CONTRACT = os.path.normpath(os.path.join(RESEARCH_DIR, "..", "..", "..", "agents", "source-applicability.md"))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="derive the source vocabulary into the source-applicability contract")
    ap.add_argument("--check", action="store_true", help="exit 1 while the block is stale; write nothing")
    ap.add_argument("--contract", default=CONTRACT, help=argparse.SUPPRESS)
    ap.add_argument("--research-dir", default=RESEARCH_DIR, help=argparse.SUPPRESS)
    args = ap.parse_args(argv)
    with open(args.contract, encoding="utf-8") as fh:
        text = fh.read()
    try:
        fresh = st.synced_contract(text, st.load_vocabulary(args.research_dir))
    except st.SourceTagError as e:
        print(f"source-tags-contract: {e}", file=sys.stderr)
        return 1
    if fresh == text:
        print("source-tags-contract: the contract's vocabulary block is current")
        return 0
    if args.check:
        print("source-tags-contract: the contract's vocabulary block is stale - run make source-tags-contract", file=sys.stderr)
        return 1
    with open(args.contract, "w", encoding="utf-8") as fh:
        fh.write(fresh)
    print(f"source-tags-contract: rewrote the vocabulary block in {args.contract}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
