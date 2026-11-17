//! The wording-only check (feature 449 T131, from `gates/wording.py`): a declared wording-only task refused when a commit since its start
//! changed what runs, `.py` versions put to one `codeid.py --ids` (the fixture's stand-in reads a file's id from its text before a `#`).

use std::path::Path;

use l7r_gate_core::ci::fixtures::{git, put};
use serde_json::json;

use super::{refusal, same_pairs, started};
use crate::tests::{repo, root_of};

const SECTION: &str = "## T01 x\n\n#### T01 Decisions\n\n**Wording only.** the words\n";

fn start(root: &Path, utc: &serde_json::Value) {
    let row = json!({"feature": "9001-x", "task": "T01", "utc": utc});
    let other = json!({"feature": "9001-x", "task": "T02", "utc": "later"});
    std::fs::write(
        root.join(".git/task-starts.jsonl"),
        format!("{row}\nnot json\n{other}\n"),
    )
    .unwrap();
}

fn commit_at(root: &Path, rel: &str, text: &str) {
    put(root, rel, text);
    git(root, &["add", "-A"]);
    let done = std::process::Command::new("git")
        .arg("-C")
        .arg(root)
        .args(["commit", "-qm", "c"])
        .env("GIT_COMMITTER_DATE", "2030-01-01T00:00:00Z")
        .env("GIT_AUTHOR_DATE", "2030-01-01T00:00:00Z")
        .status()
        .unwrap();
    assert!(done.success());
}

#[test]
fn a_wording_only_task_is_refused_only_for_a_change_in_what_runs() {
    let dir = repo("wording");
    let root = root_of(&dir);
    let d = root.join("specs/9001-x");
    let ask = |section: Option<&str>| refusal(&root, &root, &d, "T01", section).unwrap();
    assert_eq!(ask(None), "");
    assert_eq!(ask(Some("## T01 x\n")), "");
    assert!(ask(Some(SECTION)).contains("has no `make task-start`"));
    start(&root, &json!(null));
    assert!(ask(Some(SECTION)).contains("has no `make task-start`"));
    for falsy in [json!(0), json!([]), json!({})] {
        start(&root, &falsy);
        assert!(ask(Some(SECTION)).contains("has no `make task-start`"));
    }
    std::fs::write(
        root.join(".git/task-starts.jsonl"),
        "{\"feature\": \"9001-x\", \"task\": \"T01\"}\n",
    )
    .unwrap();
    assert!(ask(Some(SECTION)).contains("has no `make task-start`"));
    start(&root, &json!("2029-12-31T00:00:00Z"));
    assert_eq!(ask(Some(SECTION)), "");
}

/// A repository whose wording-only task T01 started before the commits the test makes, and its reading of the refusal (feature 449 T167:
/// the one test that held every case took over FR-008's tenth of a second, so the commits since a start are tests of their own).
fn started_before(tag: &str) -> (l7r_guard::shared::tempdir::TempDir, std::path::PathBuf) {
    let dir = repo(tag);
    let root = root_of(&dir);
    start(&root, &json!("2029-12-31T00:00:00Z"));
    (dir, root)
}

#[test]
fn a_comment_the_feature_s_records_and_a_glossary_entry_change_nothing_that_runs() {
    let (_dir, root) = started_before("wording-calm");
    let d = root.join("specs/9001-x");
    let ask = |section: Option<&str>| refusal(&root, &root, &d, "T01", section).unwrap();
    // a comment, the feature's records and a glossary entry change nothing that runs
    commit_at(&root, "scripts/a.py", "x = 1 # a comment\n");
    commit_at(&root, "specs/9001-x/notes.md", "n\n");
    commit_at(
        &root,
        "l7r/diagram/interactive/assets/glossary/w.json",
        "{}\n",
    );
    assert_eq!(ask(Some(SECTION)), "");
}

#[test]
fn code_a_new_file_and_anything_else_change_what_runs_until_a_later_start() {
    let (_dir, root) = started_before("wording-moved");
    let d = root.join("specs/9001-x");
    let ask = |section: Option<&str>| refusal(&root, &root, &d, "T01", section).unwrap();
    // code does, and a new file, and anything else
    commit_at(&root, "docs/x.md", "d\n");
    commit_at(&root, "scripts/a.py", "x = 2\n");
    let said = ask(Some(SECTION));
    assert!(said.contains("but scripts/a.py changed in what runs"));
    // a start after the commits reads none of them
    start(&root, &json!("2031-01-01T00:00:00Z"));
    assert_eq!(ask(Some(SECTION)), "");
    // a start's time not text is read as Python's `str` of it
    start(&root, &json!(true));
    assert!(ask(Some(SECTION)).contains("changed in what runs"));
}

#[test]
fn what_python_raised_raises() {
    let dir = repo("wording-raise");
    let root = root_of(&dir);
    let d = root.join("specs/9001-x");
    std::fs::write(root.join(".git/task-starts.jsonl"), "[1]\n").unwrap();
    assert!(refusal(&root, &root, &d, "T01", Some(SECTION)).is_err());
    std::fs::write(root.join(".git/task-starts.jsonl"), [0xff]).unwrap();
    assert!(refusal(&root, &root, &d, "T01", Some(SECTION)).is_err());
    // outside a repository there is no start log
    assert_eq!(started(&dir, "9001-x", "T01").unwrap(), json!(""));
    // `codeid.py` missing or failing raises
    start(&root, &json!("2029-12-31T00:00:00Z"));
    commit_at(&root, "scripts/a.py", "x = 3\n");
    assert!(refusal(&root, &dir, &d, "T01", Some(SECTION))
        .unwrap_err()
        .contains("could not say"));
    assert_eq!(same_pairs(&dir, &[]).unwrap(), Vec::<bool>::new());
}
