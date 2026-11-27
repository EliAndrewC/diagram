//! A rounded dispatch's spent fields (451 T387, T488), split out of `rounds/tests.rs` at the 1,000-line bar.

use serde_json::json;

use super::super::returned;

/// A rounded dispatch keeps no `counted` or `quote_notes` (451 T387): both are read only by its own return, before it rounds; an
/// unrounded one keeps both, for the return still to come.
#[test]
fn a_rounded_dispatch_drops_what_only_its_return_read() {
    let row = |rounded: bool, aid: &str| {
        json!({"aid": aid, "check": "quote-check", "state": "running", "subjects": ["q:0105"],
        "counted": ["quote-check|q:0105"], "quote_notes": {"0105.drawing#bath": "abc"}, "marks": {"fresh": []}, "rounded": rounded, "t": 1.0})
    };
    let mut state = json!({"dispatches": {"old": row(true, "a0"), "new": row(false, "a1"), "wait": row(false, "a2")}});
    returned(&mut state, "a1", "VERDICT: PASS", None);
    for (tid, kept) in [("old", false), ("new", false), ("wait", true)] {
        let d = &state["dispatches"][tid];
        let had = (
            d.get("counted").is_some(),
            d.get("quote_notes").is_some(),
            d.get("marks").is_some(),
        );
        assert_eq!(had, (kept, kept, kept));
    }
    assert_eq!(state["rounds"]["quote-check|q:0105"], json!(1));
}
