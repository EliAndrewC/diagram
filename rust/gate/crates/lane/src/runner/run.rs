//! THE BATCH RUN (feature 461 T14, plan D5, D6 step 1, D8, D14; data-model.md): the runner's batch step and its resume, plugged into
//! T12's loop ([`super::work`]). A step forms D5's batch ([`crate::batch::form`]) where no batch is open, writes its `batch` line
//! (the changes' full shas, read once, so a later hand-in moves no batch - D14), and runs it:
//!
//! 1. the lane's tree brought to `origin/main` (`builder-tree lane`, T13's call through `builder_tree::cli`), its launcher's
//!    `l7r-gate` built there where stale (T54: so a batch that carries nothing leaves the next start no build), and the changes
//!    `origin/main` already holds dropped (a resumed batch whose set was pushed: data-model.md, "Recovery");
//! 2. each change carried onto the tree, oldest first, by `make carry COMMIT=<sha>` in the tree - the lane carries the batch's OWN
//!    shas, where `make land`'s own carry (`carry_done`) would read the done refs afresh and take a hand-in that moved one after the
//!    batch formed; in the lane's linked tree the carry keeps the done refs (451 T404), and the lane deletes them after the push;
//!    one `carry` line;
//! 3. `make land F=<feature> T="<tasks>" NOTE="<the changes' subjects> - landed by the lane, batch <b>"` there - the gate, the ticks
//!    and the push are the landing's own - its output the attempt's own file, `l7r-lane/attempts/<batch>-<n>.log` (D6 step 1,
//!    never overwritten: `n` continues from the batch's `run` lines); one `run` line, and one `push` line where it pushed - exit 0,
//!    or any other with every change on `origin/main` once fetched: the landing's exit 3 (pushed, other sessions' edits merged)
//!    reaches the runner as make's 2, as every failed recipe's does;
//! 4. each landed change's done ref deleted where it still names the batch's sha (`update-ref -d <ref> <sha>`: a later hand-in that
//!    moved it keeps its ref), then the `landed` line and ONE `owed` line, the status `make lane-wait` will print (T20).
//!
//! The environment `make` gets (contracts/lane-cli.md): `SPECIFY_FEATURE` (and its `_DIRECTORY`), `L7R_LANE_BATCH`, and, as
//! `land-alone.sh` runs its own landing in this same worktree, `L7R_LAND_ALONE=1` (the tree is the landing, never sent alone again)
//! and `SYNC_BACKUP=off`; with the caller's `MSG`, `GUARD`, `T`, `F`, `L7R_GATE_TREE` and make's own `MAKEFLAGS`, `MAKEOVERRIDES`,
//! `MFLAGS` and `MAKELEVEL` removed ([`STRIPPED`]) - a runner a hand-in started inherits `make builder-done`'s, and a variable given
//! on that make's command line reaches a grandchild make through `MAKEFLAGS`.
//!
//! THE SEAMS LEFT (T14 builds the green path): a carry that stops, and a red or refused landing, end the step with an error after
//! their line (a red one also ONE `owed` line naming the attempt file), the batch left OPEN - the runner stops (`error: ...`) rather
//! than form or run again every poll, and the next `make lane-start` resumes it as a new attempt. The red's attribution and
//! ejection are T15's, a carry conflict's repair entry phase 3's, a failed push's T19's.

use std::collections::BTreeSet;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};

use l7r_gate_task::builder_done::{held_by, REFS};
use serde_json::{json, Value};

use crate::batch;
use crate::log::{self, Batch, HandIn, World};

/// What `make` in the lane's tree never inherits from the runner's caller (the module's doc).
pub const STRIPPED: [&str; 9] = [
    "MSG",
    "GUARD",
    "T",
    "F",
    "L7R_GATE_TREE",
    "MAKEFLAGS",
    "MAKEOVERRIDES",
    "MFLAGS",
    "MAKELEVEL",
];
/// The attempts' directory, in the lane's directory.
pub const ATTEMPTS: &str = "attempts";

/// What a batch run reads: the clone's git common directory and the clock (seconds since the epoch), for a run's minutes.
pub struct Lane<'a> {
    pub common: &'a Path,
    pub now: &'a dyn Fn() -> f64,
}

impl Lane<'_> {
    /// The clone: the common directory's work tree.
    fn clone_dir(&self) -> PathBuf {
        self.common.parent().unwrap_or(self.common).to_path_buf()
    }

    fn append(&self, event: &str, fields: &Value) -> Result<(), String> {
        log::append(
            self.common,
            &l7r_gate_core::record::repo::utc_now(),
            event,
            fields,
        )
    }
}

/// `git -C dir args`: its exit, stdout and stderr.
fn git(dir: &Path, args: &[&str]) -> (Option<i32>, String, String) {
    Command::new("git")
        .arg("-C")
        .arg(dir)
        .args(args)
        .output()
        .map_or((None, String::new(), String::new()), |o| {
            (
                o.status.code(),
                String::from_utf8_lossy(&o.stdout).into_owned(),
                String::from_utf8_lossy(&o.stderr).into_owned(),
            )
        })
}

/// The done refs' names and commits.
fn done_refs(common: &Path) -> Vec<(String, String)> {
    git(
        common,
        &["for-each-ref", "--format=%(refname) %(objectname)", REFS],
    )
    .1
    .lines()
    .filter_map(|l| l.split_once(' '))
    .map(|(r, s)| (r.to_owned(), s.to_owned()))
    .collect()
}

/// Every hand-in of the pool's log.
fn all_hand_ins(common: &Path) -> Vec<HandIn> {
    log::hand_ins(&log::lines_of(&common.join(l7r_shared::builder_queue::LOG)))
}

/// THE BATCH STEP: where no batch is open, D5's batch formed, its `batch` line written and the batch run; true where one ran.
///
/// # Errors
///
/// The run's own (the module's doc), or a line that could not be written.
pub fn step(l: &Lane) -> Result<bool, String> {
    let lane = log::read(l.common);
    let batches = log::batches(&lane);
    if batches.iter().any(Batch::open) {
        return Ok(false);
    }
    let refs: BTreeSet<String> = done_refs(l.common).into_iter().map(|(_, s)| s).collect();
    let hand_ins = log::on_lane(all_hand_ins(l.common), &refs, &lane);
    let commits: Vec<String> = hand_ins.iter().map(|h| h.commit.clone()).collect();
    let on_main = held_by(&l.clone_dir(), "origin/main", &commits);
    let w = World {
        hand_ins: &hand_ins,
        on_main: &on_main,
        log: &lane,
        batches: &batches,
    };
    let picked: Vec<HandIn> = batch::form(&w, batch::LANE_MAX)
        .into_iter()
        .cloned()
        .collect();
    let Some(first) = picked.first() else {
        return Ok(false);
    };
    let id = batch::next_id(&lane, &first.feature);
    let shas: Vec<&str> = picked.iter().map(|h| h.commit.as_str()).collect();
    l.append("batch", &json!({"batch": id, "changes": shas}))?;
    run_batch(l, &id, &picked)?;
    Ok(true)
}

/// RECOVERY's run (data-model.md): the open batch `b` of a killed runner, its `remaining` changes run as a new attempt on the tree
/// brought to `origin/main` again.
///
/// # Errors
///
/// A remaining change no hand-in of the pool's log names, or the run's own.
pub fn resume(l: &Lane, b: &Batch, remaining: &[String]) -> Result<(), String> {
    let all = all_hand_ins(l.common);
    let changes = remaining
        .iter()
        .map(|c| {
            all.iter()
                .find(|h| log::names(&h.commit, c))
                .cloned()
                .ok_or_else(|| {
                    format!(
                        "lane: batch {}'s change {c} is no hand-in of the pool's log",
                        b.id
                    )
                })
        })
        .collect::<Result<Vec<_>, _>>()?;
    run_batch(l, &b.id, &changes)
}

/// The short sha a `run` or `push` line's `set` holds.
fn short(sha: &str) -> String {
    sha.chars().take(10).collect()
}

/// A command in the lane's tree, its environment as the module's doc says.
fn in_tree(tree: &Path, args: &[&str], env: &[(&str, &str)]) -> Command {
    let mut c = Command::new("make");
    c.args(args).current_dir(tree).stdin(Stdio::null());
    for k in STRIPPED {
        c.env_remove(k);
    }
    c.envs(env.iter().copied());
    c
}

/// The batch `id` of `changes` (one feature's) run on the lane's tree (the module's doc, steps 1-4).
fn run_batch(l: &Lane, id: &str, changes: &[HandIn]) -> Result<(), String> {
    let began = (l.now)();
    let brought = l7r_gate_task::builder_tree::cli(&["lane".to_owned()], &l.clone_dir());
    if brought.code != 0 {
        return Err(format!("lane: batch {id}: {}", brought.stderr.trim()));
    }
    let tree = PathBuf::from(brought.stdout.trim());
    // THE BUILD AT THE RESET (461 T54): the reset moved the tree's sources; where nothing is carried after it, no `make` of the
    // batch runs the launcher, and the next start's build (T51) waited out the whole move in a hand-in's foreground - up to 112 s
    // measured 2026-11-27 (T51's scratch timing). With a carry it is the build `make carry`'s launcher would make; a failure stops
    // nothing here: the carry's launcher, or the next start, says why.
    let launcher = tree.join("scripts/gates").join(super::LAUNCHER);
    if launcher.is_file() {
        let _ = super::prebuild(&launcher);
    }
    let shas: Vec<String> = changes.iter().map(|h| h.commit.clone()).collect();
    let on_main = held_by(&tree, "HEAD", &shas);
    let todo: Vec<&HandIn> = changes
        .iter()
        .filter(|h| !on_main.contains(&h.commit))
        .collect();
    let mut runs = log::batches(&log::read(l.common))
        .into_iter()
        .rev()
        .find(|b| b.id == id)
        .map_or(0, |b| {
            b.lines.iter().filter(|x| x["event"] == "run").count()
        });
    if let Some(first) = todo.first() {
        carry(l, id, &tree, &todo)?;
        runs += 1;
        land(l, id, &tree, &first.feature, &todo, runs, began)?;
    }
    for (name, sha) in done_refs(l.common) {
        if shas.contains(&sha) {
            let _ = git(l.common, &["update-ref", "-d", &name, &sha]);
        }
    }
    let minutes = ((l.now)() - began) / 60.0;
    let minutes = (minutes * 10.0).round() / 10.0;
    l.append(
        "landed",
        &json!({"batch": id, "landed": shas, "ejected": [], "runs": runs, "minutes": minutes}),
    )?;
    let tasks: Vec<String> = changes.iter().flat_map(|h| h.tasks.clone()).collect();
    let feature = changes.first().map_or("", |h| h.feature.as_str());
    let line = format!(
        "lane: batch {id} landed - {feature} {} ({} change(s), {runs} run(s), {minutes} minutes)",
        tasks.join(" "),
        changes.len()
    );
    l.append("owed", &json!({"batch": id, "line": line}))
}

/// Step 2: each of `todo` carried onto `tree`, oldest first, by `make carry COMMIT=`; one `carry` line.
fn carry(l: &Lane, id: &str, tree: &Path, todo: &[&HandIn]) -> Result<(), String> {
    for h in todo {
        let arg = format!("COMMIT={}", h.commit);
        let done = in_tree(tree, &["--no-print-directory", "carry", &arg], &[]).output();
        // a make that cannot be started is a carry that stopped (exit -1), its line written as any other's
        let (code, stderr) = done.as_ref().map_or((-1, String::new()), |o| {
            (
                o.status.code().unwrap_or(-1),
                String::from_utf8_lossy(&o.stderr).into_owned(),
            )
        });
        if code != 0 {
            let conflict: Vec<String> = git(tree, &["diff", "--name-only", "--diff-filter=U"])
                .1
                .lines()
                .map(str::to_owned)
                .collect();
            l.append(
                "carry",
                &json!({"batch": id, "code": code, "conflict": conflict}),
            )?;
            return Err(format!(
                "lane: batch {id}: the carry of {} stopped (exit {code}; conflicting: {}) - the batch stays open, resumed at the next make lane-start; a carry conflict's repair entry is 461 phase 3's: {}",
                short(&h.commit),
                conflict.join(", "),
                stderr.trim()
            ));
        }
    }
    l.append("carry", &json!({"batch": id, "code": 0, "conflict": []}))
}

/// Whether `origin/main`, fetched, holds every one of `shas` (Recovery's rule): how a landing whose `make` did not end 0 is read -
/// GNU make ends 2 for any recipe that failed, so the landing's own exit 3 (pushed, other sessions' edits merged) arrives as 2.
fn on_origin(tree: &Path, shas: &[&str]) -> bool {
    let _ = git(tree, &["fetch", "-q", "origin", "main"]);
    let wanted: Vec<String> = shas.iter().map(|s| (*s).to_owned()).collect();
    held_by(tree, "refs/remotes/origin/main", &wanted).len() == wanted.len()
}

/// Step 3: `make land` in `tree` over `todo`, attempt `n`; its `run` line, and its `push` line where it pushed.
fn land(
    l: &Lane,
    id: &str,
    tree: &Path,
    feature: &str,
    todo: &[&HandIn],
    n: usize,
    began: f64,
) -> Result<(), String> {
    let spec = l7r_gate_task::tick::spec_dir(tree, feature)
        .and_then(|d| Some(d.file_name()?.to_string_lossy().into_owned()))
        .ok_or_else(|| {
            format!(
                "lane: batch {id}: no single specs/{feature}-* directory in the lane's tree {}",
                tree.display()
            )
        })?;
    let shas: Vec<&str> = todo.iter().map(|h| h.commit.as_str()).collect();
    let mut args = vec!["log", "--no-walk=unsorted", "--format=%s"];
    args.extend(shas.iter().copied());
    let subjects: Vec<String> = git(tree, &args).1.lines().map(str::to_owned).collect();
    let note = format!(
        "NOTE={} - landed by the lane, batch {id}",
        subjects.join("; ")
    );
    let tasks: Vec<String> = todo.iter().flat_map(|h| h.tasks.clone()).collect();
    let (f_arg, t_arg) = (format!("F={feature}"), format!("T={}", tasks.join(" ")));
    let attempt = l
        .common
        .join(log::DIR)
        .join(ATTEMPTS)
        .join(format!("{id}-{n}.log"));
    let (file, err) = std::fs::create_dir_all(attempt.parent().unwrap_or(l.common))
        .and_then(|()| std::fs::File::create(&attempt))
        .and_then(|f| Ok((f.try_clone()?, f)))
        .map_err(|e| format!("lane: {}: {e}", attempt.display()))?;
    let spec_dir = format!("specs/{spec}");
    let env = [
        ("SPECIFY_FEATURE", spec.as_str()),
        ("SPECIFY_FEATURE_DIRECTORY", spec_dir.as_str()),
        ("L7R_LANE_BATCH", id),
        ("L7R_LAND_ALONE", "1"),
        ("SYNC_BACKUP", "off"),
    ];
    let status = in_tree(
        tree,
        &["--no-print-directory", "land", &f_arg, &t_arg, &note],
        &env,
    )
    .stdout(file)
    .stderr(err)
    .status();
    // a make that cannot be started is a red run (exit -1), its line and its owed line written as any other's
    let code = status.map_or(-1, |s| s.code().unwrap_or(-1));
    let set: Vec<String> = shas.iter().map(|s| short(s)).collect();
    let minutes = (((l.now)() - began) / 6.0).round() / 10.0;
    let at = attempt.to_string_lossy();
    l.append(
        "run",
        &json!({"batch": id, "n": n, "set": set, "code": code, "minutes": minutes, "attempt": at, "red": []}),
    )?;
    if code == 0 || on_origin(tree, &shas) {
        return l.append("push", &json!({"batch": id, "set": set, "code": code}));
    }
    let line = format!(
        "lane: batch {id} red at attempt {n} (make land exit {code}) - the runner stopped, the batch open; its attribution and ejection are 461 T15's: {at}"
    );
    l.append("owed", &json!({"batch": id, "line": line}))?;
    Err(line)
}

#[cfg(test)]
mod tests;
