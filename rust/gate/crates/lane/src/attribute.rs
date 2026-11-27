//! A RED BATCH'S ATTRIBUTION (feature 461 T15, plan D6 step 2 and "By phase"; data-model.md, the `run` line's `red` and the
//! `attribute` line): which of a red attempt's changes the gate's own record names. Pure: the caller hands in the event log's lines,
//! the attempt's span and tree, its output and each change's delta, and gets the red units and the verdict back.
//!
//! THE RED UNITS, read from the record of the attempt alone:
//! - a red `test`, `lint`, `cover-build`, `cover-run` or `build` Phase line ([`STEPS`]) whose span lies inside the attempt's and whose
//!   `clone` is the lane's tree (other trees' builders write to the same feature's log at the same time), ONE UNIT A LINE,
//!   `<crate dir> <step>` (data-model.md's form) - a line naming several crates one unit over all of them (`<dir> <dir> <step>`, the
//!   first [`NAMED`] dirs and `(+<k> more)`), which names every change under any of them. WHY a line and not a crate: a `cover-build`
//!   is one compile of a crate family, and its red says only that one of them failed - read a unit a crate, an innocent change under
//!   another crate of the family was placed and ejected beside the culprit. Of the clone's 2,723 `cover-build` lines, 947 named 2 to 28
//!   crates; every `test`, `lint`, `build` and `cover-run` line named one (observed 2026-11-27, method: every `Phase` line of the
//!   clone's `l7r-events/*.jsonl` counted by step and crate count);
//! - a red hook suite, named in the attempt's output by `make hooks-test`'s `HOOK TESTS FAILED: <job>` line, the job its guard's file
//!   name (`agent-model-hooks.sh`) or a shard of it (`agent-model-hooks.sh.3`; `tests/hooks/hookrun.sh`'s id); D6's spelling
//!   `test-<name>-hooks.sh` read too; one unit `hooks <guard file>`;
//! - a first-pass refusal row, each line under `make land`'s `Every refusal:` (the first pass refused before anything ran), one unit
//!   `first-pass <row>`.
//!
//! WHICH CHANGE A UNIT NAMES (D6 step 2): a crate's (each crate's of a several-crate unit) every change whose delta has a path under its directory (`dir/`, the slash kept,
//! so `rust/gate` is no prefix of `rust/gate2`; a crate's dependents are NOT counted - a change to `core` that reddens `lane`'s tests is
//! unplaced, the literal reading of "a crate by its directory", which phase 3's halving then places); a suite's, by its own file - the
//! guard's script of that name anywhere, `tests/hooks/test-<stem>.sh` and its shards - and its guard's sources
//! (`rust/guard/src/guards/<snake>*` and the shared crate's `rust/guard/shared/src/guards/<snake>*`, the stem's dashes as
//! underscores); a row's, by a path of the delta the row's text names, or by the tasks the row opens with (`T13, T14: ...`, the first
//! pass's own form for a task's refusal).
//!
//! THE VERDICT IN PHASE 2 ([`attribute`]): every red unit names exactly one change - those changes are placed, each with its units,
//! and ejected (`why` `red`); anything else - no unit read (a red the record does not hold), a unit no change touches, or a unit
//! several changes touch - is UNPLACED, and the whole batch is ejected as one repair entry (`why` `unplaced`). Several candidates are
//! read as unplaced where D6 would halve over them: the halving is phase 3's (T24, which replaces this one function); label: the
//! algorithmically easier route, the plan silent on several candidates before phase 3.

use std::fmt::Write as _;
use std::path::Path;

use serde_json::Value;

/// The Phase steps whose red names its crates (D6 step 2; R2): `format` is left out, as the plan leaves it.
pub const STEPS: [&str; 5] = ["test", "lint", "cover-build", "cover-run", "build"];
/// `make hooks-test`'s line for a red suite (the Makefile's `hooks-test` recipe).
const SUITE: &str = "HOOK TESTS FAILED: ";
/// `make land`'s first pass, refused before anything ran: its rows follow, two spaces in (`land.rs`).
const ROWS: &str = "Every refusal:";
/// A first-pass row's unit is cut to this many characters (the line `make lane-wait` prints stays one line).
const ROW_CUT: usize = 120;
/// A several-crate unit names this many of its crates and counts the rest, so the owed line stays one line (GUESS knob, a reading aid).
const NAMED: usize = 3;

/// One red unit and what it is.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Red {
    /// As the `run` line's `red` and a repair entry's `units` write it.
    pub unit: String,
    kind: Kind,
}

#[derive(Debug, Clone, PartialEq, Eq)]
enum Kind {
    /// The crates' directories one Phase line names, from the tree's root.
    Crates(Vec<String>),
    /// A guard's file name.
    Suite(String),
    /// A first-pass row, whole.
    Row(String),
}

/// A change as attribution reads it: the paths its delta touches and its tasks.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Change {
    pub files: Vec<String>,
    pub tasks: Vec<String>,
}

/// The verdict on a red attempt (the module's doc).
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Verdict {
    /// Each placed change, by its index among the changes, with its units, in the changes' order.
    Placed(Vec<(usize, Vec<String>)>),
    Unplaced,
}

/// The text with its ANSI color sequences (`ESC [ ... m`) taken out.
fn plain(text: &str) -> String {
    let mut out = String::with_capacity(text.len());
    let mut chars = text.chars();
    while let Some(c) = chars.next() {
        if c == '\u{1b}' {
            chars.by_ref().find(char::is_ascii_alphabetic);
        } else {
            out.push(c);
        }
    }
    out
}

/// A path's canonical form where it has one, else itself.
fn canon(p: &Path) -> std::path::PathBuf {
    std::fs::canonicalize(p).unwrap_or_else(|_| p.to_path_buf())
}

/// The red units of an attempt: its red Phase lines among `events`, inside `span` (`t0` and `t1` as the event log stamps them) and in
/// `tree`, and its red suites and first-pass rows in `output`; each unit once, in the order read.
#[must_use]
pub fn reds(events: &[Value], span: (&str, &str), tree: &Path, output: &str) -> Vec<Red> {
    let tree = canon(tree);
    let mut out: Vec<Red> = Vec::new();
    let mut add = |r: Red| {
        if !out.contains(&r) {
            out.push(r);
        }
    };
    for e in events {
        let step = e["step"].as_str().unwrap_or_default();
        let (t0, t1) = (
            e["t0"].as_str().unwrap_or_default(),
            e["t1"].as_str().unwrap_or_default(),
        );
        let inside = t0 >= span.0 && !t1.is_empty() && t1 <= span.1;
        let here = e["clone"]
            .as_str()
            .is_some_and(|c| canon(Path::new(c)) == tree);
        if e["ev"] != "Phase" || !STEPS.contains(&step) || e["code"] == 0 || !inside || !here {
            continue;
        }
        let crates: Vec<&str> = e["crates"]
            .as_array()
            .into_iter()
            .flatten()
            .filter_map(Value::as_str)
            .collect();
        if crates.is_empty() {
            continue;
        }
        let mut shown = crates[..crates.len().min(NAMED)].join(" ");
        if crates.len() > NAMED {
            let _ = write!(shown, " (+{} more)", crates.len() - NAMED);
        }
        add(Red {
            unit: format!("{shown} {step}"),
            kind: Kind::Crates(
                crates
                    .iter()
                    .map(|c| c.trim_end_matches('/').to_owned())
                    .collect(),
            ),
        });
    }
    let text = plain(output);
    let mut in_rows = false;
    for line in text.lines() {
        if let Some(job) = line.split_once(SUITE).map(|(_, j)| j) {
            let guard = suite_of(job.split_whitespace().next().unwrap_or_default());
            add(Red {
                unit: format!("hooks {guard}"),
                kind: Kind::Suite(guard),
            });
        }
        if line.contains(ROWS) {
            in_rows = true;
            continue;
        }
        match line.strip_prefix("  ").map(str::trim) {
            Some(row) if in_rows && !row.is_empty() => add(Red {
                unit: format!(
                    "first-pass {}",
                    row.chars().take(ROW_CUT).collect::<String>()
                ),
                kind: Kind::Row(row.to_owned()),
            }),
            _ => in_rows = false,
        }
    }
    out
}

/// A suite job's guard file: a shard's `.<k>` and D6's `test-` spelling taken off.
fn suite_of(job: &str) -> String {
    let job = job.strip_prefix("test-").unwrap_or(job);
    match job.rsplit_once('.') {
        Some((head, k)) if !k.is_empty() && k.chars().all(|c| c.is_ascii_digit()) => {
            head.to_owned()
        }
        _ => job.to_owned(),
    }
}

/// Whether `red` names a change of `files` and `tasks` (the module's doc).
fn touches(red: &Red, change: &Change) -> bool {
    match &red.kind {
        Kind::Crates(dirs) => dirs.iter().any(|d| {
            let dir = format!("{d}/");
            change.files.iter().any(|f| f.starts_with(&dir))
        }),
        Kind::Suite(guard) => {
            let stem = guard.strip_suffix(".sh").unwrap_or(guard);
            let test = format!("tests/hooks/test-{stem}.");
            let snake = stem.replace('-', "_");
            let sources = [
                format!("rust/guard/src/guards/{snake}"),
                format!("rust/guard/shared/src/guards/{snake}"),
            ];
            change.files.iter().any(|f| {
                Path::new(f)
                    .file_name()
                    .is_some_and(|n| n.to_string_lossy() == *guard)
                    || f.starts_with(&test)
                    || (stem.ends_with("-hooks")
                        && sources.iter().any(|s| f.starts_with(s.as_str())))
            })
        }
        Kind::Row(row) => {
            let named = row.split_once(": ").map_or(Vec::new(), |(head, _)| {
                head.split(", ").map(str::trim).collect::<Vec<_>>()
            });
            let by_task = !named.is_empty()
                && named.iter().all(|t| {
                    t.len() > 1 && t.starts_with('T') && t[1..].chars().all(|c| c.is_ascii_digit())
                })
                && named.iter().any(|t| change.tasks.iter().any(|c| c == t));
            by_task || change.files.iter().any(|f| row.contains(f.as_str()))
        }
    }
}

/// What a first pass's refusal names (461 T15's plan review, rounds 1 and 2).
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Refusal {
    /// No first-pass row among the units: the first pass did not refuse.
    None,
    /// The rows naming no change of the batch (a hold, a lock, a round no task of it owes): the runner stops, nothing ejected.
    Unnamed(Vec<String>),
    /// Every row names one change or more: the changes any row names, by their indices, in order.
    Named(Vec<usize>),
}

/// The first pass's refusal among `reds` over `changes` (the [`Refusal`] cases): a row naming no change stops the batch, though
/// another names one - nothing lands while it stands, and its named change is ejected on the resume once it clears.
#[must_use]
pub fn refusal(reds: &[Red], changes: &[Change]) -> Refusal {
    let rows: Vec<&Red> = reds
        .iter()
        .filter(|r| matches!(r.kind, Kind::Row(_)))
        .collect();
    if rows.is_empty() {
        return Refusal::None;
    }
    let unnamed: Vec<String> = rows
        .iter()
        .filter(|r| !changes.iter().any(|c| touches(r, c)))
        .map(|r| r.unit.clone())
        .collect();
    if !unnamed.is_empty() {
        return Refusal::Unnamed(unnamed);
    }
    Refusal::Named(
        (0..changes.len())
            .filter(|&i| rows.iter().any(|r| touches(r, &changes[i])))
            .collect(),
    )
}

/// The phase-2 verdict on `reds` over `changes` (the module's doc).
#[must_use]
pub fn attribute(reds: &[Red], changes: &[Change]) -> Verdict {
    let mut placed: Vec<(usize, Vec<String>)> = Vec::new();
    for red in reds {
        let names: Vec<usize> = (0..changes.len())
            .filter(|&i| touches(red, &changes[i]))
            .collect();
        let [one] = names[..] else {
            return Verdict::Unplaced;
        };
        match placed.iter_mut().find(|(i, _)| *i == one) {
            Some((_, units)) => units.push(red.unit.clone()),
            None => placed.push((one, vec![red.unit.clone()])),
        }
    }
    if placed.is_empty() {
        return Verdict::Unplaced;
    }
    placed.sort_by_key(|(i, _)| *i);
    Verdict::Placed(placed)
}

#[cfg(test)]
mod tests;
