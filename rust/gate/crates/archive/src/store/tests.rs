//! The working copy (feature 449 T146), on a local bare remote: each write and its commit, the lock, the push.

use std::path::Path;

use super::{b64, first_chars, git_env, py_g, py_list, remote, token_from, Archive};
use crate::testkit::{git, World};

#[test]
fn the_pat_goes_as_a_header_and_the_token_is_the_gates() {
    let env = git_env("t0k");
    assert_eq!(env[0], ("GIT_CONFIG_COUNT".to_owned(), "1".to_owned()));
    assert_eq!(
        env[2].1,
        format!("AUTHORIZATION: basic {}", b64(b"x-access-token:t0k"))
    );
    assert_eq!(b64(b"x-access-token:t0k"), "eC1hY2Nlc3MtdG9rZW46dDBr");
    assert_eq!(
        [b64(b""), b64(b"a"), b64(b"ab"), b64(b"abc")],
        ["", "YQ==", "YWI=", "YWJj"]
    );
    assert_eq!(
        remote(),
        "https://github.com/EliAndrewC/diagram-research.git"
    );
    let w = World::new("store-token");
    let gate = w.dir.path().join("gate.sh");
    // written by `install`, never this process: a script it wrote itself can be "Text file busy" when run (451 T160)
    l7r_gate_core::write_executable(
        &gate,
        "#!/bin/sh\necho \"  secret-$1 in $(basename \"$PWD\")  \"\n",
    );
    // the gate's `github-token`, run in the mirror, its words stripped; none where the gate cannot run
    assert_eq!(
        token_from(&gate, &w.dir.path().join("m")),
        "secret-github-token in m"
    );
    assert_eq!(token_from(Path::new("/no/such/gate"), w.dir.path()), "");
    assert_eq!(
        (first_chars("abcdef", 3), py_g(600.0), py_g(0.5)),
        ("abc".to_owned(), "600".to_owned(), "0.5".to_owned())
    );
    assert_eq!(py_list(&["git", "it's"]), "['git', \"it's\"]");
}

#[test]
fn a_capture_lands_once_in_its_own_directory_and_the_counter_counts_it() {
    let w = World::new("store-put");
    let store = w.store();
    assert_eq!(store.unpushed(), 0);
    let files = vec![("a.txt".to_owned(), b"aaaa".to_vec())];
    assert_eq!(
        store.put("ab/abc/T1", &files, "first").unwrap(),
        "ab/abc/T1"
    );
    assert_eq!(
        store.put("ab/abc/T1", &files, "second").unwrap(),
        "ab/abc/T1-2"
    );
    assert_eq!(
        store.put("ab/abc/T1", &files, "third").unwrap(),
        "ab/abc/T1-3"
    );
    assert_eq!(store.unpushed(), 12);
    assert_eq!(w.subjects()[..3], ["third", "second", "first"]);
    std::fs::write(w.home.join("source-archive.unpushed"), "x").unwrap();
    assert_eq!(store.unpushed(), 0);
    assert_eq!(store.push().unwrap(), "");
    assert_eq!(
        std::fs::read_to_string(w.home.join("source-archive.unpushed")).unwrap(),
        "0"
    );
    assert!(git(&w.remote, &["log", "--format=%s"]).starts_with("third"));
}

/// A file once, a folder once, each committed with its bytes counted: apart from the captures above, whose commits and push it never
/// read, on a world of its own - the two together were past FR-008's tenth of a second (feature 449 T167).
#[test]
fn the_gms_copy_lands_once_and_its_bytes_are_counted() {
    let w = World::new("store-copy");
    let store = w.store();
    std::fs::write(w.gm.join("f.pdf"), b"pdf!").unwrap();
    std::fs::create_dir_all(w.gm.join("dir/sub")).unwrap();
    std::fs::write(w.gm.join("dir/x"), b"12").unwrap();
    std::fs::write(w.gm.join("dir/sub/y"), b"345").unwrap();
    assert!(store
        .copy_in("gm-copies/f.pdf", &w.gm.join("f.pdf"))
        .unwrap());
    assert!(!store
        .copy_in("gm-copies/f.pdf", &w.gm.join("f.pdf"))
        .unwrap());
    assert!(store
        .copy_in("gm-copies/deep/dir", &w.gm.join("dir"))
        .unwrap());
    assert_eq!(
        std::fs::read(store.dir.join("gm-copies/deep/dir/sub/y")).unwrap(),
        b"345"
    );
    assert_eq!(store.unpushed(), 9);
    store
        .put_file("gm-copies/f.pdf.txt", b"text", "the text")
        .unwrap();
    store
        .put_file("gm-copies/f.pdf.txt", b"again", "never")
        .unwrap();
    assert_eq!(
        std::fs::read(store.dir.join("gm-copies/f.pdf.txt")).unwrap(),
        b"text"
    );
    assert_eq!(w.subjects()[0], "the text");
    assert!(store
        .copy_in("gm-copies/missing", &w.gm.join("missing"))
        .is_err());
}

#[test]
fn ensure_clones_once_a_push_that_fails_says_why_and_the_lock_waits() {
    let w = World::new("store-ensure");
    let store = w.store();
    std::fs::remove_dir_all(&store.dir).unwrap();
    store.ensure().unwrap();
    store.ensure().unwrap();
    assert_eq!(
        git(&store.dir, &["config", "user.name"]).trim(),
        "diagram source archive"
    );
}

/// An empty remote: the clone is put on `main`, and a push with nothing committed is no failure. What was one test of the store's
/// clone, its push and its lock is one of each, every part on a scratch directory of its own - the four clones and the lock's wait
/// together were twice FR-008's tenth of a second (feature 449 T167).
#[test]
fn an_empty_remote_is_cloned_onto_main_and_its_push_is_no_failure() {
    let w = l7r_shared::tempdir::TempDir::new("archive-store-empty");
    let empty = w.path().join("empty.git");
    git(w.path(), &["init", "-q", "--bare", empty.to_str().unwrap()]);
    let mut fresh = Archive::new(
        &w.path().join("fresh"),
        Some(vec![("GIT_TERMINAL_PROMPT".into(), "0".into())]),
    );
    fresh.remote = empty.to_string_lossy().into_owned();
    fresh.ensure().unwrap();
    assert_eq!(
        git(&fresh.dir, &["symbolic-ref", "--short", "HEAD"]).trim(),
        "main"
    );
    assert_eq!(fresh.push().unwrap(), "");
}

#[test]
fn a_remote_that_is_not_there_is_not_cloned() {
    let w = l7r_shared::tempdir::TempDir::new("archive-store-nowhere");
    let mut store = Archive::new(w.path(), None);
    store.remote = w.path().join("nowhere.git").to_string_lossy().into_owned();
    let err = store.ensure().unwrap_err();
    assert_eq!(err.kind, "RuntimeError");
    assert!(
        err.message
            .starts_with("could not clone the archive: fatal:"),
        "{}",
        err.message
    );
}

/// A push to a remote that is gone, the lock held and waited for, a git that fails.
#[test]
fn a_push_that_fails_says_why_and_the_lock_waits() {
    let w = World::new("store-push");
    let store = w.store();
    store
        .put("x/T", &[("f".to_owned(), b"1".to_vec())], "one")
        .unwrap();
    git(
        &store.dir,
        &["remote", "set-url", "origin", "/no/such/remote.git"],
    );
    let why = store.push().unwrap();
    assert!(why.contains("does not appear to be a git repository") || why.starts_with("fatal"));
    let held = store.locked(1.0).unwrap();
    // a hundredth of a second waited out where a tenth was, the whole of FR-008's bar (feature 449 T167)
    let err = store.locked(0.01).unwrap_err();
    assert_eq!(
        (err.kind, err.message.ends_with("within 0.01s")),
        ("TimeoutError", true)
    );
    drop(held);
    let mut nowhere = w.store();
    nowhere.home = w.home.join("file-not-dir");
    std::fs::write(&nowhere.home, "x").unwrap();
    assert_eq!(nowhere.locked(0.1).unwrap_err().kind, "OSError");
    let err = store.git(&["no-such-command"], true).unwrap_err();
    assert_eq!(err.kind, "CalledProcessError");
    assert!(
        err.message
            .contains("'no-such-command']' returned non-zero exit status 1."),
        "{}",
        err.message
    );
}

fn chmod(path: &Path, mode: &str) {
    std::process::Command::new("chmod")
        .arg(mode)
        .arg(path)
        .status()
        .unwrap();
}

#[test]
fn a_git_that_will_not_run_or_fails_silently() {
    let w = World::new("store-git");
    let mut store = w.store();
    store.git_program = "/no/such/git".to_owned();
    assert_eq!(store.git(&["status"], false).unwrap_err().kind, "OSError");
    std::fs::remove_dir_all(&store.dir).unwrap();
    assert_eq!(store.ensure().unwrap_err().kind, "OSError");
    let quiet = w.dir.path().join("quiet-git");
    std::fs::write(
        &quiet,
        "#!/bin/sh\nfor a in \"$@\"; do [ \"$a\" = push ] && exit 3; done\nexit 0\n",
    )
    .unwrap();
    chmod(&quiet, "+x");
    store.git_program = quiet.to_string_lossy().into_owned();
    assert_eq!(store.push().unwrap(), "git push exited 3");
}

#[test]
fn a_write_the_disk_refuses_is_an_os_error() {
    let w = World::new("store-disk");
    let store = w.store();
    std::fs::write(store.dir.join("blocker"), "a file").unwrap();
    assert_eq!(
        store
            .put("blocker/T", &[("f".to_owned(), vec![])], "m")
            .unwrap_err()
            .kind,
        "OSError"
    );
    assert_eq!(
        store.put_file("blocker/x/f", b"", "m").unwrap_err().kind,
        "OSError"
    );
    assert_eq!(
        store.copy_in("blocker/x/f", &w.gm).unwrap_err().kind,
        "OSError"
    );
    // a file name with a folder the capture does not make; the counter's file a folder
    assert_eq!(
        store
            .put("ok/T", &[("sub/f".to_owned(), vec![])], "m")
            .unwrap_err()
            .kind,
        "OSError"
    );
    std::fs::create_dir_all(w.home.join("source-archive.unpushed")).unwrap();
    assert_eq!(
        store
            .put("ok/U", &[("f".to_owned(), vec![])], "m")
            .unwrap_err()
            .kind,
        "OSError"
    );
    // a folder the copy cannot read, and one it cannot write into
    std::fs::create_dir_all(w.gm.join("locked/inner")).unwrap();
    chmod(&w.gm.join("locked"), "000");
    assert_eq!(
        store
            .copy_in("gm-copies/locked", &w.gm.join("locked"))
            .unwrap_err()
            .kind,
        "OSError"
    );
    chmod(&w.gm.join("locked"), "755");
    std::fs::create_dir_all(store.dir.join("readonly")).unwrap();
    chmod(&store.dir.join("readonly"), "555");
    assert_eq!(
        store
            .copy_in("readonly/locked", &w.gm.join("locked"))
            .unwrap_err()
            .kind,
        "OSError"
    );
    assert_eq!(
        store.put_file("readonly/f", b"x", "m").unwrap_err().kind,
        "OSError"
    );
    chmod(&store.dir.join("readonly"), "755");
    let mut gone = w.store();
    gone.dir = w.dir.path().join("no-dir/source-archive");
    std::fs::write(w.dir.path().join("no-dir"), "a file").unwrap();
    assert_eq!(gone.ensure().unwrap_err().kind, "OSError");
}
