//! Two builders at once in two pool trees, through the command (feature 451 T391, T393): one session, a builder for T1 in `pool-a`
//! (handed out for the bundle `T1,T3`) and one for T2 in `pool-b`, each inside its own `make builder-checks` at the same moment;
//! `pool-a`'s build line carries T9, the task of that tree's last `make task-start`, as every pool tree's line did before 451 T332.
//! `pool-b` was MADE for T2 (a `make` row, no `take`). The session then carries both trees and lands the three.

use std::fmt::Write as _;
use std::path::Path;

use serde_json::{json, Value};

use super::super::events::ts;
use super::cli;

fn at(ms: &str) -> String {
    format!("2026-11-26T10:{ms}Z")
}

fn line(t: &str, ev: &str, extra: &Value) -> Value {
    let mut v = json!({"t": at(t), "sid": "s", "ev": ev});
    for (k, x) in extra.as_object().unwrap() {
        v[k] = x.clone();
    }
    v
}

fn bash(t0: &str, t1: &str, id: &str, extra: &Value) -> [Value; 2] {
    let mut e = extra.clone();
    e["tool"] = json!("Bash");
    e["id"] = json!(id);
    [line(t0, "PreToolUse", &e), line(t1, "PostToolUse", &e)]
}

fn builder(t: &str, call: &str, aid: &str, task: &str) -> [Value; 3] {
    [
        line(t, "PreToolUse", &json!({"tool": "Agent", "id": call})),
        line(
            t,
            "PostToolUse",
            &json!({"tool": "Agent", "id": call, "aid": aid}),
        ),
        line(
            t,
            "SubagentStart",
            &json!({"aid": aid, "agent": "general-purpose", "task": task}),
        ),
    ]
}

fn phase(src: &str, step: &str, (t0, t1): (&str, &str), extra: &Value) -> Value {
    line(
        t1,
        "Phase",
        &json!({"src": src, "step": step, "t0": at(t0), "t1": at(t1)}),
    )
    .as_object()
    .unwrap()
    .iter()
    .chain(extra.as_object().unwrap())
    .map(|(k, x)| (k.clone(), x.clone()))
    .collect::<serde_json::Map<String, Value>>()
    .into()
}

fn lines() -> Vec<Value> {
    let mut all = vec![line("00:00", "UserPromptSubmit", &json!({}))];
    all.extend(builder("00:10", "a1", "B1", "T1"));
    all.extend(builder("00:11", "a2", "B2", "T2"));
    let checks = |by: &str, task: &str| json!({"make": "builder-checks", "by": by, "task": task});
    all.extend(bash("00:20", "02:00", "c1", &checks("B1", "T1")));
    all.extend(bash("00:30", "02:00", "c2", &checks("B2", "T2")));
    // pool-a's build, 40 s, under the task of the tree's last start
    all.push(phase(
        "rust",
        "build",
        ("00:40", "01:20"),
        &json!({"make": "builder-checks", "clone": "/x/pool-a", "task": "T9"}),
    ));
    for aid in ["B1", "B2"] {
        all.push(line(
            "02:05",
            "SubagentStop",
            &json!({"aid": aid, "agent": "general-purpose"}),
        ));
    }
    all.push(line("02:06", "UserPromptSubmit", &json!({"gm": false})));
    all.extend(bash("02:10", "02:20", "cy", &json!({"make": "carry"})));
    all.extend(bash("02:22", "02:30", "cz", &json!({"make": "carry"})));
    all.extend(bash("02:40", "03:10", "l1", &json!({"make": "land"})));
    all.push(phase(
        "land",
        "end",
        ("02:45", "03:05"),
        &json!({"tasks": ["T1", "T2", "T3"], "landed": true}),
    ));
    all
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
    let hand = |event: &str, tree: &str, detail: &str| json!({"utc": at("00:01"), "event": event, "tree": tree, "detail": detail});
    std::fs::write(
        git.join("builder-pool.log"),
        format!(
            "{}\n{}\n",
            hand("take", "/x/pool-a", "451 T1,T3"),
            // a tree made for its task: its first holder is written so, never as a take
            hand("make", "/x/pool-b", "451 T2")
        ),
    )
    .unwrap();
    let tu = |id: &str, cmd: &str| json!({"message": {"content": [{"type": "tool_use", "id": id, "name": "Bash", "input": {"command": cmd}}]}});
    let home = d.join("home/p");
    std::fs::create_dir_all(&home).unwrap();
    std::fs::write(
        home.join("s.jsonl"),
        format!(
            "{}\n{}\n{}\n",
            tu("cy", "make carry FROM=/x/pool-a"),
            tu("cz", "make carry FROM=/x/pool-b"),
            tu("l1", "make land F=451 T=\"T1 T2 T3\" NOTE=x")
        ),
    )
    .unwrap();
    let root = d.join("root").display().to_string();
    let list = [
        "--root",
        &root,
        "--since",
        &at("00:00"),
        "--until",
        &at("03:30"),
    ];
    let args: Vec<String> = list.iter().map(|s| (*s).to_owned()).collect();
    let r = cli(
        &args,
        Path::new(&d.join("home")),
        &d.join("clones"),
        ts(&at("04:00")).unwrap(),
    );
    assert_eq!(r.code, 0, "{}", r.stderr);
    r.stdout
}

fn section<'a>(out: &'a str, task: &str) -> &'a str {
    let from = out.find(&format!("## 451-x {task} (landed")).unwrap();
    let rest = &out[from + 3..];
    &rest[..rest.find("\n## ").unwrap()]
}

/// T391: the 40 s build is T1's - its tree's holder's - where its line's stale task tied it to the run begun last, T2's.
#[test]
fn a_pool_tree_s_build_is_its_holder_s_whatever_task_its_line_names() {
    let out = report("task-time-pool-retask");
    let (one, two) = (section(&out, "T1"), section(&out, "T2"));
    assert!(one.contains("| compile | 0.7 | "), "{one}");
    assert!(one.contains("| tests | 1.0 | "), "{one}");
    assert!(!two.contains("| compile |"), "{two}");
    assert!(two.contains("| tests | 1.5 | "), "{two}");
    // only the attribution moves: the window's compile is the same 40 s
    let window = "| compile | 0.7 | 9.5% | 0.7 | 9.5% |";
    assert!(out.contains(window), "{out}");
    assert!(out.contains("0 phases tied to no run"), "{out}");
}

/// T393: the carry of a tree held for the bundle `T1,T3` is each member's, and its run is the first's - never a task `T1,T3`'s.
/// And a tree made for its task (T274's, 2026-11-26) is held from its making: its carry is found.
#[test]
fn a_bundle_s_carry_is_each_of_its_tasks() {
    let out = report("task-time-pool-bundle");
    for want in [
        "| 451-x T1 | 10:03 | 1 | 1.9 | 2.1 | 2.1 | its carry, 10:02 |",
        // the tree MADE for T2 names its carry's task as a take does
        "| 451-x T2 | 10:03 | 1 | 1.9 | 2.0 | 2.0 | its carry, 10:02 |",
        "| 451-x T3 | 10:03 | 0 | 0.0 | 0.0 | 0.0 | its carry, 10:02 |",
    ] {
        assert!(out.contains(want), "{want}\n{out}");
    }
    assert!(section(&out, "T1").contains("| make carry | carry into the clone | 1 | 0.2 | "));
    assert!(!out.contains("T1,T3"), "{out}");
}
