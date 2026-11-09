//! The door opens only to a permitted entry of this work.

use serde_json::json;

use super::super::fixtures::{commit, git, put, repo};
use super::check;

fn entry(dir: &std::path::Path, name: &str, target: &str, outcome: &str, sha: &str) {
    put(
        dir,
        &format!("dev/bypass-log/2026-11/{name}.json"),
        &json!({"target": target, "outcome": outcome, "commit": sha, "why": "w"}).to_string(),
    );
}

#[test]
fn no_entry_at_all_and_entries_that_do_not_count_are_named_apart() {
    let dir = repo("door");
    assert!(check(&dir, "origin/main").1.contains("no FULL entry"));
    put(&dir, "dev/bypass-log/bad.json", "not json");
    entry(&dir, "a", "done", "permitted", "");
    assert!(check(&dir, "origin/main").1.contains("no FULL entry"));
    entry(&dir, "b", "FULL sweep", "cancelled", "");
    assert_eq!(check(&dir, "origin/main").0, false);
    assert!(check(&dir, "origin/main")
        .1
        .contains("no committed `permitted` FULL entry"));
}

#[test]
fn an_entry_from_main_authorizes_nothing_and_one_of_this_work_opens_it() {
    let dir = repo("door2");
    let inherited = git(&dir, &["rev-parse", "HEAD"]);
    entry(&dir, "a", "FULL", "permitted", &inherited);
    entry(&dir, "b", "FULL", "permitted", "");
    entry(
        &dir,
        "c",
        "FULL",
        "permitted",
        "0000000000000000000000000000000000000000",
    );
    assert_eq!(check(&dir, "origin/main").0, false);
    commit(&dir, "x.txt", "1");
    let ours = git(&dir, &["rev-parse", "HEAD"]);
    entry(&dir, "z", "FULL", "permitted", &ours);
    let (ok, why) = check(&dir, "origin/main");
    assert!(ok && why.contains("z.json") && why.ends_with("authorizes FULL: w"));
}
