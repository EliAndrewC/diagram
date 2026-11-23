//! Every engine claim on a tagged item holds its tag's class (feature 451 T187, `l7r_gate_claims::claims::item_labels`), over the real
//! tree: a relabel on a page names here each claim to flip, with the backing to write.

#[test]
fn every_claim_on_a_tagged_item_holds_its_tag() {
    let said = l7r_gate_claims::claims::item_labels::check(&super::root()).unwrap();
    // each line names the claim and the backing to write
    assert_eq!(said.join("\n"), "");
}
