"""tooling tests split out of `tests.test_switches` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

SKILL = Path(__file__).resolve().parents[2]


def _remote(root: Path) -> str:
    return str(json.loads((root / "dev/switches.json").read_text(encoding="utf-8"))["remote"]["state"])


def make(skill: Path, *args: str, home: Path | None = None) -> subprocess.CompletedProcess[str]:
    # THE PARENT RUN'S VARIABLES ARE STRIPPED, and the list is one variable wider than it was.
    #
    # MAKEFLAGS (feature 145): under `make test-full` the parent make exports `COV_FLOORS=1` through
    # MAKEFLAGS, and the fixture's make then inherited it - no `-m "not rolls_map"`, no
    # `--ignore=tests/full` - so these two tests failed in every FULL run and passed everywhere else.
    #
    # FULL and REF_WHY (feature 166): the same defect one variable over, and it hid for the same reason -
    # it can only be seen from inside a FULL run. A variable set on make's COMMAND LINE is exported into
    # the environment of its recipes, so `make done FULL=1` puts FULL=1 in os.environ, the fixture's own
    # `make done` inherits it, and that make meets the FULL prompt with no terminal to answer it and
    # refuses. Clearing MAKEFLAGS never touched it, because FULL arrives as a plain environment variable
    # rather than through the flags. Measured 2026-08-30: this is why the target failed on both FULL runs
    # of feature 166 and passes at every other scope.
    return subprocess.run(
        ["make", "--no-print-directory", "-C", str(skill), *args],
        capture_output=True,
        text=True,
        stdin=subprocess.DEVNULL,
        # ...and HOME, where a test asks: `hooks-test` runs the user-level hook's own suite (`~/.claude/hooks/test-*.sh`) in every
        # repository that has not kept its pass, a fresh fixture's every run - 5.5 s that is not the fixture's (feature 444 T36)
        env={**os.environ, "MAKEFLAGS": "", "MFLAGS": "", "FULL": "", "REF_WHY": "", **({"HOME": str(home)} if home else {})},
    )


# `regressions` left this list with feature 166: the target rebuilt the frozen negative-fixture corpus,
# and the corpus was a set of bad manifests each proving one retired check still fired.
LOCKED_TARGETS = ("cohort", "test-full", "cache-audit", "perf", "perf-gate", "done FULL=1", "ci-check FULL=1", "ci-check TARGET=cohort", "ci-merge FULL=1", "maps SCOPE=all")


@pytest.mark.tooling
@pytest.mark.tooling
def test_make_uses_six_workers_on_a_shared_box_and_every_core_on_codebuild(fixture_skill: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """GM 2026-08-26 (T23): the quick set is as fast on 8 workers as on 22, and the laptop runs several
    sessions at once - so a fixed count everywhere except CodeBuild, which is dedicated and announces itself.
    SIX since feature 213 (FR-009, specs/213 research R4): four full test phases on identical content ran in
    346 s on 4 workers, 301 s on 6 and 297-322 s on 8, and the rule was the smallest count within 10% of the
    fastest. TEN since feature 221 (GM 2026-09-09, specs/221 research R2): the same rule on today's gate -
    49 / 45 / 40 / 45 s at 6 / 8 / 10 / 12 workers - with two concurrent gates at 5.9 GiB under the GM's 8. SIX AGAIN
    since 2026-10-04 (the Makefile's note at XDIST_WORKERS): on the 4-minute suite, under the load the sessions run at,
    10 workers was no faster than 6, and 6 is ~1.4 GB less a gate; quick's rule also picks 6."""
    monkeypatch.delenv("CODEBUILD_BUILD_ID", raising=False)
    assert "-n 6" in make(fixture_skill, "-n", "quick", "CPU_COUNT=22").stdout
    assert "-n 4" in make(fixture_skill, "-n", "quick", "CPU_COUNT=4").stdout, "never more workers than cores (GM 2026-08-26)"
    monkeypatch.setenv("CODEBUILD_BUILD_ID", "diagram-merge:abc")
    assert "-n auto" in make(fixture_skill, "-n", "quick", "CPU_COUNT=4").stdout


@pytest.mark.tooling
@pytest.mark.parametrize("target", ("ci-check", "ci-image", "ci-check FULL=1"))
def test_make_remote_targets_refuse_when_remote_is_off(fixture_skill: Path, target: str) -> None:
    (fixture_skill / "dev/switches.json").write_text(json.dumps({"remote": {"state": "off", "why": "fixture off", "who": "t", "utc": "U"}}), encoding="utf-8")
    p = make(fixture_skill, *target.split())
    assert p.returncode != 0 and "remote is OFF" in p.stderr and "make ci-on" in p.stderr, p.stdout + p.stderr


@pytest.mark.tooling
def test_make_switch_targets_require_a_reason_and_commit(fixture_skill: Path) -> None:
    """The REMOTE switch, which survived feature 185; the scope half went with the lock."""
    root = fixture_skill  # the project is the repository root (feature 329)
    subprocess.run(["git", "-C", str(root), "config", "user.email", "t@t"], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.name", "t"], check=True)
    assert make(fixture_skill, "ci-off").returncode != 0  # no REASON
    p = make(fixture_skill, "ci-off", "REASON=no AWS")
    assert p.returncode == 0 and _remote(fixture_skill) == "off"
    log = subprocess.run(["git", "-C", str(root), "log", "--oneline"], capture_output=True, text=True).stdout
    assert "remote off - no AWS" in log
    p = make(fixture_skill, "switches")
    assert p.returncode == 0 and "no AWS" in p.stdout
    p = make(fixture_skill, "ci-on", "REASON=back on")
    assert p.returncode == 0 and _remote(fixture_skill) != "off"
    log = subprocess.run(["git", "-C", str(root), "log", "--oneline"], capture_output=True, text=True).stdout
    assert log.count("\n") == 2  # two throws/releases, two commits


@pytest.mark.tooling
def test_make_done_short_circuits_on_an_unchanged_gate_key(fixture_skill: Path) -> None:
    from l7r.diagram.ci import state

    root = fixture_skill  # the project is the repository root (feature 329)
    (root / "scripts").mkdir(exist_ok=True)
    # The Makefile's `done` recipe reaches into scripts/, so the fixture must carry what it calls.
    # `check-run-plausible.py` joined that set on 2026-09-05 and the fixture went red immediately -
    # which is the suite doing its job: a guard the fixture cannot find exits non-zero and the
    # short-circuit path fails, so a missing script reads as a broken gate rather than a silent pass.
    # `hooks/lib/usage_log.py` joined it with feature 406: each of those checks records its run through it.
    for script in ("gates/codeid.py", "gates/check-run-plausible.py", "measure/ratchet.py", "gates/commit-run-record.sh", "hooks/lib/usage_log.py"):
        (root / "scripts" / script).parent.mkdir(parents=True, exist_ok=True)
        (root / "scripts" / script).write_bytes((SKILL / "scripts" / script).read_bytes())
    subprocess.run(["git", "-C", str(root), "config", "user.email", "t@t"], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.name", "t"], check=True)
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", "base"], check=True)
    state.write(root, state.GREEN, "done")
    # the hooks stamp fresh too, as a green gate leaves it: with it stale the shortcut runs `hooks-test` first (feature 375
    # amendment 7, FR-032), which this fixture's few guards cannot pass
    subprocess.run([str(SKILL / "scripts/gates/l7r-gate.sh"), "stamp", "--write", "hooks"], cwd=root, check=True, capture_output=True)
    p = make(fixture_skill, "done")
    assert p.returncode == 0 and "already verified" in p.stdout and "reference settlement" not in p.stdout, p.stdout + p.stderr
    (root / "docs").mkdir()
    (root / "docs" / "note.md").write_text("only documentation\n")
    p = make(fixture_skill, "done")
    assert p.returncode == 0 and "already verified" in p.stdout, p.stdout + p.stderr
    assert any(json.loads(f.read_text())["result"] == "already-verified" for f in (fixture_skill / "dev" / "run-log").rglob("*.json"))
    # the GM's second amendment: a Makefile / pyproject / scripts edit does NOT owe the gate (there is no flag in either direction - FR-022)
    (fixture_skill / "pyproject.toml").write_text((fixture_skill / "pyproject.toml").read_text() + "\n# edited\n")
    (fixture_skill / "Makefile").write_text((fixture_skill / "Makefile").read_text() + "\n# edited\n")
    p = make(fixture_skill, "done")
    assert p.returncode == 0 and "already verified" in p.stdout, p.stdout + p.stderr
    # ...but a scripts/ edit leaves the `hooks` stamp stale, and the shortcut runs `hooks-test` before it answers (feature 375
    # amendment 7, FR-032: it answered green while the push refused on that stamp) - here red, this fixture's guards untested
    (root / "scripts" / "x-hooks.sh").write_text("echo guard\n")
    p = make(fixture_skill, "done", home=root.parent)
    assert p.returncode != 0 and "the hooks stamp is stale" in p.stdout and "GUARD WITHOUT A TEST" in p.stdout + p.stderr, p.stdout + p.stderr
    assert "gate green" not in p.stdout, "a red hooks-test is no green gate"
    assert "$(FORCE)" not in (SKILL / "Makefile").read_text()
    # a .py under the skill (even outside l7r/) DOES: the decision says so
    (fixture_skill / ".explain.py").write_text("x = 1\n")
    assert subprocess.run([str(SKILL / "scripts/gates/l7r-gate.sh"), "state", "verified-done"], cwd=root, capture_output=True, check=False).returncode == 1
    # FULL never short-circuits (here it is refused for lack of a terminal, before any prompt - the point is it never said "already verified")
    p = make(fixture_skill, "done", "FULL=1")
    assert "already verified" not in p.stdout


@pytest.mark.tooling
def test_quick_collects_only_the_quick_tree(fixture_skill: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """GM 2026-08-26 (T29): pytest recurses into subdirectories, so the tier, gate and tooling trees are kept out
    of `make quick` ONLY by the explicit --ignore list in QUICK_TREE - this pins that list so a tree added later
    without an ignore, or an ignore dropped, fails here rather than silently re-collecting a thousand items."""
    monkeypatch.delenv("CODEBUILD_BUILD_ID", raising=False)
    cmd = make(fixture_skill, "-n", "quick").stdout
    # tests/tooling joined the list for good on 2026-09-27 (the GM's ruling): it used to be collected whenever the
    # tooling had changed, so it could not be pinned here.
    for tree in ("tests/tier_town", "tests/tier_city", "tests/gate", "tests/full", "tests/tooling"):
        assert f"--ignore={tree}" in cmd, f"{tree} would be collected by make quick"
    # ...and the `tooling` tests that live elsewhere (tests/tools) by their marker
    assert '-m "not rolls_map and not tooling"' in cmd, "a tooling-marked test outside tests/tooling would run in make quick"


@pytest.mark.tooling
def _runs(recipe: str) -> str:
    """The recipe's EXECUTED lines, without its `: "..."` comments.

    The comments are prose and they name flags in order to explain them - feature 237's own comment says why
    `--deselect` filters after collection where an argument restricts before it - and a guard that greps the
    raw text therefore fires on a sentence rather than on a command. What these assertions are about is what
    make would RUN, so that is what they are given.
    """
    return "\n".join(ln for ln in recipe.splitlines() if not ln.strip().startswith(': "'))


def test_the_directory_decides_when_a_test_runs(fixture_skill: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """THE THREE TREES (feature 135, GM 2026-08-27: "the directory into which we added is the thing that inherently
    determines When and under what circumstance that test is run"). Quick collects `tests/` minus the tier, gate,
    tooling and full trees; the gate collects everything but `tests/full`; the full run collects everything and says
    so with `L7R_TESTS_FULL=1`. Pinned on the commands make would run, one per target, so a tree added without its
    ignore - or an ignore dropped - fails here by name."""
    monkeypatch.delenv("CODEBUILD_BUILD_ID", raising=False)
    # (the trees as they stand with the port switch at integrated; at rust-only the gate also leaves out the engine's trees, below)
    quick = _runs(make(fixture_skill, "-n", "quick", "PORT=integrated").stdout)
    gate = _runs(make(fixture_skill, "-n", "test", "PORT=integrated").stdout)
    full = _runs(make(fixture_skill, "-n", "test-full", "PORT=integrated").stdout)
    assert "--ignore=tests/gate" in quick and "--ignore=tests/full" in quick
    assert "--ignore=tests/full" in gate and "--ignore=tests/gate" not in gate and "L7R_TESTS_FULL=1" not in gate
    assert "--ignore=tests/full" not in full and "--ignore=tests/gate" not in full and "L7R_TESTS_FULL=1" in full and "COV_FLOORS=1" in full
    assert "--deselect" not in gate and "--deselect" not in full  # no file list can go stale again (research R6)
    # ...AND AT RUST-ONLY NO PYTHON SETTLEMENT-ENGINE TEST AND NO MAP ROLL (feature 444 FR-023, the GM 2026-11-07)
    rust_only = _runs(make(fixture_skill, "-n", "test", "PORT=rust-only").stdout)
    assert '-m "not rolls_map"' in rust_only  # the engine trees are deleted, not ignored (feature 444 T39)


# ---- feature 174: the /proc readers, which no test could reach through the real filesystem -------
# Both take their reader as an argument or read one file, so both are testable without a live
# process tree - which is why they get unit tests rather than an exemption.
