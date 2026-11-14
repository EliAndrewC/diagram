//! The crate's shared helpers: Python's path readings, each checked against what Python 3.14 answers for the same text.

use super::{
    abspath, basename, cwd, dirname, py_join, py_path, py_suffix_stem, raised, read_lossy,
    read_strict, realpath, relpath, text,
};
use std::path::Path;

#[test]
fn each_tool_answers_from_the_process() {
    let ask = |verb: &str, a: &[&str]| {
        super::cli(verb, &a.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>())
    };
    assert!(ask("page-session", &["only", "two"])
        .stderr
        .contains("ValueError"));
    for verb in ["brief-load", "coord", "research-claims", "escape-take"] {
        assert_eq!(ask(verb, &[]).code, 2, "{verb}");
    }
    assert_eq!(ask("coord", &["lines", "/no/such/file", "x"]).code, 2);
    // `make append`'s LINE read from the environment, which a test run does not set
    assert!(ask("coord", &["append", "/no/such/x.md"])
        .stderr
        .starts_with("make append: LINE="));
}

#[test]
fn a_raise_and_the_two_reads() {
    let r = raised("coord", "out".to_owned(), "ValueError: x");
    assert_eq!((r.code, r.stdout.as_str()), (1, "out"));
    assert_eq!(
        r.stderr,
        "Traceback (most recent call last):\n  l7r-gate coord\nValueError: x\n"
    );
    let dir = l7r_gate_core::ci::fixtures::scratch("pages-read");
    std::fs::write(dir.join("a"), "a\r\nb\rc").unwrap();
    assert_eq!(read_strict(&dir.join("a")).unwrap(), "a\nb\nc");
    std::fs::write(dir.join("b"), [b'x', 0xff]).unwrap();
    assert!(read_strict(&dir.join("b"))
        .unwrap_err()
        .starts_with("UnicodeDecodeError"));
    assert_eq!(read_lossy(&dir.join("b")), "x\u{fffd}");
    assert!(read_strict(&dir.join("none")).is_err());
    assert_eq!(read_lossy(&dir.join("none")), "");
}

#[test]
fn the_path_texts_read_as_python_reads_them() {
    let ss = |p: &str| py_suffix_stem(Path::new(p));
    assert_eq!(
        ss("d/v2-write.md"),
        ("v2-write".to_owned(), ".md".to_owned())
    );
    assert_eq!(ss(".hidden"), (".hidden".to_owned(), String::new()));
    assert_eq!(ss("a."), ("a".to_owned(), ".".to_owned()));
    assert_eq!(ss("plain"), ("plain".to_owned(), String::new()));
    assert_eq!(
        (py_join("", "b"), py_join("a/", "b"), py_join("a", "b")),
        ("b".to_owned(), "a/b".to_owned(), "a/b".to_owned())
    );
    assert_eq!(
        (basename("/a/b.md"), basename("b"), basename("a/")),
        ("b.md", "b", "")
    );
    assert_eq!(
        (
            dirname("a/b"),
            dirname("/a"),
            dirname("a"),
            dirname("a//b"),
            dirname("//b")
        ),
        ("a", "/", "", "a", "//")
    );
    assert_eq!(abspath("x/../y/./z", "/c"), "/c/y/z");
    assert_eq!(abspath("/a/..//b", "/c"), "/b");
    assert_eq!(relpath("/r/specs/x", "/r", "/"), "specs/x");
    assert_eq!(relpath("/r", "/r", "/"), ".");
    assert_eq!(relpath("/elsewhere/b", "/r/c", "/"), "../../elsewhere/b");
    assert_eq!(relpath("rel", "/c", "/c"), "rel");
    assert!(cwd().starts_with('/'));
    assert_eq!(text(Path::new("/a/b")), "/a/b");
    assert_eq!(py_path("./a//b/"), Path::new("a/b"));
}

#[test]
fn realpath_resolves_each_link_as_it_meets_it() {
    let dir = l7r_gate_core::ci::fixtures::scratch("pages-realpath");
    let d = std::fs::canonicalize(&*dir).unwrap();
    let d = d.to_string_lossy().into_owned();
    std::fs::create_dir_all(format!("{d}/real/sub")).unwrap();
    std::os::unix::fs::symlink(format!("{d}/real"), format!("{d}/abs")).unwrap();
    std::os::unix::fs::symlink("real/sub", format!("{d}/rel")).unwrap();
    std::os::unix::fs::symlink("loop", format!("{d}/loop")).unwrap();
    assert_eq!(
        realpath(&format!("{d}/abs/sub/f"), "/"),
        format!("{d}/real/sub/f")
    );
    // a `..` after a link applies to where the link led, not to the text
    assert_eq!(
        realpath(&format!("{d}/rel/../x"), "/"),
        format!("{d}/real/x")
    );
    assert_eq!(realpath("rel/./sub//", &d), format!("{d}/real/sub/sub"));
    // the same link met twice is read from what it resolved to the first time
    assert_eq!(
        realpath(&format!("{d}/abs/../abs/sub"), "/"),
        format!("{d}/real/sub")
    );
    assert_eq!(realpath(&format!("{d}/loop/x"), "/"), format!("{d}/loop/x"));
    assert_eq!(realpath("/..", "/"), "/");
    assert_eq!(realpath("/a/..", "/"), "/");
    assert_eq!(realpath("missing/../m", "/no/such"), "/no/such/m");
}
