//! In a clone the local settings gain the exclusion naming the MIRROR's root CLAUDE.md - once, and keeping every other key; the mirror itself is never touched.

use std::path::PathBuf;

use serde_json::Value;

use super::ensure;

fn world(tag: &str) -> (crate::shared::tempdir::TempDir, PathBuf, PathBuf) {
    let mirror = crate::shared::tempdir::TempDir::new(&format!("guard-settings-{tag}"));
    let clone = mirror.join(".clones/c");
    std::fs::create_dir_all(&clone).unwrap();
    let canon = mirror.canonicalize().unwrap();
    (mirror, canon, clone)
}

fn read(clone: &std::path::Path) -> Value {
    serde_json::from_str(
        &std::fs::read_to_string(clone.join(".claude/settings.local.json")).unwrap(),
    )
    .unwrap()
}

#[test]
fn a_clone_gains_the_exclusion_once_and_keeps_its_other_keys() {
    let (_dir, mirror, clone) = world("once");
    let target = mirror.join("CLAUDE.md").to_string_lossy().into_owned();
    std::fs::create_dir_all(clone.join(".claude")).unwrap();
    std::fs::write(
        clone.join(".claude/settings.local.json"),
        "{\"other\": 1, \"claudeMdExcludes\": [\"/x\"]}",
    )
    .unwrap();
    let said = ensure(&clone);
    assert!(said.starts_with("clone-settings:") && said.contains(&target));
    let got = read(&clone);
    assert_eq!(got["other"], 1);
    assert_eq!(got["claudeMdExcludes"], serde_json::json!(["/x", target]));
    assert_eq!(ensure(&clone), "");
}

#[test]
fn a_fresh_clone_and_an_empty_file_are_written() {
    let (_dir, _, clone) = world("fresh");
    assert!(!ensure(&clone).is_empty());
    assert_eq!(
        read(&clone)["claudeMdExcludes"].as_array().unwrap().len(),
        1
    );
    let (_dir, _, empty) = world("empty");
    std::fs::create_dir_all(empty.join(".claude")).unwrap();
    std::fs::write(empty.join(".claude/settings.local.json"), "").unwrap();
    assert!(!ensure(&empty).is_empty());
}

#[test]
fn the_mirror_is_left_alone_and_a_bad_file_is_reported() {
    let (_dir, mirror, clone) = world("alone");
    assert_eq!(ensure(&mirror), "");
    assert!(!mirror.join(".claude").exists());
    std::fs::create_dir_all(clone.join(".claude")).unwrap();
    std::fs::write(clone.join(".claude/settings.local.json"), "not json").unwrap();
    assert!(ensure(&clone).contains("is not JSON"));
    assert_eq!(
        std::fs::read_to_string(clone.join(".claude/settings.local.json")).unwrap(),
        "not json"
    );
    assert_eq!(ensure(&mirror.join("absent")), "");
}
