//! RED FIRST (feature 451 T182): a tooling fix built in Rust inside the task being landed is recorded as landing with that task. Observed
//! 2026-11-23 (451 T177, `ask:guard-wordings-sleep-and-slot`): `make arbiter-fix-done` wanted the test on main, `LAND=` runs `make
//! land-tooling`, which rightly refuses `rust/`, and the task's own `make land` was refused by the open fix. `LANDING=<task>` takes a fix
//! whose files and test are committed in the clone, writes no done row, and leaves it pending for that task's landing to settle.

use std::path::{Path, PathBuf};

use serde_json::Value;

use super::verbs::committed;
use super::{clone_at, open_fixes, run};

const TEST: &str = "rust/x/src/tests.rs";
const FIX: &str = "rust/x/src/x.rs";

/// An open fix `ask:e1` in 999-x, whose T01 is open and T02 ticked, and the fix's file and test written but not committed.
fn fixture(tag: &str) -> l7r_shared::tempdir::Held<PathBuf> {
    let root = clone_at(tag);
    std::fs::write(
        root.join("specs/999-x/arbiter.jsonl"),
        "{\"trigger\": \"ask:e1\", \"fix\": \"open\", \"tooling_fix\": \"e\"}\n",
    )
    .unwrap();
    std::fs::write(
        root.join("specs/999-x/tasks.md"),
        "# Tasks\n\n- [ ] T01 a\n- [x] T02 b\n",
    )
    .unwrap();
    std::fs::create_dir_all(root.join("rust/x/src")).unwrap();
    std::fs::write(root.join(FIX), "fn x() {}\n").unwrap();
    std::fs::write(root.join(TEST), "fn t() {}\n").unwrap();
    root
}

fn done(root: &Path, extra: &[&str]) -> crate::Reply {
    let mut args = vec!["fix", "done", "ask:e1", "the fix built here", TEST];
    args.extend_from_slice(extra);
    run(root, &args)
}

fn pending(root: &Path) -> Value {
    serde_json::from_str(
        &std::fs::read_to_string(root.join(".git/arbiter-fix-landing.json")).unwrap_or_default(),
    )
    .unwrap_or(Value::Null)
}

#[test]
fn a_fix_committed_with_its_task_waits_for_that_landing() {
    let root = fixture("landing");
    // not on main and no LANDING: the refusal names the route
    let r = done(&root, &[]);
    assert_eq!(r.code, 1);
    assert!(
        r.stderr
            .contains("LANDING=<the task> FILES=\"<the fix's files>\""),
        "{}",
        r.stderr
    );
    // the fix's files and test committed as they stand, first
    let r = done(&root, &["--landing", "T01", "--files", FIX]);
    assert_eq!(r.code, 1);
    assert!(
        r.stderr
            .contains(&format!("{FIX} is not committed as it stands")),
        "{}",
        r.stderr
    );
    committed(&root, FIX);
    committed(&root, TEST);
    for (extra, said) in [
        (vec!["--landing", "T01"], "FILES= names the fix's files"),
        (
            vec!["--landing", "T09", "--files", FIX],
            "T09 is no open task of 999-x",
        ),
        (
            vec!["--landing", "T02", "--files", FIX, "--feature", "999-x"],
            "T02 is no open task of 999-x",
        ),
        (
            vec!["--landing", "T01", "--files", FIX, "--feature", "998"],
            "no feature 998 under specs/",
        ),
    ] {
        let r = done(&root, &extra);
        assert_eq!(r.code, 1, "{extra:?}: {}", r.stderr);
        assert!(r.stderr.contains(said), "{extra:?}: {}", r.stderr);
    }
    let r = run(
        &root,
        &[
            "fix",
            "declined",
            "ask:e1",
            "it overhauls things",
            "--landing",
            "T01",
        ],
    );
    assert!(
        r.stderr.contains("LANDING= settles a fix that is done"),
        "{}",
        r.stderr
    );
    let r = done(&root, &["--bogus", "x"]);
    assert_eq!(r.code, 2, "{}", r.stderr);
    // pending: no done row, the fix still open, its entry kept for the landing
    let r = done(
        &root,
        &["--landing", "T01", "--files", FIX, "--feature", "999"],
    );
    assert_eq!(r.code, 0, "{}", r.stderr);
    assert_eq!(
        r.stdout,
        "arbiter-fix-done: 1 fix(es) pending - ask:e1: each settles as `make land F=999-x T=T01` pushes, its done row in that landing's tick commit\n"
    );
    assert_eq!(open_fixes(&root.join("specs/999-x")).len(), 1);
    let got = pending(&root);
    let entry = &got[0];
    assert_eq!(entry["trigger"], "ask:e1");
    assert_eq!(entry["feature"], "999-x");
    assert_eq!(entry["task"], "T01");
    assert_eq!(entry["home"], "999-x");
    assert_eq!(entry["test"], TEST);
    assert_eq!(entry["files"], serde_json::json!([FIX]));
    assert_eq!(entry["note"], "the fix built here");
}
