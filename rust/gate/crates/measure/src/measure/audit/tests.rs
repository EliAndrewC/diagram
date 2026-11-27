//! `make audit`'s three ported sections over scratch records: each line as the one-liners printed it, and their raises.

use std::path::Path;

use l7r_gate_core::ci::fixtures::{git, put, scratch};

use super::{cli, guard_dir, pad, percent, Counter};

fn run(args: &[&str], cwd: &Path, guards: &Path) -> crate::Reply {
    cli(
        &args.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>(),
        cwd,
        guards,
        &cwd.join("no-clones"),
    )
}

#[test]
fn the_gate_runs_and_the_bypasses_print_as_the_recipe_printed_them() {
    let dir = scratch("audit-runs");
    let none = dir.join("none");
    let empty = run(&["runs"], &dir, &none);
    assert_eq!(empty.code, 0);
    assert_eq!(
        empty.stdout,
        "\n\x1b[1mGate runs\x1b[0m (dev/run-log/)\n  (none yet)\n\n\x1b[1mBypasses\x1b[0m (dev/bypass-log/) - a FULL run is only justified at the END of a feature\n  (none yet)\n\n"
    );
    put(
        &dir,
        "dev/run-log/2026-11/b.json",
        r#"{"utc": "2026-11-02", "scope": "done", "seconds": 12, "result": "green", "commit": "abc", "mode": "full", "selected": 40}"#,
    );
    put(
        &dir,
        "dev/run-log/a.json",
        r#"{"utc": "2026-11-01", "scope": "quick", "seconds": 1.5, "result": "red", "commit": "def"}"#,
    );
    put(&dir, "dev/run-log/.hidden.json", "not json");
    put(&dir, "dev/run-log/notes.txt", "x");
    put(
        &dir,
        "dev/bypass-log/2026-11/r.json",
        r#"{"utc": "2026-11-03", "guard": "claims-gate", "why": "a reason"}"#,
    );
    put(
        &dir,
        "dev/bypass-log/2026-11/s.json",
        r#"{"utc": "2026-11-04", "outcome": "", "what": "", "reason": ""}"#,
    );
    let said = run(&["runs"], &dir, &none);
    assert_eq!(said.code, 0);
    assert!(said
        .stdout
        .contains("  2026-11-01  quick      1.5s  red                    def  \n"));
    assert!(said
        .stdout
        .contains("  2026-11-02  done        12s  green                  abc  full 40\n"));
    assert!(said.stdout.contains("  2 runs: done=1, quick=1\n"));
    assert!(said.stdout.contains("  2026-11-03  claims-gate a reason\n"));
    assert!(said.stdout.contains("  2026-11-04  ?          \n"));
}

#[test]
fn a_record_the_recipe_raised_on_fails_the_section() {
    let dir = scratch("audit-runs-bad");
    let none = dir.join("none");
    put(&dir, "dev/run-log/a.json", "{");
    assert_eq!(run(&["runs"], &dir, &none).code, 1);
    for (body, why) in [
        (
            r#"{"utc": "1", "seconds": 1, "result": "r", "commit": "c"}"#,
            "KeyError: 'scope'",
        ),
        (
            r#"{"utc": "1", "scope": null, "seconds": 1, "result": "r", "commit": "c"}"#,
            "NoneType.__format__",
        ),
        (
            r#"{"utc": "1", "scope": "s", "seconds": 1, "result": "r", "commit": "c", "mode": 3}"#,
            "unsupported operand",
        ),
        (r"[1]", "AttributeError"),
        (r#"{"utc": 5}"#, "KeyError: 'scope'"),
    ] {
        put(&dir, "dev/run-log/a.json", body);
        let said = run(&["runs"], &dir, &none);
        assert_eq!(said.code, 1);
        assert!(said.stderr.contains(why), "{why}");
    }
    put(
        &dir,
        "dev/run-log/a.json",
        r#"{"utc": "1", "scope": "s", "seconds": true, "result": "r", "commit": "c"}"#,
    );
    put(&dir, "dev/bypass-log/b.json", r#"{"utc": "1", "why": 5}"#);
    let said = run(&["runs"], &dir, &none);
    assert!(said.stdout.contains("     1s"));
    assert!(said.stderr.contains("'int' object is not subscriptable"));
    std::fs::write(dir.join("dev/bypass-log/b.json"), [0xff]).unwrap();
    assert_eq!(run(&["runs"], &dir, &none).code, 1);
}

#[test]
fn the_guard_firings_are_counted_by_guard_and_rule() {
    let dir = scratch("audit-guards");
    let log = dir.join("guard-log");
    let empty = run(&["guards"], &dir, &log);
    assert_eq!(
        empty.stdout,
        "\x1b[1mGuard firings\x1b[0m (~/.claude/guard-log/) - what each guard did: blocked, rewrote, reminded, escaped\n  (none recorded yet)\n  0 entries\n\n"
    );
    put(
        &log,
        "1.json",
        r#"{"utc": "2026-11-01T10:00:00Z", "guard": "make-only", "event": "blocked", "rule": "bare-cargo", "detail": ""}"#,
    );
    put(
        &log,
        "2.json",
        r#"{"utc": "2026-11-02T11:00:00Z", "guard": "make-only", "event": "escaped", "detail": "a reason given"}"#,
    );
    put(
        &log,
        "3.json",
        r#"{"utc": "2026-11-03T12:00:00Z", "guard": "make-only", "event": "blocked", "rule": "bare-cargo", "detail": null}"#,
    );
    put(
        &log,
        "4.json",
        r#"{"utc": "2026-11-04T13:00:00Z", "guard": "readme", "event": "reminded", "detail": ""}"#,
    );
    put(
        &log,
        "5.json",
        r#"{"utc": "2026-11-05T14:00:00Z", "guard": "pair", "event": "escaped", "detail": ""}"#,
    );
    put(&log, "empty.json", "");
    put(&log, "x.txt", "not a record");
    let said = run(&["guards"], &dir, &log);
    assert_eq!(said.code, 0);
    assert!(said
        .stdout
        .contains("  make-only    blocked=2, escaped=1   escape rate 33%\n"));
    assert!(said
        .stdout
        .contains("               by rule: bare-cargo=2, escaped=1\n"));
    assert!(said.stdout.contains("  readme       reminded=1\n"));
    assert!(said
        .stdout
        .contains("  pair         escaped=1   escape rate 100%\n"));
    assert!(said.stdout.contains("\x1b[1m  escapes taken, with what the session said\x1b[0m\n    11-05T14:00  pair         (no reason recorded)\n    11-02T11:00  make-only    a reason given\n"));
    assert!(said
        .stdout
        .ends_with("  5 entries, 2026-11-01T10:00:00Z to 2026-11-05T14:00:00Z\n\n"));
    put(
        &log,
        "6.json",
        r#"{"utc": "2026-11-06", "guard": "g", "event": "escaped"}"#,
    );
    assert!(run(&["guards"], &dir, &log)
        .stderr
        .contains("KeyError: 'detail'"));
    put(
        &log,
        "6.json",
        r#"{"utc": 6, "guard": "g", "event": "blocked"}"#,
    );
    assert_eq!(run(&["guards"], &dir, &log).code, 1);
    put(
        &log,
        "6.json",
        r#"{"guard": "g", "event": "blocked", "rule": "r"}"#,
    );
    assert!(run(&["guards"], &dir, &log)
        .stderr
        .contains("KeyError: 'utc'"));
}

#[test]
fn the_feature_numbers_are_read_from_main_s_mirror() {
    let dir = scratch("audit-claims");
    let clone = dir.join(".clones/one");
    std::fs::create_dir_all(&clone).unwrap();
    git(&clone, &["init", "-q"]);
    let none = dir.join("none");
    let path = dir.join(".specify/feature-numbers.jsonl").canonicalize();
    assert!(path.is_err());
    let empty = run(&["claims"], &clone, &none);
    assert!(empty
        .stdout
        .contains("(none yet - every claim made by make claim lands here)\n\n"));
    put(&dir, ".specify/feature-numbers.jsonl", "{\"utc\": \"2026-11-01T00:00:00Z\", \"number\": 449, \"slug\": \"rust-codebase\", \"clone\": \"one\"}\n\n{}\n");
    let said = run(&["claims"], &clone, &none);
    assert!(said
        .stdout
        .contains("  2026-11-01T00:00:00Z  449  rust-codebase                            one\n"));
    assert!(said
        .stdout
        .contains("  ?                       0  ?                                        ?\n"));
    assert!(said.stdout.contains("  2 claims recorded\n"));
    // a clone outside `.clones` reads its own; outside any repository, `.specify` under the working directory
    git(&dir, &["init", "-q"]);
    assert!(run(&["claims"], &dir, &none)
        .stdout
        .contains("2 claims recorded"));
    let bare = scratch("audit-claims-none");
    assert!(run(&["claims"], &bare, &none)
        .stdout
        .contains("(.specify/feature-numbers.jsonl - make claim"));
    put(&dir, ".specify/feature-numbers.jsonl", "[1]\n");
    assert_eq!(run(&["claims"], &dir, &none).code, 1);
    put(&dir, ".specify/feature-numbers.jsonl", "{\n");
    assert_eq!(run(&["claims"], &dir, &none).code, 1);
    std::fs::write(dir.join(".specify/feature-numbers.jsonl"), [0xff]).unwrap();
    assert_eq!(run(&["claims"], &dir, &none).code, 1);
}

#[test]
fn the_helpers_format_as_python_formats() {
    assert_eq!(run(&["nope"], Path::new("."), Path::new(".")).code, 2);
    assert_eq!(
        pad(&serde_json::json!("ab"), true, 4),
        Ok("ab  ".to_owned())
    );
    assert_eq!(pad(&serde_json::json!(7), false, 3), Ok("  7".to_owned()));
    assert_eq!(pad(&serde_json::json!(false), true, 2), Ok("0 ".to_owned()));
    assert!(pad(&serde_json::json!([1]), true, 2)
        .unwrap_err()
        .contains("list"));
    assert!(pad(&serde_json::json!({}), true, 2)
        .unwrap_err()
        .contains("dict"));
    assert_eq!(percent(0.125), "12%");
    assert_eq!(percent(0.375), "38%");
    let mut c = Counter::default();
    for k in ["b", "a", "b", "c"] {
        c.add(serde_json::json!(k));
    }
    assert_eq!(
        c.most_common(2),
        vec![(serde_json::json!("b"), 2), (serde_json::json!("a"), 1)]
    );
    assert_eq!(c.get("z"), 0);
    let home = Path::new("/home/u");
    assert_eq!(guard_dir(None, home), home.join(".claude/guard-log/"));
    assert_eq!(guard_dir(Some(""), home), Path::new("/"));
    assert_eq!(guard_dir(Some("/var/g"), home), Path::new("/var/g/"));
    assert_eq!(guard_dir(Some("~"), home), home.join(""));
    assert_eq!(super::type_name(&serde_json::json!(1.5)), "float");
    assert_eq!(super::type_name(&serde_json::json!("s")), "str");
    assert!(!super::truthy(&serde_json::json!(0)) && super::truthy(&serde_json::json!([1])));
    assert!(!super::truthy(&serde_json::Value::Null) && super::truthy(&serde_json::json!(true)));
    assert!(super::truthy(&serde_json::json!({"a": 1})) && !super::truthy(&serde_json::json!("")));
    assert_eq!(super::type_name(&serde_json::json!(true)), "bool");
    assert_eq!(
        super::py_sorted(vec![(serde_json::json!([1]), 1)], false),
        Ok(vec![1])
    );
    assert!(super::py_sorted(
        vec![(serde_json::json!(1), 1), (serde_json::json!("a"), 2)],
        false
    )
    .unwrap_err()
    .contains("'int' and 'str'"));
    assert!(super::py_sorted(
        vec![(serde_json::json!(null), 1), (serde_json::json!(null), 2)],
        false
    )
    .is_err());
    assert_eq!(
        super::py_sorted(
            vec![
                (serde_json::json!(true), 1),
                (serde_json::json!(0.5), 2),
                (serde_json::json!(false), 3)
            ],
            true
        ),
        Ok(vec![1, 2, 3])
    );
    assert!(super::io(std::io::Error::other("gone")).contains("gone"));
    assert!(super::field(&serde_json::json!(1), "x")
        .unwrap_err()
        .contains("int indices"));
}

/// Feature 451 T270: a `PLAN_REVIEW_OK` record is classed by its `held` list (451 T262's field), never by its reason - every record
/// here carries the one standing reason that 451 T261 read as a cause.
#[test]
fn a_plan_gate_escape_is_classed_by_what_its_record_says_was_held() {
    let dir = scratch("audit-held");
    let none = dir.join("none");
    let record = |name: &str, target: &str, held: Option<&str>| {
        let held = held.map_or_else(String::new, |h| format!(r#", "held": {h}"#));
        put(
            &dir,
            &format!("dev/bypass-log/2026-11/{name}.json"),
            &format!(
                r#"{{"utc": "2026-11-26T0{name}", "target": "{target}", "why": "unstarted tasks' template stubs"{held}}}"#
            ),
        );
    };
    // another escape's record, and one whose target is no text, are no plan-gate escape: no class lines for them alone
    record("0", "plan-gate decide-defer", None);
    put(
        &dir,
        "dev/bypass-log/2026-11/00.json",
        r#"{"utc": "2026-11-26T00", "target": 7, "why": "x"}"#,
    );
    assert!(!run(&["runs"], &dir, &none).stdout.contains("held"));
    // written before 451 T262, or a `held` that is no list: nothing to class by
    record("1", "plan-gate push", None);
    record("2", "plan-gate tick 451-x", Some(r#""blocks""#));
    // honored where the gate listed no feature
    record("3", "plan-gate push", Some("[]"));
    // a feature held with no block listed: its plan or its review record missing
    record(
        "4",
        "plan-gate tick 451-x",
        Some(
            r#"[{"feature": "specs/451-x", "rule": "plan-missing", "blocks": []}, {"feature": "specs/9-y", "rule": "plan-review-missing"}]"#,
        ),
    );
    // blocks held at a push (two records) and at a tick (three), one row of several carrying them
    let blocks = r#"[{"feature": "specs/9-y", "rule": "plan-review-missing", "blocks": []}, {"feature": "specs/451-x", "rule": "plan-review-stale", "blocks": ["T1 (why)"]}]"#;
    record("5", "plan-gate push", Some(blocks));
    record("6", "plan-gate push", Some(blocks));
    record("7", "plan-gate tick 451-x", Some(blocks));
    record("8", "plan-gate tick 451-x", Some(blocks));
    record("9", "plan-gate tick 9-y", Some(blocks));
    let said = run(&["runs"], &dir, &none);
    assert_eq!(said.code, 0);
    let tail = said
        .stdout
        .split_once("  PLAN_REVIEW_OK escapes")
        .map_or("", |(_, t)| t);
    assert_eq!(
        tail,
        concat!(
            " by what the plan gate held (each record's `held` list, never its reason) - 9 records\n",
            "       2  held not recorded (a record before 451 T262)\n",
            "       1  nothing held\n",
            "       1  a plan or its review record missing, no block listed\n",
            "       2  at a push: blocks held, of ticked tasks or outside every task\n",
            "       3  at a tick: blocks held, of the asked task, of tasks ticked before it or outside every task\n",
            "\n"
        )
    );
}

/// 451 T444's fixture log: each row's file name, guard, event, rule and detail (a JSON value) - each class left out and each look-alike.
const FIXTURE_ROWS: [(&str, &str, &str, &str, &str); 15] = [
    (
        "c1",
        "checks",
        "escaped",
        "check-closed",
        r#""nothing to close here""#,
    ),
    (
        "c2",
        "checks",
        "escaped",
        "check-closed",
        r#""nothing to close here""#,
    ),
    (
        "c3",
        "checks",
        "escaped",
        "check-closed",
        r#""nothing to close here: the session's own""#,
    ),
    (
        "p1",
        "plan-gate",
        "blocked",
        "plan-review-stale",
        r#""449-x: 1 block(s) of plan.md changed""#,
    ),
    (
        "p2",
        "plan-gate",
        "escaped",
        "plan-review-ok",
        r#""449-x: 451 T41 reviewed CLEAR""#,
    ),
    (
        "p3",
        "plan-gate",
        "blocked",
        "plan-review-missing",
        r#""specs/600-x""#,
    ),
    (
        "p4",
        "plan-gate",
        "escaped",
        "plan-review-ok",
        r#""451-real: T1 reviewed CLEAR""#,
    ),
    (
        "p5",
        "plan-gate",
        "blocked",
        "plan-review-stale",
        r#""451-real: 1 block(s)""#,
    ),
    (
        "p6",
        "plan-gate",
        "escaped",
        "plan-review-ok",
        r#""3-way split reviewed CLEAR""#,
    ),
    ("p7", "plan-gate", "blocked", "plan-missing", "null"),
    ("p8", "plan-gate", "blocked", "plan-missing", "7"),
    (
        "p9",
        "plan-gate",
        "escaped",
        "plan-review-ok",
        r#""the reason: a colon in it""#,
    ),
    (
        "t1",
        "task-add",
        "blocked",
        "quick-red",
        r#""9001-x T03: sh q.sh: failed (exit 1)""#,
    ),
    (
        "t2",
        "task-add",
        "blocked",
        "quick-red",
        r#""451-real T37: l7r-gate check spec-lint --delta .: failed (exit 1)""#,
    ),
    (
        "s1",
        "sync-with-main",
        "blocked",
        "closing-owes",
        r#""closing""#,
    ),
];

/// Feature 451 T444: the test fixtures' rows already on the live guard log (451 T143 stopped new ones) are left out where content
/// tells them apart, and the count says how many; their look-alikes - a real reason, a filed feature, a refusal - stay counted.
#[test]
fn the_test_fixtures_rows_are_left_out_and_counted() {
    let dir = scratch("audit-fixtures");
    let log = dir.join("guard-log");
    for (name, guard, event, rule, detail) in FIXTURE_ROWS {
        let text = format!(
            r#"{{"utc": "2026-11-22T10:00:00Z", "guard": "{guard}", "event": "{event}", "rule": "{rule}", "detail": {detail}}}"#
        );
        put(&log, &format!("{name}.json"), &text);
    }
    // with no specs/ directory nothing names a feature that is missing, so only the check-closed rows are left out
    let bare = run(&["guards"], &dir, &log);
    assert!(bare
        .stdout
        .contains("  plan-gate    blocked=5, escaped=4   escape rate 44%\n"));
    assert!(bare.stdout.contains("  left out, as test fixtures' rows (451 T444, T468): 2 - checks check-closed \"nothing to close here\" 2\n"));
    put(&dir, "specs/451-real/spec.md", "");
    let said = run(&["guards"], &dir, &log);
    assert_eq!(said.code, 0);
    assert!(said
        .stdout
        .contains("  checks       escaped=1   escape rate 100%\n"));
    assert!(said
        .stdout
        .contains("  plan-gate    blocked=3, escaped=3   escape rate 50%\n"));
    assert!(said
        .stdout
        .contains("  task-add     blocked=1   escape rate 0%\n"));
    assert!(said
        .stdout
        .contains("  sync-with-main blocked=1   escape rate unknown; since the event logs began 0 told, 20 short of a rate\n"));
    assert!(said.stdout.contains("  9 entries, "));
    assert!(said.stdout.contains(concat!(
        "  left out, as test fixtures' rows (451 T444, T468): 6 - checks check-closed \"nothing to close here\" 2; ",
        "plan-gate naming a feature with no specs/ directory 3 (449-x 2, 600-x 1); ",
        "task-add naming a feature with no specs/ directory 1 (9001-x 1)\n",
        "  cannot tell (451 T468): sync-with-main closing-owes 1 with no event log's Phase line to read - ",
    )));
}

/// T468's event logs: the repository's at `dir`, and a clone's under `<dir>/clones`, which holds `dir` again by a link and a file.
fn closing_events(dir: &Path) -> std::path::PathBuf {
    let phase = |step: &str, krate: &str, t0: &str, t1: &str| {
        format!(
            r#"{{"ev":"Phase","src":"rust","step":"{step}","crates":["rust/gate/crates/{krate}"],"t0":"{t0}","t1":"{t1}","code":0}}"#
        )
    };
    let events = [
        phase(
            "build",
            "guard",
            "2026-11-20T11:57:18.961Z",
            "2026-11-20T11:57:19.000Z",
        ),
        phase(
            "test",
            "cohort",
            "2026-11-22T09:59:59.500Z",
            "2026-11-22T10:00:01.900Z",
        ),
        phase(
            "cover-run",
            "cohort",
            "2026-11-23T08:59:50.000Z",
            "2026-11-23T09:00:00.400Z",
        ),
        phase(
            "build",
            "cohort",
            "2026-11-22T10:59:59.000Z",
            "2026-11-22T11:00:01.000Z",
        ),
        phase(
            "test",
            "guard",
            "2026-11-25T08:59:00.000Z",
            "2026-11-25T09:01:00.000Z",
        ),
        phase(
            "test",
            "cohort",
            "2026-11-27T06:59:00.000Z",
            "2026-11-27T07:01:00.000Z",
        ),
        r#"{"ev":"Phase","step":"test","t0":"2026-11-01T00:00:00.000Z"}"#.to_owned(),
        r#"{"ev":"Phase", not json"#.to_owned(),
        r#"{"t":"2026-11-02T00:00:00.000Z","ev":"Stop"}"#.to_owned(),
    ];
    put(
        dir,
        ".git/l7r-events/451-x.jsonl",
        &(events.join("\n") + "\n"),
    );
    put(
        dir,
        ".git/l7r-events/451-x.jsonl.pre-t168",
        &phase(
            "test",
            "cohort",
            "2026-11-19T07:59:00.000Z",
            "2026-11-19T08:01:00.000Z",
        ),
    );
    let clones = dir.join("clones");
    let other = clones.join("other");
    std::fs::create_dir_all(&other).unwrap();
    git(&other, &["init", "-q"]);
    put(
        &other,
        ".git/l7r-events/452-y.jsonl",
        &phase(
            "test",
            "cohort",
            "2026-11-24T09:00:00.000Z",
            "2026-11-24T09:00:06.000Z",
        ),
    );
    std::os::unix::fs::symlink(dir, clones.join("same")).unwrap();
    put(&clones, "a-file", "");
    clones
}

/// T468's world: a repository whose event log and a clone's hold cohort test runs, and a guard log of `closing-owes` rows.
fn closing_world() -> (
    l7r_shared::tempdir::TempDir,
    std::path::PathBuf,
    std::path::PathBuf,
) {
    let dir = scratch("audit-closing");
    git(&dir, &["init", "-q"]);
    let log = dir.join("guard-log");
    let row = |name: &str, utc: &str, event: &str, rule: &str| {
        put(
            &log,
            &format!("{name}.json"),
            &format!(
                r#"{{"utc": "{utc}", "guard": "sync-with-main", "event": "{event}", "rule": "{rule}", "detail": "closing"}}"#
            ),
        );
    };
    row("a-early", "2026-11-19T08:00:00Z", "blocked", "closing-owes");
    row(
        "b-in-test",
        "2026-11-22T10:00:01Z",
        "blocked",
        "closing-owes",
    );
    row(
        "c-in-cover",
        "2026-11-23T09:00:00Z",
        "blocked",
        "closing-owes",
    );
    row(
        "d-in-clone",
        "2026-11-24T09:00:05Z",
        "blocked",
        "closing-owes",
    );
    row("e-real", "2026-11-22T11:00:00Z", "blocked", "closing-owes");
    row(
        "f-other-crate",
        "2026-11-25T09:00:00Z",
        "blocked",
        "closing-owes",
    );
    row(
        "g-after-t143",
        "2026-11-27T07:00:00Z",
        "blocked",
        "closing-owes",
    );
    row("h-escape", "2026-11-22T12:00:00Z", "escaped", "close-ok");
    let clones = closing_events(&dir);
    (dir, log, clones)
}

/// The cohort push tests' `closing-owes` rows, byte for byte a real refusal's, are told by the event logs' cohort test runs (451
/// T468): a row inside one is left out, a row after 451 T143's landing is counted wherever it stands, a row before the logs' first
/// `Phase` line cannot be told and makes the guard's escape rate unknown, and with no event log at all every such row is untold.
#[test]
fn the_cohort_tests_closing_rows_are_told_by_the_event_logs_test_runs() {
    let (dir, log, clones) = closing_world();
    let said = cli(&["guards".to_owned()], &dir, &log, &clones);
    assert_eq!(said.code, 0);
    assert!(said
        .stdout
        .contains("  sync-with-main blocked=4, escaped=1   escape rate unknown; since the event logs began 4 told, 16 short of a rate\n"));
    assert!(said.stdout.contains("  left out, as test fixtures' rows (451 T444, T468): 3 - sync-with-main closing-owes inside a cohort crate's test run 3\n"));
    assert!(said.stdout.contains("  cannot tell (451 T468): sync-with-main closing-owes 1 before the event logs' first Phase line, 2026-11-20T11:57:18Z, with no test run to stand in - a fixture's row is a real refusal's byte for byte, so its escape rate is unknown\n"));
    std::fs::remove_file(log.join("a-early.json")).unwrap();
    let told = cli(&["guards".to_owned()], &dir, &log, &clones);
    assert!(told
        .stdout
        .contains("  sync-with-main blocked=3, escaped=1   escape rate 25%\n"));
    assert!(!told.stdout.contains("cannot tell"));
    // no event log: every closing-owes row before T143's landing is untold, none left out
    let bare = scratch("audit-closing-bare");
    let none = cli(&["guards".to_owned()], &bare, &log, &bare.join("none"));
    assert!(none
        .stdout
        .contains("  sync-with-main blocked=6, escaped=1   escape rate unknown; since the event logs began 0 told, 20 short of a rate\n"));
    assert!(none.stdout.contains("  cannot tell (451 T468): sync-with-main closing-owes 5 with no event log's Phase line to read - "));
    assert!(!none.stdout.contains("left out"));
}

/// 451 T480: while untold rows keep the guard's rate unknown, the rows told since the event logs began give a rate of their own
/// once there are `TOLD_ENOUGH` of them; a told row is one the audit keeps, at or after the first `Phase` line.
#[test]
fn the_told_rows_give_a_rate_beside_unknown_once_there_are_enough() {
    let (dir, log, clones) = closing_world();
    for i in 0..16 {
        let event = if i < 4 { "escaped" } else { "blocked" };
        put(
            &log,
            &format!("told-{i}.json"),
            &format!(
                r#"{{"utc": "2026-11-26T10:00:{i:02}Z", "guard": "sync-with-main", "event": "{event}", "rule": "closing-owes", "detail": "closing"}}"#
            ),
        );
    }
    let said = cli(&["guards".to_owned()], &dir, &log, &clones);
    assert!(said
        .stdout
        .contains("  sync-with-main blocked=16, escaped=5   escape rate unknown; since the event logs began 25% (20 told)\n"));
}
