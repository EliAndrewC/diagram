//! The pool's log read as holds, and a `Phase` line re-tasked by them (feature 451 T391, T393).

use serde_json::{json, Value};

use super::{first, holder, holds, of, retask, Hold};
use crate::measure::events::{or_s, ts, Event};

fn at(hm: &str) -> String {
    format!("2026-11-26T{hm}:00Z")
}

fn secs(hm: &str) -> f64 {
    ts(&at(hm)).unwrap()
}

fn row(hm: &str, event: &str, tree: &str, detail: &str) -> String {
    format!(
        "{}\n",
        json!({"utc": at(hm), "event": event, "tree": tree, "detail": detail})
    )
}

/// A clone at `d/<name>` whose pool log holds `rows`.
fn clone_with(d: &std::path::Path, name: &str, rows: &[String]) -> std::path::PathBuf {
    let base = d.join(name);
    std::fs::create_dir_all(base.join(".git")).unwrap();
    std::fs::write(base.join(".git/builder-pool.log"), rows.concat()).unwrap();
    base
}

fn phase(tree: &str, hm: &str, task: &str, feature: &str) -> Event {
    let mut v = json!({"ev": "Phase", "clone": format!("/c/{tree}"), "t0": at(hm), "task": task});
    if !feature.is_empty() {
        v["feature"] = json!(feature);
    }
    v.as_object().unwrap().clone()
}

#[test]
fn a_holder_s_detail_splits_on_spaces_and_commas() {
    let own = |list: &[&str]| list.iter().map(|t| (*t).to_owned()).collect::<Vec<_>>();
    assert_eq!(
        holder("451 T324,T345"),
        ("451".to_owned(), own(&["T324", "T345"]))
    );
    assert_eq!(holder("451 T309"), ("451".to_owned(), own(&["T309"])));
    assert_eq!(
        holder("451 T1, T2  T3"),
        ("451".to_owned(), own(&["T1", "T2", "T3"]))
    );
    assert_eq!(holder("free"), ("free".to_owned(), own(&[])));
    assert_eq!(holder(""), (String::new(), own(&[])));
    assert_eq!(first("451 T324,T345"), "451 T324");
    assert_eq!(first("451 T309"), "451 T309");
    assert_eq!(first("free"), "free");
    assert_eq!(first(""), "");
}

#[test]
fn the_log_is_read_as_holds_each_ended_by_its_release_or_the_next_handout() {
    let d = crate::checks::scratch("task-time-holds");
    let rows = [
        // an adopted tree that was held is a hold; one adopted free is none
        row("10:00", "adopt", "/c/a", "451 T1"),
        row("10:00", "adopt", "/c/b/", "free"),
        row("10:10", "release", "/c/a", "451 T1"),
        // a release of a tree nobody holds, a pre-warm's row, a row with no time and a line that is no record change nothing
        row("10:11", "release", "/c/b", "451 T7"),
        row("10:12", "prewarm", "/c/a", "since abc, pid 1"),
        format!(
            "{}\n",
            json!({"event": "take", "tree": "/c/a", "detail": "451 T8"})
        ),
        "not a record\n".to_owned(),
        row("10:20", "take", "/c/a", "451 T2,T3"),
        // handed on with no release between
        row("10:30", "take", "/c/a", "452 T4"),
        row("10:25", "take", "/c/b", "451 T5"),
        // a tree made for a task is that task's from its making
        row("10:40", "make", "/c/m", "451 T9"),
    ];
    let one = clone_with(&d, "one", &rows);
    // a second clone's own log, and the first named again (a worktree's base): each log read once
    let two = clone_with(&d, "two", &[row("11:00", "take", "/c/z", "451 T6")]);
    let hold = |from: &str, until: Option<&str>, tree: &str, feature: &str, tasks: &[&str]| Hold {
        from: secs(from),
        until: until.map_or(f64::INFINITY, secs),
        tree: tree.to_owned(),
        feature: feature.to_owned(),
        tasks: tasks.iter().map(|t| (*t).to_owned()).collect(),
    };
    let want = vec![
        hold("10:00", Some("10:10"), "a", "451", &["T1"]),
        hold("10:20", Some("10:30"), "a", "451", &["T2", "T3"]),
        hold("10:30", None, "a", "452", &["T4"]),
        hold("10:25", None, "b", "451", &["T5"]),
        hold("10:40", None, "m", "451", &["T9"]),
        hold("11:00", None, "z", "451", &["T6"]),
    ];
    assert_eq!(holds(&[one.clone(), two, one, d.join("none")]), want);
    // the trees a report reads: its root, and every clone beside it
    std::fs::create_dir_all(d.join("clones")).unwrap();
    assert_eq!(of(&d.join("two"), &d.join("clones")), want[5..]);
}

#[test]
fn a_phase_line_takes_its_tree_s_holder_s_first_task_and_keeps_its_own_elsewhere() {
    let d = crate::checks::scratch("task-time-retask");
    let rows = [
        row("10:00", "take", "/c/a", "451 T1"),
        row("10:10", "release", "/c/a", "451 T1"),
        row("10:20", "take", "/c/a", "451 T2,T3"),
    ];
    let held = holds(&[clone_with(&d, "one", &rows)]);
    let mut lines: Vec<Event> = vec![
        // held by T1: the stale task goes
        phase("a", "10:05", "T9", "451-x"),
        // nobody held it: its own task stands
        phase("a", "10:15", "T9", "451-x"),
        // before the log's first row, and a tree the log does not know
        phase("a", "09:00", "T9", "451-x"),
        phase("q", "10:05", "T9", "451-x"),
        // a bundle: the stale task goes to its first, its second member's own line stands
        phase("a", "10:25", "T9", "451-x"),
        phase("a", "10:26", "T3", "451-x"),
        // filed under a feature the holder was not held for, by its tag and by `home`
        phase("a", "10:27", "T9", "4510-y"),
        phase("a", "10:28", "T9", ""),
        // the holder's feature by its number alone
        phase("a", "10:29", "T9", "451"),
        // a line with no task and one with no start
        phase("a", "10:29", "", "451-x"),
        json!({"ev": "Phase", "clone": "/c/a", "task": "T9", "feature": "451-x"})
            .as_object()
            .unwrap()
            .clone(),
        // never a line that is no phase
        json!({"ev": "BgEnd", "clone": "/c/a", "t0": at("10:25"), "task": "T9", "feature": "451-x"})
            .as_object()
            .unwrap()
            .clone(),
    ];
    retask(&mut lines, &held, "900-z");
    let tasks: Vec<String> = lines.iter().map(|e| or_s(e, "task")).collect();
    assert_eq!(
        tasks,
        ["T1", "T9", "T9", "T9", "T2", "T3", "T9", "T9", "T2", "T2", "T9", "T9"]
    );
    // `home` is the feature of a line that carries none
    let mut bare = vec![phase("a", "10:25", "T9", "")];
    retask(&mut bare, &held, "451-x");
    assert_eq!(bare[0].get("task"), Some(&Value::String("T2".to_owned())));
}
