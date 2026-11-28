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
    // a red repair's builder reads the gate's output first
    assert_eq!(
        r1.read(),
        "the gate's output /c/.git/l7r-lane/attempts/461-7-2.log"
    );
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
        // a hand-in of T14 BEFORE r2's change's own (`bbb`, 02:00:01) closes nothing; a done not handed in neither; another
        // feature's T14 neither
        r#"{"utc": "2026-11-28T01:59:59Z", "event": "done", "detail": "461 T14", "commit": "ggg", "handed_in": true}"#,
        "\n",
        r#"{"utc": "2026-11-28T05:00:00Z", "event": "done", "detail": "461 T14", "commit": "hhh"}"#,
        "\n",
        r#"{"utc": "2026-11-28T05:00:00Z", "event": "done", "detail": "451 T14", "commit": "iii", "handed_in": true}"#,
        "\n",
    );
    put(&log, &(DONES.to_owned() + more));
    assert_eq!(ids(&open(&common)), ["r2", "r3"]);
    // a later hand-in of T14, briefed without REPAIR=: r2 superseded - though made while r2's batch was open, before its 03:00:06
    // eject (461 T26, D14: it waited for that batch, then supersedes the ejected one)
    let later = r#"{"utc": "2026-11-28T03:00:03Z", "event": "done", "detail": "461 T14,T20", "commit": "jjj", "handed_in": true}"#;
    put(&log, &(DONES.to_owned() + more + later + "\n"));
    assert_eq!(ids(&open(&common)), ["r3"]);
}

/// 461 T67: an arbiter's repair (T18's `file_ruled`: `attempt` the trigger, `units` the ruling's words) reads the ruling's row in
/// the clone's `specs/<spec>/arbiter.jsonl` - the last holding its trigger - and the batch `stop` line's attempts, and names no crate.
#[test]
fn an_arbiter_s_repair_reads_its_ruling_s_row_and_the_stop_line_s_attempts() {
    let dir = TempDir::new("builder-queue-repairs-arbiter");
    let common = dir.join("c/.git");
    let entry = |id: &str, batch: &str| {
        format!("{{\"repair\": \"{id}\", \"feature\": \"461-landing-lane\", \"tasks\": [\"T13\"], \"kind\": \"fix\", \"batch\": \"{batch}\", \"why\": \"arbiter\", \"units\": [\"continue: fix the test\"], \"attempt\": \"ask:lane-T13\"}}\n")
    };
    put(
        &common.join("l7r-lane/repairs.jsonl"),
        &(entry("r1", "461-3") + &entry("r2", "461-4")),
    );
    let lane = concat!(
        r#"{"event": "stop", "pid": 7, "why": "idle"}"#,
        "\n",
        r#"{"event": "stop", "batch": "461-3", "why": "arbiter", "trigger": "ask:lane-T13-3", "attempts": "/x.log"}"#,
        "\n",
        r#"{"event": "stop", "batch": "461-3", "why": "arbiter", "trigger": "ask:lane-T13", "attempts": "/a/461-1-2.log /b/461-3-1.log"}"#,
        "\n",
        r#"{"event": "eject", "of_batch": "461-3", "change": "aaa", "repair": "r1", "why": "arbiter"}"#,
        "\n",
        r#"{"event": "eject", "of_batch": "461-4", "change": "bbb", "repair": "r2", "why": "arbiter"}"#,
        "\n",
    );
    put(&common.join("l7r-lane/lane.jsonl"), lane);
    let rulings = dir.join("c/specs/461-landing-lane/arbiter.jsonl");
    let rows = "{\"trigger\": \"ask:lane-T13\", \"ruling\": \"accept\"}\n{\"trigger\": \"ask:other\"}\n{\"trigger\": \"ask:lane-T13\", \"ruling\": \"continue\"}\n";
    put(&rulings, rows);
    let all = open(&common);
    let (r1, r2) = (&all[0], &all[1]);
    // paths outside the clone, and an attempt in another directory than the first's, named whole
    let clone = dir.join("c");
    assert_eq!(r1.read(), format!("the ruling of ask:lane-T13 and the red attempts, in {}: specs/461-landing-lane/arbiter.jsonl line 3, /a/461-1-2.log /b/461-3-1.log", clone.display()));
    assert!(r1.crates().is_empty());
    assert_eq!(
        r1.command(),
        "make builder-brief T=T13 F=461 KIND=fix REPAIR=r1"
    );
    // a batch no stop line names reads no attempts; a file no row of which holds the trigger is named alone
    assert!(r2.attempts.is_empty());
    put(&rulings, "{\"trigger\": \"ask:other\"}\n");
    assert_eq!(
        open(&common)[0].ruling,
        "specs/461-landing-lane/arbiter.jsonl"
    );
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
