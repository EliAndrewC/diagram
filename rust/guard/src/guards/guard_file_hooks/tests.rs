//! The decider over a fixture checkout (`tests/hooks/test-guard-file-hooks.sh`, replayed through the shim, is the verdict).

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::{decide, judge, now_from, permit_reason, read_context, recipe_hazards};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;
use crate::shared::tool::ask;

fn world(tag: &str) -> PathBuf {
    crate::shared::log::quiet();
    let d = std::env::temp_dir().join(format!("l7r-guard-gf-{tag}-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&d);
    std::fs::create_dir_all(d.join("scripts/hooks")).unwrap();
    std::fs::create_dir_all(d.join("specs/x")).unwrap();
    std::fs::create_dir_all(d.join("tests")).unwrap();
    let d = d.canonicalize().unwrap();
    assert!(ask(
        std::path::Path::new("/"),
        "git",
        &["init", "-q", &d.to_string_lossy()],
        ""
    )
    .ok());
    std::fs::write(d.join("Makefile"), "all:\n").unwrap();
    d
}

fn edit(file: &str, new: &str) -> Vec<Answer> {
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Edit", "tool_input": {"file_path": file, "new_string": new, "old_string": ""}}),
    };
    judge(&e, &Session::from_input(&e.input), 1000.0)
}

fn refused(got: &[Answer], words: &str) -> bool {
    matches!(got, [Answer::Refuse(t)] if t.contains(words))
}

fn p(d: &Path, rel: &str) -> String {
    d.join(rel).to_string_lossy().into_owned()
}

#[test]
fn a_guard_is_refused_with_no_marker_and_passes_with_a_reason() {
    let d = world("guard");
    let hook = p(&d, "scripts/hooks/a-hooks.sh");
    assert!(refused(
        &edit(&hook, "x"),
        "is a GUARD, not ordinary source"
    ));
    assert!(refused(
        &edit(&p(&d, ".claude/settings.json"), "x"),
        "make guard-edit FILE="
    ));
    assert!(refused(&edit(&p(&d, "tests/rolls.py"), "x"), "GUARD"));
    assert!(refused(&edit(&p(&d, "dev/switches.json"), "x"), "GUARD"));
    assert!(refused(&edit(&p(&d, "dev/work-budget.json"), "x"), "GUARD"));
    assert!(edit(&hook, "GUARD_EDIT_OK: it fired on correct work").is_empty());
    assert!(refused(&edit(&hook, "GUARD_EDIT_OK"), "with no reason"));
    assert!(edit(&p(&d, "tests/hooks/test-a-hooks.sh"), "x").is_empty());
    assert!(edit(&p(&d, "notes.md"), "GUARD_EDIT_OK").is_empty());
}

#[test]
fn the_root_makefile_takes_no_marker_and_a_permit_stands_an_hour() {
    let d = world("permit");
    let root = p(&d, "Makefile");
    assert!(refused(
        &edit(&root, "GUARD_EDIT_OK: a reason here"),
        "which takes none"
    ));
    assert!(refused(&edit(&root, "x"), "is a GUARD"));
    let rows = format!(
        "{}\n{}\n",
        json!({"file": root, "reason": "the older one", "at": 100.0}),
        json!({"file": root, "reason": "the live one", "at": 900.0})
    );
    std::fs::write(d.join(".git/l7r-guard-permits.jsonl"), rows).unwrap();
    assert_eq!(permit_reason(&root, 1000.0), "the live one");
    assert_eq!(permit_reason(&root, 900.0 + 3601.0), "");
    assert!(edit(&root, "x").is_empty());
    let write = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Write", "tool_input": {"file_path": root, "content": "all:\nGUARD_EDIT_OK: new one\n"}}),
    };
    assert!(refused(
        &judge(&write, &Session::from_input(&write.input), 1000.0),
        "which takes none"
    ));
    assert_eq!(permit_reason("/no/such/x", 1.0), "");
    assert_eq!(permit_reason(&d.to_string_lossy(), 1.0), "");
    assert!((now_from(Some("5".to_owned())) - 5.0).abs() < 1e-6);
    assert!(now_from(None) > 1.0);
    std::fs::write(d.join(".git/l7r-guard-permits.jsonl"), "not json\n").unwrap();
    assert_eq!(permit_reason(&root, 1000.0), "");
}

#[test]
fn a_recipe_comment_that_would_run_is_refused_on_any_makefile() {
    let d = world("hazard");
    let sub = p(&d, "specs/x/Makefile");
    assert!(refused(
        &edit(&sub, "\t: \"see `make x`\""),
        "COMMAND SUBSTITUTION"
    ));
    assert!(refused(
        &edit(&p(&d, "a.mk"), "\t@: \"key $$(git)\""),
        "There is no escape token"
    ));
    assert_eq!(
        recipe_hazards("a\n\t: \"`b`\"\n\t: 'c `d`'\n# `e`\n\t: \"\\`f\\`\"").len(),
        1
    );
    assert_eq!(recipe_hazards("x\n\t: \"`b`\""), ["2: : \"`b`\""]);
}

#[test]
fn a_read_of_a_guard_is_told_for_free() {
    let d = world("read");
    let read = |path: &str| {
        let e = Event {
            name: "PreToolUse".to_owned(),
            input: json!({"tool_name": "Read", "tool_input": {"file_path": path}}),
        };
        judge(&e, &Session::from_input(&e.input), 1.0)
    };
    assert!(
        matches!(&read(&p(&d, "Makefile"))[..], [Answer::Notice(t)] if t.contains("root Makefile"))
    );
    assert!(
        matches!(&read(&p(&d, "tests/rolls.py"))[..], [Answer::Notice(t)] if t.contains("make roll-audit"))
    );
    assert!(
        matches!(&read(&p(&d, "scripts/a-hooks.sh"))[..], [Answer::Notice(t)] if t.contains("This is a GUARD file"))
    );
    assert!(read(&p(&d, "notes.md")).is_empty());
    assert!(read(&p(&d, "specs/x/Makefile")).is_empty());
    assert_eq!(read_context("/r/scripts/tests/hooks/test-a-hooks.sh"), None);
}

#[test]
fn an_input_with_no_file_passes() {
    let d: Value = json!({"tool_name": "Edit"});
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: d,
    };
    assert!(decide(&e, &Session::from_input(&e.input)).is_empty());
}
