//! `l7r-gate set-down` (feature 449 T135, from `set-down.py`): the reason, the one directory, the part B the arbiter has not ruled on,
//! the usage cap, the escape, the row written and what the Python raised.

use std::path::Path;

use l7r_gate_core::ci::fixtures::{put, scratch};
use l7r_shared::tempdir::TempDir;

use super::{cli, cli_with, get, git_dir, truthy};
use crate::tests::{env_of, repo, root_of};

fn words(a: &[&str]) -> Vec<String> {
    a.iter().map(|s| (*s).to_owned()).collect()
}

fn down(root: &Path, env: &[(&str, &str)]) -> crate::Reply {
    let mut pairs = vec![("SET_DOWN_WHY", "the reason given")];
    pairs.extend_from_slice(env);
    cli_with(&words(&["9001"]), root, &env_of(&pairs))
}

#[test]
fn a_set_down_is_recorded_once_its_reason_and_directory_hold() {
    let dir = repo("set-down");
    let root = root_of(&dir);
    let said = cli_with(
        &words(&["9001"]),
        &root,
        &env_of(&[("SET_DOWN_WHY", " waiting  on caf\u{e9} ")]),
    );
    assert_eq!(said.code, 0, "{}", said.stderr);
    assert_eq!(said.stdout, "set-down: 9001-x set down (waiting  on caf\u{e9}); a turn may end with its tasks open until the next make task-start\n");
    let rows = std::fs::read_to_string(root.join(".git/set-downs.jsonl")).unwrap();
    assert!(rows.starts_with(
        "{\"feature\": \"9001-x\", \"why\": \"waiting  on caf\\u00e9\", \"utc\": \"20"
    ));
    for (args, why) in [
        (&["9001"][..], "one"),
        (&[][..], "two words"),
        (&["9001", "x"][..], "two words"),
    ] {
        assert_eq!(
            cli_with(&words(args), &root, &env_of(&[("SET_DOWN_WHY", why)])).code,
            2
        );
    }
    put(&root, "specs/9002-a/x", "");
    put(&root, "specs/9002-b/x", "");
    put(&root, "specs/9003-file", "");
    for f in ["9002", "9003", "99"] {
        let r = cli_with(
            &words(&[f]),
            &root,
            &env_of(&[("SET_DOWN_WHY", "two words")]),
        );
        assert_eq!(
            (r.code, r.stderr.as_str()),
            (
                2,
                format!("set-down: no single specs/{f}* directory\n").as_str()
            )
        );
    }
    assert_eq!(
        cli_with(
            &words(&["/abs"]),
            &root,
            &env_of(&[("SET_DOWN_WHY", "two words")])
        )
        .code,
        1
    );
    let bare = scratch("set-down-bare");
    assert_eq!(
        cli_with(
            &words(&["9001"]),
            &bare,
            &env_of(&[("SET_DOWN_WHY", "two words")])
        )
        .code,
        1
    );
    // the set-downs file a directory: its append raised
    std::fs::remove_file(root.join(".git/set-downs.jsonl")).unwrap();
    std::fs::create_dir(root.join(".git/set-downs.jsonl")).unwrap();
    assert_eq!(down(&root, &[]).code, 1);
    assert_eq!(cli(&words(&[]), &root).code, 2);
    assert_eq!(
        git_dir(Path::new("/nonexistent/x")),
        Path::new("/nonexistent/x/.git")
    );
}

#[test]
fn an_owed_part_b_holds_the_set_down_until_the_arbiter_rules() {
    let dir = repo("set-down-owed");
    let root = root_of(&dir);
    let owed = root.join(".git/approach-owed.json");
    std::fs::write(
        &owed,
        r#"[{"feature": "9001-x", "task": "T02", "trigger": "older", "part": "", "utc": "2026-10-20T00:00:00Z"},
            {"feature": "9001-x", "task": "T01", "trigger": "cohort@x", "part": "B", "utc": "2026-10-21T19:28:05Z"},
            {"feature": "9001-x", "trigger": "no task named"},
            {"feature": "9001-x", "task": "T02", "trigger": "same time", "utc": "2026-10-21T19:28:05Z"},
            {"feature": "9001-x", "task": "T03", "part": "A", "utc": "2026-10-22T00:00:00Z"},
            {"feature": "9001-x", "task": "T09", "utc": "2026-10-23T00:00:00Z"},
            {"feature": "other", "task": "T01"}, "a string"]"#,
    )
    .unwrap();
    let refused = down(&root, &[]);
    assert_eq!(refused.code, 2);
    assert!(refused
        .stderr
        .starts_with("set-down: refused - cohort@x at 2026-10-21T19:28:05Z owes T01 a part B"));
    assert!(refused
        .stderr
        .contains("make arbiter-ask SUBJECT=set-down-T01"));
    assert_eq!(down(&root, &[("SET_DOWN_OK", "the cap wind-down")]).code, 0);
    let arbiter = root.join("specs/9001-x/arbiter.jsonl");
    std::fs::write(&arbiter, "{\"utc\": \"2026-10-21T19:00:00Z\"}\nnot json\n").unwrap();
    assert_eq!(down(&root, &[]).code, 2);
    std::fs::write(&arbiter, "{\"utc\": \"2026-10-21T19:40:00Z\"}\n").unwrap();
    assert_eq!(down(&root, &[]).code, 0);
    std::fs::write(&arbiter, "{\"utc\": \"2026-10-21T19:40:00Z\"}\n[1]\n").unwrap();
    assert!(down(&root, &[])
        .stderr
        .contains("AttributeError: 'list' object"));
    std::fs::remove_file(&arbiter).unwrap();
    // what reads as nothing owed, and what raised
    for text in ["{\"a\": 1}", "\"text\"", "not json"] {
        std::fs::write(&owed, text).unwrap();
        assert_eq!(down(&root, &[]).code, 0, "{text}");
    }
    std::fs::write(&owed, [0xff]).unwrap();
    assert_eq!(down(&root, &[]).code, 0);
    std::fs::write(&owed, "3").unwrap();
    assert!(down(&root, &[])
        .stderr
        .contains("TypeError: 'int' object is not iterable"));
    std::fs::write(&owed, "[{\"feature\": \"9001-x\", \"task\": null}]").unwrap();
    std::fs::write(root.join("specs/9001-x/tasks.md"), "- [ ] None here\n").unwrap();
    assert!(down(&root, &[])
        .stderr
        .contains("refused - None at None owes None"));
    std::fs::write(root.join("specs/9001-x/tasks.md"), [0xff]).unwrap();
    assert_eq!(down(&root, &[]).code, 1);
    std::fs::remove_file(root.join("specs/9001-x/tasks.md")).unwrap();
    assert_eq!(down(&root, &[]).code, 0);
}

/// A repository and a usage-cap directory, the session's words naming it: what the cap's tests share (feature 449 T167: one test of
/// them took over FR-008's tenth of a second, each `set-down` asking git three times, so it is three tests, each its own repository).
fn capped(tag: &str) -> (TempDir, std::path::PathBuf, TempDir) {
    let dir = repo(tag);
    let root = root_of(&dir);
    let cap = scratch(&format!("{tag}-dir"));
    (dir, root, cap)
}

#[test]
fn under_the_usage_cap_the_set_down_waits_on_a_set_down_ruling() {
    let (_dir, root, cap) = capped("set-down-cap");
    let cap_s = cap.to_string_lossy().into_owned();
    let session = [
        ("CLAUDE_CODE_SESSION_ID", "s/1"),
        ("USAGE_CAP_DIR", cap_s.as_str()),
    ];
    let put_cap = |name: &str, text: &str| std::fs::write(cap.join(name), text).unwrap();
    // no reading: nothing holds it
    assert_eq!(down(&root, &session).code, 0);
    put_cap("budget-s_1.json", "{\"cap\": 80.0}");
    put_cap("latest-s_1.json", "{\"seven_day\": 69}");
    let refused = down(&root, &session);
    assert_eq!(refused.code, 2);
    assert!(
        refused
            .stderr
            .contains("the weekly cap is 80% and the 7-day figure is 69%")
            && refused.stderr.contains("SUBJECT=set-down-9001")
    );
    let starts = root.join(".git/task-starts.jsonl");
    std::fs::write(&starts, "{\"feature\": \"9001-x\", \"utc\": \"2026-10-19T00:00:00Z\"}\n{\"feature\": \"other\", \"utc\": \"2027\"}\nnot json\n").unwrap();
    let arbiter = root.join("specs/9001-x/arbiter.jsonl");
    std::fs::write(
        &arbiter,
        "{\"trigger\": \"ask:set-down-9001\", \"utc\": \"2026-10-18T00:00:00Z\"}\nskip\n",
    )
    .unwrap();
    assert_eq!(down(&root, &session).code, 2);
    // a later row of an earlier time, undone (`make task-unstart`, 451 T359), is no start: the start of the 19th is still the last
    let undone = "{\"feature\": \"9001-x\", \"task\": \"T02\", \"utc\": \"2026-10-17T00:00:00Z\"}\n{\"unstart\": {\"feature\": \"9001-x\", \"task\": \"T02\"}, \"tree\": \"/t\", \"utc\": \"u\"}\n";
    let before = std::fs::read_to_string(&starts).unwrap();
    std::fs::write(&starts, format!("{before}{undone}")).unwrap();
    assert_eq!(down(&root, &session).code, 2);
    std::fs::write(&arbiter, "{\"trigger\": \"ask:other\", \"utc\": \"2026-10-20T00:00:00Z\"}\n{\"trigger\": \"ask:set-down-9001\", \"utc\": \"2026-10-20T00:00:00Z\"}\n[1]\n").unwrap();
    assert_eq!(down(&root, &session).code, 0);
    std::fs::write(&arbiter, "[1]\n").unwrap();
    assert_eq!(down(&root, &session).code, 1);
    std::fs::remove_file(&arbiter).unwrap();
    std::fs::write(&starts, "[1]\n").unwrap();
    assert_eq!(down(&root, &session).code, 1);
}

/// The cap's second part (feature 449 T167): at the cap; past the week; the account's soft cap where no goal is armed, 90 where none.
#[test]
fn at_the_cap_or_past_its_week_nothing_holds_and_the_account_s_cap_stands_in() {
    let (_dir, root, cap) = capped("set-down-cap-at");
    let cap_s = cap.to_string_lossy().into_owned();
    let session = [
        ("CLAUDE_CODE_SESSION_ID", "s/1"),
        ("USAGE_CAP_DIR", cap_s.as_str()),
    ];
    let put_cap = |name: &str, text: &str| std::fs::write(cap.join(name), text).unwrap();
    put_cap("budget-s_1.json", "{\"cap\": 80.0}");
    put_cap("latest-s_1.json", "{\"seven_day\": 80}");
    assert_eq!(down(&root, &session).code, 0);
    put_cap(
        "latest-s_1.json",
        "{\"seven_day\": 69, \"seven_day_resets_at\": 1}",
    );
    assert_eq!(down(&root, &session).code, 0);
    std::fs::remove_file(cap.join("budget-s_1.json")).unwrap();
    put_cap(
        "latest-s_1.json",
        "{\"seven_day\": 76.5, \"account\": {\"uuid\": \"u-1\"}}",
    );
    assert!(down(&root, &session)
        .stderr
        .contains("the weekly cap is 90% and the 7-day figure is 76.5%"));
    put_cap("caps.json", "{\"u-1\": {\"cap\": 70}}");
    assert_eq!(down(&root, &session).code, 0);
    put_cap("caps.json", "{\"u-1\": \"not a dict\"}");
    assert_eq!(down(&root, &session).code, 1);
}

/// The cap's last part (feature 449 T167): a cap file that is no table, a figure that is no number, and no session at all.
#[test]
fn a_cap_or_a_figure_of_the_wrong_kind_and_no_session_read_as_python_read_them() {
    let (_dir, root, cap) = capped("set-down-cap-kinds");
    let cap_s = cap.to_string_lossy().into_owned();
    let session = [
        ("CLAUDE_CODE_SESSION_ID", "s/1"),
        ("USAGE_CAP_DIR", cap_s.as_str()),
    ];
    let put_cap = |name: &str, text: &str| std::fs::write(cap.join(name), text).unwrap();
    put_cap("caps.json", "[1]");
    put_cap(
        "latest-s_1.json",
        "{\"seven_day\": 50, \"account\": {\"uuid\": \"u-1\"}}",
    );
    assert!(down(&root, &session)
        .stderr
        .contains("the weekly cap is 90%"));
    put_cap(
        "latest-s_1.json",
        "{\"seven_day\": true, \"account\": \"text\"}",
    );
    assert_eq!(down(&root, &session).code, 1);
    put_cap("latest-s_1.json", "{\"seven_day\": \"69\"}");
    assert_eq!(down(&root, &session).code, 0);
    // no session: nothing read; the cap's directory from the home
    assert_eq!(down(&root, &[("HOME", "/nonexistent")]).code, 0);
    assert_eq!(
        down(
            &root,
            &[("CLAUDE_CODE_SESSION_ID", "s"), ("HOME", "/nonexistent")]
        )
        .code,
        0
    );
}

#[test]
fn python_s_truth_and_get() {
    use serde_json::json;
    let kinds: Vec<&str> = [
        json!(null),
        json!(true),
        json!(1.5),
        json!(1),
        json!("s"),
        json!([]),
        json!({}),
    ]
    .iter()
    .map(super::kind)
    .collect();
    assert_eq!(
        kinds,
        ["NoneType", "bool", "float", "int", "str", "list", "dict"]
    );
    let truths: Vec<bool> = [
        json!(null),
        json!(true),
        json!(0),
        json!(0.5),
        json!(""),
        json!([1]),
        json!({}),
    ]
    .iter()
    .map(truthy)
    .collect();
    assert_eq!(truths, [false, true, false, true, false, true, false]);
    assert_eq!(get(None, "k"), Ok(None));
    assert_eq!(get(Some(&json!({"k": 1})), "k"), Ok(Some(&json!(1))));
    assert_eq!(get(Some(&json!(0)), "k"), Ok(None));
    assert!(get(Some(&json!(1.5)), "k").unwrap_err().contains("'float'"));
    assert!(get(Some(&json!(null)), "k").is_ok());
}

/// Feature 451 T29 (found landing T06, 2026-11-20): 449 was set down with T241 parked while `.git/active-task` still named 449 T241, so
/// every push touching 449's specs was held as that task's. A set-down clears the clone's mark when it names the set-down feature.
#[test]
fn a_set_down_clears_its_feature_s_started_task_mark_and_a_later_start_sets_it_again() {
    let dir = repo("set-down-mark");
    let root = root_of(&dir);
    let mark = root.join(".git/active-task");
    let ours = "{\"feature\": \"9001-x\", \"task\": \"T02\"}\n";
    // a refused set-down keeps the mark
    std::fs::write(&mark, ours).unwrap();
    let refused = cli_with(
        &words(&["9001"]),
        &root,
        &env_of(&[("SET_DOWN_WHY", "one")]),
    );
    assert_eq!(refused.code, 2);
    assert!(mark.exists());
    // another feature's mark is left as it stands
    put(&root, "specs/9002-y/spec.md", "**Status**: In progress\n");
    let theirs = "{\"feature\": \"9002-y\", \"task\": \"T05\"}\n";
    std::fs::write(&mark, theirs).unwrap();
    assert_eq!(down(&root, &[]).code, 0);
    assert_eq!(std::fs::read_to_string(&mark).unwrap(), theirs);
    // a mark that cannot be read, or names no feature, fails nothing and stays
    for text in [&b"not json"[..], &[0xff][..], &b"[1]"[..]] {
        std::fs::write(&mark, text).unwrap();
        assert_eq!(down(&root, &[]).code, 0);
        assert_eq!(std::fs::read(&mark).unwrap(), text);
    }
    // the set-down feature's own: cleared, and said so
    std::fs::write(&mark, ours).unwrap();
    let said = down(&root, &[]);
    assert_eq!(said.code, 0, "{}", said.stderr);
    assert!(!mark.exists());
    assert!(
        said.stdout.contains("its started-task mark (T02) cleared"),
        "{}",
        said.stdout
    );
    // a mark of the feature naming no task: cleared, the task read as the Python's `str(None)`
    std::fs::write(&mark, "{\"feature\": \"9001-x\"}\n").unwrap();
    assert!(down(&root, &[])
        .stdout
        .contains("its started-task mark (None) cleared"));
    assert!(!mark.exists());
    // no mark at all: nothing to clear, nothing said of one
    assert!(!down(&root, &[]).stdout.contains("mark"));
    // a later task-start of the feature sets it again
    let env = env_of(&[("L7R_GATE_TREE", &root.to_string_lossy())]);
    assert_eq!(
        crate::task_start::cli_with(&words(&["9001", "T01"]), &root, &env).code,
        0
    );
    // ...as the task's own mark (451 T254), which a set-down of its feature in this tree clears again
    let own = root.join(".git/task-marks/9001-x/T01.json");
    assert!(std::fs::read_to_string(&own)
        .unwrap()
        .starts_with("{\"feature\": \"9001-x\", \"task\": \"T01\", \"tree\": "));
    assert!(down(&root, &[])
        .stdout
        .contains("its started-task mark (T01) cleared"));
    assert!(!own.exists());
}

/// The stop before the parked stages (feature 449 T244): under the cap, with no ruling, a feature whose open tasks are all a parked
/// stage's is set down, naming the GM's ruling; one other open task, or the stage resumed, and the cap holds it again.
#[test]
fn only_parked_stages_left_the_stop_is_taken_under_the_cap_naming_the_ruling() {
    let (_dir, root, cap) = capped("set-down-parked");
    let cap_s = cap.to_string_lossy().into_owned();
    let session = [
        ("CLAUDE_CODE_SESSION_ID", "s/1"),
        ("USAGE_CAP_DIR", cap_s.as_str()),
    ];
    std::fs::write(cap.join("budget-s_1.json"), "{\"cap\": 80.0}").unwrap();
    std::fs::write(cap.join("latest-s_1.json"), "{\"seven_day\": 69}").unwrap();
    put(&root, "rust/parked/src/homesteads.rs", "");
    put(&root, "rust/parked/src/track.rs", "");
    let tasks = "- [x] T29 phase: seat - done\n- [ ] T30 phase: homesteads - every household\n- [ ] T32 phase: track - the road\n- [ ] GM review (make gm-reviewed F=9001)\n";
    put(&root, "specs/9001-x/tasks.md", tasks);
    let taken = down(&root, &session);
    assert_eq!(taken.code, 0, "{}", taken.stderr);
    let ok1 = taken
        .stdout
        .contains("every open task is a parked hamlet stage");
    assert!(ok1, "{}", taken.stdout);
    let ok2 = taken
        .stdout
        .contains("Stop before homesteads, and talk first");
    assert!(ok2, "{}", taken.stdout);
    let rows = std::fs::read_to_string(root.join(".git/set-downs.jsonl")).unwrap();
    assert!(rows.contains("\"ruling\""), "{rows}");
    // another open task: the cap holds the set-down as before
    put(
        &root,
        "specs/9001-x/tasks.md",
        &format!("{tasks}- [ ] T34 the port switch\n"),
    );
    let held = down(&root, &session);
    assert_eq!(held.code, 2, "{}", held.stdout);
    // a resumed stage is work again
    put(&root, "specs/9001-x/tasks.md", tasks);
    std::fs::write(
        root.join(".git/parked-resumed.jsonl"),
        "{\"stage\": \"track\"}\n",
    )
    .unwrap();
    let resumed = down(&root, &session);
    assert_eq!(resumed.code, 2, "{}", resumed.stdout);
    // no open box at all is not the stop
    put(&root, "specs/9001-x/tasks.md", "- [x] T30 done\n");
    let none = down(&root, &session);
    assert_eq!(none.code, 2, "{}", none.stdout);
}
