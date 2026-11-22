//! A bundle's one plan section (451 T141): `make decide T=a,b,c` reads it and prints one MODE 4 dispatch judging every task in it, its
//! one verdict is recorded under each task, and the tick, `plan decided` and the builder-stop guard read it as each task's.

use serde_json::{json, Value};

use super::super::tick_gate;
use super::{feature_at, repo, run, write_json};

const BUNDLE: &str = "# plan\n\n**D1 - a decision.** Each tub by a door.\n\n### T05, T06, T07 (bundle)\n\n- **Approach**: three small fixes, one pass.\n\n### T05, T06, T07 Approach (checklist part A)\n\n1. **The goal.** T05: the bath; T06: the well; T07: the gate.\n\n### T08 the next\n\n- a lane\n";
const BOXES: &str =
    "# Tasks\n\n- [ ] T05 the bath\n- [ ] T06 the well\n- [ ] T07 the gate\n- [ ] T08 the lane\n";

fn bundle_feature(plan: &str) -> (l7r_shared::tempdir::TempDir, std::path::PathBuf) {
    let root = repo();
    let dir = feature_at(&root, Some(plan), None, "375-x");
    std::fs::write(dir.join("tasks.md"), BOXES).unwrap();
    std::fs::create_dir_all(root.join("dev")).unwrap();
    (root, dir)
}

#[test]
fn decide_on_a_bundle_prints_one_dispatch_judging_every_task() {
    let (root, _dir) = bundle_feature(BUNDLE);
    let decided = run(&root, &["decide", "375", "T05,T06,T07"]);
    assert_eq!(decided.code, 0, "{}", decided.stderr);
    let prompts = decided.stdout.matches("MODE 4: PLAN REVIEW").count();
    assert_eq!(prompts, 1, "{}", decided.stdout);
    assert!(
        decided
            .stdout
            .contains("BUNDLE (451 T141): this one section is the plan of T05, T06, T07"),
        "{}",
        decided.stdout
    );
    assert!(
        decided.stdout.contains("judge every task in it"),
        "{}",
        decided.stdout
    );
    let spaced = run(&root, &["decide", "375", "T05 T06 T07"]);
    assert_eq!(spaced.code, 0, "{}", spaced.stderr);
    let sha_lead = run(&root, &["section-sha", "375", "T05"]).stdout;
    let sha_bundle = run(&root, &["section-sha", "375", "T05,T06,T07"]).stdout;
    assert_eq!(sha_lead, sha_bundle);
}

#[test]
fn decide_refuses_a_bundle_whose_members_do_not_share_its_section() {
    let apart = BUNDLE.replace(
        "### T08 the next",
        "### T06 (<why: the finding>)\n\n- the template\n\n### T08 the next",
    );
    let (root, _dir) = bundle_feature(&apart);
    let refused = run(&root, &["decide", "375", "T05,T06,T07"]);
    assert_eq!(refused.code, 2);
    assert!(
        refused.stderr.contains("T06's section is not the bundle's"),
        "{}",
        refused.stderr
    );
    assert!(
        refused.stderr.contains("delete T06's own headings"),
        "{}",
        refused.stderr
    );
    let (root, _dir) = bundle_feature(BUNDLE);
    let short = run(&root, &["decide", "375", "T05,T06"]);
    assert_eq!(short.code, 2);
    assert!(
        short
            .stderr
            .contains("the bundle's heading lists T05, T06, T07: make decide F=375 T=T05,T06,T07"),
        "{}",
        short.stderr
    );
    let none = run(&root, &["decide", "375", "T08,T09"]);
    assert_eq!(none.code, 2);
    assert!(
        none.stderr.contains("no plan section names T09"),
        "{}",
        none.stderr
    );
}

#[test]
fn a_bundle_s_one_verdict_is_each_task_s() {
    // the plan reviewed at its stage while each task held its own template; the builder then made them one bundle section
    let templates = "# plan\n\n**D1 - a decision.** Each tub by a door.\n\n### T05 (<why>)\n\n- a\n\n### T06 (<why>)\n\n- b\n\n### T07 (<why>)\n\n- c\n\n### T08 the next\n\n- a lane\n";
    let (root, dir) = bundle_feature(templates);
    let whole = json!({"plan_sha256": super::super::sections::digest(templates.as_bytes()), "decisions": [], "verdict": "CLEAR"});
    let staged = write_json(&root, "p.json", &whole);
    let at_stage = run(&root, &["record", "375", &staged, "--as", "spec-fidelity"]);
    assert_eq!(at_stage.code, 0, "{}", at_stage.stderr);
    std::fs::write(dir.join("plan.md"), BUNDLE).unwrap();
    let tree = root.display().to_string();
    let (open, _) = tick_gate(&dir, &root, None, "T07");
    assert!(!open, "the bundle's blocks are owed before its review");
    let before = run(&root, &["decided", &tree, "375-x", "T06"]);
    assert_eq!(before.code, 1, "{}", before.stdout);
    let sha = run(&root, &["section-sha", "375", "T05,T06,T07"])
        .stdout
        .trim()
        .to_owned();
    let src = write_json(
        &root,
        "v.json",
        &json!({"section_sha256": sha, "decisions": []}),
    );
    let recorded = run(
        &root,
        &["record-task", "375", "T05", &src, "--as", "spec-fidelity"],
    );
    assert_eq!(recorded.code, 0, "{}", recorded.stderr);
    let review: Value =
        serde_json::from_str(&std::fs::read_to_string(dir.join("plan-review.json")).unwrap())
            .unwrap();
    for t in ["T05", "T06", "T07"] {
        let verdict = review["tasks"][t]["verdict"]
            .as_str()
            .unwrap_or_default()
            .to_owned();
        assert_eq!(verdict, "CLEAR", "{t}");
        let at = review["tasks"][t]["section_sha256"]
            .as_str()
            .unwrap_or_default()
            .to_owned();
        assert_eq!(at, sha, "{t}");
        let stop = run(&root, &["decided", &tree, "375-x", t]);
        assert_eq!(stop.code, 0, "{t}: {}", stop.stdout);
        let (ticks, why) = tick_gate(&dir, &root, None, t);
        assert!(ticks, "{t}: {why}");
    }
    assert!(review["tasks"].get("T08").is_none());
    // the mark's task, the bundle's first: the checks' wait reads its verdict
    std::fs::create_dir_all(root.join(".specify")).unwrap();
    std::fs::write(
        root.join(".specify/feature.json"),
        "{\"feature_directory\": \"specs/375-x\"}",
    )
    .unwrap();
    std::fs::write(
        root.join(".git/active-task"),
        "{\"feature\": \"375-x\", \"task\": \"T05\", \"tasks\": [\"T05\", \"T06\", \"T07\"]}\n",
    )
    .unwrap();
    let waits = run(&root, &["decided", &tree]);
    assert_eq!(waits.code, 0, "{}", waits.stdout);
}

#[test]
fn a_bundle_s_approach_block_answers_for_each_task() {
    let (root, dir) = bundle_feature(BUNDLE);
    std::fs::create_dir_all(root.join("docs")).unwrap();
    std::fs::write(
        root.join("docs/approach-checklist.md"),
        "# Checklist\n\n## A. At task start\n\n1. **The goal.** x\n",
    )
    .unwrap();
    for t in ["T05", "T06", "T07"] {
        let why = super::super::approach::refusal(&dir, &root, t);
        assert_eq!(why, None, "{t}");
    }
    let missing = super::super::approach::refusal(&dir, &root, "T08").unwrap_or_default();
    assert!(missing.contains("no `### T08 Approach` block"), "{missing}");
}
