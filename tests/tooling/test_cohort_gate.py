"""`scripts/gates/cohort_gate.py` (feature 386): the landing cohort the gated push requires - which records count, the fresh
block's rotating first seed, the regression reading, and when `make cohort-landing` rolls main's baseline. The push's refusal
and escape are driven end to end by `tests/hooks/test-cohort-gate.sh`."""

from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]


def _load():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("_cohort_gate", REPO / "scripts/gates/cohort_gate.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cg = _load()


def _git(root: pathlib.Path, *a: str) -> str:
    return subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", *a], capture_output=True, text=True, check=True).stdout.strip()


def _repo(tmp: pathlib.Path) -> tuple[pathlib.Path, str, str]:
    """main's engine at `base`; branch `work` changes it at `head`."""
    (tmp / "l7r").mkdir()
    (tmp / "pool").mkdir()
    (tmp / "l7r/a.py").write_text("X = 1\n")
    (tmp / "pool/p.txt").write_text("p\n")
    _git(tmp, "init", "-q", "-b", "main")
    _git(tmp, "add", "-A")
    _git(tmp, "commit", "-qm", "base")
    base = _git(tmp, "rev-parse", "--short", "HEAD")
    _git(tmp, "checkout", "-qb", "work")
    (tmp / "l7r/a.py").write_text("X = 2\n")
    _git(tmp, "commit", "-qam", "work")
    return tmp, base, _git(tmp, "rev-parse", "--short", "HEAD")


def _rec(root: pathlib.Path, utc: str, commit: str, first: int, bad: set[int] = frozenset(), fresh: int = 48, **extra: object) -> dict:  # type: ignore[assignment]
    """A record as `cohort_audit.write_record` writes it: 48 fixed seeds from `first`, the pinned rows, `fresh` seeds from 20000."""

    def seed(n: int, **more: object) -> dict:
        return {"seed": n, "verdict": "fail" if n in bad else "pass", "failures": ["lane_knots"] if n in bad else [], "counts": {"lane_knots": 1} if n in bad else {}, **more}

    seeds = [seed(n) for n in [*range(first, first + 48), *range(901, 907)]] + [seed(n, fresh=True) for n in range(20000, 20000 + fresh)]
    rec = {"utc": utc, "commit": commit, "first_seed": first, "households": None, "count": len(seeds), "seeds": seeds, **extra}
    log = root / "dev/cohort-log"
    log.mkdir(parents=True, exist_ok=True)
    (log / f"2026{utc}-t.json").write_text(json.dumps(rec))
    return rec


def test_the_fresh_seed_follows_the_engine_and_stays_above_the_fixed_range(tmp_path: pathlib.Path) -> None:
    root, _base, _head = _repo(tmp_path)
    one = cg.fresh_seed(root)
    assert one == cg.fresh_seed(root), "one engine, one block: a re-run is served from the roll cache"
    assert cg.FRESH_BASE <= one < cg.FRESH_BASE + cg.FRESH_SPAN
    (root / "pool/p.txt").write_text("q\n")
    assert cg.fresh_seed(root) != one, "an uncommitted engine diff is another engine"
    (root / "pool/p.txt").write_text("p\n")
    (root / "README").write_text("docs\n")
    assert cg.fresh_seed(root) == one, "a change outside the engine is the same engine"


def test_which_records_count(tmp_path: pathlib.Path) -> None:
    root, base, head = _repo(tmp_path)
    recs = [
        _rec(root, "u1", base, 1),  # main's engine
        _rec(root, "u2", head, 15),  # not from seed 1
        _rec(root, "u3", head, 1, engine_diff="abc"),  # rolled over an uncommitted engine diff
        _rec(root, "u4", "nosuchcommit", 1),
        _rec(root, "u5", head, 1, fresh=10),  # a per-fix block, not the landing cohort's 48
        _rec(root, "u6", head, 1, households=40),  # a scaling roll
        dict(_rec(root, "u7", head, 1), seeds=[{"seed": 1, "verdict": "pass"}]),  # too few seeds
    ]
    assert cg.pick(root, recs) is None
    landing = _rec(root, "u8", head, 1)
    assert cg.pick(root, [*recs, landing]) == landing


def test_the_check_refuses_a_regression_and_passes_a_pre_existing_failure(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root, base, head = _repo(tmp_path)
    refusals, _notes = cg.check(root)
    assert len(refusals) == 1 and "make cohort-landing" in refusals[0]
    assert cg.needs_baseline(root), "main's engine has no 48-seed record yet"
    _rec(root, "u1", base, 1, fresh=0)
    assert not cg.needs_baseline(root), "a 48-seed record on main's engine, with or without a fresh block, is the baseline"
    _rec(root, "u2", head, 1, {5, 20001})
    refusals, notes = cg.check(root)
    assert refusals and all("seed 5 NEWLY FAILING" in r for r in refusals), "the failing fresh seed is no refusal"
    assert any("fresh block from seed 20000: 1 of 48 failed (2%) - seeds 20001" in n for n in notes), "the rate prints and never refuses"
    _rec(root, "u4", base, 1, {5})
    _rec(root, "u5", head, 1, {5})
    refusals, notes = cg.check(root)
    assert refusals == [] and any("seed 5 PRE-EXISTING" in n for n in notes)
    _rec(root, "u6", head, 1, {7})
    assert any("seed 7 NEWLY FAILING" in r for r in cg.check(root)[0])
    monkeypatch.chdir(root)
    assert cg.main(["check"]) == 1 and cg.main(["fresh-seed"]) == 0 and cg.main(["nonsense"]) == 2
    assert cg.main(["needs-baseline"]) == 1


def test_a_failing_seed_with_no_baseline_is_refused_and_main_s_is_asked_for(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root, _base, head = _repo(tmp_path)
    _rec(root, "u1", head, 1, {9})
    assert any("seed 9" in r and "NO BASELINE" in r for r in cg.check(root)[0])
    monkeypatch.chdir(root)
    assert cg.main(["needs-baseline"]) == 0


def test_it_runs_as_a_script() -> None:
    out = subprocess.run([sys.executable, str(REPO / "scripts/gates/cohort_gate.py"), "fresh-seed"], capture_output=True, text=True, cwd=REPO, check=True)
    assert int(out.stdout) >= cg.FRESH_BASE
