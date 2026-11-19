//! Every caption of a sheet seated (feature 449 T151, `labels/hand_sheet.py`'s `captions_of`, `declared_parts`, `subjects`, `seat`,
//! `repair` and their helpers; features 266, 267, 283, 286): each caption's subject found from its declaration, the captions placed in
//! the cartographer's order, each avoiding the others, and the greedy pass repaired.
//!
//! Research: the hand sheet's seating plumbing - NONE: captions grouped, ordered and tried against their subjects, each rule claimed where it is decided

#![expect(
    clippy::similar_names,
    reason = "the Python's names, kept so each line reads against its original (x0 and x1, bx0 and by0)"
)]

use std::collections::{BTreeMap, BTreeSet, HashMap};

use geo::{Area, LineString, Polygon};
use l7r_gate_research::Error;
use l7r_guard::shared::py_text::repr;

use super::super::geom::{bbox, dist, BBox, Pt};
use super::super::layout::layouts;
use super::super::obstacles::{Obstacle, ObstacleIndex};
use super::super::placer::{
    hug_gap, in_frame, judge, place, referent_box, Ask, InkPart, Kind, Placement, Subject,
    LEADERLESS_RINGS,
};
use super::super::standard::{
    chars, CENTER_ABOVE_BASELINE_EM, CLEAR_EM, PITCH_EM, REACH_EM, WEIGHT_OBSTACLE,
};
use super::classify::{band, classify, drawn_ink, leader_blockers, leader_to_ink, same_box, Seen};
use super::{char_w_of, luma, Shape, BLOCK_PX, GROUND_KINDS, LIGHT, REPAIR, STEPPED, WEIGHT_TEXT};
use crate::py::{hypot, max, min, round_int, sum};

/// A caption seated: its placement, its texts' lines as placed, and the subject it was seated against (which the Python kept only in its
/// search; the port's comparison audits a seat against it).
pub type Seated = (Placement, Vec<Vec<String>>, Subject);

/// A caption seated with its texts' indices.
pub type SeatedCaption = (Vec<usize>, Placement, Vec<Vec<String>>, Subject);

/// A seat's outline and whether it has a direction of its own ([`squared`]), which its caption takes.
type Inside = (Vec<Pt>, bool);

/// A seat beside: its outline, whether it has a direction of its own, and the drawn parts its leader ends on ([`drawn_ink`]).
type Beside = (Vec<Pt>, bool, Vec<InkPart>);

/// A box's area.
#[must_use]
pub fn area(poly: &[Pt]) -> f64 {
    let (x0, y0, x1, y1) = bbox(poly);
    (x1 - x0) * (y1 - y0)
}

/// Does `a`'s box lie within `b`'s?
#[must_use]
pub fn box_within(a: &[Pt], b: &[Pt]) -> bool {
    let (ax0, ay0, ax1, ay1) = bbox(a);
    let (bx0, by0, bx1, by1) = bbox(b);
    ax0 >= bx0 && ay0 >= by0 && ax1 <= bx1 && ay1 <= by1
}

/// The gap between two boxes (the Python's `_box_gap`).
fn box_gap(a: &[Pt], b: &[Pt]) -> f64 {
    let (ax0, ay0, ax1, ay1) = bbox(a);
    let (bx0, by0, bx1, by1) = bbox(b);
    hypot(
        max(0.0, max(ax0, bx0) - min(ax1, bx1)),
        max(0.0, max(ay0, by0) - min(ay1, by1)),
    )
}

fn corners(b: BBox) -> Vec<Pt> {
    vec![(b.0, b.1), (b.2, b.1), (b.2, b.3), (b.0, b.3)]
}

/// The box of every point of the shapes `own` names.
fn box_of(shapes: &[Shape], own: &[usize]) -> BBox {
    let pts: Vec<Pt> = own
        .iter()
        .flat_map(|&i| shapes[i].poly.iter().copied())
        .collect();
    bbox(&pts)
}

/// The sheet's captions, each the list of its `<text>` indices in document order: every text tagged with a kind (on itself or a group
/// around it) is a caption, and a text marked `data-cont="1"` is the next line of the caption before it. Untagged and `-` texts are the
/// sheet's own drawing - its title and its scale - and are not placed.
///
/// # Errors
/// A continuation with no caption before it.
///
/// Research: a sheet's captions - CONVENTION: every text tagged with a kind but `-` is a caption, a `data-cont` text its next line; the title and scale are the sheet's own drawing (feature 286)
pub fn captions_of(shapes: &[Shape]) -> Result<Vec<Vec<usize>>, Error> {
    let mut out: Vec<Vec<usize>> = Vec::new();
    for (i, s) in shapes.iter().enumerate() {
        if s.tag != "text" || s.text.is_empty() || s.kind.is_empty() || s.kind == "-" {
            continue;
        }
        if s.cont {
            let Some(last) = out.last_mut() else {
                return Err(Error::new(
                    "ValueError",
                    format!(
                        "caption line {} is marked data-cont but no caption comes before it",
                        repr(&s.text)
                    ),
                ));
            };
            last.push(i);
        } else {
            out.push(vec![i]);
        }
    }
    Ok(out)
}

/// Does the caption's text carry its own `data-kind` rather than take one from a group?
fn self_tagged(head: &Shape) -> bool {
    head.get("data-kind").is_some()
}

/// What a caption names, from its declaration alone (feature 286, plan D1): the shapes its `data-names` mark by their `data-id`, else -
/// for the one caption of a tagged group - the group's own drawn shapes. Where it stands is never read.
///
/// Research: what a caption names - CONVENTION: a caption names what its declaration marks, never what it stands nearest (feature 286, the GM)
///
/// # Errors
/// A caption that declares nothing it can name: it cannot be placed, and a caption is never dropped (feature 266).
pub fn declared_parts(head: &Shape, shapes: &[Shape], alone: bool) -> Result<Vec<usize>, Error> {
    if !head.names.is_empty() {
        let want: BTreeSet<&str> = head.names.iter().map(String::as_str).collect();
        let own: Vec<usize> = (0..shapes.len())
            .filter(|&i| {
                shapes[i].tag != "text"
                    && !shapes[i].leader
                    && shapes[i].ids.iter().any(|d| want.contains(d.as_str()))
            })
            .collect();
        let found: BTreeSet<&str> = own
            .iter()
            .flat_map(|&i| shapes[i].ids.iter().map(String::as_str))
            .collect();
        let missing: Vec<String> = want.difference(&found).map(|m| repr(m)).collect();
        if !missing.is_empty() {
            return Err(Error::new(
                "ValueError",
                format!(
                    "caption {}: data-names [{}] mark no drawn shape",
                    repr(&head.text),
                    missing.join(", ")
                ),
            ));
        }
        return Ok(own);
    }
    if alone && head.group != 0 && !self_tagged(head) {
        let own: Vec<usize> = (0..shapes.len())
            .filter(|&i| {
                shapes[i].group == head.group && shapes[i].tag != "text" && !shapes[i].leader
            })
            .collect();
        if !own.is_empty() {
            return Ok(own);
        }
    }
    Err(Error::new(
        "ValueError",
        format!(
            "caption {} ({}) names nothing: stand it alone in the tagged group it names, or give it data-names",
            repr(&head.text),
            head.kind
        ),
    ))
}

/// The area of a set of outlines' union - shapely's `unary_union(closed).area` over the `geo` crate's overlay, the one place a subject's
/// order turns on geometry the two compute apart (measured on the pool sheets by `parse/lockstep_labels.rs`).
#[must_use]
pub fn union_area(polys: &[&[Pt]]) -> f64 {
    let shapes: Vec<Polygon<f64>> = polys
        .iter()
        .map(|p| Polygon::new(LineString::from(p.to_vec()), Vec::new()))
        .collect();
    geo::unary_union(&shapes).unsigned_area()
}

/// Do the closed parts fill `box_` ([`STEPPED`] of it) - one thing whose box is its outline, not blocks in echelon?
///
/// Research: stepped subject fill - CONVENTION: a multi-part subject filling under 0.85 of its box is named against its parts, not the box - a calibration of the placer, which changes where a caption is seated
fn covers(own: &[&Shape], box_: &[Pt]) -> bool {
    let closed: Vec<&[Pt]> = own
        .iter()
        .filter(|s| !s.line && s.poly.len() >= 3)
        .map(|s| s.poly.as_slice())
        .collect();
    !closed.is_empty() && union_area(&closed) >= STEPPED * area(box_)
}

/// The drawn ink of one closed part as the sheet draws it (the Python's `_drawn_as`): its own and that of every other closed part of `own`
/// sharing its box - a fill and the outline stroked over it as two elements (Hayakawa's RESIDENCE's blocks), which draw one block (feature
/// 449 T193: a leader read off the fill alone ended inside the outline's stroke).
fn drawn_as(part: &Shape, own: &[&Shape]) -> Vec<InkPart> {
    own.iter()
        .filter(|s| {
            std::ptr::eq(**s, part)
                || (!s.line && s.poly.len() >= 3 && same_box(&s.poly, &part.poly))
        })
        .map(|s| drawn_ink(s))
        .collect()
}

/// The subjects a caption is tried against, in order (feature 286, plan D2): INSIDE first - the one closed shape it names, or the box of
/// parts that fill it, or each block of a stepped building, largest first - then BESIDE: the box, or each block. A scatter of glyphs and
/// lines has no inside, and is named beside the group, else beside any one of its glyphs - only beside a glyph where the group spreads
/// wider than the standard's reach at the caption's `size`. An area with no direction of its own - a box of parts, an irregular outline - is
/// named level, however long and narrow (feature 449 T184: an area three times taller than wide was named along its length, where 0242
/// keeps an area's caption level); a feature with a direction of its own ([`squared`]: a drawn rect, an outline whose every corner is square, an
/// ellipse of unequal radii) is turned with the sheet, and its name inside it, like a caption beside a turned feature, takes its outline's
/// first edge's angle (feature 449 T188: a turned building's roof name was set level), a quarter, half or three-quarter turn keeping it
/// level; beside it, the caption is seated off the box of what it names read in that feature's own frame ([`framed`]; feature 449 T189: a
/// turned garden holding its lantern and a lone turned block among its parts were named level beside, off the upright box). Each subject
/// beside carries the drawn ink of what it is read off as its `ink` ([`drawn_ink`]), which its leader ends on: a subject read off one part -
/// a lone shape, a scatter's member, a block of a stepped building - that part's and that of every closed part drawn with its box ([`drawn_as`]; T193: a fill and its stroked outline drawn as two elements), and a subject read off a box of several parts every
/// part's (feature 449 T191: a leader to a lone L-shaped house was scored to its box's corner over the empty ground of its notch; T192: a
/// leader to a disc ended on its drawn box, and one to several parts was scored to their box while `leader_to_ink` drew it to their ink).
///
/// Research:
///     a caption's subjects - CONVENTION: inside what it names first, then beside it; a stepped building by its blocks, largest first; a scatter beside its glyphs (feature 286, plan D2)
///     an area's caption level - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a caption naming an area with no direction of its own (a box of parts, an outline with a corner off square, a disc drawn round) is level; the name inside a feature that has a direction of its own - a drawn rect, an outline whose every corner is square (a rectangle, an L-shaped house) or an ellipse of unequal radii, which a turned group turns - takes the feature's own angle, as a turned feature's caption does
///     a turned subject's angle - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a caption naming a turned feature, beside it or inside it, takes its own angle, read off its outline's first edge, and beside it is seated off its turned edge, not off an upright box around it - a lone shape's box, a holder's box of what it holds or a lone block's box of its parts, each read in the feature's own frame, and a scatter's member by its own outline, which the placer's seats read in that member's frame; a feature turned a quarter, a half or three quarters of a turn keeps a level caption
///     a lone block's beside box - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a lone block among smaller parts is named beside the box of all its parts read in the block's own frame, not off the block alone - the page's map drawing convention (a block named among loose parts "is seated beside the smallest box holding them all"); the caption names every part, and at level this box is the upright box the caption had (feature 449 T189)
///     which subjects carry ink - CONVENTION: every subject beside carries the drawn parts it is read off as the ink its leader ends on - a subject read off one part (a lone shape, a scatter's member, a block of a stepped building) that part and every closed part drawn with its box (a fill and its stroked outline drawn as two elements draw one block), a subject read off a box of several parts every part - so the leader the placer weighs is the one `leader_to_ink` draws; an inside subject carries none, an area's name taking no leader; 0242 has the leader end at the nearest drawn point, and the ink is where that point is read (feature 449 T191, T192, T193)
#[must_use]
pub fn subjects(own: &[&Shape], size: f64) -> Vec<Subject> {
    let pts: Vec<Pt> = own.iter().flat_map(|s| s.poly.iter().copied()).collect();
    let (x0, y0, x1, y1) = bbox(&pts);
    let box_ = corners((x0, y0, x1, y1));
    let closed: Vec<&Shape> = own
        .iter()
        .copied()
        .filter(|s| !s.line && s.poly.len() >= 3)
        .collect();
    let by_area_desc = |items: &mut Vec<&Shape>| {
        items.sort_by(|a, b| {
            area(&b.poly)
                .partial_cmp(&area(&a.poly))
                .unwrap_or(std::cmp::Ordering::Equal)
        });
    };
    let mut blocks: Vec<&Shape> = own
        .iter()
        .copied()
        .filter(|s| s.tag == "rect" && area(&s.poly) >= BLOCK_PX)
        .collect();
    by_area_desc(&mut blocks);
    let holder = closed
        .iter()
        .copied()
        .fold(None, |m: Option<&Shape>, s| match m {
            Some(b) if area(&s.poly) <= area(&b.poly) => Some(b),
            _ => Some(s),
        });
    // every part's drawn ink, which the leader of a subject read off a box of several parts ends on (feature 449 T192)
    let every: Vec<InkPart> = own.iter().map(|s| drawn_ink(s)).collect();
    // each inside seat with whether it has a direction of its own - a drawn rect, an outline whose every corner is square, an ellipse of
    // unequal radii (feature 449 T188, T189) - and each beside seat with the same and the drawn ink its leader ends on: only such a
    // feature's caption is turned with it
    let level = |poly: &Vec<Pt>| (poly.clone(), false, every.clone());
    let (inner, beside): (Vec<Inside>, Vec<Beside>) = if own.len() == 1 && !closed.is_empty() {
        let one = own[0].poly.clone();
        let sq = squared(own[0]);
        // beside its box in its own frame - a rectangle's own outline, an L-shaped house's turned box (feature 449 T189); its leader to
        // its own drawn outline, not to that box's corner over the empty ground of an L's notch (feature 449 T191) or beside a disc's
        // curve (T192)
        let by = if sq {
            (framed(&one, turned(&one)), true, every.clone())
        } else {
            level(&box_)
        };
        (vec![(one, sq)], vec![by])
    } else if let Some(h) = holder.filter(|h| own.iter().all(|s| box_within(&s.poly, &h.poly))) {
        // one outline holding the rest - a garden and the lantern in it (Ochiba's inner garden) - named beside the box of them all read in
        // the holder's own frame where it has a direction of its own (feature 449 T189: a turned garden was named level beside, off the
        // upright box)
        let sq = squared(h);
        let frame = if sq { turned(&h.poly) } else { 0.0 };
        (
            vec![(h.poly.clone(), sq)],
            vec![(framed(&pts, frame), sq, every.clone())],
        )
    } else if covers(own, &box_) {
        (vec![(box_.clone(), false)], vec![level(&box_)])
    } else if !blocks.is_empty() {
        let rects: Vec<Inside> = blocks.iter().map(|b| (b.poly.clone(), true)).collect();
        // a lone block among small parts is named beside the box of them all read in the block's own frame (feature 449 T189: a lone
        // turned block was named level beside, off the upright box)
        let beside = if blocks.len() >= 2 {
            blocks
                .iter()
                .map(|b| (b.poly.clone(), true, drawn_as(b, own)))
                .collect()
        } else {
            vec![(framed(&pts, turned(&blocks[0].poly)), true, every.clone())]
        };
        (rects, beside)
    } else {
        // a scatter of like glyphs: beside the group, else beside any one of them, largest first; a group wider than the standard's
        // reach at the caption's size has no "beside" (Hayakawa's tubs were named outside the compound's corner). A member with a
        // direction of its own (a turned L-shaped house) goes as its own outline at its angle: the placer's seats read its box in that
        // frame already (`box_frame`), so its `framed` box would give the same seats, while the association gap and a leader's end,
        // read off the outline, stay on the member's ink (feature 449 T190, measured 2026-11-18)
        let mut members = closed.clone();
        by_area_desc(&mut members);
        let spread = size > 0.0 && max(x1 - x0, y1 - y0) > REACH_EM * size;
        let beside = if closed.len() > 1 {
            let mut b = if spread {
                Vec::new()
            } else {
                vec![level(&box_)]
            };
            b.extend(
                members
                    .iter()
                    .map(|s| (s.poly.clone(), squared(s), drawn_as(s, own))),
            );
            b
        } else {
            vec![level(&box_)]
        };
        (Vec::new(), beside)
    };
    let mut out = Vec::new();
    for (poly, sq) in inner {
        // a rectangle's name inside it takes the rectangle's own angle; an area with no direction of its own - a box of parts, an
        // irregular outline - is level
        let angle = if sq { turned(&poly) } else { 0.0 };
        out.push(Subject::new(Kind::Area, poly, angle));
    }
    for (poly, sq, ink) in beside {
        let angle = if sq { turned(&poly) } else { 0.0 };
        out.push(Subject {
            ink,
            ..Subject::new(Kind::Point, poly, angle)
        });
    }
    out
}

/// The box of `pts` read in the frame turned `angle` degrees, its first edge along the frame's first axis - the upright box itself where
/// the angle is level - so that a caption beside a turned feature is seated off its turned edge (feature 449 T189).
fn framed(pts: &[Pt], angle: f64) -> Vec<Pt> {
    // a level frame is turned()'s exact 0.0
    if angle == 0.0 {
        return corners(bbox(pts));
    }
    let (s, c) = (angle.to_radians().sin(), angle.to_radians().cos());
    let along: Vec<f64> = pts.iter().map(|p| p.0 * c + p.1 * s).collect();
    let across: Vec<f64> = pts.iter().map(|p| p.1 * c - p.0 * s).collect();
    let lo_hi = |xs: &[f64]| {
        xs[1..]
            .iter()
            .fold((xs[0], xs[0]), |(lo, hi), &x| (min(lo, x), max(hi, x)))
    };
    let ((u0, u1), (v0, v1)) = (lo_hi(&along), lo_hi(&across));
    let at = |u: f64, v: f64| (u * c - v * s, u * s + v * c);
    vec![at(u0, v0), at(u1, v0), at(u1, v1), at(u0, v1)]
}

/// Has this drawn shape a direction of its own, its first edge's: a `<rect>`, an outline [`square_cornered`] passes, or an ellipse of
/// unequal radii, whose axes a turned group turns - a circle alike, which an unequal scale draws as an ellipse - never a disc drawn round, whose
/// turned square box has no direction (the T188 claims round: a disc in a turned group, and a scatter's four-point kite, were named at an
/// angle; the plan review's round 3: an ellipse of unequal radii in a turned group was named level, and a circle scaled unequally too). The
/// radii are the drawn box's sides, which the reader keeps as the disc's outline. An outline of more corners, each square (an L-shaped
/// house), has its edges' direction too (feature 449 T189: a turned L-shaped house drawn as one outline was named level, where the same
/// house drawn as two rects took its angle).
///
/// Research:
///     a direction of its own - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a caption naming a turned feature is drawn at that feature's own angle and seated off its turned edge, and everything with no direction of its own is labeled level; a drawn rect and an outline of four square corners turn with their group, and an ellipse of unequal radii has its axes turned with it; a disc drawn round, an outline with a corner off square and a four-point kite have no direction
///     an outline of square corners - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: an outline of more than four corners, each square (an L-shaped house), has its edges' direction as a rectangle has - the page's map drawing convention ("A turned outline whose every corner is square has a direction of its own"), read so because the same house drawn as two rects takes its angle through its blocks, and naming it level drawn as one outline would repeat the rect-against-outline defect T188 fixed, and because 0242 gives a quarter-turned feature its direction by its edges ("it has a level edge of its own"); the simpler route, an L kept level, was priced and not taken for that inconsistency (feature 449 T189)
fn squared(s: &Shape) -> bool {
    if s.tag == "rect" {
        return true;
    }
    if matches!(s.tag.as_str(), "circle" | "ellipse") {
        // equal radii, within a turned outline's float slack, are a circle
        if !rectangular(&s.poly) {
            return false;
        }
        let (across, down) = (dist(s.poly[0], s.poly[1]), dist(s.poly[1], s.poly[2]));
        return (across - down).abs() > 1e-6 * max(across, down);
    }
    square_cornered(&s.poly)
}

/// How far from square a corner may stand and the outline still be a rectangle: within a degree, the cosine of the corner's angle under
/// the sine of one degree (feature 449 T188).
///
/// Research: a square corner - CONVENTION: a corner within 1 degree of square, so a turned rectangle drawn by hand to a tenth of a pixel is one
fn square_tol() -> f64 {
    1.0_f64.to_radians().sin()
}

/// Is this outline a rectangle - four corners, each square within [`square_tol`], a closing point repeating the first dropped - so that it
/// has a direction of its own, its first edge's, however it was drawn (feature 449 T188: a turned rectangle drawn as a polygon was named
/// level where the same `<rect>` took its angle)?
fn rectangular(poly: &[Pt]) -> bool {
    poly.len() - usize::from(poly.len() > 1 && poly[0] == poly[poly.len() - 1]) == 4
        && square_cornered(poly)
}

/// Is every corner of this outline square within [`square_tol`] - four corners or more, a closing point repeating the first dropped - a
/// rectangle or an L- or T-shaped house, whose edges all run along one turned frame and give it a direction of its own (feature 449 T189:
/// a turned L-shaped house drawn as one outline was named level, where the same house drawn as two rects took its angle)?
fn square_cornered(poly: &[Pt]) -> bool {
    let pts = if poly.len() > 1 && poly[0] == poly[poly.len() - 1] {
        &poly[..poly.len() - 1]
    } else {
        poly
    };
    let n = pts.len();
    if n < 4 {
        return false;
    }
    // each corner: the edges to the corner before and the corner after it, square where their cosine is under the tolerance
    (0..n).all(|k| {
        let (before, at, after) = (pts[(k + n - 1) % n], pts[k], pts[(k + 1) % n]);
        let back = (before.0 - at.0, before.1 - at.1);
        let on = (after.0 - at.0, after.1 - at.1);
        let (lb, lo) = (hypot(back.0, back.1), hypot(on.0, on.1));
        lb != 0.0 && lo != 0.0 && (back.0 * on.0 + back.1 * on.1).abs() / (lb * lo) <= square_tol()
    })
}

/// A turned feature's angle as its caption takes it: its outline's first edge's, level where the turn is a quarter, a half or three
/// quarters (within a millionth of a degree, the float slack of a turned outline's edge).
///
/// Research:
///     a quarter turn keeps a level caption - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a feature turned a quarter, a half or three quarters of a turn keeps a level caption
///     which edge gives the angle - CONVENTION: the outline's first edge, where a square-cornered outline has two perpendicular edges and 0242 does not say which a caption runs along (feature 449 T189)
fn turned(poly: &[Pt]) -> f64 {
    let angle = (poly[1].1 - poly[0].1)
        .atan2(poly[1].0 - poly[0].0)
        .to_degrees();
    if (angle - 90.0 * (angle / 90.0).round()).abs() < 1e-6 {
        0.0
    } else {
        angle
    }
}

/// Could a caption's block stand inside the box of what it names, within the box less the standard's gap on every side? The ORDER's
/// test, not a seat's: a caption that cannot is placed before those that can.
///
/// Research: a caption that fits inside - NONE: its widest line and its lines' height at their own faces against the box less the gap, an ordering test
#[must_use]
pub fn fits_inside(caps: &[&Shape], box_: BBox) -> bool {
    let (x0, y0, x1, y1) = box_;
    let w = caps
        .iter()
        .flat_map(|c| {
            c.lines
                .iter()
                .map(|ln| chars(ln) * c.size * char_w_of(c.attrs.as_ref(), ln, c.size))
        })
        .fold(f64::NAN, |m, v| if m.is_nan() || v > m { v } else { m });
    #[expect(clippy::cast_precision_loss, reason = "a caption's line count")]
    let h = sum(caps
        .iter()
        .map(|c| PITCH_EM * c.size * c.lines.len() as f64));
    let gap = 2.0 * CLEAR_EM * caps[0].size;
    w + gap <= x1 - x0 && h + gap <= y1 - y0
}

/// The layouts a caption of several texts may take, each its texts' lines: as declared, then each one-line text wrapped by the standard's
/// own rule to two lines, then three. A text the sheet already breaks into lines keeps its breaks.
///
/// # Panics
/// A text of no line, which the reader never makes (an empty text reads as one empty line).
///
/// Research: a several-text caption's wraps - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: one line before two, each text wrapped by the standard's rule
#[must_use]
pub fn wraps(caps: &[&Shape]) -> Vec<Vec<Vec<String>>> {
    let mut out: Vec<Vec<Vec<String>>> = Vec::new();
    for depth in 0..3 {
        let per: Vec<Vec<String>> = caps
            .iter()
            .map(|c| {
                if c.lines.len() > 1 {
                    c.lines.clone()
                } else {
                    let lays = layouts(&c.lines[0]);
                    lays[depth.min(lays.len() - 1)].clone()
                }
            })
            .collect();
        if !out.contains(&per) {
            out.push(per);
        }
    }
    out
}

/// A caption's lines as the placer measures them - all at the head's size and face - each line standing in for its own width.
fn as_head(caps: &[&Shape], cw: f64, per: &[Vec<String>]) -> Vec<String> {
    let head = caps[0];
    let mut out = Vec::new();
    for (k, (c, lines)) in caps.iter().zip(per).enumerate() {
        for ln in lines {
            if k == 0 {
                out.push(ln.clone());
            } else {
                let n =
                    chars(ln) * c.size * char_w_of(c.attrs.as_ref(), ln, c.size) / (head.size * cw);
                #[expect(
                    clippy::cast_possible_truncation,
                    clippy::cast_sign_loss,
                    reason = "a rounded character count"
                )]
                let n = max(1.0, round_int(n).unwrap_or(1.0)) as usize;
                out.push("x".repeat(n));
            }
        }
    }
    out
}

/// Where the center of each of a caption's `<text>` blocks stands in a placement: the texts stacked in order about the block's middle,
/// each taking its own lines at its OWN size's pitch, all turned with the caption.
#[must_use]
pub fn line_centers(p: &Placement, sizes: &[f64], counts: &[usize]) -> Vec<Pt> {
    #[expect(clippy::cast_precision_loss, reason = "a text's line count")]
    let heights: Vec<f64> = sizes
        .iter()
        .zip(counts)
        .map(|(s, &c)| PITCH_EM * s * c as f64)
        .collect();
    let a = p.angle.to_radians();
    let (cx, cy) = (p.x, p.y - CENTER_ABOVE_BASELINE_EM * sizes[0]);
    let mut top = -sum(heights.iter().copied()) / 2.0;
    let mut out = Vec::new();
    for h in heights {
        let dy = top + h / 2.0;
        out.push((cx - dy * a.sin(), cy + dy * a.cos()));
        top += h;
    }
    out
}

/// One sheet's seating context: its shapes, view, captions and what each names.
struct Sheet<'a> {
    shapes: &'a [Shape],
    view: BBox,
    skip: BTreeSet<usize>,
    owns: HashMap<usize, Vec<usize>>,
    named: BTreeSet<String>,
    bases: std::cell::RefCell<HashMap<(usize, usize), ObstacleIndex>>,
}

impl Sheet<'_> {
    fn own(&self, head: usize) -> Vec<&Shape> {
        self.owns[&head].iter().map(|&i| &self.shapes[i]).collect()
    }

    /// One caption placed against the others' placements, each with its caption's size: tried against each of its subjects in turn, the
    /// first free seat winning, else the least cost; `quick` tries the standard's seats only.
    ///
    /// A caption of several texts is tried in each of its [`wraps`], the first free one winning; where none clears it goes back to its
    /// declared lines, the cheapest seat of those (feature 449 T184: it kept the cheapest of all its wraps, where 0242 sends a caption
    /// that clears nowhere back to one line). A ground's name stays in its ground unless every seat there covers another name; an inside
    /// seat that covers a building gives way to a seat beside that covers no building - free, or on soft ink or a lane alone - and to
    /// nothing else (feature 449 T188: the break kept it over a free seat, and then over a seat on a lane alone).
    ///
    /// Research:
    ///     a ground's name stays in its ground - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a ground's name is set inside the ground it names, as an area caption is, unless every seat there covers another name; an inside seat covering a building - read off its cost, a drawn obstacle's or more, the placement carrying no more - is kept only while no seat beside covers no building - a free seat, or one on soft ink or a lane alone, under a drawn obstacle's cost - as a building is never covered while any other choice exists
    ///     a stranded several-text caption's wrap - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a wrap is taken only where it clears; if nothing clears, the caption goes back to its declared lines
    fn one(
        &self,
        idx: &[usize],
        others: &[(Placement, f64)],
        quick: bool,
    ) -> Result<Seated, Error> {
        let caps: Vec<&Shape> = idx.iter().map(|&i| &self.shapes[i]).collect();
        let head = caps[0];
        let own = self.own(idx[0]);
        let text = caps
            .iter()
            .flat_map(|c| c.lines.iter().map(String::as_str))
            .collect::<Vec<_>>()
            .join(" ");
        let cw = char_w_of(head.attrs.as_ref(), &head.text, head.size);
        let light = luma(head.get("fill")) > LIGHT;
        let mut best: Option<(Placement, Subject)> = None;
        let mut best_per: Vec<Vec<String>> = caps.iter().map(|c| c.lines.clone()).collect();
        // a ground's name holding an inside seat that covers a building, which only a seat covering no building may replace
        let mut kept_inside = false;
        for (k, sub) in subjects(&own, head.size).into_iter().enumerate() {
            let (index, lead) = self.context(idx[0], k, &sub, others, light);
            // a one-text caption is wrapped by the placer itself; a caption of several texts is tried in each of its wraps
            let tries = if caps.len() > 1 {
                wraps(&caps)
            } else {
                vec![best_per.clone()]
            };
            for (w, per) in tries.into_iter().enumerate() {
                let lines = (caps.len() > 1).then(|| as_head(&caps, cw, &per));
                let sizes: Option<Vec<f64>> = (caps.len() > 1).then(|| {
                    caps.iter()
                        .zip(&per)
                        .flat_map(|(c, ls)| ls.iter().map(|_| c.size))
                        .collect()
                });
                let ask = Ask {
                    frame: Some(self.view),
                    lines: lines.as_deref(),
                    char_w: cw,
                    leader_index: Some(&lead),
                    line_sizes: sizes.as_deref(),
                    extended: !quick,
                    ..Ask::default()
                };
                let p = place(&text, head.size, &sub, &index, &ask)?
                    .expect("a search that is not strict always seats");
                let free = p.cost == 0.0;
                // a wrap is taken only where it clears; with none clearing, the caption goes back to its declared lines (0242)
                // (and a ground's name keeping an inside seat over a building takes nothing after it but a seat covering no building)
                if (free || (w == 0 && (!kept_inside || p.cost < WEIGHT_OBSTACLE)))
                    && best.as_ref().is_none_or(|b| p.cost < b.0.cost)
                {
                    (best, best_per) = (Some((p, sub.clone())), per);
                }
                if free {
                    break;
                }
            }
            let b = &best.as_ref().expect("every caption has a subject").0;
            if b.cost == 0.0 {
                break;
            }
            if GROUND_KINDS.contains(&head.kind.as_str())
                && sub.kind == Kind::Area
                && b.position == "inside"
                && b.cost < WEIGHT_TEXT
            {
                // a ground's name stays in its ground unless every seat there covers another name (feature 286); an inside seat covering a
                // building (a drawn obstacle's cost or more) is kept only while no seat beside covers no building (0242, feature 449 T188)
                if b.cost < WEIGHT_OBSTACLE {
                    break;
                }
                kept_inside = true;
            }
        }
        let (best, sub) = best.expect("every caption has a subject");
        Ok((leader_to_ink(best, &own), best_per, sub))
    }

    /// A caption's two indexes against one of its subjects (the `k`th): what its block may not cover - the sheet classified for it, the
    /// ground drawn after it an obstacle to IT, every caption placed one with its own clearance and its leader - and what its leader may not
    /// cross.
    ///
    /// Research: each placed caption keeps its clearance - CONVENTION: a caption placed is an obstacle to the next at a caption's weight, keeping its own half-em clearance, and its leader too (features 267, 286)
    fn context(
        &self,
        head_at: usize,
        k: usize,
        sub: &Subject,
        others: &[(Placement, f64)],
        light: bool,
    ) -> (ObstacleIndex, ObstacleIndex) {
        let head = &self.shapes[head_at];
        let mut index = self
            .bases
            .borrow_mut()
            .entry((head_at, k))
            .or_insert_with(|| {
                let seen = Seen {
                    skip: &self.skip,
                    after: Some(head_at),
                    kind: &head.kind,
                    subject: Some(&sub.poly),
                    area: sub.kind == Kind::Area,
                    dark_inside: !light,
                    named: &self.named,
                };
                classify(self.shapes, self.view, &seen)
            })
            .clone();
        for (done, size) in others {
            // each placed caption keeps its own clearance too (`Obstacle::keep`)
            index.add(Obstacle {
                keep: CLEAR_EM * size,
                ..Obstacle::new(done.block.clone(), WEIGHT_TEXT)
            });
            if let Some((a, b)) = done.leader {
                index.add(Obstacle::new(band(a, b, 1.0), WEIGHT_TEXT));
            }
        }
        let held: Vec<&Placement> = others.iter().map(|(p, _)| p).collect();
        (
            index,
            leader_blockers(self.shapes, &self.skip, &held, sub, &self.owns[&head_at]),
        )
    }

    /// The tier a caption is placed in (feature 286): open ground's names first, then the names that must stand BESIDE their subject,
    /// then those that fit inside it, then the glyphs standing in a named ground.
    ///
    /// Research: the order captions are set - CONVENTION: the major area names before the small ones fill in around them, as a cartographer sets them (feature 286)
    fn order(&self, idx: &[usize], grounds: &[BBox]) -> i32 {
        let head = &self.shapes[idx[0]];
        let own = self.own(idx[0]);
        let (x0, y0, x1, y1) = box_of(self.shapes, &self.owns[&idx[0]]);
        let caps: Vec<&Shape> = idx.iter().map(|&i| &self.shapes[i]).collect();
        if subjects(&own, head.size)
            .iter()
            .any(|s| s.kind == Kind::Area)
            && fits_inside(&caps, (x0, y0, x1, y1))
        {
            return if GROUND_KINDS.contains(&head.kind.as_str()) {
                -1
            } else {
                1
            };
        }
        let in_ground = grounds.iter().any(|g| {
            g.0 <= x0
                && g.1 <= y0
                && x1 <= g.2
                && y1 <= g.3
                && (x1 - x0) * (y1 - y0) < (g.2 - g.0) * (g.3 - g.1)
        });
        if in_ground {
            3
        } else {
            0
        }
    }
}

/// Every caption on a sheet placed by the one placer, each avoiding the others: the caption's texts (by index), its placement and its
/// texts' lines as placed, in document order. The ORDER (feature 286): open ground's names first, then, points before areas, the names
/// that must stand BESIDE their subject, then those that fit inside it, then the glyphs standing in a named ground; each tier in document
/// order. Then [`repair`].
///
/// # Errors
/// A caption that names nothing, or a continuation with no caption before it - the Python's refusals, word for word.
///
/// # Panics
/// Never: every caption is seated before the list is read.
pub fn seat(shapes: &[Shape], view: BBox) -> Result<Vec<SeatedCaption>, Error> {
    let (sheet, caps_of) = Sheet::new(shapes, view)?;
    let grounds: Vec<BBox> = caps_of
        .iter()
        .filter(|idx| GROUND_KINDS.contains(&shapes[idx[0]].kind.as_str()))
        .map(|idx| box_of(shapes, &sheet.owns[&idx[0]]))
        .collect();
    let mut ordered: Vec<(i32, &Vec<usize>)> = caps_of
        .iter()
        .map(|idx| (sheet.order(idx, &grounds), idx))
        .collect();
    ordered.sort_by_key(|(tier, _)| *tier);
    let mut done: Vec<(usize, Seated)> = Vec::new();
    for (_, idx) in ordered {
        let others: Vec<(Placement, f64)> = done
            .iter()
            .map(|(k, (p, _, _))| (p.clone(), shapes[*k].size))
            .collect();
        done.push((idx[0], sheet.one(idx, &others, false)?));
    }
    let by_head: HashMap<usize, &Vec<usize>> = caps_of.iter().map(|idx| (idx[0], idx)).collect();
    let boxes: BTreeMap<usize, BBox> = done
        .iter()
        .map(|(k, _)| (*k, box_of(shapes, &sheet.owns[k])))
        .collect();
    let sizes: BTreeMap<usize, f64> = done.iter().map(|(k, _)| (*k, shapes[*k].size)).collect();
    repair(&mut done, &boxes, &sizes, &|k, rest, quick| {
        sheet.one(by_head[&k], rest, quick)
    })?;
    Ok(caps_of
        .iter()
        .map(|idx| {
            let (p, per, sub) = done
                .iter()
                .find(|(k, _)| *k == idx[0])
                .map(|(_, s)| s.clone())
                .expect("every caption was seated");
            (idx.clone(), p, per, sub)
        })
        .collect())
}

/// How a drawn caption stands against the rules the placer seats by (the port's comparison asks it of each side's seats, feature 449
/// T151): its block off the sheet, its gap past the hug from what it names, what it covers by the placer's own measure against every
/// other caption as drawn - the cost, and whether any of it is an overlap the placer never draws while another seat exists - and whether it
/// has a leader exactly where the standard draws one.
#[derive(Debug, Clone, PartialEq)]
pub struct Standing {
    pub off_sheet: bool,
    pub hug_gap: f64,
    pub cost: f64,
    pub overlap: bool,
    pub leader_as_ruled: bool,
}

/// Each seated caption's [`Standing`], every other caption as drawn around it.
///
/// Research: a seat's standing - NONE: the placer's own rules asked again of a finished sheet, deciding nothing
///
/// # Errors
/// A caption that names nothing, as [`seat`] refuses it.
pub fn standing(
    shapes: &[Shape],
    view: BBox,
    rows: &[SeatedCaption],
) -> Result<Vec<Standing>, Error> {
    let (sheet, _) = Sheet::new(shapes, view)?;
    let mut out = Vec::new();
    for (i, (idx, p, _, sub)) in rows.iter().enumerate() {
        let head = &shapes[idx[0]];
        let others: Vec<(Placement, f64)> = rows
            .iter()
            .enumerate()
            .filter(|(j, _)| *j != i)
            .map(|(_, r)| (r.1.clone(), shapes[r.0[0]].size))
            .collect();
        // the subject found by what it is seated off - its kind, outline and angle - not by its ink, a disc's sampled curve, which the
        // Python's floats may give a bit apart (feature 449 T192)
        let k = subjects(&sheet.own(idx[0]), head.size)
            .iter()
            .position(|s| {
                s.kind == sub.kind && s.poly == sub.poly && s.angle.to_bits() == sub.angle.to_bits()
            })
            .unwrap_or(usize::MAX);
        let (index, lead) = sheet.context(idx[0], k, sub, &others, luma(head.get("fill")) > LIGHT);
        let text = idx
            .iter()
            .flat_map(|&c| shapes[c].lines.iter().map(String::as_str))
            .collect::<Vec<_>>()
            .join(" ");
        let (cost, overlap) = judge(&text, head.size, sub, &index, Some(&lead), p);
        let point = sub.kind == Kind::Point;
        out.push(Standing {
            off_sheet: !in_frame(&p.block, Some(view)),
            hug_gap: if sub.kind == Kind::Area {
                0.0
            } else {
                hug_gap(
                    &p.block,
                    referent_box(sub, if point { &sub.poly } else { &p.block }),
                )
            },
            cost,
            overlap,
            leader_as_ruled: p.leader.is_some()
                == (p.ring >= LEADERLESS_RINGS && sub.kind != Kind::Area),
        });
    }
    Ok(out)
}

impl<'a> Sheet<'a> {
    /// The sheet's captions and what each names, every declaration read in document order (the first refusal the Python's).
    fn new(shapes: &'a [Shape], view: BBox) -> Result<(Self, Vec<Vec<usize>>), Error> {
        let caps_of = captions_of(shapes)?;
        let skip: BTreeSet<usize> = caps_of.iter().flatten().copied().collect();
        let mut per_group: HashMap<usize, usize> = HashMap::new();
        for idx in &caps_of {
            *per_group.entry(shapes[idx[0]].group).or_default() += 1;
        }
        let mut owns = HashMap::new();
        for idx in &caps_of {
            let head = &shapes[idx[0]];
            owns.insert(
                idx[0],
                declared_parts(head, shapes, per_group[&head.group] == 1)?,
            );
        }
        let named = caps_of
            .iter()
            .map(|idx| shapes[idx[0]].kind.clone())
            .collect();
        Ok((
            Sheet {
                shapes,
                view,
                skip,
                owns,
                named,
                bases: std::cell::RefCell::default(),
            },
            caps_of,
        ))
    }
}

/// The pair re-placed with `bi` lifted for `ai`, where the two together then cover less; None where the lifted caption is no cheaper or
/// the pair no better.
///
/// Research: a stranded caption's repair - CONVENTION: a stranded caption re-placed with one neighbor lifted, the pair kept only where the two together cover less (feature 286)
fn lift(
    done: &[(usize, Seated)],
    ai: usize,
    bi: usize,
    sizes: &BTreeMap<usize, f64>,
    one: One<'_>,
) -> Result<Option<(Seated, Seated)>, Error> {
    let (a, b) = (done[ai].0, done[bi].0);
    let rest: Vec<(Placement, f64)> = done
        .iter()
        .filter(|(k, _)| *k != a && *k != b)
        .map(|(k, (p, _, _))| (p.clone(), sizes[k]))
        .collect();
    let pa = one(a, &rest, true)?;
    if pa.0.cost >= done[ai].1 .0.cost {
        return Ok(None);
    }
    let mut with_a = rest;
    with_a.push((pa.0.clone(), sizes[&a]));
    let pb = one(b, &with_a, false)?;
    let better = pa.0.cost + pb.0.cost < done[ai].1 .0.cost + done[bi].1 .0.cost;
    Ok(better.then_some((pa, pb)))
}

/// One caption placed against the others (`one(key, others, quick)`).
pub type One<'a> = &'a dyn Fn(usize, &[(Placement, f64)], bool) -> Result<Seated, Error>;

/// The greedy pass's repair (feature 286): each caption left covering ink is re-placed with one neighbor lifted - a caption whose block
/// lies within [`REPAIR`] ems plus its own length of the subject's box - and the neighbor re-placed after it; the pair is kept where the two
/// together cover less. `quick` tries the standard's seats only for the lifted caption.
///
/// Research: caption repair reach - CONVENTION: a neighbor within 2 ems of a stranded caption's subject (plus the caption's length) is lifted to free a seat; a calibration of the placer.
///
/// # Errors
/// A caption's search that refused.
pub fn repair(
    done: &mut [(usize, Seated)],
    boxes: &BTreeMap<usize, BBox>,
    sizes: &BTreeMap<usize, f64>,
    one: One<'_>,
) -> Result<(), Error> {
    for ai in 0..done.len() {
        let a = done[ai].0;
        if done[ai].1 .0.cost == 0.0 {
            continue;
        }
        let block = done[ai].1 .0.block.clone();
        let reach = REPAIR * sizes[&a] + max(dist(block[0], block[1]), dist(block[1], block[2]));
        let own_box = corners(boxes[&a]);
        let near: Vec<usize> = (0..done.len())
            .filter(|&bi| bi != ai && box_gap(&done[bi].1 .0.block, &own_box) <= reach)
            .collect();
        for bi in near {
            if let Some((pa, pb)) = lift(done, ai, bi, sizes, one)? {
                (done[ai].1, done[bi].1) = (pa, pb);
                break;
            }
        }
    }
    Ok(())
}
