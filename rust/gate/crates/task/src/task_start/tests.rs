//! `l7r-gate task-start` (feature 449 T131, from `task_start.py`): the mark, the feature named, the start logged, a held feature
//! refused, a phase task's old code held and any other task's hold cleared.

use l7r_gate_core::ci::fixtures::put;

use super::{cli, cli_with, task_block};
use crate::tests::{env_of, repo, root_of};

fn words(a: &[&str]) -> Vec<String> {
    a.iter().map(|s| (*s).to_owned()).collect()
}

#[test]
fn a_task_started_is_marked_named_and_logged() {
    let dir = repo("start");
    let root = root_of(&dir);
    let env = env_of(&[("L7R_GATE_TREE", &root.to_string_lossy())]);
    assert_eq!(
        cli(&words(&["9001"]), &root).stderr,
        "usage: task_start.py <feature> <task>\n"
    );
    assert_eq!(
        cli_with(&words(&["99999", "T01"]), &root, &env).stderr,
        "task-start: no single specs/99999* directory\n"
    );
    let said = cli_with(&words(&["9001", "T01"]), &root, &env);
    assert_eq!(said.code, 0, "{}", said.stderr);
    assert_eq!(said.stdout, "task-start: 9001-x T01 is the active task - its checks need its decisions ruled first (make decide)\n");
    // the task's own mark, naming its tree (451 T254)
    let mark = std::fs::read_to_string(root.join(".git/task-marks/9001-x/T01.json")).unwrap();
    let tree = root.to_string_lossy();
    let head = format!("{{\"feature\": \"9001-x\", \"task\": \"T01\", \"tree\": \"{tree}\", \"utc\": \"20");
    assert!(mark.starts_with(&head), "{mark}");
    assert_eq!(
        std::fs::read_to_string(root.join(".specify/feature.json")).unwrap(),
        "{\n  \"feature_directory\": \"specs/9001-x\"\n}\n"
    );
    let starts = std::fs::read_to_string(root.join(".git/task-starts.jsonl")).unwrap();
    assert!(starts.starts_with("{\"feature\": \"9001-x\", \"task\": \"T01\", \"utc\": \"20"));
    assert!(starts.trim_end().ends_with(&format!("\"tree\": \"{tree}\"}}")), "{starts}");
    // by path, from below the root, the tree read where the wrapper did not say
    let by_path = format!("{}/", root.join("specs/9001-x").display());
    let again = cli(&words(&[&by_path, "T02"]), &root);
    assert_eq!(again.code, 0, "{}", again.stderr);
    assert_eq!(
        std::fs::read_to_string(root.join(".git/task-starts.jsonl"))
            .unwrap()
            .lines()
            .count(),
        2
    );
}

#[test]
fn a_held_feature_s_task_is_refused_and_a_raise_keeps_what_was_printed() {
    let dir = repo("start-held");
    let root = root_of(&dir);
    let env = env_of(&[("L7R_GATE_TREE", &root.to_string_lossy())]);
    put(
        &root,
        "specs/9001-x/spec.md",
        "**Status**: ON HOLD until feature 9003\n",
    );
    put(&root, "specs/9003-y/spec.md", "**Status**: In progress\n");
    put(&root, "specs/9003-y/tasks.md", "- [ ] T01 a\n");
    let held = cli_with(&words(&["9001", "T01"]), &root, &env);
    assert_eq!(held.code, 2);
    assert!(held.stderr.contains("is ON HOLD until 9003-y closes"));
    assert!(!root.join(".git/task-marks").exists());
    // an unreadable plan raises before anything is written
    std::fs::write(root.join("specs/9001-x/plan.md"), [0xff]).unwrap();
    assert_eq!(cli_with(&words(&["9001", "T01"]), &root, &env).code, 1);
    // `.specify` a file: the mark written, then the raise
    std::fs::remove_file(root.join("specs/9001-x/plan.md")).unwrap();
    put(&root, "specs/9001-x/spec.md", "**Status**: In progress\n");
    std::fs::remove_dir_all(root.join(".specify")).ok();
    put(&root, ".specify", "x");
    let raised = cli_with(&words(&["9001", "T01"]), &root, &env);
    assert_eq!(raised.code, 1);
    assert!(root.join(".git/task-marks").exists());
    // the start log not writable: the mark and the name written, then the raise
    std::fs::remove_file(root.join(".specify")).unwrap();
    std::fs::rename(root.join(".git/task-starts.jsonl"), root.join(".git/kept")).ok();
    std::fs::create_dir_all(root.join(".git/task-starts.jsonl")).unwrap();
    assert_eq!(cli_with(&words(&["9001", "T01"]), &root, &env).code, 1);
    std::fs::remove_dir(root.join(".git/task-starts.jsonl")).unwrap();
    // the hold's own raise
    put(
        &root,
        "specs/9001-x/spec.md",
        "**Status**: ON HOLD until feature 9003\n",
    );
    put(&root, ".specify/affects.json", "[");
    assert_eq!(cli_with(&words(&["9001", "T01"]), &root, &env).code, 1);
}

#[test]
fn a_phase_task_holds_its_old_code_and_another_task_clears_it() {
    let dir = repo("start-phase");
    let root = root_of(&dir);
    let env = env_of(&[("L7R_GATE_TREE", &root.to_string_lossy())]);
    put(
        &root,
        "l7r/diagram/frame.py",
        "def stage_water_frame(x):\n    return x\n",
    );
    put(
        &root,
        "specs/9001-x/tasks.md",
        "- [ ] T01 the frame\n      phase: water_frame\n      old-code: scripts/*.py\n- [ ] T02 other\n",
    );
    let said = cli_with(&words(&["9001", "T01"]), &root, &env);
    assert_eq!(said.code, 0, "{}", said.stderr);
    assert!(
        said.stdout
            .contains("phase-sources: T01 rebuilds `water_frame` from its derivation - "),
        "{}",
        said.stdout
    );
    let state = std::fs::read_to_string(root.join(".git/phase-sources.json")).unwrap();
    assert!(state.contains("\"scripts/a.py\""), "{state}");
    let other = cli_with(&words(&["9001", "T02"]), &root, &env);
    assert_eq!(other.code, 0);
    assert!(!root.join(".git/phase-sources.json").exists());
    // the sources' raise after the mark: what was printed is kept
    put(
        &root,
        "specs/9001-x/tasks.md",
        "- [ ] T01 x\n      phase: water_frame\n      old-code: /abs\n",
    );
    let raised = cli_with(&words(&["9001", "T01"]), &root, &env);
    assert_eq!(raised.code, 1);
    assert!(raised.stdout.contains("is the active task"));
    // no tasks.md: no block, no hold
    std::fs::remove_file(root.join("specs/9001-x/tasks.md")).unwrap();
    assert_eq!(cli_with(&words(&["9001", "T01"]), &root, &env).code, 0);
    std::fs::write(root.join("specs/9001-x/tasks.md"), [0xff]).unwrap();
    assert_eq!(cli_with(&words(&["9001", "T01"]), &root, &env).code, 1);
}

#[test]
fn a_task_s_block_runs_to_the_next_box() {
    let tasks = "- [ ] T01 a\n  phase: x\n- [x] T02 b\n  more\n";
    assert_eq!(task_block(tasks, "T01"), "- [ ] T01 a\n  phase: x\n");
    assert_eq!(task_block(tasks, "T02"), "- [x] T02 b\n  more\n");
    assert_eq!(task_block(tasks, "T03"), "");
}

/// The census entries holding `needle`, the guard log these tests write to (`crate::tests::quiet_census`).
fn census_with(needle: &str) -> usize {
    std::fs::read_dir(crate::tests::quiet_census())
        .map(|d| {
            d.filter_map(Result::ok)
                .filter(|e| std::fs::read_to_string(e.path()).is_ok_and(|t| t.contains(needle)))
                .count()
        })
        .unwrap_or(0)
}

#[test]
fn a_task_that_is_not_performance_work_waits_for_an_open_one() {
    let dir = repo("start-perf");
    let root = root_of(&dir);
    let tree = root.to_string_lossy().into_owned();
    let env = env_of(&[("L7R_GATE_TREE", &tree)]);
    // T28's own line: a `[perf]` quoted in the prose of T01 marks nothing, T02's tag after its id does
    put(
        &root,
        "specs/9001-x/tasks.md",
        "- [ ] T01 the first, a [perf] tag quoted\n- [ ] T02 [perf] the faster gate\n- [x] T09 done\n",
    );
    let refused = cli_with(&words(&["9001", "T01"]), &root, &env);
    assert_eq!(refused.code, 2, "{}", refused.stdout);
    assert!(
        refused.stderr.contains(
            "9001-x T01 is not performance work, and 9001-x T02 is (T02 [perf] the faster gate)"
        ),
        "{}",
        refused.stderr
    );
    assert!(
        refused
            .stderr
            .contains("Start it first: make task-start F=9001 T=T02"),
        "{}",
        refused.stderr
    );
    assert!(
        refused.stderr.contains("PERF_LATER_OK=\"<reason>\""),
        "{}",
        refused.stderr
    );
    assert!(!root.join(".git/task-marks").exists());
    // the performance task itself starts
    assert_eq!(cli_with(&words(&["9001", "T02"]), &root, &env).code, 0);
    // the escape: a reason of two words, recorded; one word refused
    let short = env_of(&[("L7R_GATE_TREE", &tree), ("PERF_LATER_OK", "later")]);
    let said = cli_with(&words(&["9001", "T01"]), &root, &short);
    assert_eq!(said.code, 2);
    assert!(
        said.stderr.contains("PERF_LATER_OK needs a REASON"),
        "{}",
        said.stderr
    );
    // unique to this run: the census directory outlives it
    let why = format!(
        "waiting on the T18 landing (a start-perf test, {:?})",
        std::time::SystemTime::now()
    );
    let escaped = env_of(&[("L7R_GATE_TREE", &tree), ("PERF_LATER_OK", &why)]);
    let said = cli_with(&words(&["9001", "T01"]), &root, &escaped);
    assert_eq!(said.code, 0, "{}", said.stderr);
    assert_eq!(census_with(&why), 1);
    assert!(census_with("later") >= 1);
}

#[test]
fn perf_1_s_checklist_and_another_active_feature_count_too() {
    let dir = repo("start-perf-other");
    let root = root_of(&dir);
    let env = env_of(&[("L7R_GATE_TREE", &root.to_string_lossy())]);
    // PERF=1's mark: the checklist heading in the task's plan section
    put(
        &root,
        "specs/9001-x/plan.md",
        &format!(
            "{}### T03 Performance checklist (prompts)\n",
            crate::tests::plan(&["T01", "T02", "T03"])
        ),
    );
    let said = cli_with(&words(&["9001", "T01"]), &root, &env);
    assert_eq!(said.code, 2);
    assert!(
        said.stderr.contains("make task-start F=9001 T=T03"),
        "{}",
        said.stderr
    );
    put(
        &root,
        "specs/9001-x/plan.md",
        &crate::tests::plan(&["T01", "T02", "T03"]),
    );
    // a feature started in this clone, not set down since, holding one: named, of its own feature
    put(&root, "specs/9002-y/spec.md", "**Status**: In progress\n");
    put(
        &root,
        "specs/9002-y/tasks.md",
        "- [ ] T05 [perf] split the suite\n",
    );
    put(
        &root,
        ".git/task-starts.jsonl",
        "{\"feature\": \"9002-y\", \"task\": \"T04\", \"utc\": \"2026-11-20T10:00:00Z\"}\n",
    );
    let said = cli_with(&words(&["9001", "T01"]), &root, &env);
    assert_eq!(said.code, 2);
    assert!(said.stderr.contains("and 9002-y T05 is"), "{}", said.stderr);
    assert!(
        said.stderr.contains("make task-start F=9002 T=T05"),
        "{}",
        said.stderr
    );
    // set down since its start: not active, the start passes
    put(
        &root,
        ".git/set-downs.jsonl",
        "{\"feature\": \"9002-y\", \"why\": \"a b\", \"utc\": \"2026-11-20T11:00:00Z\"}\n",
    );
    assert_eq!(cli_with(&words(&["9001", "T01"]), &root, &env).code, 0);
    // a log that cannot be read raises
    std::fs::write(root.join(".git/set-downs.jsonl"), [0xff]).unwrap();
    assert_eq!(cli_with(&words(&["9001", "T01"]), &root, &env).code, 1);
}

#[test]
fn a_parked_stage_s_task_is_refused_until_the_gm_s_words_resume_it() {
    let dir = repo("start-parked");
    let root = root_of(&dir);
    let tree = root.to_string_lossy().into_owned();
    let env = env_of(&[("L7R_GATE_TREE", &tree)]);
    put(&root, "rust/parked/src/homesteads.rs", "");
    put(
        &root,
        "specs/9001-x/tasks.md",
        "- [ ] T30 phase: homesteads - every household seated\n- [ ] T31 [perf] the faster gate\n- [ ] T29 phase: seat - the seat\n",
    );
    // the stop comes first: no PERF_LATER_OK is asked of a parked stage's task
    let refused = cli_with(&words(&["9001", "T30"]), &root, &env);
    let err = refused.stderr.as_str();
    assert_eq!(refused.code, 2, "{}", refused.stdout);
    let ok1 = err.contains("make task-start of 9001-x T30 (homesteads)");
    assert!(ok1, "{err}");
    let ok2 = err.contains("Stop before homesteads, and talk first");
    assert!(ok2, "{err}");
    let ok3 = err.contains("GM_RESUMED=\"<the GM's words resuming it>\"");
    assert!(ok3, "{err}");
    assert!(!root.join(".git/task-marks").exists());
    // a stage that is not parked is no part of it
    let seat = cli_with(&words(&["9001", "T29"]), &root, &env);
    assert!(!seat.stderr.contains("parked"), "{}", seat.stderr);
    // one word resumes nothing
    let short = env_of(&[("L7R_GATE_TREE", &tree), ("GM_RESUMED", "yes")]);
    let said = cli_with(&words(&["9001", "T30"]), &root, &short);
    assert_eq!(said.code, 2);
    let err = said.stderr.as_str();
    assert!(err.contains("GM_RESUMED needs the GM's words"), "{err}");
    let gm = format!(
        "go ahead with homesteads now (a start-parked test, {:?})",
        std::time::SystemTime::now()
    );
    let resumed = env_of(&[
        ("L7R_GATE_TREE", &tree),
        ("GM_RESUMED", &gm),
        ("PERF_LATER_OK", "the GM resumed the stage"),
    ]);
    let said = cli_with(&words(&["9001", "T30"]), &root, &resumed);
    assert_eq!(said.code, 0, "{}", said.stderr);
    let row = std::fs::read_to_string(root.join(".git/parked-resumed.jsonl")).unwrap();
    assert!(row.contains("\"stage\": \"homesteads\""), "{row}");
    assert_eq!(census_with(&gm), 1);
    // resumed, its next task starts with no words
    let again = cli_with(
        &words(&["9001", "T30"]),
        &root,
        &env_of(&[
            ("L7R_GATE_TREE", &tree),
            ("PERF_LATER_OK", "the GM resumed the stage"),
        ]),
    );
    assert_eq!(again.code, 0, "{}", again.stderr);
}

#[test]
fn a_resume_the_record_cannot_keep_is_raised_naming_the_record() {
    let dir = repo("start-parked-unkept");
    let root = root_of(&dir);
    let tree = root.to_string_lossy().into_owned();
    put(&root, "rust/parked/src/homesteads.rs", "");
    put(
        &root,
        "specs/9001-x/tasks.md",
        "- [ ] T30 phase: homesteads - every household seated\n",
    );
    // the record's path is a directory, so its append fails
    std::fs::create_dir_all(root.join(".git/parked-resumed.jsonl")).unwrap();
    let gm = format!(
        "go ahead with homesteads now (an unkept-record test, {:?})",
        std::time::SystemTime::now()
    );
    let env = env_of(&[
        ("L7R_GATE_TREE", &tree),
        ("GM_RESUMED", &gm),
        ("PERF_LATER_OK", "the GM resumed the stage"),
    ]);
    let said = cli_with(&words(&["9001", "T30"]), &root, &env);
    assert_ne!(said.code, 0, "{}", said.stdout);
    let err = said.stderr.as_str();
    assert!(err.contains("parked-resumed.jsonl"), "{err}");
}
