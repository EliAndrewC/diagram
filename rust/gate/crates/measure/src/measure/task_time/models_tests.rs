//! Feature 451 T532: every token figure split by model (each call's `message.model`) - a landed task's by actor and model, each
//! actor's window totals by model, and the window's model mix beside its concurrency; raw counts, no rate or weight.

use std::path::Path;

use serde_json::json;

use super::super::events::{ts, Event};
use super::super::where_time::columns::spent::Tok;
use super::tests::{args, world};
use super::*;

/// A usage row of a transcript on `model`, none where it is empty; a session call booked to a task runs a command naming it.
fn usage(id: &str, t: &str, model: &str, (out, cached): (u64, u64)) -> String {
    let mut msg = json!({"id": id, "usage": {"output_tokens": out, "input_tokens": 0, "cache_read_input_tokens": cached,
        "cache_creation_input_tokens": 0}});
    if !model.is_empty() {
        msg["model"] = json!(model);
    }
    if id == "m4" {
        msg["content"] = json!([{"type": "tool_use", "id": "b1", "name": "Bash", "input": {"command": "make static T=T1"}}]);
    }
    format!(
        "{}\n",
        json!({"timestamp": format!("2026-11-25T10:{t}Z"), "message": msg})
    )
}

fn append(p: &Path, text: &str) {
    let mut t = std::fs::read_to_string(p).unwrap_or_default();
    t.push_str(text);
    std::fs::write(p, t).unwrap();
}

/// The observed case (451 T532's task line: one session's transcript on two models): the session's calls on two models, one of
/// them before 451-x T1's own line and naming T1 in its command (451 T513), a builder of T1 on a third, and a call naming no
/// model - each split, each sum the unsplit one.
#[test]
fn every_token_figure_is_split_by_model() {
    let (d, root) = world();
    let home = d.join("home/p");
    append(
        &home.join("s/subagents/agent-B.jsonl"),
        &[
            usage("m1", "02:05", "claude-sonnet-5-5", (100, 1000)),
            usage("m2", "05:15", "", (10, 0)),
        ]
        .concat(),
    );
    append(
        &home.join("s.jsonl"),
        &[
            usage("m4", "00:09", "claude-opus-5-5", (50, 0)),
            usage("m5", "06:08", "claude-fable-5-2", (30, 0)),
            usage("m6", "06:49", "claude-opus-5-5", (20, 0)),
        ]
        .concat(),
    );
    let now = ts("2026-11-25T10:30:00Z").unwrap();
    let got = cli(
        &args(&[
            "--root",
            &root,
            "--since",
            "2026-11-25T10:00:00Z",
            "--until",
            "2026-11-25T10:06:50Z",
        ]),
        &d.join("home"),
        &d.join("clones"),
        now,
    );
    assert_eq!(got.code, 0, "{}", got.stderr);
    let out = got.stdout;
    for want in [
        "## Tokens by model (451 T532",
        // T1's builder on sonnet and on no model named; its session call on opus, the one naming it (451 T513)
        "| 451-x T1 | builders | (no model named) | 1 | 0.0k | 0.0k | 0.0k | 0.0k | 0.0k (0.9%) |",
        "| 451-x T1 | builders | claude-sonnet-5-5 | 1 | 0.1k | 0.0k | 1.0k | 0.0k | 1.1k (94.8%) |",
        "| 451-x T1 | session | claude-opus-5-5 | 1 | 0.1k | 0.0k | 0.0k | 0.0k | 0.1k (4.3%) |",
        // the window: every actor's calls, booked to a task or not (the opus call before T1's own line among them)
        "| the window | session | claude-fable-5-2 | 1 | 0.0k | 0.0k | 0.0k | 0.0k | 0.0k (2.5%) |",
        "| the window | session | claude-opus-5-5 | 2 | 0.1k | 0.0k | 0.0k | 0.0k | 0.1k (5.8%) |",
        "The window's model mix (451 T532): claude-sonnet-5-5 1 calls, 1.1k tokens (90.9%); claude-opus-5-5 2 calls, 0.1k tokens \
         (5.8%); claude-fable-5-2 1 calls, 0.0k tokens (2.5%); (no model named) 1 calls, 0.0k tokens (0.8%) - at 0.00 pool trees \
         held, time-weighted over the window",
    ] {
        assert!(out.contains(want), "{want}\n---\n{out}");
    }
}

/// The split's sums are the unsplit figures (each task's actor by actor, the window's every call), the window's concurrency is its
/// tree-seconds over its seconds, and a window of no calls says so.
#[test]
fn the_split_sums_to_the_unsplit_figures_and_the_concurrency_is_time_weighted() {
    use super::super::where_time::columns::spent::{add_call, Call, Models};
    use super::super::where_time::columns::Agent;
    use super::cross::{measure, Cross};
    use super::held::Hold;
    use super::models::{mix, trees};
    use super::turns::{ByModel, Read};
    use std::collections::{HashMap, HashSet};
    let tok = |out: f64| Tok {
        out,
        ..Tok::default()
    };
    let agents = [Agent {
        aid: "A".to_owned(),
        kind: "general-purpose".to_owned(),
        task: "T1".to_owned(),
        ..Agent::default()
    }];
    let stream: Vec<Event> = [
        json!({"t": "2026-11-25T10:00:00Z", "aid": "A", "feature": "451-x"}),
        json!({"t": "2026-11-25T10:00:06Z", "sid": "s", "ev": "PreToolUse", "id": "u1", "feature": "451-x", "names": ["T1"]}),
    ]
    .iter()
    .map(|v| v.as_object().unwrap().clone())
    .collect();
    let at = ts("2026-11-25T10:00:05Z").unwrap();
    let late = ts("2026-11-25T10:00:20Z").unwrap();
    let mut by = Models::new();
    add_call(&mut by, "a", tok(3.0));
    add_call(&mut by, "b", tok(4.0));
    let session = HashMap::from([(
        "s".to_owned(),
        vec![
            Call {
                at,
                tok: tok(10.0),
                uses: vec![("u1".to_owned(), vec!["T1".to_owned()])],
                model: "a".to_owned(),
            },
            Call {
                at: late,
                tok: tok(20.0),
                uses: Vec::new(),
                model: "b".to_owned(),
            },
        ],
    )]);
    let read = Read {
        calls: &HashMap::from([("A".to_owned(), 2)]),
        tokens: &HashMap::from([("A".to_owned(), tok(7.0))]),
        session: &session,
        models: &HashMap::from([("A".to_owned(), by)]),
        paged: &HashSet::new(),
    };
    let (got, unbooked, (split, window)) =
        turns::of(&stream, &agents, &read, (&HashMap::new(), 0.0));
    let key = ("451-x".to_owned(), "T1".to_owned());
    let sum = |m: &Models| {
        m.values()
            .fold((0, 0.0), |(n, o), (k, t)| (n + k, o + t.out))
    };
    let (t, s) = (&got[&key], &split[&key]);
    assert_eq!(sum(&s.builders), (t.builders, t.builders_tok.out));
    assert_eq!(sum(&s.session), (t.session, t.session_tok.out));
    assert_eq!(sum(&window.session), (t.session + unbooked.calls, 30.0));
    assert_eq!(sum(&window.builders), (2, 7.0));
    let holds = [
        Hold {
            from: 0.0,
            until: 100.0,
            tree: "a".to_owned(),
            feature: "451".to_owned(),
            tasks: vec!["T1".to_owned()],
        },
        Hold {
            from: 50.0,
            until: f64::INFINITY,
            tree: "b".to_owned(),
            feature: "451".to_owned(),
            tasks: vec!["T2".to_owned()],
        },
    ];
    let c = measure(&holds, &[], &[], (0.0, 100.0), 3);
    assert!((trees(&c, (0.0, 100.0)) - 1.5).abs() < 1e-9);
    assert!(trees(&Cross::default(), (5.0, 5.0)).abs() < f64::EPSILON);
    assert!(mix(&ByModel::default(), 0.0)
        .contains("model mix (451 T532): no calls - at 0.00 pool trees"));
}
