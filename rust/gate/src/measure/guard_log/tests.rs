//! `make guard-log` lists the firings an audit starts from.

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::cli;

fn log(rows: &[Value]) -> PathBuf {
    let dir = crate::checks::scratch("guard-log");
    for (n, r) in rows.iter().enumerate() {
        std::fs::write(dir.join(format!("{n}.json")), r.to_string()).unwrap();
    }
    std::fs::write(dir.join("broken.json"), "x").unwrap();
    dir
}

fn rows() -> Vec<Value> {
    vec![
        json!({"utc": "2026-09-05T10:00:00.1", "guard": "old", "event": "blocked", "detail": "cat > /tmp/x"}),
        json!({"utc": "2026-09-07T10:00:00", "guard": "main-tree", "event": "blocked", "rule": "named-main", "session_name": "diagram-hooks", "cwd": "/diagram/.clones/diagram-hooks", "command": "git push"}),
        json!({"utc": "2026-09-07T11:00:00", "guard": "main-tree", "event": "rewrote", "rule": "moved-to-clone", "session_name": "x", "cwd": "/diagram", "tool": "Bash", "command": "ls\n# second line", "context": {"verdict": "rewrite"}}),
        json!({"utc": "2026-09-08T10:00:00", "guard": "batching", "event": "reminded", "session": "0123456789abcdef", "command": "y"}),
    ]
}

fn ask(dir: &Path, words: &[&str]) -> crate::Reply {
    let mut owned: Vec<String> = vec!["--dir".to_owned(), dir.display().to_string()];
    owned.extend(words.iter().map(|s| (*s).to_owned()));
    cli(&owned, Path::new("/nonexistent"))
}

fn last(r: &crate::Reply) -> String {
    r.stdout.trim().lines().last().unwrap().to_owned()
}

#[test]
fn lists_every_firing_with_name_cwd_and_the_first_line() {
    let got = ask(&log(&rows()), &[]);
    let lines: Vec<&str> = got.stdout.lines().collect();
    assert_eq!(*lines.last().unwrap(), "4 firing(s)");
    assert!(lines[0].contains("unknown") && lines[0].contains("cat > /tmp/x"));
    assert!(
        lines[1].contains("diagram-hooks")
            && lines[1].contains("blocked/named-main")
            && lines[1].contains("/diagram/.clones/diagram-hooks")
    );
    assert!(lines[2].contains("rewrote/moved-to-clone") && !lines[2].contains("# second line"));
    assert!(lines[3].contains("01234567") && !lines[3].contains("0123456789abcdef"));
}

#[test]
fn filters_by_guard_since_and_event() {
    let d = log(&rows());
    assert_eq!(last(&ask(&d, &["--guard", "batching"])), "1 firing(s)");
    assert_eq!(last(&ask(&d, &["--since", "2026-09-07"])), "3 firing(s)");
    assert_eq!(last(&ask(&d, &["--event", "rewrote"])), "1 firing(s)");
    assert_eq!(
        last(&ask(
            &d,
            &[
                "--guard",
                "main-tree",
                "--event",
                "blocked",
                "--since",
                "2026-09-07"
            ]
        )),
        "1 firing(s)"
    );
    assert_eq!(
        ask(&d, &["--guard", "nothing"]).stdout.trim(),
        "(no matching firings)"
    );
    assert_eq!(ask(&d, &["--event", "nope"]).code, 2);
}

#[test]
fn full_form_prints_the_whole_command_and_the_context() {
    let out = ask(&log(&rows()), &["--full"]).stdout;
    assert!(
        out.contains("# second line")
            && out.contains("\"verdict\":\"rewrite\"")
            && out.contains("cwd: /diagram")
            && out.contains("tool: -")
    );
    let none = cli(&[], Path::new("/nonexistent"));
    assert_eq!(none.stdout, "(no matching firings)\n");
}

#[test]
fn a_blank_session_is_unknown_and_a_number_reads_as_text() {
    let d = log(&[
        json!({"utc": 1, "guard": "g", "event": "blocked", "session": "nosession", "command": "c"}),
    ]);
    let out = ask(&d, &[]).stdout;
    assert!(out.contains("unknown"));
}
