//! A ruling on a red-gate trigger no guard owes is refused where it is recorded, as its bundle is (451 T482): on 2026-11-27 the
//! arbiter ruled red-gate@2026-11-27T09:39:16Z while arbiter-owed.json held only red-gate@2026-11-27T09:39:13Z, and the ruling
//! discharged nothing (451 arbiter.jsonl row 73).

use serde_json::json;

use super::super::{record_batch, record_ruling};
use super::{clone_at, owe, own, refused, rows};

#[test]
fn a_ruling_on_an_unowed_red_gate_is_refused_naming_the_owed_one() {
    let root = clone_at("unowed-red");
    owe(
        &root,
        &json!({"red-gate@2026-11-27T09:39:13Z": {"kind": "red-gate", "feature": "999-x"}}),
    );
    let rule = json!({"ruling": "continue", "why": "w"});
    refused(
        record_ruling(
            &own(&root),
            "red-gate@2026-11-27T09:39:16Z",
            &rule,
            "round-arbiter",
            None,
            false,
        ),
        "make arbiter-bundle TRIGGER=red-gate@2026-11-27T09:39:13Z",
    );
    let both = json!({"ruling": "continue", "why": "w", "triggers": ["red-gate@2026-11-27T09:39:13Z", "red-gate@2026-11-27T09:39:16Z"]});
    refused(
        record_batch(&own(&root), &both, "round-arbiter", None),
        "red-gate@2026-11-27T09:39:16Z is owed by no guard",
    );
    assert!(rows(&root).is_empty());
    let owed = record_ruling(
        &own(&root),
        "red-gate@2026-11-27T09:39:13Z",
        &rule,
        "round-arbiter",
        None,
        false,
    );
    assert!(owed.is_ok(), "{owed:?}");
    owe(&root, &json!({}));
    refused(
        record_ruling(
            &own(&root),
            "red-gate@2026-11-27T09:39:16Z",
            &rule,
            "round-arbiter",
            None,
            false,
        ),
        "no red-gate trigger is owed now",
    );
    assert_eq!(rows(&root).len(), 1);
}
