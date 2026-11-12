//! The review ledger's measured table and what one review run cost (features 294, 371, 375; ported from `scripts/reviews/ledger_lint.py`
//! and `review_cost.py` by feature 449 T83, `ask:449-T83-scope`).
//!
//! WHY (feature 294, spec US7: "a review row without cost, class or check is refused at commit"). The ledger answered "is the review
//! pulling its weight" by impression: 7 of 133 settlement-review rows recorded a wall time, none a token count, and the "author had
//! missed?" column went empty from 2026-09-27 (research R0). From feature 294 on a review pass is a row of the MEASURED table
//! (`MEASURED_HEADING`), whose cells a script can total (`make review-census`): the check that ran, the finding's class, and the run's
//! wall time and tokens copied from `make review-cost AGENT=<id>` (`cost`).
//!
//! WHY HERE, IN THE GUARD (feature 449 T83, the port's one decision the ruling left open): the guards log every check's pass with its cost
//! cells (`checks::passes`), refuse a commit of a short row (`ledger_hooks`) and read a review's rows (`escalation_hooks`), and the guard
//! crate cannot depend on the gate's. One implementation (FR-003) therefore lives here, the guards call it in process, and the gate's
//! `l7r-gate reviews ledger-lint`, `review-cost` and `ledger-owed` build on it, as T89 reused the guard's `at_rev`.

pub mod cost;

use std::sync::LazyLock;

use fancy_regex::Regex;

use crate::shared::checks::reply::py_lines;
use crate::shared::py_text::{repr, strip};

/// The measured table's heading: the rows under it, up to the next `## `, are the ones a script totals.
pub const MEASURED_HEADING: &str = "## Review checks, measured (feature 294 on)";
/// The checks a row may name - the five map reviews (feature 294's occasions) and the record and plan checks the ledger also logs:
/// `intro-check` (feature 311), `impl-drift` (feature 316), `work-budget` (feature 443 T05), and every agent that judges the work
/// (feature 371, spec round 2: the three modal checks and `source-filter`).
pub const CHECKS: [&str; 23] = [
    "building-review",
    "entry-drift",
    "escalation-check",
    "fix-check",
    "glyph-check",
    "impl-drift",
    "intro-check",
    "modal-depiction",
    "modal-form",
    "modal-research",
    "perf-audit",
    "quote-check",
    "record-format",
    "record-style",
    "settlement-review",
    "size-audit",
    "source-applicability",
    "source-filter",
    "source-reader",
    "spec-fidelity",
    "spec-fidelity-verify",
    "translation-check",
    "work-budget",
];
/// A finding's class, in the sorted order the refusal lists them.
const CLASSES: [&str; 4] = ["geometric", "judgment", "nothing", "paperwork"];
const MISSED: [&str; 3] = ["yes", "no", "-"];
/// The table's columns, in order.
pub const COLUMNS: [&str; 10] = [
    "date",
    "check",
    "subject",
    "verdict",
    "finding",
    "class",
    "author missed?",
    "acted on",
    "wall",
    "tokens",
];
/// Feature 375 FR-007: a row written from the rule's day on says in its `acted on` whether its finding is disposed or left for the GM.
const RULE_FROM: &str = "2026-10-11";

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static WALL: LazyLock<Regex> = LazyLock::new(|| re(r"^\d+ s$"));
static TOKENS: LazyLock<Regex> = LazyLock::new(|| re(r"^\d+k in \(\d+k cached\) / [\d.]+k out$"));
/// Feature 375 FR-007: what a row's `acted on` says - DISPOSED (fixed, verified, accepted with a reason, filed as a row, or nothing
/// because nothing was found) or OPEN (left for the GM). Only an open finding owes `escalation-check`.
static DISPOSED: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(?i)\b(fix|fixed|rewritten|reworded|amended|applied|verified|accepted|filed|found row|redrawn|recorded|corrected|retired|moved|withdrawn|answered)\b",
    )
});
static OPEN: LazyLock<Regex> = LazyLock::new(|| re(r"\b(GM|held|escalat\w*|open|pending)\b"));
static CLEAN: LazyLock<Regex> =
    LazyLock::new(|| re(r"^(PASS|CLEAR|FAITHFUL|IN-STEP|INTRO-OK|NO-INTRO-NEEDED|clean)\b"));

fn hit(pattern: &Regex, text: &str) -> bool {
    pattern.is_match(text).unwrap_or(false)
}

/// A whole row's cell under `column`; "" for a column the table does not have.
#[must_use]
pub fn cell<'a>(cells: &'a [String], column: &str) -> &'a str {
    COLUMNS
        .iter()
        .position(|c| *c == column)
        .and_then(|i| cells.get(i))
        .map_or("", String::as_str)
}

/// True when a review row's findings are all disposed, false when one is left for the GM, none when the words say neither (`disposed`).
#[must_use]
pub fn disposed(cells: &[String]) -> Option<bool> {
    let acted = strip(cell(cells, "acted on"));
    let none = |s: &str| s.is_empty() || s == "-";
    if hit(&OPEN, acted) || none(acted) {
        return Some(none(acted) && none(cell(cells, "finding")));
    }
    if acted.to_lowercase() == "nothing" {
        return Some(none(cell(cells, "finding")) || hit(&CLEAN, cell(cells, "verdict")));
    }
    hit(&DISPOSED, acted).then_some(true)
}

/// (line number, cells) of every data row under the measured table's heading (`measured_rows`).
#[must_use]
pub fn measured_rows(text: &str) -> Vec<(usize, Vec<String>)> {
    let lines = py_lines(text);
    let Some(start) = lines.iter().position(|l| strip(l) == MEASURED_HEADING) else {
        return Vec::new();
    };
    let mut out = Vec::new();
    for (i, line) in lines.iter().enumerate().skip(start + 1) {
        if line.starts_with("## ") {
            break;
        }
        if !line.starts_with("| ")
            || strip(&line.replace('|', ""))
                .chars()
                .all(|c| c == '-' || c == ' ')
        {
            continue;
        }
        let cells: Vec<String> = strip(line)
            .trim_matches('|')
            .split('|')
            .map(|c| strip(c).to_owned())
            .collect();
        if cells[0] == "date" {
            continue;
        }
        out.push((i + 1, cells));
    }
    out
}

/// Each measured row short of a cell, by line (`problems`).
#[must_use]
pub fn problems(text: &str) -> Vec<String> {
    let mut out = Vec::new();
    for (n, cells) in measured_rows(text) {
        if cells.len() != COLUMNS.len() {
            out.push(format!(
                "line {n}: {} cells, the table has {} ({})",
                cells.len(),
                COLUMNS.len(),
                COLUMNS.join(" | ")
            ));
            continue;
        }
        let at = |c: &str| cell(&cells, c);
        if !CHECKS.contains(&at("check")) {
            out.push(format!(
                "line {n}: check {} is none of the checks this ledger logs",
                repr(at("check"))
            ));
        }
        if !CLASSES.contains(&at("class")) {
            out.push(format!(
                "line {n}: class {} - one of {}",
                repr(at("class")),
                CLASSES.join(", ")
            ));
        }
        if !MISSED.contains(&at("author missed?")) {
            out.push(format!(
                "line {n}: author missed? {} - yes, no or -",
                repr(at("author missed?"))
            ));
        }
        if at("date") >= RULE_FROM && disposed(&cells).is_none() {
            out.push(format!("line {n}: acted on {} - say fixed, verified, accepted (why), filed as a row, or left for the GM (feature 375)", repr(at("acted on"))));
        }
        if !hit(&WALL, at("wall")) || !hit(&TOKENS, at("tokens")) {
            out.push(format!(
                "line {n}: the cost cells are not `make review-cost AGENT=<id>`'s ({} | {})",
                repr(at("wall")),
                repr(at("tokens"))
            ));
        }
    }
    out
}

/// Whether every row of `check` among the whole rows after the first `from` (`int(from or 0)`, a negative one counted from the end as a
/// slice counts) disposes of its findings, and there is at least one: the escalation guard's question of a review it armed (feature 375).
/// A `from` `int()` refuses answers no, as the Python's raise did.
#[must_use]
pub fn disposed_since(text: &str, check: &str, from: &str) -> bool {
    let Some(from) = (if from.is_empty() {
        Some(0)
    } else {
        cost::int_text(from)
    }) else {
        return false;
    };
    let rows = measured_rows(text);
    let len = i64::try_from(rows.len()).unwrap_or(i64::MAX);
    let skip = if from < 0 { (len + from).max(0) } else { from };
    let mine: Vec<Vec<String>> = rows
        .into_iter()
        .skip(usize::try_from(skip).unwrap_or(usize::MAX))
        .map(|(_, cells)| cells)
        .filter(|cells| cells.len() == COLUMNS.len() && cell(cells, "check") == check)
        .collect();
    !mine.is_empty() && mine.iter().all(|cells| disposed(cells) == Some(true))
}

#[cfg(test)]
mod tests;
