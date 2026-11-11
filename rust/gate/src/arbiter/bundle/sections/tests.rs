//! The arbiter bundle's sections, each on a scratch repository.

use serde_json::json;

use super::*;
use crate::record::bundle::tests::{scratch, state};
use crate::record::testkit::{commit, git, put};

#[test]
fn what_owes_a_round() {
    assert_eq!(
        owe_evidence("quote-check:0094#k", "+ the k note"),
        "a changed line in `owes-round.diff` names it"
    );
    assert_eq!(
        owe_evidence("quote-check:0094#unfootnoted", ""),
        "a changed line in `owes-round.diff` names it"
    );
    assert_eq!(
        owe_evidence(
            "record-format:0094",
            "diff --git a/research/questions/0094-x.html b/x\n"
        ),
        "`owes-round.diff` changes a file of 0094"
    );
    let diff = "diff --git a/l7r/diagram/interactive/assets/modals/sheet/well.md b/x\n--- a\n+++ b/l7r/diagram/interactive/assets/modals/sheet/well.md\n-Entry: x\n+Entry: y\n+ continued\ndiff --git a/research/questions/0094-p.html b/research/questions/0094-p.html\n+++ b/research/questions/0094-p.html\n+x";
    assert_eq!(
        owe_evidence("modal-depiction:sheet/well", diff),
        "`owes-round.diff` changes its Entry, a continuation, the page 0094-p.html line(s)"
    );
    assert!(owe_evidence("modal-depiction:sheet/nope", "").starts_with("NO changed line"));
    assert!(owe_evidence("intro-check:0095", "").starts_with("NO changed line"));
    assert_eq!(
        key_since(
            &[json!({"t": 5.0, "notes": ["k"]}), json!({"t": 7.0})],
            &[
                Unit {
                    slug: "q:0094#k".to_owned(),
                    occasion: String::new(),
                    fingerprint: String::new(),
                    reading: String::new()
                },
                Unit {
                    slug: "q:0094".to_owned(),
                    occasion: String::new(),
                    fingerprint: String::new(),
                    reading: String::new()
                }
            ],
            9.0
        ),
        7.0
    );
    assert_eq!(key_since(&[], &[], 0.0), 0.0);
    assert_eq!(
        key_since(
            &[json!({"t": 5.0, "notes": ["z"]})],
            &[Unit {
                slug: "q:0094#k".to_owned(),
                occasion: String::new(),
                fingerprint: String::new(),
                reading: String::new()
            }],
            9.0
        ),
        9.0
    );
}

#[test]
fn the_capped_round_cause() {
    let root = scratch("arbiter-capped");
    crate::record::testkit::edit_everything(&root);
    let out = root.join("out");
    std::fs::create_dir_all(&out).unwrap();
    let files = vec!["research/questions/0094-trade.notes.html".to_owned()];
    let lines =
        capped_round_cause(&root, &out, ("quote-check", "q:0094"), &files, 1.0, &[]).unwrap();
    assert!(lines[1].contains("- `quote-check:0094#k`: "), "{lines:?}");
    assert!(
        capped_round_cause(&root, &out, ("quote-check", "q:0094"), &files, 0.0, &[]).unwrap()[2]
            .contains("- none; the working tree only")
    );
    assert!(std::fs::read_to_string(out.join("owes-round.diff"))
        .unwrap()
        .contains("e.org/b"));
    let lines = capped_round_cause(
        &root,
        &out,
        ("modal-research", "modal:sheet/well"),
        &[],
        0.0,
        &[],
    )
    .unwrap();
    assert!(
        lines[1].contains("- (nothing listed as owed)") || lines[1].contains("modal-"),
        "{lines:?}"
    );
    put(&root, "l7r/diagram/interactive/classes/bad.py", "class (\n");
    let lines =
        capped_round_cause(&root, &out, ("quote-check", "q:0094"), &files, 1.0, &[]).unwrap();
    assert!(
        lines[1].contains("the record's owed list could not be read"),
        "{lines:?}"
    );
    git(&root, &["add", "-A"]);
    commit(&root, "now committed");
    let lines =
        capped_round_cause(&root, &out, ("quote-check", "q:0094"), &files, 1.0, &[]).unwrap();
    assert!(lines[2].contains(" now committed"), "{lines:?}");
    assert!(capped_round_cause(
        &root,
        &root.join("research/STYLE.md"),
        ("quote-check", "q:0094"),
        &files,
        1.0,
        &[]
    )
    .is_err());
}

#[test]
fn the_cascade_and_the_oscillation() {
    let root = scratch("arbiter-flow");
    let out = root.join("out");
    std::fs::create_dir_all(&out).unwrap();
    let d = root.join("specs/500-f");
    let events = [
        json!({"ev": "PreToolUse", "tool": "Edit", "cat": "edit", "path": "/x/notes/a.html", "t": "2026-10-11T10:00:01Z", "old": "A", "new": "B"}),
        json!({"ev": "PreToolUse", "tool": "Edit", "cat": "edit", "path": "/x/notes/a.html", "t": "2026-10-11T10:00:02Z", "old": "B", "new": "A"}),
        json!({"ev": "PreToolUse", "tool": "Agent", "agent": "quote-check", "t": "2026-10-11T10:00:03Z"}),
        json!({"ev": "PreToolUse", "tool": "Edit", "old": ""}),
        json!({"ev": "PostToolUse"}),
    ];
    let log: String = events.iter().map(|e| format!("{e}\n")).collect::<String>() + "not json\n\n";
    let path = l7r_guard::guards::event_log_hooks::log_path(&root, "500-f");
    put(
        &root,
        &path.strip_prefix(&root).unwrap().to_string_lossy(),
        &log,
    );
    let all = flow_sections(&root, &out, Some(&d), &[]).unwrap();
    assert!(
        all[0].contains("the last 3 edits and dispatches on the feature")
            && all[1].contains("- /x/notes/a.html at 10:00:02: an edit put back"),
        "{all:?}"
    );
    let mine = flow_sections(&root, &out, Some(&d), &["notes/a.html".to_owned()]).unwrap();
    assert!(
        mine[0].contains("the last 2 edits on the unit's files,"),
        "{mine:?}"
    );
    let none = flow_sections(
        &root,
        &out,
        None,
        &["research/questions/0094-trade.html".to_owned()],
    )
    .unwrap();
    assert!(
        none[0].contains("(from the git log - the event log held no edit on them)")
            && none[1].contains("- none on the unit's files (from the git log"),
        "{none:?}"
    );
    assert!(std::fs::read_to_string(out.join("cascade.txt"))
        .unwrap()
        .contains(" commit "));
    assert!(flow_sections(&root, &root.join("research/STYLE.md"), None, &[]).is_err());
}

#[test]
fn the_round_counters() {
    let root = scratch("arbiter-counters");
    assert!(round_counter(&root, "quote-check|q:0094").is_empty());
    state(
        &root,
        &json!({"rounds": {"quote-check|q:0094": 3, "record-format|q:0094": 2}, "rebased": {"quote-check|q:0094": {"n": 1}}}),
    );
    assert!(round_counter(&root, "quote-check|q:0094")[0].contains("3 round(s) counted in this feature; a new change rebased the count at round 1 (`hm_checks.py`, the cap ROUND_CAP = 2"));
    assert!(!round_counter(&root, "record-format|q:0094")[0].contains("rebased"));
    put(&root, ".git/checks-open.json", "not json");
    assert!(round_counter(&root, "quote-check|q:0094").is_empty());
    state(&root, &json!({}));
    put(
        &root,
        ".specify/feature.json",
        "{\"feature_directory\": \"specs/500-f\"}",
    );
    put(
        &root,
        ".git/review-rounds.json",
        &json!({"specs/500-f": {"u": ["u@0", "u@99999999999", "bare"]}}).to_string(),
    );
    assert!(
        round_counter(&root, "u")[0].contains("epoch: never (nothing landed)")
            && round_counter(&root, "u")[0].contains("Rounds counted after it: 3 of the 3 kept")
    );
    put(&root, "specs/500-f/tasks.md", "x");
    let at = commit(&root, "landed");
    git(&root, &["update-ref", "refs/remotes/origin/main", &at]);
    let counted = &round_counter(&root, "u")[0];
    assert!(
        counted.contains("Rounds counted after it: 1 of the 3 kept - u@99999999999")
            && counted.contains("Z (the feature's tasks.md"),
        "{counted}"
    );
    put(&root, ".specify/feature.json", "{}");
    assert!(round_counter(&root, "none")[0].contains("0 of the 0 kept - none"));
}

#[test]
fn the_red_gates() {
    let root = scratch("arbiter-red");
    assert!(red_gate_runs(&root)[0].contains("- (no red make done in the run log)"));
    let head = git(&root, &["rev-parse", "HEAD"]);
    put(&root, "dev/run-log/a/1.json", &json!({"target": "done", "result": "failed: 2 tests", "commit": head, "utc": "t1", "failed_tests": 2, "failed_names": ["t::a"]}).to_string());
    put(
        &root,
        "dev/run-log/a/2.json",
        &json!({"target": "done", "result": "failed", "commit": head, "utc": "t2"}).to_string(),
    );
    put(
        &root,
        "dev/run-log/a/3.json",
        &json!({"target": "done", "result": "failed: tree moved"}).to_string(),
    );
    put(
        &root,
        "dev/run-log/a/4.json",
        &json!({"target": "done", "result": "failed", "commit": "deadbeef"}).to_string(),
    );
    put(
        &root,
        "dev/run-log/a/5.json",
        &json!({"target": "done", "result": "failed", "utc": "t5"}).to_string(),
    );
    put(&root, "dev/run-log/a/6.json", "bad");
    put(
        &root,
        "dev/run-log/a/7.json",
        &json!({"target": "quick", "result": "failed"}).to_string(),
    );
    let text = &red_gate_runs(&root)[0];
    assert!(
        text.contains("- t1 at ")
            && text.contains("  - t::a")
            && text.contains("the same commit")
            && text.contains("a run without a commit"),
        "{text}"
    );
    put(&root, "x.txt", "x");
    let next = commit(&root, "next");
    assert_eq!(
        between(&root, &json!({"commit": head}), &json!({"commit": next}))[0],
        format!("  between {head} and {next}:")
    );
    assert!(between(
        &root,
        &json!({"commit": "aaaaaaa"}),
        &json!({"commit": "bbbbbbb"})
    )[0]
    .contains("no diff from"));
    put(&root, "big.txt", &"line\n".repeat(1600));
    let big = commit(&root, "big");
    assert!(
        between(&root, &json!({"commit": next}), &json!({"commit": big}))[0]
            .contains("its stat alone")
    );
    assert!(own_line(Path::new("/proc")).is_none());
}

#[test]
fn evidence_pool_and_claims() {
    let root = scratch("arbiter-evidence");
    let out = root.join("out");
    std::fs::create_dir_all(&out).unwrap();
    put(&root, "e/route-a.txt", "the route");
    put(&root, "e2/route-a.txt", "the pool held");
    let (a, b) = (
        root.join("e/route-a.txt").to_string_lossy().into_owned(),
        root.join("e2/route-a.txt").to_string_lossy().into_owned(),
    );
    let lines = evidence_section(&out, &[a.clone(), b.clone(), "/no/such".to_owned()]).unwrap();
    assert!(
        lines[0].contains("- `evidence/route-a.txt` (from")
            && lines[0].contains("- `evidence/route-a-2.txt`")
            && lines[0].contains("- MISSING: `/no/such`")
    );
    assert!(evidence_section(&out, &[]).unwrap().is_empty());
    std::fs::write(out.join("evidence2"), "x").unwrap();
    assert!(evidence_section(&out.join("evidence2"), &[a.clone()]).is_err());
    assert!(pool_unstated("which word?", &[]).is_empty());
    assert_eq!(
        pool_unstated("does the route regress the maps?", &[a.clone(), a.clone()]),
        vec![
            "the question names a route or a regression and states no pool result",
            &format!("{a}: a route's evidence states no pool result")
        ]
    );
    assert!(pool_unstated("does the route regress the maps?", &[b]).is_empty());
    let mut run = Run::new(&root);
    assert!(
        claims_section(&mut run, &root, &["nothing named here".to_owned()])
            .unwrap()
            .is_empty()
    );
    let got = claims_section(
        &mut run,
        &root,
        &["Is `ROUND_CAP` 12 ft, or 3 households, or 99 px?".to_owned()],
    )
    .unwrap();
    assert!(got[0].contains("- `l7r/m.py::Mod.ROUND_CAP#cap` - a research page: `ROUND_CAP is 12 ft` (last verdict IN-STEP)") && got[0].contains("- `3 households`: `l7r/m.py::other#o` - GUESS: `about 3 households` (last verdict none)") && got[0].contains("- `99 px`: no claim states it"), "{got:?}");
    assert!(claims_section(&mut run, &root, &["`Nothing`".to_owned()])
        .unwrap()
        .is_empty());
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
            && lines[0].contains("### Round 3: ? (?)\n\n- every decision within"),
        "{lines:?}"
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
            && got[0].contains("spec-fidelity (no reply (stopped))\n\n- (no reply)"),
        "{got:?}"
    );
    assert!(
        spec_rounds_in(&home, &out, "600-g").unwrap()[0].contains("no spec review dispatch found")
    );
    let none = feature_section(&root, &out, None, "ask:x").unwrap();
    assert!(none.contains("found in none of: no feature directory resolved"));
    put(&root, "specs/500-f/spec.md", "s");
    put(&root, "specs/500-other/request.md", "r");
    let both = feature_section(&root, &out, Some(&d), "ask:f500-x").unwrap();
    assert!(both.contains("`request.md` (the GM's words, from specs/500-other); `spec.md` (the spec, from specs/500-f)"), "{both}");
    let outside = crate::checks::scratch("arbiter-outside");
    put(&outside, "spec.md", "s");
    assert!(feature_section(&root, &out, Some(&outside), "x")
        .unwrap()
        .contains(&format!("from {})", outside.display())));
    std::fs::remove_dir_all(&out).unwrap();
    assert!(feature_section(&root, &out, Some(&d), "x").is_err());
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
            && out.join("dispositions.json").is_file(),
        "{full:?}"
    );
    std::fs::remove_dir_all(&out).unwrap();
    assert!(review_verdicts(&root, &out, "building-review--inashiro").is_err());
}
