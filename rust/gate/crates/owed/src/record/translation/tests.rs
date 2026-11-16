//! The translated quotations a delta owes, read in process by the `research` crate (feature 449 T145).

use super::{cli, owed};
use crate::record::testkit::{commit, edit_everything, git, put, record};
use std::os::unix::fs::PermissionsExt as _;

fn args(list: &[&str]) -> Vec<String> {
    list.iter().map(|s| (*s).to_owned()).collect()
}

/// The notes a translated pair and a gloss are read from, in the record's own forms (feature 449 T145: read in process, where stubs of the
/// Python stood in).
const TRANSLATED: &str = "<li data-note=\"t\">\u{300c}the hedges\u{300d} (translated; original: \u{300c}\u{57a3}\u{6839}\u{300d})</li>\n<li data-note=\"m\">\u{300c}a run\u{300d} (translated from the Chinese by Legge; original: \u{300c}\u{4e00}\u{300d}\u{300c}\u{4e8c}\u{300d})</li>\n<li data-note=\"g\">\u{6728} (ki, \"tree\") is ours.</li>\n";

#[test]
fn a_new_pair_or_gloss_is_owed_and_a_kept_one_is_not() {
    let root = record("translation-owed");
    assert!(owed(&root).unwrap().is_empty());
    edit_everything(&root);
    put(
        &root,
        "research/questions/0094-trade.notes.html",
        TRANSLATED,
    );
    put(
        &root,
        "research/questions/citations/0001-x.notes.html",
        "<li data-note=\"c\">\u{300c}skip\u{300d} (translated; original: \u{300c}me\u{300d})</li>",
    );
    let rows = owed(&root).unwrap();
    assert!(rows
        .iter()
        .any(|r| r.1 == "t" && r.3 == "the hedges" && r.4 == "\u{57a3}\u{6839}"));
    assert!(rows
        .iter()
        .any(|r| r.1 == "a term's gloss" && r.3 == "tree (read ki)"));
    assert!(rows
        .iter()
        .any(|r| r.1 == "m" && r.2 == "the Chinese" && r.4 == "\u{4e00} ... \u{4e8c}"));
    assert!(owed(&root).unwrap() == rows);
    let r = root.to_string_lossy().into_owned();
    let all = cli(&args(&["--root", &r]));
    assert!(all.stdout.starts_with("translation-owed: ") && all.stdout.contains("  ORIGINAL:    "));
    assert!(cli(&args(&["--root", &r, "--q", "0094"]))
        .stdout
        .contains("TRANSLATION: the hedges"));
    assert!(cli(&args(&["--root", &r, "--q", "0095"]))
        .stdout
        .starts_with("translation-owed: 0 "));
    assert_eq!(cli(&args(&["--x"])).code, 2);
    // a pair the merge base already holds is owed no more
    let kept = commit(&root, "the pairs");
    git(&root, &["update-ref", "refs/remotes/origin/main", &kept]);
    assert!(owed(&root).unwrap().is_empty());
    let notes = root.join("research/questions/0094-trade.notes.html");
    std::fs::set_permissions(&notes, std::fs::Permissions::from_mode(0o000)).unwrap();
    let r0 = root.to_string_lossy().into_owned();
    assert_eq!(cli(&args(&["--root", &r0])).code, 1);
    std::fs::set_permissions(&notes, std::fs::Permissions::from_mode(0o644)).unwrap();
    git(&root, &["update-ref", "-d", "refs/remotes/origin/main"]);
    commit(&root, "no base");
    assert_eq!(owed(&root).unwrap().len(), rows.len());
    std::fs::write(
        root.join(".git/record-checks/translation-pairs.json"),
        "[1]",
    )
    .unwrap();
    assert_eq!(owed(&root).unwrap().len(), rows.len());
}

#[test]
fn a_tree_that_is_no_repository_and_a_root_that_is_not_there() {
    let plain = crate::checks::scratch("translation-plain");
    put(
        &plain,
        "research/questions/0001-a.notes.html",
        "<li data-note=\"a\">\u{300c}q\u{300d} (translated; original: \u{300c}o\u{300d})</li>",
    );
    assert_eq!(owed(&plain).unwrap().len(), 1);
    // a directory with no record owes nothing: the parse is keyed by the parser built in, where it read two `.py` files off the tree
    // and failed with them missing (feature 449 T145)
    let empty = l7r_guard::shared::tempdir::TempDir::new("translation-empty-root");
    let e = empty.to_string_lossy().into_owned();
    let none = cli(&args(&["--root", &e]));
    assert_eq!((none.code, none.stdout.as_str()), (0, "translation-owed: 0 translated quotation(s) new or changed since the merge base - each owes a translation-check\n"));
    // a root that is no directory fails as the Python's first `git` failed, with `cwd=root` (feature 449 T145, failure parity)
    let gone = cli(&args(&["--root", "/nonexistent/at/all"]));
    assert_eq!(
        (gone.code, gone.stdout.as_str(), gone.stderr.as_str()),
        (1, "", "FileNotFoundError: [Errno 2] No such file or directory: PosixPath('/nonexistent/at/all')\n")
    );
    let file = empty.join("a-file");
    std::fs::write(&file, "x").unwrap();
    let f = file.to_string_lossy().into_owned();
    assert_eq!(
        cli(&args(&["--root", &f])).stderr,
        format!("NotADirectoryError: [Errno 20] Not a directory: PosixPath('{f}')\n")
    );
}
