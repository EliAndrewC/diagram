//! THE SHEETS' TYPED COUNTS (feature 294 B15b, the audit's B11 row; moved here from `tests/test_mode_a_sheets.py` by feature 449 T170,
//! with the Python it called): a count of tubs, privies or wells typed in a pool sheet's notes' current prose agrees with what the sheet
//! draws - dated history exempt, and a count of a part. Every pool sheet of a declared Mode A tier is read as it stands on disk; the pytest
//! sweep regenerated a declared generated exception's sheet when absent or stale first, which a Rust test cannot, so such a sheet is held
//! where it has been drawn (`make quick`'s sweep draws it). It runs inside the parse's lockstep (`parse/lockstep.rs`), FR-008's one
//! end-to-end test, which reads every pool sheet already: alone it took 0.146 s, over the bar (observed 2026-11-17, method:
//! `make test-times CRATE=rust/mode_a`).
//!
//! Research:
//!     the sheets' typed counts check - NONE: a check over the pool's sheets and their notes, deciding nothing about a building

use std::path::PathBuf;

use super::stale_sheet_counts;

/// Every pool sheet's notes type the counts it draws (asked by the lockstep's end-to-end test with the pool's sheets).
pub(crate) fn every_pool_sheet_s_notes_type_the_counts_it_draws(sheets: &[PathBuf]) {
    for svg in sheets {
        let notes =
            l7r_gate_core::record::read_text(&svg.with_extension("notes.md")).unwrap_or_default();
        let text = l7r_gate_core::record::read_text(svg).unwrap();
        let stale = stale_sheet_counts(&notes, &text).unwrap();
        // the fix rides in the compared value, so a failure prints it beside the sheet and its stale counts
        assert_eq!(
            (svg.display().to_string(), stale, FIX),
            (svg.display().to_string(), Vec::<String>::new(), FIX)
        );
    }
}

const FIX: &str = "the notes type counts the sheet does not draw - correct them, or move them under a dated entry";
