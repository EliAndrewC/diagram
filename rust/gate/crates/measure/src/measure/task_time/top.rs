//! What the report opens with (feature 451 T298): ONE window-wide table of every category, one line a landed task, and the second
//! tier's section, one line a batch - before the per-task sections. On 2026-11-26 a day's report was 38 per-task tables, 2,294
//! lines, and the day's totals were summed from them by hand.

use std::collections::HashMap;
use std::fmt::Write as _;

use super::super::events::hhmm;
use super::book::{is_tier, Batch, Cell, Key, Ledger, SECOND_TIER};
use super::{is_gm, m, pct, sums, tables, total, working};

/// The window's categories, every batch's time folded to the one second-tier category.
fn folded(l: &Ledger) -> Vec<(String, Cell)> {
    let mut cats: HashMap<&str, Cell> = HashMap::new();
    for ((key, cat, _), c) in &l.cells {
        let name = if is_tier(key) { SECOND_TIER } else { cat };
        let e = cats.entry(name).or_default();
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

/// The window's one table: every category's minutes and blocking minutes, each with its share of the window's working time (the
/// GM's rows their share of the whole, and outside every other row's denominator).
pub(super) fn window_table(out: &mut String, l: &Ledger) {
    let rows = folded(l);
    let (all, work) = (total(&rows), working(&rows));
    out.push_str(
        "## The window, every category\n\n| category | minutes | % of working | blocking | % of working |\n|---|---|---|---|---|\n",
    );
    for (cat, c) in &rows {
        let of = if is_gm(cat) { all } else { work };
        let _ = writeln!(
            out,
            "| {cat} | {} | {} | {} | {} |",
            m(c.min),
            pct(c.min, of.min),
            m(c.block),
            pct(c.block, of.block)
        );
    }
    let _ = writeln!(
        out,
        "| all | {} | | {} | |\n| working (all but waiting on the GM) | {} | 100.0% | {} | 100.0% |\n\n\
         (a GM row's % is of the whole; `{SECOND_TIER}` is every batch landing's time, booked to no task: its section is below)\n",
        m(all.min),
        m(all.block),
        m(work.min),
        m(work.block)
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
    (all, work): (Cell, Cell),
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
        "\nThe second tier's blocking: {} min, {} of the window's working blocking. Expected near zero - no new task waits on the gate: \
         a gate waited on beside a task's own work blocks nothing, and this counts a repair (the session's turns from a task's carry \
         to the landing, and what they waited on), a gate the session waited on alone, and a gate run in the foreground. A rise says \
         something has begun to wait on the gate.\n",
        m(tier.block),
        pct(tier.block, work.block)
    );
    if !cats.is_empty() {
        out.push_str("Its time by what it was, every batch together:\n\n");
        tables(out, &cats, &targets, (all, work));
    }
}
