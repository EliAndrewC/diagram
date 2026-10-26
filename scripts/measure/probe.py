"""`make probe` - what a change does to every seed and every pool map, against HEAD, in one command (feature 426, D5).

    make probe [WT=<worktree>] [EXITFIRST=1] [JOBS=<n>]

In `WT` (default: this tree), with the change already applied there, it rolls the landing cohort (`cohort N=48 FRESH=0`) and
HEAD's fresh block (48 seeds from the block HEAD's engine key names, `cohort_gate.fresh_seed`), regenerates each live hamlet,
and prints:

- EVERY seed's verdict beside HEAD's, a difference marked (new failure, fixed, changed failure; same failure; same pass), so the
  seed being worked on shows whether or not it moved;
- each pool manifest's changed fields by path, lanes compared as drawn (rounded points).

HEAD's verdicts are read from `<git common dir>/probe-baselines/<HEAD's engine key>-<block>.json`; with none stored, HEAD is
rolled once in a detached worktree and stored, so two probes at one HEAD roll HEAD's block once (SC-004). `EXITFIRST=1` stops each
cohort at the first seed worse than HEAD's (`cohort_audit --exitfirst-against`). It replaces the hand-written probe scripts of
feature 417, one of which compared the SETS of failing seeds and missed a seed whose failure changed (T48).

Exit status: 1 when any seed is worse than at HEAD, else 0.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SEEDS = 48
WORSE = ("NEW FAILURE",)


def run(cmd: list[str], cwd: Path) -> tuple[int, str]:
    """`cmd` in `cwd`: (exit status, stdout and stderr together)."""
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)
    return p.returncode, p.stdout + p.stderr


def _git(root: Path, *a: str) -> str:
    return run(["git", "-C", str(root), *a], root)[1].strip()


def _cohort_gate() -> Any:  # noqa: ANN401 - the module
    spec = importlib.util.spec_from_file_location("cohort_gate", HERE.parent / "gates" / "cohort_gate.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def record_of(out: str, root: Path) -> dict[str, Any]:
    """The cohort record a `make cohort` run names ("record committed (...): <path>"), read from the clone it lands in."""
    m = re.findall(r"record committed \([^)]*\): (\S+\.json)", out)
    if not m:
        raise SystemExit(f"probe: the cohort wrote no record - its output ended:\n{out[-1500:]}")
    common = Path(_git(root, "rev-parse", "--path-format=absolute", "--git-common-dir"))
    path = Path(m[-1]) if Path(m[-1]).is_absolute() else common.parent / m[-1]
    return json.loads(path.read_text(encoding="utf-8"))


def verdicts(rec: dict[str, Any]) -> dict[int, list[str]]:
    """{seed: its sorted failures} for every seed a record rolled."""
    return {int(s["seed"]): sorted(s.get("failures") or []) for s in rec.get("seeds") or []}


def mark(head: list[str] | None, now: list[str] | None) -> str:
    """How a seed's verdict moved against HEAD's: a check new to it is worse whatever else it fails."""
    if now is None:
        return "not rolled"
    if head is None:
        return "new seed"
    if not head and not now:
        return "same pass"
    if not now:
        return "FIXED"
    if {f.split("[")[0] for f in now} - {f.split("[")[0] for f in head}:
        return "NEW FAILURE"
    return "same failure" if now == head else "changed failure"


def _show(v: list[str] | None) -> str:
    return "-" if v is None else ("pass" if not v else ", ".join(v))


def compare(head: dict[int, list[str]], now: dict[int, list[str]]) -> tuple[list[str], int]:
    """Every seed's line, HEAD's verdict beside the probe's, and how many are worse."""
    lines, worse = [], 0
    for seed in sorted({*head, *now}):
        m = mark(head.get(seed), now.get(seed))
        worse += m in WORSE
        lines.append(f"  {seed:>7}  {m:<16} HEAD: {_show(head.get(seed))}  now: {_show(now.get(seed))}")
    return lines, worse


def _drawn(v: Any) -> Any:  # noqa: ANN401 - a manifest value
    """A value as the manifest compares: points rounded to the tenth they are drawn at."""
    if isinstance(v, float):
        return round(v, 1)
    if isinstance(v, list):
        return [_drawn(x) for x in v]
    if isinstance(v, dict):
        return {k: _drawn(x) for k, x in v.items()}
    return v


def manifest_diff(old: Any, new: Any, path: str = "") -> list[str]:  # noqa: ANN401 - manifests
    """Each field path whose value differs, as drawn; a list of a different length is one change at its path."""
    a, b = _drawn(old), _drawn(new)
    if isinstance(a, dict) and isinstance(b, dict):
        return [p for k in sorted({*a, *b}, key=str) for p in manifest_diff(a.get(k), b.get(k), f"{path}.{k}" if path else str(k))]
    if isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        return [p for i, (x, y) in enumerate(zip(a, b, strict=True)) for p in manifest_diff(x, y, f"{path}[{i}]")]
    return [] if a == b else [path or "(the manifest)"]


def _cohort_cmd(jobs: str, seed: int | None) -> list[str]:
    return ["make", "--no-print-directory", "cohort", f"N={SEEDS}", "FRESH=0", f"JOBS={jobs}", *([f"SEED={seed}"] if seed else [])]


def baseline(root: Path, block: int, jobs: str) -> tuple[dict[int, list[str]], dict[int, list[str]]]:
    """HEAD's (landing, fresh) verdicts: stored per engine key and block, or rolled once in a detached worktree at HEAD."""
    cg = _cohort_gate()
    key = hashlib.sha256(cg.cohort_known.engine_key(root, "HEAD").encode()).hexdigest()[:16]
    store = Path(_git(root, "rev-parse", "--path-format=absolute", "--git-common-dir")) / "probe-baselines" / f"{key}-{block}.json"
    if store.is_file():
        data = json.loads(store.read_text(encoding="utf-8"))
        return {int(k): v for k, v in data["landing"].items()}, {int(k): v for k, v in data["fresh"].items()}
    print(f"probe: HEAD's verdicts for block {block} are not stored - rolling HEAD once in a detached worktree", flush=True)
    with tempfile.TemporaryDirectory() as tmp:
        wt = Path(tmp) / "head"
        run(["git", "-C", str(root), "worktree", "add", "-q", "--detach", str(wt), "HEAD"], root)
        try:
            landing = verdicts(record_of(run(_cohort_cmd(jobs, None), wt)[1], root))
            fresh = verdicts(record_of(run(_cohort_cmd(jobs, block), wt)[1], root))
        finally:
            run(["git", "-C", str(root), "worktree", "remove", "--force", str(wt)], root)
    store.parent.mkdir(parents=True, exist_ok=True)
    store.write_text(json.dumps({"landing": landing, "fresh": fresh}), encoding="utf-8")
    return landing, fresh


def probe_cohort(wt: Path, root: Path, seed: int | None, jobs: str, against: dict[int, list[str]] | None) -> dict[int, list[str]]:
    """The cohort rolled in `wt`, stopping at the first seed worse than `against` when given."""
    cmd = _cohort_cmd(jobs, seed)
    if against is not None:
        f = Path(tempfile.mkstemp(suffix=".json")[1])
        f.write_text(json.dumps(against), encoding="utf-8")
        cmd += ["EXITFIRST=1", f"EXITFIRST_AGAINST={f}"]
    return verdicts(record_of(run(cmd, wt)[1], root))


def pool_changes(wt: Path, root: Path) -> list[str]:
    """Each live hamlet regenerated in `wt`, its manifest's changed fields against HEAD's committed one."""
    out: list[str] = []
    for gen in sorted((wt / "pool" / "hamlets").glob("*/*.gen.py")):
        run(["make", "--no-print-directory", "map", f"GEN={gen.relative_to(wt)}"], wt)
        rel = gen.parent.relative_to(wt) / f"{gen.parent.name}.json"
        head = _git(root, "show", f"HEAD:{rel}")
        moved = manifest_diff(json.loads(head) if head else {}, json.loads((wt / rel).read_text(encoding="utf-8")))
        out.append(f"  {gen.parent.name}: " + (f"{len(moved)} field(s) moved - {', '.join(moved[:8])}{' ...' if len(moved) > 8 else ''}" if moved else "unchanged"))
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--wt", default="")
    ap.add_argument("--exitfirst", action="store_true")
    ap.add_argument("--jobs", default="3")
    args = ap.parse_args(argv)
    root = Path(_git(Path(args.root), "rev-parse", "--show-toplevel") or args.root)
    wt = Path(args.wt).resolve() if args.wt else root
    block = _cohort_gate().fresh_seed(root, "HEAD")
    head_landing, head_fresh = baseline(root, block, args.jobs)
    landing = probe_cohort(wt, root, None, args.jobs, head_landing if args.exitfirst else None)
    fresh = probe_cohort(wt, root, block, args.jobs, head_fresh if args.exitfirst else None)
    worse = 0
    for title, head, now in (("the landing cohort", head_landing, landing), (f"HEAD's fresh block from {block}", head_fresh, fresh)):
        lines, n = compare(head, now)
        worse += n
        print(f"\n{title} ({n} worse than HEAD):")
        print("\n".join(lines))
    print("\nthe pool against HEAD:")
    print("\n".join(pool_changes(wt, root)))
    print(f"\nprobe: {worse} seed(s) worse than HEAD" + (" - EXITFIRST stopped at the first" if args.exitfirst and worse else ""))
    return 1 if worse else 0


if __name__ == "__main__":
    sys.exit(main())
