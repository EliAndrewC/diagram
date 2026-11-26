//! THE BUILD SLOT (feature 451 T284; the GM 2026-11-26: "wouldn't it be better to address that with some synchronization rather than
//! pre-emptively limiting builders just in case?"): nothing kept two trees' compiles apart, so the number of builders at once was capped
//! by the chance that their compiles coincide. Measured 2026-11-26 over the three-builder run's samples and the checks' `Phase` lines
//! (`dev/measurements/2026-11-26/builder-count/slot-coincide.py`): every one of the twelve highest memory samples (5.9-6.4 GiB
//! anonymous of the container's 10) and seven of the eight highest counts of rustc (39-46) fell where all three trees were in a
//! coverage build at once, 1,396 of the window's 2,602 s; one tree's own checks never ran two compiling cargo calls at once.
//!
//! So each cargo call that compiles - a coverage build, a test build, a `cargo test`, clippy, a stage's `cargo run`; never `cargo fmt`,
//! which compiles nothing - holds one of `L7R_BUILD_SLOTS` slots for its length, machine-wide: the `flock` of a file `slot-<i>` under
//! `~/.cache/l7r-build-slots/` (`L7R_BUILD_SLOT_DIR`), outside every tree, so a builder's checks and a landing's gate take the same
//! ones. The lock is the open file's: a holder that dies, killed or not, frees its slot with no daemon and nothing to clear by hand.
//! (A slot just let go may read held for a moment more: a child another thread is starting holds a copy of the open file until its
//! exec. A waiter's next look finds it free; seen 2026-11-26 in the slot's own tests under three builders' load.)
//!
//! NEVER A DEADLOCK, NEVER A REFUSAL: a call holds one slot and waits for no second; the cargo it starts carries `L7R_BUILD_SLOT_HELD`,
//! so a gate run inside it (a crate's tests that run the checks) takes none; and the slot is throughput, not correctness, so a
//! directory that cannot be made, a `flock` that cannot start and a wait past the ceiling each let the call run without one, said on
//! stderr. `L7R_BUILD_SLOTS=0` is no slot at all.
//!
//! THE WAIT IS BOOKED: a call that waited writes one `Phase` line, `slot-wait`, which `make task-time` books as `waiting on a build
//! slot` ahead of the compile it precedes, and says so on stderr each minute it lasts.

use std::collections::BTreeMap;
use std::fs::File;
use std::io::Write as _;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::time::{Duration, Instant, SystemTime};

use super::runlock::{Clock, Wall};
use super::World;

/// How many compiling cargo calls run at once on the machine; `0` is no slot.
pub(super) const COUNT: &str = "L7R_BUILD_SLOTS";
/// Where the slot files are, when not `~/.cache/l7r-build-slots`.
pub(super) const DIR: &str = "L7R_BUILD_SLOT_DIR";
/// Set on the cargo a slot's holder starts: a gate run under it takes no slot.
pub(super) const MARK: &str = "L7R_BUILD_SLOT_HELD";
/// The seconds a call waits before it runs without a slot.
pub(super) const CEILING: &str = "L7R_BUILD_SLOT_CEILING";
/// The wait's `Phase` step.
pub(super) const STEP: &str = "slot-wait";

/// THE COUNT (GUESS, a knob: `L7R_BUILD_SLOTS`): two. Three compiles at once is the measured peak the slot is there to stop (6.4 GiB,
/// load median 42 on 22 cores, so the third added no throughput), and one cargo call already asks for a job a core (`-j` 22, left as
/// it is): at the peaks each of three ran about 15 rustc, so two fill the cores. Two at once was the measured state at two builders
/// (peak 6.3 GiB only where a landing's gate made a third). One would also hold memory, and queue every tree behind every other;
/// unmeasured. Retuned from `make task-time`'s `waiting on a build slot` minutes against the compile minutes beside them.
const DEFAULT: usize = 2;
/// THE CEILING (GUESS, a knob: `L7R_BUILD_SLOT_CEILING` seconds): past it the call runs without a slot. Fifteen minutes outlasts the
/// longest coverage build measured under three-way load (589 s), and is half the run lock's 1,800 s ceiling, which a slot's waiter
/// holds its target directory under: a hung holder costs a tree a quarter hour, never a refusal.
const CEILING_S: u64 = 900;
/// A waiter says it waits once a minute (the task: "a notice when a wait passes a minute").
const NOTICE: Duration = Duration::from_secs(60);
/// How often a waiter looks again (GUESS: half a second, against compiles of tens of seconds; each look starts one `flock` a slot).
const POLL: Duration = Duration::from_millis(500);

/// The machine's slots as one run reads them.
pub(super) struct Slots {
    pub(super) dir: PathBuf,
    pub(super) count: usize,
    pub(super) ceiling: Duration,
    pub(super) notice: Duration,
    pub(super) poll: Duration,
    /// The `flock` program (a test names one that cannot start).
    pub(super) flock: String,
    pub(super) clock: Box<dyn Clock>,
}

impl Slots {
    /// No slot: every take is a no-op (`L7R_BUILD_SLOTS=0`, a run under a holder, a test's world).
    pub(super) fn off() -> Self {
        Self::at(PathBuf::new(), 0)
    }

    /// `count` slots under `dir`, the knobs at their defaults, on the wall clock.
    pub(super) fn at(dir: PathBuf, count: usize) -> Self {
        Self {
            dir,
            count,
            ceiling: Duration::from_secs(CEILING_S),
            notice: NOTICE,
            poll: POLL,
            flock: "flock".to_owned(),
            clock: Box::new(Wall(Instant::now())),
        }
    }

    /// The run's slots, from its environment: none under a holder's mark, else `L7R_BUILD_SLOTS` of them (the default where it is
    /// unset or no number) under `L7R_BUILD_SLOT_DIR`, or the home's cache.
    pub(super) fn of(env: &dyn Fn(&str) -> Option<String>, home: &Path) -> Self {
        let set = |k: &str| env(k).filter(|v| !v.trim().is_empty());
        if set(MARK).is_some() {
            return Self::off();
        }
        let count = set(COUNT)
            .and_then(|v| v.trim().parse().ok())
            .unwrap_or(DEFAULT);
        let dir = set(DIR).map_or_else(|| home.join(".cache/l7r-build-slots"), PathBuf::from);
        let ceiling = set(CEILING)
            .and_then(|v| v.trim().parse().ok())
            .unwrap_or(CEILING_S);
        Self {
            ceiling: Duration::from_secs(ceiling),
            ..Self::at(dir, count)
        }
    }
}

/// A slot held: its open file, whose `flock` lasts as long as it does.
pub(super) struct Hold {
    _file: File,
}

/// What a take came to: the slot, where one was taken, and how long the call waited, where it waited at all.
pub(super) struct Taken {
    pub(super) hold: Option<Hold>,
    pub(super) waited: Option<Duration>,
}

enum Try {
    Got,
    Busy,
    Broken(String),
}

/// `flock -n` on the open file, through the program as `l7r_shared::tool::flock` asks it, a program that cannot start told apart from
/// a slot that is held: the first is a machine with no slots, the second a wait.
fn try_lock(flock: &str, file: &File) -> Try {
    let asked = file.try_clone().and_then(|f| {
        Command::new(flock)
            .args(["-n", "0"])
            .stdin(f)
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .status()
    });
    match asked {
        Ok(status) if status.success() => Try::Got,
        Ok(_) => Try::Busy,
        Err(e) => Try::Broken(format!("cannot run {flock}: {e}")),
    }
}

fn slot_file(slots: &Slots, i: usize) -> PathBuf {
    slots.dir.join(format!("slot-{i}"))
}

/// The first free slot, taken and signed with `who`; none where every one is held; an error where there are no slots to ask.
fn first_free(slots: &Slots, who: &str) -> Result<Option<File>, String> {
    std::fs::create_dir_all(&slots.dir)
        .map_err(|e| format!("cannot make {}: {e}", slots.dir.display()))?;
    for i in 0..slots.count {
        let path = slot_file(slots, i);
        let file = std::fs::OpenOptions::new()
            .read(true)
            .write(true)
            .create(true)
            .truncate(false)
            .open(&path)
            .map_err(|e| format!("cannot open {}: {e}", path.display()))?;
        match try_lock(&slots.flock, &file) {
            Try::Got => {
                let _ = file.set_len(0);
                let _ = (&file).write_all(who.as_bytes());
                return Ok(Some(file));
            }
            Try::Busy => {}
            Try::Broken(reason) => return Err(reason),
        }
    }
    Ok(None)
}

/// Who signed each slot, for a waiter's line.
fn holders(slots: &Slots) -> String {
    (0..slots.count)
        .filter_map(|i| std::fs::read_to_string(slot_file(slots, i)).ok())
        .map(|s| s.trim().to_owned())
        .filter(|s| !s.is_empty())
        .collect::<Vec<_>>()
        .join("; ")
}

/// Take a slot for `who`, waiting while every one is held (said through `say` each `notice`); without one where there are none to
/// take or the wait passes the ceiling, said too.
pub(super) fn take(slots: &Slots, who: &str, say: &mut dyn FnMut(&str)) -> Taken {
    let mut waited = None;
    if slots.count == 0 {
        return Taken { hold: None, waited };
    }
    let began = slots.clock.now();
    let mut next = slots.notice;
    loop {
        let so_far = slots.clock.now().saturating_sub(began);
        match first_free(slots, who) {
            Ok(Some(file)) => {
                return Taken {
                    hold: Some(Hold { _file: file }),
                    waited: waited.map(|_| so_far),
                };
            }
            Ok(None) => {}
            Err(reason) => {
                say(&format!(
                    "rust-checks: no build slot to take ({reason}) - this cargo call runs without one (feature 451 T284)\n"
                ));
                return Taken { hold: None, waited };
            }
        }
        waited = Some(so_far);
        if so_far >= slots.ceiling {
            say(&format!(
                "rust-checks: waited {} s on a build slot, the ceiling ({CEILING} seconds) - this cargo call runs without one; held by: {}\n",
                so_far.as_secs(),
                holders(slots)
            ));
            return Taken { hold: None, waited };
        }
        if so_far >= next {
            say(&format!(
                "rust-checks: waiting on a build slot, {} s so far - {} compiling cargo call(s) run at once on this machine ({COUNT}, feature 451 T284); held by: {}\n",
                so_far.as_secs(),
                slots.count,
                holders(slots)
            ));
            next += slots.notice;
        }
        slots.clock.sleep(slots.poll);
    }
}

/// A slot around the cargo call `args` that `env` is about to start: taken (its wait, where there was one, written as a `slot-wait`
/// `Phase` line and said on stderr), and the holder's mark put in `env` so nothing under the call takes a second. The slot is held
/// until what this returns is dropped.
pub(super) fn around(
    world: &World,
    args: &[String],
    env: &mut BTreeMap<String, String>,
) -> Option<Hold> {
    let began = SystemTime::now();
    let tree = world.root.file_name().unwrap_or_default().to_string_lossy();
    let what: Vec<&str> = args.iter().take(2).map(String::as_str).collect();
    let who = format!(
        "{tree} (pid {}, make {}): cargo {}\n",
        std::process::id(),
        world.make,
        what.join(" ")
    );
    let taken = take(&world.slots, &who, &mut |line| eprint!("{line}"));
    if taken.waited.is_some() {
        let none: [&Path; 0] = [];
        let code = i32::from(taken.hold.is_none());
        super::phase::wrote(world, STEP, &none, began, code);
    }
    if taken.hold.is_some() {
        env.insert(MARK.to_owned(), "1".to_owned());
    }
    taken.hold
}
