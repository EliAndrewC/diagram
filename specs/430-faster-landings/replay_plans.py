"""m:plan-replay (feature 430 T01-T02, SC-001): today's full-planned gates whose reason named a pool manifest or a non-module
file under tests/, re-planned by the CURRENT planner between the same two commits.

Each run's baseline is a green FULL `done` run before it (a full green run records the baseline): the latest one at which the
file the run's own reason names differs from the run's commit. Each clone keeps its own baseline and the run records do not name
the clone, so "the last green full run" alone can name another clone's (it did for two conftest runs, 2026-10-26). The two manifests are
rebuilt from git (`ls-tree` blob ids: engine files, `tests/`, `scripts/`) and the gate's configuration hash from each commit's
own files (`git archive` of what `gate_config.config_hash` reads), then `incremental.plan` runs on them. What this replay does
not reproduce: the baseline's coverage contexts (an empty database here, so no import-time line can send a run full, and no test
is selected by a context) and the selection fraction (`make land` sets INCR_NO_CUTOFF). It answers the MODE each rule gives.

    python3 specs/430-faster-landings/replay_plans.py
"""

import glob
import json
import os
import re
import sqlite3
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("INCR_NO_CUTOFF", "1")
from l7r.diagram.ci import gate_config, incremental  # noqa: E402
from l7r.diagram.ci.delta import is_engine  # noqa: E402

REASON = re.compile(r"pool manifest|engine file that is not Python|non-module file under tests/")


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True).stdout


def manifest_at(commit: str) -> dict:
    blobs = {}
    for line in git("ls-tree", "-r", commit).splitlines():
        meta, path = line.split("\t", 1)
        blobs[path] = meta.split()[2]
    engine = {p: b for p, b in blobs.items() if is_engine(p) or (p.endswith(".py") and p.startswith("l7r/"))}
    with tempfile.TemporaryDirectory() as tmp:
        wanted = [p for p in (*gate_config.MACHINERY, *gate_config.LOCKFILES, "Makefile", "pyproject.toml") if any(b == p or b.startswith(p + "/") for b in blobs)]
        data = subprocess.run(["git", "-C", str(ROOT), "archive", commit, "--", *wanted], capture_output=True, check=True).stdout
        tar = Path(tmp) / "a.tar"
        tar.write_bytes(data)
        with tarfile.open(tar) as t:
            t.extractall(Path(tmp) / "tree", filter="data")
        config = gate_config.config_hash(Path(tmp) / "tree")
    return {
        "engine": engine,
        "tests": {p: b for p, b in blobs.items() if p.startswith("tests/")},
        "scripts": {p: b for p, b in blobs.items() if p.startswith("scripts/")},
        "tooling": "same",
        "gate_config": config,
    }


def empty_db(path: Path) -> None:
    con = sqlite3.connect(str(path))
    con.executescript(
        "create table file (id integer primary key, path text unique); create table context (id integer primary key, context text unique);"
        "create table line_bits (file_id integer, context_id integer, numbits blob, unique (file_id, context_id));"
    )
    con.close()


def main() -> int:
    runs = []
    for f in sorted(glob.glob(str(ROOT / "dev/run-log/2026-10/*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        if d.get("target") == "done":
            runs.append((Path(f).name, d))
    greens: list[str] = []
    for name, d in runs:
        named = re.search(r"changed: (\S+)", d.get("plan_reason") or "")
        base = next((g for g in reversed(greens) if named and git("rev-parse", f"{g}:{named.group(1)}").strip() != git("rev-parse", f"{d['commit']}:{named.group(1)}").strip()), greens[-1] if greens else None)
        if name.startswith("20261026") and d.get("plan_mode") == "full" and REASON.search(d.get("plan_reason") or "") and base:
            with tempfile.TemporaryDirectory() as tmp:
                bdir = Path(tmp)
                before, now = manifest_at(base), manifest_at(d["commit"])
                (bdir / incremental.MANIFEST).write_text(json.dumps(before), encoding="utf-8")
                empty_db(bdir / incremental.COVERAGE_DB)
                (bdir / incremental.TESTS).write_text("{}", encoding="utf-8")
                incremental.baseline_dir = lambda root, b=bdir: b
                incremental.manifest = lambda root, n=now: n
                pl = incremental.plan(ROOT)
            print(f"{d['commit']} (base {base}): was full - {d['plan_reason'][:70]}\n    now {pl.mode} - {pl.reason[:150]}")
        if d.get("result") == "green" and d.get("plan_mode") == "full":
            greens.append(d["commit"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
