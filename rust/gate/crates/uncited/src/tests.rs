//! The crate's helpers (feature 449 T147; the port's answers on hand-made input, read against the Python's code; the T147 differential (`make diff-run`) holds them to the Python on the real record).

use std::path::Path;

use super::*;
use crate::testkit::W;

#[test]
fn text_helpers_read_as_python_reads() {
    assert_eq!(squeeze("a \t\n b\x1c c"), "a b c");
    assert_eq!(strip("\u{2003} x \n"), "x");
    assert_eq!((chars("日本"), first("日本語", 2)), (2, "日本".to_owned()));
    // a CJK character a token, four others one
    assert_eq!(tokens("日本abcdefgh\u{ac00}\u{f900}"), 4 + 2);
    assert_eq!(
        lines_keep("a\r\nb\rc\nd\x0be\u{2028}f"),
        ["a\r\n", "b\r", "c\n", "d\x0b", "e\u{2028}", "f"]
    );
    assert_eq!(lines_keep("a\n"), ["a\n"]);
    assert_eq!(lines("a\r\nb\n\nc"), ["a", "b", "", "c"]);
    assert!(py(r"\s").is_match("\u{1f}").unwrap());
    assert_eq!(base(Path::new("/r")), Path::new("/r"));
    assert_eq!(record_dir(Path::new("/r")), Path::new("/r/research"));
    assert_eq!(today().len(), 10);
}

#[test]
fn files_read_and_refused_as_python_named_them() {
    let w = W::new("lib-files");
    w.put("a.txt", "x\r\ny\rz");
    assert_eq!(read_text(&w.root().join("a.txt")).unwrap(), "x\ny\nz");
    let missing = read_text(&w.root().join("nope")).unwrap_err();
    assert_eq!(missing.kind, "FileNotFoundError");
    assert!(
        missing
            .message
            .starts_with("[Errno 2] No such file or directory: '"),
        "{}",
        missing.message
    );
    std::fs::write(w.root().join("bad.txt"), [0xff]).unwrap();
    assert_eq!(
        read_text(&w.root().join("bad.txt")).unwrap_err().kind,
        "UnicodeDecodeError"
    );
    assert_eq!(read_text(w.root()).unwrap_err().kind, "IsADirectoryError");
    assert_eq!(
        write_text(&w.root().join("a.txt/x"), "").unwrap_err().kind,
        "NotADirectoryError"
    );
    let ro = w.root().join("ro");
    std::fs::create_dir_all(&ro).unwrap();
    std::fs::set_permissions(&ro, std::os::unix::fs::PermissionsExt::from_mode(0o500)).unwrap();
    let denied = write_text(&ro.join("f"), "");
    std::fs::set_permissions(&ro, std::os::unix::fs::PermissionsExt::from_mode(0o700)).unwrap();
    assert_eq!(denied.unwrap_err().kind, "PermissionError");
    let other = os_error(&std::io::Error::other("odd"), Path::new("p"));
    assert_eq!(
        (other.kind, other.message.as_str()),
        ("OSError", "[Errno 0] odd: 'p'")
    );
    assert_eq!(loads("{").unwrap_err().kind, "JSONDecodeError");
    assert_eq!(name_of(Path::new("/a/b.html")), "b.html");
    assert_eq!(text_of(w.home(), "https://nowhere.org/x").unwrap(), None);
    w.page("https://e.org/p", "the page", "fetch");
    assert_eq!(
        text_of(w.home(), "https://e.org/p").unwrap().as_deref(),
        Some("the page")
    );
}

#[test]
fn the_registrys_files_and_keys() {
    let w = W::new("lib-registry");
    for name in [
        "12-x.html",
        "1-.html",
        "1a-y.html",
        "x-1.html",
        ".9-h.html",
        "3-a-b.html",
        "1.html",
    ] {
        assert_eq!(
            numbered_html(name),
            !matches!(name, "x-1.html" | ".9-h.html" | "1.html"),
        );
    }
    assert_eq!(key_of("12-x.html"), Some("x"));
    assert_eq!(key_of("3-a-b.html"), Some("a-b"));
    assert_eq!(key_of("\u{661}-k.html"), Some("k"));
    for name in ["1a-y.html", "1-.html", "x.html", "-k.html", "1-a\nb.html"] {
        assert_eq!(key_of(name), None, "{name}");
    }
    w.uncited("0100-u-key.html", "<p>https://u.org/p</p>");
    w.put("research/sources/010-works-cited/1a-odd.html", "");
    let files: Vec<String> = registry_files(w.root())
        .iter()
        .map(|f| name_of(f))
        .collect();
    assert_eq!(
        files,
        [
            "0010-src-a.html",
            "0020-l7r-notes.html",
            "0030-grok.html",
            "1a-odd.html",
            "0100-u-key.html"
        ]
    );
    let keys: Vec<String> = registry_keys(w.root()).into_iter().collect();
    assert_eq!(keys, ["grok", "l7r-notes", "src-a", "u-key"]);
    let found = entry_files(
        &w.root().join("research/sources/040-uncited-works"),
        "u-key",
    );
    assert_eq!(found.len(), 1);
    assert!(entry_files(&w.root().join("research/sources/040-uncited-works"), "key").is_empty());
    assert!(entries(&w.root().join("no-such")).is_empty());
}

#[test]
fn a_directory_made_and_a_file_removed() {
    let w = W::new("lib-fs");
    w.put("f", "x");
    assert_eq!(
        mkdir(&w.root().join("f")).unwrap_err().kind,
        "FileExistsError"
    );
    assert_eq!(
        mkdir(&w.root().join("f/g")).unwrap_err().kind,
        "NotADirectoryError"
    );
    mkdir(&w.root().join("d/e")).unwrap();
    remove_file(&w.root().join("f")).unwrap();
    assert_eq!(
        remove_file(&w.root().join("f")).unwrap_err().kind,
        "FileNotFoundError"
    );
}
