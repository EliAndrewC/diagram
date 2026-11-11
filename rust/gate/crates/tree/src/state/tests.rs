//! The record's rules on fixture repositories; the hashes against the Python they replaced are `m:t72-state`.

use std::path::{Path, PathBuf};
use std::process::Command;

use super::{
    already_verified, cli, read, record_tooling, second_red_gate, state_file, tooling_hash, utc,
    write, FAILED, GREEN,
};

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

/// A repository whose `.py` ids come from a shell stand-in, one commit in.
fn repo(tag: &str) -> (l7r_guard::shared::tempdir::TempDir, PathBuf, String) {
    let dir = l7r_guard::shared::tempdir::TempDir::new(&format!("gate-state-{tag}"));
    git(&dir, &["init", "-q", "-b", "main"]);
    git(&dir, &["config", "user.email", "t@t"]);
    git(&dir, &["config", "user.name", "t"]);
    let python = dir.join(".git/stand-in");
    std::fs::write(&python, "#!/bin/bash\nif [ \"$2\" = --semantic ]; then shift 3; for f in \"$@\"; do printf '2\\nxx'; done; else shift 2; for f in \"$@\"; do sha1sum \"$f\" | cut -d' ' -f1; done; fi\n").unwrap();
    Command::new("chmod")
        .arg("+x")
        .arg(&python)
        .status()
        .unwrap();
    put(&dir, "a.py", "x = 1\n");
    put(&dir, "scripts/s.sh", "true\n");
    git(&dir, &["add", "a.py", "scripts/s.sh"]);
    git(&dir, &["commit", "-qm", "c"]);
    let at = dir.to_path_buf();
    (dir, at, python.to_string_lossy().into_owned())
}

fn ask(dir: &Path, python: &str, args: &[&str]) -> crate::Reply {
    cli(
        &args.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>(),
        dir,
        python,
    )
}

#[test]
fn a_worktree_keeps_its_record_in_its_own_git_directory() {
    let dir = l7r_guard::shared::tempdir::TempDir::new("gate-state-wt");
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
    let (_dir, dir, py) = repo("subset");
    let gate = write(&dir, GREEN, "done", false, &py).unwrap();
    assert!(!gate.tooling.is_empty() && !gate.commit.is_empty());
    assert_eq!(write(&dir, GREEN, "quick", false, &py).unwrap(), gate);
    assert_eq!(read(&dir).unwrap().unwrap(), gate);
    put(&dir, "a.py", "x = 2\n");
    let later = write(&dir, GREEN, "quick", false, &py).unwrap();
    assert_eq!(
        (later.target.as_str(), later.tooling.as_str()),
        ("quick", gate.tooling.as_str())
    );
    let text = std::fs::read_to_string(state_file(&dir)).unwrap();
    assert!(
        text.starts_with("{\n  \"event\": \"green-local\",\n  \"target\": \"quick\",")
            && text.ends_with("}\n")
    );
}

#[test]
fn only_a_green_gate_that_ran_vouches_for_the_tooling() {
    let (_dir, dir, py) = repo("tooling");
    assert_eq!(write(&dir, GREEN, "quick", false, &py).unwrap().tooling, "");
    assert_eq!(write(&dir, FAILED, "done", false, &py).unwrap().tooling, "");
    assert_eq!(write(&dir, GREEN, "done", true, &py).unwrap().tooling, "");
    assert_eq!(
        write(&dir, GREEN, "done", false, &py).unwrap().tooling,
        tooling_hash(&dir, &py).unwrap()
    );
    assert!(write(&dir, "nonsense", "done", false, &py)
        .unwrap_err()
        .contains("unknown verification event"));
}

#[test]
fn a_second_red_gate_in_a_row_owes_the_arbiter_and_a_first_does_not() {
    let (_dir, dir, py) = repo("red");
    let owed = dir.join(".git/arbiter-owed.json");
    write(&dir, FAILED, "done", false, &py).unwrap();
    assert!(!owed.exists());
    write(&dir, FAILED, "quick", false, &py).unwrap();
    assert!(!owed.exists());
    write(&dir, FAILED, "done", false, &py).unwrap();
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
    write(&dir, GREEN, "done", false, &py).unwrap();
    assert_eq!(
        std::fs::read_to_string(dir.join(".git/last-gate")).unwrap(),
        "green-local\n"
    );
}

#[test]
fn the_tooling_can_be_vouched_for_with_or_without_a_record() {
    let (_dir, dir, py) = repo("vouch");
    let hash = record_tooling(&dir, &py).unwrap();
    let st = read(&dir).unwrap().unwrap();
    assert_eq!(
        (
            st.target.as_str(),
            st.tooling.as_str(),
            st.engine_key.as_str()
        ),
        ("tooling", hash.as_str(), "")
    );
    write(&dir, FAILED, "quick", false, &py).unwrap();
    record_tooling(&dir, &py).unwrap();
    let kept = read(&dir).unwrap().unwrap();
    assert_eq!(
        (kept.event.as_str(), kept.tooling.as_str()),
        (FAILED, hash.as_str())
    );
}

#[test]
fn only_a_green_gate_on_exactly_this_content_is_reused() {
    let (_dir, dir, py) = repo("reuse");
    let why = |d: &Path| already_verified(d, &py).unwrap();
    assert_eq!(
        why(&dir),
        (false, "no local check recorded in this clone".to_owned())
    );
    write(&dir, GREEN, "quick", false, &py).unwrap();
    assert!(why(&dir)
        .1
        .contains("only a green `make done` can be reused"));
    write(&dir, GREEN, "done", false, &py).unwrap();
    assert!(why(&dir).0 && why(&dir).1.starts_with("already verified"));
    put(&dir, "pool/a.json", "{}\n");
    assert!(why(&dir).1.contains("a pool gen or manifest changed"));
    write(&dir, GREEN, "done", false, &py).unwrap();
    put(&dir, "b.py", "y = 1\n");
    assert!(why(&dir).1.contains("the skill's Python changed"));
}

#[test]
fn the_command_line_answers_and_refuses() {
    let (_dir, dir, py) = repo("cli");
    assert_eq!(ask(&dir, &py, &["read"]).stdout, "null\n");
    assert_eq!(
        ask(&dir, &py, &["write", GREEN, "quick"]).stdout,
        "verification-state: green-local (quick) recorded\n"
    );
    assert_eq!(ask(&dir, &py, &["write", GREEN, "done", "reused"]).code, 0);
    assert!(ask(&dir, &py, &["read"])
        .stdout
        .contains("\"target\":\"done\""));
    assert!(Path::new(ask(&dir, &py, &["dir"]).stdout.trim()).ends_with(".git"));
    assert_eq!(ask(&dir, &py, &["verified-done"]).code, 0);
    assert_eq!(ask(&dir, &py, &["write", FAILED, "quick"]).code, 0);
    assert_eq!(ask(&dir, &py, &["verified-done"]).code, 1);
    assert!(ask(&dir, &py, &["tooling-green"])
        .stdout
        .starts_with("tooling: recorded green for "));
    assert_eq!(ask(&dir, &py, &["tooling-hash"]).stdout.trim().len(), 64);
    assert_eq!(ask(&dir, &py, &["write", GREEN]).code, 2);
    assert!(ask(&dir, &py, &["write", "x", "y"])
        .stderr
        .starts_with("l7r-gate state: unknown"));
    std::fs::write(state_file(&dir), "not json").unwrap();
    assert!(read(&dir).is_err());
    assert_eq!(utc(0.0), "1970-01-01T00:00:00Z");
}
