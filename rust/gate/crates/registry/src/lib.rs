//! The map's vocabulary in Rust (feature 449 T149, phase 4's S6, `ask:449-phase4-slices` Q5): the registry of kinds that
//! `l7r/diagram/interactive/classes/` and `compound_kinds/` hold ([`kinds`]), each kind's modal read from its Markdown file ([`about`]), the
//! knob conditions ([`conditions`]) and the title card's choices ([`choices`]), and the readers that ported with them: the push's
//! entry-headings check ([`headings`], `scripts/gates/check-entry-headings.py`) and `make open-questions` ([`open_questions`],
//! `scripts/record/open_questions.py`). `modals.rs` (the `owed` crate) enumerates its modals from [`kinds`] and the entry-drift report
//! (`owed`'s `record::entry`, `scripts/record/entry_owed.py`) reads [`about`].
//!
//! The Python registry, `conditions.py` and `choices.py` stay the implementation for their Python importers - the page writer (S7), the
//! Mode A sheets and `buildings/types.py` (S9-S11), the pipeline's render cache (S12) - and are frozen under Q1: an edit of them makes the
//! same change here in the same commit. `registry dump` is this library's reading of the real tree, which the slice's differential
//! compares with the Python's.

pub mod about;
pub mod choices;
pub mod cli;
pub mod conditions;
pub mod headings;
pub mod kinds;
pub mod open_questions;
#[cfg(any(test, feature = "testkit"))]
pub mod testkit;
