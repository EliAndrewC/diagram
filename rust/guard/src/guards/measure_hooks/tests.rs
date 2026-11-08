//! The decider against a temporary tree with its run log and a fake `gatecost.py` (`sh`); the verdicts against today's are the
//! suite's (`tests/hooks/test-measure-hooks.sh`, replayed through the shim).

use std::path::{Path, PathBuf};
use std::sync::Once;

use serde_json::{json, Value};

use super::{greedy_command, judge, last_gate, parse_utc, tree_of, Seams};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;

static LOG: Once = Once::new();

/// A tree with a `.git`, its streak file and seams; the clock at 1,000,000 s.
fn tree(tag: &str) -> (PathBuf, Seams) {
    LOG.call_once(|| {
        std::env::set_var(
            "GUARD_LOG_DIR",
            std::env::temp_dir().join(format!("l7r-guard-measure-log-{}", std::process::id())),
        );
    });
    let d = std::env::temp_dir().join(format!("l7r-guard-measure-{tag}-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&d);
    std::fs::create_dir_all(d.join(".git")).unwrap();
    std::fs::create_dir_all(d.join("scripts/measure")).unwrap();
    std::fs::write(d.join("scripts/measure/gatecost.py"), "echo 70\n").unwrap();
    let seams = Seams {
        streak: d.join("s.measures"),
        budget: 1,
        cadence_s: 10_800,
        now: 1_000_000,
        tree: d.clone(),
        python: "sh".to_owned(),
    };
    (d, seams)
}

fn bash(cmd: &str, dir: &Path) -> Event {
    Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash", "cwd": dir.to_string_lossy(), "tool_input": {"command": cmd}}),
    }
}

fn run(e: &Event, s: &Seams) -> Vec<Answer> {
    judge(e, &Session::from_input(&json!({})), s)
}

/// A run record of `target` ending at `end` with `result`.
fn record(d: &Path, name: &str, target: &str, start: &str, seconds: &Value, result: &str) {
    std::fs::create_dir_all(d.join("dev/run-log/2026-11")).unwrap();
    let r = json!({"target": target, "utc": start, "seconds": seconds, "result": result});
    std::fs::write(d.join("dev/run-log/2026-11").join(name), r.to_string()).unwrap();
}

#[test]
fn the_second_expensive_measurement_is_refused_once() {
    let (root, s) = tree("streak");
    assert!(
        matches!(&run(&bash("make test-full", &root), &s)[..], [Answer::Notice(n)] if n.contains("median of 70 s"))
    );
    assert!(
        matches!(&run(&bash("make done FULL=1", &root), &s)[..], [Answer::Refuse(r)] if r.contains("second EXPENSIVE"))
    );
    assert!(matches!(
        &run(&bash("make -C x test-full", &root), &s)[..],
        [Answer::Notice(_)]
    ));
    let wide = Seams { budget: 3, ..s };
    assert!(run(&bash("make test-full", &root), &wide).is_empty());
}

#[test]
fn the_reminder_carries_no_median_when_the_tool_answers_none() {
    let (root, s) = tree("nocost");
    std::fs::write(root.join("scripts/measure/gatecost.py"), "exit 1\n").unwrap();
    assert!(
        matches!(&run(&bash("make test-full", &root), &s)[..], [Answer::Notice(n)] if !n.contains("median"))
    );
}

#[test]
fn an_engine_edit_and_a_commit_reset_the_streak_and_a_test_edit_does_not() {
    let (root, s) = tree("reset");
    let edit = |p: &str| Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Edit", "tool_input": {"file_path": p}}),
    };
    std::fs::write(&s.streak, "1").unwrap();
    assert!(
        run(&edit("/r/tests/l7r/test_x.py"), &s).is_empty()
            && std::fs::read_to_string(&s.streak).unwrap() == "1"
    );
    assert!(
        run(&edit("/r/l7r/diagram/x.py"), &s).is_empty()
            && std::fs::read_to_string(&s.streak).unwrap().is_empty()
    );
    std::fs::write(&s.streak, "1").unwrap();
    assert!(
        run(&bash("git commit -q -F -", &root), &s).is_empty()
            && std::fs::read_to_string(&s.streak).unwrap().is_empty()
    );
    std::fs::write(&s.streak, "1").unwrap();
    let described = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash", "tool_input": {"command": "ls", "description": "before the git commit"}}),
    };
    assert!(
        run(&described, &s).is_empty() && std::fs::read_to_string(&s.streak).unwrap().is_empty()
    );
}

#[test]
fn measure_ok_stands_aside_with_a_reason_and_refuses_without() {
    let (root, s) = tree("escape");
    std::fs::write(&s.streak, "1").unwrap();
    assert!(run(
        &bash("make test-full  # MEASURE_OK: the record needs it", &root),
        &s
    )
    .is_empty());
    assert!(
        matches!(&run(&bash("make test-full  # MEASURE_OK", &root), &s)[..], [Answer::Refuse(r)] if r.contains("MEASURE_OK with no reason"))
    );
}

#[test]
fn a_gate_soon_after_a_green_one_is_refused_once_a_green_run() {
    let (root, s) = tree("cadence");
    record(
        &root,
        "a.json",
        "done",
        "1970-01-12T13:00:00Z",
        &json!(60),
        "green",
    );
    record(
        &root,
        "b.json",
        "quick",
        "1970-01-12T13:40:00Z",
        &json!(60),
        "green",
    );
    std::fs::write(root.join("dev/run-log/2026-11/bad.json"), "not json").unwrap();
    record(&root, "c.json", "done", "not a time", &json!(1), "green");
    let refused = run(&bash("make done", &root), &s);
    assert!(matches!(&refused[..], [Answer::Refuse(r)] if r.contains("GREEN 45 min ago")));
    assert!(run(&bash("make done", &root), &s).is_empty());
    assert!(run(&bash("make -n done", &root), &s).is_empty());
}

#[test]
fn a_red_gate_an_old_one_and_no_record_let_the_gate_run() {
    let (root, s) = tree("cadence-not");
    assert!(run(&bash("make done", &root), &s).is_empty());
    record(
        &root,
        "r.json",
        "test-full",
        "1970-01-12T13:00:00Z",
        &json!("60"),
        "red",
    );
    assert!(run(&bash("make done", &root), &s).is_empty());
    record(
        &root,
        "r.json",
        "done",
        "1970-01-12T13:00:00Z",
        &json!(60),
        "green",
    );
    std::fs::write(root.join(".git/gate-preflight-red"), "").unwrap();
    assert!(run(&bash("make done", &root), &s).is_empty());
    let late = Seams {
        now: 1_000_000 + 20_000,
        ..tree("cadence-late").1
    };
    record(
        &late.tree,
        "o.json",
        "done",
        "1970-01-12T13:00:00Z",
        &json!(60),
        "green",
    );
    assert!(run(&bash("make done", &late.tree), &late).is_empty());
}

#[test]
fn perf_outside_a_timing_pair_is_reminded() {
    let (root, s) = tree("perf");
    assert!(
        matches!(&run(&bash("make perf", &root), &s)[..], [Answer::Notice(n)] if n.contains("timing pair"))
    );
    assert!(matches!(
        &run(&bash("make perf SEED=4", &root), &s)[..],
        [Answer::Notice(_)]
    ));
    assert!(run(&bash("make perf LABEL=449-start", &root), &s).is_empty());
    assert!(run(&bash("make perf LABEL=449-end", &root), &s).is_empty());
    assert!(run(&bash("ls", &root), &s).is_empty());
    assert!(run(&bash("", &root), &s).is_empty());
    let no_cwd = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash", "tool_input": {"command": "make done"}}),
    };
    assert!(run(&no_cwd, &s).len() <= 1);
}

#[test]
fn status_prints_the_count() {
    let (_d, s) = tree("status");
    std::fs::write(&s.streak, "1").unwrap();
    let status = Event {
        name: "status".to_owned(),
        input: json!({}),
    };
    assert!(
        matches!(&run(&status, &s)[..], [Answer::Print(p)] if p == "measurements_since_reset=1 budget=1")
    );
}

#[test]
fn the_command_reads_as_the_shells_sed_and_the_tree_as_git_does() {
    assert_eq!(
        greedy_command(&json!({"tool_input": {"command": "ls", "description": "x"}})),
        "ls\",\"description\":\"x"
    );
    assert_eq!(greedy_command(&json!({"tool_input": {"cmd": "ls"}})), "");
    assert_eq!(greedy_command(&json!({"command": 3})), "");
    assert_eq!(parse_utc("1970-01-01T00:00:01Z"), Some(1));
    assert_eq!(parse_utc("2000-03-01T00:00:00Z"), Some(951_868_800));
    assert_eq!(parse_utc("1970-01-01 00:00:01"), None);
    let (d, _s) = tree("worktree");
    let wt = d.join("wt");
    std::fs::create_dir_all(&wt).unwrap();
    std::fs::write(wt.join(".git"), "gitdir: ../.git/worktrees/wt\n").unwrap();
    assert_eq!(tree_of(&wt), (wt.clone(), wt.join("../.git/worktrees/wt")));
    std::fs::write(wt.join(".git"), "gitdir: /abs/g\n").unwrap();
    assert_eq!(tree_of(&wt).1, PathBuf::from("/abs/g"));
    assert_eq!(tree_of(Path::new("/")).0, PathBuf::from("/"));
    assert!(last_gate(Path::new("/nonexistent")).is_none());
    assert!(
        super::decide(
            &Event {
                name: "status".to_owned(),
                input: json!({})
            },
            &Session::from_input(&json!({}))
        )
        .len()
            == 1
    );
}
