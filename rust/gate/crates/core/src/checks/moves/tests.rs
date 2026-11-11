//! A file only moved when its bytes stood at the base.

use super::moved_only;
use crate::ci::fixtures::{commit, put, repo};

#[test]
fn the_same_bytes_at_a_new_path_are_moved_and_an_edit_is_not() {
    let dir = repo("moves");
    commit(&dir, "old.md", "same\n");
    put(&dir, "new.md", "same\n");
    put(&dir, "edited.md", "different\n");
    let names = [
        "new.md".to_owned(),
        "edited.md".to_owned(),
        "gone.md".to_owned(),
        String::new(),
    ];
    let moved = moved_only(&dir, "HEAD", &names);
    assert_eq!(moved.into_iter().collect::<Vec<_>>(), ["new.md"]);
    assert!(moved_only(&dir, "", &names).is_empty());
    assert!(moved_only(&dir, "HEAD", &["gone.md".to_owned()]).is_empty());
}
