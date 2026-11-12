//! The coverage run's build (feature 449 T100, T105): what instruments which crate, and the builds a family's owed crates share.

use std::collections::BTreeMap;
use std::process::Command;

use super::super::{build_together, workspace_only};
use super::{calls, nested_crates, scratch, two_crates, world_with};

/// Coverage instruments the workspace's crates only (T100): the coverage flags leave RUSTFLAGS, the rest stays for every crate, and a
/// wrapper cargo calls for the workspace's crates alone adds them; written once, and left be while its text is the same; no RUSTFLAGS,
/// nothing done.
#[test]
fn coverage_instruments_the_workspace_s_crates_only() {
    let dir = scratch("rustc-cover-wrapper");
    let script = dir.join("instrument.sh");
    let lld = "-C link-arg=-fuse-ld=lld";
    let shown = || {
        BTreeMap::from([(
            "RUSTFLAGS".to_owned(),
            format!("{lld} -C instrument-coverage --cfg=coverage --cfg=trybuild_no_target"),
        )])
    };
    let mut env = shown();
    workspace_only(&mut env, &script);
    assert_eq!(env["RUSTFLAGS"], lld);
    assert_eq!(env["RUSTC_WORKSPACE_WRAPPER"], script.display().to_string());
    let text = std::fs::read_to_string(&script).unwrap();
    assert_eq!(
        text,
        "#!/bin/sh\nexec \"$@\" -C instrument-coverage --cfg=coverage --cfg=trybuild_no_target\n"
    );
    // through sh, which reads the script: executing a file this test just wrote raced another test thread's fork, which held its write
    // handle open ("Text file busy")
    let ran = Command::new("sh")
        .arg(&script)
        .args(["echo", "rustc"])
        .output()
        .unwrap();
    assert!(
        std::os::unix::fs::PermissionsExt::mode(&std::fs::metadata(&script).unwrap().permissions())
            & 0o111
            != 0
    );
    assert_eq!(
        String::from_utf8_lossy(&ran.stdout),
        "rustc -C instrument-coverage --cfg=coverage --cfg=trybuild_no_target\n"
    );
    let before = std::fs::metadata(&script).unwrap().modified().unwrap();
    std::thread::sleep(std::time::Duration::from_millis(20));
    workspace_only(&mut shown(), &script);
    let after = std::fs::metadata(&script).unwrap().modified().unwrap();
    assert_eq!(after, before, "not written again");
    let mut none = BTreeMap::new();
    workspace_only(&mut none, &script);
    assert!(none.is_empty());
}

/// The coverage builds together (T105): a family's owed crates in one cargo call, each named by its package, a family of one left to
/// its own run.
#[test]
fn a_family_s_owed_coverage_builds_go_together() {
    let (root, g, mid, low) = nested_crates();
    let world = world_with(&root, "exit 0");
    build_together(&world, &[&g, &mid, &low]);
    let asked = calls(&world);
    let together = asked
        .iter()
        .find(|c| c.starts_with("test --no-run --lib"))
        .unwrap();
    assert!(together.ends_with("-p g -p g_mid -p g_low"), "{together}");
    let (other, a, _) = two_crates();
    let alone = world_with(&other, "exit 0");
    build_together(&alone, &[&a]);
    assert!(calls(&alone)
        .iter()
        .all(|c| !c.starts_with("test --no-run --lib")));
}
