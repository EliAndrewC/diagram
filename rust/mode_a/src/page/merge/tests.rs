//! The merge's readings at their edges (feature 449 T150); part A's page lockstep held every merge to the Python's (its Python deleted by part B, the cases' answers held by `page/held.rs`).
//!
//! Research: the merge's tests - NONE: fixtures and assertions, deciding nothing about a building

use super::{attrs, extent, hits, Extent};

#[test]
fn an_unknown_extent_touches_everything_and_the_last_value_of_a_name_holds() {
    assert!(hits(None, Some(Extent::Box(0.0, 0.0, 1.0, 1.0))));
    assert!(hits(Some(Extent::Disc(0.0, 0.0, 1.0)), None));
    assert!(!hits(
        Some(Extent::Disc(0.0, 0.0, 1.0)),
        Some(Extent::Disc(3.0, 0.0, 1.0))
    ));
    assert!(hits(
        Some(Extent::Disc(0.0, 0.0, 1.0)),
        Some(Extent::Box(0.5, 0.5, 4.0, 4.0))
    ));
    assert_eq!(
        attrs("a=\"1\" b=\"2\" a=\"3\""),
        [
            ("a".to_owned(), "3".to_owned()),
            ("b".to_owned(), "2".to_owned())
        ]
    );
    for (tag, body) in [
        ("line", "x1=\"0\" y1=\"0\" x2=\"1\""),
        ("ellipse", "cx=\"0\""),
        ("rect", "x=\"0\""),
        ("circle", "r=\"1\""),
    ] {
        assert_eq!(extent(tag, &attrs(body)).unwrap(), None);
    }
}
