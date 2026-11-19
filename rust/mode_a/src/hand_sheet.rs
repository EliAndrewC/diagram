//! What the size table reads of `l7r/diagram/labels/hand_sheet.py` (feature 449 T174): [`start_tags`], one function; the rest of that
//! module (the hand sheet's caption placer) is the plan's step 3 (S8) and stays Python.
//!
//! LOCKSTEP (`ask:449-engine-order` condition 3): `hand_sheet.py` stays for its Python importers (the pool generators' pages, `make
//! sheet-render`) until step 3; an edit of its `start_tags` makes the same change here in the same commit, and `parse/lockstep.rs` holds
//! the two equal on every pool sheet.
//!
//! Research:
//!     the hand sheet's start tags - NONE: where each element's start tag lies in a sheet's text, deciding nothing about a building

use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_research::pyre::py;

use crate::sheet::Offsets;

/// FEATURE 449 T182: the sheet reader's own tokens ([`crate::sheet::TOKENS`]), so a CDATA section's tag-like run is no element, an element
/// named outside [A-Za-z] is one, and a `>` in a quoted attribute value does not end its tag - each had shifted the index every later
/// element is paired by.
static TAG: LazyLock<Regex> = LazyLock::new(|| py(crate::sheet::TOKENS));

/// Where each element's start tag lies in the source, in document order - the order `ET` iterates in, so a Shape's `at` is its index
/// here. Comments, declarations and end tags are not elements. Each span is the Python's `m.span()`, in code points.
#[must_use]
pub fn start_tags(src: &str) -> Vec<(usize, usize)> {
    let offsets = Offsets::new(src);
    TAG.find_iter(src)
        .map_while(Result::ok)
        .filter(|m| {
            m.as_str().starts_with('<')
                && !matches!(src.as_bytes()[m.start() + 1], b'!' | b'?' | b'/')
        })
        .map(|m| (offsets.at(m.start()), offsets.at(m.end())))
        .collect()
}

#[cfg(test)]
mod tests {
    use super::start_tags;

    #[test]
    fn a_start_tag_is_an_element_s_and_its_span_is_in_code_points() {
        // the spans are `CPython`'s, in code points; a tag-like run in a CDATA section is no element (T182: it counted, after a `>`)
        let src = "<?xml version=\"1.0\"?><!-- <a> --><svg>\u{6c34}<rect x=\"1\"/></svg><![CDATA[ a > <b> ]]>";
        assert_eq!(start_tags(src), [(33, 38), (39, 52)]);
    }
}
