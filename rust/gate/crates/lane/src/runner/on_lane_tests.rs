//! The runner's own hand-in source (461 T53, the coordinator's coverage addition): `on_lane` over a real git common directory - the
//! pool log's `handed_in` line, the done ref naming its commit - and a hand-in whose ref is gone off the lane.

use l7r_gate_core::ci::fixtures::{git, put, scratch};
use serde_json::json;

use super::on_lane;

#[test]
fn a_handed_in_line_whose_done_ref_names_its_commit_is_on_the_runner_s_lane() {
    let dir = scratch("lane-runner-on-lane");
    let clone = dir.path();
    git(clone, &["init", "-q", "-b", "main"]);
    git(clone, &["config", "user.email", "t@t"]);
    git(clone, &["config", "user.name", "t"]);
    put(clone, "x.txt", "x\n");
    git(clone, &["add", "-A"]);
    git(clone, &["commit", "-qm", "461 T01: the hand-in"]);
    let sha = git(clone, &["rev-parse", "HEAD"]);
    git(clone, &["update-ref", "refs/l7r/done/461-T01", &sha]);
    let common = clone.join(".git");
    let gone = "dddddddddd4444444444444444444444444444444";
    let lines = [
        json!({"utc": "u1", "event": "done", "detail": "461 T01", "commit": sha, "handed_in": true}),
        json!({"utc": "u2", "event": "done", "detail": "461 T02", "commit": gone, "handed_in": true}),
    ];
    let text = lines.map(|l| l.to_string()).join("\n");
    std::fs::write(common.join(l7r_shared::builder_queue::LOG), text).unwrap();
    assert_eq!(on_lane(&common).into_iter().collect::<Vec<_>>(), [sha]);
}
