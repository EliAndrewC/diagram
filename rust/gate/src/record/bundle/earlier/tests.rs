//! The earlier rounds a bundle carries: the rounds kept, the rulings, the replies beside the MANIFEST.

use serde_json::json;

use super::*;
use crate::record::bundle::tests::{scratch, state};
use crate::record::testkit::{commit, put};

#[test]
fn the_rounds_rulings_and_replies_of_a_unit() {
    let root = scratch("bundle-earlier");
    let out = root.join("out");
    let manifest = "owed-checks: quote-check, record-format\nunit: quote-check:0094#k fp\nunit: record-format:0094 fp\n";
    assert_eq!(
        section(&root, &out, manifest).unwrap(),
        "",
        "no check state"
    );
    put(&root, "specs/500-f/spec.md", "spec");
    commit(&root, "the feature");
    put(
        &root,
        ".specify/feature.json",
        "{\"feature_directory\": \"specs/500-f\"}",
    );
    let (one, two) = (root.join("one.md"), root.join("two.md"));
    put(&root, "one.md", "Verdict: findings\n1. the first finding of the round, long enough\nEDIT research/questions/0094-trade.html\n<<<\nold words here\n===\nnew words here\n>>>\n");
    put(&root, "two.md", "clean - 0 findings\n- a pass kept\n");
    put(
        &root,
        "specs/500-f/arbiter.jsonl",
        &format!(
            "{}\n{}\n",
            json!({"trigger": "round:quote-check|q:0094@3", "ruling": "continue", "why": "more", "what": "the notes"}),
            json!({"trigger": "round:quote-check|q:0094@2", "ruling": "accept"})
        ),
    );
    state(
        &root,
        &json!({"dispatches": {
            "a": {"check": "quote-check", "subjects": ["q:0094"], "t": 9_999_999_999.0, "state": "returned", "reply": one.to_string_lossy(), "notes": ["k"]},
            "b": {"check": "quote-check", "subjects": ["q:0094"], "t": 9_999_999_999.5, "state": "returned", "reply": two.to_string_lossy()},
            "c": {"check": "quote-check", "subjects": ["q:0094"], "t": 9_999_999_999.6, "state": "returned", "notes": ["other"]},
            "d": {"check": "quote-check", "subjects": ["q:0094"], "t": 9_999_999_999.7, "state": "running"},
            "e": {"check": "record-format", "subjects": ["q:0094"], "t": 9_999_999_999.8, "state": "returned", "reply": two.to_string_lossy()},
            "f": {"check": "quote-check", "subjects": ["q:0094"], "t": 1.0, "state": "returned", "reply": two.to_string_lossy()},
            "g": {"check": "quote-check", "subjects": ["q:0094"], "t": 9_999_999_999.9, "state": "returned", "aid": "none-such"}
        }}),
    );
    let text = section(&root, &out, manifest).unwrap();
    assert!(
        text.starts_with("\n## Earlier rounds (feature 393)\n\n"),
        "{text}"
    );
    assert!(
        text.contains("**Round 1** - verdict: none read")
            && text.contains("- NEW: the first finding")
            && text.contains("- NOT APPLIED: research/questions/0094-trade.html:"),
        "{text}"
    );
    assert!(text.contains("**Round 3** - no reply kept") && text.contains("- the round arbiter on `round:quote-check|q:0094@2`: **accept** - (no reason recorded)\n- the round arbiter on `round:quote-check|q:0094@3`: **continue** - more | what the next round looks at: the notes"), "{text}");
    assert!(out.join("earlier/quote-check-q-0094-round-1.md").is_file());
    assert_eq!(
        section(&root, &out, "owed-checks: bogus\nunit: x:0094 f\n").unwrap(),
        ""
    );
    assert_eq!(
        section(
            &root,
            &out,
            "owed-checks: quote-check\nunit: quote-check:0095 fp\n"
        )
        .unwrap(),
        ""
    );
    std::fs::write(root.join("blocked"), "a file").unwrap();
    assert!(section(&root, &root.join("blocked"), manifest).is_err());
    put(&root, ".specify/feature.json", "{}");
    assert!(feature_start(&root) == 0.0);
}
