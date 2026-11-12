//! The decider over a fixture clone, the record tools stubbed by shell snippets (`tests/hooks/test-review-round-hooks.sh`, replayed through the shim, runs the real ones).

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::{answer, classify_mode, cli, decide, plan_rounds, verdict, verdict_of, Ctx, Outcome};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;

const NO_STALE: &str = "true";
const NO_ACTIVE: &str = "true";

fn world(tag: &str) -> crate::shared::tempdir::Held<PathBuf> {
    crate::shared::log::quiet();
    let d = crate::shared::tempdir::TempDir::new(&format!("guard-round-{tag}"));
    std::fs::create_dir_all(d.join("specs/301-x")).unwrap();
    std::fs::create_dir_all(d.join("specs/302-y")).unwrap();
    std::fs::create_dir_all(d.join(".git")).unwrap();
    std::fs::write(d.join("specs/301-x/spec.md"), "# 301\n\nFR-001 stands.\n").unwrap();
    std::fs::write(d.join("specs/302-y/spec.md"), "# 302\n\n## Review history\n\n- Round 1, `spec-fidelity`: CHANGES REQUIRED, an item.\n\n## After\n\nmore\n").unwrap();
    let held = d.canonicalize().unwrap();
    d.hold(held)
}

/// The gate stub: `plan door active-task` answers `active`, every other call `stale` (feature 449 T141: the guard asks the gate itself).
fn ctx(d: &Path, stale: &str, active: &str) -> Ctx {
    std::fs::create_dir_all(d.join("scripts/gates")).unwrap();
    crate::guards::write_executable(
        &d.join("scripts/gates/l7r-gate.sh"),
        &format!(
            "#!/bin/sh\nif [ \"$1 $2 $3\" = \"plan door active-task\" ]; then\n{active}\nelse\n{stale}\nfi\n"
        ),
    );
    Ctx {
        tree: d.to_path_buf(),
    }
}

/// The active feature's arbiter record: one row a `<trigger>:<ruling>`.
fn ruled(d: &Path, rows: &[&str]) {
    std::fs::create_dir_all(d.join(".specify")).unwrap();
    std::fs::write(
        d.join(".specify/feature.json"),
        r#"{"feature_directory": "specs/301-x"}"#,
    )
    .unwrap();
    let lines: String = rows
        .iter()
        .map(|r| {
            let (t, v) = r.rsplit_once(':').unwrap();
            json!({"trigger": t, "ruling": v}).to_string() + "\n"
        })
        .collect();
    std::fs::write(d.join("specs/301-x/arbiter.jsonl"), lines).unwrap();
}

fn plain(d: &Path) -> Ctx {
    ctx(d, NO_STALE, NO_ACTIVE)
}

fn dispatch(kind: &str, prompt: &str, transcript: &str, d: &Path, c: &Ctx) -> Option<Outcome> {
    let input = json!({"session_id": "t", "transcript_path": transcript, "tool_input": {"subagent_type": kind, "prompt": prompt, "description": "x"}});
    verdict(&input, "Agent", &d.to_string_lossy(), c)
}

fn spec(prompt: &str, d: &Path, c: &Ctx) -> Outcome {
    dispatch("spec-fidelity", prompt, "", d, c).unwrap()
}

fn round_file(d: &Path, feature: &str) -> PathBuf {
    d.join(".git/review-round").join(feature).join("round")
}

fn rewrite_of(o: &Outcome) -> Option<Value> {
    o.answer.iter().find_map(|a| {
        if let Answer::Rewrite(v) = a {
            Some(v.clone())
        } else {
            None
        }
    })
}

fn rewritten(o: &Outcome) -> Value {
    rewrite_of(o).unwrap()
}

fn refused(o: &Outcome, words: &str) -> bool {
    matches!(&o.answer[..], [Answer::Refuse(t)] if t.contains(words))
}

/// A subagent transcript of `prompt` ending in `last`, the session transcript's path.
fn subagent(d: &Path, name: &str, prompt: &str, last: &str, when: u64) -> String {
    let sub = d.join("sess/subagents");
    std::fs::create_dir_all(&sub).unwrap();
    let lines = [
        json!({"message": {"role": "user", "content": prompt}}).to_string(),
        "not json".to_owned(),
        json!({"message": {"role": "assistant", "content": [{"type": "tool_use"}]}}).to_string(),
        json!({"message": {"role": "assistant", "content": [{"type": "text", "text": last}]}})
            .to_string(),
    ];
    let path = sub.join(name);
    std::fs::write(&path, lines.join("\n")).unwrap();
    let time = std::time::UNIX_EPOCH + std::time::Duration::from_secs(when);
    std::fs::File::options()
        .write(true)
        .open(&path)
        .unwrap()
        .set_modified(time)
        .unwrap();
    d.join("sess.jsonl").to_string_lossy().into_owned()
}

#[test]
fn the_mode_is_read_with_precedence() {
    assert_eq!(
        classify_mode("MODE 3 about a plan review and an exception"),
        "spec"
    );
    assert_eq!(
        classify_mode("MODE: a proposed EXCEPTION in specs/x"),
        "exception"
    );
    assert_eq!(classify_mode("MODE - plan decisions for x"), "plan");
    assert_eq!(classify_mode("MODE: other words\nPLAN REVIEW"), "plan");
    assert_eq!(classify_mode("MODE 4: PLAN REVIEW"), "plan");
    assert_eq!(classify_mode("MODE 1: EXCEPTION CHECK"), "exception");
    assert_eq!(classify_mode("review it"), "spec");
}

#[test]
fn the_last_word_or_a_stated_line_is_the_verdict() {
    assert_eq!(
        verdict_of("**Verdict: CHANGES REQUIRED.** later FAITHFUL"),
        "CHANGES REQUIRED"
    );
    assert_eq!(
        verdict_of("CHANGES REQUIRED nowhere.\n\n## FAITHFUL"),
        "FAITHFUL"
    );
    assert_eq!(verdict_of("nothing"), "");
}

#[test]
fn what_passes_untouched() {
    let d = world("pass");
    let c = plain(&d);
    assert!(dispatch("settlement-review", "x", "", &d, &c).is_none());
    assert_eq!(
        spec("MODE 4: PLAN REVIEW of specs/301-x", &d, &c).rule,
        "other-mode"
    );
    assert_eq!(
        spec("MODE 1: EXCEPTION CHECK specs/301-x", &d, &c).rule,
        "other-mode"
    );
    assert_eq!(spec("MODE 2 of specs/999-none", &d, &c).rule, "no-feature");
    assert_eq!(
        spec("MODE 2 of nothing", &d, &c).detail,
        "no specs/NNN-slug in the prompt"
    );
    let outside = json!({"tool_input": {"subagent_type": "spec-fidelity", "prompt": "MODE 2 of specs/301-x"}});
    assert_eq!(
        verdict(&outside, "Agent", "", &c).unwrap().rule,
        "no-feature"
    );
    assert!(verdict(&outside, "Bash", "", &c).is_none());
}

#[test]
fn the_first_dispatch_snapshots_and_a_history_says_so() {
    let d = world("first");
    let c = plain(&d);
    assert_eq!(spec("MODE 2 of specs/301-x", &d, &c).rule, "first-round");
    assert!(d.join(".git/review-round/301-x/snapshot/spec.md").is_file());
    let o = spec("MODE 2 of specs/302-y", &d, &c);
    assert_eq!(o.rule, "history-without-snapshot");
    assert!(rewrite_of(&o).is_none());
    assert!(matches!(&o.answer[..], [Answer::Notice(t)] if t.contains("no earlier snapshot")));
    assert_eq!(
        std::fs::read_to_string(round_file(&d, "302-y")).unwrap(),
        "1\n"
    );
}

#[test]
fn a_later_round_is_rewritten_with_the_diff_and_the_verdict() {
    let d = world("later");
    let c = plain(&d);
    spec("MODE 2 of specs/301-x", &d, &c);
    std::fs::write(
        d.join("specs/301-x/spec.md"),
        "# 301\n\nFR-001 stands.\nFR-002 added.\n",
    )
    .unwrap();
    std::fs::write(d.join("specs/301-x/new.md"), "brand new\n").unwrap();
    let tr = subagent(
        &d,
        "agent-1.jsonl",
        "MODE 2 of specs/301-x",
        "1. vague.\n\n**CHANGES REQUIRED**",
        1000,
    );
    subagent(
        &d,
        "agent-2.jsonl",
        "MODE 2 of specs/303-z; sibling specs/301-x",
        "SIBLING\n**FAITHFUL**",
        2000,
    );
    let o = dispatch(
        "spec-fidelity",
        "MODE 3 round 2 of specs/301-x",
        &tr,
        &d,
        &c,
    )
    .unwrap();
    assert_eq!((o.event, o.rule.as_str()), ("rewrote", "mode-3-preamble"));
    let v = rewritten(&o);
    let sent = v["prompt"].as_str().unwrap();
    assert!(sent.starts_with("MODE 3 (VERIFY) - round 2 of feature 301-x"));
    assert!(
        sent.contains("+FR-002 added.")
            && sent.contains("--- a/spec.md")
            && sent.contains("+brand new")
    );
    assert!(sent.contains("1. vague.") && sent.contains("VERBATIM") && !sent.contains("SIBLING"));
    assert!(sent.ends_with("=== The session's prompt follows ===\nMODE 3 round 2 of specs/301-x"));
    assert_eq!(
        (v["subagent_type"].as_str(), v["description"].as_str()),
        (Some("spec-fidelity-verify"), Some("x"))
    );
    assert_eq!(
        std::fs::read_to_string(round_file(&d, "301-x")).unwrap(),
        "2\n"
    );
    let next = dispatch("spec-fidelity-verify", "by hand specs/301-x", &tr, &d, &c).unwrap();
    assert!(rewritten(&next)["prompt"]
        .as_str()
        .unwrap()
        .contains("Nothing in the feature directory changed"));
}

#[test]
fn the_verdict_decides_the_round() {
    let d = world("verdicts");
    let c = plain(&d);
    spec("MODE 2 of specs/301-x", &d, &c);
    let tr = subagent(
        &d,
        "agent-1.jsonl",
        "MODE 2 of specs/301-x",
        "no substance\n**Verdict: NOT-REVIEWABLE.**",
        1000,
    );
    let o = dispatch("spec-fidelity", "MODE 2 of specs/301-x", &tr, &d, &c).unwrap();
    assert_eq!(o.rule, "first-reading-after-not-reviewable");
    std::fs::write(round_file(&d, "301-x"), "3\n").unwrap();
    let same = dispatch("spec-fidelity", "MODE 2 of specs/301-x", &tr, &d, &c).unwrap();
    assert!(rewritten(&same)["prompt"]
        .as_str()
        .unwrap()
        .starts_with("MODE 3 (VERIFY) - round 3 "));
    let tr2 = subagent(
        &d,
        "agent-3.jsonl",
        "MODE 3 (VERIFY) - round 3 of feature 301-x",
        "ok\n\n## FAITHFUL",
        3000,
    );
    let o = dispatch("spec-fidelity", "MODE 3 of specs/301-x", &tr2, &d, &c).unwrap();
    assert!(rewritten(&o)["prompt"]
        .as_str()
        .unwrap()
        .contains("NEW PASS"));
    assert_eq!(
        std::fs::read_to_string(d.join(".git/review-round/301-x/pass")).unwrap(),
        "2\n"
    );
    let silent = subagent(
        &d,
        "agent-4.jsonl",
        "MODE 3 of specs/301-x",
        "no word here",
        4000,
    );
    std::fs::write(
        d.join("specs/301-x/spec.md"),
        "# 301\n\n## Review history\n\n- spec-fidelity FAITHFUL\n",
    )
    .unwrap();
    assert!(dispatch("spec-fidelity", "MODE 3 of specs/301-x", &silent, &d, &c).is_some());
}

#[test]
fn the_history_is_the_fallback_and_nothing_is_said_as_much() {
    let d = world("history");
    let c = plain(&d);
    spec("MODE 2 of specs/302-y", &d, &c);
    let o = spec("MODE 3 of specs/302-y", &d, &c);
    assert!(rewritten(&o)["prompt"]
        .as_str()
        .unwrap()
        .contains("as the SESSION recorded it"));
    spec("MODE 2 of specs/301-x", &d, &c);
    let bare = spec("MODE 3 of specs/301-x", &d, &c);
    assert!(rewritten(&bare)["prompt"]
        .as_str()
        .unwrap()
        .contains("No previous verdict could be recovered"));
    assert!(dispatch("spec-fidelity", "MODE 3 of specs/301-x", "/no.txt", &d, &c).is_some());
}

#[test]
fn an_old_value_refuses_the_round_before_it_is_spent() {
    let d = world("stale");
    let c = ctx(&d, "echo 2; echo the rendered lines", NO_ACTIVE);
    spec("MODE 2 of specs/301-x", &d, &c);
    let o = spec("MODE 3 of specs/301-x", &d, &c);
    assert_eq!(o.rule, "stale-terms");
    assert!(refused(&o, "the rendered lines") && refused(&o, "make stale-terms F=301"));
    assert_eq!(
        std::fs::read_to_string(round_file(&d, "301-x")).unwrap(),
        "1\n"
    );
    assert!(refused(
        &spec("MODE 3 of specs/301-x STALE_TERMS_OK", &d, &c),
        "with no reason"
    ));
    let o = spec(
        "MODE 3 of specs/301-x STALE_TERMS_OK=\"it describes the proposal\"",
        &d,
        &c,
    );
    assert_eq!(o.rule, "mode-3-preamble-stale-ok");
    assert!(o.detail.contains("describes the proposal"));
}

#[test]
fn the_escape_refreshes_the_snapshot_and_needs_a_reason() {
    let d = world("escape");
    let c = plain(&d);
    assert!(refused(
        &spec("MODE 3 of specs/301-x REVIEW_ROUND_OK", &d, &c),
        "with no reason"
    ));
    let esc = "MODE 3 of specs/301-x REVIEW_ROUND_OK=\"restructured, read it whole\"";
    assert_eq!(spec(esc, &d, &c).rule, "review-round-ok");
    assert!(d.join(".git/review-round/301-x/snapshot/spec.md").is_file());
    assert_eq!(
        std::fs::read_to_string(round_file(&d, "301-x")).unwrap(),
        "1\n"
    );
    let tr = subagent(
        &d,
        "agent-1.jsonl",
        "MODE 2 of specs/301-x",
        "**FAITHFUL**",
        1000,
    );
    std::fs::write(round_file(&d, "301-x"), "3\n").unwrap();
    assert_eq!(
        dispatch("spec-fidelity", esc, &tr, &d, &c).unwrap().rule,
        "review-round-ok"
    );
    assert_eq!(
        std::fs::read_to_string(round_file(&d, "301-x")).unwrap(),
        "1\n"
    );
    assert_eq!(
        std::fs::read_to_string(d.join(".git/review-round/301-x/pass")).unwrap(),
        "2\n"
    );
    assert_eq!(
        spec(
            "MODE 3 of specs/999-none REVIEW_ROUND_OK=\"a whole read of it\"",
            &d,
            &c
        )
        .event,
        "escaped"
    );
    let none = json!({"tool_input": {"subagent_type": "spec-fidelity", "prompt": esc}});
    assert_eq!(verdict(&none, "Agent", "", &c).unwrap().event, "escaped");
}

#[test]
fn past_the_spec_cap_the_arbiter_rules() {
    let d = world("cap");
    let c = plain(&d);
    spec("MODE 2 of specs/301-x", &d, &c);
    std::fs::write(round_file(&d, "301-x"), "5\n").unwrap();
    let o = spec("MODE 2 of specs/301-x", &d, &c);
    assert_eq!(o.rule, "spec-round-cap");
    assert!(
        refused(&o, "BLOCKED: round 6 of specs/301-x's spec review")
            && refused(
                &o,
                "make arbiter-bundle TRIGGER=\"round:spec-fidelity|301-x#1@6"
            )
    );
    assert_eq!(
        std::fs::read_to_string(round_file(&d, "301-x")).unwrap(),
        "5\n"
    );
    let o = spec(
        "MODE 2 of specs/301-x ARBITER_OK=\"the fixture cannot build it\"",
        &d,
        &c,
    );
    assert_eq!(o.rule, "mode-3-preamble-stale-ok");
    ruled(
        &d,
        &[
            "round:spec-fidelity|301-x#1@7:continue",
            "round:spec-fidelity|301-x#1@8:continue",
        ],
    );
    std::fs::write(round_file(&d, "301-x"), "6\n").unwrap();
    assert_eq!(spec("MODE 2 of specs/301-x", &d, &c).event, "rewrote");
    ruled(
        &d,
        &[
            "round:spec-fidelity|301-x#1@7:continue",
            "round:spec-fidelity|301-x#1@8:accept",
        ],
    );
    assert!(rewritten(&spec("MODE 2 of specs/301-x", &d, &c))["prompt"]
        .as_str()
        .unwrap()
        .contains("round 1 of feature"));
}

#[test]
fn a_tasks_plan_rounds_are_counted_back_to_its_clear() {
    let d = world("plan");
    let dir = d.join("specs/301-x");
    let r = |v: &str, b: &str| json!({"verdict": v, "blocks": [b]});
    let reviews = json!({"block_reviews": [r("BLOCKED", "### T14 D"), r("CLEAR", "### T14 D"), r("BLOCKED", "### T14 A"), r("BLOCKED", "### T03 D"), r("BLOCKED", "## T14 D"), r("CLEAR", "### T140 D")]});
    std::fs::write(dir.join("plan-review.json"), reviews.to_string()).unwrap();
    assert_eq!(plan_rounds(&dir, "T14"), 2);
    assert_eq!(plan_rounds(&d.join("none"), "T14"), 0);
}

#[test]
fn the_third_plan_round_goes_to_the_arbiter() {
    let d = world("plancap");
    let dir = d.join("specs/301-x");
    let active = format!("echo '[\"{}\", \"T14\"]'", dir.display());
    let c = ctx(&d, NO_STALE, &active);
    let r = json!({"verdict": "BLOCKED", "blocks": ["### T14 D"]});
    std::fs::write(
        dir.join("plan-review.json"),
        json!({"block_reviews": [r]}).to_string(),
    )
    .unwrap();
    let plan = "MODE 4: PLAN REVIEW of 2 block(s)";
    assert_eq!(spec(plan, &d, &c).rule, "other-mode");
    std::fs::write(
        dir.join("plan-review.json"),
        json!({"block_reviews": [r, r]}).to_string(),
    )
    .unwrap();
    let o = spec(plan, &d, &c);
    assert_eq!(o.rule, "plan-round-cap");
    assert!(
        refused(&o, "BLOCKED: round 3 of T14's plan review")
            && refused(&o, "round:spec-fidelity|plan:301-x#T14@3")
    );
    let esc = spec(
        "MODE 4: PLAN REVIEW ARBITER_OK=\"the arbiter ruled it\"",
        &d,
        &c,
    );
    assert_eq!(
        (esc.event, esc.rule.as_str()),
        ("escaped", "plan-round-cap")
    );
    ruled(&d, &["round:spec-fidelity|plan:301-x#T14@4:continue"]);
    assert_eq!(spec(plan, &d, &c).rule, "other-mode");
    // feature 449 T141: a gate that fails, a null directory, an empty task or output that is not JSON holds nothing, as the snippet's did
    let dir_s = dir.display().to_string();
    for active in [
        format!("echo '[\"{dir_s}\", \"T14\"]'; exit 1"),
        "echo '[null, \"T14\"]'".to_owned(),
        format!("echo '[\"{dir_s}\", \"\"]'"),
        "echo not json".to_owned(),
    ] {
        ruled(&d, &[]);
        assert_eq!(
            spec(plan, &d, &ctx(&d, NO_STALE, &active)).rule,
            "other-mode"
        );
    }
}

#[test]
fn the_answers_and_the_command_line() {
    let d = world("answers");
    let c = plain(&d);
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Agent", "tool_input": {"subagent_type": "spec-fidelity", "prompt": "MODE 2 of specs/301-x"}}),
    };
    assert!(answer(&e, &Session::from_input(&e.input), &d.to_string_lossy(), &c).is_empty());
    let other = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Agent", "tool_input": {"subagent_type": "quote-check"}}),
    };
    assert!(answer(&other, &Session::from_input(&other.input), "", &c).is_empty());
    let args = |a: &[&str]| a.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>();
    assert_eq!(
        cli(&args(&["state", &d.to_string_lossy(), "301-x"])).stdout,
        "round=1 snapshot=yes"
    );
    assert_eq!(
        cli(&args(&["state", "/no", "x"])).stdout,
        "round=0 snapshot=no"
    );
    assert_eq!(
        cli(&args(&["verdict-of", "**FAITHFUL**"])).stdout,
        "FAITHFUL"
    );
    assert_eq!(cli(&args(&["nope"])).code, 1);
    let bash = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash"}),
    };
    assert!(decide(&bash, &Session::from_input(&bash.input)).is_empty());
    let outside = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Agent", "cwd": "/no/such/place", "tool_input": {"subagent_type": "spec-fidelity", "prompt": "MODE 1"}}),
    };
    assert!(decide(&outside, &Session::from_input(&outside.input)).is_empty());
    let map = d.join(".clones/.session-clones");
    std::fs::create_dir_all(&map).unwrap();
    std::fs::write(map.join("s-rr"), d.to_string_lossy().as_bytes()).unwrap();
    let main = d.to_string_lossy().into_owned();
    let named = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Agent", "session_id": "s-rr", "tool_input": {"subagent_type": "spec-fidelity", "prompt": "MODE 1"}}),
    };
    let session = Session::with_env(&named.input, |k| (k == "CLONE_MAIN").then(|| main.clone()));
    assert!(decide(&named, &session).is_empty());
}

#[test]
fn the_transcripts_odd_shapes_are_read_past() {
    let d = world("odd");
    let c = plain(&d);
    spec("MODE 2 of specs/301-x", &d, &c);
    let tr = subagent(
        &d,
        "agent-1.jsonl",
        "MODE 2 of specs/301-x",
        "**CHANGES REQUIRED** really",
        1000,
    );
    let sub = d.join("sess/subagents");
    let good = std::fs::read_to_string(sub.join("agent-1.jsonl")).unwrap();
    let blank = json!({"message": {"role": "assistant", "content": [{"type": "tool_use"}]}});
    std::fs::write(
        sub.join("agent-1.jsonl"),
        format!("{good}\n{blank}\nnot json"),
    )
    .unwrap();
    std::fs::write(sub.join("agent-8.jsonl"), "not json first\n").unwrap();
    std::fs::write(sub.join("agent-9.jsonl"), "{}\n").unwrap();
    std::fs::write(sub.join("other.txt"), "x").unwrap();
    let o = dispatch("spec-fidelity", "MODE 3 of specs/301-x", &tr, &d, &c).unwrap();
    assert!(rewritten(&o)["prompt"].as_str().unwrap().contains("really"));
}

#[test]
fn the_snapshot_walks_directories_and_a_missing_spec_is_no_history() {
    let d = world("walk");
    let c = plain(&d);
    std::fs::remove_file(d.join("specs/301-x/spec.md")).unwrap();
    std::fs::create_dir_all(d.join("specs/301-x/deep")).unwrap();
    std::fs::create_dir_all(d.join("specs/301-x/__pycache__")).unwrap();
    std::fs::write(d.join("specs/301-x/deep/a.md"), "x").unwrap();
    std::fs::write(d.join("specs/301-x/__pycache__/b.py"), "x").unwrap();
    std::fs::write(d.join("specs/301-x/skipped.bin"), "x").unwrap();
    assert_eq!(spec("MODE 2 of specs/301-x", &d, &c).rule, "first-round");
    let snap = d.join(".git/review-round/301-x/snapshot");
    assert!(
        snap.join("deep/a.md").is_file()
            && !snap.join("__pycache__").exists()
            && !snap.join("skipped.bin").exists()
    );
}

#[test]
fn an_escape_after_a_faithful_history_starts_a_new_pass() {
    let d = world("hist-esc");
    let c = plain(&d);
    std::fs::write(
        d.join("specs/302-y/spec.md"),
        "## Review history\n\n- round 2, FAITHFUL\n",
    )
    .unwrap();
    assert_eq!(
        spec(
            "MODE 3 of specs/302-y REVIEW_ROUND_OK=\"a whole read of it\"",
            &d,
            &c
        )
        .event,
        "escaped"
    );
    assert_eq!(
        std::fs::read_to_string(d.join(".git/review-round/302-y/pass")).unwrap(),
        "2\n"
    );
}

#[test]
fn inside_a_repository_the_clone_is_its_top_level() {
    let d = world("repo");
    let at = d.to_string_lossy().into_owned();
    std::fs::remove_dir_all(d.join(".git")).unwrap();
    assert!(crate::shared::tool::ask(Path::new("/"), "git", &["init", "-q", &at], "").ok());
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Agent", "cwd": at, "tool_input": {"subagent_type": "spec-fidelity", "prompt": "MODE 1"}}),
    };
    assert!(decide(&e, &Session::from_input(&e.input)).is_empty());
}
