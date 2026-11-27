//! THE LANE'S RUNNER (feature 461 T12, plan D2, data-model.md "Recovery"): ONE detached `l7r-gate lane --work <common>` a clone, as
//! `make page-session`'s runner starts `page-session --work` (`pages`' `runner.rs`). `make lane-start` - and, from phase 2's base, every
//! hand-in ([`on_hand_in`]) - starts it through `setsid`, so it has a session and a process group of its own, its standard streams
//! `/dev/null` and none of the caller's descriptors (a caller reading the start through a pipe would otherwise wait for the RUNNER to
//! end, as the page-session launch's first run did). It holds `l7r-lane/lane.lock` of the git common directory by `flock`; the lock is
//! the truth of whether a runner lives, and the pid written into the file is read only while the lock is held, so a stale pid from a
//! killed runner never names a live one. A second start finds the lock held and is a no-op naming the first's pid.
//!
//! ITS LOOP ([`work`]), each [`POLL_S`]: a stop request naming this runner ends it; a hand-in the runner has not seen moves the idle
//! clock; the batch step runs (T14's [`run::step`]: forms D5's batch where none is open and runs it); and [`LANE_IDLE_S`] with no
//! new hand-in and no batch run ends it. The clock runs from the newest hand-in, not from "nothing waiting", so a runner over a
//! hand-in it cannot yet batch still idles out. Every start and stop is a line of the lane's log, with `pid` and `why` and never a
//! `batch` field: `log::state_of` reads a `stop` naming a batch as that batch `stopped`, which Recovery skips.
//!
//! RECOVERY: at start the log's last batch, where open (neither `landed` nor `stopped`), is handed to the resume step with the
//! changes its own lines leave ([`remaining`]: not ejected); the production step asks `origin/main` too and runs them as a new attempt
//! on the tree brought to `origin/main` again ([`run::resume`], T14). Its `start` line says `resume <batch>`.
//!
//! THE STOP ([`stop`], `make lane-stop`): a request file naming the runner's pid, which the runner reads between batches, so the batch
//! in flight finishes first; the stop waits [`STOP_WAIT_S`] for it and otherwise says it is asked. `NOW=1` ends the runner's process
//! group at once (TERM, then KILL past the wait), as `make land-stop` stops a landing, and the STOPPER writes the `stop` line, which
//! the killed runner cannot; its open batch is resumed at the next start. A request no runner read (it was killed) names a pid that is
//! not the next runner's, which drops it at its start.

use std::collections::BTreeSet;
use std::fmt::Write as _;
use std::io::{Seek as _, Write as _};
use std::path::{Path, PathBuf};
use std::time::{Duration, Instant, SystemTime};

use l7r_gate_core::Reply;
use l7r_shared::tool::{flock, flock_within};
use serde_json::json;

use crate::log::{self, Batch};

pub mod run;

/// The runner's lock, in the lane's directory.
pub const LOCK: &str = "lane.lock";
/// The stop request `make lane-stop` leaves for the runner, in the lane's directory.
pub const STOP: &str = "stop-request";
/// GUESS knob (`LANE_IDLE_S`, plan D2; `dev/audits/lane-runner.md`): the seconds with no hand-in after which the runner ends. A stopped
/// runner costs one restart at the next hand-in (which starts it again), a running idle one a sleeping process; an hour keeps it up
/// across a builder's usual stretch between hand-ins without leaving it overnight.
pub const LANE_IDLE_S: f64 = 3600.0;
/// GUESS knob (`LANE_POLL_S`): the loop's period. A hand-in waits at most this long to be seen, against a gate of minutes; each tick
/// reads the pool's log, the done refs and the lane's log.
pub const POLL_S: f64 = 5.0;
/// GUESS: how long a start waits for the runner it spawned to hold the lock before it says it failed - from the spawn to the lock
/// only: the launcher's rebuild of a stale `l7r-gate` runs before the spawn and is waited for whole ([`prebuild`], 461 T51).
pub const START_WAIT_S: f64 = 5.0;
/// The launcher's file name (`scripts/gates/l7r-gate.sh`): a runner program so named is built before the spawn ([`prebuild`]).
pub const LAUNCHER: &str = "l7r-gate.sh";
/// How long the runner tries for its lock before it leaves to the runner holding it: a probe of [`held`] (a start's, a stop's)
/// takes the lock for an instant when it is free, so a single try could lose to it and leave no runner (a GUESS bound, past any
/// probe's few milliseconds).
pub const TAKE_S: f64 = 1.0;
/// GUESS: how long a stop waits for the runner to end - after the batch in flight, or after TERM before KILL with `NOW=1`.
pub const STOP_WAIT_S: f64 = 10.0;

/// The lock's path under the git common directory `common`.
#[must_use]
pub fn lock_path(common: &Path) -> PathBuf {
    common.join(log::DIR).join(LOCK)
}

/// The stop request's path under `common`.
#[must_use]
pub fn stop_path(common: &Path) -> PathBuf {
    common.join(log::DIR).join(STOP)
}

/// Whether a runner holds the lock: the file opened (never made) and [`free`] asked of it.
#[must_use]
pub fn held(common: &Path) -> bool {
    std::fs::File::open(lock_path(common)).is_ok_and(|f| !free(&f))
}

/// The probe: the lock asked for at once on `f`; true where it was got, and then let go at once by `flock -u` rather than by the
/// file's close, which frees it only once every copy of the descriptor is closed - and a child another thread of the caller forks
/// holds one until its `exec` (461 T14: the runner's tests read a runner that had ended, 2 runs in 10 under load).
fn free(f: &std::fs::File) -> bool {
    let got = flock(f, "-n");
    if got {
        let _ = flock(f, "-u");
    }
    got
}

/// The runner's lock let go by `flock -u` before the file closes, for [`free`]'s reason: a copy of the descriptor in a child forked
/// meanwhile would otherwise hold it past the runner's end.
fn release(lock: std::fs::File) {
    let _ = flock(&lock, "-u");
    drop(lock);
}

/// The live runner's pid: the lock held, and the pid it wrote there.
#[must_use]
pub fn holder(common: &Path) -> Option<u32> {
    if !held(common) {
        return None;
    }
    std::fs::read_to_string(lock_path(common))
        .ok()?
        .trim()
        .parse()
        .ok()
}

/// The runner's command line, which the stall watchdog matches exactly (`stall_watchdog_hooks/pass.rs`, `runs_lane`).
#[must_use]
pub fn argv(exe: &Path, common: &Path) -> Vec<String> {
    vec![
        exe.to_string_lossy().into_owned(),
        "lane".to_owned(),
        "--work".to_owned(),
        common.to_string_lossy().into_owned(),
    ]
}

fn reply(stdout: String, stderr: String, code: i32) -> Reply {
    Reply {
        stdout,
        stderr,
        code,
    }
}

/// Wait up to `secs` for `done`, asking it every 20 ms and at least once.
fn within(secs: f64, done: impl Fn() -> bool) -> bool {
    let end = Instant::now() + Duration::from_secs_f64(secs.max(0.0));
    loop {
        if done() {
            return true;
        }
        if Instant::now() >= end {
            return false;
        }
        std::thread::sleep(Duration::from_millis(20));
    }
}

/// Every descriptor past the standard three marked close-on-exec, so the detached runner holds none of the caller's (`pages`'
/// `runner::close_inherited`, the same measured reason).
fn close_inherited() {
    extern "C" {
        fn fcntl(fd: i32, cmd: i32, arg: i32) -> i32;
    }
    let fds: Vec<i32> = std::fs::read_dir("/proc/self/fd")
        .map(|d| {
            d.filter_map(Result::ok)
                .filter_map(|e| e.file_name().to_str()?.parse().ok())
                .collect()
        })
        .unwrap_or_default();
    for fd in fds.into_iter().filter(|fd| *fd > 2) {
        // SAFETY: F_SETFD (2) sets only the descriptor's close-on-exec flag (FD_CLOEXEC, 1); a descriptor gone already is an EBADF
        unsafe {
            fcntl(fd, 2, 1);
        }
    }
}

/// The runner's spawn: `launcher` over `words`, from the common directory `words` ends in, its standard streams `/dev/null`, and
/// none of [`run::STRIPPED`] inherited (461 T14, T12's "For T14": a runner a hand-in started kept `make builder-done`'s `MSG`,
/// `GUARD`, `T`, `F` and `L7R_GATE_TREE` for its life, and `T` and `F` would reach the `make land` it runs).
fn spawn_command(launcher: &str, words: &[String]) -> std::process::Command {
    let mut c = std::process::Command::new(launcher);
    c.args(words)
        .current_dir(words.last().map_or(".", String::as_str))
        .stdin(std::process::Stdio::null())
        .stdout(std::process::Stdio::null())
        .stderr(std::process::Stdio::null());
    for k in run::STRIPPED {
        c.env_remove(k);
    }
    c
}

/// THE PROGRAM THE RUNNER RUNS (461 T14, T12's "For T14"): the lane's tree's own `scripts/gates/l7r-gate.sh` - which builds that
/// tree's `l7r-gate` where stale and `exec`s it, so the runner's argv is still `<target>/tool/l7r-gate lane --work <common>`, the
/// stall watchdog's - where the pool's registry holds a lane's tree with the script; else `fallback`, the caller's binary (no lane's
/// tree adopted yet: phase 1, or a scratch repository). The caller's own was the pool tree's build, rebuilt or recycled under it.
#[must_use]
pub fn runner_exe(common: &Path, fallback: &Path) -> PathBuf {
    l7r_shared::builder_pool::read_all(common)
        .into_iter()
        .find(l7r_shared::builder_pool::Tree::lane)
        .map(|t| t.tree.join("scripts/gates/l7r-gate.sh"))
        .filter(|p| p.is_file())
        .unwrap_or_else(|| fallback.to_path_buf())
}

/// THE BUILD BEFORE THE SPAWN (461 T51): where `exe` is the launcher ([`LAUNCHER`], [`runner_exe`]'s choice), it is run first as
/// `L7R_GATE_PRINT_FRESH=1 <exe>`, in the foreground, with the spawn's environment ([`run::STRIPPED`] removed) and neither
/// `L7R_GATE_STALE_OK` nor `L7R_GATE_NO_BUILD` (each would make it build nothing), so it builds the lane tree's `l7r-gate` where
/// stale and the spawned launcher finds it fresh and `exec`s at once. Why: the launcher rebuilds that binary after every reset of
/// the lane's tree that moved its sources - measured 2026-11-27 on a scratch clone with a copy of the lane tree's build cache, under a
/// load of 27 to 46 on 22 cores: 2.2 s and 15.0 s across single landed commits, 112 s across a day's commits, 102 s for a tree
/// whose every source was new (as a tree made again is) - while the start waited [`START_WAIT_S`] (5 s) from the spawn and then said
/// "holds no lock" of a runner that came up after its build. Waiting on the detached child instead would hide a failed build, its
/// standard streams `/dev/null`; here cargo's words reach the caller. Any other `exe` (the caller's binary) builds nothing. `Err` is
/// the reply's stderr.
fn prebuild(exe: &Path) -> Result<(), String> {
    if exe.file_name().and_then(|n| n.to_str()) != Some(LAUNCHER) {
        return Ok(());
    }
    let mut c = std::process::Command::new(exe);
    c.env("L7R_GATE_PRINT_FRESH", "1")
        .env_remove("L7R_GATE_STALE_OK")
        .env_remove("L7R_GATE_NO_BUILD")
        .stdin(std::process::Stdio::null());
    for k in run::STRIPPED {
        c.env_remove(k);
    }
    let out = c
        .output()
        .map_err(|e| format!("lane: {}: {e}\n", exe.display()))?;
    if out.status.success() {
        return Ok(());
    }
    Err(format!(
        "lane: the runner's program could not be built (exit {}), so no runner started - fix what it says and run make lane-start again (`L7R_GATE_PRINT_FRESH=1 {}` builds it alone):\n{}",
        out.status.code().unwrap_or(-1),
        exe.display(),
        String::from_utf8_lossy(&out.stderr)
    ))
}

/// `make lane-start`: the runner of `common` started detached through `launcher`, or the one running named. Exit 0 either way; 1
/// where the runner's program could not be built ([`prebuild`]), the spawn failed or the runner took no lock within `wait_s`.
#[must_use]
pub fn start(common: &Path, exe: &Path, launcher: &str, wait_s: f64) -> Reply {
    if let Some(pid) = holder(common) {
        return reply(
            format!("lane: the runner already runs (pid {pid})\n"),
            String::new(),
            0,
        );
    }
    if let Err(e) = prebuild(exe) {
        return reply(String::new(), e, 1);
    }
    let _ = std::fs::create_dir_all(common.join(log::DIR));
    close_inherited();
    let words = argv(exe, common);
    let spawned = spawn_command(launcher, &words).spawn();
    if let Err(e) = spawned {
        return reply(String::new(), format!("lane: {launcher}: {e}\n"), 1);
    }
    if within(wait_s, || holder(common).is_some()) {
        let pid = holder(common).unwrap_or_default();
        return reply(
            format!("lane: the runner started (pid {pid})\n"),
            String::new(),
            0,
        );
    }
    reply(
        String::new(),
        format!(
            "lane: started `{}`, but it holds no lock after {wait_s} s - run make lane-start again; a second failure is the runner's own (run `{}` by hand to see why)\n",
            words.join(" "),
            words.join(" ")
        ),
        1,
    )
}

/// `kill -<sig> -- -<pgid>`: the runner's whole process group, its gate's children with it.
fn kill_group(sig: &str, pid: u32) {
    let _ = std::process::Command::new("kill")
        .args([&format!("-{sig}"), "--", &format!("-{pid}")])
        .stdout(std::process::Stdio::null())
        .stderr(std::process::Stdio::null())
        .status();
}

/// `make lane-stop` (`now` false): the runner asked to end after its batch in flight, waited for `wait_s`; `NOW=1` (`now`): its
/// process group ended at once and its `stop` line written here. Exit 0; with no runner, says so.
#[must_use]
pub fn stop(common: &Path, now: bool, wait_s: f64) -> Reply {
    let Some(pid) = holder(common) else {
        return reply("lane: no runner\n".to_owned(), String::new(), 0);
    };
    if now {
        kill_group("TERM", pid);
        if !within(wait_s, || !held(common)) {
            kill_group("KILL", pid);
            within(wait_s, || !held(common));
        }
        let fields = json!({"pid": pid, "why": "make lane-stop NOW=1"});
        let wrote = log::append(
            common,
            &l7r_gate_core::record::repo::utc_now(),
            "stop",
            &fields,
        );
        return reply(
            format!("lane: the runner (pid {pid}) stopped at once (NOW=1)\n"),
            wrote.err().unwrap_or_default(),
            0,
        );
    }
    if let Err(e) = std::fs::write(stop_path(common), pid.to_string()) {
        return reply(
            String::new(),
            format!("lane: {}: {e}\n", stop_path(common).display()),
            1,
        );
    }
    let mut out = String::new();
    if within(wait_s, || !held(common)) {
        let _ = writeln!(
            out,
            "lane: the runner (pid {pid}) stopped after its batch in flight"
        );
    } else {
        let _ = writeln!(
            out,
            "lane: the runner (pid {pid}) is asked to stop; it ends after the batch in flight (make lane shows it; make lane-stop NOW=1 ends it at once)"
        );
    }
    reply(out, String::new(), 0)
}

/// The resume seam: an open batch and the changes its lines leave.
pub type Resume<'a> = dyn FnMut(&Batch, &[String]) -> Result<(), String> + 'a;

/// What one runner's loop reads and calls, handed in so a test drives it on a clock of its own.
pub struct Run<'a> {
    pub common: &'a Path,
    pub pid: u32,
    pub idle_s: f64,
    pub poll_s: f64,
    /// Seconds since the epoch.
    pub now: &'a dyn Fn() -> f64,
    pub sleep: &'a dyn Fn(f64),
    /// The commits of every hand-in on the lane now.
    pub hand_ins: &'a dyn Fn() -> BTreeSet<String>,
    /// Recovery: the open batch of a killed runner and the changes its lines leave.
    pub resume: &'a mut Resume<'a>,
    /// One batch step (T14): true when it ran a batch.
    pub step: &'a mut dyn FnMut() -> Result<bool, String>,
}

/// Two names of one commit: equal, or one a prefix of the other (a run's `set` holds short shas).
fn same(a: &str, b: &str) -> bool {
    !a.is_empty() && !b.is_empty() && (a.starts_with(b) || b.starts_with(a))
}

/// The changes of `b` still to run: not ejected by its own lines, and not among `on_main` (already landed).
#[must_use]
pub fn remaining(b: &Batch, on_main: &BTreeSet<String>) -> Vec<String> {
    let ejected: Vec<&str> = b
        .lines
        .iter()
        .filter(|l| l["event"] == "eject")
        .filter_map(|l| l["change"].as_str())
        .collect();
    b.changes
        .iter()
        .filter(|c| !ejected.iter().any(|e| same(c, e)))
        .filter(|c| !on_main.iter().any(|m| same(c, m)))
        .cloned()
        .collect()
}

/// The stop request's pid, where one is left.
fn requested(common: &Path) -> Option<String> {
    std::fs::read_to_string(stop_path(common))
        .ok()
        .map(|t| t.trim().to_owned())
}

/// The runner's loop, from its `start` line to its `stop` line: the why it stopped (`idle`, `make lane-stop`).
///
/// # Errors
///
/// A step or the resume that failed, or a log line that could not be written; the `stop` line names it where it can be written.
pub fn work(run: &mut Run) -> Result<String, String> {
    let (common, pid) = (run.common, run.pid);
    let stamp = || l7r_gate_core::record::repo::utc_now();
    let end = |why: &str| log::append(common, &stamp(), "stop", &json!({"pid": pid, "why": why}));
    let fail = |e: String| {
        let _ = end(&format!("error: {e}"));
        e
    };
    if requested(common).is_some_and(|p| p != pid.to_string()) {
        let _ = std::fs::remove_file(stop_path(common));
    }
    let open = log::batches(&log::read(common)).pop().filter(Batch::open);
    let why = open.as_ref().map_or_else(
        || "make lane-start".to_owned(),
        |b| format!("resume {}", b.id),
    );
    log::append(common, &stamp(), "start", &json!({"pid": pid, "why": why}))?;
    if let Some(b) = open {
        (run.resume)(&b, &remaining(&b, &BTreeSet::new())).map_err(fail)?;
    }
    let mut seen = BTreeSet::new();
    let mut last = (run.now)();
    loop {
        if requested(common).is_some_and(|p| p == pid.to_string()) {
            let _ = std::fs::remove_file(stop_path(common));
            end("make lane-stop")?;
            return Ok("make lane-stop".to_owned());
        }
        let now_on = (run.hand_ins)();
        if !now_on.is_subset(&seen) {
            last = (run.now)();
            seen.extend(now_on);
        }
        if (run.step)().map_err(fail)? {
            last = (run.now)();
        }
        if (run.now)() - last >= run.idle_s {
            end("idle")?;
            return Ok("idle".to_owned());
        }
        (run.sleep)(run.poll_s);
    }
}

/// A knob's seconds from `env`, else its default; a value that is no number is refused naming it.
pub(crate) fn knob(
    env: &dyn Fn(&str) -> Option<String>,
    name: &str,
    default: f64,
) -> Result<f64, String> {
    env(name).map_or(Ok(default), |v| {
        v.trim()
            .parse()
            .map_err(|_| format!("lane: {name}={v} is no number of seconds\n"))
    })
}

/// The commits of every hand-in on the lane of `common`, read as `make lane` reads them.
fn on_lane(common: &Path) -> BTreeSet<String> {
    let pool = log::lines_of(&common.join(l7r_shared::builder_queue::LOG));
    let refs = crate::lane::git(
        common,
        &[
            "for-each-ref",
            "--format=%(objectname)",
            l7r_gate_task::builder_done::REFS,
        ],
    )
    .unwrap_or_default()
    .lines()
    .map(str::to_owned)
    .collect();
    log::on_lane(log::hand_ins(&pool), &refs, &log::read(common))
        .into_iter()
        .map(|h| h.commit)
        .collect()
}

/// `l7r-gate lane --work <common>`: the detached runner itself. It takes the lock or leaves at once (another runner won the race),
/// writes its pid into the lock file and runs [`work`] with the standing seams: the batch step and the resume of [`run`] (T14).
#[must_use]
pub fn work_cli(common: &Path, env: &dyn Fn(&str) -> Option<String>) -> Reply {
    let knobs = knob(env, "LANE_IDLE_S", LANE_IDLE_S)
        .and_then(|idle| Ok((idle, knob(env, "LANE_POLL_S", POLL_S)?)));
    let (idle_s, poll_s) = match knobs {
        Ok(k) => k,
        Err(e) => return reply(String::new(), e, 2),
    };
    if !common.is_dir() {
        return reply(
            String::new(),
            format!("lane: {} is no git directory\n", common.display()),
            1,
        );
    }
    let mut lock = match flock_within(&lock_path(common), TAKE_S) {
        Ok(Some(f)) => f,
        Ok(None) => return reply(String::new(), String::new(), 0),
        Err(e) => {
            return reply(
                String::new(),
                format!("lane: {}: {e}\n", lock_path(common).display()),
                1,
            )
        }
    };
    let pid = std::process::id();
    let _ = lock
        .set_len(0)
        .and_then(|()| lock.rewind())
        .and_then(|()| lock.write_all(pid.to_string().as_bytes()));
    let now = || {
        SystemTime::now()
            .duration_since(SystemTime::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs_f64()
    };
    let sleep = |s: f64| std::thread::sleep(Duration::from_secs_f64(s.max(0.0)));
    let hand_ins = || on_lane(common);
    let lane = run::Lane { common, now: &now };
    let mut resume = |b: &Batch, r: &[String]| run::resume(&lane, b, r);
    let mut step = || run::step(&lane);
    let mut run = Run {
        common,
        pid,
        idle_s,
        poll_s,
        now: &now,
        sleep: &sleep,
        hand_ins: &hand_ins,
        resume: &mut resume,
        step: &mut step,
    };
    let done = work(&mut run);
    release(lock);
    match done {
        Ok(why) => reply(
            format!("lane: the runner stopped ({why})\n"),
            String::new(),
            0,
        ),
        Err(e) => reply(String::new(), format!("lane: the runner failed: {e}\n"), 1),
    }
}

/// Every hand-in starts the runner, idempotently (plan D2) - from phase 2's base, `HAND_IN_BASE` = `origin`: in phase 1 the
/// coordinator still lands by hand, and a runner batching the same hand-ins would race it. A refused hand-in starts nothing; the
/// start's line is added after the hand-in's, and its failure never changes the hand-in's exit. `land` is `l7r-gate land`'s
/// arguments: any verb but `--hand-in` passes through untouched.
#[must_use]
pub fn on_hand_in(
    land: &[String],
    mut done: Reply,
    base: Option<&str>,
    cwd: &Path,
    exe: &Path,
) -> Reply {
    if land.first().map(String::as_str) != Some("--hand-in")
        || done.code != 0
        || base != Some("origin")
    {
        return done;
    }
    let Some(common) = crate::lane::common_dir(cwd) else {
        let _ = writeln!(
            done.stderr,
            "lane: {} is in no git repository",
            cwd.display()
        );
        return done;
    };
    let started = start(&common, &runner_exe(&common, exe), "setsid", START_WAIT_S);
    done.stdout += &started.stdout;
    done.stderr += &started.stderr;
    done
}

#[cfg(test)]
mod tests;

#[cfg(test)]
mod start_tests;
