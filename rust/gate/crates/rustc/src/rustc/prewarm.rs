//! THE PRE-WARM (feature 451 T316; the GM 2026-11-26: "would it make sense to begin compiling immediately within a work tree
//! builder?"): `l7r-gate rust prewarm --since <commit>`, started detached by `make builder-tree` when it hands a pool tree out
//! (`task/src/builder_tree.rs`). A pool tree's build cache is warm for what the tree last built; the commits others landed since are
//! compiled by the builder's first test run, and a builder reads for a median 4.6 to 5.7 minutes before its first source edit
//! (`dev/measurements/2026-11-26/split-reproduction`). So the test builds of the crates whose build moved are asked while it reads.
//!
//! - WHAT IS BUILT: each crate whose build reads a file the commits `<since>..HEAD` changed - its own sources, a crate's it builds
//!   from, the workspace's manifests (`Kept::reads_any` over the lint key's inputs, `Reads::Source`) - fewest dependencies first. The
//!   build is the one a real run asks first (`stepped`, 449 T93's `binary_key`): `cargo test --no-run`, its words and environment from
//!   the builder every cargo call of the checks uses (`cargo_call`), so the run then finds it fresh. Nothing is run and no result is
//!   kept: a kept result is a real run's alone. The lint's build (clippy's own artifacts) and a coverage build are not warmed.
//! - IT YIELDS. It is the one compile nobody waits on, so it holds a slot only while another is SPARE: it takes one only where one
//!   is free at that instant (`slot::free_now`) and a second is free beside it (`slot::spare`), never waits in the slots' queue,
//!   and looks every poll while its cargo runs - a real run of the checks in ITS tree (a live member of the run lock's record,
//!   `runlock::busy`; the pre-warm joins none) ends it, that run having the build from there; and once no slot is spare - a compile
//!   of any tree took the last - it kills its cargo, gives its slot back and tries the crate again when two are free. So the next
//!   compile to start, of any tree and whatever slot code that tree runs, finds a slot: none waits behind a pre-warm for more than
//!   a poll. With one slot on the machine it never builds. What cargo finished stays built.
//! - IT NEVER FAILS ANYTHING: nothing waits on it, it exits 0 whatever cargo said (a crate that does not build is the builder's own
//!   run's to report), one pre-warm a tree at a time (`prewarm.lock` in the target directory), and it stops at its ceiling.
//!   `L7R_PREWARM=0` is no pre-warm.
//! - IT IS BOOKED APART: each cargo call it makes writes one `Phase` line, step `prewarm`, make target `prewarm` - never `build`, so
//!   `make task-time` puts none of it in the task's own compile (`measure`'s `columns::category`).

use std::collections::{BTreeSet, VecDeque};
use std::fmt::Write as _;
use std::os::unix::process::CommandExt as _;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::time::{Duration, Instant, SystemTime};

use super::kept::{git_z, Kept, Reads};
use super::{cargo_call, crates, phase, runlock, shown, slot, test_args, World};
use crate::Reply;

/// The command's name, its `Phase` step and its make target.
pub(super) const STEP: &str = "prewarm";
/// `0` is no pre-warm.
const OFF: &str = "L7R_PREWARM";
/// The seconds a pre-warm lasts at most.
const CEILING: &str = "L7R_PREWARM_CEILING";
/// THE CEILING (GUESS, a knob: `L7R_PREWARM_CEILING` seconds): fifteen minutes, the build slot's own ceiling - past the 4.6 to 5.7
/// minutes a builder reads before its first edit, so a pre-warm nobody cut short is never left running under a tree for long.
const CEILING_S: u64 = 900;
/// How often it looks for a real run or for no slot spare (GUESS: the slot's and the run lock's own half second - the longest a real run's
/// cargo call waits on the pre-warm's).
const POLL: Duration = Duration::from_millis(500);
/// The code a `Phase` line carries for a build cut short (a shell's own for an interrupted program).
const CUT: i32 = 130;
const USAGE: &str = "usage: l7r-gate rust prewarm --since <commit>\n";

/// What a pre-warm reads the time by.
pub(super) struct Knobs {
    pub(super) poll: Duration,
    pub(super) ceiling: Duration,
    pub(super) proc_root: PathBuf,
    /// The seconds it waits its turn on the tree's `prewarm.lock`: a lock just let go can read held for a moment more (a child
    /// another thread is starting holds a copy of the open file until its exec, as `slot.rs` says of a slot).
    pub(super) lock_s: f64,
}

impl Knobs {
    /// The knobs of a run: the ceiling from `L7R_PREWARM_CEILING` where it names whole seconds.
    pub(super) fn of(world: &World) -> Self {
        let ceiling = world
            .root
            .opt(CEILING)
            .and_then(|v| v.trim().parse().ok())
            .unwrap_or(CEILING_S);
        Self {
            poll: POLL,
            ceiling: Duration::from_secs(ceiling),
            proc_root: PathBuf::from("/proc"),
            lock_s: 1.0,
        }
    }
}

/// How one crate's build ended: cargo's own exit, or cut short.
enum End {
    Built(i32),
    Cut,
}

/// The machine has slots and none is free: the next compile to start would wait behind this one.
fn crowded(world: &World) -> bool {
    world.slots.count > 0 && !slot::spare(&world.slots)
}

fn real_run(world: &World, knobs: &Knobs) -> bool {
    runlock::dirs_of(world)
        .iter()
        .any(|d| runlock::busy(d, &knobs.proc_root))
}

/// The crates whose build reads a file the commits `since..HEAD` changed, a crate before the crates that build on it.
fn moved(world: &World, since: &str) -> Vec<PathBuf> {
    let files: BTreeSet<String> = git_z(&world.root, &["diff", "--name-only", "-z", since, "HEAD"])
        .into_iter()
        .collect();
    let all = crates(&world.root, &[]);
    let kept = Kept::read(world, STEP, Reads::Source, &all);
    let mut found: Vec<(usize, PathBuf)> = all
        .iter()
        .filter(|m| kept.reads_any(&world.root, STEP, m, &files))
        .map(|m| (kept.builds_from(&world.root, m), m.clone()))
        .collect();
    found.sort();
    found.into_iter().map(|(_, m)| m).collect()
}

/// One crate's test build, under `hold` where the machine has slots: watched every poll, and cut short - cargo and what it started
/// killed as one process group - once a real run starts in the tree, no slot is spare or the ceiling passes. Its `Phase` line
/// is written either way.
fn build(
    world: &World,
    manifest: &Path,
    knobs: &Knobs,
    hold: Option<slot::Hold>,
    until: Instant,
) -> End {
    let words = test_args("test", manifest, true);
    let args: Vec<&str> = words.iter().map(String::as_str).collect();
    let (all, mut env) = cargo_call(world, &args, manifest, &[], None);
    // as under any holder (`slot::around`): nothing the build starts takes a second slot
    env.insert(slot::MARK.to_owned(), "1".to_owned());
    let began = SystemTime::now();
    let started = Command::new(&world.cargo)
        .current_dir(&*world.root)
        .args(&all)
        .envs(&env)
        .env_remove("L7R_GATE_TREE")
        .stdin(Stdio::null())
        .stdout(Stdio::null())
        .process_group(0)
        .spawn();
    let how = match started {
        Err(_) => End::Built(127),
        Ok(mut child) => loop {
            if let Some(status) = child.try_wait().ok().flatten() {
                break End::Built(status.code().unwrap_or(1));
            }
            if real_run(world, knobs) || crowded(world) || Instant::now() >= until {
                let _ = Command::new("kill")
                    .args(["-TERM", "--", &format!("-{}", child.id())])
                    .status();
                let _ = child.wait();
                break End::Cut;
            }
            std::thread::sleep(knobs.poll);
        },
    };
    drop(hold);
    let code = match how {
        End::Built(code) => code,
        End::Cut => CUT,
    };
    phase::wrote(world, STEP, &[manifest], began, code);
    how
}

fn said(stdout: String, code: i32) -> Reply {
    Reply {
        stdout,
        stderr: String::new(),
        code,
    }
}

/// `l7r-gate rust prewarm --since <commit>`: what it did, a line a crate, exit 0 but for a usage error.
pub(super) fn run(world: &World, args: &[String], knobs: &Knobs) -> Reply {
    let [flag, since] = args else {
        return said(USAGE.to_owned(), 2);
    };
    if flag != "--since" {
        return said(USAGE.to_owned(), 2);
    }
    if world.root.opt(OFF).as_deref() == Some("0") {
        return said(format!("prewarm: off ({OFF}=0)\n"), 0);
    }
    let Ok(Some(_one)) =
        l7r_shared::tool::flock_within(&world.target.join("prewarm.lock"), knobs.lock_s)
    else {
        return said(
            "prewarm: another pre-warm of this tree is at work - nothing started\n".to_owned(),
            0,
        );
    };
    let mut todo: VecDeque<PathBuf> = moved(world, since).into();
    let mut out = format!(
        "prewarm: {} crate(s) whose build moved since {since}\n",
        todo.len()
    );
    let until = Instant::now() + knobs.ceiling;
    let who = format!(
        "{} (pid {}, pre-warm): cargo test --no-run\n",
        world.root.file_name().unwrap_or_default().to_string_lossy(),
        std::process::id()
    );
    while let Some(manifest) = todo.front().cloned() {
        if real_run(world, knobs) {
            let _ = writeln!(out, "prewarm: a run of the checks started in this tree and has the build from here - {} crate(s) left to it", todo.len());
            break;
        }
        if Instant::now() >= until {
            let _ = writeln!(
                out,
                "prewarm: stopped at its ceiling of {} s ({CEILING}) - {} crate(s) not built",
                knobs.ceiling.as_secs(),
                todo.len()
            );
            break;
        }
        let slots = world.slots.count > 0;
        let hold = slots
            .then(|| slot::free_now(&world.slots, &who))
            .flatten()
            .filter(|_| slot::spare(&world.slots));
        if slots && hold.is_none() {
            // no slot free, or none spare beside it: a real compile's first
            std::thread::sleep(knobs.poll);
            continue;
        }
        let began = Instant::now();
        let name = shown(world, &manifest);
        match build(world, &manifest, knobs, hold, until) {
            End::Built(0) => {
                let secs = began.elapsed().as_secs_f64();
                let _ = writeln!(
                    out,
                    "prewarm: {name} - its test build is warm ({secs:.1} s)"
                );
                todo.pop_front();
            }
            End::Built(code) => {
                let _ = writeln!(out, "prewarm: {name} - cargo test --no-run exited {code}; left to the builder's own run, which says why");
                todo.pop_front();
            }
            // the loop's head says why, or waits for a spare slot and builds the crate again
            End::Cut => {
                let _ = writeln!(out, "prewarm: {name} - cut short, its slot given back");
            }
        }
    }
    said(out, 0)
}
