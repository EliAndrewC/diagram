//! `l7r-gate builder-done` (feature 451 T394; the GM, 2026-11-27, on `make task-time`'s 123.3 blocking minutes for the second tier:
//! "if our tooling indicates that we have spent over 2 hours blocking on the second tier then that's a HUGE problem, either with
//! our measurements or with our process, and we should get to the botom of that ASAP"): A POOL TREE GOES TO ITS NEXT TASK THE
//! MOMENT ITS BUILDER'S WORK IS COMMITTED. Measured 2026-11-27 (`dev/measurements/2026-11-27/tree-idle/results.md`): the three warm
//! trees stood idle 336 of 1,440 tree-minutes (23%) of an eight-hour window with the queue never short, because the coordinating
//! session worked a builder's end in the order commit, carry, resolve, check, land - and only then briefed the next builder.
//! Nothing requires that order: a linked worktree's commit is in the clone's object store, and `make carry` takes `COMMIT=`.
//!
//! `make builder-done T=<task(s)> F=<n> MSG="<subject>" [GUARD="<guard-edit reason>"]`, in the pool tree the registry says the
//! tasks hold (never passed):
//!
//! 1. REFUSES WITH NOTHING DONE where the tree holds an operation git left unfinished (a cherry-pick, merge, revert, rebase), an
//!    unmerged path, a conflict's markers in a changed file (`conflict_marker_hooks::has_conflict`, its exemption kept), nothing
//!    to commit, a changed guard file with no `GUARD=` (the refusal prints the exact re-run), or a done commit of one of the tasks
//!    that is not yet carried (the ref is never written over while its commit waits; `make builder-tree` refuses that task's next
//!    handout first, [`handout_waits`], 451 T398, so this is the backstop for a tree held some other way);
//! 2. removes the stray `default_*.profraw` files an instrumented binary dropped;
//! 3. stages everything not ignored and commits it through `git commit -F <file>`: `MSG` the subject, a `GUARD_EDIT_OK:` line when
//!    `GUARD=` is given, the co-author trailer;
//! 4. writes the commit under `refs/l7r/done/<feature>-<task>`, one ref a task, so it outlives the tree's next handout (the handout
//!    detaches the tree at the clone's HEAD, and an unreferenced commit is git's to prune), and appends a `done` line to the pool's
//!    log (the tree, the holder, the commit, the time);
//! 5. releases the tree, as `make builder-tree-release` does ([`builder_tree::release`]);
//! 6. prints, last, the two commands the session runs next, IN THIS ORDER: the next dispatch, then the carry. It never carries,
//!    lands or pushes.
//!
//! THE GUARD-FILE RULE IS ASKED HERE, IN PROCESS: the guards are hooks on a tool call, and a `git commit` this command runs is none,
//! so nothing else would hold the commit to its `GUARD_EDIT_OK:` line. [`guard_file`] is a COPY of the guard's list
//! (`rust/guard/src/guards/guard_file_hooks.rs`, `named`), which lives in the guard's binary crate where no gate crate may read it
//! (`check guard-deps`); moving it to `l7r_shared` is an edit of the guard's own sources and its suites, left to a task of its own.
//!
//! THE NEXT DISPATCH IS THE QUEUE'S (451 T313, T395): step 1 is `specs/<feature>/queue.txt`'s next READY entry (performance work first, FR-013) that overlaps no task
//! holding a tree, with its exact `make builder-brief` command ([`crate::builder_queue::dispatch`]); with none to hand out, or no
//! queue to read, it says why and the command still ends 0 - the tree is committed. A placeholder stood here while the queue was
//! prose (`queue.md`: numbered items naming several tasks, "after T316", "LANDED"), which no code could read without guessing.
//!
//! WHAT IS CARRIED ([`uncarried`], which `make builder-trees` lists after the trees): a done commit waits while its ref stands
//! and the clone's HEAD holds no commit of its AUTHOR'S TIME and SUBJECT. `make carry` in the clone (one in a linked worktree keeps it,
//! 451 T404) deletes the ref at its verified end -
//! carried, or an empty pick skipped because HEAD holds the changes already (451 T397) - so the ref alone would do for a commit
//! carried by that command; the second test covers a commit that reached HEAD another way (a carry stopped on a conflict and
//! finished by hand): a carry is a cherry-pick, so the carried commit has another id and `git branch --contains` never names it,
//! while a cherry-pick keeps the author's time and the subject. A carry that kept both sides of a conflict is still found, where a
//! patch-id comparison (`git cherry`) would miss it.

use std::collections::{BTreeMap, BTreeSet};
use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::process::Command;

use l7r_gate_core::Reply;
use l7r_shared::builder_pool;
use l7r_shared::guards::conflict_marker_hooks::has_conflict;
use serde_json::{json, Value};

use crate::builder_tree::{self, feature_key, refused, task_list, text, Env, Pool};
use crate::reply;

const USAGE: &str = "usage: make builder-done T=<task(s)> F=<n> MSG=\"<the commit's subject>\" [GUARD=\"<guard-edit reason>\"]\n";
pub(crate) const TRAILER: &str = "Co-Authored-By: Claude Fable 5.2 <noreply@anthropic.com>";
/// Where a done commit is kept: `refs/l7r/done/<feature>-<task>`. The carry deletes the ref at its verified end (the land crate's
/// `carry.rs`, `spent`).
pub const REFS: &str = l7r_shared::builder_queue::DONE_REFS;
/// The file of the tree's own git directory the commit's message is written to.
const MESSAGE: &str = "builder-done-message";
/// What git leaves in a tree's git directory while an operation stands unfinished, and its name.
const OPS: [(&str, &str); 6] = [
    ("CHERRY_PICK_HEAD", "cherry-pick"),
    ("MERGE_HEAD", "merge"),
    ("REVERT_HEAD", "revert"),
    ("sequencer/todo", "pick of several commits"),
    ("rebase-merge", "rebase"),
    ("rebase-apply", "rebase or mailbox apply"),
];

/// `git -C dir args`: whether it succeeded, what it printed, and what it said on stderr.
fn git(dir: &Path, args: &[&str]) -> (bool, String, String) {
    let done = Command::new("git").arg("-C").arg(dir).args(args).output();
    done.map_or((false, String::new(), String::new()), |o| {
        (
            o.status.success(),
            String::from_utf8_lossy(&o.stdout).into_owned(),
            String::from_utf8_lossy(&o.stderr).into_owned(),
        )
    })
}

/// A guard file by its path in the tree: the guard's own list (`guard_file_hooks::named`), copied (the module's doc says why).
pub(crate) fn guard_file(rel: &str) -> bool {
    let file = format!("/{rel}");
    let hook_script = file.contains("/scripts/") && file.ends_with("-hooks.sh");
    let suite = file.contains("/tests/hooks/test-") && file.ends_with("-hooks.sh");
    let named = file.ends_with("/Makefile")
        || hook_script
        || [
            "/.claude/settings.json",
            "/tests/rolls.py",
            "/dev/switches.json",
            "/dev/work-budget.json",
        ]
        .iter()
        .any(|n| file.ends_with(n));
    let guard_crate = ["/rust/guard/", "/rust/guard/shared/"]
        .iter()
        .any(|c| file == format!("{c}Cargo.toml") || file.starts_with(&format!("{c}src/")));
    let source =
        guard_crate || file == "/scripts/hooks/l7r-guard.sh" || file == "/scripts/hooks/l7r-hook";
    let test = file.ends_with("/tests.rs") || file.contains("/tests/");
    (named && !suite) || (source && !test)
}

/// `s` as one word of a shell command.
pub(crate) fn quoted(s: &str) -> String {
    format!("'{}'", s.replace('\'', "'\\''"))
}

/// A done commit kept under a ref: the ref's name after [`REFS`], the commit, and what a carry keeps of it - its author's time and
/// its subject.
struct Done {
    name: String,
    sha: String,
    key: String,
}

impl Done {
    fn subject(&self) -> &str {
        self.key.split_once('\t').map_or("", |(_, s)| s)
    }
}

/// Every done commit the clone keeps a ref for, by the ref's name.
fn dones(clone: &Path) -> Vec<Done> {
    let format = "--format=%(refname:lstrip=3)%09%(objectname)%09%(authordate:unix)%09%(subject)";
    let (_, out, _) = git(clone, &["for-each-ref", format, REFS]);
    out.lines()
        .filter_map(|l| {
            let mut parts = l.splitn(3, '\t');
            Some(Done {
                name: parts.next()?.to_owned(),
                sha: parts.next()?.to_owned(),
                key: parts.next()?.to_owned(),
            })
        })
        .collect()
}

/// Those of `dones` the clone's HEAD does not hold (the module's doc: by the author's time and the subject, which a cherry-pick
/// keeps): one read of the clone's history since the oldest of them.
fn uncarried<'a>(clone: &Path, dones: &'a [Done]) -> Vec<&'a Done> {
    let time = |d: &Done| d.key.split('\t').next().and_then(|t| t.parse::<u64>().ok());
    let Some(oldest) = dones.iter().filter_map(time).min() else {
        return Vec::new();
    };
    let since = format!("--since=@{}", oldest.saturating_sub(1));
    let (_, held, _) = git(clone, &["log", "--format=%at%x09%s", &since, "HEAD"]);
    let held: BTreeSet<&str> = held.lines().collect();
    dones
        .iter()
        .filter(|d| !held.contains(d.key.as_str()))
        .collect()
}

/// The tree the pool's log says a done commit was made in; the clone where it names none (every worktree shares its objects, so
/// the carry finds the commit from any of them).
fn tree_of(p: &Pool, sha: &str) -> PathBuf {
    let log = std::fs::read_to_string(p.common.join("builder-pool.log")).unwrap_or_default();
    log.lines()
        .filter_map(|l| serde_json::from_str::<Value>(l).ok())
        .filter(|e| e["event"] == "done" && e["commit"] == sha)
        .filter_map(|e| e["tree"].as_str().map(PathBuf::from))
        .next_back()
        .unwrap_or_else(|| p.clone.clone())
}

/// THE QUEUE ENTRY THE TREE'S BUILDER SERVED (451 T313's review, round 1): the last `brief` line naming an entry that the pool's log
/// holds for `tree` and `holder` since the tree was last taken, made or adopted. A successor briefed on the tree it already held
/// writes a `brief` line and no take, so it inherits the entry its tree was briefed for; a tree briefed for none names none, and
/// the queue counts its done line as before.
fn entry_of(p: &Pool, tree: &Path, holder: &str) -> Option<u64> {
    let log = std::fs::read_to_string(p.common.join("builder-pool.log")).unwrap_or_default();
    let ours: Vec<Value> = log
        .lines()
        .filter_map(|l| serde_json::from_str::<Value>(l).ok())
        .filter(|e| e["tree"].as_str() == Some(&*tree.to_string_lossy()))
        .collect();
    let held = |e: &&Value| matches!(e["event"].as_str(), Some("take" | "make" | "adopt"));
    let from = ours.iter().rposition(|e| held(&e)).unwrap_or(0);
    ours[from..]
        .iter()
        .filter(|e| e["event"] == "brief" && e["detail"] == holder)
        .filter_map(|e| e["entry"].as_u64())
        .next_back()
}

fn carry_command(p: &Pool, sha: &str) -> String {
    format!("make carry FROM={} COMMIT={sha}", tree_of(p, sha).display())
}

/// What `make builder-trees` says after the trees: each commit done and not yet carried, the tasks it is kept for and its carry.
pub(crate) fn listed(p: &Pool) -> String {
    let dones = dones(&p.clone);
    let mut open: BTreeMap<&str, Vec<&Done>> = BTreeMap::new();
    for d in uncarried(&p.clone, &dones) {
        open.entry(d.sha.as_str()).or_default().push(d);
    }
    if open.is_empty() {
        return "builder-trees: no done commit waits on its carry\n".to_owned();
    }
    let mut out = format!(
        "builder-trees: commits done and not yet carried into {} (make builder-done kept each under {REFS}): {}\n",
        p.clone.display(),
        open.len()
    );
    for (sha, kept) in open {
        let names: Vec<&str> = kept.iter().map(|d| d.name.as_str()).collect();
        let _ = writeln!(
            out,
            "  {}  {}  {}\n    {}",
            sha.get(..10).unwrap_or(sha),
            names.join(", "),
            kept[0].subject(),
            carry_command(p, sha)
        );
    }
    out
}

/// What a caller asks: the tasks, the feature's key, the commit's subject and the guard-edit reason.
struct Ask<'a> {
    tasks: &'a [String],
    feature: &'a str,
    subject: &'a str,
    guard: &'a str,
}

impl Ask<'_> {
    /// The command as it was run, `GUARD=` left for the caller to add.
    fn command(&self) -> String {
        format!(
            "make builder-done T={} F={} MSG={}",
            self.tasks.join(","),
            self.feature,
            quoted(self.subject)
        )
    }

    fn ref_of(&self, task: &str) -> String {
        format!("{}-{task}", self.feature)
    }
}

/// The paths `git add -A` would stage in `tree`, each with its two status letters.
fn changed(tree: &Path) -> Vec<(String, String)> {
    let (_, out, _) = git(
        tree,
        &["status", "--porcelain", "--no-renames", "-uall", "-z"],
    );
    out.split('\0')
        .filter_map(|e| Some((e.get(..2)?.to_owned(), e.get(3..)?.to_owned())))
        .collect()
}

/// Why `tree` is not committed, nothing done; none where it is ready.
fn unready(p: &Pool, tree: &Path, a: &Ask, dones: &[Done]) -> Option<String> {
    let at = tree.display();
    let git_dir = builder_tree::tree_git_dir(tree);
    if let Some((marker, name)) = OPS.iter().find(|(m, _)| git_dir.join(m).exists()) {
        return Some(format!("builder-done: refused - nothing done: {at} holds an unfinished {name} ({marker}); finish or abort it there, then run this again\n"));
    }
    let paths = changed(tree);
    let unmerged = |xy: &str| xy.contains('U') || xy == "AA" || xy == "DD";
    if let Some((_, path)) = paths.iter().find(|(xy, _)| unmerged(xy)) {
        return Some(format!("builder-done: refused - nothing done: in {at} an unmerged path stands: {path}; resolve it and git add it, then run this again\n"));
    }
    if paths.is_empty() {
        return Some(format!("builder-done: refused - nothing to commit in {at}: the builder's work is not there (committed already, or in another tree); make builder-tree-release T={} F={} frees the tree\n", a.tasks.join(","), a.feature));
    }
    let marked =
        |path: &String| std::fs::read_to_string(tree.join(path)).is_ok_and(|t| has_conflict(&t));
    if let Some((_, path)) = paths.iter().find(|(_, path)| marked(path)) {
        return Some(format!("builder-done: refused - nothing done: a conflict's markers stand in {path} of {at}; resolve them, then run this again\n"));
    }
    let guards: Vec<&str> = paths
        .iter()
        .map(|(_, path)| path.as_str())
        .filter(|path| guard_file(path))
        .collect();
    if a.guard.is_empty() && !guards.is_empty() {
        return Some(format!("builder-done: refused - nothing done: the commit changes a guard file ({}), and its message owes a GUARD_EDIT_OK: line with the reason. Run it again with GUARD=:\n  {} GUARD=\"<what the guard-file edit does, and why it is legitimate>\"\n", guards.join(", "), a.command()));
    }
    waits(p, dones, a.tasks, a.feature)
        .map(|w| format!("builder-done: refused - nothing done: {w}\n"))
}

/// The done commit of one of `tasks` that is not yet carried, in a refusal's words: its ref, its commit and the carry to run first.
fn waits(p: &Pool, dones: &[Done], tasks: &[String], feature: &str) -> Option<String> {
    let names: Vec<String> = tasks.iter().map(|t| format!("{feature}-{t}")).collect();
    let waiting = uncarried(&p.clone, dones);
    let waits = waiting.iter().find(|d| names.contains(&d.name))?;
    Some(format!(
        "{REFS}{} ({}, \"{}\") is done and not yet carried - carry it first: {}",
        waits.name,
        waits.sha.get(..10).unwrap_or(&waits.sha),
        waits.subject(),
        carry_command(p, &waits.sha)
    ))
}

/// The done commits of `feature`'s `tasks` that `tree`'s HEAD does not hold ([`uncarried`]'s test), each ONCE - two tasks built in
/// one bundle share a commit - and OLDEST FIRST by its author's time, the sha breaking a tie: what `make land` carries before anything
/// else (451 T397 part (c)). Each is the commit's sha with the refs it is kept under.
#[must_use]
pub fn to_carry(tree: &Path, feature: &str, tasks: &[String]) -> Vec<(String, Vec<String>)> {
    let key = feature_key(feature);
    let names: Vec<String> = tasks.iter().map(|t| format!("{key}-{t}")).collect();
    let dones = dones(tree);
    let mut open: BTreeMap<(u64, String), Vec<String>> = BTreeMap::new();
    for d in uncarried(tree, &dones) {
        let at = d.key.split('\t').next().and_then(|t| t.parse().ok());
        if names.contains(&d.name) {
            open.entry((at.unwrap_or_default(), d.sha.clone()))
                .or_default()
                .push(format!("{REFS}{}", d.name));
        }
    }
    open.into_iter()
        .map(|((_, sha), refs)| (sha, refs))
        .collect()
}

/// Why `tasks` are handed no tree yet (`make builder-tree`, 451 T398): one of them has a done commit the clone's HEAD does not hold,
/// and a handout brings its tree to that HEAD - so the task's next builder (a closing half) would start without the work it closes.
/// None where nothing of theirs waits. The carry it names always ends the wait: it deletes the ref at its verified end, also where
/// the pick came out empty (451 T397).
pub(crate) fn handout_waits(p: &Pool, tasks: &[String], feature: &str) -> Option<String> {
    let w = waits(p, &dones(&p.clone), tasks, feature)?;
    Some(format!("builder-tree: refused - no tree handed out: {w}\n  a handout starts at the clone's HEAD, so this task's next builder would start without that commit's work\n"))
}

/// The stray profile files of `tree` (`default_*.profraw`, ignored), removed.
fn sweep(tree: &Path) {
    let (_, out, _) = git(
        tree,
        &["ls-files", "-o", "-z", "--", ":(glob)**/default_*.profraw"],
    );
    for stray in out.split('\0').filter(|f| !f.is_empty()) {
        let _ = std::fs::remove_file(tree.join(stray));
    }
}

/// The tree committed, kept and released (the module's doc, steps 2 to 6).
fn commit(p: &Pool, tree: &Path, a: &Ask, dones: &[Done], env: &Env) -> Reply {
    let at = tree.display();
    sweep(tree);
    let guard = if a.guard.is_empty() {
        String::new()
    } else {
        format!("GUARD_EDIT_OK: {}\n", a.guard)
    };
    let file = builder_tree::tree_git_dir(tree).join(MESSAGE);
    let _ = std::fs::write(&file, format!("{}\n{guard}\n{TRAILER}\n", a.subject));
    git(tree, &["add", "-A"]);
    let (ok, _, why) = git(tree, &["commit", "-q", "-F", &file.to_string_lossy()]);
    if !ok {
        git(tree, &["reset", "-q"]);
        return reply(String::new(), format!("builder-done: git commit failed in {at} - nothing committed, nothing left staged, the tree still held:\n{why}"), 1);
    }
    let sha = text(git(tree, &["rev-parse", "HEAD"]).1.as_bytes());
    // a carried commit's ref has done its job; the refs left are the commits that wait
    let waiting: Vec<&str> = uncarried(&p.clone, dones)
        .iter()
        .map(|d| d.name.as_str())
        .collect();
    for d in dones.iter().filter(|d| !waiting.contains(&d.name.as_str())) {
        git(
            &p.clone,
            &["update-ref", "-d", &format!("{REFS}{}", d.name)],
        );
    }
    let mut kept = Vec::new();
    for task in a.tasks {
        let name = format!("{REFS}{}", a.ref_of(task));
        git(&p.clone, &["update-ref", &name, &sha]);
        kept.push(name);
    }
    let holder = format!("{} {}", a.feature, a.tasks.join(","));
    let mut line =
        json!({"utc": env.now, "event": "done", "tree": tree, "detail": holder, "commit": sha});
    if let Some(k) = entry_of(p, tree, &holder) {
        line["entry"] = json!(k);
    }
    builder_tree::log_line(p, &line);
    let freed = builder_tree::release(p, a.tasks, a.feature, env);
    let next = crate::builder_queue::dispatch(p, a.feature);
    let out = format!(
        "builder-done: {at} committed as {} (\"{}\"), kept at {}\n{}builder-done: NEXT, in this order - the next dispatch FIRST, the carry after it (the tree is free now; the carry and the landing can run while the next builder works; ONLY these tasks' own next builder, a closing half, is dispatched after the carry - its tree starts at the clone's HEAD):\n  1. {next}  2. {}\n",
        sha.get(..10).unwrap_or(&sha),
        a.subject,
        kept.join(", "),
        freed.stdout,
        carry_command(p, &sha)
    );
    reply(out, freed.stderr, freed.code)
}

/// `l7r-gate builder-done <tasks> <feature>` from `cwd`, `MSG` and `GUARD` read from the environment.
#[must_use]
pub fn cli(args: &[String], cwd: &Path) -> Reply {
    let var = |n: &str| std::env::var(n).unwrap_or_default();
    cli_with(args, cwd, &var("MSG"), &var("GUARD"))
}

/// [`cli`] with the subject and the guard-edit reason handed in, as the land crate's test of the whole sequence asks it
/// (`land/carry/tests.rs`: a test never sets `MSG` in its own process, where every other test's commands would inherit it).
#[must_use]
pub fn cli_with(args: &[String], cwd: &Path, msg: &str, guard: &str) -> Reply {
    run(args, cwd, &Env::live(), msg, guard)
}

pub(crate) fn run(args: &[String], cwd: &Path, env: &Env, msg: &str, guard: &str) -> Reply {
    let arg = |i: usize| args.get(i).map_or("", String::as_str);
    let tasks = task_list(arg(0));
    let feature = feature_key(arg(1));
    if tasks.is_empty() {
        return refused(USAGE.to_owned());
    }
    if feature.is_empty() {
        return refused(format!(
            "builder-done: refused - F=<feature> (or SPECIFY_FEATURE) names the feature whose tasks hold the tree\n{USAGE}"
        ));
    }
    let subject = msg.trim();
    if subject.is_empty() || subject.contains('\n') {
        return refused(format!(
            "builder-done: refused - MSG is the commit's subject, one line\n{USAGE}"
        ));
    }
    let guard = guard.trim();
    if !guard.is_empty() && !l7r_shared::escape::enough(guard) {
        return refused("builder-done: refused - GUARD needs a reason of two words or more: it is the commit's GUARD_EDIT_OK: line\n".to_owned());
    }
    let Some(p) = builder_tree::pool(cwd) else {
        return refused("builder-done: not in a git repository\n".to_owned());
    };
    let trees = builder_pool::read(&p.common);
    let Some(held) = trees
        .iter()
        .find(|t| builder_tree::holds(t, &tasks, &feature))
    else {
        return refused(format!(
            "builder-done: refused - {feature} {} holds no pool tree (make builder-trees lists them)\n",
            tasks.join(",")
        ));
    };
    let all = |a: &[String]| a.iter().cloned().collect::<BTreeSet<String>>();
    if all(&held.tasks) != all(&tasks) {
        return refused(format!(
            "builder-done: refused - {} is held by {}: make builder-done T={} F={feature} MSG=...\n",
            held.tree.display(),
            held.holder(),
            held.tasks.join(",")
        ));
    }
    if !held.tree.is_dir() {
        return refused(format!(
            "builder-done: refused - {} is gone from disk: make builder-tree-release T={} F={feature}, then make builder-tree-drop\n",
            held.tree.display(),
            held.tasks.join(",")
        ));
    }
    let ask = Ask {
        tasks: &held.tasks,
        feature: &feature,
        subject,
        guard,
    };
    let dones = dones(&p.clone);
    if let Some(why) = unready(&p, &held.tree, &ask, &dones) {
        return refused(why);
    }
    commit(&p, &held.tree, &ask, &dones, env)
}

#[cfg(test)]
mod tests;
