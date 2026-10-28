"""`scripts/measure/cohort_known.py` (feature 374, the round arbiter's tooling fix on ask:w155-cohort-seed10): a failing
cohort seed an open found row already lists is named with that row, so the session goes there before probing."""

from __future__ import annotations

import importlib.util
import json
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[2]


def _load():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("_cohort_known", REPO / "scripts/measure/cohort_known.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _engine_tree(root: pathlib.Path) -> None:
    """`l7r/` and the `gate-stamp.py` the engine key loads from the tree it reads (as `tests/tooling/ci/conftest.py` copies it)."""
    (root / "l7r").mkdir(parents=True)
    (root / "scripts/gates").mkdir(parents=True)
    (root / "scripts/gates/gate-stamp.py").write_text((REPO / "scripts/gates/gate-stamp.py").read_text(encoding="utf-8"), encoding="utf-8")
    (root / "scripts/gates/codeid.py").write_text((REPO / "scripts/gates/codeid.py").read_text(encoding="utf-8"), encoding="utf-8")  # gate-stamp loads its code id beside it (feature 426 D2)


def test_the_seeds_a_row_lists_are_read_from_its_words() -> None:
    ck = _load()
    assert ck.seeds_named("re-dealt seats move a refusal into the cohort (seeds 7, 2, 10, 8 under routes B-D)") == {7, 2, 10, 8}
    assert ck.seeds_named("Inashiro and valley seed 18 and 22 when ...") == {18, 22}
    assert ck.seeds_named("no seed named, 40 households") == set()


def test_a_failing_seed_an_open_row_lists_is_named_and_a_closed_row_is_not(tmp_path: pathlib.Path) -> None:
    ck = _load()
    audit = tmp_path / "specs/328-match-the-research/audit"
    audit.mkdir(parents=True)
    rows = [
        {"key": "settle#re-deal", "tier": "E4", "fix": "the web carries a re-deal", "found": "seeds 7, 2, 10, 8 under routes B-D"},
        {"key": "closed#row", "tier": "E1", "fix": "x", "found": "seed 10 once"},
    ]
    (audit / "found-wave149.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    (audit / "waves.json").write_text(json.dumps({"closed#row": "150"}))
    logs = tmp_path / "dev/cohort-log"
    logs.mkdir(parents=True)
    record = {"seeds": [{"seed": 10, "verdict": "fail"}, {"seed": 3, "verdict": "fail"}, {"seed": 7, "verdict": "pass"}]}
    (logs / "20261013T125506Z-x.json").write_text(json.dumps(record))
    (logs / "features.json").write_text("{}")  # the feature index beside the records sorts after them
    said = ck.known(tmp_path, ck.newest(tmp_path))
    assert said == ["cohort: seed 10 is named by an open found row - settle#re-deal (E4); go to that row before probing"]
    assert ck.main(["--root", str(tmp_path)]) == 0
    assert ck.newest(tmp_path / "nowhere") is None


def _seed(n: int, verdict: str = "pass", counts: dict | None = None, failures: list | None = None) -> dict:
    return {"seed": n, "verdict": verdict, "counts": counts or {}, "failures": failures or list(counts or {})}


def test_each_failing_seed_is_read_against_its_baseline_on_mains_engine() -> None:
    """Feature 385 T03 (the round arbiter's tooling fix on hour:385-approach-checklist@6): a count like 59/60 hid two failing
    seeds, and seed 57's lane knots went from 1 to 4 while it read "pre-existing"."""
    ck = _load()
    base = {
        "utc": "20261017T1000Z",
        "commit": "main1",
        "households": None,
        "seeds": [_seed(17, "fail", {"lane_knots": 1}), _seed(21), _seed(55, "fail", {"lane_knots": 1}), _seed(57, "fail", {"lane_knots": 1}), _seed(58, "fail", failures=["refused:WebRefused"])],
    }
    other = {"utc": "20261017T1100Z", "commit": "clone9", "households": None, "seeds": [_seed(60)]}
    now = {
        "utc": "20261017T2000Z",
        "commit": "x",
        "households": None,
        "seeds": [
            _seed(17),
            _seed(21, "fail", {"fabric": 2}),
            _seed(55, "fail", {"lane_knots": 1}),
            _seed(57, "fail", {"lane_knots": 4}),
            _seed(58, "refused", failures=["refused:WebRefused", "lane_knots"]),
            _seed(59, "fail", {"bends": 1}),
            _seed(60, "fail", {"bends": 1}),
            _seed(61),
        ],
    }
    got = ck.standing(now, ck.baselines(now, [base, other], lambda c: c.startswith("main")))
    assert got[0] == "cohort: seed 17 FIXED (was: lane_knots 1)"
    assert got[1] == "cohort: seed 21 NEWLY FAILING (fabric 2)"
    assert got[2] == "cohort: seed 55 PRE-EXISTING (lane_knots 1; was: lane_knots 1)"
    assert got[3] == "cohort: seed 57 WORSENED (lane_knots 4; was: lane_knots 1)"
    assert got[4].startswith("cohort: seed 58 WORSENED"), "a rule new to it"
    assert "seed 59 fails (bends 1) with NO BASELINE" in got[5] and "make -C /tmp/base cohort N=1 SEED=59" in got[5]
    assert "seed 60 fails" in got[6], "a record off main's engine is no baseline"
    assert len(got) == 7, "a seed passing at both says nothing"


def test_a_commit_is_on_mains_engine_when_no_engine_file_differs(tmp_path: pathlib.Path) -> None:
    import subprocess

    ck = _load()
    root = tmp_path / "r"
    _engine_tree(root)

    def git(*a: str) -> str:
        return subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", *a], check=True, capture_output=True, text=True).stdout.strip()

    git("init", "-q", "-b", "main")
    (root / "l7r" / "a.py").write_text("x = 1\n")
    git("add", "-A")
    git("commit", "-qm", "engine")
    (root / "notes.md").write_text("n\n")
    git("add", "-A")
    git("commit", "-qm", "a spec")
    spec_only = git("rev-parse", "HEAD")
    git("checkout", "-q", "-b", "side")
    (root / "l7r" / "CLAUDE.md").write_text("docs\n")
    (root / "l7r" / "a.py").write_text('"""A docstring."""\n\n# a comment\nx  =  1\n')
    git("add", "-A")
    git("commit", "-qm", "docs, a docstring, a comment and formatting under l7r/")
    words_only = git("rev-parse", "HEAD")
    (root / "l7r" / "a.py").write_text("x = 2\n")
    git("commit", "-qam", "engine moved")
    moved = git("rev-parse", "HEAD")
    git("checkout", "-q", "main")
    assert ck.same_engine(root, spec_only) and not ck.same_engine(root, moved)
    assert ck.same_engine(root, words_only), "a docs or docstring edit under l7r/ is main's engine still (the GM, 2026-10-18)"
    assert not ck.same_engine(root, "nosuchcommit") and ck.engine_key(root, "nosuchcommit") == ""


def test_a_roll_over_an_uncommitted_engine_diff_is_stamped_and_never_a_baseline(tmp_path: pathlib.Path) -> None:
    """Feature 385 T04: the wave 155 patch, applied uncommitted, rolled a record naming HEAD's commit - read as a second HEAD
    baseline. `--stamp` writes the diff's digest into the newest record; `baselines` and the approach gate skip such a record."""
    import subprocess

    ck = _load()
    root = tmp_path / "r"
    _engine_tree(root)
    (root / "dev" / "cohort-log").mkdir(parents=True)

    def git(*a: str) -> None:
        subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", *a], check=True, capture_output=True)

    git("init", "-q", "-b", "main")
    (root / "l7r" / "a.py").write_text("x = 1\n")
    git("add", "-A")
    git("commit", "-qm", "engine")
    rec = root / "dev" / "cohort-log" / "20261018T0000Z-x.json"
    rec.write_text(json.dumps({"utc": "20261018T0000Z", "commit": "main1", "seeds": [_seed(10)]}))
    assert ck.stamp(root) == "" and "engine_diff" not in json.loads(rec.read_text()), "a clean engine stamps nothing"
    assert ck.main(["--root", str(root), "--stamp"]) == 0
    (root / "l7r" / "CLAUDE.md").write_text("docs\n")
    (root / "l7r" / "a.py").write_text('"""A docstring."""\n\n# a comment\nx  =  1\n')
    assert ck.stamp(root) == "", "docs, a docstring or a comment under l7r/ is no engine diff (the GM, 2026-10-18)"
    (root / "l7r" / "a.py").write_text("x = 2\n")
    assert ck.main(["--root", str(root), "--stamp"]) == 0
    stamped = json.loads(rec.read_text())
    assert len(stamped["engine_diff"]) == 16
    now = {"utc": "20261018T0100Z", "commit": "x", "households": None, "seeds": [_seed(10, "fail", {"bends": 1})]}
    assert ck.baselines(now, [stamped], lambda c: True) == {}, "a dirty roll is no baseline"
    assert ck.baselines(now, [{k: v for k, v in stamped.items() if k != "engine_diff"}], lambda c: True)


def test_a_counter_only_successor_is_the_same_engine_and_an_added_file_is_not(tmp_path: pathlib.Path) -> None:
    """Feature 446 FR-002: a commit that only adds counter blocks keeps main's engine for the cohort, so a counter-only landing's
    record stays the baseline; any other change, an added file and a non-counter `if __debug__:` among them, is another engine."""
    import subprocess

    ck = _load()
    root = tmp_path / "r"
    _engine_tree(root)

    def git(*a: str) -> str:
        return subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", *a], check=True, capture_output=True, text=True).stdout.strip()

    body = "def f(xs):\n    n = 0\n    for x in xs:\n        n += x\n    return n\n"
    git("init", "-q", "-b", "main")
    (root / "l7r" / "a.py").write_text(body)
    git("add", "-A")
    git("commit", "-qm", "engine")
    base = git("rev-parse", "HEAD")
    (root / "l7r" / "a.py").write_text(body.replace("    n = 0\n", '    n = 0\n    if __debug__:\n        OPS["candidate@f"] += len(xs)\n'))
    git("commit", "-qam", "a counter")
    counted = git("rev-parse", "HEAD")
    assert ck.counter_only(root, base, counted) and ck.same_key(root, base, counted), "a counter block is the same engine"
    (root / "l7r" / "a.py").write_text(body.replace("    n = 0\n", "    n = 0\n    if __debug__:\n        n += 1\n"))
    git("commit", "-qam", "a debug block that is code")
    coded = git("rev-parse", "HEAD")
    assert not ck.counter_only(root, base, coded) and not ck.same_key(root, base, coded)
    (root / "l7r" / "a.py").write_text(body)
    (root / "l7r" / "b.py").write_text("y = 1\n")
    git("add", "-A")
    git("commit", "-qm", "a new engine file")
    assert not ck.counter_only(root, base, git("rev-parse", "HEAD")), "an added file is no counter-only change"
    assert not ck.counter_only(root, base, base), "no engine file differing is not a counter-only delta"
    assert not ck.counter_only(root, base, "nosuchcommit")


def test_the_counter_only_test_reads_the_landing_s_own_engine_list(tmp_path: pathlib.Path) -> None:
    """Feature 446 (the plan review's ruling on D2): a path the landing counts as engine (`land.py`'s `ENGINE`, `l7r/diagram/ci/`
    among them) changed beside a counter block is no counter-only delta - one list, `codeid.ENGINE`, read by both."""
    import importlib.util
    import subprocess

    ck = _load()
    spec = importlib.util.spec_from_file_location("_land_for_446", REPO / "scripts" / "land.py")
    assert spec and spec.loader
    land = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(land)
    assert land.ENGINE is ck._codeid().ENGINE, "the landing and the counter-only test share one list"
    root = tmp_path / "r"
    _engine_tree(root)
    (root / "l7r" / "diagram" / "ci").mkdir(parents=True)

    def git(*a: str) -> str:
        return subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", *a], check=True, capture_output=True, text=True).stdout.strip()

    body = "def f(xs):\n    n = 0\n    return n\n"
    (root / "l7r" / "a.py").write_text(body)
    (root / "l7r" / "diagram" / "ci" / "c.py").write_text("x = 1\n")
    git("init", "-q", "-b", "main")
    git("add", "-A")
    git("commit", "-qm", "engine")
    base = git("rev-parse", "HEAD")
    (root / "l7r" / "a.py").write_text(body.replace("    n = 0\n", '    n = 0\n    if __debug__:\n        OPS["a@f"] += 1\n'))
    (root / "l7r" / "diagram" / "ci" / "c.py").write_text("x = 2\n")
    git("commit", "-qam", "a counter beside a ci change")
    assert not ck.counter_only(root, base, git("rev-parse", "HEAD")), "the ci change is the landing's engine: not counter-only"
