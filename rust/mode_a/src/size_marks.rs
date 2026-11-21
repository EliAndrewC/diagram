//! The sized marks a rect table misses (feature 449 T174): `l7r/diagram/tools/pack_audit/size_marks.py` ported whole - every circle,
//! ellipse, path, line, polyline and polygon of a Mode A sheet in feet, named by its `data-kind` tag ([`mark_rows`], the second section
//! `make size-table` prints), and the tagged kinds no row names ([`untabled_kinds`], feature 294 B15c). A tree crown, a tub, a road, an
//! arch is drawn as a circle or a stroke, so the rect table alone left `size-audit` to measure it by hand.
//!
//! THE PYTHON IS DELETED: `size_marks.py` went with the Python audit, its lockstep retired with it (feature 449 T212; `specs/449-rust-codebase/engine-plan.md`: lockstep tests retire with their Python): this module's own tests pin its behavior, and the pool sweep (`crate::pool_sweep`) puts every pool sheet and red fixture through it (its B15c sweep among them).
//!
//! Research:
//!     the size marks - NONE: a sheet's tagged marks measured in feet, deciding nothing about a building

use std::collections::BTreeSet;

use l7r_gate_research::Error;
use l7r_shared::pyjson::py_float;

use crate::grids::FTPX;
use crate::py::{fmt_g, hypot, round_to, sum};
use crate::tagged::{marks, Mark};

/// The element tags a mark row lists (a rect is the rect table's).
pub const MARK_TAGS: [&str; 6] = ["circle", "ellipse", "path", "line", "polyline", "polygon"];
/// The not-highlighted ruling (`interactive.classes.NOT_HIGHLIGHTED`): ink no table row is owed.
pub const NOT_HIGHLIGHTED: &str = "-";

/// One sized mark: its tag, kind, box (ft), its line length (ft, a stroke's run; 0 for a closed shape) and stroke (ft).
#[derive(Debug, Clone, PartialEq)]
pub struct MarkRow {
    pub tag: String,
    pub kind: String,
    pub x_px: f64,
    pub y_px: f64,
    pub w_ft: f64,
    pub h_ft: f64,
    pub length_ft: f64,
    pub stroke_ft: f64,
}

/// A run's length: Python's `sum` of `math.hypot` over each step.
fn length(pts: &[(f64, f64)]) -> f64 {
    sum(pts
        .windows(2)
        .map(|p| hypot(p[1].0 - p[0].0, p[1].1 - p[0].1)))
}

/// Every tagged circle, ellipse, path, line, polyline and polygon, in feet, largest first.
///
/// # Errors
/// [`marks`]' refusal.
pub fn mark_rows(svg: &str) -> Result<Vec<MarkRow>, Error> {
    let mut out = Vec::new();
    for m in marks(svg)? {
        let Some(kind) = m.kind.as_deref().filter(|k| *k != NOT_HIGHLIGHTED) else {
            continue;
        };
        if !MARK_TAGS.contains(&m.tag.as_str()) {
            continue;
        }
        let stroke = m.stroke_width()?;
        out.push(MarkRow {
            kind: kind.to_owned(),
            x_px: round_to(m.x, 1),
            y_px: round_to(m.y, 1),
            w_ft: round_to(m.w / FTPX, 1),
            h_ft: round_to(m.h / FTPX, 1),
            length_ft: round_to(length(&m.pts) / FTPX, 1),
            stroke_ft: round_to(stroke / FTPX, 1),
            tag: m.tag,
        });
    }
    // the Python's `sort(key=lambda r: -(...))`, stable: a NaN key (a coordinate past a float's range) is not ordered as its timsort
    // would order it, and no sheet draws one
    out.sort_by(|a, b| {
        let key = |r: &MarkRow| -(r.w_ft * r.h_ft + r.length_ft);
        key(a)
            .partial_cmp(&key(b))
            .unwrap_or(std::cmp::Ordering::Equal)
    });
    Ok(out)
}

/// A row of either table: a rect with an area, or a mark of [`MARK_TAGS`].
fn sized(m: &Mark) -> bool {
    (m.tag == "rect" && m.w > 0.0 && m.h > 0.0) || MARK_TAGS.contains(&m.tag.as_str())
}

/// The tagged kinds that no rect row and no mark row carries, as its own kind or as a kind it is a part of - sized nowhere a size audit
/// reads. A group kind whose parts carry kinds of their own is listed by its parts' rows; a kind tagged on nothing but captions has no
/// drawn extent to size, so it owes no row (feature 294: the rule holds a DRAWN feature to the table).
///
/// # Errors
/// [`marks`]' refusal.
pub fn untabled_kinds(svg: &str) -> Result<Vec<String>, Error> {
    let ms = marks(svg)?;
    let listed: BTreeSet<&str> = ms
        .iter()
        .filter(|m| sized(m))
        .flat_map(|m| m.kind.iter().chain(&m.lineage).map(String::as_str))
        .collect();
    let tagged: BTreeSet<&str> = ms
        .iter()
        .filter(|m| m.tag != "text")
        .filter_map(|m| m.kind.as_deref())
        .collect();
    Ok(tagged
        .difference(&listed)
        .filter(|k| **k != NOT_HIGHLIGHTED)
        .map(|k| (*k).to_owned())
        .collect())
}

/// The mark rows as the size table's second section.
#[must_use]
pub fn render(rows: &[MarkRow]) -> String {
    let mut lines = vec![
        format!(
            "marks (circles, ellipses, paths, lines, polygons): {}",
            rows.len()
        ),
        format!(
            "{:>7}{:>7}{:>8}{:>8}  {:<9}{:<14}kind (data-kind)",
            "w ft", "h ft", "run ft", "ink ft", "tag", "at px"
        ),
    ];
    for r in rows {
        lines.push(format!(
            "{:>7}{:>7}{:>8}{:>8}  {:<9}{:<14}{}",
            py_float(r.w_ft),
            py_float(r.h_ft),
            py_float(r.length_ft),
            py_float(r.stroke_ft),
            r.tag,
            format!("{},{}", fmt_g(r.x_px), fmt_g(r.y_px)),
            r.kind
        ));
    }
    lines.join("\n")
}

#[cfg(test)]
mod tests;
