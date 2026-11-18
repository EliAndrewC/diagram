//! What a caption may and may not cover, indexed once (feature 449 T151, `labels/obstacles.py` whole; feature 266, FR-006, FR-009,
//! FR-014). Built ONCE per label phase and asked per candidate - the engine's standing rule for a keep-out that does not change during a
//! search (constitution X clause 15). Each placed caption is added as it lands, so the next caption sees it. The index prunes; the exact
//! polygon tests decide - the Python's tests in its order, so a verdict here is the Python's.
//!
//! Research: obstacle index - NONE: indexing and exact geometry

#![expect(
    clippy::similar_names,
    reason = "the Python's names, kept so each line reads against its original (x0 and x1, bx0 and by0)"
)]

use std::collections::{HashMap, HashSet};

use super::geom::{
    bbox, box_gap, centroid, dist, inside, least, poly_gap, poly_seg_gap, seg_dist, BBox, Pt,
};
use super::standard::{WAY_NOTCH, WEIGHT_WAY};
use crate::py::max;
use crate::work_counts::count;

/// The civic groups: when a caption's SUBJECT is a named civic building, every other NAMED civic building keeps its full weight; a
/// caption whose subject is not is waived onto its group like any other (FR-014).
///
/// Research: named civic buildings - research/questions/0243-what-labels-may-cover-and-how-districts-are-named-on-town-and-city-maps.drawing.html: ministry, governor and temple keep full weight against another civic caption
pub const CIVIC_GROUPS: [&str; 3] = ["ministry", "governor", "temple"];

/// The words that name a caption group, where a group is named by more than its own word (feature 328 wave 5): the samurai houses and
/// estates the samurai caption's alone, so a merchant's estate's name covers none of them (feature 449 T188).
///
/// Research: a funerary caption covers the funerary structures - research/questions/0243-what-labels-may-cover-and-how-districts-are-named-on-town-and-city-maps.drawing.html: a graveyard, cremation, mausoleum or ossuary caption may cover any of the funerary structures, and a samurai caption the samurai houses and estates
///     a shrine caption may cover the temples - research/questions/0243-what-labels-may-cover-and-how-districts-are-named-on-town-and-city-maps.drawing.html: 0243 §11
///     a guard or inspection caption may cover the gate's posts - research/questions/0243-what-labels-may-cover-and-how-districts-are-named-on-town-and-city-maps.drawing.html: 0243 §9
pub const GROUP_WORDS: [(&str, &[&str]); 4] = [
    (
        "funerary",
        &[
            "funerary",
            "cemetery",
            "graveyard",
            "cremation",
            "mausoleum",
            "ossuary",
        ],
    ),
    ("estate", &["samurai"]),
    ("temple", &["temple", "shrine"]),
    ("gate", &["gate", "guard", "inspection"]),
];

/// Does a caption's lower-cased text `words` name the caption `group` (its own word, or one of [`GROUP_WORDS`])? A word is named WHOLE
/// ([`caption_words`]): irrigated fields name no gate, though their letters hold one, and the ministries name the ministry, which no
/// substring of theirs did (feature 449 T188: the words were matched as substrings).
///
/// Research: a caption's wording names its group - research/questions/0243-what-labels-may-cover-and-how-districts-are-named-on-town-and-city-maps.drawing.html: a caption's own wording says which groups of buildings it may cover - a group named by its own word, whole, where no list of words is given for it (a flophouse caption the flophouses, a ministry's name the ministries), else by one of its words, whole
#[must_use]
pub fn names_group(group: Option<&str>, words: &str) -> bool {
    let Some(group) = group.filter(|g| !g.is_empty()) else {
        return false;
    };
    let own = [group];
    let ws: &[&str] = GROUP_WORDS
        .iter()
        .find(|(g, _)| *g == group)
        .map_or(&own, |(_, ws)| ws);
    let said = caption_words(words);
    ws.iter().any(|w| {
        let plural = w
            .strip_suffix('y')
            .map_or_else(|| (*w).to_owned(), |stem| format!("{stem}ies"));
        [(*w).to_owned(), format!("{w}s"), format!("{w}es"), plural]
            .iter()
            .any(|form| said.contains(form.as_str()))
    })
}

/// A caption's words, whole: its runs of letters, any other character a break (`guard-house` is `guard` and `house`, `temple's` `temple`
/// and `s`). A group's word is named by itself or its plural - `s`, `es`, a `y` turned `ies` (`ministries`).
///
/// Research: a caption's words - CONVENTION: a word is a run of letters, named by itself or its plural, as 0243's examples speak of a flophouse caption and the flophouses
#[must_use]
pub fn caption_words(words: &str) -> HashSet<&str> {
    words
        .split(|c: char| !c.is_ascii_lowercase())
        .filter(|w| !w.is_empty())
        .collect()
}

/// How much farther than a caption's own subject a neighbor may stand and still claim the caption (labels L6, the ASSOCIATION): a tie
/// counts, and this is float slack on the tie only.
pub const ASSOCIATION_TIE: f64 = 1e-6;

/// The grid's cell, in drawing units: a pruning grain, not a rule.
pub const CELL: f64 = 32.0;

/// A drawn thing a caption is scored against (the Python's `Obstacle`, its fields and their meaning the same): `weight` on Esri's 0-1,000
/// scale; `group` the caption word that may cover it; `named` a civic building with a name of its own; `inner` ink inside a subject its
/// caption must still avoid; `keep` a gap the obstacle asks for itself; `soft` ink a caption may be set on when no seat is free; `circle`
/// `(x, y, r)` a disc measured as a disc, `poly` then its box.
#[derive(Debug, Clone, PartialEq, Default)]
pub struct Obstacle {
    pub poly: Vec<Pt>,
    pub weight: f64,
    pub group: Option<String>,
    pub named: bool,
    pub inner: bool,
    pub keep: f64,
    pub soft: bool,
    pub circle: Option<(f64, f64, f64)>,
}

impl Obstacle {
    /// An obstacle of `poly` at `weight`, every other field its default.
    #[must_use]
    pub fn new(poly: Vec<Pt>, weight: f64) -> Self {
        Self {
            poly,
            weight,
            ..Self::default()
        }
    }
}

/// A lane, road, stream or ditch: a polyline a caption may cross at [`WEIGHT_WAY`], with its drawn half-width; a `soft` way may be crossed
/// when no seat is free.
#[derive(Debug, Clone, PartialEq, Default)]
pub struct Way {
    pub pts: Vec<Pt>,
    pub half_width: f64,
    pub soft: bool,
}

type Cell = (i64, i64);

/// The cells a box covers. A coordinate the sheet reader refused as no finite number never reaches here (`hand_sheet::read`).
#[expect(
    clippy::cast_possible_truncation,
    reason = "a floored finite drawing coordinate over the cell, far inside i64"
)]
fn cells(b: BBox) -> Vec<Cell> {
    let (x0, y0, x1, y1) = b;
    let f = |v: f64| (v / CELL).floor() as i64;
    let mut out = Vec::new();
    for i in f(x0)..=f(x1) {
        for j in f(y0)..=f(y1) {
            out.push((i, j));
        }
    }
    out
}

/// Obstacles and ways bucketed by grid cell.
#[derive(Debug, Clone, Default)]
pub struct ObstacleIndex {
    pub obstacles: Vec<Obstacle>,
    boxes: Vec<BBox>,
    level: Vec<bool>,
    pub ways: Vec<Way>,
    ob: HashMap<Cell, Vec<usize>>,
    segs: HashMap<Cell, Vec<(usize, usize, Pt, Pt)>>,
    seg_boxes: Vec<BBox>,
}

/// What a caption is: its subject's outline (absent for a line), its words, and whether its subject is a named civic building.
#[derive(Debug, Clone, Copy)]
pub struct Asker<'a> {
    pub subject: Option<&'a [Pt]>,
    pub text: &'a str,
    pub civic: bool,
}

impl ObstacleIndex {
    /// An index of `obstacles` and `ways`.
    #[must_use]
    pub fn new(obstacles: Vec<Obstacle>, ways: Vec<Way>) -> Self {
        let mut out = Self::default();
        for o in obstacles {
            out.add(o);
        }
        for w in ways {
            out.add_way(w);
        }
        out
    }

    /// File an obstacle in every cell its box, grown by its own `keep`, covers.
    pub fn add(&mut self, o: Obstacle) {
        let i = self.obstacles.len();
        let b = bbox(&o.poly);
        self.boxes.push(b);
        self.level.push(level_rect(&o.poly));
        let (bx0, by0, bx1, by1) = b;
        for c in cells((bx0 - o.keep, by0 - o.keep, bx1 + o.keep, by1 + o.keep)) {
            self.ob.entry(c).or_default().push(i);
        }
        self.obstacles.push(o);
    }

    /// File each segment of a way in every cell its box, grown by the way's half-width and the notch, covers.
    pub fn add_way(&mut self, w: Way) {
        let wid = self.ways.len();
        let reach = w.half_width + WAY_NOTCH;
        for pair in w.pts.windows(2) {
            let (a, b) = (pair[0], pair[1]);
            let sid = self.seg_boxes.len();
            let (lx, ly) = (crate::py::min(a.0, b.0), crate::py::min(a.1, b.1));
            let (hx, hy) = (max(a.0, b.0), max(a.1, b.1));
            self.seg_boxes.push((lx, ly, hx, hy));
            for c in cells((lx - reach, ly - reach, hx + reach, hy + reach)) {
                self.segs.entry(c).or_default().push((wid, sid, a, b));
            }
        }
        self.ways.push(w);
    }

    /// The weight a caption set on `block` covers ([`ObstacleIndex::score`]'s first half).
    #[must_use]
    pub fn cost(&self, block: &[Pt], clear: f64, who: Asker<'_>, own_gap: Option<f64>) -> f64 {
        self.score(block, clear, who, own_gap).0
    }

    /// Is the obstacle waived for this caption: no weight, of a group its words name (but a named civic building when its subject is
    /// one), or its subject itself?
    ///
    /// Research: what a caption may cover - research/questions/0243-what-labels-may-cover-and-how-districts-are-named-on-town-and-city-maps.drawing.html: its own subject and the buildings of a group its words name, never a named civic building when its subject is one
    fn waived(o: &Obstacle, who: Asker<'_>, words: &str) -> bool {
        o.weight == 0.0
            || (names_group(o.group.as_deref(), words)
                && !(who.civic
                    && o.named
                    && o.group
                        .as_deref()
                        .is_some_and(|g| CIVIC_GROUPS.contains(&g))))
    }

    /// The weight a caption set on `block` covers - every obstacle it comes within `clear` of, except its own subject and any built
    /// feature of a group its text names (FR-014), plus [`WEIGHT_WAY`] per way it crosses - and whether any of it is an OVERLAP (an
    /// obstacle or way not `soft`; feature 287, D10). `own_gap`, the block's gap to its own POINT subject, adds the ASSOCIATION: an
    /// obstacle outside the subject standing as near the block as the subject does, or nearer, counts too.
    ///
    /// Research:
    ///     what a caption may cover - research/questions/0243-what-labels-may-cover-and-how-districts-are-named-on-town-and-city-maps.drawing.html: its own subject and the buildings of a group its words name, never a named
    ///         civic building when its subject is one
    ///     association - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a neighbor as near as the subject, or nearer, counts as covered
    ///     ways crossed - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: each way crossed adds its weight
    #[must_use]
    pub fn score(
        &self,
        block: &[Pt],
        clear: f64,
        who: Asker<'_>,
        own_gap: Option<f64>,
    ) -> (f64, bool) {
        let bb = bbox(block);
        let (x0, y0, x1, y1) = bb;
        let level = level_rect(block);
        let own_lim = own_gap.map_or(f64::NEG_INFINITY, |g| g + ASSOCIATION_TIE);
        let reach = max(clear, own_lim);
        let cs = cells((x0 - reach, y0 - reach, x1 + reach, y1 + reach));
        let mut seen = HashSet::new();
        let words = who.text.to_lowercase();
        let (mut total, mut hard) = (0.0, false);
        for c in &cs {
            for &i in self.ob.get(c).into_iter().flatten() {
                if !seen.insert(i) {
                    continue;
                }
                let o = &self.obstacles[i];
                let need = max(clear, o.keep);
                let bg = box_gap(bb, self.boxes[i]);
                if bg >= need - 1e-6 && bg > own_lim {
                    continue; // the boxes' gap bounds the outlines' from below: clear by the boxes, clear (feature 286)
                }
                if Self::waived(o, who, &words)
                    || who.subject.is_some_and(|s| !o.inner && part_of(&o.poly, s))
                {
                    continue;
                }
                // a disc is measured as a disc; two level rectangles are their boxes (feature 286)
                let gap = match o.circle {
                    Some(circle) => circle_gap(block, circle),
                    None if level && self.level[i] => bg,
                    None => poly_gap(block, &o.poly),
                };
                let mut near = gap < need - 1e-6; // strict: a seat exactly one offset off is clear (plan P6)...
                if !near && gap <= own_lim {
                    if let Some(subject) = who.subject {
                        let (cx, cy) = centroid(&o.poly);
                        near = !inside(cx, cy, subject); // ...unless its own subject stands no nearer (the association)
                    }
                }
                if near {
                    total += o.weight;
                    hard = hard || !o.soft;
                }
            }
        }
        // EACH SEGMENT MEASURED ONCE (feature 287, the board's 216 s siting): a segment filed in several cells is measured once
        let (mut crossed, mut measured) = (HashSet::new(), HashSet::new());
        let mut n_crossed = 0_u32;
        for c in &cs {
            for &(wid, sid, a, b) in self.segs.get(c).into_iter().flatten() {
                if crossed.contains(&wid) || !measured.insert(sid) {
                    continue;
                }
                let need = self.ways[wid].half_width + WAY_NOTCH;
                if box_gap(bb, self.seg_boxes[sid]) >= need {
                    continue;
                }
                if poly_seg_gap(block, a, b) < need {
                    crossed.insert(wid);
                    n_crossed += 1;
                    hard = hard || !self.ways[wid].soft;
                }
            }
        }
        (total + WEIGHT_WAY * f64::from(n_crossed), hard)
    }

    /// Does any obstacle outside `subject` stand within `gap` of `block` - as near as the subject or nearer, a tie counting? The
    /// association term of [`ObstacleIndex::score`] asked alone, of EVERY obstacle whatever its group, measured as `score` measures.
    ///
    /// Research: association - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a neighbor as near as the subject, or nearer, counts, a tie the neighbor's
    #[must_use]
    pub fn nearer_than(&self, block: &[Pt], gap: f64, subject: &[Pt]) -> bool {
        let bb = bbox(block);
        let (x0, y0, x1, y1) = bb;
        let lim = gap + ASSOCIATION_TIE;
        let mut seen = HashSet::new();
        for c in cells((x0 - lim, y0 - lim, x1 + lim, y1 + lim)) {
            for &i in self.ob.get(&c).into_iter().flatten() {
                if !seen.insert(i) {
                    continue;
                }
                if box_gap(bb, self.boxes[i]) > lim {
                    continue; // the boxes' gap bounds the outlines' from below
                }
                let o = &self.obstacles[i];
                let (cx, cy) = centroid(&o.poly);
                if part_of(&o.poly, subject) || inside(cx, cy, subject) {
                    continue;
                }
                let g = o
                    .circle
                    .map_or_else(|| poly_gap(block, &o.poly), |c| circle_gap(block, c));
                if g <= lim {
                    return true;
                }
            }
        }
        false
    }

    /// Does `score` count something against `block` that stays counted however the block is moved by up to `slack` - an obstacle or way
    /// nearer it than its own clearance less `slack`, or an overlap deeper than `slack`? Then no seat within `slack` of this one is free,
    /// and a strict search need not measure it or nudge it (feature 287). Asks the first such thing and stops.
    ///
    /// Research: a seat blocked beyond a nudge - NONE: a bound proving no nudge can free a seat, deciding nothing `score` would not
    #[must_use]
    pub fn blocked(&self, block: &[Pt], clear: f64, slack: f64, who: Asker<'_>) -> bool {
        count("candidate@Obstacles.blocked", 1);
        let bb = bbox(block);
        let (x0, y0, x1, y1) = bb;
        let (cx, cy) = (crate::py::half_sum(x0, x1), crate::py::half_sum(y0, y1)); // a rectangle's center is its box's
        let inner = crate::py::min(dist(block[0], block[1]), dist(block[1], block[2])) / 2.0; // the block is a rectangle (`rect`)
        let words = who.text.to_lowercase();
        for c in cells((x0 - clear, y0 - clear, x1 + clear, y1 + clear)) {
            for &i in self.ob.get(&c).into_iter().flatten() {
                let o = &self.obstacles[i];
                let need = max(clear, o.keep) - 1e-6;
                let bg = box_gap(bb, self.boxes[i]);
                if bg > 0.0 && bg >= need - slack {
                    continue; // apart by more than a moved block could close
                }
                if Self::waived(o, who, &words)
                    || who.subject.is_some_and(|s| !o.inner && part_of(&o.poly, s))
                {
                    continue;
                }
                if let Some((ox, oy, r)) = o.circle {
                    let reach = if inside(ox, oy, block) {
                        0.0
                    } else {
                        least(super::geom::ring_edges(block).map(|(a, b)| seg_dist((ox, oy), a, b)))
                    };
                    if reach - r < need - slack {
                        return true;
                    }
                    continue;
                }
                let gap = if self.level[i] && level_rect(block) {
                    bg
                } else {
                    poly_gap(block, &o.poly)
                };
                if gap < need - slack {
                    return true;
                }
                if gap == 0.0
                    && inside(cx, cy, &o.poly)
                    && least(
                        super::geom::ring_edges(&o.poly).map(|(a, b)| seg_dist((cx, cy), a, b)),
                    ) > slack
                {
                    return true;
                }
            }
            for &(wid, sid, a, b) in self.segs.get(&c).into_iter().flatten() {
                let need = self.ways[wid].half_width + WAY_NOTCH;
                if box_gap(bb, self.seg_boxes[sid]) >= need {
                    continue;
                }
                if poly_seg_gap(block, a, b) < need - slack
                    || seg_dist((cx, cy), a, b) + slack < inner
                {
                    return true;
                }
            }
        }
        false
    }
}

/// THE ONE PREDICATE of the association as the reader meets it (labels L6): does the caption on `block` stand nearer its own `subject`
/// than any obstacle `index` holds - strictly, a tie being the neighbor's?
///
/// Research: association - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: nearer its own subject than any other drawn thing, strictly
#[must_use]
pub fn stands_nearest(block: &[Pt], subject: &[Pt], index: &ObstacleIndex) -> bool {
    !index.nearer_than(block, poly_gap(block, subject), subject)
}

/// The gap between a caption's block and a disc `(x, y, r)`: 0 when they meet.
#[must_use]
pub fn circle_gap(block: &[Pt], circle: (f64, f64, f64)) -> f64 {
    let (x, y, r) = circle;
    if inside(x, y, block) {
        return 0.0;
    }
    let edge = least(super::geom::ring_edges(block).map(|(a, b)| seg_dist((x, y), a, b)));
    max(0.0, edge - r)
}

/// A disc as an obstacle - a tree crown (feature 287, labels L7): its box files it, the disc measures it.
#[must_use]
pub fn circle_obstacle(x: f64, y: f64, r: f64, weight: f64, group: Option<&str>) -> Obstacle {
    Obstacle {
        poly: vec![
            (x - r, y - r),
            (x + r, y - r),
            (x + r, y + r),
            (x - r, y + r),
        ],
        weight,
        group: group.map(str::to_owned),
        circle: Some((x, y, r)),
        ..Obstacle::default()
    }
}

/// Is this outline a level rectangle - four corners, every edge along an axis - so that its box is itself?
#[must_use]
pub fn level_rect(poly: &[Pt]) -> bool {
    poly.len() == 4
        && super::geom::ring_edges(poly)
            .all(|(a, b)| (a.0 - b.0).abs() < 1e-9 || (a.1 - b.1).abs() < 1e-9)
}

/// Is this obstacle the subject itself? Its center lies inside the subject, its box inside the subject's box (1 unit of slack), and it
/// spans at least half the subject's box: a board's own record, a building's own rect - a well in a court is NOT the court.
///
/// Research: an obstacle that is its caption's subject - CONVENTION: an obstacle is the subject when its center lies inside it, its box within the subject's (1 unit of slack) and it spans half the subject's box; a well in a court is not the court
#[must_use]
pub fn part_of(poly: &[Pt], subject: &[Pt]) -> bool {
    let (sx0, sy0, sx1, sy1) = bbox(subject);
    let (ox0, oy0, ox1, oy1) = bbox(poly);
    if !(ox0 >= sx0 - 1.0 && oy0 >= sy0 - 1.0 && ox1 <= sx1 + 1.0 && oy1 <= sy1 + 1.0) {
        return false; // the cheap box test first: an obstacle not within the subject's box is not the subject
    }
    let (cx, cy) = centroid(poly);
    inside(cx, cy, subject) && (ox1 - ox0) * (oy1 - oy0) >= 0.5 * (sx1 - sx0) * (sy1 - sy0)
}

#[cfg(test)]
mod tests;
