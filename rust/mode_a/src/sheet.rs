//! A Mode A sheet's reader (feature 449 T170): `l7r/diagram/interactive/sheet.py`'s tree - [`Node`], [`parse`], [`DEFS`] and
//! [`element_kinds`] - ported for the audit's parse ([`crate::parse`]) and its tagged marks ([`crate::tagged`]); the page writing half of
//! `sheet.py` (`pieces`, `census`, `write_sheet_page`) is [`page`] (the plan's step 2, feature 449 T150).
//!
//! The reader TOKENIZES rather than parsing as XML (the Python's own reason: the page is a second serialization of the sheet's bytes), so a
//! node holds slices of the sheet, never copies.
//!
//! OFFSETS ARE THE PYTHON'S (feature 449 T170): a node's `start` is what `m.start()` gave the Python - a count of CODE POINTS, which the
//! audit keys a label's kind by - where the regex crate counts bytes, so every offset this crate hands out goes through [`Offsets`]. On an
//! ASCII sheet (all six pool sheets, observed 2026-11-17, method: a grep for a byte over 0x7f) the two are the same.
//!
//! LOCKSTEP (`ask:449-engine-order` condition 3): `sheet.py`'s reader stays the implementation for the Python that imports it (`pack_audit`)
//! until step 3 (its page half is Rust alone since T150); an edit of its reader makes the same change here in the same commit, and `parse/lockstep.rs`
//! holds the two equal on every pool sheet.
//!
//! Research:
//!     the sheet's reader - NONE: a tokenizer and a tree, deciding nothing about a building

use std::collections::BTreeMap;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_research::pyre::py;
use l7r_gate_research::Error;

/// The element whose content is never ink: patterns, gradients and clip paths are referenced, not drawn.
pub const DEFS: &str = "defs";

static TOKEN: LazyLock<Regex> = LazyLock::new(|| py(r"(?s)<!--.*?-->|<[^>]*>|[^<]+"));
static NAME: LazyLock<Regex> = LazyLock::new(|| py(r"</?\s*([A-Za-z][\w:.-]*)"));
static KIND: LazyLock<Regex> = LazyLock::new(|| py(r#"\sdata-kind="([^"]*)""#));
static PART_OF: LazyLock<Regex> = LazyLock::new(|| py(r#"\sdata-part-of="([^"]*)""#));

/// A byte offset of a sheet as the Python's code-point offset (`m.start()` on a `str`).
pub struct Offsets {
    /// the code point each byte begins, where the sheet is not all ASCII
    table: Option<Vec<usize>>,
}

impl Offsets {
    #[must_use]
    pub fn new(text: &str) -> Self {
        if text.is_ascii() {
            return Self { table: None };
        }
        let mut table = vec![0; text.len() + 1];
        let mut n = 0;
        for (i, c) in text.char_indices() {
            for slot in &mut table[i..i + c.len_utf8()] {
                *slot = n;
            }
            n += 1;
        }
        table[text.len()] = n;
        Self { table: Some(table) }
    }

    /// The code point at byte `at`.
    #[must_use]
    pub fn at(&self, at: usize) -> usize {
        self.table.as_ref().map_or(at, |t| t[at])
    }
}

/// One element of the sheet: its opening tag, its children, its closing tag (empty for a self-closing element); `text` holds a text or
/// whitespace run instead, and then there is no element (`name` empty).
#[derive(Debug, Default)]
pub struct Node<'a> {
    pub open: &'a str,
    pub name: &'a str,
    pub children: Vec<Node<'a>>,
    pub close: &'a str,
    pub text: &'a str,
    /// the code-point offset of the opening tag in the sheet (-1 for a text run, as the Python's default)
    pub start: i64,
}

/// The first group of `re` in `text`, as the Python's `m.group(1) if m else None`.
pub(crate) fn group<'t>(re: &Regex, text: &'t str) -> Option<&'t str> {
    re.captures(text)
        .ok()
        .flatten()
        .and_then(|c| c.get(1))
        .map(|m| m.as_str())
}

impl Node<'_> {
    /// The element's own `data-kind`.
    #[must_use]
    pub fn kind(&self) -> Option<&str> {
        group(&KIND, self.open)
    }

    /// The kind this element is a PART of though drawn outside its group (`data-part-of`, feature 264).
    #[must_use]
    pub fn part_of(&self) -> Option<&str> {
        group(&PART_OF, self.open)
    }

    /// The element's own bytes, reassembled - comments inside it are dropped, nothing else changes.
    #[must_use]
    pub fn source(&self) -> String {
        if self.name.is_empty() {
            return self.text.to_owned();
        }
        let mut out = self.open.to_owned();
        for c in &self.children {
            out += &c.source();
        }
        out + self.close
    }
}

/// The sheet as a tree rooted at its `<svg>` element; whatever precedes the root is not part of the drawing.
///
/// # Errors
/// The Python's `ValueError`: a closing tag that closes nothing open, a sheet that ends inside an element, or no `<svg>` element.
pub fn parse(svg: &str) -> Result<Node<'_>, Error> {
    let offsets = Offsets::new(svg);
    let mut stack: Vec<Node<'_>> = vec![Node {
        name: "#document",
        start: -1,
        ..Node::default()
    }];
    for m in TOKEN.find_iter(svg).flatten() {
        let tok = m.as_str();
        if tok.starts_with("<!") || tok.starts_with("<?") {
            continue;
        }
        if !tok.starts_with('<') {
            let text = Node {
                text: tok,
                start: -1,
                ..Node::default()
            };
            last(&mut stack).children.push(text);
            continue;
        }
        let name = NAME
            .captures(tok)
            .ok()
            .flatten()
            .filter(|c| c.get(0).is_some_and(|m| m.start() == 0))
            .and_then(|c| c.get(1))
            .map_or("", |m| m.as_str());
        if tok.starts_with("</") {
            if stack.len() < 2 || last(&mut stack).name != name {
                return Err(Error::new(
                    "ValueError",
                    format!(
                        "unbalanced </{name}> in the sheet (open: {})",
                        last(&mut stack).name
                    ),
                ));
            }
            let mut done = stack.pop().unwrap_or_default();
            done.close = tok;
            last(&mut stack).children.push(done);
            continue;
        }
        let node = Node {
            open: tok,
            name,
            start: i64::try_from(offsets.at(m.start())).unwrap_or(i64::MAX),
            ..Node::default()
        };
        if tok.ends_with("/>") {
            last(&mut stack).children.push(node);
        } else {
            stack.push(node);
        }
    }
    if stack.len() != 1 {
        return Err(Error::new(
            "ValueError",
            format!("the sheet ends inside <{}>", last(&mut stack).name),
        ));
    }
    let document = stack.pop().unwrap_or_default();
    document
        .children
        .into_iter()
        .find(|c| c.name == "svg")
        .ok_or_else(|| Error::new("ValueError", "no <svg> element in the sheet"))
}

/// The open element a token goes into (the stack is never empty: the document is its floor, popped only past the loop).
fn last<'s, 'a>(stack: &'s mut [Node<'a>]) -> &'s mut Node<'a> {
    let n = stack.len() - 1;
    &mut stack[n]
}

/// The kind of every tagged-or-inheriting element, keyed by the code-point offset of its opening tag - how the audit learns what each
/// label it found belongs to (feature 262, FR-003a). Untagged elements are absent; `<defs>` content is absent.
///
/// # Errors
/// [`parse`]'s refusal.
pub fn element_kinds(svg: &str) -> Result<BTreeMap<i64, String>, Error> {
    fn visit(node: &Node<'_>, inherited: Option<&str>, out: &mut BTreeMap<i64, String>) {
        if node.name.is_empty() || node.name == DEFS {
            return;
        }
        let kind = node.kind().or(inherited);
        if let Some(k) = kind {
            out.insert(node.start, k.to_owned());
        }
        for c in &node.children {
            visit(c, kind, out);
        }
    }
    let mut out = BTreeMap::new();
    visit(&parse(svg)?, None, &mut out);
    Ok(out)
}

pub mod page;

#[cfg(test)]
mod tests;
