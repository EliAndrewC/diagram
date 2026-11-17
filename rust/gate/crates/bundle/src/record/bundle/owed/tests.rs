//! What a bundle is owed, refused and carries, on the testkit's record.

use std::collections::HashSet;

use super::*;
use crate::record::bundle::tests::scratch;
use crate::record::testkit::{edit_everything, put};

fn unit(slug: &str, occasion: &str) -> Unit {
    Unit {
        slug: slug.to_owned(),
        occasion: occasion.to_owned(),
        fingerprint: "fp".to_owned(),
        reading: String::new(),
    }
}

#[test]
fn a_question_bundle_is_owed_refused_or_escaped() {
    let root = scratch("bundle-owed-q");
    assert_eq!(question_of("94"), "0094");
    assert_eq!(question_of("x"), "x");
    assert_eq!(
        owed_for_question(&root, "0094", "record-style", "", None)
            .unwrap()
            .1,
        "record-style"
    );
    let (rows, checks, why) = owed_for_question(&root, "0094", "all", "", None).unwrap();
    assert!(rows.is_empty() && checks.is_empty());
    assert!(
        why.contains("no record check is owed on question 0094")
            && why.contains("(nothing: no record check")
    );
    let why = owed_for_question(&root, "0094", "quote-check", "x", None)
        .unwrap()
        .2;
    assert!(why.starts_with("NOT_OWED_OK needs a REASON"));
}

/// What was one test of a question bundle owed, refused or escaped is four, each on a scratch record of its own: its nine owed
/// computations together were past FR-008's tenth of a second (feature 449 T167).
#[test]
fn a_question_bundle_escaped_with_a_reason_is_owed_every_check() {
    let root = scratch("bundle-owed-q-escaped");
    let (rows, checks, _) =
        owed_for_question(&root, "0094", "all", "an audit asked", None).unwrap();
    assert_eq!(
        checks,
        "intro-check record-format quote-check translation-check"
    );
    assert!(
        rows.iter().any(|u| u.slug == "quote-check:0094#k")
            && rows
                .iter()
                .any(|u| u.slug == "quote-check:0094.drawing#unfootnoted")
    );
    assert_eq!(
        owed_for_question(&root, "0094", "quote-check", "an audit asked", None)
            .unwrap()
            .1,
        "quote-check"
    );
}

#[test]
fn an_edited_question_is_owed_and_another_refused() {
    let root = scratch("bundle-owed-q-edited");
    edit_everything(&root);
    let (rows, checks, why) = owed_for_question(&root, "0094", "all", "", None).unwrap();
    assert!(why.is_empty() && !rows.is_empty() && checks.contains("quote-check"));
    let refused = owed_for_question(&root, "0095", "quote-check", "", None)
        .unwrap()
        .2;
    assert!(refused.contains("What IS owed:\n    "));
}

/// A drawing page's own units, and an entry-drift asked of rows already in hand.
#[test]
fn a_drawing_page_is_owed_its_own_units() {
    let root = scratch("bundle-owed-q-page");
    edit_everything(&root);
    let page = owed_for_question(&root, "0094-trade.drawing.html", "all", "", None)
        .unwrap()
        .0;
    assert!(page
        .iter()
        .all(|u| !u.subject().contains('#') || u.subject().contains(".drawing")));
    let drift = owed_for_question(
        &root,
        "0094",
        "entry-drift",
        "an audit asked",
        Some(&[unit("entry-drift:well", "o")]),
    )
    .unwrap();
    assert_eq!(drift.0.len(), 1);
}

#[test]
fn a_key_bundle_is_owed_refused_or_escaped() {
    let root = scratch("bundle-owed-key");
    let why = owed_for_key(&root, "key-a", false, "", "", None).unwrap().2;
    assert!(why.contains("its write-up did not change. NOT_OWED_OK"));
    let why = owed_for_key(&root, "key-a", true, "", "", None).unwrap().2;
    assert!(why.contains("its notes did not change. NEW="));
    assert!(owed_for_key(&root, "key-a", true, "", "x", None)
        .unwrap()
        .2
        .starts_with("NEW needs"));
    assert!(owed_for_key(&root, "key-a", false, "x", "", None)
        .unwrap()
        .2
        .starts_with("NOT_OWED_OK needs"));
    assert_eq!(
        owed_for_key(&root, "key-a", true, "", "a claim read", None)
            .unwrap()
            .1,
        "source-reader"
    );
}

/// An edited write-up owes its applicability check and edited notes their reader: apart from the refusals above, on a scratch record of
/// its own - the seven owed computations together were at FR-008's tenth of a second (feature 449 T167).
#[test]
fn an_edited_key_is_owed_its_checks() {
    let root = scratch("bundle-owed-key-edited");
    edit_everything(&root);
    let (rows, check, _) = owed_for_key(&root, "key-a", false, "", "", None).unwrap();
    assert_eq!((rows.len(), check.as_str()), (1, "source-applicability"));
    let (rows, check, _) = owed_for_key(&root, "key-b", true, "", "", None).unwrap();
    assert_eq!((rows.len(), check.as_str()), (1, "source-reader"));
}

#[test]
fn the_lines_and_cuts_a_bundle_carries() {
    let rows = vec![
        unit("quote-check:0094#k", "a note changed"),
        unit("quote-check:0094#unfootnoted", ""),
        unit("entry-drift:well", "o"),
        unit("entry-drift:barn", ""),
    ];
    let text = manifest_lines(&rows, "quote-check", "a reason given");
    assert!(
        text.contains("not-owed: a reason given\nunit: quote-check:0094#k fp\n")
            && text.contains("owed: quote-check:0094#k - a note changed\n")
    );
    assert!(!manifest_lines(&rows, "x", "").contains("not-owed"));
    let batch: HashSet<String> = ["k".to_owned()].into();
    assert_eq!(batch_units(&rows, &batch, true).len(), 2);
    assert_eq!(batch_units(&rows, &HashSet::new(), false).len(), 0);
    assert_eq!(kind_units(&rows, "well").len(), 3);
    assert!(unfootnoted_owed(&rows) && !unfootnoted_owed(&rows[2..]));
    assert_eq!(owed_notes(&rows), ["k".to_owned()].into());
}

#[test]
fn the_intro_bundle_text() {
    let root = scratch("bundle-owed-intro");
    let mut docs = None;
    let text = intro_bundle_text(&root, "0094", &mut docs).unwrap();
    assert!(text.starts_with("=== QUESTION 0094 - origin `research/questions/0094-trade.html`"));
    assert!(
        text.contains("--- how our maps draw it")
            && text.contains("--- the map elements written from it")
    );
    let other = intro_bundle_text(&root, "0095", &mut docs).unwrap();
    assert!(other.contains("- NoticeBoard") && !other.contains("how our maps draw it"));
    assert_eq!(intro_bundle_text(&root, "0777", &mut docs).unwrap(), "");
    put(
        &root,
        "l7r/diagram/interactive/assets/modals/hamlet/privy.md",
        "Name: The named one\nAbout: x\nEntry: research/questions/0095-other.html\n",
    );
    let named = intro_bundle_text(&root, "0095", &mut None).unwrap();
    assert!(named.contains("- The named one"));
    std::fs::write(root.join("research/questions/0095-other.html"), [0xff]).unwrap();
    assert!(intro_bundle_text(&root, "0095", &mut None).is_err());
    // a modal file that cannot be read (a class module that did not lex, before feature 449 T149)
    std::fs::write(
        root.join("l7r/diagram/interactive/assets/modals/hamlet/privy.md"),
        [0xff],
    )
    .unwrap();
    put(&root, "research/questions/0095-other.html", "<h2>x</h2>");
    assert!(intro_bundle_text(&root, "0095", &mut None).is_err());
    std::fs::write(
        root.join("research/questions/0094-trade.drawing.html"),
        [0xff],
    )
    .unwrap();
    assert!(intro_bundle_text(&root, "0094", &mut Some(Vec::new())).is_err());
    assert!(reason_ok("two words"));
}

#[test]
fn a_question_no_modal_draws_from() {
    let root = scratch("bundle-owed-unnamed");
    put(
        &root,
        "research/questions/0096-alone.html",
        "<h2 id=\"alone\">Alone</h2>\n<p>x</p>\n",
    );
    assert!(intro_bundle_text(&root, "0096", &mut None)
        .unwrap()
        .contains("- (none: no modal's Entry names this question)"));
}
