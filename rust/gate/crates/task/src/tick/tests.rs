//! `l7r-gate tick` (feature 449 T131): its arguments, the feature found, every refusal path of the command, the closing tick, the archive
//! and its record, the land's first pass, and `--resolve` for `task-add.py`.

use std::path::Path;

use l7r_gate_core::ci::fixtures::{git, put};

use super::{checks, cli, cli_with, repo_root, spec_dir, tick, Checked};
use crate::tests::{ask, env_of, repo, root_of, REASON};

fn words(a: &[&str]) -> Vec<String> {
    a.iter().map(|s| (*s).to_owned()).collect()
}

#[test]
fn the_command_line_s_arguments_and_resolution() {
    let dir = repo("cli");
    let root = root_of(&dir);
    let none = env_of(&[]);
    let usage = cli_with(&words(&["9001"]), &root, &none);
    assert_eq!(usage.code, 2);
    assert!(usage
        .stderr
        .starts_with("usage: tick-task.py <feature> <task> <note>"));
    assert_eq!(cli(&words(&[]), &root).code, 2);
    // the process's own environment read for `make tick`'s note
    assert_eq!(
        cli(&words(&["99999", "T01", "--note-from-env"]), &root).code,
        2
    );
    let missing = cli_with(&words(&["99999", "T01", "n"]), &root, &none);
    assert!(missing
        .stderr
        .starts_with("tick: no single specs/99999* directory under"));
    put(&root, "specs/9002-e/spec.md", "x");
    assert!(cli_with(&words(&["9002", "T01", "n"]), &root, &none)
        .stderr
        .ends_with("tasks.md does not exist\n"));
    // the note from the environment, `make tick`'s form
    let env = env_of(&[
        ("TICK_NOTE", "from the environment"),
        ("PLAN_REVIEW_OK", REASON),
        ("L7R_GATE_TREE", &root.to_string_lossy()),
    ]);
    let done = cli_with(&words(&["9001", "T01", "--note-from-env"]), &root, &env);
    assert_eq!(done.code, 0, "{}", done.stderr);
    assert!(done
        .stdout
        .contains("ticked - [x] T01 the first\n2 task(s) still open in specs/9001-x/tasks.md\n"));
    assert!(std::fs::read_to_string(root.join("specs/9001-x/tasks.md"))
        .unwrap()
        .contains("verify: DONE. from the environment"));
    // `--landing` is `make land`'s alone
    let landing = cli_with(
        &words(&["9001", "T02", "n", "--landing"]),
        &root,
        &env_of(&[("L7R_LAND_TICKS", "T05")]),
    );
    assert!(landing.stderr.contains("--landing is `make land`'s"));
    let named = cli_with(
        &words(&["9001", "T02", "landed", "--landing"]),
        &root,
        &env_of(&[("L7R_LAND_TICKS", "T01 T02"), ("PLAN_REVIEW_OK", REASON)]),
    );
    assert_eq!(named.code, 0, "{}", named.stderr);
}

#[test]
fn the_root_and_the_feature_are_found_as_tick_task_found_them() {
    let dir = repo("resolve");
    let root = root_of(&dir);
    assert_eq!(repo_root(&root.join("specs")), root);
    // outside a repository: the nearest ancestor holding `specs/`, else the place itself
    let bare = dir.join("bare");
    put(&bare, "specs/1-a/tasks.md", "x");
    std::fs::create_dir_all(bare.join("deep")).unwrap();
    assert_eq!(repo_root(&bare.join("deep")), bare.canonicalize().unwrap());
    let lone = dir.join("lone");
    std::fs::create_dir_all(&lone).unwrap();
    assert_eq!(repo_root(&lone), lone.canonicalize().unwrap());
    assert_eq!(
        repo_root(Path::new("/nonexistent-place")),
        Path::new("/nonexistent-place")
    );
    assert_eq!(spec_dir(&root, "9001"), Some(root.join("specs/9001-x")));
    assert_eq!(spec_dir(&root, "./9001-x"), Some(root.join("specs/9001-x")));
    put(&root, "specs/9001-y/x", "");
    assert_eq!(spec_dir(&root, "9001"), None);
    let said = cli(&words(&["--resolve", "9001-x"]), &root);
    assert_eq!(
        said.stdout,
        format!(
            "[\"{}\", \"{}\"]\n",
            root.display(),
            root.join("specs/9001-x").display()
        )
    );
    assert!(cli(&words(&["--resolve", "9"]), &root)
        .stdout
        .ends_with(", null]\n"));
    assert_eq!(cli(&words(&["--resolve"]), &root).code, 2);
}

#[test]
fn every_refusal_of_the_tick_and_what_it_prints() {
    let dir = repo("refusals");
    let root = root_of(&dir);
    let d = root.join("specs/9001-x");
    let a = |task: &'static str, note: &'static str| ask(&root, &d, task, note);
    // the plan gate's own message comes before a refusal of the text
    let empty = tick(&a("T01", "  "), false, false);
    assert_eq!(empty.code, 2);
    assert!(empty.stdout.contains("BYPASSED"));
    assert!(empty
        .stderr
        .starts_with("tick: refused - the verify note is empty"));
    assert!(tick(&a("T09", "n"), false, false)
        .stderr
        .contains("T09 is already ticked ("));
    let boxes = tick(&a("T02", "n"), true, false);
    assert_eq!(
        (
            boxes.code,
            boxes.stderr.starts_with("--boxes: no research-box line")
        ),
        (1, true)
    );
    assert!(tick(&a("T03", "n"), false, false)
        .stderr
        .contains("research box unticked"));
    let ticked = tick(&a("T03", "n"), true, false);
    assert_eq!(ticked.code, 0, "{}", ticked.stderr);
    // a refusal that raises: tasks.md unreadable as text
    std::fs::write(d.join("tasks.md"), b"- [ ] T01 a\n\xff").unwrap();
    assert_eq!(tick(&a("T01", "n"), false, false).code, 1);
    // tasks.md gone after the refusals are asked is a raise
    std::fs::remove_file(d.join("tasks.md")).unwrap();
    assert_eq!(tick(&a("T01", "n"), false, false).code, 1);
}

#[test]
fn the_last_tick_closes_only_past_the_closing_check_and_the_archive_is_recorded() {
    let dir = repo("close");
    let root = root_of(&dir);
    let d = root.join("specs/9001-x");
    std::fs::write(d.join("tasks.md"), "- [x] T01 a\n- [ ] T02 b\n").unwrap();
    let refused = tick(&ask(&root, &d, "T02", "n"), false, false);
    assert_eq!(refused.code, 2, "{}", refused.stderr);
    assert!(refused
        .stderr
        .contains("this tick would close the feature, and:\n  9001-x has no report.md"));
    put(&d, "report.md", "# r\n");
    let closed = tick(&ask(&root, &d, "T02", "n"), false, false);
    assert_eq!(closed.code, 0, "{}", closed.stderr);
    assert!(closed.stdout.contains("0 task(s) still open"));
    // the implementation check, in process since feature 449 T132: the feature is not tagged `research record`, so it owes nothing
    assert_eq!(closed.stderr, "");
    let usage = std::fs::read_to_string(root.join(".git/tool-usage.jsonl")).unwrap();
    assert!(usage
        .contains("\"tool\": \"tick-archive\", \"kind\": \"step\", \"outcome\": \"unchanged\""));
    // a closing check that cannot read its record raises
    std::fs::write(d.join("tasks.md"), "- [x] T01 a\n- [ ] T02 b\n").unwrap();
    put(&d, "measurements.json", "5");
    assert_eq!(tick(&ask(&root, &d, "T02", "n"), false, false).code, 1);
}

#[test]
fn a_finished_section_is_archived_at_the_tick() {
    let dir = repo("archive");
    let root = root_of(&dir);
    let d = root.join("specs/9001-x");
    // the plan reviewed CLEAR by the plan gate's own record, then T01's tick finishes its section
    let text = std::fs::read_to_string(d.join("plan.md")).unwrap();
    let verdict = serde_json::json!({"plan_sha256": l7r_guard::shared::sha256::hex(text.as_bytes()), "decisions": [], "verdict": "CLEAR"});
    let file = dir.join("verdict.json");
    std::fs::write(&file, verdict.to_string()).unwrap();
    let no_claims = |_: &[String]| crate::Reply {
        stdout: String::new(),
        stderr: String::new(),
        code: 0,
    };
    assert_eq!(no_claims(&[]).code, 0);
    let recorded = l7r_gate_plan::plan::cli(
        &words(&[
            "record",
            "9001",
            &file.to_string_lossy(),
            "--as",
            "spec-fidelity",
        ]),
        &root,
        &no_claims,
    );
    assert_eq!(recorded.code, 0, "{}", recorded.stderr);
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "plan"]);
    let mut gated = ask(&root, &d, "T01", "n");
    gated.escaped = None;
    let said = tick(&gated, false, false);
    assert_eq!(said.code, 0, "{}", said.stderr);
    assert!(
        said.stdout
            .ends_with("tick: archived the plan sections of T01, T09 to plan-done.md\n"),
        "{}",
        said.stdout
    );
    let usage = std::fs::read_to_string(root.join(".git/tool-usage.jsonl")).unwrap();
    assert!(
        usage.contains("\"tool\": \"tick-archive\", \"kind\": \"step\", \"outcome\": \"changed\"")
    );
    // a tick of a feature directory outside the root raises after its write, as `relative_to` did
    let elsewhere = repo("archive-elsewhere");
    let other = root_of(&elsewhere).join("specs/9001-x");
    let outside = tick(&ask(&root, &other, "T02", "n"), false, false);
    assert_eq!(outside.code, 1);
    assert!(outside.stderr.contains("is not in the subpath of"));
    // a tasks.md the tick cannot write raises
    let tasks = d.join("tasks.md");
    let mut perms = std::fs::metadata(&tasks).unwrap().permissions();
    std::os::unix::fs::PermissionsExt::set_mode(&mut perms, 0o444);
    std::fs::set_permissions(&tasks, perms).unwrap();
    let locked = tick(&ask(&root, &d, "T02", "n"), false, false);
    assert_eq!(locked.code, 1, "{}", locked.stderr);
}

#[test]
fn a_feature_with_no_plan_ticks_with_no_archive() {
    let dir = repo("no-plan");
    let root = root_of(&dir);
    let d = root.join("specs/9001-x");
    std::fs::remove_file(d.join("plan.md")).unwrap();
    std::fs::remove_file(root.join("docs/approach-checklist.md")).unwrap();
    let said = tick(&ask(&root, &d, "T02", "n"), false, false);
    assert_eq!(said.code, 0, "{}", said.stderr);
    assert!(said
        .stdout
        .ends_with("2 task(s) still open in specs/9001-x/tasks.md\n"));
    assert!(!root.join(".git/tool-usage.jsonl").exists());
}

#[test]
fn the_land_s_first_pass_asks_every_task_in_one_reading() {
    let dir = repo("checks");
    let root = root_of(&dir);
    let d = root.join("specs/9001-x");
    let env = env_of(&[
        ("PLAN_REVIEW_OK", REASON),
        ("L7R_GATE_TREE", &root.to_string_lossy()),
    ]);
    let rows = checks(&root, &d, "n", &words(&["T01", "T03", "T09"]), false, &env).unwrap();
    assert_eq!(
        rows[0],
        Checked {
            task: "T01".to_owned(),
            tick: String::new(),
            refusal: String::new(),
            box_open: false
        }
    );
    assert!(rows[1].refusal.contains("research box unticked") && rows[1].box_open);
    assert_eq!(rows[2].tick, "T09 is already ticked");
    // under BOXES=1 the open box is no refusal, and is still read
    let boxed = checks(&root, &d, "n", &words(&["T03"]), true, &env).unwrap();
    assert!(boxed[0].refusal.is_empty() && boxed[0].box_open);
    // the command's form: JSON, its usage, a missing feature and a raise
    let said = cli_with(
        &words(&["--land-check", "9001", "n", "T01", "--boxes"]),
        &root,
        &env,
    );
    assert_eq!(
        said.stdout,
        "[{\"task\": \"T01\", \"tick\": \"\", \"refusal\": \"\", \"box_open\": false}]\n"
    );
    assert_eq!(
        cli_with(&words(&["--land-check", "9001", "n"]), &root, &env).code,
        2
    );
    assert_eq!(
        cli_with(&words(&["--land-check", "9", "n", "T01"]), &root, &env).code,
        2
    );
    std::fs::remove_file(d.join("tasks.md")).unwrap();
    assert_eq!(
        cli_with(&words(&["--land-check", "9001", "n", "T01"]), &root, &env).code,
        1
    );
    // a refusal that raises fails the pass
    put(&d, "tasks.md", "- [ ] T01 a\n");
    std::fs::write(d.join("plan.md"), [0xff]).unwrap();
    assert!(checks(&root, &d, "n", &words(&["T01"]), false, &env).is_err());
}
