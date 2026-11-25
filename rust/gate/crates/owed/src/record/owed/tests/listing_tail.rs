//! The listing's closing line: its count and the pop-ups it owes, met by a read cut to the tail (451 T241).

/// A read cut to the listing's tail still meets its count and every pop-up it owes (451 T241: P15's coordinator read the listing
/// through `tail -6`, met two of its eleven pop-ups and briefed hamlet/marsh as not owed, where the listing owed it).
#[test]
fn a_cut_read_of_the_listing_still_meets_its_count_and_its_pop_ups() {
    let root = super::listed("owed-listing-tail");
    let said = super::run(&root, &[]).stdout;
    let first = said.lines().next().unwrap();
    let last = said.lines().last().unwrap();
    assert!(last.starts_with(first), "{last}");
    assert!(
        last.ends_with(
            " - every unit is listed above; pop-ups owed: choice/bamboo--both hamlet/notice-board hamlet/well sheet/well"
        ),
        "{last}"
    );
    let one = super::run(&root, &["--q", "94"]).stdout;
    let (first, last) = (one.lines().next().unwrap(), one.lines().last().unwrap());
    assert_eq!(last, format!("{first} - every unit is listed above"));
}
