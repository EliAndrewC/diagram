//! A measurement's waits on a scratch slot directory (feature 451 T426): a `slot-wait` line marked `scratch`, or one of the
//! record's known unmarked ones, is booked to no category - neither waiting on a build slot nor the compile whose span holds it -
//! its seconds its run's own, and the runs table's note counts it.

use std::collections::HashMap;

use serde_json::{json, Value};

use super::*;

fn ev(v: &Value) -> Event {
    v.as_object().unwrap().clone()
}

fn at(hms: &str) -> String {
    format!("2026-11-27T{hms}Z")
}

#[test]
fn a_scratch_slot_wait_is_booked_to_no_category_and_counted() {
    let call = |id: &str, ev_: &str, t: &str| {
        ev(
            &json!({"t": at(t), "sid": "s", "ev": ev_, "tool": "Bash", "id": id, "make": "rust-test", "task": "T9"}),
        )
    };
    let stream = [
        call("toolu_a", "PreToolUse", "01:00:00"),
        call("toolu_a", "PostToolUse", "01:05:00"),
        call("toolu_b", "PreToolUse", "01:50:00"),
        call("toolu_b", "PostToolUse", "01:52:00"),
    ];
    let phase = |step: &str, t0: &str, t1: &str, more: &Value| {
        let mut v = json!({"ev": "Phase", "src": "rust", "sid": "s", "step": step, "make": "rust-test", "task": "T9",
            "t0": at(t0), "t1": at(t1), "clone": "/c/diagram-backlog-t269"});
        for (k, x) in more.as_object().unwrap() {
            v[k] = x.clone();
        }
        ev(&v)
    };
    let none = json!({});
    let aside = [
        // a build whose span holds a marked scratch wait of 60 s: compile keeps only the 50 s after it
        phase("build", "01:00:10", "01:02:00", &none),
        phase(
            "slot-wait",
            "01:00:10",
            "01:01:10",
            &json!({"scratch": true}),
        ),
        // a real wait, unmarked: waiting on a build slot as before
        phase("slot-wait", "01:03:00", "01:03:20", &none),
        // the record's known unmarked scratch holds: tree t270, 01:48:50 to 02:01:30Z (451 T420)
        phase(
            "slot-wait",
            "01:50:10",
            "01:50:40",
            &json!({"clone": "/c/diagram-backlog-t270"}),
        ),
        // the same minute in another tree is real
        phase("slot-wait", "01:51:00", "01:51:05", &none),
    ];
    let (stops, enq) = (HashMap::new(), HashMap::new());
    let w = Window {
        stopped: &stops,
        queued: &HashMap::new(),
        end: ts(&at("03:00:00")).unwrap(),
        enqueued: &enq,
        goal: "done",
    };
    let r = runs(&stream, &aside, &[], &w).unwrap();
    let rows = by_task(&r);
    let t = &rows[0].1;
    let got: Vec<f64> = [SLOT_WAIT, "compile", "tests"]
        .iter()
        .map(|c| t.get(&(*c).to_owned()))
        .collect();
    // 420 s of runs: 25 s waiting (20 + 5), 50 s compile, the rest (345 s, the two scratch holds' 90 s in it) the runs' bucket
    assert_eq!(got, [25.0, 50.0, 345.0]);
    assert_eq!(r.loose, (0, 0.0));
    let text = render(&r, &[]);
    let said = "waits on a scratch slot directory (451 T426): 2 (1.5 min), booked to no category";
    assert!(text.contains(said), "{text}");
    // every second of the runs in the minutes: the real wait in its column, the scratch holds in the bucket
    assert!(
        text.contains("| T9 | 2 | 7.0 | 5.8 | 0.8 | 0.4 |"),
        "{text}"
    );
}

#[test]
fn a_scratch_line_is_told_by_its_mark_or_the_record_s_known_holds() {
    let line = |v: Value| ev(&v);
    let wait = |t0: &str, clone: &str| {
        line(json!({"src": "rust", "step": "slot-wait", "t0": at(t0), "clone": clone}))
    };
    assert!(scratch_wait(&line(
        json!({"src": "rust", "step": "slot-wait", "scratch": true})
    )));
    assert!(!scratch_wait(&line(
        json!({"src": "rust", "step": "slot-wait", "scratch": false})
    )));
    // a `slot-small` line is booked to no category already: the mark does not make it a wait
    assert!(!scratch_wait(&line(
        json!({"src": "rust", "step": "slot-small", "scratch": true})
    )));
    assert!(scratch_wait(&wait("01:48:50", "/c/diagram-backlog-t270")));
    assert!(scratch_wait(&wait("02:01:30", "/c/diagram-backlog-t270")));
    assert!(!scratch_wait(&wait("01:48:49", "/c/diagram-backlog-t270")));
    assert!(!scratch_wait(&wait("02:01:31", "/c/diagram-backlog-t270")));
    assert!(!scratch_wait(&wait("01:50:00", "/c/diagram-backlog-t271")));
    assert!(!scratch_wait(&line(
        json!({"src": "rust", "step": "slot-wait", "t0": 7, "clone": "/c/diagram-backlog-t270"})
    )));
    // what is no slot-wait is never one
    assert!(!scratch_wait(&line(
        json!({"src": "rust", "step": "build", "scratch": true})
    )));
}
