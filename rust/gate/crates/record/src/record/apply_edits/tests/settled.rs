//! Only a factual round cascades (451 T188) and a settled choice stays settled (451 T190): a wording round's EDITs settle every unit
//! they alone moved that was answered before them, whatever its check; a factual round's leave those owed; an EDIT putting back the
//! words an earlier round's EDIT replaced is refused before it is applied, unless it states the factual error with its evidence.

use std::path::Path;

use l7r_gate_core::record::testkit::{put, PAGE, WELL};

use super::{assemblable, edit, page, run};
use crate::record::owed::{self, answers};

/// A record with every kind of owed edit, an assembled registry, and every modal-accuracy unit answered where it stands.
fn answered(tag: &str) -> l7r_shared::tempdir::TempDir {
    let root = l7r_gate_core::record::testkit::record(tag);
    l7r_gate_core::record::testkit::edit_everything(&root);
    assemblable(&root);
    let store = answers::store_in(&l7r_shared::env::Rooted::with(&*root, &[]));
    for (slug, fp) in owed::fingerprints(&root, &["modal-accuracy".to_owned()]).unwrap() {
        answers::write_answer(&store, &slug, &fp, "0 findings", None).unwrap();
    }
    root
}

#[test]
fn a_wording_round_settles_a_later_check_s_answered_unit_and_a_factual_one_does_not() {
    let root = answered("apply-edits-wording");
    let form = run(
        &root,
        &format!(
            "modal-form: Well - 1 finding (1 FIX)\n{}",
            edit(WELL, "It is deep.", Some("It is a deep one."))
        ),
        &[],
    );
    assert!(
        form.stdout.contains(
            "modal-accuracy:hamlet/well: settled with its answer - a wording round's EDITs alone moved it, no fact changed (451 T188)"
        ),
        "{}",
        form.stdout
    );
    let root = answered("apply-edits-factual");
    let truth = run(
        &root,
        &format!(
            "modal-depiction: well - 1 finding\nunit: modal-depiction:hamlet/well x\n{}",
            edit(WELL, "Drawn round.", Some("Drawn as a ring.")).replacen(
                "EDIT ",
                "EDIT (TRUTH) ",
                1
            )
        ),
        &[],
    );
    assert!(!truth.stdout.contains("451 T188"), "{}", truth.stdout);
}

/// The check state of `root` holding one returned record-format round whose reply is `reply`.
fn state_with(root: &Path, reply: &str) {
    put(root, ".git/check-replies/r1.md", reply);
    let state = serde_json::json!({"dispatches": {"toolu_r1": {
        "check": "record-format", "subjects": ["q:0094"], "state": "answered", "t": 1.0,
        "reply": root.join(".git/check-replies/r1.md").to_string_lossy(),
    }}});
    put(root, ".git/checks-open.json", &state.to_string());
}

#[test]
fn an_edit_putting_back_what_an_earlier_round_replaced_is_refused_unless_it_states_the_fact() {
    let root = l7r_gate_core::record::testkit::record("apply-edits-reversal");
    let was = "More here.";
    let now = "More words here.";
    std::fs::write(root.join(PAGE), page(&root).replace(was, now)).unwrap();
    state_with(
        &root,
        &format!("record-format: 0094 - 1\n{}", edit(PAGE, was, Some(now))),
    );
    let back = format!("record-style: 0094 - 1\n{}", edit(PAGE, now, Some(was)));
    let refused = run(&root, &back, &[]);
    assert!(
        refused.stdout.contains(
            "REFUSED - it puts back the words an earlier record-format round's EDIT replaced"
        ),
        "{}",
        refused.stdout
    );
    assert!(refused.stdout.contains("REVERSES round <n>:"));
    assert_eq!(refused.code, 1);
    assert!(page(&root).contains(now));
    // a wording check's finding cannot reverse a settled choice, its evidence or not
    let styled = format!(
        "record-style: 0094 - 1\nREVERSES round 1: the old words were right - evidence: \"the page reads more here\"\n{}",
        edit(PAGE, now, Some(was))
    );
    assert_eq!(run(&root, &styled, &[]).code, 1);
    // a factual finding naming its error but no evidence is still refused
    let bare = format!(
        "quote-check: 0094 - 1\nREVERSES round 1: the source says so\n{}",
        edit(PAGE, now, Some(was))
    );
    assert!(run(&root, &bare, &[])
        .stdout
        .contains("REFUSED - it puts back"));
    let stated = format!(
        "quote-check: 0094 - 1\nREVERSES round 1: round 1 dropped a fact the source states - evidence: \"more here\", research/questions/0094-trade.html\n{}",
        edit(PAGE, now, Some(was))
    );
    let applied = run(&root, &stated, &[]);
    assert!(!applied.stdout.contains("REFUSED"), "{}", applied.stdout);
    assert!(page(&root).contains(was));
}

#[test]
fn an_edit_that_puts_back_nothing_and_a_tree_with_no_check_state_are_let_through() {
    let root = l7r_gate_core::record::testkit::record("apply-edits-no-state");
    let fresh = run(
        &root,
        &format!(
            "record-format: 0094 - 1\n{}",
            edit(PAGE, "More here.", Some("More words here."))
        ),
        &[],
    );
    assert!(!fresh.stdout.contains("REFUSED"), "{}", fresh.stdout);
    state_with(&root, "record-format: 0094 - 0 findings\n");
    let other = run(
        &root,
        &format!(
            "record-format: 0094 - 1\n{}",
            edit(PAGE, "More words here.", Some("More here, now."))
        ),
        &[],
    );
    assert!(!other.stdout.contains("REFUSED"), "{}", other.stdout);
    // the round's own reply, kept in the state as it returned, is no earlier round of itself
    let own = format!(
        "record-format: 0094 - 1\n{}",
        edit(PAGE, "More here, now.", Some("More here."))
    );
    state_with(&root, &own);
    assert!(!run(&root, &own, &[]).stdout.contains("REFUSED"));
}

/// `answered`'s record with its record-format unit answered too, where it stands.
fn format_answered(tag: &str) -> l7r_shared::tempdir::TempDir {
    let root = answered(tag);
    let store = answers::store_in(&l7r_shared::env::Rooted::with(&*root, &[]));
    let rec = owed::read_at(&root, None, Some(&std::collections::HashSet::new())).unwrap();
    let unit = "record-format:0094";
    let fp = crate::record::units::fingerprint(&rec, unit);
    answers::write_answer(&store, unit, &fp, "0 findings", None).unwrap();
    root
}

#[test]
fn in_a_mixed_round_a_unit_only_its_wording_edits_moved_settles_and_one_a_factual_edit_moved_does_not(
) {
    let links =
        |p: &str, o: &str, n: &str| edit(p, o, Some(n)).replacen("EDIT ", "EDIT (LINKS) ", 1);
    let truth =
        |p: &str, o: &str, n: &str| edit(p, o, Some(n)).replacen("EDIT ", "EDIT (TRUTH) ", 1);
    let root = format_answered("apply-edits-mixed");
    let mixed = run(
        &root,
        &format!(
            "modal-depiction: well - 2 findings\n{}{}",
            truth(WELL, "Drawn round.", "Drawn as a ring."),
            links(PAGE, "More here.", "More here, too.")
        ),
        &[],
    );
    assert!(
        mixed.stdout.contains(
            "record-format:0094: settled with its answer - a wording round's EDITs alone moved it"
        ),
        "{}",
        mixed.stdout
    );
    assert!(page(&root).contains("More here, too.") && mixed.code == 0);
    let root = format_answered("apply-edits-mixed-factual");
    let factual = run(
        &root,
        &format!(
            "modal-depiction: well - 2 findings\n{}{}",
            links(WELL, "Drawn round.", "Drawn as a ring."),
            truth(PAGE, "More here.", "More here, too.")
        ),
        &[],
    );
    assert!(
        !factual.stdout.contains("record-format:0094: settled"),
        "{}",
        factual.stdout
    );
}
