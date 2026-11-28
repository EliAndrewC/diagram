//! The lane's log (feature 461 T11): its write, its reading of a torn line and the repairs open; the computed states' tests moved
//! with them to `l7r_shared::lane_log` (461 T63).

use serde_json::{json, Value};

use super::{append, path, read, repairs_open};

const A: &str = "aaaaaaaaaa1111111111111111111111111111111";
const B: &str = "bbbbbbbbbb2222222222222222222222222222222";
const C: &str = "cccccccccc3333333333333333333333333333333";

fn done(utc: &str, detail: &str, commit: &str) -> Value {
    json!({"utc": utc, "event": "done", "tree": "/t", "detail": detail, "commit": commit, "handed_in": true})
}

#[test]
fn a_line_is_appended_whole_and_a_torn_or_foreign_line_is_skipped_on_reading() {
    let dir = l7r_gate_core::ci::fixtures::scratch("lane-log-append");
    let common = dir.path();
    assert!(read(common).is_empty());
    append(
        common,
        "2026-11-28T03:01:44Z",
        "run",
        &json!({"batch": "461-7", "n": 2, "code": 1}),
    )
    .unwrap();
    append(common, "2026-11-28T03:02:00Z", "start", &Value::Null).unwrap();
    let text = std::fs::read_to_string(path(common)).unwrap();
    assert!(text.ends_with("}\n"));
    std::fs::write(path(common), format!("{text}[1]\n{{\"utc\": \"torn")).unwrap();
    let lines = read(common);
    assert_eq!(lines.len(), 2);
    assert_eq!(lines[0]["utc"], "2026-11-28T03:01:44Z");
    assert_eq!(lines[0]["event"], "run");
    assert_eq!(lines[0]["n"], 2);
    assert_eq!(
        lines[1],
        json!({"utc": "2026-11-28T03:02:00Z", "event": "start"})
    );
    // an event the data model does not name is refused, nothing written
    let bad = append(common, "t", "rerun", &json!({})).unwrap_err();
    assert!(bad.contains("no event rerun") && bad.contains("start, stop, batch"));
    // a common directory that is a file cannot hold the lane's
    let file = common.join("plain");
    std::fs::write(&file, "").unwrap();
    let err = append(&file, "t", "start", &json!({})).unwrap_err();
    assert!(err.starts_with("lane: ") && err.contains("l7r-lane/lane.jsonl"));
}

/// The repairs open are the queue's reader's (461 T65): an entry filed and ejected is open, listed once however many `eject`
/// lines name it, until a done line answers it by `repair_of`; an entry no `eject` line names is not yet open. (The supersede is
/// pinned through `make lane`'s status, `lane::tests`.)
#[test]
fn a_repair_is_open_until_a_hand_in_names_it_and_is_listed_once() {
    let dir = l7r_gate_core::ci::fixtures::scratch("lane-log-repairs");
    let common = dir.path();
    for (change, task) in [(A, "T01"), (B, "T02"), (C, "T03")] {
        let entry = crate::repairs::Entry {
            feature: "461-landing-lane".into(),
            tasks: vec![task.into()],
            kind: "fix".into(),
            ejected: vec![change.into()],
            batch: "461-1".into(),
            why: "red".into(),
            units: Vec::new(),
            attempt: "a.log".into(),
        };
        let id = crate::repairs::file(common, "t1", &entry).unwrap();
        // C's entry is filed, its `eject` line never written (a runner killed between them)
        for _ in 0..usize::from(change != C) * 2 {
            let fields = json!({"batch": "461-1", "change": change, "repair": id});
            append(common, "t1", "eject", &fields).unwrap();
        }
    }
    assert_eq!(repairs_open(common), ["r1", "r2"]);
    let mut answer = done("t0", "461 T01", A);
    answer["repair_of"] = json!("r1");
    std::fs::write(
        common.join(l7r_shared::builder_queue::LOG),
        format!("{answer}\n"),
    )
    .unwrap();
    assert_eq!(repairs_open(common), ["r2"]);
}
