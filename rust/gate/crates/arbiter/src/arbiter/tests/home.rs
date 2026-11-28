//! RED FIRST (feature 451 T179): a trigger's feature, resolved once. Observed 2026-11-23: `round:spec-fidelity|plan:specs/449-rust-codebase#T377@3`
//! (the feature's path, where its directory name is the form) was ruled in 451's log, its accept clearing 18 of 451's blocks; and the
//! mirror's feature "" entry for a reversal ruled in the clone stayed owed, holding every check dispatch that read it for days.

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::super::home::{named, resolve};
use super::super::{record_batch, record_ruling};
use super::{clone_at, owe, own, python_tools, refused, rows, rule_file, run};

const PLAN: &str = "# p\n\n## Shared\n\nshared\n\n## T05 the bath\n\nbody\n";

fn tasks(d: &Path, lines: &str) {
    std::fs::write(d.join("tasks.md"), format!("# Tasks\n\n{lines}")).unwrap();
}

fn owed_at(common: &Path) -> Value {
    serde_json::from_str(&std::fs::read_to_string(common.join("arbiter-owed.json")).unwrap())
        .unwrap()
}

fn accept() -> Value {
    json!({"ruling": "accept", "why": "fine"})
}

#[test]
fn a_trigger_naming_its_feature_by_path_is_refused_and_nothing_is_written() {
    let root = clone_at("home-path");
    python_tools(&root);
    let d = root.join("specs/999-x");
    tasks(&d, "- [ ] T01 a\n");
    std::fs::write(d.join("plan.md"), PLAN).unwrap();
    for (trigger, said) in [
        (
            "round:spec-fidelity|plan:specs/999-x#T01@3",
            "names no feature",
        ),
        (
            "round:spec-fidelity|plan:999-x#T377@3",
            "names no task of 999-x",
        ),
        ("round:spec-fidelity|plan:999-x@3", "names no task of 999-x"),
        ("round:spec-fidelity|specs/999-x#1@6", "names no feature"),
    ] {
        refused(
            record_ruling(
                &own(&root),
                trigger,
                &accept(),
                "round-arbiter",
                None,
                false,
            ),
            said,
        );
        let file = rule_file(&root, "a.json", &accept());
        let r = run(&root, &["ruled", trigger, &file, "--as", "round-arbiter"]);
        assert_eq!(r.code, 1, "{trigger}: {}", r.stderr);
        assert!(r.stderr.contains("`round:spec-fidelity|"), "{}", r.stderr);
    }
    // a batch with one such member writes no row at all
    owe(
        &root,
        &json!({"round:a|q:1@3": {"kind": "round", "unit": "a|q:1", "feature": "999-x", "t": 1}}),
    );
    refused(
        record_batch(
            &own(&root),
            &json!({"ruling": "continue", "why": "w", "triggers": ["round:a|q:1@3", "round:spec-fidelity|plan:specs/999-x#T01@3"]}),
            "round-arbiter",
            None,
        ),
        "round:spec-fidelity|plan:specs/999-x#T01@3: round:spec-fidelity|plan:specs/999-x#T01@3 names no feature",
    );
    assert!(rows(&root).is_empty());
    assert!(!d.join("plan-review.json").exists());
}

#[test]
fn a_ruling_is_filed_in_the_feature_its_trigger_names_or_was_owed_in() {
    let root = clone_at("home-filed");
    python_tools(&root);
    let other = root.join("specs/449-y");
    std::fs::create_dir_all(&other).unwrap();
    tasks(&other, "- [ ] T05 the bath\n");
    std::fs::write(other.join("plan.md"), PLAN).unwrap();
    // a log's rows that are no ruling - a fix's settling, a line that is no JSON - are no trigger it has ruled
    std::fs::write(
        other.join("arbiter.jsonl"),
        "{\"fix_of\": \"ask:f\", \"status\": \"done\"}\nnot json\n",
    )
    .unwrap();
    assert!(super::super::home::ruled_in(&other).is_empty());
    // owed while 449 was active, ruled while 999 is: filed in 449's log, never the active feature's
    owe(
        &root,
        &json!({
            "round:quote-check|q:1@3": {"kind": "round", "unit": "quote-check|q:1", "feature": "449-y", "t": 1},
            "reversal:/f": {"kind": "reversal", "unit": "/f", "feature": "", "t": 1},
            "reversal:/g": {"kind": "reversal", "unit": "/g", "feature": "448-gone", "t": 1},
        }),
    );
    let w = json!({"ruling": "continue", "why": "w"});
    record_ruling(
        &own(&root),
        "round:quote-check|q:1@3",
        &w,
        "round-arbiter",
        None,
        false,
    )
    .unwrap();
    assert_eq!(super::super::home::ruled_in(&other).len(), 1);
    assert!(rows(&root).is_empty());
    // feature "" and a feature not here: the active one
    for t in ["reversal:/f", "reversal:/g"] {
        record_ruling(&own(&root), t, &w, "round-arbiter", None, false).unwrap();
    }
    assert_eq!(rows(&root).len(), 2);
    // a plan round naming 449's task: filed there, its accept applied to 449's plan, and said so
    let file = rule_file(&root, "a.json", &accept());
    let r = run(
        &root,
        &[
            "ruled",
            "round:spec-fidelity|plan:449-y#T05@3",
            &file,
            "--as",
            "round-arbiter",
        ],
    );
    assert_eq!(r.code, 0, "{}", r.stderr);
    assert!(
        r.stdout.contains("recorded in 449-y's arbiter.jsonl"),
        "{}",
        r.stdout
    );
    assert!(
        r.stdout
            .contains("of T05's section recorded CLEAR: ## T05 the bath"),
        "{}",
        r.stdout
    );
    assert!(!root.join("specs/999-x/plan-review.json").exists());
    refused(
        record_ruling(
            &own(&root),
            "round:spec-fidelity|plan:449-y#T05@3",
            &accept(),
            "round-arbiter",
            None,
            false,
        ),
        "already ruled",
    );
    // a batch's member owed in 449 is filed there too, and its plan accept applied there
    owe(
        &root,
        &json!({"ask:449-T05-again": {"kind": "ask", "unit": "", "feature": "449-y", "t": 1, "review": "plan"}}),
    );
    let batch = rule_file(
        &root,
        "b.json",
        &json!({"ruling": "accept", "why": "fine", "triggers": ["ask:449-T05-again"]}),
    );
    let r = run(&root, &["ruled-batch", &batch, "--as", "round-arbiter"]);
    assert_eq!(r.code, 0, "{}", r.stderr);
    assert!(
        r.stdout.contains("of T05's section recorded CLEAR"),
        "{}",
        r.stdout
    );
    assert!(super::super::home::ruled_in(&other).contains_key("ask:449-T05-again"));
    refused(
        record_batch(
            &own(&root),
            &json!({"ruling": "continue", "why": "w", "triggers": ["ask:449-T05-again"]}),
            "round-arbiter",
            None,
        ),
        "already ruled: ask:449-T05-again",
    );
}

/// A mirror at `<tmp>/m` and its clone at `<tmp>/m/.clones/c`, the clone's feature 999-x.
fn mirrored(tag: &str) -> (l7r_shared::tempdir::Held<PathBuf>, PathBuf) {
    let base = l7r_shared::tempdir::TempDir::new(&format!("gate-arbiter-{tag}"));
    let top = std::fs::canonicalize(&base).unwrap();
    let mirror = top.join("m");
    let clone = mirror.join(".clones/c");
    std::fs::create_dir_all(mirror.join(".git")).unwrap();
    std::fs::create_dir_all(clone.join("specs/999-x")).unwrap();
    assert!(std::process::Command::new("git")
        .arg("-C")
        .arg(&clone)
        .args(["init", "-q"])
        .status()
        .unwrap()
        .success());
    std::fs::create_dir_all(clone.join(".specify")).unwrap();
    std::fs::write(
        clone.join(".specify/feature.json"),
        r#"{"feature_directory": "specs/999-x"}"#,
    )
    .unwrap();
    (base.hold(mirror), clone)
}

#[test]
fn a_ruling_clears_its_trigger_from_the_mirror_s_owed_file_too() {
    let (mirror, clone) = mirrored("mirror-pop");
    let w = json!({"ruling": "continue", "why": "w"});
    // no owed file in the mirror: the clone's alone, and none written there
    owe(
        &clone,
        &json!({"ask:a": {"kind": "ask", "unit": "", "feature": "999-x", "t": 1}}),
    );
    record_ruling(&own(&clone), "ask:a", &w, "round-arbiter", None, false).unwrap();
    assert!(!mirror.join(".git/arbiter-owed.json").exists());
    std::fs::write(
        mirror.join(".git/arbiter-owed.json"),
        json!({
            "reversal:/f": {"kind": "reversal", "unit": "/f", "feature": "", "t": 1},
            "cascade@1": {"kind": "cascade", "unit": "", "feature": "777-other", "t": 1},
            "ask:b": {"kind": "ask", "unit": "", "feature": "999-x", "t": 1},
        })
        .to_string(),
    )
    .unwrap();
    owe(
        &clone,
        &json!({
            "reversal:/f": {"kind": "reversal", "unit": "/f", "feature": "999-x", "t": 1},
            "cascade@1": {"kind": "cascade", "unit": "", "feature": "999-x", "t": 1},
        }),
    );
    for t in ["reversal:/f", "cascade@1", "ask:b"] {
        record_ruling(&own(&clone), t, &w, "round-arbiter", None, false).unwrap();
    }
    let left = owed_at(&mirror.join(".git"));
    // the feature-less entry and this feature's are cleared; another feature's `cascade@1` is its own
    assert_eq!(
        left.as_object().unwrap().keys().collect::<Vec<_>>(),
        ["cascade@1"]
    );
    assert_eq!(owed_at(&clone.join(".git")), json!({}));
}

#[test]
fn an_ask_is_filed_under_its_feature_or_refused() {
    let root = clone_at("home-ask");
    tasks(&root.join("specs/999-x"), "- [ ] T01 a\n");
    for (args, said) in [
        (
            vec!["ask", "998-elsewhere", "why is this here"],
            "names feature 998, which 0 directories",
        ),
        (
            vec!["ask", "999-T377-q", "why is this here", "plan"],
            "names T377, no task of 999-x",
        ),
        (
            vec!["ask", "about-T377", "why is this here", "plan"],
            "names T377, no task of 999-x",
        ),
        (
            vec!["ask", "999-t377-q", "why is this here", "plan"],
            "names T377, no task of 999-x",
        ),
    ] {
        let r = run(&root, &args);
        assert_eq!(r.code, 2, "{args:?}: {}", r.stderr);
        assert!(r.stderr.contains(said), "{args:?}: {}", r.stderr);
        assert!(r.stderr.contains("`ask:<NNN>-<slug>`"), "{}", r.stderr);
    }
    assert!(!root.join(".git/arbiter-owed.json").exists());
    let r = run(&root, &["ask", "999-T01-q", "why is this here", "plan"]);
    assert_eq!(r.code, 0, "{}", r.stderr);
    assert_eq!(
        owed_at(&root.join(".git"))["ask:999-T01-q"]["feature"],
        "999-x"
    );
    // no feature resolves: refused at filing, never filed as feature ""
    let orphan = clone_at("home-ask-orphan");
    std::fs::remove_file(orphan.join(".specify/feature.json")).unwrap();
    let r = run(&orphan, &["ask", "foo", "why is this here"]);
    assert_eq!(r.code, 2, "{}", r.stderr);
    assert!(
        r.stderr.contains("no feature to file ask:foo under"),
        "{}",
        r.stderr
    );
    assert!(!orphan.join(".git/arbiter-owed.json").exists());
    let r = run(&orphan, &["ask", "foo-T01", "why is this here", "plan"]);
    assert!(
        r.stderr.contains("names T01, no task of no feature"),
        "{}",
        r.stderr
    );
    // an owed file that cannot be written: not filed, and said so
    std::fs::remove_file(root.join(".git/arbiter-owed.json")).unwrap();
    std::fs::create_dir(root.join(".git/arbiter-owed.json")).unwrap();
    let r = run(&root, &["ask", "999-T01-r", "why is this here"]);
    assert_eq!(r.code, 1, "{}", r.stderr);
    assert!(
        r.stderr.contains("ask:999-T01-r was not filed"),
        "{}",
        r.stderr
    );
}

#[test]
fn the_named_feature_reads_each_form() {
    let root = clone_at("home-named");
    let r = own(&root);
    assert_eq!(named(&r, "round:quote-check|q:1@3", "").unwrap(), None);
    assert_eq!(named(&r, "ask:foo", "").unwrap(), None);
    assert_eq!(named(&r, "ask:foo", "plan").unwrap(), None);
    assert_eq!(
        named(&r, "round:spec-fidelity|999-x#1@6", "").unwrap(),
        Some(root.join("specs/999-x"))
    );
    assert_eq!(
        named(&r, "ask:999-a", "").unwrap(),
        Some(root.join("specs/999-x"))
    );
    std::fs::create_dir_all(root.join("specs/999-y")).unwrap();
    assert!(named(&r, "ask:999-a", "")
        .unwrap_err()
        .contains("which 2 directories"));
    let orphan = clone_at("home-named-orphan");
    std::fs::remove_file(orphan.join(".specify/feature.json")).unwrap();
    assert!(resolve(&own(&orphan), "ask:x")
        .unwrap_err()
        .contains("no active feature"));
}

/// RED FIRST (461 T84): the ruling of red-gate@2026-11-28T03:47:58Z on 461 T74/T63's landing was filed in 462's `arbiter.jsonl` -
/// the clone's `.specify/feature.json` - and charged 462 T22, a waiting task, a part B. The tripwire's row now names the landing
/// (`home`, `tasks`, `tree`'s `state::second_red_gate`): the ruling is filed there, and its part B owed by the landing's tasks
/// still open, never the pointer's active task.
#[test]
fn a_red_gate_ruling_is_filed_under_the_landing_that_tripped_it() {
    let root = clone_at("home-red-gate");
    std::fs::create_dir_all(root.join("docs")).unwrap();
    std::fs::write(root.join("docs/approach-checklist.md"), "1. one\n").unwrap();
    let active = root.join("specs/999-x");
    tasks(&active, "- [ ] T22 waiting\n");
    std::fs::write(active.join("plan.md"), "# p\n\n### T22 w\n").unwrap();
    let landing = root.join("specs/461-x");
    std::fs::create_dir_all(&landing).unwrap();
    tasks(
        &landing,
        "- [x] T63 landed\n- [ ] T74 open\n- [ ] T81 other\n",
    );
    std::fs::write(landing.join("plan.md"), "# p\n\n### T74 a\n").unwrap();
    owe(
        &root,
        &json!({"red-gate@1": {"kind": "red-gate", "detail": "a second red make done in a row", "unit": "", "t": 1, "home": "461-x", "tasks": ["T74", "T63"]}}),
    );
    let file = rule_file(
        &root,
        "r.json",
        &json!({"ruling": "continue", "why": "w", "what": "again"}),
    );
    let r = run(
        &root,
        &["ruled", "red-gate@1", &file, "--as", "round-arbiter"],
    );
    assert_eq!(r.code, 0, "{}", r.stderr);
    assert!(r.stdout.contains("recorded in 461-x's arbiter.jsonl"));
    assert!(rows(&root).is_empty());
    let filed = std::fs::read_to_string(landing.join("arbiter.jsonl")).unwrap();
    assert!(
        filed.contains("\"trigger\": \"red-gate@1\"")
            && filed.contains("\"tasks\": [\"T74\", \"T63\"]")
    );
    let owed = std::fs::read_to_string(root.join(".git/approach-owed.json")).unwrap();
    assert!(owed.contains("\"feature\": \"461-x\"") && owed.contains("\"task\": \"T74\""));
    assert!(!owed.contains("T22") && !owed.contains("T63") && !owed.contains("T81"));
    assert!(r.stdout.contains("T74 owes the checklist's"));
    // a landing whose tasks have all landed owes no part B, and charges no other task
    owe(
        &root,
        &json!({"red-gate@2": {"kind": "red-gate", "unit": "", "t": 2, "home": "461-x", "tasks": ["T63"]}}),
    );
    std::fs::remove_file(root.join(".git/approach-owed.json")).unwrap();
    let r = run(
        &root,
        &["ruled", "red-gate@2", &file, "--as", "round-arbiter"],
    );
    assert_eq!(r.code, 0, "{}", r.stderr);
    assert!(!root.join(".git/approach-owed.json").exists());
    assert!(!r.stdout.contains("owes the checklist"), "{}", r.stdout);
}
