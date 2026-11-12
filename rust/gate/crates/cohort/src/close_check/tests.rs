//! `l7r-gate close-check` on scratch repositories: every form, the usage log, every raise (feature 449 T127). The same outputs as
//! `scripts/gates/close_check.py` are the differential's (`scratchpad/t127/diff.py`); these pin the branches.

use std::path::Path;
use std::process::Command;

use l7r_gate_reviews::reviews::closing::Tools;

use super::{cli, cli_in, resolve, USAGE};
use crate::checks::scratch;
use crate::Reply;

fn git(root: &Path, args: &[&str]) {
    let done = Command::new("git")
        .arg("-C")
        .arg(root)
        .args(["-c", "user.email=t@t", "-c", "user.name=t"])
        .args(args)
        .output()
        .unwrap();
    assert!(done.status.success(), "{args:?}");
}

fn put(root: &Path, rel: &str, text: &str) {
    let p = root.join(rel);
    std::fs::create_dir_all(p.parent().unwrap()).unwrap();
    std::fs::write(p, text).unwrap();
}

/// A repository whose `origin/main` is its first commit, with an `impl_check.py` stand-in that owes nothing.
fn repo(tag: &str) -> l7r_guard::shared::tempdir::Held<std::path::PathBuf> {
    let tmp = scratch(tag);
    let root = std::fs::canonicalize(&tmp).unwrap();
    git(&root, &["init", "-q", "-b", "main"]);
    put(
        &root,
        "scripts/record/impl_check.py",
        "import json, sys\nprint(json.dumps([[] for a in sys.argv[2:]]))\n",
    );
    put(&root, "specs/100-old/tasks.md", "- [x] T1\n");
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "base"]);
    git(&root, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
    tmp.hold(root)
}

fn run(root: &Path, words: &[&str]) -> Reply {
    let tools = Tools {
        tree: root,
        python: "python3",
    };
    let args: Vec<String> = words.iter().map(|w| (*w).to_owned()).collect();
    cli_in(&args, &tools, root)
}

/// The outcomes the usage log recorded, in order.
fn usage(root: &Path) -> Vec<String> {
    std::fs::read_to_string(root.join(".git/tool-usage.jsonl"))
        .unwrap_or_default()
        .lines()
        .map(|l| {
            let v: serde_json::Value = serde_json::from_str(l).unwrap();
            assert_eq!(v["tool"], "close_check");
            v["outcome"].as_str().unwrap().to_owned()
        })
        .collect()
}

#[test]
fn a_feature_s_reasons_one_a_line() {
    let root = repo("close-one");
    put(&root, "specs/200-a/spec.md", "x\n");
    put(&root, "specs/201-b/spec.md", "Carried: SC-001 -> 200 key\n");
    let got = run(&root, &["specs/../specs/200-a"]);
    assert_eq!(
        (got.code, got.stdout.as_str()),
        (1, "200-a has no report.md - `make feature-report F=200 WRITE=1` writes it (FR-009)\n201-b's SC-001 is carried here and `key` is not in 200-a/measurements.json (FR-014)\n")
    );
    put(&root, "specs/200-a/report.md", "r");
    put(&root, "specs/200-a/measurements.json", r#"{"key": 1}"#);
    assert_eq!(run(&root, &["specs/200-a"]).code, 0);
    assert_eq!(usage(&root), ["refused", "passed"]);
    // the same reasons as JSON, no usage line
    let got = run(&root, &["--reasons-json", "specs/201-b", "specs"]);
    assert_eq!(
        got.stdout,
        "[\"201-b has no report.md - `make feature-report F=201 WRITE=1` writes it (FR-009)\"]\n"
    );
    assert!(run(&root, &["--reasons-json", "specs/x-b", "specs"])
        .stderr
        .starts_with("Traceback (most recent call last):\n  l7r-gate close-check\nValueError"));
    // a passing run's warning passes through on the command line, as the import let it (feature 449 T127)
    put(
        &root,
        "scripts/record/impl_check.py",
        "import json, sys\nsys.stderr.write('a warning\\n')\nprint(json.dumps([[] for a in sys.argv[2:]]))\n",
    );
    assert_eq!(
        run(&root, &["--reasons-json", "specs/201-b", "specs"]).stderr,
        "a warning\n"
    );
    assert_eq!(run(&root, &["specs/201-b"]).stderr, "a warning\n");
    // impl_check raising: what it printed comes first, as the import's stderr did, and the command's own trace closes it
    put(
        &root,
        "scripts/record/impl_check.py",
        "import sys\nsys.stderr.write('a warning\\n')\nraise ValueError('the claims door is shut')\n",
    );
    let got = run(&root, &["--reasons-json", "specs/201-b", "specs"]);
    assert_eq!(got.code, 1);
    let want = "ValueError: the claims door is shut\nTraceback (most recent call last):\n  l7r-gate close-check\nimpl_check.missing raised";
    assert!(got
        .stderr
        .starts_with("a warning\nTraceback (most recent call last):\n  File"));
    assert!(got.stderr.contains(want));
    // a raise records nothing: the two runs above and the warned one
    assert!(run(&root, &["x"]).stderr.contains("ValueError"));
    assert_eq!(usage(&root).len(), 3);
}

#[test]
fn the_usage_text_and_the_carries() {
    let root = repo("close-usage");
    for words in [&[][..], &["a", "b"], &["--reasons-json", "x"]] {
        let got = run(&root, words);
        assert_eq!((got.code, got.stderr.as_str()), (2, USAGE));
    }
    put(&root, "specs/201-b/spec.md", "Carried: SC-001 -> 200 key\n");
    let got = run(&root, &["--carries", "extra"]);
    assert_eq!(
        (got.code, got.stdout.as_str()),
        (0, "201-b SC-001 -> 200 `key`\n")
    );
    assert_eq!(usage(&root), ["refused", "refused", "refused", "passed"]);
    std::fs::create_dir_all(root.join("specs/202-c/spec.md")).unwrap();
    assert!(run(&root, &["--carries"]).stderr.contains("OSError"));
}

#[test]
fn the_push_asks_every_touched_feature_that_reads_closed() {
    let root = repo("close-push");
    put(&root, "specs/200-a/tasks.md", "- [x] T1\n");
    put(&root, "specs/201-b/tasks.md", "- [ ] T1\n");
    put(&root, "specs/202-c/tasks.md", "- [x] T1\n");
    put(&root, "specs/202-c/report.md", "r");
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "touch"]);
    git(&root, &["rm", "-rq", "specs/100-old"]);
    git(&root, &["commit", "-qm", "gone"]);
    let want = "200-a has no report.md - `make feature-report F=200 WRITE=1` writes it (FR-009)\n";
    assert_eq!(run(&root, &["--push"]).stdout, want);
    assert_eq!(run(&root, &["--push", "HEAD~1...HEAD", "ignored"]).code, 0);
    // a broken vocabulary fails every state, as `--each-state` did
    put(&root, ".specify/affects.json", "{");
    assert!(run(&root, &["--push"])
        .stderr
        .contains("speckit-todo --each-state"));
}

#[test]
fn the_grandfathered_list_is_written_from_the_closed_features() {
    let root = repo("close-old");
    put(&root, "specs/200-a/tasks.md", "- [ ] T1\n");
    put(&root, "specs/file", "");
    std::fs::create_dir_all(root.join("scripts/gates")).unwrap();
    let got = run(&root, &["--write-grandfathered"]);
    assert_eq!(
        got.stdout,
        "close-check: 1 feature(s) closed before the check\n"
    );
    let list = root.join("scripts/gates/closed-before-375.txt");
    assert_eq!(std::fs::read_to_string(&list).unwrap(), "100-old\n");
    assert_eq!(run(&root, &["specs/100-old"]).code, 0);
    put(&root, ".specify/affects.json", "{");
    assert!(run(&root, &["--write-grandfathered"])
        .stderr
        .contains("Traceback"));
    std::fs::remove_file(root.join(".specify/affects.json")).unwrap();
    // an unreadable specs directory, and a list that cannot be written, raise
    std::fs::set_permissions(
        root.join("specs"),
        std::os::unix::fs::PermissionsExt::from_mode(0o000),
    )
    .unwrap();
    let unreadable = run(&root, &["--write-grandfathered"]);
    std::fs::set_permissions(
        root.join("specs"),
        std::os::unix::fs::PermissionsExt::from_mode(0o755),
    )
    .unwrap();
    assert!(
        unreadable.stderr.contains("OSError"),
        "{}",
        unreadable.stderr
    );
    std::fs::remove_file(&list).unwrap();
    std::fs::create_dir_all(&list).unwrap();
    assert!(run(&root, &["--write-grandfathered"])
        .stderr
        .contains("OSError"));
    // no specs directory: an empty list
    std::fs::remove_dir(&list).unwrap();
    let elsewhere = root.join("scripts");
    let tools = Tools {
        tree: &root,
        python: "python3",
    };
    let got = cli_in(&["--write-grandfathered".to_owned()], &tools, &elsewhere);
    assert_eq!(
        got.stdout,
        "close-check: 0 feature(s) closed before the check\n"
    );
    assert_eq!(std::fs::read_to_string(&list).unwrap(), "\n");
}

#[test]
fn a_path_resolves_as_pathlib_resolves_it() {
    let root = repo("close-resolve");
    std::os::unix::fs::symlink(root.join("specs"), root.join("link")).unwrap();
    assert_eq!(resolve("link/100-old", &root), root.join("specs/100-old"));
    assert_eq!(resolve("/a/./b/../c", &root), Path::new("/a/c"));
    assert_eq!(resolve("no/../x", &root), root.join("x"));
}

#[test]
fn the_process_form_reads_its_working_directory() {
    // run where the tests run: `x` is no number, so the reasons raise before anything is asked or recorded
    assert_eq!(
        cli(&[
            "--reasons-json".to_owned(),
            "x".to_owned(),
            "/no/specs".to_owned()
        ])
        .code,
        1
    );
}
