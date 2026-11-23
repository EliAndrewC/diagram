//! A relabel cascades by regeneration and owes no check (feature 451 T187; the GM 2026-11-23, request.md "the convergence talk":
//! *"Shouldn't attested versus guess be something that cascades mechanically rather than requiring a review, though?"*). A pop-up whose
//! Guesses bullet is a reference to the item (`{NNNN#<id>}`, `l7r_gate_registry::items`) does not repeat the page's words, so the
//! triage's first filter (`record::triage::change::fires`) clears the relabel with no agent, and the registry fills its Guesses tab from
//! the tag; the same pop-up with the guess written out in its own words is sent on, as every label change was before.

use std::collections::HashSet;

use l7r_gate_core::checks::scratch;
use l7r_gate_core::record::testkit::put;
use l7r_gate_registry::about::{about_feature, parse_explanation};
use l7r_gate_registry::items::resolve;

use crate::record::triage::change::{fires, new_findings, page_change};

fn page(label: &str, says: &str) -> String {
    format!(
        r#"<h2 id="x">How our maps draw shrines</h2>
<ul>
<li><strong>Why does the shrine stand in a corner, beside a tree?</strong><br>A household's god was kept in a corner of its lot, at an old tree or a stone. {says}<span class="item" data-item="tree" data-label="{label}" data-guess="The tree beside the shrine: no account gives a household's shrine a tree beside it as the custom"></span></li>
</ul>"#
    )
}

const BY_REFERENCE: &str = "About: A shrine in a corner of the grounds.\n\nGuesses:\n- {0218#tree}\n\nName: Shrine\nCovers: `shrine`\nSources: not recorded\nEntry: research/questions/0218-the-compounds-own-shrine-yashikigami.html\nDrawing: research/questions/0218-the-compounds-own-shrine-yashikigami.drawing.html\n";
const IN_ITS_WORDS: &str = "About: A shrine in a corner of the grounds.\n\nGuesses:\n- Our maps set the compound's shrine where a household's stood, and give it the tree as well.\n\nName: Shrine\nCovers: `shrine`\nSources: not recorded\nEntry: research/questions/0218-the-compounds-own-shrine-yashikigami.html\n";

fn popup(modal: &str) -> String {
    let parts = parse_explanation(Some(modal), "Shrine").unwrap();
    parts
        .iter()
        .filter(|(k, _)| ["About", "Guesses", "Depiction"].contains(&k.as_str()))
        .map(|(_, v)| v.clone())
        .collect::<Vec<_>>()
        .join("\n")
}

#[test]
fn a_relabel_regenerates_the_bullet_and_owes_no_check() {
    let old = page("ATTESTED", "Our maps set the compound's shrine where a household's stood, and give it the tree as well.");
    let fresh = page("GUESS", "Our maps set the compound's shrine where a household's stood. That they give it a tree beside it as well is a GUESS.");
    let none: HashSet<String> = HashSet::new();
    let c = page_change(&old, &fresh, &none, &none, &[]);
    assert_eq!(c.pairs.len(), 1, "the relabel is a changed block: {c:?}");
    let blocks: Vec<String> = l7r_shared::checks::pages::read_page(&fresh)
        .blocks
        .into_iter()
        .map(|b| b.words)
        .collect();
    let found = new_findings(&old, &fresh);
    // a pop-up reading the item by reference owes nothing; the guess in the pop-up's own words is sent on
    let (by_reference, in_its_words) = (popup(BY_REFERENCE), popup(IN_ITS_WORDS));
    assert_eq!(fires(&c, &blocks, &none, &by_reference, &found), None);
    assert!(fires(&c, &blocks, &none, &in_its_words, &found).is_some());
    let root = scratch("owed-item-relabel");
    let fc = || {
        about_feature(
            "Shrine",
            "shrine",
            &parse_explanation(Some(BY_REFERENCE), "Shrine").unwrap(),
        )
        .unwrap()
    };
    put(&root, "research/questions/0218-the-compounds-own-shrine-yashikigami.drawing.html", &old);
    // attested: no bullet
    assert!(resolve(&root, fc()).unwrap().guesses.is_empty());
    put(&root, "research/questions/0218-the-compounds-own-shrine-yashikigami.drawing.html", &fresh);
    // a GUESS: the bullet is the tag's
    let tree = "The tree beside the shrine: no account gives a household's shrine a tree beside it as the custom";
    assert_eq!(resolve(&root, fc()).unwrap().guesses, [tree]);
}
