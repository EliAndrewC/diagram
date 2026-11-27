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
//!   kept: a kept result is a real run's alone. A coverage build and the counting build (`test-counters`) are not warmed.
//! - IT KEEPS THE SMALL LANE'S KEYS (feature 451 T367, T411). A passing build keeps the key a wide build of the checks keeps
//!   (`kept/alone.rs`'s `keeping`), told as the checks tell it - the test build by the binary key's words (`binary_args`), so a
//!   builder's first test build after a handout is told alone and never waits for a wide slot. Measured 2026-11-27 from the clone's
//!   event log over the three hours after T347 landed: 28 of the 29 first test builds of a crate in a tree after a handout were
//!   told wide. Then, after every test build, EACH PASS OF EACH CRATE'S LINT (`lint.rs`'s `passes` and `told`, `-D warnings`
//!   handed on): clippy's check units are not the test build's, so without them a builder's first lint compiled 2.5 to 28.9 s in a
//!   wide slot (451 T355's record). A red pass is its crate's last, as in the lint, and keeps no key. `L7R_PREWARM_LINT=0` warms
//!   the test builds alone.
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
//!   `make task-time` puts none of it in the task's own compile (`measure`'s `columns::category`). Its tellings' `slot-tell` lines
//!   carry the same make target, so a count of a builder's tellings leaves them out.

use std::collections::{BTreeSet, VecDeque};
use std::fmt::Write as _;
use std::os::unix::process::CommandExt as _;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::time::{Duration, Instant, SystemTime};

use super::kept::{binary_args, git_z, Kept, Reads, Told};
use super::{cargo_call, crates, lint, phase, runlock, shown, slot, test_args, World};
use crate::Reply;

/// The command's name, its `Phase` step and its make target.
pub(super) const STEP: &str = "prewarm";
/// `0` is no pre-warm.
const OFF: &str = "L7R_PREWARM";
/// The seconds a pre-warm lasts at most.
const CEILING: &str = "L7R_PREWARM_CEILING";
/// `0` warms the test builds alone (feature 451 T411; GUESS, a knob, on: the passes added 17.3 s to a real handout's pre-warm of
/// three crates, after 3.0 s of test builds, measured 2026-11-27 on `diagram-backlog-t271` - seconds nobody waits on, in a slot
/// taken only while another is spare; `dev/measurements/2026-11-27/prewarm-keys/`).
const LINT: &str = "L7R_PREWARM_LINT";
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

/// One build the pre-warm asks of a crate: its test build, or one pass of its lint (its words).
#[derive(Clone, Copy, PartialEq)]
enum Job {
    Test,
    Lint(&'static [&'static str]),
}

impl Job {
    /// Its words to cargo, and the words handed on to what cargo runs.
    fn words(self, manifest: &Path) -> (Vec<String>, &'static [&'static str]) {
        match self {
            Self::Test => (test_args("test", manifest, true), &[]),
            Self::Lint(words) => (words.iter().map(|w| (*w).to_owned()).collect(), &lint::DENY),
        }
    }

    /// Its telling, as the checks tell the same build. (Outside a repository, where the checks tell nothing, no commit moved any
    /// crate, so nothing is asked.)
    fn told(self, world: &World, manifest: &Path, kept: &Kept) -> Told {
        match self {
            Self::Test => Told::of(world, "test", manifest, kept, &binary_args("test")),
            Self::Lint(words) => lint::told(world, words, manifest, kept),
        }
    }
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

/// The crates whose build reads a file the commits `since..HEAD` changed, a crate before the crates that build on it, and the content
/// ids their builds are told by - read as a test run reads them (`test`: with what each file compiles in), so a key the pre-warm
/// keeps is the one a run is told by.
fn moved(world: &World, since: &str) -> (Vec<PathBuf>, Kept) {
    let files: BTreeSet<String> = git_z(&world.root, &["diff", "--name-only", "-z", since, "HEAD"])
        .into_iter()
        .collect();
    let all = crates(&world.root, &[]);
    let kept = Kept::read(world, "test", Reads::Source, &all);
    let mut found: Vec<(usize, PathBuf)> = all
        .iter()
        .filter(|m| kept.reads_any(&world.root, STEP, m, &files))
        .map(|m| (kept.builds_from(&world.root, m), m.clone()))
        .collect();
    found.sort();
    (found.into_iter().map(|(_, m)| m).collect(), kept)
}

/// One build of a crate, under `hold` where the machine has slots, ALWAYS to its end (the module's "never cuts"): a real run
/// starting in the tree, the last slot taken or the ceiling passing while it runs is noted, with the time, and the build goes on.
/// Cargo is its own process group, so a signal sent to the pre-warm's group - a terminal's, a caller's timeout - does not reach
/// a rustc mid-write either. Its key is kept where it passes (`told`); its `Phase` line carries cargo's own code.
fn build(
    world: &World,
    manifest: &Path,
    job: Job,
    told: &Told,
    knobs: &Knobs,
    hold: Option<slot::Hold>,
    until: Instant,
) -> End {
    let (words, after) = job.words(manifest);
    let args: Vec<&str> = words.iter().map(String::as_str).collect();
    let (all, mut env) = cargo_call(world, &args, manifest, after, None);
    // as under any holder (`slot::around`): nothing the build starts takes a second slot
    env.insert(slot::MARK.to_owned(), "1".to_owned());
    let began = SystemTime::now();
    let mut asked: Option<Instant> = None;
    let code = told.keeping(STEP, || {
        let started = Command::new(&world.cargo)
            .current_dir(&*world.root)
            .args(&all)
            .envs(&env)
            .env_remove("L7R_GATE_TREE")
            .stdin(Stdio::null())
            .stdout(Stdio::null())
            .process_group(0)
            .spawn();
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
        (code, code == 0)
    });
    drop(hold);
    phase::wrote(world, STEP, &[manifest], began, code);
    End {
        code,
        past: asked.map(|at| at.elapsed()),
    }
}

/// What is left of the queue, as a line's end says it: the crates whose test build is left, and the lint passes after them.
fn left(todo: &VecDeque<(PathBuf, Job)>, what: &str, passes: &str) -> String {
    let tests = todo.iter().filter(|(_, j)| *j == Job::Test).count();
    let lints = todo.len() - tests;
    let mut said = format!("{tests} crate(s) {what}");
    if lints > 0 {
        let _ = write!(said, ", and {lints} lint pass(es) {passes}");
    }
    said
}

fn said(stdout: String, code: i32) -> Reply {
    Reply {
        stdout,
        stderr: String::new(),
        code,
    }
}

/// The line a build of `name`'s crate ends with: warm, with its seconds, or the exit cargo gave.
fn said_of(name: &str, job: Job, words: &[String], end: &End, took: Duration) -> String {
    let secs = took.as_secs_f64();
    // what the loop's head then does - ends the pre-warm, or waits for a spare slot - it does after this crate, never during it
    let past = end.past.map_or_else(String::new, |p| {
        format!(
            ", {:.1} s of it finishing after a run started, no slot was spare or the ceiling passed",
            p.as_secs_f64()
        )
    });
    let named = words[2..].join(" ");
    match (job, end.code) {
        (Job::Test, 0) => format!("prewarm: {name} - its test build is warm ({secs:.1} s{past})\n"),
        (Job::Test, code) => format!("prewarm: {name} - cargo test --no-run exited {code}; left to the builder's own run, which says why\n"),
        (Job::Lint(_), 0) => format!("prewarm: {name} - its lint pass {named} is warm ({secs:.1} s{past})\n"),
        (Job::Lint(_), code) => format!("prewarm: {name} - cargo clippy {named} exited {code}; its later passes left to the builder's own lint, which says why\n"),
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
    let (crates, kept) = moved(world, since);
    let mut todo: VecDeque<(PathBuf, Job)> =
        crates.iter().map(|m| (m.clone(), Job::Test)).collect();
    if world.root.opt(LINT).as_deref() != Some("0") {
        for m in &crates {
            todo.extend(
                lint::passes(m)
                    .into_iter()
                    .map(|p| (m.clone(), Job::Lint(p))),
            );
        }
    }
    let mut out = format!(
        "prewarm: {} crate(s) whose build moved since {since}\n",
        crates.len()
    );
    let until = Instant::now() + knobs.ceiling;
    let tree = world
        .root
        .file_name()
        .unwrap_or_default()
        .to_string_lossy()
        .into_owned();
    while let Some((manifest, job)) = todo.front().cloned() {
        if real_run(world, knobs) {
            let _ = writeln!(out, "prewarm: a run of the checks started in this tree and has the build from here - {}", left(&todo, "left to it", "with them"));
            break;
        }
        if Instant::now() >= until {
            let _ = writeln!(
                out,
                "prewarm: stopped at its ceiling of {} s ({CEILING}) - {}",
                knobs.ceiling.as_secs(),
                left(&todo, "not built", "not run")
            );
            break;
        }
        let (words, _) = job.words(&manifest);
        let who = format!(
            "{tree} (pid {}, pre-warm): cargo {}\n",
            std::process::id(),
            words.join(" ")
        );
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
        let told = job.told(world, &manifest, &kept);
        let end = build(world, &manifest, job, &told, knobs, hold, until);
        todo.pop_front();
        let line = said_of(&shown(world, &manifest), job, &words, &end, began.elapsed());
        out.push_str(&line);
        if matches!(job, Job::Lint(_)) && end.code != 0 {
            // a red pass is the lint's last, as in the lint itself (`lint::linted`)
            todo.retain(|(m, j)| *m != manifest || *j == Job::Test);
        }
    }
    said(out, 0)
}
