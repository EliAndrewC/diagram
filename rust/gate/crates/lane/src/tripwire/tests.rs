use serde_json::json;

use super::*;

fn hand_in(feature: &str, tasks: &[&str], commit: &str) -> HandIn {
    HandIn {
        feature: feature.into(),
        tasks: tasks.iter().map(|t| (*t).to_owned()).collect(),
        commit: commit.into(),
        at: String::new(),
        repair_of: None,
        build_half: false,
    }
}

fn eject(batch: &str, change: &str, why: &str, repair: &str) -> Value {
    json!({"event": "eject", "batch": batch, "change": change, "why": why, "repair": repair})
}

#[test]
fn a_task_s_pins_are_its_pinning_ejections_one_a_batch_keyed_by_feature_and_task() {
    let hand_ins = [
        hand_in("461", &["T02"], "aaaaaaaa01"),
        hand_in("461", &["T02"], "aaaaaaaa02"),
        hand_in("999", &["T02"], "bbbbbbbb01"),
        hand_in("461", &["T03", "T02"], "cccccccc01"),
    ];
    let lane = [
        eject("461-1", "aaaaaaaa01", "red", "r1"),
        // the same batch again (a kill between an entry and its lines): one pin
        eject("461-1", "aaaaaaaa01", "red", "r1"),
        // another feature's T02 pins nothing of 461's
        eject("999-1", "bbbbbbbb01", "red", "r2"),
        // a conflict and the ruling's own ejection pin nothing
        eject("461-2", "aaaaaaaa02", "conflict", "r3"),
        eject("461-3", "aaaaaaaa02", "arbiter", "r4"),
        // a commit no hand-in names, and a line of no batch, pin nothing
        eject("461-4", "dddddddd01", "red", "r5"),
        json!({"event": "eject", "change": "aaaaaaaa02", "why": "red"}),
        // a bundle's change pins each of its tasks; its own attempt read before its entry's
        json!({"event": "eject", "batch": "461-5", "change": "cccccccc01", "why": "unplaced", "repair": null, "attempt": "own.log"}),
        eject("461-6", "aaaaaaaa02", "inferred", "r9"),
        json!({"event": "run", "batch": "461-7", "change": "aaaaaaaa02"}),
    ];
    let repairs = [
        json!({"repair": "r1", "attempt": "one.log"}),
        json!({"repair": "r6", "attempt": "never.log"}),
    ];
    let pins_of = |task: &str| -> Vec<(String, String)> {
        pins(&lane, &repairs, &hand_ins, "461", task)
            .into_iter()
            .map(|p| (p.batch, p.attempt))
            .collect()
    };
    assert_eq!(
        pins_of("T02"),
        [
            ("461-1".to_owned(), "one.log".to_owned()),
            ("461-5".to_owned(), "own.log".to_owned()),
            // an entry the file does not hold: no attempt known
            ("461-6".to_owned(), String::new()),
        ]
    );
    assert_eq!(pins_of("T03"), [("461-5".to_owned(), "own.log".to_owned())]);
    assert!(pins_of("T09").is_empty());
}

#[test]
fn a_trip_is_a_task_pinned_in_another_batch_its_subject_and_files_its_pins() {
    let hand_ins = [hand_in("461", &["T02"], "aaaaaaaa01")];
    let lane = [
        eject("461-1", "aaaaaaaa01", "red", "r1"),
        eject("461-2", "aaaaaaaa01", "red", "r2"),
    ];
    let repairs = [
        json!({"repair": "r1", "attempt": "one.log"}),
        json!({"repair": "r2", "attempt": "two.log"}),
    ];
    let tasks = ["T02".to_owned(), "T05".to_owned()];
    // this batch's own pin is no earlier one: in batch 461-2, T02's pin before is 461-1's
    let in_two = trips(&lane, &repairs, &hand_ins, "461", &tasks, "461-2");
    assert_eq!(
        in_two,
        [Trip {
            task: "T02".into(),
            n: 2,
            before: Pin {
                batch: "461-1".into(),
                attempt: "one.log".into()
            }
        }]
    );
    assert_eq!(subject(&in_two), "lane-T02");
    assert_eq!(files(&in_two, "now.log"), ["one.log", "now.log"]);
    // a third pin: a subject of its own, the pin before the last earlier one
    let in_three = trips(&lane, &repairs, &hand_ins, "461", &tasks, "461-3");
    assert_eq!(in_three[0].n, 3);
    assert_eq!(subject(&in_three), "lane-T02-3");
    assert_eq!(files(&in_three, "now.log"), ["two.log", "now.log"]);
    // a first pin trips nothing
    assert!(trips(&lane[..1], &repairs, &hand_ins, "461", &tasks, "461-1").is_empty());
    // a bundle's tasks joined; an attempt unknown or named twice is listed once or not at all
    let both = [
        in_two[0].clone(),
        Trip {
            task: "T05".into(),
            n: 2,
            before: Pin {
                batch: "461-1".into(),
                attempt: String::new(),
            },
        },
    ];
    assert_eq!(subject(&both), "lane-T02-T05");
    assert_eq!(files(&both, "one.log"), ["one.log"]);
    assert_eq!(subject(&[]), "lane-");
}

#[test]
fn the_bundle_is_the_last_manifest_its_ask_names() {
    let out = "arbiter-ask: ask:lane-T02 recorded\nwrote `/tmp/a/MANIFEST.md`\nsee '/tmp/b/MANIFEST.md'\n";
    assert_eq!(manifest(out).as_deref(), Some("/tmp/b/MANIFEST.md"));
    assert_eq!(manifest("no bundle"), None);
}

#[test]
fn a_hold_awaits_its_ruling_until_the_ruling_s_ejection_names_its_batch() {
    let stop = json!({"event": "stop", "batch": "461-2", "why": "arbiter", "trigger": "ask:lane-T02", "spec": "461-x", "tasks": ["T02"], "held": ["aaaaaaaa02"]});
    let lane = vec![
        // the runner's own stop and a stop of no batch hold nothing
        json!({"event": "stop", "pid": 1, "why": "idle"}),
        json!({"event": "stop", "why": "arbiter"}),
        stop.clone(),
    ];
    assert_eq!(
        awaiting(&lane),
        [Held {
            batch: "461-2".into(),
            trigger: "ask:lane-T02".into(),
            spec: "461-x".into(),
            tasks: vec!["T02".into()],
            changes: vec!["aaaaaaaa02".into()],
        }]
    );
    // a bare stop line: every field empty
    let bare = [json!({"event": "stop", "batch": "461-9", "why": "arbiter"})];
    assert_eq!(awaiting(&bare)[0].trigger, "");
    let mut filed = lane.clone();
    filed.push(json!({"event": "eject", "of_batch": "461-1", "why": "arbiter"}));
    filed.push(json!({"event": "eject", "of_batch": "461-2", "why": "red"}));
    assert_eq!(awaiting(&filed).len(), 1);
    filed.push(json!({"event": "eject", "of_batch": "461-2", "why": "arbiter"}));
    assert!(awaiting(&filed).is_empty());
}

#[test]
fn a_ruling_s_units_are_its_ruling_and_what_it_asks() {
    assert_eq!(
        units(&json!({"ruling": "continue", "what": " fix it "})),
        ["continue: fix it"]
    );
    assert_eq!(units(&json!({"ruling": "accept", "what": ""})), ["accept"]);
    assert_eq!(units(&json!({})), [""]);
}
