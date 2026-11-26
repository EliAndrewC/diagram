//! The review and plan rounds and the feature's files, on a scratch repository.

use serde_json::json;

use super::*;
use crate::record::bundle::tests::scratch;
use crate::record::testkit::{commit, put};

/// A fixture transcript's modified time, set: the spec rounds sort on it, and the kernel stamps back-to-back writes from one coarse
/// clock tick - 300 of 300 triples tied here on 2026-11-26 - so a time left to the clock ties or not by the machine's load (451 T309).
fn aged(root: &std::path::Path, rel: &str, secs: u64) {
    std::fs::File::options()
        .write(true)
        .open(root.join(rel))
        .unwrap()
        .set_modified(std::time::UNIX_EPOCH + std::time::Duration::from_secs(secs))
        .unwrap();
}

#[test]
fn plans_specs_reviews_and_the_feature() {
    let root = scratch("arbiter-plans");
    let d = root.join("specs/500-f");
    assert!(plan_rounds(&d).0[0].contains("(none recorded in plan-review.json)"));
    put(&root, "specs/500-f/plan-review.json", &json!({"block_reviews": [{"blocks": ["T1"], "verdict": "CHANGES", "reviewed": "d1", "decisions": [{"id": "D1", "class": "narrowing", "summary": "s", "why": "w"}, {"class": "within"}, "x"]}, {"blocks": ["T2"]}, {"blocks": ["T1", "T2"], "decisions": []}]}).to_string());
    let (lines, plan) = plan_rounds(&d);
    assert!(
        lines[0].contains("### Round 1: CHANGES (d1)\n\n- D1 - narrowing: s w")
            && lines[0].contains("### Round 3: ? (?)\n\n- every decision within")
    );
    assert!(plan.ends_with("plan.md"));
    let home = root.join("home");
    put(
        &root,
        "home/x/y/subagents/agent-a.jsonl",
        &format!(
            "{}\n{}\n",
            json!({"message": {"content": "MODE 2 review specs/500-f/spec.md"}}),
            json!({"message": {"role": "assistant", "content": [{"type": "text", "text": "Verdict: FAITHFUL\n1. a finding of some length here"}]}})
        ),
    );
    put(
        &root,
        "home/x/y/subagents/agent-b.jsonl",
        &format!(
            "{}\n",
            json!({"message": {"content": [{"type": "text", "text": "MODE 3 (VERIFY) - round 2 of feature 500-f"}, "x"]}})
        ),
    );
    put(
        &root,
        "home/x/y/subagents/agent-e.jsonl",
        &format!(
            "{}\n",
            json!({"message": {"content": "MODE 2 of specs/500-f, stopped"}})
        ),
    );
    put(
        &root,
        "home/x/y/subagents/agent-c.jsonl",
        &format!(
            "{}\n",
            json!({"message": {"content": "MODE 4 specs/500-f"}})
        ),
    );
    // each round its own time, in the order the rounds ran: no tie here (the tie is `spec_rounds_of_one_time_keep_their_paths_order`)
    for (name, secs) in [("a", 100), ("b", 200), ("e", 300)] {
        aged(
            &root,
            &format!("home/x/y/subagents/agent-{name}.jsonl"),
            secs,
        );
    }
    put(&root, "home/x/y/subagents/agent-d.jsonl", "not json\n");
    put(&root, "home/x/y/subagents/note.txt", "");
    assert_eq!(reviewed_feature("  specs/500-f/spec.md"), "500-f");
    assert_eq!(reviewed_feature("none"), "");
    assert_eq!(
        first_prompt(&root.join("home/x/y/subagents/agent-d.jsonl")),
        ""
    );
    assert_eq!(first_prompt(&root.join("none")), "");
    put(&root, "empty.jsonl", "");
    assert_eq!(first_prompt(&root.join("empty.jsonl")), "");
    put(&root, "nomsg.jsonl", "{\"message\": null}\n");
    assert_eq!(first_prompt(&root.join("nomsg.jsonl")), "");
    let out = root.join("out");
    std::fs::create_dir_all(&out).unwrap();
    let got = spec_rounds_in(&home, &out, "500-f").unwrap();
    assert!(
        got[0].contains("### Round 1: spec-fidelity (FAITHFUL)")
            && got[0].contains("### Round 2: spec-fidelity (no verdict)")
            && got[0].contains("spec-fidelity (no reply (stopped))\n\n- (no reply)")
    );
    assert!(
        spec_rounds_in(&home, &out, "600-g").unwrap()[0].contains("no spec review dispatch found")
    );
    let none = feature_section(&root, &out, None, "ask:x").unwrap();
    assert!(none.contains("found in none of: no feature directory resolved"));
    put(&root, "specs/500-f/spec.md", "s");
    put(&root, "specs/500-other/request.md", "r");
    let both = feature_section(&root, &out, Some(&d), "ask:f500-x").unwrap();
    assert!(both.contains("`request.md` (the GM's words, from specs/500-other); `spec.md` (the spec, from specs/500-f)"));
    let outside = crate::checks::scratch("arbiter-outside");
    put(&outside, "spec.md", "s");
    assert!(feature_section(&root, &out, Some(&outside), "x")
        .unwrap()
        .contains(&format!("from {})", outside.display())));
    std::fs::remove_dir_all(&out).unwrap();
    assert!(feature_section(&root, &out, Some(&d), "x").is_err());
}

/// 451 T309: two spec review dispatches of one modified time keep their paths' order - the sort's tie-break, which the crate's
/// coverage reached only when the clock gave two of the fixture's transcripts one time (red at 451 T295's landing gate on 2026-11-26,
/// green on the re-run). The transcripts arrive sorted by path and the sort is stable, so the tie-break restates that order; this
/// pins the order, and the times are set so that the tie is the fixture's.
#[test]
fn spec_rounds_of_one_time_keep_their_paths_order() {
    let root = scratch("arbiter-spec-ties");
    let reply = |verdict: &str| {
        format!(
            "{}\n{}\n",
            json!({"message": {"content": "MODE 2 review specs/700-t/spec.md"}}),
            json!({"message": {"role": "assistant", "content": [{"type": "text", "text": format!("Verdict: {verdict}")}]}})
        )
    };
    // written later-path first, and a third dispatch of an earlier time whose path sorts last
    put(&root, "home/q/r/subagents/agent-b.jsonl", &reply("BLOCKED"));
    put(
        &root,
        "home/p/r/subagents/agent-a.jsonl",
        &reply("FAITHFUL"),
    );
    put(&root, "home/z/r/subagents/agent-c.jsonl", &reply("CLEAR"));
    aged(&root, "home/q/r/subagents/agent-b.jsonl", 500);
    aged(&root, "home/p/r/subagents/agent-a.jsonl", 500);
    aged(&root, "home/z/r/subagents/agent-c.jsonl", 400);
    let out = root.join("out");
    std::fs::create_dir_all(&out).unwrap();
    let got = spec_rounds_in(&root.join("home"), &out, "700-t").unwrap();
    let at = |round: &str| got[0].find(round).unwrap();
    assert!(
        at("### Round 1: spec-fidelity (CLEAR)") < at("### Round 2: spec-fidelity (FAITHFUL)")
            && at("### Round 2: spec-fidelity (FAITHFUL)")
                < at("### Round 3: spec-fidelity (BLOCKED)")
    );
}

/// 451 T309: a test's spec rounds and replies read the transcripts it names and, where it names none, no directory at all - never
/// this machine's `~/.claude/projects`.
#[test]
fn a_test_reads_its_own_transcripts_or_none() {
    assert_eq!(transcripts_base(), PathBuf::new());
    let out = scratch("arbiter-no-base");
    assert!(spec_rounds(&out, "500-f").unwrap()[0].contains("no spec review dispatch found"));
    TRANSCRIPTS.with(|t| *t.borrow_mut() = Some(out.to_path_buf()));
    assert_eq!(transcripts_base(), out.to_path_buf());
}

#[test]
fn a_review_units_verdict_record() {
    let root = scratch("arbiter-review");
    let out = root.join("out");
    std::fs::create_dir_all(&out).unwrap();
    assert!(review_verdicts(&root, &out, "").unwrap().is_empty());
    assert!(review_verdicts(&root, &out, "building-review--inashiro")
        .unwrap()
        .is_empty());
    put(
        &root,
        ".git/review-verdicts/building-review--inashiro.json",
        "{}",
    );
    let bare = review_verdicts(&root, &out, "building-review--inashiro").unwrap();
    assert!(
        bare[1].contains("- (no ledger row names it)")
            && bare[3].contains("- (no measurement verifies a finding)")
    );
    put(
        &root,
        ".git/review-dispositions/building-review--inashiro.json",
        "{}",
    );
    put(
        &root,
        "dev/review-ledger.md",
        "| x | building-review | inashiro |\n| y | other | inashiro |\n",
    );
    put(&root, "specs/500-f/measurements.json", &json!({"m": {"subject": "building-review--inashiro", "verifies": ["F1"], "method": "probe"}, "n": 1}).to_string());
    put(&root, "pool/hamlets/inashiro/a.txt", "a");
    commit(&root, "the sheet");
    let full = review_verdicts(&root, &out, "building-review--inashiro").unwrap();
    assert!(
        full[1].contains("| x | building-review | inashiro |")
            && full[3].contains("- `m` verifies ['F1']: probe")
            && out.join("dispositions.json").is_file()
    );
    std::fs::remove_dir_all(&out).unwrap();
    assert!(review_verdicts(&root, &out, "building-review--inashiro").is_err());
}

#[test]
fn a_verdict_record_outside_a_repository() {
    let plain = crate::checks::scratch("arbiter-reviews-plain");
    put(&plain, ".git/review-verdicts/building-review--x.json", "{}");
    let out = plain.join("out");
    std::fs::create_dir_all(&out).unwrap();
    assert_eq!(
        review_verdicts(&plain, &out, "building-review--x")
            .unwrap()
            .len(),
        4
    );
}
