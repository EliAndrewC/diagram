//! THE RUNS BEHIND A TASK'S COUNTS (feature 451 T522; the GM 2026-11-27, on T417's row of 19 compiles and 28 test runs: "I would have
//! expected the number of compiler runs to actually be strictly higher than the number of test runs ... does that mean that the
//! compiler is actually being invoked many more times than what is reflected in these numbers?"), and the tie of every `Phase` line
//! to the Bash run that holds it ([`tie`], moved here from `columns.rs` with them).
//!
//! WHAT IS COUNTED. Until T522 a task's "compiles" were its runs' `build` and `cover-build` lines and its "test runs" its `test`,
//! `cover-run`, `make quick` and preflight lines - the lines its minutes are booked by (`columns::category`). So a clippy `lint` pass
//! (one a crate, 9,507 in the 451 log) and a pool tree's `prewarm` (2,914) compiled and were not counted, a coverage run was counted a
//! test run, and a `make quick` line - written by `make task-add`'s own check too, 0 to 1 s each, nine of T417's 28 - was a test run
//! (observed 2026-11-27, method: the 451 log's `Phase` lines by `src`/`step`, and T417's rows of `make task-time
//! SINCE=2026-11-27T03:30:00Z UNTIL=2026-11-27T12:00:00Z`). Now [`kind`] counts every compiler invocation a compile - `build`,
//! `cover-build`, each `lint` pass and each `prewarm` - a unit-test binary's run (`test`) apart from a coverage run (`cover-run`), and
//! no other line: a `make quick` or preflight line holds the test lines of its own cargo calls, so counting it too counted twice.
//! The MINUTES are untouched: a lint's and a pre-warm's seconds stay where they were booked (T316: a pre-warm is no call's compile).
//!
//! WHICH COMPILED SOMETHING. A `Phase` line says nothing of what cargo did, so a cargo call that found every crate fresh (a no-op
//! check) is told by its span alone: one under [`NOOP_BELOW_S`] is counted a compile and not one that did work. Why that line: a
//! crate's no-op floor in the 451 log is 0.03 to 0.15 s for `build`, `cover-build` and `lint` (each crate's fastest line), and 0.5 s
//! for `prewarm`, whose span is polled in 0.5 s steps; a single crate's real rebuild is past 1 s (the p10 of `rust/guard/shared`'s
//! builds 1.51 s, of `rust/gate/crates/measure`'s 1.27 s), observed 2026-11-27, method: each (step, crates) pair's fastest, p10 and
//! median span over the 451 log's lines, pairs with 10 or more lines. A GUESS knob (`dev/audits/compile-noop-threshold.md`): a
//! cargo call that rebuilt one tiny crate in under a second is miscounted a no-op. The exact answer is the writer's: `kept.rs`'s
//! builds already read cargo's `--message-format=json`, whose `compiler-artifact` messages carry `fresh`, and a lint's clippy output
//! names each `Checking` crate - filed as its own task, the field this reader takes first where a line carries it.

use serde_json::Value;

use super::super::super::events::{cmp_f, get, is, or_s, ts, Event, Raised};
use super::super::task_at;
use super::{category, scratch_wait, Parts, Run, Runs, Split, SCRATCH};

/// A compile line's span under which it is counted a no-op check: a GUESS knob, the module's doc (feature 451 T522).
pub const NOOP_BELOW_S: f64 = 1.0;

/// A pool tree's pre-warm step (feature 451 T316, `rustc/prewarm.rs`): held by no Bash run, so counted under its line's own task.
pub const PREWARM: &str = "prewarm";

/// What a counted line is.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Kind {
    /// A compiler invocation: `build`, `cover-build`, a `lint` pass, a `prewarm`.
    Compile,
    /// A unit-test binary's run: `test`.
    UnitTest,
    /// A coverage run: `cover-run`.
    Coverage,
}

/// The kind of a `Phase` line counted beside a task's minutes, None for one not counted (the module's doc).
#[must_use]
pub fn kind(p: &Event) -> Option<Kind> {
    if !is(p, "src", "rust") {
        return None;
    }
    match or_s(p, "step").as_str() {
        "build" | "cover-build" | "lint" | PREWARM => Some(Kind::Compile),
        "test" => Some(Kind::UnitTest),
        "cover-run" => Some(Kind::Coverage),
        _ => None,
    }
}

/// One counted line: what the per-task listing prints.
#[derive(Debug, Clone, PartialEq)]
pub struct Ran {
    /// Its kind.
    pub kind: Kind,
    /// Its step (`build`, `lint`, `test` ...).
    pub step: String,
    /// Its span.
    pub t0: f64,
    /// Its end.
    pub t1: f64,
    /// The tree it ran in, its directory's name.
    pub tree: String,
    /// The make target its line names.
    pub make: String,
    /// Its crates, by their directories, joined with spaces.
    pub crates: String,
    /// (its log's feature, its own task): the key a pre-warm is counted under, held by no run.
    pub key: (String, String),
    /// The writer's word on whether cargo compiled anything, where its line carries one (`compiled`, a count of crates built).
    pub said: Option<bool>,
}

impl Ran {
    /// The line read, of kind `kind` over `(t0, t1)`.
    #[must_use]
    pub fn of(p: &Event, kind: Kind, (t0, t1): (f64, f64)) -> Self {
        let crates = match get(p, "crates") {
            Value::Array(a) => a
                .iter()
                .filter_map(Value::as_str)
                .collect::<Vec<_>>()
                .join(" "),
            _ => String::new(),
        };
        let tree = or_s(p, "clone");
        let task = or_s(p, "task");
        Self {
            kind,
            step: or_s(p, "step"),
            t0,
            t1,
            tree: tree.rsplit('/').next().unwrap_or_default().to_owned(),
            make: or_s(p, "make"),
            crates,
            key: (
                or_s(p, "feature"),
                if task.is_empty() {
                    "-".to_owned()
                } else {
                    task
                },
            ),
            said: get(p, "compiled").as_u64().map(|n| n > 0),
        }
    }

    /// Whether it did work: a test or coverage run always; a compile where the writer says so, else where it ran
    /// [`NOOP_BELOW_S`] or more.
    #[must_use]
    pub fn worked(&self) -> bool {
        self.kind != Kind::Compile || self.said.unwrap_or(self.t1 - self.t0 >= NOOP_BELOW_S)
    }
}

/// A task's counts: each kind's lines and their seconds, and the compiles that did work.
#[derive(Debug, Default, Clone, Copy, PartialEq)]
pub struct Counts {
    /// Unit-test binary runs and their seconds.
    pub unit: (usize, f64),
    /// Coverage runs and their seconds.
    pub cover: (usize, f64),
    /// Compiles and their seconds.
    pub compile: (usize, f64),
    /// Of the compiles, those that did work ([`Ran::worked`]).
    pub worked: usize,
}

/// The counts of `rans`.
#[must_use]
pub fn counts<'a>(rans: impl IntoIterator<Item = &'a Ran>) -> Counts {
    let mut c = Counts::default();
    for r in rans {
        let slot = match r.kind {
            Kind::Compile => &mut c.compile,
            Kind::UnitTest => &mut c.unit,
            Kind::Coverage => &mut c.cover,
        };
        slot.0 += 1;
        slot.1 += r.t1 - r.t0;
        c.worked += usize::from(r.kind == Kind::Compile && r.worked());
    }
    c
}

/// Each phase of `aside` with a [`category`] or a [`kind`] tied to its run (the module's doc of `columns.rs`), the loose counted; a
/// page session's booked by its task, a pre-warm's counted by its own.
///
/// A POOL TREE'S LINE IS ITS HOLDER'S (feature 451 T522 (d)): every builder shares its session's id, so a line written in one pool tree
/// fell inside another builder's run of the same make target, and the tie took the target alone where no run of the line's task held
/// it. T417's background `make format` run (03:58:17 to 04:00:58Z on 2026-11-27, `makes` `format builder-checks`) and its `make
/// rust-test` runs took T419's `rust-test` lines from `diagram-backlog-t271` and T314's from the session clone; so a line
/// [`super::super::super::task_time::held::retask`] found held (its `held_for`, the holder's tasks) ties only to a run of one of them.
///
/// # Errors
///
/// A `Phase` line's `t0`/`t1` the reader cannot read.
pub(super) fn tie(
    out: &mut Runs,
    aside: &[Event],
    starts: &[(f64, String)],
    end: f64,
) -> Result<(), Raised> {
    let mut held: Vec<Parts> = vec![Vec::new(); out.runs.len()];
    let mut rans: Vec<Vec<Ran>> = vec![Vec::new(); out.runs.len()];
    for p in aside.iter().filter(|p| is(p, "ev", "Phase")) {
        let scratch = scratch_wait(p);
        let col = if scratch { Some(SCRATCH) } else { category(p) };
        let counted = kind(p);
        if col.is_none() && counted.is_none() {
            continue;
        }
        let span = |k: &str| match get(p, k) {
            Value::String(t) => ts(t),
            _ => Err(format!("TypeError: a Phase line's {k} is no text")),
        };
        let (a, b) = (span("t0")?, span("t1")?);
        if a >= end {
            // after the window: the logs are read to their end, its runs cut at the window's
            continue;
        }
        if scratch {
            out.scratch.push((a, b));
        }
        let (make, task) = (or_s(p, "make"), or_s(p, "task"));
        if let (Some(col), true) = (col, is(p, "src", "page-session")) {
            let task = if task.is_empty() {
                task_at(starts, a)
            } else {
                task
            };
            out.detached.push((task, col, b.min(end) - a));
            continue;
        }
        let ran = counted.map(|k| Ran::of(p, k, (a, b)));
        if is(p, "step", PREWARM) {
            out.prewarm.extend(ran);
            continue;
        }
        let holders: Option<Vec<&str>> = match get(p, "held_for") {
            Value::Array(t) => Some(t.iter().filter_map(Value::as_str).collect()),
            _ => None,
        };
        let (same_make, same_task) = (
            |r: &Run| make.is_empty() || r.makes.contains(&make),
            |r: &Run| !task.is_empty() && r.task == task,
        );
        let holder = |r: &Run| {
            holders
                .as_ref()
                .is_none_or(|h| h.contains(&r.task.as_str()))
        };
        let fits = |r: &&Run| {
            r.sid == or_s(p, "sid")
                && (same_make(r) || same_task(r))
                && holder(r)
                && r.t0 <= a
                && b <= r.t1
        };
        let best = out
            .runs
            .iter()
            .enumerate()
            .filter(|(_, r)| fits(r))
            .max_by(|(_, x), (_, y)| {
                (same_make(x), same_task(x))
                    .cmp(&(same_make(y), same_task(y)))
                    .then(cmp_f(x.t0, y.t0))
            })
            .map(|(i, _)| i);
        match (best, col) {
            (Some(i), _) => {
                if let Some(col) = col {
                    held[i].push((col, vec![(a, b)]));
                }
                rans[i].extend(ran);
            }
            (None, Some(_)) if !scratch => {
                out.loose.0 += 1;
                out.loose.1 += b - a;
            }
            _ => {}
        }
    }
    for ((r, spans), ran) in out.runs.iter_mut().zip(held).zip(rans) {
        r.split = Split {
            ran,
            ..Split::of(&spans)
        };
    }
    Ok(())
}

#[cfg(test)]
#[path = "ran_tests.rs"]
mod tests;
