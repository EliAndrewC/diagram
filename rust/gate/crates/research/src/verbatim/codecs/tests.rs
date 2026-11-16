//! `CPython`'s strict decoders (feature 449 T145; each expected value `CPython` 3.14.4's on the same bytes, 2026-11-16).

use super::{decode, lookup};

#[test]
fn each_codec_decodes_as_cpython_does() {
    let cases: [(&str, &[u8], Option<&str>); 19] = [
        ("cp932", b"\x93\xfa\x96\x7b", Some("日本")),
        ("cp932", b"\x81", None),
        ("cp932", b"\xa0\xfd", Some("\u{f8f0}\u{f8f1}")),
        ("shift_jis", b"\x82\xa0", Some("あ")),
        ("euc_jp", b"\xa4\xa2\x8e\xb1\x8f\xb0\xa1", Some("あｱ丂")),
        ("euc_jp", b"\x8f\xa1", None),
        ("gb2312", b"\xc4\xe3", Some("你")),
        (
            "gb18030",
            b"\x81\x30\x81\x30\x90\x30\x81\x30\xa1\xa1",
            Some("\u{80}\u{10000}\u{3000}"),
        ),
        ("gb18030", b"\x84\x31\xa5\x30", None),
        ("gb18030", b"\xe3\x32\x9a\x36", None),
        ("big5", b"\xa4\x40", Some("一")),
        ("big5", b"\x87\x40", None),
        ("cp1252", b"\x80\x81", None),
        ("cp1252", b"\x80", Some("€")),
        ("latin_1", b"\xe9", Some("é")),
        ("ascii", b"\xe9", None),
        ("ascii", b"ab", Some("ab")),
        ("utf-8", b"\xe6\x9d\xb1", Some("東")),
        ("utf-8", b"\xed\xa0\x80", None),
    ];
    for (name, raw, want) in cases {
        assert_eq!(decode(raw, name).as_deref(), want, "{name} {raw:?}");
    }
    assert_eq!(decode(b"x", "koi8-r"), None);
    assert_eq!(decode(b"\x81\x30\x81\x3a", "gb18030"), None);
}

#[test]
fn a_name_is_found_as_cpython_finds_it() {
    for (name, want) in [
        ("UTF-8", Some("utf_8")),
        ("utf8", Some("utf_8")),
        ("Shift_JIS", Some("shift_jis")),
        ("x-sjis", None),
        ("windows-31j", Some("cp932")),
        ("ISO-8859-1", Some("latin_1")),
        ("euc-jp", Some("euc_jp")),
        ("gb2312", Some("gb2312")),
        ("windows-1252", Some("cp1252")),
        ("us-ascii", Some("ascii")),
        ("iso 8859.1", Some("latin_1")),
        ("-utf--8é-", Some("utf_8")),
        ("nope", None),
        ("gb.2312", None),
    ] {
        assert_eq!(lookup(name), want, "{name}");
    }
}
