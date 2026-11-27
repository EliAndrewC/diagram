//! THE RUNS BEHIND A LANDED TASK'S COUNTS, listed under its tables (feature 451 T522 (c); the GM 2026-11-27, on T417's row: "these
//! numbers make me a little concerned about whether they actually reflect what is really happening"): each counted line - when, the
//! tree it ran in, its make target, its step, its crates, its seconds and what it was counted as - so a count can be checked by eye.
//! Printed always, in start order, under the task's own tables: a flag would leave the figure it explains unexplained by default.

use std::fmt::Write as _;

use super::super::events::fixed;
use super::super::where_time::columns::ran::{Kind, Ran, NOOP_BELOW_S};
use super::book::{Key, Ledger};
use super::iso_of;

/// What a line was counted as.
fn counted(r: &Ran) -> String {
    match r.kind {
        Kind::UnitTest => "unit-test run".to_owned(),
        Kind::Coverage => "coverage run".to_owned(),
        Kind::Compile if r.worked() => "compile".to_owned(),
        Kind::Compile => format!("compile, under {} s", fixed(NOOP_BELOW_S, 1)),
    }
}

/// The listing of `key`'s counted lines, nothing where it has none.
pub fn listing(out: &mut String, whole: &Ledger, key: &Key) {
    let Some(rans) = whole.ran.get(key).filter(|r| !r.is_empty()) else {
        return;
    };
    let mut rows: Vec<&Ran> = rans.iter().collect();
    rows.sort_by(|a, b| a.t0.total_cmp(&b.t0).then(a.tree.cmp(&b.tree)));
    let _ = write!(
        out,
        "Its counted lines (451 T522), the runs behind its unit-test runs, coverage runs and compiles, by start:\n\n\
         | start (UTC) | tree | make target | step | crates | seconds | counted as |\n|---|---|---|---|---|---|---|\n"
    );
    for r in rows {
        let at = iso_of(r.t0);
        let _ = writeln!(
            out,
            "| {} | {} | {} | {} | {} | {} | {} |",
            at.get(5..19).unwrap_or(&at),
            r.tree,
            r.make,
            r.step,
            r.crates,
            fixed(r.t1 - r.t0, 1),
            counted(r)
        );
    }
    out.push('\n');
}

#[cfg(test)]
#[path = "listed_tests.rs"]
mod tests;
