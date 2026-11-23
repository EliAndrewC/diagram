//! A pop-up's Guesses as its reader meets them, references filled (feature 451 T192, the GM 2026-11-23: "Yes please tag the rest of
//! the record before resuming our port"). A Guesses bullet may be a reference, `- {NNNN#<id>}`, filled at build from the item's tag on
//! question NNNN's page (`l7r_gate_registry::items`). What a pop-up's checks judged is the bullet's TEXT, so what owes them is read
//! with each reference filled from its tag's `data-guess` whatever its label (a relabel cascades by regeneration and owes nothing, T187):
//! a bullet written out turned into a reference to a tag carrying its words owes no check; a tag's `data-guess` reworded owes each
//! pop-up that references it, as the bullet's own rewording would. The page's tags themselves are out of its fingerprint
//! (`items::strip`), so tagging a page owes no pop-up.

use std::collections::HashMap;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_registry::items::Pages;
use l7r_gate_research::record::items::{items, Item};

use super::super::units::re;

static REFERENCE: LazyLock<Regex> =
    LazyLock::new(|| re(r"^- ((?:\[[a-z_]+=[^\]]*\]\s*)*)\{(\d{4})#([a-z0-9-]+)\}\s*$"));

/// Each `(question, id)` a Guesses text references, in order, each once.
#[must_use]
pub fn references(guesses: &str) -> Vec<(String, String)> {
    let mut out: Vec<(String, String)> = guesses
        .lines()
        .filter_map(|l| REFERENCE.captures(l).ok().flatten())
        .map(|c| (c[2].to_owned(), c[3].to_owned()))
        .collect();
    out.sort();
    out.dedup();
    out
}

/// Question `number`'s research and drawing pages under `root`, as tree paths (the pages a reference's tag may sit on); `""` every
/// question's.
#[must_use]
pub fn question_files(root: &Path, number: &str) -> Vec<String> {
    let mut out: Vec<String> = std::fs::read_dir(root.join("research/questions"))
        .into_iter()
        .flatten()
        .map_while(std::io::Result::ok)
        .map(|e| e.file_name().to_string_lossy().into_owned())
        .filter(|n| {
            n.starts_with(&format!("{number}-"))
                || (number.is_empty() && n.as_bytes().get(4) == Some(&b'-'))
        })
        .filter(|n| n.ends_with(".drawing.html") || !n.trim_end_matches(".html").contains('.'))
        .map(|n| format!("research/questions/{n}"))
        .collect();
    out.sort();
    out
}

/// The item each reference names, by `(question, id)`.
pub type Tagged = HashMap<(String, String), Item>;

/// Each reference's item read from the tree now, as the registry fills it at build (`Pages::locate`, 451 T200: its own question's
/// pages first, else the one other question tagging the id), so what owes a pop-up is what its reader is shown.
#[must_use]
pub fn tagged_now(root: &Path, refs: &[(String, String)]) -> Tagged {
    let mut pages = Pages::default();
    refs.iter()
        .filter_map(|(n, id)| {
            pages
                .locate(root, n, id)
                .ok()
                .map(|it| ((n.clone(), id.clone()), it))
        })
        .collect()
}

/// Each reference's item at a revision, from `texts` (the named tree paths' texts there): its own question's pages first, else the
/// pages of the one question that tags the id now, read at that revision.
pub fn tagged_in(
    root: &Path,
    refs: &[(String, String)],
    texts: &mut dyn FnMut(&[String]) -> Vec<String>,
) -> Tagged {
    let mut out = Tagged::new();
    for (n, id) in refs {
        let home: Vec<Item> = texts(&question_files(root, n))
            .iter()
            .flat_map(|t| items(t))
            .collect();
        let found = home.into_iter().find(|i| &i.id == id).or_else(|| {
            let now = tagged_now(root, &[(n.clone(), id.clone())]);
            let it = now.get(&(n.clone(), id.clone()))?;
            let other: Vec<String> = question_files(root, "")
                .into_iter()
                .filter(|f| {
                    std::fs::read_to_string(root.join(f))
                        .is_ok_and(|t| items(&t).iter().any(|i| i.id == it.id))
                })
                .collect();
            texts(&other)
                .iter()
                .flat_map(|t| items(t))
                .find(|i| &i.id == id)
        });
        if let Some(it) = found {
            out.insert((n.clone(), id.clone()), it);
        }
    }
    out
}

/// The Guesses text with each reference whose item is found replaced by `- <condition><its data-guess>`, whatever its label; a
/// reference naming no item is left as written.
#[must_use]
pub fn resolved(guesses: &str, tagged: &Tagged) -> String {
    guesses
        .lines()
        .map(|l| {
            let Ok(Some(c)) = REFERENCE.captures(l) else {
                return l.to_owned();
            };
            tagged
                .get(&(c[2].to_owned(), c[3].to_owned()))
                .map_or_else(|| l.to_owned(), |i| format!("- {}{}", &c[1], i.guess))
        })
        .collect::<Vec<_>>()
        .join("\n")
}

#[cfg(test)]
mod tests;
