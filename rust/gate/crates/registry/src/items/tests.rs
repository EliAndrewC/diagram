//! A pop-up's Guesses filled from the record's item tags (feature 451 T187).

use std::path::Path;

use l7r_gate_core::checks::scratch;
use l7r_gate_core::record::testkit::put;

use super::{resolve, restated, Pages};
use crate::about::{about_feature, parse_explanation, FeatureClass};

const PAGE: &str = "research/questions/0218-the-compounds-own-shrine-yashikigami.drawing.html";

fn page(label: &str, word: &str) -> String {
    format!(
        r#"<ul><li><strong>The tree.</strong><br>That they give it a tree is {word}.<span class="item" data-item="tree" data-label="{label}" data-guess="The tree beside the shrine: no account gives it as the custom"></span></li></ul>"#
    )
}

const MODAL: &str = "About: A shrine in a corner.\n\nGuesses:\n- [layout=row] {0218#tree}\n- A garden: no account.\n\nName: Shrine\nCovers: `shrine`\nSources: not recorded\nEntry: research/questions/0218-the-compounds-own-shrine-yashikigami.html\nDrawing: research/questions/0218-the-compounds-own-shrine-yashikigami.drawing.html\n";

fn class(text: &str) -> FeatureClass {
    about_feature(
        "Shrine",
        "shrine",
        &parse_explanation(Some(text), "Shrine").unwrap(),
    )
    .unwrap()
}

fn guesses(root: &Path) -> Vec<String> {
    resolve(root, class(MODAL)).unwrap().guesses
}

#[test]
fn a_relabel_on_the_page_regenerates_the_bullet_and_the_pop_up_is_unchanged() {
    let root = scratch("registry-items");
    put(
        &root,
        "research/questions/0218-the-compounds-own-shrine-yashikigami.html",
        "<p>The shrine.</p>",
    );
    put(
        &root,
        "research/questions/0218-the-compounds-own-shrine-yashikigami.notes.html",
        r#"<span class="item" data-item="tree" data-label="ATTESTED"></span>"#,
    );
    put(&root, PAGE, &page("GUESS", "a GUESS"));
    assert_eq!(
        guesses(&root),
        [
            "[layout=row] The tree beside the shrine: no account gives it as the custom",
            "A garden: no account."
        ]
    );
    put(&root, PAGE, &page("ATTESTED", "historically accurate"));
    // the bullet goes with the label; the modal's text never moved
    assert_eq!(guesses(&root), ["A garden: no account."]);
}

#[test]
fn a_reference_no_tag_answers_is_refused_with_its_fix() {
    let root = scratch("registry-items-missing");
    let e = resolve(&root, class(MODAL)).unwrap_err();
    assert_eq!(e.kind, "ValueError");
    let said = e.message;
    assert!(said.contains("shrine: the Guesses bullet {0218#tree} names no item: tag it"),);
}

#[test]
fn an_about_that_states_a_tagged_guess_as_a_fact_is_named() {
    let root = scratch("registry-items-about");
    put(&root, PAGE, &page("GUESS", "a GUESS"));
    let said = MODAL.replace(
        "About: A shrine in a corner.",
        "About: A shrine in a corner. The tree beside the shrine is old.",
    );
    let mut pages = Pages::default();
    let found = restated(&root, &class(&said), &mut pages);
    assert_eq!(found.len(), 1, "{found:?}");
    assert!(found[0].contains(
        "its About states 0218#tree (\"the tree beside the shrine\"), tagged a GUESS, as a fact"
    ));
    let labeled = said.replace("is old.", "is our guess.");
    assert!(restated(&root, &class(&labeled), &mut pages).is_empty());
    put(&root, PAGE, &page("ATTESTED", "historically accurate"));
    // attested, it is a fact
    assert!(restated(&root, &class(&said), &mut Pages::default()).is_empty());
    let short = page("GUESS", "a GUESS").replace("The tree beside the shrine:", "A tree:");
    put(&root, PAGE, &short);
    // a head under three words is too short to match
    let tree = class(&said.replace("is old", "is a tree"));
    assert!(restated(&root, &tree, &mut Pages::default()).is_empty());
}

/// THE LABEL CHECK over the real tree: every modal's Guesses reference names a tagged item, every tagged page's tags are sound, and no
/// About states a tagged guess as a fact (feature 451 T187; each failure carries its fix).
#[test]
fn the_record_s_tags_and_every_pop_up_agree() {
    let tree = Path::new(env!("CARGO_MANIFEST_DIR")).join("../../../..");
    let mut faults = Vec::new();
    for entry in std::fs::read_dir(tree.join(super::QUESTIONS))
        .unwrap()
        .map(Result::unwrap)
    {
        let name = entry.file_name().to_string_lossy().into_owned();
        let text = std::fs::read_to_string(entry.path()).unwrap();
        faults.extend(l7r_gate_research::record::items::faults(&name, &text));
    }
    let mut pages = Pages::default();
    let mut files: Vec<_> = walk(&tree.join(crate::about::MODALS));
    files.sort();
    let read = |f: &std::path::PathBuf| {
        (
            std::fs::read_to_string(f).unwrap(),
            f.file_name().unwrap().to_string_lossy().into_owned(),
        )
    };
    let parse = |(text, name): (String, String)| {
        parse_explanation(Some(&text), &name).and_then(|p| about_feature(&name, &name, &p))
    };
    for fc in files.iter().map(read).filter_map(|t| parse(t).ok()) {
        faults.extend(restated(&tree, &fc, &mut pages));
        resolve(&tree, fc).unwrap();
    }
    let faults = faults.join("\n");
    assert!(faults.is_empty(), "the item labels disagree:\n{faults}");
}

fn walk(dir: &Path) -> Vec<std::path::PathBuf> {
    let paths = std::fs::read_dir(dir).unwrap().map(|e| e.unwrap().path());
    paths
        .flat_map(|p| if p.is_dir() { walk(&p) } else { vec![p] })
        .collect()
}

/// 451 T200: an item moved to another question's page is found there while exactly one other question tags its id; two make the
/// reference ambiguous, refused naming both.
#[test]
fn a_moved_item_is_found_on_the_one_other_question_that_tags_it() {
    let root = scratch("registry-items-moved");
    put(
        &root,
        "research/questions/0218-the-compounds-own-shrine-yashikigami.html",
        "<p>The shrine.</p>",
    );
    put(
        &root,
        "research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html",
        &page("GUESS", "a GUESS"),
    );
    assert_eq!(
        guesses(&root),
        [
            "[layout=row] The tree beside the shrine: no account gives it as the custom",
            "A garden: no account."
        ]
    );
    put(
        &root,
        "research/questions/0026-mulberry-and-other-crops-on-pond-dikes-sangji-guoji.html",
        &page("ATTESTED", "historically accurate"),
    );
    let said = resolve(&root, class(MODAL)).unwrap_err().message;
    let ambiguous = said.contains("questions 0026, 0036 each tag `tree` - write the one meant");
    assert!(ambiguous);
}

/// 451 T200: every page a reference read is told to the Mode A generation cache (`take_read`), so a relabel there regenerates a
/// cached sheet; a moved item's new page too.
#[test]
fn the_pages_a_reference_reads_are_told_to_the_cache() {
    let root = scratch("registry-items-read");
    put(&root, PAGE, &page("GUESS", "a GUESS"));
    put(
        &root,
        "research/questions/0218-the-compounds-own-shrine-yashikigami.html",
        "<p>The shrine.</p>",
    );
    let _ = guesses(&root);
    let read = super::take_read();
    assert!(read.contains(&root.join(PAGE)), "{read:?}");
    std::fs::remove_file(root.join(PAGE)).unwrap();
    put(
        &root,
        "research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html",
        &page("GUESS", "a GUESS"),
    );
    let _ = guesses(&root);
    assert!(super::take_read().contains(&root.join(
        "research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html"
    )));
}
