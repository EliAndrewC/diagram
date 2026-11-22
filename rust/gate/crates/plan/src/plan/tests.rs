//! The plan gate's command line, and what the other test modules share.

use std::path::{Path, PathBuf};
use std::process::Command;
use std::sync::OnceLock;

use l7r_shared::tempdir::Held;
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
/// The census's guard log, once a process, in the test build (`beside_binary`): nothing set for the whole process is dropped to remove a
/// `TempDir` (feature 449 T101).
pub(super) fn quiet_census() -> PathBuf {
    static DIR: OnceLock<PathBuf> = OnceLock::new();
    DIR.get_or_init(|| {
        let dir = l7r_shared::tempdir::beside_binary("gate-plan-census");
        std::env::set_var("GUARD_LOG_DIR", &dir);
        dir
    })
    .clone()
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

pub(super) fn feature(plan: Option<&str>, review: Option<&Value>) -> Held<PathBuf> {
    let root = scratch("plan");
    let dir = feature_at(&root, plan, review, "243-x");
    root.hold(dir)
}

pub(super) fn current(decisions: &[Value], verdict: &str, plan: &str) -> Value {
    json!({"plan_sha256": digest(plan.as_bytes()), "decisions": decisions, "verdict": verdict})
}

pub(super) fn git(root: &Path, args: &[&str]) -> String {
    let done = Command::new("git")
        .arg("-C")
        .arg(root)
        // no automatic maintenance, which each commit otherwise starts as a process of its own (feature 449 T167)
        .args([
            "-c",
            "user.name=t",
            "-c",
            "user.email=t@t",
            "-c",
            "maintenance.auto=false",
        ])
        .args(args)
        .output()
        .unwrap();
    assert!(done.status.success(), "git {args:?}");
    String::from_utf8_lossy(&done.stdout).trim().to_owned()
}

pub(super) fn repo() -> l7r_shared::tempdir::TempDir {
    let root = scratch("plan-repo");
    git(&root, &["init", "-q", "-b", "main"]);
    root
}

pub(super) fn run(root: &Path, words: &[&str]) -> crate::Reply {
    run_with(root, words, "")
}

/// `run` with `DEFER_FORM_OK` set to `why` in the environment the command reads (no process variable is set: feature 451 T32).
pub(super) fn run_deferred(root: &Path, words: &[&str], why: &str) -> crate::Reply {
    quiet_census();
    let owned: Vec<String> = words.iter().map(|s| (*s).to_owned()).collect();
    let why = why.to_owned();
    answer(
        &owned,
        root,
        &root.join("bundles"),
        "bash",
        &mut "".as_bytes(),
        &no_claims,
        &move |k| (k == "DEFER_FORM_OK").then(|| why.clone()),
    )
}

/// The claims tools, as a plan test sees them: nothing owed a triage.
fn no_claims(_: &[String]) -> crate::Reply {
    crate::Reply {
        stdout: String::new(),
        stderr: String::new(),
        code: 0,
    }
}

fn run_with(root: &Path, words: &[&str], stdin: &str) -> crate::Reply {
    quiet_census();
    let owned: Vec<String> = words.iter().map(|s| (*s).to_owned()).collect();
    answer(
        &owned,
        root,
        &root.join("bundles"),
        "bash",
        &mut stdin.as_bytes(),
        &no_claims,
        &|_| None,
    )
}

pub(super) fn write_json(dir: &Path, name: &str, value: &Value) -> String {
    let path = dir.join(name);
    std::fs::write(&path, value.to_string()).unwrap();
    path.display().to_string()
}

mod bundle;

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
    assert!(linted.stderr.contains("decide: refused - 1 finding - "));
    assert!(linted.stderr.contains("(1) the section quotes the GM"));
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
        .contains("(1) T05 has no `### T05 Approach` block"));
}

/// Feature 451 T25: a section with findings of three kinds is refused once with all three, each with its plan.md line and its fix - one
/// run, where the lint stopped at its first finding and a section of four took four runs (2026-11-20).
#[test]
fn decide_reports_every_finding_of_the_section_in_one_run() {
    let root = repo();
    let plan = "# plan\n\n## T05 x\n\n- **Approach**: the check takes 48 s on a landing.\n\nAs the GM put it, \"not in the request at all\".\n\n### T05 Approach (checklist part A)\n\n4. **World.** The ratio is 7.\n6. **The exits.** Red: ruled through `make arbiter-ask`.\n";
    feature_at(&root, Some(plan), None, "375-x");
    let got = run(&root, &["decide", "375", "T05"]);
    assert_eq!(got.code, 2);
    let told = &got.stderr;
    assert_eq!(told.matches("decide: refused").count(), 1, "{told}");
    assert!(told.contains("3 findings"), "{told}");
    for (line, words, fix) in [
        (5, "takes 48 s", "a figure with a unit"),
        (
            7,
            "not in the request at all",
            "add the GM's words to request.md",
        ),
        (11, "The ratio is 7", "Approach item 4"),
    ] {
        let at = format!("plan.md:{line}");
        let all = [at.as_str(), words, fix].iter().all(|w| told.contains(w));
        assert!(all, "{told}");
    }
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
    let said = run(&root, &["archive", "375"]).stdout;
    assert!(said.contains("1 task section(s) moved to 375-x/plan-done.md: T05"));
    // ...and the ticked task itself, to tasks-done.md (feature 449 T142); a second run moves none
    assert!(said.contains("1 ticked task(s) moved to 375-x/tasks-done.md: T05"));
    assert!(run(&root, &["archive", "375"])
        .stdout
        .contains("0 ticked task(s) moved to 375-x/tasks-done.md: none ticked"));
    // an archive that cannot be written is the verb's failure
    std::fs::write(dir.join("tasks.md"), "- [x] T07 x\n").unwrap();
    std::fs::remove_file(dir.join("tasks-done.md")).unwrap();
    std::fs::create_dir(dir.join("tasks-done.md")).unwrap();
    assert_eq!(run(&root, &["archive", "375"]).code, 1);
    std::fs::remove_dir(dir.join("tasks-done.md")).unwrap();
    std::fs::write(dir.join("tasks.md"), "- [ ] T06 the wells\n").unwrap();
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
    let spec = dir.display().to_string();
    let ask = |escaped: Option<&str>| super::tick_gate(&dir, &root, escaped, "T01");
    let (ok, refused) = ask(None);
    assert!(
        !ok && refused.contains("no current CLEAR review") && refused.contains("make plan-verdict")
    );
    assert!(ask(Some("x")).1.contains("needs a REASON"));
    let (ok, passed) = ask(Some("a superseded plan nobody implements"));
    assert!(ok && passed.contains("BYPASSED"));
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
    assert_eq!(ask(None), (true, String::new()));
}

#[test]
fn the_door_keeps_only_the_push_s_bypass_record_and_the_tick_s_asks_are_public() {
    // feature 449 T131: `plan_door.py` left with its last callers; `plan-gate.sh`'s bypass record and the review-round guard's active
    // task are the door's two verbs, and what the
    // tick asked through the door it asks in process
    let root = repo();
    let dir = feature_at(&root, Some(PLAN_TASKS), None, "375-x");
    let top = root.display().to_string();
    std::fs::create_dir_all(root.join("dev")).unwrap();
    assert_eq!(
        run(
            &root,
            &["door", "bypass-record", &top, "push", "a reason given"]
        )
        .code,
        0
    );
    assert_eq!(run(&root, &["door", "task-sections"]).code, 2);
    // the review-round guard's question
    assert_eq!(
        run(&root, &["door", "active-task", &top]).stdout,
        "[null,\"\"]\n"
    );
    assert_eq!(super::approach_refusal(&dir, &root, "T05"), None);
    assert_eq!(super::archive_finished(&dir), Vec::<String>::new());
    assert!(!super::section_wording_only("x"));
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
    assert!(super::active_feature(&root).is_some_and(|d| d.ends_with("375-x")));
    // the review-round guard's door question names it too
    let top = root.display().to_string();
    assert!(run(&root, &["door", "active-task", &top])
        .stdout
        .contains("375-x"));
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
    assert!(super::arbiter_accept_listed(&root, "t").blocks.is_empty());
}

/// RED FIRST (feature 451 T84): A TICK ANSWERS FOR ITS OWN TASK, THE TASKS TICKED BEFORE IT AND THE BLOCKS OUTSIDE EVERY TASK'S SECTION -
/// never for an open task's section nobody's tick has reached. Measured 2026-11-21 (each of feature 451's 16 landings of 2026-11-20/21
/// replayed on its tick's tree, `plan owed` with and without the other tasks' blocks): 14 of 16 were refused on the whole feature, and 6
/// of those 14 on other open tasks' sections or a filled template's old heading alone, so each landing took `PLAN_REVIEW_OK`.
#[test]
fn a_tick_answers_for_its_own_section_the_ticked_ones_and_the_shared_blocks() {
    let root = repo();
    let template = PLAN_TASKS.replace(
        "## T05 the bath (amendment 1)",
        "## T05 (<why: the finding>)",
    );
    let dir = feature_at(&root, Some(&template), None, "375-x");
    std::fs::create_dir_all(root.join("dev")).unwrap();
    let boxes = "# Tasks\n\n- [ ] T05 the bath\n- [ ] T06 the wells\n";
    std::fs::write(dir.join("tasks.md"), boxes).unwrap();
    let src = write_json(&root, "w.json", &current(&[], "CLEAR", &template));
    assert_eq!(
        run(&root, &["record", "375", &src, "--as", "spec-fidelity"]).code,
        0
    );
    // T05's builder fills its template - heading and body - and its section is reviewed; T06's is edited, nobody's tick yet
    let plan = PLAN_TASKS
        .replace(
            "- the bath 10 x 8 ft (GUESS)",
            "- the bath 10 x 8 ft (GUESS), measured from the plan",
        )
        .replace(
            "- a well by the kitchen\n",
            "- a well by the kitchen, its depth to be measured\n",
        );
    std::fs::write(dir.join("plan.md"), &plan).unwrap();
    let sha = run(&root, &["section-sha", "375", "T05"])
        .stdout
        .trim()
        .to_owned();
    let v = write_json(
        &root,
        "t.json",
        &json!({"section_sha256": sha, "decisions": []}),
    );
    assert_eq!(
        run(
            &root,
            &["record-task", "375", "T05", &v, "--as", "spec-fidelity"]
        )
        .code,
        0
    );
    let ask = |t: &str| super::tick_gate(&dir, &root, None, t);
    // neither an open task's section nor T05's own old heading holds T05's tick
    assert_eq!(ask("T05"), (true, String::new()));
    // the builder-stop guard's question: T05 may stop, T06 not; a feature or task with no section, or an unread root, passes
    let top = root.display().to_string();
    assert_eq!(
        run(&root, &["decided", &top, "375", "T05"]),
        crate::Reply {
            stdout: String::new(),
            stderr: String::new(),
            code: 0
        }
    );
    let held = run(&root, &["decided", &top, "375", "T06"]);
    assert_eq!(held.code, 1);
    assert!(held.stdout.contains("375-x T06: its plan section carries no current CLEAR verdict - run `make decide F=375 T=T06`"), "{}", held.stdout);
    for (f, t) in [("999", "T05"), ("375", "T09")] {
        assert_eq!(run(&root, &["decided", &top, f, t]).code, 0);
    }
    // a deferral that names no filed task holds the stop, whatever the verdict
    let deferred = format!("{plan}\n**Found and left?**\n- a leak in the drain, which floods the bath. Not fixed here: it needs a new pipe.\n");
    std::fs::write(dir.join("plan.md"), &deferred).unwrap();
    let held = run(&root, &["decided", &top, "375", "T06"]);
    assert!(held.stdout.contains("; and a found-and-left deferral names no filed open task - file it (`make task-add F=375"), "{}", held.stdout);
    std::fs::write(dir.join("plan.md"), &plan).unwrap();
    // T06's own tick still owes its review
    let (ok, why) = ask("T06");
    assert!(!ok && why.contains("T06 the wells"), "{why}");
    // T06 ticked: its section answers to every later tick, as the push's
    std::fs::write(
        dir.join("tasks.md"),
        boxes.replace("- [ ] T06", "- [x] T06"),
    )
    .unwrap();
    // a ticked task's stale section holds every later tick
    assert!(!ask("T05").0);
    std::fs::write(dir.join("tasks.md"), boxes).unwrap();
    // a block outside every task's section, changed: every tick refused
    std::fs::write(
        dir.join("plan.md"),
        plan.replace(
            "Each tub by a door.",
            "Each tub by a door, and a drain beside it.",
        ),
    )
    .unwrap();
    let (ok, why) = ask("T05");
    assert!(!ok && why.contains("preamble"), "{why}");
}
