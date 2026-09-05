"""The five arrows, driven against RECORDED AWS responses (T011, T014, T026, T027, T038, T046, T047,
T075, T077). The two assertions that matter most: no `start_build` on any refusal, and `stop_build`
only ever with the id this dispatcher was given."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from l7r.diagram.ci import config, dispatch, state
from l7r.diagram.ci.decision import CHECK, MERGE
from l7r.diagram.ci.delta import engine_key
from tests.tooling.ci.conftest import FakeClient, ScriptedSh, commit, git

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
    if monkeypatch is not None:
        monkeypatch.delenv("SPECIFY_FEATURE", raising=False)  # a CodeBuild run exports it (build a6e2afe6 failed this suite on exactly that)
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
    sh = ScriptedSh(make={"static format typecheck": (1, "ruff: E999")})
    c, lines = ctx(repo, sh=sh)
    out = dispatch.run(c)
    assert out.verdict == "REFUSE(static)" and c.client.calls == [("get_object", c.client.calls[0][1])]  # type: ignore[union-attr]
    assert any("static/format/types FAILED" in ln for ln in lines)


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


def test_check_dispatches_exactly_one_build_and_records_it(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine_delta_with_green(repo, False, monkeypatch)
    client = FakeClient(artifacts={})
    c, lines = ctx(repo, client=client)
    out = dispatch.run(c)
    assert out.rc == 0 and out.result == "SUCCEEDED" and out.build_id.startswith("gm-assistant-check:")
    names = client.names()
    assert names.count("start_build") == 1 and "stop_build" not in names
    kw = next(k for n, k in client.calls if n == "start_build")
    assert kw["projectName"] == config.PROJECT_CHECK and "# check" in kw["buildspecOverride"] and kw["computeTypeOverride"] == config.COMPUTE_TYPE
    env = {e["name"]: e["value"] for e in kw["environmentVariablesOverride"]}
    assert env["MAKE_TARGET"] == "soak" and env["MAILBOX"] == "session/clone" and env["CI_SCOPE"] == "reference" and env["GIT_SHA"] == git(repo, "rev-parse", "HEAD")
    assert env["SPECIFY_FEATURE"] == "", "no feature named in this fixture"
    uuid = out.build_id.split(":")[-1]
    assert ("put_object", f"go/{uuid}") in client.calls, "the build is released only after the reference check, and the key is the uuid the build polls"
    assert ("delete_object", f"go/{uuid}") in client.calls, "the fake build never consumes its signal, so the dispatcher's leftover cleanup removes it"
    # `cache:<scope>` since feature 175 - the generation cache is configured per (project, scope), and
    # the event records WHICH cache the build was pointed at. It sits beside `image:` because both are
    # start_build overrides decided just before the call.
    assert c.events == ["static:0", "push:0", "image:stock", "cache:reference", f"start_build:{out.build_id}", "reference:0", "go", "go:cleaned"]
    assert "imageOverride" not in kw, "no image marker in the bucket: the stock image bootstraps"
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
    assert kw["projectName"] == config.PROJECT_MERGE and env["MAKE_TARGET"] == "soak FULL=1" and env["CI_SCOPE"] == "full"
    assert env["SPECIFY_FEATURE"] == "130-x", "the build pairs its perf bookends by this feature"


def test_the_custom_image_is_used_once_its_marker_exists(repo: Path) -> None:
    engine_delta_with_green(repo, False)
    client = FakeClient(artifacts={"image/latest.txt": b"abc 2026-08-25"})
    c, _ = ctx(repo, client=client)
    assert dispatch.run(c).rc == 0 and "image:custom" in c.events
    kw = next(k for n, k in client.calls if n == "start_build")
    assert kw["imageOverride"] == "123.dkr.ecr/x:latest" and kw["imagePullCredentialsTypeOverride"] == "SERVICE_ROLE"


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
    # the build died before consuming its go signal (the fake never deletes it): the dispatcher cleans it up
    assert ("delete_object", f"go/{out.build_id.split(':')[-1]}") in client.calls and "go:cleaned" in c.events
    assert state.read(repo).event == state.FAILED  # type: ignore[union-attr]
    assert "stop_build" not in client.names()


def test_skip_verified_pushes_nothing_and_logs_the_build(repo: Path) -> None:
    engine_delta_with_green(repo, False)
    tree = git(repo, "merge-tree", "--write-tree", "origin/main", "HEAD").splitlines()[0]
    key = engine_key(repo, tree)
    client = FakeClient(verified={f"verified/{key}.json": json.dumps({"tree": tree, "engine_key": key, "build_id": "gm-assistant-check:earlier", "scope": "reference", "utc": "x"}).encode()})
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
    # a DOCS commit after the verification keeps the shortcut: the engine content is what was tested
    commit(repo, "docs/after.md", "written after the build\n")
    c3, _ = ctx(repo, client=FakeClient(verified=dict(client.objects)))
    assert dispatch.run(c3).verdict == "SKIP-VERIFIED", "a docs-only change after a green build must not cost a build"


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
    tree = git(repo, "rev-parse", "HEAD^{tree}")
    key = engine_key(repo, tree)
    c, _ = ctx(repo, client=FakeClient(verified={f"verified/{key}.json": b'{"build_id": "b", "scope": "full"}'}))
    rec = dispatch.verified_lookup(c, tree)
    assert rec is not None and rec.tree == tree and rec.scope == "full" and rec.build_id == "b"
    assert dispatch.verified_lookup(c, None) is None
    commit(repo, S + "l7r/diagram/m.py", "x = 'other engine content'\n")
    assert dispatch.verified_lookup(c, git(repo, "rev-parse", "HEAD^{tree}")) is None, "different engine content, no record"


def test_stream_falls_back_to_the_build_uuid_as_stream_name(repo: Path) -> None:
    client = FakeClient(statuses=["SUCCEEDED"])
    c, lines = ctx(repo, client=client)
    build = dispatch.stream(c, "gm-assistant-check:uuid-1")
    assert build["buildStatus"] == "SUCCEEDED" and any(ln.startswith("ci: [") for ln in lines)


def test_an_artifact_key_that_vanishes_between_list_and_get_is_skipped(repo: Path) -> None:
    class Flaky(FakeClient):
        def get_object(self, bucket: str, key: str) -> bytes | None:
            return None if key.startswith("artifacts/") else super().get_object(bucket, key)

    engine_delta_with_green(repo, False)
    fx = json.loads((Path(__file__).parent / "fixtures" / "start_build.json").read_text(encoding="utf-8"))
    uuid = fx["build"]["id"].split(":")[-1]
    c, _ = ctx(repo, client=Flaky(artifacts={f"artifacts/{uuid}/report/x.txt": b"x"}))
    assert dispatch.run(c).rc == 0 and not (repo / S / "dev" / "ci-artifacts").exists()


def test_no_go_withholds_the_signal_and_never_stops_the_build(repo: Path) -> None:
    """FR-036's measurement knob: the build must abort ITSELF; the dispatcher neither releases nor stops it."""
    engine_delta_with_green(repo, False)
    client = FakeClient(statuses=["IN_PROGRESS", "FAILED"])
    c, lines = ctx(repo, client=client)
    c.no_go = True
    out = dispatch.run(c)
    assert out.rc == 1 and "go:withheld" in c.events and "put_object" not in client.names() and "stop_build" not in client.names()
    assert any("WITHHELD" in ln for ln in lines)


def test_the_compute_knob_reaches_the_build_and_prices_the_run(repo: Path) -> None:
    engine_delta_with_green(repo, False)
    client = FakeClient()
    c, lines = ctx(repo, client=client, operation="cohort N=48")
    c.compute = "BUILD_GENERAL1_2XLARGE"
    assert dispatch.run(c).rc == 0
    kw = next(k for n, k in client.calls if n == "start_build")
    env = {e["name"]: e["value"] for e in kw["environmentVariablesOverride"]}
    assert kw["computeTypeOverride"] == "BUILD_GENERAL1_2XLARGE" and env["COMPUTE_TYPE"] == "BUILD_GENERAL1_2XLARGE"
    entry = json.loads(next((repo / S / "dev" / "run-log").glob("*.json")).read_text(encoding="utf-8"))
    assert entry["compute"] == "BUILD_GENERAL1_2XLARGE" and entry["cost_usd"] == round(1.0 * config.RATES["BUILD_GENERAL1_2XLARGE"], 4)
    assert any("on BUILD_GENERAL1_2XLARGE" in ln for ln in lines)


def test_a_green_local_done_on_the_same_engine_content_means_no_build(repo: Path) -> None:
    """GM 2026-08-25: the remote reference gate is the local `make done` plus the merge with main;
    when main adds no engine content, the local verdict stands and the push goes direct."""
    commit(repo, S + "l7r/diagram/m.py", "x = 2\n", "engine work")
    state.write(repo, state.GREEN, "done")
    client = FakeClient()
    c, lines = ctx(repo, client=client)
    out = dispatch.run(c)
    assert out.verdict == "SKIP-VERIFIED" and out.rc == 0 and "start_build" not in client.names()
    assert any("green local `make done`" in ln for ln in lines)
    # docs after the done: still no build
    commit(repo, "docs/x.md", "later\n")
    c2, _ = ctx(repo, client=FakeClient())
    assert dispatch.run(c2).verdict == "SKIP-VERIFIED"


def test_a_local_done_does_not_suffice_when_main_moved_on_engine_paths_or_for_quick_or_for_FULL(repo: Path) -> None:
    commit(repo, S + "l7r/diagram/m.py", "x = 2\n", "engine work")
    state.write(repo, state.GREEN, "quick")
    c, _ = ctx(repo, client=FakeClient())
    assert dispatch.run(c).verdict == "DISPATCHED", "quick is not the gate"
    state.write(repo, state.GREEN, "done")
    # FULL is not a reference-scope verdict
    (repo / S / "dev" / "bypass-log" / "p.json").write_text(
        json.dumps({"target": "ci-check FULL", "commit": git(repo, "rev-parse", "--short", "HEAD"), "outcome": "permitted", "why": "w"}), encoding="utf-8"
    )
    c2, _ = ctx(repo, client=FakeClient(), scope="full")
    assert dispatch.run(c2).verdict == "DISPATCHED"
    # main moves on an ENGINE path after the local done: the merge would test content nobody has seen
    git(repo, "checkout", "-q", "-b", "upstream", "HEAD~1")
    commit(repo, S + "l7r/diagram/other.py", "z = 1\n", "main-side engine change")
    git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
    git(repo, "checkout", "-q", "main")
    c3, _ = ctx(repo, client=FakeClient())
    assert dispatch.run(c3).verdict == "DISPATCHED"


def test_remote_off_reason_reads_the_switch(repo: Path) -> None:
    from l7r.diagram import switches

    assert dispatch.remote_off_reason(repo / S) is None
    switches.write(repo / S, "remote", "off", "budget", who="GM")
    why = dispatch.remote_off_reason(repo / S)
    assert why is not None and "remote is OFF" in why and "budget" in why and "GM" in why and "make ci-on" in why


def test_a_STALE_build_image_is_reported_by_the_files_that_changed(repo: Path) -> None:
    """Feature 174. The dispatcher compares the pushed image's marker commit against HEAD and, when
    one of the image's own inputs has changed since, says so.

    It names the FILES rather than saying "the image is old", because which file changed decides
    whether the staleness matters - a Dockerfile edit is a rebuild, a lockfile bump may not be. The
    line is a DIAGNOSTIC, not a gate: the build still dispatches, and the session is told.
    """
    engine_delta_with_green(repo, False)
    head = git(repo, "rev-parse", "HEAD").strip()
    client = FakeClient(artifacts={"image/latest.txt": f"{head} 2026-08-25".encode()})
    # the git diff against the marker's own commit reports an image input as changed
    c, lines = ctx(repo, client=client, sh=ScriptedSh())
    dispatch.run(c)
    assert "image:custom" in c.events, "the custom image is used"


def test_the_build_log_is_STREAMED_line_by_line_to_the_session(repo: Path) -> None:
    """A remote build's own output is printed as it arrives, prefixed so it reads as the build's
    voice rather than the dispatcher's - without it a paid run is a black box until it ends."""
    engine_delta_with_green(repo, False)
    client = FakeClient()  # its get_log_events answers from the recorded AWS fixture
    c, lines = ctx(repo, client=client)
    dispatch.run(c)
    assert any(n == "get_log_events" for n, _ in client.calls), "the dispatcher asks for the build's log"
    streamed = [ln for ln in lines if ln.startswith("  | ")]
    assert streamed, f"and prints each event prefixed as the build's own voice: {lines[-6:]}"


def test_a_STALE_IMAGE_is_named_by_its_changed_inputs_and_the_dispatch_still_goes(repo: Path) -> None:
    """The image is a derived artifact in ECR with no link back to the files it came from, so the
    marker's commit is diffed against HEAD over the recipe and the two lockfiles. It WARNS: a stale
    image is usually harmless and a rebuild costs the GM about a dollar on a target only they may
    authorize, so the build starts anyway and the line says which file went out of date."""
    engine_delta_with_green(repo, False)
    (repo / "Dockerfile.ci").write_text("FROM base\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "the recipe the image was built from")
    built_at = git(repo, "rev-parse", "HEAD").strip()
    (repo / "Dockerfile.ci").write_text("FROM base\nRUN apt-get install resvg\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "the recipe moved on")

    client = FakeClient(artifacts={"image/latest.txt": f"{built_at} 2026-08-25".encode()})
    c, lines = ctx(repo, client=client)
    assert dispatch.run(c).rc == 0, "a stale image never refuses the dispatch"
    assert "image:stale" in c.events
    assert any("Dockerfile.ci" in ln for ln in lines), f"and the line names the file that went stale: {lines}"


def test_the_log_DRAIN_prints_the_pages_CloudWatch_still_held_when_the_build_ended(repo: Path) -> None:
    """Build 93af6342's log jumped from wait-go to POST_BUILD with the failing command's output
    missing: the poll returned the moment the status was terminal, leaving pages unread. The drain
    keeps reading until a page comes back empty, and this asserts it PRINTS what it finds - a drain
    that read the pages and dropped them would fix nothing."""

    class _TwoPages(FakeClient):
        def get_log_events(self, group: str, stream: str, token: str | None) -> dict[str, Any]:
            self.calls.append(("get_log_events", (group, stream, token)))
            self._log_pages += 1
            if self._log_pages > 2:
                return {"events": [], "nextForwardToken": token}
            return {"events": [{"message": f"page {self._log_pages} line\n"}], "nextForwardToken": f"t{self._log_pages}"}

    client = _TwoPages(statuses=["SUCCEEDED"])
    c, lines = ctx(repo, client=client)
    dispatch.stream(c, "gm-assistant-check:uuid-1")
    assert "  | page 1 line" in lines, "the page the main poll read"
    assert "  | page 2 line" in lines, "and the page only the drain would have reached"


# --- the remote runs the tier the laptop SKIPPED, not the one it just finished (GM 2026-09-05) ------


def _target_ctx(scope: str, operation: str | None = None) -> dispatch.Context:
    """`make_target` reads only scope and operation, so this needs no repo, client or shell."""
    return dispatch.Context(root=Path("."), skill=Path("."), mode=CHECK, scope=scope, operation=operation)


def test_the_remote_target_is_the_soak_not_the_gate() -> None:
    """The whole point of the repoint: a remote build must not re-run `make done`.

    It used to, on the theory that the remote merges the latest main in first and so tests a tree
    nobody has tested. Measured, that property is vestigial - `sync-in` merges main into every clone
    on every message, and every `ci-merge` since the local short-circuit landed on 2026-08-25 has been
    SKIP-VERIFIED. A test that pins `done` here would pin the duplication back in.
    """
    ref = dispatch.make_target(_target_ctx("reference"))
    full = dispatch.make_target(_target_ctx("full"))
    assert ref == "soak" and full == "soak FULL=1"
    assert "done" not in ref and "done" not in full, "a remote build must not repeat the local gate"


def test_a_named_operation_still_wins() -> None:
    """`ci-check TARGET=<op>` is how the compute comparison and the cohort sweeps were taken; the
    repoint must not take that away."""
    assert dispatch.make_target(_target_ctx("operation", "cohort N=48")) == "cohort N=48"
