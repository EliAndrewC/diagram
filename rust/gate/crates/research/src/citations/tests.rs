//! The works a question cites and what kind of note each is (feature 449 T148): `expected.json` holds HEAD's `citations.py` on the same
//! bodies (the T148 scratch's `pycite.py`); the works block is pinned through the site's cases (`record/site/cases.json`).

use std::collections::BTreeSet;

use serde_json::Value;

use super::{cited_keys, footnote_form, grounds_reasons, is_settled};

#[test]
fn every_note_is_classified_as_the_python_classified_it() {
    let rows: Vec<Value> = serde_json::from_str(include_str!("expected.json")).unwrap();
    let canon: BTreeSet<String> = ["l7r-notes".to_owned()].into();
    assert_eq!(rows.len(), 19);
    for row in rows {
        let body = row[0].as_str().unwrap();
        assert_eq!(footnote_form(body, &canon).as_deref(), row[1].as_str());
        let reasons: Vec<&str> = row[2]
            .as_array()
            .unwrap()
            .iter()
            .map(|r| r.as_str().unwrap())
            .collect();
        assert_eq!(grounds_reasons(body), reasons, "{body}");
        assert_eq!(is_settled(body), row[3].as_bool().unwrap(), "{body}");
    }
}

#[test]
fn the_keys_in_order_of_first_citation() {
    let bodies = [
        "<a href=\"x\"><code>b</code></a> <a href=\"y\"><code>a</code></a>",
        "<a href=\"z\"><code>b</code></a> <a href=\"z\"><code>Bad</code></a>",
    ];
    assert_eq!(cited_keys(bodies), ["b", "a"]);
}
