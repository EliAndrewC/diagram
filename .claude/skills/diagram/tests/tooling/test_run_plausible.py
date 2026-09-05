"""`check-run-plausible.py`: a run too fast to have worked does not get to say it passed.

THE BUG THIS CLOSES, found live 2026-09-05. GNU make executes `$(MAKE)` sub-invocations even under
`-n`, so `make -n done` walked the whole `done` recipe having done no work and then ran its closing
`LOGRUN ... green` and `$(STATE) green-local` lines FOR REAL - writing a correctly-hashed green
verification record in about four seconds. That record is the whole of what a push demands
(`ci/state.py::already_verified`), so parse-checking a Makefile edit minted a push credential. It was
also self-perpetuating: every later gate short-circuited on it and RE-STAMPED it, so it never aged
out, and only deleting `.git/verification-state.json` forced real work.

The two real records it produced are still in `dev/run-log/` and this suite replays them.
"""

from __future__ import annotations

import glob
import importlib.util
import json
import statistics
import subprocess
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2]
GUARD = SKILL.parents[2] / "scripts" / "check-run-plausible.py"


def _mod():
    spec = importlib.util.spec_from_file_location("check_run_plausible", GUARD)
    assert spec and spec.loader
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_a_dry_run_may_not_record() -> None:
    """The motivating case: `make -n done` reaching the recording lines with nothing done."""
    m = _mod()
    ok, why = m.check("done", 320, makeflags="n")
    assert not ok and "DRY RUN" in why


def test_the_dry_run_test_reads_only_the_flag_word() -> None:
    """A variable whose VALUE contains an `n` must not read as `-n`.

    This gate is invoked with `REASON=`, `FILE=` and `TARGET=` constantly, so a naive substring test
    over the whole of MAKEFLAGS would refuse ordinary runs - and a guard that fires on correct work
    teaches a session to bypass every guard.
    """
    m = _mod()
    assert m.dry_run("n")
    assert m.dry_run("nrR")
    assert not m.dry_run("")
    assert not m.dry_run("REASON=nothing")
    assert not m.dry_run("-- REASON=iterating on Inashiro")


def test_a_run_below_the_floor_may_not_record() -> None:
    m = _mod()
    ok, why = m.check("done", 4, makeflags="")
    assert not ok and "floor" in why
    assert m.check("done", 320, makeflags="")[0], "a real gate records"


def test_the_floor_is_DERIVED_from_the_pinned_ratchet_baseline() -> None:
    """One number serves the ceiling and the floor, so there is not a second to maintain.

    A FIXED threshold would be wrong in both directions: this gate's daily median has ranged from
    21 s (feature 135, warm) to 587 s (after feature 174 made the coverage floors unconditional).
    """
    m = _mod()
    sys.path.insert(0, str(GUARD.parent))
    try:
        import _ratchet  # type: ignore[import-not-found]
    finally:
        sys.path.pop(0)
    for target in ("done", "quick"):
        assert m.floor_for(target) == max(m.ABSOLUTE_MIN, int(_ratchet.RATCHETS[target].baseline * m.FRACTION))
    assert m.floor_for("no-such-target") is None, "a target with no ratchet row is not this guard's business"


def test_the_reuse_path_is_guarded_too() -> None:
    """The short-circuit RE-STAMPS rather than earns, and that is what kept a bogus record alive."""
    r = subprocess.run([sys.executable, str(GUARD), "--reuse", "done"], capture_output=True, text=True, env={"MAKEFLAGS": "n", "PATH": "/usr/bin:/bin"}, timeout=120)
    assert r.returncode == 1 and "DRY RUN" in r.stderr
    ok = subprocess.run([sys.executable, str(GUARD), "--reuse", "done"], capture_output=True, text=True, env={"MAKEFLAGS": "", "PATH": "/usr/bin:/bin"}, timeout=120)
    assert ok.returncode == 0, "a real short-circuit must still be allowed to re-stamp"


def test_the_floor_would_have_caught_the_KNOWN_dry_runs_and_nothing_else() -> None:
    """Replayed against every green `done` on record - the claim in the guard's own docstring.

    The two known dry runs (2026-09-05, 3 s and 4 s against a 382 s day median) must fail the floor.
    Everything else must pass it, judged against the baseline pinned AT THE TIME - which is why the
    floor is a fraction rather than a constant: runs of 16-29 s in late August were legitimate, when
    the gate really did finish in ~20 s warm.
    """
    m = _mod()
    rows = []
    for f in glob.glob(str(SKILL / "dev" / "run-log" / "*.json")):
        try:
            d = json.loads(Path(f).read_text(encoding="utf-8"))
        except Exception:
            continue
        if d.get("target") == "done" and d.get("result") == "green" and d.get("utc"):
            rows.append(d)
    assert len(rows) > 100, f"expected a substantial history to replay, found {len(rows)}"

    by_day: dict[str, list[float]] = {}
    for d in rows:
        by_day.setdefault(d["utc"][:10], []).append(float(d.get("seconds") or 0))

    # An era-relative reading of the same idea the floor encodes: a run far under its own day's
    # median did no work. The floor uses the pinned baseline instead, which is the stable form.
    implausible = [d for d in rows if statistics.median(by_day[d["utc"][:10]]) > 0 and float(d.get("seconds") or 0) < 0.02 * statistics.median(by_day[d["utc"][:10]])]
    stamps = sorted(d["utc"][:19] for d in implausible)
    assert stamps == ["2026-09-05T18:01:45", "2026-09-05T18:07:40"], "the replay should name exactly the two known `make -n done` records; got " + repr(stamps)
    for d in implausible:
        assert not m.check("done", float(d["seconds"]), makeflags="")[0], f"the floor must reject the known dry run at {d['utc']}"
