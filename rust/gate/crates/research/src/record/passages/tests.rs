//! Several passages as a list (feature 449 T144; expected values `passages.py`'s on the same text, 2026-11-16).

use super::{bulleted, bulleted_notes};

const KEY: &str = "<a href=\"https://e.org\"><code>src-1</code></a>";

#[test]
fn passages_at_depth_zero_become_a_list() {
    let body = format!("{KEY} - \"one\" ; \"two\": \"three (a; \u{300c}b\u{300d})\" <!-- c; \"d\" --> / <a href=\"x\">y</a>  ");
    assert_eq!(
        bulleted(&body),
        format!("{KEY}<span class=\"sep\"> - </span><span class=\"passages\"><span class=\"pass\">\"one\"</span><span class=\"sep\"> ; </span><span class=\"pass\">\"two\":</span><span class=\"sep\"> </span><span class=\"pass sub\">\"three (a; \u{300c}b\u{300d})\" <!-- c; \"d\" --></span><span class=\"sep\"> / </span><span class=\"pass sub\"><a href=\"x\">y</a></span></span>  ")
    );
    assert_eq!(bulleted("no key"), "no key");
    assert_eq!(
        bulleted(&format!("{KEY} - one only")),
        format!("{KEY} - one only")
    );
    assert_eq!(
        bulleted(&format!(
            "{KEY} - \"a\"; <span class=\"orig\">x; \"y\"</span>; <unclosed"
        )),
        format!("{KEY} - \"a\"; <span class=\"orig\">x; \"y\"</span>; <unclosed")
    );
    let notes = format!("<li data-note=\"k\">{KEY} - \"a\"; \"b\"</li>");
    assert!(bulleted_notes(&notes).contains("<span class=\"pass\">\"b\"</span>"));
}
