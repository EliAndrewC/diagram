//! The record's rules on fixture repositories; the hashes against the Python they replaced are `m:t72-state`.

use std::path::{Path, PathBuf};
use std::process::Command;

use super::{
    already_verified, cli, read, record, second_red_gate, state_file, utc, write, Run, FAILED,
    GREEN,
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
    second_red_gate(&dir, 0.0, &Run::default()).unwrap();
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

/// RED FIRST (feature 461 T84): the ruling of red-gate@2026-11-28T03:47:58Z on 461 T74/T63's landing was filed in 462's
/// `arbiter.jsonl` - the clone's `.specify/feature.json` - and charged 462 T22 a part B, because the tripwire's row named no
/// feature. It names the landing's feature (`home`, never `feature`: that key scopes which feature's gates a row holds, and a red
/// gate holds the tree's every gate) and its tasks, where the run was told them and the feature's directory is there.
#[test]
fn a_second_red_gate_names_the_landing_it_tripped() {
    let (_dir, dir) = repo("red-home");
    std::fs::create_dir_all(dir.join("specs/461-x")).unwrap();
    let owed = dir.join(".git/arbiter-owed.json");
    let landing = Run {
        feature: "461-x".to_owned(),
        tasks: "T74 T63".to_owned(),
        ..Run::default()
    };
    record(&dir, FAILED, "done", &landing).unwrap();
    record(&dir, FAILED, "done", &landing).unwrap();
    let row: serde_json::Value =
        serde_json::from_str(&std::fs::read_to_string(&owed).unwrap()).unwrap();
    let row = row.as_object().unwrap().values().next().unwrap().clone();
    assert_eq!(row["home"], "461-x");
    assert_eq!(row["tasks"], serde_json::json!(["T74", "T63"]));
    assert_eq!(row["kind"], "red-gate");
    assert!(row.get("feature").is_none());
    // a feature with no directory, or none told, names nothing: the arbiter resolves it as before
    std::fs::remove_file(&owed).unwrap();
    let stray = Run {
        feature: "999-gone".to_owned(),
        ..Run::default()
    };
    record(&dir, FAILED, "done", &stray).unwrap();
    let text = std::fs::read_to_string(&owed).unwrap();
    assert!(!text.contains("home") && !text.contains("tasks"), "{text}");
}

/// THE STAND-DOWN'S REACH (feature 461 T17, plan D6 step 4): the lane's own rule takes a second red only for a run in the lane's
/// tree whose batch is open in `lane.jsonl`, or one the runner holding `lane.lock` started; every other run is stopped as before.
mod lane {
    use std::path::Path;

    use l7r_shared::builder_pool::{self, Tree, LANE};

    use super::{record, repo, Run, FAILED};

    /// Two red `make done`s in a row as `run`, and whether the second owed the arbiter.
    fn owed_after_two_reds(dir: &Path, batch: &str, me: u32) -> bool {
        let run = Run {
            batch: batch.to_owned(),
            me,
            ..Run::default()
        };
        let owed = dir.join(".git/arbiter-owed.json");
        let _ = std::fs::remove_file(&owed);
        let _ = std::fs::remove_file(dir.join(".git/last-gate"));
        record(dir, FAILED, "done", &run).unwrap();
        record(dir, FAILED, "done", &run).unwrap();
        owed.exists()
    }

    /// The pool's registry naming `lane` the lane's tree.
    fn lane_tree(dir: &Path, lane: &Path) {
        let tree = Tree {
            tree: lane.to_path_buf(),
            feature: String::new(),
            tasks: vec![LANE.to_owned()],
            since: "2026-11-27T00:00:00Z".to_owned(),
        };
        builder_pool::write(&dir.join(".git"), &[tree]).unwrap();
    }

    fn log(dir: &Path, lines: &[&str]) {
        std::fs::create_dir_all(dir.join(".git/l7r-lane")).unwrap();
        std::fs::write(dir.join(".git/l7r-lane/lane.jsonl"), lines.join("\n")).unwrap();
    }

    const OPEN: &str = r#"{"event":"batch","batch":"b1","changes":["c1"]}"#;

    #[test]
    fn a_run_in_the_lanes_tree_with_its_batch_open_is_left_to_the_lane() {
        let (_d, dir) = repo("lane-open");
        lane_tree(&dir, &dir);
        log(
            &dir,
            &["not json", OPEN, r#"{"event":"run","batch":"b1","code":1}"#],
        );
        assert!(!owed_after_two_reds(&dir, "b1", 0));
    }

    #[test]
    fn a_by_hand_run_outside_the_lanes_tree_is_stopped_its_batch_open_or_not() {
        let (_d, dir) = repo("lane-by-hand");
        let (_o, other) = repo("lane-other");
        lane_tree(&dir, &other);
        log(&dir, &[OPEN]);
        assert!(owed_after_two_reds(&dir, "b1", std::process::id()));
        let (_d2, none) = repo("lane-unnamed");
        lane_tree(&none, &other);
        assert!(owed_after_two_reds(&none, "b9", 0));
    }

    #[test]
    fn a_run_in_the_lanes_tree_whose_batch_is_not_open_is_stopped() {
        for (tag, batch, lines) in [
            ("none", "b2", vec![OPEN]),
            (
                "landed",
                "b1",
                vec![OPEN, r#"{"event":"landed","batch":"b1"}"#],
            ),
            (
                "stopped",
                "b1",
                vec![OPEN, r#"{"event":"stop","batch":"b1"}"#],
            ),
            ("unset", "", vec![OPEN]),
        ] {
            let (_d, dir) = repo(&format!("lane-shut-{tag}"));
            lane_tree(&dir, &dir);
            log(&dir, &lines);
            assert!(owed_after_two_reds(&dir, batch, 0), "{tag}");
        }
        let (_d, dir) = repo("lane-again");
        lane_tree(&dir, &dir);
        log(&dir, &[OPEN, r#"{"event":"stop","batch":"b1"}"#, OPEN]);
        assert!(!owed_after_two_reds(&dir, "b1", 0));
    }

    #[test]
    fn a_run_the_lanes_runner_started_is_left_to_the_lane_and_no_other() {
        let (_d, dir) = repo("lane-runner");
        lane_tree(&dir, &dir);
        let lock = dir.join(".git/l7r-lane/lane.lock");
        std::fs::create_dir_all(lock.parent().unwrap()).unwrap();
        let me = std::process::id();
        // the lock free: no runner lives, whatever pid the file holds
        std::fs::write(&lock, format!("{me}\n")).unwrap();
        assert!(owed_after_two_reds(&dir, "b2", me));
        let _held = l7r_shared::tool::flock_within(&lock, 1.0).unwrap().unwrap();
        // held by a pid that is no ancestor of this run, and by none the file can name
        let mut other = std::process::Command::new("sleep")
            .arg("5")
            .spawn()
            .unwrap();
        std::fs::write(&lock, format!("{}\n", other.id())).unwrap();
        assert!(owed_after_two_reds(&dir, "b2", me));
        other.kill().unwrap();
        other.wait().unwrap();
        std::fs::write(&lock, "nobody\n").unwrap();
        assert!(owed_after_two_reds(&dir, "b2", me));
        // held by this run's parent, or by this run itself: the runner started it
        std::fs::write(&lock, format!("{}\n", std::os::unix::process::parent_id())).unwrap();
        assert!(!owed_after_two_reds(&dir, "b2", me));
        std::fs::write(&lock, format!("{me}\n")).unwrap();
        assert!(!owed_after_two_reds(&dir, "b2", me));
        // started by the runner but in another tree: today's rule
        let (_o, other_tree) = repo("lane-runner-other");
        lane_tree(&dir, &other_tree);
        assert!(owed_after_two_reds(&dir, "b2", me));
    }
}
