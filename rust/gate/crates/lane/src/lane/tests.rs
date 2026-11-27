//! `l7r-gate lane status` (feature 461 T11) on a real repository: an empty lane, a waiting hand-in, one landed on `origin/main`,
//! an open batch, the last landed batch and a repair open; outside a repository; a verb not yet built.

use l7r_gate_core::ci::fixtures::{git, put, repo};
use serde_json::json;

use super::cli;
use crate::log;

fn words(a: &[&str]) -> Vec<String> {
    a.iter().map(|s| (*s).to_owned()).collect()
}

#[test]
fn a_verb_the_lane_lacks_is_refused_with_its_usage() {
    for args in [vec![], words(&["start"])] {
        let said = cli(&args, std::path::Path::new("."));
        assert_eq!(said.code, 2);
        assert!(said.stderr.starts_with("usage: l7r-gate lane status"));
    }
}

#[test]
fn outside_a_repository_status_is_an_error_naming_the_directory() {
    let dir = l7r_gate_core::ci::fixtures::scratch("lane-no-repo");
    let said = cli(&words(&["status"]), dir.path());
    assert_eq!(said.code, 1);
    assert!(said.stderr.contains("is in no git repository"));
}

#[test]
fn an_empty_lane_is_read_without_writing_anything() {
    let dir = repo("lane-empty");
    let said = cli(&words(&["status"]), dir.path());
    assert_eq!(said.code, 0);
    assert_eq!(
        said.stdout,
        "lane: 0 hand-in(s) on the lane, 0 waiting\nlane: no batch open\nlane: no batch landed yet\nlane: no repair open\n"
    );
    assert!(!dir.path().join(".git").join(log::DIR).exists());
}

#[test]
fn status_lists_each_hand_in_s_state_the_open_batch_the_last_landed_and_the_repairs() {
    let dir = repo("lane-status");
    let root = dir.path();
    let common = root.join(".git");
    let sha = |rel: &str, subject: &str| {
        put(root, rel, subject);
        git(root, &["add", "-A"]);
        git(root, &["commit", "-qm", subject]);
        git(root, &["rev-parse", "HEAD"])
    };
    // three hand-ins on a side branch: one waiting, one in a batch, one that reached origin/main
    git(root, &["checkout", "-qb", "side"]);
    let waiting = sha("w.txt", "461 T01: the waiting one");
    let batched = sha("b.txt", "461 T02: the batched one");
    let landed = sha("l.txt", "461 T03: the landed one");
    git(root, &["checkout", "-q", "main"]);
    git(root, &["cherry-pick", &landed]);
    git(root, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
    for (task, c) in [("T01", &waiting), ("T02", &batched), ("T03", &landed)] {
        git(
            root,
            &["update-ref", &format!("refs/l7r/done/461-{task}"), c],
        );
    }
    let pool: String = [("T01", &waiting), ("T02", &batched), ("T03", &landed)]
        .iter()
        .map(|(t, c)| {
            json!({"utc": "2026-11-28T01:00:00Z", "event": "done", "detail": format!("461 {t}"), "commit": c, "handed_in": true})
                .to_string()
                + "\n"
        })
        .collect();
    std::fs::write(common.join(l7r_shared::builder_queue::LOG), pool).unwrap();
    for (event, fields) in [
        (
            "batch",
            json!({"batch": "461-1", "changes": ["0000000aaa"]}),
        ),
        (
            "eject",
            json!({"batch": "461-1", "change": "0000000aaa", "repair": "r1", "why": "red"}),
        ),
        (
            "landed",
            json!({"batch": "461-1", "landed": [], "ejected": ["0000000aaa"], "runs": 2, "minutes": 6.5}),
        ),
        (
            "batch",
            json!({"batch": "461-2", "changes": [&batched[..10]]}),
        ),
        ("carry", json!({"batch": "461-2", "code": 0})),
    ] {
        log::append(&common, "2026-11-28T02:00:00Z", event, &fields).unwrap();
    }
    let said = cli(&words(&["status"]), root);
    assert_eq!(said.code, 0, "{}", said.stderr);
    assert_eq!(
        said.stdout,
        format!(
            "lane: 2 hand-in(s) on the lane, 1 waiting\n  461 T01  {}  waiting  2026-11-28T01:00:00Z  \"461 T01: the waiting one\"\n  461 T02  {}  in batch 461-2  2026-11-28T01:00:00Z  \"461 T02: the batched one\"\nlane: batch 461-2 gating 1, 1 change(s)\nlane: the last landed batch 461-1: 0 landed, 1 ejected, 2 run(s), 6.5 minutes\nlane: repairs open: r1\n",
            &waiting[..10],
            &batched[..10]
        )
    );
}
