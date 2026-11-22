//! The decider over a fixture checkout (`tests/hooks/test-guard-file-hooks.sh`, replayed through the shim, is the verdict).

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::{decide, judge, now_from, permit_reason, read_context, recipe_hazards};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;
use crate::shared::tool::ask;

fn world(tag: &str) -> crate::shared::tempdir::Held<PathBuf> {
    crate::shared::log::quiet();
    let d = crate::shared::tempdir::TempDir::new(&format!("guard-gf-{tag}"));
    std::fs::create_dir_all(d.join("scripts/hooks")).unwrap();
    std::fs::create_dir_all(d.join("specs/x")).unwrap();
    std::fs::create_dir_all(d.join("tests")).unwrap();
    let (keep, d) = {
        let canon = d.canonicalize().unwrap();
        (d, canon)
    };
    assert!(ask(
        std::path::Path::new("/"),
        "git",
        &["init", "-q", &d.to_string_lossy()],
        ""
    )
    .ok());
    std::fs::write(d.join("Makefile"), "all:\n").unwrap();
    // the world stands for a project tree (451 T87: under the temp directory a guard file's name is scratch, held only in one)
    crate::shared::env::set("CLONE_MAIN", &d);
    keep.hold(d)
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
    // the work budgets take no permit (`make guard-edit` refuses the file): the refusal names their writer (feature 449 T225)
    let budget = edit(&p(&d, "dev/work-budget.json"), "x");
    assert!(refused(&budget, "make budget-change PHASE="));
    assert!(!matches!(&budget[..], [Answer::Refuse(t)] if t.contains("make guard-edit FILE=")));
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
        matches!(&read(&p(&d, "tests/rolls.py"))[..], [Answer::Notice(t)] if t.contains("constitution VI") && !t.contains("roll-audit"))
    );
    assert!(
        matches!(&read(&p(&d, "scripts/a-hooks.sh"))[..], [Answer::Notice(t)] if t.contains("This is a GUARD file"))
    );
    // T227: the shell guards live in scripts/hooks/ since feature 429, and a Read of one was told nothing
    assert!(
        matches!(&read(&p(&d, "scripts/hooks/a-hooks.sh"))[..], [Answer::Notice(t)] if t.contains("This is a GUARD file"))
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
    let dir = crate::shared::tempdir::TempDir::new("guard-permit");
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

#[test]
fn the_guards_own_sources_are_held_and_granted_but_not_their_tests() {
    // T229 (ask:449-guard-sources-held): every .rs under rust/guard/src/, the crate manifest and the dispatcher script
    for held in [
        "/r/rust/guard/src/guards/make_only_hooks.rs",
        "/r/rust/guard/src/shared/tree.rs",
        // the guard's shared crate (451 T58): its sources, its manifest and its data files
        "/r/rust/guard/shared/src/tree.rs",
        "/r/rust/guard/shared/Cargo.toml",
        "/r/rust/guard/shared/src/guards/house_style_words.tsv",
        "/r/rust/guard/src/main.rs",
        "/r/rust/guard/Cargo.toml",
        "/r/rust/guard/src/agent_model_rule.txt",
        "/r/rust/guard/src/guards/house_style_words.tsv",
        "/r/scripts/hooks/l7r-guard.sh",
    ] {
        assert!(super::held(held), "{held} is held");
        assert!(super::grantable(held), "{held} is granted");
        assert!(read_context(held).is_some(), "{held} is told on a Read");
    }
    for loose in [
        "/r/rust/guard/src/guards/make_only_hooks/tests.rs",
        "/r/rust/guard/src/guards/tests.rs",
        "/r/rust/guard/src/shared/tests/tree.rs",
        "/r/rust/guard/shared/src/context/tests.rs",
        "/r/rust/guard/src/guards/tests/words.tsv",
        "/r/tests/hooks/test-make-only-hooks.sh",
        "/r/rust/other/src/lib.rs",
    ] {
        assert!(!super::held(loose), "{loose} is not held");
        assert!(!super::grantable(loose), "{loose} is not granted");
        assert_eq!(read_context(loose), None);
    }
}

/// 451 T87 (found by T79): a guard file's name in scratch - under `/tmp` or `$TMPDIR`, where `$(mktemp -d)` places a directory - is no
/// guard file, so its edit passes; the same name in a project tree, through a scratch link into one, or in a place nothing marks as
/// scratch (`/Makefile`, the walk's `$UNSET/Makefile`; `~/.claude/settings.json`, which holds the GM's own hooks) is held, as at HEAD.
#[test]
fn a_guard_file_name_in_scratch_is_not_held_but_one_in_a_project_tree_is() {
    let d = world("scratch");
    let place = crate::shared::tempdir::TempDir::new("guard-gf-scratch-place");
    let s = place.canonicalize().unwrap();
    crate::shared::env::set("TMPDIR", std::env::temp_dir());
    std::os::unix::fs::symlink(&*d, s.join("link")).unwrap();
    let freed = [
        p(&s, "Makefile"),
        p(&s, "dev/work-budget.json"),
        p(&s, "rust/guard/src/guards/a.rs"),
        "/tmp/tmp.XXXXXXXXXX/dev/work-budget.json".to_owned(),
    ];
    let got: Vec<bool> = freed.iter().map(|f| super::held(f)).collect();
    assert_eq!(got, [false; 4], "{freed:?}");
    let home = crate::shared::env::var("HOME");
    let kept = [
        p(&d, "Makefile"),
        p(&s, "link/Makefile"),
        "/Makefile".to_owned(),
        "/dev/work-budget.json".to_owned(),
        format!("{home}/.claude/settings.json"),
        "/r/scripts/hooks/a-hooks.sh".to_owned(),
    ];
    let got: Vec<bool> = kept.iter().map(|f| super::held(f)).collect();
    assert_eq!(got, [true; 6], "{kept:?}");
    let passed = edit(&p(&s, "Makefile"), "x");
    assert!(passed.is_empty(), "{passed:?}");
    let refused_here = refused(&edit(&p(&s, "link/Makefile"), "x"), "is a GUARD");
    assert!(refused_here);
}

/// 451 T87: `$TMPDIR` is scratch where it names a place of its own - not `/`, the home directory or a place holding it - and a
/// project tree under it stays one.
#[test]
fn tmpdir_is_scratch_only_where_it_is_a_place_of_its_own() {
    let d = world("tmpdir");
    crate::shared::env::set("TMPDIR", "/var/t87-scratch");
    let away = super::held("/var/t87-scratch/tmp.XXXXXXXXXX/Makefile");
    assert!(!away);
    let home = crate::shared::env::var("HOME");
    for wide in ["/".to_owned(), home.clone(), "/home".to_owned()] {
        crate::shared::env::set("TMPDIR", &wide);
        let kept = super::held(&format!("{home}/x/Makefile"));
        assert!(kept, "TMPDIR={wide}");
    }
    crate::shared::env::set("TMPDIR", &*d);
    let inside = super::held(&p(&d, "tmp.XXXXXXXXXX/Makefile"));
    assert!(inside);
    let relative = super::held("x/Makefile");
    assert!(relative);
}

/// 451 T87 (review round 2): a git worktree in scratch whose common git dir is a project repository's is a project tree - its commits
/// reach that repository - so a guard file's name in it is held: the pointer git writes, a relative one read from its own directory,
/// and one whose `commondir` cannot be read, held where it points. A worktree of scratch's own repository, and that repository, stay
/// scratch.
#[test]
fn a_worktree_in_scratch_of_a_project_repository_is_held() {
    let d = world("worktree");
    let place = crate::shared::tempdir::TempDir::new("guard-gf-worktree-place");
    let s = place.canonicalize().unwrap();
    crate::shared::env::set("TMPDIR", std::env::temp_dir());
    let name = d.file_name().unwrap().to_string_lossy().into_owned();
    for (common, pointed) in [
        (d.join(".git/worktrees/w"), "../.."),
        (s.join("repo/.git/worktrees/x"), "../.."),
    ] {
        std::fs::create_dir_all(&common).unwrap();
        std::fs::write(common.join("commondir"), pointed).unwrap();
    }
    let pointers = [
        ("wt", p(&d, ".git/worktrees/w")),
        ("rel", format!("../../{name}/.git/worktrees/w")),
        ("dangling", p(&d, ".git/worktrees/gone")),
        ("own", p(&s, "repo/.git/worktrees/x")),
    ];
    for (dir, gitdir) in &pointers {
        std::fs::create_dir_all(s.join(dir)).unwrap();
        std::fs::write(s.join(dir).join(".git"), format!("gitdir: {gitdir}\n")).unwrap();
    }
    let files = [
        "wt/Makefile",
        "wt/rust/guard/src/guards/a.rs",
        "rel/Makefile",
        "dangling/Makefile",
        "own/Makefile",
        "repo/Makefile",
    ];
    let got: Vec<bool> = files.iter().map(|f| super::held(&p(&s, f))).collect();
    assert_eq!(got, [true, true, true, true, false, false], "{files:?}");
}
