//! The view over fixture logs and a fixture pool (feature 451 T293): a builder mid-compile, a builder stopped on its plan review, a
//! landing in its gate, a free tree, a staged task - and the gaps: a resumed builder, a cut-off agent, a pool tree's mis-tasked phase.

use std::fmt::Write as _;
use std::path::Path;

use serde_json::{json, Value};

use super::*;

fn at(ms: &str) -> String {
    format!("2026-11-26T20:{ms}Z")
}

fn put(dir: &Path, rel: &str, lines: &[Value]) {
    let p = dir.join(rel);
    std::fs::create_dir_all(p.parent().unwrap()).unwrap();
    let text = lines.iter().fold(String::new(), |mut t, e| {
        let _ = writeln!(t, "{e}");
        t
    });
    std::fs::write(p, text).unwrap();
}

/// A tool line of agent `by` ("" the session) under `task`.
fn call(ev: &str, t: &str, tool: &str, id: &str, by: &str, task: &str) -> Value {
    let mut v = json!({"t": at(t), "sid": "s", "ev": ev, "tool": tool, "id": id, "task": task});
    if !by.is_empty() {
        v["by"] = json!(by);
    }
    v
}

fn with(mut v: Value, extra: &Value) -> Value {
    for (k, x) in extra.as_object().unwrap() {
        v[k] = x.clone();
    }
    v
}

fn agent(ev: &str, t: &str, aid: &str, kind: &str, task: &str) -> Value {
    json!({"t": at(t), "sid": "s", "ev": ev, "aid": aid, "agent": kind, "task": task})
}

fn phase(
    src: &str,
    step: &str,
    (t0, t1): (&str, &str),
    tree: &str,
    make: &str,
    task: &str,
) -> Value {
    json!({"ev": "Phase", "src": src, "step": step, "t0": at(t0), "t1": at(t1), "t": at(t1), "make": make,
           "clone": format!("/c/{tree}"), "sid": "s", "task": task})
}

/// The moment 20:30:00: tree b1 held by T1, its builder `aaaaaaaa1` in a foreground `make builder-checks` since 20:28 whose build
/// phase ended 20:29 (the line mis-tasked T9, as 451 T332 finds them); tree b2 held by T2, its builder `bbbbbbbb2` stopped at 20:20
/// with its `spec-fidelity` child running; tree b3 free; b4 held by T8, no builder; a `make land` of T3 in the background since
/// 20:25, its cheap phase ended 20:26; T4 carried from b2 at 20:05 (before T2 took the tree) and never landed; a `spec-fidelity`
/// cut off at 20:02.
#[expect(clippy::too_many_lines, reason = "one moment's whole world, listed")]
fn world() -> l7r_shared::tempdir::TempDir {
    let d = crate::checks::scratch("task-progress");
    let lines = vec![
        json!({"t": at("00:00"), "sid": "s", "ev": "UserPromptSubmit", "task": "T1"}),
        agent("SubagentStart", "02:00", "cutoff000", "spec-fidelity", "T7"),
        with(
            call("PreToolUse", "04:00", "Bash", "carry", "", "T4"),
            &json!({"make": "carry"}),
        ),
        with(
            call("PostToolUse", "05:00", "Bash", "carry", "", "T4"),
            &json!({"make": "carry"}),
        ),
        agent(
            "SubagentStart",
            "10:00",
            "aaaaaaaa1",
            "general-purpose",
            "T1",
        ),
        agent(
            "SubagentStart",
            "10:00",
            "bbbbbbbb2",
            "general-purpose",
            "T2",
        ),
        call("PreToolUse", "10:30", "Read", "r1", "aaaaaaaa1", "T1"),
        call("PostToolUse", "10:40", "Read", "r1", "aaaaaaaa1", "T1"),
        call("PreToolUse", "11:40", "Edit", "e1", "aaaaaaaa1", "T1"),
        call("PostToolUse", "11:45", "Edit", "e1", "aaaaaaaa1", "T1"),
        // refused by a guard: no end, and a later call of its ended
        call("PreToolUse", "11:00", "Bash", "refused", "aaaaaaaa1", "T1"),
        call("PreToolUse", "15:00", "Agent", "d1", "bbbbbbbb2", "T2"),
        with(
            call("PostToolUse", "15:01", "Agent", "d1", "bbbbbbbb2", "T2"),
            &json!({"aid": "kkkkkkkk3"}),
        ),
        agent("SubagentStart", "15:01", "kkkkkkkk3", "spec-fidelity", "T2"),
        call("PreToolUse", "16:00", "Read", "k1", "kkkkkkkk3", "T2"),
        call("PostToolUse", "16:30", "Read", "k1", "kkkkkkkk3", "T2"),
        with(
            agent(
                "SubagentStop",
                "20:00",
                "bbbbbbbb2",
                "general-purpose",
                "T2",
            ),
            &json!({"ctx": 150_000}),
        ),
        with(
            call("PreToolUse", "25:00", "Bash", "land", "", "T3"),
            &json!({"make": "land"}),
        ),
        with(
            call("PostToolUse", "25:01", "Bash", "land", "", "T3"),
            &json!({"make": "land", "bg": "bgland"}),
        ),
        json!({"t": at("25:30"), "sid": "s", "ev": "Stop", "task": "T3", "inflight": [
            {"id": "aaaaaaaa1", "type": "subagent"}, {"id": "kkkkkkkk3", "type": "subagent"}, {"id": "bgland", "type": "shell"}]}),
        with(
            call("PreToolUse", "28:00", "Bash", "bc", "aaaaaaaa1", "T1"),
            &json!({"make": "builder-checks"}),
        ),
        phase(
            "rust",
            "build",
            ("28:00", "29:00"),
            "b1",
            "builder-checks",
            "T9",
        ),
        // another tree's phase inside the same span: never this builder's
        phase(
            "rust",
            "build",
            ("28:10", "28:50"),
            "b2",
            "builder-checks",
            "T1",
        ),
        phase("land", "cheap", ("25:01", "26:00"), "root", "land", "T3"),
        // after the moment: never shown
        phase("land", "gate", ("26:00", "31:00"), "root", "land", "T3"),
        call("PreToolUse", "31:00", "Read", "late", "aaaaaaaa1", "T1"),
    ];
    put(&d, "root/.git/l7r-events/451-x.jsonl", &lines);
    let take = |t: &str, tree: &str, detail: &str| json!({"utc": at(t), "event": "take", "tree": format!("/c/{tree}"), "detail": detail});
    put(
        &d,
        "root/.git/builder-pool.log",
        &[
            take("03:00", "b2", "451 T4"),
            take("09:00", "b1", "451 T1"),
            take("09:30", "b2", "451 T2"),
        ],
    );
    let tree = |n: &str, tasks: &[&str], since: &str| json!({"tree": format!("/c/{n}"), "feature": "451", "tasks": tasks, "since": at(since)});
    std::fs::write(
        d.join("root/.git/builder-pool.json"),
        json!({"trees": [tree("b1", &["T1"], "09:00"), tree("b2", &["T2"], "09:30"), tree("b3", &[], "08:00"), tree("b4", &["T8"], "09:45")]}).to_string(),
    )
    .unwrap();
    let cmd = |id: &str, c: &str| json!({"message": {"content": [{"type": "tool_use", "id": id, "name": "Bash", "input": {"command": c}}]}});
    put(
        &d,
        "home/p/s.jsonl",
        &[
            cmd("carry", "make carry FROM=/c/b2"),
            cmd("land", "make land F=451 T=\"T3\" NOTE=x"),
        ],
    );
    let usage = json!({"type": "assistant", "message": {"role": "assistant", "usage": {"input_tokens": 1000, "cache_read_input_tokens": 200_000, "cache_creation_input_tokens": 9000}}});
    put(&d, "home/p/s/subagents/agent-aaaaaaaa1.jsonl", &[usage]);
    std::fs::create_dir_all(d.join("clones")).unwrap();
    d
}

fn seen(d: &Path) -> View {
    let now = ts(&at("30:00")).unwrap();
    view(
        &d.join("root"),
        (&d.join("home"), &d.join("clones")),
        now,
        Some(1.0),
    )
    .unwrap()
}

#[test]
fn a_builder_mid_compile_shows_its_open_run_its_last_phase_and_its_categories() {
    let d = world();
    let v = seen(&d);
    let b = &v.blocks[0];
    assert_eq!(
        (b.holder.as_str(), b.tree.as_ref().unwrap().0.as_str()),
        ("451 T1", "b1")
    );
    let a = &b.agents[0];
    assert!(a.running && !a.resumed && a.stop.is_none());
    assert_eq!(a.ctx, Some((210_000, "its transcript's last call")));
    assert_eq!(b.steps, ["aaaaaaaa now: make builder-checks, 2.0 min in; its last finished phase: rust build, ended 20:29:00"]);
    let row = |cat: &str| b.rows.iter().find(|r| r.0 == cat).map(|r| r.1);
    // the tree's own build phase, whatever task its line names (451 T332); the other tree's 40 s is not in it
    assert_eq!(row("compile"), Some(60.0));
    // the open run's other minute: the phase running now has no line yet
    assert_eq!(row("tests"), Some(60.0));
    assert_eq!(row("builders: reading code"), Some(40.0));
    assert!(row(OPEN_TURN).is_none() && !b.at_least);
}

#[test]
fn a_stopped_builder_waits_on_its_plan_review() {
    let d = world();
    let v = seen(&d);
    let b = &v.blocks[1];
    let a = &b.agents[0];
    assert!(!a.running && a.stop == Some(ts(&at("20:00")).unwrap()));
    assert_eq!(a.ctx, Some((150_000, "at its stop")));
    assert_eq!(b.steps, ["bbbbbbbb now: waiting on its spec-fidelity agent kkkkkkkk (plan review: agents), 15.0 min in"]);
    assert!(b.rows.iter().any(|r| r.0 == "plan review: agents"));
    // a held tree no builder was dispatched for
    assert_eq!(
        (v.blocks[2].holder.as_str(), v.blocks[2].agents.len()),
        ("451 T8", 0)
    );
    assert_eq!(v.blocks.len(), 3);
}

#[test]
fn a_landing_a_free_tree_a_staged_task_and_no_cut_off_agent() {
    let d = world();
    let v = seen(&d);
    assert_eq!(v.landings.len(), 1);
    let l = &v.landings[0];
    assert_eq!(
        (l.name.as_str(), l.phase.clone()),
        (
            "451 T3",
            Some(("land cheap".to_owned(), ts(&at("26:00")).unwrap()))
        )
    );
    assert!(l.rows.iter().any(|r| r.0 == "landing"), "{:?}", l.rows);
    assert_eq!(v.free, [("b3".to_owned(), at("08:00"))]);
    assert_eq!(
        v.staged,
        ["451 T4: carried 20:05:00, 25.0 min ago; no `make land` has named it"]
    );
    // the cut-off spec-fidelity has no stop, and the session's latest Stop does not name it
    assert!(v.others.is_empty(), "{:?}", v.others);
    let text = render::render(&v);
    for part in [
        "# The tasks in flight at 20:30:00 UTC (lines read from 19:30:00)",
        "## 451 T1 - tree b1, held since 20:09:00 (21.0 min)",
        "- builder aaaaaaaa (general-purpose): RUNNING; dispatched 20:10:00, 20.0 min ago; context 210k of the 300k cap (70%, its transcript's last call); its last line 2.0 min ago",
        "- builder bbbbbbbb (general-purpose): stopped 20:20:00;",
        "## 451 T8 - tree b4, held since 20:09:45",
        "- no builder has been dispatched for it since its tree was taken",
        "## Landing in flight: 451 T3 - `make land` began 20:25:00, 5.0 min in\n\n- its last finished phase: land cheap, ended 20:26:00 (4.0 min ago)",
        "- b3, free since 2026-11-26T20:08:00Z",
        "| compile | 1.0 |",
    ] {
        assert!(text.contains(part), "{part}\n{text}");
    }
}

#[test]
fn a_resumed_builder_is_at_least_and_a_model_turn_is_a_row() {
    let d = crate::checks::scratch("task-progress-resumed");
    put(
        &d,
        "root/.git/l7r-events/451-x.jsonl",
        &[
            agent(
                "SubagentStart",
                "10:00",
                "rrrrrrrr1",
                "general-purpose",
                "T5",
            ),
            agent(
                "SubagentStop",
                "15:00",
                "rrrrrrrr1",
                "general-purpose",
                "T5",
            ),
            call("PreToolUse", "20:00", "Read", "r1", "rrrrrrrr1", "T5"),
            call("PostToolUse", "20:30", "Read", "r1", "rrrrrrrr1", "T5"),
            agent("SubagentStart", "21:00", "pppppppp2", "research-pass", ""),
        ],
    );
    put(&d, "root/.git/page-sessions/run-live.log", &[]);
    std::fs::write(
        d.join("root/.git/page-sessions/run-live.log"),
        "started sid1 p1-write.md\nended sid1 rc=0\nstarted sid2 p1-check.md\n",
    )
    .unwrap();
    std::fs::write(
        d.join("root/.git/page-sessions/run-done.log"),
        "started sid1 p1-write.md\nALL DONE\n",
    )
    .unwrap();
    let v = view(
        &d.join("root"),
        (&d.join("home"), &d.join("clones")),
        ts(&at("31:00")).unwrap(),
        None,
    )
    .unwrap();
    // no pool: the builder has a block of its own, no tree
    let b = &v.blocks[0];
    assert!(b.tree.is_none() && b.at_least && b.agents[0].running && b.agents[0].resumed);
    assert_eq!(b.holder, "451 T5");
    assert_eq!(b.agents[0].ctx, None);
    assert_eq!(
        b.steps,
        ["rrrrrrrr now: a model turn, 10.5 min since its last call ended"]
    );
    assert_eq!(
        b.rows.iter().find(|r| r.0 == OPEN_TURN).map(|r| r.1),
        Some(630.0)
    );
    assert_eq!(
        v.others[0],
        "research-pass agent pppppppp (no task), dispatched by the session: 10.0 min in"
    );
    // the fixture's run log was written just now, after this view's moment: a page session's line is its log's, dated by the file
    let live = |l: &String| {
        l.starts_with("page session run-live: in p1-check.md, ")
            && l.ends_with("1 of its briefs ended")
    };
    assert!(v.others.iter().any(live));
    assert!(!v.others.iter().any(|l| l.contains("run-done")));
    let text = render::render(&v);
    for part in [
        "## 451 T5 - no pool tree is held for it",
        "RUNNING, resumed after a stop (its later start and stop lines are not read, 451 T324",
        "context not known",
        "Its minutes so far, AT LEAST (a resumed builder's later spans are not read, 451 T324)",
        "No landing is in flight.",
        "- none: every task carried has landed",
    ] {
        assert!(text.contains(part), "{part}\n{text}");
    }
}

#[test]
fn the_command_line() {
    let d = world();
    let (home, clones) = (d.join("home"), d.join("clones"));
    let run = |list: &[&str]| {
        let args: Vec<String> = list.iter().map(|s| (*s).to_owned()).collect();
        cli(&args, &home, &clones, ts(&at("30:00")).unwrap())
    };
    let root = d.join("root").to_string_lossy().into_owned();
    let ok = run(&["--root", &root, "--back", "1h"]);
    assert_eq!(ok.code, 0, "{}", ok.stderr);
    assert!(ok.stdout.contains("## 451 T1 - tree b1"));
    // as of an earlier moment the landing had not begun
    let past = run(&["--root", &root, "--back", "1h", "--at", &at("24:00")]);
    assert!(past.stdout.contains("No landing is in flight."));
    // between the session's Stop (20:25:30) and the cheap phase's end (20:26:00) the landing is in flight, no phase of it finished
    let early = run(&["--root", &root, "--back", "1h", "--at", &at("25:40")]);
    let want = "## Landing in flight: 451 T3 - `make land` began 20:25:00, 0.7 min in\n\n- no phase of it has finished\n";
    assert!(early.stdout.contains(want), "{}", early.stdout);
    assert_eq!(run(&["--back", "soon"]).code, 2);
    assert_eq!(run(&["--nope"]).code, 2);
    assert_eq!(run(&["--root", &root, "--at", "never"]).code, 1);
}

/// The moment 20:30:00, the arms `world()` leaves: tree c1 held by T1, carried twice (20:05:00 and 20:08:30), its builder
/// `cccccccc1` cut off (no stop, and the session's `Stop` at 20:25:30 does not name it) and a landing naming T1 red at 20:12; tree c2
/// held by T2, its builder `dddddddd2` in an open Read with a `make builder-checks` of its own in the background; tree c4 free, a
/// phase of it naming T6; a builder `eeeeeeee3` of T6 no tree is held for, in a foreground `make builder-checks` whose build phase
/// its own checkout wrote; and the session's foreground `make land` of T3 open, its end line already written.
fn gaps() -> l7r_shared::tempdir::TempDir {
    let d = crate::checks::scratch("task-progress-gaps");
    let make = |v: Value, target: &str| with(v, &json!({"make": target}));
    let builder =
        |aid: &str, t: &str, task: &str| agent("SubagentStart", t, aid, "general-purpose", task);
    let end = |(t0, t1): (&str, &str), task: &str, landed: bool| {
        json!({"ev": "Phase", "src": "land", "step": "end", "t0": at(t0), "t1": at(t1), "t": at(t1), "make": "land",
               "clone": "/c/root", "sid": "s", "task": task, "tasks": [task], "landed": landed})
    };
    let by =
        |ev: &str, t: &str, id: &str, who: &str, task: &str| call(ev, t, "Bash", id, who, task);
    let lines = vec![
        json!({"t": at("00:00"), "sid": "s", "ev": "UserPromptSubmit", "task": "T1"}),
        make(by("PreToolUse", "04:00", "carry1", "", "T1"), "carry"),
        make(by("PostToolUse", "05:00", "carry1", "", "T1"), "carry"),
        make(by("PreToolUse", "08:00", "carry2", "", "T1"), "carry"),
        make(by("PostToolUse", "08:30", "carry2", "", "T1"), "carry"),
        builder("cccccccc1", "10:00", "T1"),
        builder("dddddddd2", "10:00", "T2"),
        call("PreToolUse", "10:30", "Read", "r1", "cccccccc1", "T1"),
        call("PostToolUse", "10:40", "Read", "r1", "cccccccc1", "T1"),
        end(("10:00", "12:00"), "T1", false),
        builder("eeeeeeee3", "12:00", "T6"),
        json!({"t": at("25:30"), "sid": "s", "ev": "Stop", "task": "T1", "inflight": [{"id": "dddddddd2", "type": "subagent"}]}),
        make(by("PreToolUse", "26:00", "land2", "", "T3"), "land"),
        end(("26:00", "29:50"), "T3", true),
        make(
            by("PreToolUse", "27:00", "bgc", "dddddddd2", "T2"),
            "builder-checks",
        ),
        with(
            by("PostToolUse", "27:01", "bgc", "dddddddd2", "T2"),
            &json!({"make": "builder-checks", "bg": "bgd2"}),
        ),
        make(
            by("PreToolUse", "28:00", "bce", "eeeeeeee3", "T6"),
            "builder-checks",
        ),
        phase(
            "rust",
            "build",
            ("28:00", "29:00"),
            "root",
            "builder-checks",
            "T6",
        ),
        // a pool tree's phase naming the task: never a builder's that no tree is held for
        phase(
            "rust",
            "build",
            ("28:00", "29:30"),
            "c4",
            "builder-checks",
            "T6",
        ),
        call("PreToolUse", "29:00", "Read", "openread", "dddddddd2", "T2"),
    ];
    put(&d, "root/.git/l7r-events/451-x.jsonl", &lines);
    put(
        &d,
        "root/.git/builder-pool.log",
        &[json!({"utc": at("03:00"), "event": "take", "tree": "/c/c1", "detail": "451 T1"})],
    );
    let tree = |n: &str, tasks: &[&str], since: &str| json!({"tree": format!("/c/{n}"), "feature": "451", "tasks": tasks, "since": at(since)});
    std::fs::write(
        d.join("root/.git/builder-pool.json"),
        json!({"trees": [tree("c1", &["T1"], "03:00"), tree("c2", &["T2"], "09:30"), tree("c4", &[], "08:00")]}).to_string(),
    )
    .unwrap();
    let cmd = |id: &str, c: &str| json!({"message": {"content": [{"type": "tool_use", "id": id, "name": "Bash", "input": {"command": c}}]}});
    put(
        &d,
        "home/p/s.jsonl",
        &[
            cmd("carry1", "make carry FROM=/c/c1"),
            cmd("carry2", "make carry FROM=/c/c1"),
            cmd("land2", "make land F=451 T=\"T3\" NOTE=x"),
        ],
    );
    // a run log with no brief started yet
    put(&d, "root/.git/page-sessions/run-empty.log", &[]);
    std::fs::create_dir_all(d.join("clones")).unwrap();
    d
}

#[test]
fn a_cut_off_builder_a_carried_tree_and_a_landing_gone_red() {
    let d = gaps();
    let v = seen(&d);
    let b = &v.blocks[0];
    assert_eq!(b.holder, "451 T1");
    assert!(!b.agents[0].running && b.agents[0].stop.is_none());
    assert_eq!(b.steps, ["cccccccc now: nothing of its is in flight: it waits on the session (a carry, a landing, or its closing builder)"]);
    // the LATEST of its two carries
    assert_eq!(b.carried, Some(ts(&at("08:30")).unwrap()));
    assert_eq!(v.staged, ["451 T1: carried 20:08:30, 21.5 min ago; a landing naming it went red at 20:12:00 and none has run since"]);
    let empty = |l: &String| {
        l.starts_with("page session run-empty: in no brief started, ")
            && l.ends_with("0 of its briefs ended")
    };
    assert!(v.others.iter().any(empty));
    let text = render::render(&v);
    for part in [
        "- builder cccccccc (general-purpose): not running: no stop line, and its session's latest Stop does not name it in flight (cut off); dispatched 20:10:00,",
        "- carried into the clone 20:08:30, 21.5 min ago\n",
    ] {
        assert!(text.contains(part), "{part}\n{text}");
    }
}

#[test]
fn an_open_call_a_background_run_and_a_builder_with_no_tree() {
    let d = gaps();
    let v = seen(&d);
    assert_eq!(v.blocks.len(), 3);
    let b = &v.blocks[1];
    assert!(b.agents[0].running);
    assert_eq!(b.steps, ["dddddddd now: a Read call, 1.0 min in; and make builder-checks in the background, 3.0 min in; no phase of it has finished"]);
    let b = &v.blocks[2];
    assert_eq!((b.holder.as_str(), b.tree.is_none()), ("451 T6", true));
    // its own checkout's phase, not the pool tree's that names its task and ended later
    assert_eq!(b.steps, ["eeeeeeee now: make builder-checks, 2.0 min in; its last finished phase: rust build, ended 20:29:00"]);
    let compile = b.rows.iter().find(|r| r.0 == "compile").map(|r| r.1);
    assert_eq!(compile, Some(60.0));
}

#[test]
fn a_foreground_landing_whose_end_line_is_written_is_named_by_its_run() {
    let d = gaps();
    let v = seen(&d);
    assert_eq!(v.landings.len(), 1);
    let l = &v.landings[0];
    // no open attempt of a batch is its: the task is its call's, with no feature
    assert_eq!(l.name, "T3");
    assert_eq!(Some(l.t0), ts(&at("26:00")).ok());
    let ended = ts(&at("29:50")).unwrap();
    assert_eq!(l.phase, Some(("land end".to_owned(), ended)));
}

#[test]
fn nothing_running_and_a_stop_that_names_no_list() {
    let d = crate::checks::scratch("task-progress-none");
    std::fs::create_dir_all(d.join("root/.git")).unwrap();
    let v = seen(&d);
    assert!(v.blocks.is_empty() && v.landings.is_empty());
    let text = render::render(&v);
    assert!(text.contains("No pool tree is held and no builder is running.\n"));
    // a `Stop` written before the `inflight` field cannot say: a builder with no stop line is taken as running
    let start = agent(
        "SubagentStart",
        "10:00",
        "ffffffff1",
        "general-purpose",
        "T1",
    );
    let stop = json!({"t": at("25:30"), "sid": "s", "ev": "Stop", "task": "T1"});
    put(&d, "root/.git/l7r-events/451-x.jsonl", &[start, stop]);
    let v = seen(&d);
    assert!(v.blocks[0].agents[0].running);
}
