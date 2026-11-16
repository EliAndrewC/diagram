//! A page as the index read it (feature 449 T138): the expected values are `semantic_index.py`'s own (observed 2026-11-16, in the
//! interpreter).

use l7r_guard::shared::tempdir::TempDir;

use super::{fingerprint, first, passages, read_lossy, slice, squeeze, strip_html};

fn chars(s: &str) -> Vec<char> {
    s.chars().collect()
}

#[test]
fn passages_cut_at_a_space_or_at_the_size() {
    assert_eq!(
        passages(&chars(&format!("{} bbb", "a".repeat(10))), 8),
        [(0, 8), (8, 14)]
    );
    assert_eq!(
        passages(&chars(&format!("  {}", "字".repeat(20))), 8),
        [(2, 10), (10, 18), (18, 22)]
    );
    assert_eq!(passages(&chars("aaaa bb cc dd"), 8), [(0, 7), (8, 13)]);
    assert_eq!(passages(&chars(" \u{3000}\x1c "), 8), []);
    // a space before the half is not a cut: the passage takes the size
    assert_eq!(passages(&chars("a bbbbbbbbbb"), 8), [(0, 8), (8, 12)]);
}

#[test]
fn the_record_s_visible_text_and_the_keys() {
    assert_eq!(
        strip_html("<p>A&amp;B <!-- c\n -->\n<b>x</b>&nbsp;y&#x41;</p>"),
        "A&B x yA"
    );
    assert_eq!(squeeze(" a \t\n b "), " a b ");
    assert_eq!(fingerprint("a passage"), "f4508cf8cbc7eb0a6612");
    assert_eq!(fingerprint("一枚の田"), "cdba60cce0b825263d71");
    let c = chars("abcdef");
    assert_eq!(
        (
            slice(&c, 1, 3),
            slice(&c, -2, 99),
            slice(&c, 4, 2),
            slice(&c, -99, -5)
        ),
        ("bc".into(), "ef".into(), String::new(), "a".into())
    );
    assert_eq!(first("日本語", 2), "日本");
}

#[test]
fn a_file_is_read_as_python_reads_text() {
    let dir = TempDir::new("text-read");
    let p = dir.path().join("t.txt");
    std::fs::write(&p, b"a\r\nb\rc\xffd").unwrap();
    assert_eq!(read_lossy(&p).unwrap(), "a\nb\nc\u{fffd}d");
    assert!(read_lossy(&dir.path().join("none")).is_err());
}
