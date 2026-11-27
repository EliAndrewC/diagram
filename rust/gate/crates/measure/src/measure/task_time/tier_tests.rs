//! A two-tier afternoon (feature 451 T298), through the command: one session, its mark on T1 throughout. A builder for T1 runs the
//! first tier in a pool tree; the session carries it (the carry's line under another task's stale mark), runs `make quick`, lands the
//! batch T1 T2 - a red gate in the background it waits on alone, a repair, a green re-run in the foreground - then works on under
//! the mark it never moved, and starts a second landing that is still in flight at the window's end. A memory sampler, a wait loop
//! it launched in the background, runs from 00:12 to the end.

use std::fmt::Write as _;
use std::path::Path;

use serde_json::{json, Value};

use super::super::events::ts;
use super::cli;

fn at(ms: &str) -> String {
    format!("2026-11-26T10:{ms}Z")
}

/// A line of the session `s`: its task T1 by the mark alone unless `extra` names one.
fn line(t: &str, ev: &str, extra: &Value) -> Value {
    let mut v = json!({"t": at(t), "sid": "s", "ev": ev, "task": "T1", "fallback": true});
    for (k, x) in extra.as_object().unwrap() {
        v[k] = x.clone();
    }
    if extra.get("named").is_some() {
        v.as_object_mut().unwrap().remove("fallback");
        v.as_object_mut().unwrap().remove("named");
    }
    v
}

/// A Bash call's two lines.
fn bash(t0: &str, t1: &str, id: &str, extra: &Value) -> [Value; 2] {
    let mut e = extra.clone();
    e["tool"] = json!("Bash");
    e["id"] = json!(id);
    let pre = line(t0, "PreToolUse", &e);
    let mut post = line(t1, "PostToolUse", &e);
    if let Some(bg) = extra.get("bg_id") {
        post["bg"] = bg.clone();
    }
    [pre, post]
}

fn phase(src: &str, step: &str, t0: &str, t1: &str, extra: &Value) -> Value {
    let mut v = json!({"t": at(t1), "ev": "Phase", "src": src, "step": step, "t0": at(t0), "t1": at(t1), "sid": "s"});
    for (k, x) in extra.as_object().unwrap() {
        v[k] = x.clone();
    }
    v
}

fn lines() -> Vec<Value> {
    let none = json!({});
    let mut all = vec![line("00:00", "UserPromptSubmit", &none)];
    all.extend(bash(
        "00:05",
        "00:06",
        "bt",
        &json!({"make": "builder-tree", "named": 1}),
    ));
    all.extend([
        line("00:10", "PreToolUse", &json!({"tool": "Agent", "id": "a1"})),
        line(
            "00:11",
            "PostToolUse",
            &json!({"tool": "Agent", "id": "a1", "aid": "B1"}),
        ),
        line(
            "00:11",
            "SubagentStart",
            &json!({"aid": "B1", "agent": "general-purpose", "named": 1}),
        ),
    ]);
    // the memory sampler: a wait loop in the background, under the mark alone
    all.extend(bash("00:12", "00:13", "w1", &json!({"bg_id": "xs"})));
    all.push(line(
        "00:15",
        "Stop",
        &json!({"inflight": [{"id": "B1", "type": "subagent"}, {"id": "xs", "type": "shell"}]}),
    ));
    // the builder's first tier: a 5 s wait on a build slot, a 20 s build, 20 s of tests, 15 s of lint and format
    all.extend(bash(
        "00:20",
        "01:20",
        "c1",
        &json!({"make": "builder-checks", "by": "B1", "named": 1}),
    ));
    all.extend([
        phase(
            "rust",
            "slot-wait",
            "00:20",
            "00:25",
            &json!({"make": "builder-checks"}),
        ),
        phase(
            "rust",
            "build",
            "00:25",
            "00:45",
            &json!({"make": "builder-checks"}),
        ),
        phase(
            "rust",
            "test",
            "00:45",
            "01:05",
            &json!({"make": "builder-checks"}),
        ),
        line(
            "01:30",
            "SubagentStop",
            &json!({"aid": "B1", "agent": "general-purpose", "named": 1}),
        ),
        line("01:35", "UserPromptSubmit", &json!({"gm": false})),
    ]);
    // the carry, its line under another task's mark
    all.extend(bash(
        "01:40",
        "01:50",
        "cy",
        &json!({"make": "carry", "task": "T9"}),
    ));
    all.extend(bash("02:00", "02:30", "q1", &json!({"make": "quick"})));
    all.extend(landings());
    all
}

/// The afternoon from the first landing on.
fn landings() -> Vec<Value> {
    let mut all = Vec::new();
    // the first landing, in the background behind a format: its gate red
    all.extend(bash(
        "02:40",
        "02:41",
        "l1",
        &json!({"makes": ["format", "land"], "make": "format", "bg_id": "xl1", "named": 1}),
    ));
    all.extend([
        line(
            "02:42",
            "Stop",
            &json!({"inflight": [{"id": "xl1", "type": "shell"}]}),
        ),
        phase("land", "gate", "02:50", "03:20", &json!({"code": 1})),
        phase(
            "land",
            "end",
            "02:45",
            "03:25",
            &json!({"tasks": ["T1", "T2"], "landed": false}),
        ),
        json!({"t": at("03:26"), "sid": "s", "ev": "BgEnd", "id": "l1"}),
        line("03:30", "UserPromptSubmit", &json!({"gm": false})),
        // the repair
        line("03:35", "PreToolUse", &json!({"tool": "Edit", "id": "e1"})),
        line("03:36", "PostToolUse", &json!({"tool": "Edit", "id": "e1"})),
    ]);
    // the re-run, in the foreground: green
    all.extend(bash(
        "03:40",
        "04:40",
        "l2",
        &json!({"makes": ["task-start", "land"], "make": "task-start", "named": 1}),
    ));
    all.extend([
        phase("land", "gate", "03:50", "04:20", &json!({"code": 0})),
        phase(
            "land",
            "end",
            "03:45",
            "04:35",
            &json!({"tasks": ["T1", "T2"], "landed": true}),
        ),
    ]);
    // after the landing, the mark never moved: the session's own check and its own reading
    all.extend(bash("04:50", "05:00", "q2", &json!({"make": "quick"})));
    all.extend([
        line("05:05", "PreToolUse", &json!({"tool": "Read", "id": "r1"})),
        line("05:06", "PostToolUse", &json!({"tool": "Read", "id": "r1"})),
    ]);
    // the session's own background command that is no wait, under the mark alone: no task's
    all.extend(bash(
        "05:07",
        "05:08",
        "d1",
        &json!({"make": "docs", "bg_id": "xd"}),
    ));
    all.push(json!({"t": at("05:09"), "sid": "s", "ev": "BgEnd", "id": "d1"}));
    // a landing whose command names no task and wrote no end line: its line's task is all there is
    all.extend(bash(
        "05:02",
        "05:03",
        "l4",
        &json!({"make": "land", "task": "T6", "named": 1}),
    ));
    // a second landing, in flight at the window's end: no end line
    all.extend(bash(
        "05:10",
        "05:11",
        "l3",
        &json!({"make": "land", "bg_id": "xl3", "task": "T3", "named": 1}),
    ));
    // a builder for T5 beside it: the session waits on both, and the gate in flight blocks nothing
    all.extend([
        line("05:12", "PreToolUse", &json!({"tool": "Agent", "id": "a2"})),
        line(
            "05:13",
            "PostToolUse",
            &json!({"tool": "Agent", "id": "a2", "aid": "B2"}),
        ),
        line(
            "05:13",
            "SubagentStart",
            &json!({"aid": "B2", "agent": "general-purpose", "task": "T5", "named": 1}),
        ),
        line(
            "05:20",
            "Stop",
            &json!({"inflight": [{"id": "xl3", "type": "shell"}, {"id": "B2", "type": "subagent"}]}),
        ),
    ]);
    all
}

fn world(name: &str) -> (l7r_shared::tempdir::TempDir, String) {
    world_with(name, &[])
}

/// The world, with `more` lines beside the fixture's.
fn world_with(name: &str, more: &[Value]) -> (l7r_shared::tempdir::TempDir, String) {
    let d = crate::checks::scratch(name);
    let git = d.join("root/.git");
    std::fs::create_dir_all(git.join("l7r-events")).unwrap();
    let text = lines().iter().chain(more).fold(String::new(), |mut t, v| {
        let _ = writeln!(t, "{v}");
        t
    });
    std::fs::write(git.join("l7r-events/451-x.jsonl"), text).unwrap();
    // the pool's log: the tree was T1's when the carry began; a later holder, a release and a line that is no record change nothing
    std::fs::write(
        git.join("builder-pool.log"),
        format!(
            "{}\n{}\nnot a record\n{}\n",
            json!({"utc": "2026-11-26T10:00:05Z", "event": "take", "tree": "/x/pool-t1/", "detail": "451 T1"}),
            json!({"utc": "2026-11-26T10:01:55Z", "event": "release", "tree": "/x/pool-t1", "detail": "451 T1"}),
            json!({"utc": "2026-11-26T10:01:56Z", "event": "take", "tree": "/x/pool-t1", "detail": "451 T8"}),
        ),
    )
    .unwrap();
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
            tu(
                "w1",
                "while true; do sleep 30; free -m >> /tmp/mem.log; done",
            ),
            tu("w9", "for k in $(seq 12); do sleep 60; done"),
            tu("cy", "make carry FROM=/x/pool-t1"),
            tu("l4", "make land F=451"),
            tu(
                "l3",
                "make task-start T=T3 && make land F=451 T=\"T3 T4\" NOTE=x",
            ),
        ]
        .concat(),
    )
    .unwrap();
    let root = d.join("root").display().to_string();
    (d, root)
}

fn report(d: &Path, root: &str, since: &str) -> crate::Reply {
    let list = ["--root", root, "--since", since, "--until", &at("05:30")];
    let args: Vec<String> = list.iter().map(|s| (*s).to_owned()).collect();
    cli(
        &args,
        &d.join("home"),
        &d.join("clones"),
        ts(&at("06:00")).unwrap(),
    )
}

fn has(out: &str, wants: &[&str]) {
    for want in wants {
        assert!(out.contains(want), "{want}\n---\n{out}");
    }
}

/// JOB 1: the report opens with the window's one table and a line a landed task, before any task's own tables.
#[test]
fn the_report_opens_with_the_window_s_table_and_a_line_a_landed_task() {
    let (d, root) = world("task-time-top");
    let r = report(&d, &root, &at("00:00"));
    assert_eq!(r.code, 0, "{}", r.stderr);
    let out = r.stdout;
    has(
        &out,
        &[
            "## The window: the tasks' side\n\n| category | minutes | % of the tasks' | blocking | % of the tasks' |",
            "## The window: the landings' side (the second tier)\n\n",
            "| landing | ",
            "| the tasks' side, working (all but waiting on the GM) | ",
            "## The landed tasks, one line each\n\n| task | landed | builders | builder minutes | minutes | blocking | its own table ends at |",
            // the builder's 79 s from its start and stop lines; the task's own time ends at its carry
            "| 451-x T1 | 10:04 | 1 | 1.3 | ",
            "| its carry, 10:01 |",
            "| 451-x T2 | 10:04 | 0 | 0.0 | 0.0 | 0.0 | its landing's start, 10:02 (no carry found) |",
        ],
    );
    let place = |what: &str| out.find(what).unwrap();
    assert!(
        place("## The window: the tasks' side") < place("## The landed tasks, one line each")
            && place("## The landed tasks, one line each") < place("## The second tier")
            && place("## The second tier") < place("## 451-x T1 (landed")
    );
    // the GM's wait stays apart, outside every other percentage's denominator
    has(&out, &["Waiting on the GM: 0.0 min blocking"]);
}

/// JOB 2: a batch landing is booked to no task - one line a batch, its blocking on its own line, each task's table ending at its
/// carry.
#[test]
fn a_batch_landing_is_booked_to_the_second_tier_and_to_no_task() {
    let (d, root) = world("task-time-tier");
    let out = report(&d, &root, &at("00:00")).stdout;
    has(
        &out,
        &[
            "## The second tier: each batch landing, booked to no task",
            // two gate runs of 30 s, the first red after 40 s and re-run 20 s later
            "| 451-x T1 T2 | 10:04 | 2 | 1 | 1.0 | red at 10:03 after 0.7 min, re-run 0.3 min later | ",
            // the landing still in flight, its tasks read from its command
            "| 451-x T3 T4 | not landed | 1 | 0 | 0.0 | started 10:05, 0.3 min, no end line (in flight, or stopped) | 0.3 | 0.0 |",
            "| 451-x T6 | not landed | 1 | 0 | 0.0 | started 10:05, 0.0 min, no end line (in flight, or stopped) | ",
            "The second tier's blocking: ",
            "Its time by what it was, every batch together:",
            // both landings' runs are landings, whatever their command lines ran first
            "| make land | landing | 4 | ",
            "| make quick | tests | 1 | 0.5 | ",
        ],
    );
    // T1's own tables hold no landing, no gate and no `make quick`: they end at its carry
    let own =
        &out[out.find("## 451-x T1 (landed").unwrap()..out.find("## 451-x T2 (landed").unwrap()];
    assert!(!own.contains("make land") && !own.contains("| gate |") && !own.contains("make quick"));
    has(own, &["| make carry | carry into the clone | 1 | 0.2 | "]);
    // the carry is T1's, never the stale mark's task
    assert!(!out.contains("T9"), "{out}");
}

/// A gate the session waits on beside another task's leftover background wait loop is the gate's blocking, never a wait loop's: on
/// 2026-11-26 the T304 builder's measuring loop (17:49 to past 19:08, its brief `Blocks: none`) stood in the session's `inflight`
/// through the T309 T289 batch's two gate runs, ended after both, and so took the batch's 12.1 min of waiting as `wait loops`.
#[test]
fn a_gate_waited_on_beside_a_builder_s_wait_loop_is_the_gate_s_blocking() {
    // a builder of another task's background loop, started before the first landing and ended after it
    let mut more = bash(
        "02:30",
        "02:31",
        "w9",
        &json!({"by": "B9", "bg_id": "xw9", "task": "T8", "named": 1}),
    )
    .to_vec();
    more.push(json!({"t": at("03:28"), "sid": "s", "ev": "BgEnd", "id": "w9"}));
    // the session lists the pool's trees: the pool's own command, like a tree handed out
    more.extend(bash(
        "00:07",
        "00:08",
        "bts",
        &json!({"make": "builder-trees", "named": 1}),
    ));
    let (d, root) = world_with("task-time-tier-loop", &more);
    let mut text = std::fs::read_to_string(d.join("root/.git/l7r-events/451-x.jsonl")).unwrap();
    // the session's stop during the first gate lists the loop before the landing, as the real log did
    let listed = r#""inflight":[{"id":"xl1","type":"shell"}]"#;
    assert!(text.contains(listed), "{text}");
    text = text.replace(
        listed,
        r#""inflight":[{"id":"xw9","type":"shell"},{"id":"xl1","type":"shell"}]"#,
    );
    std::fs::write(d.join("root/.git/l7r-events/451-x.jsonl"), text).unwrap();
    let out = report(&d, &root, &at("00:00")).stdout;
    let tier =
        &out[out.find("## The second tier").unwrap()..out.find("## The biggest blocking").unwrap()];
    // blocking is the fifth column of a category's row: the loop's is the 2 s it outlasted the landing's run by, never the 44 s wait
    let loops = tier
        .lines()
        .find(|l| l.starts_with("| wait loops (held open, no work) |"))
        .map_or(0.0, |l| {
            l.split('|').nth(5).unwrap().trim().parse::<f64>().unwrap()
        });
    assert!(loops < 0.1, "{tier}");
    has(tier, &["| 451-x T1 T2 | 10:04 | 2 | 1 | 1.0 | "]);
    has(
        &out,
        &["| make builder-trees | builder pool (a tree handed out, freed or listed) | 1 | 0.0 | "],
    );
}

/// JOB 3: the booking faults - the session's detached command and its own check are no task's, and the pool's and the first tier's
/// targets are named.
#[test]
fn the_session_s_own_runs_are_no_task_s_and_the_pool_s_targets_are_named() {
    let (d, root) = world("task-time-faults");
    let out = report(&d, &root, &at("00:00")).stdout;
    let own =
        &out[out.find("## 451-x T1 (landed").unwrap()..out.find("## 451-x T2 (landed").unwrap()];
    // the sampler's 5 min 18 s are not T1's, and block nothing
    assert!(!own.contains("wait loop"), "{own}");
    has(
        own,
        &[
            "| make builder-tree | builder pool (a tree handed out, freed or listed) | 1 | 0.0 | ",
            // the first tier's run is its 60 s once: 5 s on the slot, 20 s compiling, 35 s tests
            "| make builder-checks | tests | 1 | 1.0 | ",
            "| waiting on a build slot | 0.1 | ",
            "| compile | 0.3 | ",
            "| tests | 0.6 | ",
        ],
    );
    assert!(!out.contains("does not book"), "{out}");
    let rest = &out
        [out.find("## The rest of the window").unwrap()..out.find("## The whole window").unwrap()];
    has(
        rest,
        &[
            "| a wait loop (until/while/sleep) | wait loops (held open, no work) | 1 | 5.3 | ",
            // the session's `make quick` after the landing is its own
            "| make quick | tests | 1 | 0.2 | ",
            "| main session: reading code | ",
            // its `make docs` in the background too
            "| make docs | record builds and docs | 1 | 0.0 | ",
        ],
    );
    has(&out, &["- wait loops (held open, no work) "]);
}

/// JOB 4: `SINCE=last` runs from the last report's end and moves the marker; a plain `SINCE=` does not.
#[test]
fn since_last_reads_the_last_report_s_end_and_writes_this_one_s() {
    let (d, root) = world("task-time-asked");
    let marker = d.join("root/.git/l7r-events/task-time-asked.log");
    // a plain window writes nothing
    assert_eq!(report(&d, &root, &at("00:00")).code, 0);
    assert!(!marker.exists());
    // the first ask: no earlier report, so the last 24 hours, said
    let first = report(&d, &root, "last");
    assert_eq!(first.code, 0, "{}", first.stderr);
    has(
        &first.stdout,
        &[
            "SINCE=last: no earlier report is recorded, so the last 24 hours, to 2026-11-26T10:05:30Z; the next `make task-time SINCE=last` starts there (the marker: ",
            "# The task time breakdown, 2026-11-25T10:06:00Z to 2026-11-26T10:05:30Z UTC",
        ],
    );
    // a restore appended an older line after it: the greatest end is read, never the last line
    let mut text = std::fs::read_to_string(&marker).unwrap();
    assert_eq!(text.lines().count(), 1);
    let _ = writeln!(
        text,
        "{}",
        json!({"until": "2026-11-26T10:02:00Z", "asked": "x"})
    );
    std::fs::write(&marker, text).unwrap();
    let second = report(&d, &root, "last");
    has(
        &second.stdout,
        &[
            "SINCE=last: from the end of the last report, 2026-11-26T10:05:30Z, to 2026-11-26T10:05:30Z;",
            "# The task time breakdown, 2026-11-26T10:05:30Z to 2026-11-26T10:05:30Z UTC (0 tasks landed)",
        ],
    );
    assert_eq!(std::fs::read_to_string(&marker).unwrap().lines().count(), 3);
    // a plain window after it moves nothing
    assert_eq!(report(&d, &root, &at("03:00")).code, 0);
    assert_eq!(std::fs::read_to_string(&marker).unwrap().lines().count(), 3);
    // a marker that cannot be written: the report is still given, and the error says what to do
    std::fs::remove_file(&marker).unwrap();
    std::fs::create_dir_all(&marker).unwrap();
    let held = report(&d, &root, "last");
    assert_eq!(held.code, 1);
    assert!(
        held.stdout.starts_with("# The task time breakdown, "),
        "{}",
        held.stdout
    );
    let tip = "so the next SINCE=last starts where this one did - make its directory writable, or ask again with SINCE=2026-11-26T10:05:30Z\n";
    assert!(
        held.stderr.starts_with("task-time: the marker ") && held.stderr.ends_with(tip),
        "{}",
        held.stderr
    );
}

/// A carry is its holder's at the run's START (451 T346): a landing's release and the next handout retake the tree in the carry's
/// last second (2026-11-26: the carry from diagram-backlog-t271 that ended 19:40:54Z, T301's, read as T308's), and a tree nobody
/// held before the run began is no task's carry.
#[test]
fn a_carry_is_the_task_s_that_held_the_tree_when_it_began() {
    use super::super::where_time::columns::{Run, Runs, Split};
    let d = crate::checks::scratch("task-time-carry-holder");
    let git = d.join("root/.git");
    std::fs::create_dir_all(&git).unwrap();
    std::fs::write(
        git.join("builder-pool.log"),
        format!(
            "{}\n{}\n{}\n{}\n",
            json!({"utc": at("00:05"), "event": "take", "tree": "/x/pool-t1", "detail": "451 T1"}),
            json!({"utc": at("01:50"), "event": "release", "tree": "/x/pool-t1", "detail": "451 T1"}),
            json!({"utc": at("01:50"), "event": "take", "tree": "/x/pool-t1", "detail": "451 T8"}),
            json!({"utc": at("01:45"), "event": "take", "tree": "/x/pool-t2", "detail": "451 T5"}),
        ),
    )
    .unwrap();
    let takes = super::tiers::takes(&[d.join("root")]);
    let run = |id: &str| Run {
        id: id.to_owned(),
        t0: ts(&at("01:40")).unwrap(),
        t1: ts(&at("01:50")).unwrap(),
        sid: "s".to_owned(),
        by: String::new(),
        bg_id: String::new(),
        makes: vec!["carry".to_owned()],
        bucket: "other",
        task: "T9".to_owned(),
        bg: false,
        open: false,
        split: Split::default(),
    };
    let runs = Runs {
        runs: vec![run("cy"), run("c2")],
        ..Runs::default()
    };
    let commands = [("cy", "/x/pool-t1"), ("c2", "/x/pool-t2")]
        .map(|(id, tree)| (id.to_owned(), format!("make carry FROM={tree}")))
        .into();
    assert_eq!(
        super::tiers::carries(&runs, &commands, &takes),
        [(
            "cy".to_owned(),
            ts(&at("01:50")).unwrap(),
            "451 T1".to_owned()
        )]
    );
}

/// The session stopped waiting on the GM inside a batch's span is the GM's row, never the batch's blocking (451 T403): over
/// 2026-11-26T17:00Z to 2026-11-27T01:00Z the second tier booked 27.6 of its 146.9 blocking minutes so, its turns ended on a question
/// to the GM between a task's carry and its landing. Here the session stops after its `make quick` and the GM answers 8 s later.
#[test]
fn the_session_waiting_on_the_gm_inside_a_batch_is_the_gm_s_row() {
    let more = [
        line("02:31", "Stop", &json!({})),
        line("02:39", "UserPromptSubmit", &json!({})),
    ];
    let (d, root) = world_with("task-time-tier-gm", &more);
    let out = report(&d, &root, &at("00:00")).stdout;
    let window = &out[..out.find("## The landed tasks").unwrap()];
    let tier =
        &out[out.find("## The second tier").unwrap()..out.find("## The biggest blocking").unwrap()];
    has(
        window,
        &[
            "| the GM | 0.0 | 0.0% | 0.1 | ",
            "Waiting on the GM: 0.1 min blocking",
        ],
    );
    assert!(!tier.contains("| the GM |"), "{tier}");
    has(
        tier,
        &["only the session's own work: its time stopped waiting on the GM is the GM's row"],
    );
}
