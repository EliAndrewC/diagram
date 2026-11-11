//! The translated quotations a delta owes, through the stubs of `quote_verbatim` and `style_prepass`.

use super::{cli, owed};
use crate::record::testkit::{commit, edit_everything, git, put, record};

fn args(list: &[&str]) -> Vec<String> {
    list.iter().map(|s| (*s).to_owned()).collect()
}

#[test]
fn a_new_pair_or_gloss_is_owed_and_a_kept_one_is_not() {
    let root = record("translation-owed");
    assert!(owed(&root).unwrap().is_empty());
    edit_everything(&root);
    put(
        &root,
        "research/questions/citations/0001-x.notes.html",
        "<li data-note=\"c\">\"skip\" \u{300c}me\u{300d}</li>",
    );
    let rows = owed(&root).unwrap();
    assert!(rows.iter().any(|r| r.1 == "t" && r.3 == "the hedges"));
    assert!(rows
        .iter()
        .any(|r| r.1 == "a term's gloss" && r.3 == "tree (read ki)"));
    assert!(rows.iter().any(|r| r.4 == "more ... x"));
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
    put(
        &root,
        "research/questions/0096-new.notes.html",
        "<li data-note=\"a\">\"q\" \u{300c}o\u{300d}</li>",
    );
    put(
        &root,
        "scripts/record/quote_verbatim.py",
        "raise ImportError('x')\n",
    );
    assert_eq!(cli(&args(&["--root", &r])).code, 1);
    std::fs::remove_file(root.join("scripts/record/style_prepass.py")).unwrap();
    assert!(owed(&root).is_err(), "a reader it cannot key");
    std::fs::write(root.join("research/questions/0097-bad.notes.html"), [0xff]).unwrap();
    assert!(owed(&root).is_err());
    git(&root, &["update-ref", "-d", "refs/remotes/origin/main"]);
    std::fs::remove_file(root.join("research/questions/0097-bad.notes.html")).unwrap();
    put(
        &root,
        "scripts/record/style_prepass.py",
        "def glosses(h):\n    return []\n",
    );
    put(
        &root,
        "scripts/record/quote_verbatim.py",
        "def _strip(b):\n    return b\n\ndef passages(t):\n    return []\n",
    );
    commit(&root, "no base");
    assert!(owed(&root).unwrap().is_empty());
    std::fs::write(
        root.join(".git/record-checks/translation-pairs.json"),
        "[1]",
    )
    .unwrap();
    assert!(owed(&root).unwrap().is_empty());
}

#[test]
fn a_tree_that_is_no_repository_and_a_root_that_is_not_there() {
    let plain = crate::checks::scratch("translation-plain");
    crate::record::testkit::stubs(&plain);
    put(
        &plain,
        "research/questions/0001-a.notes.html",
        "<li data-note=\"a\">\"q\" \u{300c}o\u{300d}</li>",
    );
    assert_eq!(owed(&plain).unwrap().len(), 1);
    assert_eq!(cli(&args(&["--root", "/nonexistent/at/all"])).code, 1);
}
