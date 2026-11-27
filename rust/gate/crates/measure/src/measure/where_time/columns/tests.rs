//! The runs, their ends, their compile split and the default goal (feature 451 T08).

use std::collections::HashMap;

use serde_json::{json, Value};

use super::*;

fn at(hms: &str) -> String {
    format!("2026-11-01T{hms}Z")
}

fn ev(v: &Value) -> Event {
    v.as_object().unwrap().clone()
}

#[test]
fn a_line_is_booked_by_its_make_else_its_frozen_cat() {
    for (cat, want) in [
        ("tests", "tests"),
        ("quick test", "tests"),
        ("test file", "tests"),
        ("gate", "gate"),
        ("land", "land"),
        ("review", "review"),
        ("docs", "docs"),
        ("spec-kit step", "spec-kit step"),
        ("other tool", "other"),
        ("edit", "other"),
    ] {
        assert_eq!(cat_bucket(cat), want, "{cat}");
    }
    // a past log's frozen `other tool` re-booked by its `make` (User Story 1 scenario 1)
    for (make, want) in [
        ("static", "tests"),
        ("rust-test", "tests"),
        ("hooks-test", "tests"),
        ("land", "land"),
    ] {
        assert_eq!(
            line_bucket(&ev(&json!({"make": make, "cat": "other tool"})), "done"),
            want
        );
    }
    assert_eq!(
        line_bucket(&ev(&json!({"make": ".DEFAULT_GOAL"})), "done"),
        "gate"
    );
    // no Makefile read: the literal word, which the table does not know
    assert_eq!(target(".DEFAULT_GOAL", ""), ".DEFAULT_GOAL");
    assert_eq!(line_bucket(&ev(&json!({"cat": "quick test"})), ""), "tests");
}

#[test]
fn the_default_goal_is_the_first_rule_unless_one_is_set() {
    let mk = "# c\nA = x:y\nB := 1\n$(foreach v,x,y): z\n.PHONY: a b\n\t@true\n  c: d\nwork-budget work-x:  ## [performance] x\n\t@true\ndone:\n";
    assert_eq!(default_goal(mk), "work-budget");
    assert_eq!(
        default_goal(&format!("{mk}.DEFAULT_GOAL := done\n")),
        "done"
    );
    assert_eq!(default_goal(".DEFAULT_GOAL =\nquick:\n"), "quick");
    assert_eq!(default_goal(".SUFFIXES:\n"), "");
    // the repository's own: its first rule is `work-budget` (Makefile line 29, read 2026-11-21)
    assert_eq!(
        bucket_of(&default_goal("work-budget:    ## [performance] x\n")),
        "tests"
    );
}

/// T08's note: bnikhrir8's launch (2026-11-20 11:44:23, the 449 log) was booked `other tool` with no make. Its command, from the session
/// transcript: a multi-line `python3 -c "..."` string, a heredoc commit, then `make land`. Since T15's reader the detector reads it.
#[test]
fn the_python_c_launch_reads_make_land() {
    let cmd = "python3 -c \"\np='specs/449-rust-codebase/plan-review.json'; s=open(p).read(); open(p,'w').write(s.replace('be'+'haviour','behavior'))\"; git add -A && git commit -q -F - <<'EOF'\nthe verdict record's spelling (T242 carries the writer's fix)\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nEOF\nL=/home/agent/.claude/jobs/c6fd72d1/tmp/t238-land.log; PLAN_REVIEW_OK=\"T238 reviewed CLEAR by spec-fidelity on 2026-11-20\" make land F=449 T=T238 NOTE=\"a Rust stage's placement change owes its declaration\" > $L 2>&1; echo \"land $?\"; grep -E \"refused|holds|HEAD -> main|GATE|be.haviour\" $L | grep -v pre-existing | head -6 | cut -c1-220";
    assert_eq!(l7r_shared::make::invoked(cmd), ["land"]);
    assert_eq!(
        l7r_shared::guards::event_log_hooks::make_target(cmd),
        "land"
    );
}

#[test]
#[expect(clippy::float_cmp, reason = "a time read back exactly")]
fn the_enqueue_row_names_a_runs_end() {
    let d = crate::checks::scratch("measure-columns-enqueue");
    let row = |ty: &str, t: Value, id: &str| json!({"type": ty, "operation": "enqueue", "timestamp": t, "content": format!("<task-notification>\n<tool-use-id>{id}</tool-use-id>\n")});
    let rows = [
        row("queue-operation", json!(at("08:00:05")), "toolu_a"),
        row("queue-operation", json!(at("08:09:00")), "toolu_a"),
        row("queue-operation", json!(at("08:00:06")), "toolu_b"),
        row("user", json!(at("08:00:07")), "toolu_c"),
        row("queue-operation", json!(5), "toolu_d"),
        row("queue-operation", json!(at("08:00:08")), "nope"),
        json!({"type": "queue-operation", "operation": "enqueue", "timestamp": at("08:00:09")}),
    ];
    let mut text: String = rows.iter().map(|r| r.to_string() + "\n").collect();
    text += "{\"operation\": \"enqueue\", half a row\n";
    std::fs::create_dir_all(d.join("p")).unwrap();
    std::fs::write(d.join("p/s.jsonl"), text).unwrap();
    let got = enqueued(&["s".to_owned(), "gone".to_owned()], &d);
    assert_eq!(got.len(), 2, "{got:?}");
    assert_eq!(got["toolu_a"], ts(&at("08:00:05")).unwrap());
    assert_eq!(got["toolu_b"], ts(&at("08:00:06")).unwrap());
}

/// D4's tie: a phase inside two runs of its session and target goes to the run of its own task, else to the one started last; a phase
/// of another step is no compile; one in no run's span is loose.
#[test]
fn a_phase_goes_to_its_tasks_run_then_the_latest() {
    let pre = |t: &str, id: &str, task: &str| {
        ev(
            &json!({"t": at(t), "sid": "s", "ev": "PreToolUse", "tool": "Bash", "id": id, "make": "rust-test", "task": task}),
        )
    };
    let post = |t: &str, id: &str| {
        ev(&json!({"t": at(t), "sid": "s", "ev": "PostToolUseFailure", "tool": "Bash", "id": id}))
    };
    let stream = [
        pre("08:00:00", "a", "T05"),
        pre("08:00:10", "b", "T06"),
        ev(
            &json!({"t": at("08:00:20"), "sid": "s", "ev": "PreToolUse", "tool": "Read", "id": "r"}),
        ),
        post("08:05:00", "a"),
        post("08:05:00", "b"),
    ];
    let phase = |step: &str, task: &str, t0: &str, t1: &str| {
        ev(
            &json!({"ev": "Phase", "sid": "s", "step": step, "make": "rust-test", "task": task, "t0": at(t0), "t1": at(t1)}),
        )
    };
    let phase_of = |make: &str, task: &str, t0: &str, t1: &str| {
        ev(
            &json!({"ev": "Phase", "sid": "s", "step": "build", "make": make, "task": task, "t0": at(t0), "t1": at(t1)}),
        )
    };
    let aside = [
        phase("build", "T05", "08:01:00", "08:02:00"),
        phase("cover-build", "", "08:03:00", "08:03:30"),
        phase("test", "T05", "08:02:00", "08:04:00"),
        phase("build", "", "08:06:00", "08:07:00"),
        // a phase whose `make` names another target, tied by its task; one whose task matches neither run, loose
        phase_of("hooks-test", "T06", "08:04:00", "08:04:10"),
        phase_of("hooks-test", "T09", "08:04:20", "08:04:30"),
        // after the window's end: no run of it, and not loose
        phase_of("rust-test", "", "09:00:00", "09:01:00"),
    ];
    let none = HashMap::new();
    let no_stops = HashMap::new();
    let w = Window {
        stopped: &no_stops,
        queued: &HashMap::new(),
        end: ts(&at("09:00:00")).unwrap(),
        enqueued: &none,
        goal: "",
    };
    let r = runs(&stream, &aside, &[], &w).unwrap();
    assert_eq!(r.runs.len(), 2);
    assert_eq!((r.runs[0].compile_s(), r.runs[1].compile_s()), (60.0, 40.0));
    assert_eq!(r.loose, (2, 70.0));
    assert_eq!(splits_by_id(&r).len(), 2);
    let bad = [ev(
        &json!({"ev": "Phase", "step": "build", "t0": 5, "t1": at("08:00:00")}),
    )];
    assert!(runs(&stream, &bad, &[], &w).is_err());
    // a run before any task start, its line naming none: the mark's `-`
    let lone = [
        ev(
            &json!({"t": at("08:00:00"), "sid": "s", "ev": "PreToolUse", "tool": "Bash", "id": "c"}),
        ),
        ev(
            &json!({"t": at("08:00:01"), "sid": "s", "ev": "PostToolUse", "tool": "Bash", "id": "c"}),
        ),
    ];
    // a call started after the window's end is none of its runs
    let mut lone = lone.to_vec();
    lone.push(ev(
        &json!({"t": at("09:30:00"), "sid": "s", "ev": "PreToolUse", "tool": "Bash", "id": "c"}),
    ));
    let r = runs(&lone, &[], &[], &w).unwrap();
    assert_eq!((r.runs[0].task.as_str(), r.runs[0].bucket), ("-", "other"));
    // a task the order does not name is rendered after those it does
    let text = render(&r, &["T09".to_owned()]);
    assert!(text.contains("\n| - | 1 | 0.0 |"), "{text}");
    assert!(overlap(&[], 0.0, 1.0).to_bits() == 0.0_f64.to_bits());
}

#[test]
fn a_task_stop_names_the_run_it_ended() {
    let d = crate::checks::scratch("measure-columns-stopped");
    let call = |name: &str, id: &str, input: Value| json!({"type": "assistant", "message": {"content": [{"type": "tool_use", "id": id, "name": name, "input": input}, {"type": "text", "text": "TaskStop"}]}});
    let main = [
        call("KillShell", "toolu_k0", json!({"shell_id": "b0"})),
        json!({"type": "user", "message": {"content": "TaskStop"}}),
    ];
    let mut text: String = main.iter().map(|r| r.to_string() + "\n").collect();
    text += "{\"TaskStop\": half a row\n";
    std::fs::create_dir_all(d.join("p/s/subagents")).unwrap();
    std::fs::write(d.join("p/s.jsonl"), text).unwrap();
    let sub = call("TaskStop", "toolu_k1", json!({"task_id": "b1"}));
    std::fs::write(
        d.join("p/s/subagents/agent-a.jsonl"),
        sub.to_string() + "\n",
    )
    .unwrap();
    let got = stopped(&["s".to_owned(), "gone".to_owned()], &d);
    assert_eq!(
        got,
        HashMap::from([
            ("toolu_k0".to_owned(), "b0".to_owned()),
            ("toolu_k1".to_owned(), "b1".to_owned())
        ])
    );
}

/// T08's final check: the day's landings were launched `make claims-owed F=451 ...; make ledger-owed; make land F=451 T=T33` (the 451
/// log, 2026-11-21 02:25:35, `makes` `["claims-owed","ledger-owed","land"]`, `make` `claims-owed`), so booked by their first target they
/// went to review: the runs table showed land 4.2 min and gate 0.0 while the landings' `src: land` phases summed 27.4 min of gate. A
/// line is booked by every target it runs, land first; a landing's `gate` and `cohort` phases are gate, its compile still compile.
#[test]
fn a_landing_is_booked_land_and_its_gate_split_out() {
    let makes = |m: &[&str]| line_bucket(&ev(&json!({"make": m[0], "makes": m})), "done");
    assert_eq!(makes(&["claims-owed", "ledger-owed", "land"]), "land");
    assert_eq!(makes(&["quick", "done"]), "gate");
    assert_eq!(makes(&["decide", "quick"]), "tests");
    assert_eq!(makes(&["where-time", "plan-delta"]), "review");
    assert_eq!(makes(&["tick", "feature-report"]), "docs");
    assert_eq!(makes(&["no-such", "task-start"]), "spec-kit step");
    assert_eq!(makes(&["no-such", "nor-this"]), "other");
    assert_eq!(makes(&["claims-owed", ".DEFAULT_GOAL"]), "gate");
    // the real launch shape: the landing's task (T07) is not the line's (T33), so only its `makes` ties its phases
    let stream = [
        ev(
            &json!({"t": at("08:00:00"), "sid": "s", "ev": "PreToolUse", "tool": "Bash", "id": "toolu_l", "cat": "review", "makes": ["claims-owed", "ledger-owed", "land"], "make": "claims-owed", "task": "T33"}),
        ),
        ev(
            &json!({"t": at("08:00:01"), "sid": "s", "ev": "PostToolUse", "tool": "Bash", "id": "toolu_l", "cat": "review", "makes": ["claims-owed", "ledger-owed", "land"], "make": "claims-owed", "bg": "b1", "task": "T33"}),
        ),
    ];
    let land = |step: &str, t0: &str, t1: &str| {
        ev(
            &json!({"ev": "Phase", "src": "land", "sid": "s", "step": step, "make": "land", "task": "T07", "t0": at(t0), "t1": at(t1)}),
        )
    };
    let aside = [
        ev(
            &json!({"t": at("08:10:00"), "ev": "BgEnd", "id": "toolu_l", "bg": "b1", "make": "claims-owed"}),
        ),
        land("cheap", "08:00:05", "08:01:00"),
        land("gate", "08:01:00", "08:06:00"),
        land("cohort", "08:02:00", "08:07:00"),
        land("end", "08:00:05", "08:09:00"),
        ev(
            &json!({"ev": "Phase", "src": "rust", "sid": "s", "step": "build", "make": "land", "task": "T07", "t0": at("08:01:30"), "t1": at("08:02:30")}),
        ),
        // a gate phase of no run's: counted loose
        land("gate", "08:20:00", "08:21:00"),
    ];
    let (none, no_stops) = (HashMap::new(), HashMap::new());
    let w = Window {
        stopped: &no_stops,
        queued: &HashMap::new(),
        end: ts(&at("09:00:00")).unwrap(),
        enqueued: &none,
        goal: "done",
    };
    let r = runs(&stream, &aside, &[], &w).unwrap();
    let l = &r.runs[0];
    assert_eq!((l.bucket, l.compile_s(), l.gate_s()), ("land", 60.0, 300.0));
    assert_eq!(r.loose, (1, 60.0));
    let rows = by_task(&r);
    let t = &rows[0].1;
    let got: Vec<f64> = ["land", "gate", "compile", "review"]
        .iter()
        .map(|c| t.get(&(*c).to_owned()))
        .collect();
    assert_eq!(got, [240.0, 300.0, 60.0, 0.0]);
    assert_eq!(
        splits_by_id(&r)["toolu_l"].spans("gate"),
        l.split.spans("gate")
    );
}

#[test]
fn a_span_less_its_cuts() {
    let cut = [(0.0, 1.0), (2.0, 3.0), (5.0, 9.0), (20.0, 21.0)];
    assert_eq!(
        minus(&[(1.5, 6.0), (10.0, 12.0)], &cut),
        [(1.5, 2.0), (3.0, 5.0), (10.0, 12.0)]
    );
}

/// Feature 451 T153: each phase's minutes go to its category - a `make done` run's compile, its hook suites (run side by side, their union
/// once), its seeds (map generation) and its counters (tests), carved first first so no second is booked twice, the rest of the run its
/// own bucket; a `make map`'s steps map generation; a page session, held by no run, booked under its task; a container step (`static`) none.
#[test]
fn each_phase_is_booked_to_its_category() {
    let call = |id: &str, ev_: &str, t: &str, make: &str| {
        ev(
            &json!({"t": at(t), "sid": "s", "ev": ev_, "tool": "Bash", "id": id, "make": make, "task": "T9"}),
        )
    };
    let stream = [
        call("toolu_d", "PreToolUse", "08:00:00", "done"),
        call("toolu_d", "PostToolUse", "08:20:00", "done"),
        call("toolu_m", "PreToolUse", "09:00:00", "map"),
        call("toolu_m", "PostToolUse", "09:01:00", "map"),
    ];
    let phase = |src: &str, step: &str, make: &str, t0: &str, t1: &str| {
        ev(
            &json!({"ev": "Phase", "src": src, "sid": "s", "step": step, "make": make, "task": "T9", "t0": at(t0), "t1": at(t1)}),
        )
    };
    let aside = [
        phase("gate", "static", "done", "08:00:00", "08:05:00"),
        phase("rust", "build", "done", "08:01:00", "08:03:00"),
        phase("hooks", "suite", "done", "08:05:00", "08:08:00"),
        phase("hooks", "suite", "done", "08:06:00", "08:09:00"),
        // a suite that compiled: its compile is compile
        phase("rust", "build", "done", "08:08:30", "08:09:00"),
        phase("gate", "seeds", "done", "08:10:00", "08:12:00"),
        phase("gate", "counters-inert", "done", "08:12:00", "08:13:00"),
        phase("rust", "test", "done", "08:12:00", "08:12:30"),
        phase("map", "generate", "map", "09:00:10", "09:00:40"),
        phase("map", "cached", "map", "09:00:40", "09:00:41"),
        phase("page-session", "write", "", "10:00:00", "10:30:00"),
        phase("page-session", "check", "", "10:30:00", "10:40:00"),
    ];
    let (none, no_stops) = (HashMap::new(), HashMap::new());
    let w = Window {
        stopped: &no_stops,
        queued: &HashMap::new(),
        end: ts(&at("11:00:00")).unwrap(),
        enqueued: &none,
        goal: "done",
    };
    let r = runs(&stream, &aside, &[], &w).unwrap();
    let d = &r.runs[0];
    let carved: Vec<(&str, f64)> = d.split.booked(d.t0, d.t1);
    let want = [
        ("compile", 150.0),
        ("hook suites", 210.0),
        ("map generation", 120.0),
        ("tests", 60.0),
    ];
    assert_eq!(carved, want);
    let rows = by_task(&r);
    let t = &rows[0].1;
    let cols = [
        "gate",
        "compile",
        "hook suites",
        "map generation",
        "tests",
        "docs",
        "review",
    ];
    let got: Vec<f64> = cols.iter().map(|c| t.get(&(*c).to_owned())).collect();
    // done's 1,200 s: 540 split out, 660 its own bucket (gate); the map run's 60 s: 31 map generation, 29 tests (its bucket)
    assert_eq!(got, [660.0, 150.0, 210.0, 151.0, 89.0, 1800.0, 600.0]);
    assert_eq!((r.loose, r.detached.len()), ((0, 0.0), 2));
    let text = render(&r, &[]);
    let header = text.contains(
        "| tests | compile | waiting on a build slot | hook suites | map generation | gate |",
    );
    assert!(header, "{text}");
}

/// Feature 451 T153: a page session's line that names no task is booked under the task started before it, a task no run of the
/// window holds getting its own row.
#[test]
fn a_task_less_page_session_is_booked_under_the_task_then_active() {
    let line = json!({"ev": "Phase", "src": "page-session", "sid": "s", "step": "write", "t0": at("10:00:00"), "t1": at("10:20:00")});
    let (none, no_stops) = (HashMap::new(), HashMap::new());
    let w = Window {
        stopped: &no_stops,
        queued: &HashMap::new(),
        end: ts(&at("11:00:00")).unwrap(),
        enqueued: &none,
        goal: "done",
    };
    let starts = [(ts(&at("09:00:00")).unwrap(), "T7".to_owned())];
    let r = runs(&[], &[ev(&line)], &starts, &w).unwrap();
    let rows = by_task(&r);
    let got: Vec<(&str, f64)> = rows
        .iter()
        .map(|(k, t)| (k.as_str(), t.get(&"docs".to_owned())))
        .collect();
    assert_eq!(got, [("T7", 1200.0)]);
}

#[test]
fn a_phase_s_category_by_its_tool_and_step() {
    let of = |src: &str, step: &str| category(&ev(&json!({"src": src, "step": step})));
    let got: Vec<Option<&str>> = [
        ("rust", "build"),
        ("rust", "cover-build"),
        ("rust", "cover-run"),
        ("rust", "lint"),
        ("rust", "slot-wait"),
        ("hooks", "suite"),
        ("map", "page"),
        ("cohort", "cohort"),
        ("gate", "reference"),
        ("gate", "preflight"),
        ("quick", "quick"),
        ("preflight", "preflight"),
        ("land", "cohort"),
        ("land", "end"),
        ("record", "site"),
        ("page-session", "check"),
        ("gate", "hooks-test"),
        ("rust", "prewarm"),
    ]
    .iter()
    .map(|(a, b)| of(a, b))
    .collect();
    let want = [
        Some("compile"),
        Some("compile"),
        Some("tests"),
        None,
        // a cargo call's wait for a build slot, a category of its own (feature 451 T284)
        Some(SLOT_WAIT),
        Some("hook suites"),
        Some("map generation"),
        Some("map generation"),
        Some("map generation"),
        Some("tests"),
        Some("tests"),
        Some("tests"),
        Some("gate"),
        None,
        Some("docs"),
        Some("review"),
        None,
        // a pool tree's pre-warm (feature 451 T316, `rustc/prewarm.rs`): a build nobody waited on, in no call's compile
        None,
    ];
    assert_eq!(got, want);
    let empty = Split::default();
    assert!(empty.spans("compile").is_empty());
}
