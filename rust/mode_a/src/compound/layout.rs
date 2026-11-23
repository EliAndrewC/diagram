//! The buildings seated (derivation T208, "The algorithm"): the court spine and the gates' approaches filed first; then the buildings in
//! tiers - the north and south rows, which own the corners, then the east and west columns, which flow below them, then the divider -
//! within a tier the highest order and then the largest first, each by one span search along its wall's band from its row's first
//! long-enough gap; a house's ell at one of its ends; the middle gate fixed once the office hall stands; and each door at its seat on
//! its face, its mouth and step asked clear. Every rule is asked before a thing is placed; nothing is placed and then moved, and a
//! building with no room on its wall is reported, never squeezed (the GM, 2026-10-12: room first).
//!
//! Research: the seating's plumbing - NONE: the layout's records, keys and box helpers; each rule claimed on the unit that asks it

#![expect(
    clippy::many_single_char_names,
    reason = "geometry in feet: boxes, edges and points named as the derivation names them"
)]
use std::collections::BTreeMap;

use l7r_gate_research::Error;

use super::count;
use super::grid::{overlaps, Grid, What};
use super::span::{centered, insert, nearest, walk, Ask, Strip};
use super::spec::{Building, Bx, Court, Face, Program, Wall};
use crate::types::Band;

/// Half the compound wall's thickness (feet).
///
/// Research: compound wall thickness - research/questions/0092-compound-walls-neribei-and-tsuijibei.drawing.html: the wall drawn 3 ft thick, centered on its line
pub const WALL_HALF: f64 = 1.5;
/// Half the divider's thickness (feet).
///
/// Research:
///     divider thickness - research/questions/0092-compound-walls-neribei-and-tsuijibei.drawing.html: the divider drawn 2 ft thick, inside the page's real thickness of a foot or two for the lighter plastered wall (the page names no divider)
pub const DIVIDER_HALF: f64 = 1.0;
/// The ground every building keeps clear of a wall's face (feet).
///
/// Research: a foot or two clear of the wall - research/questions/0092-compound-walls-neribei-and-tsuijibei.drawing.html: a building stands a foot or two off the wall's face, its eaves nearly touching; 1.5 ft, the page's GUESS spacing
pub const CLEAR: f64 = 1.5;
/// The fire gap between neighbors along a wall (feet).
///
/// Research: fire gap along a wall - GUESS research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.drawing.html: 6 ft, the low end of the page's 6-8 ft between wooden buildings and 6-10 ft at a kura, both guesses there; a knob
pub const FIRE_GAP: f64 = 6.0;
/// A gate's held approach, inside the wall (feet).
///
/// Research: a gate's held approach - GUESS: 12 ft, about the passage's own scale (the derivation's assumption 6); nothing stands in a gateway (docs/buildings.md checklist, itself a GUESS of the project)
pub const APPROACH: f64 = 12.0;
/// A gate post's side (feet), drawn outside the passage.
///
/// Research: gate posts - CONVENTION: a gate's posts drawn outside its passage, each post's inner face on the passage, 2 ft along the wall and about 4.3 ft across it on the generated plans, past the wall's ink on both faces (0093's drawing page; 449 T349, T365)
pub const POST: f64 = 2.0;
/// A door's width and depth (feet).
///
/// Research: a door's block - research/questions/0117-doorways-and-doors-to.drawing.html: a door's small block set wholly inside its building, its outer edge on the wall it opens through, drawn 6 ft wide (one ken) by about 1.3 ft, a map drawing convention
pub const DOOR: (f64, f64) = (6.0, 4.0 / 3.0);
/// The step before a door, held clear (feet).
///
/// Research: a door's step held clear - GUESS: 3 ft before a door's mouth kept clear of every part, so no tub or well stands in a doorway; a knob
pub const DOOR_STEP: f64 = 3.0;
/// A formal entrance's porch: its width along the face and its depth out from it (feet).
///
/// Research: the genkan's porch - research/questions/0104-the-formal-entrance-and-a-guests-arrival-genkan.html: about 12 by 9 ft, the one shikidai found measured (the Sayama jin'ya's council hall, 1775), its 2 ken one side and its 6 mats making the other about 9 ft (the page's reading and arithmetic); drawn along the face by 9 ft out, a GUESS: which side was width and which depth the page does not say
pub const GENKAN: (f64, f64) = (12.0, 9.0);

/// The ground a compound shrine holds past its far end along its wall for its tree: the tree's crown and its clearance off the hall
/// (feet).
///
/// Research: compound shrine tree - research/questions/0218-the-compounds-own-shrine-yashikigami.drawing.html: every compound shrine in a corner of its grounds beside one tree; its ground held as the shrine is seated, the crown's 20 ft and its 3.5 ft off the hall (the tree's GUESSES, `fixtures::TREE`)
pub const TREE_ROOM: f64 = 2.0 * super::fixtures::TREE.0 + super::fixtures::TREE.1;

/// A door seated: its building, face, block and step.
#[derive(Clone, Debug, PartialEq)]
pub struct Door {
    /// The building's index.
    pub b: usize,
    /// The face it opens through.
    pub face: Face,
    /// Its block, inside the building.
    pub bx: Bx,
    /// The step before it.
    pub step: Bx,
    /// A formal entrance's porch, built out from the face, the door at its outer edge; None for a plain door.
    pub porch: Option<Bx>,
}

impl Door {
    /// The door's middle.
    #[must_use]
    pub fn mid(&self) -> (f64, f64) {
        (
            f64::midpoint(self.bx.0, self.bx.2),
            f64::midpoint(self.bx.1, self.bx.3),
        )
    }
}

/// A wall's row: its seated intervals along the wall, grown by their fire gaps, and its deepest building.
type Row = (Vec<(f64, f64)>, f64);

/// The seated layout: the grid, each building's box, the seat order, the doors, and the openings in the walls.
pub struct Layout {
    /// The grid every thing is filed in.
    pub grid: Grid,
    /// Each building's box, by its index in the program.
    pub seats: Vec<Option<Bx>>,
    /// The order the buildings were seated in.
    pub order: Vec<usize>,
    /// The doors.
    pub doors: Vec<Door>,
    /// The middle gate's opening along the divider.
    pub middle: Option<(f64, f64)>,
    rows: BTreeMap<(u8, u8), Row>,
}

/// The face a building's wall gives it to the court: the side away from the wall.
///
/// Research:
///     a building faces its court - research/questions/0092-compound-walls-neribei-and-tsuijibei.drawing.html: a building backs onto its wall, so it faces away from it; the divider's two sides are the two courts of research/questions/0090-magistrates-compounds-jinya-and-yamen.drawing.html
#[must_use]
pub fn court_face(b: &Building) -> Face {
    match b.wall {
        Wall::Side(f) => f.opposite(),
        Wall::Divider => match b.court {
            Court::Inner => Face::N,
            Court::Outer => Face::S,
        },
    }
}

/// The wall's face a building backs.
///
/// Research:
///     a building backs its wall - research/questions/0092-compound-walls-neribei-and-tsuijibei.drawing.html: each building that backs onto the wall
#[must_use]
pub fn back_face(b: &Building) -> Face {
    court_face(b).opposite()
}

/// The court's range along an east or west wall (feet).
///
/// Research:
///     each court a step clear of its walls - research/questions/0092-compound-walls-neribei-and-tsuijibei.drawing.html: a building a foot or two clear of the wall's face; the two courts either side of the divider, research/questions/0090-magistrates-compounds-jinya-and-yamen.drawing.html
#[must_use]
pub fn court_range(p: &Program, c: Court) -> (f64, f64) {
    match c {
        Court::Inner => (WALL_HALF + CLEAR, p.divider - DIVIDER_HALF - CLEAR),
        Court::Outer => (p.divider + DIVIDER_HALF + CLEAR, p.h - WALL_HALF - CLEAR),
    }
}

/// A building's band along its wall at `inset`, and its length along the band.
///
/// Research:
///     a building against its wall - research/questions/0092-compound-walls-neribei-and-tsuijibei.drawing.html: each building backs its wall or the divider a step clear of the face, the wall's own ground taken
#[must_use]
pub fn band(p: &Program, b: &Building, inset: f64) -> (Strip, f64) {
    let off = WALL_HALF + CLEAR + inset;
    let across_x = (WALL_HALF + CLEAR, p.w - WALL_HALF - CLEAR);
    let (along_x, p0, depth, (lo, hi)) = match b.wall {
        Wall::Side(Face::N) => (true, off, b.h, across_x),
        Wall::Side(Face::S) => (true, p.h - off - b.h, b.h, across_x),
        Wall::Side(Face::W) => (false, off, b.w, court_range(p, b.court)),
        Wall::Side(Face::E) => (false, p.w - off - b.w, b.w, court_range(p, b.court)),
        Wall::Divider => {
            let d = DIVIDER_HALF + CLEAR + inset;
            let p0 = match b.court {
                Court::Outer => p.divider + d,
                Court::Inner => p.divider - d - b.h,
            };
            (true, p0, b.h, across_x)
        }
    };
    let len = if along_x { b.w } else { b.h };
    (
        Strip {
            along_x,
            p0,
            p1: p0 + depth,
            lo,
            hi,
        },
        len,
    )
}

fn row_key(b: &Building) -> (u8, u8) {
    let c = u8::from(b.court == Court::Outer);
    let w = match b.wall {
        Wall::Side(Face::N) => 0,
        Wall::Side(Face::S) => 1,
        Wall::Side(Face::E) => 2,
        Wall::Side(Face::W) => 3,
        Wall::Divider => 4,
    };
    (c, w)
}

/// The tier a building is seated in: 0 the north and south rows, 1 the east and west columns, 2 the divider.
///
/// Research: perimeter-first tiers - GUESS: the north and south rows first (they own the corners), then the east and west columns flowing below them, then the divider hall; within a tier the highest order, then the largest, first; a rank-2 store after its wall's row (docs/buildings.md, Composition, a value of the project's: no source could speak to it)
#[must_use]
pub fn tier(b: &Building) -> (u8, u8) {
    let t = match b.wall {
        Wall::Side(Face::N | Face::S) => 0,
        Wall::Side(_) => 1,
        Wall::Divider => 2,
    };
    (t, b.rank)
}

/// The buildings' seat order: by tier and rank, then highest order, then largest; an ell after its host, not in a tier.
///
/// Research:
///     perimeter-first tiers - GUESS: the seating order - the tier, then the highest order, then the largest, each ell straight after its host (docs/buildings.md, Composition, a value of the project's: no source could speak to it)
#[must_use]
pub fn seat_order(p: &Program) -> Vec<usize> {
    let mut idx: Vec<usize> = (0..p.buildings.len())
        .filter(|&i| p.buildings[i].joins.is_none())
        .collect();
    idx.sort_by(|&a, &b| {
        let (x, y) = (&p.buildings[a], &p.buildings[b]);
        count("span_compare@compound_order", 1);
        tier(x)
            .cmp(&tier(y))
            .then(y.order.cmp(&x.order))
            .then((y.w * y.h).total_cmp(&(x.w * x.h)))
    });
    let mut out = Vec::new();
    for i in idx {
        out.push(i);
        let name = &p.buildings[i].name;
        out.extend(
            (0..p.buildings.len()).filter(|&j| p.buildings[j].joins.as_deref() == Some(name)),
        );
    }
    out
}

/// The gap rule a building's search keeps: another building's fire gap along the wall (none across it, so a rear strip holds stores
/// behind an inset house), a zone's and a gate's edge.
///
/// Research:
///     the buildings seated - research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.drawing.html: buildings a fire gap apart along a wall, none on the named grounds
#[must_use]
pub fn building_rule(e: &super::grid::Ent) -> Option<(f64, f64)> {
    match e.what {
        What::Building(_) => Some((FIRE_GAP, 0.0)),
        // a held part's ground kept a step clear, so the part seated on it later keeps its own clearance
        What::Held(_) => Some((CLEAR, 0.0)),
        What::Part(..) | What::Wall => None,
        What::Zone(_) | What::Gate | What::Door(_) => Some((0.0, 0.0)),
    }
}

fn refuse(message: String) -> Error {
    Error::new("ValueError", message)
}

impl Layout {
    /// The spine and the gates filed, nothing seated.
    ///
    /// Research:
    ///     named court spine - research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.drawing.html: the spine's grounds filed before any building, so no building takes them
    ///     the walls' ground taken - research/questions/0092-compound-walls-neribei-and-tsuijibei.drawing.html: the wall's ink is its own ground, no part stands on it
    #[must_use]
    pub fn new(p: &Program) -> Self {
        let mut grid = Grid::new(p.w, p.h);
        for (i, z) in p.zones.iter().enumerate() {
            grid.file(z.bx, What::Zone(i));
        }
        for g in &p.gates {
            grid.file(gate_approach(p, g.wall, g.at, g.width), What::Gate);
        }
        // the walls' ink, which no part stands on (docs/buildings.md: structures abut a wall, they never stand in it)
        let (w, h) = (WALL_HALF, DIVIDER_HALF);
        for ink in [
            (-w, -w, p.w + w, w),
            (-w, p.h - w, p.w + w, p.h + w),
            (-w, -w, w, p.h + w),
            (p.w - w, -w, p.w + w, p.h + w),
            (0.0, p.divider - h, p.w, p.divider + h),
        ] {
            grid.file(ink, What::Wall);
        }
        Self {
            grid,
            seats: vec![None; p.buildings.len()],
            order: Vec::new(),
            doors: Vec::new(),
            middle: None,
            rows: BTreeMap::new(),
        }
    }

    /// Every building seated in its tier, the ells beside their hosts and the middle gate behind the office hall.
    ///
    /// # Errors
    /// A building with no room on its wall, outside its size band, or an ell with no free end: the program is refused, nothing squeezed.
    ///
    /// Research:
    ///     the divider's first building centered - GUESS: only the divider's first building takes the centered seat, the later ones the free span nearest the middle (docs/buildings.md: the divider hall flows centered between the columns, a value of the project's); the rest orchestration
    pub fn seat_all(&mut self, p: &Program, bands: &[(String, Band)]) -> Result<(), Error> {
        self.spine_apart(p)?;
        let mut divider_first = true;
        for i in seat_order(p) {
            let b = &p.buildings[i];
            let bx = if let Some(host) = &b.joins {
                self.seat_ell(p, i, host)?
            } else {
                let at = self.seat_one(p, i, divider_first)?;
                if b.wall == Wall::Divider {
                    divider_first = false;
                }
                at
            };
            self.keep(p, i, bx, bands)?;
            if b.kind == "office hall" && self.middle.is_none() {
                self.middle_gate(p, bx)?;
            }
        }
        Ok(())
    }

    /// Each ground of the spine asked of the grid: grounds may abut, never overlap.
    ///
    /// Research: named court spine - research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.drawing.html: forecourt, hearing court (oshirasu), garden and the ground between the courts stay open, each its own named ground
    fn spine_apart(&mut self, p: &Program) -> Result<(), Error> {
        for (i, z) in p.zones.iter().enumerate() {
            let hits = self.grid.query(z.bx, "compound_zone");
            count("rule_check@compound_zone", 1);
            if let Some(j) = hits.into_iter().find_map(|e| match self.grid.ents[e].what {
                What::Zone(j) if j != i => Some(j),
                _ => None,
            }) {
                return Err(refuse(format!(
                    "the {} and the {} overlap - the spine's grounds are each their own",
                    z.kind, p.zones[j].kind
                )));
            }
        }
        Ok(())
    }

    /// Research:
    ///     packed from the wall's low end - GUESS: a row or column seats each building at the first free span from its wall's low end, so the north and south rows own the corners (docs/buildings.md, Composition, a value of the project's)
    ///     the divider's first building centered - GUESS: centered in the free ground holding the wall's middle (docs/buildings.md: the divider hall flows centered between the columns)
    ///     gatehouse beside the gate - research/questions/0093-the-main-gate-and-its-gatekeepers-nagaya-mon.html: the gatekeepers in a gatehouse of their own beside a one-bay gate, seated nearest the main gate
    ///     the program's start - GUESS: a building the program starts at a point along its wall takes the free span nearest it, the derivation's start-end knob
    ///     second rank - research/questions/0115-servants-in-a-samurai-household-where-they-sleep-and-how-they-were-hired-hokonin.drawing.html, research/questions/0091-samurai-residences-and-their-rooms-buke-yashiki.drawing.html: the rear rank holds stores, set behind its wall's rank-1 row by a fire gap; servants lodge on the street edge, never in a rear rank
    ///     the shrine in its corner - research/questions/0218-the-compounds-own-shrine-yashikigami.drawing.html: a compound shrine in a corner of its grounds beside one tree, the tree's ground held past the shrine's far end
    fn seat_one(&mut self, p: &Program, i: usize, divider_first: bool) -> Result<Bx, Error> {
        let b = &p.buildings[i];
        let key = row_key(b);
        let inset = if b.rank == 2 {
            if !matches!(b.role.as_str(), "kura" | "takakura") {
                return Err(refuse(format!(
                    "the {} takes the second rank, which holds stores only - servants lodge on the street edge (0115)",
                    b.name
                )));
            }
            self.rows.get(&key).map_or(0.0, |r| r.1) + FIRE_GAP + b.inset
        } else {
            b.inset
        };
        let (strip, len) = band(p, b, inset);
        let ask = Ask {
            strip,
            len,
            rule: &building_rule,
            reach: FIRE_GAP,
            f: "compound_building",
        };
        let row = if b.rank == 1 && b.inset == 0.0 {
            self.rows.get(&key).map(|r| r.0.clone()).unwrap_or_default()
        } else {
            Vec::new()
        };
        let mid = f64::midpoint(strip.lo, strip.hi);
        let at = if b.beside_gate {
            let g = &p.gates[0];
            nearest(&mut self.grid, &ask, g.at - len / 2.0)
        } else if let Some(near) = b.near {
            nearest(&mut self.grid, &ask, near)
        } else if b.kind == "compound shrine" {
            // the shrine's tree's ground held past its far end as it is seated, so the tree beside it has room
            let room = Ask {
                len: len + TREE_ROOM,
                ..ask
            };
            let s = walk(&mut self.grid, &room, &row, strip.lo, 1.0);
            if let Some(s) = s {
                self.grid
                    .file(strip.bx(s + len, s + len + TREE_ROOM, 0.0), What::Held(i));
            }
            s
        } else if b.wall == Wall::Divider && divider_first {
            match centered(&mut self.grid, &ask, mid) {
                Some(s) => Some(s),
                None => nearest(&mut self.grid, &ask, mid - len / 2.0),
            }
        } else if b.wall == Wall::Divider {
            nearest(&mut self.grid, &ask, mid - len / 2.0)
        } else {
            walk(&mut self.grid, &ask, &row, strip.lo, 1.0)
        };
        let Some(s) = at else {
            return Err(refuse(format!(
                "no room on its wall for the {} ({} x {} ft) - move the envelope or the program's knob, never squeeze it (room first, the GM 2026-10-12)",
                b.name, b.w, b.h
            )));
        };
        Ok(strip.bx(s, s + len, 0.0))
    }

    /// The ell at one of its host's ends, the program's end or the one toward the middle of the wall first, one query each.
    ///
    /// Research:
    ///     kitchen abuts the house - research/questions/0091-samurai-residences-and-their-rooms-buke-yashiki.html: the kitchen projects from one side of the house as an ell, no corridor, keeping its fire gap from every other building
    ///     the ell's end toward the middle - GUESS: an ell tries its host's end toward the compound's middle first, where the program names no end
    fn seat_ell(&mut self, p: &Program, i: usize, host: &str) -> Result<Bx, Error> {
        let b = &p.buildings[i];
        // the host is seated: the seat order puts an ell straight after its host, and a host with no seat refused the program
        let j = p.buildings.iter().position(|x| x.name == host).unwrap_or(i);
        let hb = self.seats[j].unwrap_or_default();
        let back = back_face(&p.buildings[j]);
        let ends = if back.along_x() {
            [Face::W, Face::E]
        } else {
            [Face::N, Face::S]
        };
        let toward_middle = if back.along_x() {
            if f64::midpoint(hb.0, hb.2) < p.w / 2.0 {
                Face::E
            } else {
                Face::W
            }
        } else if f64::midpoint(hb.1, hb.3)
            < f64::midpoint(court_range(p, b.court).0, court_range(p, b.court).1)
        {
            Face::S
        } else {
            Face::N
        };
        let first = b.end.unwrap_or(toward_middle);
        let order = [first, if ends[0] == first { ends[1] } else { ends[0] }];
        for end in order {
            count("seat@compound_ell", 1);
            let bx = ell_box(hb, back, end, b.w, b.h);
            let hits = self.grid.query(grown(bx, FIRE_GAP), "compound_ell");
            // another building blocks within its fire gap; the host, a ground, a gate or a held ground only where they overlap
            let clear = hits.iter().all(|&e| {
                let other = matches!(self.grid.ents[e].what, What::Building(k) if k != j);
                !other && !overlaps(self.grid.ents[e].bx, bx)
            });
            count("rule_check@compound_ell", 1);
            if clear && inside(p, bx) {
                return Ok(bx);
            }
        }
        Err(refuse(format!(
            "no free end of the {host} for its ell, the {} - move the envelope or the program's knob (room first)",
            b.name
        )))
    }

    /// The building's rules asked and the building filed: its size band and its court (its wall's band holds it to its wall; the coverage
    /// band is the audit's to measure); its row where it touches the wall's face.
    ///
    /// Research:
    ///     the buildings seated - research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.drawing.html: each building held to its size band and kept in its court, its row grown by the fire gap
    fn keep(
        &mut self,
        p: &Program,
        i: usize,
        bx: Bx,
        bands: &[(String, Band)],
    ) -> Result<(), Error> {
        let b = &p.buildings[i];
        count("rule_check@compound_keep", 2);
        if let Some((_, band)) = bands.iter().find(|(k, _)| *k == b.kind) {
            if !band.presence_only() && !band.holds(b.w, b.h) {
                return Err(refuse(format!(
                    "the {} ({} x {} ft) is outside the {} band of the type's declaration",
                    b.name, b.w, b.h, b.kind
                )));
            }
        }
        let (c0, c1) = court_range(p, b.court);
        if bx.1 < c0 - 1e-6 || bx.3 > c1 + 1e-6 {
            return Err(refuse(format!("the {} stands outside its court", b.name)));
        }
        self.grid.file(bx, What::Building(i));
        self.seats[i] = Some(bx);
        self.order.push(i);
        let (strip, _) = band(p, b, 0.0);
        let ((a0, a1), (q0, q1)) = strip.split(bx);
        let touches = (q0 - strip.p0).abs() < 1e-6 || (q1 - strip.p1).abs() < 1e-6;
        if b.rank == 1 && touches {
            let row = self.rows.entry(row_key(b)).or_default();
            insert(&mut row.0, (a0 - FIRE_GAP, a1 + FIRE_GAP), "compound_row");
            row.1 = row.1.max(q1 - q0);
        }
        Ok(())
    }

    /// The middle gate in the divider beside the office hall, at the first stretch whose approach on both sides stands clear, nearest the
    /// hall's middle; its approach filed.
    ///
    /// Research: the middle gate beside the office hall - DEVIATION research/questions/0090-magistrates-compounds-jinya-and-yamen.drawing.html: the docs seat the divider's gate behind the office hall (a GUESS: no page places a jin'ya's middle gate); the hall backs the divider with only the clear ground between, so the gate opens at the first stretch beside it whose approach is clear on both sides, the hall still the privacy baffle between the hearing court and the house
    fn middle_gate(&mut self, p: &Program, hall: Bx) -> Result<(), Error> {
        let reach = DIVIDER_HALF + APPROACH;
        let rule = |e: &super::grid::Ent| match e.what {
            What::Building(_) => Some((CLEAR, 0.0)),
            What::Door(_) | What::Gate => Some((0.0, 0.0)),
            What::Zone(_) | What::Part(..) | What::Held(_) | What::Wall => None,
        };
        let len = p.middle_gate + 2.0 * POST;
        let ask = Ask {
            strip: Strip {
                along_x: true,
                p0: p.divider - reach,
                p1: p.divider + reach,
                lo: WALL_HALF + CLEAR,
                hi: p.w - WALL_HALF - CLEAR,
            },
            len,
            rule: &rule,
            reach: CLEAR,
            f: "compound_middle_gate",
        };
        let from = f64::midpoint(hall.0, hall.2) - len / 2.0;
        let s = nearest(&mut self.grid, &ask, from)
            .ok_or_else(|| refuse("no stretch of the divider holds the middle gate".to_owned()))?;
        self.grid.file(
            (s, p.divider - reach, s + len, p.divider + reach),
            What::Gate,
        );
        self.middle = Some((s + POST, s + POST + p.middle_gate));
        Ok(())
    }

    /// Every seated building's doors: the program's, or one to each dwelling at its middle, or one at the middle of its court face; each
    /// door's step asked clear of every other building and door and filed.
    ///
    /// # Errors
    /// A door whose step another building or door stands in.
    ///
    /// Research:
    ///     a door at each dwelling's middle - GUESS: no page seats a dwelling's door along its face; each at its dwelling's middle (feature 449 T187)
    ///     the default door on the court face - research/questions/0104-the-formal-entrance-and-a-guests-arrival-genkan.html: guest doors feed courts and service doors work space; a building the program gives no door opens at the middle of the face it turns to its court
    pub fn seat_doors(&mut self, p: &Program) -> Result<(), Error> {
        for &i in &self.order.clone() {
            let b = &p.buildings[i];
            let bx = self.seats[i].unwrap_or_default();
            for d in door_specs(b) {
                count("seat@compound_door", 1);
                let door = if d.genkan {
                    genkan_at(i, bx, d.face, d.at)
                } else {
                    door_at(i, bx, d.face, d.at)
                };
                let reach = door.porch.map_or(door.step, |p| union(p, door.step));
                let hits = self.grid.query(reach, "compound_door");
                count("rule_check@compound_door", 1);
                let blocked = hits.iter().any(|&e| match self.grid.ents[e].what {
                    What::Building(k) => k != i,
                    What::Door(_) => true,
                    _ => false,
                });
                if blocked {
                    return Err(refuse(format!(
                        "the {}'s door on its {:?} face opens into another building or door - move the door or the building",
                        b.name, d.face
                    )));
                }
                if let Some(p) = door.porch {
                    self.grid.file(p, What::Building(i));
                }
                self.grid.file(door.step, What::Door(i));
                self.doors.push(door);
            }
        }
        Ok(())
    }
}

/// A gate's passage and held approach inside the wall, its posts included.
///
/// Research:
///     a gate's held approach - GUESS: 12 ft held clear inside the wall across the passage and its posts (the derivation's assumption 6)
#[must_use]
pub fn gate_approach(p: &Program, wall: Face, at: f64, width: f64) -> Bx {
    let (a0, a1) = (at - width / 2.0 - POST, at + width / 2.0 + POST);
    let deep = WALL_HALF + APPROACH;
    match wall {
        Face::S => (a0, p.h - deep, a1, p.h + WALL_HALF),
        Face::N => (a0, -WALL_HALF, a1, deep),
        Face::W => (-WALL_HALF, a0, deep, a1),
        Face::E => (p.w - deep, a0, p.w + WALL_HALF, a1),
    }
}

fn union(a: Bx, b: Bx) -> Bx {
    (a.0.min(b.0), a.1.min(b.1), a.2.max(b.2), a.3.max(b.3))
}

fn grown(b: Bx, g: f64) -> Bx {
    (b.0 - g, b.1 - g, b.2 + g, b.3 + g)
}

/// Research:
///     a building inside its walls - research/questions/0092-compound-walls-neribei-and-tsuijibei.drawing.html: a foot or two clear of the wall's face
fn inside(p: &Program, b: Bx) -> bool {
    let m = WALL_HALF + CLEAR - 1e-6;
    b.0 >= m && b.1 >= m && b.2 <= p.w - m && b.3 <= p.h - m
}

/// An ell's box at `end` of its host, flush with the host's wall-side edge.
///
/// Research:
///     the ell flush with its host - GUESS: an ell's back flush with its host's back at the host's end; no page says how a kitchen ell lines up with its house
#[must_use]
pub fn ell_box(hb: Bx, back: Face, end: Face, w: f64, h: f64) -> Bx {
    match (back, end) {
        (Face::N, Face::W) => (hb.0 - w, hb.1, hb.0, hb.1 + h),
        (Face::N, _) => (hb.2, hb.1, hb.2 + w, hb.1 + h),
        (Face::S, Face::W) => (hb.0 - w, hb.3 - h, hb.0, hb.3),
        (Face::S, _) => (hb.2, hb.3 - h, hb.2 + w, hb.3),
        (Face::W, Face::N) => (hb.0, hb.1 - h, hb.0 + w, hb.1),
        (Face::W, _) => (hb.0, hb.3, hb.0 + w, hb.3 + h),
        (Face::E, Face::N) => (hb.2 - w, hb.1 - h, hb.2, hb.1),
        (Face::E, _) => (hb.2 - w, hb.3, hb.2, hb.3 + h),
    }
}

/// The doors a building opens by: the program's, or none for an open shed, or one at each dwelling's middle on its court face, or one at
/// its court face's middle.
///
/// Research:
///     an open shed doorless - CONVENTION: an open-sided workshop under a roof on posts is entered between its posts, so it is drawn with no door, as the hand sheet's cinnabar workshop is (ochiba-magistracy.svg; 449 T359)
///     a door at each dwelling's middle - GUESS: no page seats a dwelling's door along its face (feature 449 T187); a building's one door at its face's middle
///     the default door on the court face - research/questions/0104-the-formal-entrance-and-a-guests-arrival-genkan.html: guest doors feed courts and service doors work space; a building the program gives no door opens through the face toward its court
#[must_use]
pub fn door_specs(b: &Building) -> Vec<super::spec::DoorSpec> {
    if !b.doors.is_empty() {
        return b.doors.clone();
    }
    if b.interior.as_deref() == Some(super::emit::OPEN_SHED) {
        // an open-sided shed is entered between its posts: no door (449 T359)
        return Vec::new();
    }
    let face = court_face(b);
    let len = if face.along_x() { b.w } else { b.h };
    if b.bays.is_empty() {
        return vec![super::spec::DoorSpec {
            face,
            at: 0.5,
            genkan: false,
        }];
    }
    let mut edges = vec![0.0];
    edges.extend(b.bays.iter().copied());
    edges.push(len);
    edges
        .windows(2)
        .map(|w| super::spec::DoorSpec {
            face,
            at: f64::midpoint(w[0], w[1]) / len,
            genkan: false,
        })
        .collect()
}

/// A door's block and step on `face` of `bx`, its middle at `at` along the face, kept inside the face.
///
/// Research:
///     a door's block - research/questions/0117-doorways-and-doors-to.drawing.html: a door's small block set wholly inside its building, its outer edge on the wall it opens through, 6 ft by about 1.3 ft
#[must_use]
pub fn door_at(b: usize, bx: Bx, face: Face, at: f64) -> Door {
    let (a0, a1) = if face.along_x() {
        (bx.0, bx.2)
    } else {
        (bx.1, bx.3)
    };
    let half = DOOR.0 / 2.0;
    let c = (a0 + at * (a1 - a0)).clamp(a0 + half, (a1 - half).max(a0 + half));
    let (d, s) = (DOOR.1, DOOR_STEP);
    let (block, step) = match face {
        Face::N => (
            (c - half, bx.1, c + half, bx.1 + d),
            (c - half, bx.1 - s, c + half, bx.1),
        ),
        Face::S => (
            (c - half, bx.3 - d, c + half, bx.3),
            (c - half, bx.3, c + half, bx.3 + s),
        ),
        Face::W => (
            (bx.0, c - half, bx.0 + d, c + half),
            (bx.0 - s, c - half, bx.0, c + half),
        ),
        Face::E => (
            (bx.2 - d, c - half, bx.2, c + half),
            (bx.2, c - half, bx.2 + s, c + half),
        ),
    };
    Door {
        b,
        face,
        bx: block,
        step,
        porch: None,
    }
}

/// A formal entrance on `face` of `bx`, its middle at `at` along the face: a porch of [`GENKAN`] built out from the face, and the door
/// on the porch's outer edge, its step before it.
///
/// Research:
///     the genkan built out from the face - research/questions/0104-the-formal-entrance-and-a-guests-arrival-genkan.html: in a warrior's house the projecting board floor where a palanquin was set down was the genkan, and a guest of rank stepped from the palanquin straight into the building, so the porch stands out from the hall and opens onto open ground
#[must_use]
pub fn genkan_at(b: usize, bx: Bx, face: Face, at: f64) -> Door {
    let (a0, a1) = if face.along_x() {
        (bx.0, bx.2)
    } else {
        (bx.1, bx.3)
    };
    let (wide, deep) = GENKAN;
    let c = (a0 + at * (a1 - a0)).clamp(a0 + wide / 2.0, (a1 - wide / 2.0).max(a0 + wide / 2.0));
    let (p0, p1) = (c - wide / 2.0, c + wide / 2.0);
    let porch = match face {
        Face::N => (p0, bx.1 - deep, p1, bx.1),
        Face::S => (p0, bx.3, p1, bx.3 + deep),
        Face::W => (bx.0 - deep, p0, bx.0, p1),
        Face::E => (bx.2, p0, bx.2 + deep, p1),
    };
    let door = door_at(b, porch, face, 0.5);
    Door {
        porch: Some(porch),
        ..door
    }
}
