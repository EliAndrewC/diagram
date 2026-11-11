//! Each label fault a claim's own words show, and none on a right label.

use std::collections::HashMap;

use super::flag;
use crate::claims::grammar::parse_claim;
use crate::claims::tests::fixture;

#[test]
fn each_label_fault_is_flagged() {
    let root = fixture("claims-labels");
    let q = root.join("research/questions");
    let mut pages = HashMap::new();
    let f = |line: &str, pages: &mut HashMap<String, String>| {
        flag("k", &parse_claim(line).unwrap(), &q, pages)
    };
    assert!(f("a - NONE", &mut pages).is_empty());
    let got = f(
        "a - GUESS: stricter than the page, as 0054 says",
        &mut pages,
    );
    assert_eq!(got.len(), 2);
    assert!(got[0].contains("departs from a page") && got[1].contains("names 0054"));
    assert!(f("a - GUESS: 0054 is silent on it", &mut pages).is_empty());
    let got = f(
        "a - GUESS research/questions/0002-other.drawing.html: 40 ft and 7.0 ft and 7.0 ft",
        &mut pages,
    );
    assert_eq!(got, vec!["claims-label: k - `GUESS <page>` says the page records this guess, but no page it names states 7.0 ft: a bare GUESS if no page speaks, `DEVIATION <page>` if the code departs from the page's figure"]);
    assert!(f(
        "a - GUESS research/questions/0009-missing.drawing.html: 40 ft",
        &mut pages
    )[0]
    .contains("states 40 ft"));
    assert!(f(
        "a - GUESS research/questions/0002-other.drawing.html: 40.0 ft",
        &mut pages
    )
    .is_empty());
}
