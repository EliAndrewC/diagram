//! The command over two clones' logs of two features: one table across them, the landed tasks each with its tables, the rest of the
//! window apart, and the programs read from the session's and its builder's transcripts.

use std::fmt::Write as _;
use std::path::Path;

use serde_json::{json, Value};

use super::super::events::{ts, Event};
use super::book::tests::day;
use super::*;

fn put(dir: &Path, rel: &str, lines: &[Event]) {
    let p = dir.join(rel);
    std::fs::create_dir_all(p.parent().unwrap()).unwrap();
    let text = lines.iter().fold(String::new(), |mut t, e| {
        let _ = writeln!(t, "{}", Value::Object(e.clone()));
        t
    });
    std::fs::write(p, text).unwrap();
}

fn ev(v: &Value) -> Event {
    v.as_object().unwrap().clone()
}

fn args(list: &[&str]) -> Vec<String> {
    list.iter().map(|s| (*s).to_owned()).collect()
}

fn world() -> (l7r_shared::tempdir::TempDir, String) {
    let d = crate::checks::scratch("task-time");
    let (stream, mut aside, _) = day();
    let end = |t: &str, tasks: &[&str], landed: bool| {
        ev(
            &json!({"t": format!("2026-11-25T10:{t}Z"), "ev": "Phase", "src": "land", "step": "end", "t0": "2026-11-25T10:06:00Z",
            "t1": format!("2026-11-25T10:{t}Z"), "sid": "s", "tasks": tasks, "landed": landed}),
        )
    };
    aside.push(end("06:45", &["T1"], true));
    aside.push(end("06:30", &["T7"], false));
    aside.push(ev(
        &json!({"t": "2026-11-25T10:06:52Z", "ev": "Phase", "src": "page-session", "step": "write",
        "t0": "2026-11-25T10:06:00Z", "t1": "2026-11-25T10:06:52Z", "sid": "p"}),
    ));
    let mut all = stream;
    all.extend(aside);
    put(&d, "root/.git/l7r-events/451-x.jsonl", &all);
    // another clone's session under another feature, its landing of a task numbered like this feature's
    put(
        &d,
        "clones/c1/.git/l7r-events/449-z.jsonl",
        &[
            ev(
                &json!({"t": "2026-11-25T10:01:00Z", "sid": "s2", "ev": "UserPromptSubmit", "task": "T1"}),
            ),
            ev(&json!({"t": "2026-11-25T10:01:30Z", "sid": "s2", "ev": "Stop", "task": "T1"})),
            end("02:00", &["T1"], true),
        ],
    );
    let tu = |id: &str, cmd: &str| {
        format!(
            "{}\n",
            json!({"message": {"content": [{"type": "tool_use", "id": id, "name": "Bash", "input": {"command": cmd}}]}})
        )
    };
    let home = d.join("home/p");
    std::fs::create_dir_all(home.join("s/subagents")).unwrap();
    std::fs::write(home.join("s.jsonl"), tu("b4", "cargo test -p x")).unwrap();
    std::fs::write(
        home.join("s/subagents/agent-B.jsonl"),
        tu("b3", "until [ -s /tmp/x ]; do sleep 5; done"),
    )
    .unwrap();
    let root = d.join("root").display().to_string();
    (d, root)
}

#[test]
fn one_table_across_features_each_landed_task_its_own() {
    let (d, root) = world();
    let (projects, clones) = (d.join("home"), d.join("clones"));
    let now = ts("2026-11-25T10:30:00Z").unwrap();
    let r = cli(
        &args(&[
            "--root",
            &root,
            "--since",
            "2026-11-25T10:00:00Z",
            "--until",
            "2026-11-25T10:06:50Z",
        ]),
        &projects,
        &clones,
        now,
    );
    assert_eq!(r.code, 0, "{}", r.stderr);
    let out = r.stdout;
    for want in [
        "# The task time breakdown, 2026-11-25T10:00:00Z to 2026-11-25T10:06:50Z UTC (2 tasks landed)",
        "## 451-x T1 (landed 10:06)",
        "## 449-z T1 (landed 10:02)",
        "| cargo, called directly | 0.5 | ",
        "| cargo | cargo, called directly | 1 | 0.5 | ",
        "| a wait loop (until/while/sleep) | wait loops (held open, no work) | 1 | 1.8 | ",
        "| make static | tests | 1 | 1.0 | ",
        "| main session: reading code | 0.2 | ",
        "| plan review: agents | 1.0 | ",
        "| research and page sessions | 0.8 | ",
        "## The rest of the window",
        "## The whole window",
        "- tests: 2.5 min blocking (",
        "Unbooked, named: 0 Bash calls refused before running",
    ] {
        assert!(out.contains(want), "{want}\n---\n{out}");
    }
    assert!(!out.contains("T7"), "a refused landing lands nothing");
    let only = cli(
        &args(&[
            "--root",
            &root,
            "--since",
            "2026-11-25T10:00:00Z",
            "--feature",
            "449",
        ]),
        &projects,
        &clones,
        now,
    );
    assert!(
        only.stdout.contains("(1 tasks landed)") && only.stdout.contains("## 449-z T1"),
        "{}",
        only.stdout
    );
    let back = cli(
        &args(&["--root", &root, "--since", "24h"]),
        &projects,
        &clones,
        now,
    );
    assert!(
        back.stdout.contains("2026-11-24T10:30:00Z to "),
        "{}",
        back.stdout
    );
}

#[test]
fn a_landed_task_carries_its_time_before_the_window() {
    let (d, root) = world();
    let (projects, clones) = (d.join("home"), d.join("clones"));
    let now = ts("2026-11-25T10:30:00Z").unwrap();
    let late = |back: &str| {
        cli(
            &args(&[
                "--root",
                &root,
                "--since",
                "2026-11-25T10:03:00Z",
                "--until",
                "2026-11-25T10:06:50Z",
                "--back",
                back,
            ]),
            &projects,
            &clones,
            now,
        )
    };
    // the session's clock runs 10:00:00-10:06:50, 410 s; the window holds its last 230 s, and the window's own figures stay its own
    let r = late("1h");
    for want in [
        "minutes 5.6 (machine, overlapping), blocking 3.8 (the main sessions' clock)",
        "Its whole time, from 2026-11-25T09:03:00Z: 8.9 min, 6.8 min blocking; inside the window 4.8 min (53.5% of it), 3.8 min blocking (56.1%);",
    ] {
        assert!(r.stdout.contains(want), "{want}\n---\n{}", r.stdout);
    }
    // read nothing back: the task's whole time is its time inside, and a wait begun before the window (its `Stop` unread) is lost to
    // the window's own figures too - 0.8 min of its 3.8
    let z = late("0h").stdout;
    assert!(
        z.contains("blocking 0.8 (the main sessions' clock)")
            && z.contains("inside the window 2.8 min (100.0% of it), 0.8 min blocking (100.0%)")
    );
    let bad = late("x");
    assert_eq!(
        (bad.code, bad.stderr.as_str()),
        (1, "task-time: BACK=x: <N>h\n")
    );
}

#[test]
fn the_command_line_refuses_what_it_cannot_read() {
    let none = Path::new("/nonexistent");
    assert_eq!(cli(&args(&["--nope"]), none, none, 0.0).code, 2);
    let bad = cli(&args(&["--since", "xh"]), none, none, 0.0);
    assert_eq!(
        (bad.code, bad.stderr.as_str()),
        (1, "task-time: SINCE=xh: <N>h or an ISO time\n")
    );
    assert_eq!(
        since_of("2026-11-25T00:00:00Z", 0.0).unwrap(),
        "2026-11-25T00:00:00Z"
    );
    assert_eq!(pct(1.0, 0.0), "-");
    let page = ev(&json!({"ev": "Phase", "src": "page-session", "t0": 1}));
    assert!(pages(&[page]).is_err());
    // a page session run under a task books to it (the command's own world runs one under none, `-`)
    let tasked = ev(
        &json!({"ev": "Phase", "src": "page-session", "t0": "2026-11-25T10:00:00Z", "t1": "2026-11-25T10:01:00Z", "task": "T3"}),
    );
    assert_eq!(pages(&[tasked]).unwrap()[0].key.1, "T3");
}
