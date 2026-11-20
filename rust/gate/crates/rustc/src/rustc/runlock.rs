//! ONE RUN AT A TIME IN A TARGET DIRECTORY (feature 451 T23, found by T02, 2026-11-20): two builders' runs in one clone share
//! `~/.cache/l7r-cargo-target/<clone>`, its coverage families' `view/<crate>` directories and the test binaries the checks run
//! directly, none of which cargo's own build lock covers. T02's `make static` ran beside T234's cargo there and failed on corrupt or
//! missing coverage profiles in seven crates, a collision, not a result.
//!
//! So every `l7r-gate rust <cmd>` joins a record in each directory it writes (`rust-checks-run.json`, edited under the short `flock` of
//! `rust-checks-run.lock`) for its whole length. The record names one RUN: the outermost `make` above the process, so the checks one
//! `make done` runs side by side (`static` in the background beside `counters-inert` at `rust-only`) share it, and a run nested in a
//! run's tests joins its own; with no `make` above, the process is its own run. A member is a process, by its pid and start time
//! (a reused pid is another process), and is gone when the process is: a killed run leaves no lock to clear by hand. A run that finds
//! another run's live member waits, saying on stderr who holds the directory and how long it has waited, and past the ceiling refuses,
//! naming the holder.

use std::path::{Path, PathBuf};
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

use serde_json::{json, Value};

use super::World;

pub(super) const RECORD: &str = "rust-checks-run.json";
pub(super) const MUTEX: &str = "rust-checks-run.lock";

/// THE CEILING (GUESS, a knob: `L7R_RUST_LOCK_CEILING` seconds, unmeasured): meant to outlast any one check of another builder's,
/// a cold `rust cover` over every crate the longest, yet to refuse a holder that hangs within the hour; retuned from the wait lines.
const CEILING_S: u64 = 1800;
/// How often a waiter says it still waits (GUESS: often enough that a builder reading its log sees the wait, rarely enough to read).
const SAY_EVERY: Duration = Duration::from_secs(30);
/// How often a waiter looks again (GUESS: well under a second, against runs that last tens of seconds).
const POLL: Duration = Duration::from_millis(500);
/// The record's own `flock` is held for a read and a write; past this something is wrong (GUESS).
const MUTEX_S: f64 = 10.0;

/// A process: its pid and its start time in clock ticks since boot (`/proc/<pid>/stat`'s 22nd field).
#[derive(Clone, PartialEq, Eq, Debug)]
pub(super) struct Proc {
    pub(super) pid: u64,
    pub(super) start: u64,
}

/// Who asks: the run it belongs to, what that run is (`make static`), and the process itself.
pub(super) struct Taker {
    pub(super) proc_root: PathBuf,
    pub(super) run: Proc,
    pub(super) run_what: String,
    pub(super) me: Proc,
    pub(super) ceiling: Duration,
    pub(super) poll: Duration,
    pub(super) say_every: Duration,
    pub(super) mutex_s: f64,
}

/// The fields after the command name of `/proc/<pid>/stat` (the name may hold spaces and parentheses; it ends at the last `)`).
fn stat(proc_root: &Path, pid: u64) -> Option<Vec<String>> {
    let text = std::fs::read_to_string(proc_root.join(pid.to_string()).join("stat")).ok()?;
    let rest = &text[text.rfind(')')? + 1..];
    Some(rest.split_whitespace().map(str::to_owned).collect())
}

fn field(fields: &[String], at: usize) -> u64 {
    fields.get(at).and_then(|f| f.parse().ok()).unwrap_or(0)
}

fn started(proc_root: &Path, pid: u64) -> Option<u64> {
    stat(proc_root, pid).map(|f| field(&f, 19))
}

/// Whether the process is alive and still the one that joined.
fn alive(proc_root: &Path, member: &Proc) -> bool {
    started(proc_root, member.pid) == Some(member.start)
}

/// A process's command line, a word holding a space quoted (feature 451 T05): the phase lines read the run's make target from it as
/// a shell command (`phase::run_target`), and `make NOTE="two words" land` joined bare read `words` as a goal.
fn cmdline(proc_root: &Path, pid: u64) -> String {
    let raw = std::fs::read(proc_root.join(pid.to_string()).join("cmdline")).unwrap_or_default();
    raw.split(|b| *b == 0)
        .filter(|w| !w.is_empty())
        .map(|w| String::from_utf8_lossy(w).into_owned())
        .map(|w| {
            if w.contains(char::is_whitespace) {
                format!("'{w}'")
            } else {
                w
            }
        })
        .collect::<Vec<_>>()
        .join(" ")
}

/// The outermost `make` above `pid`, or `pid` itself where none is.
pub(super) fn run_of(proc_root: &Path, pid: u64) -> (Proc, String) {
    let me = Proc {
        pid,
        start: started(proc_root, pid).unwrap_or(0),
    };
    let mut run = None;
    let mut at = pid;
    while let Some(fields) = stat(proc_root, at) {
        let comm = std::fs::read_to_string(proc_root.join(at.to_string()).join("comm"))
            .unwrap_or_default();
        if ["make", "gmake"].contains(&comm.trim()) {
            run = Some(Proc {
                pid: at,
                start: field(&fields, 19),
            });
        }
        at = field(&fields, 1);
        if at <= 1 {
            break;
        }
    }
    let run = run.unwrap_or_else(|| me.clone());
    let what = cmdline(proc_root, run.pid);
    (run, what)
}

/// The ceiling a knob names in whole seconds, or `CEILING_S` where it names none.
pub(super) fn ceiling_of(knob: Option<&str>) -> Duration {
    Duration::from_secs(
        knob.and_then(|s| s.trim().parse().ok())
            .unwrap_or(CEILING_S),
    )
}

impl Taker {
    /// This process, under the live `/proc`, its ceiling from `L7R_RUST_LOCK_CEILING` where that is set.
    pub(super) fn here() -> Self {
        let proc_root = PathBuf::from("/proc");
        let (run, run_what) = run_of(&proc_root, u64::from(std::process::id()));
        let me = Proc {
            pid: u64::from(std::process::id()),
            start: started(&proc_root, u64::from(std::process::id())).unwrap_or(0),
        };
        let ceiling = ceiling_of(std::env::var("L7R_RUST_LOCK_CEILING").ok().as_deref());
        Self {
            proc_root,
            run,
            run_what,
            me,
            ceiling,
            poll: POLL,
            say_every: SAY_EVERY,
            mutex_s: MUTEX_S,
        }
    }
}

/// The directories a run writes: the clone's target directory (the coverage families' own directories are under it), and the
/// cargo target and coverage directory an override names, sorted, so two runs take them in one order.
pub(super) fn dirs_of(world: &World) -> Vec<PathBuf> {
    let mut dirs = vec![world.target.clone()];
    dirs.extend(world.target_override.as_ref().map(PathBuf::from));
    dirs.extend(world.cover_work.clone());
    dirs.sort();
    dirs.dedup();
    dirs
}

fn now() -> f64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_or(0.0, |d| d.as_secs_f64())
}

fn member_of(v: &Value) -> Proc {
    Proc {
        pid: v["pid"].as_u64().unwrap_or(0),
        start: v["start"].as_u64().unwrap_or(0),
    }
}

/// The record's live members, the dead dropped.
fn live(dir: &Path, proc_root: &Path) -> Vec<Value> {
    let text = std::fs::read_to_string(dir.join(RECORD)).unwrap_or_default();
    let record: Value = serde_json::from_str(&text).unwrap_or(Value::Null);
    record["members"]
        .as_array()
        .cloned()
        .unwrap_or_default()
        .into_iter()
        .filter(|m| alive(proc_root, &member_of(m)))
        .collect()
}

fn write(dir: &Path, members: &[Value]) {
    let _ = std::fs::write(dir.join(RECORD), json!({ "members": members }).to_string());
}

/// The record's `flock`, held while it is read and written.
pub(super) fn mutex(dir: &Path, secs: f64) -> Result<std::fs::File, String> {
    match l7r_guard::shared::tool::flock_within(&dir.join(MUTEX), secs) {
        Ok(Some(file)) => Ok(file),
        Ok(None) => Err(format!(
            "rust-checks: the lock record's own lock {} was held past {secs} s - a process stopped while it held it; it frees when that process ends\n",
            dir.join(MUTEX).display()
        )),
        Err(e) => Err(format!(
            "rust-checks: cannot open the lock record in {}: {e}\n",
            dir.display()
        )),
    }
}

/// Join the directory's run, or name the live member of another run that holds it.
fn try_join(dir: &Path, taker: &Taker, cmd: &str, token: &str) -> Result<Option<Value>, String> {
    let _held = mutex(dir, taker.mutex_s)?;
    let mut members = live(dir, &taker.proc_root);
    let run = json!({"pid": taker.run.pid, "start": taker.run.start});
    if let Some(other) = members.iter().find(|m| m["run"] != run) {
        return Ok(Some(other.clone()));
    }
    members.push(json!({
        "token": token, "pid": taker.me.pid, "start": taker.me.start, "run": run,
        "run_what": taker.run_what, "cmd": cmd, "t": now(),
    }));
    write(dir, &members);
    Ok(None)
}

fn leave(dir: &Path, taker: &Taker, token: &str) {
    if let Ok(_held) = mutex(dir, taker.mutex_s) {
        let members: Vec<Value> = live(dir, &taker.proc_root)
            .into_iter()
            .filter(|m| m["token"] != token)
            .collect();
        write(dir, &members);
    }
}

/// Who holds a directory, in words: the process, its check, its run and since when.
fn holder(m: &Value) -> String {
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "a whole second since the epoch"
    )]
    let (_, _, _, h, mi, s) = l7r_guard::shared::log::civil(m["t"].as_f64().unwrap_or(0.0) as u64);
    format!(
        "pid {} (`rust {}`), of the run `{}` (pid {}), since {h:02}:{mi:02}:{s:02} UTC",
        m["pid"],
        m["cmd"].as_str().unwrap_or(""),
        m["run_what"].as_str().unwrap_or(""),
        m["run"]["pid"],
    )
}

/// The directories held for a run; each is left when this is dropped (and is free anyway once the process is gone).
pub(super) struct Held<'a> {
    dirs: Vec<PathBuf>,
    taker: &'a Taker,
    token: String,
}

impl Drop for Held<'_> {
    fn drop(&mut self) {
        for dir in &self.dirs {
            leave(dir, self.taker, &self.token);
        }
    }
}

static SERIAL: std::sync::atomic::AtomicU64 = std::sync::atomic::AtomicU64::new(0);

/// Take every directory for the run, in order, waiting on another run's (said on stderr through `say`), refused past the ceiling.
pub(super) fn take<'a>(
    dirs: &[PathBuf],
    taker: &'a Taker,
    cmd: &str,
    say: &mut dyn FnMut(&str),
) -> Result<Held<'a>, String> {
    let token = format!(
        "{}-{}-{}",
        taker.me.pid,
        now(),
        SERIAL.fetch_add(1, std::sync::atomic::Ordering::Relaxed)
    );
    let mut held = Held {
        dirs: Vec::new(),
        taker,
        token,
    };
    let began = Instant::now();
    let mut said: Option<Instant> = None;
    for dir in dirs {
        std::fs::create_dir_all(dir)
            .map_err(|e| format!("rust-checks: cannot make {}: {e}\n", dir.display()))?;
        while let Some(other) = try_join(dir, taker, cmd, &held.token)? {
            let waited = began.elapsed().as_secs();
            if began.elapsed() >= taker.ceiling {
                return Err(format!(
                    "rust-checks: REFUSED - {} is still held after {waited} s by {}. Two runs in one target directory corrupt each other's coverage profiles (feature 451 T23). Wait for that run to end, or stop it (`kill {}`); the ceiling is L7R_RUST_LOCK_CEILING seconds ({}).\n",
                    dir.display(),
                    holder(&other),
                    other["run"]["pid"],
                    taker.ceiling.as_secs()
                ));
            }
            if said.is_none_or(|t| t.elapsed() >= taker.say_every) {
                say(&format!(
                    "rust-checks: waiting {waited} s for {}, held by {} - two runs in one target directory corrupt each other's coverage (feature 451 T23)\n",
                    dir.display(),
                    holder(&other)
                ));
                said = Some(Instant::now());
            }
            std::thread::sleep(taker.poll);
        }
        held.dirs.push(dir.clone());
    }
    Ok(held)
}
