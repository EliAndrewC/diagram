//! A KIND'S DRAWN MARKS, AT THE BASE AND NOW (feature 449 T377, the round arbiter's `ask:glyph-occasions-emit-449-T351`). Where a change
//! to the Mode A compound's drawing code cannot tell which kinds it redraws - a kind chosen at run time (`emit.rs`'s `building`), or the
//! document every mark is written into (`compound.rs`'s `sheet`) - `redrawn.rs` owed each compound's whole legend: 53 glyph checks on 449
//! T351's bundle, 48 of them on marks byte-identical or only displaced (observed 2026-11-23, method: the review tree's main and clone svgs
//! per data-kind, data-id stripped, every changed line attributed). So the sheet is read as drawn instead: each kind's marks - every tag
//! and text written under it, caption included - at the base and now, and a kind is owed only where they differ.
//!
//! A token belongs to the kind its own `data-kind` (or `data-part-of`) names, else to the kind of the element it is written inside; a
//! comment draws nothing and whitespace between tags is no mark. `data-id` is stripped: it numbers the marks in document order, so one
//! mark added renumbers every mark after it, which no reader sees. A `<defs>` entry is read by its `id`: a changed one redraws every kind
//! whose marks use it (`url(#id)`, `href="#id"`), and an entry using a changed one is changed with it. What no kind owns - the
//! document's own tags, an entry with no id - redraws what it cannot say, so a difference there is `None`: the caller owes the whole
//! legend, as before.
//!
//! Research: plumbing - NONE: reads a drawn sheet's tags by the kind they are written under, deciding nothing about a map

use std::collections::{BTreeMap, BTreeSet};
use std::fmt::Write as _;

/// A drawn sheet read by kind: each kind's tokens in document order, each `<defs>` entry's by its id ("" where it has none), and the
/// tokens no kind owns.
#[derive(Default, Debug, PartialEq, Eq)]
pub(super) struct Marks {
    kinds: BTreeMap<String, Vec<String>>,
    defs: BTreeMap<String, Vec<String>>,
    loose: Vec<String>,
}

/// The sheet's tokens: each tag, and each run of text trimmed - a comment and a run of whitespace dropped, since neither draws.
fn tokens(svg: &str) -> Vec<&str> {
    let mut out = Vec::new();
    let mut rest = svg;
    while !rest.is_empty() {
        let (token, next) = if rest.starts_with("<!--") {
            ("", rest.find("-->").map_or(rest.len(), |i| i + 3))
        } else if rest.starts_with('<') {
            let end = rest.find('>').map_or(rest.len(), |i| i + 1);
            (&rest[..end], end)
        } else {
            let end = rest.find('<').unwrap_or(rest.len());
            (rest[..end].trim(), end)
        };
        if !token.is_empty() {
            out.push(token);
        }
        rest = &rest[next..];
    }
    out
}

/// Where attribute `name` opens in `tag` (a match preceded by whitespace, so `id` never matches inside `data-id`): the start of its
/// name and of its value.
fn attr_at(tag: &str, name: &str) -> Option<(usize, usize)> {
    let key = format!("{name}=\"");
    tag.match_indices(&key)
        .find(|(i, _)| tag[..*i].ends_with(char::is_whitespace))
        .map(|(i, _)| (i, i + key.len()))
}

/// Attribute `name`'s value in `tag`.
fn attr<'a>(tag: &'a str, name: &str) -> Option<&'a str> {
    let (_, at) = attr_at(tag, name)?;
    tag[at..].find('"').map(|end| &tag[at..at + end])
}

/// `tag` without its `data-id` attributes (and the whitespace before each).
fn without_ids(tag: &str) -> String {
    let mut out = tag.to_owned();
    while let Some((name, at)) = attr_at(&out, "data-id") {
        let lead = out[..name].trim_end().len();
        let end = out[at..].find('"').map_or(out.len(), |e| at + e + 1);
        out.replace_range(lead..end, "");
    }
    out
}

/// An open element: the kind its tokens belong to, the `<defs>` entry it is in, and whether it is inside `<defs>` at all.
#[derive(Clone, Default)]
struct Open {
    kind: Option<String>,
    def: Option<String>,
    defs: bool,
}

/// The sheet `svg` read by kind.
pub(super) fn read(svg: &str) -> Marks {
    let mut m = Marks::default();
    let mut stack: Vec<Open> = Vec::new();
    for raw in tokens(svg) {
        let token = without_ids(raw);
        let tag = token.starts_with('<');
        let closing = token.starts_with("</");
        let opens = tag
            && !closing
            && !token.ends_with("/>")
            && !token.starts_with("<?")
            && !token.starts_with("<!");
        let at = if closing {
            stack.pop().unwrap_or_default()
        } else {
            let up = stack.last().cloned().unwrap_or_default();
            if up.defs {
                // a `<defs>` entry is its top-level element, named by its id
                let def = up
                    .def
                    .or_else(|| Some(attr(&token, "id").unwrap_or_default().to_owned()));
                Open {
                    kind: None,
                    def,
                    defs: true,
                }
            } else if token.starts_with("<defs") {
                Open {
                    kind: None,
                    def: None,
                    defs: true,
                }
            } else {
                let own = attr(&token, "data-kind").or_else(|| attr(&token, "data-part-of"));
                Open {
                    kind: own.map(str::to_owned).or(up.kind),
                    def: None,
                    defs: false,
                }
            }
        };
        match (&at.def, &at.kind) {
            (Some(id), _) => m.defs.entry(id.clone()).or_default().push(token),
            (None, Some(kind)) => m.kinds.entry(kind.clone()).or_default().push(token),
            (None, None) => m.loose.push(token),
        }
        if opens {
            stack.push(at);
        }
    }
    m
}

/// Whether `token` uses the `<defs>` entry `id`.
fn uses(token: &str, id: &str) -> bool {
    token.contains(&format!("url(#{id})")) || token.contains(&format!("href=\"#{id}\""))
}

/// Whether any of these tokens uses one of `ids`.
fn uses_any<'a>(mut tokens: impl Iterator<Item = &'a String>, ids: &BTreeSet<String>) -> bool {
    tokens.any(|t| ids.iter().any(|id| uses(t, id)))
}

/// The `<defs>` entries that differ between the two sheets, with every entry using one that does; `None` where an entry with no id
/// differs, which no kind's marks can be said to use.
fn changed_defs(was: &Marks, now: &Marks) -> Option<BTreeSet<String>> {
    let ids: BTreeSet<&String> = was.defs.keys().chain(now.defs.keys()).collect();
    let mut changed: BTreeSet<String> = ids
        .iter()
        .filter(|id| was.defs.get(**id) != now.defs.get(**id))
        .map(|id| (*id).clone())
        .collect();
    if changed.contains("") {
        return None;
    }
    loop {
        let more: Vec<String> = ids
            .iter()
            .filter(|id| !changed.contains(**id))
            .filter(|id| {
                let both = was.defs.get(**id).into_iter().chain(now.defs.get(**id));
                uses_any(both.flatten(), &changed)
            })
            .map(|id| (*id).clone())
            .collect();
        if more.is_empty() {
            return Some(changed);
        }
        changed.extend(more);
    }
}

/// The kinds whose drawn marks differ between the base's sheet `was` and `now` - their own tokens, or a `<defs>` entry they use - or
/// `None` where a token no kind owns differs, so the kinds it redraws cannot be told.
pub(super) fn differing(was: &Marks, now: &Marks) -> Option<BTreeSet<String>> {
    if was.loose != now.loose {
        return None;
    }
    let changed = changed_defs(was, now)?;
    let kinds: BTreeSet<&String> = was.kinds.keys().chain(now.kinds.keys()).collect();
    Some(
        kinds
            .into_iter()
            .filter(|k| {
                let (a, b) = (was.kinds.get(*k), now.kinds.get(*k));
                a != b || uses_any(a.into_iter().chain(b).flatten(), &changed)
            })
            .cloned()
            .collect(),
    )
}

/// What `kind`'s marks are, as a discharge binds them (`discharged.rs`): its tokens and every `<defs>` entry they use, hashed; `None`
/// where the sheet draws no mark of it.
pub(super) fn digest(m: &Marks, kind: &str) -> Option<String> {
    let own = m.kinds.get(kind)?;
    let mut used: BTreeSet<String> = BTreeSet::new();
    let mut reach: Vec<&String> = own.iter().collect();
    loop {
        let more: Vec<&String> = m
            .defs
            .keys()
            .filter(|id| !used.contains(*id) && reach.iter().any(|t| uses(t, id)))
            .collect();
        if more.is_empty() {
            break;
        }
        for id in more {
            used.insert(id.clone());
            reach.extend(&m.defs[id]);
        }
    }
    let mut data = String::new();
    for t in own {
        data.push_str(t);
        data.push('\n');
    }
    for id in &used {
        let _ = writeln!(data, "#{id}");
        for t in &m.defs[id] {
            data.push_str(t);
            data.push('\n');
        }
    }
    Some(l7r_shared::sha256::hex(data.as_bytes())[..16].to_owned())
}

#[cfg(test)]
mod tests;
