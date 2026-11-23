//! A claim on a tagged item held to its tag, and its class flip moving no fingerprint (feature 451 T187).

use l7r_gate_core::record::testkit::put;

use super::{check, disagreements};
use crate::claims::grammar::parse_claim;
use crate::claims::units::{from_json, Unit};

const FILE: &str = "research/questions/0218-shrine.drawing.html";

fn tagged(label: &str, says: &str) -> String {
    format!(
        r#"<li>The tree, {says}.<span class="item" data-item="tree" data-label="{label}" data-guess="The tree: none"></span></li>"#
    )
}

fn unit(line: &str) -> Unit {
    from_json(&serde_json::json!({"path": "rust/phases/src/lib.rs", "qualname": "tree", "kind": "function", "claims": [line]})).0
}

#[test]
fn a_claim_on_an_item_is_held_to_its_tag_and_its_flip_moves_no_fingerprint() {
    let root = crate::claims::tests::fixture("claims-item-labels");
    put(&root, FILE, &tagged("GUESS", "a GUESS"));
    let attested = format!("shrine tree - {FILE}#tree: a tree beside the shrine");
    let guess = format!("shrine tree - GUESS {FILE}#tree: a tree beside the shrine");
    let said = disagreements(&root, &[unit(&attested)]);
    assert_eq!(said.len(), 1, "{said:?}");
    assert!(said[0].contains("is POINTER but research/questions/0218-shrine.drawing.html#tree is tagged GUESS - write its backing `GUESS research/questions/0218-shrine.drawing.html#tree`"), "{said:?}");
    assert!(disagreements(&root, &[unit(&guess)]).is_empty());
    // the flip owes nothing
    let (was, now) = (
        parse_claim(&attested).unwrap(),
        parse_claim(&guess).unwrap(),
    );
    assert_eq!(was.normalized(), now.normalized());
    let plain = format!("shrine tree - GUESS {FILE}: a tree");
    // an untagged claim's class is still its own
    let pointer = parse_claim(&format!("shrine tree - {FILE}: a tree")).unwrap();
    assert_ne!(
        parse_claim(&plain).unwrap().normalized(),
        pointer.normalized()
    );
    let c = parse_claim(&guess).unwrap();
    assert_eq!(c.pointers, [FILE]);
    assert_eq!(c.items, [(FILE.to_owned(), "tree".to_owned())]);
    put(&root, FILE, &tagged("ATTESTED", "accurate"));
    let said = disagreements(&root, &[unit(&guess)]);
    let said = &said[0];
    assert!(said.contains("is GUESS but") && said.contains("backing `research/questions"),);
    put(&root, FILE, &tagged("CONVENTION", "a convention"));
    let conv = format!("shrine tree - CONVENTION {FILE}#tree: drawn so");
    assert!(disagreements(&root, &[unit(&conv)]).is_empty());
    let unread = "shrine tree - GUESS research/questions/0999-none.drawing.html#gone: a tree";
    assert!(disagreements(&root, &[unit(unread)])[0].contains("which no tag on that page carries"));
    let missing = format!("shrine tree - GUESS {FILE}#gone: a tree");
    assert!(
        disagreements(&root, &[unit(&missing)])[0].contains("which no tag on that page carries")
    );
    // the fixture's own claims name no item
    assert!(check(&root).unwrap().is_empty());
}

#[test]
fn a_convention_takes_only_items() {
    assert!(parse_claim(&format!("a - CONVENTION {FILE}"))
        .unwrap_err()
        .contains("`CONVENTION` takes no pointer, or only items"));
    assert!(parse_claim("a - CONVENTION").is_ok());
}

/// 451 T200: an item moved to another question's page is named with the pointer to write there, its class held to the moved tag; an id
/// two other pages tag is no move the tool can name.
#[test]
fn a_moved_item_is_named_with_its_new_pointer() {
    let root = crate::claims::tests::fixture("claims-item-moved");
    let to = "research/questions/0301-trees.drawing.html";
    put(&root, to, &tagged("GUESS", "a GUESS"));
    let claim = format!("shrine tree - GUESS {FILE}#tree: a tree beside the shrine");
    let said = disagreements(&root, &[unit(&claim)]);
    assert_eq!(said.len(), 1, "{said:?}");
    assert!(said[0].contains(&format!("names {FILE}#tree, but the item is tagged on {to} now - write its backing `GUESS {to}#tree`")), "{said:?}");
    put(
        &root,
        "research/questions/0302-more.html",
        &tagged("ATTESTED", "accurate"),
    );
    put(
        &root,
        "research/questions/0302-more.notes.html",
        &tagged("ATTESTED", "accurate"),
    );
    assert!(disagreements(&root, &[unit(&claim)])[0].contains("which no tag on that page carries"));
}

/// A split is a move (the GM 2026-11-23): where the cited page's split pointer directs the reader to the page that now tags the item,
/// the claim is followed there and owes no edit; held to that tag's class; two reached pages tagging it are refused, naming the case.
#[test]
fn a_moved_item_the_cited_page_points_to_is_followed_and_owes_no_edit() {
    let root = crate::claims::tests::fixture("claims-item-followed");
    let to = "research/questions/0301-trees.drawing.html";
    put(&root, to, &tagged("GUESS", "a GUESS"));
    put(
        &root,
        FILE,
        r#"<p>The tree moved: <a class="moved" href="0301-trees.drawing.html">its own page</a>.</p>"#,
    );
    let guess = format!("shrine tree - GUESS {FILE}#tree: a tree beside the shrine");
    assert!(disagreements(&root, &[unit(&guess)]).is_empty());
    let plain = format!("shrine tree - {FILE}#tree: a tree beside the shrine");
    let said = disagreements(&root, &[unit(&plain)]);
    let flip = said.len() == 1 && said[0].contains(&format!("moved to {to} by its split, is tagged GUESS there - write its backing `GUESS {FILE}#tree`"));
    assert!(flip, "{said:?}");
    put(
        &root,
        FILE,
        r#"<a class="moved" href="0301-trees.drawing.html">one</a> <a class="moved" href="0302-more.html">two</a>"#,
    );
    put(
        &root,
        "research/questions/0302-more.html",
        &tagged("GUESS", "a GUESS"),
    );
    let said = disagreements(&root, &[unit(&guess)]);
    let two = said.len() == 1 && said[0].contains("which pages its split reaches each tag");
    assert!(two, "{said:?}");
}
