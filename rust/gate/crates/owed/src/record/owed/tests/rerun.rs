//! A re-run on text answered before is marked so (451 T232): its earlier result stands beside it, the same bundle recorded again
//! is no re-run, and the mark goes when the text moves.

use super::super::answers::{answer_unit, keep_noted_rows, rerun_at, rerun_said, write_answer};

const FP: &str = "ee9707b851db0435";

#[test]
fn a_second_answer_on_one_fingerprint_is_a_re_run_and_a_new_fingerprint_clears_it() {
    let root = crate::checks::scratch("owed-rerun");
    let store = root.join("store");
    let slug = "modal-gaps:sheet/guest-quarters";
    let clean = "ACCURACY 0; REFERENCES 0; GAPS 0";
    answer_unit(&store, slug, FP, clean, None, "round-3").unwrap();
    assert_eq!(rerun_at(&store, slug), None, "a first answer is no re-run");
    // the same bundle recorded again, after a refused line: the same round
    answer_unit(&store, slug, FP, clean, None, "round-3").unwrap();
    assert_eq!(rerun_at(&store, slug), None, "a re-record is no re-run");
    // another bundle on the same text: a re-run, the earlier result beside it
    answer_unit(
        &store,
        slug,
        FP,
        "ACCURACY 0; REFERENCES 0; GAPS 1",
        None,
        "round-4",
    )
    .unwrap();
    assert_eq!(rerun_at(&store, slug).as_deref(), Some(clean));
    // the re-run recorded again keeps its mark
    answer_unit(
        &store,
        slug,
        FP,
        "ACCURACY 0; REFERENCES 0; GAPS 1",
        None,
        "round-4",
    )
    .unwrap();
    assert_eq!(rerun_at(&store, slug).as_deref(), Some(clean));
    let said = rerun_said(&store, &[slug.to_owned(), "modal-form:sheet/x".to_owned()]);
    assert_eq!(said.lines().count(), 1, "{said}");
    assert!(said.starts_with("record-checked: modal-gaps:sheet/guest-quarters - a re-run on text answered before (was: ACCURACY 0; REFERENCES 0; GAPS 0)"), "{said}");
    // the text moved: its next answer, or a settle's write, drops the mark
    write_answer(&store, slug, "3e948ebc96424330", "settled", None).unwrap();
    assert_eq!(rerun_at(&store, slug), None);
    // an answer named by its subject, no bundle: a fingerprint answered before is a re-run, one not is none
    answer_unit(&store, slug, FP, clean, None, "").unwrap();
    assert_eq!(rerun_at(&store, slug).as_deref(), Some("settled"));
    answer_unit(&store, "modal-form:sheet/y", FP, clean, None, "").unwrap();
    assert_eq!(rerun_at(&store, "modal-form:sheet/y"), None);
}

#[test]
fn rows_kept_as_listed_notes() {
    let root = crate::checks::scratch("owed-rerun-kept");
    let own = l7r_shared::env::Rooted::with(&root, &[]);
    assert_eq!(keep_noted_rows(&own, &[]).unwrap(), None);
    let row = serde_json::json!({"check": "modal-form", "file": "f.md", "block": "EDIT 1", "units": "modal-form:x", "note": "n"});
    assert_eq!(
        keep_noted_rows(&own, &[row]).unwrap().as_deref(),
        Some("specs/_unfiled/noted.jsonl")
    );
}
