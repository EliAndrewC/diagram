use super::{missing, read, root, FILES};

#[test]
fn every_modal_check_counts_a_split_s_moved_pointer_as_a_listing() {
    let texts: Vec<(&str, String)> = FILES.iter().map(|f| (*f, read(&root().join(f)))).collect();
    assert_eq!(missing(&texts), Vec::<String>::new());
}

#[test]
fn an_m14_without_the_pointer_clause_is_named_with_its_fix() {
    let old = "**M14. References are exactly what the write-up covers.** The question the modal draws on most is listed first.\n\n**M15.";
    let research = format!("**REFERENCES** (M14). A statement resting on an unlisted page is a finding (add it).\n\n{old}");
    let bad = missing(&[
        ("dev/modals.md", old.to_owned()),
        (".claude/agents/modal-research.md", research),
    ]);
    assert_eq!(bad.len(), 3);
    assert!(bad.iter().all(|b| b.contains("class=\"moved\"")));
}
