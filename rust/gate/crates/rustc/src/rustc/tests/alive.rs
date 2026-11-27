//! A test run past its bound has its program's live state recorded once beside its `test` Phase line (feature 451 T463, `alive.rs`):
//! a stand-in test binary starts a child and stays until the record appears, so the record catches both alive whatever the load.

use serde_json::Value;

use super::phases::phases;
use super::side::built;
use super::*;

/// A fake cargo whose `--no-run` build names one binary for the crate, its library's (`side.rs`'s `TWO_BINARIES` less one).
const ONE_BINARY: &str = r#"d="$(dirname "$0")"; for m in "$@"; do :; done; c="$(basename "$(dirname "$m")")"
case "$1 $2" in
  "test --no-run") echo '{"reason":"build-finished"}'
    echo '{"executable":"'"$d/$c"'-lib","target":{"kind":["lib"],"name":"x"}}';;
esac
exit 0"#;

/// The knob a test shortens the bound with (`alive.rs`).
const KNOB: &str = "L7R_RUST_ALIVE_MS";

/// Where a tree's records go: beside its event logs.
fn alive_dir(root: &Path) -> PathBuf {
    root.join(".git/l7r-events/alive")
}

/// A stand-in test that starts `sleep 46.3` and waits until crate `rust/a`'s record is in `dir` (at most about 10 s; records seeded
/// there are not its), then ends its child and passes on its own.
fn lingering(dir: &Path) -> String {
    format!(
        "sleep 46.3 &\ns=$!\ni=0\nwhile [ $i -lt 200 ] && ! ls \"{}\" 2>/dev/null | grep -q -- -rust-a-; do sleep 0.05; i=$((i+1)); done\n\
         kill $s\nwait $s 2>/dev/null\necho 'test result: ok. 1 passed'",
        dir.display()
    )
}

/// The world with its bound shortened to `ms`.
fn bounded(world: Held<World>, root: &Path, ms: &str) -> Held<World> {
    world.map(|w| World {
        root: l7r_shared::env::Rooted::with(root, &[(KNOB, ms)]),
        ..w
    })
}

/// The `test` Phase line of `krate`.
fn test_line<'a>(lines: &'a [Value], krate: &str) -> &'a Value {
    lines
        .iter()
        .find(|l| l["step"] == "test" && l["crates"][0] == krate)
        .unwrap()
}

/// The one record a run wrote, named on its line, checked for what it must hold.
fn caught(root: &Path, line: &Value, crate_dir: &Path) {
    let named = PathBuf::from(line["alive"].as_str().unwrap());
    assert_eq!(named.parent(), Some(alive_dir(root).as_path()));
    assert_eq!(std::fs::read_dir(alive_dir(root)).unwrap().count(), 1);
    let text = std::fs::read_to_string(&named).unwrap();
    assert!(text.contains("sleep 46.3"), "{text}");
    let cwd = format!("cwd={}", crate_dir.display());
    assert!(text.contains(&cwd), "{text}");
    assert!(text.contains("SigIgn="), "{text}");
    assert!(text.contains("thread "), "{text}");
    assert!(text.starts_with("=== "), "{text}");
}

#[test]
fn a_built_binary_past_its_bound_is_caught_once_and_named_on_its_test_line() {
    // one binary for the crate, so no quick binary beside it can pass the short bound on a loaded machine and be caught too
    let (root, _, _) = kept_crates();
    let world = bounded(world_with(&root, ONE_BINARY), &root, "100");
    let exe = world.target.join("a-lib");
    crate::write_executable(
        &exe,
        &format!("#!/bin/sh\n{}\n", lingering(&alive_dir(&root))),
    );
    let done = answer(&world, "test", &["rust/a".to_owned()], false);
    assert_eq!(done.code, 0, "{}", done.stderr);
    let lines = phases(&root);
    caught(&root, test_line(&lines, "rust/a"), &root.join("rust/a"));
}

/// 451 T470: a built binary is asked libtest's per-test times (`-Z unstable-options --report-time`, under `RUSTC_BOOTSTRAP=1`), and a
/// run past its bound has them on the end of its record, slowest first, a test with no time (ignored) last; the test lines are out of
/// the crate's output, its summary kept.
#[test]
fn a_caught_binary_s_per_test_times_end_its_record_slowest_first() {
    let (root, _, _) = kept_crates();
    let world = bounded(world_with(&root, ONE_BINARY), &root, "100");
    let exe = world.target.join("a-lib");
    let pretty = "case \"$RUSTC_BOOTSTRAP $*\" in \"1 -Z unstable-options --report-time\") \
                  printf '\\nrunning 3 tests\\ntest t::fast ... ok <0.001s>\\ntest t::off ... ignored\\ntest t::slow ... ok <31.250s>\\n\\n';; esac";
    crate::write_executable(
        &exe,
        &format!("#!/bin/sh\n{pretty}\n{}\n", lingering(&alive_dir(&root))),
    );
    let done = answer(&world, "test", &["rust/a".to_owned()], false);
    assert_eq!(done.code, 0, "{}", done.stderr);
    let (out, summary) = (
        &done.stdout,
        "rust-checks: test on rust/a: test result: ok. 1 passed",
    );
    assert!(out.contains(summary) && !out.contains("t::fast"), "{out}");
    let lines = phases(&root);
    let named = PathBuf::from(test_line(&lines, "rust/a")["alive"].as_str().unwrap());
    let text = std::fs::read_to_string(&named).unwrap();
    let times = "=== per-test times, slowest first (libtest --report-time)\ntest t::slow ... ok <31.250s>\ntest t::fast ... ok <0.001s>\ntest t::off ... ignored\n";
    assert!(text.ends_with(times), "{text}");
    assert!(text.contains("sleep 46.3"), "{text}");
}

/// 451 T473: a record written prunes the directory to the newest 50 (`alive.rs`'s `KEEP`), oldest first by mtime, never the one
/// just written.
#[test]
fn a_record_written_keeps_only_the_newest_records() {
    let (root, _, _) = kept_crates();
    let dir = alive_dir(&root);
    std::fs::create_dir_all(&dir).unwrap();
    let now = std::time::SystemTime::now();
    for i in 0..60u64 {
        let seed = dir.join(format!("1000000000-old-{i:02}-1.txt"));
        std::fs::write(&seed, "seeded").unwrap();
        let at = now - std::time::Duration::from_secs(86_400 + (60 - i) * 60);
        std::fs::File::options()
            .write(true)
            .open(&seed)
            .unwrap()
            .set_modified(at)
            .unwrap();
    }
    let world = bounded(world_with(&root, ONE_BINARY), &root, "100");
    let exe = world.target.join("a-lib");
    crate::write_executable(&exe, &format!("#!/bin/sh\n{}\n", lingering(&dir)));
    let done = answer(&world, "test", &["rust/a".to_owned()], false);
    assert_eq!(done.code, 0, "{}", done.stderr);
    let named = PathBuf::from(
        test_line(&phases(&root), "rust/a")["alive"]
            .as_str()
            .unwrap(),
    );
    let mut left: Vec<String> = std::fs::read_dir(&dir)
        .unwrap()
        .flatten()
        .map(|e| e.file_name().to_string_lossy().into_owned())
        .collect();
    left.sort();
    // the new record and the newest 49 seeds: seeds 00 to 10, the oldest, dropped
    assert_eq!(left.len(), 50);
    assert_eq!(left[0], "1000000000-old-11-1.txt");
    assert!(named.exists());
}

#[test]
fn a_cargo_test_run_past_its_bound_is_caught_through_cargo() {
    let (root, _, _) = kept_crates();
    let body = format!(
        "case \"$*\" in *--no-run*) exit 0;; esac\n{}",
        lingering(&alive_dir(&root))
    );
    let world = bounded(world_with(&root, &body), &root, "100");
    let fresh = world.map(|w| World {
        no_reuse: true,
        ..w
    });
    let done = answer(&fresh, "test", &["rust/a".to_owned()], false);
    assert_eq!(done.code, 0, "{}", done.stderr);
    let lines = phases(&root);
    // cargo runs from the tree's root, and the record holds cargo's whole tree: the stand-in's child among it
    caught(&root, test_line(&lines, "rust/a"), &root);
}

#[test]
fn a_run_inside_its_bound_records_nothing() {
    let (root, world) = built("alive-quick");
    let done = answer(&world, "test", &[], false);
    assert_eq!(done.code, 0, "{}", done.stderr);
    let lines = phases(&root);
    assert!(lines.iter().all(|l| l.get("alive").is_none()), "{lines:?}");
    assert!(!alive_dir(&root).exists());
}

/// One fake `/proc/<pid>` entry: a stat line whose name holds a space and a `)`, its parent and its start tick (field 22).
fn fake(proc: &Path, pid: &str, parent: u32, start: u32) -> PathBuf {
    let at = proc.join(pid);
    std::fs::create_dir_all(at.join(format!("task/{pid}"))).unwrap();
    let line = format!("{pid} (a) b) S {parent} {}{start} 0\n", "0 ".repeat(17));
    std::fs::write(at.join("stat"), &line).unwrap();
    std::fs::write(
        at.join(format!("task/{pid}/stat")),
        line.replace(" S ", " R "),
    )
    .unwrap();
    std::fs::write(at.join(format!("task/{pid}/comm")), format!("t-{pid}\n")).unwrap();
    std::fs::write(at.join(format!("task/{pid}/wchan")), "do_wait").unwrap();
    std::fs::write(at.join("cmdline"), format!("prog\0--{pid}\0")).unwrap();
    std::fs::write(at.join("wchan"), "hrtimer_nanosleep").unwrap();
    std::fs::write(
        at.join("status"),
        "Name:\tx\nSigIgn:\t0000000000004000\nSigCgt:\t0000000000000002\n",
    )
    .unwrap();
    std::os::unix::fs::symlink(proc, at.join("cwd")).unwrap();
    at
}

#[test]
fn the_record_reads_a_process_s_tree_from_proc_and_is_cut_at_its_cap() {
    use super::super::alive::{bounded, record};
    let dir = scratch("alive-proc");
    let proc = dir.join("proc");
    fake(&proc, "10", 1, 5000);
    fake(&proc, "11", 10, 9000);
    fake(&proc, "20", 1, 100);
    // a process gone mid-read (no stat), and one whose stat is no stat line
    std::fs::create_dir_all(proc.join("12")).unwrap();
    std::fs::create_dir_all(proc.join("13")).unwrap();
    std::fs::write(proc.join("13/stat"), "13 no name").unwrap();
    std::fs::write(proc.join("uptime"), "100.5 7.0\n").unwrap();
    std::fs::write(proc.join("loadavg"), "1.5 2.5 3.5 1/9 42\n").unwrap();
    let text = record(&proc, 10, "x past 5 ms");
    let head = "=== x past 5 ms: pid 10, load 1.5 2.5 3.5\n";
    assert!(text.starts_with(head), "{text}");
    let root_line = "--- pid 10 ppid 1 age 50.5s state S wchan hrtimer_nanosleep\n";
    assert!(text.contains(root_line), "{text}");
    let child_line = "--- pid 11 ppid 10 age 10.5s state S";
    assert!(text.contains(child_line), "{text}");
    let signals = "SigIgn=0000000000004000 SigCgt=0000000000000002";
    let detail = format!(
        "    cwd={}\n    args=prog --11\n    {signals}\n",
        proc.display()
    );
    assert!(text.contains(&detail), "{text}");
    assert!(text.contains("    thread t-11 R do_wait\n"), "{text}");
    assert!(!text.contains("pid 20 "), "{text}");
    // a root already gone is its head line alone
    assert_eq!(record(&proc, 12, "y"), "=== y: pid 12, load 1.5 2.5 3.5\n");
    assert_eq!(bounded("short".to_owned(), 10), "short");
    assert_eq!(
        bounded("ab\u{e9}cd".to_owned(), 3),
        "ab\n... cut at 2 of 6 bytes\n"
    );
}
