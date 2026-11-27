//! `l7r-gate builder-tree` (feature 451 T285): THE BUILDER POOL. A builder's worktree comes from a clone's standing pool and nothing
//! else (the GM, 2026-11-26: "we should make it so that whatever tooling we use to create worktrees automatically enforces and
//! performs the correct behavior without the opportunity for this kind of mistake in the future"), so its build cache is warm: a cold
//! tree's first closing checks took 14-30 minutes on 2026-11-26 against about a minute warm (`docs/process-decisions.md`, "Two code
//! builders at once"). The registry and why membership is not a name: `l7r_shared::builder_pool`.
//!
//! - `take <tasks> [feature]` (`make builder-tree`): the tree the tasks already hold, else the first free tree brought to the
//!   clone's HEAD (detached) and marked held, its path on stdout; with none free, ONE more made (`<clone>-b<N>`) up to the cap
//!   (`L7R_BUILDER_POOL`, `builder_pool::CAP`), said to be cold, its guard binary built before it is handed out (451 T286: a fresh
//!   tree's first closing checks died on the hook wrapper's 45 s build limit under load); at the cap, who holds each.
//! - THE PRE-WARM (451 T316; the GM, 2026-11-26: "would it make sense to begin compiling immediately within a work tree builder?"):
//!   a warm handout starts, detached, the tree's own `scripts/gates/l7r-gate.sh rust prewarm --since <commit>` - the test builds of
//!   the crates the commits since the tree's LAST HANDOUT moved, built while the builder reads (`rustc/prewarm.rs`: it starts a
//!   crate only while a build slot is spare, and ends when a real run starts in the tree, the crate in flight finished first,
//!   451 T336). The commit is the one the tree was last handed out at, kept in the tree's own git directory (`prewarm-base`): a
//!   release brings the tree to HEAD too, so its HEAD at the next handout is no measure of what its cache last built. Its output
//!   is `prewarm.log` there; a pre-warm that cannot start is said and the handout stands; `L7R_PREWARM=0` starts none.
//! - THE SAMPLER (451 T274): every handout asks `l7r-gate measure sampler start` for the clone's memory and load sampler, which
//!   starts one where none is running, so the samples the builder count is certified from never wait on a session remembering
//!   to start them (the three- and four-at-once batches of 2026-11-26 ran unsampled). What it says is said; nothing it does
//!   fails the handout; `L7R_SAMPLER=0` asks for none.
//! - WHAT HOLDS A FREE TREE: an uncommitted path - modified, deleted or untracked - whose content is not the clone's HEAD's. A
//!   builder never commits and its work is carried to the clone, so a released tree still holds the landed edits; those are in
//!   HEAD and are no work to lose, so the tree is brought to HEAD over them. Anything else refuses, each path named;
//!   `DISCARD="<reason>"` brings it over them (`git checkout -f`, `git clean -fd`: ignored files stay), the reason on the pool's log.
//!   A free tree so held is never passed over for a new cold one: the cold tree is the mistake this tool exists to end.
//! - `release <tasks> [feature]` (`make builder-tree-release`) and `landed <feature> <tasks>` (`make land`, after a landing): the
//!   tree freed, it and its build cache left in place, brought to HEAD where nothing holds it; a task holding no tree is a quiet
//!   exit 0, and `landed` exits 0 whatever happens, saying so - a release never fails a landing. A tree whose every holding task
//!   is ticked in its feature's `tasks.md` (or archived in `tasks-done.md`) is free at the next handout whatever landed it.
//! - `list` (`make builder-trees`): each tree, who holds it, since when, its cache's size.
//! - `drop <tree>` with `REASON` (`make builder-tree-drop`): the ONE way a pool tree and its cache are removed.
//! - `adopt <tree> [tasks] [feature]` (`make builder-tree-adopt`): a worktree of this clone made before the pool joins it under its
//!   own name, its cache as warm as it was.
//! - THE LANE'S TREE (feature 461 T13, plan D1): `<clone>-land`, the worktree `land-alone.sh` lands in (`L7R_LANE_TREE` names
//!   another: a path, or a name beside the clone), is adopted by the same command, with no task, under the reserved holder `lane`
//!   (`builder_pool::LANE`): never free, so no handout takes it; holding no feature, so no landing frees it; and outside the cap,
//!   which counts builders' trees. The word is reserved: a take, release, landing or adoption naming it is refused. `lane` (the
//!   runner's call at each batch's start, through [`cli`]) brings it to `origin/main` by `land-alone.sh` step 4's rule - `reset
//!   --hard`, `clean -fd`, `checkout --detach`, after a fetch: the tree is the tool's, nobody's work lives there, so whatever it
//!   holds (a stopped carry's conflict among it) goes. With none adopted it is refused with the adoption to run, never made: a new
//!   tree is cold, the price D1 declined.
//!
//! The pool's log is `<git common dir>/builder-pool.log`, a JSON line an event. Two commands at once take turns on
//! `builder-pool.lock`, held only while the registry is read and written - never over the guard's build.

use std::fmt::Write as _;
use std::io::Write as _;
use std::os::unix::process::CommandExt as _;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};

use l7r_gate_core::Reply;
use l7r_shared::builder_pool::{self, Tree};
use l7r_shared::speckit::marks;
use serde_json::json;

use crate::{git, reply};

const USAGE: &str = "usage: l7r-gate builder-tree take <tasks> <feature> | release <tasks> [feature] | landed <feature> <tasks...> | list | drop <tree> | adopt <tree> [<tasks> <feature>] | lane\n";
const RESERVED: &str = "builder-tree: refused - `lane` is the landing lane's reserved holder (feature 461 D1): no task takes, frees or adopts a tree by it; the lane's tree joins by make builder-tree-adopt TREE=<its path> with no T=\n";
const NO_FEATURE: &str = "builder-tree: refused - a hold names its feature (F=<feature>, or SPECIFY_FEATURE): a tree is freed when that feature's tasks.md shows its tasks ticked, and a hold naming none would never be\n";
const LOG: &str = l7r_shared::builder_queue::LOG;
const LOCK: &str = "builder-pool.lock";

/// What a run reads of the world outside the repository.
pub(crate) struct Env {
    /// The build cache's root (`~/.cache/l7r-cargo-target`).
    pub cache: PathBuf,
    /// The most trees the pool holds.
    pub cap: usize,
    /// The time, as the registry writes it.
    pub now: String,
    /// The tenths of a second a command waits its turn on the registry before taking a dead holder's.
    pub lock_tries: u32,
    /// `DISCARD`: the reason a free tree's uncommitted work may go.
    pub discard: String,
    /// `REASON`: why a tree is dropped.
    pub reason: String,
    /// The seconds a new tree's guard build may take.
    pub guard_secs: String,
    /// A warm handout starts the tree's pre-warm (`L7R_PREWARM` not `0`).
    pub prewarm: bool,
    /// The program and arguments that start the clone's memory sampler where none runs; empty for none (`L7R_SAMPLER=0`).
    pub sampler: Vec<String>,
    /// `L7R_LANE_TREE`: the lane's tree, a path or a name beside the clone; empty for `<clone>-land` (feature 461 D1).
    pub lane_tree: String,
    /// The program and arguments that apply a done commit onto a handed-out tree uncommitted - the gate binary's `land --carry
    /// --no-commit` (461 T05's door), given `""` and the sha, run in the tree; empty where the binary is not known (461 T09, D14).
    pub apply: Vec<String>,
}

impl Env {
    pub(crate) fn live() -> Self {
        let var = |n: &str| std::env::var(n).unwrap_or_default();
        let or = |n: &str, d: &str| {
            Some(var(n))
                .filter(|v| !v.is_empty())
                .unwrap_or(d.to_owned())
        };
        Self {
            cache: PathBuf::from(or(
                "L7R_BUILDER_CACHE",
                &format!("{}/.cache/l7r-cargo-target", var("HOME")),
            )),
            cap: var("L7R_BUILDER_POOL").parse().unwrap_or(builder_pool::CAP),
            now: crate::utc_text(crate::now_secs()),
            lock_tries: 100,
            discard: var("DISCARD"),
            reason: var("REASON"),
            // GUESS: a cold guard build was 19 s with every core busy (449 T004); thirty minutes is past any load seen
            guard_secs: or("L7R_BUILDER_GUARD_SECS", "1800"),
            prewarm: var("L7R_PREWARM") != "0",
            sampler: sampler_words(std::env::current_exe().ok(), &var("L7R_SAMPLER")),
            lane_tree: var("L7R_LANE_TREE"),
            apply: apply_words(std::env::current_exe().ok()),
        }
    }
}

/// The words that ask for the clone's sampler: the gate binary `exe` with `measure sampler start`; none where the knob
/// (`L7R_SAMPLER`) is `0` or the binary is not known. Apart from [`Env::live`] so each case is a test's, whatever the
/// environment a run of the tests has.
fn sampler_words(exe: Option<PathBuf>, knob: &str) -> Vec<String> {
    let Some(exe) = exe.filter(|_| knob != "0") else {
        return Vec::new();
    };
    [&exe.to_string_lossy(), "measure", "sampler", "start"]
        .map(str::to_owned)
        .to_vec()
}

/// The words that apply a done commit onto a tree uncommitted: the gate binary `exe` with `land --carry --no-commit`; none where
/// the binary is not known.
fn apply_words(exe: Option<PathBuf>) -> Vec<String> {
    exe.map(|exe| {
        [&exe.to_string_lossy(), "land", "--carry", "--no-commit"]
            .map(str::to_owned)
            .to_vec()
    })
    .unwrap_or_default()
}

/// The clone a command runs in: its git common directory, its main worktree and that tree's HEAD.
pub(crate) struct Pool {
    pub(crate) common: PathBuf,
    pub(crate) clone: PathBuf,
    pub(crate) head: String,
}

pub(crate) fn text(out: &[u8]) -> String {
    String::from_utf8_lossy(out).trim().to_owned()
}

pub(crate) fn pool(cwd: &Path) -> Option<Pool> {
    let (common, _) = marks::places(cwd)?;
    let clone = marks::main_top(&common);
    let head = text(&git(&clone, &["rev-parse", "HEAD"]).1);
    Some(Pool {
        common,
        clone,
        head,
    })
}

/// The registry's turn, given back when dropped.
struct Lock(PathBuf);

impl Drop for Lock {
    fn drop(&mut self) {
        let _ = std::fs::remove_file(&self.0);
    }
}

/// This command's turn on the registry: the lock file made, or after `tries` tenths of a second taken from a holder that died (a
/// turn lasts a few git calls).
fn lock(common: &Path, tries: u32) -> Lock {
    let path = common.join(LOCK);
    for _ in 0..tries {
        let made = std::fs::OpenOptions::new()
            .write(true)
            .create_new(true)
            .open(&path);
        if made.is_ok() {
            break;
        }
        std::thread::sleep(std::time::Duration::from_millis(100));
    }
    Lock(path)
}

/// A line of the pool's log.
fn note(p: &Pool, env: &Env, event: &str, tree: &Path, detail: &str) {
    log_line(
        p,
        &json!({"utc": env.now, "event": event, "tree": tree, "detail": detail}),
    );
}

/// `line` appended to the pool's log.
pub(crate) fn log_line(p: &Pool, line: &serde_json::Value) {
    log_in(&p.common, line);
}

/// `line` appended to the pool's log under the git common directory `common`.
pub(crate) fn log_in(common: &Path, line: &serde_json::Value) {
    if let Ok(mut f) = std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(common.join(LOG))
    {
        let _ = writeln!(f, "{line}");
    }
}

/// The registry written; what went wrong as a line, empty when nothing did.
fn save(p: &Pool, trees: &[Tree]) -> String {
    let done = builder_pool::write(&p.common, trees);
    done.err()
        .map(|e| format!("builder-tree: {e}\n"))
        .unwrap_or_default()
}

/// A feature as the registry keys it: its number (`451` of `451`, `451-slug` or `specs/451-slug/`), else the word given.
pub(crate) fn feature_key(f: &str) -> String {
    let name = f
        .trim()
        .trim_end_matches('/')
        .rsplit('/')
        .next()
        .unwrap_or("");
    let digits: String = name.chars().take_while(char::is_ascii_digit).collect();
    if digits.is_empty() {
        name.to_owned()
    } else {
        digits
    }
}

/// The tasks of a `T=` value: commas or spaces between them.
pub(crate) fn task_list(t: &str) -> Vec<String> {
    t.split([',', ' '])
        .filter(|w| !w.is_empty())
        .map(str::to_owned)
        .collect()
}

/// `tree` is held by one of `tasks` (of `feature`, where both name one); the lane's tree by none.
pub(crate) fn holds(tree: &Tree, tasks: &[String], feature: &str) -> bool {
    !tree.lane()
        && tree.tasks.iter().any(|t| tasks.contains(t))
        && (feature.is_empty() || tree.feature.is_empty() || tree.feature == feature)
}

/// The uncommitted paths of `tree` whose content is not `target`'s: what bringing it to `target` would lose.
fn held(tree: &Path, target: &str) -> Vec<String> {
    let (_, out) = git(
        tree,
        &["status", "--porcelain", "--no-renames", "-uall", "-z"],
    );
    String::from_utf8_lossy(&out)
        .split('\0')
        .filter_map(|e| e.get(3..))
        .filter(|p| {
            let here = text(&git(tree, &["hash-object", "--", p]).1);
            let there = text(
                &git(
                    tree,
                    &["rev-parse", "-q", "--verify", &format!("{target}:{p}")],
                )
                .1,
            );
            here != there
        })
        .map(str::to_owned)
        .collect()
}

/// `tree` brought to `target`, detached, unless a path holds it (those returned); `discard` brings it over them.
fn bring(tree: &Path, target: &str, discard: bool) -> Vec<String> {
    let lost = held(tree, target);
    if !lost.is_empty() && !discard {
        return lost;
    }
    git(tree, &["checkout", "-q", "-f", "--detach", target]);
    if discard {
        git(tree, &["clean", "-fdq"]);
    }
    Vec::new()
}

/// The first few of `paths`, and how many more.
fn some(paths: &[String]) -> String {
    let more = paths.len().saturating_sub(5);
    let shown = paths.iter().take(5).cloned().collect::<Vec<_>>().join(", ");
    if more == 0 {
        shown
    } else {
        format!("{shown} and {more} more")
    }
}

/// The new tree's guard binary, built by the tree's own hook wrapper with a limit a cold build fits (451 T286). A print-fresh call
/// waits for another call's build within that limit, then builds (451 T449), so it sets no `L7R_GUARD_COLD_SECS`: that seam would
/// add a second wait of its own before the print-fresh one (two 5 s bounds against a lock held 12 s waited 10.0 s, measured
/// 2026-11-27 with the wrapper's stub cargo; 451 T448).
fn build_guard(tree: &Path, secs: &str) -> bool {
    Command::new(tree.join("scripts/hooks/l7r-guard.sh"))
        .env("L7R_GUARD_PRINT_FRESH", "1")
        .env("L7R_GUARD_BUILD_SECS", secs)
        .stdin(Stdio::null())
        .output()
        .is_ok_and(|o| o.status.success())
}

/// Every task holding `tree` has landed in the clone - ticked in its feature's `tasks.md` or archived in `tasks-done.md` - by
/// whatever route (`make land`, `make land-batch`, a tick by hand): a tree so held is free at the next handout with no hand step
/// (the plan review of 2026-11-26: a held tree nobody releases is the next builder's cold tree). A hold naming no feature is
/// read by nothing here and waits for its release.
fn landed(p: &Pool, tree: &Tree) -> bool {
    let prefix = format!("{}-", tree.feature);
    let dirs: Vec<PathBuf> = std::fs::read_dir(p.clone.join("specs"))
        .map(|d| d.filter_map(Result::ok).map(|e| e.path()).collect())
        .unwrap_or_default();
    let text: String = dirs
        .iter()
        .filter(|d| {
            d.file_name()
                .is_some_and(|n| n.to_string_lossy().starts_with(&prefix))
        })
        .flat_map(|d| [d.join("tasks.md"), d.join("tasks-done.md")])
        .map(|f| std::fs::read_to_string(f).unwrap_or_default())
        .collect::<Vec<_>>()
        .join("\n");
    let ticked = |task: &String| {
        text.lines().map(str::trim_start).any(|l| {
            let rest = l
                .strip_prefix("- [x] ")
                .or_else(|| l.strip_prefix("- [X] "));
            rest.and_then(|r| r.split_whitespace().next()) == Some(task.as_str())
        })
    };
    !tree.free() && !tree.feature.is_empty() && tree.tasks.iter().all(ticked)
}

/// Where a tree keeps the commit it was last handed out at, and its pre-warm's log: its own git directory.
pub(crate) fn tree_git_dir(tree: &Path) -> PathBuf {
    PathBuf::from(text(&git(tree, &["rev-parse", "--absolute-git-dir"]).1))
}

const BASE: &str = "prewarm-base";
/// The tree's store of rendered guard messages, under its own git directory (the guard's `suite_tools::messages::store`).
const MESSAGES: &str = "hooks-test/messages";
const PREWARM_LOG: &str = "prewarm.log";
/// What a crate's build reads: the crates and the workspace's manifests, cargo's configuration and the toolchain's pin.
const BUILT_FROM: [&str; 4] = ["rust", ".cargo", "rust-toolchain", "rust-toolchain.toml"];

/// The commit `tree`'s build cache was last warm for - the one it was last handed out at, else `was`, its HEAD before this handout
/// brought it on - and this handout's, `head`, kept for the next.
fn last_handout(tree: &Path, was: &str, head: &str) -> String {
    let at = tree_git_dir(tree).join(BASE);
    let kept = std::fs::read_to_string(&at).unwrap_or_default();
    let _ = std::fs::write(&at, format!("{head}\n"));
    Some(kept.trim().to_owned())
        .filter(|k| !k.is_empty())
        .unwrap_or_else(|| was.to_owned())
}

/// THE PRE-WARM, STARTED (451 T316): where the commits `base..head` moved a file a crate's build reads, the tree's own gate starts
/// `rust prewarm --since <base>` in a process group of its own, its output to the tree's `prewarm.log`, and is not waited for - the
/// handout returns at once. The line said of it; nothing here fails the handout.
fn prewarm(p: &Pool, tree: &Path, base: &str, env: &Env) -> String {
    if !env.prewarm {
        return "builder-tree: no pre-warm (L7R_PREWARM=0)\n".to_owned();
    }
    let mut diff = vec!["diff", "--name-only", base, &p.head, "--"];
    diff.extend(BUILT_FROM);
    if text(&git(tree, &diff).1).is_empty() {
        return format!(
            "builder-tree: nothing to pre-warm - no crate's build moved since the tree's last handout ({})\n",
            base.get(..10).unwrap_or(base)
        );
    }
    let log = tree_git_dir(tree).join(PREWARM_LOG);
    let started = std::fs::File::create(&log).and_then(|out| {
        Command::new(tree.join("scripts/gates/l7r-gate.sh"))
            .args(["rust", "prewarm", "--since", base])
            .current_dir(tree)
            // the handout's own tree, target directory and make are not the pre-warm's: it builds in the tree it warms, as that
            // tree's checks will, and outlives the make that started it
            .env_remove("L7R_GATE_TREE")
            .env_remove("CARGO_TARGET_DIR")
            .env_remove("MAKEFLAGS")
            .env_remove("MFLAGS")
            .env_remove("MAKELEVEL")
            .stdin(Stdio::null())
            .stdout(out.try_clone()?)
            .stderr(out)
            .process_group(0)
            .spawn()
    });
    match started {
        Ok(child) => {
            note(p, env, "prewarm", tree, &format!("since {base}, pid {}", child.id()));
            format!(
                "builder-tree: pre-warming it in the background - the test builds of the crates moved since its last handout ({}); log {} (L7R_PREWARM=0 for none)\n",
                base.get(..10).unwrap_or(base),
                log.display()
            )
        }
        Err(e) => format!("builder-tree: its pre-warm did not start ({e}) - the handout stands, and the builder's first run compiles what moved\n"),
    }
}

/// THE SAMPLER, ASKED FOR (451 T274): the clone's memory and load sampler started where none is running, by the gate's own
/// `measure sampler start` run in the clone. What it said, or that it could not be asked; never a failed handout.
fn sampler(p: &Pool, env: &Env) -> String {
    let Some((program, args)) = env.sampler.split_first() else {
        return String::new();
    };
    let asked = Command::new(program)
        .args(args)
        .current_dir(&p.clone)
        .stdin(Stdio::null())
        .output();
    match asked {
        Ok(said) => format!("{}\n", text(&said.stderr)),
        Err(e) => format!("builder-tree: the memory sampler was not asked for ({program}: {e}) - the handout stands; make sampler-start starts it\n"),
    }
}

pub(crate) fn refused(why: String) -> Reply {
    reply(String::new(), why, 2)
}

/// The builders' trees of `trees`, the lane's not counted: what the cap holds to.
fn builders(trees: &[Tree]) -> usize {
    trees.iter().filter(|t| !t.lane()).count()
}

/// `tasks` names the lane's reserved holder.
fn reserved(tasks: &[String]) -> bool {
    tasks.iter().any(|t| t == builder_pool::LANE)
}

/// Where the lane's tree is: `L7R_LANE_TREE` - a path, or a name beside the clone - else `<clone>-land`.
fn lane_path(p: &Pool, env: &Env) -> PathBuf {
    let clones = p.clone.parent().unwrap_or(&p.clone);
    if env.lane_tree.is_empty() {
        let name = p.clone.file_name().unwrap_or_default().to_string_lossy();
        return clones.join(format!("{name}-land"));
    }
    clones.join(&env.lane_tree)
}

fn take(p: &Pool, tasks: &[String], feature: &str, env: &Env) -> Reply {
    if reserved(tasks) {
        return refused(RESERVED.to_owned());
    }
    if !env.discard.is_empty() && !l7r_shared::escape::enough(&env.discard) {
        return refused("builder-tree: DISCARD needs a reason of two words or more: it throws away a free tree's uncommitted work\n".to_owned());
    }
    let turn = lock(&p.common, env.lock_tries);
    let mut trees = builder_pool::read_all(&p.common);
    if let Some(t) = trees.iter().find(|t| holds(t, tasks, feature)) {
        return reply(
            format!("{}\n", t.tree.display()),
            format!(
                "builder-tree: {} already holds it (since {})\n",
                t.holder(),
                t.since
            ),
            0,
        );
    }
    // the task's own done commit not yet carried: the handout builds on it (461 T09, D14, `builder_done::build_on`), or with no
    // apply program known its next builder would start without it, and waits (451 T398)
    if let Some(why) = crate::builder_done::handout_waits(p, tasks, feature, env) {
        return refused(why);
    }
    let mut notes = String::new();
    for t in &mut trees {
        if landed(p, t) {
            let _ = writeln!(
                notes,
                "builder-tree: {} was held by {}, which has landed: free",
                t.tree.display(),
                t.holder()
            );
            note(p, env, "landed", &t.tree, &t.holder());
            t.feature.clear();
            t.tasks.clear();
            t.since.clone_from(&env.now);
        }
    }
    let mut blocked = false;
    for i in 0..trees.len() {
        let tree = trees[i].tree.clone();
        if !trees[i].free() {
            continue;
        }
        if !tree.is_dir() {
            let _ = writeln!(notes, "builder-tree: {} is in the pool and gone from disk - make builder-tree-drop TREE={} REASON=\"<why>\"", tree.display(), tree.display());
            continue;
        }
        let was = text(&git(&tree, &["rev-parse", "HEAD"]).1);
        let lost = bring(&tree, &p.head, !env.discard.is_empty());
        if !lost.is_empty() {
            blocked = true;
            let _ = writeln!(notes, "builder-tree: {} is free and held by uncommitted work that is not in the clone's HEAD: {}", tree.display(), some(&lost));
            continue;
        }
        if !env.discard.is_empty() {
            note(p, env, "discard", &tree, &env.discard);
        }
        // the tree's store of rendered guard messages is its last holder's (451 T486): left, `make guard-messages` named wordings this
        // HEAD does not render (T485's two keys, 2026-11-27); emptied, the next `make hooks-test` here fills it from this HEAD's suites
        let _ = std::fs::remove_dir_all(tree_git_dir(&tree).join(MESSAGES));
        feature.clone_into(&mut trees[i].feature);
        trees[i].tasks = tasks.to_vec();
        trees[i].since.clone_from(&env.now);
        note(p, env, "take", &tree, &trees[i].holder());
        let _ = writeln!(
            notes,
            "builder-tree: {} is held by {}, at the clone's HEAD ({}), its build cache kept: warm",
            tree.display(),
            trees[i].holder(),
            p.head.get(..10).unwrap_or(&p.head)
        );
        notes.push_str(&save(p, &trees));
        let holder = trees[i].holder();
        drop(turn);
        // outside the registry's turn (an apply can take longer than a waiting command's), before the pre-warm reads the tree
        let built = crate::builder_done::build_on(p, &tree, tasks, feature, &holder, env);
        if let Err(why) = built.map(|said| notes.push_str(&said)) {
            let _ = release(p, tasks, feature, env);
            return refused(format!("{notes}{why}"));
        }
        let base = last_handout(&tree, &was, &p.head);
        notes.push_str(&prewarm(p, &tree, &base, env));
        return reply(format!("{}\n", tree.display()), notes, 0);
    }
    if blocked {
        notes.push_str("builder-tree: refused - no tree handed out. Carry that work to the clone, or take the tree over it: make builder-tree T=<task> DISCARD=\"<why it may go>\" (a new cold tree is not made while a warm one waits)\n");
        return refused(notes);
    }
    if builders(&trees) >= env.cap {
        let _ = writeln!(notes, "builder-tree: refused - the pool is at its cap of {} (L7R_BUILDER_POOL) and none is free:", env.cap);
        for t in trees.iter().filter(|t| !t.lane()) {
            let _ = writeln!(
                notes,
                "  {}  held by {} since {}",
                t.tree.display(),
                t.holder(),
                t.since
            );
        }
        notes.push_str("builder-tree: free one with make builder-tree-release T=<task> (make land frees a landed task's), or raise the cap\n");
        return refused(notes);
    }
    make_cold(p, trees, tasks, feature, env, notes, turn)
}

/// The handout with no tree free and the pool under its cap: one more tree, made cold and said to be.
fn make_cold(
    p: &Pool,
    mut trees: Vec<Tree>,
    tasks: &[String],
    feature: &str,
    env: &Env,
    mut notes: String,
    turn: Lock,
) -> Reply {
    let name = p.clone.file_name().unwrap_or_default().to_string_lossy();
    let clones = p.clone.parent().unwrap_or(&p.clone);
    let taken = |c: &Path| c.exists() || trees.iter().any(|t| t.tree == c);
    let tree = (1..10_000)
        .map(|n| clones.join(format!("{name}-b{n}")))
        .find(|c| !taken(c))
        .unwrap_or_default();
    let tree_text = tree.to_string_lossy().into_owned();
    let (code, _) = git(
        &p.clone,
        &["worktree", "add", "-q", "--detach", &tree_text, &p.head],
    );
    if code != Some(0) {
        return refused(format!(
            "{notes}builder-tree: refused - git worktree add could not make {tree_text}\n"
        ));
    }
    trees.push(Tree {
        tree: tree.clone(),
        feature: feature.to_owned(),
        tasks: tasks.to_vec(),
        since: env.now.clone(),
    });
    notes.push_str(&save(p, &trees));
    note(p, env, "make", &tree, &trees[trees.len() - 1].holder());
    drop(turn);
    // a new tree's cache is warm for nothing: its first handout is what the next one's pre-warm is measured from
    last_handout(&tree, &p.head, &p.head);
    let _ = writeln!(notes, "builder-tree: {tree_text} is NEW and held by {}: COLD - its build cache is empty, so its first closing checks compile everything (14-30 minutes measured 2026-11-26); no pool tree was free ({} of {} now)", trees[trees.len() - 1].holder(), builders(&trees), env.cap);
    if build_guard(&tree, &env.guard_secs) {
        notes.push_str("builder-tree: its guard binary is built\n");
    } else {
        let _ = writeln!(notes, "builder-tree: its guard binary did NOT build (see {}/build.log): the disk floor of its first `make closing-checks`, `make done` or `make land` builds it, waiting up to L7R_GUARD_COLD_SECS (600 s) for another call's build", builder_pool::cache(&env.cache, &tree).display());
    }
    reply(format!("{tree_text}\n"), notes, 0)
}

pub(crate) fn release(p: &Pool, tasks: &[String], feature: &str, env: &Env) -> Reply {
    if reserved(tasks) {
        return refused(RESERVED.to_owned());
    }
    let _turn = lock(&p.common, env.lock_tries);
    let mut trees = builder_pool::read_all(&p.common);
    let mut said = String::new();
    for t in trees.iter_mut().filter(|t| holds(t, tasks, feature)) {
        let was = t.holder();
        t.feature.clear();
        t.tasks.clear();
        t.since.clone_from(&env.now);
        let gone = !t.tree.is_dir();
        let lost = if gone {
            Vec::new()
        } else {
            bring(&t.tree, &p.head, false)
        };
        note(p, env, "release", &t.tree, &was);
        let state = if gone {
            "GONE from disk (make builder-tree-drop takes it out of the pool)".to_owned()
        } else if lost.is_empty() {
            "at the clone's HEAD".to_owned()
        } else {
            format!(
                "left as it is, holding uncommitted work that is not in the clone's HEAD ({})",
                some(&lost)
            )
        };
        let _ = writeln!(said, "builder-tree: {} is free ({was} released), the tree and its build cache left in place, {state}", t.tree.display());
    }
    if said.is_empty() {
        return reply(
            format!("builder-tree: {} holds no pool tree\n", tasks.join(",")),
            String::new(),
            0,
        );
    }
    let failed = save(p, &trees);
    let code = i32::from(!failed.is_empty());
    reply(said, failed, code)
}

/// The size of a tree's build cache as `du -sh` says it, `none` where there is none.
fn cache_size(cache: &Path) -> String {
    if !cache.is_dir() {
        return "none".to_owned();
    }
    let out = Command::new("du").arg("-sh").arg(cache).output();
    size_word(&out.map(|o| text(&o.stdout)).unwrap_or_default())
}

/// The first word of `du`'s line, `?` where it printed none.
fn size_word(line: &str) -> String {
    line.split_whitespace().next().unwrap_or("?").to_owned()
}

fn list(p: &Pool, env: &Env) -> Reply {
    let trees = builder_pool::read_all(&p.common);
    let lane = if trees.iter().any(Tree::lane) {
        ", and the lane's tree"
    } else {
        ""
    };
    let mut out = format!(
        "builder-trees: {} of {} (the cap, L7R_BUILDER_POOL){lane}, of {}\n",
        builders(&trees),
        env.cap,
        p.clone.display()
    );
    for t in &trees {
        let gone = if t.tree.is_dir() {
            ""
        } else {
            "  GONE from disk"
        };
        let _ = writeln!(
            out,
            "  {}  {}  since {}  cache {}{gone}",
            t.tree.display(),
            t.holder(),
            t.since,
            cache_size(&builder_pool::cache(&env.cache, &t.tree))
        );
    }
    out.push_str(&crate::builder_done::listed(p));
    reply(out, String::new(), 0)
}

/// The registered tree `arg` names.
fn find(trees: &[Tree], arg: &str) -> Option<usize> {
    trees
        .iter()
        .position(|t| marks::same_tree(&t.tree, Path::new(arg)))
}

fn drop_tree(p: &Pool, arg: &str, env: &Env) -> Reply {
    if !l7r_shared::escape::enough(&env.reason) {
        return refused("builder-tree-drop: REASON needs two words or more: the tree's build cache goes with it, and the next tree made is cold\n".to_owned());
    }
    let _turn = lock(&p.common, env.lock_tries);
    let mut trees = builder_pool::read_all(&p.common);
    let Some(i) = find(&trees, arg) else {
        return refused(format!(
            "builder-tree-drop: {arg} is not a pool tree (make builder-trees lists them)\n"
        ));
    };
    if !trees[i].free() {
        return refused(format!(
            "builder-tree-drop: {arg} is held by {} - make builder-tree-release T={} first\n",
            trees[i].holder(),
            trees[i].tasks.join(",")
        ));
    }
    let tree = trees.remove(i).tree;
    let lost = if tree.is_dir() {
        held(&tree, &p.head)
    } else {
        Vec::new()
    };
    let tree_text = tree.to_string_lossy().into_owned();
    git(&p.clone, &["worktree", "remove", "--force", &tree_text]);
    git(&p.clone, &["worktree", "prune"]);
    let cache = builder_pool::cache(&env.cache, &tree);
    let _ = std::fs::remove_dir_all(&cache);
    note(p, env, "drop", &tree, &env.reason);
    let mut said = format!(
        "builder-tree-drop: {tree_text} and its build cache {} are removed ({})\n",
        cache.display(),
        env.reason
    );
    if !lost.is_empty() {
        let _ = writeln!(
            said,
            "builder-tree-drop: uncommitted work went with it: {}",
            some(&lost)
        );
    }
    let failed = save(p, &trees);
    let code = i32::from(!failed.is_empty());
    reply(said, failed, code)
}

fn adopt(p: &Pool, arg: &str, tasks: &[String], feature: &str, env: &Env) -> Reply {
    if reserved(tasks) {
        return refused(RESERVED.to_owned());
    }
    let _turn = lock(&p.common, env.lock_tries);
    let mut trees = builder_pool::read_all(&p.common);
    let lane = marks::same_tree(Path::new(arg), &lane_path(p, env));
    let listed = text(&git(&p.clone, &["worktree", "list", "--porcelain"]).1);
    let known = listed
        .lines()
        .filter_map(|l| l.strip_prefix("worktree "))
        // the landings' and the review's trees are their tools' (`land-alone.sh`, `land-tooling.sh`, `review-tree.sh`), but the
        // lane's, which joins as its own (feature 461 D1)
        .filter(|w| {
            lane || !["-land", "-tooling", "-review"]
                .iter()
                .any(|s| w.ends_with(s))
        })
        .find(|w| {
            marks::same_tree(Path::new(w), Path::new(arg))
                && !marks::same_tree(Path::new(w), &p.clone)
        });
    let Some(tree) = known.map(PathBuf::from) else {
        return refused(format!("builder-tree-adopt: {arg} is not a builder's worktree of {} (a worktree beside its main tree, not the landing's or the review's)\n", p.clone.display()));
    };
    if find(&trees, arg).is_some() || (!lane && builders(&trees) >= env.cap) {
        return refused(format!("builder-tree-adopt: {arg} is already in the pool, or the pool is at its cap of {} (L7R_BUILDER_POOL)\n", env.cap));
    }
    if lane && !tasks.is_empty() {
        return refused(format!("builder-tree-adopt: {arg} is the lane's tree, held by lane alone: adopt it with no T= (L7R_LANE_TREE names another)\n"));
    }
    if let Some(t) = trees.iter().find(|t| lane && t.lane()) {
        return refused(format!(
            "builder-tree-adopt: the pool holds the lane's tree already ({}): one lane, one tree\n",
            t.tree.display()
        ));
    }
    let (feature, tasks) = if lane {
        (String::new(), vec![builder_pool::LANE.to_owned()])
    } else {
        (feature.to_owned(), tasks.to_vec())
    };
    trees.push(Tree {
        tree: tree.clone(),
        feature,
        tasks,
        since: env.now.clone(),
    });
    let holder = trees[trees.len() - 1].holder();
    note(p, env, "adopt", &tree, &holder);
    let failed = save(p, &trees);
    let code = i32::from(!failed.is_empty());
    let how = if lane {
        "as the lane's tree, held by lane: no handout takes it and the cap (L7R_BUILDER_POOL) does not count it".to_owned()
    } else {
        format!("under its own name ({holder})")
    };
    reply(
        format!(
            "builder-tree-adopt: {} joins the pool {how}, its build cache as it is\n",
            tree.display()
        ),
        failed,
        code,
    )
}

/// THE LANE'S TREE AT A BATCH'S START (feature 461 T13, D1): the registry's lane tree brought to `origin/main`, fetched first, by
/// `land-alone.sh` step 4's rule (`reset --hard`, `clean -fdq`, `checkout --detach`), its path on stdout.
fn lane_start(p: &Pool, env: &Env) -> Reply {
    let trees = builder_pool::read_all(&p.common);
    let Some(t) = trees.iter().find(|t| t.lane()) else {
        return refused(format!("builder-tree lane: no lane's tree is in the pool - make builder-tree-adopt TREE={} (land-alone's worktree, its cache warm; a new tree would start cold, plan D1)\n", lane_path(p, env).display()));
    };
    let tree = &t.tree;
    if !tree.is_dir() {
        return refused(format!("builder-tree lane: the lane's tree {} is gone from disk - make builder-tree-drop TREE={} REASON=\"<why>\", then make builder-tree-adopt TREE=<the tree the lane runs in>\n", tree.display(), tree.display()));
    }
    let fetched = git(tree, &["fetch", "-q", "origin", "main"]).0 == Some(0);
    let target = text(
        &git(
            tree,
            &["rev-parse", "-q", "--verify", "refs/remotes/origin/main"],
        )
        .1,
    );
    let moved = fetched
        && !target.is_empty()
        && [
            &["reset", "-q", "--hard"][..],
            &["clean", "-fdq"],
            &["checkout", "-q", "--detach", &target],
        ]
        .iter()
        .all(|a| git(tree, a).0 == Some(0));
    if !moved {
        return refused(format!("builder-tree lane: the lane's tree {} could not be brought to origin/main (the fetch, the reset, the clean or the checkout failed: git -C {} status says where it stands)\n", tree.display(), tree.display()));
    }
    note(p, env, "lane", tree, &target);
    reply(
        format!("{}\n", tree.display()),
        format!("builder-tree lane: {} is at origin/main ({}), whatever it held gone - it is the lane's, nobody's work lives there\n", tree.display(), target.get(..10).unwrap_or(&target)),
        0,
    )
}

/// `l7r-gate builder-tree <args>` from `cwd`.
#[must_use]
pub fn cli(args: &[String], cwd: &Path) -> Reply {
    run(args, cwd, &Env::live())
}

pub(crate) fn run(args: &[String], cwd: &Path, env: &Env) -> Reply {
    let arg = |i: usize| args.get(i).map_or("", String::as_str);
    let landed = arg(0) == "landed";
    let Some(p) = pool(cwd) else {
        let why = "builder-tree: not in a git repository\n";
        return if landed {
            reply(
                String::new(),
                format!("builder-tree: the release failed - the landing stands: {why}"),
                0,
            )
        } else {
            refused(why.to_owned())
        };
    };
    // a hold that named no feature would be read by no handout's freeing step and wait on a hand release (the plan review, 2026-11-26)
    let unnamed = |tasks: &str, feature: &str| !tasks.is_empty() && feature_key(feature).is_empty();
    if (arg(0) == "take" && unnamed(arg(1), arg(2)))
        || (arg(0) == "adopt" && unnamed(arg(2), arg(3)))
    {
        return refused(NO_FEATURE.to_owned());
    }
    match (arg(0), arg(1)) {
        ("take", t) if !t.is_empty() => {
            let (tasks, feature) = (task_list(t), feature_key(arg(2)));
            let mut r = take(&p, &tasks, &feature, env);
            if r.code == 0 {
                // the tasks in flight its queue entry overlaps, said and never refused (451 T408)
                r.stderr
                    .push_str(&crate::builder_queue::overlapping(&p, &tasks, &feature));
                r.stderr.push_str(&sampler(&p, env));
            }
            r
        }
        ("release", t) if !t.is_empty() => release(&p, &task_list(t), &feature_key(arg(2)), env),
        ("landed", f) if args.len() > 2 => {
            let mut r = release(&p, &task_list(&args[2..].join(" ")), &feature_key(f), env);
            if r.code != 0 {
                r.stderr = format!(
                    "builder-tree: the release failed - the landing stands: {}",
                    r.stderr
                );
                r.code = 0;
            }
            r
        }
        ("list", _) => list(&p, env),
        ("drop", t) if !t.is_empty() => drop_tree(&p, t, env),
        ("adopt", t) if !t.is_empty() => {
            adopt(&p, t, &task_list(arg(2)), &feature_key(arg(3)), env)
        }
        ("lane", _) => lane_start(&p, env),
        _ => refused(USAGE.to_owned()),
    }
}

#[cfg(test)]
pub(crate) mod tests;
