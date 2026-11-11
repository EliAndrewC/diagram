//! The guard on a stand-in `/proc` (`tests/hooks/test-finished-run-hooks.sh`, replayed through the shim, is the verdict).

use std::path::{Path, PathBuf};

use serde_json::json;

use super::runs::Procs;
use super::{cli, decide, human, judge, report, with, Ctx};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;

/// A clone with a `.git`, and an empty stand-in process table.
pub(super) struct World {
    pub root: crate::shared::tempdir::TempDir,
    pub clone: PathBuf,
    pub proc: PathBuf,
}

pub(super) fn world(tag: &str) -> World {
    crate::shared::log::quiet();
    let root = crate::shared::tempdir::TempDir::new(&format!("guard-finished-{tag}"));
    let clone = root.join("clone");
    std::fs::create_dir_all(clone.join(".git")).unwrap();
    std::fs::create_dir_all(root.join("proc")).unwrap();
    std::fs::create_dir_all(root.join("tree/scripts/hooks/lib")).unwrap();
    std::fs::write(
        root.join("tree/scripts/hooks/lib/writer-alive.sh"),
        "exit 1\n",
    )
    .unwrap();
    let clone = clone.canonicalize().unwrap();
    World {
        proc: root.join("proc"),
        clone,
        root,
    }
}

impl World {
    /// A process: its name, parent, cwd, argv and stdout.
    pub(super) fn add(
        &self,
        pid: u32,
        comm: &str,
        parent: u32,
        cwd: &Path,
        argv: &[&str],
        stdout: Option<&Path>,
    ) {
        let d = self.proc.join(pid.to_string());
        std::fs::create_dir_all(d.join("fd")).unwrap();
        std::fs::write(d.join("comm"), format!("{comm}\n")).unwrap();
        std::fs::write(d.join("stat"), format!("{pid} ({comm}) S {parent} 0 0")).unwrap();
        std::fs::write(d.join("cmdline"), argv.join("\0") + "\0").unwrap();
        std::os::unix::fs::symlink(cwd, d.join("cwd")).unwrap();
        if let Some(out) = stdout {
            std::os::unix::fs::symlink(out, d.join("fd/1")).unwrap();
        }
    }

    pub(super) fn procs(&self) -> Procs {
        Procs {
            root: self.proc.clone(),
            mine: 99_999,
        }
    }

    fn ctx(&self) -> Ctx {
        Ctx {
            procs: self.procs(),
            tree: self.root.join("tree"),
            now: 1_000_000_000,
            pwd: "/".to_owned(),
        }
    }

    fn run(&self, name: &str) -> Vec<Answer> {
        let input = json!({"session_id": "t", "cwd": self.clone.to_string_lossy()});
        let s = Session::from_input(&input);
        judge(
            &Event {
                name: name.to_owned(),
                input,
            },
            &s,
            &self.ctx(),
        )
    }

    fn record(&self, name: &str, utc: &str, result: &str) {
        let log = self.clone.join("dev/run-log/2026-11");
        std::fs::create_dir_all(&log).unwrap();
        std::fs::write(
            log.join(name),
            json!({"utc": utc, "target": "done", "seconds": 47, "result": result}).to_string(),
        )
        .unwrap();
    }
}

fn printed(got: &[Answer]) -> String {
    match got {
        [Answer::Print(t)] => t.clone(),
        other => format!("{other:?}"),
    }
}

fn refused(got: &[Answer]) -> String {
    match got {
        [Answer::Refuse(t)] => t.clone(),
        other => format!("{other:?}"),
    }
}

#[test]
fn a_duration_reads_as_a_person_would_say_it() {
    assert_eq!(
        (printed(&[]), refused(&[])),
        ("[]".to_owned(), "[]".to_owned())
    );
    assert_eq!(
        (human(30), human(600), human(14_400)),
        ("30s".to_owned(), "10 min".to_owned(), "4 h".to_owned())
    );
}

#[test]
fn a_finished_run_is_surfaced_once_with_its_age() {
    let w = world("report");
    assert!(w.run("UserPromptSubmit").is_empty());
    w.record("a.json", "2001-09-09T01:46:40Z", "failed");
    std::fs::write(w.clone.join("dev/run-log/2026-11/note.txt"), "").unwrap();
    assert!(report(&w.clone, false, 1_000_000_060)
        .unwrap()
        .contains("finished 60s ago and it is failed (47s) - NOT still running."));
    let told = printed(&w.run("Stop"));
    assert!(told.contains("failed") && told.contains("do not end a turn"));
    assert!(w.run("UserPromptSubmit").is_empty());
    std::thread::sleep(std::time::Duration::from_millis(5));
    w.record("b.json", "not a time", "green");
    let green = printed(&w.run("UserPromptSubmit"));
    assert!(
        green.contains("finished 0s ago: green (47s). It is NOT still running.")
            && !green.contains("do not end")
    );
}

#[test]
fn outside_a_working_tree_and_with_no_cwd_it_says_nothing() {
    let w = world("outside");
    let input = json!({"cwd": "/nonexistent"});
    let s = Session::from_input(&input);
    assert!(judge(
        &Event {
            name: "Stop".to_owned(),
            input
        },
        &s,
        &w.ctx()
    )
    .is_empty());
    let e = Event {
        name: "UserPromptSubmit".to_owned(),
        input: json!({"cwd": "/"}),
    };
    assert!(decide(&e, &Session::from_input(&e.input)).is_empty());
    let none = Event {
        name: "UserPromptSubmit".to_owned(),
        input: json!({}),
    };
    assert!(judge(&none, &Session::from_input(&none.input), &w.ctx()).is_empty());
}

#[test]
fn an_unwatched_run_refuses_the_turn_once_per_root() {
    let w = world("refuse");
    let log = w.root.join("run.log");
    std::fs::write(&log, "").unwrap();
    w.add(
        100,
        "make",
        1,
        &w.clone,
        &["make", "-j2", "X=1", "sleeper"],
        Some(&log),
    );
    w.add(101, "make", 100, &w.clone, &["make", "child"], Some(&log));
    let first = refused(&w.run("Stop"));
    assert!(
        first.contains("IS STILL GOING, DETACHED")
            && first.contains(&format!(
                "pid 100 `make sleeper`, output in {}",
                log.display()
            ))
            && first.contains("GATE FAILED")
    );
    assert!(!first.contains("pid 101") && w.run("Stop").is_empty());
    std::fs::write(w.clone.join(".git/live-run.told"), "7,8").unwrap();
    assert!(!refused(&w.run("Stop")).is_empty());
}

#[test]
fn a_verify_gate_is_told_to_wait_with_make() {
    let w = world("verify");
    let log = w.root.join("verify-gate-1.log");
    std::fs::write(&log, "").unwrap();
    w.add(100, "gmake", 1, &w.clone, &["make"], Some(&log));
    let text = refused(&w.run("Stop"));
    assert!(text.contains("pid 100 `make make`") && text.contains("make verify-wait"));
}

#[test]
fn a_run_the_harness_tracks_or_a_waiter_watches_lets_the_turn_close() {
    let w = world("tracked");
    let out = w.root.join("task.output");
    std::fs::write(&out, "").unwrap();
    w.add(50, "claude", 1, Path::new("/"), &["claude"], None);
    w.add(60, "bash", 50, Path::new("/"), &["bash"], Some(&out));
    w.add(100, "make", 60, &w.clone, &["make", "done"], None);
    let got = printed(&w.run("Stop"));
    assert!(
        got.contains("the harness will wake this session")
            && got.contains(&out.to_string_lossy().into_owned())
    );
    let direct = world("direct");
    direct.add(50, "claude", 1, Path::new("/"), &["claude"], None);
    direct.add(100, "make", 50, &direct.clone, &["make", "done"], None);
    assert!(printed(&direct.run("Stop")).contains("(its output: the harness)"));
    let w2 = world("watched");
    let log = w2.root.join("watched.log");
    std::fs::write(&log, "").unwrap();
    w2.add(100, "make", 1, &w2.clone, &["make", "done"], Some(&log));
    let loop_cmd = format!("until grep -q X {}; do sleep 3; done", log.display());
    w2.add(
        200,
        "bash",
        1,
        Path::new("/"),
        &["bash", "-c", &loop_cmd],
        None,
    );
    let said = printed(&w2.run("Stop"));
    assert!(
        said.contains("a waiter (pid 200) is watching") && said.contains("will wake this session")
    );
}

#[test]
fn a_waiter_on_a_dead_producer_is_reported_and_the_marker_cleared() {
    let w = world("stale");
    let dead = w.root.join("dead.log");
    std::fs::write(&dead, "").unwrap();
    std::fs::write(w.clone.join(".git/live-run.told"), "9").unwrap();
    let cmd = format!("until grep -q X {}; do sleep 3; done", dead.display());
    w.add(300, "bash", 1, &w.clone, &["bash", "-c", &cmd], None);
    let said = printed(&w.run("Stop"));
    assert!(
        said.contains("SPINNING ON A DEAD PRODUCER")
            && said.contains(&format!("  pid 300 {}", dead.display()))
            && said.contains("stop the loop by its pid")
    );
    assert!(!w.clone.join(".git/live-run.told").exists());
}

#[test]
fn the_command_line_answers_each_mode() {
    let w = world("cli");
    let args = |a: &[&str]| a.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>();
    let c = w.clone.to_string_lossy().into_owned();
    let ctx = w.ctx();
    assert_eq!(with(&args(&["check", &c]), &ctx).stdout, "");
    w.record("a.json", "2001-09-09T01:46:40Z", "green");
    assert!(with(&args(&["check", &c]), &ctx)
        .stdout
        .starts_with("finished-run:"));
    assert_eq!(with(&args(&["seen", &c]), &ctx).stdout, "");
    assert_eq!(with(&args(&["check", &c]), &ctx).stdout, "");
    let log = w.root.join("l");
    std::fs::write(&log, "").unwrap();
    w.add(100, "make", 1, &w.clone, &["make", "x"], Some(&log));
    assert_eq!(with(&args(&["live", &c]), &ctx).stdout, "100 x\n");
    assert_eq!(
        with(&args(&["judge", &c]), &ctx).stdout,
        format!("100 x unwatched {}\n", log.display())
    );
    assert_eq!(with(&args(&["stale"]), &ctx).code, 0);
    assert_eq!(with(&args(&["stale", &c]), &ctx).code, 0);
    assert_eq!(with(&args(&["live"]), &ctx).code, 2);
    assert_eq!(cli(&args(&[])).code, 2);
}
