//! The per-task tables over the scratch feature, by start and by tick, and the command line.

use std::collections::HashMap;
use std::fmt::Write as _;
use std::path::Path;

use serde_json::{json, Value};

use super::super::feature_report::tests::{put, tree};
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
fn categories_go_to_buckets_and_gaps_to_tasks() {
    for (cat, want) in [
        ("thinking", "model"),
        ("waiting: quote-check", "record/modal checks"),
        ("dispatching: review check", "record/modal checks"),
        ("dispatching: record check", "record/modal checks"),
        ("waiting: general-purpose", "other subagent"),
        ("dispatching: other subagent", "other subagent"),
        ("edit", "tools"),
        // feature 451 T08: the guard's table's buckets are columns of their own (D2); a past log's `quick test` is tests, `gate` gate
        ("tests", "tests"),
        ("quick test", "tests"),
        ("gate", "gate"),
        ("compile", "compile"),
    ] {
        assert_eq!(bucket(cat), want, "{cat}");
    }
    let starts = [(1.0, "T01".to_owned()), (5.0, "T02".to_owned())];
    assert_eq!(task_at(&starts, 0.5), "-");
    assert_eq!(task_at(&starts, 5.0), "T02");
    let p = named_pattern("901");
    for (text, want) in [
        ("make tick T=T05", "T05"),
        ("git commit -m '901 T07: x'", "T07"),
        ("plan-bundle-T08 and ## T08 -", "T08"),
        ("task T09, TASK=T10", ""),
        ("T=T5", ""),
    ] {
        assert_eq!(named_task(text, &p), want, "{text}");
    }
    assert_eq!(named_task("plan-x-T11", &named_pattern("")), "T11");
}

#[test]
fn the_tables_book_turns_windows_and_agents() {
    let e = evs(&[
        json!({"t": at("08:00:00"), "sid": "s", "ev": "UserPromptSubmit"}),
        json!({"t": at("08:00:10"), "sid": "s", "ev": "PreToolUse", "tool": "Bash", "id": "b1", "cat": "gate"}),
        json!({"t": at("08:00:20"), "sid": "s", "ev": "PostToolUse", "tool": "Bash", "id": "b1"}),
        json!({"t": at("08:00:20"), "sid": "s", "ev": "PreToolUse", "tool": "Bash", "id": "b2"}),
        json!({"t": at("08:00:30"), "sid": "s", "ev": "Stop"}),
        json!({"t": at("08:00:40"), "sid": "s", "ev": "UserPromptSubmit", "gm": false}),
        json!({"t": at("08:00:50"), "sid": "s", "ev": "Stop"}),
        json!({"t": at("10:00:00"), "sid": "s", "ev": "UserPromptSubmit"}),
        json!({"t": at("10:00:10"), "sid": "s", "ev": "Stop"}),
        json!({"t": at("10:00:20"), "sid": "s", "ev": "UserPromptSubmit"}),
        json!({"t": at("10:00:30"), "sid": "s", "ev": "PreToolUse", "tool": "Agent", "id": "g", "agent": "spec-fidelity"}),
        json!({"t": at("10:00:31"), "sid": "s", "ev": "SubagentStart", "aid": "f", "agent": "spec-fidelity"}),
        json!({"t": at("10:00:35"), "sid": "s", "ev": "SubagentStart", "aid": "n"}),
        json!({"t": at("10:05:00"), "sid": "s", "ev": "SubagentStop", "aid": "f"}),
        json!({"t": at("10:05:01"), "sid": "s", "ev": "PostToolUse", "tool": "Agent", "id": "g", "aid": "f"}),
        json!({"t": at("10:05:02"), "sid": "s", "ev": "SubagentStop", "aid": "never"}),
        json!({"t": at("12:00:00"), "sid": "s", "ev": "Stop"}),
        json!({"t": at("12:00:01"), "sid": "s", "ev": "SubagentStop", "aid": "n"}),
    ]);
    let starts = [(0.0, "T01".to_owned())];
    let inputs = HashMap::from([("b1".to_owned(), "\"make done T=T02\"".to_owned())]);
    // the agents are the window's flight's (feature 451 T10): every line here is the feature's own
    let booking = Booking {
        flight: columns::flight(
            &columns::Runs::default(),
            &e,
            &e,
            ts(&at("12:00:01")).unwrap(),
        )
        .unwrap(),
        ..Booking::default()
    };
    let t = tables(&e, &starts, Some(&inputs), "901", &booking).unwrap();
    let text = render(
        &t,
        &[
            "-".to_owned(),
            "T01".to_owned(),
            "T02".to_owned(),
            "T09".to_owned(),
        ],
    );
    assert!(text.contains("| T02 | "), "{text}");
    assert!(text.contains("| all | "), "{text}");
    // by start, an agent naming no task goes to the mark (T01); the stop naming no start (`never`) is no agent
    let want = "| T01 | 2 | 124 | - | - | - | - | 0 | 0 | spec-fidelity 1, ? 1 |";
    assert!(text.contains(want), "{text}");
    assert_eq!(t.rules.items().len(), 3);
    let none = tables(&e, &starts, None, "", &Booking::default()).unwrap();
    assert_eq!(none.rules.items().len(), 1);
    for bad in [
        json!([{"t": "x", "ev": "Stop"}]),
        json!([{"t": at("08:00:00"), "sid": "s"}, {"t": at("08:00:01"), "sid": "s", "ev": "Stop"}]),
        json!([{"t": at("08:00:00"), "sid": "s", "ev": "Stop"}, {"t": at("08:00:01"), "sid": "s"}]),
        json!([{"t": at("08:00:00"), "ev": "SubagentStop", "aid": "a"}, {"t": "x", "ev": "PreToolUse", "tool": "Agent"}]),
    ] {
        assert!(tables(
            &evs(bad.as_array().unwrap()),
            &starts,
            None,
            "",
            &Booking::default()
        )
        .is_err());
    }
}

#[test]
fn ticks_make_windows() {
    let log = "@@2026-11-01T08:00:00+00:00\n+- [x] T01 a\n+- [x] T02 b\n@@2026-11-01T09:00:00Z\n+- [x] T01 again\n+- [x] T03\n@@ -1 +1 @@\n";
    let ticks = parse_ticks(log).unwrap();
    assert_eq!(ticks.len(), 3);
    assert!(parse_ticks("@@2026-13-01T08:00:00\n").is_err());
    assert_eq!(parse_ticks("+- [x] T01\n").unwrap(), Vec::new());
    let wins = tick_windows(&ticks, 0.0);
    assert_eq!(
        wins.iter().map(|w| w.2.as_str()).collect::<Vec<_>>(),
        ["T01+T02", "T03"]
    );
    assert_eq!(tick_windows(&ticks, wins[1].0 + 1.0).len(), 1);
}

#[test]
fn a_transcript_names_each_calls_input() {
    let home = crate::checks::scratch("measure-where-inputs");
    let line = |v: Value| v.to_string();
    put(
        &home,
        "p/s1.jsonl",
        &[
            line(json!({"message": {"content": [{"type": "tool_use", "id": "a", "input": {"x": "caf\u{e9}", "n": 1.5}}, 5]}})),
            line(json!({"message": {"content": "a tool_use string"}, "k": "tool_use"})),
            line(json!({"message": null, "k": "tool_use"})),
            "\"tool_use\" not json".to_owned(),
            line(json!({"no": "x"})),
        ]
        .join("\n"),
    );
    let got = transcript_inputs(&["s1".to_owned(), "s2".to_owned()], &home).unwrap();
    assert_eq!(got["a"], "{\"x\": \"caf\\u00e9\", \"n\": 1.5}");
    for bad in [
        "[\"tool_use\"]",
        r#"{"message": "x", "k": "tool_use"}"#,
        r#"{"message": {"content": 5}, "k": "tool_use"}"#,
        r#"{"message": {"content": true}, "k": "tool_use"}"#,
    ] {
        put(&home, "p/s3.jsonl", bad);
        assert!(transcript_inputs(&["s3".to_owned()], &home).is_err());
    }
    put(
        &home,
        "p/s3.jsonl",
        r#"{"message": {"content": 0}, "k": "tool_use"}"#,
    );
    assert!(transcript_inputs(&["s3".to_owned()], &home)
        .unwrap()
        .is_empty());
}

fn args(list: &[&str]) -> Vec<String> {
    list.iter().map(|s| (*s).to_owned()).collect()
}

#[test]
#[expect(
    clippy::too_many_lines,
    reason = "one scratch feature through every form of the command line"
)]
fn the_command_line_books_by_start_or_by_tick() {
    let d = tree("measure-where-cli");
    let root = d.display().to_string();
    let projects = d.join("home");
    let none = Path::new("/nonexistent");
    assert_eq!(cli(&[], &projects, none).code, 2);
    assert_eq!(cli(&args(&["901", "--nope"]), &projects, none).code, 2);
    let missing = cli(&args(&["903", "--root", &root]), &projects, none);
    assert_eq!(
        (missing.code, missing.stderr.as_str()),
        (2, "where-time: no specs/903-* directory\n")
    );
    assert_eq!(cli(&args(&["x", "--root", &root]), &projects, none).code, 1);
    let log = d.join(".git/l7r-events/901-s.jsonl");
    let mut text = std::fs::read_to_string(&log).unwrap();
    let _ = write!(
        text,
        "{}\n{}\n",
        json!({"t": at("07:00:00"), "sid": "z", "ev": "SubagentStart", "aid": "zz", "agent": "k"}),
        json!({"t": at("07:00:00"), "sid": "z", "ev": "SubagentStop", "aid": "zz"})
    );
    std::fs::write(&log, text).unwrap();
    let by_start = cli(&args(&["901", "--root", &root]), &projects, none);
    assert_eq!(by_start.code, 0);
    assert!(
        by_start.stdout.contains("\nbooked by: "),
        "{}",
        by_start.stdout
    );
    let since = cli(
        &args(&["901", "--root", &root, "--since", "2026-11-01T08:10:00Z"]),
        &projects,
        none,
    );
    assert_eq!(since.code, 0);
    let by_tick = cli(
        &args(&["901", "--root", &root, "--by-tick"]),
        &projects,
        none,
    );
    assert!(
        by_tick
            .stdout
            .contains("| window | from (UTC) | to (UTC) | wall minutes |"),
        "{}",
        by_tick.stdout
    );
    assert_eq!(
        cli(
            &args(&[
                "901",
                "--root",
                &root,
                "--by-tick",
                "--since",
                "2026-11-01T08:00:00Z"
            ]),
            &projects,
            none
        )
        .code,
        0
    );
    put(
        &d,
        ".git/task-starts.jsonl",
        &format!(
            "{}\n{}\n",
            json!({"feature": "901-s", "task": 5, "utc": at("08:00:00")}),
            json!({"feature": "x"})
        ),
    );
    assert_eq!(
        cli(&args(&["901", "--root", &root]), &projects, none).code,
        0
    );
    for bad in ["{", "[1]", r#"{"feature": "901-s", "task": "T1"}"#] {
        put(&d, ".git/task-starts.jsonl", bad);
        assert_eq!(
            cli(&args(&["901", "--root", &root]), &projects, none).code,
            1
        );
    }
    put(
        &d,
        ".git/task-starts.jsonl",
        r#"{"feature": "901-s", "task": "T1", "utc": 5}"#,
    );
    assert_eq!(
        cli(
            &args(&["901", "--root", &root, "--since", "2026"]),
            &projects,
            none
        )
        .code,
        1
    );
    // outside any repository the root is taken as given, and there are no starts
    let bare = crate::checks::scratch("measure-where-bare");
    std::fs::create_dir_all(bare.join("specs/901-s")).unwrap();
    assert_eq!(
        cli(
            &args(&["901", "--root", &bare.display().to_string()]),
            &projects,
            none
        )
        .code,
        0
    );
}

/// T207: a row naming no event - `{"t", "sid": "", "ev": ""}`, which a test's empty payload (and on 11-08 the self-check) wrote into the
/// clone's real log until T207 - is no session. Read as one, its rows' gaps on 2026-11-19 (03:53-06:16 and 06:41-10:36) were the 143 and
/// 236 "idle" minutes booked to T187 and T201 while the one real session worked without a break; this is that day's shape.
#[test]
fn a_row_naming_no_event_is_no_session() {
    let d = crate::checks::scratch("measure-where-blank");
    let mut text = String::new();
    for m in (0..=240).step_by(10) {
        let t = format!("2026-11-19T{:02}:{:02}:00Z", 3 + m / 60, m % 60);
        let _ = writeln!(
            text,
            "{}",
            json!({"t": t, "sid": "s", "ev": "PreToolUse", "tool": "Bash", "id": format!("b{m}"), "cat": "other tool"})
        );
    }
    for blank in [
        json!({"t": "2026-11-19T03:53:41.707Z", "sid": "", "ev": ""}),
        json!({"t": "2026-11-19T06:16:33.648Z", "sid": "", "ev": ""}),
        json!({"t": "2026-11-19T06:20:00.000Z", "sid": "", "ev": "", "tool": "Bash", "id": "", "cat": "other tool"}),
    ] {
        let _ = writeln!(text, "{blank}");
    }
    let log = d.join("449-x.jsonl");
    std::fs::write(&log, text).unwrap();
    let events = super::super::events::load_events(&[log], &[], "2026-11-19", "").unwrap();
    let t = tables(
        &events,
        &[(0.0, "T187".to_owned())],
        None,
        "449",
        &Booking::default(),
    )
    .unwrap();
    let idle: f64 = t.time.iter().map(|(_, c)| c.get(&"idle".to_owned())).sum();
    let all: f64 = t.time.iter().map(|(_, c)| total(c)).sum();
    assert_eq!(format!("{idle} {}", all / 60.0), "0 240");
    assert!(events.iter().all(|e| s(e, "sid") == "s"));
}

/// T207: SINCE cut the task starts before it, so the stretch from SINCE to the first start after it went to `-` (88 minutes on
/// 2026-11-19, while T194, started 11-18 22:40, was the task at hand); the mark at an instant is the same with SINCE as without.
#[test]
fn since_keeps_the_task_active_when_it_opens() {
    let d = tree("measure-where-since-mark");
    let root = d.display().to_string();
    put(
        &d,
        ".git/l7r-events/901-s.jsonl",
        &format!(
            "{}\n{}\n{}\n",
            json!({"t": at("09:00:00"), "sid": "q", "ev": "UserPromptSubmit", "gm": true}),
            json!({"t": at("09:10:00"), "sid": "q", "ev": "PreToolUse", "tool": "Bash", "id": "q1", "cat": "other tool"}),
            json!({"t": at("09:20:00"), "sid": "q", "ev": "Stop"})
        ),
    );
    put(
        &d,
        ".git/task-starts.jsonl",
        &format!(
            "{}\n{}\n{}\n",
            json!({"feature": "901-s", "task": "T04", "utc": at("06:00:00")}),
            json!({"feature": "901-s", "task": "T05", "utc": at("07:00:00")}),
            json!({"feature": "901-s", "task": "T06", "utc": at("09:05:00")})
        ),
    );
    let projects = d.join("home");
    let none = Path::new("/nonexistent");
    for since in [String::new(), at("08:00:00")] {
        let mut a = args(&["901", "--root", &root]);
        if !since.is_empty() {
            a.extend(args(&["--since", &since]));
        }
        let got = cli(&a, &projects, none).stdout;
        let rows: Vec<&str> = got.lines().filter_map(|l| l.split(" | ").next()).collect();
        assert_eq!(rows[2..5], ["| T05", "| T06", "| all"], "{got}");
    }
}

/// T207: a date-only SINCE cuts the task starts by the text comparison that cuts the events. Read as a time instead it is the machine's
/// local midnight - 05:00 UTC in this `America/New_York` container - and the 2026-11-19 report lost T194's and three more tasks' starts
/// and booked 37 minutes to `-`; this case goes red that way only on a machine west of UTC.
#[test]
fn a_date_only_since_cuts_the_starts_as_it_cuts_the_events() {
    let d = tree("measure-where-since-date");
    let root = d.display().to_string();
    let t = |hms: &str| format!("2026-11-01T{hms}Z");
    put(
        &d,
        ".git/l7r-events/901-s.jsonl",
        &format!(
            "{}\n{}\n{}\n",
            json!({"t": t("00:30:00"), "sid": "q", "ev": "UserPromptSubmit", "gm": true}),
            json!({"t": t("00:40:00"), "sid": "q", "ev": "PreToolUse", "tool": "Bash", "id": "q1", "cat": "other tool"}),
            json!({"t": t("00:50:00"), "sid": "q", "ev": "Stop"})
        ),
    );
    put(
        &d,
        ".git/task-starts.jsonl",
        &format!(
            "{}\n{}\n",
            json!({"feature": "901-s", "task": "T04", "utc": "2026-10-31T22:00:00Z"}),
            json!({"feature": "901-s", "task": "T05", "utc": t("00:35:00")})
        ),
    );
    let a = args(&["901", "--root", &root, "--since", "2026-11-01"]);
    let got = cli(&a, &d.join("home"), Path::new("/nonexistent")).stdout;
    let rows: Vec<&str> = got.lines().filter_map(|l| l.split(" | ").next()).collect();
    assert_eq!(rows[2..5], ["| T04", "| T05", "| all"], "{got}");
}

/// T207's pin, not a red test: 2026-11-17's 5.5 hours were the GM away, not a stall. The turn ended at 18:48:10 with its final report
/// (no background agent pending: the transcript's `turn_duration` has no `pendingBackgroundAgentCount`); the `SubagentStop` at 18:51:12 is
/// untyped with no `SubagentStart` - the harness's own away-summary agent (23 ms from the transcript's `away_summary`) - and the next
/// prompt is the GM's at 00:24:14.
#[test]
fn the_seventeenth_was_the_gm_away() {
    let e = evs(&[
        json!({"t": "2026-11-17T18:47:41.389Z", "sid": "c", "ev": "PreToolUse", "tool": "Bash", "id": "x", "cat": "other tool"}),
        json!({"t": "2026-11-17T18:47:47.404Z", "sid": "c", "ev": "PostToolUse", "tool": "Bash", "id": "x"}),
        json!({"t": "2026-11-17T18:48:10.534Z", "sid": "c", "ev": "Stop"}),
        json!({"t": "2026-11-17T18:51:12.528Z", "sid": "c", "ev": "SubagentStop", "agent": "", "aid": "aa885370bae495493"}),
        json!({"t": "2026-11-18T00:24:14.265Z", "sid": "c", "ev": "UserPromptSubmit", "gm": true}),
    ]);
    let t = tables(&e, &[], None, "449", &Booking::default()).unwrap();
    let c = row(&t.time, "-").unwrap();
    assert_eq!(format!("{}", c.get(&"idle".to_owned())), "0");
    assert_eq!(
        format!("{:.2}", c.get(&GM_AWAY.to_owned()) / 60.0),
        "336.06"
    );
    assert!(t.spent.is_empty());
}

/// Feature 451 T04 (FR-002, plan D3, D4): the two line kinds the readers did not read - a background run's `BgEnd` and a make run's
/// `Phase` - move `make where-time`'s runs table alone, which it reads since T08, and `make feature-report` reads them through it since T11
/// (one reader: the report's lines move as where-time's do, and no other report line moves). Read as events, a `Phase` line
/// inside a Bash call splits the call's gap and books its rest to whatever the gap after a `Phase` is, a `BgEnd` splits a wait between
/// turns, and a `Phase` line with no session forms a session of its own (the T207 failure).
#[test]
fn a_background_end_and_a_phase_line_leave_the_tables_as_they_were() {
    let d = tree("measure-where-aside");
    let root = d.display().to_string();
    let e = super::super::feature_report::tests::env(&d);
    let none = Path::new("/nonexistent");
    let tables = || {
        let where_time = cli(&args(&["901", "--root", &root]), &d.join("home"), none);
        let report = super::super::feature_report::cli(&args(&["--root", &root, "901"]), &e, none);
        assert_eq!((where_time.code, report.code), (0, 0));
        // the report's own build time is the one line that differs run to run
        let report: Vec<String> = report
            .stdout
            .lines()
            .filter(|l| !l.starts_with("This report took"))
            .map(str::to_owned)
            .collect();
        (where_time.stdout, report)
    };
    let before = tables();
    let log = d.join(".git/l7r-events/901-s.jsonl");
    let mut text = std::fs::read_to_string(&log).unwrap();
    for line in [
        // inside the Bash call b1 (08:03:00 to 08:04:00)
        json!({"t": at("08:03:30"), "sid": "s", "ev": "Phase", "src": "rust", "step": "build", "crates": ["rust/guard"], "t0": at("08:03:01"), "t1": at("08:03:30"), "code": 0}),
        // in the wait between the Stop at 08:05:03 and the agent's stop at 08:15:00
        json!({"t": at("08:10:00"), "sid": "s", "ev": "BgEnd", "id": "b1", "bg": "bx1", "status": "completed", "exit": 0, "make": "map", "cat": "tests", "t0": at("08:03:00")}),
        // a gate tool's line with no session to name
        json!({"t": at("09:30:00"), "sid": "", "ev": "Phase", "src": "rust", "step": "test", "crates": ["rust/guard"], "t0": at("09:29:00"), "t1": at("09:30:00"), "code": 0}),
    ] {
        let _ = writeln!(text, "{line}");
    }
    std::fs::write(&log, text).unwrap();
    let after = tables();
    let changed: Vec<(&str, &str)> = before
        .0
        .lines()
        .zip(after.0.lines())
        .filter(|(b, a)| b != a)
        .collect();
    let report: Vec<(&str, &str)> = before
        .1
        .iter()
        .zip(&after.1)
        .filter(|(b, a)| b != a)
        .map(|(b, a)| (b.as_str(), a.as_str()))
        .collect();
    assert_eq!(report, changed);
    // T08 reads the build phase inside b1: 29 of its 60 s are compile (the runs table; the wall-clock table's minutes round alike)
    let row = |x: &str| {
        format!(
            "| {x} | 1 | 1.0 | 0.5 | 0.5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |"
        )
    };
    let was = |x: &str| {
        format!(
            "| {x} | 1 | 1.0 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |"
        )
    };
    // the session-less `test` phase is booked to a category since T153, so, held by no run, it is counted loose
    let foot = |n: &str| {
        format!("runs: 1 Bash calls of every session and agent (0 in the background, 0 open at the window's end), booked by their `make` target through the guard's table (feature 451 T08); machine minutes, which overlap, never the wall clock; 0 refused before running; phases tied to no run: {n} min)")
    };
    assert_eq!(
        changed,
        [
            (was("T01").as_str(), row("T01").as_str()),
            (was("all").as_str(), row("all").as_str()),
            (foot("0 (0.0").as_str(), foot("1 (1.0").as_str())
        ]
    );
}

/// Feature 451 T08 (FR-005, plan D2, D4, D7; the spec's User Story 1 scenarios 1 and 3): one window's log through the command line. The
/// main session's `make static` (its frozen `cat` "other tool", a past log's) is re-booked tests by its `make`, its 240 s of compile
/// phases split out of its 360 s; a builder's call inside it no longer cuts it, and the builder's calls after the `Stop` keep the wait
/// on work open to the last of them. THE RUNS TABLE books every Bash call of the session and
/// its builder by its line's task: a background `rust-test` ends at its enqueue row (08:09:00), not its `BgEnd` (08:15:00); a background
/// `land` with no enqueue row at its `BgEnd`; a builder's `hamlet` at the `TaskStop` that stopped it; one with none open to `UNTIL=`; a goal-less make is the Makefile's default goal (`done`,
/// gate); a past log's `quick test` is tests; a call running at `UNTIL=` is clipped there; a refused call and a phase of no run counted.
#[test]
#[expect(
    clippy::too_many_lines,
    reason = "one window's log, its lines in time order, and its tables"
)]
fn the_columns_book_make_runs_compile_and_until() {
    let d = crate::checks::scratch("measure-where-columns");
    let ok = std::process::Command::new("git")
        .args(["init", "-q"])
        .current_dir(&d)
        .status()
        .unwrap();
    assert!(ok.success());
    put(&d, "specs/901-s/tasks.md", "- [ ] T05\n- [ ] T06\n");
    put(
        &d,
        "Makefile",
        "# the operations\nX := 1\n.PHONY: done\ndone:   ## the gate\n\t@true\nquick:\n",
    );
    put(
        &d,
        ".git/task-starts.jsonl",
        &format!(
            "{}\n",
            json!({"feature": "901-s", "task": "T05", "utc": at("07:59:00")})
        ),
    );
    let pre = |t: &str, id: &str, extra: Value| {
        let mut v = json!({"t": at(t), "sid": "s", "ev": "PreToolUse", "tool": "Bash", "id": id});
        v.as_object_mut()
            .unwrap()
            .extend(extra.as_object().unwrap().clone());
        v
    };
    let post = |t: &str, id: &str, bg: &str| {
        let mut v = json!({"t": at(t), "sid": "s", "ev": "PostToolUse", "tool": "Bash", "id": id});
        if !bg.is_empty() {
            v["bg"] = json!(bg);
        }
        v
    };
    let postb = |t: &str, id: &str, bg: &str| {
        let mut v = post(t, id, bg);
        v["by"] = json!("a1");
        v
    };
    let phase = |step: &str, make: &str, task: &str, t0: &str, t1: &str| json!({"t": at(t1), "sid": "s", "ev": "Phase", "src": "rust", "step": step, "crates": ["rust/guard"], "t0": at(t0), "t1": at(t1), "code": 0, "make": make, "task": task});
    let b = |task: &str| json!({"by": "a1", "task": task});
    let mk = |make: &str, cat: &str| json!({"make": make, "cat": cat, "by": "a1", "task": "T06"});
    let lines = [
        json!({"t": at("07:59:10"), "sid": "s", "ev": "UserPromptSubmit"}),
        pre(
            "08:00:10",
            "toolu_m1",
            json!({"make": "static", "cat": "other tool"}),
        ),
        phase("build", "static", "", "08:00:11", "08:02:11"),
        phase("cover-build", "static", "", "08:01:11", "08:04:11"),
        phase("test", "static", "", "08:04:11", "08:06:00"),
        pre("08:03:00", "toolu_x0", mk("claims-owed", "review")),
        postb("08:03:20", "toolu_x0", ""),
        post("08:06:10", "toolu_m1", ""),
        pre(
            "08:06:10",
            "toolu_m2",
            json!({"make": "rust-test", "cat": "tests"}),
        ),
        post("08:06:11", "toolu_m2", "b2"),
        pre(
            "08:06:20",
            "toolu_m3",
            json!({"make": "land", "cat": "land"}),
        ),
        post("08:06:21", "toolu_m3", "b3"),
        json!({"t": at("08:06:40"), "sid": "s", "ev": "Stop"}),
        pre("08:07:00", "toolu_x1", mk("hooks-test", "tests")),
        postb("08:08:00", "toolu_x1", ""),
        pre(
            "08:08:00",
            "toolu_x2",
            json!({"cat": "quick test", "by": "a1", "task": "T06"}),
        ),
        postb("08:08:30", "toolu_x2", ""),
        pre("08:09:00", "toolu_x3", mk(".DEFAULT_GOAL", "other tool")),
        postb("08:09:10", "toolu_x3", ""),
        pre("08:09:30", "toolu_x4", mk("static", "tests")),
        postb("08:09:31", "toolu_x4", "b4"),
        phase("build", "static", "T06", "08:10:00", "08:11:00"),
        pre("08:10:00", "toolu_x5", b("T06")),
        json!({"t": at("08:12:00"), "sid": "s", "ev": "BgEnd", "id": "toolu_m3", "bg": "b3", "status": "completed", "exit": 0, "make": "land", "t0": at("08:06:20")}),
        pre("08:11:00", "toolu_x7", mk("hamlet", "tests")),
        postb("08:11:01", "toolu_x7", "b7"),
        phase("cover-build", "map", "", "08:12:00", "08:13:00"),
        json!({"t": at("08:14:00"), "sid": "s", "ev": "PreToolUse", "tool": "TaskStop", "id": "toolu_k1", "by": "a1"}),
        json!({"t": at("08:15:00"), "sid": "s", "ev": "BgEnd", "id": "toolu_m2", "bg": "b2", "status": "completed", "exit": 0, "make": "rust-test", "t0": at("08:06:10")}),
        pre("08:19:00", "toolu_x6", mk("quick", "tests")),
        postb("08:25:00", "toolu_x6", ""),
        json!({"t": at("08:30:00"), "sid": "s", "ev": "UserPromptSubmit", "gm": false}),
    ];
    let log: String = lines.iter().map(|l| l.to_string() + "\n").collect();
    put(&d, ".git/l7r-events/901-s.jsonl", &log);
    let queued = json!({"type": "queue-operation", "operation": "enqueue", "timestamp": at("08:09:00"), "content": "<task-notification>\n<task-id>b2</task-id>\n<tool-use-id>toolu_m2</tool-use-id>\n<status>completed</status>\n</task-notification>"});
    put(&d, "home/-proj/s.jsonl", &format!("{queued}\n"));
    let stop = json!({"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "toolu_k1", "name": "TaskStop", "input": {"task_id": "b7"}}]}});
    put(
        &d,
        "home/-proj/s/subagents/agent-a1.jsonl",
        &format!("{stop}\n"),
    );
    let root = d.display().to_string();
    let r = cli(
        &args(&["901", "--root", &root, "--until", "2026-11-01T08:20:00Z"]),
        &d.join("home"),
        Path::new("/nonexistent"),
    );
    assert_eq!(r.code, 0, "{}", r.stderr);
    let out = &r.stdout;
    for want in [
        "| task | total | model | tests | compile | hook suites | map generation | gate | land | review | docs | spec-kit step | tools | background run |",
        // the wait from the 08:06:40 `Stop` (no `inflight`: before the field) booked to the session's own runs in flight (T09): the
        // landing to its `BgEnd` at 08:12, outranking the `rust-test` beside it, the rest to the last line (08:19) held by none
        "| T05 | 20 | 1 | 2 | 4 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 7 | 0 | 0 | 0 |",
        "a background shell 5 min, an agent 0 min, a monitor alone 0 min, none 7 min (feature 451 T09)",
        "| task | runs | minutes | tests | compile | hook suites | map generation | gate | land | review | docs | spec-kit step | other | in the background |",
        "| T05 | 3 | 14.5 | 4.8 | 4.0 | 0.0 | 0.0 | 0.0 | 5.7 | 0.0 | 0.0 | 0.0 | 0.0 | 8.5 |",
        "| T06 | 7 | 16.5 | 15.0 | 1.0 | 0.0 | 0.0 | 0.2 | 0.0 | 0.3 | 0.0 | 0.0 | 0.0 | 13.5 |",
        "| all | 10 | 31.0 | 19.8 | 5.0 | 0.0 | 0.0 | 0.2 | 5.7 | 0.3 | 0.0 | 0.0 | 0.0 | 22.0 |",
        "runs: 10 Bash calls of every session and agent (4 in the background, 1 open at the window's end)",
        "; 1 refused before running; phases tied to no run: 1 (1.0 min)",
    ] {
        assert!(out.contains(want), "{want}\n{out}");
    }
}

/// T08's final check, on the critical path: a foreground landing launched behind `make claims-owed` is booked land by its `makes`, and the
/// gap it holds splits into compile, the landing's gate (less that compile) and land, summing to the gap.
#[test]
fn a_landing_call_books_land_and_splits_its_gate() {
    let tool = json!({"tool": "Bash", "id": "toolu_l", "cat": "review", "makes": ["claims-owed", "land"], "make": "claims-owed"});
    let line = |t: &str, ev: &str| {
        let mut v = json!({"t": at(t), "sid": "s", "ev": ev});
        v.as_object_mut()
            .unwrap()
            .extend(tool.as_object().unwrap().clone());
        v
    };
    let lines = evs(&[
        json!({"t": at("08:00:00"), "sid": "s", "ev": "UserPromptSubmit"}),
        line("08:00:00", "PreToolUse"),
        line("08:10:00", "PostToolUse"),
        json!({"t": at("08:10:30"), "sid": "s", "ev": "Stop"}),
    ]);
    let aside = evs(&[
        json!({"ev": "Phase", "src": "land", "sid": "s", "step": "gate", "make": "land", "task": "T07", "t0": at("08:01:00"), "t1": at("08:06:00")}),
        json!({"ev": "Phase", "src": "rust", "sid": "s", "step": "build", "make": "land", "task": "T07", "t0": at("08:01:00"), "t1": at("08:02:00")}),
    ]);
    let (none, no_stops) = (HashMap::new(), HashMap::new());
    let window = columns::Window {
        stopped: &no_stops,
        queued: &HashMap::new(),
        end: ts(&at("09:00:00")).unwrap(),
        enqueued: &none,
        goal: "",
    };
    let ran = columns::runs(&lines, &aside, &[], &window).unwrap();
    let booking = Booking {
        splits: columns::splits_by_id(&ran),
        goal: String::new(),
        ..Booking::default()
    };
    let tabs = tables(&lines, &[], None, "451", &booking).unwrap();
    let c = row(&tabs.time, "-").unwrap();
    let got: Vec<f64> = ["land", "gate", "compile", "review"]
        .iter()
        .map(|k| c.get(&(*k).to_owned()))
        .collect();
    assert_eq!(got, [300.0, 240.0, 60.0, 0.0]);
}

/// T08's model check: a background builder's `SubagentStop` while the main session's own `make static` runs left the rest of the call
/// booked model (1.7 min of the window's, 13:38:59Z, measured 2026-11-21); the session was still in its call.
#[test]
fn a_builders_stop_inside_a_call_keeps_the_call() {
    let e = evs(&[
        json!({"t": at("08:00:00"), "sid": "s", "ev": "UserPromptSubmit"}),
        json!({"t": at("08:00:00"), "sid": "s", "ev": "PreToolUse", "tool": "Bash", "id": "x", "make": "static"}),
        json!({"t": at("08:01:00"), "sid": "s", "ev": "SubagentStop", "aid": "a1", "agent": "general-purpose"}),
        json!({"t": at("08:02:00"), "sid": "s", "ev": "SubagentStart", "aid": "a2", "agent": "general-purpose"}),
        json!({"t": at("08:05:00"), "sid": "s", "ev": "PostToolUse", "tool": "Bash", "id": "x", "make": "static"}),
        json!({"t": at("08:05:30"), "sid": "s", "ev": "Stop"}),
    ]);
    let t = tables(&e, &[], None, "451", &Booking::default()).unwrap();
    let c = row(&t.time, "-").unwrap();
    let got: Vec<f64> = ["tests", "model"]
        .iter()
        .map(|k| c.get(&(*k).to_owned()))
        .collect();
    assert_eq!(got, [300.0, 30.0]);
    // a background agent's launch: its `PostToolUse` and `SubagentStart` share a millisecond (07:59:11.500Z, 451 T26's builder), and
    // the session then thinks; the zero gap skipped before the session's state moved on, so 29.5 min went to `other subagent`
    let e = evs(&[
        json!({"t": at("08:00:00"), "sid": "s", "ev": "UserPromptSubmit"}),
        json!({"t": at("08:00:00"), "sid": "s", "ev": "PreToolUse", "tool": "Agent", "id": "g", "cat": "other subagent"}),
        json!({"t": at("08:00:01"), "sid": "s", "ev": "PostToolUse", "tool": "Agent", "id": "g", "cat": "other subagent"}),
        json!({"t": at("08:00:01"), "sid": "s", "ev": "SubagentStart", "aid": "a3", "agent": "general-purpose"}),
        json!({"t": at("08:10:01"), "sid": "s", "ev": "Stop"}),
    ]);
    let t = tables(&e, &[], None, "451", &Booking::default()).unwrap();
    let c = row(&t.time, "-").unwrap();
    let got: Vec<f64> = ["model", "other subagent"]
        .iter()
        .map(|k| c.get(&(*k).to_owned()))
        .collect();
    assert_eq!(got, [600.0, 1.0]);
}
