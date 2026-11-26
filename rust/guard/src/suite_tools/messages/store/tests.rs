//! The tree's store and its filling (451 T281): each worktree has its own, a skipped suite's is filled from the rendering at its
//! stamp's key, and a file of no suite on the run's roster goes.

use std::path::Path;

use super::store;
use crate::shared::tempdir::TempDir;

fn run(args: &[&str]) -> crate::protocol::Reply {
    super::super::cli(&args.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>())
}

fn git(at: &Path, args: &[&str]) {
    let done = std::process::Command::new("git")
        .arg("-C")
        .arg(at)
        .args(["-c", "user.email=t@t", "-c", "user.name=t"])
        .args(args)
        .output()
        .unwrap();
    assert!(done.status.success(), "{args:?}: {done:?}");
}

fn put(dir: &Path, name: &str, text: &str) {
    std::fs::create_dir_all(dir).unwrap();
    std::fs::write(dir.join(name), text).unwrap();
}

fn names(dir: &Path) -> Vec<String> {
    let mut out: Vec<String> = std::fs::read_dir(dir)
        .unwrap()
        .map(|e| e.unwrap().file_name().to_string_lossy().into_owned())
        .collect();
    out.sort();
    out
}

#[test]
fn each_worktree_has_its_own_store_and_a_directory_outside_a_repository_none() {
    let d = TempDir::new("messages-store");
    let at = d.canonicalize().unwrap().join("main");
    std::fs::create_dir_all(&at).unwrap();
    git(&at, &["init", "-q"]);
    git(&at, &["commit", "-q", "--allow-empty", "-m", "base"]);
    let other = at.parent().unwrap().join("other");
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
    assert_eq!(store(&at).unwrap(), at.join(".git/hooks-test/messages"));
    // a linked worktree's `.git` is a file: its store is under its own git directory, never the common one
    assert_eq!(
        store(&other).unwrap(),
        at.join(".git/worktrees/other/hooks-test/messages")
    );
    let said = run(&["store", &other.to_string_lossy()]);
    assert_eq!(
        (said.code, said.stdout.trim()),
        (0, &*store(&other).unwrap().to_string_lossy())
    );
    assert!(store(Path::new("/")).is_none());
    let none = run(&["store", "/"]);
    assert_eq!(none.code, 1);
    assert!(
        none.stderr.contains("/ is in no git repository"),
        "{}",
        none.stderr
    );
}

#[test]
fn a_skipped_suite_is_filled_from_its_key_and_a_file_of_no_suite_on_the_list_goes() {
    let d = TempDir::new("messages-gather");
    let (rendered, tree, list) = (d.join("rendered"), d.join("tree"), d.join("list"));
    // the keyed renderings: a whole suite at two keys, a split suite's two shards, another guard's whose name this one's opens
    put(&rendered, "a-hooks.sh@k1.jsonl", "a at k1\n");
    put(&rendered, "a-hooks.sh@k0.jsonl", "a at k0\n");
    put(&rendered, "s-hooks.sh.1@k2.jsonl", "s1 at k2\n");
    put(&rendered, "s-hooks.sh.2@k2.jsonl", "s2 at k2\n");
    put(&rendered, "a-hooks.sh.extra@k1.jsonl", "not a shard\n");
    put(&rendered, "notes.txt", "no rendering\n");
    // the tree's store before the run: its own stale rendering of a, a shard s no longer has, a suite that ran, another tree's guard
    put(&tree, "a-hooks.sh.jsonl", "a, stale\n");
    put(&tree, "s-hooks.sh.1.jsonl", "s1, stale\n");
    put(&tree, "s-hooks.sh.3.jsonl", "s3, a shard since removed\n");
    put(&tree, "ran-hooks.sh.jsonl", "ran, written by its own job\n");
    put(&tree, "only-theirs-hooks.sh.jsonl", "another tree's\n");
    put(
        &tree,
        "only-theirs-hooks.sh.2.jsonl",
        "another tree's shard\n",
    );
    put(&tree, "keep.txt", "not a rendering\n");
    std::fs::write(&list, "a-hooks.sh k1\ns-hooks.sh k2\nran-hooks.sh\n\n").unwrap();
    let args = [
        "gather",
        &*rendered.to_string_lossy(),
        &*tree.to_string_lossy(),
        &*list.to_string_lossy(),
    ];
    let said = run(&args);
    assert_eq!((said.code, &*said.stdout, &*said.stderr), (0, "", ""));
    assert_eq!(
        names(&tree),
        [
            "a-hooks.sh.jsonl",
            "keep.txt",
            "ran-hooks.sh.jsonl",
            "s-hooks.sh.1.jsonl",
            "s-hooks.sh.2.jsonl"
        ]
    );
    let read = |n: &str| std::fs::read_to_string(tree.join(n)).unwrap();
    assert_eq!(read("a-hooks.sh.jsonl"), "a at k1\n");
    assert_eq!(read("s-hooks.sh.1.jsonl"), "s1 at k2\n");
    assert_eq!(read("s-hooks.sh.2.jsonl"), "s2 at k2\n");
    assert_eq!(read("ran-hooks.sh.jsonl"), "ran, written by its own job\n");
    // the keyed renderings are another tree's to read too: none is taken
    assert_eq!(names(&rendered).len(), 6);
}

#[test]
fn a_skipped_suite_whose_rendering_is_gone_fails_the_run_with_the_fix_and_keeps_its_files() {
    let d = TempDir::new("messages-gather-gone");
    let (rendered, tree, list) = (d.join("rendered"), d.join("tree"), d.join("list"));
    put(
        &rendered,
        "a-hooks.sh@k9.jsonl",
        "a at another tree's key\n",
    );
    // a rendering that cannot be copied (a directory in its place) is no rendering either
    std::fs::create_dir_all(rendered.join("b-hooks.sh@k1.jsonl")).unwrap();
    put(&tree, "a-hooks.sh.jsonl", "a, its last\n");
    std::fs::write(&list, "a-hooks.sh k1\nb-hooks.sh k1\n").unwrap();
    let said = run(&[
        "gather",
        &rendered.to_string_lossy(),
        &tree.to_string_lossy(),
        &list.to_string_lossy(),
    ]);
    assert_eq!(said.code, 1);
    assert!(
        said.stderr.starts_with(
            "guard-messages: a-hooks.sh, b-hooks.sh skipped as unchanged, but no rendering"
        ),
        "{}",
        said.stderr
    );
    assert!(
        said.stderr
            .ends_with("  fix: make hooks-test again, which reruns it\n"),
        "{}",
        said.stderr
    );
    assert_eq!(names(&tree), ["a-hooks.sh.jsonl"]);
    // no list and no directories: nothing to fill, nothing to remove, and the store is made
    let empty = d.join("empty");
    let said = run(&[
        "gather",
        &d.join("none").to_string_lossy(),
        &empty.to_string_lossy(),
        &d.join("no-list").to_string_lossy(),
    ]);
    assert_eq!(said.code, 0);
    assert!(names(&empty).is_empty());
    // either verb with the wrong count of arguments is the usage
    assert_eq!(run(&["gather", "x"]).code, 64);
    assert_eq!(run(&["store"]).code, 64);
}
