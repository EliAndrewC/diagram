//! The command line over the same fakes; every route with remote off starts no client.

use std::cell::Cell;
use std::path::Path;

use super::super::aws::Aws;
use super::super::config::Secrets;
use super::super::fixtures::{commit, put, python, repo, FakeAws, FakeHost};
use super::{entry, guarded, parse, real_client, run, LiveHost, World};
use crate::ci::dispatch::Host;
use crate::state;

fn secrets_in(dir: &Path) {
    put(dir, "development-secrets.ini", "[aws]\nci_bucket = b\n");
}

/// Run a command line with a fake client; (exit code, host, how many clients were built).
fn ask(dir: &Path, args: &[&str]) -> (i32, FakeHost, u32) {
    let host = FakeHost::default();
    let built = Cell::new(0);
    let py = python(dir);
    let make = |_: &Secrets| -> Box<dyn Aws> {
        built.set(built.get() + 1);
        Box::new(FakeAws::default())
    };
    let secrets = |root: &Path| -> Result<Secrets, String> {
        std::fs::read_to_string(root.join("development-secrets.ini"))
            .map(|_| crate::ci::fixtures::secrets())
            .map_err(|e| format!("no development-secrets.ini: {e}"))
    };
    let world = World {
        python: &py,
        host: &host,
        clients: &make,
        secrets: &secrets,
        specify: None,
    };
    let code = run(
        &args.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>(),
        dir,
        &world,
    );
    (code, host, built.get())
}

fn remote_off(dir: &Path) {
    put(
        dir,
        "dev/switches.json",
        "{\"remote\": {\"state\": \"off\", \"why\": \"no AWS\", \"who\": \"GM\", \"utc\": \"U\"}}",
    );
}

fn green(dir: &Path, target: &str) {
    state::write(dir, "green-local", target, false, &python(dir)).unwrap();
}

#[test]
fn the_arguments_are_parsed_and_a_wrong_one_named() {
    let words = |w: &[&str]| w.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>();
    let a = parse(&words(&[
        "check",
        "--full",
        "--target",
        "cohort SEEDS=8",
        "--compute",
        "BUILD_GENERAL1_MEDIUM",
        "--no-go",
        "x",
    ]))
    .unwrap();
    assert!(
        a.full
            && a.no_go
            && a.target.as_deref() == Some("cohort SEEDS=8")
            && a.compute.as_deref() == Some("BUILD_GENERAL1_MEDIUM")
            && a.rest == ["x"]
    );
    assert!(parse(&words(&["--route", "status"])).unwrap().route);
    assert!(parse(&words(&["check", "--compute", "nonsense"]))
        .unwrap_err()
        .contains("not a known compute"));
    assert!(
        parse(&words(&["check", "--compute"])).is_err()
            && parse(&words(&["check", "--target"])).is_err()
    );
    assert!(parse(&words(&[]))
        .unwrap_err()
        .contains("a command is needed"));
    assert!(parse(&words(&["nonsense"]))
        .unwrap_err()
        .contains("no such argument"));
    assert!(parse(&words(&["check", "--bogus"])).is_err());
    assert!(parse(&words(&["check", "--compute", "BUILD_GENERAL1_LARGE"])).is_ok());
}

#[test]
fn a_bad_command_line_is_two_and_an_error_along_the_way_is_one() {
    let dir = repo("errors");
    assert_eq!(ask(&dir, &["nonsense"]).0, 2);
    let (code, host, _) = ask(&dir, &["check"]);
    assert_eq!(code, 1);
    assert!(host.told().contains("no development-secrets.ini"));
}

#[test]
fn the_door_and_the_spend_answer() {
    let dir = repo("door");
    let (code, host, _) = ask(&dir, &["door"]);
    assert_eq!(code, 1);
    assert!(host.said().starts_with("bypass-audit: no FULL entry"));
    let (code, host, _) = ask(&dir, &["remote-spend"]);
    assert_eq!(code, 0);
    assert!(host.said().contains("Remote spend"));
}

#[test]
fn the_route_alone_and_the_whole_status() {
    let dir = repo("route");
    secrets_in(&dir);
    let (code, host, built) = ask(&dir, &["status", "--route"]);
    assert_eq!((code, built), (0, 0));
    assert_eq!(host.said(), "DIRECT");
    let (code, host, built) = ask(&dir, &["status"]);
    assert_eq!((code, built), (0, 1));
    assert!(host.said().contains("dispatch conditions") && host.said().contains("Remote spend"));
    commit(&dir, "l7r/diagram/m.py", "x = 2\n");
    remote_off(&dir);
    let (_, host, built) = ask(&dir, &["status", "--route"]);
    assert_eq!((host.said().as_str(), built), ("GATED-LOCAL", 0));
    let (_, _, built) = ask(&dir, &["status"]);
    assert_eq!(built, 0);
}

#[test]
fn a_status_with_no_credentials_still_answers() {
    let dir = repo("nocreds");
    let (code, host, built) = ask(&dir, &["status"]);
    assert_eq!((code, built), (0, 0));
    assert!(host.said().contains("(no AWS lookup:"));
}

#[test]
fn check_and_merge_run_the_dispatcher_and_leave_the_verdict() {
    let dir = repo("run");
    secrets_in(&dir);
    commit(&dir, "l7r/diagram/m.py", "x = 2\n");
    green(&dir, "quick");
    let (code, host, built) = ask(&dir, &["check"]);
    assert_eq!((code, built), (0, 1));
    assert!(host.said().contains("DISPATCH"));
    assert_eq!(
        std::fs::read_to_string(dir.join(".git/ci-verdict")).unwrap(),
        "DISPATCHED\n"
    );
}

#[test]
fn a_cheap_operation_is_refused_as_a_remote_target_and_an_expensive_one_runs() {
    let dir = repo("target");
    secrets_in(&dir);
    commit(&dir, "l7r/diagram/m.py", "x = 2\n");
    green(&dir, "quick");
    let (code, host, built) = ask(&dir, &["check", "--target", "pack-audit"]);
    assert_eq!((code, built), (1, 0));
    assert!(host.said().contains("TARGET='pack-audit' is cheap"));
    assert!(ask(&dir, &["check", "--target", "nonsense"])
        .1
        .said()
        .contains("not a registered operation"));
    assert_eq!(ask(&dir, &["check", "--target", "cohort"]).0, 0);
    let (code, host, _) = ask(&dir, &["merge", "--target", "cohort"]);
    assert_eq!(code, 1);
    assert!(host.told().contains("--target is for ci-check only"));
}

#[test]
fn a_measurement_dispatches_with_no_engine_delta_and_says_what_it_buys() {
    let dir = repo("measure");
    secrets_in(&dir);
    green(&dir, "quick");
    let (code, host, _) = ask(&dir, &["measure", "--compute", "BUILD_GENERAL1_MEDIUM"]);
    assert_eq!(code, 0);
    assert!(host.said().contains("this run buys a NUMBER"));
}

#[test]
fn the_image_runs_on_its_own_path() {
    let dir = repo("image");
    secrets_in(&dir);
    assert_eq!(ask(&dir, &["image"]).0, 0);
}

#[test]
fn with_remote_off_a_paid_target_refuses_names_the_release_and_leaves_a_trail() {
    let dir = repo("off");
    remote_off(&dir);
    for (args, what) in [
        (vec!["check"], "ci-check"),
        (vec!["image"], "ci-image"),
        (vec!["check", "--target", "cohort"], "ci-check"),
    ] {
        let (code, host, built) = ask(&dir, &args);
        assert_eq!((code, built), (1, 0), "{what}");
        assert!(
            host.told().contains("make ci-on REASON=")
                && host.told().contains("recorded as would-have-dispatched")
        );
    }
    assert!(ask(&dir, &["remote-spend"])
        .1
        .said()
        .contains("3 attempt(s)"));
}

#[test]
fn with_remote_off_a_merge_is_local_gated() {
    let dir = repo("gated");
    remote_off(&dir);
    put(&dir, "specs/9-x/tasks.md", "- [x] T01 done\n");
    put(&dir, "specs/9-x/.faithful", "");
    put(
        &dir,
        ".specify/feature.json",
        "{\"feature_directory\": \"specs/9-x\"}",
    );
    commit(&dir, "l7r/diagram/m.py", "x = 2\n");
    green(&dir, "quick");
    let (code, host, built) = ask(&dir, &["merge"]);
    assert_eq!((code, built), (1, 0));
    assert!(
        host.said().contains("nothing landed")
            && host.said().contains("recorded as would-have-dispatched")
    );
    assert_eq!(
        std::fs::read_to_string(dir.join(".git/ci-verdict")).unwrap(),
        "REFUSE(remote-enabled)\n"
    );
    green(&dir, "done");
    let (code, host, _) = ask(&dir, &["merge"]);
    assert_eq!(code, 0);
    assert!(host
        .said()
        .contains("LOCAL-GATED (remote off) - a green local"));
    let unready = repo("unready");
    remote_off(&unready);
    let (code, host, _) = ask(&unready, &["merge"]);
    assert_eq!(code, 1);
    assert!(!host.said().contains("recorded as would-have"));
}

#[test]
fn remote_ok_passes_when_on_and_leaves_a_trail_when_off() {
    let dir = repo("ok");
    assert_eq!(ask(&dir, &["remote-ok", "ci-check"]).0, 0);
    remote_off(&dir);
    for what in [
        vec!["remote-ok"],
        vec!["remote-ok", "ci-image"],
        vec!["remote-ok", "ci-measure"],
    ] {
        let (code, host, _) = ask(&dir, &what);
        assert_eq!(code, 1);
        assert!(host.told().contains("recorded as would-have-dispatched"));
    }
}

#[test]
fn the_live_host_runs_a_real_command_and_reports_a_missing_one() {
    let host = LiveHost;
    assert_eq!(
        host.sh(&["echo", "hi"], Path::new("."), &[("A", "1")]),
        (0, "hi\n".to_owned())
    );
    assert_eq!(host.sh(&["/no/such/program"], Path::new("."), &[]).0, 127);
    host.sleep(0);
    host.out("");
    host.err("");
}

struct Procs(&'static str, String);

impl crate::ci::via_make::Procs for Procs {
    fn ancestry(&self) -> Vec<u32> {
        vec![2]
    }

    fn comm(&self, _pid: u32) -> String {
        self.0.to_owned()
    }

    fn cwd(&self, _pid: u32) -> String {
        self.1.clone()
    }

    fn cmdline(&self, _pid: u32) -> Vec<String> {
        vec![self.0.to_owned()]
    }
}

#[test]
fn outside_this_project_s_make_it_is_refused_and_says_what_to_run() {
    let dir = repo("guard");
    let host = FakeHost::default();
    let world = World {
        python: "x",
        host: &host,
        clients: &real_client,
        secrets: &crate::ci::config::load_secrets,
        specify: None,
    };
    let refused = guarded(
        &["door".to_owned()],
        &dir,
        &Procs("bash", dir.display().to_string()),
        &world,
    );
    assert_eq!(refused.code, 2);
    assert!(refused.stderr.contains("make ci-status"));
    let allowed = guarded(
        &["door".to_owned()],
        &dir,
        &Procs("make", dir.display().to_string()),
        &world,
    );
    assert_eq!(allowed.code, 1);
    assert!(host.said().starts_with("bypass-audit:"));
    let _client = real_client(&crate::ci::fixtures::secrets());
    assert_eq!(entry(&["nonsense".to_owned()], &dir).code, 2);
}
