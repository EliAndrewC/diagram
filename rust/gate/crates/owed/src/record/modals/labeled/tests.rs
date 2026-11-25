//! A drawing page's new labeled item owes `modal-form` of each pop-up whose `Drawing:` names the page, triaged first; a referenced
//! item, an ATTESTED one, and a tag added to standing words owe nothing (feature 451 T226).

use super::{fingerprint, of_modal, LABELS};
use crate::record::modals::{fingerprints, modals_now, owed};
use crate::record::testkit::{commit, git, put, record, DRAWING, WELL};
use crate::record::triage::triage_only;

fn page(blocks: &str) -> String {
    format!("<h2>How drawn</h2>\n<p>Drawn as a line.<sup class=\"fn\" data-note=\"d\"></sup></p>\n{blocks}")
}

fn item(id: &str, label: &str, says: &str) -> String {
    format!("<p>{says}<span class=\"item\" data-item=\"{id}\" data-label=\"{label}\" data-guess=\"{says}\"></span></p>\n")
}

fn form_rows(root: &std::path::Path, base: &str, uid: &str) -> Vec<(String, String, String)> {
    owed(root, base, uid)
        .unwrap()
        .into_iter()
        .filter(|r| r.0 == format!("modal-form:{uid}"))
        .collect()
}

/// P7's and P15's case: a block new on the drawing page carrying a GUESS (or UNRESEARCHED) item owes each reader's form check,
/// through the triage.
#[test]
fn a_new_labeled_item_on_a_drawing_page_owes_its_readers_form_check_triaged_first() {
    let root = record("modals-labeled-new");
    let base = git(&root, &["rev-parse", "HEAD"]);
    put(
        &root,
        DRAWING,
        &page(&item(
            "ceiling",
            "GUESS",
            "No row is drawn past 145 ft, a GUESS.",
        )),
    );
    let rows = form_rows(&root, &base, "hamlet/well");
    assert_eq!(rows.len(), 1, "{rows:?}");
    assert_eq!(
        rows[0].1,
        "a page its Drawing: names gained a labeled item (0094-trade.drawing.html#ceiling GUESS)"
    );
    assert!(triage_only(&rows[0].1));
    let m = modals_now(&root, true)
        .unwrap()
        .into_iter()
        .find(|m| m.uid() == "hamlet/well")
        .unwrap();
    let (fp_form, _) = fingerprints(&root, &m).unwrap();
    assert_ne!(rows[0].2, fp_form);
    let items = of_modal(&root, &base, &m).unwrap();
    assert_eq!(rows[0].2, fingerprint(&fp_form, &items));
    assert_eq!(form_rows(&root, &base, "choice/bamboo--both").len(), 1);
    put(
        &root,
        DRAWING,
        &page(&item(
            "corner",
            "UNRESEARCHED",
            "Past the corner 90 ft, UNRESEARCHED.",
        )),
    );
    assert_eq!(
        form_rows(&root, &base, "hamlet/well")[0].1,
        "a page its Drawing: names gained a labeled item (0094-trade.drawing.html#corner UNRESEARCHED)"
    );
}

/// An ATTESTED item, an item the pop-up's Guesses references, and a tag added to words standing on the page owe no form check; with
/// no item owed, the fingerprint is the form's own.
#[test]
fn attested_referenced_and_mere_tagging_owe_nothing() {
    let root = record("modals-labeled-none");
    let standing = "<p>The line is a GUESS.</p>\n";
    put(&root, DRAWING, &page(standing));
    let base = commit(&root, "standing");
    put(
        &root,
        DRAWING,
        &page(&item("found", "ATTESTED", "Rows ran 300 ft, as recorded.")),
    );
    assert_eq!(form_rows(&root, &base, "hamlet/well"), []);
    put(&root, DRAWING, &page("<p>The line is a GUESS.<span class=\"item\" data-item=\"line\" data-label=\"GUESS\"></span></p>\n"));
    assert_eq!(form_rows(&root, &base, "hamlet/well"), []);
    put(&root, DRAWING, &page(standing));
    put(&root, WELL, "Name: Well\nAbout: A well in the yard.\n\nIt is deep.\nGuesses: - {0094#ceiling}\nEntry: research/questions/0094-trade.html\nDepiction: Drawn round.\nDrawing: research/questions/0094-trade.drawing.html\n");
    let base = commit(&root, "referenced");
    put(
        &root,
        DRAWING,
        &page(&item(
            "ceiling",
            "GUESS",
            "No row is drawn past 140 ft, a GUESS.",
        )),
    );
    assert!(owed(&root, &base, "hamlet/well")
        .unwrap()
        .iter()
        .all(|r| !r.1.contains("gained a labeled item")));
    assert_eq!(fingerprint("fp", &[]), "fp");
    assert!(
        LABELS.contains(&"DEVIATION")
            && LABELS.contains(&"CONVENTION")
            && !LABELS.contains(&"ATTESTED")
    );
}

/// A relabel to a guess label rewrites its block (its prose carries the label word) and owes; a pop-up whose own text moved owes its
/// form check once, for its own text.
#[test]
fn a_relabel_owes_and_a_moved_text_owes_its_form_check_once() {
    let root = record("modals-labeled-relabel");
    put(
        &root,
        DRAWING,
        &page(&item(
            "width",
            "ATTESTED",
            "The band is 90 ft wide, as recorded.",
        )),
    );
    let base = commit(&root, "attested");
    put(
        &root,
        DRAWING,
        &page(&item(
            "width",
            "DEVIATION",
            "The band is 90 ft wide, a deliberate deviation.",
        )),
    );
    let rows = form_rows(&root, &base, "hamlet/well");
    assert_eq!(rows.len(), 1);
    assert!(rows[0]
        .1
        .ends_with("(0094-trade.drawing.html#width DEVIATION)"));
    put(&root, WELL, "Name: Well\nAbout: A well, changed.\nEntry: research/questions/0094-trade.html\nDepiction: Drawn round.\nDrawing: research/questions/0094-trade.drawing.html\n");
    let rows = form_rows(&root, &base, "hamlet/well");
    assert_eq!(rows.len(), 1);
    assert_eq!(rows[0].1, "its About, Guesses or Entry changed");
    assert_eq!(
        of_modal(&root, "", &modals_now(&root, true).unwrap()[0]).unwrap(),
        []
    );
}
