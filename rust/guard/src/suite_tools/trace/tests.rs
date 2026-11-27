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
    // written by `install`, never this process: a script it wrote itself can be "Text file busy" when run (451 T160)
    crate::guards::write_executable(at, &format!("#!/bin/bash\n{body}\n"));
    at.to_string_lossy().into_owned()
}

fn names(guards: &[&str]) -> Vec<String> {
    guards.iter().map(|g| (*g).to_owned()).collect()
}

fn at(guard: &str, key: &str) -> (String, String) {
    (guard.to_owned(), key.to_owned())
}

/// Feature 451 T304: two trees of different content, run in turn, each keep their trace - the suite is fresh in each at its own key,
/// whichever ran last; the oldest trace past the bound goes, and the one trace a suite before T304 goes at the next stamp.
#[test]
fn trees_of_different_content_keep_each_others_traces() {
    let (base, root, gitdir) = world("two-trees");
    let log = base.join("reads");
    std::fs::write(&log, format!("g\tc-file\t{}/a.sh\n", root.display())).unwrap();
    let legacy = gitdir.join("hooks-test/g.trace.json");
    std::fs::create_dir_all(legacy.parent().unwrap()).unwrap();
    std::fs::write(&legacy, "{}").unwrap();
    let fresh_now = || fresh(&root, &gitdir, &root, &names(&["g"]));
    stamp(&root, &gitdir, "g", "ka", 2, &log, &root);
    assert!(!legacy.exists());
    std::fs::write(root.join("a.sh"), "the other tree's\n").unwrap();
    assert!(fresh_now().is_empty());
    std::thread::sleep(std::time::Duration::from_millis(20));
    stamp(&root, &gitdir, "g", "kb", 2, &log, &root);
    assert_eq!(fresh_now(), [at("g", "kb")]);
    std::fs::write(root.join("a.sh"), "one\n").unwrap();
    assert_eq!(fresh_now(), [at("g", "ka")]);
    std::fs::write(root.join("a.sh"), "a third\n").unwrap();
    std::thread::sleep(std::time::Duration::from_millis(20));
    stamp(&root, &gitdir, "g", "kc", 2, &log, &root);
    assert!(!trace_file(&gitdir, "g", "ka").exists() && trace_file(&gitdir, "g", "kb").exists());
    std::fs::write(root.join("a.sh"), "one\n").unwrap();
    assert!(fresh_now().is_empty());
    std::fs::write(gitdir.join("hooks-test/traces/g@kd.json"), "not json").unwrap();
    std::fs::write(gitdir.join("hooks-test/traces/g@notes.txt"), "").unwrap();
    std::fs::write(root.join("a.sh"), "the other tree's\n").unwrap();
    assert_eq!(fresh_now(), [at("g", "kb")]);
}

#[test]
fn a_suites_reads_are_kept_and_judged_by_content() {
    let (base, root, gitdir) = world("kept");
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
    stamp(&root, &gitdir, "g-hooks.sh", "k1", 6, &log, &root);
    let fresh_now = || fresh(&root, &gitdir, &root, &names(&["g-hooks.sh", "other.sh"]));
    assert_eq!(fresh_now(), [at("g-hooks.sh", "k1")]);
    std::fs::write(root.join("d/b.sh"), "new\n").unwrap();
    assert!(fresh_now().is_empty(),);
    std::fs::remove_file(root.join("d/b.sh")).unwrap();
    assert_eq!(fresh_now(), [at("g-hooks.sh", "k1")]);
    std::fs::write(root.join("a.sh"), "two\n").unwrap();
    assert!(fresh_now().is_empty(), "a read changed: the suite runs");
    assert!(fresh(&root, &gitdir, &root, &names(&["other.sh"])).is_empty());
}

#[test]
fn a_stamp_keeps_the_files_dirs_and_recorder() {
    let (base, root, gitdir) = world("kept");
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
    stamp(&root, &gitdir, "g", "k1", 6, &log, &root);
    let kept: serde_json::Value =
        serde_json::from_str(&std::fs::read_to_string(trace_file(&gitdir, "g", "k1")).unwrap())
            .unwrap();
    assert_eq!(kept["dirs"]["d"], "[\"x y.txt\"]");
    assert_eq!(kept["files"]["a.sh"].as_str().unwrap().len(), 40);
    assert_eq!(kept["recorder"], "");
    assert!(kept.get("py").is_none());
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
    stamp(&root, &gitdir, "g", "k1", 6, &log, &root);
    assert!(!trace_file(&gitdir, "g", "k1").exists(),);
    assert_eq!(reads(&base.join("absent"), &root), Some(Default::default()));
    std::fs::write(root.join(".gitignore"), "ignored.txt\n").unwrap();
    std::fs::write(root.join("ignored.txt"), "x").unwrap();
    std::fs::write(
        &log,
        format!("g\tc-file\t{0}/ignored.txt\n", root.display()),
    )
    .unwrap();
    stamp(&root, &gitdir, "g", "k1", 6, &log, &root);
    assert!(!trace_file(&gitdir, "g", "k1").exists(),);
    std::fs::write(&log, "").unwrap();
    stamp(&root, &gitdir, "g", "k1", 6, &log, &root);
    assert!(!trace_file(&gitdir, "g", "k1").exists(),);
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
fn a_trace_by_another_recorder_is_not_believed() {
    let (base, root, gitdir) = world("versions");
    let log = base.join("reads");
    std::fs::write(&log, format!("g\tc-file\t{}/a.sh\n", root.display())).unwrap();
    stamp(&root, &gitdir, "g", "k1", 6, &log, &root);
    let guards = names(&["g"]);
    assert_eq!(fresh(&root, &gitdir, &root, &guards), [at("g", "k1")]);
    let source = root.join("tests/tooling/_deps_site/l7r_file_log.c");
    std::fs::create_dir_all(source.parent().unwrap()).unwrap();
    std::fs::write(&source, "int x;\n").unwrap();
    assert!(fresh(&root, &gitdir, &root, &guards).is_empty());
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
    let ask = |words: &[&str]| answer(&root, &names(words), "false");
    assert_eq!(ask(&["stamp", g, "g", "k1", "6", l, r]).code, 0);
    assert_eq!(ask(&["stamp", g, "g", "k2", "not-a-number", l, r]).code, 0);
    assert_eq!(ask(&["fresh", g, r, "g"]).stdout, "g k2\n");
    assert_eq!(ask(&["fresh", g, r, "absent"]).stdout, "");
    assert_eq!(ask(&["stamp", g, "g", l, r]).code, 2);
    assert_eq!(ask(&["shim", g]).stdout, "\n");
    assert_eq!(ask(&["bogus"]).code, 2);
    assert_eq!(ask(&[]).code, 2);
    assert_eq!(cli(&names(&["bogus"])).code, 2);
}
