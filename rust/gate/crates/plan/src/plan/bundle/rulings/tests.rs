//! A plan review's bundle carries every ruling its blocks cite (feature 449 T169).

use super::{cited, rulings};
use crate::checks::scratch;

const OWN: &str = r#"{"trigger": "ask:999-order", "kind": "ask", "unit": "", "asked": "Which first?", "ruling": "continue", "why": "The why, verbatim.", "what": "The what.", "tooling_fix": "Make the cap the standing rule.", "fix": "open", "utc": "2026-11-17T10:00:00Z"}
{"fix_of": "x", "note": "a row with no trigger", "status": "done", "test": "t", "utc": "2026-11-17T11:00:00Z"}
not json
{"trigger": "ask:999-order", "kind": "ask", "ruling": "accept", "why": "Asked again.", "what": ["Then this."], "for_gm": {"q": 1}, "utc": "2026-11-18T10:00:00Z"}
"#;

#[test]
fn the_keys_cited_are_found_once_each_in_order() {
    let bodies = [
        "Under `ask:999-order`'s condition 2 and ask:set-down-999-round-2.",
        "Again ask:999-order, then (ask:999-T1-x), but not task:999-y nor xask:999-z.",
    ];
    assert_eq!(
        cited(&bodies),
        ["ask:999-order", "ask:set-down-999-round-2", "ask:999-T1-x"]
    );
}

#[test]
fn a_sibling_cited_in_short_form_is_written_out_whole() {
    let bodies = [
        "Under `ask:449-T182-room-sizes`, `-room-layout`, `-review-close` and `-x`.",
        "`-lone` with no key before it, then `ask:9-a` and `-a-b` too long, and `ask:449-T1-x`, `-y`.",
    ];
    assert_eq!(
        cited(&bodies),
        [
            "ask:449-T182-room-sizes",
            "ask:449-T182-room-layout",
            "ask:449-T182-review-close",
            "ask:449-T182-room-x",
            "ask:9-a",
            "ask:449-T1-x",
            "ask:449-T1-y"
        ]
    );
}

#[test]
fn each_cited_ruling_rides_whole_from_the_feature_s_log_or_another_s_or_is_named_missing() {
    let root = scratch("plan-rulings");
    let own = root.join("specs/999-x");
    let other = root.join("specs/405-y");
    std::fs::create_dir_all(&own).unwrap();
    std::fs::create_dir_all(&other).unwrap();
    std::fs::create_dir_all(root.join("specs/406-no-log")).unwrap();
    std::fs::write(own.join("arbiter.jsonl"), OWN).unwrap();
    std::fs::write(
        other.join("arbiter.jsonl"),
        "{\"trigger\": \"ask:405-cut\", \"ruling\": \"continue\", \"why\": \"Another feature's.\", \"what\": \"\"}\n{\"trigger\": \"ask:999-order\", \"why\": \"never shown: the feature's own log holds it\"}\n",
    )
    .unwrap();
    let text = rulings(
        &own,
        &["Under ask:999-order, as ask:405-cut has it, and ask:999-gone."],
    );
    assert!(text.starts_with(
        "# The round arbiter's rulings the blocks cite, their ruling, why, what and tooling fix from `arbiter.jsonl`, verbatim\n\n## ask:999-order\n\nRecorded in `specs/999-x/arbiter.jsonl`:\n\n- **utc**: 2026-11-17T10:00:00Z\n- **ruling**: continue\n- **why**: The why, verbatim.\n- **what**: The what.\n- **tooling_fix**: Make the cap the standing rule.\n\n"
    ), "{text}");
    // every record of the key, in the log's order, a field that is no string shown as its JSON; an empty field left out
    assert!(text.contains("- **why**: Asked again.\n- **what**: [\"Then this.\"]\n\n"));
    // the question asked, the kind, the fix's state and the rest stay in the log; only when, the ruling, its why, its what and its tooling fix ride
    assert!(
        !text.contains("never shown")
            && !text.contains("Which first?")
            && !text.contains("- **kind**")
            && !text.contains("for_gm")
            && !text.contains("- **fix**")
    );
    assert!(text.contains("## ask:405-cut\n\nRecorded in `specs/405-y/arbiter.jsonl`:\n\n- **ruling**: continue\n- **why**: Another feature's.\n\n"));
    assert!(text.contains("## ask:999-gone\n\n(no record - no `arbiter.jsonl` under `specs/` holds a ruling whose trigger is `ask:999-gone`)"));
    let none = rulings(&own, &["no ruling named"]);
    assert!(none.ends_with("(none - the blocks cite no `ask:` ruling)\n"));
}
