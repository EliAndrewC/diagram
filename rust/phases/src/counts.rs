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
#[derive(Debug, Default)]
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
}
