//! `l7r-gate builder-brief` (feature 451 T334; the GM, 2026-11-26: "is this also part of our checklist-based process for kicking off
//! and managing builders? Or do we not have such a checklist? ... I just want to make sure that we're putting the instructions in the
//! right place"): THE STANDING PART OF A BUILDER'S BRIEF, MADE BY THE TOOLING. The sizing rules of
//! `scripts/container/builder-brief.md` were a file the coordinating session was to load and remember; on 2026-11-26 it broke them
//! five times with nothing refusing (T285, T298, T316, T308, each reaching the 300k cap; T315, "one job" that was seven crates and
//! eight levers, ended at 308k). `make builder-brief T= F= KIND=` sizes the brief FIRST, then takes the task's tree from the pool
//! (`builder_tree`, its refusals this command's) and prints the block for that kind, ready to paste at the head of a brief. Its first
//! line is the marker `builder-brief-hooks` holds a builder's dispatch to (`l7r_shared::builder_brief`).
//!
//! A BUNDLE - `T=a,b`, several tasks one builder builds in one tree - is briefed where `make builder-tree T=a,b` hands a tree out
//! for it (the coordinating session's ruling, 2026-11-26: T299 and T282 were built as one that day, and an escape on every bundle
//! would spend the audit's falsifier). The marker names the tasks joined by commas, each task's line is read, and a tree some of
//! them already hold without the others is refused here, since the guard would refuse the block made on it.
//!
//! REFUSED, each printing the command to run instead, BEFORE any tree is taken:
//! - `JOBS` past three (`JOBS_MAX`);
//! - `KIND=measurement` with no `MEASURES`, or with more than `MEASURES_MAX` things measured (a GUESS knob: 451 T315);
//! - `KIND=fix` for a task whose line names a new mechanism (`l7r_shared::builder_brief::mechanism`, shared with the queue since 451 T313's round 3): two builders, `build-half` then `closing-half`.
//!   `SIZING_OK="<reason>"` passes this one refusal alone, for a line that names a guard or a command it only repairs.
//!
//! THE BLOCK IS SHORT ON PURPOSE: `agent-prefix-hooks` refuses a prompt that repeats 2,000 characters of an earlier dispatch of its
//! type, and every builder is one type - so the whole block stays under that, and the rules a prompt cannot show stay in the file
//! it names. It keeps a line opening `STOP POINT`, which `context_cap_hooks/split.rs` knows a code builder by.

use std::fmt::Write as _;
use std::path::{Path, PathBuf};

use l7r_gate_core::Reply;
use l7r_shared::builder_brief::{mechanism, targets, Marker, JOBS_MAX, KINDS, MEASURES_MAX};
use l7r_shared::builder_pool;
use l7r_shared::builder_queue::repairs::{self, Repair};
use l7r_shared::speckit::{marks, tasks};
use serde_json::json;

use crate::builder_tree::{self, Env};
use crate::reply;

const USAGE: &str = "usage: make builder-brief T=<task(s)> F=<feature> KIND=fix|measurement|build-half|closing-half [JOBS=<1-3>] [MEASURES=<things measured>] [CRATE=\"<crate dirs>\"] [BLOCKS=\"<feature> T<n>\"] [LOAD=1] [ENTRY=<the queue entry, as make builder-next prints it>] [REPAIR=<the lane's repair entry, as make builder-next prints it>]\n";

/// What a caller says of the brief it is writing.
struct Ask<'a> {
    /// The task, or a bundle's tasks joined by commas.
    task: &'a str,
    /// The feature as given (`451`, its directory's name or path).
    feature: &'a str,
    kind: &'a str,
    jobs: usize,
    measures: &'a str,
    crates: &'a str,
    blocks: &'a str,
    load: bool,
    /// The queue entry it serves, `ENTRY=` as `make builder-next` prints it (451 T313): its ordinal among its first task's lines.
    entry: &'a str,
    /// The lane's repair entry it serves, `REPAIR=` as `make builder-next` prints it (461 T16): `r<n>`, or empty.
    repair: &'a str,
}

/// The line of `task` in a feature's tasks, open or archived.
fn task_line(all: &str, task: &str) -> Option<String> {
    all.lines()
        .find(|l| {
            let rest = l.trim_start().strip_prefix("- [");
            rest.and_then(|r| r.get(3..))
                .and_then(|r| r.split_whitespace().next())
                == Some(task)
        })
        .map(str::to_owned)
}

/// The feature's directory under `specs/` of `clone`: the one whose name is `key` or opens `key-`.
pub(crate) fn feature_dir(clone: &Path, key: &str) -> Option<PathBuf> {
    let prefix = format!("{key}-");
    let mut dirs: Vec<PathBuf> = std::fs::read_dir(clone.join("specs"))
        .map(|d| d.filter_map(Result::ok).map(|e| e.path()).collect())
        .unwrap_or_default();
    dirs.sort();
    dirs.into_iter().find(|d| {
        let name = d.file_name().unwrap_or_default().to_string_lossy();
        d.is_dir() && (name == key || name.starts_with(&prefix))
    })
}

fn refused(why: String) -> Reply {
    reply(String::new(), why, 2)
}

/// THE LANE'S REPAIR ENTRY `REPAIR=` names (461 T16): none where it names none; refused where no open entry has that id (an
/// answered or superseded one included: its fresh builder was dispatched), or where the entry is not this brief's - its feature,
/// its tasks and its kind as `make builder-next` printed them.
fn repair_of(
    a: &Ask,
    key: &str,
    tasks: &[String],
    common: &Path,
) -> Result<Option<Repair>, String> {
    if a.repair.is_empty() {
        return Ok(None);
    }
    let Some(r) = repairs::open(common).into_iter().find(|r| r.id == a.repair) else {
        return Err(format!("builder-brief: refused - REPAIR={} is no open repair entry of the lane: answered, superseded or never ejected. make builder-next names the open ones\n", a.repair));
    };
    if r.key != key || r.tasks != tasks || r.kind != a.kind {
        return Err(format!("builder-brief: refused - REPAIR={} is {} of kind {}, not this brief's: brief it as filed\n  {}\n", r.id, r.name(), r.kind, r.command()));
    }
    Ok(Some(r))
}

/// The command for one brief of `kind`.
fn command(a: &Ask, key: &str, kind: &str) -> String {
    format!("make builder-brief T={} F={key} KIND={kind}", a.task)
}

/// The sizing refusal `a` earns from its own words, before any file is read; none where it is sized.
/// `ENTRY=` as the queue entry's ordinal; none where it is not given or is no number above 0.
fn entry(a: &Ask) -> Option<u64> {
    a.entry.parse::<u64>().ok().filter(|k| *k > 0)
}

/// The brief's line of the pool's log, beside the take: the entry it serves, for `make builder-done`'s done line (451 T313); a
/// brief with none names none.
fn logged(a: &Ask, common: &Path, env: &Env, tree: &Path, holder: &str) {
    let mut line =
        json!({"utc": env.now, "event": "brief", "tree": tree, "detail": holder, "kind": a.kind});
    if let Some(k) = entry(a) {
        line["entry"] = json!(k);
    }
    if !a.repair.is_empty() {
        line["repair"] = json!(a.repair);
    }
    builder_tree::log_in(common, &line);
}

fn sizing(a: &Ask, key: &str) -> Option<String> {
    if !a.entry.is_empty() && entry(a).is_none() {
        return Some(format!("builder-brief: refused - ENTRY={} is no entry's number: give it as make builder-next prints it (ENTRY=1 is the task's first line of the queue), or leave it out\n{USAGE}", a.entry));
    }
    if !KINDS.contains(&a.kind) {
        return Some(format!(
            "builder-brief: refused - KIND={} is none of {}\n{USAGE}",
            a.kind,
            KINDS.join(", ")
        ));
    }
    if a.jobs == 0 {
        return Some(format!(
            "builder-brief: refused - JOBS is a count from 1 to {JOBS_MAX}\n{USAGE}"
        ));
    }
    if a.jobs > JOBS_MAX {
        return Some(format!(
            "builder-brief: refused - JOBS={}: a brief holds at most {JOBS_MAX} jobs (4 or more handed off 52% of the time, against 16-22%). Split it, the first builder's report the next one's brief:\n  {} JOBS={JOBS_MAX}\n  {} JOBS={}   (after the first reports; split again past {JOBS_MAX})\n",
            a.jobs,
            command(a, key, a.kind),
            command(a, key, a.kind),
            a.jobs - JOBS_MAX
        ));
    }
    if a.kind != "measurement" {
        return None;
    }
    let Ok(things) = a.measures.parse::<usize>() else {
        return Some(format!(
            "builder-brief: refused - a measurement is sized by the THINGS MEASURED as well as its jobs (451 T315: one job, seven crates and eight levers, 308k). Count them - each crate, lever or case timed is one - and run:\n  {} MEASURES=<n>   (at most {MEASURES_MAX})\n",
            command(a, key, a.kind)
        ));
    };
    (things > MEASURES_MAX).then(|| {
        format!(
            "builder-brief: refused - MEASURES={things}: a measurement brief measures at most {MEASURES_MAX} things (a GUESS knob; 451 T315's seven crates and eight levers ended at 308k). Split it, a brief each:\n  {} MEASURES={MEASURES_MAX}\n  {} MEASURES={}   (the rest; split again past {MEASURES_MAX})\n",
            command(a, key, a.kind),
            command(a, key, a.kind),
            things - MEASURES_MAX
        )
    })
}

/// The block's line naming the plan read (451 T502): `make plan-section` (T501) prints a task's sections, where builders read
/// 3.68 MB of plan text by grep and sed in two days (T499), and a builder reads the rules file's line on it only if it opens that file.
fn plan_read(task: &str) -> String {
    format!("Read your plan sections with `make plan-section T={task}`, never by grep, sed or a Read over plan.md or plan-done.md.\n")
}

/// The block for `a`, in `tree`, of the feature directory named `name`, its handoff at `handoff`.
fn block(
    a: &Ask,
    key: &str,
    name: &str,
    tree: &Path,
    handoff: &Path,
    fixing: Option<&Repair>,
) -> String {
    // a bundle's scratch files carry its first task's prefix
    let first = a.task.split(',').next().unwrap_or(a.task);
    let marker = Marker {
        feature: key.to_owned(),
        task: a.task.to_owned(),
        kind: a.kind.to_owned(),
        jobs: a.jobs,
        tree: tree.to_path_buf(),
    };
    let crates = if a.crates.is_empty() {
        "<the crates you changed>"
    } else {
        a.crates
    };
    let closes = format!("the plan section, `make decide`, the plan review (`make plan-delta F={key}`) and `make claims-triage`; you dispatch no claims-triage or impl-drift agent.");
    // TWO TIERS (451 T308; the GM 2026-11-26, docs/process-decisions.md "Two tiers of checking"): every kind that changes source runs
    // the first tier and no coverage - the closing half too, which ran `make crate-checks` until the GM's ruling that coverage is the
    // second tier's alone. The one builder that runs coverage is the one whose job is the repair of a batch gate red on it.
    // ...its one exception named in a fix's block alone, since a batch gate's coverage repair is briefed as a fix (461 T44: a build
    // half's block with every option given ran past the 2,000-character cap once it carried the hand-in line)
    let repair = if a.kind == "fix" {
        " (the one exception: a brief whose JOB is the coverage repair of a red batch gate runs `make crate-checks` on the crates it names)"
    } else {
        ""
    };
    let first_tier = format!("CHECKS, the first tier only: `make builder-checks CRATE=\"{crates}\"` and a changed guard's own suite - not closing-checks, static, hooks-test or a coverage run{repair}.");
    let (stop, checks) = match a.kind {
        "measurement" => (
            format!("STOP POINT (measurement, {} things): change NO source file. Write the record (commands, figures, units) under dev/measurements/, file each lever you price, and report; no plan section.", a.measures),
            "CHECKS: none - you change no source.".to_owned(),
        ),
        "build-half" => (
            format!("STOP POINT (build half): build and test, red-first, then END at a handoff, {}, by about 200k: what is built, each decision and why, the red-first counts, what is not done or tested. No plan section, `make decide`, plan review or claims step.", handoff.display()),
            first_tier,
        ),
        "closing-half" => (
            format!("STOP POINT (closing half): read {} first. Then the tests it lists as owed, {closes}", handoff.display()),
            first_tier,
        ),
        _ => (
            format!("STOP POINT (fix): red-first - the test failing on the old code, its counts reported - then {closes}"),
            first_tier,
        ),
    };
    let mut out = format!(
        "{}\nBlocks: {}\nTree (the pool's, held for {}): {} - `cd` into it in every command, work ONLY there, make or remove no worktree. `export SPECIFY_FEATURE={name} SPECIFY_FEATURE_DIRECTORY=specs/{name}`\nRead scripts/container/builder-brief.md first: the rules behind this block. Prefix scratch files `{}-`.\n{}",
        marker.line(),
        if a.blocks.is_empty() { "none" } else { a.blocks },
        a.task,
        tree.display(),
        first.to_lowercase(),
        plan_read(a.task)
    );
    if a.jobs > 1 {
        let _ = writeln!(out, "ORDER: the {} jobs in this brief's order; if they will not fit, finish one whole, stop, report the rest as not started.", a.jobs);
    }
    if a.load {
        out.push_str("This task LOADS the machine: it runs ALONE in its batch, bounded.\n");
    }
    // 461 T16 (D7, 451 T308): a repair's builder is FRESH and given what it needs whole - the gate's output and the change
    if let Some(r) = fixing {
        let shas: Vec<&str> = r.changes.iter().map(|c| c.get(..10).unwrap_or(c)).collect();
        let _ = writeln!(out, "REPAIR {} (batch {}, {}): the lane ejected {}, applied in your tree uncommitted - fix it on top. Read the gate's output first: {}", r.id, r.batch, r.why, shas.join(" "), r.attempt);
    }
    let _ = writeln!(out, "{stop}\n{checks}");
    if a.kind != "measurement" {
        out.push_str("Test every new line as if coverage ran (each closure counts); an assertion's message stays on its own line or is left out.\n");
    }
    // 461 T43 (US2: "A refusal a builder can answer is answered by the builder that has the context"): every builder hands in itself,
    // last, so a conflict or a first-pass refusal reaches the builder that holds the context - a fix and a closing half once their
    // review is CLEAR, a build half once its handoff is written and a measurement once its record is, their sections' asks put off at
    // their hand-in (461 T44: `land/hand_in.rs`'s `section_of`, the kind read from this brief's line of the pool's log)
    let after = match a.kind {
        "build-half" => "the handoff written",
        "measurement" => "the record written",
        _ => "review CLEAR",
    };
    let _ = writeln!(out, "HAND IN last, {after}, your one commit: `make builder-done T={} F={key} MSG=\"<subject>\"` [GUARD=\"<why>\"]. A conflict: resolve, `git add`, rerun; a refusal: answer, rerun, or report a claims one verbatim.", a.task);
    let _ = writeln!(out, "FILE what you find and leave, from your tree: `make task-add F={key} TITLE=\"<title, paths, figures>\"`; its id goes in your report's CANDIDATES.\nReport in the fixed format of scripts/container/builder-report-format.md, read at your stop point. Never land or push; never rewrite history.");
    out
}

/// `l7r-gate builder-brief <task(s)> <feature> <kind> [jobs] [measures] [crates] [blocks] [load]` from `cwd`, `SIZING_OK` its escape.
#[must_use]
pub fn cli(args: &[String], cwd: &Path) -> Reply {
    let ok = std::env::var("SIZING_OK").unwrap_or_default();
    run(args, cwd, &Env::live(), &ok)
}

pub(crate) fn run(args: &[String], cwd: &Path, env: &Env, sizing_ok: &str) -> Reply {
    let arg = |i: usize| args.get(i).map_or("", |s| s.trim());
    let bundle = builder_tree::task_list(arg(0));
    let joined = bundle.join(",");
    let a = Ask {
        task: &joined,
        feature: arg(1),
        kind: arg(2),
        jobs: Some(arg(3))
            .filter(|j| !j.is_empty())
            .map_or(1, |j| j.parse().unwrap_or(0)),
        measures: arg(4),
        crates: arg(5),
        blocks: arg(6),
        load: !arg(7).is_empty(),
        entry: arg(8),
        repair: arg(9),
    };
    let key = builder_tree::feature_key(a.feature);
    if a.task.is_empty() || key.is_empty() || a.kind.is_empty() {
        return refused(USAGE.to_owned());
    }
    if let Some(why) = sizing(&a, &key) {
        return refused(why);
    }
    let Some((common, _)) = marks::places(cwd) else {
        return refused("builder-brief: not in a git repository\n".to_owned());
    };
    let clone = marks::main_top(&common);
    let repair = match repair_of(&a, &key, &bundle, &common) {
        Ok(r) => r,
        Err(why) => return refused(why),
    };
    let Some(dir) = feature_dir(&clone, &key) else {
        return refused(format!(
            "builder-brief: refused - no specs/{key}-* in {}\n",
            clone.display()
        ));
    };
    let name = dir
        .file_name()
        .unwrap_or_default()
        .to_string_lossy()
        .into_owned();
    let all = tasks::all_text(&dir).unwrap_or_default();
    let mut lines = Vec::new();
    for t in &bundle {
        let Some(line) = task_line(&all, t) else {
            return refused(format!("builder-brief: refused - specs/{name}/tasks.md has no task {t} (make task-add F={key} TITLE=\"...\" files one)\n"));
        };
        lines.push((t, line));
    }
    let known = targets(&std::fs::read_to_string(clone.join("Makefile")).unwrap_or_default());
    let mut notes = String::new();
    let named = lines
        .iter()
        .find_map(|(t, line)| mechanism(line, &known).map(|what| (*t, what)));
    // a repair is briefed as the lane filed it: its task's line already built once, so no split is owed
    if let Some((task, what)) = named.filter(|_| a.kind == "fix" && repair.is_none()) {
        if !l7r_shared::escape::enough(sizing_ok) {
            return refused(format!(
                "builder-brief: refused - {task}'s line names a new mechanism ({what}), which is TWO builders from the start (three of three such tasks briefed as one reached the cap, 2026-11-26):\n  {}   (builds and tests, ends at a handoff)\n  {}   (after it reports: the owed tests, the plan section, the review)\nIf the line only names a mechanism this task repairs: SIZING_OK=\"<reason, two words or more>\"\n",
                command(&a, &key, "build-half"),
                command(&a, &key, "closing-half")
            ));
        }
        let _ = writeln!(notes, "builder-brief: {task}'s line names a new mechanism ({what}); briefed as one fix on SIZING_OK: {sizing_ok}");
    }
    let took = builder_tree::run(
        &["take".to_owned(), a.task.to_owned(), key.clone()],
        cwd,
        env,
    );
    if took.code != 0 {
        return took;
    }
    let tree = PathBuf::from(took.stdout.trim());
    // the pool hands a tree to a bundle that ONE of its tasks already holds; the guard holds the marker to every task it names
    let pool = builder_pool::read(&common);
    let held = pool.iter().find(|t| t.tree == tree);
    let holder = held.map(builder_pool::Tree::holder).unwrap_or_default();
    let has = |t: &String| held.is_some_and(|h| h.tasks.contains(t));
    if let Some(out) = bundle.iter().find(|t| !has(t)) {
        return refused(format!(
            "builder-brief: refused - {} is held by {holder}, which does not hold {out}: a bundle is one hold, taken whole. Brief what holds it, and {out} in a tree of its own:\n  make builder-brief T={} F={key} KIND={}\n  make builder-brief T={out} F={key} KIND={}\n",
            tree.display(),
            held.map_or_else(String::new, |h| h.tasks.join(",")),
            a.kind,
            a.kind
        ));
    }
    logged(&a, &common, env, &tree, &holder);
    let handoff = common
        .join("l7r-handoffs")
        .join(format!("{}-build.md", bundle.join("-")));
    if a.kind == "closing-half" && !handoff.is_file() {
        let _ = writeln!(notes, "builder-brief: NOTE - the build half's handoff {} is not written yet; the closing half reads it first", handoff.display());
    }
    reply(
        block(&a, &key, &name, &tree, &handoff, repair.as_ref()),
        format!("{}{notes}", took.stderr),
        0,
    )
}

#[cfg(test)]
mod tests;
