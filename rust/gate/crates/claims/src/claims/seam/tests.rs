//! A Rust stage's own findings split from the rest.

use super::split;

#[test]
fn a_landing_answers_for_its_own_findings() {
    let report = "claims: 3 in scope\n  DRIFTED        rust/phases/src/lib.rs::GAP#g - rust\n  MISLABELED     docs/buildings.md::Walls#w - doc\n  DRIFTED        docs/x.md::y#z - not changed\nUNRESEARCHED claims\n";
    let changed: Vec<String> = ["rust/phases/src/lib.rs", "docs/buildings.md"]
        .map(str::to_owned)
        .to_vec();
    let (own, left) = split(report, &changed);
    assert_eq!(
        own,
        vec!["DRIFTED        rust/phases/src/lib.rs::GAP#g - rust"]
    );
    assert_eq!(
        left,
        vec!["MISLABELED     docs/buildings.md::Walls#w - doc"]
    );
}
