//! Originals stored apart (feature 449 T144; expected values `originals.py`'s on the same text, 2026-11-16).

use super::{has_placeholder, restore, split, units};

#[test]
fn a_run_of_originals_is_one_unit() {
    let t = "original: \u{300c}A\u{300d} and \u{300c}B\u{300d}; original: \u{300c}C\u{300d} / \u{300c}no close";
    assert_eq!(units(t), vec![(0, t.find(" / ").unwrap())]);
    let nested = "original: \u{300c}a\u{ff62}b\u{ff63}\u{300d}, \u{300c}c\u{300d}";
    assert_eq!(units(nested), vec![(0, nested.len())]);
    assert!(units("original: \u{300c}never").is_empty());
}

#[test]
fn an_inline_original_moves_out_and_comes_back() {
    let notes = "<li data-note=\"k\">x original: \u{300c}A\u{300d} y original: \u{300c}B\u{300d}</li>\n<li data-note=\"j\">none</li>";
    let stored = "<li data-orig=\"k#4\">original: \u{300c}Z\u{300d}</li>\n";
    let (moved, kept) = split(notes, stored).unwrap();
    assert_eq!(
        moved,
        "<li data-note=\"k\">x <span class=\"orig\" data-orig=\"k#5\"></span> y <span class=\"orig\" data-orig=\"k#6\"></span></li>\n<li data-note=\"j\">none</li>"
    );
    assert_eq!(
        kept,
        format!("{stored}<li data-orig=\"k#5\">original: \u{300c}A\u{300d}</li>\n<li data-orig=\"k#6\">original: \u{300c}B\u{300d}</li>\n")
    );
    assert!(has_placeholder(&moved));
    assert_eq!(restore(&moved, &kept, false).unwrap(), notes);
    assert!(restore(&moved, &kept, true)
        .unwrap()
        .contains("<span class=\"orig\">original: \u{300c}A\u{300d}</span>"));
    // a placeholder already numbered past the stored ones sets where new ones start
    let (again, _) = split("<li data-note=\"k\"><span class=\"orig\" data-orig=\"k#9\"></span> original: \u{300c}Q\u{300d}</li>", "").unwrap();
    assert!(again.contains("k#10"));
}

#[test]
fn what_the_originals_refuse() {
    assert_eq!(
        restore("<span class=\"orig\" data-orig=\"k#9\"></span>", "", true)
            .unwrap_err()
            .message,
        "no original stored for `k#9` - its `.originals.html` lacks `<li data-orig=\"k#9\">`"
    );
    assert_eq!(
        split("", "<li data-orig=\"k#x\">o</li>")
            .unwrap_err()
            .message,
        "invalid literal for int() with base 10: 'x'"
    );
    assert_eq!(
        split("", "<li data-orig=\"k\">o</li>").unwrap_err().message,
        "not enough values to unpack (expected 2, got 1)"
    );
    let bad = "<li data-note=\"k\"><span class=\"orig\" data-orig=\"k#-\"></span></li>";
    assert_eq!(split(bad, "").unwrap_err().kind, "ValueError");
    assert_eq!(
        split("", "<li data-orig=\"k#+2\">o</li>").unwrap().1,
        "<li data-orig=\"k#+2\">o</li>"
    );
}
