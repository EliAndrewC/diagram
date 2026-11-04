//! The derivation's counts, shared by every rebuilt phase (feature 444 FR-012, T19 D9; T16 D6).
//!
//! Research:
//!     the counts - NONE: the work-budget's own bookkeeping

use std::collections::HashMap;

/// The derivation's count, kept by `<kind>@<function>` as the Python counters keep theirs - `candidate@roll_plan` for a draw here,
/// `write@_rust_rolls` for a field Python writes back (D9) - compiled out of a build
/// without the `counters` feature (FR-012).
///
/// Research:
///     the counts - NONE: the work-budget's own bookkeeping
#[derive(Default)]
pub struct Counts(pub HashMap<String, u64>);

impl Counts {
    #[cfg_attr(
        not(feature = "counters"),
        expect(clippy::unused_self, reason = "the counters compile out (FR-012)")
    )]
    pub fn add(&mut self, key: &str, n: u64) {
        #[cfg(feature = "counters")]
        {
            // looked up first, so a key already counted costs no allocation (the ways' point tests count by the million)
            if let Some(v) = self.0.get_mut(key) {
                *v += n;
            } else {
                self.0.insert(key.to_owned(), n);
            }
        }
        #[cfg(not(feature = "counters"))]
        let _ = (key, n);
    }

    /// The work counted, the moves, drops and placements reported and left out (`tools/work_budget.py`'s total) - the tests'
    /// reading; Python totals what a stage returns.
    #[cfg(test)]
    #[must_use]
    pub fn total(&self) -> u64 {
        self.0
            .iter()
            .filter(|(k, _)| !matches!(k.split('@').next(), Some("placed" | "dropped" | "moved")))
            .map(|(_, n)| n)
            .sum()
    }
}

thread_local! {
    /// The work the lane law's predicates count where no `Counts` is handed down to them: dozens of call sites deep, each asked of
    /// a candidate many times over, threading a counter through every one would double their signatures for bookkeeping alone.
    /// The stage that asks them drains it into its own `Counts` once (`drain_into`), so what it reports is every element counted.
    static NOTED: std::cell::RefCell<Counts> = std::cell::RefCell::new(Counts::default());
}

/// Count `n` of the work `key` in the thread's tally, for the stage to drain (compiled out without the `counters` feature).
pub fn note(key: &str, n: u64) {
    NOTED.with(|c| c.borrow_mut().add(key, n));
}

/// Move the thread's tally into `counts`, emptying it.
pub fn drain_into(counts: &mut Counts) {
    let noted = NOTED.with(|c| std::mem::take(&mut *c.borrow_mut()));
    for (k, n) in noted.0 {
        counts.add(&k, n);
    }
}
