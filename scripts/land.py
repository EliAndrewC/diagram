#!/usr/bin/env python3
"""`make land F=<feature> T="<T1 [T2 ...]>" NOTE="<what was verified>"` - one command lands one task or several and ticks them
(feature 405 T33, D5; it grew from 385 T117's `land-batch`, which `make land-batch` still names).

WHY (the GM 2026-10-20, after 405's first claim: "It sounds like the landing being the biggest cost is something that we need to
do something about"). T12's fix took 5 minutes and its landing 15: six refusals met one at a time, each a session round trip,
and `make done` and `make cohort-landing` each started by hand only after a refusal named it - while the checks themselves take
seconds (`specs/405-engine-findings-from-385/landing-analysis.md`).

    land.py <feature> "<T1 [T2 ...]>"          (the note from $LAND_NOTE)

Pass 1 runs nothing long and prints EVERY refusal together: each task's tick refusals but "not landed yet", uncommitted work,
owed ledger rows, the claims gate, what holds the landing (with the tasks named, `L7R_LAND_TICKS`), the review gate and the plan
gate. Pass 2: `make done` when the green-gate stamp does not cover this content; `make cohort-landing` when the delta carries
engine code and the cohort gate would refuse - BESIDE the gate when both are owed (405 T48, D21); what those runs regenerate
under `pool/` is committed; then the
claims gate, waited on - its round runs beside the gate (405 T50); then each tick, committed, and ONE `scripts/sync-with-main.sh
done` with `L7R_LAND_TICKS` set carries work and ticks (405 T51). A failed landing ticks nothing (a failed push reverts its ticks).
"""

from __future__ import annotations

import importlib.util
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
#: the engine paths (`l7r.diagram.ci.delta.is_engine`'s list, feature 132 FR-008): a delta with one owes the landing cohort
ENGINE = re.compile(r"^(l7r/.*\.py|pool/.*\.gen\.py|pool/.*\.json)$")


def _tick_task():  # noqa: ANN202 - `tick-task.py` by path (its name has a hyphen)
    spec = importlib.util.spec_from_file_location("tick_task", HERE / "tick-task.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(root: Path, cmd: list[str], env: dict[str, str] | None = None, quiet: bool = True) -> tuple[int, str]:
    """A command from the clone: (its exit code, its output)."""
    out = subprocess.run(cmd, cwd=root, capture_output=quiet, text=True, env={**os.environ, **(env or {})})
    return out.returncode, (out.stdout or "") + (out.stderr or "") if quiet else ""


def write_ledger(root: Path, d: Path) -> None:
    """The ledger rows the push would name as owed, written and committed: the plan reviews' (385 T72) and every other pass
    traced to this feature - its claims round's above all (405 T39, D13). Asked in the first pass, and again after the claims
    wait (405 T52, D27: T49's claims round ran beside the gate, after the first pass, and its row was written by hand)."""
    ledger = str(root / "dev" / "review-ledger.md")
    run(root, [sys.executable, str(HERE / "reviews" / "ledger_owed.py"), "--write-plan-reviews", "--ledger", ledger])
    run(root, [sys.executable, str(HERE / "reviews" / "ledger_owed.py"), "--write", f"specs/{d.name}/ (the records its checks wrote; make land)", "--ledger", ledger])
    if run(root, ["git", "status", "--porcelain", "--", "dev/review-ledger.md"])[1].strip():
        run(root, ["git", "commit", "-q", "-m", "the review passes' ledger rows, written at landing (make land)", "--", "dev/review-ledger.md"])


def file_carries(root: Path, d: Path) -> None:
    """Every carried claims finding filed as an open task of the feature and committed (405 T36, D10) - asked in the first pass
    and again in the claims wait, where a round beside the gate meets new carries (405 T77)."""
    num = d.name.split("-", 1)[0]
    rc, said = run(root, [sys.executable, str(HERE / "record" / "claims.py"), "--root", str(root), "carry", "--feature", num])
    if rc == 0 and "filed into" in said:
        print(f"land: {said.strip()}", flush=True)
        rel = str(d.relative_to(root))
        run(root, ["git", "add", "--", f"{rel}/tasks.md", f"{rel}/claims-carried.jsonl"])
        run(root, ["git", "commit", "-q", "-m", f"{d.name}: claims findings outside the change filed as a task (make land, 405 T36)"])


def cheap_refusals(root: Path, d: Path, tasks: list[str], note: str, deferred: list[str] | None = None) -> list[str]:
    """Pass 1: every refusal the landing would meet that costs seconds to ask, all of them - but the claims gate's, which goes to
    `deferred` when given (405 T50, D23: the claims round runs beside the gate, and the landing waits for it before the push)."""
    tt = _tick_task()
    text = (d / "tasks.md").read_text(encoding="utf-8")
    by_why: dict[str, list[str]] = {}  # one refusal shared by several tasks (an hour's step-back) is printed once, naming them all
    for task in tasks:
        try:
            tt.tick(text, task, note)
        except ValueError as e:
            by_why.setdefault(str(e), []).append(task)
            continue
        why, _msg = tt.refusal(root, d, task, note, landed=False)
        if why:
            by_why.setdefault(why, []).append(task)
    stops = [f"{', '.join(ts)}: {why}" for why, ts in by_why.items()]
    write_ledger(root, d)
    # ...and the make-targets page, regenerated where the Makefile moved (feature 405 T46, D19): the push's `make-docs` check
    # refused T43's landing after its hooks-test, for a page `make docs` writes in a second
    if run(root, [sys.executable, str(HERE / "make-docs.py"), str(root), "--check"])[0]:
        run(root, [sys.executable, str(HERE / "make-docs.py"), str(root), "--write"])
        run(root, ["git", "commit", "-q", "-m", "docs/make-targets.html regenerated at landing (make land, 405 T46)", "--", "docs/make-targets.html"])
    # A MOVED UNIT KEEPS ITS CLAIMS' ROWS (405 T58): a file split into a package at the 1,000-line bar re-keys them, owing nothing
    run(root, [sys.executable, str(HERE / "record" / "claims.py"), "--root", str(root), "rekey"])
    if run(root, ["git", "status", "--porcelain", "--", "dev/claims-index.json"])[1].strip():
        run(root, ["git", "commit", "-q", "-m", "claim rows carried to the files their units moved to (make land, 405 T58)", "--", "dev/claims-index.json"])
    # A FINDING OUTSIDE THE CHANGE IS FILED, NOT REFUSED (feature 405 T36, D10): the carry files every carried claims finding as an
    # open task of this feature - what `make claims-carry` does by hand - and the box lands with the work
    file_carries(root, d)
    # THE LANDING'S OWN ESCAPES ARE COMMITTED, NOT REFUSED (feature 408): an escape the ticks above honored (PLAN_REVIEW_OK)
    # writes its dev/bypass-log record in this very pass, so the tree check below refused every rerun on records of its own
    if run(root, ["git", "status", "--porcelain", "--", "dev/bypass-log"])[1].strip():
        run(root, ["git", "add", "--", "dev/bypass-log"])
        run(root, ["git", "commit", "-q", "-m", "the landing's escape records (make land, 408)", "--", "dev/bypass-log"])
    if run(root, ["git", "status", "--porcelain"])[1].strip():
        stops.append("uncommitted changes - commit them first")
    _rc, owed = run(root, [sys.executable, str(HERE / "reviews" / "ledger_owed.py"), "--ledger", str(root / "dev" / "review-ledger.md")])
    if "| ? |" in owed:
        stops.append('review passes with no ledger row - make ledger-owed WRITE="<where you recorded what you did>"')
    env = {"L7R_LAND_TICKS": " ".join(tasks)}
    held = run(root, [sys.executable, str(HERE / "speckit-todo.py"), "--holding", str(d)], env)[1].strip()
    if held:
        stops.append(f"held by {held}")
    # A RED-GATE TRIPWIRE HOLDS THE LANDING'S GATE (feature 405 T44, D18): asked here with the others, on a landing that runs one
    if not os.environ.get("ARBITER_OK") and engine_delta(root):
        rc, out = run(root, [sys.executable, str(HERE / "hooks" / "lib" / "hm_arbiter.py"), "gate-held"])
        if rc:
            stops.append(out.strip().removeprefix("make done: refused - "))
    for gate in ("claims-gate.sh", "review-gate.sh", "plan-gate.sh"):
        rc, out = run(root, [str(HERE / "gates" / gate)], env)
        if rc:
            said = f"{gate}: " + " | ".join(ln.strip() for ln in out.splitlines() if ln.strip() and "pre-existing" not in ln)[-600:]
            (deferred if deferred is not None and gate == "claims-gate.sh" else stops).append(said)
    return stops


#: how long the landing waits for the claims round after its gate, asking every CLAIMS_POLL_S (405 T50, D23)
CLAIMS_WAIT_S = 1200.0
CLAIMS_POLL_S = 15.0


def wait_for_claims(root: Path, tasks: list[str], d: Path | None = None) -> str:
    """The claims gate passing and the tree clean - the claims round recorded and committed beside the gate - or, past
    `CLAIMS_WAIT_S`, the refusal that still stands (405 T50, D23)."""
    import time  # noqa: PLC0415

    env = {"L7R_LAND_TICKS": " ".join(tasks)}
    end, said = time.monotonic() + CLAIMS_WAIT_S, ""
    while True:
        rc, out = run(root, [str(HERE / "gates" / "claims-gate.sh")], env)
        if rc and d is not None and "carry:" in out and not any(w in out for w in ("owed (", "introduced:")):
            file_carries(root, d)  # a carry is filed, not waited on (405 T77: batch 5's wait needed `make claims-carry` by hand)
            rc, out = run(root, [str(HERE / "gates" / "claims-gate.sh")], env)
        dirty = run(root, ["git", "status", "--porcelain"])[1].strip()
        if not rc and not dirty:
            return ""
        why = ("claims-gate.sh: " + " | ".join(ln.strip() for ln in out.splitlines() if ln.strip() and "pre-existing" not in ln)[-600:]) if rc else f"uncommitted changes: {dirty.splitlines()[0]}"
        if time.monotonic() >= end:
            return why
        if why != said:
            print(f"land: waiting for the claims round before the push - {why}", flush=True)
            said = why
        time.sleep(CLAIMS_POLL_S)


def engine_delta(root: Path) -> bool:
    run(root, ["git", "fetch", "-q", "origin"])
    names = run(root, ["git", "diff", "--name-only", "origin/main...HEAD"])[1].split()
    return any(ENGINE.match(n) for n in names)


def commit_regenerated(root: Path, why: str) -> None:
    """What a gate run regenerated under `pool/` (T12: Kuwabata's manifest), committed so the push carries it."""
    if run(root, ["git", "status", "--porcelain", "--", "pool/"])[1].strip():
        run(root, ["git", "add", "--", "pool/"])
        run(root, ["git", "commit", "-q", "-m", f"regenerated by the landing's {why} (make land)"])


def make(root: Path, target: str) -> int:
    """A make target from the clone, its output passed through."""
    return subprocess.run(["make", "--no-print-directory", target], cwd=root).returncode


def push(root: Path, tasks: list[str]) -> int:
    """The landing: `scripts/sync-with-main.sh done` once, the tasks named so they hold nothing (D4)."""
    return subprocess.run([str(HERE / "sync-with-main.sh"), "done"], cwd=root, env={**os.environ, "L7R_LAND_TICKS": " ".join(tasks)}).returncode


#: the gate the green-gate stamp names for each stale area: "(make done again)", "(make hooks-test again)", "(make page-check again)"
NAMED_GATE = re.compile(r"\(make ([\w-]+) again\)")


#: what the gate holds at its peak, kept free for it when the cohort's workers are sized (3.1 GB on six workers, measured
#: 2026-10-04, rounded up), and the Makefile's own per-roll allowance for a cohort worker (`make cohort` JOBS=)
GATE_RESERVE_MB = 3500
ROLL_MB = 500
GATE_WORKERS = 6


def memory_free_mb(cgroup: Path = Path("/sys/fs/cgroup")) -> int:
    """The memory free to this container, MB: the host's MemAvailable, and - where the container has a cgroup v2 limit - no more
    than that limit less what the cgroup holds, its reclaimable file cache given back (405 T72: sized from the host's 9.5 GB
    alone, the batch-3 landing's 12 workers took the containers' shared 10 GB cap to 9.0 GB)."""
    try:
        avail = next(int(ln.split()[1]) // 1024 for ln in Path("/proc/meminfo").read_text().splitlines() if ln.startswith("MemAvailable:"))
    except OSError, StopIteration, ValueError:
        avail = GATE_RESERVE_MB + 4 * ROLL_MB
    try:
        cap = (cgroup / "memory.max").read_text().strip()
        if cap != "max":
            held = int((cgroup / "memory.current").read_text())
            cache = next((int(ln.split()[1]) for ln in (cgroup / "memory.stat").read_text().splitlines() if ln.startswith("inactive_file ")), 0)
            avail = min(avail, (int(cap) - held + cache) // (1024 * 1024))
    except OSError, ValueError:
        pass
    return avail


def cohort_jobs(cgroup: Path = Path("/sys/fs/cgroup")) -> tuple[int, int]:
    """The cohort's workers beside a running gate - the cpus the gate leaves and the memory it leaves, at least 2 - and the
    memory (MB) they were sized from (`memory_free_mb`)."""
    avail = memory_free_mb(cgroup)
    return max(2, min((os.cpu_count() or 4) - 2 - GATE_WORKERS, (avail - GATE_RESERVE_MB) // ROLL_MB)), avail


def start_cohort(root: Path) -> tuple[subprocess.Popen, Path]:
    """`make cohort-landing` in its own process group, beside the gate (405 T48, D21): its rolls are no gate's (the census
    variable removed), its reference check leaves the gate's `roll-cache-class` alone, its output to a log under the git dir."""
    jobs, avail = cohort_jobs()
    log = Path(run(root, ["git", "rev-parse", "--absolute-git-dir"])[1].strip() or root / ".git") / "land-cohort.log"
    env = {k: v for k, v in os.environ.items() if not k.startswith("L7R_ROLL_CENSUS")} | {"L7R_REF_NO_CLASS": "1"}
    print(f"land: make cohort-landing JOBS={jobs} beside the gate ({avail} MB free to the container; its log {log})", flush=True)
    with log.open("w") as fh:
        proc = subprocess.Popen(["make", "--no-print-directory", "cohort-landing", f"JOBS={jobs}"], cwd=root, env=env, stdout=fh, stderr=subprocess.STDOUT, start_new_session=True)
    return proc, log


def stop_cohort(proc: subprocess.Popen | None) -> None:
    """The cohort's whole process group ended - a red gate voids what it would record, and no exit leaves it running."""
    if proc is not None and proc.poll() is None:
        import contextlib  # noqa: PLC0415
        import signal  # noqa: PLC0415

        with contextlib.suppress(ProcessLookupError):
            os.killpg(proc.pid, signal.SIGTERM)
        proc.wait()


def commit_records(root: Path) -> None:
    """A run record the gate or the cohort could not commit - two commits at once, one lost the index lock - committed here."""
    if run(root, ["git", "status", "--porcelain", "--", "dev/cohort-log", "dev/run-log"])[1].strip():
        run(root, ["git", "add", "--", "dev/cohort-log", "dev/run-log"])
        run(root, ["git", "commit", "-q", "-m", "the run records (make land)", "--", "dev/cohort-log", "dev/run-log"])


def long_runs(root: Path) -> int:
    """Pass 2's runs, each only where its record does not cover this content; 0 when the push may go. The green-gate stamp names
    the gate each stale area owes (make done, make hooks-test, make page-check) and each named one runs - T30-T35's own landing
    owed hooks-test alone, which a `make done` would not have stamped."""
    stamp = [sys.executable, str(HERE / "gates" / "gate-stamp.py"), "--check", "origin/main"]
    rc, out = run(root, stamp)
    if rc:
        targets = list(dict.fromkeys(NAMED_GATE.findall(out)) or ["done"])
        # THE COHORT BESIDE THE GATE (405 T48, D21): they share no work - the gate rolls the five pool maps, the cohort its seeds
        # and rows - and T19's landing spent 4.4 of its 7 minutes on the cohort after a green gate
        cohort, log = None, Path()
        if "done" in targets and engine_delta(root) and run(root, [sys.executable, str(HERE / "gates" / "cohort_gate.py"), "check"])[0]:
            cohort, log = start_cohort(root)
        try:
            for target in targets:
                print(f"land: the green-gate stamp does not cover this content - make {target}", flush=True)
                if make(root, target):
                    print(f"land: make {target} is red - nothing landed; fix it and run make land again", file=sys.stderr)
                    return 1
            if cohort is not None:
                print("land: the gate is green - waiting for the landing cohort beside it", flush=True)
                said = log.read_text(errors="replace").splitlines() if cohort.wait() is not None else []
                print("\n".join(ln for ln in said if "passed the whole gate" in ln or "fresh block" in ln or "REGRESS" in ln.upper()), flush=True)
                if cohort.returncode:
                    print(f"land: the landing cohort refused - nothing landed ({log})", file=sys.stderr)
                    return 1
        finally:
            stop_cohort(cohort)
        commit_records(root)
        commit_regenerated(root, "gate")
        rc, out = run(root, stamp)
        if rc:
            print("land: the gates it named are green, but the green-gate stamp still refuses - nothing landed:\n" + out, file=sys.stderr)
            return 1
    if engine_delta(root) and run(root, [sys.executable, str(HERE / "gates" / "cohort_gate.py"), "check"])[0]:
        print("land: no landing cohort on this engine - make cohort-landing", flush=True)
        if make(root, "cohort-landing"):
            print("land: the landing cohort refused - nothing landed (above)", file=sys.stderr)
            return 1
        commit_regenerated(root, "cohort")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) != 2 or not (tasks := argv[1].split()):
        print('usage: land.py <feature> "<T1 [T2 ...]>"   (make land F=405 T=T12 NOTE="what was verified")', file=sys.stderr)
        return 2
    # A STOPPED LANDING STOPS ITS RUNS (405 T79): Python's default SIGTERM exits without `finally`, so a landing stopped by hand
    # left its gate and the cohort beside it running as orphans (batch 6); raised as SystemExit, the cleanup runs
    import signal  # noqa: PLC0415

    def _stopped(*_a: object) -> None:
        # ...the gate too: `make done` runs in this process's group (the cohort in its own session, stopped by the `finally`)
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        os.killpg(os.getpgrp(), signal.SIGTERM)
        sys.exit(143)

    signal.signal(signal.SIGTERM, _stopped)
    note = os.environ.get("LAND_NOTE", "").strip()
    if not note:
        print("land: refused - NOTE= is empty; say what was verified, as make tick asks", file=sys.stderr)
        return 2
    tt = _tick_task()
    root = tt.repo_root()
    d = tt.spec_dir(root, argv[0])
    if d is None or not (d / "tasks.md").is_file():
        print(f"land: no single specs/{argv[0]}* directory with a tasks.md under {root}", file=sys.stderr)
        return 2
    claims: list[str] = []
    stops = cheap_refusals(root, d, tasks, note, claims)
    if stops:
        print("land: refused before anything ran - nothing landed, nothing ticked. Every refusal:\n  " + "\n  ".join(stops + claims), file=sys.stderr)
        return 2
    if claims:
        print(f"land: the claims round is owed ({claims[0][:160]}) - the gate runs beside it; the push waits for it", flush=True)
    if rc := long_runs(root):
        return rc
    if why := wait_for_claims(root, tasks, d):
        print(f"land: the gates are green, but the claims round did not finish in {CLAIMS_WAIT_S / 60:.0f} min - nothing landed: {why}", file=sys.stderr)
        return 2
    write_ledger(root, d)  # the passes the claims round made beside the gate (405 T52, D27)
    # ONE PUSH, THE TICKS IN IT (405 T51, D24): T13's landing pushed its work, then its ticks - two runs of every push check
    rel = str(d.relative_to(root))
    how = f"landed in batch {'+'.join(tasks)}" if len(tasks) > 1 else "landed"
    os.environ["L7R_LAND_TICKS"] = " ".join(tasks)  # the tasks the landing ticks: `--landing` is honored for these alone
    failed = [task for task in tasks if tt.main([argv[0], task, f"{how}: {note}", "--landing"])]
    if failed:
        run(root, ["git", "checkout", "--", rel])  # the ticks already written put back: a landing that does not push ticks nothing
        print(f"land: {', '.join(failed)} refused its tick (above) - nothing landed, nothing ticked", file=sys.stderr)
        return 2
    run(root, ["git", "add", "--", rel])
    run(root, ["git", "commit", "-q", "-m", f"{d.name}: {' '.join(tasks)} ticked (make land)"])
    tick_sha = run(root, ["git", "rev-parse", "HEAD"])[1].strip()
    if rc := push(root, tasks):
        run(root, ["git", "revert", "--no-edit", tick_sha])  # a new commit, nothing rewritten: the tasks read open again
        print(f"land: the push failed (exit {rc}) - its ticks reverted, nothing landed; fix it and run make land again", file=sys.stderr)
        return rc
    print(f"land: {' '.join(tasks)} landed and ticked")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(HERE / "hooks" / "lib"))
    sys.dont_write_bytecode = True  # a record leaves no __pycache__ in the worktree (feature 406)
    import usage_log  # noqa: E402 - feature 406: the landing command records its run

    sys.exit(usage_log.exited("land", main(sys.argv[1:])))
