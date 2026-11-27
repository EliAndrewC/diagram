//! What the report opens with (feature 451 T298): the window's table - in two parts since 451 T510, the tasks' side and the
//! landings', each its own denominator - one line a landed task, and the second
//! tier's section, one line a batch - before the per-task sections. On 2026-11-26 a day's report was 38 per-task tables, 2,294
//! lines, and the day's totals were summed from them by hand.

use std::collections::HashMap;
use std::fmt::Write as _;

use super::super::events::hhmm;
use super::book::{is_tier, Batch, Cell, Key, Ledger};
use super::cross::{self, Cross};
use super::{is_gm, landing_side, m, pct, sums, tables, total, Sides};

/// The window's categories over the cells `pick` takes, largest first.
fn folded(l: &Ledger, pick: &dyn Fn(&Key, &str) -> bool) -> Vec<(String, Cell)> {
    let mut cats: HashMap<&str, Cell> = HashMap::new();
    for ((_, cat, _), c) in l.cells.iter().filter(|((k, cat, _), _)| pick(k, cat)) {
        let e = cats.entry(cat).or_default();
        e.min += c.min;
        e.block += c.block;
    }
    let mut rows: Vec<(String, Cell)> = cats
        .into_iter()
        .map(|(k, v)| (k.to_owned(), v))
        .filter(|(_, v)| v.min + v.block > 0.0)
        .collect();
    rows.sort_by(|a, b| {
        (b.1.block + b.1.min)
            .total_cmp(&(a.1.block + a.1.min))
            .then(a.0.cmp(&b.0))
    });
    rows
}

/// One side's table: its rows, each a percentage of the side's own working time `of`.
fn side_table(out: &mut String, heading: &str, (rows, of): (&[(String, Cell)], Cell), name: &str) {
    let _ = write!(
        out,
        "## The window: {heading}\n\n| category | minutes | % of {name} | blocking | % of {name} |\n|---|---|---|---|---|\n"
    );
    for (cat, c) in rows {
        let _ = writeln!(
            out,
            "| {cat} | {} | {} | {} | {} |",
            m(c.min),
            pct(c.min, of.min),
            m(c.block),
            pct(c.block, of.block)
        );
    }
}

/// The window's table in two parts (451 T510, the GM 2026-11-27: "the denominators should just be totally separate except to the
/// degree that things in one category actually are blocking things in the other category"): the tasks' side - what is booked to a
/// task or to the session's own, and the minutes a task waited on a landing (`cross`) - and the landings' side - every batch's time
/// and every carry - each a percentage of its own working time; the GM's rows apart, of the whole, as before.
pub(super) fn window_table(out: &mut String, l: &Ledger, d: &Sides, cross: &Cross) {
    let tasks = folded(l, &|k, c| !landing_side(k, c) && !is_gm(c));
    side_table(out, "the tasks' side", (&tasks, d.tasks), "the tasks'");
    let _ = writeln!(
        out,
        "| a task waited on a landing (cross-blocking) | - | | {} | {} |\n\
         | the tasks' side, working (all but waiting on the GM) | {} | 100.0% | {} | 100.0% |\n\n{}",
        m(cross.both),
        pct(cross.both, d.tasks.block),
        m(d.tasks.min),
        m(d.tasks.block),
        cross::said(cross)
    );
    let landings = folded(l, &landing_side);
    side_table(
        out,
        "the landings' side (the second tier)",
        (&landings, d.landings),
        "the landings'",
    );
    let _ = writeln!(
        out,
        "| the landings' side, working | {} | 100.0% | {} | 100.0% |\n\n\
         (every batch landing's time, booked to no task - its section is below - and every carry into the clone; its blocking is the \
         session's clock, never a task's but where the line above counts one)\n",
        m(d.landings.min),
        m(d.landings.block)
    );
    out.push_str(
        "Waiting on the GM, apart from both sides:\n\n| category | minutes | % of the whole | blocking | % of the whole |\n|---|---|---|---|---|\n",
    );
    for (cat, c) in &folded(l, &|_, c| is_gm(c)) {
        let _ = writeln!(
            out,
            "| {cat} | {} | {} | {} | {} |",
            m(c.min),
            pct(c.min, d.whole.min),
            m(c.block),
            pct(c.block, d.whole.block)
        );
    }
    let _ = writeln!(
        out,
        "| the whole (both sides and the GM) | {} | | {} | |\n",
        m(d.whole.min),
        m(d.whole.block)
    );
}

/// Where a landed task's own table ends: its carry into the clone, else its landing's start.
fn ends(batches: &[Batch], key: &Key, landed: f64) -> String {
    let mine = |b: &&Batch| b.feature == key.0 && b.tasks.contains(&key.1);
    let from = batches
        .iter()
        .filter(mine)
        .map(|b| b.from(&key.1))
        .fold(landed, f64::min);
    if batches
        .iter()
        .filter(mine)
        .any(|b| b.carried.iter().any(|(t, _)| *t == key.1))
    {
        format!("its carry, {}", hhmm(from))
    } else {
        format!("its landing's start, {} (no carry found)", hhmm(from))
    }
}

/// One line a landed task: its builders' minutes from the event log, its whole minutes and blocking minutes, when it landed.
pub(super) fn task_lines(
    out: &mut String,
    whole: &Ledger,
    landed: &[(f64, Key)],
    batches: &[Batch],
) {
    out.push_str(
        "## The landed tasks, one line each\n\n| task | landed | builders | builder minutes | minutes | blocking | its own table ends at |\n|---|---|---|---|---|---|---|\n",
    );
    for (t, k) in landed {
        let all = total(&sums(whole, &|x| x == k).0);
        let (secs, n) = whole.builders.get(k).copied().unwrap_or_default();
        let _ = writeln!(
            out,
            "| {} {} | {} | {n} | {} | {} | {} | {} |",
            k.0,
            k.1,
            hhmm(*t),
            m(secs),
            m(all.min),
            m(all.block),
            ends(batches, k, *t)
        );
    }
    out.push_str(
        "\n(builder minutes are each builder's spans in the event log, each start to its stop, never its report's account - a resumed \
         builder's every span, the time it was stopped between them left out, its lines that run on after a stop with no start line \
         logged a span from the first of them, 451 T382; minutes and blocking are the task's whole time, read back \
         before the window, to where its own table ends)\n\n",
    );
}

/// A batch's failures and what each cost: each red attempt with the minutes to its re-run, an attempt still in flight named.
fn failures(b: &Batch) -> String {
    let mut out: Vec<String> = Vec::new();
    for (i, a) in b.attempts.iter().enumerate().filter(|(_, a)| !a.landed) {
        let ran = m(a.t1 - a.t0);
        out.push(if a.open {
            format!(
                "started {}, {ran} min, no end line (in flight, or stopped)",
                hhmm(a.t0)
            )
        } else {
            match b.attempts.get(i + 1) {
                Some(next) => format!(
                    "red at {} after {ran} min, re-run {} min later",
                    hhmm(a.t1),
                    m(next.t0 - a.t1)
                ),
                None => format!("red at {} after {ran} min, not re-run", hhmm(a.t1)),
            }
        });
    }
    if out.is_empty() {
        "none".to_owned()
    } else {
        out.join("; ")
    }
}

/// The second tier's section: one line a batch with an attempt in the window, its blocking on its own line, then its time by what
/// it was.
pub(super) fn second_tier(
    out: &mut String,
    l: &Ledger,
    batches: &[Batch],
    (lo, hi): (f64, f64),
    d: &Sides,
) {
    out.push_str(
        "## The second tier: each batch landing, booked to no task\n\n\
         | batch | landed | gate runs | re-runs | gate minutes | failures and their repair | minutes | blocking |\n|---|---|---|---|---|---|---|---|\n",
    );
    for b in batches
        .iter()
        .filter(|b| b.attempts.iter().any(|a| a.t1 >= lo && a.t0 <= hi))
    {
        let key = b.key();
        let c = total(&sums(l, &|x| *x == key).0);
        let n = b.attempts.len();
        let _ = writeln!(
            out,
            "| {} {} | {} | {n} | {} | {} | {} | {} | {} |",
            b.feature,
            b.tasks.join(" "),
            b.landed().map_or_else(|| "not landed".to_owned(), hhmm),
            n - 1,
            m(b.attempts.iter().fold(0.0, |s, a| s + a.gate)),
            failures(b),
            m(c.min),
            m(c.block)
        );
    }
    let (cats, targets) = sums(l, &is_tier);
    let tier = total(&cats);
    let _ = writeln!(
        out,
        "\nThe second tier's blocking: {} min, {} of the landings' side's working blocking (the rest of that side is the carries, \
         booked to the tasks they carried, whose own tables end there). Expected near zero - no new task waits on the gate: \
         a gate waited on beside a task's own work blocks nothing, and this counts a repair (the session's turns from a task's carry \
         to the landing, and what they waited on), a gate the session waited on alone, and a gate run in the foreground - only the \
         session's own work: its time stopped waiting on the GM is the GM's row (451 T403). A rise is not by itself a task's wait: \
         what a task waited on a landing is the tasks' side's cross-blocking row.\n",
        m(tier.block),
        pct(tier.block, d.landings.block)
    );
    if !cats.is_empty() {
        out.push_str("Its time by what it was, every batch together:\n\n");
        tables(out, &cats, &targets, d, true);
    }
}
