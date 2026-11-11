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
    edit_everything(&root);
    let (rows, checks, why) = owed_for_question(&root, "0094", "all", "", None).unwrap();
    assert!(
        why.is_empty() && !rows.is_empty() && checks.contains("quote-check"),
        "{checks} {why}"
    );
    let refused = owed_for_question(&root, "0095", "quote-check", "", None)
        .unwrap()
        .2;
    assert!(refused.contains("What IS owed:\n    "), "{refused}");
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
            && text.contains("--- the map elements written from it"),
        "{text}"
    );
    let other = intro_bundle_text(&root, "0095", &mut docs).unwrap();
    assert!(
        other.contains("- Barn") && !other.contains("how our maps draw it"),
        "{other}"
    );
    assert_eq!(intro_bundle_text(&root, "0777", &mut docs).unwrap(), "");
    put(&root, "l7r/diagram/interactive/classes/more.py", "class Named(Kind):\n    \"\"\"Name: The named one\n    About: x\n    Entry: research/questions/0095-other.html\n    \"\"\"\n    key = \"named\"\n");
    let named = intro_bundle_text(&root, "0095", &mut None).unwrap();
    assert!(named.contains("- The named one"), "{named}");
    std::fs::write(root.join("research/questions/0095-other.html"), [0xff]).unwrap();
    assert!(intro_bundle_text(&root, "0095", &mut None).is_err());
    put(&root, "l7r/diagram/interactive/classes/bad.py", "class (\n");
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
