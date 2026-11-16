//! `l7r/diagram/interactive/record/`'s S1 modules (feature 449 T144), one module each under the Python's name. The site, its links, its
//! pages and the money tooltips (`site.py`, `site_links.py`, `site_pages.py`, `money.py`) are S5's.

pub mod absence;
pub mod archive;
pub mod blocked;
pub mod confusables;
pub mod contents;
pub mod fragments;
pub mod notes;
pub mod originals;
pub mod passages;
pub mod questions;
pub mod site_notes;
pub mod source_tags;
pub mod split;
pub mod store;
pub mod xref;

/// `assemble.py`: the page as a reader opens it - front, the sections in order with their entries, tail - concatenated byte for byte,
/// nothing reformatted (feature 258), so the record's bytes stay what a session wrote.
#[must_use]
pub fn assemble(page: &split::Page) -> String {
    let mut out = page.front.clone();
    for section in &page.sections {
        out.push_str(&section.text);
        for entry in &section.entries {
            out.push_str(&entry.text);
        }
    }
    out.push_str(&page.tail);
    out
}
