//! The Rust tooling fixture (feature 444 T17): one stage-shaped function and the module Python imports.

use pyo3::prelude::*;

/// Sums a row of counts, as a stage sums its work.
///
/// Research: the fixture's stand-in claim, read by the claims reader's Rust form (`research/questions/0000-fixture.html`).
/// Steps:
/// 1. sum the counts
#[must_use]
pub fn total(counts: &[u64]) -> u64 {
    counts.iter().sum()
}

/// The stage's entry from Python: the counts in, their total out.
#[pyfunction]
#[expect(
    clippy::needless_pass_by_value,
    reason = "PyO3 hands a Vec from a Python list"
)]
fn stage_total(counts: Vec<u64>) -> u64 {
    total(&counts)
}

/// The module Python imports.
///
/// # Errors
/// When the function cannot be added to the module.
#[pymodule]
fn l7r_fixture(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(stage_total, m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::total;

    #[test]
    fn the_total_of_a_row_is_its_sum() {
        assert_eq!(total(&[1, 2, 3]), 6);
    }
}
