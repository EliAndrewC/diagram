//! The plan gate's command line, and what the other test modules share.

use std::path::{Path, PathBuf};
use std::process::Command;
use std::sync::Once;

use serde_json::{json, Value};

use super::answer;
use super::sections::digest;
use crate::checks::scratch;

pub(super) const PLAN: &str = "# plan\n\n**P1 - a decision.**\n";
pub(super) const TASKS: &str =
    "# Tasks\n\n- [ ] T01 plan review\n      verify:\n- [ ] T02 build it\n      verify:\n";
pub(super) const PLAN_TASKS: &str = "# plan\n\n**D1 - a decision.** Each tub by a door.\n\n## T05 the bath (amendment 1)\n\n- the bath 10 x 8 ft (GUESS)\n\n## T06 the wells\n\n- a well by the kitchen\n";

pub(super) fn narrow_bad() -> Value {
    json!({"id": "P1", "summary": "a cutoff", "class": "narrowing", "ruling": "NOT LEGITIMATE", "why": "w"})
}

pub(super) fn narrow_ok() -> Value {
    json!({"id": "P1", "summary": "a cutoff", "class": "narrowing", "ruling": "LEGITIMATE", "why": "w"})
}

pub(super) fn within() -> Value {
    json!({"id": "P2", "summary": "a module", "class": "within", "why": "w"})
}

/// The guard census of these tests: never the live one.
pub(super) fn quiet_census() -> PathBuf {
    static ONCE: Once = Once::new();
    let dir = std::env::temp_dir().join(format!("l7r-gate-plan-census-{}", std::process::id()));
    ONCE.call_once(|| std::env::set_var("GUARD_LOG_DIR", &dir));
    dir
}

pub(super) fn feature_at(
    root: &Path,
    plan: Option<&str>,
    review: Option<&Value>,
    name: &str,
) -> PathBuf {
    quiet_census();
    let dir = root.join("specs").join(name);
    std::fs::create_dir_all(&dir).unwrap();
    std::fs::write(dir.join("tasks.md"), TASKS).unwrap();
    std::fs::write(
        dir.join("request.md"),
        "# the request\n\n> the GM's words\n",
    )
    .unwrap();
    if let Some(text) = plan {
        std::fs::write(dir.join("plan.md"), text).unwrap();
    }
    if let Some(value) = review {
        std::fs::write(dir.join("plan-review.json"), value.to_string()).unwrap();
    }
    dir
}

pub(super) fn feature(plan: Option<&str>, review: Option<&Value>) -> PathBuf {
    feature_at(&scratch("plan"), plan, review, "243-x")
}

pub(super) fn current(decisions: &[Value], verdict: &str, plan: &str) -> Value {
    json!({"plan_sha256": digest(plan.as_bytes()), "decisions": decisions, "verdict": verdict})
}

pub(super) fn git(root: &Path, args: &[&str]) -> String {
    let done = Command::new("git")
        .arg("-C")
        .arg(root)
        .args(["-c", "user.name=t", "-c", "user.email=t@t"])
        .args(args)
        .output()
        .unwrap();
    assert!(done.status.success(), "git {args:?}");
    String::from_utf8_lossy(&done.stdout).trim().to_owned()
}

pub(super) fn repo() -> PathBuf {
    let root = scratch("plan-repo");
    git(&root, &["init", "-q", "-b", "main"]);
    root
}

pub(super) fn run(root: &Path, words: &[&str]) -> crate::Reply {
    run_with(root, words, "", None)
}

/// The claims tools, as a plan test sees them: nothing owed a triage.
fn no_claims(_: &[String]) -> crate::Reply {
    crate::Reply {
        stdout: String::new(),
        stderr: String::new(),
        code: 0,
    }
}

fn run_with(root: &Path, words: &[&str], stdin: &str, escaped: Option<&str>) -> crate::Reply {
    quiet_census();
    let owned: Vec<String> = words.iter().map(|s| (*s).to_owned()).collect();
    answer(
        &owned,
        root,
        &root.join("bundles"),
        "bash",
        &mut stdin.as_bytes(),
        escaped,
        &no_claims,
    )
}

fn write_json(dir: &Path, name: &str, value: &Value) -> String {
    let path = dir.join(name);
    std::fs::write(&path, value.to_string()).unwrap();
    path.display().to_string()
}

#[test]
fn the_record_verbs_resolve_a_feature_and_report() {
    let dir = feature(Some(PLAN), None);
    let root = dir.parent().unwrap().parent().unwrap().to_owned();
    let src = write_json(&root, "review.json", &current(&[within()], "CLEAR", PLAN));
    let spec = dir.display().to_string();
    let declined = run(&root, &["record", &spec, &src, "--as", "main"]);
    assert_eq!(declined.code, 2);
    assert!(declined.stderr.contains("declined"));
    assert_eq!(
        run(
            &root,
            &["record", "specs/nope", &src, "--as", "spec-fidelity"]
        )
        .code,
        2
    );
    assert_eq!(
        run(
            &root,
            &["record", &spec, "/no/such.json", "--as", "spec-fidelity"]
        )
        .code,
        1
    );
    let done = run(&root, &["record", &spec, &src, "--as", "spec-fidelity"]);
    assert_eq!(done.code, 0);
    assert!(done.stdout.contains("CLEAR recorded"));
    assert_eq!(run(&root, &["owed", &spec]).code, 0);
    let other = feature(Some(PLAN), None);
    assert_eq!(run(&root, &["owed", &other.display().to_string()]).code, 1);
    assert_eq!(run(&root, &["what"]).code, 2);
    assert_eq!(run(&root, &["record", &spec, &src, "--bad", "x"]).code, 2);
}

#[test]
fn the_task_and_block_verdict_verbs() {
    let root = repo();
    feature_at(&root, Some(PLAN_TASKS), None, "375-x");
    let sha = run(&root, &["section-sha", "375", "T05"])
        .stdout
        .trim()
        .to_owned();
    assert_eq!(sha.len(), 64);
    let src = write_json(
        &root,
        "v.json",
        &json!({"section_sha256": sha, "decisions": []}),
    );
    assert_eq!(
        run(&root, &["record-task", "375", "T05", &src, "--as", "main"]).code,
        2
    );
    assert_eq!(
        run(
            &root,
            &["record-task", "999", "T05", &src, "--as", "spec-fidelity"]
        )
        .code,
        2
    );
    assert!(run(
        &root,
        &["record-task", "375", "T05", &src, "--as", "spec-fidelity"]
    )
    .stdout
    .contains("CLEAR recorded for 375-x T05 (0 decision(s))"));
    let empty = write_json(&root, "e.json", &json!({}));
    assert_eq!(
        run(
            &root,
            &["record-task", "375", "T05", &empty, "--as", "spec-fidelity"]
        )
        .code,
        1
    );
    let key = "## T06 the wells";
    let block = super::sections::block_digest("## T06 the wells\n\n- a well by the kitchen\n");
    let src = write_json(
        &root,
        "b.json",
        &json!({"blocks": {key: block}, "decisions": []}),
    );
    assert!(run(
        &root,
        &["record-blocks", "375", &src, "--as", "spec-fidelity"]
    )
    .stdout
    .contains("for 1 block(s)"));
    let slimmed = run(&root, &["slim", "375"]);
    assert!(
        slimmed.stdout.contains("its verdicts kept"),
        "{}",
        slimmed.stderr
    );
    assert_eq!(run(&root, &["slim", "999"]).code, 2);
    let without = feature_at(&root, Some("# x\n"), None, "376-y");
    assert_eq!(run(&root, &["slim", "376"]).stdout, "");
    assert!(without.is_dir());
}

#[test]
fn the_decide_commands_and_the_guard_that_waits_for_them() {
    let root = repo();
    let dir = feature_at(&root, Some(PLAN_TASKS), None, "375-x");
    std::fs::write(
        dir.join("tasks.md"),
        "- [ ] T05 the bath\n- [ ] T06 the wells\n",
    )
    .unwrap();
    let decided = run(&root, &["decide", "375", "T05"]);
    assert!(
        decided
            .stdout
            .contains("MODE 4: PLAN REVIEW of one task's section"),
        "{}",
        decided.stderr
    );
    let manifest = decided
        .stdout
        .split("read ")
        .nth(1)
        .unwrap()
        .split(" and the files")
        .next()
        .unwrap()
        .to_owned();
    assert!(std::fs::read_to_string(manifest)
        .unwrap()
        .contains("TASK=T05"));
    assert_eq!(run(&root, &["decide", "375", "T99"]).code, 2);
    std::fs::create_dir_all(root.join(".specify")).unwrap();
    std::fs::write(
        root.join(".specify/feature.json"),
        "{\"feature_directory\": \"specs/375-x\"}",
    )
    .unwrap();
    let waits = run(&root, &["decided", &root.display().to_string()]);
    assert_eq!(waits.code, 1);
    assert!(waits.stdout.contains("T05: its plan section"));
    let sha = run(&root, &["section-sha", "375", "T05"])
        .stdout
        .trim()
        .to_owned();
    let src = write_json(
        &root,
        "v.json",
        &json!({"section_sha256": sha, "decisions": []}),
    );
    assert_eq!(
        run(
            &root,
            &["record-task", "375", "T05", &src, "--as", "spec-fidelity"]
        )
        .code,
        0
    );
    assert_eq!(
        run(&root, &["decided", &root.display().to_string()]).code,
        0
    );
}

#[test]
fn decide_refuses_on_the_lint_and_on_the_checklist_before_any_review() {
    let root = repo();
    feature_at(
        &root,
        Some("## T05 x\n\nthe GM said \"not in the request at all\".\n"),
        None,
        "375-x",
    );
    let linted = run(&root, &["decide", "375", "T05"]);
    assert_eq!(linted.code, 2);
    assert!(linted
        .stderr
        .contains("decide: refused - the section quotes the GM"));
    feature_at(&root, Some(PLAN_TASKS), None, "376-y");
    std::fs::create_dir_all(root.join("docs")).unwrap();
    std::fs::write(
        root.join("docs/approach-checklist.md"),
        "## A. x\n\n1. one\n",
    )
    .unwrap();
    let asked = run(&root, &["decide", "376", "T05"]);
    assert_eq!(asked.code, 2);
    assert!(asked
        .stderr
        .contains("decide: refused - T05 has no `### T05 Approach` block"));
}

#[test]
fn a_wording_only_section_is_named_and_a_missing_request_writes_no_bundle() {
    let root = repo();
    feature_at(
        &root,
        Some("## T05 x\n\n### T05 Decisions\n\n**Wording only.** a comment.\n"),
        None,
        "375-x",
    );
    assert!(run(&root, &["decide", "375", "T05"])
        .stdout
        .contains("wording only - no plan review is owed"));
    let dir = feature_at(&root, Some(PLAN_TASKS), None, "376-y");
    std::fs::remove_file(dir.join("request.md")).unwrap();
    let refused = run(&root, &["decide", "376", "T05"]);
    assert_eq!(refused.code, 1);
    assert!(refused.stderr.contains("request.md is missing"));
    let delta = run(&root, &["delta", "376"]);
    assert_eq!(delta.code, 1);
    assert!(delta.stderr.contains("request.md is missing"));
}

#[test]
fn the_delta_owes_changed_blocks_and_says_when_none_is() {
    let root = repo();
    let dir = feature_at(&root, Some(PLAN_TASKS), None, "375-x");
    let owed = run(&root, &["delta", "375"]);
    assert!(
        owed.stdout
            .contains("changed block(s) of feature 375-x's plan"),
        "{}",
        owed.stderr
    );
    let src = write_json(&root, "w.json", &current(&[], "CLEAR", PLAN_TASKS));
    assert_eq!(
        run(&root, &["record", "375", &src, "--as", "spec-fidelity"]).code,
        0
    );
    assert!(run(&root, &["delta", "375"])
        .stdout
        .contains("no block of 375-x's plan is owed"));
    std::fs::write(
        dir.join("plan.md"),
        PLAN_TASKS.replace("**D1 - a decision.**", "(observed 2099-01-01T00:00Z)"),
    )
    .unwrap();
    assert_eq!(run(&root, &["delta", "375"]).code, 0);
    std::fs::write(
        dir.join("plan.md"),
        format!("{PLAN_TASKS}\n### T07 part B (2099-01-01T00:00Z)\n\nx\n"),
    )
    .unwrap();
    let ahead = run(&root, &["delta", "375"]);
    assert_eq!(ahead.code, 1);
    assert!(ahead.stderr.contains("stamped after the clock"));
    std::fs::write(
        dir.join("plan.md"),
        format!("{PLAN_TASKS}\n## T07 x\n\nthe GM said \"words nobody said\".\n"),
    )
    .unwrap();
    let linted = run(&root, &["delta", "375"]);
    assert_eq!(linted.code, 1);
    assert!(linted.stderr.contains("refused, no bundle written"));
    assert_eq!(run(&root, &["delta", "999"]).code, 2);
    let blocked = write_json(
        &root,
        "x.json",
        &json!({"blocks": {"## T07 x": super::sections::block_digest("## T07 x\n")}, "decisions": []}),
    );
    std::fs::write(dir.join("plan.md"), format!("{PLAN_TASKS}\n## T07 x\n")).unwrap();
    let bad = current(
        &[narrow_bad()],
        "BLOCKED",
        &format!("{PLAN_TASKS}\n## T07 x\n"),
    );
    let src = write_json(&root, "w.json", &bad);
    assert_eq!(
        run(&root, &["record", "375", &src, "--as", "spec-fidelity"]).code,
        0
    );
    assert!(run(&root, &["delta", "375"]).stdout.contains("MODE 4"));
    assert!(blocked.ends_with("x.json"));
}

#[test]
fn archive_and_accept_verbs() {
    let root = repo();
    let dir = feature_at(&root, Some(PLAN_TASKS), None, "375-x");
    assert!(run(&root, &["archive", "375"])
        .stdout
        .contains("0 task section(s) moved"));
    std::fs::write(
        dir.join("tasks.md"),
        "- [x] T05 the bath\n- [ ] T06 the wells\n",
    )
    .unwrap();
    let src = write_json(&root, "w.json", &current(&[], "CLEAR", PLAN_TASKS));
    assert_eq!(
        run(&root, &["record", "375", &src, "--as", "spec-fidelity"]).code,
        0
    );
    assert!(run(&root, &["archive", "375"])
        .stdout
        .contains("1 task section(s) moved to 375-x/plan-done.md: T05"));
    assert_eq!(run(&root, &["arbiter-accept", "999", "x"]).code, 2);
    let trigger = "round:spec-fidelity|plan:375-x#T06@3";
    assert_eq!(run(&root, &["arbiter-accept", "375", trigger]).code, 2);
    std::fs::write(
        dir.join("arbiter.jsonl"),
        format!("{}\n", json!({"trigger": trigger, "ruling": "accept"})),
    )
    .unwrap();
    assert!(run(&root, &["arbiter-accept", "375", trigger])
        .stdout
        .contains("recorded CLEAR on"));
    assert_eq!(run(&root, &["arbiter-accept", "375", "no-such"]).code, 1);
}

#[test]
fn the_push_verb_lists_what_it_owes() {
    let root = repo();
    std::fs::write(root.join("README"), "x").unwrap();
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "base"]);
    git(&root, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
    let dir = feature_at(&root, Some(PLAN), None, "001-a");
    std::fs::write(
        dir.join("tasks.md"),
        TASKS.replace("- [ ] T01", "- [x] T01"),
    )
    .unwrap();
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "work"]);
    let owed = run(&root, &["push"]);
    assert_eq!(owed.code, 1);
    assert!(owed
        .stdout
        .starts_with("specs/001-a\tplan-review-missing\t"));
    assert_eq!(run(&root, &["push", "HEAD..HEAD"]).code, 0);
}

#[test]
fn a_tick_is_refused_then_escaped_only_with_a_reason_and_recorded() {
    let dir = feature(Some(PLAN), None);
    let root = dir.parent().unwrap().parent().unwrap().to_owned();
    std::fs::create_dir_all(root.join("dev")).unwrap();
    let (spec, top) = (dir.display().to_string(), root.display().to_string());
    let ask = |escaped: Option<&str>| {
        run_with(&root, &["door", "tick-permitted", &spec, &top], "", escaped).stdout
    };
    let refused = ask(None);
    assert!(
        refused.contains("no current CLEAR review")
            && refused.contains("make plan-verdict")
            && refused.starts_with("[false,")
    );
    assert!(ask(Some("x")).contains("needs a REASON"));
    let passed = ask(Some("a superseded plan nobody implements"));
    assert!(passed.starts_with("[true,") && passed.contains("BYPASSED"));
    let month = std::fs::read_dir(root.join("dev/bypass-log"))
        .unwrap()
        .next()
        .unwrap()
        .unwrap()
        .path();
    let entries: Vec<_> = std::fs::read_dir(month).unwrap().flatten().collect();
    assert_eq!(entries.len(), 1);
    assert!(std::fs::read_to_string(entries[0].path())
        .unwrap()
        .contains("a superseded plan"));
    let src = write_json(&root, "w.json", &current(&[], "CLEAR", PLAN));
    assert_eq!(
        run(&root, &["record", &spec, &src, "--as", "spec-fidelity"]).code,
        0
    );
    assert_eq!(ask(None), "[true,\"\"]\n");
}

#[test]
fn the_door_forwards_each_verb() {
    let root = repo();
    let dir = feature_at(&root, Some(PLAN_TASKS), None, "375-x");
    let top = root.display().to_string();
    let spec = dir.display().to_string();
    let sections = run_with(&root, &["door", "task-sections"], PLAN_TASKS, None).stdout;
    assert!(sections.contains("\"T05\":"));
    assert!(run_with(&root, &["door", "blocks"], "# x\n", None)
        .stdout
        .starts_with("[[\"preamble\","));
    assert_eq!(
        run(&root, &["door", "active-task", &top]).stdout,
        "[null,\"\"]\n"
    );
    assert_eq!(
        run(&root, &["door", "touched-features", &top, "HEAD"]).stdout,
        "[]\n"
    );
    assert!(run(&root, &["door", "resolve", "375", &top])
        .stdout
        .contains("375-x"));
    assert_eq!(
        run(&root, &["door", "resolve", "999", &top]).stdout,
        "null\n"
    );
    assert_eq!(
        run(&root, &["door", "approach-refusal", &spec, &top, "T05"]).stdout,
        "null\n"
    );
    assert_eq!(
        run(&root, &["door", "approach-ruled", &top, "other:x"]).stdout,
        "null\n"
    );
    assert_eq!(run(&root, &["door", "archive", &spec]).stdout, "[]\n");
    assert_eq!(run(&root, &["door", "accept", &spec, "no-such"]).code, 1);
    assert_eq!(
        run_with(&root, &["door", "wording-only"], "x", None).stdout,
        "false\n"
    );
    std::fs::write(
        dir.join("arbiter.jsonl"),
        format!(
            "{}\n",
            json!({"trigger": "round:spec-fidelity|plan:x", "ruling": "accept"})
        ),
    )
    .unwrap();
    assert!(run(
        &root,
        &["door", "accept", &spec, "round:spec-fidelity|plan:x"]
    )
    .stdout
    .starts_with('['));
    std::fs::create_dir_all(root.join("dev")).unwrap();
    assert_eq!(
        run(
            &root,
            &["door", "bypass-record", &top, "push", "a reason given"]
        )
        .code,
        0
    );
    assert_eq!(run(&root, &["door", "nonsense"]).code, 2);
}

#[test]
fn the_approach_verbs_record_their_run() {
    let root = repo();
    let dir = feature_at(&root, Some("## T05 x\n"), None, "375-x");
    std::fs::create_dir_all(root.join("docs")).unwrap();
    std::fs::write(
        root.join("docs/approach-checklist.md"),
        "## A. x\n\n1. one\n",
    )
    .unwrap();
    let refused = run(&root, &["approach", "owed", "375", "T05"]);
    assert_eq!(refused.code, 1);
    assert!(refused.stdout.contains("no `### T05 Approach`"));
    std::fs::write(
        dir.join("plan.md"),
        "## T05 x\n\n### T05 Approach\n\n1. **a** b\n",
    )
    .unwrap();
    assert_eq!(run(&root, &["approach", "owed", "375", "T05"]).stdout, "");
    assert_eq!(run(&root, &["approach", "ruled", "x"]).stdout, "");
    assert_eq!(
        run(&root, &["approach", "owe-in-flight", "x", "B"]).stdout,
        ""
    );
    assert_eq!(run(&root, &["approach", "nonsense"]).code, 2);
    let usage = std::fs::read_to_string(root.join(".git/tool-usage.jsonl")).unwrap();
    assert!(
        usage.contains("\"tool\": \"approach_gate\"") && usage.contains("\"outcome\": \"refused\"")
    );
}

#[test]
fn the_records_are_written_with_one_space_and_a_newline() {
    assert_eq!(
        super::pretty(&json!({"a": [1], "é": {}})),
        "{\n \"a\": [\n  1\n ],\n \"é\": {}\n}\n"
    );
    assert_eq!(super::today().len(), 10);
    assert_eq!(super::now_utc().len(), 20);
}

#[test]
fn a_tree_with_no_dev_directory_records_no_bypass_and_triage_is_named_when_owed() {
    let root = scratch("nodev");
    super::bypass_record(&root, "push", "a reason given");
    assert!(!root.join("dev").exists());
    assert!(super::hint_of("x\n3\n").contains("claims owed a triage: 3"));
    assert_eq!(super::hint_of("0\n"), "");
    assert_eq!(super::triage_hint(&root, &no_claims), "");
    assert!(super::triage_hint(&root, &|_| crate::Reply {
        stdout: "2\n".to_owned(),
        stderr: String::new(),
        code: 0
    })
    .contains("triage: 2"));
}

#[test]
fn the_verbs_report_what_is_owed_after_and_read_the_active_feature() {
    let root = repo();
    let dir = feature_at(
        &root,
        Some("# p\n\n### T05 Decisions\n\n**D1 - x.** first\n"),
        None,
        "375-x",
    );
    std::fs::create_dir_all(root.join("docs")).unwrap();
    std::fs::write(
        root.join("docs/approach-checklist.md"),
        "## A. x\n\n1. one\n\n## B. y\n\n1. two\n",
    )
    .unwrap();
    let key = "### T05 Decisions";
    let first = super::sections::block_digest("### T05 Decisions\n\n**D1 - x.** first\n");
    let src = write_json(
        &root,
        "a.json",
        &json!({"blocks": {key: first}, "decisions": []}),
    );
    assert_eq!(
        run(
            &root,
            &["record-blocks", "375", &src, "--as", "spec-fidelity"]
        )
        .code,
        0
    );
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "reviewed"]);
    let changed = "### T05 Decisions\n\n**D1 - x.** a wholly different rule stated here\n";
    std::fs::write(dir.join("plan.md"), format!("# p\n\n{changed}")).unwrap();
    let src = write_json(
        &root,
        "b.json",
        &json!({"blocks": {key: super::sections::block_digest(changed)}, "decisions": []}),
    );
    assert!(run(
        &root,
        &["record-blocks", "375", &src, "--as", "spec-fidelity"]
    )
    .stdout
    .contains("approach owed: re-decided:"));
    std::fs::write(&src, "not json").unwrap();
    assert_eq!(
        run(
            &root,
            &["record-blocks", "375", &src, "--as", "spec-fidelity"]
        )
        .code,
        1
    );
    std::fs::create_dir_all(root.join(".specify")).unwrap();
    std::fs::write(
        root.join(".specify/feature.json"),
        "{\"feature_directory\": \"specs/375-x\"}",
    )
    .unwrap();
    assert!(
        run(&root, &["door", "active-task", &root.display().to_string()])
            .stdout
            .contains("375-x")
    );
    assert!(run(&root, &["approach", "ruled", "hour:1"])
        .stdout
        .contains("approach owed: hour:1"));
    assert_eq!(
        super::cli(&["no-such-verb".to_owned()], &root, &no_claims).code,
        2
    );
}

#[test]
fn what_the_other_tools_ask_of_the_plan_answers_nothing_on_an_empty_tree() {
    let root = crate::checks::scratch("plan-asked");
    assert_eq!(super::owe_in_flight(&root, "t", "B"), None);
    assert_eq!(super::active_feature(&root), None);
    assert_eq!(super::resolve_feature("999", &root), None);
    assert_eq!(super::approach_ruled(&root, "t"), None);
    assert!(super::arbiter_accept_listed(&root, "t").is_empty());
}
