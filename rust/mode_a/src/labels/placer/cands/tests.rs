//! The rings and a block's lines as the Python measured them (feature 449 T151; each printed by `labels/placer.py` under `CPython`
//! 3.14.4, 2026-11-18). The candidates themselves are held by `placer/tests.rs`' sixty scenes.
//!
//! Research:
//!     its tests - NONE: the port held to the Python's answers, deciding nothing about a building

use super::{outer_rings, rings, sized_half};

#[test]
fn the_rings_and_a_block_s_lines_are_the_python_s() {
    assert_eq!(
        rings(8.0),
        (1..=16).map(|k| f64::from(k) * 4.0).collect::<Vec<_>>()
    );
    assert_eq!(
        outer_rings(8.0),
        (16..=27)
            .map(|k| (k, f64::from(u32::try_from(k).unwrap()) * 4.0 + 4.0))
            .collect::<Vec<_>>()
    );
    // a large caption's rings stop at the hug, and it has no leader ring past them
    assert_eq!(
        (rings(40.0), outer_rings(40.0)),
        (vec![20.0, 40.0, 60.0, 80.0, 100.0], Vec::new())
    );
    // a caption of no size has no leader ring (the Python's loop never ended)
    assert!(outer_rings(0.0).is_empty() && outer_rings(f64::NAN).is_empty());
    let lines = ["BATH".to_owned(), "xx".to_owned()];
    assert_eq!(
        sized_half(&lines, 12.0, 0.55, Some(&[12.0, 8.0])),
        (13.200_000_000_000_001, 10.9)
    );
    assert_eq!(
        sized_half(&lines[..1], 12.0, 0.55, Some(&[])),
        (13.200_000_000_000_001, 6.300_000_000_000_001)
    );
}
