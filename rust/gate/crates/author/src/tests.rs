//! The crate's shared helpers.

use super::{raised, read_strict};

#[test]
fn a_raise_and_a_strict_read() {
    let r = raised("claim", "out".to_owned(), "before\n", "ValueError: x");
    assert_eq!((r.code, r.stdout.as_str()), (1, "out"));
    assert_eq!(
        r.stderr,
        "before\nTraceback (most recent call last):\n  l7r-gate claim\nValueError: x\n"
    );
    let dir = l7r_gate_core::ci::fixtures::scratch("author-read");
    std::fs::write(dir.join("a"), "a\r\nb\rc").unwrap();
    assert_eq!(read_strict(&dir.join("a")).unwrap(), "a\nb\nc");
    std::fs::write(dir.join("b"), [0xff]).unwrap();
    assert!(read_strict(&dir.join("b"))
        .unwrap_err()
        .starts_with("UnicodeDecodeError"));
    assert!(read_strict(&dir.join("none")).is_err());
}
