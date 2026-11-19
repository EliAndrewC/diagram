//! The derivation over fixture trees, and the rules that matter over the real one. The failure that matters is UNDER-running, so every assertion is written in that direction.

use std::path::Path;

use super::{answer, cli, Tree};

fn put(root: &Path, file: &str, text: &str) {
    let path = root.join(file);
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

fn tree(tag: &str) -> crate::shared::tempdir::TempDir {
    let root = crate::shared::tempdir::TempDir::new(&format!("guard-deps-{tag}"));
    for (file, text) in [
        (
            "scripts/hooks/a-hooks.sh",
            ". \"$X/lib/guardlog.sh\"\n# detection lives in hm_mention.py\n",
        ),
        (
            "scripts/hooks/lib/guardlog.sh",
            "python3 \"$H/hm_escape.py\" reason  # and not_this.py\n",
        ),
        (
            "scripts/hooks/lib/hm_escape.py",
            "\"\"\"Split out of hm_mention.py.\"\"\"\nfrom hm_shape import strip\n",
        ),
        ("scripts/hooks/lib/hm_shape.py", "X = 1\n"),
        ("scripts/hooks/lib/hm_mention.py", "Y = 1\n"),
        ("scripts/hooks/lib/__pycache__/hm_shape.py", "stale\n"),
        (
            "scripts/gates/gate-stamp.py",
            "ROOTS = {\"hooks\": (\"scripts\", (\"*.sh\", \"*.py\"))}\n",
        ),
        (
            "scripts/gates/prose.py",
            "\"\"\"globs scripts/*.sh in prose only\"\"\"\nX = 1\n",
        ),
        ("scripts/notes.md", "no\n"),
        ("scripts/sync-with-main.sh", "echo\n"),
        (
            "tests/hooks/test-a-hooks.sh",
            "\"$HERE/a-hooks.sh\" pretool\n",
        ),
        ("tests/hooks/hookrun.sh", "echo\n"),
        ("tests/hooks/fixtures/deep.sh", "echo\n"),
        (
            "tests/hooks/rusty-hooks.sh",
            "exec l7r-guard --only rusty\n",
        ),
        ("scripts/hooks/lib/commented-hooks.sh", "# only comments\n"),
        ("tests/hooks/dup-hooks.sh", "echo link\n"),
        ("scripts/hooks/dup-hooks.sh", "echo forwarder\n"),
        ("rust/Cargo.toml", "[workspace]\n"),
        ("rust/guard/src/a.rs", "fn a() {}\n"),
        ("Makefile", "land:\n\techo\n"),
        (
            "tests/hooks/test-make-hooks.sh",
            "make -f \"$ROOT/Makefile\" land\n",
        ),
        ("scripts/hooks/make-hooks.sh", "echo\n"),
    ] {
        put(&root, file, text);
    }
    root
}

fn names(deps: &[String], wanted: &str) -> bool {
    deps.iter().any(|d| d == wanted)
}

fn strings(words: &[&str]) -> Vec<String> {
    words.iter().map(|w| (*w).to_owned()).collect()
}

#[test]
fn a_dependency_reached_only_through_another_helper_still_counts() {
    let root = tree("transitive");
    let deps = Tree::at(&root).deps_for("a-hooks.sh");
    assert!(names(&deps, "a-hooks.sh") && names(&deps, "test-a-hooks.sh"));
    assert!(names(&deps, "guardlog.sh"));
    assert!(names(&deps, "hm_escape.py"));
    assert!(names(&deps, "hm_shape.py"));
}

#[test]
fn a_mention_in_a_comment_or_a_docstring_is_not_a_dependency() {
    let root = tree("mention");
    let deps = Tree::at(&root).deps_for("a-hooks.sh");
    assert!(!names(&deps, "hm_mention.py"));
    assert!(!names(&deps, "not_this.py"));
}

#[test]
fn the_held_suite_and_a_suite_that_globs_the_tree_depend_on_all_of_it() {
    let root = tree("whole");
    let t = Tree::at(&root);
    let (held, globbing) = (t.deps_for("sync-with-main.sh"), t.deps_for("gate-stamp.py"));
    assert!(names(&held, "hm_mention.py") && names(&globbing, "hm_mention.py"));
    assert!(!names(&t.deps_for("prose.py"), "hm_mention.py"),);
    assert!(names(
        &t.deps_for("commented-hooks.sh"),
        "commented-hooks.sh"
    ));
    assert_eq!(
        t.deps_for("gate-stamp.py")
            .iter()
            .filter(|d| *d == "hm_shape.py")
            .count(),
        1,
    );
}

#[test]
fn a_python_guards_suite_is_its_shell_name() {
    assert_eq!(super::suite_of("gate-stamp.py"), "test-gate-stamp.sh");
    assert_eq!(super::suite_of("a-hooks.sh"), "test-a-hooks.sh");
}

#[test]
fn the_key_moves_with_a_transitive_dependency_and_not_with_a_comment_free_stranger() {
    let root = tree("key");
    let before = Tree::at(&root).key_for("a-hooks.sh");
    put(&root, "scripts/hooks/lib/hm_mention.py", "Y = 2\n");
    assert_eq!(Tree::at(&root).key_for("a-hooks.sh"), before);
    put(&root, "scripts/hooks/lib/hm_shape.py", "X = 2\n");
    assert_ne!(Tree::at(&root).key_for("a-hooks.sh"), before);
}

#[test]
fn a_suite_that_names_the_makefile_goes_stale_when_the_makefile_changes() {
    let root = tree("makefile");
    let (make, other) = (
        Tree::at(&root).key_for("make-hooks.sh"),
        Tree::at(&root).key_for("a-hooks.sh"),
    );
    put(&root, "Makefile", "land:\n\techo changed\n");
    assert_ne!(Tree::at(&root).key_for("make-hooks.sh"), make);
    assert_eq!(Tree::at(&root).key_for("a-hooks.sh"), other);
}

#[test]
fn a_name_kept_twice_is_one_entry_with_its_last_path() {
    let root = tree("dup");
    let t = Tree::at(&root);
    assert_eq!(
        t.index.iter().filter(|(n, _)| n == "dup-hooks.sh").count(),
        1
    );
    assert!(t.paths["dup-hooks.sh"].ends_with("tests/hooks/dup-hooks.sh"));
}

#[test]
fn a_suite_that_drives_the_rust_guard_is_keyed_by_its_sources() {
    let root = tree("rust");
    let t = Tree::at(&root);
    let inputs = t.rust_inputs("rusty-hooks.sh");
    assert!(
        inputs.iter().any(|q| q.ends_with("rust/Cargo.toml"))
            && inputs.iter().any(|q| q.ends_with("rust/guard/src/a.rs"))
    );
    assert!(t.rust_inputs("a-hooks.sh").is_empty());
    let before = t.key_for("rusty-hooks.sh");
    put(&root, "rust/guard/src/a.rs", "fn b() {}\n");
    assert_ne!(Tree::at(&root).key_for("rusty-hooks.sh"), before);
}

#[test]
fn the_command_line() {
    let root = tree("cli");
    let t = Tree::at(&root);
    let ask = |words: &[&str]| answer(&t, &strings(words));
    let keys = ask(&["--keys", "a-hooks.sh", "gate-stamp.py"]).stdout;
    assert_eq!(keys.lines().count(), 2);
    assert!(keys.starts_with(&format!("a-hooks.sh {}\n", t.key_for("a-hooks.sh"))));
    assert!(ask(&["--all"]).stdout.contains("sync-with-main.sh "));
    assert!(ask(&["--all"]).stdout.starts_with("a-hooks.sh "));
    assert!(ask(&["--deps", "a-hooks.sh"])
        .stdout
        .contains("scripts/hooks/lib/guardlog.sh"));
    assert!(ask(&["--deps", "rusty-hooks.sh"])
        .stdout
        .contains("rust/Cargo.toml"));
    assert_eq!(ask(&["a-hooks.sh"]).stdout.trim(), t.key_for("a-hooks.sh"));
    assert_eq!(ask(&["--pydeps", "tests/test_a.py"]).code, 2);
    assert_eq!(ask(&["--bogus"]).code, 2);
    assert_eq!(ask(&[]).code, 2);
    assert_eq!(cli(&strings(&["--bogus"])).code, 2);
}

#[test]
fn the_limits_on_how_far_a_helper_reaches_hold_over_the_real_tree() {
    let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
    let t = Tree::at(&root);
    let mut guards: Vec<String> = vec!["record-edit-hooks.sh".to_owned()];
    guards.sort();
    guards.dedup();
    let reach = |helper: &str| {
        guards
            .iter()
            .filter(|g| names(&t.deps_for(g), helper))
            .count()
    };
    for guard in &guards {
        assert!(
            names(&t.deps_for(guard), guard) && names(&t.deps_for(guard), &format!("test-{guard}"))
        );
    }
    // a floor: a derivation that stopped following the graph would make these small, which is the failure that passes a broken suite
    assert!(reach("guardlog.sh") + 3 >= guards.len());
    let deps = t.deps_for("sync-with-main.sh");
    // feature 449 T129: `hm_shape.py` and `hm_escape.py` are gone; the escape read is the gate's, by `l7r-gate.sh`
    assert!(names(&deps, "l7r-gate.sh") && names(&deps, "guardlog.sh"));
}

#[test]
fn over_the_real_tree_the_rules_hold() {
    let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
    let t = Tree::at(&root);
    assert!(t.deps_for("sync-with-main.sh").len() > 20);
    let helpers = |g: &str| t.deps_for(g).len();
    assert!(helpers("claims-gate.sh") < t.index.len());
    let deps = t.deps_for("claims-gate.sh");
    assert!(names(&deps, "guardlog.sh"));
    let on_disk = std::fs::read_dir(root.join("scripts/hooks/lib"))
        .unwrap()
        .flatten();
    for file in on_disk
        .map(|e| e.file_name().to_string_lossy().into_owned())
        .filter(|n| matches!(super::suffix(n), "py" | "sh"))
    {
        assert!(names(&t.shared, &file),);
    }
    assert!(t.key_for("l7r-guard.sh").len() == 16 && !t.rust_inputs("l7r-guard.sh").is_empty());
}

#[test]
fn a_tree_that_is_not_there_indexes_nothing() {
    let t = Tree::at(Path::new("/no/such/tree/at/all"));
    assert!(t.index.is_empty() && t.shared == ["hookrun.sh"]);
}
