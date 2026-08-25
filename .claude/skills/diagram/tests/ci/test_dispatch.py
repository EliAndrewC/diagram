"""The five arrows, driven against RECORDED AWS responses (T011, T014, T026, T027, T038, T046, T047,
T075, T077). The two assertions that matter most: no `start_build` on any refusal, and `stop_build`
only ever with the id this dispatcher was given."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from l7r.diagram.ci import config, dispatch, state
from l7r.diagram.ci.decision import CHECK, MERGE
from tests.ci.conftest import FakeClient, ScriptedSh, commit, git

S = ".claude/skills/diagram/"


def secrets() -> config.Secrets:
    return config.Secrets("us-east-1", "AK", "SK", "bucket", "123.dkr.ecr/x", "/aws/codebuild/gm-assistant", "PAT", "mem")


def ctx(repo: Path, mode: str = CHECK, client: FakeClient | None = None, sh: ScriptedSh | None = None, scope: str = "reference", operation: str | None = None) -> tuple[dispatch.Context, list[str]]:
    lines: list[str] = []
    c = dispatch.Context(
        root=repo,
        skill=repo / S,
        mode=mode,
        scope=scope,
        operation=operation,
        secrets=secrets(),
        client=client or FakeClient(),
        sh=sh or ScriptedSh(),
        sleep=lambda s: None,
        out=lines.append,
        stream_poll_s=0,
    )
    return c, lines


def engine_delta_with_green(repo: Path, feature: bool = True, monkeypatch: pytest.MonkeyPatch | None = None) -> None:
    commit(repo, S + "l7r/diagram/m.py", "x = 2\n", "engine work")
    state.write(repo, state.GREEN, "quick")
    if feature and monkeypatch is not None:
        d = repo / "specs" / "130-x"
        d.mkdir(parents=True)
        (d / "tasks.md").write_text("- [x] T001 done\n", encoding="utf-8")
        (d / "spec.md").write_text("FAITHFUL\n", encoding="utf-8")
        monkeypatch.setenv("SPECIFY_FEATURE", "130-x")


# ---- refusals: NOTHING touches AWS ---------------------------------------------------------------


def test_direct_route_starts_no_build(repo: Path) -> None:
    commit(repo, "docs/x.md", "docs\n")
    state.write(repo, state.GREEN, "quick")
    c, lines = ctx(repo)
    out = dispatch.run(c)
    assert out.rc == 1 and out.verdict == "REFUSE(route-is-gated)"
    assert "start_build" not in c.client.names()  # type: ignore[union-attr]
    assert any("nothing dispatched" in ln for ln in lines)


def test_failed_gate_refuses_and_names_make_quick(repo: Path) -> None:
    commit(repo, S + "l7r/diagram/m.py", "x = 2\n")
    state.write(repo, state.FAILED, "done")
    c, lines = ctx(repo)
    out = dispatch.run(c)
    assert out.verdict == "REFUSE(green-local-since-edit)" and "start_build" not in c.client.names()  # type: ignore[union-attr]
    assert any("make quick" in ln for ln in lines)


def test_edit_after_green_refuses_with_the_hash_reason(repo: Path) -> None:
    commit(repo, S + "l7r/diagram/m.py", "x = 2\n")
    state.write(repo, state.GREEN, "quick")
    commit(repo, S + "l7r/diagram/m.py", "x = 3\n", "edited after the green run")
    c, lines = ctx(repo)
    out = dispatch.run(c)
    assert out.verdict == "REFUSE(green-local-since-edit)" and any("different code" in ln for ln in lines)
    assert "start_build" not in c.client.names()  # type: ignore[union-attr]


def test_merge_conflict_is_caught_locally_before_any_build(repo: Path) -> None:
    git(repo, "checkout", "-q", "-b", "upstream")
    commit(repo, S + "l7r/diagram/m.py", "x = 'main'\n", "main-side")
    git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
    git(repo, "checkout", "-q", "main")
    commit(repo, S + "l7r/diagram/m.py", "x = 'ours'\n", "ours")
    state.write(repo, state.GREEN, "quick")
    c, lines = ctx(repo)
    out = dispatch.run(c)
    assert out.verdict == "REFUSE(merge-conflict)" and "start_build" not in c.client.names()  # type: ignore[union-attr]
    assert any("MERGE CONFLICT" in ln for ln in lines)


def test_lint_failure_starts_no_build(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine_delta_with_green(repo, True, monkeypatch)
    sh = ScriptedSh(make={"lint format typecheck": (1, "ruff: E999")})
    c, lines = ctx(repo, sh=sh)
    out = dispatch.run(c)
    assert out.verdict == "REFUSE(lint)" and c.client.calls == [("get_object", c.client.calls[0][1])]  # type: ignore[union-attr]
    assert any("lint/format/types FAILED" in ln for ln in lines)


def test_mailbox_push_failure_starts_no_build(repo: Path) -> None:
    engine_delta_with_green(repo, False)
    c, _ = ctx(repo, sh=ScriptedSh(push_rc=1))
    assert dispatch.run(c).verdict == "REFUSE(mailbox-push)" and "start_build" not in c.client.names()  # type: ignore[union-attr]


def test_full_scope_without_the_committed_answer_is_refused(repo: Path) -> None:
    engine_delta_with_green(repo, False)
    c, lines = ctx(repo, scope="full")
    assert dispatch.run(c).verdict == "REFUSE(full-not-authorized)" and "start_build" not in c.client.names()  # type: ignore[union-attr]


def test_merge_with_open_tasks_is_refused(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine_delta_with_green(repo, True, monkeypatch)
    (repo / "specs" / "130-x" / "tasks.md").write_text("- [ ] T009 still open\n", encoding="utf-8")
    c, lines = ctx(repo, mode=MERGE)
    assert dispatch.run(c).verdict == "REFUSE(feature-complete)" and "start_build" not in c.client.names()  # type: ignore[union-attr]
    assert any("T009 still open" in ln for ln in lines)


def test_the_breaker_is_reported_with_the_detach_instruction(repo: Path) -> None:
    engine_delta_with_green(repo, False)
    c, lines = ctx(repo, client=FakeClient(deny_start=True))
    out = dispatch.run(c)
    assert out.verdict == "REFUSE(breaker-tripped)"
    assert any("hard stop has TRIPPED" in ln for ln in lines) and any("detach-user-policy" in ln for ln in lines)
    assert "stop_build" not in c.client.names()  # type: ignore[union-attr]


# ---- the happy path, and the parked-build abort ----------------------------------------------------


def test_check_dispatches_exactly_one_build_and_records_it(repo: Path) -> None:
    engine_delta_with_green(repo, False)
    client = FakeClient(artifacts={})
    c, lines = ctx(repo, client=client)
    out = dispatch.run(c)
    assert out.rc == 0 and out.result == "SUCCEEDED" and out.build_id.startswith("gm-assistant-check:")
    names = client.names()
    assert names.count("start_build") == 1 and "stop_build" not in names
    kw = next(k for n, k in client.calls if n == "start_build")
    assert kw["projectName"] == config.PROJECT_CHECK and "# check" in kw["buildspecOverride"] and kw["computeTypeOverride"] == config.COMPUTE_TYPE
    env = {e["name"]: e["value"] for e in kw["environmentVariablesOverride"]}
    assert env["MAKE_TARGET"] == "done" and env["MAILBOX"] == "session/clone" and env["CI_SCOPE"] == "reference" and env["GIT_SHA"] == git(repo, "rev-parse", "HEAD")
    assert ("put_object", f"go/{out.build_id}") in client.calls, "the build is released only after the reference check"
    assert c.events == ["lint:0", "push:0", f"start_build:{out.build_id}", "reference:0", "go"]
    logs = [json.loads(p.read_text(encoding="utf-8")) for p in (repo / S / "dev" / "run-log").glob("*.json")]
    assert len(logs) == 1 and logs[0]["where"] == "codebuild" and logs[0]["build_id"] == out.build_id and logs[0]["result"] == "SUCCEEDED" and logs[0]["minutes"] == 1.0
    assert any(ln.startswith("  | ") for ln in lines), "the build log streams into the output"
    assert state.read(repo).event == state.GREEN  # type: ignore[union-attr]


def test_merge_uses_the_merge_project_and_full_scope_travels(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine_delta_with_green(repo, True, monkeypatch)
    sha = git(repo, "rev-parse", "--short", "HEAD")
    (repo / S / "dev" / "bypass-log" / "p.json").write_text(json.dumps({"target": "ci-merge FULL", "commit": sha, "outcome": "permitted", "why": "end of feature"}), encoding="utf-8")
    client = FakeClient()
    c, _ = ctx(repo, mode=MERGE, client=client, scope="full")
    out = dispatch.run(c)
    assert out.rc == 0
    kw = next(k for n, k in client.calls if n == "start_build")
    env = {e["name"]: e["value"] for e in kw["environmentVariablesOverride"]}
    assert kw["projectName"] == config.PROJECT_MERGE and env["MAKE_TARGET"] == "done FULL=1" and env["CI_SCOPE"] == "full"


def test_an_operation_target_is_dispatched_as_itself(repo: Path) -> None:
    engine_delta_with_green(repo, False)
    client = FakeClient()
    c, _ = ctx(repo, client=client, operation="cohort N=48")
    assert dispatch.run(c).rc == 0
    env = {e["name"]: e["value"] for e in next(k for n, k in client.calls if n == "start_build")["environmentVariablesOverride"]}
    assert env["MAKE_TARGET"] == "cohort N=48" and env["CI_SCOPE"] == "operation"


def test_local_reference_failure_stops_OUR_build_and_records_the_abort(repo: Path) -> None:
    engine_delta_with_green(repo, False)
    client = FakeClient()
    c, lines = ctx(repo, client=client, sh=ScriptedSh(make={"reference": (1, "reference settlement (Inashiro, seed 4): FAILING")}))
    out = dispatch.run(c)
    assert out.rc == 1 and out.verdict == "ABORTED(local-reference)"
    stops = [i for n, i in client.calls if n == "stop_build"]
    assert stops == [out.build_id], "only the id this dispatcher got back is ever stopped"
    assert "put_object" not in client.names(), "no go signal"
    assert state.read(repo).event == state.FAILED  # type: ignore[union-attr]
    entry = json.loads(next((repo / S / "dev" / "run-log").glob("*.json")).read_text(encoding="utf-8"))
    assert entry["result"] == "aborted-local-reference" and entry["minutes"] == 1.0
    assert any("stopped" in ln for ln in lines)


def test_a_failed_remote_build_records_failed_gate(repo: Path) -> None:
    engine_delta_with_green(repo, False)
    client = FakeClient(statuses=["IN_PROGRESS", "FAILED"])
    c, _ = ctx(repo, client=client)
    out = dispatch.run(c)
    assert out.rc == 1 and out.result == "FAILED"
    assert state.read(repo).event == state.FAILED  # type: ignore[union-attr]
    assert "stop_build" not in client.names()


def test_skip_verified_pushes_nothing_and_logs_the_build(repo: Path) -> None:
    engine_delta_with_green(repo, False)
    tree = git(repo, "merge-tree", "--write-tree", "origin/main", "HEAD").splitlines()[0]
    client = FakeClient(verified={f"verified/{tree}.json": json.dumps({"tree": tree, "build_id": "gm-assistant-check:earlier", "scope": "reference", "utc": "x"}).encode()})
    c, lines = ctx(repo, client=client)
    out = dispatch.run(c)
    assert out.rc == 0 and out.verdict == "SKIP-VERIFIED" and "start_build" not in client.names()
    entry = json.loads(next((repo / S / "dev" / "run-log").glob("*.json")).read_text(encoding="utf-8"))
    assert entry["result"] == "skip-verified" and entry["build_id"] == "gm-assistant-check:earlier" and entry["cost_usd"] == 0
    # a reference-scope record does NOT satisfy a FULL dispatch (FR-027)
    (repo / S / "dev" / "bypass-log" / "p.json").write_text(
        json.dumps({"target": "ci-check FULL", "commit": git(repo, "rev-parse", "--short", "HEAD"), "outcome": "permitted", "why": "w"}), encoding="utf-8"
    )
    c2, _ = ctx(repo, client=FakeClient(verified=dict(client.objects)), scope="full")
    assert dispatch.run(c2).verdict == "DISPATCHED"


def test_artifacts_land_in_perf_log_and_ci_artifacts(repo: Path) -> None:
    engine_delta_with_green(repo, False)
    fx = json.loads((Path(__file__).parent / "fixtures" / "start_build.json").read_text(encoding="utf-8"))
    uuid = fx["build"]["id"].split(":")[-1]
    client = FakeClient(artifacts={f"artifacts/{uuid}/perf-log/20260825T000000Z-130-end-codebuild.json": b"{}", f"artifacts/{uuid}/report/cohort.txt": b"48 seeds", f"artifacts/{uuid}/": b""})
    c, _ = ctx(repo, client=client, scope="reference")
    assert dispatch.run(c).rc == 0
    assert (repo / S / "dev" / "perf-log" / "20260825T000000Z-130-end-codebuild.json").is_file()
    assert (repo / S / "dev" / "ci-artifacts" / uuid / "report" / "cohort.txt").read_bytes() == b"48 seeds"


def test_billed_minutes_rounds_up_and_ignores_queue_time() -> None:
    build = {
        "phases": [
            {"phaseType": "SUBMITTED", "durationInSeconds": 0},
            {"phaseType": "QUEUED", "durationInSeconds": 500},
            {"phaseType": "PROVISIONING", "durationInSeconds": 7},
            {"phaseType": "BUILD", "durationInSeconds": 61},
            {"phaseType": "COMPLETED"},
        ]
    }
    assert dispatch.billed_minutes(build) == 2.0
    assert dispatch.billed_minutes({"phases": []}) == 0.0


def test_status_text_makes_no_aws_call_on_a_direct_route(repo: Path) -> None:
    commit(repo, "docs/x.md", "docs\n")
    client = FakeClient()
    c, _ = ctx(repo, client=client)
    text, d = dispatch.status_text(c)
    assert "route DIRECT" in text and client.calls == [] and d.verdict.startswith("REFUSE")


def test_status_text_without_a_client_still_reports(repo: Path) -> None:
    commit(repo, S + "l7r/diagram/m.py", "x = 2\n")
    c, _ = ctx(repo)
    c.client = None
    text, _ = dispatch.status_text(c)
    assert "route GATED" in text and "no verified record" in text


def test_run_image_builds_on_the_check_project_with_privilege(repo: Path) -> None:
    client = FakeClient()
    c, _ = ctx(repo, mode="image", client=client)
    out = dispatch.run_image(c)
    assert out.rc == 0
    kw = next(k for n, k in client.calls if n == "start_build")
    assert kw["projectName"] == config.PROJECT_CHECK and kw["privilegedModeOverride"] is True and "# image" in kw["buildspecOverride"]
    c2, _ = ctx(repo, mode="image", sh=ScriptedSh(push_rc=1))
    assert dispatch.run_image(c2).verdict == "REFUSE(mailbox-push)"


def test_default_sh_runs_a_real_command(tmp_path: Path) -> None:
    rc, out = dispatch.default_sh(["sh", "-c", "echo $CI_T; exit 3"], tmp_path, {"CI_T": "hello"})
    assert rc == 3 and out.strip() == "hello"


def test_verified_lookup_shapes(repo: Path) -> None:
    c, _ = ctx(repo, client=FakeClient(verified={"verified/t.json": b'{"build_id": "b", "scope": "full"}'}))
    rec = dispatch.verified_lookup(c, "t")
    assert rec is not None and rec.tree == "t" and rec.scope == "full" and rec.build_id == "b"
    assert dispatch.verified_lookup(c, None) is None and dispatch.verified_lookup(c, "missing") is None


def test_stream_falls_back_to_the_build_uuid_as_stream_name(repo: Path) -> None:
    client = FakeClient(statuses=["SUCCEEDED"])
    c, lines = ctx(repo, client=client)
    build = dispatch.stream(c, "gm-assistant-check:uuid-1")
    assert build["buildStatus"] == "SUCCEEDED" and any(ln.startswith("ci: [") for ln in lines)
