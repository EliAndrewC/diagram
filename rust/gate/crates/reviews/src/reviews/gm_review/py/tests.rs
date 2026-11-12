//! Python's own readings, each against what `CPython` 3.14 answers (the values below are its).

use std::path::Path;

use serde_json::json;

use super::{
    columns, columns_of, decode_error, get, has, head, py_int, read_text, rstrip, stdout_columns,
    stty_columns, text, truthy, wrap, wrote, Raised,
};

#[test]
fn a_rows_in_and_get_as_python_reads_them() {
    assert!(has(&json!({"reviewed": 1}), "reviewed").unwrap());
    assert!(has(&json!(["reviewed"]), "reviewed").unwrap());
    assert!(!has(&json!([1]), "reviewed").unwrap());
    assert!(has(&json!("was reviewed"), "reviewed").unwrap());
    for (v, t) in [
        (json!(1), "int"),
        (json!(1.5), "float"),
        (json!(null), "NoneType"),
        (json!(true), "bool"),
    ] {
        assert_eq!(
            has(&v, "x").unwrap_err(),
            Raised::Trace(format!(
                "TypeError: argument of type '{t}' is not a container or iterable"
            ))
        );
    }
    assert_eq!(get(&json!({"a": 1}), "a").unwrap(), Some(&json!(1)));
    for (v, t) in [
        (json!("s"), "str"),
        (json!([]), "list"),
        (json!({}), "dict"),
    ] {
        let named = if t == "dict" {
            get(&v, "a").unwrap().is_none()
        } else {
            get(&v, "a").unwrap_err()
                == Raised::Trace(format!(
                    "AttributeError: '{t}' object has no attribute 'get'"
                ))
        };
        assert!(named);
    }
    assert_eq!(text(&json!({"a": null}), "a").unwrap(), "None");
    assert_eq!(text(&json!({}), "a").unwrap(), "");
    assert_eq!(format!("{}", Raised::Exit("bye".to_owned())), "bye");
    assert_eq!(super::type_name(&json!({})), "dict");
}

#[test]
fn truth_and_int_and_slices() {
    for (v, want) in [
        (None, false),
        (Some(json!(null)), false),
        (Some(json!(false)), false),
        (Some(json!(true)), true),
        (Some(json!(0)), false),
        (Some(json!(0.0)), false),
        (Some(json!(2)), true),
        (Some(json!("")), false),
        (Some(json!("x")), true),
        (Some(json!([])), false),
        (Some(json!([0])), true),
        (Some(json!({})), false),
        (Some(json!({"a": 1})), true),
    ] {
        assert_eq!(truthy(v.as_ref()), want, "{v:?}");
    }
    for (s, n) in [
        ("7", 7),
        (" 7\n", 7),
        ("+7", 7),
        ("-7", -7),
        ("0_1", 1),
        ("007", 7),
    ] {
        assert_eq!(py_int(s).unwrap(), n, "{s}");
    }
    // the last overflows i128, where Python's int has no bound: a row number past 10^38, which no queue reaches
    for s in [
        "",
        "-",
        "x",
        "1.5",
        "_1",
        "1_",
        "1__0",
        "1 2",
        "99999999999999999999999999999999999999999",
    ] {
        assert_eq!(
            py_int(s).unwrap_err(),
            Raised::Refused(format!(
                "invalid literal for int() with base 10: {}",
                l7r_guard::shared::py_text::repr(s)
            ))
        );
    }
    assert_eq!(head("abcdef", 3), "abc");
    assert_eq!(head("abcdef", 30), "abcdef");
    assert_eq!(head("abcdef", -2), "abcd");
    assert_eq!(head("abc", -9), "");
    assert_eq!(head("caf\u{e9}s", 4), "caf\u{e9}");
    assert_eq!(rstrip("a \u{a0}\x1c"), "a");
}

#[test]
fn a_files_bad_bytes_raise_as_pythons_decoder_words_them() {
    let cases: [(&[u8], &str); 5] = [
        (
            b"ab\xff",
            "can't decode byte 0xff in position 2: invalid start byte",
        ),
        (
            b"\xc3(",
            "can't decode byte 0xc3 in position 0: invalid continuation byte",
        ),
        (
            b"x\xe2\x82(",
            "can't decode bytes in position 1-2: invalid continuation byte",
        ),
        (
            b"\xe2\x82",
            "can't decode bytes in position 0-1: unexpected end of data",
        ),
        (
            b"ok\xc3",
            "can't decode byte 0xc3 in position 2: unexpected end of data",
        ),
    ];
    for (bytes, want) in cases {
        let e = std::str::from_utf8(bytes).unwrap_err();
        assert_eq!(
            decode_error(bytes, &e),
            format!("'utf-8' codec can't {}", &want[6..])
        );
    }
    let d = super::super::super::tests::dir("gm-py-read");
    std::fs::write(d.join("crlf"), "a\r\nb\rc\n").unwrap();
    assert_eq!(read_text(&d.join("crlf")).unwrap(), "a\nb\nc\n");
    std::fs::write(d.join("bad"), b"\xff").unwrap();
    assert!(
        matches!(read_text(&d.join("bad")), Err(Raised::Refused(m)) if m.ends_with("invalid start byte"))
    );
    assert!(
        matches!(read_text(&d.join("none")), Err(Raised::Trace(m)) if m.starts_with("OSError"))
    );
    let failed = std::fs::write(d.join("no/such"), "x");
    assert!(
        matches!(wrote(Path::new("x"), failed), Err(Raised::Trace(m)) if m.starts_with("OSError"))
    );
}

/// A terminal 80 columns wide, and one that says it has none.
const EIGHTY: fn() -> Option<usize> = || Some(80);
const ZERO: fn() -> Option<usize> = || Some(0);

#[test]
fn the_terminal_width_as_shutil_reads_it() {
    assert_eq!(columns_of(Some("60"), true, EIGHTY, 140), 60);
    assert_eq!(columns_of(Some(" 61 "), false, EIGHTY, 140), 61);
    for env in [None, Some("0"), Some("-3"), Some("abc")] {
        assert_eq!(columns_of(env, true, EIGHTY, 140), 80);
        assert_eq!(columns_of(env, false, EIGHTY, 140), 140);
        assert_eq!(columns_of(env, true, ZERO, 110), 110);
    }
    // not a terminal here: stty refuses, the fallback stands
    let _ = stdout_columns();
    assert_eq!(
        stty_columns(std::fs::File::open("/dev/null").unwrap()),
        None
    );
    assert!(columns(77) > 0);
}

#[test]
fn textwrap_as_python_wraps() {
    let w = |t: &str, width: i128, a: &str, b: &str| wrap(t, width, a, b);
    assert_eq!(w("", 10, "", ""), Vec::<String>::new());
    assert_eq!(w("   ", 10, "", ""), Vec::<String>::new());
    assert_eq!(
        w("one two three four", 9, "", ""),
        ["one two", "three", "four"]
    );
    assert_eq!(
        w("a well-known-and-loved word", 12, "", ""),
        ["a well-", "known-and-", "loved word"]
    );
    assert_eq!(w("x--y em--dashes", 6, "", ""), ["x--y", "em--", "dashes"]);
    assert_eq!(w("abcdefghij", 4, "", ""), ["abcd", "efgh", "ij"]);
    assert_eq!(w("ab-cdefghij", 5, "", ""), ["ab-cd", "efghi", "j"]);
    assert_eq!(w("a1-bcdefgh", 5, "", ""), ["a1-", "bcdef", "gh"]);
    assert_eq!(w("--------abc", 5, "", ""), ["-----", "---ab", "c"]);
    assert_eq!(
        w("tab\there\nnew\rline", 30, "", ""),
        ["tab     here new line"]
    );
    assert_eq!(w("a\x0bb\x0cc", 30, "", ""), ["a b c"]);
    assert_eq!(
        w("the label: some text here", 14, "    ", "      "),
        ["    the label:", "      some", "      text", "      here"]
    );
    assert_eq!(
        w("abc def", 2, "    ", "      "),
        ["    a", "      b", "      c", "      d", "      e", "      f"]
    );
    assert_eq!(w("abc  def", 4, "", ""), ["abc", "def"]);
    assert_eq!(w("abcd efghijklmn", 5, "", ""), ["abcd", "efghi", "jklmn"]);
    assert_eq!(w("café naïve über", 6, "", ""), ["café", "naïve", "über"]);
}
