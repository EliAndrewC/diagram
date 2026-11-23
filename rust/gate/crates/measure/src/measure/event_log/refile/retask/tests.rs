//! The re-tasking (feature 451 T168) on a scratch clone: a page session's lines booked to the mark move to the task its brief names,
//! another session's lines stay, a second run changes nothing, a dry run writes nothing, an unlisted session and a missing log are
//! reported.

use std::path::Path;

use serde_json::Value;

fn args(list: &[&str]) -> Vec<String> {
    list.iter().map(|s| (*s).to_owned()).collect()
}

fn put(path: &Path, text: &str) {
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

fn tasks(path: &Path) -> Vec<String> {
    std::fs::read_to_string(path)
        .unwrap()
        .lines()
        .map(|l| match serde_json::from_str::<Value>(l) {
            Ok(v) => format!(
                "{}:{}",
                v["sid"].as_str().unwrap_or("-"),
                v["task"].as_str().unwrap_or("-")
            ),
            Err(_) => "junk".into(),
        })
        .collect()
}

fn world(d: &Path) -> std::path::PathBuf {
    let brief = d.join("specs/449-b/briefs/t330a-checks.md");
    put(&brief, "# Brief - feature 449 T330 and T333.5\n");
    put(
        &d.join(".git/page-sessions/index.txt"),
        &format!(
            "aaa {}\nnotask {}\n",
            brief.display(),
            d.join("specs/449-b/briefs/plain.md").display()
        ),
    );
    put(&d.join("specs/449-b/briefs/plain.md"), "# nothing\n");
    let log = d.join(".git/l7r-events/449-b.jsonl");
    put(
        &log,
        concat!(
            "{\"sid\":\"aaa\",\"task\":\"T312\"}\n",
            "{\"sid\":\"aaa\",\"task\":\"T328\"}\n",
            "{\"sid\":\"aaa\"}\n",
            "{\"sid\":\"aaa\",\"task\":\"T330\"}\n",
            "{\"sid\":\"bbb\",\"task\":\"T312\"}\n",
            "junk\n",
        ),
    );
    log
}

fn run(d: &Path, extra: &[&str]) -> crate::Reply {
    let events = d.join(".git/l7r-events");
    let mut a = vec![
        "--root",
        d.to_str().unwrap(),
        "--dir",
        events.to_str().unwrap(),
    ];
    a.extend_from_slice(extra);
    super::super::cli_in(&args(&a), l7r_shared::env::Rooted::with(".", &[]).reader())
}

#[test]
fn a_page_sessions_lines_move_to_its_briefs_task_and_a_second_run_changes_nothing() {
    let d = crate::checks::scratch("measure-retask");
    let log = world(&d);
    let r = run(&d, &["--retask", "aaa"]);
    assert_eq!(r.code, 0);
    assert!(r.stdout.contains(
        "aaa in 449-b: before [- 1, T312 1, T328 1, T330 1], after [T330 4], 3 re-booked"
    ));
    assert_eq!(
        tasks(&log),
        ["aaa:T330", "aaa:T330", "aaa:T330", "aaa:T330", "bbb:T312", "junk"]
    );
    let again = run(&d, &["--retask", "aaa"]);
    assert!(again.stdout.contains("0 re-booked"));
    assert_eq!(tasks(&log).len(), 6);
}

#[test]
fn a_dry_run_writes_nothing() {
    let d = crate::checks::scratch("measure-retask");
    let log = world(&d);
    let before = std::fs::read(&log).unwrap();
    let r = run(&d, &["--retask", "aaa", "--dry-run"]);
    assert!(r.stdout.contains("3 re-booked (dry run: nothing written)"));
    assert_eq!(std::fs::read(&log).unwrap(), before);
}

#[test]
fn an_unlisted_session_or_one_whose_brief_names_no_task_is_left() {
    let d = crate::checks::scratch("measure-retask");
    let log = world(&d);
    let before = std::fs::read(&log).unwrap();
    let r = run(&d, &["--retask", "zzz", "--retask", "notask"]);
    assert_eq!(r.code, 0);
    assert_eq!(
        r.stdout
            .matches("no page-session brief naming a task")
            .count(),
        2
    );
    assert_eq!(std::fs::read(&log).unwrap(), before);
}

#[test]
fn a_missing_log_fails() {
    let d = crate::checks::scratch("measure-retask-fail");
    world(&d);
    std::fs::remove_file(d.join(".git/l7r-events/449-b.jsonl")).unwrap();
    let r = run(&d, &["--retask", "aaa"]);
    assert_eq!(r.code, 1);
    assert!(r.stderr.starts_with("retask: "));
}
