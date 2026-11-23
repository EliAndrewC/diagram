//! Which owed units a new review round owes nothing (feature 451 T199; the GM 2026-11-23, "check whether there are any other gaps
//! like this"; the gap audit's item 11, T188's rule reaching building-review): a unit whose last verdict STANDS is named answered by
//! `make verify` (`scripts/gates/review-tree.sh`) and left out of the dispatch count.
//!
//! A verdict stands where it is a PASS or NEEDS-WORK carried to its sheet as the sheet reads now ([`super::carried`], 451 T176: the
//! drawing and notes hash as the review read them) and every finding it raised and `make review-accept` did not record as left is minor
//! ([`MINOR`]). A fixed error or questionable finding owes a round even on an unchanged sheet (its fix may be in the docs, as round 2's
//! `ochiba-roundtrip-test` E1 was, 2026-11-23); a finding of no severity, or of one this table does not know, owes one too (fail closed).
//!
//! WHY, measured 2026-11-23 over the 66 building-review rounds the session transcripts hold (`UNIT=building-review--` in a subagent's
//! log): 60 later rounds; 12 followed a round whose open findings were only nitpick or outside. Of the 7 whose two prompts name review
//! trees, 3 rounds' sheets moved, each for a new task's layout change (T352/T367, T392), and 4 sheets were byte-identical between the
//! two trees (ochiba-magistracy 13:26 and 16:09, ubame-magistracy 13:26, hayakawa-magistracy 16:05) - dispatched only because `make
//! verify` told the builder to dispatch every owed unit, though each verdict was carried. 0 of the 7 attributable were owed by a nitpick
//! fixed on the sheet alone, and 5 of the 12 are unknown (that case is `scoped.rs`'s, by the GM's rule, not a measured saving). The
//! measured cost is at the dispatch: 4 of 60 rounds, about 150-340 s and 0.5-1.3M tokens each (the ledger's rows).
//!
//! Research: a standing verdict owes no round - NONE: review bookkeeping, no map decision

use std::path::Path;

use super::{
    accepted_ids, carried, latest_verdict, raised_findings, round_key, text_of, unit_content_key,
};

/// The severities whose finding, fixed, owes no new round: a nitpick (building-review's wording or small finding, T188's wording
/// class), an `outside` finding (on a part the occasion did not change, filed, never the verdict's), a `confirmation` (an earlier
/// round's finding confirmed fixed).
pub const MINOR: [&str; 3] = ["nitpick", "outside", "confirmation"];

/// Whether `unit`'s last verdict stands on its sheet as the sheet reads now, so a round owes nothing.
#[must_use]
pub fn stands(clone: &Path, unit: &str) -> bool {
    let Some(v) = latest_verdict(clone, unit) else {
        return false;
    };
    let left = accepted_ids(clone, unit, &round_key(&v));
    raised_findings(&v).iter().all(|f| {
        MINOR.contains(&text_of(f, "severity", "").as_str())
            || left.contains(&text_of(f, "id", "None"))
    }) && carried(&v, || unit_content_key(clone, unit))
}

/// The units of `units` whose verdict [`stands`], one a line (`reviews prereq standing --maps "<units>"`).
#[must_use]
pub fn standing(clone: &Path, units: &str) -> String {
    let named: Vec<&str> = units
        .split_whitespace()
        .filter(|u| stands(clone, u))
        .collect();
    named.iter().map(|u| (*u).to_owned() + "\n").collect()
}

#[cfg(test)]
mod tests;
