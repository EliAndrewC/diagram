//! Tagging a page and turning a written-out Guesses bullet into a reference owe no pop-up check; rewording a referenced tag's bullet
//! does (feature 451 T192).

use super::{references, resolved, tagged_now};
use crate::record::modals::owed;
use crate::record::testkit::{commit, git, put, record, DRAWING, WELL};

const WRITTEN: &str = "Name: Well\nAbout: A well in the yard.\n\nIt is deep.\nGuesses: - a guess\n  continued\n- another\nEntry: research/questions/0094-trade.html\nDepiction: Drawn round.\nDrawing: research/questions/0094-trade.drawing.html\n";
const BY_REFERENCE: &str = "Name: Well\nAbout: A well in the yard.\n\nIt is deep.\nGuesses: - {0094#g}\n- another\nEntry: research/questions/0094-trade.html\nDepiction: Drawn round.\nDrawing: research/questions/0094-trade.drawing.html\n";

fn drawing(guess: &str) -> String {
    format!("<h2>How drawn</h2>\n<p>Drawn as a line.<sup class=\"fn\" data-note=\"d\"></sup> The line is a GUESS.<span class=\"item\" data-item=\"g\" data-label=\"GUESS\" data-guess=\"{guess}\"></span></p>\n")
}

#[test]
fn a_page_gaining_a_tag_owes_no_pop_up() {
    let root = record("modals-refs-tag");
    put(&root, DRAWING, "<h2>How drawn</h2>\n<p>Drawn as a line.<sup class=\"fn\" data-note=\"d\"></sup> The line is a GUESS.</p>\n");
    put(&root, WELL, WRITTEN);
    let base = commit(&root, "untagged");
    put(&root, DRAWING, &drawing("a guess continued"));
    assert_eq!(owed(&root, &base, "hamlet/well").unwrap(), []);
}

#[test]
fn a_bullet_made_a_reference_owes_nothing_and_its_tag_reworded_owes_the_checks() {
    let root = record("modals-refs-reference");
    put(&root, DRAWING, &drawing("a guess continued"));
    put(&root, WELL, WRITTEN);
    let base = commit(&root, "tagged");
    put(&root, WELL, BY_REFERENCE);
    assert_eq!(owed(&root, &base, "hamlet/well").unwrap(), []);
    let base = commit(&root, "by reference");
    put(&root, DRAWING, &drawing("a guess, reworded"));
    let rows = owed(&root, &base, "hamlet/well").unwrap();
    assert!(rows
        .iter()
        .any(|r| r.0 == "modal-form:hamlet/well" && r.1 == "its About, Guesses or Entry changed"));
    assert!(!git(&root, &["status", "--short"]).is_empty());
}

#[test]
fn a_reference_is_filled_whatever_its_label_and_one_naming_no_item_is_left() {
    let root = record("modals-refs-resolved");
    put(
        &root,
        DRAWING,
        &drawing("a guess continued")
            .replace("\"GUESS\"", "\"ATTESTED\"")
            .replace(" The line is a GUESS.", ""),
    );
    let text =
        "- {0094#g}\n- [season=winter] {0094#g}\n- {0094#nope}\n- {0095#x}\n- {0095#g}\n- plain";
    let refs = references(text);
    assert_eq!(refs.len(), 4);
    let tagged = tagged_now(&root, &refs);
    // `{0095#g}` names an item 0095 does not tag: filled from the one other question tagging `g`, as the registry fills it (T200)
    assert_eq!(
        resolved(text, &tagged),
        "- a guess continued\n- [season=winter] a guess continued\n- {0094#nope}\n- {0095#x}\n- a guess continued\n- plain"
    );
}

/// A reference to an item tagged on another question than its own is read from that question's page at the base too, so a
/// rewording there owes the pop-up its checks (451 T200's moved items).
#[test]
fn a_moved_item_s_reworded_bullet_owes_the_checks() {
    let root = record("modals-refs-moved");
    put(&root, DRAWING, &drawing("a guess continued"));
    put(&root, WELL, &BY_REFERENCE.replace("{0094#g}", "{0095#g}"));
    let base = commit(&root, "moved");
    assert_eq!(owed(&root, &base, "hamlet/well").unwrap(), []);
    put(&root, DRAWING, &drawing("a guess, reworded"));
    let rows = owed(&root, &base, "hamlet/well").unwrap();
    assert!(rows
        .iter()
        .any(|r| r.0 == "modal-form:hamlet/well" && r.1 == "its About, Guesses or Entry changed"));
}
