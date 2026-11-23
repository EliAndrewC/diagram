//! An item's label as data (feature 451 T187; the GM 2026-11-23, request.md "the convergence talk": *"Shouldn't attested versus guess be
//! something that cascades mechanically rather than requiring a review, though?"*): a finding of a page carries a TAG, an empty token
//! inside its block, naming the item and its label once:
//!
//! `<span class="item" data-item="<id>" data-label="<ATTESTED|GUESS|CONVENTION|DEVIATION>" data-guess="<the Guesses bullet>"></span>`
//!
//! What reads the label reads it from here: a pop-up's Guesses bullet `{NNNN#<id>}` is filled from the tag at build
//! (`l7r_gate_registry::items`), and an engine claim naming `research/questions/NNNN-<slug>.drawing.html#<id>` is held to it
//! (`l7r_gate_claims`, `item_labels`). So a relabel is one edit on the page, and what reads it regenerates.
//!
//! The token is EMPTY and sits INSIDE the block, never as an attribute of its `<li>`: `<li>\s*<strong>` is matched bare by the style
//! prepass (`style.rs`) and the triage's findings (`owed::record::triage::change`), which an attribute would silently stop. Empty, it adds
//! no word to the block (`pages::words` drops markup), so tagging a page changes nothing a page check reads. `data-guess` is the bullet a
//! pop-up shows while the item is a GUESS, written once on the page; the block's own prose must carry the label word the tag names
//! ([`faults`]), so the page never says one label and its tag another.

use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_shared::checks::pages::words;
use l7r_shared::html_text::unescape;

use crate::re;

/// The labels a tag takes: the claim grammar's classes for a decision (`GUESS`, `CONVENTION`, `DEVIATION`) and `ATTESTED` for a pointer
/// claim's, historically accurate. An untagged item is UNKNOWN, never attested.
pub const LABELS: [&str; 4] = ["ATTESTED", "GUESS", "CONVENTION", "DEVIATION"];

static TAG: LazyLock<Regex> =
    LazyLock::new(|| re(r#"<span class="item"((?:\s+data-[a-z]+="[^"]*")*)\s*></span>"#));
static ATTR: LazyLock<Regex> = LazyLock::new(|| re(r#"data-([a-z]+)="([^"]*)""#));
static OPEN: LazyLock<Regex> = LazyLock::new(|| re(r"<(?:li|p)\b[^>]*>"));
static CLOSE: LazyLock<Regex> = LazyLock::new(|| re(r"</(?:li|p)>"));
static ID: LazyLock<Regex> = LazyLock::new(|| re(r"^[a-z0-9][a-z0-9-]*\z"));
static CONVENTION_WORD: LazyLock<Regex> = LazyLock::new(|| re(r"(?i)\bconvention"));
static DEVIATION_WORD: LazyLock<Regex> = LazyLock::new(|| re(r"(?i)\bdeviation"));

/// One tagged item: its id, label and Guesses bullet, and the words of the block it sits in.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Item {
    pub id: String,
    pub label: String,
    pub guess: String,
    pub block: String,
}

fn attr(attrs: &str, name: &str) -> String {
    ATTR.captures_iter(attrs)
        .map_while(Result::ok)
        .find(|c| &c[1] == name)
        .map_or_else(String::new, |c| unescape(&c[2]))
}

/// The words of the `<li>` or `<p>` that holds the byte at `at`.
fn block_at(html: &str, at: usize) -> String {
    let start = OPEN
        .find_iter(&html[..at])
        .map_while(Result::ok)
        .last()
        .map_or(0, |m| m.start());
    let end = CLOSE
        .find_from_pos(html, at)
        .ok()
        .flatten()
        .map_or(html.len(), |m| m.end());
    words(&html[start..end])
}

/// Every tagged item of a page, in page order.
#[must_use]
pub fn items(html: &str) -> Vec<Item> {
    TAG.captures_iter(html)
        .map_while(Result::ok)
        .map(|c| {
            let attrs = c.get(1).map_or("", |m| m.as_str());
            Item {
                id: attr(attrs, "item"),
                label: attr(attrs, "label"),
                guess: attr(attrs, "guess"),
                block: block_at(html, c.get(0).map_or(0, |m| m.start())),
            }
        })
        .collect()
}

/// Whether the block's own words carry the label its tag names.
fn says(item: &Item) -> bool {
    let guess = item.block.contains("GUESS");
    let found = |w: &Regex| w.is_match(&item.block).unwrap_or(false);
    match item.label.as_str() {
        "GUESS" => guess,
        "CONVENTION" => !guess && found(&CONVENTION_WORD),
        "DEVIATION" => !guess && found(&DEVIATION_WORD),
        _ => !guess,
    }
}

/// What is wrong with a page's tags, each fault with its fix; `name` is the page's file name.
#[must_use]
pub fn faults(name: &str, html: &str) -> Vec<String> {
    let mut out = Vec::new();
    let mut seen = std::collections::HashSet::new();
    for it in items(html) {
        let who = format!("{name}: item `{}`", it.id);
        if !ID.is_match(&it.id).unwrap_or(false) {
            out.push(format!(
                "{who} - data-item must be a lowercase slug (`a-z`, `0-9`, `-`)"
            ));
        } else if !seen.insert(it.id.clone()) {
            out.push(format!(
                "{who} - tagged twice: an item id is unique on its page"
            ));
        }
        if !LABELS.contains(&it.label.as_str()) {
            out.push(format!(
                "{who} - data-label `{}` is not one of {}",
                it.label,
                LABELS.join(", ")
            ));
            continue;
        }
        if it.label == "GUESS" && it.guess.trim().is_empty() {
            out.push(format!("{who} - a GUESS tag carries its Guesses bullet: add data-guess=\"<what is guessed>: <why no page says>\""));
        }
        if !says(&it) {
            out.push(format!(
                "{who} - its tag says {} but its block's words do not: write the label in the block (GUESS as `a GUESS`, a convention or a deviation by name, an ATTESTED block with no `GUESS`), or retag it - the two are one label"
            , it.label));
        }
    }
    out
}

#[cfg(test)]
mod tests;
