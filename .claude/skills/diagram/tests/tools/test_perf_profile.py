"""Tier 2 of the performance evidence (`tools/perf_profile.py`) - cProfile one stage of one seed.

Feature 174, under the GM's 2026-09-02 ruling. The module had never been measured and its own
docstring claimed exemption; that claim is gone.

What matters here is the DEGRADATION contract (FR-011b): the raw `.prof` goes to a gitignored
directory and, when an archive repository is configured, is pushed there - and when the push fails
for any reason, the derived table is still written and the tool still succeeds. A perf tool that
took the gate down because a remote was unreachable would be uninstalled within a week.

`tooling`: it runs a real generator stage and writes files.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from l7r.diagram.tools import perf_profile

pytestmark = pytest.mark.tooling


def test_the_archive_url_is_overridable_and_an_EMPTY_value_disables_it(monkeypatch: pytest.MonkeyPatch) -> None:
    """An empty `PERF_ARCHIVE` is not "unset" - it is the documented off switch, and the status line
    has to say the derived table stands on its own rather than implying a push happened."""
    monkeypatch.delenv("PERF_ARCHIVE", raising=False)
    assert perf_profile._archive_url() == perf_profile.DEFAULT_ARCHIVE
    assert "configured" in perf_profile.archive_status()

    monkeypatch.setenv("PERF_ARCHIVE", "")
    assert perf_profile._archive_url() == ""
    assert "archive disabled" in perf_profile.archive_status()
    assert "stands on its own" in perf_profile.archive_status()


def test_the_git_environment_carries_the_PAT_through_ASKPASS_never_a_command_line(monkeypatch: pytest.MonkeyPatch) -> None:
    """The token reaches git through GIT_ASKPASS, so it never appears in an argv anybody can read
    from `ps` or a log. When the secrets file is absent the tool degrades to an anonymous clone
    rather than raising - a public archive still works."""
    # THE TEST OWNS ITS ENVIRONMENT, and this is a fix a REMOTE build found (feature 177, build
    # cf341865). `_git_env()` starts from `os.environ`, and a CodeBuild build is handed `GITHUB_TOKEN`
    # as a build environment variable - so in that container the old `if "GITHUB_TOKEN" in env:` fired
    # on the AMBIENT token while `load_secrets` had failed (no `development-secrets.ini` in a build),
    # the `env.update` that sets all three keys never ran, and the assertion died on
    # `KeyError: 'GIT_ASKPASS'`. The old `bare` assertion had the same flaw in the other direction:
    # `"GITHUB_TOKEN" not in bare` is a statement about the ambient environment, not about the
    # function. Neither could fail on a laptop, which is exactly why nothing caught them until the
    # gate ran somewhere nobody lives.
    import l7r.diagram.ci.config as cfg

    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GIT_ASKPASS", raising=False)
    monkeypatch.setattr(cfg, "load_secrets", lambda root: cfg.Secrets("r", "a", "s", "b", "e", "g", "the-pat", "m"))
    env = perf_profile._git_env()
    assert env["GITHUB_TOKEN"] == "the-pat", "the token comes from the secrets file, not from the ambient environment"
    assert env["GIT_ASKPASS"].endswith("git-askpass-token.sh") and env["GIT_TERMINAL_PROMPT"] == "0"

    def missing(*_a: Any, **_kw: Any) -> Any:
        raise FileNotFoundError("no development-secrets.ini")

    monkeypatch.setattr(cfg, "load_secrets", missing)
    bare = perf_profile._git_env()
    assert "GITHUB_TOKEN" not in bare, "no secrets, no token - and no exception"
    assert "GIT_ASKPASS" not in bare, "and nothing half-set: the three keys go in together or not at all"


def test_archive_is_SKIPPED_when_disabled_and_a_failure_DEGRADES_rather_than_raising(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """FR-011b in one test: the archive is best-effort. Both the disabled path and the failed-push
    path return a sentence for the report; neither propagates, because the derived table - the thing
    the finding actually rests on - is committed regardless."""
    raw = tmp_path / "a.prof"
    raw.write_text("x")

    monkeypatch.setenv("PERF_ARCHIVE", "")
    assert perf_profile.archive(str(raw)).startswith("archive skipped")

    monkeypatch.setenv("PERF_ARCHIVE", "https://example.invalid/archive")

    def fail(*_a: Any, **_kw: Any) -> Any:
        raise subprocess.CalledProcessError(1, "git", stderr="fatal: could not read Username")

    monkeypatch.setattr(subprocess, "run", fail)
    said = perf_profile.archive(str(raw))
    assert said.startswith("archive FAILED") and "could not read Username" in said
    assert "committed here regardless" in said


def test_archive_reports_the_push_when_every_git_step_succeeds(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    raw = tmp_path / "b.prof"
    raw.write_text("x")
    monkeypatch.setenv("PERF_ARCHIVE", "https://example.invalid/archive")
    monkeypatch.setattr(perf_profile, "RAW_DIR", str(tmp_path))
    seen: list[list[str]] = []

    def ok(cmd: list[str], **_kw: Any) -> Any:
        seen.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(subprocess, "run", ok)
    said = perf_profile.archive(str(raw))
    assert said.startswith("archived b.prof")
    assert any(c[:2] == ["git", "clone"] for c in seen), "a fresh working copy is cloned shallow"
    assert any("push" in c for c in seen)


def test_an_unknown_stage_is_refused_and_NAMES_the_stages_there_are() -> None:
    """A typo'd stage is the common error, so the refusal lists what was available - the alternative
    is a reader running the profiler four more times to guess the spelling."""
    with pytest.raises(SystemExit, match="no stage 'nosuchstage'"):
        perf_profile.profile_stage(5, "nosuchstage")
    try:
        perf_profile.profile_stage(5, "nosuchstage")
    except SystemExit as e:
        assert "the stages are:" in str(e) and "," in str(e)


def test_profiling_the_FIRST_stage_writes_a_raw_prof_and_a_table_that_says_what_it_measured(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The real thing, on the cheapest stage there is. Two properties the head line has to carry, and
    both are honesty rather than data: the profiled time is under cProfile (~+225%, research R2) and
    so is NOT comparable with a snapshot's plain time, and the raw file is gitignored with the
    archive's status named - a reader must not think the `.prof` is committed."""
    monkeypatch.setattr(perf_profile, "RAW_DIR", str(tmp_path / "raw"))
    monkeypatch.setenv("PERF_ARCHIVE", "")
    table, raw = perf_profile.profile_stage(5, "water_frame", top=5)

    assert Path(raw).is_file() and raw.endswith(".prof"), "the raw profile lands on disk"
    assert str(tmp_path) in raw, "in the raw directory, not beside the committed evidence"
    assert "perf-profile seed 5 stage water_frame" in table
    assert "under cProfile" in table and "+225%" in table, "the table says its number is inflated"
    assert "gitignored" in table and "archive disabled" in table
    assert "cumulative" in table or "function calls" in table, "and it carries pstats' own output"


def test_main_writes_the_DERIVED_table_beside_the_snapshots_and_names_it_by_feature(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """The derived table is a few kilobytes and IS committed (FR-011); the filename carries the
    feature number so a later reader can tie the evidence to the work that asked for it. `adhoc` is
    the honest fallback when no feature is exported - not a blank, which would collide."""
    monkeypatch.setattr(perf_profile, "LOG_DIR", str(tmp_path / "log"))
    monkeypatch.setattr(perf_profile, "profile_stage", lambda seed, stage, top: (f"TABLE seed={seed} stage={stage} top={top}\n", "/tmp/x.prof"))
    monkeypatch.setattr(perf_profile, "archive", lambda _raw: "archive skipped: disabled")

    assert perf_profile.main(["--seed", "9", "--stage", "web", "--top", "3", "--feature", "174-one-hundred"]) == 0
    written = list((tmp_path / "log").glob("*.txt"))
    assert len(written) == 1
    assert "-profile-174-seed9-web.txt" in written[0].name, "keyed by feature NUMBER, seed and stage"
    assert written[0].read_text() == "TABLE seed=9 stage=web top=3\n"
    out = capsys.readouterr().out
    assert "TABLE seed=9" in out and "archive skipped" in out, "the archive's verdict is reported, not swallowed"

    monkeypatch.delenv("SPECIFY_FEATURE", raising=False)
    assert perf_profile.main(["--seed", "1", "--stage", "web"]) == 0
    assert any("-profile-adhoc-" in p.name for p in (tmp_path / "log").glob("*.txt")), "no feature exported -> adhoc"


def test_a_LATER_stage_is_profiled_alone_while_the_stages_before_it_are_timed_plainly(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """ "the stage runs ONCE, profiled" - the ones before it still have to run (a stage needs the
    state its predecessors built) but they are timed WITHOUT the profiler, and that plain total is
    reported separately so the two numbers are never added together."""
    monkeypatch.setattr(perf_profile, "RAW_DIR", str(tmp_path / "raw"))
    monkeypatch.setenv("PERF_ARCHIVE", "")
    table, _raw = perf_profile.profile_stage(5, "sink", top=3)
    assert "stage sink" in table
    head = table.splitlines()[0]
    assert "the stages before it took" in head
    plain = float(head.split("took ")[1].split("s")[0])
    assert plain > 0.0, "water_frame and field really ran, unprofiled"


def test_an_EXISTING_archive_checkout_is_pulled_rather_than_recloned(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Cloning afresh every time would re-download the whole archive to add one file; once a working
    copy exists it is fast-forwarded instead. The `.git` directory is the discriminator."""
    raw = tmp_path / "c.prof"
    raw.write_text("x")
    monkeypatch.setenv("PERF_ARCHIVE", "https://example.invalid/archive")
    monkeypatch.setattr(perf_profile, "RAW_DIR", str(tmp_path))
    (tmp_path / "archive" / ".git").mkdir(parents=True)
    seen: list[list[str]] = []

    def ok(cmd: list[str], **_kw: Any) -> Any:
        seen.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(subprocess, "run", ok)
    assert perf_profile.archive(str(raw)).startswith("archived c.prof")
    assert not any(c[:2] == ["git", "clone"] for c in seen), "an existing checkout is not re-cloned"
    assert any("pull" in c for c in seen), "it is fast-forwarded"
    assert any("config" in c and "user.name" in c for c in seen), "and the committer identity is set locally"


def test_the_skill_root_is_put_on_sys_path_when_it_is_not_already_there(monkeypatch: pytest.MonkeyPatch) -> None:
    """The module is run as a script by `make perf-profile`, where the skill root is NOT on the path
    - under pytest it always is, so the import-time branch that fixes that would never otherwise be
    executed. Re-imported with the entry removed, it puts it back."""
    import importlib

    monkeypatch.setattr(sys, "path", [p for p in sys.path if Path(p).resolve() != Path(perf_profile.SKILL).resolve()])
    reloaded = importlib.reload(perf_profile)
    assert Path(reloaded.SKILL).resolve() in [Path(p).resolve() for p in sys.path], "it inserted the skill root"
