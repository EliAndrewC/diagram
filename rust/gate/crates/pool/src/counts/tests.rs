use super::Counts;

/// A count is charged to its tree and kind in a counting build; any other build counts nothing and holds nothing.
#[test]
fn a_count_lands_on_its_tree_and_kind_only_in_a_counting_build() {
    let mut c = Counts::default();
    c.add("pool", "dir_list", 2);
    c.add("pool", "dir_list", 1);
    c.add("legacy-hand-authored-pool", "classify", 4);
    #[cfg(feature = "counters")]
    {
        let pool = c.of("pool");
        assert_eq!(pool.len(), super::KINDS.len());
        assert_eq!(pool[0], ("dir_list", 3));
        assert!(pool[1..].iter().all(|(_, n)| *n == 0));
        assert!(c.of("legacy-hand-authored-pool").contains(&("classify", 4)));
    }
    #[cfg(not(feature = "counters"))]
    assert_eq!(c, Counts::default());
}
