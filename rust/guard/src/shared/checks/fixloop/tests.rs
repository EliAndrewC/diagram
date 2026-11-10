use serde_json::{json, Value};

use super::{hold, notes_of, read_reply, returned};
use crate::shared::checks::testkit::clone_at;

#[test]
fn a_reply_names_its_footnotes_whole() {
    let manifest = "unit: quote-check:0105.drawing#bath f1\nunit: quote-check:0105#deed f2\nunit: quote-check:0105#deed-4 f3\nunit: quote-check:0105#unfootnoted f4\nunit: other:0105#x f5\n";
    let notes = notes_of(manifest);
    assert_eq!(notes.len(), 3);
    assert_eq!(notes["0105.drawing#bath"], "f1");
    let names: Vec<String> = notes.keys().cloned().collect();
    let reply = "1 of 2\n\nbath: PARTIAL, one thing\ndeed passes\n3 NOT-READABLE (deed-4)\nOUTSIDE THE CHANGE\n\ndeed: DIFFERS\n";
    let (flagged, passed) = read_reply(reply, &names);
    assert_eq!(flagged["0105.drawing#bath"], "bath: PARTIAL, one thing");
    assert!(!flagged.contains_key("0105#deed-4"));
    assert!(passed.contains("0105#deed") && passed.contains("0105#deed-4"));
    let (none_flagged, none_passed) = read_reply("", &names);
    assert!(none_flagged.is_empty() && none_passed.is_empty());
}

fn d(notes: &Value) -> Value {
    json!({"check": "quote-check", "quote_notes": notes})
}

#[test]
fn a_flag_counts_only_a_failed_fix() {
    let mut state = json!({});
    let notes = json!({"0105#bath": "f1", "0105#ok": "g1"});
    returned(
        &mut state,
        &json!({"check": "other", "quote_notes": notes}),
        "x",
    );
    returned(&mut state, &json!({"check": "quote-check"}), "x");
    returned(&mut state, &d(&notes), "   ");
    assert_eq!(state, json!({}));
    returned(
        &mut state,
        &d(&notes),
        "head\nbath PARTIAL first\nok fine\n",
    );
    assert_eq!(state["flags"]["0105#bath"]["n"], json!(1));
    returned(&mut state, &d(&notes), "head\nbath PARTIAL second\n");
    assert_eq!(
        state["flags"]["0105#bath"]["lines"],
        json!(["bath PARTIAL second"])
    );
    assert_eq!(state["flags"]["0105#bath"]["n"], json!(1));
    let moved = json!({"0105#bath": "f2"});
    returned(&mut state, &d(&moved), "head\nbath PARTIAL third\n");
    assert_eq!(state["flags"]["0105#bath"]["n"], json!(2));
    assert_eq!(
        state["flags"]["0105#bath"]["lines"],
        json!(["bath PARTIAL second", "bath PARTIAL third"])
    );
    returned(&mut state, &d(&moved), "head\nbath is fine\n");
    assert!(state["flags"].get("0105#bath").is_none());
}

fn flagged(n: u64) -> Value {
    json!({"rounds": {}, "flags": {"0105#bath": {"n": n, "fp": "old", "lines": ["L1", "L2"]}}})
}

#[test]
fn a_footnote_whose_fix_keeps_failing_is_held() {
    let root = clone_at("fixloop-hold");
    let manifest = "unit: quote-check:0105#bath newfp\n";
    let mut state = flagged(2);
    assert_eq!(hold(&mut state, &root, "record-format", manifest, 1.0), "");
    assert_eq!(
        hold(&mut flagged(1), &root, "quote-check", manifest, 1.0),
        ""
    );
    assert_eq!(
        hold(
            &mut json!({"flags": {"0105#bath": {"n": 2, "fp": "newfp"}}}),
            &root,
            "quote-check",
            manifest,
            1.0
        ),
        ""
    );
    assert_eq!(
        hold(&mut json!({}), &root, "quote-check", manifest, 1.0),
        ""
    );
    let msg = hold(&mut state, &root, "quote-check", manifest, 1.0);
    assert!(msg.contains("round:quote-check|q:0105@3"));
    assert_eq!(
        state["flag_trips"]["0105#bath"],
        json!("round:quote-check|q:0105@3")
    );
    let again = hold(&mut state, &root, "quote-check", manifest, 1.0);
    assert!(again.contains("round:quote-check|q:0105@3"));
    std::fs::write(
        root.join("specs/999-x/arbiter.jsonl"),
        "{\"trigger\": \"round:quote-check|q:0105@3\", \"ruling\": \"continue\"}\n",
    )
    .unwrap();
    assert_eq!(hold(&mut state, &root, "quote-check", manifest, 1.0), "");
    assert_eq!(state["flags"]["0105#bath"]["n"], json!(1));
    assert!(state["flag_trips"].get("0105#bath").is_none());
    state["flags"]["0105#bath"]["n"] = json!(2);
    state["flag_trips"]["0105#bath"] = json!("round:quote-check|q:0105@3");
    std::fs::write(
        root.join("specs/999-x/arbiter.jsonl"),
        "{\"trigger\": \"round:quote-check|q:0105@3\", \"ruling\": \"accept\"}\n",
    )
    .unwrap();
    assert_eq!(hold(&mut state, &root, "quote-check", manifest, 1.0), "");
    assert_eq!(state["flags"]["0105#bath"]["n"], json!(0));
    state["flag_trips"]["0105#bath"] = json!("round:quote-check|q:0105@3");
    state["flags"].as_object_mut().unwrap().remove("0105#bath");
    assert_eq!(hold(&mut state, &root, "quote-check", manifest, 1.0), "");
    let mut used = json!({"rounds": {"quote-check|q:0105": 9}, "flags": {"0105.drawing#bath": {"n": 2, "fp": "old"}}});
    let msg = hold(
        &mut used,
        &root,
        "quote-check",
        "unit: quote-check:0105.drawing#bath z\n",
        1.0,
    );
    assert!(msg.contains("@10"));
    let d2 = clone_at("fixloop-used");
    std::fs::write(
        d2.join("specs/999-x/arbiter.jsonl"),
        "{\"trigger\": \"round:quote-check|q:0105@6\", \"ruling\": \"accept\"}\n",
    )
    .unwrap();
    let mut s = flagged(2);
    let m = hold(&mut s, &d2, "quote-check", manifest, 1.0);
    assert!(m.contains("@7"));
}
