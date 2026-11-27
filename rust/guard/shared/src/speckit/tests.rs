//! The state rule, the tags and the holding box over scratch feature directories (feature 449 T118); `scratchpad/t83s2/` compares the
//! command with the Python it replaced.

use std::path::{Path, PathBuf};

use serde_json::json;

use super::*;
use crate::tempdir::TempDir;
use crate::tool::ask;

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

/// `git <args>` in `at`, its stdout; the test fails where git does.
fn git(at: &Path, args: &[&str]) -> String {
    let said = ask(at, "git", args, "");
    assert!(said.ok(), "git {args:?}: {}", said.err);
    said.out
}

/// A task's edit of `tree`/`rel`, half a second after `at`'s HEAD was committed: what the event log writer files for an Edit.
fn edited(at: &Path, tree: &Path, feature: &str, task: &str, rel: &str) {
    let secs: u64 = git(at, &["log", "-1", "--format=%ct"])
        .trim()
        .parse()
        .unwrap();
    let (y, m, d, h, mi, sec) = crate::log::civil(secs);
    let line = json!({"ev": "PostToolUse", "cat": "edit", "task": task,
        "t": format!("{y:04}-{m:02}-{d:02}T{h:02}:{mi:02}:{sec:02}.500Z"), "path": tree.join(rel).to_string_lossy()});
    let log = at.join(format!(".git/l7r-events/{feature}.jsonl"));
    std::fs::create_dir_all(log.parent().unwrap()).unwrap();
    let mut text = std::fs::read_to_string(&log).unwrap_or_default();
    text.push_str(&serde_json::to_string(&line).unwrap());
    text.push('\n');
    std::fs::write(log, text).unwrap();
}

/// A mark as `make task-start` writes it, in `tree`.
fn mark(at: &Path, tree: &Path, feature: &str, task: &str, utc: &str) {
    marks::write(
        &at.join(".git"),
        tree,
        json!({"feature": feature, "task": task}),
        utc,
    )
    .unwrap();
}

/// A commit of what is staged in `at`, by a fixed author.
fn commit_all(at: &Path, message: &str) {
    git(
        at,
        &[
            "-c",
            "user.email=t@t",
            "-c",
            "user.name=t",
            "commit",
            "-qm",
            message,
        ],
    );
}

/// RED FIRST (feature 451 T254, its plan review's round 2): this tree's STARTED task holds its push whatever the delta carries, another
/// worktree's only by the files of its the push carries, and a landing that ticks a task, or rules its tasks ready (451 T101), is not
/// held by it.
#[test]
fn this_trees_started_task_holds_and_another_trees_only_by_the_edits_the_push_carries() {
    let (_d, at) = repo("holding");
    let d = at.join("specs/007-x");
    std::fs::create_dir_all(&d).unwrap();
    assert!(holding(&d).unwrap().is_empty());
    put(
        &d,
        "tasks.md",
        "- [ ] T7701 the open one\n- [x] T7702 ticked\n  some text\n  - [ ] a pass under it\n- [x] T7703 ticked\n\n  - [ ] after a blank\n- [x] T7704 last\n  - [x] done under it\n- [ ] T7707 the other tree's\n",
    );
    git(&at, &["add", "-A"]);
    commit_all(&at, "base");
    git(&at, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
    // THIS TREE'S started task holds its push though the delta holds none of its files (feature 405 T32's D4, kept by 451 T254's
    // plan review, round 2)
    mark(&at, &at, "007-x", "T7701", "2026-11-25T10:00:00Z");
    assert_eq!(active_task(&d).unwrap(), "T7701");
    let own = ["T7701 the open one  <- the active task (make task-start), open: land it with make land F=7 T=T7701"];
    assert_eq!(holding(&d).unwrap(), own);
    put(&at, "a.rs", "fn a() {}\n");
    git(&at, &["add", "-A"]);
    commit_all(&at, "its work");
    assert_eq!(holding(&d).unwrap(), own);
    // ...and with its edit of a file the delta carries, held the same way
    edited(&at, &at, "007-x", "T7701", "a.rs");
    assert_eq!(holding(&d).unwrap(), own);
    crate::env::set("L7R_LAND_TICKS", "T7700 T7701");
    crate::env::set("SPECIFY_FEATURE", "007-x");
    assert!(holding(&d).unwrap().is_empty());
    crate::env::unset("SPECIFY_FEATURE");
    crate::env::unset("L7R_LAND_TICKS");
    // 451 T101: a landing of another task is held by it, unless the landing ruled every task it ticks ready beside it
    assert_eq!(holding_with(&d, "T7703").unwrap().len(), 1);
    crate::env::set("L7R_LAND_READY", "T7703");
    // 451 T432: the ruling exempts the LANDED feature's hold alone (`SPECIFY_FEATURE`, which make land exports beside it): another
    // feature's ready landing, or one naming no feature, is held by this one's started task
    crate::env::set("SPECIFY_FEATURE", "008-y");
    assert_eq!(holding_with(&d, "T7703").unwrap().len(), 1);
    crate::env::unset("SPECIFY_FEATURE");
    assert_eq!(holding_with(&d, "T7703").unwrap().len(), 1);
    crate::env::set("SPECIFY_FEATURE", "007-x");
    assert!(holding_with(&d, "T7703").unwrap().is_empty());
    assert_eq!(holding_with(&d, "T7703 T7704").unwrap().len(), 1);
    assert_eq!(holding_with(&d, "").unwrap().len(), 1);
    crate::env::unset("L7R_LAND_READY");
    crate::env::unset("SPECIFY_FEATURE");
    // a ticked task with an open box under it is still in progress; one with none, or no box, holds nothing
    for (task, want) in [("T7702", 1), ("T7703", 0), ("T7704", 0), ("T7799", 0)] {
        marks::remove(&at.join(".git"), "007-x", &["T7701".to_owned()]);
        mark(&at, &at, "007-x", task, "2026-11-25T11:00:00Z");
        edited(&at, &at, "007-x", task, "a.rs");
        assert_eq!(holding(&d).unwrap().len(), want, "{task}");
        marks::remove(&at.join(".git"), "007-x", &[task.to_owned()]);
    }
    mark(&at, &at, "007-x", "T7702", "2026-11-25T11:00:00Z");
    assert_eq!(
        holding(&d).unwrap(),
        ["a pass under it (open under T7702)  <- the active task (make task-start), open: land it with make land F=7 T=T7702"]
    );
    marks::remove(&at.join(".git"), "007", &["T7702".to_owned()]);
    // ANOTHER WORKTREE'S started task: its start moves no mark of this tree, and it holds this push only by its own files, its edit
    // lines naming its own tree's paths
    let other = at.join("other");
    git(
        &at,
        &[
            "worktree",
            "add",
            "-q",
            "--detach",
            &other.to_string_lossy(),
        ],
    );
    mark(&at, &other, "007-x", "T7707", "2026-11-25T12:00:00Z");
    assert_eq!(active_task(&other.join("specs/007-x")).unwrap(), "T7707");
    assert_eq!(active_task(&d).unwrap(), "");
    assert!(holding(&d).unwrap().is_empty());
    put(&at, "b.rs", "fn b() {}\n");
    git(&at, &["add", "b.rs"]);
    commit_all(&at, "carried over");
    edited(&at, &other, "007-x", "T7707", "b.rs");
    assert_eq!(
        holding(&d).unwrap(),
        ["T7707 the other tree's  <- started (make task-start), its edit of b.rs in this push: land it with make land F=7 T=T7707"]
    );
    // 451 T437: once that worktree is removed its mark holds nothing - nor once its path is a plain directory again, a tree of
    // this repository no more
    git(
        &at,
        &["worktree", "remove", "--force", &other.to_string_lossy()],
    );
    assert!(holding(&d).unwrap().is_empty());
    std::fs::create_dir_all(&other).unwrap();
    assert!(holding(&d).unwrap().is_empty());
    // a mark naming no tree is read as this tree's: the hold fails closed
    let bare = at.join(".git/task-marks/007-x/T7701.json");
    std::fs::write(
        &bare,
        r#"{"feature": "007-x", "task": "T7701", "utc": "2026-11-25T12:30:00Z"}"#,
    )
    .unwrap();
    assert_eq!(holding(&d).unwrap().len(), 1);
    std::fs::remove_file(bare).unwrap();
    let e = at.join("specs/000-y");
    put(&e, "tasks.md", "- [ ] T7705 x\n");
    mark(&at, &at, "000-y", "T7705", "2026-11-25T13:00:00Z");
    edited(&at, &at, "000-y", "T7705", "b.rs");
    assert!(holding(&e).unwrap()[0].ends_with("F=0 T=T7705"));
    let n = at.join("specs/draft-y");
    put(&n, "tasks.md", "- [ ] T7706 x\n");
    mark(&at, &at, "draft-y", "T7706", "2026-11-25T13:00:00Z");
    edited(&at, &at, "draft-y", "T7706", "b.rs");
    assert!(holding(&n).unwrap()[0].ends_with("F=draft-y T=T7706"));
}

/// RED FIRST (451 T479): a landing's ticks are the LANDED feature's alone (`SPECIFY_FEATURE`, which make land exports beside
/// `L7R_LAND_TICKS`), so feature 008's landing of T7708 leaves feature 007's started T7708 holding; a push naming no feature exempts none.
#[test]
fn a_landings_ticks_exempt_no_other_features_started_task_of_the_same_id() {
    let (_d, at) = repo("colliding-tick");
    let (seven, eight) = (at.join("specs/007-x"), at.join("specs/008-y"));
    put(&seven, "tasks.md", "- [ ] T7708 seven's\n");
    put(&eight, "tasks.md", "- [ ] T7708 eight's\n");
    git(&at, &["add", "-A"]);
    commit_all(&at, "base");
    git(&at, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
    mark(&at, &at, "007-x", "T7708", "2026-11-27T10:00:00Z");
    mark(&at, &at, "008-y", "T7708", "2026-11-27T10:00:01Z");
    crate::env::set("L7R_LAND_TICKS", "T7708");
    crate::env::set("SPECIFY_FEATURE", "008-y");
    let held = (
        holding(&seven).unwrap().len(),
        holding(&eight).unwrap().len(),
    );
    crate::env::unset("SPECIFY_FEATURE");
    let unnamed = (
        holding(&seven).unwrap().len(),
        holding(&eight).unwrap().len(),
    );
    crate::env::unset("L7R_LAND_TICKS");
    assert_eq!((held, unnamed), ((1, 0), (1, 1)));
    // in process: the ticks handed in are the named feature's, and `holding_with` the directory's own
    assert_eq!(holding_for(&seven, "T7708", "008-y").unwrap().len(), 1);
    assert!(holding_for(&seven, "T7708", "007-x").unwrap().is_empty());
    assert!(holding_with(&eight, "T7708").unwrap().is_empty());
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

/// 451 T254's edges of the hold: a feature outside any repository holds nothing, another tree's started task holds nothing where git
/// cannot say what the push carries (no `origin/main`), and the starts file's rows name trees the edit lines are read against.
#[test]
fn the_hold_outside_a_repository_and_without_a_delta_is_none() {
    let outside = TempDir::new("guard-speckit-no-repo");
    put(&outside, "specs/7-x/tasks.md", "- [ ] T1 x\n");
    assert!(holding(&outside.join("specs/7-x")).unwrap().is_empty());
    let (_d, at) = repo("hold-no-delta");
    let d = at.join("specs/7-x");
    put(&at, "specs/7-x/tasks.md", "- [ ] T1 x\n");
    let other = at.join("other");
    // a worktree that still stands (451 T437: a mark of a tree gone holds nothing before the delta is asked)
    let id = ["-c", "user.email=t@t", "-c", "user.name=t"];
    git(
        &at,
        &[&id[..], &["commit", "-q", "--allow-empty", "-m", "b"]].concat(),
    );
    git(
        &at,
        &[
            "worktree",
            "add",
            "-q",
            "--detach",
            &other.to_string_lossy(),
        ],
    );
    mark(&at, &other, "7-x", "T1", "2026-11-25T10:00:00Z");
    put(
        &at,
        ".git/task-starts.jsonl",
        "{\"feature\": \"7-x\", \"task\": \"T1\", \"tree\": \"/gone\"}\nnot json\n",
    );
    assert!(holding(&d).unwrap().is_empty());
    git(
        &at,
        &[
            "-c",
            "user.email=t@t",
            "-c",
            "user.name=t",
            "commit",
            "-q",
            "--allow-empty",
            "-m",
            "a",
        ],
    );
    git(&at, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
    assert!(holding(&d).unwrap().is_empty());
}

/// 451 T359: the box of a withdrawn task is a ticked one carrying ` Withdrawn YYYY-MM-DD: ` - at any indent, either case of the
/// tick - and nothing else is: an open box, the word with no date, a date that is no date, or a line cut short of its why.
#[test]
fn a_withdrawn_box_is_ticked_and_dated() {
    for yes in [
        "- [x] T06 the wells Withdrawn 2026-11-26: a duplicate of T05",
        "  - [X] T06 said 'Withdrawn: <why>' Withdrawn 2026-11-26: no defect",
    ] {
        assert!(withdrawn_box(yes), "{yes}");
    }
    for no in [
        "- [ ] T06 the wells Withdrawn 2026-11-26: a duplicate of T05",
        "- [x] T06 the wells",
        "- [x] T06 ticked with 'Withdrawn: <why>'",
        "- [x] T06 the wells Withdrawn 2026-11-26",
        "- [x] T06 the wells Withdrawn 2026/11/26: a duplicate",
        "- [x] T06 the wells Withdrawn 2026-1a-26: a duplicate",
        "- [x] T06 the wells Withdrawn 20261-1-26: a duplicate",
        "- [x] T06 the wells Withdrawn 2026-11-26 - a duplicate",
    ] {
        assert!(!withdrawn_box(no), "{no}");
    }
}
