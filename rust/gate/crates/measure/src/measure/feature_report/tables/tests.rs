//! The report's tables over small event lists.

use serde_json::{json, Map, Value};

use super::*;

fn evs(list: &[Value]) -> Vec<Event> {
    list.iter()
        .map(|v| v.as_object().unwrap().clone())
        .collect()
}

fn at(hms: &str) -> String {
    format!("2026-11-01T{hms}Z")
}

#[test]
fn the_time_splits_into_its_categories() {
    let e = evs(&[
        json!({"t": at("08:00:00"), "sid": "s", "ev": "UserPromptSubmit"}),
        json!({"t": at("08:00:10"), "sid": "s", "ev": "PreToolUse", "tool": "Bash", "id": "b", "cat": "gate"}),
        json!({"t": at("08:00:20"), "sid": "s", "ev": "PostToolUse", "tool": "Bash", "id": "b"}),
        json!({"t": at("08:00:30"), "sid": "s", "ev": "PreToolUse", "tool": "Agent", "id": "a", "agent": "x"}),
        json!({"t": at("08:00:31"), "sid": "s", "ev": "SubagentStart", "aid": "x1"}),
        json!({"t": at("08:00:40"), "sid": "s", "ev": "PostToolUse", "tool": "Agent", "id": "a", "aid": "x1"}),
        json!({"t": at("08:00:50"), "sid": "s", "ev": "PreToolUse", "tool": "Edit", "id": "e", "cat": "edit", "path": "/r/specs/9-f/spec.md"}),
        json!({"t": at("08:01:00"), "sid": "s", "ev": "PostToolUse", "tool": "Edit", "id": "e"}),
        json!({"t": at("08:01:10"), "sid": "s", "ev": "Stop"}),
        json!({"t": at("08:01:20"), "sid": "s", "ev": "SubagentStop", "aid": "x1"}),
        json!({"t": at("08:01:30"), "sid": "s", "ev": "Stop"}),
        json!({"t": at("08:01:40"), "sid": "s", "ev": "UserPromptSubmit", "gm": false}),
        json!({"t": at("08:01:50"), "sid": "s", "ev": "Stop"}),
        json!({"t": at("08:02:00"), "sid": "s", "ev": "UserPromptSubmit"}),
        json!({"t": at("08:02:10"), "sid": "s", "ev": "PreToolUse", "tool": "Read", "id": "r"}),
        json!({"t": at("08:02:20"), "sid": "s", "ev": "Stop"}),
        json!({"t": at("08:02:30"), "sid": "s", "ev": "SubagentStop", "aid": "q", "agent": "quote-check"}),
        json!({"t": at("08:02:40"), "sid": "s", "ev": "SubagentStop"}),
        json!({"t": at("08:02:40"), "sid": "s", "ev": "SubagentStop"}),
        json!({"t": at("10:00:00"), "sid": "s", "ev": "Stop"}),
        json!({"t": at("10:00:10"), "sid": "s", "ev": "PreToolUse", "tool": "Agent", "id": "fg", "agent": "fore"}),
        json!({"t": at("10:00:20"), "sid": "s", "ev": "SubagentStop", "aid": "fx"}),
        json!({"t": at("10:00:30"), "sid": "s", "ev": "PostToolUse", "tool": "Agent", "id": "fg", "aid": "fx"}),
    ]);
    let split = split_time(&e, "9-f").unwrap();
    let cats: Vec<&str> = split.items().iter().map(|(k, _)| k.as_str()).collect();
    for want in [
        "thinking",
        "gate",
        "dispatching: other tool",
        "writing the spec",
        "edit",
        "waiting: subagent",
        "waiting: a background run",
        "waiting: the GM",
        "other tool",
        "waiting: quote-check",
        "idle (over an hour)",
        "waiting: fore",
    ] {
        assert!(cats.contains(&want), "{want}: {cats:?}");
    }
    assert!(split_time(
        &evs(&[
            json!({"t": "x", "ev": "Stop"}),
            json!({"t": "y", "ev": "Stop"})
        ]),
        "f"
    )
    .is_err());
    let detail = tool_detail(&evs(&[
        json!({"t": at("08:00:00"), "ev": "PreToolUse", "cat": "other tool", "id": "1", "make": "map"}),
        json!({"t": at("08:00:10"), "ev": "PostToolUse", "id": "1"}),
        json!({"t": at("08:00:20"), "ev": "PreToolUse", "cat": "other tool", "id": "2", "tool": "Read"}),
        json!({"t": at("08:00:20"), "ev": "PostToolUse", "id": "2"}),
        json!({"t": at("08:00:30"), "ev": "PreToolUse", "cat": "other tool", "id": "3", "tool": "Grep"}),
        json!({"t": at("08:00:40"), "ev": "PostToolUse", "id": "3"}),
        json!({"t": at("08:00:50"), "ev": "PostToolUse", "id": "4"}),
    ]))
    .unwrap();
    assert_eq!(
        detail
            .items()
            .iter()
            .map(|(k, _)| k.as_str())
            .collect::<Vec<_>>(),
        ["make map", "Grep"]
    );
}

#[test]
fn dispatches_rounds_and_tripwires_are_counted() {
    let agent = |id: &str, agent: &str, cat: &str, extra: Value| {
        let mut m = json!({"t": at("08:00:00"), "ev": "PreToolUse", "tool": "Agent", "id": id, "agent": agent, "cat": cat});
        m.as_object_mut()
            .unwrap()
            .extend(extra.as_object().unwrap().clone());
        m
    };
    let mut list = Vec::new();
    for i in 0..3 {
        list.push(agent(
            &format!("q{i}"),
            "quote-check",
            "record check",
            json!({"manifest": "/tmp/l7r-check/0105-quote-check/MANIFEST.md", "waiver": i}),
        ));
        list.push(json!({"t": at("08:00:01"), "ev": "PostToolUse", "tool": "Agent", "id": format!("q{i}")}));
        list.push(agent(
            &format!("g{i}"),
            "glyph-check",
            "review check",
            json!({"unit": "wheel,"}),
        ));
        list.push(json!({"t": at("08:00:01"), "ev": "PostToolUse", "tool": "Agent", "id": format!("g{i}")}));
    }
    list.push(agent(
        "",
        "glyph-check",
        "review check",
        json!({"unit": "wheel"}),
    ));
    list.push(agent(
        "refused",
        "glyph-check",
        "review check",
        json!({"unit": "wheel"}),
    ));
    list.push(agent("n", "glyph-check", "review check", json!({})));
    list.push(agent("", "glyph-check", "review check", json!({})));
    list.push(agent(
        "o",
        "general-purpose",
        "other subagent",
        json!({"manifest": "MANIFEST.md"}),
    ));
    list.push(json!({"t": at("08:00:02"), "ev": "SubagentStop", "agent": "quote-check", "verdict": "clean"}));
    list.push(json!({"t": at("08:00:02"), "ev": "SubagentStop", "agent": "quote-check", "verdict": "findings"}));
    list.push(json!({"t": at("08:00:02"), "ev": "SubagentStop", "agent": "spec-fidelity", "verdict": "BLOCKED"}));
    let e = evs(&list);
    let wires = tripwires(
        &e,
        &[
            ("1".to_owned(), "red".to_owned()),
            ("2".to_owned(), "red".to_owned()),
            ("3".to_owned(), "green".to_owned()),
        ],
    );
    let what: Vec<&str> = wires.iter().map(|(_, w)| w.as_str()).collect();
    assert_eq!(
        what,
        [
            "red-gate",
            "round:glyph-check|wheel@3",
            "round:glyph-check|wheel@4",
            "round:quote-check|0105@3 (ran on the GM's waiver)"
        ]
    );
    let (by_type, rounds) = dispatches(&e).unwrap();
    assert_eq!(by_type.items().len(), 3);
    assert_eq!(rounds.items().len(), 2);
    assert!(dispatches(&evs(&[json!({"t": "x"})])).is_err());
    assert_eq!(verdicts(&e).len(), 2);
    assert_eq!(
        subject("/tmp/l7r-check/0105-quote-check/MANIFEST.md"),
        "0105"
    );
    assert_eq!(subject("/a/b/c/x.md"), "c");
    assert_eq!(subject("x.md"), "");
    assert_eq!(path_name("/a/b.md/"), "b.md");
    assert_eq!(path_name(""), "");
    assert_eq!(
        tool_cat(&evs(&[json!({"tool": "Agent"})])[0]),
        "dispatching: other tool"
    );
}

#[test]
fn each_task_is_split_at_its_decision_points() {
    let e = evs(&[
        json!({"t": at("08:00:00"), "ev": "Stop"}),
        json!({"t": at("08:30:00"), "ev": "SubagentStop", "agent": "round-arbiter"}),
        json!({"t": at("08:20:00"), "ev": "SubagentStop", "agent": "spec-fidelity"}),
        json!({"t": at("08:31:00"), "ev": "SubagentStop", "agent": "other"}),
        json!({"t": at("09:00:00"), "ev": "Stop"}),
    ]);
    let t = |h: &str| super::super::super::events::ts(&at(h)).unwrap();
    let starts = [
        ("T02".to_owned(), t("08:10:00")),
        ("T01".to_owned(), t("08:00:00")),
    ];
    let ticks = [("T01".to_owned(), t("08:40:00")), ("T02".to_owned(), 0.0)];
    assert_eq!(
        task_rows(&e, &starts, &ticks).unwrap(),
        [
            "| T01 | 40 min | 30 min | 10 min | 2 | 20, 10, 10 |",
            "| T02 | 50 min | 20 min | 30 min | 2 | 10, 10, 30 |"
        ]
    );
    assert_eq!(
        task_rows(&[], &starts[..1], &[]).unwrap()[0],
        format!(
            "| T02 | {} (open) | 0 min | {} | 0 | {} |",
            hm(-t("08:10:00")),
            hm(-t("08:10:00")),
            fixed(-t("08:10:00") / 60.0, 0)
        )
    );
    assert!(task_rows(&evs(&[json!({"t": "x", "ev": "Stop"})]), &starts, &[]).is_err());
    assert!(task_rows(
        &evs(&[
            json!({"t": "x", "ev": "SubagentStop", "agent": "round-arbiter"}),
            json!({"t": at("08:00:00")})
        ]),
        &starts,
        &[]
    )
    .is_err());
    assert_eq!(sorted_starts(&starts)[0].0, "T01");
}

#[test]
fn each_check_is_costed_per_changed_line() {
    let e = evs(&[json!({"aid": "a1"}), json!({"aid": "a2"}), json!({})]);
    let pass = |v: Value| -> Map<String, Value> { v.as_object().unwrap().clone() };
    let passes = [
        pass(
            json!({"check": "q", "agent": "a1", "wall": "90 s", "tokens": "1.5k in (1k cached) / 2M out"}),
        ),
        pass(json!({"check": "q", "agent": "a2", "wall": "x", "tokens": ""})),
        pass(json!({"agent": "a2", "wall": "1s", "tokens": "300 in / 3 out"})),
        pass(json!({"check": "q", "agent": "zz"})),
    ];
    assert_eq!(
        check_rows(&e, &passes, 0).unwrap(),
        [
            "| q | 2 | 2 min | 2k | 2000.0k | 2.000 | 1.5k |",
            "| ? | 1 | 0 min | 0k | 0.0k | 1.000 | 0.3k |"
        ]
    );
    assert_eq!(
        check_rows(
            &e,
            &[pass(
                json!({"check": "q", "agent": "a1", "wall": "1.2.3 s"})
            )],
            1
        ),
        None
    );
    assert_eq!(
        check_rows(
            &e,
            &[pass(
                json!({"check": "q", "agent": "a1", "wall": "1 s", "tokens": ". in / 1 out"})
            )],
            1
        ),
        None
    );
    assert_eq!(
        check_rows(
            &e,
            &[pass(
                json!({"check": "q", "agent": "a1", "wall": "1 s", "tokens": "1 in / . out"})
            )],
            1
        ),
        None
    );
    assert_eq!(
        under(std::path::Path::new("/a"), std::path::Path::new("/a/b")),
        "b"
    );
}
