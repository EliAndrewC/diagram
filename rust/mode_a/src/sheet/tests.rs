//! The sheet's reader (feature 449 T170): the tree, its offsets, its kinds and its refusals.
//!
//! Research:
//!     the sheet reader's tests - NONE: fixtures and assertions, deciding nothing about a building

use super::{element_kinds, parse, Offsets};
use crate::py::uncaught;

#[test]
fn the_tree_keeps_the_sheet_s_bytes_less_its_comments() {
    let svg = "<?xml?><!-- a note --><svg a=\"1\"><g data-kind=\"hall\" data-part-of=\"court\"><!-- x --><rect/>t</g></svg>";
    let root = parse(svg).unwrap();
    assert_eq!(
        root.source(),
        "<svg a=\"1\"><g data-kind=\"hall\" data-part-of=\"court\"><rect/>t</g></svg>"
    );
    let g = &root.children[0];
    assert_eq!(
        (g.kind(), g.part_of(), g.start),
        (Some("hall"), Some("court"), 33)
    );
    assert_eq!((g.children[1].text, g.children[1].start), ("t", -1));
}

#[test]
fn an_offset_counts_code_points_as_the_python_s_did() {
    let svg = "<svg><text>\u{6c34}</text><g data-kind=\"k\"/></svg>";
    assert_eq!(
        element_kinds(svg).unwrap().into_iter().collect::<Vec<_>>(),
        [(19, "k".to_owned())]
    );
    let o = Offsets::new("a\u{6c34}b");
    assert_eq!((o.at(0), o.at(1), o.at(4), o.at(5)), (0, 1, 2, 3));
    assert_eq!(Offsets::new("ab").at(2), 2);
}

#[test]
fn a_sheet_that_does_not_balance_is_refused() {
    let refused = |svg: &str| uncaught(&parse(svg).unwrap_err());
    assert_eq!(
        refused("<svg></g></svg>"),
        "ValueError: unbalanced </g> in the sheet (open: svg)\n"
    );
    assert_eq!(
        refused("</svg>"),
        "ValueError: unbalanced </svg> in the sheet (open: #document)\n"
    );
    assert_eq!(
        refused("<svg><g>"),
        "ValueError: the sheet ends inside <g>\n"
    );
    assert_eq!(
        refused("<rect/>"),
        "ValueError: no <svg> element in the sheet\n"
    );
    assert!(element_kinds("<g>").is_err());
    // the definitions are no ink, and an inherited kind keys every element under it
    let kinds = element_kinds(
        "<svg data-kind=\"-\"><defs data-kind=\"d\"><rect/></defs><g><rect/></g></svg>",
    )
    .unwrap();
    assert_eq!(kinds.values().collect::<Vec<_>>(), ["-", "-", "-"]);
}

/// T182: the reader reads what `ElementTree` reads - a `>` in a quoted value, a CDATA section's tag-like run (kept as the sheet's text),
/// a declaration's internal subset, an element named outside [A-Za-z], a `data-kind` in single quotes - each of which it refused or
/// misread.
#[test]
fn the_reader_reads_every_sheet_the_xml_reader_accepts() {
    let svg = "<!DOCTYPE svg [<!ENTITY e \"x\">]><svg><text data-kind='note' title=\"a>b\"><![CDATA[ a > <b> </c> ]]></text>\
               <_x data-part-of = \"court\"/><g data-kind=\"hall\"><rect/></g></svg>";
    let root = parse(svg).unwrap();
    let text = &root.children[0];
    assert_eq!((text.name, text.kind()), ("text", Some("note")));
    assert_eq!(text.children[0].text, "<![CDATA[ a > <b> </c> ]]>");
    assert_eq!(
        (root.children[1].name, root.children[1].part_of()),
        ("_x", Some("court"))
    );
    assert_eq!(
        element_kinds(svg)
            .unwrap()
            .into_values()
            .collect::<Vec<_>>(),
        ["note", "hall", "hall"]
    );
    assert_eq!(
        crate::hand_sheet::start_tags(svg)
            .into_iter()
            .map(|(a, _)| a)
            .collect::<Vec<_>>(),
        [32, 37, 105, 133, 153]
    );
}
