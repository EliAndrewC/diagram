//! The runner (feature 461 T12) on scratch repositories: a second start a no-op naming the first's pid, the stop at once and after the
//! batch in flight, the idle stop, a killed runner's open batch resumed from the log, the runner's own lines naming no batch, the
//! detached process's command line and its start from a hand-in.

use std::cell::{Cell, RefCell};
use std::collections::BTreeSet;
use std::path::{Path, PathBuf};

use l7r_gate_core::ci::fixtures::repo;
use serde_json::json;

use super::{
    argv, held, holder, lock_path, on_hand_in, remaining, start, stop, stop_path, work, work_cli,
    Run, STOP,
};
use crate::log::{self, BatchState};

/// A stand-in for `l7r-gate`: called as `<exe> lane --work <common>`, it takes the lock as the runner does, writes its pid there and
/// sleeps holding it; `exit 0` where the lock is held already (the runner's own race).
fn fake_exe(dir: &Path) -> PathBuf {
    let exe = dir.join("fake-l7r-gate");
    l7r_gate_core::write_executable(
        &exe,
        "#!/bin/sh\nexec 9<>\"$3/l7r-lane/lane.lock\"\nflock -w 1 9 || exit 0\necho $$ > \"$3/l7r-lane/lane.lock\"\nexec sleep 30\n",
    );
    exe
}

fn common_of(dir: &Path) -> PathBuf {
    dir.join(".git")
}

fn no_env(_: &str) -> Option<String> {
    None
}

#[test]
fn a_second_start_is_a_no_op_naming_the_first_s_pid_and_stop_now_ends_it() {
    let dir = repo("lane-start");
    let common = common_of(dir.path());
    let exe = fake_exe(dir.path());
    assert_eq!(holder(&common), None);
    let first = start(&common, &exe, "setsid", 5.0);
    assert_eq!(first.code, 0);
    let pid = holder(&common).unwrap();
    assert_eq!(
        first.stdout,
        format!("lane: the runner started (pid {pid})\n")
    );
    let second = start(&common, &exe, "setsid", 5.0);
    assert_eq!(second.code, 0);
    assert_eq!(
        second.stdout,
        format!("lane: the runner already runs (pid {pid})\n")
    );
    let stopped = stop(&common, true, 5.0);
    assert_eq!(stopped.code, 0);
    assert_eq!(
        stopped.stdout,
        format!("lane: the runner (pid {pid}) stopped at once (NOW=1)\n")
    );
    assert!(!held(&common));
    // the stopper writes the runner's `stop` line, and it names no batch: a batch open when it was killed is resumed, not stopped
    let lines = log::read(&common);
    let last = lines.last().unwrap();
    assert_eq!(last["event"], "stop");
    assert_eq!(last["pid"], pid);
    assert!(last.get("batch").is_none());
    assert_eq!(stop(&common, true, 1.0).stdout, "lane: no runner\n");
}

#[test]
fn a_start_that_cannot_spawn_or_whose_runner_takes_no_lock_is_an_error() {
    let dir = repo("lane-start-fails");
    let common = common_of(dir.path());
    let exe = fake_exe(dir.path());
    let gone = start(&common, &exe, "/no/such/setsid", 1.0);
    assert_eq!(gone.code, 1);
    assert!(gone.stderr.starts_with("lane: /no/such/setsid: "));
    let idle = dir.path().join("idle-exe");
    l7r_gate_core::write_executable(&idle, "#!/bin/sh\nexit 0\n");
    let none = start(&common, &idle, "setsid", 0.2);
    assert_eq!(none.code, 1);
    assert!(none.stderr.contains("holds no lock"));
}

#[test]
fn a_stop_after_the_batch_asks_the_runner_and_waits_for_it() {
    let dir = repo("lane-stop-soft");
    let common = common_of(dir.path());
    let exe = fake_exe(dir.path());
    assert_eq!(start(&common, &exe, "setsid", 5.0).code, 0);
    let pid = holder(&common).unwrap();
    // the stand-in never reads the request, so the stop says it is asked and leaves it to the runner
    let asked = stop(&common, false, 0.2);
    assert_eq!(asked.code, 0);
    assert!(asked.stdout.contains(&format!("pid {pid}")));
    assert!(asked.stdout.contains("ends after the batch in flight"));
    assert_eq!(
        std::fs::read_to_string(stop_path(&common)).unwrap(),
        pid.to_string()
    );
    assert_eq!(stop(&common, true, 5.0).code, 0);
}

/// A stand-in runner with its own `body` after the lock is taken and its pid written.
fn runner_like(dir: &Path, name: &str, body: &str) -> PathBuf {
    let exe = dir.join(name);
    let head = "#!/bin/sh\nexec 9<>\"$3/l7r-lane/lane.lock\"\nflock -w 1 9 || exit 0\necho $$ > \"$3/l7r-lane/lane.lock\"\n";
    l7r_gate_core::write_executable(&exe, &format!("{head}{body}"));
    exe
}

#[test]
fn a_runner_deaf_to_term_is_killed_and_one_that_reads_the_request_ends_after_its_batch() {
    let dir = repo("lane-stop-hard");
    let common = common_of(dir.path());
    let deaf = runner_like(dir.path(), "deaf", "trap '' TERM\nexec sleep 30\n");
    assert_eq!(start(&common, &deaf, "setsid", 5.0).code, 0);
    let pid = holder(&common).unwrap();
    // a request that cannot be written is an error naming the file
    std::fs::create_dir_all(stop_path(&common)).unwrap();
    let unwritten = stop(&common, false, 0.2);
    assert_eq!(unwritten.code, 1);
    assert!(unwritten.stderr.contains(STOP));
    std::fs::remove_dir(stop_path(&common)).unwrap();
    // a stop line that cannot be written is said on stderr; the stop still ends the runner
    std::fs::create_dir_all(log::path(&common)).unwrap();
    let killed = stop(&common, true, 0.3);
    assert!(killed.stderr.starts_with("lane: "));
    std::fs::remove_dir(log::path(&common)).unwrap();
    assert_eq!(
        killed.stdout,
        format!("lane: the runner (pid {pid}) stopped at once (NOW=1)\n")
    );
    assert!(!held(&common));
    let polite = runner_like(
        dir.path(),
        "polite",
        "while [ ! -f \"$3/l7r-lane/stop-request\" ]; do sleep 0.05; done\n",
    );
    assert_eq!(start(&common, &polite, "setsid", 5.0).code, 0);
    let pid = holder(&common).unwrap();
    let asked = stop(&common, false, 5.0);
    assert_eq!(
        asked.stdout,
        format!("lane: the runner (pid {pid}) stopped after its batch in flight\n")
    );
}

#[test]
fn the_runner_s_argv_is_its_own_verb_and_the_common_directory() {
    let words = argv(Path::new("/b/l7r-gate"), Path::new("/c/.git"));
    assert_eq!(words, ["/b/l7r-gate", "lane", "--work", "/c/.git"]);
    assert_eq!(
        lock_path(Path::new("/c")),
        Path::new("/c/l7r-lane/lane.lock")
    );
}

/// A loop's world: a clock that moves by each sleep, the hand-ins seen at each tick, and what the seams were asked.
struct Fake {
    clock: Cell<f64>,
    ticks: RefCell<Vec<BTreeSet<String>>>,
}

impl Fake {
    fn new(ticks: &[&[&str]]) -> Self {
        Self {
            clock: Cell::new(1000.0),
            ticks: RefCell::new(
                ticks
                    .iter()
                    .map(|t| t.iter().map(|s| (*s).to_owned()).collect())
                    .collect(),
            ),
        }
    }

    fn hand_ins(&self) -> BTreeSet<String> {
        let mut t = self.ticks.borrow_mut();
        if t.len() > 1 {
            t.remove(0)
        } else {
            t.first().cloned().unwrap_or_default()
        }
    }
}

#[test]
fn the_runner_stops_idle_once_no_hand_in_arrives_for_the_knob_s_seconds() {
    let dir = l7r_gate_core::ci::fixtures::scratch("lane-idle");
    let f = Fake::new(&[&["a"], &["a"], &["a", "b"], &["a", "b"]]);
    let (now, sleep) = (|| f.clock.get(), |s: f64| f.clock.set(f.clock.get() + s));
    let hand_ins = || f.hand_ins();
    let mut resumed = Vec::new();
    let mut resume = |b: &log::Batch, r: &[String]| {
        resumed.push((b.id.clone(), r.to_vec()));
        Ok(())
    };
    let steps = Cell::new(0);
    let mut step = || {
        steps.set(steps.get() + 1);
        Ok(false)
    };
    let mut run = Run {
        common: dir.path(),
        pid: 7,
        idle_s: 30.0,
        poll_s: 10.0,
        now: &now,
        sleep: &sleep,
        hand_ins: &hand_ins,
        resume: &mut resume,
        step: &mut step,
    };
    assert_eq!(work(&mut run).unwrap(), "idle");
    // `b` arrived at the third tick (t = 1020), so the idle clock ran from there: stopped at 1050, not 1030
    assert!((f.clock.get() - 1050.0).abs() < 1e-9);
    assert_eq!(steps.get(), 6);
    assert!(resumed.is_empty());
    let lines = log::read(dir.path());
    assert_eq!(lines.len(), 2);
    assert_eq!(lines[0]["event"], "start");
    assert_eq!(lines[0]["why"], "make lane-start");
    assert_eq!(lines[1]["event"], "stop");
    assert_eq!(lines[1]["why"], "idle");
    assert_eq!(lines[1]["pid"], 7);
}

#[test]
fn a_batch_run_resets_the_idle_clock_and_a_failing_step_ends_the_runner_with_its_line() {
    let dir = l7r_gate_core::ci::fixtures::scratch("lane-step");
    let f = Fake::new(&[&[]]);
    let (now, sleep) = (|| f.clock.get(), |s: f64| f.clock.set(f.clock.get() + s));
    let hand_ins = || f.hand_ins();
    let mut resume = |_: &log::Batch, _: &[String]| Ok(());
    let n = Cell::new(0);
    let mut step = || {
        n.set(n.get() + 1);
        match n.get() {
            1 => Ok(true),
            2 => Ok(false),
            _ => Err("the batch's carry raised".to_owned()),
        }
    };
    let mut run = Run {
        common: dir.path(),
        pid: 8,
        idle_s: 100.0,
        poll_s: 10.0,
        now: &now,
        sleep: &sleep,
        hand_ins: &hand_ins,
        resume: &mut resume,
        step: &mut step,
    };
    assert_eq!(work(&mut run).unwrap_err(), "the batch's carry raised");
    let last = log::read(dir.path()).pop().unwrap();
    assert_eq!(last["why"], "error: the batch's carry raised");
}

#[test]
fn a_stop_request_ends_its_own_runner_and_one_left_for_another_is_dropped() {
    let dir = l7r_gate_core::ci::fixtures::scratch("lane-request");
    let common = dir.path();
    std::fs::create_dir_all(common.join(log::DIR)).unwrap();
    // a request a runner before this one never read must not end this one at its start
    std::fs::write(stop_path(common), "1").unwrap();
    let f = Fake::new(&[&[]]);
    let now = || f.clock.get();
    let sleep = |s: f64| {
        f.clock.set(f.clock.get() + s);
        std::fs::write(stop_path(common), "9").unwrap();
    };
    let hand_ins = || f.hand_ins();
    let mut resume = |_: &log::Batch, _: &[String]| Ok(());
    let mut step = || Ok(false);
    let mut run = Run {
        common,
        pid: 9,
        idle_s: 1000.0,
        poll_s: 10.0,
        now: &now,
        sleep: &sleep,
        hand_ins: &hand_ins,
        resume: &mut resume,
        step: &mut step,
    };
    assert_eq!(work(&mut run).unwrap(), "make lane-stop");
    assert!((f.clock.get() - 1010.0).abs() < 1e-9);
    assert!(!stop_path(common).exists());
}

#[test]
fn a_killed_runner_s_open_batch_is_resumed_from_the_log_and_a_closed_one_is_not() {
    let dir = l7r_gate_core::ci::fixtures::scratch("lane-recover");
    let common = dir.path();
    let put = |event: &str, fields: serde_json::Value| {
        log::append(common, "2026-11-28T03:00:00Z", event, &fields).unwrap();
    };
    put(
        "batch",
        json!({"batch": "461-1", "changes": ["aaaaaaa1", "bbbbbbb2"]}),
    );
    put(
        "landed",
        json!({"batch": "461-1", "landed": ["aaaaaaa1", "bbbbbbb2"], "ejected": [], "runs": 1, "minutes": 3}),
    );
    put(
        "batch",
        json!({"batch": "461-2", "changes": ["ccccccc3", "ddddddd4", "eeeeeee5"]}),
    );
    put(
        "carry",
        json!({"batch": "461-2", "code": 0, "conflict": []}),
    );
    put(
        "eject",
        json!({"batch": "461-2", "change": "ddddddd4", "repair": "r1", "why": "conflict"}),
    );
    // the runner was killed here: no `landed`, no `stop` naming the batch
    let batch = log::batches(&log::read(common)).pop().unwrap();
    assert_eq!(batch.state, BatchState::Gating(1));
    let on_main: BTreeSet<String> = ["ccccccc3".to_owned()].into();
    assert_eq!(remaining(&batch, &on_main), ["eeeeeee5"]);
    let f = Fake::new(&[&[]]);
    let (now, sleep) = (|| f.clock.get(), |s: f64| f.clock.set(f.clock.get() + s));
    let hand_ins = || f.hand_ins();
    let mut resumed = Vec::new();
    let mut resume = |b: &log::Batch, r: &[String]| {
        resumed.push((b.id.clone(), r.to_vec()));
        Ok(())
    };
    let mut step = || Ok(false);
    let mut run = Run {
        common,
        pid: 11,
        idle_s: 0.0,
        poll_s: 1.0,
        now: &now,
        sleep: &sleep,
        hand_ins: &hand_ins,
        resume: &mut resume,
        step: &mut step,
    };
    assert_eq!(work(&mut run).unwrap(), "idle");
    // `remaining` here is asked of `origin/main` by the production seam; the loop hands the batch's own reading to `resume`
    assert_eq!(
        resumed,
        [(
            "461-2".to_owned(),
            vec!["ccccccc3".to_owned(), "eeeeeee5".to_owned()]
        )]
    );
    let start_line = log::read(common)
        .into_iter()
        .rev()
        .find(|l| l["event"] == "start")
        .unwrap();
    assert_eq!(start_line["why"], "resume 461-2");
    assert!(start_line.get("batch").is_none());
    // the resumed batch is still open (its run is T14's), and a batch closed by a `stop` naming it is never resumed
    put(
        "stop",
        json!({"batch": "461-2", "pid": 11, "why": "arbiter owed"}),
    );
    let mut again = Vec::new();
    let mut resume = |b: &log::Batch, _: &[String]| {
        again.push(b.id.clone());
        Ok(())
    };
    let mut step = || Ok(false);
    let mut run = Run {
        common,
        pid: 12,
        idle_s: 0.0,
        poll_s: 1.0,
        now: &now,
        sleep: &sleep,
        hand_ins: &hand_ins,
        resume: &mut resume,
        step: &mut step,
    };
    assert_eq!(work(&mut run).unwrap(), "idle");
    assert!(again.is_empty());
}

#[test]
fn a_resume_that_fails_ends_the_runner_with_its_line() {
    let dir = l7r_gate_core::ci::fixtures::scratch("lane-resume-fails");
    let common = dir.path();
    log::append(
        common,
        "t",
        "batch",
        &json!({"batch": "461-3", "changes": ["fffffff6"]}),
    )
    .unwrap();
    let now = || 0.0;
    let sleep = |_: f64| {};
    let hand_ins = BTreeSet::new;
    let mut resume = |_: &log::Batch, _: &[String]| Err("no tree".to_owned());
    let mut step = || Ok(false);
    let mut run = Run {
        common,
        pid: 13,
        idle_s: 0.0,
        poll_s: 1.0,
        now: &now,
        sleep: &sleep,
        hand_ins: &hand_ins,
        resume: &mut resume,
        step: &mut step,
    };
    assert_eq!(work(&mut run).unwrap_err(), "no tree");
    assert_eq!(log::read(common).pop().unwrap()["why"], "error: no tree");
}

#[test]
fn the_work_command_holds_the_lock_reads_its_knobs_and_a_second_runner_leaves_quietly() {
    let dir = repo("lane-work");
    let common = common_of(dir.path());
    let env = |k: &str| match k {
        "LANE_IDLE_S" => Some("0.05".to_owned()),
        "LANE_POLL_S" => Some("0.01".to_owned()),
        _ => None,
    };
    let done = work_cli(&common, &env);
    assert_eq!(done.code, 0);
    assert_eq!(done.stdout, "lane: the runner stopped (idle)\n");
    assert!(!held(&common));
    let lines = log::read(&common);
    assert_eq!(lines[0]["pid"], std::process::id());
    // held by another: the runner that lost the race ends at once, writing nothing
    let lock = l7r_shared::tool::flock_within(&lock_path(&common), 1.0)
        .unwrap()
        .unwrap();
    let quiet = work_cli(&common, &no_env);
    assert_eq!((quiet.code, quiet.stdout.as_str()), (0, ""));
    assert_eq!(log::read(&common).len(), lines.len());
    drop(lock);
    // a knob that is no number is refused before anything is held
    let bad = |k: &str| (k == "LANE_IDLE_S").then(|| "an hour".to_owned());
    let refused = work_cli(&common, &bad);
    assert_eq!(refused.code, 2);
    assert!(refused.stderr.contains("LANE_IDLE_S"));
    // no git directory, a lock that cannot be opened, and a log that cannot be written are each an error exit
    let out_of_repo = l7r_gate_core::ci::fixtures::scratch("lane-work-norepo");
    let missing = out_of_repo.path().join("missing").join(".git");
    let gone = work_cli(&missing, &env);
    assert_eq!(gone.code, 1);
    assert!(gone.stderr.contains("is no git directory"));
    assert!(!missing.exists());
    let odd = out_of_repo.path().join("odd");
    std::fs::create_dir_all(lock_path(&odd)).unwrap();
    assert_eq!(work_cli(&odd, &env).code, 1);
    let unlogged = out_of_repo.path().join("unlogged");
    std::fs::create_dir_all(log::path(&unlogged)).unwrap();
    let failed = work_cli(&unlogged, &env);
    assert_eq!(failed.code, 1);
    assert!(failed.stderr.starts_with("lane: the runner failed: lane: "));
}

#[test]
fn a_hand_in_starts_the_runner_only_from_phase_two_s_base_and_only_when_it_succeeded() {
    let dir = repo("lane-hand-in");
    let common = common_of(dir.path());
    let exe = fake_exe(dir.path());
    let hand_in = ["--hand-in".to_owned(), "T01".to_owned()];
    let ok = || l7r_gate_core::Reply {
        stdout: "handed in to the lane (make lane for its place)\n".to_owned(),
        stderr: String::new(),
        code: 0,
    };
    // any other `land` verb (a landing, a carry) starts nothing, whatever the base
    let landing = ["T01".to_owned()];
    assert_eq!(
        on_hand_in(&landing, ok(), Some("origin"), dir.path(), &exe),
        ok()
    );
    // phase 1 (the base the clone's HEAD, or unset): the coordinator still lands by hand, so no runner is started
    for base in [None, Some("clone")] {
        assert_eq!(on_hand_in(&hand_in, ok(), base, dir.path(), &exe), ok());
    }
    assert!(!held(&common));
    let refused = || l7r_gate_core::Reply { code: 2, ..ok() };
    assert_eq!(
        on_hand_in(&hand_in, refused(), Some("origin"), dir.path(), &exe),
        refused()
    );
    assert!(!held(&common));
    let started = on_hand_in(&hand_in, ok(), Some("origin"), dir.path(), &exe);
    assert_eq!(started.code, 0);
    let pid = holder(&common).unwrap();
    assert!(started
        .stdout
        .ends_with(&format!("lane: the runner started (pid {pid})\n")));
    let again = on_hand_in(&hand_in, ok(), Some("origin"), dir.path(), &exe);
    assert!(again
        .stdout
        .ends_with(&format!("lane: the runner already runs (pid {pid})\n")));
    assert_eq!(stop(&common, true, 5.0).code, 0);
    // outside a repository the hand-in's reply stands, with the lane's error after it
    let nowhere = l7r_gate_core::ci::fixtures::scratch("lane-hand-in-norepo");
    let lost = on_hand_in(&hand_in, ok(), Some("origin"), nowhere.path(), &exe);
    assert_eq!(lost.code, 0);
    assert!(lost.stderr.contains("is in no git repository"));
}

#[test]
fn the_work_command_sees_a_real_hand_in_and_resumes_an_open_batch_of_the_log() {
    use l7r_gate_core::ci::fixtures::{commit, git};
    let dir = repo("lane-work-real");
    let root = dir.path();
    let common = common_of(root);
    git(root, &["checkout", "-qb", "side"]);
    commit(root, "w.txt", "w");
    let sha = git(root, &["rev-parse", "HEAD"]);
    git(root, &["checkout", "-q", "main"]);
    git(root, &["update-ref", "refs/l7r/done/461-T01", &sha]);
    let done = json!({"utc": "2026-11-28T01:00:00Z", "event": "done", "detail": "461 T01", "commit": sha, "handed_in": true});
    std::fs::write(
        common.join(l7r_shared::builder_queue::LOG),
        format!("{done}\n"),
    )
    .unwrap();
    log::append(
        &common,
        "t",
        "batch",
        &json!({"batch": "461-1", "changes": [sha]}),
    )
    .unwrap();
    let env = |k: &str| match k {
        "LANE_IDLE_S" => Some("0.05".to_owned()),
        "LANE_POLL_S" => Some("0.01".to_owned()),
        _ => None,
    };
    let worked = work_cli(&common, &env);
    assert_eq!(worked.stdout, "lane: the runner stopped (idle)\n");
    let lines = log::read(&common);
    let start_line = lines.iter().find(|l| l["event"] == "start").unwrap();
    assert_eq!(start_line["why"], "resume 461-1");
    // the batch is left open for T14's run: the next runner resumes it again
    assert!(log::batches(&lines).pop().unwrap().open());
}
