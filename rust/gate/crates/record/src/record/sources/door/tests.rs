//! The page cache's door for the Python that stays (feature 449 T145): a page stored and told back, and each refusal.

use l7r_guard::shared::tempdir::TempDir;

use super::put_cli;

const LIST: &str = r#"{"domains": [{"domain": "bad.example", "reason": "machine text", "approved": {"date": "2026-10-02", "words": "block it"}}]}"#;

fn a(list: &[&str]) -> Vec<String> {
    list.iter().map(|s| (*s).to_owned()).collect()
}

#[test]
fn a_page_is_stored_and_its_meta_told_back() {
    let d = TempDir::new("sources-door-put");
    let root = d.join("c");
    std::fs::create_dir_all(root.join(".git")).unwrap();
    std::fs::create_dir_all(root.join("research")).unwrap();
    std::fs::write(root.join("research/blocked-domains.json"), LIST).unwrap();
    let home = d.join("home").to_string_lossy().into_owned();
    let got = put_cli(
        &a(&[
            "--home",
            &home,
            "--url",
            "https://e.org/a",
            "--fetched",
            "2026-11-01T00:00:00+00:00",
            "--origin",
            "wayback",
            "--inexact",
        ]),
        &root,
        &mut "One. Two.".as_bytes(),
    );
    assert_eq!(got.code, 0, "{}", got.stderr);
    let said: serde_json::Value = serde_json::from_str(&got.stdout).unwrap();
    assert_eq!(
        (
            said["origin"].as_str(),
            said["exact"].as_bool(),
            said["chars"].as_u64()
        ),
        (Some("wayback"), Some(false), Some(9))
    );
    assert_eq!(said["files"], serde_json::json!(["page.txt"]));
    let dir = std::path::PathBuf::from(said["dir"].as_str().unwrap());
    assert_eq!(
        std::fs::read_to_string(dir.join("text.txt")).unwrap(),
        "One. Two."
    );
    // an empty time is the Python's falsy one: now
    let now = put_cli(
        &a(&["--home", &home, "--url", "https://e.org/b", "--fetched", ""]),
        &root,
        &mut "x".as_bytes(),
    );
    assert!(!now.stdout.contains("\"fetched\": \"\""));
    assert_eq!(
        put_cli(
            &a(&["--home", &home, "--url", "https://bad.example/x"]),
            &root,
            &mut "x".as_bytes()
        )
        .code,
        1
    );
    assert_eq!(
        put_cli(&a(&["--home", &home]), &root, &mut "x".as_bytes()).code,
        2
    );
    assert_eq!(put_cli(&a(&["--nope"]), &root, &mut "x".as_bytes()).code, 2);
    // the verb as `sources` dispatches it (refused before it reads stdin)
    assert_eq!(super::super::cli(&a(&["put", "--nope"]), &root).code, 2);
    assert_eq!(
        put_cli(
            &a(&["--home", &home, "--url", "https://e.org/c"]),
            &root,
            &mut [0xffu8].as_slice()
        )
        .code,
        1
    );
}
