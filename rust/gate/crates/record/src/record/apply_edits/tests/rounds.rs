//! The round's settling: a reply that names no check, a round whose units cannot be read, an edit found applied by hand, and each unit
//! the blocks alone moved, settled or still owed (feature 449 T145). Feature 449 T167 cut its two tests into parts, each on a record of
//! its own: every round with EDITs reads what is owed before and after its blocks, nine git processes a reading, and each of the two
//! took over FR-008's tenth of a second; a part starts from the files as the parts before it left them, written where it needs them.

use std::path::Path;

use l7r_gate_core::record::testkit::{edit_everything, record, NOTES, PAGE, WELL};

use super::super::cli;
use super::{assemblable, edit, page, run};
use crate::record::owed::{self, answers};
use crate::record::units;

const KYAKHTA: &str =
    "<p>A short distance apart.<sup class=\"fn\" data-note=\"k\"></sup> More here, now.</p>";

/// A record with every kind of owed edit in its working tree, and the page's line the round tests edit.
fn edited(tag: &str) -> (l7r_shared::tempdir::TempDir, String, String) {
    let root = record(tag);
    edit_everything(&root);
    let current = page(&root);
    let old = current
        .lines()
        .find(|l| l.contains("A short distance apart"))
        .unwrap()
        .to_owned();
    (root, current, old)
}

#[test]
fn a_round_settles_and_a_reply_with_no_check_says_so() {
    let (root, _, old) = edited("apply-edits-round");
    let none = run(
        &root,
        &format!(
            "a reply with no counts line\n{}",
            edit(PAGE, &old, Some(KYAKHTA))
        ),
        &[],
    );
    assert!(none
        .stdout
        .contains("apply-edits: the reply names no check, so the units it answered stay owed"));
    let back = run(
        &root,
        &format!(
            "quote-check: 0094 - 1 finding\n{}",
            edit(PAGE, KYAKHTA, Some(&old))
        ),
        &[],
    );
    assert!(
        back.stdout
            .contains("apply-edits: the quote-check round's own EDITs, applied verbatim:"),
        "{}",
        back.stdout
    );
}

#[test]
fn a_round_whose_units_cannot_be_read_says_so_and_its_edits_stand() {
    let (root, _, old) = edited("apply-edits-unread");
    // a record-format round reads the prepass, which needs the registry assembled; this record's has no front matter
    let unread = run(
        &root,
        &format!(
            "record-format: 0094 - 1 finding\n{}",
            edit(PAGE, &old, Some(KYAKHTA))
        ),
        &[],
    );
    assert!(
        unread
            .stdout
            .contains("apply-edits: could not read the round's units (RecordError: "),
        "{}",
        unread.stdout
    );
    let notes = std::fs::read_to_string(root.join(NOTES)).unwrap();
    let note_line = notes
        .lines()
        .find(|l| l.contains("data-note=\"n\""))
        .unwrap()
        .to_owned();
    let moved = run(
        &root,
        &format!(
            "record-format: 0094 - 1\n{}",
            edit(NOTES, &note_line, Some(&note_line.replace("<li", "<li  ")))
        ),
        &[],
    );
    assert_eq!(moved.code, 0, "{}", moved.stdout);
}

#[test]
fn an_edit_found_applied_by_hand_is_settled_through_its_reply() {
    let (root, current, old) = edited("apply-edits-hand");
    std::fs::write(root.join(PAGE), current.replace(&old, KYAKHTA)).unwrap();
    let hand = run(
        &root,
        &format!("quote-check: 0094 - 1\n{}", edit(PAGE, &old, Some(KYAKHTA))),
        &[],
    );
    assert!(hand
        .stdout
        .contains("found applied by hand - settled through its reply"));
}

#[test]
fn a_skipped_block_the_refused_command_lines_and_a_tree_that_is_no_repository() {
    let (root, current, old) = edited("apply-edits-skip");
    let skipped = run(
        &root,
        &format!("quote-check: x\n{}", edit(PAGE, "no such", Some("x"))),
        &["--skip", "1"],
    );
    assert!(skipped.stdout.contains("  1. skipped (--skip)"));
    assert_eq!(run(&root, "quote-check: x\n", &[]).code, 2);
    assert_eq!(
        run(
            &root,
            &format!("quote-check: x\n{}", edit(PAGE, "a", Some("b"))),
            &["--skip", "1,x"]
        )
        .code,
        1
    );
    assert_eq!(cli(&["none.md".to_owned()], &root).code, 1);
    assert_eq!(cli(&[], &root).code, 2);
    assert_eq!(cli(&["r".to_owned(), "--bogus".to_owned()], &root).code, 2);
    std::fs::write(root.join(PAGE), current.replace(&old, KYAKHTA)).unwrap();
    std::fs::remove_dir_all(root.join(".git")).unwrap();
    let plain = run(
        &root,
        &format!("quote-check: 0094\n{}", edit(PAGE, KYAKHTA, Some(&old))),
        &[],
    );
    assert!(!plain.stdout.contains("round's own EDITs"));
}

/// A record with every kind of owed edit and an assembled registry, and its answer store.
fn settling(tag: &str) -> (l7r_shared::tempdir::TempDir, std::path::PathBuf) {
    let root = record(tag);
    edit_everything(&root);
    assemblable(&root);
    let store = answers::store_in(&l7r_shared::env::Rooted::with(&*root, &[]));
    (root, store)
}

/// Every note line of the notes with " Grounds: more." added, as the record-format round of
/// `a_round_settles_another_check_s_quote_but_not_a_word_its_prepass_now_raises` leaves them.
fn grounds(root: &Path) -> String {
    std::fs::read_to_string(root.join(NOTES))
        .unwrap()
        .lines()
        .filter(|l| l.starts_with("<li"))
        .map(|l| edit(NOTES, l, Some(&l.replace("</li>", " Grounds: more.</li>"))))
        .collect()
}

/// The notes as that round leaves them, written by hand.
fn with_grounds(root: &Path) {
    let notes = std::fs::read_to_string(root.join(NOTES)).unwrap();
    let grounded: String = notes
        .lines()
        .map(|l| {
            if l.starts_with("<li") {
                l.replace("</li>", " Grounds: more.</li>")
            } else {
                l.to_owned()
            }
        })
        .fold(String::new(), |all, l| all + &l + "\n");
    std::fs::write(root.join(NOTES), grounded).unwrap();
}

#[test]
fn a_round_settles_what_its_blocks_alone_moved() {
    let (root, store) = settling("apply-edits-settle");
    let research: Vec<(String, String)> =
        owed::fingerprints(&root, &["modal-accuracy".to_owned()]).unwrap();
    for (slug, fp) in &research {
        answers::write_answer(&store, slug, fp, "1 finding", None).unwrap();
    }
    let depiction = run(
        &root,
        &format!(
            "modal-depiction: well - 1 finding\n{}",
            edit(WELL, "It is deep.", Some("It is very deep."))
        ),
        &[],
    );
    assert!(depiction.stdout.contains("modal-accuracy:hamlet/well: settled with its answer - the modal-depiction round's blocks alone moved it (it runs before them)"), "{}", depiction.stdout);
    assert!(depiction.stdout.contains(
        "modal-gaps:hamlet/well: still owed - not answered at the words before these blocks"
    ));
}

#[test]
fn a_round_settles_another_check_s_quote_but_not_a_word_its_prepass_now_raises() {
    let (root, store) = settling("apply-edits-grounds");
    // the first owed quote-check unit answered, `0094#k`, at its fingerprint read from the record as the round reads it: the owed
    // reading of every unit is nine git processes, and with it the test sat at FR-008's tenth of a second; the two readings give the
    // same fingerprint for every owed quote-check and record-format unit of this record (feature 449 T167, observed 2026-11-17, method:
    // both compared in the crate's test build)
    let rec = owed::read_at(&root, None, Some(&std::collections::HashSet::new())).unwrap();
    let k = "quote-check:0094#k";
    answers::write_answer(&store, k, &units::fingerprint(&rec, k), "0 findings", None).unwrap();
    let blocks = grounds(&root);
    let format = run(
        &root,
        &format!(
            "record-format: 0094 - 2 findings\n{blocks}{}",
            edit(PAGE, "More here.", Some("More here. Grounds: added."))
        ),
        &[],
    );
    assert!(format.stdout.contains("record-format:0094: still owed - its prepass now raises Grounds:, added, grounds, which the round never ruled on"), "{}", format.stdout);
    assert!(format.stdout.contains(
        "quote-check:0094#k: settled - another check's fix, outside its quotation and its claim"
    ));
    assert!(format.stdout.contains(
        "quote-check:0094#n: still owed - not answered at the words before these blocks"
    ));
}

#[test]
fn a_round_raising_no_new_word_settles_when_it_is_recorded() {
    let (root, _) = settling("apply-edits-calm");
    with_grounds(&root);
    let grounded = page(&root).replace("More here.", "More here. Grounds: added.");
    std::fs::write(root.join(PAGE), grounded).unwrap();
    let calm = run(
        &root,
        &format!(
            "record-format: 0094 - 1\n{}",
            edit(PAGE, "More here. Grounds: added.", Some("More here."))
        ),
        &[],
    );
    assert!(
        calm.stdout
            .contains("record-format:0094: settles when `make record-checked` records this round"),
        "{}",
        calm.stdout
    );
}

#[test]
fn a_round_whose_answer_stands_at_the_words_before_its_blocks_settles_with_it() {
    let (root, store) = settling("apply-edits-answered");
    with_grounds(&root);
    // the one owed record-format unit answered at its fingerprint read as the round reads it (feature 449 T167, as above)
    let rec = owed::read_at(&root, None, Some(&std::collections::HashSet::new())).unwrap();
    let unit = "record-format:0094";
    answers::write_answer(
        &store,
        unit,
        &units::fingerprint(&rec, unit),
        "1 finding",
        None,
    )
    .unwrap();
    let answered = run(
        &root,
        &format!(
            "record-format: 0094 - 1\n{}",
            edit(PAGE, "More here.", Some("Here."))
        ),
        &[],
    );
    assert!(
        answered
            .stdout
            .contains("record-format:0094: settled with its answered round"),
        "{}",
        answered.stdout
    );
}

#[test]
fn a_quote_whose_quotation_moved_stays_owed() {
    let (root, _) = settling("apply-edits-inside");
    with_grounds(&root);
    let inside: String = std::fs::read_to_string(root.join(NOTES))
        .unwrap()
        .lines()
        .filter(|l| l.contains("data-note=\"n\""))
        .map(|l| edit(NOTES, l, Some(&l.replace("\"new\"", "\"newer\""))))
        .collect();
    let moved = run(&root, &format!("intro-check: 0094 - 1\n{inside}"), &[]);
    assert!(
        moved
            .stdout
            .contains("quote-check:0094#n: still owed - its quotation or its claim changed"),
        "{}",
        moved.stdout
    );
}
