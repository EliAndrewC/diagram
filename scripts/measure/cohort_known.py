"""The cohort's failing seeds that an open found row already names (feature 374, the round arbiter's tooling fix on
ask:w155-cohort-seed10).

A seed that newly fails is often one a found row has already measured failing for the same reason: the web-settle row
`settle_the_web#a re-deal of the seats` lists seeds 7, 2, 10 and 8, and wave 155 spent a `settle_knots` probe on seed 10
before going to it. `make cohort` runs this after a failing roll: it reads the newest cohort record (`dev/cohort-log/`),
takes its failing seeds, and prints every OPEN found row (`specs/328-match-the-research/audit/found-*.jsonl`, not closed in
`waves.json`) whose words list one of them, so the session goes to the known row first.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

AUDIT = pathlib.Path("specs/328-match-the-research/audit")
_SEEDS = re.compile(r"\bseeds?\s+((?:\d+(?:\s*,\s*|\s+and\s+|\s*,\s*and\s+)?)+)", re.IGNORECASE)


def seeds_named(text: str) -> set[int]:
    """Every seed number a row's words list after "seed" or "seeds" ("seeds 7, 2, 10, 8", "seed 18 and 22")."""
    return {int(n) for m in _SEEDS.finditer(text) for n in re.findall(r"\d+", m.group(1))}


def failing_seeds(record: dict) -> list[int]:
    return [int(x["seed"]) for x in record.get("seeds") or [] if x.get("verdict") != "pass"]


def open_rows(root: pathlib.Path) -> list[dict]:
    closed = json.loads((root / AUDIT / "waves.json").read_text()) if (root / AUDIT / "waves.json").exists() else {}
    rows = []
    for f in sorted((root / AUDIT).glob("found-*.jsonl")):
        for line in f.read_text().splitlines():
            if line.strip():
                row = json.loads(line)
                if row.get("key") and row["key"] not in closed:
                    rows.append(row)
    return rows


def known(root: pathlib.Path, record: dict) -> list[str]:
    """One line per failing seed an open found row names: the seed, the row's key and tier."""
    out = []
    rows = [(r, seeds_named(" ".join(str(r.get(k) or "") for k in ("fix", "found")))) for r in open_rows(root)]
    for seed in failing_seeds(record):
        for r, named in rows:
            if seed in named:
                out.append(f"cohort: seed {seed} is named by an open found row - {r['key']} ({r.get('tier', '?')}); go to that row before probing")
    return out


def newest(root: pathlib.Path) -> dict | None:
    logs = sorted((root / "dev/cohort-log").glob("[0-9]*.json"))  # the records, not the feature index beside them
    return json.loads(logs[-1].read_text()) if logs else None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".")
    args = ap.parse_args(argv)
    root = pathlib.Path(args.root)
    record = newest(root)
    for line in known(root, record) if record else []:
        print(line)
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "gates"))
    import approach_gate  # noqa: PLC0415 - feature 385 D9: a seed newly failing owes the task's part B

    owed = approach_gate.cohort(root)
    if owed:
        print(owed)
    return 0



if __name__ == "__main__":
    sys.exit(main())
