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
    assert_eq!(bad.len(), 5);
    assert!(bad.iter().all(|b| b.contains("class=\"moved\"")));
}

/// 451 T234: a D5, and modal-depiction's LINKS contract, without the split's clause are named; with it, clean.
#[test]
fn a_d5_or_links_without_the_split_clause_is_named() {
    let m14 = "**M14. References.** A split is a move: a <a class=\"moved\"> pointer counts.\n\n";
    let d5 = "**D5. The drawing pages, linked.** The tab ends with the pages.\n\n";
    let links = "**LINKS** (D5, D6). The links are exactly the drawing pages.\n\n";
    let bad = missing(&[(
        ".claude/agents/modal-depiction.md",
        format!("{m14}{d5}{links}"),
    )]);
    assert_eq!(bad.len(), 2, "{bad:?}");
    assert!(bad[0].contains("its D5 does not say"));
    assert!(bad[1].contains("its LINKS contract does not say"));
    let clause = " A split adds its <a class=\"moved\"> target.\n\n";
    let good = format!(
        "{m14}{}{}",
        d5.replace(".\n\n", clause),
        links.replace(".\n\n", clause)
    );
    assert_eq!(
        missing(&[(".claude/agents/modal-depiction.md", good)]),
        Vec::<String>::new()
    );
}
