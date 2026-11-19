//! `l7r-mode-a caption-counts <sheet.svg>`: the caption placer's counted work on one hand sheet, per caption (feature 449 T198) - a
//! command of the counting build alone (the crate's `counters` feature), so no drawing build carries it. The sheet is read and seated as
//! [`super::placed`] seats it; the counts are the run's ([`crate::work_counts::ops`]) and each scope's - `greedy <head>` a caption's
//! search in the greedy pass, `repair <head>` its repair - with each caption's text, what it names, and where it landed. One JSON object.
//!
//! Research: the placer's counted work - NONE: it counts, and decides nothing about the place

use std::collections::BTreeMap;
use std::time::Instant;

use l7r_gate_research::Error;
use serde_json::{json, Value};

use super::{read_sheet, seat};
use crate::labels::placer::Kind;
use crate::work_counts::{by_scope, ops, reset};

/// The counts of one sheet's seating, as JSON: the seat's wall time (the counting build's, so above a drawing build's), the run's counts,
/// those counted outside every caption's scope, and each caption's.
///
/// # Errors
/// The sheet unreadable, or the placer's refusals, as [`super::placed`] meets them.
pub fn report(src: &str) -> Result<String, Error> {
    let (shapes, view) = read_sheet(src)?;
    reset();
    let began = Instant::now();
    let seated = seat(&shapes, view)?;
    let took = began.elapsed().as_secs_f64();
    let totals = ops();
    let scopes: BTreeMap<String, BTreeMap<String, u64>> = by_scope().into_iter().collect();
    let mut unscoped = totals.clone();
    for counts in scopes.values() {
        for (k, n) in counts {
            if let Some(v) = unscoped.get_mut(k) {
                *v -= n;
            }
        }
    }
    unscoped.retain(|_, n| *n > 0);
    let captions: Vec<Value> = seated
        .iter()
        .map(|(idx, p, per, sub)| {
            let text: Vec<&str> = idx
                .iter()
                .flat_map(|&i| shapes[i].lines.iter().map(String::as_str))
                .collect();
            let of = |phase: &str| {
                let name = format!("{phase} {}", idx[0]);
                scopes.get(&name).cloned().unwrap_or_default()
            };
            let kind = match sub.kind {
                Kind::Point => "point",
                Kind::Line => "line",
                Kind::Area => "area",
            };
            json!({
                "head": idx[0],
                "text": text.join(" "),
                "kind": kind,
                "poly_pts": sub.poly.len(),
                "ink_parts": sub.ink.len(),
                "ink_pts": sub.ink.iter().map(|i| i.pts.len()).sum::<usize>(),
                "ring": p.ring,
                "rank": p.rank,
                "position": p.position,
                "cost": p.cost,
                "leader": p.leader.is_some(),
                "lines": per.iter().map(Vec::len).sum::<usize>(),
                "greedy": of("greedy"),
                "repair": of("repair"),
            })
        })
        .collect();
    let out = json!({
        "seat_s": took,
        "shapes": shapes.len(),
        "totals": totals,
        "unscoped": unscoped,
        "captions": captions,
    });
    Ok(format!("{out}\n"))
}

#[cfg(test)]
mod tests {
    use super::report;

    /// A sheet of one caption naming one tub: its search counted under its scope, the run's counts holding it (T198).
    #[test]
    fn a_caption_is_counted_under_its_own_scope() {
        let src = concat!(
            r##"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300"><rect x="0" y="0" width="400" height="300" fill="#EFE3C2" data-kind="-"/>"##,
            r##"<g data-kind="tub"><circle cx="50" cy="50" r="5"/><text x="80" y="80" font-size="6">tub</text></g></svg>"##
        );
        let got: serde_json::Value = serde_json::from_str(&report(src).unwrap()).unwrap();
        let cap = &got["captions"][0];
        assert_eq!(cap["text"], "tub");
        assert!(cap["greedy"]["call@place"].as_u64().unwrap() >= 1);
        assert!(got["totals"]["call@place"].as_u64().unwrap() >= 1);
        assert!(got["seat_s"].as_f64().unwrap() >= 0.0);
    }

    /// An unreadable sheet is refused as the placer refuses it.
    #[test]
    fn a_sheet_that_is_no_xml_is_refused() {
        assert!(report("<svg").is_err());
    }
}
