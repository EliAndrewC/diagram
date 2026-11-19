//! The sheet's ink as the placer asks it (feature 449 T202, the derivation's "Indexes"): one grid of uniform cells over the sheet's
//! extent, built once a sheet, each blocking or crossable drawn thing filed by its box in every cell the box overlaps, and each placed
//! caption filed the same way as it is seated. A query reads the cells its box overlaps, every entry in them once (a visit stamp), and
//! compares each entry's box with its own; only an entry whose box met a block is tested against its true outline.
//!
//! Research: the grid - NONE: an index over the drawn shapes, deciding nothing about where a caption stands; what is filed, and at what weight, is claimed at [`Index::build`]

use super::captions::{is_declared, WAY_KINDS};
use super::geom::{bbox, boxes_meet, convex, holds, quad_meets, ring, Bx, Pt};
use super::Shape;
use crate::work_counts::count;

/// The grid's cell, in px.
///
/// Research: the cell - NONE: 48 px (16 ft), the measured cheapest of 32, 48 and 64 px over the six pool sheets and about one mean caption block (the derivation's "Indexes"), an index's grain deciding no seat
pub const CELL_PX: f64 = 48.0;

/// The least half-width a stroke is filed at, so a hairline still has a band to meet.
///
/// Research: the thinnest stroke - CONVENTION: half a pixel a side, as a leader's end reads a stroke (feature 449 T192); a drawn size on the sheet, not in the world
pub const MIN_HALF_PX: f64 = 0.5;

/// What covering an entry costs a caption, in buildings: a building or fixture 1, a way half a building, another caption two.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Weight {
    Block,
    Way,
    Text,
    /// Another caption's feature, an area drawn by no ink of its own (a room marked out): a caption set on it reads as naming it.
    Named,
    /// Another caption's open ground (a court, a garden): another ground's name set on it reads as naming it.
    NamedGround,
    /// Open ground no caption names, filed only so a caption it is painted over knows it is hidden.
    Ground,
}

impl Weight {
    /// The weight in buildings.
    ///
    /// Research:
    ///     a way crossed - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a road or stream crossed counts as half a building (the page's calibration)
    ///     another named area covered - CONVENTION: one set on another caption's area weighs as that caption - 0242's "plainly the name of this feature and no other" read as feature 286's rule; the page gives no weight
    ///     a caption covered - GUESS: covering another caption weighs two buildings - 0242 orders a caption, the feature, a building and a fixture as never covered while any other choice exists, and does not give a figure; covering a caption makes two names unreadable
    ///     hidden under open ground - GUESS: a block that a filled court or garden no caption names is painted over (`Ground`) weighs two buildings, as a caption covered, since the fill hides its words as another caption's would; no page weighs a hidden caption
    #[must_use]
    pub fn of(self) -> f64 {
        match self {
            Weight::Block => 1.0,
            Weight::Way => 0.5,
            Weight::Text | Weight::Named | Weight::NamedGround | Weight::Ground => 2.0,
        }
    }
}

/// One filed outline: a filled body, one stroked segment as its band, or a caption's block.
#[derive(Clone, Debug)]
#[expect(
    clippy::struct_excessive_bools,
    reason = "four independent facts of a filed outline, each read alone"
)]
pub struct Entry {
    /// The drawn shape it came from; `None` for a caption or leader the placer seated.
    pub shape: Option<usize>,
    pub poly: Vec<Pt>,
    pub convex: bool,
    pub bx: Bx,
    pub weight: Weight,
    /// A filled body's stroke half-width: its outline is ink even where its floor is a caption's ground.
    pub edge: f64,
    /// Segments an exact test of it counts (`exact_test`): a rectangle, disc, band or block one, a path one a point pair.
    pub segs: u64,
    /// A drawn shape's filled body, filed whole (not a stroke's band nor a caption's block).
    pub body: bool,
    /// A band of a named body's stroked outline.
    pub outline: bool,
    /// A band of a wall: a caption is not seated across it from its feature.
    pub wall: bool,
    /// A seated caption's letters, its filed outline being them with their air: empty for anything else.
    pub core: Vec<Pt>,
}

/// The grid and what it holds.
pub struct Index {
    pub view: Bx,
    cols: usize,
    rows: usize,
    cells: Vec<Vec<u32>>,
    pub entries: Vec<Entry>,
    stamp: Vec<u32>,
    now: u32,
    /// Each indexed shape's box, for the holding test (a shape wholly holding a caption's feature is its ground).
    pub shape_box: Vec<Option<Bx>>,
    /// Each shape's place in the paint order (its element's in the document): what is painted after a caption lies over it.
    pub paint: Vec<usize>,
    /// How many captions name each shape.
    pub named_by: Vec<u16>,
    /// Is each shape open ground?
    pub ground: Vec<bool>,
    /// Does each shape draw ink (a fill, a stroke)? An outline drawn with neither only marks out an area, and hides nothing.
    pub visible: Vec<bool>,
    /// The widest stroke half-width a filed body carries: how far past an entry's box its drawn edge can reach.
    pub widest_edge: f64,
    /// Is each shape of a kind some caption names (a well's gear, though no caption names the gear itself)?
    pub kind_named: Vec<bool>,
}

/// The ground kinds: open ground a caption lies on as on empty paper.
///
/// Research: open ground - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: fields, scrub, groves and open ground are not in the way at all - courts, gardens, yards, practice grounds, clearings and groves (the derivation's assumption 1)
pub const GROUND_KINDS: [&str; 13] = [
    "inner court",
    "outer court",
    "hearing court",
    "border court",
    "garden",
    "vegetable garden",
    "practice ground",
    "cart yard",
    "rear yard",
    "precinct clearing",
    "shrine grove",
    "garden pines",
    "kitchen yard",
];

/// How far past the reader's measure a seated text (a title, a scale bar's figure) is filed at each end, in ems of its own size.
///
/// Research: a title's ends - GUESS: 0.6 em, no page sizing the reader's error on the sheet's own lettering; the sheet reader's glyph widths put a pool sheet's 30 px bold title 17-20 px short at each end of the rendered line (observed 2026-11-19, hayakawa-magistracy's PNG against the reader's box), and a caption seated against the measured end was drawn over the title's last letter - covering another caption, which 0242 forbids while any other choice exists
pub const FURNITURE_PAD_EM: f64 = 0.6;

/// A four-cornered text block lengthened by `pad` at each end along its longer side (its reading direction), whatever order its corners
/// come in.
#[must_use]
pub fn padded(poly: &[Pt], pad: f64) -> Vec<Pt> {
    if poly.len() != 4 {
        return poly.to_vec();
    }
    let edge = |a: Pt, b: Pt| (b.0 - a.0, b.1 - a.1);
    let (e1, e2) = (edge(poly[0], poly[1]), edge(poly[1], poly[2]));
    let (dx, dy) = if e1.0.hypot(e1.1) >= e2.0.hypot(e2.1) {
        e1
    } else {
        e2
    };
    let len = dx.hypot(dy);
    if len <= 0.0 {
        return poly.to_vec();
    }
    let (ux, uy) = (dx / len, dy / len);
    let c = (
        poly.iter().map(|p| p.0).sum::<f64>() / 4.0,
        poly.iter().map(|p| p.1).sum::<f64>() / 4.0,
    );
    poly.iter()
        .map(|&p| {
            let t = (p.0 - c.0) * ux + (p.1 - c.1) * uy;
            let k = if t >= 0.0 { pad } else { -pad };
            (p.0 + ux * k, p.1 + uy * k)
        })
        .collect()
}

/// The kinds that are a wall: a caption is not seated across one from its feature.
///
/// Research: walls - CONVENTION: the compound wall and a court divider; 0242 and 0330 say nothing of walls, and a caption beyond one names the wrong court (observed 2026-11-19: a pool sheet's kitchen name led across the court divider into the outer court)
pub const WALL_KINDS: [&str; 2] = ["compound wall", "court divider"];

/// What a caption's search has met while it ran: its feature's own lines, and named parts its feature holds.
#[derive(Default)]
pub struct Met {
    pub own_lines: std::cell::Cell<bool>,
    pub held_named: std::cell::Cell<bool>,
}

/// A band around one stroked segment.
#[must_use]
pub fn band(a: Pt, b: Pt, half: f64) -> Vec<Pt> {
    let (dx, dy) = (b.0 - a.0, b.1 - a.1);
    let len = dx.hypot(dy);
    let (ux, uy) = if len > 0.0 {
        (dx / len, dy / len)
    } else {
        (1.0, 0.0)
    };
    let (nx, ny) = (-uy * half, ux * half);
    vec![
        (a.0 + nx, a.1 + ny),
        (b.0 + nx, b.1 + ny),
        (b.0 - nx, b.1 - ny),
        (a.0 - nx, a.1 - ny),
    ]
}

fn grain(v: f64, lo: f64, n: usize) -> usize {
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        clippy::cast_precision_loss,
        reason = "a cell index, clamped to the grid"
    )]
    let i = ((v - lo) / CELL_PX).floor().clamp(0.0, (n - 1) as f64) as usize;
    i
}

impl Index {
    /// An empty grid over the sheet's view.
    #[must_use]
    pub fn new(view: Bx) -> Index {
        #[expect(
            clippy::cast_possible_truncation,
            clippy::cast_sign_loss,
            reason = "a sheet's size in cells"
        )]
        let span = |a: f64, b: f64| (((b - a) / CELL_PX).ceil().max(1.0)) as usize;
        let (cols, rows) = (span(view.0, view.2), span(view.1, view.3));
        Index {
            view,
            cols,
            rows,
            cells: vec![Vec::new(); cols * rows],
            entries: Vec::new(),
            stamp: Vec::new(),
            now: 0,
            shape_box: Vec::new(),
            paint: Vec::new(),
            named_by: Vec::new(),
            ground: Vec::new(),
            kind_named: Vec::new(),
            visible: Vec::new(),
            widest_edge: 0.0,
        }
    }

    fn span(&self, b: Bx) -> (usize, usize, usize, usize) {
        (
            grain(b.0, self.view.0, self.cols),
            grain(b.1, self.view.1, self.rows),
            grain(b.2, self.view.0, self.cols),
            grain(b.3, self.view.1, self.rows),
        )
    }

    /// File an outline in every cell its box overlaps (`index_insert`, one a cell written).
    pub fn file(
        &mut self,
        shape: Option<usize>,
        poly: Vec<Pt>,
        weight: Weight,
        (edge, segs, body): (f64, u64, bool),
    ) {
        let bx = bbox(&poly);
        #[expect(
            clippy::cast_possible_truncation,
            reason = "a sheet's entries, far under 2^32"
        )]
        let id = self.entries.len() as u32;
        let (c0, r0, c1, r1) = self.span(bx);
        for r in r0..=r1 {
            for c in c0..=c1 {
                self.cells[r * self.cols + c].push(id);
            }
        }
        count("index_insert@file", ((c1 - c0 + 1) * (r1 - r0 + 1)) as u64);
        let convex = convex(&poly);
        self.widest_edge = self.widest_edge.max(edge);
        self.entries.push(Entry {
            shape,
            poly,
            convex,
            bx,
            weight,
            edge,
            segs,
            body,
            outline: false,
            wall: false,
            core: Vec::new(),
        });
        self.stamp.push(0);
    }

    /// The sheet's ink filed once (the derivation's build): every drawn thing a caption may not cover, at its weight.
    ///
    /// Research:
    ///     what blocks - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a caption never lies on another caption, a building, a well or a small fixture while any other choice exists; every drawn kind but open ground blocks, walls and doors included (the derivation's assumption 1)
    ///     ways crossable - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a lane or a ditch may be crossed, at half a building's weight
    ///     open ground unfiled - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: open ground is not in the way at all, so unnamed ground painted before every caption is never read (its drawn border aside, the next claims)
    ///     the sheet's furniture - CONVENTION: the background (the one untagged rect over the whole view) is paper; a title or a scale bar's figure is a caption already seated, and its bar is ink (the derivation counted the untagged kind as ground; a caption over the scale bar reads as naming it)
    ///     texture and leaders - CONVENTION: a texture's strokes lie on a body already filed, and a leader drawn on the sheet is the caption's own, so neither is filed (feature 267's texture, feature 283's leader marks)
    ///     a named body's outline - CONVENTION: a body some caption names is filed with its stroked outline as bands too, ink to the caption inside it (feature 267 round 4: a name inside its building is not on its drawn outline); a body no caption names that holds a caption's feature is that caption's ground, outline and all
    ///     strokes by their bands - CONVENTION: a stroke, and an unfilled outline's edges, are ink only where drawn, so each segment is filed as its band - a compound wall's path holds the whole compound in its box, and filed whole it would cover every seat inside
    ///     named areas - CONVENTION: reading 0242's "plainly the name of this feature and no other", every area some caption names that no ink of its own marks - a room drawn only by its walls, a court, a garden - is filed: a room's for every caption it does not hold, a ground's for another ground's caption (CONVENTION of this placer, feature 286's rules: a name set on a named thing reads as naming it, and a ground's name set on another named ground reads as naming that ground; a building's name on open ground reads as the building's - blocking far seats on another court too was tried 2026-11-19 and sent a pool sheet's shrine name onto a wall and a house)
    ///     a ground's border - CONVENTION: a ground's drawn border is ink even where its floor is free space (feature 267), filed as its bands and crossed, where nothing clear is near, at a way's half weight (a dashed yard edge is crossed as a lane is); a tree's or a grove's round canopy is ground to its edge
    ///     painted over - CONVENTION: a filled ground painted after the sheet's first caption is filed too, as anything painted after a caption in the sheet's order hides it, open ground included (observed 2026-11-19 on hayakawa-magistracy while this placer was written: its RESIDENCE caption lay under the inner garden drawn after it); a ground painted before every caption hides none, and its geometry is never read
    #[must_use]
    pub fn build(shapes: &[Shape], view: Bx, named_by: Vec<u16>, first_caption: usize) -> Index {
        let mut ix = Index::new(view);
        ix.shape_box = vec![None; shapes.len()];
        ix.paint = shapes.iter().map(|s| s.at).collect();
        ix.ground = shapes
            .iter()
            .map(|s| GROUND_KINDS.contains(&s.kind.as_str()))
            .collect();
        let named_kinds: std::collections::BTreeSet<&str> = shapes
            .iter()
            .zip(&named_by)
            .filter(|(_, &n)| n > 0)
            .map(|(s, _)| s.kind.as_str())
            .collect();
        ix.kind_named = shapes
            .iter()
            .map(|s| named_kinds.contains(s.kind.as_str()))
            .collect();
        ix.named_by = named_by;
        ix.visible = shapes
            .iter()
            .map(|s| s.line || s.filled || s.edge > 0.0)
            .collect();
        for (i, s) in shapes.iter().enumerate() {
            if s.tag == "text" {
                ix.file_text(i, s);
                continue;
            }
            if s.leader || s.texture || s.poly.len() < 2 || background(s, view) {
                continue;
            }
            let area = !s.line && s.poly.len() >= 3;
            let named = ix.named_by.get(i).copied().unwrap_or(0) > 0;
            let unseen = ix.ground[i] || (!s.line && !s.filled && s.edge <= 0.0);
            if unseen {
                ix.file_unseen(i, s, (named, area, first_caption));
                continue;
            }
            let segs = if s.line || matches!(s.tag.as_str(), "rect" | "circle" | "ellipse") {
                if s.line {
                    (s.poly.len() - 1) as u64
                } else {
                    1
                }
            } else {
                s.poly.len() as u64
            };
            count("shape_box@build", segs);
            ix.shape_box[i] = Some(bbox(&s.poly));
            let weight = if WAY_KINDS.contains(&s.kind.as_str()) {
                Weight::Way
            } else {
                Weight::Block
            };
            if s.line {
                let half = s.half.max(MIN_HALF_PX);
                let wall = WALL_KINDS.contains(&s.kind.as_str());
                for w in s.poly.windows(2) {
                    ix.file(Some(i), band(w[0], w[1], half), weight, (0.0, 1, false));
                    let last = ix.entries.len() - 1;
                    ix.entries[last].wall = wall;
                }
            } else if s.filled {
                ix.file(Some(i), s.poly.clone(), weight, (s.edge, segs, true));
                if named && s.edge > 0.0 {
                    // a named body's stroked outline is ink even to the caption it holds
                    let edges: Vec<(Pt, Pt)> = ring(&s.poly).collect();
                    for (a, b) in edges {
                        ix.file(Some(i), band(a, b, s.edge), weight, (0.0, 1, false));
                        let last = ix.entries.len() - 1;
                        ix.entries[last].outline = true;
                    }
                }
            } else {
                // unfilled, so stroked (an unstroked unfilled outline draws nothing, and was passed over above)
                let half = s.edge.max(MIN_HALF_PX);
                let edges: Vec<(Pt, Pt)> = ring(&s.poly).collect();
                for (a, b) in edges {
                    ix.file(Some(i), band(a, b, half), weight, (0.0, 1, false));
                }
            }
        }
        ix
    }

    /// A seated text (a title, a scale bar's figure) filed as a caption, lengthened at its ends; a declaration is filed when seated.
    fn file_text(&mut self, i: usize, s: &Shape) {
        if !is_declared(s) && !s.poly.is_empty() {
            self.file(
                Some(i),
                padded(&s.poly, FURNITURE_PAD_EM * s.size),
                Weight::Text,
                (0.0, 1, false),
            );
        }
    }

    /// Open ground or an unmarked outline: its drawn border as crossable bands, and - named, or filled and painted after the first
    /// caption - its area.
    fn file_unseen(
        &mut self,
        i: usize,
        s: &Shape,
        (named, area, first_caption): (bool, bool, usize),
    ) {
        let disc = matches!(s.tag.as_str(), "circle" | "ellipse");
        if self.ground[i] && area && !disc && s.edge > 0.0 {
            // a ground's drawn border is ink, though its floor is free
            count("shape_box@build", s.poly.len() as u64);
            let edges: Vec<(Pt, Pt)> = ring(&s.poly).collect();
            for (a, b) in edges {
                self.file(
                    Some(i),
                    band(a, b, s.edge.max(MIN_HALF_PX)),
                    Weight::Way,
                    (0.0, 1, false),
                );
            }
        }
        if area && (named || (self.ground[i] && s.filled && s.at > first_caption)) {
            count("shape_box@build", s.poly.len() as u64);
            self.shape_box[i] = Some(bbox(&s.poly));
            let w = match (self.ground[i], named) {
                (true, true) => Weight::NamedGround,
                (true, false) => Weight::Ground,
                _ => Weight::Named,
            };
            self.file(Some(i), s.poly.clone(), w, (0.0, s.poly.len() as u64, true));
        }
    }

    /// The entries whose cells a box overlaps, each once (`index_query`, `index_cell`, `index_entry`).
    pub fn query(&mut self, b: Bx, at: &str) -> Vec<u32> {
        self.now += 1;
        count(&format!("index_query@{at}"), 1);
        let (c0, r0, c1, r1) = self.span(b);
        count(
            &format!("index_cell@{at}"),
            ((c1 - c0 + 1) * (r1 - r0 + 1)) as u64,
        );
        let mut out = Vec::new();
        for r in r0..=r1 {
            for c in c0..=c1 {
                let cell = &self.cells[r * self.cols + c];
                count(&format!("index_entry@{at}"), cell.len() as u64);
                for &e in cell {
                    let st = &mut self.stamp[e as usize];
                    if *st != self.now {
                        *st = self.now;
                        out.push(e);
                    }
                }
            }
        }
        out
    }
}

/// Is this the sheet's background: an untagged rect over the whole view?
fn background(s: &Shape, view: Bx) -> bool {
    s.kind == "-" && s.tag == "rect" && holds(bbox(&s.poly), view)
}

/// What a caption's seat is tested against, beside the grid: its own parts, its feature's box, whether it names open ground, and where
/// its first line stands in the paint order.
#[derive(Clone, Copy)]
#[expect(
    clippy::struct_excessive_bools,
    reason = "independent facts of one caption's search, each read alone"
)]
pub struct Own<'a> {
    pub parts: &'a [usize],
    pub fbox_sheet: Option<Bx>,
    /// Does the caption name open ground?
    pub ground: bool,
    /// The paint order of its first line element: ink painted after it lies over it.
    pub at: usize,
    /// Are the feature's own strokes (its partitions, its details) ink to it? The first pass on the feature asks so.
    pub clear_own_lines: bool,
    /// On the feature, the paint order of its filled outline: what is painted before it, beneath it, is hidden there.
    pub under: Option<usize>,
    /// A region's last pass: the named parts its feature holds (its rooms) are its own ground.
    pub region: bool,
    /// What the search has met.
    pub met: &'a Met,
    /// The paint order of its tagged group and of the group's last element.
    pub subtree: Option<(usize, usize)>,
    /// A region's last pass: how far above and below another caption's letters it keeps, so the two do not read as one block.
    pub stack: f64,
    /// The feature's very last pass: its own outline's stroke is no obstacle (a name as wide as its feature).
    pub on_outline: bool,
}

impl Own<'_> {
    /// How an entry stands to this caption: `Skip` (its own feature, or a shape it is no obstacle to) or `Ink`.
    ///
    /// Research:
    ///     the feature's own parts - CONVENTION: the derivation's clean test, reading 0242's "a feature large enough to hold its name is named on itself": its own parts - its partitions and details included - are no obstacle to its caption (the derivation's clean test), but its drawn outline is, and a part another caption names is that caption's, a name set on it reading as naming it
    ///     the ground it stands on - CONVENTION: a body wholly holding the caption's feature (a room's building) is its ground, but a named body's drawn outline is ink (feature 267 round 4)
    ///     painted over - CONVENTION: anything painted after the caption lies over it and hides it, its own parts included (feature 267's rule, as the sheet reader's classification states it)
    ///     its own details - CONVENTION: ink drawn within the caption's own tagged group that no caption names, of a kind no caption names (a weighing floor's steelyard and bales, tagged with kinds of their own; not a well's gear drawn in a kitchen, its kind the well's) is the feature's own detail, which a caption named on its feature may lie across where nothing clear of it is left, as of its own lines - never another feature's ink (the coordinator's ruling 2026-11-19: a pool sheet's weighing floor was led 211 px onto the hearing court, read as part of it)
    ///     its own outline, last - CONVENTION: a name wider than its feature's inside but not its outline lies across the outline's own stroke, tried only once no place at the usual gap is clean and before any sweep - read as naming it, where every place beside covers another building (tried before the usual gap, it set a notice board's name across the board's planks) (the coordinator's ruling 2026-11-19: a pool sheet's weighing floor, 0.6 px a side too wide, was led 211 px onto the hearing court)
    ///     a region's name not stacked - CONVENTION: across its rooms, a region's name keeps a line's height above and below another caption's letters, so the two do not read as one block (the coordinator's ruling 2026-11-19: a pool sheet's RESIDENCE sat directly above "guest room" and read as its title)
    ///     beneath its outline - CONVENTION: on its feature, ink painted before the feature's filled outline lies beneath it and is hidden there (a kitchen drawn over the end of the house it belongs to)
    ///     a region over its rooms - CONVENTION: a region's name (a house, a court) is set on the region; where no place on it is clear of the named rooms it holds, it is set across them and the air about their names, never across the names (0242 names an area on itself, and says nothing of rooms; the coordinator's ruling 2026-11-19 that a region's name belongs inside its region)
    ///     its own lines first - CONVENTION: on its feature, a caption first keeps off the feature's own strokes (a partition through a building's middle strikes its name through), and lies across them only where no place on the feature is clear of them (a pool sheet's kitchen named across its pantry line rather than led out across a wall); the derivation's rule, own parts no obstacle, is the second pass
    #[must_use]
    pub fn stance(&self, ix: &Index, e: &Entry) -> Stance {
        let Some(s) = e.shape else {
            return Stance::Ink;
        };
        if ix.paint[s] > self.at && ix.visible[s] {
            return Stance::Ink;
        }
        if self.under.is_some_and(|u| ix.paint[s] < u) {
            return Stance::Skip;
        }
        let holding =
            || matches!((ix.shape_box[s], self.fbox_sheet), (Some(sb), Some(fb)) if holds(sb, fb));
        let held = || matches!(self.fbox_sheet, Some(fb) if holds(fb, e.bx));
        // ink drawn within the caption's own group that no caption names is its feature's own detail (a weighing floor's steelyard)
        let detail = ix.named_by[s] == 0
            && !ix.kind_named[s]
            && self
                .subtree
                .is_some_and(|(g, last)| ix.paint[s] > g && ix.paint[s] <= last);
        if self.parts.contains(&s) || detail {
            if ix.named_by[s] >= 2 && !holding() {
                self.met.held_named.set(true);
                return if self.region {
                    Stance::Skip
                } else {
                    Stance::Ink
                };
            }
            if !e.body && !e.outline {
                self.met.own_lines.set(true);
            }
            let own_line = self.clear_own_lines && !e.body;
            return if (e.outline && !self.on_outline) || own_line {
                Stance::Ink
            } else {
                Stance::Skip
            };
        }
        match e.weight {
            Weight::Ground => return Stance::Skip,
            // a named court or garden is ground to what stands in it and to a building's name; another ground's name on it reads as
            // naming it
            Weight::NamedGround if holding() || !self.ground => return Stance::Skip,
            _ => {}
        }
        if e.body && holding() {
            return Stance::Skip;
        }
        if ix.named_by[s] >= 1 && held() {
            self.met.held_named.set(true);
            if self.region {
                return Stance::Skip;
            }
        }
        Stance::Ink
    }
}

/// How an entry stands to one caption ([`Own::stance`]).
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Stance {
    Skip,
    Ink,
}

/// Does a block cover this entry, as the caption stands to it? `exact_test` counts its segments.
#[must_use]
pub fn covers(quad: &[Pt; 4], e: &Entry, stance: Stance, region: (bool, f64)) -> bool {
    match stance {
        Stance::Skip => false,
        Stance::Ink => {
            count("exact_test@covers", e.segs);
            quad_meets(quad, &e.reach(region), e.convex)
        }
    }
}

impl Entry {
    /// What a caption must keep off: the entry's outline, or - a region's last pass - a seated caption's letters without their air, but
    /// with a line's height (`stack`) above and below them.
    #[must_use]
    pub fn reach(&self, (region, stack): (bool, f64)) -> std::borrow::Cow<'_, [Pt]> {
        if region && !self.core.is_empty() {
            let b = bbox(&self.core);
            let (y0, y1) = (b.1 - stack, b.3 + stack);
            std::borrow::Cow::Owned(vec![(b.0, y0), (b.2, y0), (b.2, y1), (b.0, y1)])
        } else {
            std::borrow::Cow::Borrowed(&self.poly)
        }
    }
}

/// Does a box meet an entry's box?
#[must_use]
pub fn near(b: Bx, e: &Entry) -> bool {
    boxes_meet(b, e.bx)
}

#[cfg(test)]
mod tests {
    use super::{band, padded, Index, Weight};

    #[test]
    fn the_weights_are_buildings() {
        assert!((Weight::Way.of() - 0.5).abs() < 1e-12);
        assert!((Weight::Block.of() - 1.0).abs() < 1e-12);
        assert!((Weight::Text.of() - 2.0).abs() < 1e-12);
    }

    /// A seated text is lengthened along its reading direction, whatever order its corners come in.
    #[test]
    fn a_text_is_padded_along_its_line() {
        let wide = [(0.0, 0.0), (10.0, 0.0), (10.0, 2.0), (0.0, 2.0)];
        let got = padded(&wide, 1.0);
        assert_eq!(got[0], (-1.0, 0.0));
        assert_eq!(got[2], (11.0, 2.0));
        let rotated = [(0.0, 0.0), (0.0, 2.0), (10.0, 2.0), (10.0, 0.0)];
        assert_eq!(padded(&rotated, 1.0)[2], (11.0, 2.0));
        assert_eq!(padded(&wide[..3], 1.0).len(), 3);
        assert_eq!(padded(&[(1.0, 1.0); 4], 1.0)[0], (1.0, 1.0));
    }

    #[test]
    fn a_band_has_a_width_even_for_a_point() {
        let b = band((0.0, 0.0), (0.0, 0.0), 1.0);
        assert_eq!(b[0], (0.0, 1.0));
    }

    /// A query reads each entry once though it lies in several cells, and a box off the grid reads its edge cells.
    #[test]
    fn a_query_reads_each_entry_once() {
        let mut ix = Index::new((0.0, 0.0, 200.0, 200.0));
        ix.file(
            None,
            vec![(10.0, 10.0), (150.0, 10.0), (150.0, 150.0), (10.0, 150.0)],
            Weight::Block,
            (0.0, 1, true),
        );
        assert_eq!(ix.query((0.0, 0.0, 200.0, 200.0), "t"), vec![0]);
        assert_eq!(ix.query((-500.0, -500.0, -400.0, -400.0), "t"), vec![0]);
    }
}
