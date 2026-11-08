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

#[test]
fn make_guard_edit_grants_a_guard_file_with_a_reason_and_only_that() {
    let dir = std::env::temp_dir().join(format!("l7r-guard-permit-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&dir);
    std::fs::create_dir_all(dir.join("scripts/hooks")).unwrap();
    assert!(std::process::Command::new("git")
        .arg("-C")
        .arg(&dir)
        .args(["init", "-q"])
        .status()
        .unwrap()
        .success());
    let hook = dir.join("scripts/hooks/x-hooks.sh");
    std::fs::write(&hook, "").unwrap();
    let readme = dir.join("notes.md");
    std::fs::write(&readme, "").unwrap();
    let path = |p: &std::path::Path| p.to_str().unwrap().to_owned();
    let grant =
        |file: &str, why: &str| super::cli(&["grant".to_owned(), file.to_owned(), why.to_owned()]);
    assert_eq!(super::cli(&["grant".to_owned()]).code, 2);
    assert_eq!(
        super::cli(&["nope".to_owned(), "a".to_owned(), "b".to_owned()]).code,
        2
    );
    assert!(grant(&path(&readme), "a reason for it")
        .stderr
        .contains("is not a guard file"));
    assert!(grant(&path(&hook), "x")
        .stderr
        .contains("two words and eight characters"));
    let done = grant(&path(&hook), "adding a case to it");
    assert_eq!(done.code, 0);
    assert!(
        done.stdout.contains("may be edited until")
            && done.stdout.ends_with("- adding a case to it\n")
    );
    let real = hook.canonicalize().unwrap();
    let real = real.to_str().unwrap();
    let now = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap()
        .as_secs_f64();
    assert_eq!(super::permit_reason(real, now), "adding a case to it");
    assert_eq!(super::permit_reason(real, now + 7200.0), "");
    assert_eq!(grant(&path(&hook), "a second reason here").code, 0);
    let store = dir.join(".git/l7r-guard-permits.jsonl");
    assert_eq!(std::fs::read_to_string(&store).unwrap().lines().count(), 2);
    assert!(super::live_rows(&store, now + 7200.0).is_empty());
    std::fs::write(&store, "not json\n").unwrap();
    assert!(super::live_rows(&store, now).is_empty());
    assert!(
        super::grantable("/r/scripts/hooks/pair-hooks.sh")
            && !super::grantable("/r/tests/hooks/test-pair-hooks.sh")
    );
    assert_eq!(super::real_path("/no/such/file"), "/no/such/file");
}

#[test]
fn no_recipe_comment_in_the_repository_would_run() {
    let root = concat!(env!("CARGO_MANIFEST_DIR"), "/../..");
    let tracked = std::process::Command::new("git")
        .args(["-C", root, "ls-files", "--", "Makefile", "*/Makefile"])
        .output()
        .unwrap();
    let names = String::from_utf8_lossy(&tracked.stdout).into_owned();
    assert!(names.lines().any(|n| n == "Makefile"));
    let bad: Vec<String> = names
        .lines()
        .flat_map(|n| {
            super::recipe_hazards(&std::fs::read_to_string(format!("{root}/{n}")).unwrap())
        })
        .collect();
    assert_eq!(bad, Vec::<String>::new());
}

#[test]
fn the_recipe_detector_fires_on_each_hazard_and_passes_each_safe_form() {
    let fires = [
        "\t: \"GUARD_EDIT_OK: feature 207 - `make test-full` is the gate's test phase\" ; \\",
        "\t@: \"see `make help`\"",
        "\t: \"the key is $$(git rev-parse HEAD) here\"",
        "\t: \"a brace form $${HOME} too\"",
    ];
    let safe = [
        "\t: \"GUARD_EDIT_OK: feature 207 - make test-full is the gate's test phase\" ; \\",
        "\t: \"the target is \\`make done\\`\"",
        "\t: \"make runs \\$$(MAKE) sub-invocations even under -n\" ; \\",
        "\t: 'GUARD_EDIT_OK: `make done` in single quotes is inert'",
        "# `make done` in a hash comment is make's, never the shell's",
        "\t@echo \"$$(date) runs on purpose - a command, not a comment\"",
        "\t: \"a make-level $(VAR) is expanded by make, not the shell\"",
    ];
    assert!(fires.iter().all(|l| super::recipe_hazards(l).len() == 1));
    assert!(safe.iter().all(|l| super::recipe_hazards(l).is_empty()));
    let text = format!("target:\n{}\n{}\n{}\n", safe[0], fires[0], fires[2]);
    let lines: Vec<String> = super::recipe_hazards(&text)
        .iter()
        .filter_map(|h| h.split(':').next().map(str::to_owned))
        .collect();
    assert_eq!(lines, ["3", "4"]);
}
