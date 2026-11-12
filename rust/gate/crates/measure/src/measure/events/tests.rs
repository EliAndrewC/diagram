//! The Python's readings and arithmetic, each against the value the Python gave (the differential's figures, `diff.py`).

use std::os::unix::process::ExitStatusExt as _;
use std::path::{Path, PathBuf};
use std::process::{ExitStatus, Output};

use serde_json::{json, Value};

use super::*;

fn ev(v: &Value) -> Event {
    v.as_object().unwrap().clone()
}

/// A scratch repository with one commit.
fn repo(tag: &str) -> l7r_guard::shared::tempdir::TempDir {
    let d = crate::checks::scratch(tag);
    let run = |args: &[&str]| {
        assert!(std::process::Command::new("git")
            .arg("-C")
            .arg(&*d)
            .args(args)
            .output()
            .unwrap()
            .status
            .success());
    };
    run(&["init", "-q"]);
    run(&[
        "-c",
        "user.name=a",
        "-c",
        "user.email=a@b",
        "commit",
        "-q",
        "--allow-empty",
        "-m",
        "x",
    ]);
    d
}

#[test]
fn an_event_is_read_as_the_python_read_its_dict() {
    let e =
        ev(&json!({"t": "2026-11-01T08:00:00Z", "a": 0, "b": "x", "c": null, "d": true, "n": 5}));
    assert_eq!(get(&e, "zz"), &Value::Null);
    assert_eq!(s(&e, "zz"), "None");
    assert_eq!(s(&e, "d"), "True");
    assert_eq!(or_s(&e, "a"), "");
    assert_eq!(or_s(&e, "n"), "5");
    assert_eq!(or_text(&json!(null), "dflt"), "dflt");
    assert!(on(&e, "b") && !on(&e, "c"));
    assert!(is(&e, "b", "x") && !is(&e, "n", "5"));
    assert!(need(&e, "b").is_ok());
    assert_eq!(need(&e, "zz").unwrap_err(), "KeyError: 'zz'");
    assert_eq!(t_text(&e), "2026-11-01T08:00:00Z");
    assert_eq!(t_text(&ev(&json!({}))), "");
}

#[test]
fn a_time_reads_as_fromisoformat_reads_it() {
    assert!((ts("2026-11-01T08:00:00Z").unwrap() - 1_793_520_000.0).abs() < 1e-6);
    assert!((ts("2026-11-01T08:00:00.000123+01:00").unwrap() - 1_793_516_400.000_123).abs() < 1e-6);
    // a naive time is the machine's local one, whatever its zone
    assert!(ts("2026-11-01T08:00:00").is_ok());
    assert!(ts("2026-13-01T08:00:00Z")
        .unwrap_err()
        .starts_with("ValueError"));
    assert!(ts("0001-01-01T00:00:00").is_err());
    assert!(t_of(&ev(&json!({"t": "2026-11-01"}))).is_ok());
    assert!(t_of(&ev(&json!({}))).unwrap_err().starts_with("KeyError"));
    assert!(t_of(&ev(&json!({"t": 5})))
        .unwrap_err()
        .starts_with("AttributeError"));
    assert_eq!(
        iso_utc("2026-11-01T11:00:15-04:00").unwrap(),
        "2026-11-01T15:00:15Z"
    );
    assert!(iso_utc("x").is_err());
}

#[test]
fn figures_print_as_python_prints_them() {
    assert_eq!(fixed(0.5, 0), "0");
    assert_eq!(fixed(1.5, 0), "2");
    assert_eq!(fixed(2.5, 0), "2");
    assert_eq!(fixed(0.125, 2), "0.12");
    assert_eq!(fixed(-0.2, 0), "-0");
    assert_eq!(hm(29.0), "0 min");
    assert_eq!(hm(90.0), "2 min");
    assert_eq!(hm(150.0), "2 min");
    assert_eq!(hm(3600.0 * 2.0 + 300.0), "2 h 05 min");
    assert_eq!(hhmm(1_793_520_000.0), "08:00");
    assert_eq!(hhmm(1_793_520_059.999_999_7), "08:01");
    assert_eq!(hhmm(-0.5), "00:00");
    assert_eq!(cmp_f(1.0, 2.0), std::cmp::Ordering::Less);
    assert_eq!(cmp_f(f64::NAN, 2.0), std::cmp::Ordering::Equal);
}

#[test]
fn float_and_int_read_text_as_python_reads_it() {
    assert!((py_float_of(&json!(true)).unwrap() - 1.0).abs() < 1e-9);
    assert!((py_float_of(&json!(2.5)).unwrap() - 2.5).abs() < 1e-9);
    assert!((py_float_of(&json!(" 6_000 ")).unwrap() - 6000.0).abs() < 1e-9);
    assert!(py_float_of(&json!("abc"))
        .unwrap_err()
        .starts_with("ValueError"));
    assert!(py_float_of(&json!([1]))
        .unwrap_err()
        .starts_with("TypeError"));
    for bad in ["_1", "1_", "1__0", "."] {
        assert_eq!(py_float_text(bad), None, "{bad}");
    }
    assert_eq!(py_float_text("1."), Some(1.0));
    assert_eq!(py_int("+12").unwrap(), 12);
    assert_eq!(py_int(" -3 ").unwrap(), -3);
    assert_eq!(py_int("1_0").unwrap(), 10);
    for bad in ["", "-", "_1", "1__0", "a", "1.0", &"9".repeat(50)] {
        assert!(py_int(bad).is_err(), "{bad}");
    }
}

#[test]
fn a_tally_keeps_its_order() {
    let mut t: Tally<String> = Tally::default();
    assert!(t.is_empty());
    t.add(&"b".to_owned(), 1.0);
    t.add(&"a".to_owned(), 2.0);
    t.add(&"c".to_owned(), 1.0);
    t.add(&"b".to_owned(), 1.0);
    assert!((t.get(&"b".to_owned()) - 2.0).abs() < 1e-9);
    assert!(t.get(&"z".to_owned()).abs() < 1e-9);
    assert_eq!(t.items().len(), 3);
    let order: Vec<String> = t.most_common().into_iter().map(|(k, _)| k).collect();
    assert_eq!(order, ["b", "a", "c"]);
}

#[test]
fn git_and_files_read_as_text_mode_read_them() {
    let d = repo("measure-events-git");
    assert!(git(&d, &["rev-parse", "HEAD"]).unwrap().len() > 30);
    assert_eq!(git(&d, &["no-such-command"]).unwrap(), "");
    assert!(git_with("/nonexistent/git", &d, &[])
        .unwrap_err()
        .starts_with("FileNotFoundError"));
    let out = |stdout: &[u8], stderr: &[u8], code: i32| Output {
        status: ExitStatus::from_raw(code << 8),
        stdout: stdout.to_vec(),
        stderr: stderr.to_vec(),
    };
    assert_eq!(text_of(out(b"a\r\nb\rc", b"", 0)).unwrap(), "a\nb\nc");
    assert!(text_of(out(b"\xff", b"", 0)).is_err());
    assert!(text_of(out(b"", b"\xff", 1)).is_err());
    let f = d.join("t.txt");
    std::fs::write(&f, "a\r\nb").unwrap();
    assert_eq!(read_text(&f).unwrap(), "a\nb");
    std::fs::write(&f, b"\xff").unwrap();
    assert!(read_text(&f).unwrap_err().starts_with("UnicodeDecodeError"));
    assert!(read_text(&d.join("none"))
        .unwrap_err()
        .starts_with("OSError"));
    assert_eq!(text_if_file(&d.join("none")).unwrap(), "");
    assert_eq!(names(&d.join("none")), Vec::<String>::new());
    assert_eq!(re(r"a+").find("baa").unwrap().unwrap().as_str(), "aa");
    assert_eq!(py_path_parts("/a/./b//c/"), ["a", "b", "c"]);
}

#[test]
fn a_feature_and_its_logs_are_found() {
    let d = repo("measure-events-logs");
    std::fs::create_dir_all(d.join("specs/012-b")).unwrap();
    std::fs::create_dir_all(d.join("specs/012-a")).unwrap();
    std::fs::write(d.join("specs/0120-x"), "").unwrap();
    assert_eq!(spec_dir(&d, " 12").unwrap(), Some(d.join("specs/012-a")));
    assert_eq!(spec_dir(&d, "13").unwrap(), None);
    assert!(spec_dir(&d, "x").is_err());
    let log = |root: &Path| root.join(".git/l7r-events/012-a.jsonl");
    std::fs::create_dir_all(log(&d).parent().unwrap()).unwrap();
    std::fs::write(log(&d), "").unwrap();
    let clones = d.join("clones");
    assert_eq!(event_logs(&d, "012-a", &clones), [log(&d)]);
    for c in ["c1", "c2", "c3"] {
        std::fs::create_dir_all(clones.join(c)).unwrap();
    }
    std::fs::create_dir_all(clones.join("c1/.git/l7r-events")).unwrap();
    std::fs::write(log(&clones.join("c1")), "").unwrap();
    // a worktree sharing this clone's git dir: its log is the same file, read once
    std::fs::write(
        clones.join("c2/.git"),
        format!("gitdir: {}\n", d.join(".git").display()),
    )
    .unwrap();
    assert_eq!(
        event_logs(&d, "012-a", &clones),
        [log(&d), log(&clones.join("c1"))]
    );
}

fn put(dir: &Path, name: &str, text: &str) -> PathBuf {
    let p = dir.join(name);
    std::fs::write(&p, text).unwrap();
    p
}

#[test]
fn events_load_deduplicated_and_in_time_order() {
    let d = crate::checks::scratch("measure-events-load");
    let a = put(
        &d,
        "a.jsonl",
        concat!(
            r#"{"t": "2026-11-01T08:00:03Z", "ev": "PreToolUse", "id": "x"}"#,
            "\n",
            r#"{"t": "2026-11-01T08:00:03.5Z", "ev": "PreToolUse", "id": "x"}"#,
            "\n",
            r#"{"t": "2026-11-01T08:00:01Z", "ev": "SubagentStop", "aid": "q"}"#,
            "\n",
            r#"{"t": "2026-11-01T08:00:02Z", "ev": "SubagentStop", "aid": "q"}"#,
            "\n",
            r#"{"t": "2026-11-01T08:00:00.1Z", "ev": "Stop", "sid": "s"}"#,
            "\n",
            r#"{"t": "2026-11-01T08:00:00.9Z", "ev": "Stop", "sid": "s"}"#,
            "\n",
            r#"{"t": "2026-11-02T00:00:00Z", "ev": "Stop"}"#,
            "\n",
            r#"{"t": "", "ev": "Stop"}"#,
            "\n",
        ),
    );
    let tr = put(
        &d,
        "t.jsonl",
        r#"{"type": "user", "timestamp": "2026-11-01T07:00:00Z", "message": {"content": "hi"}}"#,
    );
    let got = load_events(&[a.clone()], &[tr], "", "2026-11-01T23").unwrap();
    let ts: Vec<&str> = got.iter().map(t_text).collect();
    assert_eq!(
        ts,
        [
            "2026-11-01T07:00:00Z",
            "2026-11-01T08:00:00.1Z",
            "2026-11-01T08:00:01Z",
            "2026-11-01T08:00:03Z"
        ]
    );
    assert_eq!(
        load_events(&[a.clone()], &[], "2026-11-01T08:00:02", "")
            .unwrap()
            .len(),
        3
    );
    let list = put(&d, "l.jsonl", "[1]\n");
    assert!(load_events(&[list], &[], "", "")
        .unwrap_err()
        .starts_with("AttributeError"));
    assert!(load_events(&[d.join("none")], &[], "", "")
        .unwrap_err()
        .starts_with("OSError"));
    let bad = put(&d, "b.jsonl", "5\n");
    assert!(load_events(&[], &[bad], "", "").is_err());
    let num = put(&d, "n.jsonl", r#"{"t": 5, "ev": "Stop"}"#);
    assert!(load_events(&[num], &[], "", "")
        .unwrap_err()
        .starts_with("TypeError"));
}
