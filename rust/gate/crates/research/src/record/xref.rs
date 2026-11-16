//! Cross-links between a research page and the drawing page about it (`record/xref.py`, features 292, 303; ported by feature 449 T144). A
//! link is never typed: the pairing is the STEM, or a lone drawing page's `about:`, and the build writes a small link under both headings,
//! two-way by construction (the GM, 2026-09-29: *"that linking should be automated"*).

use crate::record::questions::{Page, Record};
use crate::{re, Error, Result};

pub const TO_RENDERING: &str = "How it's drawn";
pub const TO_RESEARCH: &str = "The history behind it";

/// A drawing page and the research page it is about, by file name.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Pair {
    pub drawing: String,
    pub research: String,
}

/// Every drawing page with the research page it is about, in number order.
#[must_use]
pub fn pairs(record: &Record) -> Vec<Pair> {
    let mut out = Vec::new();
    for q in &record.questions {
        let Some(drawing) = &q.drawing else { continue };
        let about = if q.research.is_some() {
            Some(q)
        } else {
            q.about.as_deref().and_then(|a| record.by_stem(a))
        };
        if let Some(research) = about.and_then(|a| a.research.as_ref()) {
            out.push(Pair {
                drawing: drawing.file.clone(),
                research: research.file.clone(),
            });
        }
    }
    out
}

/// The page with a `<span class="xref">` written at the start of its heading, linking each page it is paired with.
///
/// # Errors
/// A page whose heading is not in its text (the Python's assertion; `questions.load` read every heading from this text).
pub fn link(page_html: &str, page: &Page, all_pairs: &[Pair]) -> Result<String> {
    let mut anchors: Vec<String> = all_pairs
        .iter()
        .filter(|p| p.research == page.file)
        .map(|p| format!(r#"<a href="{}">{TO_RENDERING}</a>"#, p.drawing))
        .collect();
    anchors.extend(
        all_pairs
            .iter()
            .filter(|p| p.drawing == page.file)
            .map(|p| format!(r#"<a href="{}">{TO_RESEARCH}</a>"#, p.research)),
    );
    if anchors.is_empty() {
        return Ok(page_html.to_owned());
    }
    let heading = re(&format!(
        r#"<h[23] id="{}">"#,
        fancy_regex::escape(&page.heading_id)
    ));
    let m = heading
        .find(page_html)
        .ok()
        .flatten()
        .ok_or_else(|| Error::new("AssertionError", page.file.clone()))?;
    Ok(format!(
        r#"{}<span class="xref">{}</span>{}"#,
        &page_html[..m.end()],
        anchors.join(" - "),
        &page_html[m.end()..]
    ))
}

#[cfg(test)]
mod tests;
