//! A claim's class held to the tag of the item it names (feature 451 T187; the GM 2026-11-23, request.md "the convergence talk":
//! *"Shouldn't attested versus guess be something that cascades mechanically rather than requiring a review, though?"*). A claim whose
//! pointer names an item, `research/questions/NNNN-<slug>[.drawing].html#<id>`, carries the class its tag says
//! (`l7r_gate_research::record::items`): `GUESS`, `CONVENTION`, `DEVIATION`, or a plain pointer for ATTESTED. A relabel on the page makes
//! this name each claim to flip, and the flip moves no fingerprint (`grammar::Claim::normalized`), so it owes no impl-drift.
//!
//! A MOVED ITEM (451 T200, the gap audit's item 12b; the GM 2026-11-23: "a split is a move", and "as long as the original page being
//! linked to directs a reader to the other page where the full information can be found, then nothing needs to cascade simply because
//! a split occurs"): an item no longer on the page a claim names is FOLLOWED where that page's split pointers reach the one page that
//! now tags it - the claim owes no edit, its class held to that tag, and its round reads the reached page already
//! (`bundle::read_pages`). Where no pointer directs the reader there, an item tagged on exactly one other page is named with the
//! pointer to write, since the cited page no longer leads to it.

use std::collections::HashMap;
use std::path::Path;

use l7r_gate_research::record::items::{items, Item};

use super::scope::all_units;
use super::units::Unit;
use crate::record::repo::Fail;

/// Every tagged item of every research and drawing page of the record (not a notes page), each with its page's repository path.
pub(super) fn every_tag(root: &Path) -> Vec<(String, Item)> {
    let dir = "research/questions";
    let mut names: Vec<String> = std::fs::read_dir(root.join(dir))
        .into_iter()
        .flatten()
        .map_while(std::io::Result::ok)
        .map(|e| e.file_name().to_string_lossy().into_owned())
        .filter(|n| {
            n.ends_with(".drawing.html")
                || (Path::new(n).extension().is_some_and(|e| e == "html")
                    && !n.trim_end_matches(".html").contains('.'))
        })
        .collect();
    names.sort();
    names
        .into_iter()
        .flat_map(|n| {
            let file = format!("{dir}/{n}");
            items(&std::fs::read_to_string(root.join(&file)).unwrap_or_default())
                .into_iter()
                .map(move |i| (file.clone(), i))
        })
        .collect()
}

/// The backing a claim on `file#id` writes for an item labeled `label`.
fn backing(label: &str, file: &str, id: &str) -> String {
    let want = if label == "ATTESTED" {
        String::new()
    } else {
        format!("{label} ")
    };
    format!("{want}{file}#{id}")
}

/// The claim class an item's label asks for.
fn class_for(label: &str) -> &str {
    if label == "ATTESTED" {
        "POINTER"
    } else {
        label
    }
}

/// Each claim on a tagged item whose class its tag does not hold, with the fix.
#[must_use]
pub fn disagreements(root: &Path, units: &[Unit]) -> Vec<String> {
    let mut pages: HashMap<String, Vec<Item>> = HashMap::new();
    let mut elsewhere: Option<Vec<(String, Item)>> = None;
    let mut out = Vec::new();
    for u in units {
        for c in &u.claims {
            for (file, id) in &c.items {
                let tags = pages.entry(file.clone()).or_insert_with(|| {
                    std::fs::read_to_string(root.join(file))
                        .map_or_else(|_| Vec::new(), |t| items(&t))
                });
                let key = u.key(c);
                match tags.iter().find(|i| &i.id == id) {
                    None => {
                        let all = elsewhere.get_or_insert_with(|| every_tag(root));
                        let moved: Vec<&(String, Item)> = all
                            .iter()
                            .filter(|(f, i)| &i.id == id && f != file)
                            .collect();
                        // the pages the cited page's split pointers reach, the claim's own reading (T196's `follow`)
                        let reached = crate::record::triage::change::follow(
                            std::slice::from_ref(file),
                            |page| std::fs::read_to_string(root.join(page)).unwrap_or_default(),
                            str::to_owned,
                        );
                        let followed: Vec<&&(String, Item)> = moved
                            .iter()
                            .filter(|(page, _)| reached.contains(page))
                            .collect();
                        match followed.as_slice() {
                            [(to, it)] => {
                                if class_for(&it.label) != c.backing {
                                    out.push(format!(
                                        "{key}: is {} but {file}#{id}, moved to {to} by its split, is tagged {} there - write its backing `{}` (the flip owes no impl-drift)",
                                        c.backing,
                                        it.label,
                                        backing(&it.label, file, id)
                                    ));
                                }
                                continue;
                            }
                            [] => {}
                            _ => {
                                out.push(format!("{key}: names {file}#{id}, which pages its split reaches each tag - write the one meant"));
                                continue;
                            }
                        }
                        match moved.as_slice() {
                            [(to, it)] => out.push(format!(
                                "{key}: names {file}#{id}, but the item is tagged on {to} now - write its backing `{}`",
                                backing(&it.label, to, id)
                            )),
                            _ => out.push(format!("{key}: names {file}#{id}, which no tag on that page carries - tag the item, or point at the page alone")),
                        }
                    }
                    Some(it) if class_for(&it.label) != c.backing => {
                        out.push(format!(
                            "{key}: is {} but {file}#{id} is tagged {} - write its backing `{}` (the flip owes no impl-drift)",
                            c.backing,
                            it.label,
                            backing(&it.label, file, id)
                        ));
                    }
                    Some(_) => {}
                }
            }
        }
    }
    out
}

/// [`disagreements`] over every unit in scope at `root`.
///
/// # Errors
/// Where a unit's source cannot be read.
pub fn check(root: &Path) -> Result<Vec<String>, Fail> {
    let units: Vec<Unit> = all_units(root, false)?
        .into_iter()
        .map(|(u, _)| u)
        .collect();
    Ok(disagreements(root, &units))
}

#[cfg(test)]
mod tests;
