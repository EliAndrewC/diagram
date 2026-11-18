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

/// FIXED (feature 449 T183, T150's finding): the geometry's pattern took `d="a"` out of `id="a"`, so a copy of a mark carrying an id
/// gained a `d` - a path two of them, a line a `d` it never had. An attribute is matched only at its own name.
#[test]
fn a_copy_takes_no_d_out_of_an_id() {
    let copies = super::hit_copies(
        "<path id=\"p\" d=\"M0,0L5,5\" stroke=\"#000\"/><line x1=\"0\" y1=\"0\" x2=\"9\" y2=\"9\" data-id=\"a\" grid=\"x\"/>",
        super::HIT_DEFAULT,
    )
    .unwrap();
    assert_eq!(
        copies,
        "<path d=\"M0,0L5,5\" fill=\"none\" class=\"hit\" style=\"pointer-events: stroke; stroke-width: 6.0px\"/>\
         <line x1=\"0\" y1=\"0\" x2=\"9\" y2=\"9\" fill=\"none\" class=\"hit\" style=\"pointer-events: stroke; stroke-width: 6.0px\"/>"
    );
}
