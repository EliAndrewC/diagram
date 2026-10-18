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
import hashlib
import json
import pathlib
import re
import subprocess
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


# ---- against HEAD's engine (feature 385 T03, the round arbiter's tooling fix on hour:385-approach-checklist@6 and ask:t03-d17-route):
# a count like 59/60 hid two failing seeds (55, 57) and a changed denominator (60 vs 66), and seed 57's lane knots went from 1
# to 4 while it read "pre-existing"


def same_engine(root: pathlib.Path, commit: str) -> bool:
    """Was `commit` rolled on main's engine - the generator and the pool's generators as they are on main? A record rolled in a
    detached worktree at the clone's HEAD counts whenever the clone's own commits change no engine file."""
    ref = "origin/main" if subprocess.run(["git", "-C", str(root), "rev-parse", "-q", "--verify", "origin/main"], capture_output=True).returncode == 0 else "main"
    return subprocess.run(["git", "-C", str(root), "diff", "--quiet", commit, ref, "--", "l7r", "pool"], capture_output=True).returncode == 0


def baselines(record: dict, earlier: list[dict], ok) -> dict[int, dict]:  # noqa: ANN001 - a predicate on a commit
    """Each seed's baseline: its entry in the newest earlier record, rolled at the same household count on main's engine."""
    out: dict[int, dict] = {}
    for r in sorted(earlier, key=lambda r: str(r.get("utc")), reverse=True):
        if (str(r.get("utc")) >= str(record.get("utc")) or r.get("households") != record.get("households") or not r.get("commit")
                or r.get("engine_diff") or not ok(str(r["commit"]))):  # a roll over an uncommitted engine diff is not its commit's
            continue
        for b in r.get("seeds") or []:
            out.setdefault(int(b["seed"]), b)
    return out


def standing(record: dict, base: dict[int, dict]) -> list[str]:
    """One line per seed that fails now or failed at its baseline: FIXED, NEWLY FAILING, WORSENED (a rule's count up, or a rule
    new to it), PRE-EXISTING - or, with no baseline on main's engine, the command that rolls one."""
    out = []
    for x in (y for y in record.get("seeds") or [] if not y.get("fresh")):  # a fresh seed has no baseline by construction (feature 386)
        n, b, now_bad = int(x["seed"]), base.get(int(x["seed"])), x.get("verdict") != "pass"
        rules = ", ".join(f"{k} {v}" for k, v in sorted((x.get("counts") or {}).items())) or ", ".join(x.get("failures") or [])
        if b is None:
            if now_bad:
                out.append(f"cohort: seed {n} fails ({rules}) with NO BASELINE on main's engine - roll one: git worktree add --detach /tmp/base origin/main && make -C /tmp/base cohort N=1 SEED={n}")
            continue
        was_bad = b.get("verdict") != "pass"
        was = ", ".join(f"{k} {v}" for k, v in sorted((b.get("counts") or {}).items())) or ", ".join(b.get("failures") or [])
        if not now_bad and was_bad:
            out.append(f"cohort: seed {n} FIXED (was: {was})")
        elif now_bad and not was_bad:
            out.append(f"cohort: seed {n} NEWLY FAILING ({rules})")
        elif now_bad:
            worse = [k for k, v in (x.get("counts") or {}).items() if v > (b.get("counts") or {}).get(k, 0)] if b.get("counts") is not None else []
            worse += [f for f in x.get("failures") or [] if f not in (b.get("failures") or [])]
            out.append(f"cohort: seed {n} {'WORSENED' if worse else 'PRE-EXISTING'} ({rules}; was: {was})")
    return out


def newest(root: pathlib.Path) -> dict | None:
    logs = sorted((root / "dev/cohort-log").glob("[0-9]*.json"))  # the records, not the feature index beside them
    return json.loads(logs[-1].read_text()) if logs else None


ENGINE_PATHS = ("l7r", "pool")


def stamp(root: pathlib.Path) -> str:
    """Mark the newest record rolled over an uncommitted engine diff with that diff's digest (`engine_diff`), so it is never read
    as its commit's baseline (feature 385 T04: the wave 155 patch, applied uncommitted, rolled a record that named HEAD and read
    as a second HEAD baseline). Returns the digest, or '' for a clean engine."""
    logs = sorted((root / "dev/cohort-log").glob("[0-9]*.json"))
    diff = subprocess.run(["git", "-C", str(root), "diff", "HEAD", "--", *ENGINE_PATHS], capture_output=True, text=True).stdout
    if not logs or not diff:
        return ""
    digest = hashlib.sha256(diff.encode()).hexdigest()[:16]
    rec = json.loads(logs[-1].read_text())
    rec["engine_diff"] = digest
    logs[-1].write_text(json.dumps(rec, indent=1) + "\n")
    return digest


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--stamp", action="store_true", help="only mark the newest record with its uncommitted engine diff's digest")
    args = ap.parse_args(argv)
    root = pathlib.Path(args.root)
    if args.stamp:
        d = stamp(root)
        if d:
            print(f"cohort: rolled over an uncommitted engine diff ({d}) - recorded so, never read as {ENGINE_PATHS} at its commit")
        return 0
    record = newest(root)
    for line in known(root, record) if record else []:
        print(line)
    if record:
        earlier = [json.loads(f.read_text()) for f in sorted((root / "dev/cohort-log").glob("[0-9]*.json"))[:-1]]
        for line in standing(record, baselines(record, earlier, lambda c: same_engine(root, c))):
            print(line)
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "gates"))
    import approach_gate  # noqa: PLC0415 - feature 385 D9: a seed newly failing owes the task's part B

    owed = approach_gate.cohort(root)
    if owed:
        print(owed)
    return 0



if __name__ == "__main__":
    sys.exit(main())
