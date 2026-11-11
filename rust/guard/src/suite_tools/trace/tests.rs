//! What a suite read, kept and judged by content, over fixture repositories (the recorder itself is `tests/tooling/test_file_log.py`'s).

use std::path::{Path, PathBuf};
use std::process::Command;

use super::{answer, cli, fresh, reads, relpath, shim, stamp, trace_file};

fn git(root: &Path, args: &[&str]) {
    assert!(Command::new("git")
        .arg("-C")
        .arg(root)
        .args(args)
        .output()
        .unwrap()
        .status
        .success());
}

fn world(tag: &str) -> (crate::shared::tempdir::TempDir, PathBuf, PathBuf) {
    let base = crate::shared::tempdir::TempDir::new(&format!("guard-trace-{tag}"));
    let (root, gitdir) = (base.join("repo"), base.join("gitdir"));
    std::fs::create_dir_all(&root).unwrap();
    git(&root, &["init", "-q"]);
    std::fs::write(root.join("a.sh"), "one\n").unwrap();
    (base, root, gitdir)
}

fn script(at: &Path, body: &str) -> String {
    std::fs::write(at, format!("#!/bin/bash\n{body}\n")).unwrap();
    Command::new("chmod").arg("+x").arg(at).status().unwrap();
    at.to_string_lossy().into_owned()
}

fn names(guards: &[&str]) -> Vec<String> {
    guards.iter().map(|g| (*g).to_owned()).collect()
}

#[test]
fn a_suites_reads_are_kept_and_judged_by_content() {
    let (base, root, gitdir) = world("kept");
    let python = "python3";
    std::fs::create_dir_all(root.join("d")).unwrap();
    std::fs::write(root.join("d/a"), "x").unwrap();
    let log = base.join("suite.reads");
    std::fs::write(
        &log,
        format!(
            "g\tc-file\t{0}/a.sh\ng\tc-dir\t{0}/d\ng\tc-dir\t{0}\n",
            root.display()
        ),
    )
    .unwrap();
    stamp(&root, &gitdir, "g-hooks.sh", &log, &root, python);
    let fresh_now = || {
        fresh(
            &root,
            &gitdir,
            &root,
            &names(&["g-hooks.sh", "other.sh"]),
            python,
        )
    };
    assert_eq!(fresh_now(), ["g-hooks.sh"]);
    std::fs::write(root.join("d/b.sh"), "new\n").unwrap();
    assert!(fresh_now().is_empty(),);
    std::fs::remove_file(root.join("d/b.sh")).unwrap();
    assert_eq!(fresh_now(), ["g-hooks.sh"]);
    std::fs::write(root.join("a.sh"), "two\n").unwrap();
    assert!(fresh_now().is_empty(), "a read changed: the suite runs");
    assert!(fresh(&root, &gitdir, &root, &names(&["other.sh"]), python).is_empty());
}

#[test]
fn a_stamp_kept_by_the_python_stands() {
    let (base, root, gitdir) = world("python");
    git(&root, &["add", "a.sh"]);
    std::fs::create_dir_all(root.join("d")).unwrap();
    std::fs::write(root.join("d/x y.txt"), "z").unwrap();
    git(&root, &["add", "d"]);
    let log = base.join("reads");
    std::fs::write(
        &log,
        format!("g\tc-file\t{0}/a.sh\ng\tc-dir\t{0}/d\n", root.display()),
    )
    .unwrap();
    stamp(&root, &gitdir, "g", &log, &root, "python3");
    let kept: serde_json::Value =
        serde_json::from_str(&std::fs::read_to_string(trace_file(&gitdir, "g")).unwrap()).unwrap();
    assert_eq!(kept["dirs"]["d"], "[\"x y.txt\"]");
    assert_eq!(kept["files"]["a.sh"].as_str().unwrap().len(), 40);
    assert_eq!(kept["recorder"], "");
    assert!(kept["py"].as_str().unwrap().starts_with('3'));
}

#[test]
fn what_cannot_be_traced_keeps_the_deps_key() {
    let (base, root, gitdir) = world("untraced");
    let log = base.join("reads");
    std::fs::write(
        &log,
        format!(
            "g\tc-file\t{0}/a.sh\ng\tc-git\t{0}/.git/HEAD\n",
            root.display()
        ),
    )
    .unwrap();
    stamp(&root, &gitdir, "g", &log, &root, "python3");
    assert!(!trace_file(&gitdir, "g").exists(),);
    assert_eq!(reads(&base.join("absent"), &root), Some(Default::default()));
    std::fs::write(root.join(".gitignore"), "ignored.txt\n").unwrap();
    std::fs::write(root.join("ignored.txt"), "x").unwrap();
    std::fs::write(
        &log,
        format!("g\tc-file\t{0}/ignored.txt\n", root.display()),
    )
    .unwrap();
    stamp(&root, &gitdir, "g", &log, &root, "python3");
    assert!(!trace_file(&gitdir, "g").exists(),);
    std::fs::write(&log, "").unwrap();
    stamp(&root, &gitdir, "g", &log, &root, "python3");
    assert!(!trace_file(&gitdir, "g").exists(),);
}

#[test]
fn a_read_is_named_as_the_repository_names_it() {
    let (base, root, _) = world("names");
    let log = base.join("reads");
    let at = root.display();
    std::fs::write(&log, format!("g\tc-file\t{at}/scripts/__pycache__/m.cpython-314.pyc\ng\tc-file\t{at}/.git/l7r-cache/x\ng\tc-file\t{at}/.git/hooks-test/y\ng\tc-dir\t{at}/.git\ng\tc-dir\t{at}\ng\tc-other\t{at}/z\nnot-a-record\ng\tc-file\t{at}/q/../n.sh\n")).unwrap();
    let (files, dirs) = reads(&log, &root).unwrap();
    assert_eq!(
        files.into_iter().collect::<Vec<_>>(),
        ["n.sh", "scripts/m.py"]
    );
    assert!(dirs.is_empty());
    assert_eq!(relpath("/a/b/c", Path::new("/a/d")), "../b/c");
    assert_eq!(
        super::rel("/r/__pycache__/x.txt", Path::new("/r")),
        "__pycache__/x.txt"
    );
}

#[test]
fn a_state_is_its_id_or_what_stands_there() {
    let (base, root, gitdir) = world("states");
    std::fs::create_dir_all(root.join("sub")).unwrap();
    git(&root, &["add", "a.sh"]);
    std::fs::write(root.join("a.sh"), "changed\n").unwrap();
    std::fs::write(root.join("new.sh"), "new\n").unwrap();
    let now = super::Now::of(&root);
    assert_eq!(now.file_state("nope"), "absent");
    assert_eq!(now.file_state("sub"), "dir");
    assert_eq!(now.file_state("a.sh").len(), 40,);
    assert_eq!(now.file_state("new.sh").len(), 40,);
    assert_eq!(now.dir_state("nope"), "[]");
    assert_eq!(super::hash_file(&root.join("nope")), "gone");
    assert_eq!(
        super::hash_file(&root.join("new.sh")),
        "3e757656cf36eca53338e520d134963a44f793f8",
    );
    drop((base, gitdir));
}

#[test]
fn a_trace_by_another_python_or_recorder_is_not_believed() {
    let (base, root, gitdir) = world("versions");
    let (old, new) = (
        script(&base.join("old"), "printf 3.11"),
        script(&base.join("new"), "printf 3.14"),
    );
    let log = base.join("reads");
    std::fs::write(&log, format!("g\tc-file\t{}/a.sh\n", root.display())).unwrap();
    stamp(&root, &gitdir, "g", &log, &root, &old);
    let guards = names(&["g"]);
    assert_eq!(fresh(&root, &gitdir, &root, &guards, &old), ["g"]);
    assert!(fresh(&root, &gitdir, &root, &guards, &new).is_empty());
    let source = root.join("tests/tooling/_deps_site/l7r_file_log.c");
    std::fs::create_dir_all(source.parent().unwrap()).unwrap();
    std::fs::write(&source, "int x;\n").unwrap();
    assert!(fresh(&root, &gitdir, &root, &guards, &old).is_empty());
    assert!(fresh(&root, &gitdir, &root, &guards, "/no/such/python").is_empty());
}

#[test]
fn the_recorder_is_built_once_per_version_of_its_source() {
    let (base, root, gitdir) = world("shim");
    let compiler = script(
        &base.join("cc"),
        "for a in \"$@\"; do [ \"$prev\" = -o ] && echo so > \"$a\"; prev=$a; done",
    );
    assert_eq!(shim(&root, &gitdir, &compiler), "", "no source");
    let source = root.join("tests/tooling/_deps_site/l7r_file_log.c");
    std::fs::create_dir_all(source.parent().unwrap()).unwrap();
    std::fs::write(&source, "int x;\n").unwrap();
    let broken = script(&base.join("broken"), "exit 1");
    assert_eq!(shim(&root, &gitdir, &broken), "");
    assert_eq!(shim(&root, &gitdir, "/no/such/compiler"), "");
    let built = shim(&root, &gitdir, &compiler);
    assert!(
        Path::new(&built).extension().is_some_and(|e| e == "so") && Path::new(&built).is_file()
    );
    assert_eq!(shim(&root, &gitdir, &broken), built, "built once");
}

#[test]
fn a_git_that_answers_nothing_is_an_empty_tree() {
    let (base, _, gitdir) = world("nogit");
    let outside = base.join("not-a-repo");
    std::fs::create_dir_all(&outside).unwrap();
    assert!(super::Now::of(&outside).ids.is_empty());
    drop(gitdir);
}

#[test]
fn the_command_line() {
    let (base, root, gitdir) = world("cli");
    let log = base.join("reads");
    std::fs::write(&log, format!("g\tc-file\t{}/a.sh\n", root.display())).unwrap();
    let (r, g, l) = (
        root.to_str().unwrap(),
        gitdir.to_str().unwrap(),
        log.to_str().unwrap(),
    );
    let ask = |words: &[&str]| answer(&root, &names(words), "false", "python3");
    assert_eq!(ask(&["stamp", g, "g", l, r]).code, 0);
    assert_eq!(ask(&["fresh", g, r, "g"]).stdout, "g\n");
    assert_eq!(ask(&["fresh", g, r, "absent"]).stdout, "\n");
    assert_eq!(ask(&["shim", g]).stdout, "\n");
    assert_eq!(ask(&["bogus"]).code, 2);
    assert_eq!(ask(&[]).code, 2);
    assert_eq!(cli(&names(&["bogus"])).code, 2);
}
