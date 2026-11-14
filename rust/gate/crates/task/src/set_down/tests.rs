//! `l7r-gate set-down` (feature 449 T135, from `set-down.py`): the reason, the one directory, the part B the arbiter has not ruled on,
//! the usage cap, the escape, the row written and what the Python raised.

use std::path::Path;

use l7r_gate_core::ci::fixtures::{put, scratch};

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

#[test]
fn under_the_usage_cap_the_set_down_waits_on_a_set_down_ruling() {
    let dir = repo("set-down-cap");
    let root = root_of(&dir);
    let cap = scratch("set-down-cap-dir");
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
    std::fs::write(&arbiter, "{\"trigger\": \"ask:other\", \"utc\": \"2026-10-20T00:00:00Z\"}\n{\"trigger\": \"ask:set-down-9001\", \"utc\": \"2026-10-20T00:00:00Z\"}\n[1]\n").unwrap();
    assert_eq!(down(&root, &session).code, 0);
    std::fs::write(&arbiter, "[1]\n").unwrap();
    assert_eq!(down(&root, &session).code, 1);
    std::fs::remove_file(&arbiter).unwrap();
    std::fs::write(&starts, "[1]\n").unwrap();
    assert_eq!(down(&root, &session).code, 1);
    std::fs::remove_file(&starts).unwrap();
    // at the cap; past the week; the account's soft cap where no goal is armed, 90 where none
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
