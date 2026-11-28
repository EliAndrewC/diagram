//! The wake-up (feature 461 T20) on a scratch common directory and a clock of its own: the owed lines past the mark printed once
//! and the mark moved, the wait blocking until one comes; a dead runner over an open batch said once a death and only after the
//! grace; the quiet cases - a live runner, no open batch; the command's knobs and its exits.

use std::cell::{Cell, RefCell};
use std::path::Path;

use l7r_shared::tempdir::TempDir;
use serde_json::{json, Value};

use super::{dead, unserved, wait, wait_cli, waiting_on, Wait, DEAD};
use crate::log::{self, HandIn};

fn line(common: &Path, event: &str, fields: &Value) {
    log::append(common, "2026-11-28T03:00:00Z", event, fields).unwrap();
}

fn owed(common: &Path, text: &str) {
    line(common, "owed", &json!({"batch": "461-1", "line": text}));
}

/// A wait on `common` over a clock that each sleep moves on, the runner `alive` as given, and `at_sleep` run at each sleep with its
/// count; the lines it returned and the sleeps it took.
fn run(
    common: &Path,
    alive: bool,
    at_sleep: &dyn Fn(usize),
) -> (Result<Vec<String>, String>, usize) {
    run_on(common, alive, None, at_sleep)
}

/// [`run`] with the hand-ins waiting given, as from phase 2's base (461 T56).
fn run_on(
    common: &Path,
    alive: bool,
    waiting: Option<&dyn Fn() -> Vec<HandIn>>,
    at_sleep: &dyn Fn(usize),
) -> (Result<Vec<String>, String>, usize) {
    let clock = Cell::new(1000.0);
    let sleeps = Cell::new(0);
    let now = || clock.get();
    let sleep = |s: f64| {
        clock.set(clock.get() + s);
        sleeps.set(sleeps.get() + 1);
        at_sleep(sleeps.get());
    };
    let alive = move || alive;
    let w = Wait {
        common,
        poll_s: 5.0,
        grace_s: 30.0,
        now: &now,
        sleep: &sleep,
        alive: &alive,
        waiting,
    };
    (wait(&w), sleeps.get())
}

/// A sleep that does nothing more: the first test asserts it was never reached, the dead runner's test reaches it.
fn nothing(_: usize) {}

#[test]
fn owed_lines_past_the_mark_are_printed_once_and_the_wait_blocks_for_the_next() {
    let t = TempDir::new("lane-wake-once");
    let c = t.path();
    line(
        c,
        "batch",
        &json!({"batch": "461-1", "changes": ["a1b2c3d4e5"]}),
    );
    owed(
        c,
        "lane: batch 461-1 landed - 461 T01 (1 change(s), 1 run(s), 4.2 minutes)",
    );
    line(
        c,
        "landed",
        &json!({"batch": "461-1", "landed": ["a1b2c3d4e5"]}),
    );
    let (got, sleeps) = run(c, false, &nothing);
    assert_eq!(
        got.unwrap(),
        ["lane: batch 461-1 landed - 461 T01 (1 change(s), 1 run(s), 4.2 minutes)"]
    );
    assert_eq!(sleeps, 0);
    // nothing past the mark now: the wait sleeps until the lane owes the next line, and prints that one alone
    let (got, sleeps) = run(c, false, &|n| {
        if n == 3 {
            owed(c, "lane: batch 461-2 landed");
        }
    });
    assert_eq!(got.unwrap(), ["lane: batch 461-2 landed"]);
    assert_eq!(sleeps, 3);
}

#[test]
fn a_dead_runner_over_an_open_batch_is_said_once_a_death_after_the_grace() {
    let t = TempDir::new("lane-wake-dead");
    let c = t.path();
    line(c, "start", &json!({"pid": 7, "why": "make lane-start"}));
    line(
        c,
        "batch",
        &json!({"batch": "461-1", "changes": ["a1b2c3d4e5", "f6a7b8c9d0"]}),
    );
    line(
        c,
        "carry",
        &json!({"batch": "461-1", "code": 1, "conflict": ["x.rs"]}),
    );
    line(
        c,
        "stop",
        &json!({"pid": 7, "why": "error: lane: batch 461-1: carry stopped"}),
    );
    let (got, sleeps) = run(c, false, &nothing);
    assert_eq!(
        got.unwrap(),
        ["lane: the runner is not running and batch 461-1 is open (2 change(s), gating 1; it stopped: error: lane: batch 461-1: carry stopped) - make lane-start resumes it"]
    );
    // the grace: 30 s of 5 s polls, the first poll at once
    assert_eq!(sleeps, 6);
    let last = log::read(c).pop().unwrap();
    assert_eq!(
        (last["event"].as_str(), last["why"].as_str()),
        (Some("owed"), Some(DEAD))
    );
    // said once a death: the re-armed wait blocks until the lane owes another line
    let (got, _) = run(c, false, &|n| {
        if n == 20 {
            owed(c, "lane: batch 461-1 landed");
        }
    });
    assert_eq!(got.unwrap(), ["lane: batch 461-1 landed"]);
    // a runner started again and killed with no stop line: a new death, said again
    line(c, "start", &json!({"pid": 8, "why": "resume 461-1"}));
    let (got, _) = run(c, false, &nothing);
    assert!(got.unwrap()[0]
        .ends_with("it ended with no stop line (killed)) - make lane-start resumes it"));
}

#[test]
fn a_red_run_s_own_line_tells_the_death_so_one_red_wakes_once() {
    let t = TempDir::new("lane-wake-red");
    let c = t.path();
    line(c, "start", &json!({"pid": 7, "why": "make lane-start"}));
    line(
        c,
        "batch",
        &json!({"batch": "461-1", "changes": ["a1b2c3d4e5"]}),
    );
    // the runner's own line that it stopped with the batch open (461 T15: a `make` with no exit code), then its stop
    line(
        c,
        "owed",
        &json!({"batch": "461-1", "stopped": true, "line": "lane: batch 461-1: make land ended with no exit code at attempt 1 (it could not start, or was killed) - the runner stopped, the batch open: a.log"}),
    );
    line(
        c,
        "stop",
        &json!({"pid": 7, "why": "error: lane: batch 461-1 red"}),
    );
    let (got, _) = run(c, false, &nothing);
    assert!(got.unwrap()[0].contains("no exit code at attempt 1"));
    // the re-armed wait, far past the grace, says no death: the runner's line told it
    let (got, sleeps) = run(c, false, &|n| {
        if n == 20 {
            owed(c, "lane: batch 461-1 landed");
        }
    });
    assert_eq!(
        (got.unwrap(), sleeps),
        (vec!["lane: batch 461-1 landed".to_owned()], 20)
    );
    assert!(!log::read(c).iter().any(|l| l["why"] == DEAD));
}

/// 461 T15: a red attempt's ejection owes its line while the runner goes on to the next attempt, so it tells no death - a runner
/// killed after it leaves the batch open, and that death is said once.
#[test]
fn an_ejection_s_line_tells_no_death_so_a_runner_killed_after_it_is_said() {
    let t = TempDir::new("lane-wake-ejected");
    let c = t.path();
    line(c, "start", &json!({"pid": 7, "why": "make lane-start"}));
    line(
        c,
        "batch",
        &json!({"batch": "461-1", "changes": ["a1b2c3d4e5", "f6a7b8c9d0"]}),
    );
    owed(c, "lane: batch 461-1 red at attempt 1 - 461 T02 ejected as repair r1 (red: lib/two test) - make builder-next hands it to a fresh builder: a.log");
    let (got, _) = run(c, false, &nothing);
    assert!(got.unwrap()[0].contains("ejected as repair r1"));
    // far past the grace (50 polls against the grace's 6) a wait that said nothing fails here, so the old rule's silence is a red, not
    // a hang on the fake clock; one line, so the guard no right answer reaches leaves no line unrun (461 T62)
    let (got, _) = run(c, false, &|n| assert!(n < 50));
    assert!(got.unwrap()[0].starts_with("lane: the runner is not running and batch 461-1 is open"));
    assert_eq!(log::read(c).iter().filter(|l| l["why"] == DEAD).count(), 1);
}

#[test]
fn a_live_runner_or_no_open_batch_is_quiet() {
    let t = TempDir::new("lane-wake-quiet");
    let c = t.path();
    line(
        c,
        "batch",
        &json!({"batch": "461-1", "changes": ["a1b2c3d4e5"]}),
    );
    let (got, _) = run(c, true, &|n| {
        if n == 12 {
            owed(c, "lane: escape");
        }
    });
    assert_eq!(got.unwrap(), ["lane: escape"]);
    // the batch landed and the runner gone (idle, or make lane-stop): nothing is stranded, so nothing is said
    line(
        c,
        "landed",
        &json!({"batch": "461-1", "landed": ["a1b2c3d4e5"]}),
    );
    line(c, "stop", &json!({"pid": 7, "why": "idle"}));
    let (got, _) = run(c, false, &|n| {
        if n == 12 {
            owed(c, "lane: escape 2");
        }
    });
    assert_eq!(got.unwrap(), ["lane: escape 2"]);
    assert!(!log::read(c).iter().any(|l| l["why"] == DEAD));
    assert!(dead(&log::read(c)).is_none());
    // no log at all: no batch, no runner, nothing written
    assert!(dead(&[]).is_none());
}

#[test]
fn a_runner_seen_inside_the_grace_starts_it_again() {
    let t = TempDir::new("lane-wake-grace");
    let c = t.path();
    line(
        c,
        "batch",
        &json!({"batch": "461-1", "changes": ["a1b2c3d4e5"]}),
    );
    // the runner gone at polls 0-4, holding the lock at poll 5, gone again after: the grace runs from poll 6, so the line comes at 12
    let polls = RefCell::new(0);
    let clock = Cell::new(0.0);
    let now = || clock.get();
    let sleep = |s: f64| clock.set(clock.get() + s);
    let alive = || {
        *polls.borrow_mut() += 1;
        *polls.borrow() == 6
    };
    let w = Wait {
        common: c,
        poll_s: 5.0,
        grace_s: 30.0,
        now: &now,
        sleep: &sleep,
        alive: &alive,
        waiting: None,
    };
    assert!(wait(&w).unwrap()[0].contains("batch 461-1 is open"));
    assert!((clock.get() - 60.0).abs() < 1e-9);
}

#[test]
fn the_command_prints_the_lines_and_refuses_a_knob_that_is_no_number() {
    let t = TempDir::new("lane-wake-cli");
    let c = t.path();
    owed(c, "lane: one");
    owed(c, "lane: two");
    let got = wait_cli(c, &|_| None);
    assert_eq!(
        (got.stdout.as_str(), got.code),
        ("lane: one\nlane: two\n", 0)
    );
    // nothing past the mark: the command sleeps on the real clock until a line comes
    let writer = {
        let c = c.to_path_buf();
        std::thread::spawn(move || {
            std::thread::sleep(std::time::Duration::from_millis(50));
            owed(&c, "lane: three");
        })
    };
    let slept = wait_cli(c, &|k| (k == "LANE_WAIT_POLL_S").then(|| "0.01".to_owned()));
    writer.join().unwrap();
    assert_eq!(slept.stdout, "lane: three\n");
    let bad = wait_cli(c, &|k| {
        (k == "LANE_DEAD_GRACE_S").then(|| "soon".to_owned())
    });
    assert_eq!(bad.code, 2);
    assert!(bad.stderr.contains("LANE_DEAD_GRACE_S=soon"));
}

#[test]
fn a_dead_line_that_cannot_be_written_is_an_error() {
    use std::os::unix::fs::PermissionsExt as _;
    let t = TempDir::new("lane-wake-ro");
    let c = t.path();
    line(
        c,
        "batch",
        &json!({"batch": "461-1", "changes": ["a1b2c3d4e5"]}),
    );
    let file = log::path(c);
    std::fs::set_permissions(&file, std::fs::Permissions::from_mode(0o444)).unwrap();
    let got = wait_cli(c, &|_| Some("0".to_owned()));
    std::fs::set_permissions(&file, std::fs::Permissions::from_mode(0o644)).unwrap();
    assert_eq!(got.code, 1);
    assert!(got.stderr.contains("lane.jsonl"));
}

fn hand_in(tasks: &str, commit: &str, at: &str) -> HandIn {
    HandIn {
        feature: "461".to_owned(),
        tasks: tasks.split(',').map(str::to_owned).collect(),
        commit: commit.to_owned(),
        at: at.to_owned(),
        repair_of: None,
        build_half: false,
    }
}

/// 461 T56: from phase 2's base every hand-in starts the runner, so a waiting hand-in no runner serves (its start failed) is said
/// once a hand-in after the grace - a later hand-in whose start fails too said itself - and phase 1's is quiet.
#[test]
fn a_waiting_hand_in_no_runner_serves_is_said_once_from_phase_2_s_base() {
    let t = TempDir::new("lane-wake-unserved");
    let c = t.path();
    let one = hand_in("T12", "a1b2c3d4e5f6", "2026-11-28T04:00:00Z");
    let ins = RefCell::new(vec![one.clone()]);
    let waiting = || ins.borrow().clone();
    // phase 1 (no seam): quiet far past the grace
    let (got, _) = run_on(c, false, None, &|n| {
        if n == 20 {
            owed(c, "lane: phase 1");
        }
    });
    assert_eq!(got.unwrap(), ["lane: phase 1"]);
    // phase 2, no lane line at all: said after the grace, naming the hand-in
    let (got, sleeps) = run_on(c, false, Some(&waiting), &|n| assert!(n < 50));
    assert_eq!(
        got.unwrap(),
        ["lane: the runner is not running and 1 hand-in(s) wait with no batch formed (461 T12 (a1b2c3d4e5); no runner has started) - make lane-start starts it"]
    );
    assert_eq!(sleeps, 6);
    let last = log::read(c).pop().unwrap();
    assert_eq!(
        (last["why"].as_str(), &last["unserved"]),
        (Some(DEAD), &json!(["a1b2c3d4e5f6"]))
    );
    // said once: the re-armed wait blocks until another line
    let (got, _) = run_on(c, false, Some(&waiting), &|n| {
        if n == 20 {
            owed(c, "lane: next");
        }
    });
    assert_eq!(got.unwrap(), ["lane: next"]);
    // a second hand-in whose start failed too, after an idle runner's lines: said itself, the first not again
    line(c, "start", &json!({"pid": 9, "why": "make lane-start"}));
    line(c, "stop", &json!({"pid": 9, "why": "idle"}));
    line(
        c,
        "owed",
        &json!({"why": DEAD, "unserved": ["a1b2c3d4e5f6"], "line": "x"}),
    );
    assert_eq!(run(c, false, &nothing).0.unwrap(), ["x"]);
    let two = hand_in("T14", "f6e5d4c3b2a1", "2026-11-28T05:00:00Z");
    ins.borrow_mut().push(two);
    let (got, _) = run_on(c, false, Some(&waiting), &|n| assert!(n < 50));
    assert_eq!(
        got.unwrap(),
        ["lane: the runner is not running and 1 hand-in(s) wait with no batch formed (461 T14 (f6e5d4c3b2); it stopped: idle) - make lane-start starts it"]
    );
    // a live runner serves them: quiet
    let (got, _) = run_on(c, true, Some(&waiting), &|n| {
        if n == 20 {
            owed(c, "lane: live");
        }
    });
    assert_eq!(got.unwrap(), ["lane: live"]);
}

#[test]
fn an_open_batch_or_a_make_lane_stop_over_the_hand_in_says_no_unserved_line() {
    let one = hand_in("T12", "a1b2c3d4e5f6", "2026-11-28T04:00:00Z");
    let later = hand_in("T14", "f6e5d4c3b2a1", "2026-11-28T06:00:00Z");
    let start = json!({"event": "start", "utc": "2026-11-28T03:00:00Z"});
    let stop =
        json!({"event": "stop", "why": "make lane-stop NOW=1", "utc": "2026-11-28T05:00:00Z"});
    // the coordinator stopped the runner over the first on purpose: only the one handed in after is said
    let got = unserved(
        &[start.clone(), stop.clone()],
        &[one.clone(), later.clone()],
    );
    assert_eq!(got, [later.clone()]);
    // a start after that stop: both again
    let restart = json!({"event": "start", "utc": "2026-11-28T07:00:00Z"});
    let both = unserved(&[start.clone(), stop, restart], &[one.clone(), later]);
    assert_eq!(both.len(), 2);
    assert!(super::unserved_line(&[start.clone()], &[one.clone()])
        .ends_with("(killed)) - make lane-start starts it"));
    // a batch open: its own death line says it
    let batch = json!({"event": "batch", "batch": "461-1", "changes": ["a1b2c3d4e5f6"]});
    assert!(unserved(&[start, batch], &[one]).is_empty());
}

fn git(repo: &Path, args: &[&str]) -> String {
    let out = std::process::Command::new("git")
        .arg("-C")
        .arg(repo)
        .args(["-c", "user.name=t", "-c", "user.email=t@t"])
        .args(args)
        .output()
        .unwrap();
    String::from_utf8_lossy(&out.stdout).trim().to_owned()
}

/// The command on a real repository: a done ref and its pool line, `HAND_IN_BASE=origin`, no runner - the hand-in said; read as
/// `make lane` reads it: none once the lane landed it or `origin/main` holds it, none with no pool log.
#[test]
fn the_command_from_phase_2_s_base_says_a_real_hand_in_no_runner_serves() {
    let t = TempDir::new("lane-wake-unserved-cli");
    git(t.path(), &["init", "-q"]);
    git(
        t.path(),
        &["commit", "-q", "--allow-empty", "-m", "461 T12: one"],
    );
    let sha = git(t.path(), &["rev-parse", "HEAD"]);
    let common = t.path().join(".git");
    assert!(waiting_on(&common).is_empty());
    git(t.path(), &["update-ref", "refs/l7r/done/461-T12", &sha]);
    let done = json!({"event": "done", "handed_in": true, "detail": "461 T12", "commit": sha, "utc": "2026-11-28T04:00:00Z"});
    std::fs::write(common.join("builder-pool.log"), format!("{done}\n")).unwrap();
    assert_eq!(waiting_on(&common).len(), 1);
    let env = |k: &str| match k {
        "HAND_IN_BASE" => Some("origin".to_owned()),
        _ => Some("0".to_owned()),
    };
    // phase 1's base, named: no death line, the wait ended by the next line a thread writes
    let writer = {
        let c = common.clone();
        std::thread::spawn(move || {
            std::thread::sleep(std::time::Duration::from_millis(50));
            log::append(
                &c,
                "2026-11-28T04:30:00Z",
                "owed",
                &json!({"line": "lane: phase 1"}),
            )
            .unwrap();
        })
    };
    let quiet = wait_cli(&common, &|k| {
        (k == "HAND_IN_BASE")
            .then(|| "clone".to_owned())
            .or(Some("0.01".to_owned()))
    });
    writer.join().unwrap();
    assert_eq!(quiet.stdout, "lane: phase 1\n");
    assert!(!log::read(&common).iter().any(|l| l["why"] == DEAD));
    // the death owed at once (grace 0); a wait that says none is ended by a line two seconds on, a red rather than a hang
    let late = {
        let c = common.clone();
        std::thread::spawn(move || {
            std::thread::sleep(std::time::Duration::from_secs(2));
            log::append(
                &c,
                "2026-11-28T04:40:00Z",
                "owed",
                &json!({"line": "lane: late"}),
            )
            .unwrap();
        })
    };
    let got = wait_cli(&common, &env);
    late.join().unwrap();
    assert_eq!(got.code, 0);
    assert!(got.stdout.contains(&format!("461 T12 ({})", &sha[..10])));
    // origin/main holds it: landed, nothing waits
    git(t.path(), &["update-ref", "refs/remotes/origin/main", &sha]);
    assert!(waiting_on(&common).is_empty());
    git(t.path(), &["update-ref", "-d", "refs/remotes/origin/main"]);
    // the lane landed it: nothing waits, and origin/main is not asked
    let landed = json!({"batch": "461-1", "landed": [sha]});
    log::append(&common, "2026-11-28T05:00:00Z", "landed", &landed).unwrap();
    assert!(waiting_on(&common).is_empty());
}

/// 461 T63: a later hand-in of the task supersedes an earlier one though it has left the lane - its done ref is deleted only when it
/// is carried or landed, or overwritten by a later hand-in still - so the earlier one, kept on the lane by a stopped batch's line,
/// waits for nothing: the Stop rule's reading (`l7r_shared::lane_wake`), which this crate's did not share.
#[test]
fn a_later_hand_in_off_the_lane_still_supersedes_an_earlier_one_on_it() {
    let t = TempDir::new("lane-wake-superseded-off-lane");
    git(t.path(), &["init", "-q"]);
    for s in ["461 T12: one", "461 T12: two"] {
        git(t.path(), &["commit", "-q", "--allow-empty", "-m", s]);
    }
    let (one, two) = (
        git(t.path(), &["rev-parse", "HEAD~1"]),
        git(t.path(), &["rev-parse", "HEAD"]),
    );
    let common = t.path().join(".git");
    let done = |sha: &str, at: &str| json!({"event": "done", "handed_in": true, "detail": "461 T12", "commit": sha, "utc": at});
    let pool = format!("{}\n{}\n", done(&one, "u1"), done(&two, "u2"));
    std::fs::write(common.join("builder-pool.log"), pool).unwrap();
    log::append(
        &common,
        "u3",
        "batch",
        &json!({"batch": "461-1", "changes": [one]}),
    )
    .unwrap();
    log::append(
        &common,
        "u4",
        "stop",
        &json!({"batch": "461-1", "why": "arbiter"}),
    )
    .unwrap();
    // the later one's ref stands: it waits, the earlier superseded
    git(t.path(), &["update-ref", "refs/l7r/done/461-T12", &two]);
    let waits: Vec<String> = waiting_on(&common).into_iter().map(|h| h.commit).collect();
    assert_eq!(waits, [two]);
    // carried by hand, its ref gone: off the lane, and the earlier one still superseded by it
    git(t.path(), &["update-ref", "-d", "refs/l7r/done/461-T12"]);
    assert!(waiting_on(&common).is_empty());
}
