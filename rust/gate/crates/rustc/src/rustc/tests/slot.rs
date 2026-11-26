//! The machine-wide build slot (feature 451 T284): N compiling cargo calls at once, the next waits; a dead holder frees its slot; a
//! run under a holder takes none; and no slot to take is never a refusal.

use std::collections::BTreeMap;
use std::io::{BufRead as _, BufReader};
use std::path::Path;
use std::process::{Command, Stdio};
use std::sync::mpsc::{channel, Receiver, Sender};
use std::sync::Mutex;
use std::time::{Duration, Instant};

use super::phases::phases;
use super::runlock::Stepped;
use super::{calls, two_crates, world_with, World};
use crate::checks::scratch;
use crate::rustc::runlock::{Clock, Wall};
use crate::rustc::slot::{around, take, Slots, CEILING, COUNT, DIR, MARK, STEP};
use crate::rustc::{cargo, cargo_in};

pub(super) fn quiet(_: &str) {}

/// The wall clock, telling `waiting` at each sleep: a test lets a slot go only once the waiter is in its wait, however long the host
/// took to start it (a fixed pause raced the waiter's thread under three builders' load).
struct Telling(Wall, Mutex<Sender<()>>);

impl Clock for Telling {
    fn now(&self) -> Duration {
        self.0.now()
    }

    fn sleep(&self, d: Duration) {
        let _ = self.1.lock().unwrap().send(());
        self.0.sleep(d);
    }
}

/// `count` quick slots under `dir` whose waiter tells the receiver each time it finds none free.
pub(super) fn telling(dir: &Path, count: usize) -> (Slots, Receiver<()>) {
    let (tell, waiting) = channel();
    let clock = Telling(Wall(Instant::now()), Mutex::new(tell));
    let slots = Slots {
        clock: Box::new(clock),
        ..quick(dir, count)
    };
    (slots, waiting)
}

/// `count` slots under `dir`, looked at every 10 ms of the wall clock.
pub(super) fn quick(dir: &Path, count: usize) -> Slots {
    Slots {
        poll: Duration::from_millis(10),
        ..Slots::at(dir.to_path_buf(), count)
    }
}

#[test]
fn the_call_past_the_count_waits_and_goes_on_when_a_holder_lets_go() {
    let dir = scratch("slot-count");
    let slots = quick(&dir, 2);
    let first = take(&slots, "one\n", &mut quiet);
    let second = take(&slots, "two\n", &mut quiet);
    // two slots, two holders, neither waited
    assert!(first.hold.is_some() && second.hold.is_some());
    assert!(first.waited.is_none() && second.waited.is_none());
    let (patient, waiting) = telling(&dir, 2);
    let (tell, told) = channel();
    std::thread::scope(|s| {
        s.spawn(|| {
            let _ = tell.send(take(&patient, "three\n", &mut quiet));
        });
        // the third waits for as long as both are held
        waiting.recv_timeout(Duration::from_secs(30)).unwrap();
        assert!(told.try_recv().is_err(), "it has looked and not come back");
        drop(first);
        let third = told.recv_timeout(Duration::from_secs(30)).unwrap();
        assert!(third.hold.is_some(), "the freed slot is the third's");
        assert!(third.waited.is_some(), "and it waited for it");
        // and the slot it took is signed with its name
        let signed: Vec<String> = (0..2)
            .map(|i| std::fs::read_to_string(dir.join(format!("slot-{i}"))).unwrap())
            .collect();
        assert!(signed.contains(&"three\n".to_owned()), "{signed:?}");
        assert!(signed.contains(&"two\n".to_owned()), "{signed:?}");
    });
}

#[test]
fn a_killed_holder_s_slot_is_free() {
    let dir = scratch("slot-killed");
    let file = dir.join("slot-0");
    // another process holds the one slot as the gate holds it - the `flock` of its own open file - and is killed outright
    let mut holder = Command::new("sh")
        .args([
            "-c",
            "exec 9>>\"$1\"; flock -n 9 || exit 1; echo held; exec sleep 600",
            "sh",
        ])
        .arg(&file)
        .stdout(Stdio::piped())
        .spawn()
        .unwrap();
    let mut line = String::new();
    BufReader::new(holder.stdout.take().unwrap())
        .read_line(&mut line)
        .unwrap();
    assert_eq!(line, "held\n");
    let stepped = Slots {
        ceiling: Duration::ZERO,
        clock: Box::new(Stepped::default()),
        ..quick(&dir, 1)
    };
    let refused = take(&stepped, "me\n", &mut quiet);
    assert!(refused.hold.is_none(), "the slot is held while it lives");
    holder.kill().unwrap();
    holder.wait().unwrap();
    let taken = take(&quick(&dir, 1), "me\n", &mut quiet);
    assert!(taken.hold.is_some(), "a SIGKILL leaves nothing to clear");
}

#[test]
fn a_run_under_a_holder_takes_no_slot_and_the_cargo_a_holder_starts_carries_its_mark() {
    let dir = scratch("slot-nested");
    let (root, a, _) = two_crates();
    // the fake cargo notes the mark it was started with, and whether the one slot is held around it
    // (a slot just let go may read held for a moment - a child another test's thread is starting holds a copy of the open file until
    // its exec - so the call that should find it free waits for it, as a waiter's next look does; the two that should find it held
    // do not wait)
    let body = "d=\"$(dirname \"$0\")\"\nWAIT=$(cat \"$d/wait\")\necho \"mark=$L7R_BUILD_SLOT_HELD\" >> \"$d/marks\"\nexec 9>>\"$SLOT\"; flock -w \"$WAIT\" 9 && echo free >> \"$d/marks\"\nexit 0";
    let slot = dir.join("slot-0");
    let world =
        world_with(&root, &body.replace("$SLOT", &slot.display().to_string())).map(|w| World {
            slots: quick(&dir, 1),
            ..w
        });
    let wait = world.target.join("wait");
    let body_wait = |secs: &str| std::fs::write(&wait, secs).unwrap();
    body_wait("0");
    assert_eq!(cargo(&world, &["clippy"], &a, &[]).code, 0);
    assert_eq!(cargo(&world, &["test", "--no-run"], &a, &[]).code, 0);
    body_wait("30");
    // `cargo fmt` compiles nothing: no slot (its mark is whatever this test's own process was started with - under a `cargo test`
    // that holds a slot, the holder's)
    assert_eq!(cargo(&world, &["fmt", "--check"], &a, &[]).code, 0);
    let marks = std::fs::read_to_string(world.target.join("marks")).unwrap();
    let marks: Vec<&str> = marks.lines().collect();
    assert_eq!(marks[..2], ["mark=1", "mark=1"], "{marks:?}");
    assert_eq!((marks.len(), marks[3]), (4, "free"), "{marks:?}");
    assert_eq!(calls(&world).len(), 3);
    // a gate run started under the mark has no slots at all: with the one slot held, its take is at once and holds nothing, so a
    // crate's tests that run the checks never wait on the slot their own `cargo test` holds
    let held = take(&world.slots, "outer\n", &mut quiet);
    assert!(held.hold.is_some());
    let env = |k: &str| match k {
        MARK | COUNT => Some("1".to_owned()),
        DIR => Some(dir.display().to_string()),
        _ => None,
    };
    let inner = Slots::of(&env, Path::new("/home/x"));
    assert_eq!(inner.count, 0);
    let nested = take(&inner, "inner\n", &mut quiet);
    assert!(nested.hold.is_none() && nested.waited.is_none());
    // and its own cargo calls run: nothing of the slot is asked
    body_wait("0");
    let under = world.map(|w| World { slots: inner, ..w });
    assert_eq!(cargo_in(&under, &["test"], &a, &[], None).code, 0);
    drop(held);
}

#[test]
fn the_knobs_are_read_from_the_run_s_environment() {
    let home = Path::new("/home/x");
    let plain = Slots::of(&|_| None, home);
    assert_eq!(plain.count, 2, "the default");
    assert_eq!(plain.dir, home.join(".cache/l7r-build-slots"));
    assert_eq!(plain.ceiling, Duration::from_secs(900));
    assert_eq!(plain.notice, Duration::from_secs(60));
    let set = |k: &str| match k {
        COUNT => Some("5".to_owned()),
        DIR => Some("/elsewhere".to_owned()),
        CEILING => Some("7".to_owned()),
        _ => None,
    };
    let knobs = Slots::of(&set, home);
    assert_eq!(
        (knobs.count, knobs.dir.as_path(), knobs.ceiling),
        (5, Path::new("/elsewhere"), Duration::from_secs(7))
    );
    // no number, or nothing, is the default; zero is no slot, and nothing is made or asked
    let blank = |k: &str| (k == COUNT || k == CEILING || k == MARK).then(|| " ".to_owned());
    assert_eq!(Slots::of(&blank, home).count, 2);
    let words = |k: &str| (k == COUNT || k == CEILING).then(|| "many".to_owned());
    let worded = Slots::of(&words, home);
    assert_eq!(
        (worded.count, worded.ceiling),
        (2, Duration::from_secs(900))
    );
    let dir = scratch("slot-zero");
    let zero = |k: &str| match k {
        COUNT => Some("0".to_owned()),
        DIR => Some(dir.join("slots").display().to_string()),
        _ => None,
    };
    let off = take(&Slots::of(&zero, home), "me\n", &mut quiet);
    assert!(off.hold.is_none() && off.waited.is_none());
    assert!(!dir.join("slots").exists());
    assert_eq!(Slots::off().count, 0);
}

#[test]
fn a_wait_is_said_each_minute_and_past_the_ceiling_the_call_runs_without_a_slot() {
    let dir = scratch("slot-wait");
    let who = "t270 (pid 7, make closing-checks): cargo test --no-run";
    let held = take(&quick(&dir, 1), &format!("{who}\n"), &mut quiet);
    assert!(held.hold.is_some());
    // a stepped clock: a look every 30 s, a line each minute, the ceiling at 150 s
    let slots = Slots {
        ceiling: Duration::from_secs(150),
        poll: Duration::from_secs(30),
        clock: Box::new(Stepped::default()),
        ..quick(&dir, 1)
    };
    let mut said = Vec::new();
    let taken = take(&slots, "me\n", &mut |l| said.push(l.to_owned()));
    assert!(taken.hold.is_none());
    assert_eq!(taken.waited, Some(Duration::from_secs(150)));
    let waiting = |s: u64| {
        format!("rust-checks: waiting on a build slot, {s} s so far - 1 compiling cargo call(s) run at once on this machine (L7R_BUILD_SLOTS, feature 451 T284); held by: {who}\n")
    };
    assert_eq!(
        said,
        [
            waiting(60),
            waiting(120),
            format!("rust-checks: waited 150 s on a build slot, the ceiling (L7R_BUILD_SLOT_CEILING seconds) - this cargo call runs without one; held by: {who}\n"),
        ]
    );
}

#[test]
fn no_slots_to_take_is_said_and_the_call_runs() {
    let dir = scratch("slot-broken");
    let mut said = Vec::new();
    // no `flock` program
    let no_flock = Slots {
        flock: "/nonexistent/flock".to_owned(),
        ..quick(&dir, 1)
    };
    let taken = take(&no_flock, "me\n", &mut |l| said.push(l.to_owned()));
    assert!(taken.hold.is_none());
    // a slot directory that cannot be made
    std::fs::write(dir.join("file"), "").unwrap();
    let no_dir = quick(&dir.join("file/slots"), 1);
    let taken = take(&no_dir, "me\n", &mut |l| said.push(l.to_owned()));
    assert!(taken.hold.is_none());
    // a slot file that cannot be opened
    std::fs::create_dir_all(dir.join("dirs/slot-0")).unwrap();
    let no_file = quick(&dir.join("dirs"), 1);
    let taken = take(&no_file, "me\n", &mut |l| said.push(l.to_owned()));
    assert!(taken.hold.is_none() && taken.waited.is_none());
    assert_eq!(said.len(), 3, "{said:?}");
    let whys = [
        "cannot run /nonexistent/flock: ",
        "cannot make ",
        "cannot open ",
    ];
    for (line, why) in said.iter().zip(whys) {
        assert!(
            line.starts_with(&format!("rust-checks: no build slot to take ({why}"))
                && line.ends_with(" - this cargo call runs without one (feature 451 T284)\n"),
            "{line}"
        );
    }
}

#[test]
fn a_call_that_waited_writes_its_wait_as_a_phase_line_and_one_that_did_not_writes_none() {
    let dir = scratch("slot-phase");
    let (root, _, _) = two_crates();
    let world = world_with(&root, "exit 0").map(|w| World {
        slots: quick(&dir, 1),
        ..w
    });
    let args = [
        "test".to_owned(),
        "--no-run".to_owned(),
        "--quiet".to_owned(),
    ];
    let mut env = BTreeMap::new();
    let held = around(&world, &args, &mut env);
    assert!(held.is_some());
    assert_eq!(env.get(MARK).map(String::as_str), Some("1"));
    assert_eq!(phases(&root).len(), 0, "no wait, no line");
    let signed = std::fs::read_to_string(dir.join("slot-0")).unwrap();
    let tree = root.file_name().unwrap().to_string_lossy().into_owned();
    let pid = std::process::id();
    assert_eq!(
        signed,
        format!("{tree} (pid {pid}, make static): cargo test --no-run\n")
    );
    // the slot held, a second call waits to its ceiling (none here) and runs without: its wait is one `slot-wait` line, code 1
    let waiter = world.map(|w| World {
        slots: Slots {
            ceiling: Duration::ZERO,
            ..quick(&dir, 1)
        },
        ..w
    });
    let mut env = BTreeMap::new();
    assert!(around(&waiter, &args, &mut env).is_none());
    assert!(env.is_empty(), "no slot, no mark");
    let lines = phases(&root);
    assert_eq!(lines.len(), 1, "{lines:?}");
    assert_eq!(lines[0]["src"], "rust");
    assert_eq!(lines[0]["step"], STEP);
    assert_eq!(lines[0]["code"], 1);
    assert_eq!(lines[0]["make"], "static");
    assert_eq!(lines[0]["crates"], serde_json::json!([]));
    // a wait that ends with the slot is code 0
    drop(held);
    // (taken by a taker that waits: a slot just let go may read held for a moment, as the nested test says)
    let again = take(&quick(&dir, 1), "holder\n", &mut quiet).hold;
    assert!(again.is_some());
    let (slots, waiting) = telling(&dir, 1);
    let patient = waiter.map(|w| World { slots, ..w });
    let (tell, told) = channel();
    std::thread::scope(|s| {
        s.spawn(|| {
            let mut env = BTreeMap::new();
            let got = around(&patient, &args, &mut env);
            let _ = tell.send(got.is_some());
        });
        waiting.recv_timeout(Duration::from_secs(30)).unwrap();
        assert!(told.try_recv().is_err());
        drop(again);
        assert!(told.recv_timeout(Duration::from_secs(30)).unwrap());
    });
    let lines = phases(&root);
    assert_eq!(lines.len(), 2, "{lines:?}");
    assert_eq!(lines[1]["code"], 0);
}
