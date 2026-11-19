//! The declared captions of a hand sheet as the placer seats them (feature 449 T202): each caption's line elements (a `<text>` and the
//! `data-cont` lines after it), what it names (its `data-names` ids, else the drawn shapes of the tagged group it stands in), its block as
//! drawn, and the frame its feature sets - the feature's box in that frame and the angle the caption takes. Read once a sheet, from the
//! shapes the sheet reader gives ([`crate::labels::hand_sheet::read_sheet`]).
//!
//! Research: the declared captions - NONE: the sheet's declarations read as the sheet states them (docs/buildings.md, feature 340), deciding nothing about where a caption stands

use std::collections::{BTreeMap, BTreeSet};

use super::geom::{bbox, dist, turn, Bx, Pt};
use super::Shape;
use crate::work_counts::count;

/// A line's height as the sheet draws it, in ems: the caption writer stands its lines this far apart
/// (and the writer before T202, `labels/svg.rs`'s `caption_svg`, deleted with the old placer), so the block a caption is seated as is the block it is drawn as.
///
/// Research: the line pitch - CONVENTION: 1.15 em a line, the pitch the caption writer draws at
pub const PITCH_EM: f64 = 1.15;

/// The share of a line's box above its baseline, in ems: the writer centers a line 0.275 em above its baseline, half the 1.15 em pitch
/// below its top, so a line's baseline stands 0.85 em below its top.
///
/// Research: the baseline in its line - CONVENTION: 0.85 em below the line's top, the caption writer's centering
pub const BASELINE_EM: f64 = 0.85;

/// The kinds that are a way, a road's or a stream's: crossable at half a building's weight, and named along their own bearing.
///
/// Research: the ways - CONVENTION: roads, approaches, footpaths, rivers and revetments are ways (research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: "A lane or a ditch may be crossed"), the derivation's assumption 1
pub const WAY_KINDS: [&str; 5] = ["road", "approach", "footpath", "river", "revetment"];

/// One line element of a caption: its shape's index, its lines, its letter size and its width as drawn.
#[derive(Clone, Debug, PartialEq)]
pub struct Elem {
    pub shape: usize,
    pub lines: Vec<String>,
    pub size: f64,
    pub width: f64,
}

/// A declared caption: its elements (the head first), what it names, its feature's frame and box in it, and its block.
#[derive(Clone, Debug, PartialEq)]
pub struct Caption {
    pub elems: Vec<Elem>,
    /// The indexes of the drawn shapes it names.
    pub parts: Vec<usize>,
    /// The angle of the feature's frame, and so of the caption, in degrees (never upside down).
    pub angle: f64,
    /// The feature's box in its own frame (sheet coordinates turned back by `angle`); `None` where it names nothing drawn.
    pub fbox: Option<Bx>,
    /// The feature's box on the sheet.
    pub fsheet: Option<Bx>,
    pub w: f64,
    pub h: f64,
    /// The usual gap: half the caption's letter height.
    pub gap: f64,
    /// Does it name open ground (a court, a garden)?
    pub ground: bool,
    /// The part that holds all the others, the outline it is named on (`None` where the parts are loose, or only strokes), and its box
    /// in the feature's frame.
    pub holder: Option<(usize, Bx)>,
    /// The paint order of its first line element - or, where it is written at its group's end, of the group's last element.
    pub at: usize,
    /// Loose parts' outlines, the nearest the middle of all first: each part's index, and its box in the feature's frame and on the sheet.
    pub members: Vec<(usize, Bx, Bx)>,
    /// Where it is written: at its tagged group's end (the byte of the group's closing tag), or `None` in place.
    pub move_to: Option<usize>,
    /// The paint order of its tagged group and of the group's last element: what is drawn within the group.
    pub subtree: Option<(usize, usize)>,
}

impl Caption {
    /// The caption's words on one line, as declared.
    #[must_use]
    pub fn text(&self) -> String {
        self.elems
            .iter()
            .flat_map(|e| e.lines.iter().map(String::as_str))
            .collect::<Vec<_>>()
            .join(" ")
    }

    /// The head element's shape index.
    #[must_use]
    pub fn head(&self) -> usize {
        self.elems[0].shape
    }

    /// Can its words be cut across lines? Only a caption declared as one line of one element, of two words or more.
    ///
    /// Research: what may be cut - CONVENTION: only a caption declared as one line of one element, holding a space, is cut across lines, and only between words (0242's "words are never broken"); a caption the sheet already declares on several lines or elements keeps the lines it was given, since its author chose them and the page says nothing of re-cutting them
    #[must_use]
    pub fn cuttable(&self) -> bool {
        self.elems.len() == 1
            && self.elems[0].lines.len() == 1
            && self.elems[0].lines[0].contains(' ')
    }
}

/// The block of a set of elements: its width (the widest line) and height (each line at its pitch).
#[must_use]
pub fn block_of(elems: &[Elem]) -> (f64, f64) {
    elems.iter().fold((0.0_f64, 0.0), |(w, h), e| {
        #[expect(clippy::cast_precision_loss, reason = "a caption's line count")]
        let n = e.lines.len() as f64;
        (w.max(e.width), h + n * PITCH_EM * e.size)
    })
}

/// Is this text a caption the sheet declares - one with no seat of its own, or one naming its drawn shapes - rather than sheet furniture
/// (a title, a scale bar's figure)?
///
/// Research: a declaration - CONVENTION: a `<text>` with `data-names`, or with no `x` inside a tagged group, is a caption the placer seats; one written at its own `x` names nothing and is furniture (feature 340)
#[must_use]
pub fn is_declared(s: &Shape) -> bool {
    if s.tag != "text" {
        return false;
    }
    let seated = s.attrs.as_ref().is_some_and(|a| a.get("x").is_some());
    s.cont || !s.names.is_empty() || (!seated && !s.kind.is_empty() && s.kind != "-")
}

/// A text element's drawn width: its block (as the reader measured it) turned back by its frame's angle.
fn drawn_width(s: &Shape) -> f64 {
    let ang = crate::labels::hand_sheet::read::angle(s.frame);
    let back: Vec<Pt> = s.poly.iter().map(|&p| turn(p, -ang)).collect();
    let b = bbox(&back);
    b.2 - b.0
}

fn elem(i: usize, s: &Shape) -> Elem {
    Elem {
        shape: i,
        lines: s.lines.clone(),
        size: s.size,
        width: drawn_width(s),
    }
}

/// Every declared caption of the sheet, in declaration order, each with what it names resolved: a `data-cont` line joins the caption
/// before it; parts are looked up once, by the ids or groups some caption names (`name_lookup`, one a part found).
///
/// Research:
///     the usual gap - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: half the height of the caption's lettering (its head line's letter size), the page's calibration
///     open ground - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: fields, scrub, groves and open ground are not in the way at all - a caption is marked as naming open ground when any of its parts is a ground kind (`GROUND_KINDS`), the mark the placer's stance reads
///     a holder before loose parts - CONVENTION: where one outline holds the rest (`holder`) the caption is named on that outline, else beside the box of all its parts, and its parts are not tried one by one; only where none holds them are they loose parts (`members`)
#[must_use]
pub fn declared(shapes: &[Shape]) -> Vec<Caption> {
    let mut caps: Vec<(Vec<Elem>, Vec<String>, usize)> = Vec::new();
    for (i, s) in shapes.iter().enumerate() {
        if !is_declared(s) {
            continue;
        }
        if s.cont {
            if let Some(last) = caps.last_mut() {
                last.0.push(elem(i, s));
            }
            continue;
        }
        caps.push((vec![elem(i, s)], s.names.clone(), s.group));
    }
    let wanted_ids: BTreeSet<&str> = caps
        .iter()
        .flat_map(|c| c.1.iter().map(String::as_str))
        .collect();
    let wanted_groups: BTreeSet<usize> = caps
        .iter()
        .filter(|c| c.1.is_empty())
        .map(|c| c.2)
        .collect();
    let mut by_id: BTreeMap<&str, Vec<usize>> = BTreeMap::new();
    let mut by_group: BTreeMap<usize, Vec<usize>> = BTreeMap::new();
    for (i, s) in shapes.iter().enumerate() {
        if s.tag == "text" || s.leader || s.poly.is_empty() {
            continue;
        }
        for id in s.ids.iter().filter(|id| wanted_ids.contains(id.as_str())) {
            count("name_lookup@declared", 1);
            by_id.entry(id.as_str()).or_default().push(i);
        }
        if s.group != 0 && wanted_groups.contains(&s.group) {
            count("name_lookup@declared", 1);
            by_group.entry(s.group).or_default().push(i);
        }
    }
    caps.into_iter()
        .map(|(elems, names, group)| {
            let mut parts: Vec<usize> = if names.is_empty() {
                by_group.get(&group).cloned().unwrap_or_default()
            } else {
                names
                    .iter()
                    .flat_map(|n| by_id.get(n.as_str()).cloned().unwrap_or_default())
                    .collect()
            };
            parts.sort_unstable();
            parts.dedup();
            let angle = feature_angle(shapes, &parts);
            let fbox = (!parts.is_empty()).then(|| {
                let pts: Vec<Pt> = parts
                    .iter()
                    .flat_map(|&p| shapes[p].poly.iter().map(|&q| turn(q, -angle)))
                    .collect();
                bbox(&pts)
            });
            let fsheet = (!parts.is_empty()).then(|| {
                bbox(
                    &parts
                        .iter()
                        .flat_map(|&p| shapes[p].poly.iter().copied())
                        .collect::<Vec<_>>(),
                )
            });
            let (w, h) = block_of(&elems);
            let gap = elems[0].size / 2.0;
            let ground = parts
                .iter()
                .any(|&p| super::index::GROUND_KINDS.contains(&shapes[p].kind.as_str()));
            let holder = holder(shapes, &parts, angle);
            let at = elems.iter().map(|e| shapes[e.shape].at).min().unwrap_or(0);
            let members = if holder.is_none() {
                members(shapes, &parts, angle)
            } else {
                Vec::new()
            };
            Caption {
                elems,
                parts,
                angle,
                fbox,
                fsheet,
                w,
                h,
                gap,
                ground,
                holder,
                at,
                members,
                move_to: None,
                subtree: None,
            }
        })
        .collect()
}

/// A loose feature's outlines, nearest the middle of them all first: each part's box in the feature's frame and on the sheet (none for
/// a feature of fewer than two outlines - a road, a wall - which is named beside the box around it).
///
/// Research: a member of loose parts - DEVIATION research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: the page seats a block named among loose parts beside the smallest box holding them all; this placer, for two or more closed outlines no one of which holds the rest, names the caption on one of the parts where it fits (a house of two blocks named on one), else seats it beside one, the nearest the middle of them all first, a leader past twice the gap tying it to the nearest part - because the box of parts scattered across a sheet (a compound's fire-water tubs) spans the compound, and a name beside it names nothing
#[must_use]
pub fn members(shapes: &[Shape], parts: &[usize], angle: f64) -> Vec<(usize, Bx, Bx)> {
    let closed: Vec<usize> = parts
        .iter()
        .copied()
        .filter(|&p| !shapes[p].line && shapes[p].poly.len() >= 3)
        .collect();
    if closed.len() < 2 {
        return Vec::new();
    }
    let all = bbox(
        &closed
            .iter()
            .flat_map(|&p| shapes[p].poly.iter().copied())
            .collect::<Vec<_>>(),
    );
    let m = (f64::midpoint(all.0, all.2), f64::midpoint(all.1, all.3));
    let mut out: Vec<(f64, usize, Bx, Bx)> = closed
        .iter()
        .map(|&p| {
            let sb = bbox(&shapes[p].poly);
            let lb = bbox(
                &shapes[p]
                    .poly
                    .iter()
                    .map(|&q| turn(q, -angle))
                    .collect::<Vec<_>>(),
            );
            (
                dist((f64::midpoint(sb.0, sb.2), f64::midpoint(sb.1, sb.3)), m),
                p,
                lb,
                sb,
            )
        })
        .collect();
    out.sort_by(|a, b| a.0.total_cmp(&b.0));
    out.into_iter().map(|(_, p, lb, sb)| (p, lb, sb)).collect()
}

/// How much of the box around all a feature's parts its largest outline must cover to hold the others.
///
/// Research: an outline holding the others - GUESS research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: half; the page names "an outline holding the others" but gives no measure, and a building's step or porch drawn a few feet past its walls (Hoshigaoka's hall, 6 px of a 102 px box) must not make it loose parts, while scattered tubs (a hundredth of their box) and a barge with its mooring lines (under half) are
pub const HOLDER_SHARE: f64 = 0.5;

/// The outline a caption is named on: the largest closed part, where its box covers at least [`HOLDER_SHARE`] of the box around all the
/// parts (one outline, or one holding the rest), with its box in the feature's frame.
///
/// Research: loose parts - CONVENTION: 0242 seats a block named among loose parts, or an outline holding the others, beside the smallest box holding them all (its turned-feature rule); this placer names a feature whose one outline holds its parts on itself, reading 0242's "a feature large enough to hold its name is named on itself", else beside the box of all its parts - and a feature of fewer than two closed outlines beside that box too; two or more loose outlines are seated by `members`' rule, on or beside one part - never on the bare ground between loose parts
#[must_use]
pub fn holder(shapes: &[Shape], parts: &[usize], angle: f64) -> Option<(usize, Bx)> {
    let area = |b: Bx| (b.2 - b.0) * (b.3 - b.1);
    let big = parts
        .iter()
        .copied()
        .filter(|&p| !shapes[p].line && shapes[p].poly.len() >= 3)
        .max_by(|&a, &b| area(bbox(&shapes[a].poly)).total_cmp(&area(bbox(&shapes[b].poly))))?;
    let hb = bbox(&shapes[big].poly);
    let union = bbox(
        &parts
            .iter()
            .flat_map(|&p| shapes[p].poly.iter().copied())
            .collect::<Vec<_>>(),
    );
    (area(hb) >= HOLDER_SHARE * area(union)).then(|| {
        (
            big,
            bbox(
                &shapes[big]
                    .poly
                    .iter()
                    .map(|&q| turn(q, -angle))
                    .collect::<Vec<_>>(),
            ),
        )
    })
}

/// A turned outline's angle in degrees as its caption reads it: [`upright`], and a quarter, half or three quarters of a turn read level
/// (a line's bearing is [`upright`] alone).
///
/// Research:
///     never upside down - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: where the feature's angle would set the words upside down, the caption is turned a half turn
///     quarter turns read level - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a feature turned a quarter, a half or three quarters of a turn keeps a level caption - a turned outline, which has a level edge of its own; never a road's bearing
///     a whole turn's tolerance - NONE: 0.01 degree, a rounding of the drawn angle
#[must_use]
pub fn readable(deg: f64) -> f64 {
    let a = upright(deg);
    let off_quarter = (a.rem_euclid(90.0)).min(90.0 - a.rem_euclid(90.0));
    if off_quarter < 0.01 {
        0.0
    } else {
        a
    }
}

/// An angle in degrees turned the right way up: within (-90, 90], so the words are never upside down - a line's bearing, which keeps
/// even a quarter turn (a road has no level edge of its own for a level caption to line up with).
///
/// Research: never upside down - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: where the feature's angle would set the words upside down, the caption is turned a half turn; nothing else changes its angle
#[must_use]
pub fn upright(deg: f64) -> f64 {
    let a = deg.rem_euclid(180.0);
    if a > 90.0 {
        a - 180.0
    } else {
        a
    }
}

/// The direction of an edge, in degrees.
fn bearing(a: Pt, b: Pt) -> f64 {
    (b.1 - a.1).atan2(b.0 - a.0).to_degrees()
}

/// Does every corner of a closed outline turn square?
fn square_cornered(poly: &[Pt]) -> bool {
    let n = poly.len();
    n >= 4
        && (0..n).all(|i| {
            let (a, b, c) = (poly[i], poly[(i + 1) % n], poly[(i + 2) % n]);
            let dot = (b.0 - a.0) * (c.0 - b.0) + (b.1 - a.1) * (c.1 - b.1);
            dot.abs() <= 1e-3 * dist(a, b) * dist(b, c)
        })
}

/// The angle a caption takes from what it names.
///
/// Research:
///     a turned outline's direction - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a turned outline whose every corner is square, or a turned ellipse of unequal radii, has a direction of its own; among loose parts the largest block's angle is taken
///     a line's bearing - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a road's name follows the road, at its bearing exactly - a north-south road's turned a quarter, the quarter-turn rule being a turned outline's - and never upside down
///     the longest stretch - DEVIATION research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: the page takes a road's bearing from the stretch its caption is seated against; here it is taken once a caption, before it is seated, from the longest stretch of the first way among its parts, and the caption is seated in that frame - a frame read from the seat would depend on the seat it frames, and the eight places of a frame are what the search ranks
///     the rest level - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: everything with no direction of its own is labeled level
#[must_use]
pub fn feature_angle(shapes: &[Shape], parts: &[usize]) -> f64 {
    let closed = parts
        .iter()
        .map(|&p| &shapes[p])
        .filter(|s| !s.line && s.poly.len() >= 4)
        .max_by(|a, b| {
            let (x, y) = (bbox(&a.poly), bbox(&b.poly));
            ((x.2 - x.0) * (x.3 - x.1)).total_cmp(&((y.2 - y.0) * (y.3 - y.1)))
        });
    if let Some(s) = closed {
        let disc = s.tag == "circle" || s.tag == "ellipse";
        let round = disc && (dist(s.poly[0], s.poly[1]) - dist(s.poly[1], s.poly[2])).abs() < 1e-6;
        if !round && square_cornered(&s.poly) {
            return readable(bearing(s.poly[0], s.poly[1]));
        }
        return 0.0;
    }
    let way = parts
        .iter()
        .map(|&p| &shapes[p])
        .find(|s| s.line && WAY_KINDS.contains(&s.kind.as_str()));
    way.and_then(|s| {
        super::geom::path(&s.poly).max_by(|x, y| dist(x.0, x.1).total_cmp(&dist(y.0, y.1)))
    })
    .map_or(0.0, |(a, b)| upright(bearing(a, b)))
}
