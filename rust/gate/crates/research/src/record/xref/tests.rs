//! The cross-links (feature 449 T144; each expected value `xref.py`'s on the same record, 2026-11-16).

use super::{link, pairs, Pair};
use crate::fixture::record;
use crate::record::questions;

#[test]
fn a_drawing_page_links_its_research_page_both_ways() {
    let dir = record();
    let r = questions::load(&dir).unwrap();
    let all = pairs(&r);
    assert_eq!(
        all,
        [
            Pair {
                drawing: "0001-paddies.drawing.html".into(),
                research: "0001-paddies.html".into()
            },
            Pair {
                drawing: "0003-more-drawn.drawing.html".into(),
                research: "0001-paddies.html".into()
            },
        ]
    );
    let coins = r.by_file("0002-coins.html").unwrap();
    assert_eq!(link(&coins.text, coins, &all).unwrap(), coins.text);
    let paddies = r.by_file("0001-paddies.html").unwrap();
    assert_eq!(
        link("no heading here", paddies, &all).unwrap_err().kind,
        "AssertionError"
    );
}
