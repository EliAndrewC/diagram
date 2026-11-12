//! The coverage run's build (feature 449 T100, T105, T108): what instruments which crate, and the builds a family's owed crates share.

use std::collections::BTreeMap;
use std::process::Command;

use super::super::cover::{uncovered_each, workspace_only};
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

/// The coverage builds together (T105): a family's owed crates in one cargo call, each named by its package, a family of one by its
/// manifest alone; a failed build of several asked again a crate at a time, and a crate with no binary named failing by name (T108).
#[test]
fn a_family_s_owed_coverage_builds_go_together_and_a_failed_one_crate_by_crate() {
    let (root, g, mid, low) = nested_crates();
    let builds = |world: &super::World| -> Vec<String> {
        calls(world)
            .into_iter()
            .filter(|c| c.starts_with("test --no-run --lib"))
            .collect()
    };
    let world = world_with(&root, "exit 0");
    let (got, said) = uncovered_each(&world, &[&g, &mid, &low]);
    let together = builds(&world);
    assert_eq!(together.len(), 1);
    assert!(
        together[0].ends_with("-p g -p g_mid -p g_low"),
        "{}",
        together[0]
    );
    assert!(
        said.contains("cover build of 3 crate(s)")
            && said.contains("of 3 crate(s), ")
            && said.contains(" at a time")
    );
    let failed = BTreeMap::from([(
        root.join("rust/g/crates/low").display().to_string(),
        vec![0],
    )]);
    assert_eq!(got[&low], failed);
    let broke = world_with(&root, "[ \"$2\" = --no-run ] && exit 1\nexit 0");
    let (got, said) = uncovered_each(&broke, &[&g, &mid, &low]);
    assert_eq!(builds(&broke).len(), 4);
    assert!(said.contains("cover build of 1 crate(s)"));
    assert_eq!((got.len(), &got[&low]), (3, &failed));
    let (other, a, _) = two_crates();
    let alone = world_with(&other, "exit 0");
    let _ = uncovered_each(&alone, &[&a]);
    assert!(builds(&alone).iter().all(|c| !c.contains(" -p ")));
    assert_eq!(builds(&alone).len(), 1);
}
