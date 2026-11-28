//! What the lane holds for its coordinator (feature 461 T21, D9's Stop rule): an open batch, read as the lane crate's `state_of`
//! reads it, and a waiting hand-in while the runner lives - a landed, ejected or superseded one, and phase 1's hand-ins with no
//! runner, holding nothing.

use std::path::Path;
use std::process::Command;

use serde_json::json;

use super::{dir, holds, holds_at, origin_base, FILE, RUNNER_LOCK};
use crate::tempdir::TempDir;
use crate::tool::flock;

fn lane(common: &Path, lines: &[serde_json::Value]) {
    std::fs::create_dir_all(dir(common)).unwrap();
    let text: String = lines.iter().map(|l| l.to_string() + "\n").collect();
    std::fs::write(dir(common).join(FILE), text).unwrap();
}

fn git(repo: &Path, args: &[&str]) -> String {
    let out = Command::new("git")
        .arg("-C")
        .arg(repo)
        .args(args)
        .output()
        .unwrap();
    String::from_utf8_lossy(&out.stdout).trim().to_owned()
}

/// A repository with one empty commit a subject, their shas.
fn repo(t: &TempDir, subjects: &[&str]) -> Vec<String> {
    git(t.path(), &["init", "-q"]);
    let commit = |s: &&str| {
        let who = ["-c", "user.name=t", "-c", "user.email=t@t"];
        let what = ["commit", "-q", "--allow-empty", "-m", s];
        git(t.path(), &[&who[..], &what[..]].concat());
        git(t.path(), &["rev-parse", "HEAD"])
    };
    subjects.iter().map(commit).collect()
}

fn done(commit: &str, detail: &str) -> String {
    format!(
        "{}\n",
        json!({"event": "done", "handed_in": true, "detail": detail, "commit": commit, "utc": "2026-11-28T01:00:00Z"})
    )
}

#[test]
fn an_open_batch_is_held_until_it_lands_or_stops_and_a_resumed_one_again() {
    let t = TempDir::new("lane-holds-batch");
    assert_eq!(holds(t.path()), None);
    let batch = json!({"event": "batch", "batch": "461-1", "changes": ["abcdef1"]});
    lane(t.path(), std::slice::from_ref(&batch));
    assert_eq!(holds(t.path()).as_deref(), Some("batch 461-1 is open"));
    // its own owed line, or another batch's landed line, ends nothing
    let owed = json!({"event": "owed", "batch": "461-1", "line": "x"});
    let other = json!({"event": "landed", "batch": "461-0"});
    lane(t.path(), &[batch.clone(), owed, other]);
    assert_eq!(holds(t.path()).as_deref(), Some("batch 461-1 is open"));
    for end in ["landed", "stop"] {
        let ended = json!({"event": end, "batch": "461-1"});
        lane(t.path(), &[batch.clone(), ended.clone()]);
        assert_eq!(holds(t.path()), None);
        // a carry after a stop: the batch resumed, open again
        let carry = json!({"event": "carry", "batch": "461-1"});
        lane(t.path(), &[batch.clone(), ended, carry]);
        assert_eq!(holds(t.path()).as_deref(), Some("batch 461-1 is open"));
    }
}

#[test]
fn a_waiting_hand_in_is_held_only_while_the_runner_lives() {
    // phase 1's base, named (461 T64: unset is phase 2's)
    crate::env::set("HAND_IN_BASE", "clone");
    let t = TempDir::new("lane-holds-hand-in");
    let shas = repo(&t, &["one", "two"]);
    let common = t.path().join(".git");
    git(t.path(), &["update-ref", "refs/l7r/done/461-T12", &shas[0]]);
    std::fs::write(common.join("builder-pool.log"), done(&shas[0], "461 T12")).unwrap();
    lane(&common, &[json!({"event": "start"})]);
    // phase 1: no runner, the hand-in landed by hand - nothing held
    assert_eq!(holds(&common), None);
    let lock = std::fs::File::create(dir(&common).join(RUNNER_LOCK)).unwrap();
    assert!(flock(&lock, "-x"));
    let want = format!("hand-in 461 T12 ({}) waiting", &shas[0][..10]);
    assert_eq!(holds(&common), Some(want));
    // landed, or ejected, by the lane's own lines: nothing held
    let landed = json!({"event": "landed", "batch": "461-1", "landed": [shas[0]]});
    lane(&common, &[landed]);
    assert_eq!(holds(&common), None);
    let eject =
        json!({"event": "eject", "batch": "461-1", "change": &shas[0][..7], "repair": "r1"});
    lane(&common, &[eject]);
    assert_eq!(holds(&common), None);
    let out = json!({"event": "landed", "batch": "461-1", "landed": [], "ejected": [shas[0]]});
    lane(&common, &[out]);
    assert_eq!(holds(&common), None);
    // a stopped batch's hand-in waits, as the lane's state reads it
    let batch = json!({"event": "batch", "batch": "461-1", "changes": [shas[0]]});
    lane(
        &common,
        &[batch, json!({"event": "stop", "batch": "461-1"})],
    );
    assert!(holds(&common).is_some_and(|h| h.starts_with("hand-in 461 T12 (")));
    // a later hand-in of the task supersedes it and waits itself (a commit's repeated line read once); off the lane, nothing held
    lane(&common, &[json!({"event": "start"})]);
    let log =
        done(&shas[0], "461 T12") + &done(&shas[0], "461 T12") + &done(&shas[1], "461 T12,T14");
    std::fs::write(common.join("builder-pool.log"), log).unwrap();
    git(t.path(), &["update-ref", "refs/l7r/done/461-T12", &shas[1]]);
    let want = format!("hand-in 461 T12,T14 ({}) waiting", &shas[1][..10]);
    assert_eq!(holds(&common), Some(want.clone()));
    // the earlier one still on the lane by a stopped batch's line: superseded by the later hand-in of its task, not held
    let batch = json!({"event": "batch", "batch": "461-2", "changes": [shas[0]]});
    lane(
        &common,
        &[batch, json!({"event": "stop", "batch": "461-2"})],
    );
    assert_eq!(holds(&common), Some(want));
    git(t.path(), &["update-ref", "-d", "refs/l7r/done/461-T12"]);
    assert_eq!(holds(&common), None);
    assert!(flock(&lock, "-u"));
}

/// 461 T64: from phase 2's base every hand-in starts the runner, so a waiting hand-in no runner serves - its start failed, perhaps
/// before the lane wrote any line - holds the stop, which keeps armed the wait that says the death (461 T56); phase 1's is quiet.
#[test]
fn from_phase_2_s_base_a_waiting_hand_in_holds_with_no_runner_and_no_lane_log() {
    let t = TempDir::new("lane-holds-origin");
    let shas = repo(&t, &["one"]);
    let common = t.path().join(".git");
    git(t.path(), &["update-ref", "refs/l7r/done/461-T12", &shas[0]]);
    // no hand-in on the pool's log yet: nothing held
    assert_eq!(holds_at(&common, true), None);
    std::fs::write(common.join("builder-pool.log"), done(&shas[0], "461 T12")).unwrap();
    let want = format!("hand-in 461 T12 ({}) waiting", &shas[0][..10]);
    crate::env::set("HAND_IN_BASE", "origin");
    assert_eq!(holds(&common), Some(want.clone()));
    crate::env::set("HAND_IN_BASE", "clone");
    assert_eq!(holds(&common), None);
    assert_eq!(holds_at(&common, true), Some(want.clone()));
    assert_eq!(holds_at(&common, false), None);
    // with the lane's log, a runner that idled out: the same
    let idle = [
        json!({"event": "start"}),
        json!({"event": "stop", "why": "idle"}),
    ];
    lane(&common, &idle);
    assert_eq!(holds_at(&common, true), Some(want));
    assert_eq!(holds_at(&common, false), None);
    // landed by the lane: nothing held on either base
    let landed = json!({"event": "landed", "batch": "461-1", "landed": [shas[0]]});
    lane(&common, &[landed]);
    assert_eq!(holds_at(&common, true), None);
}

#[test]
fn the_phase_2_base_is_unset_empty_or_origin_as_t22_reads_it() {
    assert!(origin_base(Some("origin")));
    assert!(origin_base(Some("")));
    assert!(origin_base(None));
    assert!(!origin_base(Some("clone")));
    assert!(!origin_base(Some("soon")));
}
