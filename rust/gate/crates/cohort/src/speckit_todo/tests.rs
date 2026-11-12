//! `l7r-gate speckit-todo` over scratch trees: every flag, the report's groupings, the clones beside a tree, the check's two refusals and
//! the work budget's view (feature 449 T118); `scratchpad/t83s2/` compares it with the Python it replaced, byte for byte.

use std::path::{Path, PathBuf};
use std::time::{Duration, SystemTime};

use l7r_gate_core::ci::fixtures::{commit, git, put, repo, scratch};
use serde_json::json;

use super::work_budget_view::lines;
use super::{cli, truthy};

const VOCAB: &str = r#"{"tags": {"hamlet": {"stage": "now"}, "village": {"stage": "village"}, "town": {"stage": "town"}, "tooling": {"stage": "now"}}, "aliases": {"every tier": ["hamlet", "village", "town"]}, "placeholders": {"village": "380-village"}}"#;

fn run(cwd: &Path, args: &[&str]) -> super::Reply {
    cli(
        &args.iter().map(|a| (*a).to_owned()).collect::<Vec<_>>(),
        cwd,
    )
}

/// A tree of features in each state, with its vocabulary.
fn tree(root: &Path) {
    put(root, ".specify/affects.json", VOCAB);
    put(
        root,
        "specs/1-filed/spec.md",
        "# Feature 1: Filed\n**Affects**: hamlet\n",
    );
    put(
        root,
        "specs/2-planned/spec.md",
        "# Planned\n**Affects**: every tier\n",
    );
    put(root, "specs/2-planned/tasks.md", "- [ ] T1 a\n");
    put(
        root,
        "specs/3-going/spec.md",
        "# Going\n**Affects**: town\n",
    );
    put(
        root,
        "specs/3-going/tasks.md",
        "- [x] T1 a\n- [ ] T2 b\n- [ ] T3 c\n",
    );
    put(
        root,
        "specs/380-village/spec.md",
        "# Village\n**Affects**: village\n",
    );
    put(
        root,
        "specs/4-done/spec.md",
        "# Done\n**Status**: Done (2026-10-10)\n",
    );
    put(root, "specs/5-ticked/tasks.md", "- [x] T1 a\n");
    put(
        root,
        "specs/6-review/spec.md",
        "# Review\n**Affects**: tooling\n",
    );
    put(
        root,
        "specs/6-review/tasks.md",
        "- [x] T1 a\n- [ ] GM review\n",
    );
    put(root, "specs/6-review/gm-review.jsonl", "{\"row\": 1}\n");
}

#[test]
fn the_report_groups_the_open_by_stage_and_lists_the_closed() {
    let dir = repo("todo-report");
    tree(&dir);
    let r = run(&dir, &["--root", &dir.to_string_lossy(), "--all"]);
    assert_eq!(r.code, 0, "{}", r.stderr);
    assert!(r.stdout.starts_with("FILED (2)\n  owed at now (1)\n    1-filed  Filed  [hamlet]\n  owed at village (1)\n    380-village  Village  [village]\n\nPLANNED (1)\n  owed at now (1)\n    2-planned  Planned  0/1  [hamlet, village, town]\n"));
    assert!(r
        .stdout
        .contains("  owed at town (1)\n    3-going  Going  1/3  [town]\n"));
    assert!(r.stdout.contains(
        "DONE - GM REVIEW PENDING (1)\n  owed at now (1)\n    6-review  Review  1/2  [tooling]\n"
    ));
    assert!(r.stdout.contains("CLOSED (2)\n  4-done  Done  Done (2026-10-10)\n  5-ticked  ticked  (no spec.md)  every task ticked\n"));
    assert!(r
        .stdout
        .ends_with("open: 2 filed, 1 planned, 1 in progress; closed: 2\n"));
    let log = std::fs::read_to_string(dir.join(".git/tool-usage.jsonl")).unwrap();
    assert!(
        log.contains("\"tool\": \"speckit-todo\", \"kind\": \"check\", \"outcome\": \"passed\"")
    );
    let by = run(&dir, &["--root", &dir.to_string_lossy(), "--by-affects"]);
    assert!(by
        .stdout
        .contains("PLANNED (1)\n  affects hamlet (1)\n    2-planned"));
    assert!(by.stdout.contains("  affects village (1)\n    380-village"));
    let bare = scratch("todo-bare");
    put(&bare, "specs/9-x/tasks.md", "- [ ] T1\n");
    let by = run(&bare, &["--root", &bare.to_string_lossy(), "--by-affects"]);
    assert!(by
        .stdout
        .contains("  affects NOTHING NAMED (make speckit-todo CHECK=1 says how to set it) (1)\n"));
}

#[test]
fn a_tag_filter_keeps_the_features_carrying_it_and_refuses_an_unknown_tag() {
    let dir = repo("todo-affects");
    tree(&dir);
    let root = dir.to_string_lossy().into_owned();
    let r = run(&dir, &["--root", &root, "--affects", "Town"]);
    assert!(r.stdout.starts_with("affects town\n\nFILED (0)\n"));
    assert!(r
        .stdout
        .ends_with("open: 0 filed, 1 planned, 1 in progress; closed: 0 (affects town)\n"));
    let bad = run(&dir, &["--root", &root, "--affects", "town, castles"]);
    assert_eq!(bad.code, 2);
    assert_eq!(
        bad.stderr,
        "speckit-todo: AFFECTS names no tag it knows: castles\nTags: hamlet, village, town, tooling, every tier.\n"
    );
    let none = run(&dir, &["--root", &root, "--affects", " , "]);
    assert!(none.stderr.contains("knows:  , \n"));
    let log = std::fs::read_to_string(dir.join(".git/tool-usage.jsonl")).unwrap();
    assert!(log.contains("\"outcome\": \"refused\""));
}

#[test]
fn the_check_names_the_missing_tags_and_the_features_outside_their_placeholder() {
    let dir = repo("todo-check");
    let root = dir.to_string_lossy().into_owned();
    assert_eq!(run(&dir, &["--root", &root, "--check"]).code, 0);
    put(&dir, "specs/7-x/tasks.md", "- [ ] T1\n");
    // no vocabulary: nothing to check
    assert_eq!(run(&dir, &["--root", &root, "--check"]).code, 0);
    tree(&dir);
    put(&dir, "specs/8-y/spec.md", "# Y\n**Affects**: castles\n");
    put(&dir, "specs/9-z/spec.md", "# Z\n**Affects**: town\n");
    put(
        &dir,
        "specs/10-w/spec.md",
        "# W\n**Owed at**: village\n**Affects**: hamlet\n",
    );
    put(&dir, "specs/11-v/spec.md", "# V\n");
    let r = run(&dir, &["--root", &root, "--check"]);
    assert_eq!(r.code, 1);
    assert!(r.stderr.starts_with("speckit-todo: 3 open feature(s) do not say what they affect:\n  specs/11-v/spec.md  (no **Affects** line)\n  specs/7-x/spec.md  (no spec.md - write one first)\n  specs/8-y/spec.md  (unknown: castles)\nAdd this line"));
    assert!(r
        .stderr
        .contains("Tags: hamlet, village, town, tooling, every tier.\nA new tag"));
    assert!(r.stderr.contains("speckit-todo: 3 feature(s) owed at a tier not yet scripted sit outside that tier's placeholder:\n  specs/10-w/  (owed at village): carry its text into specs/380-village/spec.md under '## Carried items' and close it '**Status**: Superseded by 380 (<date>): carried word for word ...'\n"));
    assert!(r.stderr.contains("  specs/3-going/  (owed at town, which has no placeholder yet): make it the town tier's placeholder - add \"town\": \"3-going\" under \"placeholders\" in .specify/affects.json\n"));
    assert!(r
        .stderr
        .ends_with("scripted kind too - hamlet, magistracy - if it is owed now.)\n"));
    put(
        &dir,
        ".specify/affects.json",
        &VOCAB.replace("\"380-village\"", "5"),
    );
    assert!(run(&dir, &["--root", &root, "--check"])
        .stderr
        .contains("AttributeError"));
}

#[test]
fn the_single_answers_come_first_in_mains_order() {
    let dir = repo("todo-single");
    tree(&dir);
    let d = dir.join("specs/3-going");
    let at = d.to_string_lossy().into_owned();
    put(
        &dir,
        ".git/active-task",
        r#"{"feature": "3-going", "task": "T2"}"#,
    );
    let held = run(&dir, &["--holding", &at, "--check", "--state", &at]);
    assert_eq!(
        held.stdout,
        "T2 b  <- the active task (make task-start), open: land it with make land F=3 T=T2\n"
    );
    assert_eq!(run(&dir, &["--closed-by-status", &at]).stdout, "no\n");
    let done = dir.join("specs/4-done").to_string_lossy().into_owned();
    assert_eq!(
        run(&dir, &["--closed-by-status", &done, "--state", &at]).stdout,
        "yes\n"
    );
    assert_eq!(run(&dir, &["--state", &at]).stdout, "in progress\n");
    assert_eq!(
        run(&dir, &["--holding", "", "--state", &done]).stdout,
        "closed\n"
    );
    let each = run(
        &dir,
        &[
            "--each-state",
            &at,
            &done,
            "/no/such",
            &format!("{at}/../4-done/"),
        ],
    );
    assert_eq!(each.stdout, "in progress\nclosed\nfiled\nclosed\n");
    let lines = std::fs::read_to_string(dir.join(".git/tool-usage.jsonl"))
        .unwrap()
        .lines()
        .count();
    assert_eq!(lines, 5, "--each-state records no run");
    std::fs::remove_file(d.join("tasks.md")).unwrap();
    std::os::unix::fs::symlink("/proc/self/mem", d.join("tasks.md")).unwrap();
    let unreadable = run(&dir, &["--each-state", &done, &at]);
    assert_eq!(unreadable.code, 1);
    assert!(unreadable.stdout.starts_with("closed\nerror: "));
    assert!(unreadable.stderr.contains("3-going: "));
    let broken = run(&dir, &["--state", &at]);
    assert_eq!(broken.code, 1);
    assert!(broken
        .stderr
        .starts_with("Traceback (most recent call last):\n"));
    let root = dir.to_string_lossy().into_owned();
    let given = run(&dir, &["--root", &root, "--each-state", &done]);
    assert_eq!((given.code, given.stdout.as_str()), (0, "closed\n"));
    // a broken vocabulary fails each form that read it (feature 449 T118 D7): `--state`, `--each-state` above the directory, and
    // `--each-state --root` before any line
    put(&dir, ".specify/affects.json", "not json");
    assert!(run(&dir, &["--state", &done])
        .stderr
        .starts_with("Traceback"));
    let each = run(&dir, &["--each-state", &done]);
    assert_eq!(
        (each.code, each.stdout.as_str()),
        (
            1,
            "error: json.decoder.JSONDecodeError: expected ident at line 1 column 2\n"
        )
    );
    let given = run(&dir, &["--root", &root, "--each-state", &done]);
    assert_eq!((given.code, given.stdout.as_str()), (1, ""));
    assert!(given.stderr.starts_with("Traceback"));
    assert_eq!(run(&dir, &["--root", &root, "--affects", "town"]).code, 1);
    assert_eq!(run(&dir, &["--nonsense"]).code, 2);
}

/// A clone beside the tree, `origin/main` at its first commit, its session's event log written `hours` ago.
fn clone(dir: &Path, name: &str, hours: u64) -> PathBuf {
    let c = dir.join(".clones").join(name);
    std::fs::create_dir_all(&c).unwrap();
    git(&c, &["init", "-q", "-b", "main"]);
    git(&c, &["config", "user.email", "t@t"]);
    git(&c, &["config", "user.name", "t"]);
    tree(&c);
    put(&c, "specs/4-done/tasks.md", "- [x] T1\n");
    commit(&c, "x", "x\n");
    git(&c, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
    put(&c, ".git/l7r-events/f.jsonl", "{}\n");
    let when = SystemTime::now() - Duration::from_secs(hours * 3600);
    std::fs::File::options()
        .write(true)
        .open(c.join(".git/l7r-events/f.jsonl"))
        .unwrap()
        .set_modified(when)
        .unwrap();
    c
}

#[test]
fn a_clone_holding_a_feature_differently_is_shown_as_it_holds_it() {
    let dir = scratch("todo-clones");
    let root = clone(&dir, "main", 100);
    let b = clone(&dir, "b", 1);
    put(
        &b,
        "specs/3-going/tasks.md",
        "- [x] T1\n- [x] T2\n- [x] T3\n",
    );
    put(
        &b,
        "specs/4-done/spec.md",
        "# Done\n**Status**: Implemented\n",
    );
    put(&b, "specs/4-done/tasks.md", "- [x] T1\n- [ ] T2 reopened\n");
    put(&b, "specs/5-ticked/tasks.md", "- [x] T1\n- [x] T2\n");
    let c = clone(&dir, "c", 2);
    put(
        &c,
        "specs/3-going/tasks.md",
        "- [x] T1\n- [x] T2\n- [ ] T3\n",
    );
    put(&c, "specs/1-filed/spec.md", "# moved\n");
    std::fs::remove_dir_all(c.join("specs/1-filed")).unwrap();
    let stale = clone(&dir, "stale", 30);
    put(
        &stale,
        "specs/3-going/tasks.md",
        "- [x] T1\n- [x] T2\n- [x] T3\n",
    );
    std::fs::create_dir_all(dir.join(".clones/no-git")).unwrap();
    put(&dir, ".clones/not-a-repo/.git/l7r-events/f.jsonl", "{}\n");
    let r = run(&root, &["--root", &root.to_string_lossy(), "--all"]);
    assert!(r.stdout.contains("    3-going  Going  3/3  [town]  [in b (done there), not landed]\n    3-going  Going  2/3  [town]  [in c, not landed]\n"), "{}", r.stdout);
    assert!(r
        .stdout
        .contains("    4-done  Done  1/2  [in b, not landed]\n"));
    assert!(!r.stdout.contains("in stale"));
    assert!(r.stdout.contains("CLOSED (1)\n  5-ticked"));
    let away = scratch("todo-away");
    let gone = away.join("nowhere");
    assert!(run(&away, &["--root", &gone.to_string_lossy()])
        .stdout
        .ends_with("closed: 0\n"));
}

#[test]
fn feature_444s_row_carries_the_work_budgets_view() {
    let dir = repo("todo-444");
    put(&dir, "specs/444-hamlet/tasks.md", "- [ ] T1\n");
    let root = dir.to_string_lossy().into_owned();
    let r = run(&dir, &["--root", &root]);
    assert!(r.stdout.contains(
        "    444-hamlet  hamlet  0/1  (no spec.md)\n      work budget: no standing record yet"
    ));
    put(&dir, "dev/work-budget.md", "| stage |\n| a | b | c |\r\n");
    assert!(run(&dir, &["--root", &root])
        .stdout
        .contains("0/1  (no spec.md)\n        c (1): a (b)\n        moved since"));
    put(&dir, "dev/work-budget.md", "| x |\n");
    assert_eq!(run(&dir, &["--root", &root]).code, 1);
}

#[test]
fn the_view_summarizes_the_record_and_what_moved() {
    let dir = scratch("todo-view");
    assert_eq!(lines(&dir).unwrap().len(), 1);
    put(
        &dir,
        "dev/work-budget.md",
        "# Work budget\n\n| stage | ops @40 | exponent | budget @40 | ops @40 | status |\n|---|---|---|---|---|---|\n| **the whole roll** | 1 | 1.1 | 9 | 2,000 | WITHIN |\n| streets | - | - | - | 5 | WITHIN |\n| walls | - | - | - | - | OVER |\n| wells | 1 | 1 | 1 | 3 | WITHIN |\n",
    );
    assert_eq!(
        lines(&dir).unwrap(),
        [
            "work budget (dev/work-budget.md): the whole roll 2,000 counted operations @40, exponent 1.1, budget 9, WITHIN",
            "  WITHIN (2): streets (5), wells (3)",
            "  OVER (1): walls",
            "  moved since the previous run (@40): none",
        ]
    );
    let run40 = |stages: serde_json::Value| json!({"summary": {"stages": stages}}).to_string();
    put(
        &dir,
        "dev/work-budget/1.json",
        &run40(
            json!({"a": {"per": {"40": {"ops": 1500.5}}}, "b": {"per": {"40": {"ops": 7}}}, "roll": {"per": {"40": {"ops": 1}}}}),
        ),
    );
    // one run moves nothing
    assert!(lines(&dir).unwrap().last().unwrap().ends_with("none"));
    put(
        &dir,
        "dev/work-budget/2.json",
        &run40(
            json!({"c": {"per": {"40": {"ops": -2_500_000}}}, "b": {"per": {"40": {"ops": 7.0}}}, "roll": {"per": {"40": {"ops": 2}}}, "d": {"per": {}}, "e": {"per": {"40": {"ops": true}}}}),
        ),
    );
    assert_eq!(
        lines(&dir).unwrap().last().unwrap(),
        "  moved since the previous run (@40): c 0 -> -2,500,000; e 0 -> 1; a 1,500 -> 0"
    );
    put(
        &dir,
        "dev/work-budget.md",
        "| stage | x |\n| **the whole roll** | 1 |\n",
    );
    assert_eq!(lines(&dir).unwrap()[0], "work budget (dev/work-budget.md): the whole roll - counted operations @40, exponent -, budget -, -");
    for bad in [
        json!([]).to_string(),
        json!({"summary": [1]}).to_string(),
        json!({"summary": {"stages": [1]}}).to_string(),
        run40(json!({"a": 1})),
        run40(json!({"a": {"per": [1]}})),
        run40(json!({"a": {"per": {"40": {"x": 1}}}})),
        run40(json!({"a": {"per": {"40": {"ops": "many"}}}})),
        "not json".to_owned(),
    ] {
        put(&dir, "dev/work-budget/3.json", &bad);
        assert!(lines(&dir).is_err(), "{bad}");
    }
    put(
        &dir,
        "dev/work-budget/3.json",
        &json!({"summary": {}}).to_string(),
    );
    assert!(lines(&dir)
        .unwrap()
        .last()
        .unwrap()
        .ends_with("c -2,500,000 -> 0; b 7 -> 0; e 1 -> 0"));
    std::fs::write(dir.join("dev/work-budget/3.json"), b"\xff").unwrap();
    assert!(lines(&dir).is_err());
    std::fs::remove_file(dir.join("dev/work-budget/3.json")).unwrap();
    std::fs::create_dir_all(dir.join("dev/work-budget/3.json")).unwrap();
    assert!(lines(&dir).is_err());
    std::fs::write(dir.join("dev/work-budget.md"), b"\xff").unwrap();
    assert!(lines(&dir).is_err());
}

#[test]
fn python_truth_of_a_placeholder() {
    for (v, want) in [
        (json!(null), false),
        (json!(true), true),
        (json!(0), false),
        (json!(""), false),
        (json!([1]), true),
        (json!({}), false),
    ] {
        assert_eq!(truthy(&v), want, "{v}");
    }
}

/// The landing's in-process holding (feature 449 T121): the tasks it ticks handed in, the run recorded as the command recorded it, and
/// a broken active-task mark failing as the command's traceback.
#[test]
fn the_landing_asks_the_holding_box_in_process() {
    let dir = repo("todo-holding-reply");
    tree(&dir);
    let at = dir.join("specs/3-going").to_string_lossy().into_owned();
    put(
        &dir,
        ".git/active-task",
        r#"{"feature": "3-going", "task": "T2"}"#,
    );
    let held = super::holding_reply(&at, "T9", &dir);
    assert!(held.stdout.contains("<- the active task"), "{held:?}");
    assert_eq!(super::holding_reply(&at, "T2 T9", &dir).stdout, "");
    let usage = std::fs::read_to_string(dir.join(".git/tool-usage.jsonl")).unwrap();
    assert!(usage.contains("\"speckit-todo\""));
    put(&dir, ".git/active-task", "[1]");
    assert_eq!(super::holding_reply(&at, "", &dir).code, 1);
}
