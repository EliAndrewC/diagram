//! `l7r-mode-a caption-counts <sheet.svg>`: the caption placer's counted work on one hand sheet, per caption (feature 449 T198; wired to
//! the placer rebuilt from its derivation by T202, [`crate::caption_place`]) - a command of the counting build alone (the crate's
//! `counters` feature), so no drawing build carries it. The sheet is read and seated as [`crate::caption_place::placed`] seats it; the
//! counts are the run's ([`crate::work_counts::ops`]), the build's (the scope `build`: the grid filed, the captions read) and each
//! caption's (the scope `place <head>`), with each caption's text, how it was seated and where. `by_kind` sums the run's counts by the
//! derivation's kinds, the figure `make budget-sheets` compares with each sheet's budget. One JSON object.
//!
//! Research: the placer's counted work - NONE: it counts, and decides nothing about the place

use std::collections::BTreeMap;
use std::time::Instant;

use l7r_gate_research::Error;
use serde_json::{json, Value};

use super::read_sheet;
use crate::caption_place::search::How;
use crate::caption_place::seat;
use crate::work_counts::{by_kind, by_scope, ops, reset};

/// The counts of one sheet's seating, as JSON: the seat's wall time (the counting build's, so above a drawing build's), the run's counts
/// by key and by kind with their total, the build's, and each caption's.
///
/// # Errors
/// The sheet unreadable, or the placer's refusals, as [`crate::caption_place::placed`] meets them.
pub fn report(src: &str) -> Result<String, Error> {
    let (shapes, view) = read_sheet(src)?;
    reset();
    let began = Instant::now();
    let seated = seat(src, &shapes, view)?;
    let took = began.elapsed().as_secs_f64();
    let totals = ops();
    let kinds = by_kind(&totals);
    let scopes: BTreeMap<String, BTreeMap<String, u64>> = by_scope().into_iter().collect();
    let captions: Vec<Value> = seated
        .iter()
        .map(|(cap, s)| {
            let (how, rank, offset, cover) = match s.how {
                How::Inside(d) => ("inside", None, Some(d), None),
                How::Gap(r) => ("gap", Some(r), None, None),
                How::Swept(d, r) => ("swept", Some(r), Some(d), None),
                How::CoverLeast(c) => ("cover-least", None, None, Some(c)),
            };
            json!({
                "head": cap.head(),
                "text": cap.text(),
                "parts": cap.parts.len(),
                "how": how,
                "rank": rank,
                "offset": offset,
                "gap": cap.gap,
                "block": [s.w, s.h],
                "angle": s.angle,
                "feature": cap.fsheet.map(|b| [b.0, b.1, b.2, b.3]),
                "cover": cover,
                "center": [s.center.0, s.center.1],
                "leader": s.leader.is_some(),
                "cut": s.cut,
                "counts": scopes.get(&format!("place {}", cap.head())).cloned().unwrap_or_default(),
            })
        })
        .collect();
    let out = json!({
        "seat_s": took,
        "shapes": shapes.len(),
        "totals": totals,
        "by_kind": kinds,
        "total": kinds.values().sum::<u64>(),
        "build": scopes.get("build").cloned().unwrap_or_default(),
        "captions": captions,
        "furniture": shapes
            .iter()
            .filter(|s| s.tag == "text" && !crate::caption_place::captions::is_declared(s))
            .map(|s| {
                let b = crate::caption_place::geom::bbox(&s.poly);
                json!({"text": s.text, "size": s.size, "box": [b.0, b.1, b.2, b.3]})
            })
            .collect::<Vec<_>>(),
    });
    Ok(format!("{out}\n"))
}

#[cfg(test)]
mod tests {
    use super::report;

    /// A sheet of one caption naming one tub: its search counted under its own scope, the run's counts holding it and summed by kind
    /// (T198, T202).
    #[test]
    fn a_caption_is_counted_under_its_own_scope() {
        let src = concat!(
            r##"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300"><rect x="0" y="0" width="400" height="300" fill="#EFE3C2" data-kind="-"/>"##,
            r##"<g data-kind="tub"><circle cx="50" cy="50" r="5"/><text font-size="6">tub</text></g></svg>"##
        );
        let got: serde_json::Value = serde_json::from_str(&report(src).unwrap()).unwrap();
        let cap = &got["captions"][0];
        assert_eq!(cap["text"], "tub");
        // the tub's 10 px disc holds its 6 px name: named on itself (0242)
        assert_eq!(cap["how"], "inside");
        assert!(cap["counts"]["seat@inside"].as_u64().unwrap() >= 1);
        assert!(got["by_kind"]["seat"].as_u64().unwrap() >= 1);
        assert!(got["total"].as_u64().unwrap() >= got["by_kind"]["write"].as_u64().unwrap());
        assert!(got["seat_s"].as_f64().unwrap() >= 0.0);
    }

    /// An unreadable sheet is refused as the placer refuses it.
    #[test]
    fn a_sheet_that_is_no_xml_is_refused() {
        assert!(report("<svg").is_err());
    }
}
