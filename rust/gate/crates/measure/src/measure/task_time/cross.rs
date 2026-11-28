//! A TASK'S WAIT ON A LANDING (feature 451 T510; the GM 2026-11-27: "the denominators should just be totally separate except to the
//! degree that things in one category actually are blocking things in the other category"): the report's window is two sides, the
//! tasks' and the landings' (the second tier), each its own denominator, and this is the one figure that crosses - the minutes a
//! task's work waited because a landing held the session - booked into the tasks' side's blocking.
//!
//! WHY. Over 2026-11-27T02:00Z to 14:29Z the window's one table put the second tier at 568.3 of 680.0 working blocking minutes
//! (83.6%), every other row a percentage of the same total, while the pool trees were busy 93%, 98% and 83% of the window: the
//! landings' blocking is the session's own clock, and only part of it held a task back.
//!
//! THE SOURCES, each read from a record:
//! - A FREE POOL TREE NOT HANDED OUT WHILE A LANDING RAN (the pool's log, `builder-pool.log`, every clone's, [`super::held::holds`];
//!   the landings' spans, each attempt's `land` `end` line, `t0` to `t1`): each second of a landing's span, the trees standing free
//!   from a holder's release to the tree's next handout or, with none logged, the window's end, at most the open builder places
//!   (`L7R_BUILDERS`, default 3, less the trees held then). A span with no later handout counts to the window's end (461 T33): ended
//!   at the next handout alone, a closed window's figure grew as later handouts reached the log (2026-11-27T02:00Z to 14:29Z read
//!   32.3 min at 14:40Z and 53.7 at 17:55Z), so a tree freed and never retaken counts too, held under the places left open.
//! - A HANDOUT REFUSED WHILE ITS TASK'S DONE COMMIT WAS NOT CARRIED (451 T398: `make builder-tree` refuses it and writes nothing to the
//!   pool's log): a main session's `make builder-tree` or `make builder-brief` that failed (its `PostToolUseFailure` line), its
//!   task (the command's `T=`) with a `done` row in the pool's log before it and no carry of it since, from the refusal to the task's
//!   next handout or carry, else the window's end.
//!
//! The pool's log is one a clone (its worktrees share the clone's git directory), so its holds and the clone's landings are one
//! pool's; a second clone's log, read beside it, is counted the same way.
//!
//! Counted once a second, the larger of the two there (a refused closing half and the tree it would take are one wait).
//!
//! NOT IN THE RECORDS, said on the report's line: whether the queue held a READY entry while a tree stood free (its states are computed
//! when asked and never logged, so the first source is an upper bound: a free tree is taken to have had work waiting); a
//! refusal's reason (only the transcript's tool result says it); a builder's resume held by a gate (no record ties a message's
//! delivery to a landing); and a builder's wait on a build slot a gate held, booked on the tasks' side already as `waiting on a build
//! slot`, so not counted again.

use std::collections::HashSet;
use std::path::PathBuf;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_shared::guards::event_log_hooks::common_git_dir;
use serde_json::Value;

use super::super::events::{is, or_s, re, ts, Event};
use super::super::where_time::columns::Runs;
use super::book::Batch;
use super::held::{holder, Hold};
use super::tiers::{Carry, Take};

static TASK: LazyLock<Regex> = LazyLock::new(|| re(r#"\sT=["']?([^\s"',]+)"#));

/// The open builder places when `L7R_BUILDERS` names none (the pool's own default).
pub const CAP: usize = 3;

/// The figure and its sources, in seconds.
#[derive(Debug, Clone, Copy, PartialEq, Default)]
pub struct Cross {
    /// A free pool tree not handed out while a landing ran.
    pub idle: f64,
    /// A handout refused while its task's done commit was not carried.
    pub refused: f64,
    /// How many handouts were refused so.
    pub n_refused: usize,
    /// The row's figure: each second once, the larger source there.
    pub both: f64,
    /// The builder places read.
    pub cap: usize,
    /// Pool trees held, each second once a tree: the window's tree-seconds (451 T532).
    pub held: f64,
}

/// One task's done commits: when, and the tasks the `done` row names.
pub type Done = (f64, Vec<String>);

/// Every `done` row of the pool logs of `bases`, each log read once.
#[must_use]
pub fn dones(bases: &[PathBuf]) -> Vec<Done> {
    let mut seen: Vec<PathBuf> = Vec::new();
    let mut out = Vec::new();
    for base in bases {
        let log = common_git_dir(base).join("builder-pool.log");
        let path = std::fs::canonicalize(&log).unwrap_or(log);
        if seen.contains(&path) {
            continue;
        }
        let text = std::fs::read_to_string(&path).unwrap_or_default();
        seen.push(path);
        for v in text
            .lines()
            .filter_map(|l| serde_json::from_str::<Value>(l).ok())
        {
            let field = |k: &str| v.get(k).and_then(Value::as_str).unwrap_or("").to_owned();
            if let (true, Ok(at)) = (field("event") == "done", ts(&field("utc"))) {
                out.push((at, holder(&field("detail")).1));
            }
        }
    }
    out
}

/// What the refusals are read from.
pub struct Records<'a> {
    /// The window's runs.
    pub runs: &'a Runs,
    /// The stream's lines (a failed call's `PostToolUseFailure`).
    pub stream: &'a [Event],
    /// Each call's command.
    pub commands: &'a std::collections::HashMap<String, String>,
    /// The pool's `done` rows.
    pub dones: &'a [Done],
    /// The pool's handouts.
    pub takes: &'a [Take],
    /// The carries found.
    pub carried: &'a [Carry],
}

/// Each refused handout's wait, `(from, to)` (the module's doc, its second source), `hi` the window's end.
#[must_use]
pub fn refusals(r: &Records, hi: f64) -> Vec<(f64, f64)> {
    let failed: HashSet<String> = r
        .stream
        .iter()
        .filter(|e| is(e, "ev", "PostToolUseFailure"))
        .map(|e| or_s(e, "id"))
        .collect();
    let mut out = Vec::new();
    for run in r.runs.runs.iter().filter(|x| {
        x.by.is_empty()
            && failed.contains(&x.id)
            && x.makes
                .iter()
                .any(|m| m == "builder-tree" || m == "builder-brief")
    }) {
        let command = r.commands.get(&run.id).map_or("", String::as_str);
        let Ok(Some(c)) = TASK.captures(command) else {
            continue;
        };
        let task = c[1].to_owned();
        let names = |d: &str| holder(d).1.contains(&task);
        let carried = |from: f64, to: f64| {
            r.carried
                .iter()
                .any(|(_, t, d)| names(d) && from <= *t && *t <= to)
        };
        let Some(done) = r
            .dones
            .iter()
            .filter(|(t, tasks)| *t <= run.t0 && tasks.contains(&task))
            .map(|(t, _)| *t)
            .reduce(f64::max)
        else {
            continue;
        };
        if carried(done, run.t0) {
            continue;
        }
        let next = r
            .takes
            .iter()
            .filter(|(t, _, d)| *t > run.t0 && names(d))
            .map(|(t, _, _)| *t)
            .chain(
                r.carried
                    .iter()
                    .filter(|(_, t, d)| *t > run.t0 && names(d))
                    .map(|(_, t, _)| *t),
            )
            .fold(hi, f64::min);
        out.push((run.t0, next));
    }
    out
}

/// Each tree's free spans, `(from, to)`: from a release to the tree's next handout, or open (`to` infinite, clipped at the window's
/// end by [`measure`]) where none follows (461 T33).
fn gaps(holds: &[Hold]) -> Vec<(f64, f64)> {
    let mut out = Vec::new();
    let mut trees: Vec<&str> = holds.iter().map(|h| h.tree.as_str()).collect();
    trees.sort_unstable();
    trees.dedup();
    for tree in trees {
        let mut mine: Vec<&Hold> = holds.iter().filter(|h| h.tree == tree).collect();
        mine.sort_by(|a, b| a.from.total_cmp(&b.from));
        for (i, h) in mine.iter().enumerate() {
            let next = mine.get(i + 1).map_or(f64::INFINITY, |n| n.from);
            if h.until.is_finite() && h.until < next {
                out.push((h.until, next));
            }
        }
    }
    out
}

/// The figure (the module's doc) over the window `(lo, hi)`, `cap` the builder places.
#[must_use]
pub fn measure(
    holds: &[Hold],
    batches: &[Batch],
    refused: &[(f64, f64)],
    (lo, hi): (f64, f64),
    cap: usize,
) -> Cross {
    let free = gaps(holds);
    let landings: Vec<(f64, f64)> = batches
        .iter()
        .flat_map(|b| b.attempts.iter().map(|a| (a.t0, a.t1)))
        .collect();
    let mut cuts: Vec<f64> = vec![lo, hi];
    for (x, y) in free.iter().chain(&landings).chain(refused) {
        cuts.extend([*x, *y]);
    }
    cuts.extend(holds.iter().flat_map(|h| [h.from, h.until]));
    cuts.retain(|t| t.is_finite() && lo <= *t && *t <= hi);
    cuts.sort_by(f64::total_cmp);
    cuts.dedup();
    let inside = |s: &[(f64, f64)], t: f64| s.iter().filter(|(x, y)| *x <= t && t < *y).count();
    let mut out = Cross {
        n_refused: refused.len(),
        cap,
        ..Cross::default()
    };
    for w in cuts.windows(2) {
        let (mid, span) = (f64::midpoint(w[0], w[1]), w[1] - w[0]);
        let held = holds
            .iter()
            .filter(|h| h.from <= mid && mid < h.until)
            .count();
        let idle = if inside(&landings, mid) > 0 {
            inside(&free, mid).min(cap.saturating_sub(held))
        } else {
            0
        };
        let refusing = inside(refused, mid);
        #[expect(clippy::cast_precision_loss, reason = "a count of trees or tasks")]
        let (trees, tasks, most) = (idle as f64, refusing as f64, idle.max(refusing) as f64);
        out.idle += trees * span;
        out.refused += tasks * span;
        out.both += most * span;
        #[expect(clippy::cast_precision_loss, reason = "a count of trees")]
        let trees = held as f64;
        out.held += trees * span;
    }
    out
}

/// The builder places: `L7R_BUILDERS` where it names a number, else [`CAP`].
#[must_use]
pub fn cap_of(env: Option<&str>) -> usize {
    env.and_then(|v| v.trim().parse().ok()).unwrap_or(CAP)
}

/// The report's paragraph under the tasks' side.
#[must_use]
pub fn said(c: &Cross) -> String {
    let m = super::m;
    format!(
        "A task waited on a landing (cross-blocking): {} min, in the tasks' side's blocking. Counted once a second, the larger of its \
         two sources there: a free pool tree not handed out while a landing ran: {} min (a tree free from a release to its next \
         handout or the window's end, during a landing's span - its `land` end line's start to its end - while fewer than {} trees were held, \
         `L7R_BUILDERS`; the pool's log `builder-pool.log` and the event log); a handout refused while its task's done commit was not \
         carried: {} min ({} refused) (a main session's failed `make builder-tree` or `make builder-brief` whose task has a `done` \
         row in the pool's log and no carry since, to its next handout or carry). Not in the records: whether the queue held a READY \
         entry while a tree stood free (its states are never logged, so the first source is an upper bound: a free tree is taken to \
         have had work waiting); a refusal's reason (only the transcript's tool result says it); a builder's resume held by a \
         gate; and a builder's wait on a build slot a gate held, booked on the tasks' side already as `waiting on a build slot`, so \
         not counted again (451 T510).\n",
        m(c.both),
        m(c.idle),
        c.cap,
        m(c.refused),
        c.n_refused
    )
}

#[cfg(test)]
#[path = "cross_unit_tests.rs"]
mod tests;
