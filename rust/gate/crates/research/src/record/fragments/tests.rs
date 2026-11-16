//! Where a registry fragment lives (feature 449 T144; expected values `fragments.py`'s).

use super::{key_of, ordered, page_dir, position_of};

#[test]
fn a_fragment_name_reads_as_the_python_reads_it() {
    assert_eq!(page_dir("SOURCES.html"), "sources");
    assert_eq!(page_dir("ways.html"), "ways");
    assert_eq!(page_dir("ways"), "ways");
    assert_eq!(key_of("work-fei-1939"), "fei-1939");
    assert_eq!(key_of("fei-1939"), "fei-1939");
    let names: Vec<String> = [
        "020-b.html",
        "_front.html",
        "3-a.html",
        "010-c.html",
        "x.txt",
        "\u{0661}0-d.html",
    ]
    .iter()
    .map(|s| (*s).to_owned())
    .collect();
    assert_eq!(
        ordered(&names),
        ["3-a.html", "010-c.html", "\u{0661}0-d.html", "020-b.html"]
    );
    assert_eq!(position_of("040-x.html\n").unwrap(), 40);
    assert_eq!(
        position_of("bad.html").unwrap_err().message,
        "bad.html: a fragment of an ordered kind must be named <prefix>-<id>.html"
    );
    assert_eq!(
        position_of("99999999999999999999999999999999999999999-x.html").unwrap(),
        u128::MAX
    );
}
