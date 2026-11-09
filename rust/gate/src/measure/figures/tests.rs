//! Reports, never records; a moved count fails and a timing does not.

use std::path::Path;

use serde_json::{json, Value};

use super::{cli, compare, error_name, float, py_str, refused, rerun, shlex, DELETED_ENGINE};

fn feature(root: &Path, name: &str, entries: &Value) -> std::path::PathBuf {
    let d = root.join("specs").join(name);
    std::fs::create_dir_all(&d).unwrap();
    std::fs::write(d.join("measurements.json"), entries.to_string()).unwrap();
    d
}

#[test]
fn a_figure_that_rolls_the_deleted_engine_is_listed_and_never_run() {
    let root = crate::checks::scratch("figures-engine");
    let ran = root.join("ran");
    let shown = ran.display();
    let d = feature(
        &root,
        "1-a",
        &json!({"rolled": {"command": format!("touch {shown} l7r/diagram/hamletgen/__main__.py"), "value": 1}, "module": {"command": format!("python3 -m l7r.diagram.settlement --touch {shown}"), "value": 2}, "tested": {"command": format!("touch {shown} tests/waterfields/"), "value": 3}}),
    );
    let (failures, _, skipped) = rerun(&d, &root);
    assert!(!ran.exists() && failures.is_empty() && skipped.len() == 3);
    assert!(skipped
        .iter()
        .all(|s| s.contains("runs the deleted Python hamlet engine (feature 444)")));
    for command in [
        "make figures SPEC=specs/444-work-budget-program",
        "python3 scripts/x.py --settlement-form nucleated",
        "rust/phases",
    ] {
        assert!(!DELETED_ENGINE.is_match(command).unwrap());
    }
}

#[test]
fn a_moved_count_fails_and_a_timing_is_reported() {
    let recorded = json!({"n": {"value": 560}, "t": {"value": 100.0, "varies": true}, "near": {"value": 100.0, "varies": 0.25}, "same": {"value": 1}, "gone": {"value": 1}, "zero": {"value": 0.0, "varies": true}, "text": {"value": "a", "varies": 0.5}, "off": {"value": 1, "varies": false}});
    let fresh = json!({"n": {"value": 561}, "t": {"value": 130.0, "load": 2}, "near": {"value": 120.0}, "same": {"value": 1.0}, "zero": {"value": 1.0}, "text": {"value": [1]}, "off": {"value": 2}});
    let (failures, reports) = compare(&recorded, &fresh);
    assert_eq!(failures.len(), 2);
    assert!(failures[0].contains("`n`") && failures[0].contains("560 -> 561"));
    assert!(failures[1].contains("`off`"));
    assert!(reports
        .iter()
        .any(|r| r.contains("`t`") && r.contains("band of 10%") && r.contains("load 2")));
    assert!(reports
        .iter()
        .any(|r| r.contains("`zero`") && r.contains("load ?")));
    assert!(reports.iter().any(|r| r.contains("`text`")));
    assert!(!reports.iter().any(|r| r.contains("`near`")));
}

#[test]
fn values_print_as_python_printed_them() {
    assert_eq!(py_str(&json!("a")), "a");
    assert_eq!(
        py_str(&json!([1, "b", null, true, false, {"k": 2}])),
        "[1, 'b', None, True, False, {'k': 2}]"
    );
}

#[test]
fn a_re_run_is_restored_and_a_command_that_cannot_run_is_listed() {
    let root = crate::checks::scratch("figures-restore");
    let path = root.join("specs/1-a/measurements.json");
    let script = root.join("h.sh");
    crate::write_executable(
        &script,
        &format!(
            "#!/bin/sh\nprintf '{{\"n\": {{\"value\": 999}}}}' > {}\n",
            path.display()
        ),
    );
    let failing = root.join("f.sh");
    crate::write_executable(&failing, "#!/bin/sh\necho why >&2\nexit 3\n");
    let quiet = root.join("q.sh");
    crate::write_executable(&quiet, "#!/bin/sh\nexit 4\n");
    let d = feature(
        &root,
        "1-a",
        &json!({"n": {"value": 560, "command": script.display().to_string()}, "a": {"command": failing.display().to_string()}, "b": {"command": quiet.display().to_string()}, "c": {"command": "/no/such/program x"}, "d": {"command": "say 'open"}, "e": {"command": "touch x <tree> here"}, "f": {"note": "no command"}}),
    );
    let original = std::fs::read_to_string(&path).unwrap();
    let (failures, _, skipped) = rerun(&d, &root);
    assert!(!failures.is_empty());
    assert_eq!(std::fs::read_to_string(&path).unwrap(), original);
    for expected in [
        "\n      why",
        "\n      exit 4",
        "(FileNotFoundError)",
        "(ValueError)",
        "names a <placeholder>",
    ] {
        assert!(skipped.iter().any(|s| s.contains(expected)), "{expected}");
    }
    assert!(refused("cargo test").is_none());
}

#[test]
fn words_split_as_the_shell_splits_them() {
    assert_eq!(
        shlex("a 'b c' \"d\\\"e\" f\\ g \"\"").unwrap(),
        ["a", "b c", "d\"e", "f g", ""]
    );
    assert_eq!(shlex("a\\"), None);
    assert_eq!(shlex("'open"), None);
    assert_eq!(shlex("  ").unwrap(), Vec::<String>::new());
    assert_eq!(shlex("''").unwrap(), [""]);
}

#[test]
fn a_named_spec_it_cannot_re_run_is_refused_and_every_feature_is_read() {
    let root = crate::checks::scratch("figures-cli");
    std::fs::create_dir_all(root.join("specs/240-x")).unwrap();
    let got = cli(&["specs/240-x".to_owned()], &root);
    assert!(got.code == 1 && got.stderr.contains("nothing was re-run"));
    feature(&root, "241-y", &json!({"n": {"value": 1}}));
    let all = cli(&["-v".to_owned()], &root);
    assert_eq!(all.code, 0);
    assert!(all.stdout.starts_with(
        "241-y: 0 moved count(s), 0 timing(s) outside their band, 0 command(s) not re-measured"
    ));
    let script = root.join("h.sh");
    let path = root.join("specs/242-z/measurements.json");
    crate::write_executable(
        &script,
        &format!(
            "#!/bin/sh\nprintf '{{\"n\": {{\"value\": 2}}}}' > {}\n",
            path.display()
        ),
    );
    feature(
        &root,
        "242-z",
        &json!({"n": {"value": 1, "command": script.display().to_string()}}),
    );
    let named = root.join("specs/242-z").display().to_string();
    let moved = cli(&[named], &root);
    assert!(moved.code == 1 && moved.stdout.contains("FAIL   `n`"));
}

#[test]
fn float_and_the_errors_read_as_python_named_them() {
    assert_eq!(float(&json!(true)), Some(1.0));
    assert_eq!(float(&json!("2.5")), Some(2.5));
    assert_eq!(float(&json!([1])), None);
    assert_eq!(
        error_name(&std::io::Error::from(std::io::ErrorKind::PermissionDenied)),
        "PermissionError"
    );
    assert_eq!(
        error_name(&std::io::Error::from(std::io::ErrorKind::Other)),
        "OSError"
    );
}
