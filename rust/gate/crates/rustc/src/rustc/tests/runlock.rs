//! One run at a time in a target directory (feature 451 T23).

use std::path::Path;
use std::sync::atomic::{AtomicU64, Ordering};
use std::time::{Duration, Instant};

use serde_json::json;

use super::{two_crates, world_with};
use crate::checks::scratch;
use crate::rustc::locked_dispatch;
use crate::rustc::runlock::{
    ceiling_of, dirs_of, mutex, run_of, take, Clock, Proc, Taker, Wall, MUTEX, RECORD,
};

/// A fake cargo that notes when it is entered while another call is inside it: `mkdir` is atomic, so of two calls at once one finds
/// the directory made.
const OVERLAP: &str = "d=\"$(dirname \"$0\")\"\nif mkdir \"$d/busy\" 2>/dev/null; then sleep 0.1; rmdir \"$d/busy\"; else echo overlap >> \"$d/overlaps\"; sleep 0.1; fi\nexit 0";

/// This process: its pid and its start, read as the lock reads them.
fn me() -> Proc {
    let pid = u64::from(std::process::id());
    let text = std::fs::read_to_string(format!("/proc/{pid}/stat")).unwrap();
    let start = text[text.rfind(')').unwrap() + 1..]
        .split_whitespace()
        .nth(19)
        .unwrap()
        .parse()
        .unwrap();
    Proc { pid, start }
}

/// A taker of run `run` in this process, under the live `/proc`, quick to give up.
fn taker(run: u64, ceiling_ms: u64) -> Taker {
    Taker {
        proc_root: "/proc".into(),
        run: Proc { pid: run, start: 7 },
        run_what: format!("make run-{run}"),
        me: me(),
        ceiling: Duration::from_millis(ceiling_ms),
        poll: Duration::from_millis(10),
        say_every: Duration::ZERO,
        mutex_s: 5.0,
        clock: Box::new(Wall(Instant::now())),
    }
}

/// A clock that moves only when slept on, by the sleep (feature 451 T35): a wait's lines are counted against the ceiling over the
/// poll, not against how long the host took to run them. A wait that never ends reads it past `READS` and panics, not hangs.
#[derive(Default)]
pub(super) struct Stepped {
    at_ns: AtomicU64,
    reads: AtomicU64,
}

const READS: u64 = 100;

impl Clock for Stepped {
    fn now(&self) -> Duration {
        let n = self.reads.fetch_add(1, Ordering::Relaxed);
        assert!(
            n < READS,
            "the wait read the clock {READS} times: it never ended"
        );
        Duration::from_nanos(self.at_ns.load(Ordering::Relaxed))
    }

    fn sleep(&self, d: Duration) {
        self.at_ns
            .fetch_add(u64::try_from(d.as_nanos()).unwrap(), Ordering::Relaxed);
    }
}

/// A live member of run `run` written into `dir`'s record: this process, as another run's check would be.
fn stage(dir: &Path, run: u64, start: u64) {
    let m = me();
    std::fs::write(
        dir.join(RECORD),
        json!({"members": [{"token": "staged", "pid": m.pid, "start": start, "run": {"pid": run, "start": 7},
            "run_what": "make static", "cmd": "cover", "t": 0.0}]})
        .to_string(),
    )
    .unwrap();
}

#[test]
fn two_runs_in_one_target_directory_take_turns() {
    let (root, _, _) = two_crates();
    let mut world = world_with(&root, OVERLAP);
    world.no_reuse = true;
    let args = vec!["lint".to_owned()];
    let (a, b) = (taker(900_001, 60_000), taker(900_002, 60_000));
    std::thread::scope(|s| {
        for t in [&a, &b] {
            let (world, args) = (&world, &args);
            s.spawn(move || locked_dispatch(world, args, t));
        }
    });
    let calls = std::fs::read_to_string(world.target.join("calls")).unwrap_or_default();
    assert!(
        calls.lines().count() >= 4,
        "each run called cargo on both crates: {calls}"
    );
    let overlaps = std::fs::read_to_string(world.target.join("overlaps")).unwrap_or_default();
    assert_eq!(overlaps, "", "two runs were inside cargo at once");
    // each left the record as it found it
    let record = std::fs::read_to_string(world.target.join(RECORD)).unwrap();
    assert_eq!(record, r#"{"members":[]}"#);
}

#[test]
fn a_check_of_the_same_run_joins_without_waiting() {
    let dir = scratch("runlock-join");
    stage(&dir, 900_003, me().start);
    let t = taker(900_003, 0);
    let mut said = Vec::new();
    let held = take(&[dir.to_path_buf()], &t, "test-counters", &mut |l| {
        said.push(l.to_owned());
    });
    assert!(held.is_ok());
    assert!(said.is_empty(), "{said:?}");
    let record = std::fs::read_to_string(dir.join(RECORD)).unwrap();
    assert_eq!(record.matches("\"pid\":900003").count(), 2, "{record}");
    drop(held);
    let record = std::fs::read_to_string(dir.join(RECORD)).unwrap();
    assert!(
        record.contains("staged") && record.matches("token").count() == 1,
        "{record}"
    );
}

#[test]
fn another_runs_holder_is_waited_for_named_and_past_the_ceiling_refused() {
    let dir = scratch("runlock-wait");
    stage(&dir, 900_004, me().start);
    let t = Taker {
        clock: Box::new(Stepped::default()),
        ..taker(900_005, 60)
    };
    let mut said = Vec::new();
    let held = take(&[dir.to_path_buf()], &t, "cover", &mut |l| {
        said.push(l.to_owned());
    });
    let why = held.err().unwrap();
    // a 60 ms ceiling at a 10 ms poll: waited 0, 10, ... 50 ms, a line each at say_every 0, refused at 60
    assert_eq!(said.len(), 6, "said each poll at say_every 0: {said:?}");
    assert!(
        said[0].starts_with("rust-checks: waiting 0 s for "),
        "{}",
        said[0]
    );
    let pid = me().pid;
    let named = format!("held by pid {pid} (`rust cover`), of the run `make static` (pid 900004), since 00:00:00 UTC");
    assert!(said[0].contains(&named), "{}", said[0]);
    assert!(why.starts_with("rust-checks: REFUSED - "), "{why}");
    assert!(
        why.contains("still held after 0 s by pid") && why.contains("`kill 900004`"),
        "{why}"
    );
}

#[test]
fn a_member_whose_process_is_gone_holds_nothing() {
    let dir = scratch("runlock-dead");
    // this pid, but another start: a pid the kernel gave to another process
    stage(&dir, 900_006, me().start + 1);
    let t = taker(900_007, 0);
    assert!(take(&[dir.to_path_buf()], &t, "lint", &mut |_| {}).is_ok());
}

#[test]
fn a_refusal_is_the_checks_reply_and_a_usage_error_takes_no_lock() {
    let (root, _, _) = two_crates();
    let world = world_with(&root, "exit 0");
    stage(&world.target, 900_008, me().start);
    // waited on (said on stderr) for 30 ms, then refused
    let reply = locked_dispatch(&world, &["dead".to_owned()], &taker(900_009, 30));
    let t = taker(900_009, 0);
    assert_eq!(reply.code, 1);
    assert!(reply.stderr.contains("REFUSED"), "{}", reply.stderr);
    // `test-times` is a check too; a word that is none is the usage, with the holder still there
    let reply = locked_dispatch(
        &world,
        &[
            "test-times".to_owned(),
            "--crate".to_owned(),
            "rust/a".to_owned(),
        ],
        &t,
    );
    assert!(reply.stderr.contains("REFUSED"), "{}", reply.stderr);
    let reply = locked_dispatch(&world, &["nothing".to_owned()], &t);
    assert_eq!(reply.code, 2);
}

#[test]
fn the_run_is_the_outermost_make_above_the_process() {
    let proc_root = scratch("runlock-proc");
    // 50 l7r-rust <- 40 sh <- 30 make static <- 20 make done <- 10 bash <- 1
    for (pid, comm, ppid, line) in [
        (50, "l7r-rust", 40, "l7r-rust\0cover\0"),
        (40, "sh", 30, "sh\0-c\0x\0"),
        (30, "make", 20, "make\0static\0"),
        (20, "make", 10, "make\0NOTE=two words\0done\0"),
        (10, "bash (x)", 1, "bash\0"),
    ] {
        let d = proc_root.join(pid.to_string());
        std::fs::create_dir_all(&d).unwrap();
        std::fs::write(d.join("comm"), format!("{comm}\n")).unwrap();
        let rest: Vec<String> = (0..20).map(|i| (pid * 100 + i).to_string()).collect();
        std::fs::write(
            d.join("stat"),
            format!("{pid} ({comm}) S {ppid} {}\n", rest[2..].join(" ")),
        )
        .unwrap();
        std::fs::write(d.join("cmdline"), line).unwrap();
    }
    let (run, what) = run_of(&proc_root, 50);
    // a word holding a space is quoted, so the run's target is read past it (feature 451 T05)
    assert_eq!((run.pid, what.as_str()), (20, "make 'NOTE=two words' done"));
    assert_eq!(super::super::phase::run_target(&what, "test"), "done");
    assert_eq!(run.start, 2019);
    // a make's own shell is of the same run; a make is its own outermost one
    assert_eq!(run_of(&proc_root, 40).0.pid, 20);
    assert_eq!(run_of(&proc_root, 20).0.pid, 20);
    // no make above: the process is its own run
    let (run, what) = run_of(&proc_root, 10);
    assert_eq!((run.pid, run.start, what.as_str()), (10, 1019, "bash"));
    // a process with no record is its own run, its start unknown
    let (run, _) = run_of(&proc_root, 99);
    assert_eq!((run.pid, run.start), (99, 0));
}

#[test]
fn every_directory_a_run_writes_is_taken_once_in_order() {
    let (root, _, _) = two_crates();
    let mut world = world_with(&root, "exit 0");
    assert_eq!(dirs_of(&world), [world.target.clone()]);
    world.target_override = Some("/b".to_owned());
    world.cover_work = Some("/a".into());
    assert_eq!(
        dirs_of(&world),
        ["/a".into(), "/b".into(), world.target.clone()]
    );
    world.cover_work = Some(world.target.clone());
    assert_eq!(dirs_of(&world).len(), 2);
}

#[test]
fn a_directory_that_cannot_be_made_or_locked_is_said() {
    let dir = scratch("runlock-bad");
    let file = dir.join("file");
    std::fs::write(&file, "").unwrap();
    let t = taker(900_010, 0);
    let why = take(&[file.join("under")], &t, "lint", &mut |_| {})
        .err()
        .unwrap();
    assert!(why.starts_with("rust-checks: cannot make "), "{why}");
    let why = mutex(&file, 0.1).err().unwrap();
    assert!(why.contains("cannot open the lock record"), "{why}");
    // the record's own lock held elsewhere: said, not waited on forever
    let _other = l7r_shared::tool::flock_within(&dir.join(MUTEX), 1.0)
        .unwrap()
        .unwrap();
    let why = mutex(&dir, 0.05).err().unwrap();
    assert!(why.contains("was held past 0.05 s"), "{why}");
}

#[test]
fn the_ceiling_is_a_knob_in_seconds() {
    assert_eq!(ceiling_of(Some("90")), Duration::from_secs(90));
    assert_eq!(ceiling_of(Some("soon")), Duration::from_secs(1800));
    assert_eq!(ceiling_of(None), Duration::from_secs(1800));
}

#[test]
fn a_one_file_format_takes_no_lock_and_never_waits_on_another_run() {
    let (root, _, _) = two_crates();
    let world = world_with(&root, "exit 0");
    crate::write_executable(&world.path_dir.join("rustfmt"), "#!/bin/sh\ncat\n");
    stage(&world.target, 900_010, me().start);
    // another run holds the target directory: a check is refused at once (ceiling 0), the one-file format runs
    let held = locked_dispatch(&world, &["dead".to_owned()], &taker(900_011, 0));
    assert!(held.stderr.contains("REFUSED"), "{}", held.stderr);
    let words = ["format", "--file", "rust/a/src/lib.rs"].map(str::to_owned);
    let done = locked_dispatch(&world, &words, &taker(900_011, 0));
    assert_eq!(done.code, 0, "{}", done.stderr);
    assert!(done.stdout.contains("already formatted"), "{}", done.stdout);
}
