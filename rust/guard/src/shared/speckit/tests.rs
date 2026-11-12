//! The state rule, the tags and the holding box over scratch feature directories (feature 449 T118); `scratchpad/t83s2/` compares the
//! command with the Python it replaced.

use std::path::{Path, PathBuf};

use serde_json::json;

use super::*;
use crate::shared::tempdir::TempDir;
use crate::shared::tool::ask;

fn put(root: &Path, rel: &str, text: &str) {
    let path = root.join(rel);
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

/// A scratch git repository, its path canonical.
fn repo(tag: &str) -> (TempDir, PathBuf) {
    let d = TempDir::new(&format!("guard-speckit-{tag}"));
    let at = d.canonicalize().unwrap();
    assert!(ask(&at, "git", &["init", "-q"], "").ok());
    (d, at)
}

fn vocab() -> Vocabulary {
    Vocabulary {
        stage: vec![
            ("hamlet".to_owned(), Some("now".to_owned())),
            ("village".to_owned(), Some("village".to_owned())),
            ("town".to_owned(), Some("town".to_owned())),
            ("odd".to_owned(), None),
        ],
        aliases: vec![(
            "every tier".to_owned(),
            vec!["town".to_owned(), "village".to_owned(), "nope".to_owned()],
        )],
        placeholders: vec![("village".to_owned(), json!("380-v"))],
    }
}

#[test]
fn a_path_reads_as_python_reads_it() {
    assert_eq!(py_path(""), PathBuf::from("."));
    assert_eq!(py_path("./a//b/./c/"), PathBuf::from("a/b/c"));
    assert_eq!(py_parent(Path::new("a/b")), PathBuf::from("a"));
    assert_eq!(py_parent(Path::new("a")), PathBuf::from("."));
    assert_eq!(py_parent(Path::new("/")), PathBuf::from("/"));
    assert_eq!(py_name(Path::new("specs/9-x")), "9-x");
    assert_eq!(py_name(Path::new("/")), "");
}

#[test]
fn lines_split_where_python_splits_them() {
    assert_eq!(
        splitlines("a\r\nb\rc\x0bd\u{2028}e\n"),
        ["a", "b", "c", "d", "e"]
    );
    assert_eq!(splitlines("a\n\nb"), ["a", "", "b"]);
    assert!(splitlines("").is_empty());
}

#[test]
fn a_file_is_read_with_its_line_ends_translated_and_bad_bytes_replaced() {
    let (_d, at) = repo("read");
    std::fs::write(at.join("f"), b"a\r\nb\rc\xff").unwrap();
    assert_eq!(read_text(&at.join("f")).unwrap(), "a\nb\nc\u{fffd}");
    assert!(read_text(&at.join("missing")).is_err());
    assert_eq!(text_if_file(&at.join("missing")).unwrap(), "");
}

#[test]
fn the_vocabulary_is_read_in_the_files_order() {
    let (_d, at) = repo("vocab");
    assert_eq!(vocabulary(&at).unwrap(), Vocabulary::default());
    put(
        &at,
        AFFECTS,
        r#"{"tags": {"b": {"stage": "now"}, "a": {"stage": 3}}, "aliases": {"x": ["a", 1], "y": "ab"}, "placeholders": {"village": "380-v"}}"#,
    );
    let v = vocabulary(&at).unwrap();
    assert_eq!(
        v.stage,
        [
            ("b".to_owned(), Some("now".to_owned())),
            ("a".to_owned(), None)
        ]
    );
    assert_eq!(v.aliases[0].1, ["a", "1"]);
    assert_eq!(v.aliases[1].1, ["a", "b"]);
    assert_eq!(v.placeholder("village"), Some(&json!("380-v")));
    assert_eq!(v.placeholder("town"), None);
    for (bad, says) in [
        ("{\"aliases\": {\"x\": 3}}", "TypeError"),
        ("{\"tags\": {\"a\": {}}}", "KeyError"),
        ("[]", "AttributeError"),
        ("not json", "JSONDecodeError"),
    ] {
        put(&at, AFFECTS, bad);
        assert!(vocabulary(&at).unwrap_err().contains(says), "{bad}");
    }
    std::fs::write(at.join(AFFECTS), b"\xff").unwrap();
    assert!(vocabulary(&at).unwrap_err().contains("UnicodeDecodeError"));
    std::fs::remove_file(at.join(AFFECTS)).unwrap();
    std::fs::create_dir_all(at.join(AFFECTS)).unwrap();
    assert_eq!(vocabulary(&at).unwrap(), Vocabulary::default());
}

#[test]
fn an_unreadable_vocabulary_raises() {
    let (_d, at) = repo("vocab-unreadable");
    put(&at, AFFECTS, "{}");
    std::os::unix::fs::symlink(at.join("nowhere"), at.join("dangling")).unwrap();
    std::fs::remove_file(at.join(AFFECTS)).unwrap();
    std::os::unix::fs::symlink("/proc/self/mem", at.join(AFFECTS)).unwrap();
    assert!(vocabulary(&at).is_err());
}

#[test]
fn the_tags_expand_aliases_once_each_and_name_the_unknown() {
    let v = vocab();
    let (known, unknown) = affects("# T\n\n**Affects**: Hamlet, every tier, town, , NOPE\n", &v);
    assert_eq!(known, ["hamlet", "town", "village"]);
    assert_eq!(unknown, ["nope"]);
    assert_eq!(affects("**Affects:** odd\n", &v).0, ["odd"]);
    assert_eq!(affects("no line\n", &v), (Vec::new(), Vec::new()));
    assert_eq!(derived_stage(&known, &v), "now");
    assert_eq!(
        derived_stage(&["town".to_owned(), "village".to_owned()], &v),
        "village"
    );
    assert_eq!(derived_stage(&["odd".to_owned()], &v), "");
}

#[test]
fn an_owed_at_line_names_a_stage_or_nothing() {
    assert_eq!(owed_at("**Owed at**: Town - the GM said so\n"), "town");
    assert_eq!(owed_at("**Owed at:** village, then\n"), "village");
    assert_eq!(owed_at("**Owed at**: capital\n"), "capital");
    assert_eq!(owed_at("**Owed at**: someday\n"), "");
    assert_eq!(owed_at("nothing\n"), "");
}

#[test]
fn the_state_rule_reads_the_status_line_and_the_column_zero_boxes() {
    let (_d, at) = repo("state");
    let d = at.join("specs/9-x");
    std::fs::create_dir_all(&d).unwrap();
    assert_eq!(state(&d).unwrap(), "filed");
    put(&d, "tasks.md", "- [ ] T9001 a\n  - [x] nested\n");
    assert_eq!(state(&d).unwrap(), "planned");
    put(
        &d,
        "tasks.md",
        "- [X] T9001 a\n- [ ] T9002 b\n- [ ] T9003 c\n",
    );
    assert_eq!(state(&d).unwrap(), "in progress");
    put(&d, "tasks.md", "- [x] T9001 a\n");
    assert_eq!(state(&d).unwrap(), "closed");
    put(&d, "tasks.md", "- [x] T9001 a\n- [ ] GM review\n");
    assert_eq!(state(&d).unwrap(), "in progress");
    put(&d, "gm-review.jsonl", "{\"reviewed\": 1}\n\n{\"row\": 1}\n");
    let f = feature(&d, &vocab()).unwrap();
    assert_eq!(
        (f.state.as_str(), f.why.as_str()),
        ("done - GM review pending", "make gm-reviewed F=9")
    );
    assert_eq!(
        (f.ticked, f.total, f.no_spec, f.title.as_str()),
        (1, 2, true, "x")
    );
    put(
        &d,
        "spec.md",
        "# Feature 9: The Title\n\n**Status**: Superseded by 10\n**Affects**: village\n",
    );
    let f = feature(&d, &vocab()).unwrap();
    assert_eq!(
        (f.state.as_str(), f.why.as_str()),
        ("closed", "Superseded by 10")
    );
    assert_eq!(
        (f.title.as_str(), f.owed.as_str()),
        ("The Title", "village")
    );
    assert!(closed_by_status(&d).unwrap());
    put(
        &d,
        "spec.md",
        "# T\n**Status:** Implemented\n**Owed at**: town\n**Affects**: hamlet\n",
    );
    assert!(!closed_by_status(&d).unwrap());
    assert_eq!(feature(&d, &vocab()).unwrap().owed, "town");
    assert!(!closed_by_status(&at.join("specs/none")).unwrap());
    std::fs::remove_file(d.join("spec.md")).unwrap();
    std::os::unix::fs::symlink("/proc/self/mem", d.join("spec.md")).unwrap();
    assert!(closed_by_status(&d).is_err());
    assert!(state(&d).is_err());
    assert!(state_given_vocabulary(&d).is_err());
    assert!(feature(&d, &vocab()).is_err());
}

#[test]
fn a_json_value_reads_as_python_prints_it() {
    for (v, text, truthy) in [
        (json!(null), "None", false),
        (json!(true), "True", true),
        (json!(false), "False", false),
        (json!("T1"), "T1", true),
        (json!(""), "", false),
        (json!(5), "5", true),
        (json!(0.0), "0.0", false),
        (json!([1]), "[1]", true),
        (json!({}), "{}", false),
    ] {
        assert_eq!(py_str(&v), (text.to_owned(), truthy), "{v}");
    }
}

#[test]
fn the_active_task_is_the_marks_when_it_names_this_feature() {
    let (_d, at) = repo("active");
    let d = at.join("specs/9-x");
    std::fs::create_dir_all(&d).unwrap();
    assert_eq!(active_task(&d).unwrap(), "");
    assert_eq!(active_task(Path::new("/no/such/dir")).unwrap(), "");
    for (mark, want) in [
        (r#"{"feature": "9-x", "task": "T9001"}"#, "T9001"),
        (r#"{"feature": "9-x", "task": 7}"#, "7"),
        (r#"{"feature": "9-x", "task": 0}"#, ""),
        (r#"{"feature": "8-y", "task": "T9001"}"#, ""),
        (r#"{"feature": "9-x"}"#, ""),
        ("not json", ""),
    ] {
        put(&at, ".git/active-task", mark);
        assert_eq!(active_task(&d).unwrap(), want, "{mark}");
    }
    std::fs::write(at.join(".git/active-task"), b"\xff").unwrap();
    assert_eq!(active_task(&d).unwrap(), "");
    put(&at, ".git/active-task", "[1]");
    assert!(active_task(&d).is_err());
    std::fs::remove_file(at.join(".git/active-task")).unwrap();
    std::os::unix::fs::symlink("/proc/self/mem", at.join(".git/active-task")).unwrap();
    assert!(active_task(&d).is_err());
}

#[test]
fn only_the_active_task_holds_and_a_landing_that_ticks_it_does_not() {
    let (_d, at) = repo("holding");
    let d = at.join("specs/007-x");
    std::fs::create_dir_all(&d).unwrap();
    assert!(holding(&d).unwrap().is_empty());
    put(
        &d,
        "tasks.md",
        "- [ ] T7701 the open one\n- [x] T7702 ticked\n  some text\n  - [ ] a pass under it\n- [x] T7703 ticked\n\n  - [ ] after a blank\n- [x] T7704 last\n  - [x] done under it\n",
    );
    put(
        &at,
        ".git/active-task",
        r#"{"feature": "007-x", "task": "T7701"}"#,
    );
    assert_eq!(
        holding(&d).unwrap(),
        ["T7701 the open one  <- the active task (make task-start), open: land it with make land F=7 T=T7701"]
    );
    for (task, want) in [("T7702", 1), ("T7703", 0), ("T7704", 0), ("T7799", 0)] {
        put(
            &at,
            ".git/active-task",
            &format!(r#"{{"feature": "007-x", "task": "{task}"}}"#),
        );
        assert_eq!(holding(&d).unwrap().len(), want, "{task}");
    }
    put(
        &at,
        ".git/active-task",
        r#"{"feature": "007-x", "task": "T7702"}"#,
    );
    assert_eq!(
        holding(&d).unwrap(),
        ["a pass under it  <- open under the active task T7702: land it with make land F=7 T=T7702"]
    );
    std::env::set_var("L7R_LAND_TICKS", "T7700 T7702");
    assert!(holding(&d).unwrap().is_empty());
    std::env::remove_var("L7R_LAND_TICKS");
    let e = at.join("specs/000-y");
    put(&e, "tasks.md", "- [ ] T7705 x\n");
    put(
        &at,
        ".git/active-task",
        r#"{"feature": "000-y", "task": "T7705"}"#,
    );
    assert!(holding(&e).unwrap()[0].ends_with("F=0 T=T7705"));
    let n = at.join("specs/draft-y");
    put(&n, "tasks.md", "- [ ] T7706 x\n");
    put(
        &at,
        ".git/active-task",
        r#"{"feature": "draft-y", "task": "T7706"}"#,
    );
    assert!(holding(&n).unwrap()[0].ends_with("F=draft-y T=T7706"));
}

#[test]
fn every_feature_directory_is_read_in_name_order() {
    let (_d, at) = repo("features");
    assert!(features(&at.join("specs")).unwrap().is_empty());
    put(&at, "specs/2-b/spec.md", "# B\n");
    put(&at, "specs/1-a/tasks.md", "- [ ] T1 x\n");
    put(&at, "specs/README", "a file\n");
    let names: Vec<String> = features(&at.join("specs"))
        .unwrap()
        .into_iter()
        .map(|f| f.name)
        .collect();
    assert_eq!(names, ["1-a", "2-b"]);
    assert_eq!(feature_dirs(&at.join("specs")).len(), 2);
    assert_eq!(gm_rows(&at.join("specs/1-a")).unwrap(), 0);
    assert_eq!(number_of("12-ab-c"), "12");
}

#[test]
fn a_broken_vocabulary_above_the_directory_fails_its_state() {
    // the Python's `feature(d)` read `vocabulary(d.parent.parent)` first and raised on a broken one (feature 449 T118 D7, FR-002)
    let (_d, at) = repo("state-vocab");
    let d = at.join("specs/9-x");
    put(&d, "tasks.md", "- [x] T9001 a\n");
    assert_eq!(state(&d).unwrap(), "closed");
    put(&at, AFFECTS, "not json");
    assert!(state(&d).unwrap_err().contains("JSONDecodeError"));
    assert_eq!(state_given_vocabulary(&d).unwrap(), "closed");
}
