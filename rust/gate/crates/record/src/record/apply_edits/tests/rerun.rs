//! A re-run's wording EDIT on a pop-up answered before at its text is held and listed, not applied (451 T232); `RERUN_OK` applies it,
//! logged; a factual EDIT of a re-run applies, as a first round's does.

use std::path::Path;

use l7r_gate_core::record::testkit::WELL;

use super::{edit, run};
use crate::record::owed::{self, answers};

/// A scratch record whose `check` unit on hamlet/well was answered twice at its text, so a re-run; its store.
fn rerun_of(tag: &str, check: &str) -> (l7r_shared::tempdir::TempDir, std::path::PathBuf) {
    rerun_on(tag, check, "hamlet/well")
}

/// [`rerun_of`] on `subject`: a pop-up's unit or a research question's number.
fn rerun_on(
    tag: &str,
    check: &str,
    subject: &str,
) -> (l7r_shared::tempdir::TempDir, std::path::PathBuf) {
    let root = l7r_gate_core::record::testkit::record(tag);
    l7r_gate_core::record::testkit::edit_everything(&root);
    super::assemblable(&root);
    let store = answers::store_in(&l7r_shared::env::Rooted::with(&*root, &[]));
    let slug = format!("{check}:{subject}");
    // the mark is read against the unit's recorded fingerprint, which its next answer moves before any EDIT of it applies
    let fp = owed::fingerprints(&root, &[check.to_owned()])
        .unwrap()
        .into_iter()
        .find(|(s, _)| *s == slug)
        .map_or_else(|| "a1b2c3d4e5f60718".to_owned(), |p| p.1);
    answers::answer_unit(&store, &slug, &fp, "0 findings", None, "").unwrap();
    answers::answer_unit(&store, &slug, &fp, "1 finding (1 FIX)", None, "").unwrap();
    (root, store)
}

fn well(root: &Path) -> String {
    std::fs::read_to_string(root.join(WELL)).unwrap()
}

#[test]
fn a_re_run_s_wording_edit_on_text_answered_before_is_held_and_listed() {
    let (root, _) = rerun_of("apply-edits-rerun", "modal-form");
    let reply = format!(
        "modal-form: Well - 1 finding (1 FIX)\n{}",
        edit(WELL, "It is deep.", Some("It is a deep one."))
    );
    let said = run(&root, &reply, &[]);
    assert!(
        well(&root).contains("It is deep.") && !well(&root).contains("a deep one"),
        "{}",
        said.stdout
    );
    assert!(said.stdout.starts_with("apply-edits: held EDIT 1 (l7r/diagram/interactive/assets/modals/hamlet/well.md) - modal-form:hamlet/well was answered at this text before (was: 0 findings)"), "{}", said.stdout);
    assert!(
        said.stdout
            .contains("listed, not applied, kept in specs/_unfiled/noted.jsonl (451 T232)"),
        "{}",
        said.stdout
    );
    let rows = super::super::rerun::kept(&root);
    assert_eq!(rows.len(), 1, "{rows:?}");
    assert_eq!(rows[0]["block"], "EDIT 1");
    // a dry run holds nothing and says nothing of it
    let dry = run(&root, &reply, &["--dry-run"]);
    assert!(!dry.stdout.contains("451 T232"), "{}", dry.stdout);
    // a reason too short is refused; a reason applies it
    let short = run(&root, &reply, &["--rerun-ok", "now"]);
    assert_eq!(short.code, 2, "{}", short.stderr);
    let ok = run(&root, &reply, &["--rerun-ok", "the GM asked for it"]);
    assert!(
        ok.stdout.starts_with(
            "apply-edits: RERUN_OK - a re-run's EDITs applied on modal-form:hamlet/well (451 T232)"
        ),
        "{}",
        ok.stdout
    );
    assert!(well(&root).contains("It is a deep one."));
}

#[test]
fn a_re_run_s_factual_edit_and_a_first_round_s_apply() {
    // modal-research's findings are factual: a re-run's EDIT applies and cascades as a first round's does (451 T188)
    let (root, store) = rerun_of("apply-edits-rerun-fact", "modal-accuracy");
    // every check of the reply re-ran at this text, so only the EDIT's being factual lets it through
    let fp = answers::read_answer(&store, "modal-accuracy:hamlet/well")["fingerprint"]
        .as_str()
        .unwrap()
        .to_owned();
    for slug in ["modal-references:hamlet/well", "modal-gaps:hamlet/well"] {
        answers::answer_unit(&store, slug, &fp, "0 findings", None, "").unwrap();
        answers::answer_unit(&store, slug, &fp, "0 findings", None, "").unwrap();
    }
    let said = run(
        &root,
        &format!(
            "modal-research: Well - ACCURACY 1 findings; REFERENCES 0; GAPS 0\n{}",
            edit(WELL, "It is deep.", Some("It is a deep one."))
        ),
        &[],
    );
    assert!(!said.stdout.contains("451 T232"), "{}", said.stdout);
    assert!(well(&root).contains("It is a deep one."));
    // the form unit answered once: its round's wording EDIT applies, as before
    let root = l7r_gate_core::record::testkit::record("apply-edits-rerun-first");
    l7r_gate_core::record::testkit::edit_everything(&root);
    super::assemblable(&root);
    let said = run(
        &root,
        &format!(
            "modal-form: Well - 1 finding (1 FIX)\n{}",
            edit(WELL, "It is deep.", Some("It is a deep one."))
        ),
        &[],
    );
    assert!(!said.stdout.contains("451 T232"), "{}", said.stdout);
    assert!(well(&root).contains("It is a deep one."));
}

#[test]
fn a_hold_that_cannot_keep_its_note_or_log_its_escape_refuses() {
    let (root, _) = rerun_of("apply-edits-rerun-fail", "modal-form");
    let reply = format!(
        "modal-form: Well - 1 finding (1 FIX)\n{}",
        edit(WELL, "It is deep.", Some("It is a deep one."))
    );
    // the notes' directory and the bypass log's are files, so neither can be written
    l7r_gate_core::record::testkit::put(&root, "specs/_unfiled", "a file");
    l7r_gate_core::record::testkit::put(&root, "dev/bypass-log", "a file");
    let kept = run(&root, &reply, &[]);
    assert_eq!(kept.code, 2, "{}", kept.stdout);
    let logged = run(&root, &reply, &["--rerun-ok", "the GM asked for it"]);
    assert_eq!(logged.code, 2, "{}", logged.stdout);
    assert!(well(&root).contains("It is deep."));
}

fn text(root: &Path, file: &str) -> String {
    std::fs::read_to_string(root.join(file)).unwrap()
}

/// A research page's record check re-run on its text (451 T249): a record-format re-run's wording EDIT on its question - the page or
/// its drawing, one unit - is held and listed, while a first round's EDIT on another question of the same reply applies.
#[test]
fn a_re_run_s_wording_edit_on_a_research_page_answered_before_is_held_and_listed() {
    use l7r_gate_core::record::testkit::{DRAWING, PAGE};
    const OTHER: &str = "research/questions/0095-other.html";
    let (root, _) = rerun_on("apply-edits-rerun-page", "record-format", "0094");
    let reply = format!(
        "record-format: 0094, 0095 - 3 findings (3 EDIT)\n{}{}{}",
        edit(
            PAGE,
            "An unmarked claim, reworded.",
            Some("A claim, reworded.")
        ),
        edit(
            DRAWING,
            "Drawn as a line, thin.",
            Some("Drawn as a thin line.")
        ),
        edit(OTHER, "<p>Body.</p>", Some("<p>The body.</p>"))
    );
    let said = run(&root, &reply, &[]);
    assert!(
        text(&root, PAGE).contains("An unmarked claim, reworded."),
        "{}",
        said.stdout
    );
    assert!(
        text(&root, DRAWING).contains("Drawn as a line, thin."),
        "{}",
        said.stdout
    );
    assert!(
        text(&root, OTHER).contains("The body."),
        "{}{}",
        said.stdout,
        said.stderr
    );
    assert!(said.stdout.starts_with("apply-edits: held EDIT 1 (research/questions/0094-trade.html) - record-format:0094 was answered at this text before (was: 0 findings)"), "{}", said.stdout);
    assert!(said.stdout.contains("apply-edits: held EDIT 2 (research/questions/0094-trade.drawing.html) - record-format:0094"), "{}", said.stdout);
    let rows = super::super::rerun::kept(&root);
    assert_eq!(rows.len(), 2, "{rows:?}");
    assert_eq!(rows[0]["units"], "record-format:0094");
    // RERUN_OK applies them, as for a pop-up
    let ok = run(&root, &reply, &["--rerun-ok", "the GM asked for it"]);
    assert!(ok.stdout.starts_with("apply-edits: RERUN_OK - a re-run's EDITs applied on record-format:0094 record-format:0094 (451 T232)"), "{}", ok.stdout);
    assert!(text(&root, PAGE).contains("A claim, reworded."));
}

/// A record check whose findings are factual (quote-check, translation-check) applies a re-run's EDIT on a research page, and a
/// page's source write-up is no question unit, so it is never held (451 T249).
#[test]
fn a_re_run_s_factual_edit_on_a_research_page_applies() {
    use l7r_gate_core::record::testkit::PAGE;
    let (root, _) = rerun_on("apply-edits-rerun-page-fact", "quote-check", "0094#k");
    let store = answers::store_in(&l7r_shared::env::Rooted::with(&*root, &[]));
    answers::answer_unit(
        &store,
        "quote-check:0094",
        "f0f0f0f0f0f0f0f0",
        "0 findings",
        None,
        "",
    )
    .unwrap();
    answers::answer_unit(
        &store,
        "quote-check:0094",
        "f0f0f0f0f0f0f0f0",
        "0 findings",
        None,
        "",
    )
    .unwrap();
    let said = run(
        &root,
        &format!(
            "quote-check: 0094 - 1 finding\n{}",
            edit(
                PAGE,
                "An unmarked claim, reworded.",
                Some("A claim, reworded.")
            )
        ),
        &[],
    );
    assert!(!said.stdout.contains("451 T232"), "{}", said.stdout);
    assert!(text(&root, PAGE).contains("A claim, reworded."));
    // a record-format re-run's EDIT on a write-up under research/sources/ names no question: applied
    let (root, _) = rerun_on("apply-edits-rerun-source", "record-format", "0094");
    let src = "research/sources/010-works-cited/0001-key-a.html";
    let said = run(
        &root,
        &format!(
            "record-format: 0094 - 1 finding\n{}",
            edit(src, "<p>Write-up A.</p>", Some("<p>Write-up A, read.</p>"))
        ),
        &[],
    );
    assert!(!said.stdout.contains("451 T232"), "{}", said.stdout);
    assert!(
        text(&root, src).contains("Write-up A, read."),
        "{}{}",
        said.stdout,
        said.stderr
    );
}
