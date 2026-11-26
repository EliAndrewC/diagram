//! 451 T101: a landing the mark's task holds lands beside it where each of its tasks is started, its plan section CLEAR and its files
//! its own; the push is told so; each reason it cannot is said.

use l7r_gate_core::ci::fixtures::put;

use super::super::tests::{fx, has, Fx, NOTE};
use super::{open_tasks, started_tasks};
use l7r_shared::speckit::touch::{edit_lines, last_changes};

const HELD: &str =
    "T2 two  <- the active task (make task-start), open: land it with make land F=449 T=T2\n";

/// A file committed on the delta at a time far ahead, so an edit line of 2099-01-01 is in it and one of 2099-12-01 after it.
fn committed(fx: &Fx, rel: &str) {
    put(&fx.root, rel, "x\n");
    for args in [&["add", "-A"][..], &["commit", "-qm", rel]] {
        let ok = std::process::Command::new("git")
            .args(args)
            .current_dir(&fx.root)
            .env("GIT_COMMITTER_DATE", "2099-06-01T00:00:00Z")
            .status()
            .unwrap()
            .success();
        assert!(ok);
    }
}

/// A line of the feature's event log: `task` wrote `rel` at `t`, by an edit or (`bash`) a shell write.
fn wrote(fx: &Fx, task: &str, rel: &str, t: &str, bash: bool) {
    let path = format!("{}/{rel}", fx.root.display());
    let line = if bash {
        format!(
            r#"{{"t":"{t}","ev":"PostToolUse","tool":"Bash","cat":"other tool","writes":["{path}"],"task":"{task}"}}"#
        )
    } else {
        format!(
            r#"{{"t":"{t}","ev":"PostToolUse","tool":"Edit","cat":"edit","path":"{path}","task":"{task}"}}"#
        )
    };
    let log = fx.root.join(".git/l7r-events/449-x.jsonl");
    let old = std::fs::read_to_string(&log).unwrap_or_default();
    put(
        &fx.root,
        ".git/l7r-events/449-x.jsonl",
        &format!("{old}{line}\n"),
    );
}

fn started(fx: &Fx, tasks: &[&str]) {
    use std::fmt::Write as _;
    let mut rows = String::new();
    for t in tasks {
        writeln!(
            rows,
            "{{\"feature\": \"449-x\", \"task\": \"{t}\", \"utc\": \"2026-11-21T00:00:00Z\"}}"
        )
        .unwrap();
    }
    put(&fx.root, ".git/task-starts.jsonl", &rows);
}

fn land(fx: &Fx) -> Result<i32, String> {
    fx.land
        .land(&fx.root.join("specs/449-x"), &["T1".to_owned()], NOTE)
}

/// The bug T101 fixes: T1, started, CLEAR and its files its own, was refused "held by" T2, the task started after it; now it lands, and
/// the push is told the ruling (`L7R_LAND_READY`), since the push asks the mark's hold again.
#[test]
fn a_ready_task_lands_beside_the_mark_s_task_and_the_push_is_told() {
    let fx = fx("ready-beside");
    *fx.answers.holding.borrow_mut() = HELD.to_owned();
    started(&fx, &["T1", "T2"]);
    committed(&fx, "src/t1.rs");
    wrote(&fx, "T1", "src/t1.rs", "2099-01-01T00:00:00Z", false);
    // T2's edit of T1's file after the delta's commit of it, and T2's edit of the sectioned plan.md: neither is in T1's delta
    wrote(&fx, "T2", "src/t1.rs", "2099-12-01T00:00:00Z", false);
    wrote(
        &fx,
        "T2",
        "specs/449-x/plan.md",
        "2099-01-01T00:00:00Z",
        false,
    );
    fx.answer(
        "sync-with-main.sh done",
        "sh",
        "printf 'READY=%s\\n' \"$L7R_LAND_READY\" >> \"$STUB_DIR/log\"\n",
    );
    assert_eq!(land(&fx), Ok(0), "{:?}", fx.said());
    let out = fx.said().0;
    has(&out, "land: T1 ready beside the active task");
    let log = fx.log();
    assert!(log.contains("READY=T1\n"), "{log}");
    let decided = format!("l7r-gate.sh plan decided {} 449-x T1", fx.root.display());
    assert!(log.contains(&decided), "{log}");
}

/// Each reason a task cannot land beside the mark's is said with the hold: never started, its section not CLEAR, a delta file holding
/// another open task's edit (by an edit or a shell write) - and the push is told nothing where the hold never fired.
#[test]
fn a_task_not_ready_stays_held_and_says_why() {
    let fx = fx("ready-not");
    *fx.answers.holding.borrow_mut() = HELD.to_owned();
    started(&fx, &["T2"]);
    committed(&fx, "src/t2.rs");
    committed(&fx, "src/t2b.rs");
    wrote(&fx, "T2", "src/t2.rs", "2099-01-01T00:00:00Z", false);
    wrote(&fx, "T2", "src/t2b.rs", "2099-01-01T00:00:00Z", true);
    // a write outside the clone names none of its files
    let log = fx.root.join(".git/l7r-events/449-x.jsonl");
    let old = std::fs::read_to_string(&log).unwrap();
    let foreign = r#"{"t":"2099-01-01T00:00:00Z","ev":"PostToolUse","cat":"edit","path":"/elsewhere/src/t2.rs","task":"T2"}"#;
    put(
        &fx.root,
        ".git/l7r-events/449-x.jsonl",
        &format!("{old}{foreign}\n"),
    );
    let decided = format!("l7r-gate.sh plan decided {} 449-x T1", fx.root.display());
    fx.answer(&decided, "rc", "1");
    fx.answer(
        &decided,
        "out",
        "449-x T1: its plan section carries no current CLEAR verdict\n",
    );
    assert_eq!(land(&fx), Ok(2));
    let err = fx.said().1;
    assert!(err.contains("held by T2 two"), "{err}");
    assert!(err.contains("T1 cannot land beside it (451 T101)"), "{err}");
    has(
        &err,
        "T1 was never started in this clone (make task-start F=449 T=T1)",
    );
    has(
        &err,
        "449-x T1: its plan section carries no current CLEAR verdict",
    );
    assert!(err.contains("src/t2.rs in the delta holds T2's edit of 2099-01-01T00:00:00Z, not theirs - land them together (make land F=449 T=\"T1 T2\")"), "{err}");
    has(&err, "src/t2b.rs in the delta holds T2's edit");
    // no hold, no ruling: the push is told nothing
    let quiet = super::super::tests::fx("ready-quiet");
    started(&quiet, &["T1"]);
    assert!(quiet
        .land
        .not_ready(&quiet.root.join("specs/449-x"), &["T1".to_owned()])
        .unwrap()
        .is_empty());
    quiet
        .land
        .export_ready(&quiet.root.join("specs/449-x"), &["T1".to_owned()])
        .unwrap();
    assert!(!quiet
        .land
        .exported
        .borrow()
        .iter()
        .any(|(k, _)| k == "L7R_LAND_READY"));
}

/// A task started while the gate ran moves the mark: the push asks the ruling again where the first pass made none.
#[test]
fn the_push_asks_the_ruling_again_where_the_mark_moved_while_the_gate_ran() {
    let fx = fx("ready-moved");
    started(&fx, &["T1"]);
    let d = fx.root.join("specs/449-x");
    let tasks = ["T1".to_owned()];
    *fx.answers.holding.borrow_mut() = HELD.to_owned();
    fx.land.export_ready(&d, &tasks).unwrap();
    assert!(fx
        .land
        .exported
        .borrow()
        .iter()
        .any(|(k, v)| k == "L7R_LAND_READY" && v == "T1"));
    // ...and a task not ready is not named
    let not = super::super::tests::fx("ready-moved-not");
    *not.answers.holding.borrow_mut() = HELD.to_owned();
    not.land
        .export_ready(&not.root.join("specs/449-x"), &tasks)
        .unwrap();
    assert!(!not
        .land
        .exported
        .borrow()
        .iter()
        .any(|(k, _)| k == "L7R_LAND_READY"));
}

/// The readings: the starts of one feature, the open task lines, each file's newest commit, and the event lines a ruling reads -
/// a fallback line, one with no task, an unreadable time, another feature's log and a line that is no JSON passed over.
#[test]
fn the_readings_take_what_the_ruling_needs_and_pass_over_the_rest() {
    let dir = l7r_gate_core::ci::fixtures::scratch("ready-readings");
    put(&dir, "starts.jsonl", "{\"feature\": \"449-x\", \"task\": \"T1\"}\nnot json\n{\"feature\": \"450-y\", \"task\": \"T2\"}\n{\"feature\": \"449-x\"}\n");
    assert_eq!(
        started_tasks(&dir.join("starts.jsonl"), "449-x")
            .into_iter()
            .collect::<Vec<_>>(),
        ["T1"]
    );
    assert!(started_tasks(&dir.join("none.jsonl"), "449-x").is_empty());
    let open =
        open_tasks("- [ ] T1 one\n- [x] T2 two\n  - [ ] T3 under\n- [ ] GM review\n- [ ] \n");
    assert_eq!(open.into_iter().collect::<Vec<_>>(), ["T1", "T3"]);
    let changes = last_changes("@20\na.rs\nb.rs\n\n@10\na.rs\n@bad\nc.rs\n");
    assert_eq!(
        (changes["a.rs"], changes["b.rs"], changes["c.rs"]),
        (20, 20, 0)
    );
    let lines = [
        r#"{"t":"2099-01-01T00:00:00Z","ev":"PostToolUse","cat":"edit","path":"/c/a.rs","task":"T1"}"#,
        r#"{"t":"2099-01-01T00:00:00Z","ev":"PostToolUse","cat":"edit","path":"/c/b.rs","task":"T1","fallback":true}"#,
        r#"{"t":"2099-01-01T00:00:00Z","ev":"PostToolUse","cat":"edit","path":"/c/c.rs"}"#,
        r#"{"t":"soon","ev":"PostToolUse","cat":"edit","path":"/c/d.rs","task":"T1"}"#,
        r#"{"t":"2099","ev":"PostToolUse","cat":"edit" not json"#,
        r#"{"t":"2099-01-01T00:00:00Z","ev":"PreToolUse","cat":"edit","path":"/c/e.rs","task":"T1"}"#,
        r#"{"t":"2099-01-01T00:00:00Z","ev":"PostToolUse","cat":"other tool","writes":["/c/f.rs",3],"task":"T2"}"#,
    ];
    put(&dir, "events/449-x.jsonl", &(lines.join("\n") + "\n"));
    put(
        &dir,
        "events/449-x-2.jsonl",
        &(lines[0].replace("a.rs", "g.rs") + "\n"),
    );
    put(
        &dir,
        "events/450-y.jsonl",
        &(lines[0].replace("a.rs", "h.rs") + "\n"),
    );
    put(
        &dir,
        "events/449-x.txt",
        &(lines[0].replace("a.rs", "i.rs") + "\n"),
    );
    let got: Vec<(String, String)> = edit_lines(&dir.join("events"), "449-x")
        .into_iter()
        .map(|(task, _, path)| (task, path))
        .collect();
    let want = [("T1", "/c/g.rs"), ("T1", "/c/a.rs"), ("T2", "/c/f.rs")];
    let want: Vec<(String, String)> = want
        .iter()
        .map(|(a, b)| ((*a).to_owned(), (*b).to_owned()))
        .collect();
    assert_eq!(got, want);
    assert!(edit_lines(&dir.join("no-events"), "449-x").is_empty());
}
