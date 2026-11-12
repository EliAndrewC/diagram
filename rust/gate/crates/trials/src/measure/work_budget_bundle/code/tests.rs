//! The audit's readings that no bundle on a scratch tree reaches alone (feature 449 T134).

use std::path::Path;

use serde_json::json;

use super::{bundled_name, counter_keys};

#[test]
fn a_file_is_bundled_by_its_path_from_the_root() {
    assert_eq!(
        bundled_name(Path::new("/r"), Path::new("/r/rust/phases/src/brook.rs")),
        "rust__phases__src__brook.rs"
    );
    // outside the root, its name alone
    assert_eq!(
        bundled_name(Path::new("/r"), Path::new("/elsewhere/brook.rs")),
        "brook.rs",
    );
}

#[test]
fn a_rows_counters_are_read_as_python_iterates_them() {
    let rows = [
        json!({"ops": {"a@f": 1, "plain": 2}}),
        json!({"ops": ["b@g", "x"]}),
        json!({"ops": null}),
        json!({"ops": false}),
        json!({"ops": ""}),
        json!({"ops": 0}),
        json!({}),
    ];
    assert_eq!(counter_keys(&rows).unwrap(), ["a@f", "b@g"]);
    for bad in [json!({"ops": 5}), json!({"ops": [5]}), json!({"ops": "x"})] {
        assert!(counter_keys(&[bad.clone()]).is_err(), "{bad}");
    }
}
