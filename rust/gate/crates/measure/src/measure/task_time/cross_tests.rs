//! The window in two parts, and a task's wait on a landing (feature 451 T510; the GM 2026-11-27: "the denominators should just be
//! totally separate except to the degree that things in one category actually are blocking things in the other category").
//!
//! The fixture: a builder for T2 in tree `pb` runs from 00:11 to 05:00 beside a landing of T1 (02:00 to 04:00, its gate 02:10 to
//! 03:50) the session waits on. Tree `pa` was freed at 01:00 by T1's build half and handed to T1's closing half only at 04:30, after
//! the landing; the session's handout for it at 02:30 was refused (T1's done commit not yet carried). Tree `pc` stood free from
//! 00:30 to 01:30 with no landing running, and from 03:00 on with no handout after it - counted to the window's end, so 03:00 to
//! 04:00 of the landing (461 T33). The session waits on the GM 05:10 to 05:20.

use std::fmt::Write as _;

use serde_json::{json, Value};

use super::super::events::ts;
use super::cli;

fn at(ms: &str) -> String {
    format!("2026-11-26T10:{ms}Z")
}

fn line(t: &str, ev: &str, extra: &Value) -> Value {
    let mut v = json!({"t": at(t), "sid": "s", "ev": ev, "task": "T1"});
    for (k, x) in extra.as_object().unwrap() {
        v[k] = x.clone();
    }
    v
}

fn bash(t0: &str, t1: &str, id: &str, extra: &Value, end: &str) -> [Value; 2] {
    let mut e = extra.clone();
    e["tool"] = json!("Bash");
    e["id"] = json!(id);
    [line(t0, "PreToolUse", &e), line(t1, end, &e)]
}

fn phase(step: &str, t0: &str, t1: &str, extra: &Value) -> Value {
    let mut v = json!({"t": at(t1), "ev": "Phase", "src": "land", "step": step, "t0": at(t0), "t1": at(t1), "sid": "s"});
    for (k, x) in extra.as_object().unwrap() {
        v[k] = x.clone();
    }
    v
}

fn lines() -> Vec<Value> {
    let none = json!({});
    let mut all = vec![
        line("00:00", "UserPromptSubmit", &none),
        line("00:10", "PreToolUse", &json!({"tool": "Agent", "id": "a2"})),
        line(
            "00:11",
            "PostToolUse",
            &json!({"tool": "Agent", "id": "a2", "aid": "B2"}),
        ),
        line(
            "00:11",
            "SubagentStart",
            &json!({"aid": "B2", "agent": "general-purpose", "task": "T2"}),
        ),
        line(
            "00:20",
            "Stop",
            &json!({"inflight": [{"id": "B2", "type": "subagent"}]}),
        ),
        line("01:55", "UserPromptSubmit", &json!({"gm": false})),
    ];
    all.extend(bash(
        "02:00",
        "02:01",
        "l1",
        &json!({"make": "land", "bg_id": "xl1"}),
        "PostToolUse",
    ));
    all.extend([
        line(
            "02:02",
            "Stop",
            &json!({"inflight": [{"id": "xl1", "type": "shell"}, {"id": "B2", "type": "subagent"}]}),
        ),
        line("02:29", "UserPromptSubmit", &json!({"gm": false})),
    ]);
    // the handout refused: T1's done commit is not yet carried
    all.extend(bash(
        "02:30",
        "02:31",
        "rb",
        &json!({"make": "builder-brief"}),
        "PostToolUseFailure",
    ));
    all.extend([
        line(
            "02:32",
            "Stop",
            &json!({"inflight": [{"id": "xl1", "type": "shell"}, {"id": "B2", "type": "subagent"}]}),
        ),
        phase("gate", "02:10", "03:50", &json!({"code": 0})),
        phase(
            "end",
            "02:00",
            "04:00",
            &json!({"tasks": ["T1"], "landed": true}),
        ),
        json!({"t": at("04:01"), "sid": "s", "ev": "BgEnd", "id": "l1"}),
        line("04:10", "UserPromptSubmit", &json!({"gm": false})),
        line(
            "04:20",
            "Stop",
            &json!({"inflight": [{"id": "B2", "type": "subagent"}]}),
        ),
        line(
            "05:00",
            "SubagentStop",
            &json!({"aid": "B2", "agent": "general-purpose", "task": "T2"}),
        ),
        line("05:01", "UserPromptSubmit", &json!({"gm": false})),
        // the session waits on the GM
        line("05:10", "Stop", &none),
        line("05:20", "UserPromptSubmit", &none),
    ]);
    all
}

fn pool() -> String {
    let row = |t: &str, event: &str, tree: &str, detail: &str| json!({"utc": at(t), "event": event, "tree": format!("/x/{tree}"), "detail": detail});
    [
        row("00:00", "take", "pa", "451 T1"),
        row("00:00", "take", "pb", "451 T2"),
        row("00:00", "take", "pc", "451 T4"),
        row("00:30", "release", "pc", "451 T4"),
        row("01:00", "done", "pa", "451 T1"),
        row("01:00", "release", "pa", "451 T1"),
        row("01:30", "take", "pc", "451 T5"),
        row("03:00", "release", "pc", "451 T5"),
        row("04:30", "take", "pa", "451 T1"),
    ]
    .iter()
    .fold(String::new(), |mut t, v| {
        let _ = writeln!(t, "{v}");
        t
    })
}

fn report(name: &str) -> String {
    let d = crate::checks::scratch(name);
    let git = d.join("root/.git");
    std::fs::create_dir_all(git.join("l7r-events")).unwrap();
    let text = lines().iter().fold(String::new(), |mut t, v| {
        let _ = writeln!(t, "{v}");
        t
    });
    std::fs::write(git.join("l7r-events/451-x.jsonl"), text).unwrap();
    std::fs::write(git.join("builder-pool.log"), pool()).unwrap();
    let tu = |id: &str, cmd: &str| {
        format!(
            "{}\n",
            json!({"message": {"content": [{"type": "tool_use", "id": id, "name": "Bash", "input": {"command": cmd}}]}})
        )
    };
    let home = d.join("home/p");
    std::fs::create_dir_all(&home).unwrap();
    std::fs::write(
        home.join("s.jsonl"),
        [
            tu("l1", "make land F=451 T=T1 NOTE=x"),
            tu("rb", "make builder-brief T=T1 F=451 KIND=closing-half"),
        ]
        .concat(),
    )
    .unwrap();
    let root = d.join("root").display().to_string();
    let list = [
        "--root",
        &root,
        "--since",
        &at("00:00"),
        "--until",
        &at("05:30"),
    ];
    let args: Vec<String> = list.iter().map(|s| (*s).to_owned()).collect();
    let r = cli(
        &args,
        &d.join("home"),
        &d.join("clones"),
        ts(&at("06:00")).unwrap(),
    );
    assert_eq!(r.code, 0, "{}", r.stderr);
    r.stdout
}

fn has(out: &str, wants: &[&str]) {
    for want in wants {
        assert!(out.contains(want), "{want}\n---\n{out}");
    }
}

/// The percentage column `n` (1-based, of `| a | b | ...`) of each row of the table under `heading`, its totals rows left out.
fn shares(out: &str, heading: &str, n: usize) -> f64 {
    let from = out.find(heading).unwrap();
    out[from..]
        .lines()
        .skip(4)
        .take_while(|l| l.starts_with('|'))
        .filter(|l| !l.starts_with("| the tasks' side,") && !l.starts_with("| the landings' side,"))
        .filter_map(|l| {
            l.split('|')
                .nth(n)?
                .trim()
                .strip_suffix('%')?
                .parse::<f64>()
                .ok()
        })
        .sum()
}

/// The window's table in two parts, each with its own totals: no percentage of one part is of the other's total, the GM's row
/// stays apart as it was, and the tasks' side carries the minutes a task waited on a landing.
#[test]
fn the_window_s_table_is_in_two_parts_each_its_own_denominator() {
    let out = report("task-time-cross-parts");
    let tasks = "## The window: the tasks' side";
    let landings = "## The window: the landings' side (the second tier)";
    has(
        &out,
        &[
            &format!("{tasks}\n\n| category | minutes | % of the tasks' | blocking | % of the tasks' |"),
            &format!("{landings}\n\n| category | minutes | % of the landings' | blocking | % of the landings' |"),
            "| the tasks' side, working (all but waiting on the GM) | ",
            "| the landings' side, working | ",
            // the cross-blocking row: 02:00 to 04:30, a tree free while a landing ran and the refused handout, counted once a second -
            // two trees, pa and pc, 03:00 to 04:00 (461 T33)
            "| a task waited on a landing (cross-blocking) | - | | 3.5 | ",
            // the GM's row as before: of the whole
            "| the GM | 0.0 | 0.0% | 0.2 | ",
        ],
    );
    let (t, l) = (out.find(tasks).unwrap(), out.find(landings).unwrap());
    assert!(t < l && l < out.find("## The landed tasks").unwrap());
    // the landing's own run is on its side alone (its gate, waited on beside the builder, blocks nothing)
    assert!(!out[t..l].contains("| landing |"), "{out}");
    has(&out[l..], &["| landing | "]);
    // each part's percentages sum to its own 100
    for (h, n) in [(tasks, 5), (landings, 3), (landings, 5)] {
        let sum = shares(&out, h, n);
        assert!((sum - 100.0).abs() < 0.5, "{h} column {n}: {sum}\n{out}");
    }
}

/// The cross-blocking row names each source and its figure, and what the records cannot show.
#[test]
fn a_task_s_wait_on_a_landing_names_each_source() {
    let out = report("task-time-cross-sources");
    has(
        &out,
        &[
            "A task waited on a landing (cross-blocking): 3.5 min, in the tasks' side's blocking.",
            // pa free 01:00 to 04:30, the landing 02:00 to 04:00: 2.0; pc free from 03:00 with no handout after, counted to the
            // window's end (461 T33): 03:00 to 04:00 of the landing, 1.0; its 00:30 to 01:30 span had no landing
            "a free pool tree not handed out while a landing ran: 3.0 min",
            // the refused handout at 02:30, to T1's next handout at 04:30
            "a handout refused while its task's done commit was not carried: 2.0 min (1 refused)",
            "Not in the records:",
        ],
    );
}
