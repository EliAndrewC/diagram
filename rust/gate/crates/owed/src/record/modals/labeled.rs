//! A drawing page's NEW labeled item owes the pop-ups that read the page a look at their Guesses tab (feature 451 T226). A pop-up's
//! `Drawing:` page moving owes it `modal-depiction` alone (`owed_row`), whose contract is the Depiction tab; the figure the map draws as a
//! guess is a Guesses bullet (dev/modals.md M8, M11), which `modal-form` judges. So page session P7's two new GUESS items on 0097's
//! drawing page (`barracks-length-ceiling`, `row-of-48-ft`) and P15's new UNRESEARCHED `toe-shoulder-past-corner` on 0057's reached no
//! check of `sheet/barracks`' or `hamlet/marsh`'s Guesses tab. An item whose tag is new on the page, or whose label changed, to one of
//! [`LABELS`], in a block whose words did not stand on the page before (a tag added to standing words is T192's tagging, which owes
//! nothing; a relabel rewrites its block, whose prose carries the label word, `items::faults`) now owes `modal-form` of each About-form pop-up whose `Drawing:` names the page, unless its Guesses tab references the item
//! (`{NNNN#<id>}`: the registry fills that bullet from the tag, so it cascades by regeneration, T187). The occasion opens "a page its ",
//! so the unit goes to `make modal-triage` first, as every page-moved unit does (feature 375 FR-001), and the triage reads the pop-up's
//! drawing pages for it.

use std::collections::{BTreeMap, HashMap};
use std::path::Path;

use l7r_gate_research::record::items::{blocks, items, Item};

use super::super::delta::Delta;
use super::super::repo::read_universal;
use super::super::units::digest;
use super::{followed, refs, Modal};

/// The labels a new or relabeled item owes on: a guess, an unresearched figure, a deviation and a convention (the five labels but
/// ATTESTED, 451 T236). Only GUESS and UNRESEARCHED are Guesses bullets (M8, M11); a DEVIATION is told in About and a CONVENTION on the
/// Depiction tab (M13), which `modal-form` judges too (M13 is its rule), so all four owe its look.
pub const LABELS: [&str; 4] = ["GUESS", "UNRESEARCHED", "DEVIATION", "CONVENTION"];

/// Each drawing page's items whose tag is new on it since the base, or whose label changed, to one of [`LABELS`].
pub type Gained = BTreeMap<String, Vec<Item>>;

/// The items each of `pages` gained against `base` (read through `delta`); none where there is no base.
///
/// # Errors
///
/// Where a page cannot be read: the error says which and why.
pub fn gained(delta: &mut Delta, base: &str, pages: &[String]) -> Result<Gained, String> {
    let mut out = Gained::new();
    if base.is_empty() || pages.is_empty() {
        return Ok(out);
    }
    let root = delta.root().to_path_buf();
    let before = delta.texts(base, pages);
    for (page, old) in pages.iter().zip(before) {
        let was: HashMap<String, String> =
            items(&old).into_iter().map(|i| (i.id, i.label)).collect();
        let standing = blocks(&old);
        let text = read_universal(&root.join(page))?.unwrap_or_default();
        let new: Vec<Item> = items(&text)
            .into_iter()
            .filter(|i| {
                LABELS.contains(&i.label.as_str())
                    && was.get(&i.id) != Some(&i.label)
                    && !standing.contains(&i.block)
            })
            .collect();
        if !new.is_empty() {
            out.insert(page.clone(), new);
        }
    }
    Ok(out)
}

/// Every page each pop-up's `Drawing:` names (split pointers followed), sorted, each once.
#[must_use]
pub fn drawing_pages(root: &Path, modals: &[Modal]) -> Vec<String> {
    let mut all: Vec<String> = modals
        .iter()
        .flat_map(|m| followed(root, &m.drawing_files()))
        .collect();
    all.sort();
    all.dedup();
    all
}

/// The items of `gained` on the pages `m`'s `Drawing:` names that its Guesses tab does not reference, `(page, item)` in page order.
#[must_use]
pub fn owed_items(root: &Path, m: &Modal, gained: &Gained) -> Vec<(String, Item)> {
    let referenced = refs::references(m.tag("Guesses"));
    followed(root, &m.drawing_files())
        .into_iter()
        .flat_map(|page| {
            let number = super::stem(&page).chars().take(4).collect::<String>();
            gained
                .get(&page)
                .into_iter()
                .flatten()
                .filter(|i| !referenced.contains(&(number.clone(), i.id.clone())))
                .map(|i| (page.clone(), i.clone()))
                .collect::<Vec<_>>()
        })
        .collect()
}

/// The occasion: "a page its Drawing: names gained a labeled item (<page>#<id> <LABEL>, ...)".
#[must_use]
pub fn occasion(owed: &[(String, Item)]) -> String {
    let named: Vec<String> = owed
        .iter()
        .map(|(page, i)| {
            format!(
                "{}#{} {}",
                super::name_list(std::slice::from_ref(page)),
                i.id,
                i.label
            )
        })
        .collect();
    format!(
        "a page its Drawing: names gained a labeled item ({})",
        named.join(", ")
    )
}

/// The form unit's fingerprint while such items are owed: the form fingerprint and the items, so an answer covers these items and a
/// later item owes again; with none, the form fingerprint itself.
#[must_use]
pub fn fingerprint(fp_form: &str, owed: &[(String, Item)]) -> String {
    if owed.is_empty() {
        return fp_form.to_owned();
    }
    let mut parts = vec![fp_form.to_owned()];
    parts.extend(
        owed.iter()
            .map(|(page, i)| format!("{page}#{} {}", i.id, i.label)),
    );
    digest(&parts.iter().map(String::as_str).collect::<Vec<_>>())
}

/// [`owed_items`] for one pop-up against `base`, read afresh: what its form bundle shows and the triage holds for it.
///
/// # Errors
///
/// Where a page cannot be read: the error says which and why.
pub fn of_modal(root: &Path, base: &str, m: &Modal) -> Result<Vec<(String, Item)>, String> {
    let pages = followed(root, &m.drawing_files());
    let gained = gained(&mut Delta::new(root), base, &pages)?;
    Ok(owed_items(root, m, &gained))
}

#[cfg(test)]
mod tests;
