//! Where the model and the runtime are (feature 449 T138).

use std::path::PathBuf;

use l7r_shared::tempdir::TempDir;

use super::{online_cpus, pinned, runtime, snapshot, threads, REPO};

#[test]
fn the_runtime_is_named_moved_or_pinned() {
    let v = pinned("ONNXRUNTIME_VERSION");
    assert!(!v.is_empty());
    assert_eq!(pinned("NO_SUCH"), "");
    let named = |k: &str| {
        (k == "L7R_ONNXRUNTIME")
            .then(|| "/x.so".to_owned())
            .unwrap_or_default()
    };
    assert_eq!(runtime(&named), PathBuf::from("/x.so"));
    let moved = |k: &str| {
        (k == "L7R_ONNXRUNTIME_HOME")
            .then(|| "/o".to_owned())
            .unwrap_or_default()
    };
    assert_eq!(
        runtime(&moved),
        PathBuf::from(format!(
            "/o/{v}/onnxruntime-linux-x64-{v}/lib/libonnxruntime.so.{v}"
        ))
    );
}

#[test]
fn the_model_is_the_snapshot_refs_main_names() {
    let dir = TempDir::new("embed-snap");
    let base = dir.path().join("models--Xenova--bge-m3");
    assert!(snapshot(dir.path(), REPO)
        .unwrap_err()
        .contains("is not in"));
    std::fs::create_dir_all(base.join("refs")).unwrap();
    std::fs::write(base.join("refs/main"), "abc").unwrap();
    assert!(snapshot(dir.path(), REPO).is_err());
    std::fs::create_dir_all(base.join("snapshots/abc/onnx")).unwrap();
    std::fs::write(base.join("snapshots/abc/onnx/model_int8.onnx"), "").unwrap();
    assert_eq!(
        snapshot(dir.path(), REPO).unwrap(),
        base.join("snapshots/abc")
    );
}

#[test]
fn half_the_cpus_online() {
    assert_eq!(threads("0-21\n"), 11);
    assert_eq!(threads("0,2-3"), 1);
    assert_eq!(threads("0-1,4-7"), 3);
    assert_eq!(threads("0"), 1);
    // unreadable: the process's own count
    assert!(threads("") >= 1);
    assert!(threads("x,3-1,y-2") >= 1);
    let _ = online_cpus();
}
