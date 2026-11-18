//! Its unit tests (feature 449 T174).
//!
//! Research:
//!     its tests - NONE: tests, deciding nothing about a building

use super::{byte_at, fromstring, in_attribute, past_markup, start_tag, Element};

/// The refusal's class, as the traceback's last line names it.
fn refusal(text: &str) -> &'static str {
    fromstring(text).unwrap_err().kind
}

fn attrs(el: &Element) -> Vec<(String, String)> {
    el.attrib
        .iter()
        .map(|(k, v)| (k.clone(), v.clone()))
        .collect()
}

#[test]
fn a_sheet_reads_as_element_tree_reads_it() {
    // each value `CPython` 3.14.4's `ET.fromstring` gave on the same text
    let root = fromstring(r#"<svg xmlns="http://www.w3.org/2000/svg" xmlns:xl="http://x"><rect xl:width="5" width='3&amp;&#65;'/><!--c--><g><circle/></g></svg>"#).unwrap();
    let tags: Vec<&str> = root.elements().iter().map(|e| e.tag.as_str()).collect();
    assert_eq!(tags, ["svg", "rect", "g", "circle"]);
    let rect = &root.children[0];
    assert_eq!(
        attrs(rect),
        [
            ("width".to_owned(), "3&A".to_owned()),
            ("{http://x}width".to_owned(), "5".to_owned())
        ]
    );
    assert_eq!((rect.get("width"), rect.get("x")), (Some("3&A"), None));
    assert_eq!(fromstring("\u{feff}<svg/>").unwrap().tag, "svg");
}

#[test]
fn under_an_external_dtd_an_unknown_entity_in_an_attribute_is_skipped_as_expat_skips_it() {
    let root = fromstring("<!DOCTYPE svg SYSTEM \"x.dtd\" [<!ENTITY w \"1\">]>\n<?pi x?><!-- <a x=\" --><svg><![CDATA[ < ]]>\n<rect x='a&e;5' y=\"&w;\" z=\"&q;&r;\"/></svg>").unwrap();
    assert_eq!(
        attrs(&root.children[0]),
        [
            ("x".to_owned(), "a5".to_owned()),
            ("y".to_owned(), "1".to_owned()),
            ("z".to_owned(), String::new())
        ]
    );
    // in text it is refused; so it is with no external DTD, or one the sheet declares standalone
    let p = super::PARSE_ERROR;
    assert_eq!(
        refusal("<!DOCTYPE svg PUBLIC \"p\" \"x.dtd\"><svg>\n<!-- <a x=\" -->&e;</svg>"),
        p
    );
    assert_eq!(refusal("<?xml version=\"1.0\" standalone=\"yes\"?><!DOCTYPE svg SYSTEM \"x.dtd\"><svg x=\"&e;\"/>"), p);
    assert_eq!(refusal("<svg x=\"&e;\"/>"), p);
}

#[test]
fn what_expat_refuses_is_refused() {
    let p = super::PARSE_ERROR;
    for text in [
        "",
        "<svg><a:rect/></svg>",
        "<svg/><svg/>",
        "<svg>]]></svg>",
        "<svg a=\"1\" a=\"2\"/>",
    ] {
        assert_eq!(refusal(text), p, "{text}");
    }
    let e = fromstring("<svg xmlns:a=\"u\"><g xmlns:a=\"\"/></svg>").unwrap_err();
    assert_eq!(
        (e.kind, e.message.as_str()),
        (p, "must not undeclare prefix")
    );
}

#[test]
fn the_reading_s_helpers_find_their_place() {
    assert_eq!(byte_at("ab\n\u{6c34}cd", 2, 2), 6);
    assert_eq!(byte_at("ab", 1, 9), 2);
    // a reference's place: in a value, or not
    let text = "<!DOCTYPE s [ <!ENTITY a '>'> ]><s t='&x;'>&y;</s>";
    assert!(in_attribute(text, text.find("&x").unwrap()));
    assert!(!in_attribute(text, text.find("&y").unwrap()));
    // unclosed forms run to the end
    assert_eq!(past_markup(b"<!x 'y", 0), 6);
    assert_eq!(start_tag(b"<a b='c", 0, 99), (7, false));
    assert!(!in_attribute("<!-- x", 5));
}

#[test]
fn an_element_keeps_its_namespace_and_its_own_text_as_element_tree_does() {
    // `el.text` is the text before the first child, a comment's two sides joined; `{uri}name` keys a tag by its namespace (feature 449
    // T151, a caption's line and its `<tspan>`s)
    let el = fromstring(r#"<svg xmlns="http://www.w3.org/2000/svg"><text>a<!-- c -->b<tspan>c</tspan>d</text><p:x xmlns:p="urn:p"/></svg>"#).unwrap();
    let text = &el.children[0];
    assert_eq!(
        (
            text.text.as_str(),
            text.ns.as_str(),
            text.children[0].text.as_str()
        ),
        ("ab", "http://www.w3.org/2000/svg", "c")
    );
    assert_eq!(
        (el.children[1].ns.as_str(), el.children[1].text.as_str()),
        ("urn:p", "")
    );
}
