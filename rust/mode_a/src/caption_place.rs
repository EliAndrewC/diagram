//! THE HAND SHEETS' CAPTION PLACER, rebuilt from its derivation (feature 449 T202; `specs/449-rust-codebase/derivations/T198-placer.md`,
//! judged SOUND and budgeted per pool sheet by T201): a hand-drawn Mode A sheet's declared captions seated as 0242 and 0330 require, by a
//! search doing the work its job needs and no more. Written from the derivation and the two drawing pages alone (the GM, 2026-10-30: "we
//! are not trying to re-implement the same algorithms"), never from the placer it replaces.
//!
//! The sheet is read once ([`crate::labels::hand_sheet::read_sheet`]); its ink filed once in a grid of 48 px cells ([`index`]); each
//! declared caption ([`captions`]) seated in declaration order ([`search`]) - on its feature, else at the eight ranked places at the usual
//! gap, else swept outward a cell at a time, else where it covers least - its block and leader ([`leader`]) filed as it is seated, so no
//! later caption covers it; and the seats written into the sheet's text ([`write`]). Nothing is placed and then moved.
//!
//! The counted work (the crate's `counters` feature): the derivation's kinds, each `<kind>@<function>` - `seat`, `index_query`,
//! `index_cell`, `index_entry`, `exact_test`, `shape_distance`, `sweep_interval`, `sweep_compare`, `wrap_cut`, `index_insert`,
//! `shape_box`, `name_lookup`, `write` (`leader_crossing` budgeted 0 and never counted: no rule owes it). `l7r-mode-a caption-counts`
//! reads them per caption.
//!
//! Research: the caption placer - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html, research/questions/0330-how-a-leader-line-ties-a-caption-to-its-feature.drawing.html: every rule claimed where the search decides it

pub mod captions;
pub mod geom;
pub mod index;
pub mod leader;
pub mod search;
pub mod wrap;
pub mod write;

use l7r_gate_research::Error;

use self::captions::{declared, Caption};
use self::geom::Bx;
use self::index::Index;
use self::search::{Placer, Seat};
use crate::labels::hand_sheet::read_sheet;
pub use crate::labels::hand_sheet::Shape;

/// Every declared caption of a read sheet seated, in the order [`nested_first`] gives: areas before points, the most nested first,
/// declaration order breaking ties.
///
/// # Errors
/// A declared caption that names nothing drawn: it has no feature to stand on or beside.
///
/// Research: the seating order - NONE: captions are seated in the order `nested_first` gives (its own claim: areas first, the most nested first), declaration order breaking its ties - an order this function leaves to it, deciding none of its own
pub fn seat(src: &str, shapes: &[Shape], view: Bx) -> Result<Vec<(Caption, Seat)>, Error> {
    #[cfg(feature = "counters")]
    crate::work_counts::scope("build");
    let mut caps = declared(shapes);
    written_last(src, shapes, &mut caps);
    if let Some(c) = caps.iter().find(|c| c.fbox.is_none()) {
        return Err(Error::new(
            "ValueError",
            format!("the caption {:?} names nothing drawn", c.text()),
        ));
    }
    let mut named_by = vec![0_u16; shapes.len()];
    for p in caps.iter().flat_map(|c| c.parts.iter().copied()) {
        named_by[p] = named_by[p].saturating_add(1);
    }
    let first = caps.iter().map(|c| c.at).min().unwrap_or(usize::MAX);
    let mut placer = Placer {
        shapes,
        ix: Index::build(shapes, view, named_by, first),
    };
    let order = nested_first(&mut placer.ix, &caps);
    let mut caps: Vec<Option<Caption>> = caps.into_iter().map(Some).collect();
    let mut out = Vec::with_capacity(caps.len());
    for cap in order.into_iter().filter_map(|i| caps[i].take()) {
        #[cfg(feature = "counters")]
        crate::work_counts::scope(&format!("place {}", cap.head()));
        let s = placer.seat(&cap);
        out.push((cap, s));
    }
    Ok(out)
}

/// The order captions are seated in: the names that fit on their own feature first, the most nested of them first - a room before the
/// house that holds it, the house before its court - and then the names of points, seated beside them; each caption's depth the named
/// outlines holding its feature's middle (one point asked of the grid), ties in declaration order.
///
/// Research: the most constrained first - CONVENTION: an area's name has only its area - a room's its room, the house's the house - while a point's name has eight places and a sweep beside it; seating the areas first, the most nested of them first, leaves each region's name the room its parts' names do not need (the coordinator's ruling 2026-11-19, the standard most-constrained-first order in place of a place-then-move repair; a house's name declared before its rooms took the middle of them, and a practice yard's posts' names, seated first, took the middle of the yard, on a pool sheet)
fn nested_first(ix: &mut Index, caps: &[Caption]) -> Vec<usize> {
    let mut depth: Vec<(usize, usize, usize)> = Vec::with_capacity(caps.len());
    for (i, cap) in caps.iter().enumerate() {
        let fb = cap.fsheet.unwrap_or_default();
        let m = (f64::midpoint(fb.0, fb.2), f64::midpoint(fb.1, fb.3));
        let mut holders: Vec<usize> = Vec::new();
        for id in ix.query((m.0, m.1, m.0, m.1), "nested_first") {
            let e = &ix.entries[id as usize];
            let Some(s) = e.shape else { continue };
            let named = ix.named_by[s] >= 1 && !cap.parts.contains(&s);
            if named && e.body && geom::holds(e.bx, fb) && !holders.contains(&s) {
                holders.push(s);
            }
        }
        // a name that fits on its own feature (on one of its parts) is an area's; any other a point's, named beside
        let fits = cap
            .holder
            .iter()
            .map(|h| h.1)
            .chain(cap.members.iter().map(|m| m.1))
            .any(|hb| Placer::inside_layout(cap, hb).is_some());
        depth.push((usize::from(!fits), holders.len(), i));
    }
    depth.sort_by(|a, b| a.0.cmp(&b.0).then(b.1.cmp(&a.1)).then(a.2.cmp(&b.2)));
    depth.into_iter().map(|(_, _, i)| i).collect()
}

/// Each caption declared as a child of its tagged group (not of an element within it) is written at the group's end, and so painted
/// after all of the group: its paint order is the group's last element's.
fn written_last(src: &str, shapes: &[Shape], caps: &mut [Caption]) {
    let spans = crate::hand_sheet::start_tags(src);
    let bytes = write::byte_at(src);
    let byte = |at: usize| bytes[spans[at].0];
    for cap in caps.iter_mut() {
        let g = shapes[cap.head()].group;
        if g == shapes[cap.head()].at {
            continue;
        }
        let children: Vec<usize> = cap.elems.iter().map(|e| byte(shapes[e.shape].at)).collect();
        // a group holding a caption has an end; every line a child of the group itself, or the caption stays where it is declared
        let end = write::group_end(src, (byte(g), bytes[spans[g].1]), &children);
        let (subtree, move_to, at) = end.map_or((None, None, cap.at), |(close, direct)| {
            let last = spans.partition_point(|s| bytes[s.0] < close) - 1;
            let moved = direct.iter().all(|&d| d);
            (
                Some((g, last)),
                moved.then_some(close),
                if moved { last } else { cap.at },
            )
        });
        (cap.subtree, cap.move_to, cap.at) = (subtree, move_to, at);
    }
}

/// A hand sheet's text with every declared caption placed: what the sheet driver renders, pages and audits.
///
/// # Errors
/// The sheet unreadable ([`read_sheet`]'s refusals), or a caption naming nothing drawn.
pub fn placed(src: &str) -> Result<String, Error> {
    let (shapes, view) = read_sheet(src)?;
    let seated = seat(src, &shapes, view)?;
    Ok(write::write(src, &shapes, &seated))
}

#[cfg(test)]
mod tests;
