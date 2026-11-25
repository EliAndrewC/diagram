//! A re-run's wording EDIT on a pop-up answered before at its text is held and listed, not applied (451 T232); `RERUN_OK` applies it,
//! logged; a factual EDIT of a re-run applies, as a first round's does.

use std::path::Path;

use l7r_gate_core::record::testkit::WELL;

use super::{edit, run};
use crate::record::owed::{self, answers};

/// A scratch record whose `check` unit on hamlet/well was answered twice at its text, so a re-run; its store.
fn rerun_of(tag: &str, check: &str) -> (l7r_shared::tempdir::TempDir, std::path::PathBuf) {
    let root = l7r_gate_core::record::testkit::record(tag);
    l7r_gate_core::record::testkit::edit_everything(&root);
    super::assemblable(&root);
    let store = answers::store_in(&l7r_shared::env::Rooted::with(&*root, &[]));
    let slug = format!("{check}:hamlet/well");
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
