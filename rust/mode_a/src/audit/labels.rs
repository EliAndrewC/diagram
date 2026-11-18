//! A program item paired with the footprint that draws it (feature 449 T175, `pack_audit/labels.py` whole; feature 254, D7): the
//! pairing the band check makes, BY THE TAGS, never by where a caption stands (feature 286: a caption's position is the placer's
//! output) - the same tags `make size-table` names each rect by, so the size table and the band check cannot drift apart.
//!
//! Research:
//!     the program's labels - NONE: a declared item found on a sheet by its tag or its label, deciding nothing the declaration does not

use l7r_gate_research::pyre::py;
use l7r_gate_research::Error;
use l7r_guard::shared::py_text::split;

use super::checks::first_max;
use crate::grids::FTPX;
use crate::parse::{Label, ParsedPlan, Rect};
use crate::py::fixed;
use crate::types::{classification, BuildingType, Kinds, RequiredItem};

/// The footprint the sheet draws under `kind`: the LARGEST structure tagged with it (a building's parts carry its tag and are smaller,
/// a stepped building is measured on its main block), None when no structure is.
#[must_use]
pub fn footprint<'p>(plan: &'p ParsedPlan, kind: &str) -> Option<&'p Rect> {
    first_max(
        plan.structures
            .iter()
            .filter(|r| plan.label_kinds.get(&r.pos).map(String::as_str) == Some(kind)),
        |r| r.area_px(),
    )
}

/// The sheet's labels a LABELED item's pattern finds, case-blind, over the whole text, its runs of space read as one (a kind item,
/// feature 262, is found by its tag and never by a label).
#[must_use]
pub fn matches<'p>(item: &RequiredItem, labels: &'p [Label]) -> Vec<&'p Label> {
    // a kind item never asks: `types.py`'s `_item` gives every item a label or a kind, and the callers ask a kind first
    let re = py(&format!(
        "(?i){}",
        item.label.as_deref().unwrap_or_default()
    ));
    labels
        .iter()
        .filter(|lb| re.is_match(&split(&lb.text).join(" ")).unwrap_or(false))
        .collect()
}

/// Whether the sheet draws `item`: by an element DECLARED with its id (the no-obvious-labels rule), else a kind item by any element
/// tagged with its kind, a labeled one by a label its pattern finds.
fn present(item: &RequiredItem, plan: &ParsedPlan) -> bool {
    if plan.ids.contains(&item.id) {
        return true;
    }
    if let Some(kind) = &item.kind {
        return plan.kinds.contains(kind);
    }
    !matches(item, &plan.labels).is_empty()
}

/// How the sheet shows an item, in the words a missing-item finding uses.
fn how_found(item: &RequiredItem) -> String {
    match &item.kind {
        Some(kind) => format!("an element tagged data-kind=\"{kind}\""),
        None => format!(
            "a label matching /{}/",
            item.label.as_deref().unwrap_or_default()
        ),
    }
}

/// Every required item of the type's program is on the sheet; an item a knob or the declared form makes absent is not asked for, and a
/// SITE item (feature 257) only where `site` - the classes the declared map shows inside the sheet's frame - says the map has its class
/// there (None: no declaration, every site item asked for; the GM 2026-09-20: the map shows none of that class, the sheet draws none).
#[must_use]
pub fn check_program(
    plan: &ParsedPlan,
    btype: &BuildingType,
    form: Option<&str>,
    site: Option<&[(String, bool)]>,
) -> Vec<String> {
    let mut out = Vec::new();
    for item in &btype.required {
        if item.optional || item.band_for(form).is_none() {
            continue;
        }
        if let (Some(cls), Some(site)) = (&item.site, site) {
            if !site.iter().any(|(k, v)| k == cls && *v) {
                continue;
            }
        }
        if !present(item, plan) {
            out.push(format!(
                "no `{}` on the sheet ({}, or an element marked id=\"{}\")",
                item.id,
                how_found(item),
                item.id
            ));
        }
    }
    out
}

/// The kinds the sheet draws `item` under, in document order: a kind item's own; a labeled item's, the kinds its matching labels are
/// tagged with (an untagged label names nothing the check can measure).
#[must_use]
pub fn kinds_of(item: &RequiredItem, plan: &ParsedPlan) -> Vec<String> {
    if let Some(kind) = &item.kind {
        return vec![kind.clone()];
    }
    let mut out: Vec<String> = Vec::new();
    for lb in matches(item, &plan.labels) {
        if let Some(kind) = plan.label_kinds.get(&lb.pos) {
            if !out.contains(kind) {
                out.push(kind.clone());
            }
        }
    }
    out
}

/// Every required item's footprint lies in its declared band (feet, either orientation); one footprint an item, the first kind the
/// sheet draws one under.
///
/// # Errors
/// [`classification`]'s refusal of an item whose band fails: a kind the Mode A registry does not know.
pub fn check_bands(
    plan: &ParsedPlan,
    btype: &BuildingType,
    form: Option<&str>,
    kinds: &mut Kinds,
) -> Result<Vec<String>, Error> {
    let mut out = Vec::new();
    for item in &btype.required {
        let Some(band) = item.band_for(form) else {
            continue;
        };
        if band.presence_only() {
            continue;
        }
        for kind in kinds_of(item, plan) {
            let Some(r) = footprint(plan, &kind) else {
                continue; // drawn as ground or not at all: the program check's business, not a size's
            };
            let (w_ft, h_ft) = (r.w / FTPX, r.h / FTPX);
            if !band.holds(w_ft, h_ft) {
                let want = match band.area {
                    Some(a) if !(a.0 <= w_ft * h_ft && w_ft * h_ft <= a.1) => {
                        format!("area {}-{} sq ft", fixed(a.0, 0), fixed(a.1, 0))
                    }
                    // `holds` passes anything without both, so this is the w-by-h case
                    _ => {
                        let (bw, bh) = (band.w.unwrap_or_default(), band.h.unwrap_or_default());
                        format!(
                            "w {}-{} by h {}-{} ft",
                            fixed(bw.0, 0),
                            fixed(bw.1, 0),
                            fixed(bh.0, 0),
                            fixed(bh.1, 0)
                        )
                    }
                };
                let (cls, why) = classification(item, kinds)?;
                out.push(format!(
                    "`{}` ({kind}) is {} x {} ft ({} sq ft) at svg({},{}) - the band is {want} ({cls}: {why})",
                    item.id,
                    fixed(w_ft, 0),
                    fixed(h_ft, 0),
                    fixed(w_ft * h_ft, 0),
                    fixed(r.x, 0),
                    fixed(r.y, 0)
                ));
            }
            break;
        }
    }
    Ok(out)
}
