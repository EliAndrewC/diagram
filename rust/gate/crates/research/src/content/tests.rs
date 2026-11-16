//! The page's content assets (feature 449 T144; `content.py` read the same files).

use super::{content, ASSETS};
use crate::fixture::put;

#[test]
fn an_asset_is_its_json_and_a_broken_one_is_refused() {
    let tree = l7r_gate_core::checks::scratch("research-content");
    put(
        &tree,
        &format!("{ASSETS}/page-text.json"),
        "{\"a\": [1, 2.5]}",
    );
    put(&tree, &format!("{ASSETS}/broken.json"), "{");
    assert_eq!(
        content(&tree, "page-text.json").unwrap(),
        serde_json::json!({"a": [1, 2.5]})
    );
    assert_eq!(
        content(&tree, "broken.json").unwrap_err().kind,
        "JSONDecodeError"
    );
    assert_eq!(content(&tree, "none.json").unwrap_err().kind, "OSError");
}
