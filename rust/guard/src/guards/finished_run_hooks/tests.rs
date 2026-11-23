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
        // 451 T177 (message-check): the wait names the output, so the run line says it once
        first.contains("IS STILL RUNNING; NOTHING WILL WAKE THIS SESSION FOR IT:")
            && first.contains(&format!(
                "pid 100 `make sleeper`: wait on it in the background: until grep -qE \"gate green|GATE NOT GREEN|GATE FAILED\" {}; do sleep 20; done",
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

/// The notices of the session's transcript as Claude Code writes them (`set_down_hooks`' own tests' shapes, 451 T65).
fn notice(id: &str, summary: &str) -> String {
    format!(
        r#"{{"type":"user","message":{{"role":"user","content":"<task-notification>\n<task-id>{id}</task-id>\n<status>completed</status>\n<summary>{summary}</summary>\n</task-notification>"}}}}"#
    )
}

impl World {
    /// The harness as a background session's process is (451 T85, measured 2026-11-21 on this session's own): its `comm` its
    /// executable's name, `.../claude/versions/2.1.325`, and its first argument `claude bg-spare`.
    fn versioned_harness(&self, pid: u32) {
        self.add(
            pid,
            "2.1.325",
            1,
            Path::new("/"),
            &["claude bg-spare", "--bg-spare", "/tmp/x.claim.sock"],
            None,
        );
    }

    /// A run the harness `harness` holds: the shell it ran (pid 60) writing `tasks/<task>.output`, and `make <target>` (pid 100)
    /// under it in the clone; the output file.
    fn held_run(&self, harness: u32, task: &str, target: &str) -> PathBuf {
        let tasks = self.root.join("tmp/-diagram/s/tasks");
        std::fs::create_dir_all(&tasks).unwrap();
        let out = tasks.join(format!("{task}.output"));
        std::fs::write(&out, "").unwrap();
        self.add(
            60,
            "bash",
            harness,
            Path::new("/"),
            &["bash", "-c", "make"],
            Some(&out),
        );
        self.add(100, "make", 60, &self.clone, &["make", target], Some(&out));
        out
    }

    /// The event log's line for a background launch, as `event_log_hooks` writes it: `bg` the task, `by` the calling agent.
    fn launched(&self, task: &str, by: Option<&str>) {
        self.launched_in("t", task, by);
    }

    /// [`Self::launched`] by session `sid`.
    fn launched_in(&self, sid: &str, task: &str, by: Option<&str>) {
        let dir = self.clone.join(".git/l7r-events");
        std::fs::create_dir_all(&dir).unwrap();
        let by = by.map_or_else(String::new, |a| format!(r#","by":"{a}""#));
        let line = format!(
            r#"{{"t":"T","sid":"{sid}","ev":"PostToolUse","tool":"Bash","id":"u"{by},"ms":4,"bg":"{task}"}}"#
        );
        let log = dir.join("451-x.jsonl");
        let had = std::fs::read_to_string(&log).unwrap_or_default();
        std::fs::write(&log, had + &line + "\n").unwrap();
    }

    /// A Stop whose payload names the session's transcript.
    fn stop_in(&self, transcript: &Path) -> Vec<Answer> {
        let input = json!({"session_id": "t", "cwd": self.clone.to_string_lossy(), "transcript_path": transcript.to_string_lossy()});
        let s = Session::from_input(&input);
        let e = Event {
            name: "Stop".to_owned(),
            input,
        };
        judge(&e, &s, &self.ctx())
    }

    /// A `SessionStart` of `source` (451 T171): `compact` after a compaction.
    fn start_in(&self, source: &str) -> Vec<Answer> {
        let input =
            json!({"session_id": "t", "cwd": self.clone.to_string_lossy(), "source": source});
        let s = Session::from_input(&input);
        let e = Event {
            name: "SessionStart".to_owned(),
            input,
        };
        judge(&e, &s, &self.ctx())
    }

    fn transcript(&self, lines: &[String]) -> PathBuf {
        let tr = self.root.join("session.jsonl");
        std::fs::write(&tr, lines.join("\n") + "\n").unwrap();
        tr
    }
}

/// 451 T85: a background session's harness is named by its version (`comm` `2.1.325`), so `comm == "claude"` found no harness and
/// every run the session's own background call started read as detached: 10 of the 24 run-still-going refusals of 2026-11-21
/// 00:00-08:00 were the session's own `make claims-owed ledger-owed land`, run in the background.
#[test]
fn a_harness_named_by_its_version_tracks_the_session_s_own_run() {
    let w = world("versioned");
    w.versioned_harness(50);
    let out = w.held_run(50, "bmain", "land");
    w.launched("bmain", None);
    let tr = w.transcript(&[]);
    let said = printed(&w.stop_in(&tr));
    let woke = said.contains("the harness will wake this session")
        && said.contains(&out.to_string_lossy().into_owned());
    assert!(woke); // said names the harness's wake and the run's output
    let args = vec!["judge".to_owned(), w.clone.to_string_lossy().into_owned()];
    assert!(with(&args, &w.ctx()).stdout.contains(" land tracked "));
}

/// 451 T85: a run a builder started is the builder's to wait on while it runs - its own notice wakes the session - by
/// `set_down_hooks`' reading (T65: launched or resumed, or interim with its own work going); once its final notice is in, nothing
/// will, so the run is refused like a detached one, and a waiter on its output lets the turn close.
#[test]
fn a_run_its_still_running_builder_started_lets_the_turn_close_until_the_builder_stops() {
    let w = world("builder");
    w.versioned_harness(50);
    let out = w.held_run(50, "bbuild", "rust-test");
    w.launched("bbuild", Some("abuild"));
    let launched = r#"{"toolUseResult": {"agentId": "abuild"}}"#.to_owned();
    let tr = w.transcript(&[launched.clone()]);
    let said = printed(&w.stop_in(&tr));
    assert!(
        said.contains(
            "`make rust-test` (pid 100) is still going; its builder abuild is still running"
        ) && said.contains(&out.to_string_lossy().into_owned())
    );
    // interim: the builder ended its turn waiting on its own background work, this run
    let own = tr.with_extension("").join("subagents");
    std::fs::create_dir_all(&own).unwrap();
    std::fs::write(
        own.join("agent-abuild.jsonl"),
        r#"{"isSidechain":true,"agentId":"abuild","toolUseResult":{"backgroundTaskId":"bbuild"}}"#
            .to_owned()
            + "\n",
    )
    .unwrap();
    let waiting = notice(
        "abuild",
        r#"Agent \"T85\" is waiting on its own background work"#,
    );
    let tr = w.transcript(&[launched.clone(), waiting.clone()]);
    assert!(printed(&w.stop_in(&tr)).contains("its builder abuild is still running"));
    // its final notice: the builder has stopped, and nothing will wake the session for its run
    let tr = w.transcript(&[
        launched,
        waiting,
        notice("abuild", r#"Agent \"T85\" completed"#),
    ]);
    let text = refused(&w.stop_in(&tr));
    let named = format!(
        "pid 100 `make rust-test`: wait on it in the background: until grep -qE \"gate green|GATE NOT GREEN|GATE FAILED\" {}; do sleep 20; done",
        out.display()
    );
    assert!(text.contains(&named));
    assert!(w.stop_in(&tr).is_empty(), "once per root run");
    std::fs::remove_file(w.clone.join(".git/live-run.told")).unwrap();
    let wait = format!("until grep -q X {}; do sleep 3; done", out.display());
    w.add(200, "bash", 1, Path::new("/"), &["bash", "-c", &wait], None);
    assert!(printed(&w.stop_in(&tr)).contains("a waiter (pid 200) is watching"));
}

/// 451 T85: under a harness named `claude` too, a stopped builder's run is refused; a launch whose agent the session's transcript
/// never names (an agent's own sub-agent), or a transcript that cannot be read, is not a running builder either; a run whose launch
/// no log names (a foreground call, or a background one whose `PostToolUse` line has not come - 4 s after the run started, 2026-11-20
/// 23:22:49) is held by an agent mid-call, and stays the harness's (feature 246).
#[test]
fn a_stopped_or_unknown_builder_s_run_refuses_and_an_unlogged_one_stays_tracked() {
    let w = world("stopped");
    w.add(50, "claude", 1, Path::new("/"), &["claude"], None);
    w.held_run(50, "bgone", "static");
    w.launched("bother", Some("aother"));
    let tr = w.transcript(&[
        r#"{"toolUseResult": {"agentId": "agone"}}"#.to_owned(),
        notice("agone", r#"Agent \"T84\" completed"#),
    ]);
    assert!(printed(&w.stop_in(&tr)).contains("the harness will wake this session"));
    w.launched("bgone", Some("agone"));
    assert!(refused(&w.stop_in(&tr)).contains("pid 100 `make static`"));
    std::fs::remove_file(w.clone.join(".git/live-run.told")).unwrap();
    let nested = world("nested");
    nested.versioned_harness(50);
    nested.held_run(50, "bsub", "static");
    nested.launched("bsub", Some("asub"));
    let empty = nested.transcript(&[]);
    assert!(refused(&nested.stop_in(&empty)).contains("pid 100 `make static`"));
    std::fs::remove_file(nested.clone.join(".git/live-run.told")).unwrap();
    // no transcript: refused all the same - and, the block unchanged, in one line (451 T171)
    assert_eq!(
        refused(&nested.run("Stop")),
        "still: A MAKE RUN THIS SESSION STARTED IS STILL - unchanged since 01:46"
    );
}

/// 451 T171: A RUN THAT ENDED WHILE IT WAS READ IS NO RUN. At 05:45:17 on 2026-11-23 the coordinator's turn was refused over `make
/// quick` and its `make _quick`, both `output in (no file)`, 3 s after quick's Phase line ended: a run gone before its ancestors are
/// read has none, so it read as a root with no output. A zombie's run has ended too.
#[test]
fn a_run_that_ends_while_it_is_read_is_no_run() {
    let w = world("gone");
    w.add(100, "make", 1, &w.clone, &["make", "quick"], None);
    std::fs::remove_file(w.proc.join("100/stat")).unwrap();
    assert!(w.run("Stop").is_empty());
    std::fs::write(w.proc.join("100/stat"), "100 (make) Z 1 0 0").unwrap();
    assert!(w.run("Stop").is_empty());
    std::fs::write(w.proc.join("100/stat"), "100 (make) S 1 0 0").unwrap();
    assert!(refused(&w.run("Stop")).contains(
        "pid 100 `make quick`, no output file: wait on it in the background: while kill -0 100 2>/dev/null; do sleep 20; done"
    ));
}

/// 451 T171: A RUN IS ITS STARTER'S TO WAIT ON. A launch line whose `sid` is another session's - a page session's in the same clone - is
/// that session's run, its own Stop's to name; one a builder's own sub-agent made (`by` an agent the session's transcript never names,
/// its meta's `parentAgentId` a running builder whose own transcript launched it) waits on the sub-agent while it runs, and is refused
/// once it has stopped - in full, then, unchanged, in one line, and in full again after a Stop that passed without it.
#[test]
fn another_session_s_run_or_a_builder_s_sub_agent_s_is_left_to_its_starter() {
    let w = world("starter");
    w.versioned_harness(50);
    let out = w.held_run(50, "bpage", "lines");
    w.launched_in("page", "bpage", Some("apage"));
    let tr = w.transcript(&[]);
    let said = printed(&w.stop_in(&tr));
    assert!(said.contains(
        "`make lines` (pid 100) is still going; session page started it, and that session's own Stop names it"
    ) && said.contains(&out.to_string_lossy().into_owned()));
    let args = vec!["judge".to_owned(), w.clone.to_string_lossy().into_owned()];
    assert!(with(&args, &w.ctx()).stdout.contains(" lines tracked "));
    let sub = world("sub-agent");
    sub.versioned_harness(50);
    sub.held_run(50, "bsub", "rust-test");
    sub.launched("bsub", Some("asub"));
    let tr = sub.transcript(&[r#"{"toolUseResult": {"agentId": "abuild"}}"#.to_owned()]);
    let own = tr.with_extension("").join("subagents");
    std::fs::create_dir_all(&own).unwrap();
    let meta = json!({"spawnDepth": 2, "parentAgentId": "abuild"}).to_string();
    std::fs::write(own.join("agent-asub.meta.json"), meta).unwrap();
    let launch = "{\"agentId\":\"abuild\",\"toolUseResult\":{\"agentId\":\"asub\"}}\n";
    std::fs::write(own.join("agent-abuild.jsonl"), launch).unwrap();
    let said = printed(&sub.stop_in(&tr));
    let waits = "`make rust-test` (pid 100) is still going; its builder asub is still running";
    assert!(said.contains(waits), "{said}");
    // the sub-agent has stopped: refused in full, and again in one line
    let ended = notice("asub", r#"Agent \"review\" completed"#);
    std::fs::write(own.join("agent-abuild.jsonl"), format!("{launch}{ended}\n")).unwrap();
    assert!(refused(&sub.stop_in(&tr))
        .contains("pid 100 `make rust-test`: wait on it in the background"));
    std::fs::remove_file(sub.clone.join(".git/live-run.told")).unwrap();
    assert!(refused(&sub.stop_in(&tr)).starts_with("still: A MAKE RUN THIS SESSION"));
    // a Stop that passes without the block - a waiter on the run's output - and its return is said in full
    std::fs::remove_file(sub.clone.join(".git/live-run.told")).unwrap();
    let out = sub.root.join("tmp/-diagram/s/tasks/bsub.output");
    let wait = format!("until grep -q X {}; do sleep 3; done", out.display());
    sub.add(200, "bash", 1, Path::new("/"), &["bash", "-c", &wait], None);
    assert!(printed(&sub.stop_in(&tr)).contains("a waiter (pid 200) is watching"));
    std::fs::remove_dir_all(sub.proc.join("200")).unwrap();
    assert!(refused(&sub.stop_in(&tr))
        .contains("pid 100 `make rust-test`: wait on it in the background"));
}

/// 451 T171: A COMPACTION FORGETS WHAT WAS SAID (the GM's "no loss of fidelity"): a run refused in full, then in one line, is refused
/// in full again after a `SessionStart` whose source is `compact`, its command with it; the `SessionStart` itself says nothing.
#[test]
fn after_a_compaction_the_run_refusal_is_said_in_full_again() {
    let w = world("forget");
    w.versioned_harness(50);
    w.held_run(50, "bgone", "rust-test");
    w.launched("bgone", Some("agone"));
    let tr = w.transcript(&[]);
    let first = refused(&w.stop_in(&tr));
    let named = first.contains("pid 100 `make rust-test`: wait on it in the background");
    assert!(named, "{first}");
    std::fs::remove_file(w.clone.join(".git/live-run.told")).unwrap();
    assert!(refused(&w.stop_in(&tr)).starts_with("still: A MAKE RUN THIS SESSION"));
    assert!(w.start_in("compact").is_empty());
    std::fs::remove_file(w.clone.join(".git/live-run.told")).unwrap();
    assert_eq!(refused(&w.stop_in(&tr)), first);
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
    let l = log.to_string_lossy().into_owned();
    assert_eq!(with(&args(&["alive", &l]), &ctx).code, 1);
    w.add(
        101,
        "bash",
        1,
        &w.clone,
        &["bash", "-c", &format!("sleep 9; echo x >> {l}")],
        None,
    );
    let alive = with(&args(&["alive", &l]), &ctx);
    assert_eq!(
        (alive.stdout.as_str(), alive.code),
        ("alive 101 writes it\n", 0)
    );
    assert_eq!(with(&args(&["alive"]), &ctx).code, 2);
    assert_eq!(cli(&args(&[])).code, 2);
}

/// THE IDLE CHECK'S PROCESS TABLE (451 T193): a session's background shell is the one whose stdout or stderr is its
/// `<session>/tasks/<id>.output`, another session's or a file elsewhere is none; a waiter on a dead producer is its pid and file; a
/// table with no process cannot be read.
#[test]
fn the_idle_check_reads_which_shells_run_and_which_wait_on_the_dead() {
    use crate::guards::set_down_hooks::Procs as _;
    let w = world("idle-procs");
    assert_eq!(w.ctx().writers("s1"), None, "an empty table");
    let tasks = w.root.join("tmp/s1/tasks");
    std::fs::create_dir_all(&tasks).unwrap();
    let dead = w.root.join("run.log");
    std::fs::write(&dead, "").unwrap();
    let cmd = format!(
        "until grep -q '^ALL DONE' {}; do sleep 60; done",
        dead.display()
    );
    w.add(
        300,
        "bash",
        1,
        &w.clone,
        &["bash", "-c", &cmd],
        Some(&tasks.join("bw1.output")),
    );
    std::os::unix::fs::symlink(tasks.join("bw1.output"), w.proc.join("300/fd/2")).unwrap();
    w.add(
        301,
        "sleep",
        300,
        &w.clone,
        &["sleep", "60"],
        Some(&tasks.join("bw1.output")),
    );
    w.add(
        302,
        "bash",
        1,
        &w.clone,
        &["bash"],
        Some(&w.root.join("tmp/s2/tasks/bo.output")),
    );
    w.add(
        303,
        "bash",
        1,
        &w.clone,
        &["bash"],
        Some(&w.root.join("tmp/s1/other/bq.output")),
    );
    w.add(
        304,
        "bash",
        1,
        &w.clone,
        &["bash"],
        Some(&w.root.join("tmp/s1/tasks/bq.log")),
    );
    w.add(305, "bash", 1, &w.clone, &["bash"], None);
    let held = w.ctx().writers("s1").unwrap();
    assert_eq!(held.len(), 1, "{held:?}");
    assert_eq!(held["bw1"], vec![300, 301]);
    assert_eq!(w.ctx().stale(), vec![(300, dead.display().to_string())]);
}

/// A Monitor told by its command line (451 T193): a live process holding the fragment, never this one, an ancestor or a zombie.
#[test]
fn a_running_command_is_found_by_its_command_line() {
    use crate::guards::set_down_hooks::Procs as _;
    let w = world("idle-running");
    let line = "until grep -q '\"'\"'^ALL DONE'\"'\"' /c/run.log; do sleep 60; done";
    w.add(
        400,
        "bash",
        1,
        &w.clone,
        &["bash", "-c", &format!("eval '{line}'")],
        None,
    );
    w.add(
        401,
        "bash",
        1,
        &w.clone,
        &["bash", "-c", &format!("eval '{line}'")],
        None,
    );
    std::fs::write(w.proc.join("401/stat"), "401 (bash) Z 1 0 0").unwrap();
    w.add(
        99_999,
        "l7r-guard",
        1,
        &w.clone,
        &["l7r-guard", "/c/run.log; do sleep 60; done"],
        None,
    );
    assert_eq!(w.ctx().running("/c/run.log; do sleep 60; done"), vec![400]);
    assert!(w.ctx().running("nothing runs this").is_empty());
}
