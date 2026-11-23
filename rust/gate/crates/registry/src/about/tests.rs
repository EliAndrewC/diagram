//! The About form read and refused as `_base.py` reads and refuses it (feature 449 T149; each expected message the Python's own words).

use super::{
    about_feature, about_paragraphs, classes, compound_classes, feature, get, guess_bullets,
    install_siblings, modal_rel, modal_text, not_highlighted, parse_explanation, sibling_pairs,
    slug, FeatureClass,
};
use crate::kinds::{HAMLET_REGISTRY, SHEET_REGISTRY};
use l7r_gate_core::checks::scratch;
use l7r_gate_core::record::testkit::put;

fn parts(text: &str) -> Vec<(String, String)> {
    parse_explanation(Some(text), "K").unwrap()
}

fn refused(text: &str) -> String {
    let e = parse_explanation(Some(text), "K")
        .and_then(|p| about_feature("K", "k", &p))
        .unwrap_err();
    format!("{}: {}", e.kind, e.message)
}

const DATA: &str = "Name: N\nCovers: c\nSources: a, , b\nEntry: research/questions/x.html\n";

#[test]
fn the_text_s_tags_are_read_in_their_order() {
    let got = parts("About: one\n  two\n\n\n three\n\nGuesses:\n- a\n  b\n- c\nDepiction: d\nName: N\nAbout: again\n");
    assert_eq!(get(&got, "About"), "again");
    assert_eq!(get(&got, "Guesses"), "- a b\n- c");
    assert_eq!(got[0].0, "About");
    assert_eq!(
        get(&parts("About: one\n  two\n\n\n three\n"), "About"),
        "one two\n\nthree"
    );
    // a tab expands as `inspect.cleandoc` expands it, to the next multiple of eight
    assert_eq!(
        get(&parts("About: a\tb\rName: x\ty"), "About"),
        "a        b"
    );
    assert_eq!(get(&parts("About: a\tb\rName: x\ty"), "Name"), "x y");
    // a guess's first line, not a bullet, opens the list; a blank line in Depiction breaks its paragraph
    assert_eq!(
        get(
            &parts("About: a\nGuesses: first\nmore\nDepiction: p\n\nq\n"),
            "Guesses"
        ),
        "first more"
    );
    assert_eq!(
        get(&parts("About: a\nDepiction:\n\np\n\nq\n"), "Depiction"),
        "p\n\nq"
    );
    assert_eq!(about_paragraphs("a  b\n\n \n\nc"), ["a b", "c"]);
    assert_eq!(guess_bullets("- a \n\n-  b"), ["a", "b"]);
    assert_eq!(get(&got, "Nothing"), "");
}

#[test]
fn a_text_with_no_about_or_a_line_before_its_tags_is_refused() {
    for (text, want) in [
        (None, "K: the explanation is the docstring, and there is none"),
        (Some("  \n "), "K: the explanation is the docstring, and there is none"),
        (Some("Stray 'line'\nAbout: x"), "K: text before the first tag (\"Stray 'line'\") - every line belongs to a tag, About: first"),
        (Some("Name: n\n"), "K: the docstring has no About: section"),
        (Some("About:\n"), "K: the docstring has no About: section"),
    ] {
        let e = parse_explanation(text, "K").unwrap_err();
        assert_eq!((e.kind, e.message.as_str()), ("ValueError", want));
    }
}

#[test]
fn the_about_form_takes_what_it_takes() {
    let ok = format!("About: a\n\n[winter_crop=wheat] b\nGuesses:\n- g\nDepiction: d\nDrawing: research/questions/x.drawing.html\nForm: particular\n{DATA}");
    let fc = about_feature("K", "k", &parts(&ok)).unwrap();
    assert_eq!(
        fc,
        FeatureClass {
            key: "k".into(),
            name: "N".into(),
            covers: "c".into(),
            sources: vec!["a".into(), "b".into()],
            entry: "research/questions/x.html".into(),
            siblings: vec![],
            about: vec!["a".into(), "[winter_crop=wheat] b".into()],
            guesses: vec!["g".into()],
            form: "particular".into(),
            depiction: vec!["d".into()],
            drawing: "research/questions/x.drawing.html".into(),
        }
    );
    assert_eq!(fc.json()["siblings"], serde_json::json!({}));
    assert_eq!(
        about_feature("K", "k", &parts(&format!("About: a\n{DATA}")))
            .unwrap()
            .form,
        "standard"
    );
    for (text, want) in [
        ("About: a\nName: N\n".to_owned(), "ValueError: K: the docstring has no Covers: section"),
        (format!("About: a\nLabel: GUESS\n{DATA}"), "ValueError: K: the About form takes no Label: - a guess is a bullet under Guesses: (dev/modals.md M11)"),
        (format!("About: a\nWhy: w\nNote: n\n{DATA}"), "ValueError: K: the About form replaces What/Why/Note/Caveat - remove Why:, Note:"),
        (format!("About: a\nForm: odd\n{DATA}"), "ValueError: K: Form: 'odd' is not one of ['particular', 'standard']"),
        (format!("About: a\nForm:\n{DATA}"), "ValueError: K: Form: '' is not one of ['particular', 'standard']"),
        (format!("About: a\n{DATA}").replace("x.html", "x.drawing.html"), "ValueError: K: a 'how our maps draw it' page belongs under Drawing:, not Entry: (the Depiction tab - dev/modals.md D-rules)"),
        (format!("About: a\nGuesses:\n- on the older hand-drawn maps it was\n{DATA}"), "ValueError: K: Guesses: names the older maps ('older hand-drawn maps') - they will all be scripted before anyone else reads this; say what the scripted maps do and drop the exception (dev/modals.md M21)"),
        (format!("About: a\nGuesses: g\n{DATA}"), "ValueError: K: each guess is a bullet - start every line under Guesses: with '- '"),
        (format!("About: [Bad=x] a\n{DATA}"), "ValueError: K: a modal condition is written [knob=value] or [knob=value|value], lower case: '[Bad=x] a' (dev/modals.md M22)"),
    ] {
        assert_eq!(refused(&text), want);
    }
}

#[test]
fn siblings_are_installed_both_ways_and_an_unknown_one_refused() {
    let fc = |key: &str| FeatureClass {
        key: key.into(),
        ..FeatureClass::default()
    };
    let pair = |a: &str, b: &str, t: &str| ((a.to_owned(), b.to_owned()), t.to_owned());
    let got = install_siblings(
        vec![fc("a"), fc("b"), fc("c"), fc("a")],
        &[
            pair("a", "b", "x"),
            pair("c", "a", "y"),
            pair("b", "a", "z"),
        ],
    )
    .unwrap();
    assert_eq!(got.len(), 3);
    assert_eq!(
        got[0].siblings,
        [
            ("b".to_owned(), "z".to_owned()),
            ("c".to_owned(), "y".to_owned())
        ]
    );
    assert_eq!(got[1].siblings, [("a".to_owned(), "z".to_owned())]);
    let e = install_siblings(vec![fc("a")], &[pair("a", "nope", "x")]).unwrap_err();
    assert_eq!(
        (e.kind, e.message.as_str()),
        (
            "KeyError",
            "sibling pair names an unknown class: ('a', 'nope')"
        )
    );
}

#[test]
fn the_registries_load_from_their_files() {
    let root = scratch("registry-about");
    assert!(sibling_pairs(&root).is_err());
    crate::testkit::modals(&root, "research/questions/x.html");
    put(&root, "l7r/diagram/interactive/assets/siblings.json", "{\"texts\": {\"t\": \"shared\"}, \"pairs\": [[\"farmhouse\", \"storage shed\", \"@t\"], [\"byre\", \"garden\", \"own\"], [\"byre\", \"garden\", \"again\"]]}");
    let pairs = sibling_pairs(&root).unwrap();
    assert_eq!(pairs.len(), 2);
    assert_eq!(pairs[1].1, "again");
    let hamlet = classes(&root).unwrap();
    assert_eq!((hamlet.len(), hamlet[0].key.as_str()), (61, "farmhouse"));
    assert_eq!(
        hamlet[0].siblings,
        [("storage shed".to_owned(), "shared".to_owned())]
    );
    assert_eq!(
        hamlet[0].json()["siblings"],
        serde_json::json!({"storage shed": "shared"})
    );
    assert_eq!(compound_classes(&root).unwrap().len(), 101);
    put(
        &root,
        "l7r/diagram/interactive/assets/siblings.json",
        "{\"texts\": {}, \"pairs\": [[\"farmhouse\", \"byre\", \"@gone\"]]}",
    );
    assert_eq!(classes(&root).unwrap_err().message, "gone");
    // a kind with no file is the Python's kind with no text; a file that is not UTF-8 cannot be read
    let farmhouse = modal_rel(&HAMLET_REGISTRY, "farmhouse");
    std::fs::remove_file(root.join(&farmhouse)).unwrap();
    assert_eq!(
        modal_text(&root, &HAMLET_REGISTRY, "farmhouse").unwrap(),
        None
    );
    assert_eq!(
        feature(&root, &HAMLET_REGISTRY, "Farmhouse", "farmhouse")
            .unwrap_err()
            .message,
        "Farmhouse: the explanation is the docstring, and there is none"
    );
    std::fs::write(root.join(&farmhouse), [0xff]).unwrap();
    assert_eq!(
        modal_text(&root, &HAMLET_REGISTRY, "farmhouse")
            .unwrap_err()
            .kind,
        "OSError"
    );
    assert_eq!(
        modal_rel(&SHEET_REGISTRY, "karo's house"),
        "l7r/diagram/interactive/assets/modals/sheet/karo-s-house.md"
    );
    assert_eq!(slug("A b-9'c"), "a-b-9-c");
}

#[test]
fn the_not_highlighted_rulings_are_read_from_the_page_text() {
    let root = scratch("registry-rulings");
    assert!(not_highlighted(&root).is_err());
    put(
        &root,
        "l7r/diagram/interactive/assets/page-text.json",
        "{\"not_highlighted_rulings\": [[\"a\", \"b\", \"c\", \"d\"]]}",
    );
    let (rulings, overturned) = not_highlighted(&root).unwrap();
    assert_eq!(rulings, [["a", "b", "c", "d"].map(str::to_owned)]);
    assert!(overturned.is_empty());
}
