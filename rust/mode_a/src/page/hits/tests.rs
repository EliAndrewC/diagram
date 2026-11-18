//! The hit geometry at its edges (feature 449 T150); part A's page lockstep held every copy, region, layer and clip to the Python's (its Python deleted by part B, the cases' answers held by `page/held.rs`).
//!
//! Research: the hit geometry's tests - NONE: fixtures and assertions, deciding nothing about a building

use super::{open, part_of, widen, wrap};
use crate::tags::{ClsTag, Key};

#[test]
fn a_group_opens_with_its_slug_and_its_escaped_key() {
    assert_eq!(
        open("karo's house", true),
        "<g class=\"f f-karo-s-house planted\" data-k=\"karo&#x27;s house\">"
    );
    assert_eq!(widen("bund"), Some((8.0, 12.0, 6.0)));
    assert_eq!(widen("well"), None);
    assert_eq!(
        part_of("<g class=\"f x\"", &["k".to_owned()])
            .unwrap_err()
            .message,
        "substring not found"
    );
    let planted = ClsTag::Key(Key {
        name: "copse".into(),
        planted: true,
    });
    assert!(wrap("<rect/>", &planted)
        .unwrap()
        .starts_with("<g class=\"f f-copse planted\""));
    assert_eq!(wrap("<rect/>", &ClsTag::Unruled).unwrap(), "<rect/>");
}
