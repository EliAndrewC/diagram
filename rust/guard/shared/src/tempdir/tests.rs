use std::fs::File;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::time::{Duration, SystemTime};

use super::{beside_binary, TempDir};

#[test]
fn a_new_directory_is_named_by_its_tag_and_this_process() {
    let dir = TempDir::new("tempdir-name");
    let name = dir
        .path()
        .file_name()
        .unwrap()
        .to_string_lossy()
        .into_owned();
    assert!(name.starts_with(&format!("l7r-tempdir-name-p{}-", std::process::id())));
    assert!(dir.is_dir());
    assert_eq!(AsRef::<Path>::as_ref(&dir), dir.path());
    assert!(format!("{dir:?}").contains("tempdir-name"));
}

/// The whole temp directory is listed once a process, whatever the number of `TempDir`s and tags (feature 451 T370: one listing a
/// call was 14 to 16 ms under a `/tmp` of 5,443 entries, 509 of them in a run of the guard crate's tests).
#[test]
fn the_temp_directory_is_listed_once_a_process() {
    let made = [
        TempDir::new("tempdir-once"),
        TempDir::new("tempdir-once-b"),
        TempDir::new("tempdir-once"),
    ];
    assert!(made.iter().all(|d| d.is_dir()));
    let listings = super::SWEEPS.load(std::sync::atomic::Ordering::Relaxed);
    assert_eq!(listings, 1);
}

/// A process stopped by a signal leaves its directories (no `Drop` runs): the next process's sweep removes those of a gone pid,
/// whatever their tag (feature 451 T370), and keeps a live process's, a file, a name not of the form, a hook suite's directory and a
/// directory the checks left before T101.
#[test]
fn a_gone_process_s_directories_go_with_the_next_process_of_any_tag() {
    use super::sweep_dead;
    let parent = TempDir::new("tempdir-sweep");
    let proc = TempDir::new("tempdir-sweep-proc");
    std::fs::create_dir_all(proc.join("77")).unwrap();
    let hours_ago = SystemTime::now() - Duration::from_secs(4 * 3600);
    let make = |n: &str| {
        std::fs::create_dir_all(parent.join(n).join("inside")).unwrap();
        File::open(parent.join(n))
            .unwrap()
            .set_modified(hours_ago)
            .unwrap();
    };
    std::fs::create_dir_all(parent.join("l7r-t-p99999993-0")).unwrap(); // gone, but changed within the hours: kept
    make("l7r-t-p99999991-0"); // gone: removed
    make("l7r-t-p77-3"); // live: kept
    make("l7r-u-p99999991-0"); // another tag, gone: removed
    make("l7r-gate-ci-stop-handler-p99999991-71"); // a tag with hyphens, gone: removed
    make("l7r-a-p5-p99999991-2"); // a tag that ends as a pid would, gone: removed
    make("l7r-a-p5-p77-2"); // the same tag, live: kept
    make("l7r-t-99999991-0"); // the form before T101, the GM's pile: kept
    make("l7r-gate-check-p5-99999991-0"); // that form under a tag ending `-p5`: kept
    make("l7r-gate-check-99999991-0-name"); // that form with its name: kept
    make("l7r-hooks-suite-x-hooks.sh-p99999991.AbCdEf"); // a hook suite's directory, its runner's to remove: kept
    make("l7r-p99999991-0"); // no tag: kept
    make("l7r-test-scratch"); // what a test process shares: kept
    make("other-t-p99999991-0"); // not the helper's: kept
    make("l7r-t-px-0"); // not a pid: kept
    make("l7r-t-p99999991-x"); // not a sequence: kept
    make("l7r-t-p99999991"); // no sequence: kept
    std::fs::write(parent.join("l7r-t-p99999992-0"), "a file").unwrap(); // kept
    let three_hours_ago = SystemTime::now() - Duration::from_secs(3 * 3600);
    sweep_dead(&parent, &proc, three_hours_ago);
    let mut left: Vec<String> = std::fs::read_dir(&*parent)
        .unwrap()
        .flatten()
        .map(|e| e.file_name().to_string_lossy().into_owned())
        .collect();
    left.sort();
    assert_eq!(
        left,
        [
            "l7r-a-p5-p77-2",
            "l7r-gate-check-99999991-0-name",
            "l7r-gate-check-p5-99999991-0",
            "l7r-hooks-suite-x-hooks.sh-p99999991.AbCdEf",
            "l7r-p99999991-0",
            "l7r-t-99999991-0",
            "l7r-t-p77-3",
            "l7r-t-p99999991",
            "l7r-t-p99999991-x",
            "l7r-t-p99999992-0",
            "l7r-t-p99999993-0",
            "l7r-t-px-0",
            "l7r-test-scratch",
            "other-t-p99999991-0"
        ]
    );
    sweep_dead(&parent.join("missing"), &proc, three_hours_ago);
}

/// The step a signaled test process runs before its exit: the signal's number beside its note.
fn note_the_signal(signum: i32) {
    if let Some(note) = std::env::var_os("L7R_TEMPDIR_SIGNALED") {
        let _ = std::fs::write(
            format!("{}.before", Path::new(&note).display()),
            signum.to_string(),
        );
    }
}

/// INT and TERM end a process through its handler, which removes every `TempDir` it holds and exits as the signal would (128 + its
/// number): this test runs itself as that process, which makes one and waits to be stopped.
#[test]
fn an_int_or_a_term_removes_the_process_s_directories() {
    if let Some(note) = std::env::var_os("L7R_TEMPDIR_SIGNALED") {
        super::before_exit(note_the_signal);
        let dir = TempDir::new("tempdir-signaled");
        let kept = TempDir::new("tempdir-signaled-kept").keep();
        std::fs::write(note, format!("{}\n{}", dir.display(), kept.display())).unwrap();
        loop {
            std::thread::sleep(Duration::from_secs(1));
        }
    }
    // a process started with INT ignored (a background job's) passes that on, and an ignored INT stays ignored: then only TERM is sent
    let status = std::fs::read_to_string("/proc/self/status").unwrap();
    let ignored = status
        .lines()
        .find_map(|l| l.strip_prefix("SigIgn:"))
        .and_then(|m| u64::from_str_radix(m.trim(), 16).ok())
        .unwrap();
    let all = [("TERM", 15), ("INT", 2)];
    let sent_ints = usize::from(ignored & 2 == 0);
    for &(name, number) in &all[..=sent_ints] {
        let note_dir = TempDir::new("tempdir-signal-note");
        let note = note_dir.join("note");
        let mut child = Command::new(std::env::current_exe().unwrap())
            .args([
                "--exact",
                "tempdir::tests::an_int_or_a_term_removes_the_process_s_directories",
            ])
            .env("L7R_TEMPDIR_SIGNALED", &note)
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .spawn()
            .unwrap();
        // polled every 2 ms, the ceiling still 10 s: at 25 ms the two children's four waits rounded up to 0.1 s against FR-008's tenth
        // of a second (feature 449 T167)
        let said = (0..5000)
            .find_map(|_| {
                std::thread::sleep(Duration::from_millis(2));
                std::fs::read_to_string(&note)
                    .ok()
                    .filter(|t| t.contains('\n'))
            })
            .unwrap();
        let (held, kept) = said.split_once('\n').unwrap();
        assert!(Path::new(held).is_dir(), "{name}");
        let before = note_dir.join("note.before");
        let sent = Command::new("kill")
            .args([format!("-{name}"), child.id().to_string()])
            .status()
            .unwrap();
        assert!(sent.success());
        let ended = (0..5000).find_map(|_| {
            std::thread::sleep(Duration::from_millis(2));
            child.try_wait().unwrap()
        });
        let _ = child.kill();
        assert_eq!(ended.and_then(|s| s.code()), Some(128 + number), "{name}");
        assert!(!Path::new(held).exists(), "{name}: held, removed");
        // the process's own step ran first, with the signal's number (feature 449 T121)
        assert_eq!(
            std::fs::read_to_string(&before).ok(),
            Some(number.to_string())
        );
        // one kept is no longer the process's to remove
        assert!(Path::new(kept).is_dir(), "{name}: the kept one stays");
        std::fs::remove_dir_all(kept).unwrap();
    }
}

#[test]
fn two_of_one_tag_are_two_directories() {
    let (a, b) = (TempDir::new("tempdir-two"), TempDir::new("tempdir-two"));
    assert_ne!(a.path(), b.path());
}

#[test]
fn it_is_gone_when_dropped_with_what_it_holds() {
    let dir = TempDir::new("tempdir-drop");
    std::fs::create_dir_all(dir.join("a/b")).unwrap();
    std::fs::write(dir.join("a/b/c"), "x").unwrap();
    let at: PathBuf = dir.to_path_buf();
    drop(dir);
    assert!(!at.exists());
}

#[test]
fn it_is_gone_after_a_panic_inside_catch_unwind() {
    let at = std::sync::Mutex::new(None::<PathBuf>);
    let result = std::panic::catch_unwind(|| {
        let dir = TempDir::new("tempdir-panic");
        std::fs::write(dir.join("f"), "x").unwrap();
        *at.lock().unwrap() = Some(dir.to_path_buf());
        panic!("a failing test");
    });
    assert!(result.is_err());
    let at = at.lock().unwrap().clone().unwrap();
    assert!(!at.exists());
}

#[test]
fn a_kept_directory_outlives_it() {
    let at = TempDir::new("tempdir-keep").keep();
    assert!(at.is_dir());
    std::fs::remove_dir_all(&at).unwrap();
    assert!(!Path::new(&at).exists());
}

#[test]
fn a_held_value_keeps_its_directory_until_it_goes() {
    let dir = TempDir::new("tempdir-held");
    let root = dir.to_path_buf();
    let inner = dir.join("a");
    let held = dir.hold(inner.clone());
    std::fs::create_dir_all(&*held).unwrap();
    assert_eq!(AsRef::<Path>::as_ref(&held), inner.as_path());
    assert!(format!("{held:?}").contains("tempdir-held"));
    drop(held);
    assert!(!root.exists());
    let mut text = TempDir::new("tempdir-text").hold("a".to_owned());
    let kept = TempDir::new("tempdir-map");
    let at = kept.to_path_buf();
    let mapped = kept.hold(1).map(|n| n + 1);
    assert!(*mapped == 2 && at.is_dir());
    drop(mapped);
    assert!(!at.exists());
    let named = TempDir::new("tempdir-json");
    assert_eq!(serde_json::json!({"d": named, "t": text})["t"], "a");
    assert_eq!(std::path::Path::new(&text), Path::new("a"));
    assert_eq!(std::path::Path::new(&named), named.path());
    text.push('b');
    assert_eq!(format!("{text}"), "ab");
}

#[test]
fn a_directory_beside_the_binary_is_emptied_for_each_process() {
    let dir = beside_binary("tempdir-beside");
    std::fs::write(dir.join("old"), "x").unwrap();
    let again = beside_binary("tempdir-beside");
    assert_eq!(dir, again);
    assert!(again.is_dir() && !again.join("old").exists());
    // under the temp directory, which `make rust-test` makes the run's own and removes whole when the run ends
    assert_eq!(
        again,
        std::env::temp_dir().join("l7r-test-scratch/tempdir-beside")
    );
    std::fs::remove_dir_all(&again).unwrap();
}

/// THE HELPER'S OWN SUBDIRECTORY (feature 462 T371, lever B of 451 T365): a process's directories go under `<temp dir>/l7r-tmp`, and its
/// sweep lists that alone - so a dead process's leftover there goes and one at the temp directory's top level is never read. Measured
/// 2026-11-26: a listing of a `/tmp` of 5,443 entries was 14 to 16 ms, of a directory that never grew 0.06 ms
/// (`dev/measurements/2026-11-26/tmp-clutter/t365-results.md`). The sweep runs once a process (T370), so a child process shows it.
#[test]
fn its_directories_and_its_sweep_stay_in_one_subdirectory() {
    if let Some(note) = std::env::var_os("L7R_TEMPDIR_SUBDIR") {
        let made = TempDir::new("tempdir-subdir").keep();
        std::fs::write(note, made.display().to_string()).unwrap();
        return;
    }
    let fixture = TempDir::new("tempdir-subdir-fixture");
    let hours_ago = SystemTime::now() - Duration::from_secs(4 * 3600);
    for gone in ["l7r-t-p99999991-0", "l7r-tmp/l7r-t-p99999991-0"] {
        std::fs::create_dir_all(fixture.join(gone)).unwrap();
        File::open(fixture.join(gone))
            .unwrap()
            .set_modified(hours_ago)
            .unwrap();
    }
    let note = fixture.join("note");
    let ran = Command::new(std::env::current_exe().unwrap())
        .args([
            "--exact",
            "tempdir::tests::its_directories_and_its_sweep_stay_in_one_subdirectory",
        ])
        .env("TMPDIR", &*fixture)
        .env("L7R_TEMPDIR_SUBDIR", &note)
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status()
        .unwrap();
    assert!(ran.success());
    let made = PathBuf::from(std::fs::read_to_string(&note).unwrap());
    assert_eq!(made.parent(), Some(fixture.join("l7r-tmp").as_path()));
    assert!(made.is_dir());
    // the top level is not listed: its leftover waits for the scratch sweep's /tmp rule (451 T374), not this one
    assert!(fixture.join("l7r-t-p99999991-0").is_dir());
    assert!(!fixture.join("l7r-tmp/l7r-t-p99999991-0").exists());
}
