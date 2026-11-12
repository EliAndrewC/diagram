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

/// A process stopped by a signal leaves its directories (no `Drop` runs): the next `TempDir` of the tag removes those of a gone pid,
/// keeps a live process's, another tag's, a file, a name not of the form, and a directory the checks left before T101.
#[test]
fn a_gone_process_s_directories_go_with_the_next_of_their_tag() {
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
    make("l7r-u-p99999991-0"); // another tag: kept
    make("l7r-t-99999991-0"); // the form before T101, the GM's pile: kept
    make("l7r-t-px-0"); // not a pid: kept
    make("l7r-t-p99999991-x"); // not a sequence: kept
    make("l7r-t-p99999991"); // no sequence: kept
    std::fs::write(parent.join("l7r-t-p99999992-0"), "a file").unwrap(); // kept
    let three_hours_ago = SystemTime::now() - Duration::from_secs(3 * 3600);
    sweep_dead(&parent, "t", &proc, three_hours_ago);
    let mut left: Vec<String> = std::fs::read_dir(&*parent)
        .unwrap()
        .flatten()
        .map(|e| e.file_name().to_string_lossy().into_owned())
        .collect();
    left.sort();
    assert_eq!(
        left,
        [
            "l7r-t-99999991-0",
            "l7r-t-p77-3",
            "l7r-t-p99999991",
            "l7r-t-p99999991-x",
            "l7r-t-p99999992-0",
            "l7r-t-p99999993-0",
            "l7r-t-px-0",
            "l7r-u-p99999991-0"
        ]
    );
    sweep_dead(&parent.join("missing"), "t", &proc, three_hours_ago);
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
                "shared::tempdir::tests::an_int_or_a_term_removes_the_process_s_directories",
            ])
            .env("L7R_TEMPDIR_SIGNALED", &note)
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .spawn()
            .unwrap();
        let said = (0..400)
            .find_map(|_| {
                std::thread::sleep(Duration::from_millis(25));
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
        let ended = (0..400).find_map(|_| {
            std::thread::sleep(Duration::from_millis(25));
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
