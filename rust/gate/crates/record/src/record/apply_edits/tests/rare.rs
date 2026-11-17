//! The rarer paths of a run (feature 449 T145), one after another on one record until feature 449 T167 cut them into parts, each on a
//! record of its own: every round with EDITs reads what is owed before and after its blocks, nine git processes a reading, and the one
//! test took over FR-008's tenth of a second; a part starts from the files as the parts before it left them, written where it needs them.

use std::os::unix::fs::PermissionsExt as _;

use l7r_gate_core::record::testkit::{put, record, NOTES, PAGE};

use super::{assemblable, edit, page, run, scratch};

/// A record with an assembled registry.
fn assembled(tag: &str) -> l7r_guard::shared::tempdir::TempDir {
    let root = record(tag);
    assemblable(&root);
    root
}

#[test]
fn the_rarer_paths_of_a_run() {
    let root = assembled("apply-edits-rare");
    assert_eq!(
        super::super::round::named("plain words"),
        "ValueError: plain words"
    );
    assert_eq!(super::super::round::named("KeyError: 'x'"), "KeyError: 'x'");
    // a modal-form EDIT on a record file: no pop-up, so nothing research fixed
    let not_modal = run(
        &root,
        &format!(
            "modal-form: x - 1\n{}",
            edit(PAGE, "More here.", Some("More, here."))
        ),
        &[],
    );
    assert!(not_modal.stdout.contains("applied to 0094-trade.html"));
    // a dry run reads and writes nothing
    let dry = run(
        &root,
        &format!(
            "quote-check: x\n{}",
            edit(PAGE, "More, here.", Some("More here."))
        ),
        &["--dry-run"],
    );
    assert!(
        dry.stdout.contains("applied to 0094-trade.html") && page(&root).contains("More, here.")
    );
}

#[test]
fn a_modal_form_edit_that_drops_what_research_fixed_is_refused() {
    let root = assembled("apply-edits-held");
    put(
        &root,
        "l7r/diagram/interactive/assets/modals/classes/y.md",
        "About: a fixed fact and more.\n",
    );
    super::super::HELD
        .with(|h| *h.borrow_mut() = Some(vec!["a fixed fact".to_owned(), "and more".to_owned()]));
    let y = "l7r/diagram/interactive/assets/modals/classes/y.md";
    let dropped = run(
        &root,
        &format!(
            "modal-form: y - 1\n{}",
            edit(y, "a fixed fact and more", Some("a fixed fact"))
        ),
        &[],
    );
    assert!(
        dropped.stdout.contains(
            "REFUSED - a modal-form EDIT drops wording a research round fixed ('and more')"
        ),
        "{}",
        dropped.stdout
    );
    let kept = run(
        &root,
        &format!("modal-form: y - 1\n{}", edit(y, "About:", Some("About -"))),
        &[],
    );
    assert!(kept.stdout.contains("applied to y.md"));
    super::super::HELD.with(|h| *h.borrow_mut() = None);
}

#[test]
fn a_record_format_round_whose_blocks_raise_no_new_word_settles_its_unit() {
    let root = assembled("apply-edits-rare-calm");
    let comma = page(&root).replace("More here.", "More, here.");
    std::fs::write(root.join(PAGE), comma).unwrap();
    let calm = run(
        &root,
        &format!(
            "record-format: 0094 - 1\nGLOSSARY quiet | | a def\n{}",
            edit(PAGE, "More, here.", Some("More here."))
        ),
        &[],
    );
    assert!(
        calm.stdout
            .contains("apply-edits: 2 block(s), 0 refused - then `make glossary`"),
        "{}",
        calm.stdout
    );
}

#[test]
fn another_check_s_fix_outside_a_quotation_on_a_note_nothing_owed_is_settled() {
    let root = assembled("apply-edits-rare-fresh");
    let note = std::fs::read_to_string(root.join(NOTES))
        .unwrap()
        .lines()
        .find(|l| l.contains("data-note=\"k\""))
        .unwrap()
        .to_owned();
    let fresh = run(
        &root,
        &format!(
            "record-format: 0094 - 1\n{}",
            edit(NOTES, &note, Some(&note.replace("</li>", " Also.</li>")))
        ),
        &[],
    );
    assert!(
        fresh
            .stdout
            .contains("quote-check:0094#k: settled - another check's fix"),
        "{}",
        fresh.stdout
    );
}

#[test]
fn a_store_that_cannot_be_written_and_a_ledger_held_or_unreadable() {
    let root = assembled("apply-edits-rare-store");
    // the note the part above moved, as it left it: what makes the quote-check units owed
    let notes = std::fs::read_to_string(root.join(NOTES)).unwrap();
    let k = notes
        .lines()
        .find(|l| l.contains("data-note=\"k\""))
        .unwrap()
        .to_owned();
    let also = notes.replace(&k, &k.replace("</li>", " Also.</li>"));
    std::fs::write(root.join(NOTES), also).unwrap();
    // the store cannot be written: the round cannot settle, and the edits stand
    let store = crate::record::owed::answers::store(&root);
    let _ = std::fs::remove_dir_all(&store);
    std::fs::write(&store, "a file where the store goes").unwrap();
    let unsettled = run(
        &root,
        &format!(
            "quote-check: 0094 - 1\n{}",
            edit(PAGE, "More here.", Some("More here, now."))
        ),
        &[],
    );
    assert!(unsettled.stdout.contains("could not settle ("));
    std::fs::remove_file(&store).unwrap();
    // a glossary term another clone holds, and a ledger that cannot be read
    std::fs::create_dir_all(root.join(".specify")).unwrap();
    std::fs::write(
        root.join(".specify/prefixes.jsonl"),
        "{\"kind\": \"glossary\", \"key\": \"held\", \"prefix\": 5, \"clone\": \"/elsewhere\"}\n",
    )
    .unwrap();
    assert!(
        run(&root, "record-format: 0094\nGLOSSARY held | | d\n", &[])
            .stdout
            .contains("REFUSED - 'held' is already being defined in /elsewhere")
    );
    std::fs::write(root.join(".specify/prefixes.jsonl"), "[1]\n").unwrap();
    assert_eq!(
        run(&root, "record-format: 0094\nGLOSSARY other | | d\n", &[]).code,
        1
    );
}

#[test]
fn a_file_that_cannot_be_read_is_refused() {
    let root = assembled("apply-edits-rare-bad");
    put(&root, &scratch("bad"), "x");
    std::fs::write(root.join(scratch("bad")), [0xff]).unwrap();
    assert_eq!(
        run(
            &root,
            &format!("quote-check: x\n{}", edit(&scratch("bad"), "a", Some("b"))),
            &["--dry-run"]
        )
        .code,
        1
    );
    assert_eq!(
        run(
            &root,
            &format!("quote-check: x\n{}", edit(&scratch("bad"), "a", Some("b"))),
            &[]
        )
        .code,
        1
    );
}

#[test]
fn a_file_that_cannot_be_written_is_refused() {
    let root = assembled("apply-edits-rare-locked");
    put(&root, &scratch("locked"), "old\n");
    std::fs::set_permissions(
        root.join(scratch("locked")),
        std::fs::Permissions::from_mode(0o444),
    )
    .unwrap();
    assert_eq!(
        run(
            &root,
            &format!(
                "quote-check: x\n{}",
                edit(&scratch("locked"), "old", Some("new"))
            ),
            &[]
        )
        .code,
        1
    );
    std::fs::write(root.join(scratch("locked2")), "new\n").unwrap();
    std::fs::set_permissions(
        root.join(scratch("locked2")),
        std::fs::Permissions::from_mode(0o444),
    )
    .unwrap();
    assert_eq!(
        run(
            &root,
            &format!(
                "quote-check: x\n{}",
                edit(&scratch("locked2"), "old", Some("new"))
            ),
            &[]
        )
        .code,
        1
    );
}
