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

use std::path::{Path, PathBuf};

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

/// Every notes file in the pool and the frozen exhibits that carries a census block.
fn notes_with_blocks(root: &Path) -> Vec<PathBuf> {
    let mut out = Vec::new();
    for tree in ["pool", "legacy-hand-authored-pool"] {
        for tier in std::fs::read_dir(root.join(tree))
            .into_iter()
            .flatten()
            .flatten()
        {
            for map in std::fs::read_dir(tier.path())
                .into_iter()
                .flatten()
                .flatten()
            {
                let name = map.file_name().to_string_lossy().into_owned();
                let notes = map.path().join(format!("{name}.notes.md"));
                if l7r_gate_core::record::read_text(&notes).is_ok_and(|t| t.contains(super::BEGIN))
                {
                    out.push(notes);
                }
            }
        }
    }
    out.sort();
    out
}

/// THE CENSUS BLOCKS ARE FRESH (feature 152's test, `tests/test_notes_census.py`, dropped by feature 444 T39 on a wrong label and
/// restored by feature 449 T171): every census block a notes file carries is the one `make notes-census` writes from the manifest
/// beside it, and the five scripted hamlets each carry one - the counts a review keeps catching stale are those. Asked by the
/// lockstep's end-to-end test, which reads the pool already: the five hamlets' manifests and their ways out cost more than a unit test's
/// bar.
pub(crate) fn every_census_block_is_its_manifest_s(root: &Path) {
    let with = notes_with_blocks(root);
    let names: Vec<String> = with
        .iter()
        .map(|p| p.file_name().unwrap().to_string_lossy().into_owned())
        .collect();
    let missing: Vec<&str> = ["inashiro", "kashikawa", "kuwabata", "mizuguchi", "sawada"]
        .into_iter()
        .filter(|want| !names.contains(&format!("{want}.notes.md")))
        .collect();
    // the hamlets with no census block ride in the compared value
    assert_eq!(missing, Vec::<&str>::new());
    for notes in with {
        let text = l7r_gate_core::record::read_text(&notes).unwrap();
        let shown = notes.display().to_string();
        let manifest = PathBuf::from(format!("{}.json", shown.trim_end_matches(".notes.md")));
        let m =
            l7r_guard::shared::pyjson::loads(&l7r_gate_core::record::read_text(&manifest).unwrap())
                .unwrap();
        let (i, j) = (
            text.find(super::BEGIN).unwrap(),
            text.find(super::END).unwrap(),
        );
        let got = &text[i..j + super::END.len()];
        // the fix rides in the compared value, so a failure prints it beside the notes file
        assert_eq!(
            (shown.as_str(), got, STALE),
            (shown.as_str(), super::block(&m).unwrap().as_str(), STALE)
        );
    }
}

const STALE: &str = "the census block is stale - run `make notes-census`";
