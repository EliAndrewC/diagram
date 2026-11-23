//! `l7r/diagram/interactive/record/`'s modules, one each under the Python's name: S1's reading half (feature 449 T144), and S5's site, its
//! links, its pages and the money tooltips (`site.py`, `site_links.py`, `site_pages.py`, `money.py`; feature 449 T148).

pub mod absence;
pub mod archive;
pub mod blocked;
pub mod confusables;
pub mod contents;
pub mod fragments;
pub mod items;
pub mod money;
pub mod notes;
pub mod originals;
pub mod passages;
pub mod questions;
pub mod site;
pub mod site_links;
pub mod site_notes;
pub mod site_pages;
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
