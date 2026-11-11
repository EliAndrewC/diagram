//! The route and a gated push's conditions, on a real repository with a stand-in Python.

use super::super::fixtures::{commit, git, python, repo};
use super::{cli, entry};
use crate::state;

fn ask(dir: &std::path::Path, py: &str, args: &[&str]) -> crate::Reply {
    let owned: Vec<String> = args.iter().map(|s| (*s).to_owned()).collect();
    cli(&owned, dir, py, None)
}

#[test]
fn the_route_is_direct_with_no_engine_code_and_gated_with_it() {
    let dir = repo("route");
    let py = python(&dir);
    commit(&dir, "docs/a.md", "x");
    assert_eq!(ask(&dir, &py, &["status", "--route"]).stdout, "DIRECT\n");
    commit(&dir, "l7r/diagram/m.py", "x = 2\n");
    assert_eq!(ask(&dir, &py, &["status", "--route"]).stdout, "GATED\n");
}

#[test]
fn a_gated_push_needs_a_green_local_done_of_exactly_the_merged_engine_content() {
    let dir = repo("gated");
    let py = python(&dir);
    commit(&dir, "l7r/diagram/m.py", "x = 2\n");
    let none = ask(&dir, &py, &["gated-check"]);
    assert_eq!(none.code, 1);
    assert!(
        none.stdout.contains("no local check recorded") && none.stdout.contains("verdict: REFUSE(")
    );
    state::write(&dir, "failed-gate", "done", false, &py).unwrap();
    assert!(ask(&dir, &py, &["status"])
        .stdout
        .contains("the last gate FAILED"));
    state::write(&dir, "green-local", "quick", false, &py).unwrap();
    let quick = ask(&dir, &py, &["gated-check"]);
    assert!(quick.stdout.contains("no green local `make done`"));
    state::write(&dir, "green-local", "done", false, &py).unwrap();
    let done = ask(&dir, &py, &["gated-check"]);
    assert_eq!(done.code, i32::from(!done.stdout.contains("verdict: PUSH")));
    assert!(done
        .stdout
        .contains("a green local `make done` on exactly the engine content"));
    commit(&dir, "l7r/diagram/m.py", "x = 3\n");
    assert!(ask(&dir, &py, &["gated-check"])
        .stdout
        .contains("the code changed since"));
}

#[test]
fn a_merge_conflict_refuses_before_the_conditions_and_the_usage_says_what_exists() {
    let dir = repo("conflict");
    let py = python(&dir);
    commit(&dir, "l7r/diagram/m.py", "ours = 1\n");
    let head = git(&dir, &["rev-parse", "HEAD"]);
    git(&dir, &["reset", "-q", "--hard", "HEAD~1"]);
    commit(&dir, "l7r/diagram/m.py", "theirs = 1\n");
    git(&dir, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
    git(&dir, &["reset", "-q", "--hard", &head]);
    let got = ask(&dir, &py, &["gated-check"]);
    assert_eq!(got.code, 1);
    assert!(got.stdout.contains("verdict: REFUSE(merge-conflict)"));
    assert_eq!(ask(&dir, &py, &["nonsense"]).code, 2);
}

#[test]
fn an_unreadable_repository_is_an_error_and_the_live_door_refuses_outside_make() {
    let dir = super::super::fixtures::scratch("norepo");
    assert_eq!(ask(&dir, "python3", &["status", "--route"]).code, 2);
    assert_eq!(ask(&dir, "python3", &["status"]).code, 2);
    assert_eq!(ask(&dir, "python3", &["gated-check"]).code, 2);
    assert_eq!(entry(&["status".to_owned()], &dir).code, 2);
}

#[test]
fn every_condition_holding_is_a_push() {
    let row = |passed| super::Condition {
        name: "a",
        passed,
        why: String::new(),
    };
    assert_eq!(super::verdict_of(&[row(true), row(true)]), "PUSH");
    assert_eq!(super::verdict_of(&[row(true), row(false)]), "REFUSE(a)");
}

/// A process table with one make in it, run in `cwd`, or none.
struct Under(Option<String>);

impl crate::ci::via_make::Procs for Under {
    fn ancestry(&self) -> Vec<u32> {
        self.0.iter().map(|_| 1).collect()
    }

    fn comm(&self, _: u32) -> String {
        "make".to_owned()
    }

    fn cwd(&self, _: u32) -> String {
        self.0.clone().unwrap_or_default()
    }

    fn cmdline(&self, _: u32) -> Vec<String> {
        vec!["make".to_owned(), "ci-status".to_owned()]
    }
}

#[test]
fn outside_make_the_route_refuses_and_names_the_target_and_under_it_answers() {
    let dir = repo("no-make");
    let got = super::guarded(&["status".to_owned()], &dir, &Under(None), "python3", None);
    assert_eq!(got.code, 2);
    assert!(got.stderr.contains("make ci-status"));
    let here = Under(Some(dir.display().to_string()));
    let got = super::guarded(&["nonsense".to_owned()], &dir, &here, "python3", None);
    assert!(!got.stderr.contains("make ci-status"));
}
