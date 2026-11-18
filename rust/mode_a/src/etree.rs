//! `xml.etree.ElementTree.fromstring` as the ported tools need it (feature 449 T174): `make size-table`'s Python read the plan with
//! `ElementTree` (expat), not with the sheet's tokenizer ([`crate::sheet`]), so its port reads the plan as expat does - an entity or a
//! character reference in an attribute decoded, a single-quoted attribute taken, a namespaced attribute kept apart from the plain one
//! (`ElementTree` keys it `{uri}name`), and a sheet that is not well formed refused with `ElementTree`'s `ParseError`.
//!
//! WHY roxmltree AND TWO RULES OVER IT: the crate accepts and refuses as expat does on every probed form but two (observed 2026-11-17,
//! method: 30 forms through `CPython` 3.14.4's `ET.fromstring` and roxmltree 0.20.0, scratchpad t174/xmlprobe), and those two are
//! followed here: expat refuses a prefix undeclared (`xmlns:p=""`, XML 1.0's namespaces forbid it) where roxmltree binds the prefix to
//! nothing; and under an external DTD (`SYSTEM` or `PUBLIC`, not `standalone="yes"`) expat SKIPS an entity it was never told of in an
//! attribute (`ElementTree` reads `x="&e;"` as an empty value) where roxmltree refuses it - in text `ElementTree` refuses it too, so that
//! refusal stands. The refusal's words are the library's (`ask:449-T066-json-message`): its class is `ElementTree`'s.
//!
//! Research:
//!     the plan's XML reading - NONE: a sheet read as an XML tree, deciding nothing about a building

use std::collections::BTreeMap;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_research::pyre::py;
use l7r_gate_research::Error;

/// The class Python named an XML refusal by, as its traceback's last line prints it.
pub const PARSE_ERROR: &str = "xml.etree.ElementTree.ParseError";

static EXTERNAL_DTD: LazyLock<Regex> =
    LazyLock::new(|| py(r"<!DOCTYPE\s+[^\s>\[]+\s+(?:SYSTEM|PUBLIC)\s"));
static STANDALONE: LazyLock<Regex> =
    LazyLock::new(|| py(r#"^﻿?<\?xml[^>]*\sstandalone\s*=\s*["']yes["']"#));

/// One element as `ElementTree` holds it: its tag's local name (`ElementTree`'s `{uri}` stripped, as the tools' `tag()` strips it), its
/// attributes keyed as `ElementTree` keys them, and its child elements in document order (comments, text and processing instructions are
/// not elements).
#[derive(Debug, Default, PartialEq)]
pub struct Element {
    pub tag: String,
    pub attrib: BTreeMap<String, String>,
    pub children: Vec<Element>,
    /// `"".join(el.itertext())`: every text node within it, entities decoded, in document order (feature 449 T175, the audit's ink
    /// bounds read a caption's length by it); a comment is no text, as `ElementTree` drops comments
    pub itertext: String,
}

impl Element {
    /// `el.get(name)`.
    #[must_use]
    pub fn get(&self, name: &str) -> Option<&str> {
        self.attrib.get(name).map(String::as_str)
    }

    /// `el.iter()`: this element and every element below it, in document order.
    #[must_use]
    pub fn elements(&self) -> Vec<&Element> {
        let mut out = vec![self];
        for c in &self.children {
            out.extend(c.elements());
        }
        out
    }
}

fn refused(message: impl Into<String>) -> Error {
    Error::new(PARSE_ERROR, message)
}

/// `ET.fromstring(text)`: the root element.
///
/// # Errors
/// `ElementTree`'s `ParseError` for a sheet expat refuses.
pub fn fromstring(text: &str) -> Result<Element, Error> {
    let skips =
        EXTERNAL_DTD.is_match(text).unwrap_or(false) && !STANDALONE.is_match(text).unwrap_or(false);
    let mut owned = text.to_owned();
    let options = roxmltree::ParsingOptions {
        allow_dtd: true,
        ..roxmltree::ParsingOptions::default()
    };
    loop {
        match roxmltree::Document::parse_with_options(&owned, options) {
            Ok(doc) => return element(doc.root_element()),
            Err(roxmltree::Error::UnknownEntityReference(name, pos)) if skips => {
                let at = byte_at(&owned, pos.row, pos.col);
                if !in_attribute(&owned, at) {
                    return Err(refused(
                        roxmltree::Error::UnknownEntityReference(name, pos).to_string(),
                    ));
                }
                // the reference is dropped as expat skips it, and the sheet read again
                owned.replace_range(at..at + name.len() + 2, "");
            }
            Err(e) => return Err(refused(e.to_string())),
        }
    }
}

/// The element and what is below it, owned; an undeclared prefix (`xmlns:p=""`) refused as expat refuses it.
fn element(node: roxmltree::Node<'_, '_>) -> Result<Element, Error> {
    if node
        .namespaces()
        .any(|ns| ns.name().is_some() && ns.uri().is_empty())
    {
        return Err(refused("must not undeclare prefix"));
    }
    let attrib = node
        .attributes()
        .map(|a| {
            let key = a
                .namespace()
                .map_or_else(|| a.name().to_owned(), |ns| format!("{{{ns}}}{}", a.name()));
            (key, a.value().to_owned())
        })
        .collect();
    let children = node
        .children()
        .filter(roxmltree::Node::is_element)
        .map(element)
        .collect::<Result<_, _>>()?;
    let itertext = node
        .descendants()
        .filter(roxmltree::Node::is_text)
        .filter_map(|t| t.text())
        .collect();
    Ok(Element {
        tag: node.tag_name().name().to_owned(),
        attrib,
        children,
        itertext,
    })
}

/// The byte offset of roxmltree's 1-based row and column (a column counts characters).
fn byte_at(text: &str, row: u32, col: u32) -> usize {
    let mut start = 0;
    for _ in 1..row {
        start += text[start..].find('\n').map_or(0, |i| i + 1);
    }
    let skip = usize::try_from(col.saturating_sub(1)).unwrap_or(usize::MAX);
    text[start..]
        .char_indices()
        .nth(skip)
        .map_or(text.len(), |(i, _)| start + i)
}

/// Whether byte `at` lies inside a quoted attribute value of a start tag: the sheet is read forward from its start - comments,
/// character data, processing instructions and the document type skipped whole - since roxmltree parsed it well formed up to `at`.
fn in_attribute(text: &str, at: usize) -> bool {
    let b = text.as_bytes();
    let mut i = 0;
    let skip_to = |from: usize, end: &str| {
        text[from..]
            .find(end)
            .map_or(b.len(), |j| from + j + end.len())
    };
    while i < at {
        if b[i] != b'<' {
            i += 1;
        } else if text[i..].starts_with("<!--") {
            i = skip_to(i, "-->");
        } else if text[i..].starts_with("<![CDATA[") {
            i = skip_to(i, "]]>");
        } else if text[i..].starts_with("<?") {
            i = skip_to(i, "?>");
        } else if text[i..].starts_with("<!") {
            i = past_markup(b, i);
        } else {
            let (end, inside) = start_tag(b, i, at);
            if inside {
                return true;
            }
            i = end;
        }
    }
    false
}

/// Past a declaration's closing `>`: quoted strings and an internal subset in `[...]` read through.
fn past_markup(b: &[u8], mut i: usize) -> usize {
    let (mut quote, mut depth) = (None, 0_usize);
    while i < b.len() {
        match (quote, b[i]) {
            (Some(q), c) if c == q => quote = None,
            (None, c @ (b'"' | b'\'')) => quote = Some(c),
            (None, b'[') => depth += 1,
            (None, b']') => depth = depth.saturating_sub(1),
            (None, b'>') if depth == 0 => return i + 1,
            _ => {}
        }
        i += 1;
    }
    i
}

/// A tag from `i`: where it ends, and whether `at` lies inside one of its quoted values.
fn start_tag(b: &[u8], mut i: usize, at: usize) -> (usize, bool) {
    let mut quote = None;
    while i < b.len() {
        match (quote, b[i]) {
            (Some(q), c) if c == q => quote = None,
            (Some(_), _) if i == at => return (i, true),
            (None, c @ (b'"' | b'\'')) => quote = Some(c),
            (None, b'>') => return (i + 1, false),
            _ => {}
        }
        i += 1;
    }
    (i, false)
}

#[cfg(test)]
mod tests;
