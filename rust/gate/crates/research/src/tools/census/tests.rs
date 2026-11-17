//! The footnote census (feature 449 T148): the report is HEAD's `footnote_census.render(census(...))` on the crate's fixture tree.

use super::run;
use crate::fixture::{put, tree};

const REPORT: &str = "section          cited  grounds  ABSENT  settled\n------------------------------------------------\ndrawing: Land        0        0       0        0\nresearch: Coin       0        0       0        0\nresearch: Land       1        0       0        0\n------------------------------------------------\nTOTAL                1        0       0        0\n\nMALFORMED: 1 footnote(s) match no form - the gate will name them\n\nThe backlog is ABSENT: 0. The other three columns owe nothing.\n";

#[test]
fn the_census_is_the_pythons() {
    let t = tree();
    let r = run(&[], &t).unwrap();
    assert_eq!((r.stdout.as_str(), r.code), (REPORT, 0));
    let bad = run(&["--x".to_owned()], &t).unwrap();
    assert_eq!(
        (bad.code, bad.stderr.as_str()),
        (
            2,
            "l7r-gate record footnote-census: error: unrecognized arguments: --x\n"
        )
    );
    put(&t, &q("0001-paddies.notes.html"), "<li data-note=\"k\">no publicly readable source (searched 2026-01-01: x) settled 2026-02-02</li>\n<li data-note=\"n\">no source is owed: physical necessity</li>\n");
    put(&t, &q("0001-paddies.originals.html"), "");
    let r = run(&[], &t).unwrap();
    assert!(
        r.stdout
            .contains("research: Land       0        1       0        1\n")
            && !r.stdout.contains("MALFORMED")
    );
    std::fs::remove_file(t.join("research/tags.json")).unwrap();
    assert_eq!(run(&[], &t).unwrap_err().kind, "RecordError");
}

/// A question file's path in the fixture tree, built from its parts.
fn q(name: &str) -> String {
    format!("research/{}/{name}", crate::record::questions::QUESTIONS)
}
