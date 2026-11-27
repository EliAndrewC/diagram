//! `l7r-gate task-withdraw` (451 T359): a filed task ticked `Withdrawn`, its unfilled plan stub removed, who and why in the event
//! log; every refusal together and nothing written while one stands.

use l7r_gate_core::ci::fixtures::{git, put};
use l7r_gate_plan::plan::template::{PERFORMANCE, TEMPLATE};

use super::{cli, cli_with, names, without_stub};
use crate::tests::{env_of, repo, root_of};
use crate::{now_secs, utc_text};

fn words(a: &[&str]) -> Vec<String> {
    a.iter().map(|s| (*s).to_owned()).collect()
}

fn stub(task: &str, perf: bool) -> String {
    let text = format!("{TEMPLATE}{}", if perf { PERFORMANCE } else { "" });
    format!("{}\n\n", text.replace("{T}", task).trim_end_matches('\n'))
}

const WHY: &str = "a duplicate of T01";

/// RED FIRST: two filed tasks withdrawn at once - each box ticked with its text kept and the withdrawal appended, each unfilled
/// stub (one with the performance checklist) out of plan.md and the rest of both files as they were, a line a task in the event log.
#[test]
fn a_filed_task_is_ticked_withdrawn_and_its_stub_removed() {
    let dir = repo("withdraw");
    let root = root_of(&dir);
    let events = dir.join("events");
    let env = env_of(&[("L7R_EVENTS_DIR", &events.to_string_lossy())]);
    let tasks = std::fs::read_to_string(root.join("specs/9001-x/tasks.md")).unwrap();
    let plan = std::fs::read_to_string(root.join("specs/9001-x/plan.md")).unwrap();
    let filed = format!("{tasks}- [ ] T10 a duplicate\n      research: rendering\n- [ ] T11 no defect\n- [ ] T12 no section\n");
    put(&root, "specs/9001-x/tasks.md", &filed);
    let with = format!(
        "{plan}{}{}## T99 - the close\n",
        stub("T10", false),
        stub("T11", true)
    );
    put(&root, "specs/9001-x/plan.md", &with);
    let said = cli_with(&words(&["9001", "T10,T11 T12"]), &root, WHY, &env);
    assert_eq!(said.code, 0, "{}", said.stderr);
    let date = utc_text(now_secs())[..10].to_owned();
    let now = std::fs::read_to_string(root.join("specs/9001-x/tasks.md")).unwrap();
    let want = format!("{tasks}- [x] T10 a duplicate Withdrawn {date}: {WHY}\n      research: rendering\n- [x] T11 no defect Withdrawn {date}: {WHY}\n- [x] T12 no section Withdrawn {date}: {WHY}\n");
    assert_eq!(now, want);
    // the line as written is the form its readers know (the plan gate's scope asks it)
    let withdrawn = now
        .lines()
        .filter(|l| l7r_shared::speckit::withdrawn_box(l));
    assert_eq!(withdrawn.count(), 3);
    // and the next tick's archive moves each, its line still that form in tasks-done.md
    let (_, done, moved) = l7r_shared::speckit::tasks::archive_text(&now, "", "9001-x").unwrap();
    let all = ["T10", "T11", "T12"]
        .iter()
        .all(|t| moved.iter().any(|m| m == t));
    let archived = done
        .lines()
        .filter(|l| l7r_shared::speckit::withdrawn_box(l));
    assert_eq!((all, archived.count()), (true, 3));
    let left = std::fs::read_to_string(root.join("specs/9001-x/plan.md")).unwrap();
    assert_eq!(left, format!("{plan}## T99 - the close\n"));
    let first = format!("task-withdraw: 9001-x T10 ticked `Withdrawn {date}: {WHY}` in specs/9001-x/tasks.md, its unfilled plan stub removed from specs/9001-x/plan.md\n");
    assert!(said.stdout.starts_with(&first), "{}", said.stdout);
    let third = format!(
        "task-withdraw: 9001-x T12 ticked `Withdrawn {date}: {WHY}` in specs/9001-x/tasks.md\n"
    );
    assert!(said.stdout.contains(&third), "{}", said.stdout);
    let last = "task-withdraw: changed specs/9001-x/tasks.md specs/9001-x/plan.md - nothing staged or committed; recorded in ";
    assert!(said.stdout.contains(last), "{}", said.stdout);
    let log = std::fs::read_to_string(events.join("9001-x.jsonl")).unwrap();
    let rows: Vec<serde_json::Value> = log
        .lines()
        .map(|l| serde_json::from_str(l).unwrap())
        .collect();
    assert_eq!(rows.len(), 3);
    assert_eq!(rows[1]["ev"], "TaskWithdrawn");
    assert_eq!(rows[1]["task"], "T11");
    assert_eq!(rows[1]["why"], WHY);
    assert_eq!(rows[1]["tree"].as_str(), root.to_str());
    // nothing staged or committed
    let status = crate::git(&root, &["status", "--porcelain"]).1;
    assert_eq!(
        String::from_utf8_lossy(&status),
        " M specs/9001-x/plan.md\n M specs/9001-x/tasks.md\n"
    );
    // withdrawn again: already ticked, as an archived task is
    let again = cli_with(&words(&["9001", "T10"]), &root, WHY, &env);
    assert_eq!(
        again.stderr,
        "task-withdraw: refused, nothing written (451 T359):\n  T10 is already ticked\n"
    );
    put(&root, "specs/9001-x/tasks-done.md", "- [x] T08 archived\n");
    let archived = cli_with(&words(&["9001", "T08"]), &root, WHY, &env);
    assert!(archived.stderr.contains("  T08 is already ticked\n"));
    // a task with no section, and no plan.md at all: the box alone
    std::fs::remove_file(root.join("specs/9001-x/plan.md")).unwrap();
    let alone = cli_with(&words(&["9001", "T02"]), &root, WHY, &env);
    assert_eq!(alone.code, 0, "{}", alone.stderr);
    assert!(alone
        .stdout
        .contains("task-withdraw: changed specs/9001-x/tasks.md - nothing"));
}

/// RED FIRST: each refusal, all of a run's together, and neither file touched.
#[test]
fn a_task_worked_started_or_carried_is_refused_and_nothing_is_written() {
    let dir = repo("withdraw-refused");
    let root = root_of(&dir);
    let env = env_of(&[("L7R_EVENTS_DIR", &dir.join("events").to_string_lossy())]);
    let usage = cli(&words(&["9001"]), &root, WHY);
    assert_eq!(
        (
            usage.code,
            usage.stderr.starts_with("usage: make task-withdraw F=")
        ),
        (2, true)
    );
    assert_eq!(cli_with(&words(&["9001", " , "]), &root, WHY, &env).code, 2);
    let thin = cli_with(&words(&["9001", "T01"]), &root, "dup", &env);
    assert!(thin.stderr.starts_with("task-withdraw: WHY needs a REASON"));
    let none = cli_with(&words(&["99999", "T01"]), &root, WHY, &env);
    assert!(none
        .stderr
        .starts_with("task-withdraw: no single specs/99999* directory with a tasks.md under "));
    // T01's section is filled in (the fixture's), T03 holds an open research box, T09 is ticked, T77 was never filed
    let before = std::fs::read_to_string(root.join("specs/9001-x/tasks.md")).unwrap();
    let said = cli_with(&words(&["9001", "T01 T03 T09 T77"]), &root, WHY, &env);
    assert_eq!(said.code, 2);
    let want = "task-withdraw: refused, nothing written (451 T359):\n  T01's plan section has been filled in (9001-x/plan.md): it is no withdrawal but a landing - make land F=9001 T=T01 - or empty the section back to its template first\n  T03 holds an open box under its line (a `research: physical` task's): a ticked task with one open is never archived - close it by hand\n  T09 is already ticked\n  T77 is no open task of 9001-x/tasks.md\n";
    assert_eq!(said.stderr, want);
    assert_eq!(
        std::fs::read_to_string(root.join("specs/9001-x/tasks.md")).unwrap(),
        before
    );
    // an unfilled stub with more under the task's headings is filled in; a stub alone, reviewed, carries a verdict
    put(
        &root,
        "specs/9001-x/plan.md",
        &format!("{}### T02 Notes\n\nmore\n", stub("T02", false)),
    );
    let more = cli_with(&words(&["9001", "T02"]), &root, WHY, &env);
    assert!(more
        .stderr
        .contains("T02's plan section has been filled in"));
    put(&root, "specs/9001-x/plan.md", &stub("T02", false));
    put(
        &root,
        "specs/9001-x/plan-review.json",
        "{\"tasks\": {\"T02\": {\"reviewed\": \"2026-11-26\"}}}",
    );
    let ruled = cli_with(&words(&["9001", "T02"]), &root, WHY, &env);
    assert!(ruled.stderr.contains("  T02's plan section carries a review verdict (9001-x/plan-review.json): a reviewed task is no withdrawal but a landing - make land F=9001 T=T02\n"), "{}", ruled.stderr);
    put(&root, "specs/9001-x/plan-review.json", "not json");
    // started in a tree: a mark naming it, a bundle's member among them
    let start_env = env_of(&[("L7R_GATE_TREE", &root.to_string_lossy())]);
    assert_eq!(
        crate::task_start::cli_with(&words(&["9001", "T01,T02"]), &root, &start_env).code,
        0
    );
    let started = cli_with(&words(&["9001", "T02"]), &root, WHY, &env);
    let tree = root.to_string_lossy();
    assert_eq!(started.stderr, format!("task-withdraw: refused, nothing written (451 T359):\n  T02 is started in {tree} (make task-start): unstart it there first - make -C {tree} task-unstart F=9001 T=T01\n"));
    std::fs::remove_dir_all(root.join(".git/task-marks")).unwrap();
    // 451 T437: a mark of a tree that no longer exists is no start - the refusal is the carried code's alone
    let gone = dir.join("removed-tree").to_string_lossy().into_owned();
    put(&root, ".git/task-marks/9001-x/T02.json", &format!("{{\"feature\": \"9001-x\", \"task\": \"T02\", \"tree\": \"{gone}\", \"utc\": \"2026-11-26T00:00:00Z\"}}\n"));
    // its code carried: a commit since origin/main whose head names the feature's number and the task
    put(&root, "scripts/b.py", "y = 2\n");
    git(&root, &["add", "scripts/b.py"]);
    git(&root, &["commit", "-qm", "9001 T02: the second, built"]);
    let carried = cli_with(&words(&["9001", "T02"]), &root, WHY, &env);
    assert!(carried.stderr.contains("  T02's code is carried in the clone (the commit \"9001 T02: the second, built\", since origin/main): a task with code closes by a landing - make land F=9001 T=T02\n"), "{}", carried.stderr);
    assert!(!carried.stderr.contains("is started"), "{}", carried.stderr);
    git(&root, &["push", "-q", "origin", "main"]);
    // the feature's last open boxes: the closing check is the last tick's
    put(
        &root,
        "specs/9001-x/tasks.md",
        "- [ ] T02 the second\n- [x] T09 done\n",
    );
    let last = cli_with(&words(&["9001", "T02"]), &root, WHY, &env);
    assert_eq!(last.stderr, "task-withdraw: refused, nothing written (451 T359):\n  T02 would leave 9001-x no open box: the feature's last tick runs the closing check, which a withdrawal does not - close it with make tick F=9001\n");
    // a file that cannot be read raises, and a held filing lock refuses
    std::fs::write(root.join("specs/9001-x/plan.md"), [0xff]).unwrap();
    assert_eq!(cli_with(&words(&["9001", "T02"]), &root, WHY, &env).code, 1);
    let _held =
        l7r_shared::tool::flock_within(&root.join(".git/task-add-9001-x.lock"), 1.0).unwrap();
    let at_once = env_of(&[("L7R_TASK_ADD_LOCK_WAIT", "0")]);
    let locked = cli_with(&words(&["9001", "T02"]), &root, WHY, &at_once);
    assert!(locked.stderr.contains("still holds"), "{}", locked.stderr);
}

/// RED FIRST (451 T366): a task a builder holds a pool tree for, with no start made, is refused with the release named; a tree held
/// for another feature's task of that id, and a free one, hold nothing; a hold naming no feature is any feature's.
#[test]
fn a_task_a_builder_holds_a_pool_tree_for_is_refused() {
    let dir = repo("withdraw-pooled");
    let root = root_of(&dir);
    let env = env_of(&[("L7R_EVENTS_DIR", &dir.join("events").to_string_lossy())]);
    let tree = root.to_string_lossy();
    let pool = |feature: &str, tasks: &[&str]| {
        let tree = l7r_shared::builder_pool::Tree {
            tree: root.join("pool-b1"),
            feature: feature.to_owned(),
            tasks: words(tasks),
            since: "2026-11-26T22:29:28Z".to_owned(),
        };
        l7r_shared::builder_pool::write(&root.join(".git"), &[tree]).unwrap();
    };
    pool("9001", &["T07", "T02"]);
    let held = cli_with(&words(&["9001", "T02"]), &root, WHY, &env);
    assert_eq!(held.stderr, format!("task-withdraw: refused, nothing written (451 T359):\n  T02 is held by a builder's pool tree ({tree}/pool-b1, held for 9001 T07,T02 since 2026-11-26T22:29:28Z): its builder may be working it - free the tree first: make builder-tree-release T=T02 F=9001\n"));
    for (feature, tasks) in [("9002", &["T02"][..]), ("", &[])] {
        pool(feature, tasks);
        // the command's own entry, the environment read from the process: refused for T77 alone, the pool naming nothing
        let other = cli(&words(&["9001", "T77"]), &root, WHY);
        assert_eq!(other.stderr, "task-withdraw: refused, nothing written (451 T359):\n  T77 is no open task of 9001-x/tasks.md\n");
    }
    pool("", &["T02"]);
    let bare = cli_with(&words(&["9001", "T02"]), &root, WHY, &env);
    let named = bare
        .stderr
        .contains("  T02 is held by a builder's pool tree (");
    assert!(named);
}

/// The two readings by themselves: a commit subject that names a task as its own, and a plan without a task's stub.
#[test]
fn a_subject_names_its_task_and_a_stub_is_the_template_alone() {
    assert!(names("451 T359: the two ways out", "451", "T359"));
    assert!(names("451 T299 T282: a bundle", "451", "T282"));
    assert!(!names("451 T35: another", "451", "T359"));
    assert!(!names("4510 T359: another feature", "451", "T359"));
    assert!(!names("the sampler's log, and T359 filed", "451", "T359"));
    assert!(!names("451 T1: it mentions T359 after", "451", "T359"));
    // no heading of the task, one that only mentions it among them
    let other = "### T180 (449's T351 and T359 bundles)\n\ntext\n";
    assert_eq!(without_stub(other, "T359"), Ok(None));
    // the stub at the end of the file with no blank line after, and a hand-filled section
    let bare = stub("T359", false);
    assert_eq!(
        without_stub(bare.trim_end(), "T359"),
        Ok(Some(String::new()))
    );
    assert_eq!(
        without_stub("### T358, T359 (bundle)\n\nfilled\n", "T359"),
        Err(())
    );
}
