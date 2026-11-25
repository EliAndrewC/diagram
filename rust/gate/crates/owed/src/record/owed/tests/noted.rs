//! A listed note, echoed with its unit and kept in the feature's `noted.jsonl` (451 T229).

use super::super::answers::file_outside_with;

/// Page session P7's cascade, 2026-11-24: impl-drift's reply on `build.rs` carried a `NOTED, NOT FILED` line and modal-research's an
/// OUTSIDE THE CHANGE note as prose, each filed nothing (T219) and neither echoed by the recording command. The two lines are the
/// saved replies' own, verbatim (`impl-5.txt`, `modal-research-reply-1.txt`), each in the frame it came in.
#[test]
fn a_listed_note_is_echoed_with_its_unit_and_kept() {
    let root = crate::checks::scratch("owed-noted");
    let own = l7r_shared::env::Rooted::with(&root, &[]);
    let impl_5 = "VERDICT rust/phases/src/field/build.rs::build#the hem's line IN-STEP - `hem_in` gets wild-middle\n\nNOTED, NOT FILED\n- rust/phases/src/field/build.rs | build | where the middle is cleared and the winter crop is pinned bare (not barley), only the one hem band is drawn, while the page says \"a bare winter paddy is drawn only where the fan's dry ground can grow the hamlet's whole grain need\". The bundle shows no spec that sets this pin, so no map is shown to have this problem.\n";
    let got = file_outside_with(
        &own,
        "impl-drift",
        impl_5,
        "rust/phases/src/field/build.rs::build#the hem's line",
    )
    .unwrap();
    let said = got.said("claims-checked");
    assert!(got.filed.is_empty(), "{said}");
    assert!(
        said.starts_with("claims-checked: listed, not filed - rust/phases/src/field/build.rs | build | where the middle is cleared")
            && said.contains("kept in specs/_unfiled/noted.jsonl (451 T229)"),
        "{said}"
    );
    let research = "   >>>\n\nOUTSIDE THE CHANGE\nThe Depiction tab says the plan draws the quarters \"never a square block\". The Sakai block bears on that, but the Depiction tab is for `modal-depiction` to judge, not this check.\n\n---\n\nBundles judged:\n- /tmp/l7r-check/p7c-modal-research/01-sheet-barracks/MANIFEST.md\n";
    let said = file_outside_with(
        &own,
        "modal-research",
        research,
        "modal-research:sheet/retainers--quarters",
    )
    .unwrap()
    .said("record-checked");
    assert_eq!(said.lines().count(), 2, "{said}");
    assert!(said.starts_with("record-checked: listed, not filed - modal-research:sheet/retainers--quarters | The Depiction tab says"), "{said}");
    // a note under NOTED is never filed, even naming an effect; one after a closing paragraph is no note; a row beside them still files
    let mixed = "## OUTSIDE THE CHANGE\n- a.rs | f | the door is drawn on the wrong wall | effect: sheet - a door on the wrong wall\n\n- b.rs | g | a wording\n\nA closing paragraph.\n- c.rs | h | not a note\n**NOTED, NOT FILED**:\n- d.rs | k | chosen not to file | effect: map - a reader meets it\nloose words\n# Next\n- e.rs | m | past the heading\n";
    let got = file_outside_with(&own, "impl-drift", mixed, "").unwrap();
    let said = got.said("claims-checked");
    assert_eq!((got.filed.len(), got.dropped.len()), (1, 3), "{said}");
    assert!(
        said.contains("listed, not filed - impl-drift's reply, no unit named | loose words")
            && !said.contains("c.rs")
            && !said.contains("e.rs"),
        "{said}"
    );
    // a section saying it is empty is no note, and its paragraph ends it: the saved replies' own forms; `None of ...` is a note
    for empty in [
        "OUTSIDE THE CHANGE\nNone.\n\nFiles:\n- /x/0295.html\n",
        "NOTED, NOT FILED\nnone (every block and note is listed under THE CHANGE).\n",
    ] {
        let said = file_outside_with(&own, "quote-check", empty, "")
            .unwrap()
            .said("record-checked");
        assert!(said.is_empty(), "{said}");
    }
    let said = file_outside_with(
        &own,
        "impl-drift",
        "NOTED, NOT FILED\nNone of the pages gives the width.\n",
        "k",
    )
    .unwrap()
    .said("x");
    assert!(
        said.starts_with("x: listed, not filed - k | None of the pages"),
        "{said}"
    );
    let kept = std::fs::read_to_string(root.join("specs/_unfiled/noted.jsonl")).unwrap();
    assert_eq!(kept.lines().count(), 6, "{kept}");
    // recorded again (after a refused line or a hold), nothing is kept twice
    file_outside_with(
        &own,
        "impl-drift",
        impl_5,
        "rust/phases/src/field/build.rs::build#the hem's line",
    )
    .unwrap();
    let again = std::fs::read_to_string(root.join("specs/_unfiled/noted.jsonl")).unwrap();
    assert_eq!(again, kept);
}
