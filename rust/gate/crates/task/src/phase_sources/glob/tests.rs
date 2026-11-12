//! `Path.glob` as an `old-code:` line's patterns are matched (feature 449 T131): checked case by case against `CPython` 3.14 on the same
//! tree in the differential (`scratchpad/t131/diff.py`, the `ts-phase-*` cases).

use std::path::{Path, PathBuf};

use l7r_gate_core::ci::fixtures::{put, scratch};

use super::{glob, part_regex};

fn names(root: &Path, pattern: &str) -> Vec<String> {
    let mut out: Vec<String> = glob(root, pattern)
        .unwrap()
        .iter()
        .map(|p| {
            p.strip_prefix(root)
                .unwrap_or(p)
                .to_string_lossy()
                .into_owned()
        })
        .collect();
    out.sort();
    out
}

#[test]
fn each_part_matches_as_fnmatch_does() {
    let m = |pat: &str, name: &str| part_regex(pat).unwrap().is_match(name).unwrap();
    assert!(m("*.py", ".hidden.py") && m("a?c", "abc") && !m("a?c", "ac"));
    assert!(m("[ab].py", "a.py") && !m("[!a].py", "a.py") && m("[!a].py", "b.py"));
    assert!(m("[]x]", "]") && m("[!]x]", "y") && m("[^x]", "^"));
    assert!(m("[a", "[a") && m("[\\]", "\\") && m("a.b", "a.b") && !m("a.b", "axb"));
    // fnmatch's ranges: an empty one dropped, a class of nothing matching nothing, its negation anything
    assert!(
        !m("[z-a].py", "z.py") && m("[!z-a]", "q") && m("[a-cz-a]", "b") && !m("[a-cz-a]", "z")
    );
    assert!(
        m("[a-]", "-") && m("[-a]", "-") && m("[a-c-e]", "-") && m("[&~|]", "~") && m("[a[]", "[")
    );
    assert!(
        m("[!a[]", "b")
            && !m("[!a[]", "[")
            && m("[^a]", "^")
            && !m("[^a]", "b")
            && m("[\\-z]", "y")
    );
    // a part the engine cannot compile raises, where Python would have compiled it (no `old-code:` line reaches it)
    assert!(part_regex(&"?".repeat(400_000))
        .unwrap_err()
        .starts_with("re.error"));
}

#[test]
fn a_pattern_walks_the_tree_as_path_glob_walks_it() {
    let dir = scratch("task-glob");
    let root: PathBuf = dir.to_path_buf();
    for f in [
        "a.py",
        "b.py",
        ".c.py",
        "sub/d.py",
        "sub/deep/e.py",
        "sub/deep/f.txt",
    ] {
        put(&root, f, "");
    }
    std::os::unix::fs::symlink(root.join("sub"), root.join("link")).unwrap();
    assert_eq!(names(&root, "*.py"), vec![".c.py", "a.py", "b.py"]);
    assert_eq!(
        names(&root, "**/*.py"),
        vec![".c.py", "a.py", "b.py", "sub/d.py", "sub/deep/e.py"]
    );
    assert_eq!(
        names(&root, "sub/**"),
        vec![
            "sub",
            "sub/d.py",
            "sub/deep",
            "sub/deep/e.py",
            "sub/deep/f.txt"
        ]
    );
    assert_eq!(names(&root, "*/d.py"), vec!["link/d.py", "sub/d.py"]);
    assert_eq!(names(&root, "a.py"), vec!["a.py"]);
    assert_eq!(names(&root, "none.py"), Vec::<String>::new());
    assert_eq!(names(&root, "./sub//d.py"), vec!["sub/d.py"]);
    assert_eq!(names(&root, "sub/"), vec!["sub"]);
    assert_eq!(names(&root, "a.py/"), Vec::<String>::new());
    assert!(glob(&root, "").unwrap_err().starts_with("ValueError"));
    assert!(glob(&root, "/etc/*")
        .unwrap_err()
        .starts_with("NotImplementedError"));
    assert_eq!(names(&root, "[z-a].py"), Vec::<String>::new());
    assert!(glob(&root, &format!("{}/x", "?".repeat(400_000))).is_err());
}
