//! The count against a temporary clone and its log; the refusal through the hook chain. The suite
//! (`tests/hooks/test-static-runs-hooks.sh`, replayed through the shim) drives the binary on the same cases.

use std::path::Path;

use serde_json::{json, Value};

use super::{
    answer, crates_of, delta_crates, judge, refusal, runs, stamp, Said, STATIC_RUNS_A_TASK,
};
use crate::guards::event_log_hooks;
use crate::protocol::{run, Answer, Event};
use crate::shared::session::Session;
use crate::shared::tempdir::TempDir;

const F: &str = "451-x";

/// A clone with feature 451's directory, its `feature.json`, `task-starts.jsonl` holding `starts` and its log holding `lines`.
fn clone(tag: &str, starts: &[(&str, &str)], lines: &[Value]) -> TempDir {
    let d = TempDir::new(&format!("guard-static-{tag}"));
    std::fs::create_dir_all(d.join(".git/l7r-events")).unwrap();
    std::fs::create_dir_all(d.join("specs").join(F)).unwrap();
    std::fs::create_dir_all(d.join(".specify")).unwrap();
    std::fs::write(
        d.join(".specify/feature.json"),
        format!(r#"{{"feature_directory": "specs/{F}"}}"#),
    )
    .unwrap();
    let starts: Vec<Value> = starts
        .iter()
        .map(|(task, utc)| json!({"feature": F, "task": task, "utc": utc}))
        .collect();
    std::fs::write(d.join(".git/task-starts.jsonl"), jsonl(&starts)).unwrap();
    write_log(&d, lines);
    d
}

/// Lines as a JSONL file holds them, each ended.
fn jsonl(lines: &[Value]) -> String {
    lines.iter().map(|l| l.to_string() + "\n").collect()
}

fn write_log(d: &Path, lines: &[Value]) {
    std::fs::write(
        d.join(".git/l7r-events").join(format!("{F}.jsonl")),
        jsonl(lines),
    )
    .unwrap();
}

/// A run of `make static` by `task` at `t` that ran: its `PreToolUse` line and its `PostToolUse`.
fn ran(id: &str, t: &str, task: &str) -> [Value; 2] {
    [
        json!({"t": t, "ev": "PreToolUse", "tool": "Bash", "id": id, "make": "static", "task": task}),
        json!({"t": t, "ev": "PostToolUse", "tool": "Bash", "id": id, "make": "static", "task": task}),
    ]
}

fn end(t: &str, tasks: &[&str], landed: bool, code: i32) -> Value {
    json!({"ev": "Phase", "src": "land", "step": "end", "t": t, "code": code, "make": "land", "task": tasks[0], "tasks": tasks, "landed": landed})
}

/// A call's hook input, backgrounded as a closing check must be (T55); [`foreground`] the same call without it.
fn input(d: &Path, cmd: &str) -> Value {
    json!({"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_use_id": "toolu_now", "cwd": d.to_string_lossy(), "tool_input": {"command": cmd, "run_in_background": true}})
}

fn foreground(d: &Path, cmd: &str) -> Value {
    let mut v = input(d, cmd);
    v["tool_input"]
        .as_object_mut()
        .unwrap()
        .remove("run_in_background");
    v
}

fn none(_: &str) -> Option<String> {
    None
}

fn guard_crate(_: &Path) -> Vec<String> {
    vec!["rust/guard".to_owned()]
}

fn said(d: &Path, cmd: &str) -> Option<Said> {
    judge(&input(d, cmd), Path::new("/"), &none, &guard_crate)
}

/// T06's refusal after its two runs.
fn refused() -> Said {
    Said::Refused {
        feature: F.to_owned(),
        task: "T06".to_owned(),
        runs: 2,
        crates: vec!["rust/guard".to_owned()],
    }
}

fn two_runs() -> Vec<Value> {
    [
        ran("a", "2026-11-20T10:01:00.000Z", "T06"),
        ran("b", "2026-11-20T10:02:00.000Z", "T06"),
    ]
    .concat()
}

#[test]
fn the_third_run_since_the_first_start_is_refused_naming_the_crates_checks() {
    let d = clone("third", &[("T06", "2026-11-20T10:00:00Z")], &two_runs());
    assert_eq!(STATIC_RUNS_A_TASK, 2);
    assert_eq!(said(&d, "make static"), Some(refused()));
    assert_eq!(
        said(&d, "make rust-test CRATE=rust/guard && make static"),
        Some(refused())
    );
    let one = clone("one", &[("T06", "2026-11-20T10:00:00Z")], &two_runs()[..2]);
    assert_eq!(said(&one, "make static"), None);
    let text = refusal(
        F,
        "T06",
        2,
        &["rust/guard".to_owned(), "rust/gate/crates/land".to_owned()],
    );
    for want in [
        "T06 of 451-x has run `make static` 2 times",
        "make crate-checks CRATE=\"rust/guard rust/gate/crates/land\"\n",
        "STATIC_OK=\"<reason>\"",
    ] {
        assert!(text.contains(want), "{want} in {text}");
    }
    assert!(refusal(F, "T06", 2, &[]).contains("changes no Rust crate"));
}

#[test]
fn a_landing_that_went_out_starts_the_count_again_whatever_its_exit_code() {
    for (tag, landing) in [
        ("land0", end("2026-11-20T10:03:00.000Z", &["T06"], true, 0)),
        // exit 3 with its ticks standing: the push went out, so it landed (T06's `landed`)
        ("land3", end("2026-11-20T10:03:00.000Z", &["T06"], true, 3)),
        // a batch landing whose `task` is its first id: T06 is in its `tasks`
        (
            "batch",
            end("2026-11-20T10:03:00.000Z", &["T18", "T06", "T30"], true, 0),
        ),
    ] {
        let mut lines = two_runs();
        lines.push(landing);
        let d = clone(tag, &[("T06", "2026-11-20T10:00:00Z")], &lines);
        assert_eq!(said(&d, "make static"), None, "{tag}");
        lines.extend(ran("c", "2026-11-20T10:04:00.000Z", "T06"));
        lines.extend(ran("e", "2026-11-20T10:05:00.000Z", "T06"));
        write_log(&d, &lines);
        // {tag}, two runs after
        assert_eq!(said(&d, "make static"), Some(refused()));
    }
}

#[test]
fn a_refused_landing_resets_nothing_whatever_its_exit_code() {
    for (tag, landing) in [
        (
            "refused1",
            end("2026-11-20T10:01:30.000Z", &["T06"], false, 1),
        ),
        (
            "refused0",
            end("2026-11-20T10:01:30.000Z", &["T06"], false, 0),
        ),
        // a landing of another task is no landing of this one
        ("other", end("2026-11-20T10:01:30.000Z", &["T07"], true, 0)),
    ] {
        let mut lines = two_runs();
        lines.insert(2, landing);
        let d = clone(tag, &[("T06", "2026-11-20T10:00:00Z")], &lines);
        assert_eq!(said(&d, "make static"), Some(refused()), "{tag}");
    }
}

#[test]
fn a_task_never_landed_counts_from_its_first_start_and_a_second_start_resets_nothing() {
    let mut lines = ran("old", "2026-11-20T09:59:00.000Z", "T06").to_vec();
    lines.extend(ran("a", "2026-11-20T10:01:00.000Z", "T06"));
    let d = clone("first", &[("T06", "2026-11-20T10:00:00Z")], &lines);
    // the run before the first start is not counted
    assert_eq!(said(&d, "make static"), None);
    lines.extend(ran("b", "2026-11-20T10:02:00.000Z", "T06"));
    write_log(&d, &lines);
    assert_eq!(said(&d, "make static"), Some(refused()));
    let again = clone(
        "again",
        &[
            ("T06", "2026-11-20T10:00:00Z"),
            ("T07", "2026-11-20T10:02:30Z"),
            ("T06", "2026-11-20T10:03:00Z"),
        ],
        &two_runs(),
    );
    // a second task-start resets nothing
    assert_eq!(said(&again, "make static"), Some(refused()));
    // neither a landing nor a start: every run of it counts
    assert_eq!(runs(&two_runs(), "", F, "T06", "x"), 2);
}

#[test]
fn only_the_tasks_runs_that_ran_are_counted() {
    let mut lines = ran("a", "2026-11-20T10:01:00.000Z", "T06").to_vec();
    lines.extend(ran("other", "2026-11-20T10:01:10.000Z", "T07"));
    lines.extend(
        ran("quick", "2026-11-20T10:01:20.000Z", "T06").map(|mut l| {
            l["make"] = json!("quick");
            l
        }),
    );
    // refused by another guard: a PreToolUse line and nothing after it
    lines.push(ran("refused", "2026-11-20T10:01:30.000Z", "T06")[0].clone());
    // the call being judged, were it logged with a result
    lines.extend(ran("toolu_now", "2026-11-20T10:01:40.000Z", "T06"));
    let d = clone("only", &[("T06", "2026-11-20T10:00:00Z")], &lines);
    assert_eq!(said(&d, "make static"), None);
    // a run named after another target counts; so does one whose result is a failure
    lines.extend(ran("both", "2026-11-20T10:02:00.000Z", "T06").map(|mut l| {
        l["make"] = json!("rust-test");
        l["makes"] = json!(["rust-test", "static"]);
        l
    }));
    write_log(&d, &lines);
    assert_eq!(said(&d, "make static"), Some(refused()));
    let mut failed = ran("a", "2026-11-20T10:01:00.000Z", "T06").to_vec();
    failed.extend(ran("f", "2026-11-20T10:02:00.000Z", "T06"));
    failed[3]["ev"] = json!("PostToolUseFailure");
    assert_eq!(runs(&failed, "", F, "T06", "x"), 2);
}

/// The writer's half (T14): a call running more than one target lists them all, so a `make static` after another target is counted.
#[test]
fn the_log_line_of_a_call_running_several_targets_lists_them_all() {
    let line = |cmd: &str| {
        event_log_hooks::line(
            &json!({"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": cmd}}),
            "T",
        )
    };
    let both = line("make rust-test CRATE=rust/guard && make static && make static");
    assert_eq!(both["make"], json!("rust-test"));
    assert_eq!(both["makes"], json!(["rust-test", "static"]));
    assert!(line("make static").get("makes").is_none());
    assert!(line("ls").get("makes").is_none());
}

#[test]
fn a_start_and_a_line_are_compared_as_times() {
    assert_eq!(stamp("2026-11-20T10:00:00Z"), "2026-11-20T10:00:00.000Z");
    assert_eq!(
        stamp("2026-11-20T10:00:00.500Z"),
        "2026-11-20T10:00:00.500Z"
    );
    // a run in the start's own second counts, though `.` sorts before `Z` as text
    let lines = [
        ran("a", "2026-11-20T10:00:00.000Z", "T06"),
        ran("b", "2026-11-20T10:00:00.400Z", "T06"),
    ]
    .concat();
    let starts = format!(
        "{}\n",
        json!({"feature": F, "task": "T06", "utc": "2026-11-20T10:00:00Z"})
    );
    assert_eq!(runs(&lines, &starts, F, "T06", "x"), 2);
}

#[test]
fn the_escape_passes_with_a_reason_and_is_refused_without_one() {
    let d = clone("escape", &[("T06", "2026-11-20T10:00:00Z")], &two_runs());
    assert_eq!(
        said(&d, "STATIC_OK=\"the landing gate needs it\" make static"),
        Some(Said::Escaped("the landing gate needs it".to_owned()))
    );
    assert!(
        matches!(said(&d, "make static STATIC_OK"), Some(Said::NoReason(t)) if t.contains("STATIC_OK with no reason"))
    );
}

#[test]
fn a_call_that_runs_no_static_is_not_read_and_one_with_no_task_passes_recorded() {
    let d = clone("mention", &[("T06", "2026-11-20T10:00:00Z")], &two_runs());
    for cmd in [
        "grep static Makefile",
        "echo 'make static'",
        "make quick",
        "make rust-test CRATE=rust/static",
    ] {
        assert_eq!(said(&d, cmd), None, "{cmd}");
    }
    let bare = clone("notask", &[], &two_runs());
    assert_eq!(said(&bare, "make static"), Some(Said::NoTask));
    // no clone
    assert_eq!(
        judge(
            &input(Path::new("/"), "make static"),
            Path::new("/"),
            &none,
            &guard_crate
        ),
        None
    );
}

#[test]
fn a_builder_and_the_main_session_share_the_count_by_task() {
    // one run by the main session (a fallback line) and one by T06's builder
    let mut lines = ran("main", "2026-11-20T10:01:00.000Z", "T06").to_vec();
    lines[0]["fallback"] = json!(true);
    lines.extend(
        ran("builder", "2026-11-20T10:02:00.000Z", "T06").map(|mut l| {
            l["by"] = json!("abc");
            l
        }),
    );
    let d = clone("shared", &[("T06", "2026-11-20T10:00:00Z")], &lines);
    // the main session's call
    assert_eq!(said(&d, "make static"), Some(refused()));
    std::fs::create_dir_all(d.join("s/subagents")).unwrap();
    std::fs::write(
        d.join("s/subagents/agent-abc.meta.json"),
        r#"{"description": "451 T06: the builder"}"#,
    )
    .unwrap();
    let mut builder = input(&d, "make static");
    builder["agent_id"] = json!("abc");
    builder["transcript_path"] = json!(d.join("s.jsonl").to_string_lossy());
    // the builder's call
    assert_eq!(
        judge(&builder, Path::new("/"), &none, &guard_crate),
        Some(refused())
    );
}

#[test]
fn the_crates_are_the_packages_above_the_deltas_rust_files() {
    let d = TempDir::new("guard-static-crates");
    std::fs::create_dir_all(d.join("rust/a/src")).unwrap();
    std::fs::create_dir_all(d.join("rust/b/src")).unwrap();
    std::fs::write(d.join("rust/Cargo.toml"), "[workspace]\n").unwrap();
    std::fs::write(d.join("rust/a/Cargo.toml"), "[package]\nname = \"a\"\n").unwrap();
    std::fs::write(d.join("rust/b/Cargo.toml"), "[package]\nname = \"b\"\n").unwrap();
    std::fs::write(d.join("rust/b/src/lib.rs"), "").unwrap();
    std::fs::write(d.join("docs.md"), "").unwrap();
    let paths = [
        "rust/a/src/x.rs",
        "rust/Cargo.toml",
        "docs.md",
        "rust/a/Cargo.toml",
    ];
    assert_eq!(crates_of(&d, paths.into_iter()), ["rust/a"]);
    let git = |args: &[&str]| {
        assert!(std::process::Command::new("git")
            .arg("-C")
            .arg(d.path())
            .args([
                "-c",
                "user.name=t",
                "-c",
                "user.email=t@t",
                "-c",
                "commit.gpgsign=false"
            ])
            .args(args)
            .output()
            .unwrap()
            .status
            .success());
    };
    git(&["init", "-q"]);
    git(&["add", "rust/Cargo.toml", "rust/b", "docs.md"]);
    git(&["commit", "-qm", "base"]);
    // no origin/main: the untracked files alone
    assert_eq!(delta_crates(&d), ["rust/a"]);
    git(&["update-ref", "refs/remotes/origin/main", "HEAD"]);
    std::fs::write(d.join("rust/b/src/lib.rs"), "// changed\n").unwrap();
    assert_eq!(delta_crates(&d), ["rust/a", "rust/b"]);
}

/// THE WHOLE CHAIN: the event log writes the call's own line before this guard reads, and that line is not a run; the crate-scoped
/// checks the refusal names pass every guard that reads a Bash command.
#[test]
fn through_the_chain_the_calls_own_line_is_no_run_and_the_named_checks_pass() {
    crate::shared::log::quiet();
    let d = clone(
        "chain",
        &[("T06", "2026-11-20T10:00:00Z")],
        &two_runs()[..2],
    );
    // the event log's line written first, then this guard's answer - each with no environment of the process's, which a session's
    // exported `L7R_FEATURE_DIRECTORY` or `L7R_EVENTS_DIR` would otherwise turn
    let call = |dir: &Path, cmd: &str, id: &str| {
        let mut e = Event {
            name: "PreToolUse".to_owned(),
            input: input(dir, cmd),
        };
        e.input["tool_use_id"] = json!(id);
        let stamp = event_log_hooks::now_stamp(std::time::SystemTime::now());
        event_log_hooks::append(&e.input, &stamp, Path::new("/"), &none);
        answer(&e, &Session::from_input(&e.input), Path::new("/"), &none)
    };
    // a refusal is one `Refuse` answer; its text read through the answers' printed form
    let refused_with = |answers: &[Answer]| {
        assert!(matches!(answers, [Answer::Refuse(_)]));
        format!("{answers:?}")
    };
    // a passed call, backgrounded, says nothing
    let passed = |answers: &[Answer]| answers.is_empty();
    // one run, and the call's own line, which the event log has just written
    assert!(passed(&call(&d, "make static", "toolu_x")));
    let own =
        std::fs::read_to_string(d.join(".git/l7r-events").join(format!("{F}.jsonl"))).unwrap();
    assert!(own.contains("toolu_x"));
    write_log(&d, &two_runs());
    assert!(
        refused_with(&call(&d, "make static", "toolu_y")).contains("has run `make static` 2 times")
    );
    assert!(passed(&call(
        &d,
        "STATIC_OK=\"the gate needs it now\" make static",
        "toolu_z"
    )));
    assert!(refused_with(&call(&d, "make static STATIC_OK", "toolu_w"))
        .contains("STATIC_OK with no reason"));
    let bare = clone("chain-notask", &[], &[]);
    assert!(passed(&call(&bare, "make static", "toolu_v")));
    // the hook's own entry, the process's environment read: a clone with no task start passes whatever the session exports
    let mut e = Event {
        name: "PreToolUse".to_owned(),
        input: input(&bare, "make static"),
    };
    assert_eq!(run(&mut e, &[super::GUARD]).code, 0);
    let bash = [
        crate::guards::gate_hooks::GUARD,
        crate::guards::measure_hooks::GUARD,
        crate::guards::no_poll_hooks::GUARD,
        crate::guards::make_only_hooks::GUARD,
        crate::guards::shell_check_hooks::GUARD,
    ];
    let text = refusal(
        F,
        "T06",
        2,
        &["rust/guard".to_owned(), "rust/phases".to_owned()],
    );
    let named: Vec<&str> = text
        .lines()
        .map(str::trim)
        .filter(|l| l.starts_with("make crate-checks"))
        .collect();
    assert_eq!(named.len(), 1, "one scoped command: {text}");
    for cmd in named {
        let mut e = Event {
            name: "PreToolUse".to_owned(),
            input: input(&d, cmd),
        };
        let reply = run(&mut e, &bash);
        assert_eq!(reply.code, 0, "{cmd}: {}", reply.stderr);
    }
}

/// A run of `make closing-checks` (feature 451 T55) by `task` at `t` that ran: it runs `make static`, so it is a run of it.
fn closing(id: &str, t: &str, task: &str) -> [Value; 2] {
    [
        json!({"t": t, "ev": "PreToolUse", "tool": "Bash", "id": id, "make": "closing-checks", "task": task}),
        json!({"t": t, "ev": "PostToolUse", "tool": "Bash", "id": id, "make": "closing-checks", "task": task, "bg": "b1"}),
    ]
}

#[test]
fn a_closing_checks_run_is_a_static_run_and_a_call_of_it_is_counted() {
    let lines = [
        closing("a", "2026-11-20T10:01:00.000Z", "T06"),
        ran("b", "2026-11-20T10:02:00.000Z", "T06"),
    ]
    .concat();
    let d = clone("closing", &[("T06", "2026-11-20T10:00:00Z")], &lines);
    assert_eq!(said(&d, "make static"), Some(refused()));
    assert_eq!(said(&d, "make closing-checks"), Some(refused()));
    assert_eq!(
        said(&d, "make rust-test CRATE=rust/guard && make closing-checks"),
        Some(refused())
    );
    let one = clone(
        "closing-one",
        &[("T06", "2026-11-20T10:00:00Z")],
        &closing("a", "2026-11-20T10:01:00.000Z", "T06"),
    );
    assert_eq!(said(&one, "make closing-checks"), None);
    assert_eq!(said(&one, "echo make closing-checks"), None);
    // the closing run it names is the task's own (451 T86): with no T= it would judge the whole clone
    assert!(
        refusal(F, "T06", 2, &[]).contains("`make closing-checks T=T06 F=451` in the background")
    );
}

#[test]
fn through_the_guard_a_decide_before_the_closing_checks_is_told_the_order_and_recorded() {
    crate::shared::log::quiet();
    let d = clone("order", &[("T06", "2026-11-20T10:00:00Z")], &[]);
    let path = d.join("rust/guard/src/x.rs").to_string_lossy().into_owned();
    write_log(
        &d,
        &[
            json!({"t": "2026-11-20T10:01:00.000Z", "ev": "PostToolUse", "tool": "Edit", "id": "e1", "by": "a1", "path": path}),
        ],
    );
    let mut e = Event {
        name: "PreToolUse".to_owned(),
        input: input(&d, "make decide F=451 T=T06"),
    };
    e.input["agent_id"] = json!("a1");
    let got = answer(&e, &Session::from_input(&e.input), Path::new("/"), &none);
    let told = matches!(got.as_slice(), [Answer::Notice(n)] if n.contains("rust/guard/src/x.rs"));
    assert!(told);
    // outside a clone, nothing to read: nothing said
    let mut out = Event {
        name: "PreToolUse".to_owned(),
        input: input(Path::new("/"), "make decide F=451 T=T06"),
    };
    out.input["agent_id"] = json!("a1");
    assert!(answer(
        &out,
        &Session::from_input(&out.input),
        Path::new("/"),
        &none
    )
    .is_empty());
}

/// THE TWO RULES TOGETHER (T55): a foreground closing check is refused whatever the count, and past the count both refusals are said at
/// once; each rule is escaped only by its own token.
#[test]
fn through_the_guard_a_foreground_closing_check_is_refused_beside_the_count() {
    crate::shared::log::quiet();
    let at = |v: Value| {
        let e = Event {
            name: "PreToolUse".to_owned(),
            input: v,
        };
        answer(&e, &Session::from_input(&e.input), Path::new("/"), &none)
    };
    // each refusal's text, in its printed form
    let refusals = |answers: &[Answer]| -> Vec<String> {
        answers
            .iter()
            .filter(|a| matches!(a, Answer::Refuse(_)))
            .map(|a| format!("{a:?}"))
            .collect()
    };
    let one = clone(
        "fg-one",
        &[("T06", "2026-11-20T10:00:00Z")],
        &ran("a", "2026-11-20T10:01:00.000Z", "T06"),
    );
    // under the count: the foreground refusal alone, the background call silent
    let got = refusals(&at(foreground(&one, "make static")));
    assert!(
        matches!(got.as_slice(), [t] if t.contains("run_in_background: true") && t.contains("FOREGROUND_OK"))
    );
    assert!(at(input(&one, "make static")).is_empty());
    assert!(at(foreground(
        &one,
        "FOREGROUND_OK=\"the next edit needs it\" make static"
    ))
    .is_empty());
    let bare = refusals(&at(foreground(&one, "make hooks-test FOREGROUND_OK")));
    assert!(matches!(bare.as_slice(), [t] if t.contains("FOREGROUND_OK with no reason")));
    // past the count: both refusals at once
    let past = clone("fg-past", &[("T06", "2026-11-20T10:00:00Z")], &two_runs());
    let both = refusals(&at(foreground(&past, "make closing-checks")));
    assert_eq!(both.len(), 2);
    // both name the caller's own closing run, its task and feature read from the call's filing in the clone (451 T86)
    let run = "make closing-checks T=T06 F=451";
    assert!(both.iter().all(|r| r.contains(run)), "{both:?}");
    assert!(
        both[0].contains("has run `make static` 2 times")
            && both[1].contains("run_in_background: true")
    );
    // the count's escape stands the count aside, not the foreground rule
    let counted = refusals(&at(foreground(
        &past,
        "STATIC_OK=\"the closing run of the task\" make closing-checks",
    )));
    assert!(matches!(counted.as_slice(), [t] if t.contains("run_in_background: true")));
    // the foreground rule's escape stands only it aside
    let fg_ok = refusals(&at(foreground(
        &past,
        "FOREGROUND_OK=\"the next edit needs it\" make static",
    )));
    assert!(matches!(fg_ok.as_slice(), [t] if t.contains("has run `make static` 2 times")));
}
