//! `make audit`'s three ported sections over scratch records: each line as the one-liners printed it, and their raises.

use std::path::Path;

use l7r_gate_core::ci::fixtures::{git, put, scratch};

use super::{cli, guard_dir, pad, percent, Counter};

fn run(args: &[&str], cwd: &Path, guards: &Path) -> crate::Reply {
    cli(
        &args.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>(),
        cwd,
        guards,
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
