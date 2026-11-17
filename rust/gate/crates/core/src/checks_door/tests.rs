use serde_json::{json, Value};

use super::keep_batches;

#[test]
fn the_batches_are_kept_whole_or_the_failure_named() {
    let d = l7r_guard::shared::tempdir::TempDir::new("gate-core-door");
    assert!(std::process::Command::new("git")
        .arg("-C")
        .arg(&d)
        .args(["init", "-q"])
        .status()
        .unwrap()
        .success());
    keep_batches(&d, &json!({"modal-form": ["a"]})).unwrap();
    let kept: Value =
        serde_json::from_str(&std::fs::read_to_string(d.join(".git/modal-batches.json")).unwrap())
            .unwrap();
    assert_eq!(kept["batches"], json!({"modal-form": ["a"]}));
    assert!(keep_batches(std::path::Path::new("/proc/nonexistent/x"), &json!({})).is_err());
    std::fs::remove_file(d.join(".git/modal-batches.json")).unwrap();
    std::fs::create_dir_all(d.join(".git/modal-batches.json")).unwrap();
    assert!(keep_batches(&d, &json!({})).is_err());
}
