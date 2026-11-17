//! The glossary as the record reads it (feature 449 T148): its script's bytes are HEAD's `record_glossary_js` on the same terms
//! (`source/expected.json`, checked in `source/tests.rs`); here, what `glossary.py`'s import refused.

use super::load;
use crate::fixture::put;
use l7r_gate_core::checks::scratch;

#[test]
fn a_glossary_the_import_could_not_build_is_refused() {
    let d = scratch("glossary-load");
    let at = "l7r/diagram/interactive/assets/glossary.json";
    for (text, kind, message) in [
        (
            "[1]",
            "AttributeError",
            "'list' object has no attribute 'items'",
        ),
        ("{\"a\": {\"def\": 1}}", "KeyError", "'variants'"),
        ("{\"a\": {\"variants\": []}}", "KeyError", "'def'"),
        (
            "{\"a\": {\"variants\": [1], \"def\": 1}}",
            "TypeError",
            "a glossary variant is text",
        ),
        (
            "{\"a\": {\"variants\": \"ab\", \"def\": 1}}",
            "TypeError",
            "a glossary variant is text",
        ),
    ] {
        put(&d, at, text);
        let e = load(&d).unwrap_err();
        assert_eq!((e.kind, e.message.as_str()), (kind, message), "{text}");
    }
    put(
        &d,
        at,
        "{\"a\": {\"variants\": [], \"def\": 1, \"cased\": 0}}",
    );
    assert!(!load(&d).unwrap()[0].cased);
}
