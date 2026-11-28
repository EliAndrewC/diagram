//! A text both sides hold, judged by [`super::chosen`] alone (461 T74): the case the three-sided fixtures reach only through a whole
//! carry - the clone changed a section's words while the builder changed its archive markers alone - kept as the clone's.

use super::chosen;

const MARK: &str =
    "<!-- plan-archive: T9 to T9 moved to plan-done.md, 2026-11-28 (feature 375 FR-044) -->\n";

#[test]
fn the_clone_s_words_are_kept_where_the_builder_changed_its_markers_alone() {
    let was = "### T1 (a)\n\nold words\n";
    let ours = "### T1 (a)\n\nnew words\n";
    let theirs = format!("{was}\n{MARK}");
    assert_eq!(
        chosen(was, ours, &theirs, "### T1 (a)").unwrap().as_deref(),
        Some(ours)
    );
}
