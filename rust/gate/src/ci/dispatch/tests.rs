//! The five arrows against recorded shapes; what matters most is that no `start_build` happens on any refusal and `stop_build` is only ever called with the id this dispatcher got back.

use std::cell::RefCell;
use std::path::Path;

use serde_json::json;

use super::super::decision::{CHECK, MEASURE, MERGE};
use super::super::fixtures::{commit, git, put, python, repo, secrets, FakeAws, FakeHost};
use super::{
    aws, billed_minutes, cache_location, make_target, operations, registered_operation, run,
    run_image, status_text, verified_lookup, Context, Outcome,
};
use crate::{delta, state};

struct Run {
    client: FakeAws,
    host: FakeHost,
    py: String,
}

impl Run {
    fn new(dir: &Path) -> Self {
        Self {
            client: FakeAws::default(),
            host: FakeHost::default(),
            py: python(dir),
        }
    }

    fn ctx<'a>(
        &'a self,
        dir: &'a Path,
        mode: &'a str,
        scope: &'a str,
        operation: Option<&'a str>,
    ) -> Context<'a> {
        Context {
            root: dir,
            mode,
            scope,
            operation,
            compute: "BUILD_GENERAL1_LARGE",
            no_go: false,
            secrets: Some(secrets()),
            client: Some(&self.client),
            host: &self.host,
            python: &self.py,
            specify: None,
            poll_s: 0,
            events: RefCell::new(Vec::new()),
        }
    }

    fn check(&self, dir: &Path) -> Outcome {
        run(&self.ctx(dir, CHECK, "reference", None)).unwrap()
    }
}

/// Engine work committed, with a green `quick` on it.
fn engine_with_green(dir: &Path, r: &Run) {
    commit(dir, "l7r/diagram/m.py", "x = 2\n");
    state::write(dir, "green-local", "quick", false, &r.py).unwrap();
}

fn no_build(r: &Run) {
    assert_eq!(r.client.called("start_build"), 0);
}

#[test]
fn a_direct_route_starts_no_build() {
    let dir = repo("direct");
    let r = Run::new(&dir);
    commit(&dir, "docs/a.md", "x");
    state::write(&dir, "green-local", "quick", false, &r.py).unwrap();
    let out = r.check(&dir);
    assert_eq!(
        (out.rc, out.verdict.as_str()),
        (1, "REFUSE(route-is-gated)")
    );
    no_build(&r);
    assert!(r.host.said().contains("nothing dispatched"));
}

#[test]
fn a_failed_gate_and_an_edit_after_green_each_refuse_with_their_reason() {
    let dir = repo("red");
    let r = Run::new(&dir);
    commit(&dir, "l7r/diagram/m.py", "x = 2\n");
    state::write(&dir, "failed-gate", "done", false, &r.py).unwrap();
    assert_eq!(r.check(&dir).verdict, "REFUSE(green-local-since-edit)");
    assert!(r.host.said().contains("run `make quick`"));
    no_build(&r);
    let later = Run::new(&dir);
    state::write(&dir, "green-local", "quick", false, &later.py).unwrap();
    put(&dir, "l7r/diagram/m.py", "x = 3\n");
    assert_eq!(later.check(&dir).verdict, "REFUSE(green-local-since-edit)");
    assert!(later.host.said().contains("DIFFERENT code"));
}

#[test]
fn a_merge_conflict_is_caught_locally_before_any_build() {
    let dir = repo("conflict");
    let r = Run::new(&dir);
    git(&dir, &["checkout", "-qb", "other"]);
    commit(&dir, "l7r/diagram/m.py", "x = 9\n");
    git(&dir, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
    git(&dir, &["checkout", "-q", "main"]);
    engine_with_green(&dir, &r);
    let (text, _) = status_text(&r.ctx(&dir, CHECK, "reference", None)).unwrap();
    assert!(text.contains("MERGE CONFLICT with origin/main"));
    assert_eq!(r.check(&dir).verdict, "REFUSE(merge-conflict)");
    no_build(&r);
}

#[test]
fn a_lint_failure_and_a_push_failure_start_no_build() {
    let dir = repo("lint");
    let mut r = Run::new(&dir);
    engine_with_green(&dir, &r);
    r.host
        .make
        .insert("static format typecheck".to_owned(), (1, "E501".to_owned()));
    assert_eq!(r.check(&dir).verdict, "REFUSE(static)");
    assert!(r.host.said().contains("E501"));
    no_build(&r);
    let mut pushless = Run::new(&dir);
    pushless.host.push_rc = 1;
    assert_eq!(pushless.check(&dir).verdict, "REFUSE(mailbox-push)");
    assert!(pushless.host.said().contains("fatal: could not push"));
    no_build(&pushless);
}

#[test]
fn the_full_scope_needs_its_committed_answer() {
    let dir = repo("full");
    let r = Run::new(&dir);
    engine_with_green(&dir, &r);
    let out = run(&r.ctx(&dir, CHECK, "full", None)).unwrap();
    assert_eq!(out.verdict, "REFUSE(full-not-authorized)");
    no_build(&r);
    let sha = git(&dir, &["rev-parse", "HEAD"]);
    put(
        &dir,
        "dev/bypass-log/a.json",
        &json!({"target": "FULL", "outcome": "permitted", "commit": sha, "why": "w"}).to_string(),
    );
    let opened = Run::new(&dir);
    state::write(&dir, "green-local", "quick", false, &opened.py).unwrap();
    assert_eq!(
        run(&opened.ctx(&dir, CHECK, "full", None)).unwrap().verdict,
        "DISPATCHED"
    );
    assert_eq!(
        opened.client.request()["environmentVariablesOverride"][2]["value"],
        "soak FULL=1"
    );
    assert_eq!(
        opened.client.request()["environmentVariablesOverride"][4]["value"],
        "full"
    );
}

#[test]
fn the_breaker_is_reported_with_the_detach_instruction_and_another_denial_as_itself() {
    let dir = repo("breaker");
    let r = Run::new(&dir);
    engine_with_green(&dir, &r);
    *r.client.deny_start.borrow_mut() = Some("codebuild:StartBuild".to_owned());
    assert_eq!(r.check(&dir).verdict, "REFUSE(breaker-tripped)");
    assert!(r.host.said().contains("aws iam detach-user-policy"));
    let other = Run::new(&dir);
    *other.client.deny_start.borrow_mut() = Some("s3:Other".to_owned());
    assert_eq!(other.check(&dir).verdict, "REFUSE(aws-denied)");
    let mut broken = Run::new(&dir);
    broken.client.fail_start = true;
    assert_eq!(
        run(&broken.ctx(&dir, CHECK, "reference", None)).unwrap_err(),
        "throttled"
    );
}

#[test]
fn a_check_dispatches_one_parked_build_and_records_it() {
    let dir = repo("check");
    let r = Run::new(&dir);
    engine_with_green(&dir, &r);
    r.client.pages.borrow_mut().extend([
        json!({"events": [{"message": "hello\n"}, {"message": "world"}], "nextForwardToken": "n1"}),
        json!({"events": [{"message": "last"}], "nextForwardToken": ""}),
    ]);
    let out = r.check(&dir);
    assert_eq!(
        (
            out.rc,
            out.verdict.as_str(),
            out.result.as_str(),
            out.build_id.as_str()
        ),
        (0, "DISPATCHED", "SUCCEEDED", "gm-assistant-check:abc-123")
    );
    assert!((out.minutes - 2.0).abs() < f64::EPSILON);
    assert_eq!(r.client.called("start_build"), 1);
    assert_eq!(r.client.called("stop_build"), 0);
    assert_eq!(r.client.called("put_object go/abc-123"), 1);
    assert_eq!(r.client.called("put_object cache"), 0); // only a build writes the cache a build restores (177 FR-003): the location travels with start_build
    let said = r.host.said();
    assert!(
        said.contains("  | hello\n  | world")
            && said.contains("  | last")
            && said.contains("ci: [IN_PROGRESS]")
            && said.contains("~$0.04"),
    );
    let req = r.client.request();
    assert_eq!(req["projectName"], "gm-assistant-check");
    assert_eq!(req["buildspecOverride"], "# check\n");
    assert_eq!(req["environmentVariablesOverride"][2]["value"], "soak");
    assert!(req["environmentVariablesOverride"][1]["value"]
        .as_str()
        .unwrap()
        .starts_with("session/"));
    assert_eq!(
        req["cacheOverride"]["location"],
        "bucket/cache/gm-assistant-check/reference"
    );
    assert!(req.get("imageOverride").is_none());
    let logs = super::runlog::log_files(&dir, super::runlog::RUN_LOG);
    let entry: serde_json::Value =
        serde_json::from_str(&std::fs::read_to_string(&logs[0]).unwrap()).unwrap();
    assert_eq!(
        (
            entry["result"].as_str(),
            entry["target"].as_str(),
            entry["reason"].as_str()
        ),
        (Some("SUCCEEDED"), Some("ci-check"), Some("soak"))
    );
}

#[test]
fn a_merge_uses_the_merge_project() {
    let dir = repo("merge");
    let r = Run::new(&dir);
    engine_with_green(&dir, &r);
    put(&dir, "specs/9-x/tasks.md", "- [x] T01 done\n");
    put(&dir, "specs/9-x/.faithful", "");
    put(
        &dir,
        ".specify/feature.json",
        "{\"feature_directory\": \"specs/9-x\"}",
    );
    state::write(&dir, "green-local", "quick", false, &r.py).unwrap();
    assert_eq!(
        run(&r.ctx(&dir, MERGE, "reference", None)).unwrap().verdict,
        "DISPATCHED"
    );
    assert_eq!(r.client.request()["projectName"], "gm-assistant-merge");
    assert_eq!(
        r.client.request()["environmentVariablesOverride"][7]["value"],
        "9-x"
    );
}

#[test]
fn a_merge_with_an_open_held_task_is_refused() {
    let dir = repo("open");
    let r = Run::new(&dir);
    engine_with_green(&dir, &r);
    put(&dir, "specs/9-x/tasks.md", "- [ ] T01 open\n");
    put(&dir, "specs/9-x/.faithful", "");
    put(&dir, "specs/9-x/.holding", "T01 open  <- active\n");
    put(
        &dir,
        ".specify/feature.json",
        "{\"feature_directory\": \"specs/9-x\"}",
    );
    state::write(&dir, "green-local", "quick", false, &r.py).unwrap();
    assert_eq!(
        run(&r.ctx(&dir, MERGE, "reference", None)).unwrap().verdict,
        "REFUSE(feature-complete)"
    );
    no_build(&r);
}

#[test]
fn the_custom_image_is_used_once_its_marker_exists_and_a_stale_one_is_named() {
    let dir = repo("image");
    let r = Run::new(&dir);
    let built = git(&dir, &["rev-parse", "HEAD"]);
    r.client.objects.borrow_mut().insert(
        "image/latest.txt".to_owned(),
        format!("{built} 2026").into_bytes(),
    );
    commit(&dir, "Dockerfile.ci", "FROM x\n");
    engine_with_green(&dir, &r);
    assert_eq!(r.check(&dir).verdict, "DISPATCHED");
    assert_eq!(r.client.request()["imageOverride"], "123.dkr.ecr/x:latest");
    assert!(r.host.said().contains("image STALE: Dockerfile.ci changed"));
    let unreadable = Run::new(&dir);
    unreadable
        .client
        .objects
        .borrow_mut()
        .insert("image/latest.txt".to_owned(), b"garbage".to_vec());
    state::write(&dir, "green-local", "quick", false, &unreadable.py).unwrap();
    assert_eq!(unreadable.check(&dir).verdict, "DISPATCHED");
    assert!(!unreadable.host.said().contains("STALE"));
}

#[test]
fn an_operation_is_dispatched_as_itself_and_its_cache_keyed_on_the_registered_name() {
    let dir = repo("op");
    let r = Run::new(&dir);
    engine_with_green(&dir, &r);
    assert_eq!(
        run(&r.ctx(&dir, CHECK, "reference", Some("cohort SEEDS=8")))
            .unwrap()
            .verdict,
        "DISPATCHED"
    );
    let req = r.client.request();
    assert_eq!(
        req["environmentVariablesOverride"][2]["value"],
        "cohort SEEDS=8"
    );
    assert_eq!(req["environmentVariablesOverride"][4]["value"], "operation");
    assert_eq!(
        req["cacheOverride"]["location"],
        "bucket/cache/gm-assistant-check/reference/cohort"
    );
}

#[test]
fn the_cache_location_is_bounded_and_the_registry_is_read() {
    assert_eq!(cache_location("b", "p", "full", None), "b/cache/p/full");
    let dir = repo("reg");
    assert_eq!(
        operations(&dir)[0],
        ("cohort".to_owned(), "expensive".to_owned())
    );
    assert_eq!(
        registered_operation(&dir, Some("cohort SEEDS=9")).as_deref(),
        Some("cohort")
    );
    assert_eq!(registered_operation(&dir, Some("nonsense")), None);
    assert_eq!(registered_operation(&dir, None), None);
}

#[test]
fn a_local_reference_failure_stops_our_build_and_records_the_abort() {
    let dir = repo("abort");
    let mut r = Run::new(&dir);
    engine_with_green(&dir, &r);
    r.host
        .make
        .insert("_reference".to_owned(), (1, "red".to_owned()));
    let out = r.check(&dir);
    assert_eq!(
        (out.verdict.as_str(), out.result.as_str()),
        ("ABORTED(local-reference)", "aborted-local-reference")
    );
    assert_eq!(
        r.client
            .calls
            .borrow()
            .iter()
            .filter(|c| c.starts_with("stop_build"))
            .cloned()
            .collect::<Vec<_>>(),
        ["stop_build gm-assistant-check:abc-123"]
    );
    assert_eq!(r.client.called("put_object"), 0);
    assert_eq!(state::read(&dir).unwrap().unwrap().event, "failed-gate");
}

#[test]
fn a_failed_remote_build_records_failed_gate_and_a_consumed_signal_is_cleaned() {
    let dir = repo("failed");
    let r = Run::new(&dir);
    engine_with_green(&dir, &r);
    *r.client.statuses.borrow_mut() = vec!["FAILED".to_owned()];
    let out = r.check(&dir);
    assert_eq!((out.rc, out.result.as_str()), (1, "FAILED"));
    assert_eq!(state::read(&dir).unwrap().unwrap().event, "failed-gate");
    assert_eq!(r.client.called("delete_object go/abc-123"), 1);
}

#[test]
fn a_verified_record_skips_the_build_and_logs_who_verified_it() {
    let dir = repo("skip");
    let r = Run::new(&dir);
    engine_with_green(&dir, &r);
    let key = delta::engine_key(&dir, "HEAD", &r.py).unwrap();
    let tree = git(&dir, &["merge-tree", "--write-tree", "origin/main", "HEAD"]);
    assert_eq!(
        delta::engine_key(&dir, tree.lines().next().unwrap(), &r.py).unwrap(),
        key
    );
    r.client.objects.borrow_mut().insert(
        format!("verified/{key}.json"),
        json!({"build_id": "b:9", "scope": "full", "utc": "U"})
            .to_string()
            .into_bytes(),
    );
    let out = r.check(&dir);
    assert_eq!((out.rc, out.verdict.as_str()), (0, "SKIP-VERIFIED"));
    no_build(&r);
    let logs = super::runlog::log_files(&dir, super::runlog::RUN_LOG);
    let entry: serde_json::Value =
        serde_json::from_str(&std::fs::read_to_string(&logs[0]).unwrap()).unwrap();
    assert_eq!(
        (entry["result"].as_str(), entry["build_id"].as_str()),
        (Some("skip-verified"), Some("b:9"))
    );
}

#[test]
fn a_green_local_done_vouches_only_for_the_same_engine_content() {
    let dir = repo("local");
    let r = Run::new(&dir);
    commit(&dir, "l7r/diagram/m.py", "x = 2\n");
    state::write(&dir, "green-local", "done", false, &r.py).unwrap();
    let out = r.check(&dir);
    assert_eq!(out.verdict, "SKIP-VERIFIED");
    no_build(&r);
    git(&dir, &["checkout", "-qb", "base", "origin/main"]);
    commit(&dir, "l7r/diagram/other.py", "y = 1\n");
    git(&dir, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
    git(&dir, &["checkout", "-q", "main"]);
    let moved = Run::new(&dir);
    assert_eq!(moved.check(&dir).verdict, "DISPATCHED");
}

#[test]
fn artifacts_land_where_they_belong_and_one_that_vanishes_is_skipped() {
    let dir = repo("artifacts");
    let mut r = Run::new(&dir);
    engine_with_green(&dir, &r);
    r.client.vanish = Some("artifacts/abc-123/gone.txt".to_owned());
    for key in [
        "artifacts/abc-123/perf-log/p.json",
        "artifacts/abc-123/report.txt",
        "artifacts/abc-123/gone.txt",
        "artifacts/abc-123/",
    ] {
        r.client
            .objects
            .borrow_mut()
            .insert(key.to_owned(), b"x".to_vec());
    }
    r.check(&dir);
    assert!(
        dir.join("dev/perf-log/p.json").is_file()
            && dir.join("dev/ci-artifacts/abc-123/report.txt").is_file()
    );
    assert!(!dir.join("dev/ci-artifacts/abc-123/gone.txt").exists());
    assert!(r.host.said().contains("2 artifact file(s) fetched"));
}

#[test]
fn billed_minutes_round_up_and_ignore_the_queue() {
    assert!((billed_minutes(&json!({"phases": [{"phaseType": "QUEUED", "durationInSeconds": 900}, {"phaseType": "BUILD", "durationInSeconds": 61}, {"phaseType": "COMPLETED"}]})) - 2.0).abs() < f64::EPSILON);
    assert!(billed_minutes(&json!({"phases": []})).abs() < f64::EPSILON);
    assert!(
        (billed_minutes(&json!({"phases": [{"phaseType": "BUILD", "durationInSeconds": 1}]}))
            - 1.0)
            .abs()
            < f64::EPSILON
    );
}

#[test]
fn the_status_needs_no_client_and_makes_no_call_on_a_direct_route() {
    let dir = repo("status");
    let r = Run::new(&dir);
    let mut ctx = r.ctx(&dir, CHECK, "reference", None);
    assert_eq!(
        status_text(&ctx).unwrap().1.verdict,
        "REFUSE(route-is-gated)"
    );
    assert_eq!(r.client.called("get_object"), 0);
    ctx.client = None;
    commit(&dir, "l7r/diagram/m.py", "x = 2\n");
    let (text, _) = status_text(&ctx).unwrap();
    assert!(
        text.contains("no local check recorded")
            && text.contains("would-be tree: ")
            && text.contains("route GATED")
    );
    assert_eq!(verified_lookup(&ctx, None).unwrap(), None);
}

#[test]
fn a_run_needs_its_client_and_a_measurement_says_what_mode_it_is() {
    let dir = repo("need");
    let r = Run::new(&dir);
    let mut ctx = r.ctx(&dir, MEASURE, "reference", None);
    ctx.client = None;
    assert!(run(&ctx).is_err() && run_image(&ctx).is_err());
    state::write(&dir, "green-local", "quick", false, &r.py).unwrap();
    let measured = run(&r.ctx(&dir, MEASURE, "reference", None)).unwrap();
    assert_eq!(measured.verdict, "DISPATCHED");
    assert_eq!(r.client.request()["buildspecOverride"], "# measure\n");
}

#[test]
fn the_image_builds_on_the_check_project_with_privilege() {
    let dir = repo("img");
    let r = Run::new(&dir);
    let out = run_image(&r.ctx(&dir, "image", "reference", None)).unwrap();
    assert_eq!((out.rc, out.result.as_str()), (0, "SUCCEEDED"));
    let req = r.client.request();
    assert_eq!(
        (
            req["projectName"].as_str(),
            req["privilegedModeOverride"].as_bool(),
            req["computeTypeOverride"].as_str()
        ),
        (
            Some("gm-assistant-check"),
            Some(true),
            Some("BUILD_GENERAL1_MEDIUM")
        )
    );
    let mut pushless = Run::new(&dir);
    pushless.host.push_rc = 1;
    assert_eq!(
        run_image(&pushless.ctx(&dir, "image", "reference", None))
            .unwrap()
            .verdict,
        "REFUSE(mailbox-push)"
    );
    no_build(&pushless);
}

#[test]
fn the_go_signal_can_be_withheld_and_the_compute_knob_prices_the_run() {
    let dir = repo("nogo");
    let r = Run::new(&dir);
    engine_with_green(&dir, &r);
    let mut ctx = r.ctx(&dir, CHECK, "reference", None);
    ctx.no_go = true;
    ctx.compute = "BUILD_GENERAL1_2XLARGE";
    run(&ctx).unwrap();
    assert_eq!(r.client.called("put_object"), 0);
    assert_eq!(r.client.called("stop_build"), 0);
    assert!(ctx.events.borrow().contains(&"go:withheld".to_owned()));
    assert!(
        r.host.said().contains("~$0.40")
            && r.client.request()["computeTypeOverride"] == "BUILD_GENERAL1_2XLARGE"
    );
}

#[test]
fn the_log_falls_back_to_the_build_uuid_and_drains_what_cloudwatch_still_held() {
    let dir = repo("drain");
    let mut r = Run::new(&dir);
    engine_with_green(&dir, &r);
    r.client.logs = json!({});
    *r.client.statuses.borrow_mut() = vec!["SUCCEEDED".to_owned()];
    r.client.pages.borrow_mut().extend((0..3).map(|n| json!({"events": [{"message": format!("line {n}")}], "nextForwardToken": format!("n{n}")})));
    r.check(&dir);
    assert!(r.host.said().contains("  | line 2"));
    assert!(r
        .client
        .calls
        .borrow()
        .iter()
        .any(|c| c == "get_log_events /aws/codebuild/gm-assistant abc-123"));
}

#[test]
fn an_aws_failure_is_its_text() {
    assert_eq!(
        aws::<()>(Err(super::AwsError::Other("x".to_owned()))),
        Err("x".to_owned())
    );
}

#[test]
fn the_remote_target_is_the_soak_and_a_named_operation_wins() {
    assert_eq!(make_target(None, "reference"), "soak");
    assert_eq!(make_target(None, "full"), "soak FULL=1");
    assert_eq!(make_target(Some("cohort"), "full"), "cohort");
}
