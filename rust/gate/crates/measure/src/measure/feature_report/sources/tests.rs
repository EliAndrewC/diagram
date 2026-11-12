//! The report's git and run-log readers over the scratch feature, and the raises the Python's readers had.

use std::collections::HashSet;

use serde_json::json;

use super::super::tests::{git, put, tree};
use super::*;

#[test]
fn the_commits_their_lines_and_their_gates_are_read() {
    let d = tree("measure-sources-git");
    let cs = commits(&d, "901", "", "").unwrap();
    assert_eq!(cs.len(), 2);
    assert_eq!(cs[0].1, "2026-11-01T15:00:15Z");
    assert_eq!(commits(&d, "901", "2026-11-01T09", "").unwrap().len(), 1);
    assert_eq!(commits(&d, "901", "", "2026-11-01T09").unwrap().len(), 1);
    let shas: Vec<&str> = cs.iter().map(|c| c.0.as_str()).collect();
    assert_eq!(diff_lines(&d, &shas).unwrap(), 3);
    let set: HashSet<&str> = shas.iter().copied().collect();
    assert_eq!(gate_sequence(&d, &set, "", "").unwrap().len(), 3);
    assert_eq!(
        gate_sequence(&d, &set, "2026-11-01T08:17", "2026-11-01T08:17:30").unwrap(),
        [("2026-11-01T08:17:00Z".to_owned(), "red".to_owned())]
    );
    let g = gates(&d, &set, "", "").unwrap();
    assert_eq!(g.items().len(), 3);
    assert_eq!(plan_blocks(&d, "901-s", &set).unwrap(), 1);
    // what the run log skips, and what it raises on
    put(&d, "dev/run-log/bad.json", "not json");
    std::fs::write(d.join("dev/run-log/latin.json"), b"\xff").unwrap();
    std::fs::create_dir_all(d.join("dev/run-log/dir.json")).unwrap();
    put(
        &d,
        "dev/run-log/n.json",
        &json!({"target": "done", "commit": null, "utc": "2026-11-01T08:00:00Z", "result": null})
            .to_string(),
    );
    std::os::unix::fs::symlink(d.join("dev/run-log/m"), d.join("dev/run-log/linked")).unwrap();
    assert_eq!(gates(&d, &set, "", "").unwrap().items().len(), 3);
    put(&d, "dev/run-log/list.json", "[1]");
    assert!(gates(&d, &set, "", "")
        .unwrap_err()
        .starts_with("AttributeError"));
    // a subject holding a line separator splits the Python's line, which then has no fields to unpack
    git(
        &d,
        "2026-11-01T12:00:00Z",
        &[
            "commit",
            "-q",
            "--allow-empty",
            "-m",
            "Feature 901 a\u{2028}b",
        ],
    );
    assert!(commits(&d, "901", "", "")
        .unwrap_err()
        .starts_with("ValueError"));
    assert!(commits(&d, "x", "", "").is_err());
}

#[test]
fn the_spec_tasks_and_starts_are_read() {
    let d = tree("measure-sources-tasks");
    let rounds = spec_rounds("- Round 1 (x): CHANGES REQUIRED - a\n- spec-fidelity-verify, amendment 3 round 2 (y): NOT FAITHFUL\n- other\n");
    assert_eq!(rounds.items().len(), 2);
    assert_eq!(tasks_done(&d.join("specs/901-s")).unwrap(), (1, 2));
    assert_eq!(tasks_done(&d.join("specs/none")).unwrap(), (0, 0));
    std::fs::write(d.join("specs/901-s/tasks.md"), b"\xff").unwrap();
    assert!(tasks_done(&d.join("specs/901-s")).is_err());
    assert_eq!(task_ticks(&d, "901-s").unwrap().len(), 1);
    put(&d, "specs/901-s/tasks.md", "- [x] T01\n- [x] T02\n");
    git(&d, "2026-11-01T12:00:00Z", &["commit", "-qam", "901 T02"]);
    assert_eq!(task_ticks(&d, "901-s").unwrap().len(), 2);
    let starts = task_starts(&d, "901-s").unwrap();
    assert_eq!(
        starts.iter().map(|s| s.0.as_str()).collect::<Vec<_>>(),
        ["T01", "T02", "T03"]
    );
    put(
        &d,
        ".git/task-starts.jsonl",
        &format!(
            "not json\r\n{}\r\n{}\n{}\n",
            json!({"feature": "901-s", "task": "T01", "utc": "2026-11-01T08:00:00Z"}),
            json!({"feature": "901-s", "task": "T01", "utc": "2026-11-01T09:00:00Z"}),
            json!({"feature": "other", "task": "T01"})
        ),
    );
    assert_eq!(task_starts(&d, "901-s").unwrap().len(), 1);
    for bad in [
        "[1]",
        r#"{"feature": "901-s", "task": "T1"}"#,
        r#"{"feature": "901-s", "task": "T1", "utc": "x"}"#,
    ] {
        put(&d, ".git/task-starts.jsonl", bad);
        assert!(task_starts(&d, "901-s").is_err(), "{bad}");
    }
    let bare = crate::checks::scratch("measure-sources-bare");
    assert_eq!(task_starts(&bare, "901-s").unwrap(), Vec::new());
}
