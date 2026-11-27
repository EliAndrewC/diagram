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
        "## 451-x T1 (landed 10:06; no start recorded",
        "## 449-z T1 (landed 10:02; no start recorded",
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
    // a refused landing lands nothing: its batch is named in the second tier's section, not landed, and no task's section is its
    assert!(out.contains("| 451-x T7 | not landed | 1 | 0 | ") && !out.contains("## 451-x T7"));
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
        "minutes 5.6 (machine, overlapping), blocking 3.8 (by task and dependency",
        // T1's own table ends where its landing starts (no carry found): the session's last 45 s are the second tier's (451 T298)
        "the landed tasks' 3.0)",
        "Its whole time, from 2026-11-25T09:03:00Z: 8.1 min, 6.0 min blocking; inside the window 4.0 min (49.2% of it), 3.0 min blocking (50.0%);",
    ] {
        assert!(r.stdout.contains(want), "{want}\n---\n{}", r.stdout);
    }
    // read nothing back: the task's whole time is its time inside, and a wait begun before the window (its `Stop` unread) is lost to
    // the window's own figures too - 0.8 min of its 3.8
    let z = late("0h").stdout;
    // (those 0.8 min, the session's time from the landing's start, are the second tier's since 451 T298)
    for want in [
        "blocking 0.8 (by task and dependency",
        "inside the window 2.0 min (100.0% of it), 0.0 min blocking (-)",
    ] {
        assert!(z.contains(want), "{want}\n---\n{z}");
    }
    let bad = late("x");
    assert_eq!(
        (bad.code, bad.stderr.as_str()),
        (1, "task-time: BACK=x: <N>h\n")
    );
}

#[test]
fn a_landed_task_started_before_the_read_back_is_named() {
    let (d, root) = world();
    let (projects, clones) = (d.join("home"), d.join("clones"));
    let now = ts("2026-11-25T10:30:00Z").unwrap();
    let run = |back: &str| {
        cli(
            &args(&[
                "--root",
                &root,
                "--since",
                "2026-11-25T10:01:00Z",
                "--back",
                back,
            ]),
            &projects,
            &clones,
            now,
        )
        .stdout
    };
    // no start recorded anywhere: each landed task is named, since its time before the read-back may be missing
    let none = run("1h");
    assert!(
        none.contains("## 449-z T1 (landed 10:02; no start recorded: its time before 2026-11-25T09:01:00Z may be missing)")
            && none.contains("`BACK=` reads further): 451-x T1, 449-z T1 -")
    );
    // its first start counts (a restart is not its start), from any tree's record
    let line = |f: &str, t: &str, at: &str| ev(&json!({"feature": f, "task": t, "utc": at}));
    put(
        &d,
        "root/.git/task-starts.jsonl",
        &[
            line("451-x", "T1", "2026-11-25T09:30:00Z"),
            line("451-x", "T1", "2026-11-25T08:00:00Z"),
            // a line with no time is no start
            ev(&json!({"feature": "449-z", "task": "T1"})),
        ],
    );
    put(
        &d,
        "clones/c1/.git/task-starts.jsonl",
        &[line("449-z", "T1", "2026-11-25T10:00:30Z")],
    );
    let one = run("1h");
    for want in [
        "## 451-x T1 (landed 10:06; started 2026-11-25T08:00:00Z, before the read-back: its time before 2026-11-25T09:01:00Z is not in its tables)",
        "## 449-z T1 (landed 10:02)\n",
        "Cut at the read-back (2026-11-25T09:01:00Z, `BACK=` reads further): 451-x T1 - ",
    ] {
        assert!(one.contains(want), "{want}\n---\n{one}");
    }
    // read back far enough and nothing is cut
    let all = run("3h");
    assert!(
        all.contains("## 451-x T1 (landed 10:06)\n")
            && all.contains("`BACK=` reads further): none - ")
    );
    // a start undone (`make task-unstart`, 451 T359) is no start: the task's first start is the one made after it
    let undo = ev(
        &json!({"unstart": {"feature": "451-x", "task": "T1"}, "tree": "/t", "utc": "2026-11-25T09:00:00Z"}),
    );
    put(
        &d,
        "root/.git/task-starts.jsonl",
        &[
            line("451-x", "T1", "2026-11-25T08:00:00Z"),
            undo,
            line("451-x", "T1", "2026-11-25T09:30:00Z"),
        ],
    );
    let first = starts(Path::new(&root), &clones);
    let key = ("451-x".to_owned(), "T1".to_owned());
    assert_eq!(first.get(&key).copied(), ts("2026-11-25T09:30:00Z").ok());
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

#[test]
fn waiting_on_the_gm_is_out_of_every_other_percentage() {
    let cell = |min: f64, block: f64| book::Cell {
        min: min * 60.0,
        block: block * 60.0,
        fg: 0.0,
    };
    // a task's 100 blocking minutes, 20 of them waiting on the GM, in a window of 200, 40 of them his
    let cats = vec![
        ("the GM".to_owned(), cell(0.0, 20.0)),
        ("tests".to_owned(), cell(30.0, 80.0)),
    ];
    let targets = vec![(
        "make static".to_owned(),
        "tests".to_owned(),
        1,
        cell(30.0, 80.0),
    )];
    let whole = cell(60.0, 200.0);
    let mut out = String::new();
    let d = super::Sides {
        whole,
        tasks: cell(60.0, 160.0),
        landings: cell(0.0, 0.0),
    };
    tables(&mut out, &cats, &targets, &d, false);
    for want in [
        // his row: of the whole, the task's 100 and the window's 200
        "| the GM | 0.0 | 0.0% | 0.0% | 20.0 | 20.0% | 10.0% |",
        // every other row: of the working time, the task's 80 and the window's 160
        "| tests | 30.0 | 100.0% | 50.0% | 80.0 | 100.0% | 50.0% |",
        "| make static | tests | 1 | 30.0 | 100.0% | 50.0% | 80.0 | 100.0% | 50.0% |",
        "| all | 30.0 | | 50.0% | 100.0 | | 50.0% |",
        "| working (all but waiting on the GM) | 30.0 | | 50.0% | 80.0 | | 50.0% |",
    ] {
        assert!(out.contains(want), "{want}\n---\n{out}");
    }
    assert!(!is_gm("tests") && is_gm("the GM away"));
}

/// Work waited on that blocked no task is named in the header, largest first, never in the blocking (451 T243).
#[test]
fn waited_on_work_blocking_no_task_is_named_apart() {
    let mut l = Ledger::default();
    l.free.insert(book::PAGES.to_owned(), 600.0);
    l.free.insert("plan review: agents".to_owned(), 120.0);
    let text = render(
        (&l, &Ledger::default()),
        (&[], &[]),
        ((0.0, 3600.0), 0.0, &BTreeMap::new()),
        (&columns::Runs::default(), &super::cross::Cross::default()),
    );
    let want = "blocking no task (a page session or research pass whose brief names none, work whose clue is `Blocks: none`): 12.0 min \
                - research and page sessions 10.0 - plan review: agents 2.0.\n";
    assert!(text.contains(want));
}

/// Feature 451 T426: a measurement's wait on a scratch slot directory is booked to no category - not `waiting on a build slot`, not
/// the compile whose span holds it - and the footnote counts the window's, a line in the read-back left out of that count.
#[test]
fn a_scratch_slot_wait_is_left_out_and_counted_in_the_footnote() {
    let (d, root) = world();
    let (projects, clones) = (d.join("home"), d.join("clones"));
    let log = d.join("root/.git/l7r-events/451-x.jsonl");
    let wait = |t0: &str, t1: &str| {
        json!({"t": t1, "ev": "Phase", "src": "rust", "step": "slot-wait", "t0": t0, "t1": t1, "make": "static", "sid": "s",
            "scratch": true})
    };
    let mut text = std::fs::read_to_string(&log).unwrap();
    for w in [
        wait("2026-11-25T10:00:45Z", "2026-11-25T10:00:55Z"),
        wait("2026-11-25T09:59:00Z", "2026-11-25T09:59:30Z"),
    ] {
        let _ = writeln!(text, "{w}");
    }
    std::fs::write(&log, text).unwrap();
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
        "| make static | tests | 1 | 1.0 | ",
        "waits on a scratch slot directory (451 T426): 1 in the window (0.2 min), booked to no category",
        "Unbooked, named: 0 Bash calls refused before running (no run); 0 phases tied to no run",
    ] {
        assert!(out.contains(want), "{want}\n---\n{out}");
    }
    assert!(!out.contains("| waiting on a build slot |"), "{out}");
}
