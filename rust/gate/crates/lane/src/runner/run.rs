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
//! on that make's command line reaches a grandchild make through `MAKEFLAGS`. `L7R_FEATURE_DIRECTORY` is removed too (461 T15): the
//! event log's writer files a check's Phase line under that variable's feature before `SPECIFY_FEATURE`'s, so a caller's stale one
//! would file the attempt's lines where the attribution never reads them.
//!
//! A RED ATTEMPT (461 T15, D6 step 2 and "By phase", D7): its output and the gate's Phase lines of its span in the lane's tree are
//! read by [`crate::attribute`]; the `run` line names the red units, an `attribute` line the candidates, and phase 2's ejection
//! follows - each change the record places a repair entry of its own (`why` `red`), else the whole of what ran as ONE entry (`why`
//! `unplaced`) - written to `l7r-lane/repairs.jsonl` ([`crate::repairs`]) before the change's `eject` line, one `owed` line an entry.
//! The rest runs again as the next attempt on the tree brought to `origin/main` anew; a batch that ejects everything ends with a
//! `landed` line that lands nothing. An ejected change's done ref is kept: its repair's hand-in supersedes it (D7, D14).
//!
//! A GREEN ATTEMPT WHOSE PUSH FAILED (461 T19; plan, Risks, "Two writers of main", D7's table): told by the landing's own line
//! ([`PUSH_FAILED`]) in the attempt's output with the set not on `origin/main` once fetched; no attribution runs, and the `run` line
//! is followed by a `push` line with `"failed": true`. The first such failure of a batch (a resumed batch's earlier ones counted
//! from its `push` lines) runs the same set again on the tree brought to the new `origin/main`; the second files the set as ONE
//! repair entry of kind `integrate`, `why` `push`, before its `eject` lines, and ends the batch with its `landed` line and ONE
//! `owed` line, the entry's - never `stopped`.
//!
//! THE SEAMS LEFT: a carry that stops ends the step with an error after its line, and a `make` that cannot start (exit -1, no
//! change's fault) or a first pass that refused with a row naming no change of the batch (461 T15's plan review) after its `owed` line, the batch left OPEN - the runner stops (`error: ...`) rather than form or run again every
//! poll, and the next `make lane-start` resumes it as a new attempt. A carry conflict's repair entry is phase 3's (T25), the halving that replaces the whole-batch ejection T24's, the tripwire by task T18's.

use std::collections::BTreeSet;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::time::SystemTime;

use l7r_gate_task::builder_done::{held_by, REFS};
use l7r_shared::guards::event_log_hooks::{log_path_in, now_stamp};
use serde_json::{json, Value};

use crate::attribute::{self, Change, Refusal, Verdict};
use crate::log::{self, Batch, HandIn, World};
use crate::{batch, repairs};

/// What `make` in the lane's tree never inherits from the runner's caller (the module's doc).
pub const STRIPPED: [&str; 10] = [
    "MSG",
    "GUARD",
    "T",
    "F",
    "L7R_GATE_TREE",
    "MAKEFLAGS",
    "MAKEOVERRIDES",
    "MFLAGS",
    "MAKELEVEL",
    "L7R_FEATURE_DIRECTORY",
];
/// The attempts' directory, in the lane's directory.
pub const ATTEMPTS: &str = "attempts";

/// What a batch run reads: the clone's git common directory and the clock (seconds since the epoch), for a run's minutes.
pub struct Lane<'a> {
    pub common: &'a Path,
    pub now: &'a dyn Fn() -> f64,
    /// The environment the gate's event log is found by (`L7R_EVENTS_DIR`), as the landing's own `make` inherits it: the process's
    /// ([`process_env`]) in the runner, a test's own (451 T38: no session's export reaches a test).
    pub env: &'a dyn Fn(&str) -> Option<String>,
}

/// The process's environment, the runner's [`Lane::env`].
#[must_use]
pub fn process_env(name: &str) -> Option<String> {
    std::env::var(name).ok()
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

/// The tree brought to `origin/main` for batch `id` (T13's `builder-tree lane`).
fn bring(l: &Lane, id: &str) -> Result<PathBuf, String> {
    let brought = l7r_gate_task::builder_tree::cli(&["lane".to_owned()], &l.clone_dir());
    if brought.code != 0 {
        return Err(format!("lane: batch {id}: {}", brought.stderr.trim()));
    }
    let tree = PathBuf::from(brought.stdout.trim());
    // THE BUILD AT THE RESET (461 T54): the reset moved the tree's sources; where nothing is carried after it, no `make` of the
    // batch runs the launcher, and the next start's build (T51) waited out the whole move in a hand-in's foreground - up to 112 s
    // measured 2026-11-27 (T51's scratch timing). With a carry it is the build `make carry`'s launcher would make; a failure stops
    // nothing here: the carry's launcher, or the next start, says why. Every reset of a batch builds (461 T15: a red attempt's
    // rest runs again on the tree reset anew).
    let launcher = tree.join("scripts/gates").join(super::LAUNCHER);
    if launcher.is_file() {
        let _ = super::prebuild(&launcher);
    }
    Ok(tree)
}

/// The batch `id` of `changes` (one feature's) run on the lane's tree (the module's doc, steps 1-4): attempts until one pushes, each
/// red attempt ejecting the changes its record places - or, unplaced, every change left - and the rest run again on the tree brought
/// to `origin/main` anew. Every red attempt ejects one change at least, so the loop ends.
fn run_batch(l: &Lane, id: &str, changes: &[HandIn]) -> Result<(), String> {
    let began = (l.now)();
    let mut left: Vec<HandIn> = changes.to_vec();
    let mut landed: Vec<String> = Vec::new();
    let earlier = log::batches(&log::read(l.common))
        .into_iter()
        .rev()
        .find(|b| b.id == id)
        .map_or(Vec::new(), |b| b.lines);
    let mut runs = earlier.iter().filter(|x| x["event"] == "run").count();
    // a resumed batch's failed pushes count (461 T19): the batch runs again ONCE after a failed push, whichever runner ran it
    let mut push_failures = earlier
        .iter()
        .filter(|x| x["event"] == "push" && x["failed"] == true)
        .count();
    // the batch's one `owed` line where an `integrate` repair ended it, in place of the landed line's
    let mut said: Option<String> = None;
    loop {
        let tree = bring(l, id)?;
        let shas: Vec<String> = left.iter().map(|h| h.commit.clone()).collect();
        let on_main = held_by(&tree, "HEAD", &shas);
        landed.extend(shas.iter().filter(|s| on_main.contains(*s)).cloned());
        let todo: Vec<&HandIn> = left
            .iter()
            .filter(|h| !on_main.contains(&h.commit))
            .collect();
        let Some(first) = todo.first() else {
            break;
        };
        carry(l, id, &tree, &todo)?;
        runs += 1;
        match land(l, id, &tree, &first.feature, &todo, runs, began)? {
            Attempt::Pushed => {
                landed.extend(todo.iter().map(|h| h.commit.clone()));
                break;
            }
            // THE PUSH FAILED AFTER A GREEN GATE (461 T19; plan, Risks, "Two writers of main"): the first time, the same set runs again
            // on the tree brought to the new `origin/main`; the second, the set is one `integrate` repair and the batch ends
            Attempt::PushFailed {
                line,
                attempt,
                spec,
            } => {
                push_failures += 1;
                if push_failures < 2 {
                    left = todo.into_iter().cloned().collect();
                    continue;
                }
                said = Some(integrate(l, id, &todo, &line, &attempt, &spec)?);
                break;
            }
            Attempt::Red(out) => {
                let ejected = eject(l, id, &todo, &out)?;
                let rest: Vec<HandIn> = todo
                    .into_iter()
                    .filter(|h| !ejected.contains(&h.commit))
                    .cloned()
                    .collect();
                left = rest;
            }
        }
    }
    for (name, sha) in done_refs(l.common) {
        if landed.contains(&sha) {
            let _ = git(l.common, &["update-ref", "-d", &name, &sha]);
        }
    }
    let ejected: Vec<String> = log::batches(&log::read(l.common))
        .into_iter()
        .rev()
        .find(|b| b.id == id)
        .map_or(Vec::new(), |b| {
            b.lines
                .iter()
                .filter(|x| x["event"] == "eject")
                .filter_map(|x| x["change"].as_str().map(str::to_owned))
                .collect()
        });
    let minutes = ((l.now)() - began) / 60.0;
    let minutes = (minutes * 10.0).round() / 10.0;
    l.append(
        "landed",
        &json!({"batch": id, "landed": landed, "ejected": ejected, "runs": runs, "minutes": minutes}),
    )?;
    let line = said.unwrap_or_else(|| {
        let on: Vec<&HandIn> = changes
            .iter()
            .filter(|h| landed.contains(&h.commit))
            .collect();
        ended(id, &on, ejected.len(), runs, minutes)
    });
    l.append("owed", &json!({"batch": id, "line": line}))
}

/// The `owed` line of batch `id` ended with `on` landed and `ejected` changes ejected.
fn ended(id: &str, on: &[&HandIn], ejected: usize, runs: usize, minutes: f64) -> String {
    let tasks: Vec<String> = on.iter().flat_map(|h| h.tasks.clone()).collect();
    let out = if ejected == 0 {
        String::new()
    } else {
        format!(", {ejected} ejected")
    };
    match on.first() {
        None => format!(
            "lane: batch {id} ended - nothing landed{out} ({runs} run(s), {minutes} minutes)"
        ),
        Some(first) => format!(
            "lane: batch {id} landed - {} {} ({} change(s){out}, {runs} run(s), {minutes} minutes)",
            first.feature,
            tasks.join(" "),
            on.len()
        ),
    }
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

/// The landing's own line for a push that failed after a green gate (`land.rs`'s `land: the push failed (exit <rc>) - ...`), read
/// from the attempt's output as the suites' and the first pass's lines are (461 T19).
pub const PUSH_FAILED: &str = "land: the push failed (exit ";

/// How an attempt ended (step 3).
enum Attempt {
    /// Its push went out.
    Pushed,
    /// Its gate green, its push failed: the landing's [`PUSH_FAILED`] line and the attempt file.
    PushFailed {
        line: String,
        attempt: String,
        spec: String,
    },
    /// Red, for its ejection.
    Red(Redden),
}

/// A red attempt, as its ejection reads it.
struct Redden {
    n: usize,
    /// The feature's spec directory's name, as a repair entry names its feature.
    spec: String,
    attempt: String,
    units: Vec<String>,
    verdict: Verdict,
    /// The changes an unplaced verdict ejects, by their indices: every change, or those a first-pass refusal names.
    unplaced: Vec<usize>,
}

/// The landing's `NOTE=`: the subjects of `shas` in `tree`, and the batch `id`.
fn note_of(tree: &Path, id: &str, shas: &[&str]) -> String {
    let mut args = vec!["log", "--no-walk=unsorted", "--format=%s"];
    args.extend(shas.iter().copied());
    let subjects: Vec<String> = git(tree, &args).1.lines().map(str::to_owned).collect();
    format!(
        "NOTE={} - landed by the lane, batch {id}",
        subjects.join("; ")
    )
}

/// Attempt `n`'s own file of batch `id`, created: its path and two handles on it, the landing's stdout and stderr.
fn attempt_file(
    l: &Lane,
    id: &str,
    n: usize,
) -> Result<(PathBuf, std::fs::File, std::fs::File), String> {
    let attempt = l
        .common
        .join(log::DIR)
        .join(ATTEMPTS)
        .join(format!("{id}-{n}.log"));
    let (file, err) = std::fs::create_dir_all(attempt.parent().unwrap_or(l.common))
        .and_then(|()| std::fs::File::create(&attempt))
        .and_then(|f| Ok((f.try_clone()?, f)))
        .map_err(|e| format!("lane: {}: {e}", attempt.display()))?;
    Ok((attempt, file, err))
}

/// Step 3: `make land` in `tree` over `todo`, attempt `n`; its `run` line, and its `push` line where it pushed, or where its push
/// failed after a green gate (`"failed": true`, 461 T19: no red to read, so no attribution); a red attempt read against the gate's
/// record (`attribute`, T15) and handed back for its ejection.
fn land(
    l: &Lane,
    id: &str,
    tree: &Path,
    feature: &str,
    todo: &[&HandIn],
    n: usize,
    began: f64,
) -> Result<Attempt, String> {
    let spec = l7r_gate_task::tick::spec_dir(tree, feature)
        .and_then(|d| Some(d.file_name()?.to_string_lossy().into_owned()))
        .ok_or_else(|| {
            format!(
                "lane: batch {id}: no single specs/{feature}-* directory in the lane's tree {}",
                tree.display()
            )
        })?;
    let shas: Vec<&str> = todo.iter().map(|h| h.commit.as_str()).collect();
    let note = note_of(tree, id, &shas);
    let tasks: Vec<String> = todo.iter().flat_map(|h| h.tasks.clone()).collect();
    let (f_arg, t_arg) = (format!("F={feature}"), format!("T={}", tasks.join(" ")));
    let (attempt, file, err) = attempt_file(l, id, n)?;
    let spec_dir = format!("specs/{spec}");
    let env = [
        ("SPECIFY_FEATURE", spec.as_str()),
        ("SPECIFY_FEATURE_DIRECTORY", spec_dir.as_str()),
        ("L7R_LANE_BATCH", id),
        ("L7R_LAND_ALONE", "1"),
        ("SYNC_BACKUP", "off"),
    ];
    let t0 = now_stamp(SystemTime::now());
    let status = in_tree(
        tree,
        &["--no-print-directory", "land", &f_arg, &t_arg, &note],
        &env,
    )
    .stdout(file)
    .stderr(err)
    .status();
    let t1 = now_stamp(SystemTime::now());
    // a make that cannot be started, or one killed, is exit -1: no change's fault, so nothing is ejected - the runner stops, the batch
    // open
    let code = status.map_or(-1, |s| s.code().unwrap_or(-1));
    let set: Vec<String> = shas.iter().map(|s| short(s)).collect();
    let minutes = (((l.now)() - began) / 6.0).round() / 10.0;
    let at = attempt.to_string_lossy().into_owned();
    let pushed = code == 0 || on_origin(tree, &shas);
    let output = std::fs::read_to_string(&attempt).unwrap_or_default();
    let push_failed = (!pushed && code != -1)
        .then(|| output.lines().find(|x| x.contains(PUSH_FAILED)))
        .flatten()
        .map(|x| x.trim().to_owned());
    let red = (!pushed && code != -1 && push_failed.is_none()).then(|| {
        let events = log::lines_of(&log_path_in(tree, &spec, l.env));
        let reds = attribute::reds(&events, (&t0, &t1), tree, &output);
        let changes: Vec<Change> = todo.iter().map(|h| change_of(tree, h)).collect();
        let verdict = attribute::attribute(&reds, &changes);
        let refused = attribute::refusal(&reds, &changes);
        (
            reds.into_iter().map(|r| r.unit).collect::<Vec<_>>(),
            verdict,
            refused,
        )
    });
    let units = red.as_ref().map_or(Vec::new(), |(u, _, _)| u.clone());
    l.append(
        "run",
        &json!({"batch": id, "n": n, "set": set, "code": code, "minutes": minutes, "attempt": at, "red": units}),
    )?;
    if pushed {
        l.append("push", &json!({"batch": id, "set": set, "code": code}))?;
        return Ok(Attempt::Pushed);
    }
    if let Some(line) = push_failed {
        l.append(
            "push",
            &json!({"batch": id, "set": set, "code": code, "failed": true}),
        )?;
        return Ok(Attempt::PushFailed {
            line,
            attempt: at,
            spec,
        });
    }
    let Some((units, verdict, refused)) = red else {
        return stopped(
            l,
            id,
            format!("lane: batch {id}: make land ended with no exit code at attempt {n} (it could not start, or was killed) - the runner stopped, the batch open: {at}"),
        );
    };
    // A FIRST-PASS REFUSAL NAMING NO CHANGE EJECTS NOTHING (461 T15's plan review, round 1): a hold, a lock or an owed round is no
    // change's fault and refuses their repairs again, so the runner stops with the batch open, as at exit -1; a refusal whose every
    // row names one change of the batch ejects those changes as any placed red does
    if let Refusal::Unnamed(rows) = &refused {
        return stopped(
            l,
            id,
            format!("lane: batch {id}: make land's first pass refused at attempt {n}, a row naming no change of the batch ({}) - the runner stopped, the batch open, nothing ejected: {at}", rows.join("; ")),
        );
    }
    // a refusal naming several changes ejects those it names as one entry, the rest run again (round 2); every change else
    let unplaced = match refused {
        Refusal::Named(named) => named,
        Refusal::None | Refusal::Unnamed(_) => (0..todo.len()).collect(),
    };
    Ok(Attempt::Red(Redden {
        n,
        spec,
        attempt: at,
        units,
        verdict,
        unplaced,
    }))
}

/// The runner stopped with batch `id` open: its own `owed` line, `"stopped": true` so no death line follows it (`wake::dead`), and
/// the line as the step's error.
fn stopped<T>(l: &Lane, id: &str, line: String) -> Result<T, String> {
    l.append(
        "owed",
        &json!({"batch": id, crate::wake::STOPPED: true, "line": line}),
    )?;
    Err(line)
}

/// A change as attribution reads it: the paths its commit touches against its parent, and its tasks.
fn change_of(tree: &Path, h: &HandIn) -> Change {
    let files = git(
        tree,
        &[
            "diff-tree",
            "--no-commit-id",
            "--name-only",
            "-r",
            &h.commit,
        ],
    )
    .1
    .lines()
    .map(str::to_owned)
    .collect();
    Change {
        files,
        tasks: h.tasks.clone(),
    }
}

/// A GREEN SET WHOSE PUSH FAILED TWICE (461 T19, D7's table): every change of `todo` filed as ONE repair entry of kind `integrate`,
/// `why` `push` - `tasks` every change's, `units` the landing's push line, `attempt` the second attempt's file, the push's output -
/// before its `eject` lines (`repairs`' doc); the batch's one `owed` line, returned for the `landed` line to be followed by. Never
/// `stopped`: the fresh builder's hand-in supersedes the set (D7), and the lane goes on with the next batch.
fn integrate(
    l: &Lane,
    id: &str,
    todo: &[&HandIn],
    push: &str,
    attempt: &str,
    spec: &str,
) -> Result<String, String> {
    let tasks: Vec<String> = todo.iter().flat_map(|h| h.tasks.clone()).collect();
    let entry = repairs::Entry {
        feature: spec.to_owned(),
        tasks: tasks.clone(),
        kind: "integrate".to_owned(),
        ejected: todo.iter().map(|h| h.commit.clone()).collect(),
        batch: id.to_owned(),
        why: "push".to_owned(),
        units: vec![push.to_owned()],
        attempt: attempt.to_owned(),
    };
    let r = repairs::file(l.common, &l7r_gate_core::record::repo::utc_now(), &entry)?;
    for h in todo {
        l.append(
            "eject",
            &json!({"batch": id, "change": h.commit, "repair": r, "why": "push"}),
        )?;
    }
    let feature = todo.first().map_or("", |h| h.feature.as_str());
    Ok(format!(
        "lane: batch {id} green but its push failed twice - {feature} {} filed as repair {r} (integrate, push: {push}) - make builder-next hands it to a fresh builder: {attempt}",
        tasks.join(" ")
    ))
}

/// PHASE 2'S EJECTION (D6 "By phase", D7): the `attribute` line, then each placed change as a repair entry of its own (`why` `red`,
/// its units), or, unplaced, every change of `todo` as ONE entry (`why` `unplaced`, every unit read) - each entry filed before its
/// `eject` lines (`repairs`' doc), then one `owed` line an entry, naming it and the attempt file. The ejected commits, returned.
fn eject(l: &Lane, id: &str, todo: &[&HandIn], red: &Redden) -> Result<Vec<String>, String> {
    let groups: Vec<(Vec<&HandIn>, Vec<String>, &str)> = match &red.verdict {
        Verdict::Unplaced => vec![(
            red.unplaced.iter().map(|&i| todo[i]).collect(),
            red.units.clone(),
            "unplaced",
        )],
        Verdict::Placed(placed) => placed
            .iter()
            .map(|(i, units)| (vec![todo[*i]], units.clone(), "red"))
            .collect(),
    };
    let how = if red.verdict == Verdict::Unplaced {
        "none"
    } else {
        "record"
    };
    let candidates: Vec<&str> = groups
        .iter()
        .flat_map(|(hs, _, _)| hs.iter().map(|h| h.commit.as_str()))
        .collect();
    l.append(
        "attribute",
        &json!({"batch": id, "candidates": candidates, "how": how}),
    )?;
    for (hs, units, why) in &groups {
        let tasks: Vec<String> = hs.iter().flat_map(|h| h.tasks.clone()).collect();
        let entry = repairs::Entry {
            feature: red.spec.clone(),
            tasks: tasks.clone(),
            kind: "fix".to_owned(),
            ejected: hs.iter().map(|h| h.commit.clone()).collect(),
            batch: id.to_owned(),
            why: (*why).to_owned(),
            units: units.clone(),
            attempt: red.attempt.clone(),
        };
        let r = repairs::file(l.common, &l7r_gate_core::record::repo::utc_now(), &entry)?;
        for h in hs {
            l.append(
                "eject",
                &json!({"batch": id, "change": h.commit, "repair": r, "why": why}),
            )?;
        }
        let named = if units.is_empty() {
            "the record names none".to_owned()
        } else {
            units.join(", ")
        };
        let feature = hs.first().map_or("", |h| h.feature.as_str());
        let line = format!(
            "lane: batch {id} red at attempt {} - {feature} {} ejected as repair {r} ({why}: {named}) - make builder-next hands it to a fresh builder: {}",
            red.n,
            tasks.join(" "),
            red.attempt
        );
        l.append("owed", &json!({"batch": id, "line": line}))?;
    }
    Ok(candidates.into_iter().map(str::to_owned).collect())
}

#[cfg(test)]
mod tests;
