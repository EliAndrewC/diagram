//! The repair entries the queue offers (461 T16): offered only once an `eject` line names one, its changes those lines', closed by a
//! done line's `repair_of` or a later hand-in of its task, passed over in flight or of a kind no brief takes, and offered by the
//! idle rule before a READY queue entry.

use std::path::Path;

use super::super::{idle, Idle, Verdict};
use super::*;
use crate::tempdir::TempDir;

fn put(path: &Path, text: &str) {
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

const ENTRIES: &str = concat!(
    r#"{"utc": "2026-11-28T03:00:00Z", "repair": "r1", "feature": "461-landing-lane", "tasks": ["T13"], "kind": "fix", "ejected": ["aaa"], "batch": "461-7", "why": "red", "units": ["rust/gate/crates/land test", "rust/a rust/b rust/c (+2 more) cover-build", "tests/hooks/test-x.sh"], "attempt": "/c/.git/l7r-lane/attempts/461-7-2.log"}"#,
    "\n",
    r#"{"utc": "2026-11-28T03:00:01Z", "repair": "r2", "feature": "461-landing-lane", "tasks": ["T14", "T15"], "kind": "fix", "ejected": ["bbb", "ccc"], "batch": "461-8", "why": "unplaced", "units": [], "attempt": "/a2.log"}"#,
    "\n",
    r#"{"utc": "2026-11-28T03:00:02Z", "repair": "r3", "feature": "461-landing-lane", "tasks": ["T16"], "kind": "integrate", "ejected": ["ddd"], "batch": "461-9", "why": "push", "units": [], "attempt": "/a3.log"}"#,
    "\n",
    r#"{"utc": "2026-11-28T03:00:03Z", "repair": "r4", "feature": "461-landing-lane", "tasks": ["T17"], "kind": "fix", "ejected": ["eee"], "batch": "461-9", "why": "red", "units": [], "attempt": "/a4.log"}"#,
    "\n",
    "{torn\n",
);

/// r1, r2 (only `bbb` ejected: `ccc` landed on a resume), r3 ejected; r4 filed and never ejected.
const LANE: &str = concat!(
    r#"{"utc": "2026-11-28T03:00:05Z", "event": "eject", "batch": "461-7", "change": "aaa", "repair": "r1", "why": "red"}"#,
    "\n",
    r#"{"utc": "2026-11-28T03:00:06Z", "event": "eject", "batch": "461-8", "change": "bbb", "repair": "r2", "why": "unplaced"}"#,
    "\n",
    r#"{"utc": "2026-11-28T03:00:07Z", "event": "eject", "batch": "461-9", "change": "ddd", "repair": "r3", "why": "push"}"#,
    "\n",
);

const DONES: &str = concat!(
    r#"{"utc": "2026-11-28T02:00:00Z", "event": "done", "detail": "461 T13", "commit": "aaa", "handed_in": true}"#,
    "\n",
    r#"{"utc": "2026-11-28T02:00:01Z", "event": "done", "detail": "461 T14", "commit": "bbb", "handed_in": true}"#,
    "\n",
);

fn world(tag: &str) -> (TempDir, std::path::PathBuf) {
    let dir = TempDir::new(&format!("builder-queue-repairs-{tag}"));
    let common = dir.join("c/.git");
    put(&common.join("l7r-lane/repairs.jsonl"), ENTRIES);
    put(&common.join("l7r-lane/lane.jsonl"), LANE);
    put(&common.join("builder-pool.log"), DONES);
    (dir, common)
}

fn ids(rs: &[Repair]) -> Vec<&str> {
    rs.iter().map(|r| r.id.as_str()).collect()
}

#[test]
fn an_entry_is_open_once_ejected_its_changes_and_tasks_the_eject_lines() {
    let (_dir, common) = world("open");
    let all = open(&common);
    // r4 has no eject line: never offered
    assert_eq!(ids(&all), ["r1", "r2", "r3"]);
    // r2's changes are its eject lines', its tasks their done lines' - not the entry's `ejected` or `tasks`
    assert_eq!(
        (all[1].changes.clone(), all[1].tasks.clone()),
        (vec!["bbb".to_owned()], vec!["T14".to_owned()])
    );
    // r3's change has no done line: the entry's tasks
    assert_eq!(all[2].tasks, ["T16"]);
    let r1 = &all[0];
    assert_eq!(
        (r1.key.as_str(), r1.batch.as_str(), r1.why.as_str()),
        ("461", "461-7", "red")
    );
    assert_eq!(r1.attempt, "/c/.git/l7r-lane/attempts/461-7-2.log");
    assert_eq!(r1.name(), "461 T13 (repair r1)");
    // a crate a unit's dirs, the family's `(+k more)` cut, a suite naming none
    assert_eq!(
        r1.crates(),
        ["rust/gate/crates/land", "rust/a", "rust/b", "rust/c"]
    );
    assert_eq!(
        r1.command(),
        "make builder-brief T=T13 F=461 KIND=fix CRATE=\"rust/gate/crates/land rust/a rust/b rust/c\" REPAIR=r1"
    );
    assert_eq!(
        all[1].command(),
        "make builder-brief T=T14 F=461 KIND=fix REPAIR=r2"
    );
    // no file: none
    assert!(open(&common.join("nowhere")).is_empty());
}

#[test]
fn a_repair_is_closed_by_its_answer_or_a_later_hand_in_of_its_task() {
    let (_dir, common) = world("closed");
    let log = common.join("builder-pool.log");
    let more = concat!(
        // r1 answered by a done line naming it
        r#"{"utc": "2026-11-28T04:00:00Z", "event": "done", "detail": "461 T13", "commit": "fff", "repair_of": "r1"}"#,
        "\n",
        // a hand-in of T14 BEFORE r2's ejection closes nothing; a done not handed in neither; another feature's T14 neither
        r#"{"utc": "2026-11-28T03:00:00Z", "event": "done", "detail": "461 T14", "commit": "ggg", "handed_in": true}"#,
        "\n",
        r#"{"utc": "2026-11-28T05:00:00Z", "event": "done", "detail": "461 T14", "commit": "hhh"}"#,
        "\n",
        r#"{"utc": "2026-11-28T05:00:00Z", "event": "done", "detail": "451 T14", "commit": "iii", "handed_in": true}"#,
        "\n",
    );
    put(&log, &(DONES.to_owned() + more));
    assert_eq!(ids(&open(&common)), ["r2", "r3"]);
    // a later hand-in of T14, briefed without REPAIR=: r2 superseded
    let later = r#"{"utc": "2026-11-28T05:00:01Z", "event": "done", "detail": "461 T14,T20", "commit": "jjj", "handed_in": true}"#;
    put(&log, &(DONES.to_owned() + more + later + "\n"));
    assert_eq!(ids(&open(&common)), ["r3"]);
}

#[test]
fn in_flight_and_a_kind_no_brief_takes_are_passed_over() {
    let (dir, common) = world("offer");
    let held = vec![Tree {
        tree: dir.join("c-b0"),
        feature: "461".to_owned(),
        tasks: vec!["T13".to_owned()],
        since: String::new(),
    }];
    let o = offer(&common, &held);
    assert_eq!(ids(&o.ready), ["r2"]);
    let passed: Vec<(&str, &str)> = o
        .passed
        .iter()
        .map(|(r, w)| (r.id.as_str(), w.as_str()))
        .collect();
    assert_eq!(passed[0].0, "r1");
    let why = passed[0].1;
    assert!(why.starts_with("in flight (461 T13 holds "), "{why}");
    assert_eq!(
        passed[1],
        (
            "r3",
            "kind integrate is no kind make builder-brief takes yet: brief its builder by hand"
        )
    );
    // another feature's hold of T13 holds nothing back
    let other = vec![Tree {
        feature: "451".to_owned(),
        ..held[0].clone()
    }];
    assert_eq!(ids(&offer(&common, &other).ready), ["r1", "r2"]);
}

#[test]
fn the_knob_puts_repairs_after_the_queue() {
    assert!(first());
    crate::env::set(KNOB, "0");
    assert!(!first());
    crate::env::set(KNOB, "1");
    assert!(first());
}

/// A clone whose pool has one free tree, a queue with a READY entry, and the lane's repair entries.
fn clone_with_queue(tag: &str) -> (TempDir, std::path::PathBuf) {
    let (dir, common) = world(tag);
    let clone = common.parent().unwrap().to_path_buf();
    put(&clone.join("specs/451-x/tasks.md"), "- [ ] T3 open\n");
    put(
        &clone.join("specs/451-x/queue.txt"),
        "T3 fix crates=rust/guard files=-\n",
    );
    std::fs::create_dir_all(dir.join("c-b1")).unwrap();
    let pool = format!(
        r#"{{"trees": [{{"tree": "{}/c-b1", "feature": "", "tasks": [], "since": ""}}]}}"#,
        dir.display()
    );
    put(&common.join("builder-pool.json"), &pool);
    // no `.git` repository is needed for the queue: the done refs read as none
    (dir, clone)
}

#[test]
fn a_free_tree_is_idle_over_an_open_repair_before_a_ready_queue_entry() {
    let (dir, clone) = clone_with_queue("idle");
    let want = Idle {
        tree: dir.join("c-b1"),
        tasks: "461 T13 (repair r1), a FRESH builder".to_owned(),
        command: "make builder-brief T=T13 F=461 KIND=fix CRATE=\"rust/gate/crates/land rust/a rust/b rust/c\" REPAIR=r1".to_owned(),
        flag: String::new(),
        unlisted: Vec::new(),
    };
    assert_eq!(idle(&clone, 3), Verdict::Idle(want));
    // the knob at 0: the queue's READY entry first
    crate::env::set(KNOB, "0");
    assert!(matches!(idle(&clone, 3), Verdict::Idle(q) if q.tasks == "451 T3"));
    // with no queue entry READY, the repair still
    std::fs::remove_file(clone.join("specs/451-x/queue.txt")).unwrap();
    assert!(matches!(
        idle(&clone, 3),
        Verdict::Idle(r) if r.tasks == "461 T13 (repair r1), a FRESH builder"
    ));
    crate::env::unset(KNOB);
}
