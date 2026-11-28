//! A FAILURE REPRODUCED UNDER LOAD, BOUNDED (feature 462 T321, moved from 451): `l7r-gate rust under-load --cmd CMD --copies N
//! --loops N --max-minutes M [--burners N]`, behind `make under-load`. It runs `sh -c CMD` in COPIES copies at once, each LOOPS
//! times, beside BURNERS busy loops, prints the red count, the 1-minute load at its start, peak and end with their times, and writes
//! one `Phase` line (`src: rust`, step `under-load`, its make target `under-load`, which the guard's table books to tests). WHY: 451
//! T104's and T304's builders held the machine at a load of 240 to 400 for over an hour by hand (2026-11-26), slowing two batch gates
//! and failing a third suite; 462 T107/T173's and 461 T58's ran 10x and 30x loops by hand at loads of 38 to 86 (2026-11-27).
//!
//! - THE BOUND HOLDS WHATEVER THE CALLER DOES. The command re-runs itself as a WARDEN in a process group of its own, still under the
//!   caller's `make` (so the copies' own `make`s are the same run, `runlock.rs`, and overlap rather than queue on the tree's lock).
//!   The warden starts a SENTINEL first, `sleep <bound>; kill -s KILL 0`, whose group every copy and burner then joins: the warden
//!   stays outside it, so at its bound (or when every loop has run) it ends the group, TERM then KILL after [`GRACE_S`]; and should
//!   the warden itself die, the sentinel kills its own group at the bound plus twice the grace - the deadline the child enforces. The
//!   warden reads its standard input, a pipe its caller holds and never writes: at that pipe's end (the caller killed, its group
//!   killed) it ends the group at once and still writes its line, `ended: the caller went away`. The sentinel is reaped last, so
//!   the group's id is never reused while the warden can still signal it.
//! - ACCEPTED LIMITATIONS (462 T321, priced in its handoff): a CMD that starts a process group of its own (`setsid`, `timeout`, the
//!   pre-warm's cargo) leaves the group, and that part is ended only by its own parent; a sweep of `/proc` by an environment mark was
//!   priced and not built. A kill at the bound can cut a rustc mid-write (`prewarm.rs`: 29 of 54 cut builds failed to link after), so
//!   build first, then load: the help says so, and `stale.rs` heals such a link once.
//! - WHAT RE-RUNS: a plain `make rust-test` keeps its crate's green after the first loop and runs nothing after it; give it `ONLY=`
//!   (never kept) or run the test binary itself.
//! - THE COUNTS: a run's exit other than 0 is red, but a run ended by the bound or by the caller's going is CUT, counted apart. Each
//!   run's output goes to `c<copy>-l<loop>.log` in a directory of its own under the temporary directory; the green runs' logs are
//!   removed at the end. The exit is 1 where any run was red, else 0.

pub(super) mod warden;

use std::ffi::OsString;
use std::io::Read;
use std::os::unix::process::CommandExt as _;
use std::path::PathBuf;
use std::process::{Command, Stdio};
use std::time::Duration;

use super::World;
use crate::Reply;

/// The command's name, its `Phase` step and its make target.
pub(super) const STEP: &str = "under-load";
/// Set on the warden's environment: the run that does the work (taken off every process it starts).
pub(super) const WARDEN: &str = "L7R_UNDER_LOAD_WARDEN";
/// THE LONGEST BOUND ASKED (GUESS, a knob): an hour, the length 451 T104's and T304's hand loads ran past.
const MAX_MINUTES_CAP: f64 = 60.0;
/// THE MOST PROCESSES AT ONCE, copies and burners together, a multiple of the cores (GUESS, a knob): three, past tonight's 30
/// copies on 22 cores (a load of 38 to 86) and short of the loads of 240 to 400 this exists to prevent.
const PER_CORE: usize = 3;
/// THE GRACE between the TERM and the KILL (GUESS, a knob): ten seconds, a cargo run's own shutdown.
const GRACE_S: f64 = 10.0;
/// A burner: a shell's busy loop, one core.
const BURNER: &str = "while :; do :; done";
const USAGE: &str = "usage: make under-load CMD=\"<command>\" COPIES=<n> LOOPS=<n> MAX_MINUTES=<m> [BURNERS=<n>] - runs CMD in COPIES copies at once, each LOOPS times, beside BURNERS busy loops, all ended at MAX_MINUTES whatever the caller does; build first (a kill at the bound can cut a rustc), and give a make rust-test ONLY= so each loop runs again\n";

/// What was asked.
#[derive(Debug, Clone, PartialEq)]
pub(super) struct Ask {
    pub(super) cmd: String,
    pub(super) copies: usize,
    pub(super) loops: usize,
    pub(super) burners: usize,
    pub(super) max: Duration,
}

/// What the run reads the machine and the time by.
pub(super) struct Knobs {
    /// The program the warden is, and its words: this program, run again with its own words.
    pub(super) exe: PathBuf,
    pub(super) argv: Vec<OsString>,
    /// How often the warden looks at its loops, the load and the time.
    pub(super) poll: Duration,
    pub(super) grace: Duration,
    pub(super) burner: String,
    /// The shell every run, burner, sentinel and signal goes through.
    pub(super) shell: String,
    /// Where `loadavg` is read.
    pub(super) proc_root: PathBuf,
    /// Where each run's log directory is made.
    pub(super) out_root: PathBuf,
    pub(super) cores: usize,
}

impl Knobs {
    pub(super) fn here() -> Self {
        Self {
            exe: std::env::current_exe().unwrap_or_default(),
            argv: std::env::args_os().skip(1).collect(),
            poll: Duration::from_millis(500),
            grace: Duration::from_secs_f64(GRACE_S),
            burner: BURNER.to_owned(),
            shell: "sh".to_owned(),
            proc_root: PathBuf::from("/proc"),
            out_root: std::env::temp_dir(),
            cores: std::thread::available_parallelism().map_or(1, usize::from),
        }
    }
}

fn number(words: &[String], flag: &str) -> Result<Option<f64>, String> {
    match words.iter().position(|w| w == flag) {
        None => Ok(None),
        Some(i) => words
            .get(i + 1)
            .and_then(|v| v.parse::<f64>().ok())
            .filter(|v| v.is_finite() && *v >= 0.0)
            .map(Some)
            .ok_or_else(|| format!("under-load: {flag} takes a number\n")),
    }
}

#[expect(
    clippy::cast_possible_truncation,
    clippy::cast_sign_loss,
    reason = "a count was read as a whole non-negative number"
)]
fn count(words: &[String], flag: &str, least: usize) -> Result<usize, String> {
    let n = number(words, flag)?.unwrap_or(0.0);
    if n.fract() != 0.0 || (n as usize) < least {
        return Err(format!(
            "under-load: {flag} takes a whole number, at least {least}\n"
        ));
    }
    Ok(n as usize)
}

/// The words read, or the usage error.
pub(super) fn parse(words: &[String], cores: usize) -> Result<Ask, String> {
    let cmd = words
        .iter()
        .position(|w| w == "--cmd")
        .and_then(|i| words.get(i + 1))
        .filter(|c| !c.trim().is_empty())
        .ok_or("under-load: CMD is required\n")?
        .clone();
    let (copies, loops) = (count(words, "--copies", 1)?, count(words, "--loops", 1)?);
    let burners = count(words, "--burners", 0)?;
    let minutes = number(words, "--max-minutes")?.unwrap_or(0.0);
    if minutes <= 0.0 || minutes > MAX_MINUTES_CAP {
        return Err(format!(
            "under-load: MAX_MINUTES is required, above 0 and at most {MAX_MINUTES_CAP}\n"
        ));
    }
    let most = PER_CORE * cores;
    if copies + burners > most {
        return Err(format!(
            "under-load: COPIES + BURNERS is {}, past {most} ({PER_CORE} a core on {cores})\n",
            copies + burners
        ));
    }
    Ok(Ask {
        cmd,
        copies,
        loops,
        burners,
        max: Duration::from_secs_f64(minutes * 60.0),
    })
}

/// The command: the usage checked, then the warden's run (`warden` set: this is the warden, its caller's pipe on `caller`) or the
/// caller's, which starts the warden and hands back its report.
pub(super) fn entry(
    world: &World,
    words: &[String],
    knobs: &Knobs,
    warden: bool,
    caller: Box<dyn Read + Send>,
) -> Reply {
    match parse(words, knobs.cores) {
        Err(why) => Reply {
            stdout: String::new(),
            stderr: format!("{why}{USAGE}"),
            code: 2,
        },
        Ok(ask) if warden => warden::run(world, &ask, knobs, caller),
        Ok(_) => supervise(knobs),
    }
}

/// The caller's side: the warden started in a group of its own, its standard input a pipe held here until it ends, its report read.
fn supervise(knobs: &Knobs) -> Reply {
    let started = Command::new(&knobs.exe)
        .args(&knobs.argv)
        .env(WARDEN, "1")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .process_group(0)
        .spawn();
    let mut child = match started {
        Ok(c) => c,
        Err(e) => {
            return Reply {
                stdout: String::new(),
                stderr: format!("under-load: {}: {e}\n", knobs.exe.display()),
                code: 1,
            }
        }
    };
    let held = child.stdin.take();
    let mut stdout = String::new();
    if let Some(mut out) = child.stdout.take() {
        let _ = out.read_to_string(&mut stdout);
    }
    let code = child.wait().ok().and_then(|s| s.code()).unwrap_or(1);
    drop(held);
    Reply {
        stdout,
        stderr: String::new(),
        code,
    }
}
