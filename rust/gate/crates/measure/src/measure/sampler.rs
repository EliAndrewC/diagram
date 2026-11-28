//! `l7r-gate measure sampler` (feature 451 T274): THE MEMORY AND LOAD SAMPLER. The number of builders at once is certified against
//! the container's memory limit (10 GiB, no swap) from samples, and on 2026-11-26 those samples were a shell loop the coordinating
//! session started by hand - so the three- and four-at-once comment batches ran unsampled (`docs/process-decisions.md`, "Two code
//! builders at once"). Tooling, not remembering: `make builder-tree` starts the sampler with every handout.
//!
//! - `start` (`make sampler-start`): one sampler a clone. `<git common dir>/l7r-sampler.pid` holds the sampler's pid and its start
//!   time (the 22nd field of its `/proc/<pid>/stat`); a start that finds that process alive says one is running, and one that finds
//!   it gone (or a zombie) replaces it. The sampler is `l7r-gate measure sampler run`, started through `setsid` with its standard
//!   streams `/dev/null` and none of the caller's descriptors (a caller reading the start through a pipe would otherwise wait
//!   twelve hours, and a build slot's `flock` descriptor would be held as long).
//! - `run`: the sampler itself. It writes its own pid and start time to the pid file, then every `L7R_SAMPLE_S` seconds (10) one
//!   JSON line to `<git common dir>/l7r-events/samples/mem-samples.jsonl`, read straight from the cgroup's files and `/proc` - no
//!   `make`, no program started a sample. It ends when the pid file no longer names it (a stop, a second sampler, the clone
//!   deleted), after `L7R_SAMPLE_MAX_H` hours (12), and when the file passes [`MAX_BYTES`]; each end is a line of `sampler.log`
//!   beside the samples. Where a build replaces its binary it `exec`s the new one (`run --common <dir> --first <its first
//!   start>`, the same pid, its hours counted from the first start), so a sample reads with the built code within one interval
//!   (461 T61); a re-run that fails samples on and asks again at the next sample.
//! - `stop` (`make sampler-stop`): the pid file removed and the sampler sent `TERM`.
//! - `status` (`make sampler`): running or not, the file's lines and size, the last line of `sampler.log`.
//! - `report` (`make sampler-report`): [`report`].
//!
//! WHY A FOLDER OF ITS OWN under `l7r-events/`: every reader of that directory takes a `.jsonl` there for a feature's event log -
//! the hook's launch lookup scans the most recently written first (`event_log_hooks.rs`, `launch_line`), `make task-time` and the
//! step-back bundle read every one, and `make speckit-todo` calls a clone active by the newest file's time - so a file written
//! every ten seconds beside them would be scanned by every hook and keep an idle clone "active". None of them descends.
//!
//! THE SIZE BOUND, [`MAX_BYTES`], is 4 MiB: a line is about 280 bytes with four trees held (11,097 bytes for 40 samples, measured
//! 2026-11-26), so a twelve-hour run at ten seconds is 4,320 lines, about 1.2 MB, and 4 MiB holds about 42 sampled hours. A start
//! that finds the file past the bound moves it to `mem-samples.1.jsonl` (the one before it dropped) and begins a new one, so
//! sampling never ends for good at the bound and the two files together are at most 8 MiB, about 84 sampled hours; the report
//! reads both.

use std::fmt::Write as _;
use std::io::Write as _;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};

use l7r_shared::builder_pool;
use serde_json::{json, Value};

use crate::Reply;

pub mod report;

/// The pid file, in the git common directory: `<pid> <start time>`.
pub const PID: &str = "l7r-sampler.pid";
/// The samples' folder, under the git common directory.
pub const DIR: &str = "l7r-events/samples";
/// The samples being written.
pub const FILE: &str = "mem-samples.jsonl";
/// The file before it, moved there when a start found it past the bound.
pub const KEPT: &str = "mem-samples.1.jsonl";
/// Each start and end of a sampler, a line.
const LOG: &str = "sampler.log";
/// The seconds between samples unless `L7R_SAMPLE_S` says otherwise: the hand loop's interval of 2026-11-26, kept so the kept logs
/// and the sampler's compare sample for sample.
pub const EVERY_S: u64 = 10;
/// The hours a sampler runs unless `L7R_SAMPLE_MAX_H` says otherwise. GUESS: longer than any batch of builders run so far (the
/// longest, 2026-11-25/26, about ten hours), so a sampler nobody stops still ends.
pub const MAX_H: u64 = 12;
/// The size past which a sampler ends and the next start begins a new file (the module's note has the arithmetic).
pub const MAX_BYTES: u64 = 4 << 20;
/// The anonymous memory, in GiB, a sample is counted over unless `L7R_MEM_MARGIN_GIB` says otherwise. GUESS: 3 GiB under the
/// 10 GiB limit, the margin the two- and three-builder runs of 2026-11-26 were read against (peaks 6.3 and 6.4 GiB); a knob.
pub const MARGIN_GIB: f64 = 7.0;

const USAGE: &str = "usage: l7r-gate measure sampler start | stop | status | run --common <git common dir> | report [--since <ISO UTC>] [--until <ISO UTC>] [--log <file>]...\n";

/// What a sampler reads of the world outside its clone.
pub struct Env {
    /// The clone's git common directory.
    pub common: PathBuf,
    /// The cgroup's files (`/sys/fs/cgroup`).
    pub cgroup: PathBuf,
    /// `/proc`.
    pub proc: PathBuf,
    /// The seconds between samples.
    pub every_s: u64,
    /// The seconds a sampler runs.
    pub max_s: u64,
    /// The size past which it ends.
    pub max_bytes: u64,
    /// The machine's cores.
    pub cores: usize,
    /// The margin a sample is counted over, GiB.
    pub margin_gib: f64,
    /// The detached sampler's program and arguments.
    pub worker: Vec<String>,
    /// The tenths of a second a start waits for its sampler to name itself.
    pub wait_tenths: u32,
    /// The program this sampler runs, where it re-runs itself once rebuilt (none: never).
    pub exe: Option<PathBuf>,
    /// When the first sampler of this run began, where this one is its re-run (`--first`).
    pub first: Option<u64>,
    /// Replaces this process by the program and arguments given; what it returns is why it could not.
    pub exec: fn(&[String]) -> std::io::Error,
}

impl Env {
    fn live(common: &Path) -> Self {
        let var = |n: &str| std::env::var(n).unwrap_or_default();
        let exe = std::env::current_exe().unwrap_or_default();
        Self {
            common: common.to_path_buf(),
            cgroup: PathBuf::from("/sys/fs/cgroup"),
            proc: PathBuf::from("/proc"),
            every_s: var("L7R_SAMPLE_S").parse().unwrap_or(EVERY_S).max(1),
            max_s: var("L7R_SAMPLE_MAX_H").parse().unwrap_or(MAX_H) * 3600,
            max_bytes: MAX_BYTES,
            cores: std::thread::available_parallelism().map_or(1, std::num::NonZero::get),
            margin_gib: var("L7R_MEM_MARGIN_GIB").parse().unwrap_or(MARGIN_GIB),
            worker: [
                "setsid",
                &exe.to_string_lossy(),
                "measure",
                "sampler",
                "run",
                "--common",
                &common.to_string_lossy(),
            ]
            .map(str::to_owned)
            .to_vec(),
            wait_tenths: 30,
            exe: Some(exe),
            first: None,
            exec: exec_live,
        }
    }

    fn samples(&self) -> PathBuf {
        self.common.join(DIR).join(FILE)
    }
}

/// This process replaced by `argv`'s program, `exec(3)`: it returns only where that failed.
fn exec_live(argv: &[String]) -> std::io::Error {
    use std::os::unix::process::CommandExt as _;
    let Some((program, words)) = argv.split_first() else {
        return std::io::Error::other("no program");
    };
    Command::new(program).args(words).exec()
}

fn reply(stderr: String, code: i32) -> Reply {
    Reply {
        stdout: String::new(),
        stderr,
        code,
    }
}

fn read(path: &Path) -> String {
    std::fs::read_to_string(path).unwrap_or_default()
}

/// The number after `key` on the line of `text` that opens with it (`anon 123` of `memory.stat`, `oom_kill 0` of `memory.events`).
fn keyed(text: &str, key: &str) -> Option<u64> {
    text.lines()
        .find_map(|l| l.strip_prefix(key)?.strip_prefix(' ')?.trim().parse().ok())
}

/// A pressure file's `total=` on its `some` or `full` line, microseconds stalled since the cgroup began.
fn stalled(text: &str, kind: &str) -> Option<u64> {
    let line = text.lines().find(|l| l.starts_with(kind))?;
    line.split_whitespace()
        .find_map(|w| w.strip_prefix("total=")?.parse().ok())
}

/// The processes whose command name is `rustc`.
fn rustc(proc: &Path) -> usize {
    std::fs::read_dir(proc)
        .into_iter()
        .flatten()
        .flatten()
        .filter(|e| {
            e.file_name()
                .to_string_lossy()
                .bytes()
                .all(|b| b.is_ascii_digit())
        })
        .filter(|e| read(&e.path().join("comm")).trim() == "rustc")
        .count()
}

/// The start time of process `pid` (the 22nd field of its `stat`, read after the command name's last `)`); none where it is gone
/// or a zombie.
fn began(proc: &Path, pid: u32) -> Option<u64> {
    let text = read(&proc.join(pid.to_string()).join("stat"));
    let mut fields = text.rsplit_once(')')?.1.split_whitespace();
    let state = fields.next()?;
    let start = fields.nth(18)?.parse().ok()?;
    (state != "Z").then_some(start)
}

/// What the pid file names: a pid and its start time.
fn named(env: &Env) -> Option<(u32, u64)> {
    let text = read(&env.common.join(PID));
    let (pid, start) = text.trim().split_once(' ')?;
    Some((pid.parse().ok()?, start.parse().ok()?))
}

/// The sampler the pid file names, where that process is alive.
fn running(env: &Env) -> Option<u32> {
    let (pid, start) = named(env)?;
    (began(&env.proc, pid) == Some(start)).then_some(pid)
}

#[expect(clippy::many_single_char_names, reason = "the fields of a date")]
fn utc(secs: u64) -> String {
    let (y, m, d, h, mi, s) = l7r_shared::log::civil(secs);
    format!("{y:04}-{m:02}-{d:02}T{h:02}:{mi:02}:{s:02}Z")
}

fn now() -> u64 {
    std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map_or(0, |d| d.as_secs())
}

/// ONE SAMPLE at `secs`: anonymous memory (`anon`, the in-use figure here: shmem and unreclaimable slab are zero, the rest of
/// `cur` is page cache, which is given back), `memory.current`, `memory.peak` and `memory.max` in bytes, the memory and CPU
/// stall totals in microseconds, the one-minute load and the cores, the OOM kills, the `rustc` processes, and who holds each
/// held pool tree. A figure its file does not give is left out (`max` where the limit is `max`, `cpu_some_us` where
/// `/proc/pressure/cpu` is not there).
#[must_use]
pub fn sample(env: &Env, secs: u64) -> Value {
    let cg = |name: &str| read(&env.cgroup.join(name));
    let pressure = cg("memory.pressure");
    let held: Vec<String> = builder_pool::read(&env.common)
        .iter()
        .filter(|t| !t.free())
        .map(builder_pool::Tree::holder)
        .collect();
    let load1: Option<f64> = read(&env.proc.join("loadavg"))
        .split_whitespace()
        .next()
        .and_then(|w| w.parse().ok());
    let mut row = json!({
        "utc": utc(secs),
        "anon": keyed(&cg("memory.stat"), "anon"),
        "cur": cg("memory.current").trim().parse::<u64>().ok(),
        "peak": cg("memory.peak").trim().parse::<u64>().ok(),
        "max": cg("memory.max").trim().parse::<u64>().ok(),
        "mem_some_us": stalled(&pressure, "some"),
        "mem_full_us": stalled(&pressure, "full"),
        "cpu_some_us": stalled(&read(&env.proc.join("pressure/cpu")), "some"),
        "load1": load1,
        "cores": env.cores,
        "oom_kill": keyed(&cg("memory.events"), "oom_kill"),
        "rustc": rustc(&env.proc),
        "held": held,
    });
    if let Some(fields) = row.as_object_mut() {
        fields.retain(|_, v| !v.is_null());
    }
    row
}

/// `line` at the end of `path`; a line that cannot be written is lost, never an error of the sampler's - and its folder is not
/// made here: a sampler whose clone was deleted under it ends without making the clone's directories again.
fn append(path: &Path, line: &str) {
    let file = std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(path);
    if let Ok(mut f) = file {
        let _ = writeln!(f, "{line}");
    }
}

fn size(path: &Path) -> u64 {
    path.metadata().map_or(0, |m| m.len())
}

/// The program at this sampler's path where it is no longer the one this process runs - a build replaced it (461 T61: pid
/// 3387947 ran the code it started with for its twelve hours, listing the lane's tree in 215 samples after 461 T13 left it out).
/// Two `stat`s, the cheap stand-in for a content id: `<proc>/self/exe` follows the kernel's link to the file this process runs,
/// even once unlinked, and its device and inode are the path's until a build puts a new file there. A path not there (a build
/// mid-link) is no rebuild.
fn rebuilt(env: &Env) -> Option<&Path> {
    use std::os::unix::fs::MetadataExt as _;
    let exe = env.exe.as_deref()?;
    let id = |p: &Path| p.metadata().ok().map(|m| (m.dev(), m.ino()));
    let (running, there) = (id(&env.proc.join("self/exe"))?, id(exe)?);
    (running != there).then_some(exe)
}

/// The re-run's words: the sampler's own `run`, its first start carried so its hours count from there.
fn rerun(env: &Env, exe: &Path, first: u64) -> Vec<String> {
    let common = env.common.to_string_lossy();
    [
        &*exe.to_string_lossy(),
        "measure",
        "sampler",
        "run",
        "--common",
        &common,
        "--first",
        &first.to_string(),
    ]
    .map(str::to_owned)
    .to_vec()
}

/// THE SAMPLER'S LOOP, as process `me` (its pid and start time): the pid file written, then a sample and a nap until the pid file
/// names another, the hours pass or the file passes its bound - and, its binary rebuilt, the new one `exec`ed in its place, the
/// same pid and start time, so the pid file still names it (461 T61). Why it ended, which `sampler.log` keeps too.
pub fn work(
    env: &Env,
    me: (u32, u64),
    clock: &mut dyn FnMut() -> u64,
    nap: &mut dyn FnMut(u64),
) -> &'static str {
    let pid = env.common.join(PID);
    let dir = env.common.join(DIR);
    let mine = format!("{} {}\n", me.0, me.1);
    let _ = std::fs::create_dir_all(&dir);
    let _ = std::fs::write(&pid, &mine);
    let at0 = clock();
    let first = env.first.unwrap_or(at0);
    let (said, from) = match env.first {
        None => ("started", String::new()),
        Some(f) => (
            "runs its rebuilt binary",
            format!(" (its hours from {})", utc(f)),
        ),
    };
    append(
        &dir.join(LOG),
        &format!(
            "{} pid {} {said}, a sample every {} s{from}",
            utc(at0),
            me.0,
            env.every_s
        ),
    );
    let why = loop {
        let at = clock();
        if read(&pid) != mine {
            break "the pid file no longer names it (stopped, or another sampler took its place)";
        }
        if at.saturating_sub(first) >= env.max_s {
            break "its hours are up (L7R_SAMPLE_MAX_H)";
        }
        if size(&env.samples()) >= env.max_bytes {
            break "the samples file is past its size bound - the next start begins a new one";
        }
        if let Some(exe) = rebuilt(env) {
            // returns only where the re-run failed (a build mid-write): sample on in this code, and ask again at the next sample
            let _ = (env.exec)(&rerun(env, exe, first));
        }
        append(&env.samples(), &sample(env, at).to_string());
        nap(env.every_s);
    };
    if read(&pid) == mine {
        let _ = std::fs::remove_file(&pid);
    }
    append(
        &dir.join(LOG),
        &format!("{} pid {} ended: {why}", utc(clock()), me.0),
    );
    why
}

/// Every descriptor past the standard three marked close-on-exec, so the detached sampler holds none of the caller's (as the page
/// sessions' runner does, `pages/src/runner.rs`): a `make builder-tree` read through a pipe would otherwise wait for the sampler
/// to end, and a build slot's or a run lock's `flock` would be held for its twelve hours.
fn close_inherited() {
    extern "C" {
        fn fcntl(fd: i32, cmd: i32, arg: i32) -> i32;
    }
    let fds: Vec<i32> = std::fs::read_dir("/proc/self/fd")
        .into_iter()
        .flatten()
        .flatten()
        .filter_map(|e| e.file_name().to_str()?.parse().ok())
        .collect();
    for fd in fds.into_iter().filter(|fd| *fd > 2) {
        // SAFETY: F_SETFD (2) sets only the descriptor's close-on-exec flag (FD_CLOEXEC, 1); a descriptor gone already is an EBADF
        unsafe {
            fcntl(fd, 2, 1);
        }
    }
}

/// `start`: the running sampler named, or a new one started detached - a dead one's pid file replaced, a samples file past its
/// bound moved aside first.
fn start(env: &Env) -> Reply {
    let file = env.samples();
    if let Some(pid) = running(env) {
        return reply(format!("sampler: one is running (pid {pid}), a sample every {} s to {} - make sampler-stop ends it\n", env.every_s, file.display()), 0);
    }
    let mut said = String::new();
    if let Some((pid, _)) = named(env) {
        said = format!("sampler: the one the pid file named (pid {pid}) is gone - replaced\n");
    }
    if size(&file) >= env.max_bytes {
        let kept = file.with_file_name(KEPT);
        let _ = std::fs::rename(&file, &kept);
        let _ = writeln!(
            said,
            "sampler: the samples file was past its bound ({} bytes): moved to {}, a new one begun",
            env.max_bytes,
            kept.display()
        );
    }
    let _ = std::fs::remove_file(env.common.join(PID));
    close_inherited();
    let spawned = env
        .worker
        .split_first()
        .ok_or_else(|| "no program".to_owned())
        .and_then(|(program, args)| {
            Command::new(program)
                .args(args)
                .current_dir(&env.common)
                .stdin(Stdio::null())
                .stdout(Stdio::null())
                .stderr(Stdio::null())
                .spawn()
                .map_err(|e| format!("{program}: {e}"))
        });
    if let Err(e) = spawned {
        return reply(format!("{said}sampler: not started ({e})\n"), 1);
    }
    for _ in 0..env.wait_tenths {
        if running(env).is_some() {
            break;
        }
        std::thread::sleep(std::time::Duration::from_millis(100));
    }
    match running(env) {
        Some(pid) => reply(format!("{said}sampler: started (pid {pid}), a sample every {} s to {} for at most {} h - make sampler-stop ends it, make sampler-report reads it\n", env.every_s, file.display(), env.max_s / 3600), 0),
        None => reply(format!("{said}sampler: started, but it has not written {} after {} s - make sampler says whether it runs\n", env.common.join(PID).display(), env.wait_tenths / 10), 1),
    }
}

/// `stop`: the pid file removed, which ends the sampler at its next sample, and the process sent `TERM`, which ends it now.
fn stop(env: &Env) -> Reply {
    let was = running(env);
    let _ = std::fs::remove_file(env.common.join(PID));
    let Some(pid) = was else {
        return reply("sampler: none is running\n".to_owned(), 0);
    };
    let _ = Command::new("kill")
        .arg(pid.to_string())
        .stderr(Stdio::null())
        .status();
    append(
        &env.common.join(DIR).join(LOG),
        &format!("{} pid {pid} stopped (make sampler-stop)", utc(now())),
    );
    reply(
        format!(
            "sampler: stopped (pid {pid}); its samples are {} - make sampler-report reads them\n",
            env.samples().display()
        ),
        0,
    )
}

/// `status`: running or not, what the samples file holds, and the log's last line.
fn status(env: &Env) -> Reply {
    let file = env.samples();
    let state = running(env).map_or_else(
        || "sampler: none is running - make sampler-start (make builder-tree starts one with each handout)".to_owned(),
        |pid| format!("sampler: running (pid {pid}), a sample every {} s", env.every_s),
    );
    let log = read(&env.common.join(DIR).join(LOG));
    reply(
        format!(
            "{state}\nsampler: {} holds {} lines, {} bytes (its bound {})\nsampler: last, {}\n",
            file.display(),
            read(&file).lines().count(),
            size(&file),
            env.max_bytes,
            log.lines().last().unwrap_or("nothing logged")
        ),
        0,
    )
}

/// `run`: the sampler, as this process, on the clock.
fn run(env: &Env) -> Reply {
    let pid = std::process::id();
    let me = (pid, began(&env.proc, pid).unwrap_or(0));
    let why = work(env, me, &mut now, &mut |s| {
        std::thread::sleep(std::time::Duration::from_secs(s));
    });
    reply(format!("sampler: ended - {why}\n"), 0)
}

fn verb(args: &[String], env: &Env) -> Reply {
    match args.first().map(String::as_str) {
        Some("start") => start(env),
        Some("stop") => stop(env),
        Some("status") => status(env),
        Some("run") => run(env),
        Some("report") => report::cli(&args[1..], env),
        _ => reply(USAGE.to_owned(), 2),
    }
}

/// `l7r-gate measure sampler <args>` from `cwd`: the clone is `--common <dir>`'s, else the one `cwd` is in; `--first <secs>` is a
/// re-run's first start.
#[must_use]
pub fn cli(args: &[String], cwd: &Path) -> Reply {
    let flag = |name: &str| {
        args.iter()
            .position(|a| a == name)
            .and_then(|i| args.get(i + 1))
    };
    let Some(common) = flag("--common")
        .map(PathBuf::from)
        .or_else(|| l7r_shared::speckit::marks::places(cwd).map(|(common, _)| common))
    else {
        return reply("sampler: not in a git repository\n".to_owned(), 2);
    };
    let mut env = Env::live(&common);
    env.first = flag("--first").and_then(|f| f.parse().ok());
    verb(args, &env)
}

#[cfg(test)]
mod tests;
