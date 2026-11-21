//! Quick's checks over what `make task-add` wrote (feature 451 T19): the mask, the comparison, a check that cannot run or is killed, and
//! `QUICK_OK` - refused without a reason, taken and recorded with one.

use super::{failed, introduced, mask, Failure};
use crate::task_add::cli_with;
use crate::task_add::tests::quick_repo;
use crate::tests::{env_of, quiet_census};

fn failure(check: &str, finding: &str) -> Failure {
    Failure {
        check: check.to_owned(),
        finding: finding.to_owned(),
    }
}

#[test]
fn locations_are_masked_and_ids_are_not() {
    assert_eq!(
        mask("a.md:12:3: cites FR-023, line 4 and lines 7"),
        "a.md:#: cites FR-023, line # and lines #"
    );
    assert_ne!(mask("cites FR-023"), mask("cites FR-024"));
    // a finding moved by the box is the same; one more of it is new; a check's other findings are its own
    let without = [
        failure("lint", "t.md:9: x"),
        failure("lint", "failed (exit 1)"),
    ];
    let with = [
        failure("lint", "t.md:11: x"),
        failure("lint", "t.md:12: x"),
        failure("lint", "failed (exit 1)"),
        failure("other", "t.md:11: x"),
    ];
    assert_eq!(
        introduced(&with, &without),
        vec![
            failure("lint", "t.md:12: x"),
            failure("other", "t.md:11: x")
        ]
    );
    assert_eq!(failure("c", "f").shown(), "  c: f\n");
}

#[test]
fn a_check_that_cannot_run_or_is_killed_is_a_failure() {
    let gone = failed("c", Err(std::io::Error::other("no sh")));
    assert_eq!(gone, vec![failure("c", "could not run: no sh")]);
    let killed = std::process::Command::new("sh")
        .args(["-c", "echo said; kill -9 $$"])
        .output();
    assert_eq!(
        failed("c", killed),
        vec![
            failure("c", "failed (killed by a signal)"),
            failure("c", "said")
        ]
    );
}

#[test]
fn quick_ok_without_a_reason_is_refused_and_with_one_is_taken_and_recorded() {
    let census = quiet_census();
    let (_dir, root) = quick_repo("task-add-quick-ok");
    let words = vec!["9001".to_owned()];
    let tasks = root.join("specs/9001-x/tasks.md");
    let before = std::fs::read(&tasks).unwrap();
    let short = cli_with(
        &words,
        &root,
        "cite FR-404",
        &env_of(&[("QUICK_OK", "later")]),
    );
    assert_eq!(short.code, 2);
    assert!(short.stderr.contains("QUICK_OK needs a REASON"));
    assert_eq!(std::fs::read(&tasks).unwrap(), before);
    let why = "the id is defined by a spec landing next";
    let taken = cli_with(&words, &root, "cite FR-404", &env_of(&[("QUICK_OK", why)]));
    assert_eq!(taken.code, 0, "{}", taken.stderr);
    assert!(taken
        .stderr
        .contains("QUICK_OK taken (recorded) - T10 kept"));
    assert!(taken.stderr.contains("cites FR-404"));
    assert!(std::fs::read_to_string(&tasks)
        .unwrap()
        .contains("- [ ] T10 cite FR-404\n"));
    let logged = std::fs::read_dir(&census).unwrap().flatten().any(|e| {
        std::fs::read_to_string(e.path())
            .unwrap_or_default()
            .contains(why)
    });
    assert!(logged, "the escape is recorded in the guard log");
}

#[test]
fn make_that_cannot_start_lists_nothing() {
    let none = super::lines(std::path::Path::new("/nonexistent-dir-of-t19"));
    assert!(none.unwrap_err().starts_with("make -n quick: "));
}

/// A file that cannot be put back raises: a check that leaves the feature's directory read-only, so the plan.md task-add created
/// cannot be removed.
#[test]
fn a_file_that_cannot_be_put_back_raises() {
    let (_dir, root) = quick_repo("task-add-quick-raise");
    l7r_gate_core::ci::fixtures::put(
        &root,
        "Makefile",
        "quick:\n\t@chmod 555 specs/9001-x; false\n",
    );
    let d = root.join("specs/9001-x");
    std::fs::remove_file(d.join("plan.md")).unwrap();
    let raised = cli_with(&["9001".to_owned()], &root, "a line", &env_of(&[]));
    std::process::Command::new("chmod")
        .args(["755", d.to_str().unwrap()])
        .status()
        .unwrap();
    assert_eq!(raised.code, 1, "{}", raised.stderr);
    assert!(raised.stderr.contains("plan.md"), "{}", raised.stderr);
}

/// The tests' escapes go to the crate's scratch log, never the real one (451 T19: a probe of `QUICK_OK` on the real tree left two rows
/// for T37 in `~/.claude/guard-log`; a test that recorded there would leave one at every run). The log is the crate's census BEFORE
/// anything records, the escape lands there, and no file this process wrote in `$HOME/.claude/guard-log` holds it.
#[test]
fn an_escape_taken_by_a_test_lands_in_the_scratch_log_and_not_the_real_one() {
    let (_dir, root) = quick_repo("task-add-quick-log");
    let scratch = l7r_shared::log::dir() == quiet_census();
    assert!(scratch, "a test records into the real guard log");
    let why = "the scratch-log pin of T19's tests";
    let taken = cli_with(
        &["9001".to_owned()],
        &root,
        "cite FR-404",
        &env_of(&[("QUICK_OK", why)]),
    );
    assert_eq!(taken.code, 0, "{}", taken.stderr);
    let holds = |dir: &std::path::Path, own: &dyn Fn(&str) -> bool| {
        std::fs::read_dir(dir)
            .into_iter()
            .flatten()
            .flatten()
            .any(|e| {
                own(&e.file_name().to_string_lossy())
                    && std::fs::read_to_string(e.path())
                        .unwrap_or_default()
                        .contains(why)
            })
    };
    assert!(holds(&quiet_census(), &|_| true), "not in the scratch log");
    let pid = format!("-{}.json", std::process::id());
    let real =
        std::path::Path::new(&std::env::var("HOME").unwrap_or_default()).join(".claude/guard-log");
    let leaked = holds(&real, &|n| n.ends_with(&pid));
    assert!(!leaked, "the real guard log holds a test's escape");
}
