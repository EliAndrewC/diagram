//! The crate's own helpers (feature 449 T138).

use std::path::Path;

use super::{head, index_dir, Error};

#[test]
fn python_slices_and_the_index_folder() {
    assert_eq!(
        (head(5, 3), head(5, 9), head(5, -2), head(5, -9), head(0, 1)),
        (3, 5, 3, 0, 0)
    );
    assert_eq!(
        index_dir(Path::new("/a")),
        Path::new("/a/semantic-index/bge-m3-int8")
    );
    assert_eq!(Error("x".to_owned()).to_string(), "x");
}
