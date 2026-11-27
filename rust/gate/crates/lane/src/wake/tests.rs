//! The wake-up (feature 461 T20) on a scratch common directory and a clock of its own: the owed lines past the mark printed once
//! and the mark moved, the wait blocking until one comes; a dead runner over an open batch said once a death and only after the
//! grace; the quiet cases - a live runner, no open batch; the command's knobs and its exits.

use std::cell::{Cell, RefCell};
use std::path::Path;

use l7r_shared::tempdir::TempDir;
use serde_json::{json, Value};

use super::{dead, wait, wait_cli, Wait, DEAD};
use crate::log;

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
    // far past the grace a line of its own ends a wait that said nothing, so the old rule's silence is a red, not a hang
    let (got, _) = run(c, false, &|n| {
        if n == 50 {
            owed(c, "past the grace");
        }
    });
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
