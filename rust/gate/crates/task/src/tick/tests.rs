//! `l7r-gate tick` (feature 449 T131): its arguments, the feature found, every refusal path of the command, the closing tick, the archive
//! and its record, the land's first pass, and `--resolve` for `task-add.py`.

use std::path::Path;

use l7r_gate_core::ci::fixtures::{git, put};

use super::{checks, cli, cli_with, repo_root, spec_dir, tick, Checked, Section};
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
    // the ticked task, archived at its tick (feature 449 T142)
    assert!(
        std::fs::read_to_string(root.join("specs/9001-x/tasks-done.md"))
            .unwrap()
            .contains("verify: DONE. from the environment")
    );
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
    // ...and `make land`'s first pass is told so before its gate (451 T307 part 2): where the tasks asked are every open box, the
    // closing check's reasons join the last one's refusal; a task that would not tick, or a box left open, asks nothing
    let env = env_of(&[
        ("PLAN_REVIEW_OK", REASON),
        ("L7R_GATE_TREE", &root.to_string_lossy()),
    ]);
    let first =
        |ids: &[&str]| checks(&root, &d, "n", &words(ids), false, &env, Section::Owed).unwrap();
    let said = first(&["T02"]).remove(0).refusal;
    let why = "tick: refused - this tick would close the feature, and:\n  9001-x has no report.md";
    assert!(said.contains(why), "{said}");
    // ...but not at a build half's hand-in (461 T60): the close is its closing half's to answer
    let at = |section| {
        checks(&root, &d, "n", &words(&["T02"]), false, &env, section)
            .unwrap()
            .remove(0)
            .refusal
    };
    assert_eq!(at(Section::Closing), "");
    assert_eq!(first(&["T09"])[0].refusal, "");
    std::fs::write(d.join("tasks.md"), "- [ ] T01 a\n- [ ] T02 b\n").unwrap();
    assert_eq!(first(&["T02"])[0].refusal, "");
    assert!(first(&["T01", "T02"])[1]
        .refusal
        .contains("would close the feature"));
    std::fs::write(d.join("tasks.md"), "- [x] T01 a\n- [ ] T02 b\n").unwrap();
    put(&d, "report.md", "# r\n");
    assert_eq!(first(&["T02"])[0].refusal, "");
    let closed = tick(&ask(&root, &d, "T02", "n"), false, false);
    assert_eq!(closed.code, 0, "{}", closed.stderr);
    assert!(closed.stdout.contains("0 task(s) still open"));
    // the implementation check, in process since feature 449 T132: the feature is not tagged `research record`, so it owes nothing
    assert_eq!(closed.stderr, "");
    // the plan's sections stay (no CLEAR review), the two ticked tasks move: the step changed something (feature 449 T142)
    let usage = std::fs::read_to_string(root.join(".git/tool-usage.jsonl")).unwrap();
    assert!(
        usage.contains("\"tool\": \"tick-archive\", \"kind\": \"step\", \"outcome\": \"changed\"")
    );
    assert!(closed
        .stdout
        .ends_with("tick: archived the ticked task(s) T01, T02 to tasks-done.md\n"));
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
    let verdict = serde_json::json!({"plan_sha256": l7r_shared::sha256::hex(text.as_bytes()), "decisions": [], "verdict": "CLEAR"});
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
        said.stdout.ends_with("tick: archived the plan sections of T01, T09 to plan-done.md\ntick: archived the ticked task(s) T01, T09 to tasks-done.md\n"),
        "{}",
        said.stdout
    );
    let usage = std::fs::read_to_string(root.join(".git/tool-usage.jsonl")).unwrap();
    assert!(
        usage.contains("\"tool\": \"tick-archive\", \"kind\": \"step\", \"outcome\": \"changed\"")
    );
}

/// The archive's test's failures, on a repository of their own (feature 449 T167: they read nothing the archive wrote, and the two
/// together took over FR-008's tenth of a second).
#[test]
fn a_tick_outside_the_root_or_of_a_tasks_md_it_cannot_write_raises() {
    let dir = repo("archive-fails");
    let root = root_of(&dir);
    let d = root.join("specs/9001-x");
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

/// 451 T537: where the feature's records are split, what a tick archives is folded into a new part; a fold that cannot write is said
/// and the tick done, its task in the flat tail.
#[test]
fn a_split_feature_s_tick_folds_its_archive_into_parts() {
    let dir = repo("split");
    let root = root_of(&dir);
    let d = root.join("specs/9001-x");
    std::fs::remove_file(d.join("plan.md")).unwrap();
    std::fs::remove_file(root.join("docs/approach-checklist.md")).unwrap();
    // a task left open, so no tick here closes the feature
    let tasks = std::fs::read_to_string(d.join("tasks.md")).unwrap();
    std::fs::write(d.join("tasks.md"), tasks + "- [ ] T04 left open\n").unwrap();
    assert_eq!(tick(&ask(&root, &d, "T02", "n"), false, false).code, 0);
    l7r_shared::speckit::archive::fold(&d, true).unwrap();
    let said = tick(&ask(&root, &d, "T01", "n"), false, false);
    assert_eq!(said.code, 0, "{}", said.stderr);
    assert!(
        said.stdout
            .contains("tick: folded the archive into 1 part(s) under "),
        "{}",
        said.stdout
    );
    assert!(!d.join("tasks-done.md").exists());
    let done = l7r_shared::speckit::tasks::done_text(&d).unwrap();
    assert!(done.contains("- [x] T01 the first") && done.contains("- [x] T09 done"));
    // the parts' directory a file: the fold fails, the tick stands
    std::fs::remove_dir_all(d.join("archive/tasks-done")).unwrap();
    std::fs::write(d.join("archive/tasks-done"), "in the way").unwrap();
    let kept = tick(&ask(&root, &d, "T03", "n"), true, false);
    assert_eq!(kept.code, 0, "{}", kept.stderr);
    assert!(
        kept.stderr.contains("tick: the archive stays flat - "),
        "{}",
        kept.stderr
    );
    assert!(d.join("tasks-done.md").is_file());
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
    // ...but the ticked tasks move, and the step is recorded where no plan.md stands too (feature 449 T142)
    assert!(said.stdout.ends_with(
        "2 task(s) still open in specs/9001-x/tasks.md\ntick: archived the ticked task(s) T02, T09 to tasks-done.md\n"
    ));
    let usage = std::fs::read_to_string(root.join(".git/tool-usage.jsonl")).unwrap();
    assert!(usage.contains("\"outcome\": \"changed\""));
    // an archived task is already ticked, for the tick and the land's first pass alike
    assert!(tick(&ask(&root, &d, "T09", "n"), false, false)
        .stderr
        .contains("T09 is already ticked ("));
    // ...and an id in neither file is no task
    assert!(tick(&ask(&root, &d, "T77", "n"), false, false)
        .stderr
        .contains("no open task T77 in tasks.md"));
    // an old capital `- [X]`, which the tick never read as its own, is no open task archived or not
    let done = std::fs::read_to_string(d.join("tasks-done.md")).unwrap();
    std::fs::write(d.join("tasks-done.md"), format!("{done}- [X] T66 old\n")).unwrap();
    assert!(tick(&ask(&root, &d, "T66", "n"), false, false)
        .stderr
        .contains("no open task T66 in tasks.md"));
    // an archive that cannot be written leaves the task ticked in tasks.md, said, and the tick done
    std::fs::remove_file(d.join("tasks-done.md")).unwrap();
    std::fs::create_dir(d.join("tasks-done.md")).unwrap();
    let kept = tick(&ask(&root, &d, "T01", "n"), false, false);
    assert_eq!(kept.code, 0, "{}", kept.stderr);
    assert!(kept
        .stderr
        .starts_with("tick: the ticked tasks stay in tasks.md - "));
    let usage = std::fs::read_to_string(root.join(".git/tool-usage.jsonl")).unwrap();
    assert!(usage.contains("\"outcome\": \"unchanged\""));
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
    let rows = checks(
        &root,
        &d,
        "n",
        &words(&["T01", "T03", "T09"]),
        false,
        &env,
        Section::Owed,
    )
    .unwrap();
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
    let boxed = checks(&root, &d, "n", &words(&["T03"]), true, &env, Section::Owed).unwrap();
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
    assert!(checks(&root, &d, "n", &words(&["T01"]), false, &env, Section::Owed).is_err());
}

#[test]
fn the_archive_form_moves_the_ticked_tasks_alone() {
    // feature 449 T142: the tick's last step by hand
    let dir = repo("archive-form");
    let root = root_of(&dir);
    let d = root.join("specs/9001-x");
    assert_eq!(cli(&words(&["--archive"]), &root).code, 2);
    assert_eq!(cli(&words(&["--archive", "9"]), &root).code, 2);
    assert_eq!(
        cli(&words(&["--archive", "9001"]), &root).stdout,
        "tick --archive: 1 ticked task(s) moved to 9001-x/tasks-done.md: T09\n"
    );
    assert_eq!(
        cli(&words(&["--archive", "9001"]), &root).stdout,
        "tick --archive: 0 ticked task(s) moved to 9001-x/tasks-done.md: none\n"
    );
    put(&d, "tasks.md", "- [x] T05 x\n");
    std::fs::remove_file(d.join("tasks-done.md")).unwrap();
    std::fs::create_dir(d.join("tasks-done.md")).unwrap();
    let failed = cli(&words(&["--archive", "9001"]), &root);
    assert_eq!(failed.code, 1);
    assert!(failed.stderr.starts_with("tick --archive: "));
}

/// RED FIRST (feature 451 T182): a round-arbiter tooling fix recorded as landing with a task (`make arbiter-fix-done ... LANDING=`)
/// holds the land's first pass of that task no longer - its done row goes out in the landing's own tick commit - while a landing of
/// another task, and a plain `make tick`, are still held (observed 2026-11-23: 451 T177's land refused by the fix it carried).
#[test]
fn a_fix_landing_with_its_task_holds_that_landing_s_first_pass_no_longer() {
    let dir = repo("checks-fix");
    let root = root_of(&dir);
    let d = root.join("specs/9001-x");
    put(
        &d,
        "arbiter.jsonl",
        &format!(
            "{}\n",
            serde_json::json!({"trigger": "ask:9001-f", "fix": "open", "tooling_fix": "build it"})
        ),
    );
    let env = env_of(&[
        ("PLAN_REVIEW_OK", REASON),
        ("L7R_GATE_TREE", &root.to_string_lossy()),
    ]);
    let held = |task: &str| {
        checks(&root, &d, "n", &words(&[task]), false, &env, Section::Owed).unwrap()[0]
            .refusal
            .contains("tooling fix is open")
    };
    assert!(held("T01"));
    put(
        &root,
        ".git/arbiter-fix-landing.json",
        &serde_json::json!([{"trigger": "ask:9001-f", "feature": "9001-x", "task": "T01", "home": "9001-x"}]).to_string(),
    );
    assert!(!held("T01"));
    assert!(held("T02"));
    let plain = tick(&ask(&root, &d, "T01", "n"), false, false);
    assert_eq!(plain.code, 2);
    assert!(
        plain.stderr.contains("tooling fix is open"),
        "{}",
        plain.stderr
    );
}

/// RED FIRST (451 T307 part 2): a task whose work was built inside another task's reviewed section closes with it - `Built here:`
/// in the host's section, the host CLEAR and in the landing or ticked, its own section the unfilled stub - and is refused otherwise,
/// in the first pass (`checks`) as at the tick.
#[test]
fn a_task_built_inside_another_s_section_closes_with_it() {
    let dir = repo("built-inside");
    let root = root_of(&dir);
    let d = root.join("specs/9001-x");
    let host = "## T01 the task\n\n### T01 Approach (checklist part A)\n\n1. **one** answered\n\nBuilt here: T05 - the half it absorbed\n\n";
    let stub = l7r_gate_plan::plan::template::stubs("T05")[1].clone();
    let plan = format!("{host}{stub}\n## T06 the task\n\n### T06 Approach (checklist part A)\n\n1. **one** answered\n\n");
    put(&root, "specs/9001-x/plan.md", &plan);
    let tasks = "- [ ] T01 host\n- [ ] T05 absorbed\n- [ ] T06 left open\n";
    put(&root, "specs/9001-x/tasks.md", tasks);
    let sec = l7r_shared::plan_text::task_sections(&plan)
        .remove("T01")
        .unwrap();
    let digest = l7r_shared::sha256::hex(sec.as_bytes());
    let review = format!(
        "{{\"tasks\": {{\"T01\": {{\"verdict\": \"CLEAR\", \"section_sha256\": \"{digest}\"}}}}}}"
    );
    put(&root, "specs/9001-x/plan-review.json", &review);
    let env = env_of(&[
        ("PLAN_REVIEW_OK", REASON),
        ("L7R_GATE_TREE", &root.to_string_lossy()),
    ]);
    let first =
        |ids: &[&str]| checks(&root, &d, "n", &words(ids), false, &env, Section::Owed).unwrap();
    // alone, its host neither landing nor ticked; beside it, in either order, nothing
    let alone = first(&["T05"]).remove(0).refusal;
    assert!(alone.contains("T05 is named built inside T01's section (`Built here: T05 - the half it absorbed`), but T01 is neither in this landing nor ticked - make land F=9001 T=\"T01 T05\""), "{alone}");
    assert!(first(&["T05", "T01"])
        .iter()
        .all(|c| c.refusal.is_empty() && c.tick.is_empty()));
    assert!(first(&["T01", "T05"]).iter().all(|c| c.refusal.is_empty()));
    // the tick: its box says so, its stub is gone, the event written
    let mut b = ask(&root, &d, "T05", "landed in batch");
    b.landing = words(&["T05", "T01"]);
    let ticked = tick(&b, false, true);
    assert_eq!(ticked.code, 0, "{}", ticked.stderr);
    assert!(ticked.stdout.contains("tick: T05 closed built inside T01's section, its unfilled plan stub removed from 9001-x/plan.md; recorded in"), "{}", ticked.stdout);
    let now = std::fs::read_to_string(d.join("plan.md")).unwrap();
    assert!(!now.contains("### T05") && now.contains("Built here: T05"));
    let done = std::fs::read_to_string(d.join("tasks-done.md")).unwrap_or_default()
        + &std::fs::read_to_string(d.join("tasks.md")).unwrap();
    assert!(done.contains("- [x] T05 absorbed built inside T01\n"));
    // ...its host already ticked: alone, nothing; its host not CLEAR, or its own section filled: refused, each said
    put(&root, "specs/9001-x/plan.md", &plan);
    put(
        &root,
        "specs/9001-x/tasks.md",
        "- [x] T01 host\n- [ ] T05 absorbed\n- [ ] T06 left open\n",
    );
    assert_eq!(first(&["T05"])[0].refusal, "");
    put(&root, "specs/9001-x/plan-review.json", "{}");
    let filled = plan.replace("<the place as it should be>", "the wells drawn");
    put(&root, "specs/9001-x/plan.md", &filled);
    let both = first(&["T05"]).remove(0).refusal;
    assert!(
        both.contains("but its own plan section has been filled in (9001-x/plan.md)")
            && both.contains(
                "; and T01's section carries no current CLEAR verdict - make decide F=9001 T=T01"
            )
    );
    let refused = tick(&ask(&root, &d, "T05", "n"), false, true);
    assert_eq!(refused.code, 2);
    // a task no section names is asked as before: its own Approach block
    put(
        &root,
        "specs/9001-x/plan.md",
        &plan.replace("Built here: T05 - the half it absorbed\n\n", ""),
    );
    assert!(!first(&["T05"])[0].refusal.contains("built inside"));
}

/// A task built inside a host already archived to plan-done.md, with no plan.md left and no stub of its own: closed, nothing
/// removed; and a plan.md that cannot be read as text raises the tick (451 T307 part 2, the batch gate's coverage).
#[test]
fn a_task_built_inside_an_archived_host_closes_and_an_unreadable_plan_raises() {
    let dir = repo("built-inside-archived");
    let root = root_of(&dir);
    let d = root.join("specs/9001-x");
    let host = "## T01 the task\n\n### T01 Approach (checklist part A)\n\n1. **one** answered\n\nBuilt here: T05 - the half it absorbed\n\n";
    put(&root, "specs/9001-x/plan-done.md", host);
    put(
        &root,
        "specs/9001-x/tasks.md",
        "- [x] T01 host\n- [ ] T05 absorbed\n- [ ] T06 left open\n",
    );
    let sec = l7r_shared::plan_text::task_sections(host)
        .remove("T01")
        .unwrap();
    let digest = l7r_shared::sha256::hex(sec.as_bytes());
    let review = format!(
        "{{\"tasks\": {{\"T01\": {{\"verdict\": \"CLEAR\", \"section_sha256\": \"{digest}\"}}}}}}"
    );
    put(&root, "specs/9001-x/plan-review.json", &review);
    let ticked = tick(&ask(&root, &d, "T05", "landed in batch"), false, true);
    assert_eq!(ticked.code, 0, "{}", ticked.stderr);
    assert!(ticked
        .stdout
        .contains("tick: T05 closed built inside T01's section; recorded in"));
    put(
        &root,
        "specs/9001-x/tasks.md",
        "- [x] T01 host\n- [ ] T05 absorbed\n- [ ] T06 left open\n",
    );
    // a plan.md with the task's stub that cannot be written: the tick raises with the write's error
    let stub = l7r_gate_plan::plan::template::stubs("T05")[1].clone();
    put(&root, "specs/9001-x/plan.md", &stub);
    let mut ro = std::fs::metadata(d.join("plan.md")).unwrap().permissions();
    ro.set_readonly(true);
    std::fs::set_permissions(d.join("plan.md"), ro).unwrap();
    let raised = tick(&ask(&root, &d, "T05", "landed in batch"), false, true);
    let mut rw = std::fs::metadata(d.join("plan.md")).unwrap().permissions();
    #[expect(
        clippy::permissions_set_readonly_false,
        reason = "the fixture's file is made writable again so its directory can be removed"
    )]
    rw.set_readonly(false);
    std::fs::set_permissions(d.join("plan.md"), rw).unwrap();
    assert_ne!(raised.code, 0);
}

/// 461 T44: a stub section's two asks - the plan gate's of the task and its Approach block's - are put off at `Section::Closing` (a
/// build half's hand-in, since 461 T75 the one kind that puts them off), every other ask standing; `Section::Owed`, and the tick
/// itself, still ask both.
#[test]
fn a_section_owed_later_puts_off_only_the_plan_gate_and_the_approach_ask() {
    let dir = repo("section-later");
    let root = root_of(&dir);
    let d = root.join("specs/9001-x");
    let stub = l7r_gate_plan::plan::template::stubs("T05")[1].clone();
    put(&root, "specs/9001-x/plan.md", &stub);
    put(
        &root,
        "specs/9001-x/tasks.md",
        "- [ ] T05 a build half\n- [ ] T06 left open\n",
    );
    put(
        &root,
        "docs/approach-checklist.md",
        "## A. the approach\n\n1. one\n13. one the stub leaves unanswered\n",
    );
    let env = env_of(&[("L7R_GATE_TREE", &root.to_string_lossy())]);
    let asked = |section| {
        checks(&root, &d, "n", &words(&["T05"]), false, &env, section)
            .unwrap()
            .remove(0)
    };
    let owed = asked(Section::Owed).refusal;
    let unreviewed = owed.contains("plan decisions have no current CLEAR review");
    let approach = owed.contains("T05's Approach block leaves part A item(s) 13 unanswered");
    assert!(unreviewed && approach, "{owed}");
    let later = asked(Section::Closing);
    assert_eq!((later.tick.as_str(), later.refusal.as_str()), ("", ""));
    // the tick owes it whatever: its ask is Owed
    let mut a = ask(&root, &d, "T05", "n");
    a.escaped = None;
    assert!(tick(&a, false, true)
        .stderr
        .contains("plan decisions have no current CLEAR review"));
    // ...and another ask still stands at Closing: the task's line already ticked
    put(
        &root,
        "specs/9001-x/tasks.md",
        "- [x] T05 a build half\n- [ ] T06 left open\n",
    );
    assert!(asked(Section::Closing).tick.contains("already ticked"));
}
