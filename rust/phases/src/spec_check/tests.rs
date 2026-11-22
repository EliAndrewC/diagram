//! The spec check's tests (feature 449 T252): the reference hamlet clean, a spec that does not parse, and every refusal and broken
//! rule a problem.
//!
//! Research:
//!     the spec check's tests - NONE: fixtures and assertions, deciding nothing about a place

use super::{listed, problems};
use crate::driver::Refused;

/// The reference hamlet's spec (Inashiro's, `pool/hamlets/inashiro/inashiro.spec.json`) rolls clean through every stage and rule.
#[test]
fn the_reference_hamlet_rolls_clean() {
    let spec = r#"{"name": "Inashiro", "seed": 4, "households": 15, "down_deg": 90, "water_sink": "pond", "settlement_form": "nucleated"}"#;
    assert_eq!(problems(spec), Vec::<String>::new());
}

/// A spec that does not parse is one problem naming why.
#[test]
fn a_spec_that_does_not_parse_is_a_problem() {
    let found = problems("{not json");
    assert_eq!(found.len(), 1);
    assert!(found[0].starts_with("its spec does not parse: "));
}

/// A stage's error, each refusal and each broken rule are each a problem, in that order.
#[test]
fn every_refusal_and_broken_rule_is_a_problem() {
    assert_eq!(
        listed(Err(Refused("no room".to_owned()))),
        vec!["FAILED: no room".to_owned()]
    );
    assert_eq!(
        listed(Ok((
            vec!["a".to_owned()],
            vec!["b".to_owned(), "c".to_owned()]
        ))),
        vec![
            "REFUSED: a".to_owned(),
            "BROKE: b".to_owned(),
            "BROKE: c".to_owned()
        ]
    );
    assert_eq!(listed(Ok((Vec::new(), Vec::new()))), Vec::<String>::new());
}
