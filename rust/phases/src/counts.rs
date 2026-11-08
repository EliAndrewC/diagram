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

/// Add `n` to the counter `key` of a stage's map - compiled out of a build without the `counters` feature, as `Counts::add` is
/// (FR-012; the GM 2026-11-07: "We should probably run with counters compiled out by default"). The seat's, the sink's, the hem's
/// and the driver's counts went into their maps in every build before, a key allocated a count.
pub fn tally(counts: &mut HashMap<String, u64>, key: &str, n: u64) {
    #[cfg(feature = "counters")]
    if n > 0 {
        *counts.entry(key.to_owned()).or_insert(0) += n;
    }
    #[cfg(not(feature = "counters"))]
    let _ = (counts, key, n);
}

/// Add every count of `from` into `into` - compiled out with the counters, as `tally` is: without them every map is empty.
pub fn merge<'a>(
    into: &mut HashMap<String, u64>,
    from: impl IntoIterator<Item = (&'a String, &'a u64)>,
) {
    #[cfg(feature = "counters")]
    for (k, n) in from {
        *into.entry(k.clone()).or_insert(0) += n;
    }
    // ...the iterator drained all the same (every map empty without them, nothing to add): its stage's closures run as they do in
    // the counting build, so a coverage run reaches the code that names each stage's counts
    #[cfg(not(feature = "counters"))]
    let _ = (into, from.into_iter().count());
}

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
