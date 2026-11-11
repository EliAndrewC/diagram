//! The arbiter's bundle end to end, on a scratch record with a check state, an owed record and a feature.

use std::path::Path;

use serde_json::json;

use super::*;
use crate::record::bundle::tests::{args, scratch, state};
use crate::record::testkit::put;

fn feature(root: &Path) {
    put(
        root,
        ".specify/feature.json",
        "{\"feature_directory\": \"specs/500-f\"}",
    );
    put(root, "specs/500-f/spec.md", "the spec");
    put(root, "specs/500-f/request.md", "the GM's words");
    put(root, "specs/500-f/plan-review.json", &json!({"block_reviews": [{"blocks": ["T1"], "verdict": "CLEAR", "reviewed": "d", "decisions": []}]}).to_string());
    put(root, "specs/500-f/plan.md", "the plan");
}

fn owed(root: &Path, value: &serde_json::Value) {
    std::fs::write(
        root.join(".git").join("arbiter-owed.json"),
        value.to_string(),
    )
    .unwrap();
}

/// The bundle's tests give the capped round's owed list instead of computing it (T99): the owed crate tests that computation, about
/// 35 `git` calls a time, and these test the bundle around it.
fn no_owed() {
    super::sections::GIVEN.with(|g| *g.borrow_mut() = Some(Ok(Vec::new())));
}

fn bundle_cli(root: &Path, extra: &[&str]) -> Reply {
    let r = root.to_string_lossy().into_owned();
    let mut a = vec!["--root", r.as_str()];
    a.extend(extra);
    cli(&args(&a))
}

#[test]
fn a_round_trigger_and_its_rounds() {
    no_owed();
    let root = scratch("arbiter-bundle-round");
    feature(&root);
    let reply = root.join("r.md");
    put(&root, "r.md", "1. a finding raised about the passage on 0094\nEDIT research/questions/0094-trade.html\n<<<\nAn unmarked claim.\n===\nA marked claim.\n>>>\n");
    state(
        &root,
        &json!({"feature": "500-f", "rounds": {"quote-check|q:0094": 1}, "dispatches": {
            "a": {"check": "quote-check", "subjects": ["q:0094"], "t": 1.0, "state": "returned", "reply": reply.to_string_lossy(), "owed": ["a note changed"]},
            "b": {"check": "record-format", "subjects": ["q:0094"], "t": 2.0, "state": "returned", "reply": reply.to_string_lossy()},
            "c": {"check": "quote-check", "subjects": ["q:0094"], "t": 3.0, "state": "returned", "manifest": "/tmp/m"}
        }}),
    );
    let out = root.join("out");
    let o = out.to_string_lossy().into_owned();
    let refused = bundle_cli(&root, &["round:quote-check|q:0094@2", "--out", &o]);
    assert_eq!(refused.code, 2);
    assert!(refused
        .stderr
        .contains("no reply kept for round 2 (quote-check, bundle /tmp/m)"));
    assert!(!out.exists());
    let r = bundle_cli(
        &root,
        &[
            "round:quote-check|q:0094@2",
            "--out",
            &o,
            "--missing-ok",
            "the reply was pruned",
        ],
    );
    assert_eq!(r.code, 0);
    assert!(r.stdout.ends_with("arbiter-bundle: dispatch `round-arbiter` on that MANIFEST; it records its own ruling (make arbiter-ruled)\n"));
    let text = std::fs::read_to_string(out.join("MANIFEST.md")).unwrap();
    for part in [
        "## Rounds - quote-check on q:0094",
        "The owed round is the counter's round 2",
        "Owed by: a note changed",
        "## The last answered round's EDITs",
        "## What owes the capped round",
        "## The round counter",
        "## Missing from the record (bundled anyway: the reply was pruned)",
        "## The cascade",
        "## The feature",
    ] {
        assert!(text.contains(part));
    }
    assert!(out.join("round-1-quote-check.md").is_file() && out.join("edits.diff").is_file());
    assert_eq!(
        bundle_cli(&root, &["round:quote-check|q:0094@5", "--out", &o]).code,
        2
    );
    let none = bundle_cli(&root, &["round:intro-check|q:0094@1", "--out", &o]);
    assert!(none
        .stderr
        .contains("no dispatch of intro-check on q:0094 in the check state"));
    let default = bundle_cli(
        &root,
        &[
            "round:quote-check|q:0094@2",
            "--missing-ok",
            "the reply was pruned",
        ],
    );
    assert!(default.stdout.starts_with(
        &default_root()
            .join("arbiter-round-quote-check-q-0094-2/MANIFEST.md")
            .to_string_lossy()
            .into_owned()
    ));
}

#[test]
fn an_ask_s_bundle_and_a_busy_out() {
    no_owed();
    // the spec rounds read a fixture's transcripts, not this machine's (T99)
    let none = scratch("arbiter-no-transcripts");
    super::reviews::TRANSCRIPTS.with(|t| *t.borrow_mut() = Some(none.to_path_buf()));
    let root = scratch("arbiter-bundle-kinds");
    feature(&root);
    owed(
        &root,
        &json!({
            "ask:probe": {"kind": "ask", "detail": "Does ROUND_CAP hold at 12 ft? The plan review rounds, and two knots here.", "unit": ""},
            "reversal:research/questions/0094-trade.html@1": {"kind": "reversal", "detail": "A -> B -> A"}
        }),
    );
    put(&root, "e/route.txt", "the route rolled");
    let o = root.join("out").to_string_lossy().into_owned();
    let ev = root.join("e/route.txt").to_string_lossy().into_owned();
    let ask = bundle_cli(
        &root,
        &[
            "ask:probe",
            "--out",
            &o,
            "--evidence",
            &format!("{ev} /no/such"),
        ],
    );
    assert_eq!(ask.code, 0);
    let text = std::fs::read_to_string(root.join("out/MANIFEST.md")).unwrap();
    for part in ["## The question\n\nDoes ROUND_CAP", "## The evidence the question cites", "## The room table", "## The numbers it names", "## The plan review's rounds", "## Edits between rounds\n\n`edits.diff` beside this file: the last 20 commits touching specs/500-f/plan.md"] {
        assert!(text.contains(part));
    }
    put(&root, "busy", "a file where the bundle goes");
    assert_eq!(
        bundle_cli(
            &root,
            &["ask:x", "--out", &root.join("busy").to_string_lossy()]
        )
        .code,
        1
    );
}

/// The reversals, a red gate and the review rounds, split from the ask's test (T99): together they took 0.123 s run alone,
/// over FR-008's bar.
#[test]
fn reversals_red_gates_and_reviews() {
    no_owed();
    // the spec rounds read a fixture's transcripts, not this machine's (T99)
    let none = scratch("arbiter-no-transcripts");
    super::reviews::TRANSCRIPTS.with(|t| *t.borrow_mut() = Some(none.to_path_buf()));
    let root = scratch("arbiter-bundle-kinds");
    feature(&root);
    owed(
        &root,
        &json!({
            "ask:probe": {"kind": "ask", "detail": "Does ROUND_CAP hold at 12 ft? The plan review rounds, and two knots here.", "unit": ""},
            "reversal:research/questions/0094-trade.html@1": {"kind": "reversal", "detail": "A -> B -> A"}
        }),
    );
    let o = root.join("out").to_string_lossy().into_owned();
    let file = root
        .join("research/questions/0094-trade.html")
        .to_string_lossy()
        .into_owned();
    for trigger in [
        "reversal:research/questions/0094-trade.html@1",
        &format!("reversal:{file}@1"),
        "reversal:q:0094@1",
    ] {
        let r = bundle_cli(&root, &[trigger, "--out", &o]);
        assert_eq!(r.code, 0);
    }
    assert!(bundle_cli(&root, &["reversal:no/such.html@1", "--out", &o])
        .stderr
        .contains("a reversal with no check rounds on "));
    assert_eq!(
        bundle_cli(&root, &["red-gate@2026-10-19T00:59:47Z", "--out", &o]).code,
        0
    );
    assert_eq!(
        bundle_cli(&root, &["round:spec-fidelity|plan:500-f#T1@3", "--out", &o]).code,
        0
    );
    assert!(std::fs::read_to_string(root.join("out/MANIFEST.md"))
        .unwrap()
        .contains("## The plan review's rounds"));
    assert_eq!(
        bundle_cli(&root, &["round:spec-fidelity|500-f#1@3", "--out", &o]).code,
        0
    );
    assert!(std::fs::read_to_string(root.join("out/MANIFEST.md"))
        .unwrap()
        .contains("## Rounds - the spec review of 500-f"));
    put(&root, ".git/review-verdicts/building-review--x.json", "{}");
    owed(
        &root,
        &json!({"round:building-review|building-review--x@3": {"kind": "round", "unit": "building-review|building-review--x"}}),
    );
    assert_eq!(
        bundle_cli(
            &root,
            &["round:building-review|building-review--x@3", "--out", &o]
        )
        .code,
        0
    );
    assert!(std::fs::read_to_string(root.join("out/MANIFEST.md"))
        .unwrap()
        .contains("## The earlier rounds (from the verdict record"));
}

#[test]
fn a_batch_and_the_command_line() {
    no_owed();
    let root = scratch("arbiter-bundle-batch");
    feature(&root);
    let reply = root.join("r.md");
    put(&root, "r.md", "clean - 0 findings\n");
    state(
        &root,
        &json!({"feature": "500-f", "rounds": {"quote-check|q:0094": 2}, "dispatches": {
            "a": {"check": "quote-check", "subjects": ["q:0094"], "t": 1.0, "state": "returned", "reply": reply.to_string_lossy()},
            "b": {"check": "quote-check", "subjects": ["q:0094"], "t": 2.0, "state": "returned", "reply": reply.to_string_lossy()}
        }}),
    );
    let o = root.join("out").to_string_lossy().into_owned();
    assert!(bundle_cli(&root, &["--batch", "--out", &o])
        .stderr
        .contains("no round trigger is owed a ruling"));
    owed(
        &root,
        &json!({"round:quote-check|q:0094@3": {"kind": "round", "unit": "quote-check|q:0094"}, "round:quote-check|q:0777@3": {"kind": "round", "unit": "quote-check|q:0777", "feature": "999-other"}}),
    );
    let batch = bundle_cli(&root, &["--batch", "--out", &o]);
    assert_eq!(batch.code, 0);
    let text = std::fs::read_to_string(root.join("out/MANIFEST.md")).unwrap();
    assert!(
        text.contains(
            "- `round:quote-check|q:0094@3` - its bundle: `round-quote-check-q-0094-3/MANIFEST.md`"
        ) && text.contains("Left out - owed in another feature")
    );
    assert!(bundle_cli(
        &root,
        &[
            "--batch",
            "--triggers",
            "round:quote-check|q:0094@9",
            "--out",
            &o
        ]
    )
    .stderr
    .contains("a named round is not its unit's next"));
    owed(
        &root,
        &json!({"round:intro-check|q:0094@1": {"kind": "round", "unit": "intro-check|q:0094"}}),
    );
    assert!(bundle_cli(&root, &["--batch", "--out", &o])
        .stderr
        .contains("round:intro-check|q:0094@1: no dispatch of intro-check"));
    assert_eq!(bundle_cli(&root, &["--batch"]).code, 2);
    put(&root, "busy", "x");
    owed(
        &root,
        &json!({"round:quote-check|q:0094@3": {"kind": "round", "unit": "quote-check|q:0094"}}),
    );
    assert_eq!(
        bundle_cli(
            &root,
            &["--batch", "--out", &root.join("busy/sub").to_string_lossy()]
        )
        .code,
        1
    );
    assert_eq!(bundle_cli(&root, &["round-3@449-T065-plan"]).code, 2);
    assert_eq!(bundle_cli(&root, &[]).code, 2);
    assert_eq!(
        bundle_cli(&root, &["ask:x", "--missing-ok", "gone"]).code,
        2
    );
    assert_eq!(bundle_cli(&root, &["--bogus"]).code, 2);
    assert_eq!(bundle_cli(&root, &["--check-ask", "which word?"]).code, 0);
    let ask = bundle_cli(&root, &["--check-ask", "does the route regress the maps?"]);
    assert!(
        ask.code == 2
            && ask
                .stderr
                .starts_with("arbiter-ask: the question names a route")
    );
    assert_eq!(
        crate::arbiter::cli(&args(&["bundle", "--check-ask", "x"])).code,
        0
    );
    assert_eq!(batch_dir("Round:A--B"), "round-a-b");
}

#[test]
fn the_rare_paths_of_the_arbiters_bundle() {
    no_owed();
    let root = scratch("arbiter-bundle-rare");
    feature(&root);
    state(
        &root,
        &json!({"feature": "other", "dispatches": {"a": {"check": "quote-check", "subjects": ["q:0094"], "t": 1.0}}}),
    );
    let o = root.join("out").to_string_lossy().into_owned();
    let missing = bundle_cli(&root, &["round:quote-check|q:0094@1", "--out", &o]);
    assert!(missing
        .stderr
        .contains("no reply kept for round 1 (quote-check, bundle ?)"));
    owed(
        &root,
        &json!({"reversal:x@1": {"kind": "reversal", "unit": "no/such/thing.txt"}, "reversal:y@1": {"kind": "reversal", "unit": "q:0777"}}),
    );
    assert!(bundle_cli(&root, &["reversal:x@1", "--out", &o])
        .stderr
        .contains("a reversal with no check rounds on no/such/thing.txt"));
    assert!(bundle_cli(&root, &["reversal:y@1", "--out", &o])
        .stderr
        .contains("a reversal with no check rounds on q:0777 and no history of ?"));
    let plain = crate::checks::scratch("arbiter-bundle-plain");
    assert!(rounds_section(&plain, &plain, "c", "s", "t")
        .unwrap()
        .kept
        .is_empty());
    assert_eq!(counted(&plain, "u"), 0);
    assert_eq!(counted(&root, "quote-check|q:0094"), 0);
    put(&root, ".specify/feature.json", "{}");
    assert_eq!(counted(&root, "quote-check|q:0094"), 0);
    feature(&root);
    owed(
        &root,
        &json!({"round:quote-check|q:0094@1": {"kind": "round", "unit": "quote-check|q:0094"}}),
    );
    let spec = root.join("specs/500-f/spec.md");
    std::fs::set_permissions(&spec, std::os::unix::fs::PermissionsExt::from_mode(0o000)).unwrap();
    let failed = bundle_cli(
        &root,
        &["--batch", "--out", &o, "--missing-ok", "a probe asked"],
    );
    std::fs::set_permissions(&spec, std::os::unix::fs::PermissionsExt::from_mode(0o644)).unwrap();
    assert_eq!(failed.code, 1);
}
