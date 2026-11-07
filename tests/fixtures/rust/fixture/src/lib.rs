//! The Rust tooling fixture (feature 444 T17): one stage-shaped function, its own test reaching it.

/// Sums a row of counts, as a stage sums its work.
///
/// Research: the fixture's stand-in claim, read by the claims reader's Rust form (`research/questions/0000-fixture.html`).
/// Steps:
/// 1. sum the counts
#[must_use]
pub fn total(counts: &[u64]) -> u64 {
    counts.iter().sum()
}

#[cfg(test)]
mod tests {
    use super::total;

    #[test]
    fn the_total_of_a_row_is_its_sum() {
        assert_eq!(total(&[1, 2, 3]), 6);
    }
}
