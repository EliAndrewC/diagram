//! The start through the lane tree's launcher (feature 461 T51): a stale `l7r-gate` is built before the detached spawn, so a build
//! longer than the start's wait never reads as "holds no lock"; a build that fails starts nothing and says why.

use std::path::{Path, PathBuf};
use std::time::Duration;

use l7r_gate_core::ci::fixtures::repo;

use super::{holder, start, stop};

/// A stand-in for `scripts/gates/l7r-gate.sh`: with `L7R_GATE_PRINT_FRESH` it "builds" - 0.6 s where `<it>.stale` exists, a line
/// in `<it>.builds` - and prints its path, or fails as cargo does where `<it>.fail` exists; without it, it runs as the runner (the
/// same build first where still stale), taking the lock and holding it.
fn fake_launcher(dir: &Path) -> PathBuf {
    let gates = dir.join("gates");
    std::fs::create_dir_all(&gates).unwrap();
    let exe = gates.join("l7r-gate.sh");
    l7r_gate_core::write_executable(
        &exe,
        "#!/bin/sh\n\
         if [ -n \"$L7R_GATE_PRINT_FRESH\" ]; then\n\
           [ -e \"$0.fail\" ] && { echo 'error[E0425]: cannot find value `x`' >&2; exit 1; }\n\
           [ -e \"$0.stale\" ] && { sleep 0.6; rm -f \"$0.stale\"; echo built >> \"$0.builds\"; }\n\
           echo \"$0\"; exit 0\n\
         fi\n\
         [ -e \"$0.stale\" ] && { sleep 0.6; rm -f \"$0.stale\"; }\n\
         exec 9<>\"$3/l7r-lane/lane.lock\"\nflock -w 1 9 || exit 0\necho $$ > \"$3/l7r-lane/lane.lock\"\nexec sleep 30\n",
    );
    exe
}

/// The runner a start may have left, stopped whatever the start said (on the old code it comes up after the start gave up).
fn reap(common: &Path) {
    for _ in 0..150 {
        if holder(common).is_some() {
            break;
        }
        std::thread::sleep(Duration::from_millis(20));
    }
    let _ = stop(common, true, 5.0);
}

#[test]
fn a_stale_launcher_is_built_before_the_spawn_so_a_long_build_is_no_failed_start() {
    let dir = repo("lane-start-build");
    let common = dir.path().join(".git");
    let exe = fake_launcher(dir.path());
    std::fs::write(exe.with_extension("sh.stale"), "").unwrap();
    // the build (0.6 s) outlasts the wait (0.3 s), as the lane tree's rebuild outlasts START_WAIT_S
    let started = start(&common, &exe, "setsid", 0.3);
    let pid = holder(&common);
    reap(&common);
    assert_eq!(started.stderr, "");
    assert_eq!(started.code, 0);
    assert_eq!(
        started.stdout,
        format!("lane: the runner started (pid {})\n", pid.unwrap())
    );
    assert_eq!(
        std::fs::read_to_string(exe.with_extension("sh.builds")).unwrap(),
        "built\n"
    );
}

#[test]
fn a_build_that_fails_or_a_launcher_that_cannot_run_starts_nothing_and_says_why() {
    let dir = repo("lane-start-build-fails");
    let common = dir.path().join(".git");
    let exe = fake_launcher(dir.path());
    std::fs::write(exe.with_extension("sh.fail"), "").unwrap();
    let failed = start(&common, &exe, "setsid", 0.3);
    reap(&common);
    assert_eq!(failed.code, 1);
    let said = failed.stderr.as_str();
    assert!(said.contains("could not be built (exit 1)"));
    assert!(said.contains("error[E0425]: cannot find value `x`"));
    assert!(!super::lock_path(&common).exists());
    let gone = dir.path().join("nowhere/l7r-gate.sh");
    let missing = start(&common, &gone, "setsid", 0.3);
    assert_eq!(missing.code, 1);
    let named = format!("lane: {}: ", gone.display());
    assert!(missing.stderr.starts_with(&named));
    assert!(!super::lock_path(&common).exists());
}
