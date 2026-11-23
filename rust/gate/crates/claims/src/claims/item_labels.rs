//! A claim's class held to the tag of the item it names (feature 451 T187; the GM 2026-11-23, request.md "the convergence talk":
//! *"Shouldn't attested versus guess be something that cascades mechanically rather than requiring a review, though?"*). A claim whose
//! pointer names an item, `research/questions/NNNN-<slug>[.drawing].html#<id>`, carries the class its tag says
//! (`l7r_gate_research::record::items`): `GUESS`, `CONVENTION`, `DEVIATION`, or a plain pointer for ATTESTED. A relabel on the page makes
//! this name each claim to flip, and the flip moves no fingerprint (`grammar::Claim::normalized`), so it owes no impl-drift.

use std::collections::HashMap;
use std::path::Path;

use l7r_gate_research::record::items::{items, Item};

use super::scope::all_units;
use super::units::Unit;
use crate::record::repo::Fail;

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
                    None => out.push(format!("{key}: names {file}#{id}, which no tag on that page carries - tag the item, or point at the page alone")),
                    Some(it) if class_for(&it.label) != c.backing => {
                        let want = if it.label == "ATTESTED" { String::new() } else { format!("{} ", it.label) };
                        out.push(format!(
                            "{key}: is {} but {file}#{id} is tagged {} - write its backing `{want}{file}#{id}` (the flip owes no impl-drift)",
                            c.backing, it.label
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
