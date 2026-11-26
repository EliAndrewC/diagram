//! A recording from the wrong tree names the tree that holds the reviewed text (451 T257).

use serde_json::{json, Map, Value};

use super::super::record::{record_blocks, record_task, Stop};
use super::super::sections::{block_digest, blocks, digest, task_sections};
use super::super::tests::{feature_at, git, repo, within, PLAN_TASKS};
use super::trees;

fn refusal<T: std::fmt::Debug>(got: Result<T, Stop>) -> String {
    match got.unwrap_err() {
        Stop::Refused(why) | Stop::Declined(why) => why,
    }
}

/// The clone with its plan committed, and a worktree of it whose T05 section and a new block are a builder's.
fn clone_and_worktree() -> (
    l7r_shared::tempdir::TempDir,
    std::path::PathBuf,
    std::path::PathBuf,
) {
    let root = repo();
    let dir = feature_at(&root, Some(PLAN_TASKS), None, "243-x");
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "c"]);
    let wt = root.join("wt");
    git(
        &root,
        &["worktree", "add", "-q", "--detach", wt.to_str().unwrap()],
    );
    let built = PLAN_TASKS.replace("the bath 10 x 8 ft", "the bath 12 x 9 ft")
        + "\n## T07 a new task\n\n- its approach\n";
    std::fs::write(wt.join("specs/243-x/plan.md"), built).unwrap();
    (root, dir, wt)
}

fn worktree_plan(wt: &std::path::Path) -> String {
    std::fs::read_to_string(wt.join("specs/243-x/plan.md")).unwrap()
}

#[test]
fn a_task_recorded_from_the_clone_names_the_worktree_that_holds_its_section() {
    let (_root, dir, wt) = clone_and_worktree();
    let sha = digest(task_sections(&worktree_plan(&wt))["T05"].as_bytes());
    let why = refusal(record_task(
        &dir,
        "T05",
        &json!({"section_sha256": sha, "decisions": [within()]}),
        "spec-fidelity",
        Some("2026-11-25"),
    ));
    let wt = std::fs::canonicalize(&wt).unwrap().display().to_string();
    assert!(why.contains("section_sha256 does not match T05's section"));
    assert!(why.contains(&format!("the text reviewed is in {wt} - record it there: make -C {wt} plan-verdict F=243 TASK=T05 FILE=")), "{why}");
    // a digest no tree holds keeps the message it had, no tree named
    let why = refusal(record_task(
        &dir,
        "T05",
        &json!({"section_sha256": "nope", "decisions": [within()]}),
        "spec-fidelity",
        None,
    ));
    assert!(!why.contains("the text reviewed is in"), "{why}");
}

#[test]
fn blocks_recorded_from_the_clone_name_the_worktree_absent_or_changed() {
    let (_root, dir, wt) = clone_and_worktree();
    let plan = worktree_plan(&wt);
    let all = blocks(&plan);
    let sha_of = |key: &str| block_digest(&all.iter().find(|(k, ..)| k == key).unwrap().1);
    let wt = std::fs::canonicalize(&wt).unwrap().display().to_string();
    let there = format!("the text reviewed is in {wt} - record it there: make -C {wt} plan-verdict F=243 BLOCKS=1 FILE=");
    for key in ["## T07 a new task", "## T05 the bath (amendment 1)"] {
        let mut named = Map::new();
        named.insert(key.to_owned(), Value::from(sha_of(key)));
        let why = refusal(record_blocks(
            &dir,
            &json!({"blocks": named, "decisions": []}),
            "spec-fidelity",
            None,
        ));
        assert!(why.contains(&there), "{key}: {why}");
    }
    let why = refusal(record_blocks(
        &dir,
        &json!({"blocks": {"## T07 a new task": "nope"}, "decisions": []}),
        "spec-fidelity",
        None,
    ));
    assert!(why.contains("plan.md has no block") && !why.contains("the text reviewed is in"));
}

#[test]
fn the_trees_leave_out_their_own() {
    let (root, _dir, wt) = clone_and_worktree();
    let listed = trees(&root);
    assert_eq!(listed.len(), 1, "{listed:?}");
    assert_eq!(
        std::fs::canonicalize(&listed[0]).unwrap(),
        std::fs::canonicalize(&wt).unwrap()
    );
    assert_eq!(trees(&wt).len(), 1, "from the worktree, the clone");
}
