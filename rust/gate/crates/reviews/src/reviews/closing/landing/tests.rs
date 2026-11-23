//! A fix pending on its landing (feature 451 T182): the hold it lifts, the rows it writes, put back and forgotten. The landing's own
//! flow - T177's sequence, a fix carried into the tick commit - is the `land` crate's test (`land/tests/fix.rs`).

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::super::super::tests::{dir, put};
use super::super::open_fixes;
use super::{add, fix_hold_landing, forget, pending, settle_landing, PENDING};

fn tasks(t: &[&str]) -> Vec<String> {
    t.iter().map(|s| (*s).to_owned()).collect()
}

/// A clone with open fixes `t1` and `t2` in 200-a, its log's last line unterminated.
fn clone(tag: &str) -> l7r_shared::tempdir::Held<PathBuf> {
    let root = dir(tag);
    std::fs::create_dir_all(root.join(".git")).unwrap();
    put(
        &root,
        "specs/200-a/arbiter.jsonl",
        &format!(
            "{}\n{}",
            json!({"trigger": "t1", "fix": "open", "tooling_fix": "one"}),
            json!({"trigger": "t2", "fix": "open", "tooling_fix": "two"})
        ),
    );
    root
}

fn entry(trigger: &str, task: &str, home: &str) -> Value {
    json!({"trigger": trigger, "feature": "200-a", "task": task, "home": home, "note": format!("{trigger} built"), "test": "tests/t.sh"})
}

fn log(root: &Path) -> String {
    std::fs::read_to_string(root.join("specs/200-a/arbiter.jsonl")).unwrap()
}

#[test]
fn a_pending_fix_lifts_its_landing_s_hold_and_settles_as_it_lands() {
    let root = clone("landing-hold");
    let a = root.join("specs/200-a");
    assert!(pending(&root).is_empty());
    let hold = fix_hold_landing(&a, &root, &tasks(&["T1"]));
    let both = hold.contains("    t1: one\n") && hold.contains("    t2: two\n");
    assert!(both, "{hold}");
    assert!(hold.contains("LANDING=<the task>"), "{hold}");
    add(&root, json!({"trigger": "t1", "note": "replaced"})).unwrap();
    add(&root, entry("t1", "T1", "200-a")).unwrap();
    add(&root, entry("t9", "T1", "201-gone")).unwrap();
    assert_eq!(pending(&root).len(), 2);
    let hold = fix_hold_landing(&a, &root, &tasks(&["T1"]));
    let t2_alone = !hold.contains("t1:") && hold.contains("    t2: two\n");
    assert!(t2_alone, "{hold}");
    assert!(fix_hold_landing(&a, &root, &tasks(&["T2"])).contains("    t1: one\n"));
    add(&root, entry("t2", "T1", "200-a")).unwrap();
    assert_eq!(fix_hold_landing(&a, &root, &tasks(&["T1"])), "");
    let before = log(&root);
    let settled = settle_landing(&root, &a, &tasks(&["T1"]), "2026-11-23T00:00:00Z").unwrap();
    assert_eq!(settled.triggers, ["t1", "t9", "t2"]);
    assert_eq!(
        settled.rows,
        [("t1", "T1"), ("t2", "T1")].map(|(t, k)| (t.to_owned(), k.to_owned()))
    );
    assert!(open_fixes(&a).is_empty());
    let last: Value = serde_json::from_str(log(&root).lines().last().unwrap()).unwrap();
    assert_eq!(
        last,
        json!({"fix_of": "t2", "status": "done", "note": "t2 built (landed with 200-a T1)", "test": "tests/t.sh", "utc": "2026-11-23T00:00:00Z"})
    );
    assert_eq!(settled.homes.len(), 1);
    assert_eq!(
        settled.said(),
        "land: t1 settled in the tick commit (the round arbiter's tooling fix, landed with T1)\n\
         land: t2 settled in the tick commit (the round arbiter's tooling fix, landed with T1)\n"
    );
    settled.undo().unwrap();
    assert_eq!(log(&root), before);
    forget(&root, &tasks(&["t1"])).unwrap();
    assert_eq!(pending(&root).len(), 2);
    forget(&root, &settled.triggers).unwrap();
    assert!(!root.join(".git").join(PENDING).exists());
    forget(&root, &settled.triggers).unwrap();
}

#[test]
fn a_pending_file_unread_or_unwritten_is_said() {
    let root = clone("landing-unwritten");
    put(&root, &format!(".git/{PENDING}"), "not a list");
    assert!(pending(&root).is_empty());
    std::fs::remove_file(root.join(".git").join(PENDING)).unwrap();
    std::fs::create_dir(root.join(".git").join(PENDING)).unwrap();
    assert!(add(&root, entry("t1", "T1", "200-a"))
        .unwrap_err()
        .starts_with(PENDING));
    assert!(forget(&root, &[]).unwrap_err().starts_with(PENDING));
    // a log that cannot be read is said, and nothing settles
    std::fs::remove_dir(root.join(".git").join(PENDING)).unwrap();
    add(&root, entry("t1", "T1", "200-a")).unwrap();
    let a = root.join("specs/200-a");
    let settled = settle_landing(&root, &a, &tasks(&["T1"]), "now").unwrap();
    std::fs::remove_file(a.join("arbiter.jsonl")).unwrap();
    std::fs::create_dir(a.join("arbiter.jsonl")).unwrap();
    assert!(settled.undo().unwrap_err().starts_with(PENDING));
}
