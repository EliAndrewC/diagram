//! A standing verdict is no round owed (451 T199), on a scratch repository.

use serde_json::json;

use super::super::super::tests::{put, repo, sheet};
use super::super::content_key;
use super::standing;

/// RED FIRST (451 T199): the 2026-11-23 wave's two shapes - hayakawa-magistracy's PASS with one nitpick on an unchanged sheet stands;
/// ochiba-roundtrip-test's NEEDS-WORK whose error was fixed (in the docs) owes its round on the same unchanged sheet.
#[test]
fn a_carried_verdict_with_only_minor_findings_stands_and_a_fixed_error_owes_its_round() {
    let r = repo("stands");
    sheet(&r, "legacy-hand-authored-pool", "s", &["gate"]);
    let reviewed = content_key(&r, "s");
    let v = ".git/review-verdicts/building-review--s.json";
    let at = |verdict: &str, findings: serde_json::Value, content: &str| {
        put(&r, v, &json!({"verdict": verdict, "engine_key": "K0", "content_key": content, "findings": findings}).to_string());
    };
    let stands = || standing(&r, "building-review--s nope") == "building-review--s\n";
    at(
        "PASS",
        json!([{"id": "N1", "severity": "nitpick"}, {"id": "C1", "severity": "confirmation"}, {"id": "O1", "severity": "outside"}]),
        &reviewed,
    );
    assert!(stands());
    // the command `make verify` asks
    let root = r.to_string_lossy().into_owned();
    let said = super::super::cli(
        &["standing", "--maps", "building-review--s", "--clone", &root].map(str::to_owned),
    );
    assert_eq!(said.stdout, "building-review--s\n");

    at(
        "NEEDS-WORK",
        json!([{"id": "E1", "severity": "error"}, {"id": "N1", "severity": "nitpick"}]),
        &reviewed,
    );
    assert!(!stands());
    // an error deliberately left (`make review-accept`) changed nothing, so the verdict stands
    put(
        &r,
        ".git/review-dispositions/building-review--s.json",
        &json!({"accepted": [{"finding": "E1", "round": "K0", "reason": "left on purpose"}]})
            .to_string(),
    );
    assert!(stands());
    // a questionable one, or one of no severity, owes the round
    at(
        "PASS",
        json!([{"id": "Q1", "severity": "questionable"}]),
        &reviewed,
    );
    assert!(!stands());
    at("PASS", json!([{"id": "F1"}]), &reviewed);
    assert!(!stands());
    // no judgment, or the sheet moved
    at("NOT-REVIEWABLE", json!([]), &reviewed);
    assert!(!stands());
    at("PASS", json!([]), "0000000000000000");
    assert!(!stands());
}
