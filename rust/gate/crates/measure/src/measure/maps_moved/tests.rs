//! The cases of `test_maps_moved.py`.

use std::path::{Path, PathBuf};

use super::{cli, moved};

fn git(dir: &Path, args: &[&str]) {
    let done = std::process::Command::new("git")
        .arg("-C")
        .arg(dir)
        .args(args)
        .output()
        .unwrap();
    assert!(done.status.success());
}

fn repo(tag: &str) -> PathBuf {
    let root = crate::checks::scratch(tag);
    git(&root, &["init", "-q"]);
    git(&root, &["config", "user.email", "t@t"]);
    git(&root, &["config", "user.name", "t"]);
    for m in ["sawada", "inashiro"] {
        let d = root.join("pool/hamlets").join(m);
        std::fs::create_dir_all(&d).unwrap();
        std::fs::write(d.join(format!("{m}.json")), "{\"board\": 0}\n").unwrap();
        std::fs::write(d.join(format!("{m}.gen.py")), "# gen\n").unwrap();
    }
    git(&root, &["add", "."]);
    git(&root, &["commit", "-qm", "a"]);
    root
}

fn words(list: &[&str]) -> Vec<String> {
    list.iter().map(|s| (*s).to_owned()).collect()
}

const SAWADA: &str = "pool/hamlets/sawada/sawada";

#[test]
fn names_exactly_the_changed_manifest() {
    let root = repo("mm-changed");
    std::fs::write(root.join(format!("{SAWADA}.json")), "{\"board\": 76.4}\n").unwrap();
    assert_eq!(moved(&root, None), [format!("{SAWADA}.json")]);
    let got = cli(&[], &root);
    assert_eq!(got.stdout, format!("moved against HEAD: {SAWADA}.json\n"));
}

#[test]
fn nothing_moved_says_so() {
    let root = repo("mm-none");
    let got = cli(
        &words(&["--root", &root.display().to_string()]),
        Path::new("/nonexistent"),
    );
    assert_eq!(
        (got.code, got.stdout.as_str()),
        (0, "no pool manifest moved against HEAD\n")
    );
}

#[test]
fn only_reads_one_map_from_its_gen() {
    let root = repo("mm-only");
    std::fs::write(root.join(format!("{SAWADA}.json")), "{\"board\": 76.4}\n").unwrap();
    assert!(moved(&root, Some("pool/hamlets/inashiro/inashiro.gen.py")).is_empty());
    assert_eq!(
        moved(&root, Some(&format!("{SAWADA}.gen.py"))),
        [format!("{SAWADA}.json")]
    );
    assert_eq!(
        moved(&root, Some(&format!("{SAWADA}.json"))),
        [format!("{SAWADA}.json")]
    );
    let got = cli(
        &words(&["--only", "pool/hamlets/inashiro/inashiro.gen.py"]),
        &root,
    );
    assert_eq!(
        got.stdout,
        "this map's manifest is unchanged against HEAD\n"
    );
}

#[test]
fn an_untracked_manifest_counts_as_moved() {
    let root = repo("mm-new");
    let d = root.join("pool/hamlets/kuwabata");
    std::fs::create_dir(&d).unwrap();
    std::fs::write(d.join("kuwabata.json"), "{}\n").unwrap();
    assert_eq!(moved(&root, None), ["pool/hamlets/kuwabata/kuwabata.json"]);
}
