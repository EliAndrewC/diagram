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
//! - IT YIELDS BETWEEN CRATES. It is the one compile nobody waits on, so it STARTS a crate only while a slot is SPARE: it takes one
//!   only where one is free at that instant (`slot::free_now`) and a second is free beside it (`slot::spare`), and never waits in
//!   the slots' queue. A real run of the checks in ITS tree (a live member of the run lock's record, `runlock::busy`; the pre-warm
//!   joins none) ends it, that run having the build from there, and so does its ceiling; with no slot spare it starts nothing more
//!   until two are free. With one slot on the machine it never builds.
//! - IT NEVER CUTS A BUILD IN FLIGHT (feature 451 T336). The first form killed its cargo, and the rustc under it, the moment a real
//!   run started or the last slot was taken. A test build killed while its rustc is past the front end can leave the crate's last
//!   FINISHED incremental session - the one the next build starts from - written into, and every later link of that crate then
//!   fails (`rust-lld: error: undefined hidden symbol ... .llvm.<n>`) until the crate's incremental directories are removed.
//!   Measured 2026-11-26 on `rust/guard`: of 54 tries with a build cut, 29 then failed to link (SIGTERM 16 of 31, SIGKILL 7 of 10,
//!   SIGINT 6 of 13) - each of them a cut that had changed files of the finished session in place, none a cut in the build's
//!   first 3 s - and none of 20 tries left to finish did (`dev/measurements/2026-11-26/prewarm-link/`). (Inferred, not read in
//!   rustc: the working session's files are hard links of the finished one's, written in place under the dev profile's
//!   `opt-level = 2`.) No moment safe to kill at is visible from outside, so the crate in flight is always finished, its slot held
//!   until then: a real run's cargo waits on cargo's own lock of the build directory for the rest of that one crate, and a compile
//!   of another tree can wait in the slots' queue as long (of 160 crates pre-warmed on 2026-11-26 the median took 2.0 s, nine in
//!   ten under 13.0 s, the longest, `rust/mode_a`, 82.7 s; the limitation accepted and the alternatives priced in
//!   `dev/audits/builder-prewarm.md`). Do not bring the kill back to shorten that wait: a failed link costs its builder a
//!   from-nothing rebuild (`stale.rs` heals it once), and the wait is bounded by one crate.
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
/// How often it looks whether its cargo is done, and for a spare slot before it starts a crate (GUESS: the slot's and the run lock's
/// own half second).
const POLL: Duration = Duration::from_millis(500);
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

/// How one crate's build ended: cargo's own exit, and how long it ran on after the moment the pre-warm would yield - a real run in
/// its tree, no slot spare, the ceiling - where there was one (what never cutting a build costs, said on the crate's line).
struct End {
    code: i32,
    past: Option<Duration>,
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

/// One crate's test build, under `hold` where the machine has slots, ALWAYS to its end (the module's "never cuts"): a real run
/// starting in the tree, the last slot taken or the ceiling passing while it runs is noted, with the time, and the build goes on.
/// Cargo is its own process group, so a signal sent to the pre-warm's group - a terminal's, a caller's timeout - does not reach
/// a rustc mid-write either. Its `Phase` line carries cargo's own code.
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
    let mut asked: Option<Instant> = None;
    let code = match started {
        Err(_) => 127,
        Ok(mut child) => loop {
            if let Some(status) = child.try_wait().ok().flatten() {
                break status.code().unwrap_or(1);
            }
            if asked.is_none()
                && (real_run(world, knobs) || crowded(world) || Instant::now() >= until)
            {
                asked = Some(Instant::now());
            }
            std::thread::sleep(knobs.poll);
        },
    };
    drop(hold);
    phase::wrote(world, STEP, &[manifest], began, code);
    End {
        code,
        past: asked.map(|at| at.elapsed()),
    }
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
        let end = build(world, &manifest, knobs, hold, until);
        let secs = began.elapsed().as_secs_f64();
        // what the loop's head then does - ends the pre-warm, or waits for a spare slot - it does after this crate, never during it
        let past = end.past.map_or_else(String::new, |p| {
            format!(
                ", {:.1} s of it finishing after a run started, no slot was spare or the ceiling passed",
                p.as_secs_f64()
            )
        });
        if end.code == 0 {
            let _ = writeln!(
                out,
                "prewarm: {name} - its test build is warm ({secs:.1} s{past})"
            );
        } else {
            let _ = writeln!(out, "prewarm: {name} - cargo test --no-run exited {}; left to the builder's own run, which says why", end.code);
        }
        todo.pop_front();
    }
    said(out, 0)
}
