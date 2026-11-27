//! A SLOW TEST RUN CAUGHT ALIVE (feature 451 T463, found by T455): six green runs of the land crate's tests took 61 to 102 s, 58 to
//! 93 s over same-time controls, and 70 runs did not reproduce one (`dev/measurements/2026-11-27/land-test-time/results.md`), so the
//! next one is caught where it runs. A watched run - a crate's test binary run directly (`side.rs`) or its `cargo test` (`tested`) -
//! starts a thread beside its `wait`; once the program has run past `AFTER`, the thread writes ONCE what that program and every
//! process under it is doing, read from `/proc` as the record's `watch.sh` read it: each one's pid, parent, age, state, wait channel,
//! working directory, command line and ignored and caught signals (`SigIgn`, `SigCgt`: T455's one lead is a TERM that may not land),
//! and each of its threads' name, state and wait channel - libtest names a test's thread after the test, cut by the kernel to 15
//! characters (`land::stop::tes` at best). The file goes beside the event logs, in `alive/`, as the sampler's `samples/` does, and
//! the run's `test` Phase line names it (`"alive"`). The run is never signalled, never polled and never waited on for the record: a
//! run inside its bound joins a thread that ended when the run did.

use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::sync::mpsc;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

use l7r_shared::guards::event_log_hooks::log_path_in;

use super::{shown, World};

/// How long a test program runs before it is recorded: a GUESS knob. WHY 30 s: the land crate's green runs took 1.9 to 12.3 s in
/// 70 runs at load1 6 to 29, and its slow ones 61 to 102 s (T455's record, sections 1 and 4), so a run past 30 s is one of those; a
/// run caught later than 30 s still shows what it waits on; a loaded run of a large crate may pass it too, and is recorded as well.
const AFTER: Duration = Duration::from_secs(30);

/// The variable that moves `AFTER`, in milliseconds (a test's short bound).
const KNOB: &str = "L7R_RUST_ALIVE_MS";

/// A record's most bytes: a GUESS knob. A test binary's threads are about a line each, so this holds a run of hundreds of processes.
const CAP: usize = 64 * 1024;

/// A command line's most characters in the record, as `watch.sh` cut it.
const ARGS: usize = 300;

/// The kernel's clock ticks a second in `/proc/<pid>/stat`'s start time (`USER_HZ`, 100 on every Linux this runs on).
const TICKS: f64 = 100.0;

/// Where a watched run's record goes, and after how long.
pub(super) struct Bound {
    after: Duration,
    dir: PathBuf,
    name: String,
}

impl Bound {
    /// A crate's bound, its record under the tree's event-log directory.
    pub(super) fn of(world: &World, manifest: &Path) -> Bound {
        let after = world
            .root
            .opt(KNOB)
            .and_then(|v| v.parse().ok())
            .map_or(AFTER, Duration::from_millis);
        let log = log_path_in(&world.root, "", world.root.reader());
        let dir = log.parent().unwrap_or(Path::new(".")).join("alive");
        let name = shown(world, manifest).replace('/', "-");
        Bound { after, dir, name }
    }

    /// The watch on a run just started, `pid` its program.
    pub(super) fn watch(&self, pid: u32, program: &str) -> Watch {
        let (stop, stopped) = mpsc::channel::<()>();
        let (after, dir, name) = (self.after, self.dir.clone(), self.name.clone());
        let head = format!("{program} past {} ms", after.as_millis());
        let caught = std::thread::spawn(move || {
            let timed_out = stopped.recv_timeout(after) == Err(mpsc::RecvTimeoutError::Timeout);
            timed_out.then(|| write(&dir, &name, pid, &head)).flatten()
        });
        Watch { stop, caught }
    }
}

/// A run's watch, ended with the run.
pub(super) struct Watch {
    stop: mpsc::Sender<()>,
    caught: std::thread::JoinHandle<Option<PathBuf>>,
}

impl Watch {
    /// The run has ended: the record's path, where the run went past its bound.
    pub(super) fn ended(self) -> Option<PathBuf> {
        drop(self.stop);
        self.caught.join().ok().flatten()
    }
}

/// The record written, its path; none where it could not be.
fn write(dir: &Path, name: &str, pid: u32, head: &str) -> Option<PathBuf> {
    let secs = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_or(0, |d| d.as_secs());
    let path = dir.join(format!("{secs}-{name}-{pid}.txt"));
    let text = bounded(record(Path::new("/proc"), pid, head), CAP);
    std::fs::create_dir_all(dir).ok()?;
    std::fs::write(&path, text).ok().map(|()| path)
}

/// `text` cut to at most `cap` bytes, at a character's edge, with a line saying so.
pub(super) fn bounded(mut text: String, cap: usize) -> String {
    if text.len() > cap {
        let at = (0..=cap)
            .rev()
            .find(|i| text.is_char_boundary(*i))
            .unwrap_or(0);
        let whole = text.len();
        text.truncate(at);
        let _ = writeln!(text, "\n... cut at {at} of {whole} bytes");
    }
    text
}

/// What `root` and every process under it is doing, read from `proc`.
pub(super) fn record(proc: &Path, root: u32, head: &str) -> String {
    let read = |p: &Path| std::fs::read_to_string(p).unwrap_or_default();
    let uptime: f64 = read(&proc.join("uptime"))
        .split_whitespace()
        .next()
        .and_then(|u| u.parse().ok())
        .unwrap_or(0.0);
    let loadavg = read(&proc.join("loadavg"));
    let load: Vec<&str> = loadavg.split_whitespace().take(3).collect();
    let mut out = format!("=== {head}: pid {root}, load {}\n", load.join(" "));
    for pid in tree(proc, root) {
        let at = proc.join(pid.to_string());
        let Some((state, ppid, start)) = stat(&read(&at.join("stat"))) else {
            continue;
        };
        let age = uptime - start / TICKS;
        let args: String = read(&at.join("cmdline"))
            .split('\0')
            .filter(|w| !w.is_empty())
            .collect::<Vec<_>>()
            .join(" ")
            .chars()
            .take(ARGS)
            .collect();
        let cwd = std::fs::read_link(at.join("cwd")).unwrap_or_default();
        let signals: Vec<String> = read(&at.join("status"))
            .lines()
            .filter(|l| l.starts_with("SigIgn:") || l.starts_with("SigCgt:"))
            .map(|l| l.replacen(':', "=", 1).split_whitespace().collect())
            .collect();
        let _ = writeln!(
            out,
            "--- pid {pid} ppid {ppid} age {age:.1}s state {state} wchan {}\n    cwd={}\n    args={args}\n    {}",
            read(&at.join("wchan")),
            cwd.display(),
            signals.join(" ")
        );
        for task in entries(&at.join("task")) {
            let t = at.join("task").join(task.to_string());
            let state = stat(&read(&t.join("stat"))).map_or_else(String::new, |s| s.0);
            let _ = writeln!(
                out,
                "    thread {} {state} {}",
                read(&t.join("comm")).trim_end(),
                read(&t.join("wchan"))
            );
        }
    }
    out
}

/// The numbered entries of a `/proc` directory, in order.
fn entries(dir: &Path) -> Vec<u32> {
    let mut found: Vec<u32> = std::fs::read_dir(dir)
        .into_iter()
        .flatten()
        .flatten()
        .filter_map(|e| e.file_name().to_string_lossy().parse().ok())
        .collect();
    found.sort_unstable();
    found
}

/// `root` and every process under it, `root` first, then by depth.
fn tree(proc: &Path, root: u32) -> Vec<u32> {
    let parents: Vec<(u32, u32)> = entries(proc)
        .into_iter()
        .filter_map(|pid| {
            let text = std::fs::read_to_string(proc.join(pid.to_string()).join("stat")).ok()?;
            stat(&text).map(|s| (pid, s.1))
        })
        .collect();
    let mut found = vec![root];
    let mut at = 0;
    while let Some(&p) = found.get(at) {
        found.extend(parents.iter().filter(|(_, pp)| *pp == p).map(|(c, _)| *c));
        at += 1;
    }
    found
}

/// A `/proc/<pid>/stat` line's state, parent and start time in ticks, read after its name's last `)`: a name holds any character.
fn stat(text: &str) -> Option<(String, u32, f64)> {
    let fields: Vec<&str> = text
        .get(text.rfind(')')? + 1..)?
        .split_whitespace()
        .collect();
    let state = (*fields.first()?).to_owned();
    Some((
        state,
        fields.get(1)?.parse().ok()?,
        fields.get(19)?.parse().ok()?,
    ))
}
