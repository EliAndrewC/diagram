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
//! - `KIND=fix` for a task whose line names a new mechanism ([`mechanism`]): two builders, `build-half` then `closing-half`.
//!   `SIZING_OK="<reason>"` passes this one refusal alone, for a line that names a guard or a command it only repairs.
//!
//! THE BLOCK IS SHORT ON PURPOSE: `agent-prefix-hooks` refuses a prompt that repeats 2,000 characters of an earlier dispatch of its
//! type, and every builder is one type - so the whole block stays under that, and the rules a prompt cannot show stay in the file
//! it names. It keeps a line opening `STOP POINT`, which `context_cap_hooks/split.rs` knows a code builder by.

use std::collections::BTreeSet;
use std::fmt::Write as _;
use std::path::{Path, PathBuf};

use l7r_gate_core::Reply;
use l7r_shared::builder_brief::{Marker, JOBS_MAX, KINDS, MEASURES_MAX};
use l7r_shared::builder_pool;
use l7r_shared::speckit::{marks, tasks};

use crate::builder_tree::{self, Env};
use crate::reply;

const USAGE: &str = "usage: make builder-brief T=<task(s)> F=<feature> KIND=fix|measurement|build-half|closing-half [JOBS=<1-3>] [MEASURES=<things measured>] [CRATE=\"<crate dirs>\"] [BLOCKS=\"<feature> T<n>\"] [LOAD=1]\n";

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
}

/// The make targets a Makefile defines: each `name:` that opens a line.
fn targets(makefile: &str) -> BTreeSet<String> {
    let name = |c: char| c.is_ascii_alphanumeric() || matches!(c, '-' | '_' | '.');
    makefile
        .lines()
        .filter_map(|l| l.split_once(':'))
        .filter(|(head, rest)| !head.is_empty() && head.chars().all(name) && !rest.starts_with('='))
        .map(|(head, _)| head.to_owned())
        .collect()
}

/// What in a task's line names a NEW MECHANISM - a command or a guard, which is two builders from the start - or none. Kept simple:
/// one of four phrases (`a new command`, `a new guard`, `a guard refuses`, `a PreToolUse check`), or a `make <target>` whose target
/// has a hyphen and is no target of the Makefile yet. It MISSES a new command with no hyphen in its name (the hyphen is what tells a
/// target from "make sure"), a guard described in other words ("a hook that stops"), a background step measured before and after,
/// and a new verb of an existing target; it WRONGLY takes a line that names a target a sibling task has not landed yet.
pub(crate) fn mechanism(line: &str, known: &BTreeSet<String>) -> Option<String> {
    let lower = line.to_lowercase();
    let phrase = [
        "a new command",
        "a new guard",
        "a guard refuses",
        "a pretooluse check",
    ]
    .into_iter()
    .find(|p| lower.contains(p));
    if let Some(p) = phrase {
        return Some(format!("\"{p}\""));
    }
    let name = |c: char| c.is_ascii_lowercase() || c.is_ascii_digit() || c == '-';
    line.split("make ")
        .skip(1)
        .map(|rest| rest.split(|c: char| !name(c)).next().unwrap_or(""))
        .find(|t| t.contains('-') && !known.contains(*t))
        .map(|t| format!("`make {t}`, no target of the Makefile yet"))
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
fn feature_dir(clone: &Path, key: &str) -> Option<PathBuf> {
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

/// The command for one brief of `kind`.
fn command(a: &Ask, key: &str, kind: &str) -> String {
    format!("make builder-brief T={} F={key} KIND={kind}", a.task)
}

/// The sizing refusal `a` earns from its own words, before any file is read; none where it is sized.
fn sizing(a: &Ask, key: &str) -> Option<String> {
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

/// The block for `a`, in `tree`, of the feature directory named `name`, its handoff at `handoff`.
fn block(a: &Ask, key: &str, name: &str, tree: &Path, handoff: &Path) -> String {
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
    let (stop, checks) = match a.kind {
        "measurement" => (
            format!("STOP POINT (measurement, {} things): change NO source file. Write the record (commands, figures, units) under dev/measurements/, file each lever you price, and report; no plan section.", a.measures),
            "CHECKS: none - you change no source.".to_owned(),
        ),
        "build-half" => (
            format!("STOP POINT (build half): build and test, red-first, then END at a handoff, {}, by about 200k of context: what is built, each decision and why, the red-first counts, what is not done or not tested. No plan section, `make decide`, plan review or claims step.", handoff.display()),
            format!("CHECKS, the first tier only: `make builder-checks CRATE=\"{crates}\"` and a changed guard's own suite - not closing-checks, static, hooks-test or a coverage run."),
        ),
        "closing-half" => (
            format!("STOP POINT (closing half): read {} first. Then the tests it lists as owed, real coverage of the changed crates, {closes}", handoff.display()),
            format!("CHECKS: `make crate-checks CRATE=\"{crates}\"` (tests, lint, format, coverage) and a changed guard's own suite - not closing-checks, static or hooks-test."),
        ),
        _ => (
            format!("STOP POINT (fix): red-first - the test failing on the old code, its counts reported - then {closes}"),
            format!("CHECKS, the first tier only: `make builder-checks CRATE=\"{crates}\"` and a changed guard's own suite - not closing-checks, static, hooks-test or a coverage run."),
        ),
    };
    let mut out = format!(
        "{}\nBlocks: {}\nTree (the pool's, held for {}): {} - `cd` into it in every command, work ONLY there, make or remove no worktree. `export SPECIFY_FEATURE={name} SPECIFY_FEATURE_DIRECTORY=specs/{name}`\nRead scripts/container/builder-brief.md first: the rules behind this block. Prefix scratch files `{}-`.\n",
        marker.line(),
        if a.blocks.is_empty() { "none" } else { a.blocks },
        a.task,
        tree.display(),
        first.to_lowercase()
    );
    if a.jobs > 1 {
        let _ = writeln!(out, "ORDER: the {} jobs in the order this brief names; if they will not fit, finish one whole, stop, and report the rest as not started.", a.jobs);
    }
    if a.load {
        out.push_str(
            "This task LOADS the machine: it runs ALONE in its batch, bounded (451 T321).\n",
        );
    }
    let _ = writeln!(out, "{stop}\n{checks}");
    if a.kind != "measurement" {
        out.push_str("Test every new line as if coverage ran (a closure passed to max_by, filter or any counts); an assertion's message stays on the assertion's own line or is left out.\n");
    }
    let _ = writeln!(out, "FILE what you find and leave, from your tree: `make task-add F={key} TITLE=\"<title, paths, figures>\"`; its id goes in your report's CANDIDATES.\nReport in the fixed format of scripts/container/builder-report-format.md, read at your stop point. Do NOT stage, commit, land or push; never rewrite history.");
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
    if let Some((task, what)) = named.filter(|_| a.kind == "fix") {
        if !l7r_shared::escape::enough(sizing_ok) {
            return refused(format!(
                "builder-brief: refused - {task}'s line names a new mechanism ({what}), which is TWO builders from the start (three of three such tasks briefed as one reached the cap, 2026-11-26):\n  {}   (builds and tests, ends at a handoff)\n  {}   (after it reports: coverage, the plan section, the review)\nIf the line only names a mechanism this task repairs: SIZING_OK=\"<reason, two words or more>\"\n",
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
    let handoff = common
        .join("l7r-handoffs")
        .join(format!("{}-build.md", bundle.join("-")));
    if a.kind == "closing-half" && !handoff.is_file() {
        let _ = writeln!(notes, "builder-brief: NOTE - the build half's handoff {} is not written yet; the closing half reads it first", handoff.display());
    }
    reply(
        block(&a, &key, &name, &tree, &handoff),
        format!("{}{notes}", took.stderr),
        0,
    )
}

#[cfg(test)]
mod tests;
