//! Who counts as another session, and the five-minute cache.

use std::cell::Cell;
use std::path::{Path, PathBuf};

use super::{alone, chain, others, processes, session, solo, Procs};

/// A tmux server (1) running a parent session (10), which started this session (20); this session's hook (21) and a page session it started (22, under a bash 23); an unrelated
/// session (30); a process of another name (40).
fn tree() -> Procs {
    [
        (1, 0, "tmux: server"),
        (10, 1, "claude"),
        (20, 10, "claude"),
        (21, 20, "bash"),
        (23, 20, "bash"),
        (22, 23, "claude"),
        (30, 1, "claude"),
        (40, 1, "python3"),
    ]
    .into_iter()
    .map(|(pid, parent, name)| (pid, (parent, name.to_owned())))
    .collect()
}

fn dir(tag: &str) -> PathBuf {
    let path = std::env::temp_dir().join(format!("l7r-guard-solo-{tag}-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&path);
    std::fs::create_dir_all(&path).unwrap();
    path
}

fn fake(proc: &Path, pid: u32, stat: &str) {
    std::fs::create_dir_all(proc.join(pid.to_string())).unwrap();
    std::fs::write(proc.join(pid.to_string()).join("stat"), stat).unwrap();
}

#[test]
fn a_session_it_started_is_its_own_and_another_or_its_parent_is_not() {
    let procs = tree();
    assert_eq!(session(&procs, 21), Some(20));
    assert_eq!(others(&procs, Some(20)), [10, 30]);
    let lone: Procs = [
        (1, 0, "tmux: server"),
        (20, 1, "claude"),
        (23, 20, "bash"),
        (22, 23, "claude"),
    ]
    .into_iter()
    .map(|(p, a, n)| (p, (a, n.to_owned())))
    .collect();
    assert!(others(&lone, Some(20)).is_empty());
    assert_eq!(session(&procs, 40), None);
    assert_eq!(others(&lone, None), [20, 22]);
}

#[test]
fn the_answer_is_kept_five_minutes_per_session() {
    let cache = dir("cache");
    let asked = Cell::new(0);
    let procs_of = || {
        asked.set(asked.get() + 1);
        tree()
    };
    assert!(!solo(20, &cache, 1000.0, &procs_of));
    assert!(!solo(20, &cache, 1200.0, &procs_of));
    assert_eq!(asked.get(), 1);
    assert!(!solo(20, &cache, 1301.0, &procs_of));
    assert_eq!(asked.get(), 2);
    assert!(!solo(21, &cache, 1301.5, &procs_of));
    assert_eq!(asked.get(), 3);
    assert!(!solo(30, &cache, 2000.0, &procs_of));
    let garbage = cache.join("garbage");
    std::fs::create_dir_all(&garbage).unwrap();
    assert!(!solo(20, &garbage.join("file-not-dir/x"), 1.0, &tree));
    let bad_file = dir("bad");
    let kept: Vec<_> = std::fs::read_dir(&cache)
        .unwrap()
        .flatten()
        .map(|e| e.path())
        .filter(|p| p.is_file())
        .collect();
    std::fs::write(bad_file.join(kept[0].file_name().unwrap()), "not json").unwrap();
    assert!(!solo(20, &bad_file, 5.0, &tree));
}

#[test]
fn it_reads_proc_and_a_name_may_hold_parentheses() {
    let proc = dir("proc");
    fake(&proc, 5, "5 (claude) S 1 x");
    fake(&proc, 6, "6 (sh (odd) name) S 5 x");
    fake(&proc, 7, "7 (claude) S");
    fake(&proc, 8, "no parens here");
    std::fs::create_dir_all(proc.join("self")).unwrap();
    std::fs::create_dir_all(proc.join("9")).unwrap();
    let procs = processes(&proc);
    assert_eq!(procs[&6], (5, "sh (odd) name".to_owned()));
    assert_eq!(procs[&7], (0, "claude".to_owned()));
    assert_eq!(procs.len(), 3);
    assert_eq!(chain(6, &proc).len(), 2);
    assert!(chain(1, &proc).is_empty());
    fake(&proc, 11, "11 (a) S 12 x");
    fake(&proc, 12, "12 (b) S 11 x");
    assert_eq!(chain(11, &proc).len(), 2);
    assert!(processes(&proc.join("absent")).is_empty());
}

#[test]
fn the_forced_answer_and_the_look() {
    let (proc, cache) = (dir("look"), dir("look-cache"));
    assert!(alone(Some("1"), &proc, &cache, 1.0, 5));
    assert!(!alone(Some("0"), &proc, &cache, 1.0, 5));
    fake(&proc, 5, "5 (claude) S 1 x");
    assert!(alone(None, &proc, &cache, 1.0, 5));
    fake(&proc, 8, "8 (claude) S 1 x");
    assert!(!alone(Some("other"), &proc, &cache, 400.0, 5));
    assert!(
        alone(None, &proc, &dir("look-none"), 1.0, 99)
            || !alone(None, &proc, &dir("look-none2"), 1.0, 99)
    );
}
