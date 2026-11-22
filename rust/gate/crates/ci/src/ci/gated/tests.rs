//! The route and a gated push's conditions, on a real repository with a stand-in Python.

use super::super::fixtures::{commit, git, put, repo, scratch};
use super::{cli, entry};
use crate::state;

fn ask(dir: &std::path::Path, args: &[&str]) -> crate::Reply {
    let owned: Vec<String> = args.iter().map(|s| (*s).to_owned()).collect();
    cli(&owned, dir, None)
}

#[test]
fn the_route_is_direct_with_no_engine_code_and_gated_with_it() {
    let dir = repo("route");
    commit(&dir, "docs/a.md", "x");
    assert_eq!(ask(&dir, &["status", "--route"]).stdout, "DIRECT\n");
    commit(&dir, "l7r/diagram/m.py", "x = 2\n");
    assert_eq!(ask(&dir, &["status", "--route"]).stdout, "GATED\n");
}

/// A repository whose delta changes engine code: [`repo`]'s, `origin/main` at its first commit, laid out with
/// four git processes where `repo` and the commit took eight (feature 449 T167) - `git init`'s HEAD, object and ref directories and
/// config written without the process, the committer and no automatic maintenance (a process each commit) in the config itself, and
/// `origin/main` the first commit's loose ref copied.
fn engine_delta(tag: &str) -> l7r_shared::tempdir::TempDir {
    let dir = scratch(tag);
    for sub in ["objects", "refs/heads", "refs/remotes/origin"] {
        std::fs::create_dir_all(dir.join(".git").join(sub)).unwrap();
    }
    put(&dir, ".git/HEAD", "ref: refs/heads/main\n");
    put(
        &dir,
        ".git/config",
        "[core]\n\trepositoryformatversion = 0\n\tfilemode = true\n\tbare = false\n\tlogallrefupdates = true\n\
         [user]\n\temail = t@t\n\tname = t\n[maintenance]\n\tauto = false\n",
    );
    commit(&dir, "l7r/diagram/m.py", "x = 1\n");
    std::fs::copy(
        dir.join(".git/refs/heads/main"),
        dir.join(".git/refs/remotes/origin/main"),
    )
    .unwrap();
    commit(&dir, "l7r/diagram/m.py", "x = 2\n");
    dir
}

#[test]
fn a_gated_push_needs_a_green_local_done_of_exactly_the_merged_engine_content() {
    let dir = engine_delta("gated");
    let none = ask(&dir, &["gated-check"]);
    assert_eq!(none.code, 1);
    assert!(
        none.stdout.contains("no local check recorded") && none.stdout.contains("verdict: REFUSE(")
    );
    state::write(&dir, "failed-gate", "done").unwrap();
    assert!(ask(&dir, &["status"])
        .stdout
        .contains("the last gate FAILED"));
}

/// A green local `make quick` in place of `make done`, apart from the checks above (feature 449 T167: the six checks in one test ran
/// over FR-008's tenth of a second).
#[test]
fn a_green_local_quick_is_no_green_local_done() {
    let dir = engine_delta("gated-quick");
    state::write(&dir, "green-local", "quick").unwrap();
    let quick = ask(&dir, &["gated-check"]);
    assert!(quick.stdout.contains("no green local `make done`"));
}

/// The green local `make done` of [`a_gated_push_needs_a_green_local_done_of_exactly_the_merged_engine_content`] and the code moving
/// after it, a test of their own (feature 449 T167: the six checks in one test ran over FR-008's tenth of a second).
#[test]
fn a_green_local_done_pushes_until_the_code_changes() {
    let dir = engine_delta("gated-done");
    state::write(&dir, "green-local", "done").unwrap();
    let done = ask(&dir, &["gated-check"]);
    assert_eq!(done.code, i32::from(!done.stdout.contains("verdict: PUSH")));
    assert!(done
        .stdout
        .contains("a green local `make done` on exactly the engine content"));
    commit(&dir, "l7r/diagram/m.py", "x = 3\n");
    assert!(ask(&dir, &["gated-check"])
        .stdout
        .contains("the code changed since"));
}

#[test]
fn a_merge_conflict_refuses_before_the_conditions_and_the_usage_says_what_exists() {
    let dir = repo("conflict");
    commit(&dir, "l7r/diagram/m.py", "ours = 1\n");
    let head = git(&dir, &["rev-parse", "HEAD"]);
    git(&dir, &["reset", "-q", "--hard", "HEAD~1"]);
    commit(&dir, "l7r/diagram/m.py", "theirs = 1\n");
    git(&dir, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
    git(&dir, &["reset", "-q", "--hard", &head]);
    let got = ask(&dir, &["gated-check"]);
    assert_eq!(got.code, 1);
    assert!(got.stdout.contains("verdict: REFUSE(merge-conflict)"));
    assert_eq!(ask(&dir, &["nonsense"]).code, 2);
}

#[test]
fn an_unreadable_repository_is_an_error_and_the_live_door_refuses_outside_make() {
    let dir = super::super::fixtures::scratch("norepo");
    assert_eq!(ask(&dir, &["status", "--route"]).code, 2);
    assert_eq!(ask(&dir, &["status"]).code, 2);
    assert_eq!(ask(&dir, &["gated-check"]).code, 2);
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
    let got = super::guarded(&["status".to_owned()], &dir, &Under(None), None);
    assert_eq!(got.code, 2);
    assert!(got.stderr.contains("make ci-status"));
    let here = Under(Some(dir.display().to_string()));
    let got = super::guarded(&["nonsense".to_owned()], &dir, &here, None);
    assert!(!got.stderr.contains("make ci-status"));
}
