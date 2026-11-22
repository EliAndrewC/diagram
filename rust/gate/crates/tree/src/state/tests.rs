//! The record's rules on fixture repositories; the hashes against the Python they replaced are `m:t72-state`.

use std::path::{Path, PathBuf};
use std::process::Command;

use super::{already_verified, cli, read, second_red_gate, state_file, utc, write, FAILED, GREEN};

fn git(dir: &Path, args: &[&str]) {
    assert!(Command::new("git")
        .arg("-C")
        .arg(dir)
        .args(args)
        .output()
        .unwrap()
        .status
        .success());
}

fn put(dir: &Path, rel: &str, text: &str) {
    let path = dir.join(rel);
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

/// A repository one commit in.
fn repo(tag: &str) -> (l7r_shared::tempdir::TempDir, PathBuf) {
    let dir = l7r_shared::tempdir::TempDir::new(&format!("gate-state-{tag}"));
    git(&dir, &["init", "-q", "-b", "main"]);
    git(&dir, &["config", "user.email", "t@t"]);
    git(&dir, &["config", "user.name", "t"]);
    put(&dir, "a.py", "x = 1\n");
    put(&dir, "scripts/s.sh", "true\n");
    git(&dir, &["add", "a.py", "scripts/s.sh"]);
    git(&dir, &["commit", "-qm", "c"]);
    let at = dir.to_path_buf();
    (dir, at)
}

fn ask(dir: &Path, args: &[&str]) -> crate::Reply {
    cli(
        &args.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>(),
        dir,
    )
}

#[test]
fn a_worktree_keeps_its_record_in_its_own_git_directory() {
    let dir = l7r_shared::tempdir::TempDir::new("gate-state-wt");
    std::fs::write(dir.join(".git"), "gitdir: /elsewhere/wt\n").unwrap();
    assert_eq!(
        state_file(&dir),
        Path::new("/elsewhere/wt/verification-state.json")
    );
    assert_eq!(read(&dir).unwrap(), None);
    std::fs::write(dir.join(".git"), "gitdir: ../rel\n").unwrap();
    assert_eq!(state_file(&dir), dir.join("../rel/verification-state.json"));
    std::fs::write(dir.join(".git"), "something else\n").unwrap();
    assert_eq!(state_file(&dir), dir.join(".git/verification-state.json"));
}

#[test]
fn a_green_gate_stands_against_a_green_subset_on_the_same_content() {
    let (_dir, dir) = repo("subset");
    let gate = write(&dir, GREEN, "done").unwrap();
    assert!(!gate.commit.is_empty() && !gate.engine_key.is_empty());
    assert_eq!(write(&dir, GREEN, "quick").unwrap(), gate);
    assert_eq!(read(&dir).unwrap().unwrap(), gate);
    put(&dir, "a.py", "x = 2\n");
    let later = write(&dir, GREEN, "quick").unwrap();
    assert_eq!(later.target, "quick");
    let text = std::fs::read_to_string(state_file(&dir)).unwrap();
    assert!(
        text.starts_with("{\n  \"event\": \"green-local\",\n  \"target\": \"quick\",")
            && text.ends_with("}\n")
    );
}

#[test]
fn an_unknown_event_is_refused() {
    let (_dir, dir) = repo("event");
    assert!(write(&dir, "nonsense", "done")
        .unwrap_err()
        .contains("unknown verification event"));
}

#[test]
fn a_second_red_gate_in_a_row_owes_the_arbiter_and_a_first_does_not() {
    let (_dir, dir) = repo("red");
    let owed = dir.join(".git/arbiter-owed.json");
    write(&dir, FAILED, "done").unwrap();
    assert!(!owed.exists());
    write(&dir, FAILED, "quick").unwrap();
    assert!(!owed.exists());
    write(&dir, FAILED, "done").unwrap();
    let text = std::fs::read_to_string(&owed).unwrap();
    assert!(
        text.contains("\"red-gate@")
            && text.contains(
                "\n  \"detail\": \"a second red make done in a row\",\n  \"kind\": \"red-gate\""
            ),
    );
    second_red_gate(&dir, 0.0).unwrap();
    let both: serde_json::Value =
        serde_json::from_str(&std::fs::read_to_string(&owed).unwrap()).unwrap();
    assert_eq!(both.as_object().unwrap().len(), 2);
    assert!(both.get(format!("red-gate@{}", utc(0.0))).is_some());
    write(&dir, GREEN, "done").unwrap();
    assert_eq!(
        std::fs::read_to_string(dir.join(".git/last-gate")).unwrap(),
        "green-local\n"
    );
}

#[test]
fn only_a_green_gate_on_exactly_this_content_is_reused() {
    let (_dir, dir) = repo("reuse");
    let why = |d: &Path| already_verified(d).unwrap();
    assert_eq!(
        why(&dir),
        (false, "no local check recorded in this clone".to_owned())
    );
    write(&dir, GREEN, "quick").unwrap();
    assert!(why(&dir)
        .1
        .contains("only a green `make done` can be reused"));
    write(&dir, GREEN, "done").unwrap();
    assert!(why(&dir).0 && why(&dir).1.starts_with("already verified"));
    put(&dir, "pool/a.json", "{}\n");
    assert!(why(&dir)
        .1
        .contains("the engine code it tested (Python, Rust, the pool's sources) changed"));
    write(&dir, GREEN, "done").unwrap();
    put(&dir, "b.py", "y = 1\n");
    assert!(why(&dir).1.contains("the engine code it tested"));
    // a record from before the engine key was kept vouches for nothing (the diagram area now holds every engine path, T224, so a
    // record whose hash stands differs only here)
    write(&dir, GREEN, "done").unwrap();
    let file = state_file(&dir);
    let mut kept: serde_json::Value =
        serde_json::from_str(&std::fs::read_to_string(&file).unwrap()).unwrap();
    kept["engine_key"] = "".into();
    std::fs::write(&file, kept.to_string()).unwrap();
    assert!(why(&dir).1.contains("it recorded no engine key"));
}

#[test]
fn the_command_line_answers_and_refuses() {
    let (_dir, dir) = repo("cli");
    assert_eq!(ask(&dir, &["read"]).stdout, "null\n");
    assert_eq!(
        ask(&dir, &["write", GREEN, "quick"]).stdout,
        "verification-state: green-local (quick) recorded\n"
    );
    assert_eq!(ask(&dir, &["write", GREEN, "done", "reused"]).code, 0);
    assert!(ask(&dir, &["read"]).stdout.contains("\"target\":\"done\""));
    assert!(Path::new(ask(&dir, &["dir"]).stdout.trim()).ends_with(".git"));
    assert_eq!(ask(&dir, &["verified-done"]).code, 0);
    assert_eq!(ask(&dir, &["write", FAILED, "quick"]).code, 0);
    assert_eq!(ask(&dir, &["verified-done"]).code, 1);
    assert_eq!(ask(&dir, &["write", GREEN]).code, 2);
    assert!(ask(&dir, &["write", "x", "y"])
        .stderr
        .starts_with("l7r-gate state: unknown"));
    std::fs::write(state_file(&dir), "not json").unwrap();
    assert!(read(&dir).is_err());
    assert_eq!(utc(0.0), "1970-01-01T00:00:00Z");
}
