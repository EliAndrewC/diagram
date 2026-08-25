"""Tier 2 of the performance evidence (feature 129): cProfile ONE stage of ONE seed, on demand.

    python3 -m l7r.diagram.tools.perf_profile --seed 25 --stage web       (via `make perf-profile SEED=25 STAGE=web`)

WHY TRIGGERED AND NARROW. cProfile costs +225% on the real generation workload (research R2:
27.4 s -> 89.0 s on seed 4), so always-on was ruled out at the GM's 20% line. The free per-stage
delta every snapshot carries says WHICH stage grew; this says WHICH FUNCTION inside it, and it runs
only when the stage delta cannot explain a change. One stage of one seed costs ~3x that stage.

WHAT IS KEPT WHERE (FR-011, FR-011a, FR-011b). The DERIVED evidence - the top-25 cumulative
functions, plain and profiled wall times - is a few kilobytes and is committed beside the snapshots
in dev/perf-log/. The raw `.prof` goes to dev/perf-raw/ (gitignored) and, when a profile-archive
repository is configured (`PERF_ARCHIVE`, a git URL the GM provides), is pushed there; when it is
not, the tool says so and the finding here stands on its own.

By-hand tool: not under the 100% rule (it drives the generator and cProfile), but mypy --strict.
"""

from __future__ import annotations

import argparse
import cProfile
import io
import os
import pstats
import subprocess
import sys
import time
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
if SKILL not in sys.path:
    sys.path.insert(0, SKILL)
LOG_DIR = os.path.join(SKILL, "dev", "perf-log")
RAW_DIR = os.path.join(SKILL, "dev", "perf-raw")


def profile_stage(seed: int, stage: str, top: int = 25) -> tuple[str, str]:
    """(the derived table, the raw .prof path)."""
    from l7r.diagram.hamletgen import HamletSpec, plan_site
    from l7r.diagram.hamletgen.driver import STAGES
    from l7r.diagram.settlement import Settlement
    from l7r.diagram.tools.perf_snapshot import REFERENCE

    plan = plan_site(HamletSpec(seed=seed, **REFERENCE))
    s = Settlement(W=plan.W, H=plan.H, seed=seed)
    s._avoid_seats = []  # type: ignore[attr-defined]
    names = [st.__name__.replace("stage_", "") for st in STAGES]
    if stage not in names:
        raise SystemExit(f"perf-profile: no stage {stage!r}; the stages are: {', '.join(names)}")
    target = STAGES[names.index(stage)]
    plain = profiled = 0.0
    prof = cProfile.Profile()
    with redirect_stdout(io.StringIO()):
        for st in STAGES:
            if st is target:
                # the stage runs ONCE, profiled; the plain time is the snapshot's job (a second run would double the stage's side effects)
                t0 = time.time()
                prof.enable()
                st(s, plan)
                prof.disable()
                profiled = time.time() - t0
                break
            t0 = time.time()
            st(s, plan)
            plain += time.time() - t0
    os.makedirs(RAW_DIR, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    raw = os.path.join(RAW_DIR, f"{stamp}-seed{seed}-{stage}.prof")
    prof.dump_stats(raw)
    out = io.StringIO()
    st_ = pstats.Stats(prof, stream=out)
    st_.sort_stats("cumulative").print_stats(top)
    body = out.getvalue()
    head = f"perf-profile seed {seed} stage {stage}: {profiled:.1f}s under cProfile (the stages before it took {plain:.1f}s unprofiled; cProfile itself is ~+225%, research R2)\nraw: {os.path.relpath(raw, SKILL)} (gitignored; archive: {archive_status()})\n\n"
    return head + body, raw


def archive_status() -> str:
    url = os.environ.get("PERF_ARCHIVE", "")
    return (
        f"configured ({url})" if url else "no archive configured - set PERF_ARCHIVE=<git url> once the GM creates the profile repository (FR-011a); the derived table here stands on its own (FR-011b)"
    )


def archive(raw: str) -> str:
    url = os.environ.get("PERF_ARCHIVE", "")
    if not url:
        return "archive skipped: " + archive_status()
    work = os.path.join(RAW_DIR, "archive")
    try:
        if not os.path.isdir(os.path.join(work, ".git")):
            subprocess.run(["git", "clone", "-q", "--depth", "1", url, work], check=True, capture_output=True, text=True, timeout=120)
        dest = os.path.join(work, os.path.basename(raw))
        subprocess.run(["cp", raw, dest], check=True)
        subprocess.run(["git", "-C", work, "add", os.path.basename(raw)], check=True, capture_output=True)
        subprocess.run(["git", "-C", work, "commit", "-q", "-m", f"profile {os.path.basename(raw)}"], check=True, capture_output=True, text=True)
        subprocess.run(["git", "-C", work, "push", "-q"], check=True, capture_output=True, text=True, timeout=120)
        return f"archived to {url}"
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:  # pragma: no cover - the remote's failure modes
        return f"archive FAILED ({e}) - the derived table is committed here regardless (FR-011b)"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--stage", required=True)
    ap.add_argument("--top", type=int, default=25)
    ap.add_argument("--feature", default=os.environ.get("SPECIFY_FEATURE", "adhoc"))
    a = ap.parse_args(argv)
    table, raw = profile_stage(a.seed, a.stage, a.top)
    os.makedirs(LOG_DIR, exist_ok=True)
    n = "".join(ch for ch in a.feature.split("-")[0] if ch.isdigit()) or "adhoc"
    path = os.path.join(LOG_DIR, f"{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}-profile-{n}-seed{a.seed}-{a.stage}.txt")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(table)
    print(table[:2000])
    print(f"wrote {os.path.relpath(path, SKILL)} ({os.path.getsize(path)} bytes)")
    print(archive(raw))
    return 0


if __name__ == "__main__":
    from l7r.diagram._invocation import guard

    guard("l7r.diagram.tools.perf_profile")
    raise SystemExit(main())
