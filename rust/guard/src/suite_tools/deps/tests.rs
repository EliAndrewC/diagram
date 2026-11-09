//! The derivation over fixture trees, and the rules that matter over the real one. The failure that matters is UNDER-running, so every assertion is written in that direction.

use std::path::{Path, PathBuf};
use std::process::Command;

use super::{answer, cli, Tree};

fn put(root: &Path, file: &str, text: &str) {
    let path = root.join(file);
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

fn tree(tag: &str) -> PathBuf {
    let root = std::env::temp_dir().join(format!("l7r-guard-deps-{tag}-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&root);
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
fn a_script_loaded_by_a_string_is_reached_and_a_prose_mention_is_not() {
    let root = tree("strings");
    put(&root, "scripts/record/record_owed.py", "X = 1\n");
    put(&root, "scripts/record/modal_owed.py", "X = 1\n");
    put(&root, "scripts/record/moves.py", "X = 1\n");
    put(&root, "scripts/patch.py", "X = 1\n");
    put(&root, "scripts/hooks/lib/hm_arbiter.py", "X = 1\n");
    let t = Tree::at(&root);
    let refs = t.word_refs("x.py", "import json\nro = _sibling(\"record_owed\")\nmo = script(\"_modal_owed\")\nprint(\"see moves.py for why\")\n");
    assert!(refs.contains("record_owed.py") && refs.contains("modal_owed.py"));
    assert!(!refs.contains("moves.py"));
    assert!(t
        .word_refs("x.py", "P = ROOT / \"scripts\" / \"patch.py\"\n")
        .contains("patch.py"));
    assert!(t
        .word_refs("x.py", "from hm_arbiter import trip\n")
        .contains("hm_arbiter.py"));
    assert!(t
        .word_refs("x.sh", ". \"$HERE/lib/guardlog.sh\"\n")
        .contains("guardlog.sh"));
    assert!(t
        .word_refs("x.py", "x = 'broken\nguardlog.sh\n")
        .contains("guardlog.sh"),);
    assert!(!t
        .word_refs("patch.py", "x = \"patch.py\"\n")
        .contains("patch.py"),);
}

#[test]
fn a_test_depends_on_what_it_reaches_or_on_the_whole_tree_when_it_cannot_say() {
    let root = tree("pydeps");
    put(&root, "tests/conftest.py", "");
    put(&root, "tests/tooling/conftest.py", "");
    put(&root, "tests/_scripts.py", "");
    put(&root, "tests/tooling/test_reach.py", "from tests._scripts import script\nfrom tests._absent import x\nX = script(\"hm_shape\")\n");
    let all = |t: &Tree| t.index.len();
    let t = Tree::at(&root);
    let rel = |t: &Tree, f: &str| {
        t.pydeps(&root.join(f))
            .iter()
            .map(|p| t.rel(p))
            .collect::<Vec<_>>()
    };
    let reach = rel(&t, "tests/tooling/test_reach.py");
    assert!(
        reach.contains(&"tests/conftest.py".to_owned())
            && reach.contains(&"tests/tooling/conftest.py".to_owned())
    );
    assert!(
        reach.contains(&"tests/_scripts.py".to_owned())
            && reach.contains(&"scripts/hooks/lib/hm_shape.py".to_owned())
    );
    assert!(!reach.contains(&"scripts/hooks/lib/hm_mention.py".to_owned()));
    put(
        &root,
        "tests/tooling/test_shell.py",
        "X = script(\"guardlog.sh\")\n",
    );
    assert!(rel(&Tree::at(&root), "tests/tooling/test_shell.py")
        .contains(&"scripts/hooks/lib/hm_escape.py".to_owned()));
    assert!(Tree::at(&root.join("no-such-tree")).index.is_empty());
    for (file, body) in [
        (
            "tests/tooling/test_builds.py",
            "X = script(\"hm_shape\")\np = ROOT / \"scripts\" / name\n",
        ),
        (
            "tests/tooling/test_dir.py",
            "X = script(\"hm_shape\")\nS = REPO / \"scripts\"\n",
        ),
        (
            "tests/tooling/test_sh.py",
            "X = script(\"hm_shape\")\nG = \"scripts/*.sh\"\n",
        ),
        (
            "tests/tooling/test_py.py",
            "X = script(\"hm_shape\")\nG = \"scripts/*.py\"\n",
        ),
        ("tests/tooling/test_nothing.py", "X = 1\n"),
    ] {
        put(&root, file, body);
        let t = Tree::at(&root);
        assert!(t.pydeps(&root.join(file)).len() > all(&t), "{file}");
    }
    assert_eq!(
        Tree::at(&root).pydeps(&root.join("tests/absent.py")).len(),
        all(&Tree::at(&root)) + 2
    );
}

#[test]
fn an_unchanged_tree_runs_none_and_a_changed_dependency_runs_its_tests() {
    let root = tree("stale");
    let gitdir = root.join("git");
    put(&root, "tests/test_a.py", "X = script(\"hm_shape\")\n");
    put(&root, "tests/test_b.py", "X = script(\"hm_mention\")\n");
    let tests = strings(&["tests/test_a.py", "tests/test_b.py"]);
    assert_eq!(Tree::at(&root).py_stale(&gitdir, &tests), tests);
    Tree::at(&root).py_stamp(&gitdir, &tests);
    assert!(gitdir.join("hooks-test/py/tests__test_a.py").is_file());
    assert!(Tree::at(&root).py_stale(&gitdir, &tests).is_empty());
    put(&root, "scripts/hooks/lib/hm_shape.py", "X = 3\n");
    assert_eq!(
        Tree::at(&root).py_stale(&gitdir, &tests),
        ["tests/test_a.py"]
    );
}

#[test]
fn the_window_counts_what_each_commit_would_re_run() {
    let root = tree("window");
    put(&root, "tests/test_a.py", "X = script(\"hm_shape\")\n");
    put(&root, "tests/test_b.py", "X = script(\"hm_mention\")\n");
    let run = |args: &[&str]| {
        assert!(Command::new("git")
            .arg("-C")
            .arg(&root)
            .args(["-c", "user.name=t", "-c", "user.email=t@t"])
            .args(args)
            .output()
            .unwrap()
            .status
            .success());
    };
    run(&["init", "-q"]);
    run(&["add", "."]);
    run(&["commit", "-q", "-m", "all"]);
    put(&root, "scripts/hooks/lib/hm_shape.py", "X = 9\n");
    run(&["add", "."]);
    run(&["commit", "-q", "-m", "one"]);
    let t = Tree::at(&root);
    let got = t.window(
        "HEAD",
        "1",
        &strings(&["tests/test_a.py", "tests/test_b.py"]),
    );
    let lines: Vec<&str> = got.lines().collect();
    assert!(lines[0].ends_with(" 1"));
    assert_eq!(lines[1], "mean 1.0 of 2");
    let args = strings(&["--window", "HEAD", "1", "tests/test_a.py"]);
    assert!(answer(&t, &args).stdout.ends_with("mean 1.0 of 1\n"));
    assert_eq!(t.window("no-such-ref", "1", &[]), "mean 0.0 of 0\n");
}

#[test]
fn the_command_line() {
    let root = tree("cli");
    put(&root, "tests/test_a.py", "X = script(\"hm_shape\")\n");
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
    assert!(ask(&["--pydeps", "tests/test_a.py"])
        .stdout
        .contains("hm_shape.py"));
    assert_eq!(ask(&["a-hooks.sh"]).stdout.trim(), t.key_for("a-hooks.sh"));
    let git = root.join("g");
    let git = git.to_str().unwrap();
    assert_eq!(
        ask(&["--pystale", git, "tests/test_a.py"]).stdout,
        "tests/test_a.py\n"
    );
    assert_eq!(ask(&["--pystamp", git, "tests/test_a.py"]).code, 0);
    assert_eq!(ask(&["--pystale", git, "tests/test_a.py"]).stdout, "\n");
    assert_eq!(ask(&["--bogus"]).code, 2);
    assert_eq!(ask(&[]).code, 2);
    assert_eq!(cli(&strings(&["--bogus"])).code, 2);
}

#[test]
fn the_limits_on_how_far_a_helper_reaches_hold_over_the_real_tree() {
    let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
    let t = Tree::at(&root);
    let mut guards: Vec<String> = t
        .index
        .iter()
        .filter(|(n, p)| {
            n.ends_with("-hooks.sh") && p.parent().is_some_and(|d| d.ends_with("scripts/hooks"))
        })
        .map(|(n, _)| n.clone())
        .collect();
    guards.extend(["record-edit-hooks.sh".to_owned()]);
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
    // a ceiling: if it grows, the win is lost, or a mention has started counting as a dependency
    assert!(reach("gatecost.py") <= 4);
    // a floor: a derivation that stopped following the graph would make these small, which is the failure that passes a broken suite
    assert!(reach("hm_escape.py") + 3 >= guards.len());
    assert!(reach("guardlog.sh") + 3 >= guards.len());
    let deps = t.deps_for("sync-with-main.sh");
    assert!(
        names(&deps, "gatecost.py") && names(&deps, "hm_shape.py") && names(&deps, "guardlog.sh")
    );
}

#[test]
fn over_the_real_tree_the_rules_hold() {
    let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
    let t = Tree::at(&root);
    assert!(t.deps_for("sync-with-main.sh").len() > 20);
    let helpers = |g: &str| t.deps_for(g).len();
    assert!(helpers("record-edit-hooks.sh") < t.index.len());
    let deps = t.deps_for("record-edit-hooks.sh");
    assert!(names(&deps, "guardlog.sh") && names(&deps, "hm_escape.py"));
    let on_disk = std::fs::read_dir(root.join("scripts/hooks/lib"))
        .unwrap()
        .flatten();
    for file in on_disk
        .map(|e| e.file_name().to_string_lossy().into_owned())
        .filter(|n| matches!(super::suffix(n), "py" | "sh"))
    {
        assert!(names(&t.shared, &file),);
    }
    let lint = t
        .pydeps(&root.join("tests/tooling/test_ledger_lint.py"))
        .iter()
        .map(|p| t.rel(p))
        .collect::<Vec<_>>();
    assert!(
        lint.contains(&"scripts/reviews/ledger_lint.py".to_owned())
            && lint.contains(&"tests/conftest.py".to_owned())
    );
    assert!(!lint.contains(&"scripts/record/modal_bundle.py".to_owned()));
    assert!(t.key_for("l7r-guard.sh").len() == 16 && !t.rust_inputs("l7r-guard.sh").is_empty());
}
