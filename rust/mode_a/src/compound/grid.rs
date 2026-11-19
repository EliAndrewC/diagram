//! The placement grid (derivation T208, "Indexes"): uniform cells over the envelope, each thing filed by its box in every cell the box
//! overlaps as it is seated, a query reading the cells its box overlaps and every entry in them once (a visit stamp), comparing each
//! entry's box with its own. Built once, filed as things are seated, never rebuilt.
//!
//! Research: the grid - NONE: an index, deciding nothing about a building

use super::count_at;
use super::spec::Bx;

/// The grid's cell (feet).
///
/// Research: the grid cell - GUESS: 40 ft, measured by the derivation's script against 15 to 200 ft over both sheets (3,679 operations at 40 ft, the least but 60 ft's 3,593, whose cell is a fifth of the compound and whose queries read a quarter of a court); a knob, not a claim about the place
pub const CELL_FT: f64 = 40.0;

/// What an entry of the grid is.
#[derive(Clone, Debug, PartialEq)]
pub enum What {
    /// A reserved zone of the spine (its index).
    Zone(usize),
    /// A gate's passage and held approach.
    Gate,
    /// A wall's ink: no part stands on it.
    Wall,
    /// A building (its index in the program).
    Building(usize),
    /// A door's mouth and step (the building's index).
    Door(usize),
    /// Ground held for a building's part as the building is seated (the building's index): no other building stands on it.
    Held(usize),
    /// A part: its kind, and its circle where it is one (center and radius).
    Part(&'static str, Option<(f64, f64, f64)>),
}

/// One thing filed.
#[derive(Clone, Debug, PartialEq)]
pub struct Ent {
    /// Its box.
    pub bx: Bx,
    /// What it is.
    pub what: What,
}

/// The grid: its cells over the envelope and every entry filed.
pub struct Grid {
    cols: usize,
    rows: usize,
    cells: Vec<Vec<u32>>,
    stamp: Vec<u32>,
    now: u32,
    /// Every entry, in the order filed.
    pub ents: Vec<Ent>,
}

/// Whether two boxes overlap with some area (touching is not overlapping).
#[must_use]
pub fn overlaps(a: Bx, b: Bx) -> bool {
    a.0 < b.2 && b.0 < a.2 && a.1 < b.3 && b.1 < a.3
}

#[expect(
    clippy::cast_possible_truncation,
    clippy::cast_sign_loss,
    reason = "a cell index, clamped to the grid"
)]
fn cell(v: f64, n: usize) -> usize {
    ((v / CELL_FT).floor().max(0.0) as usize).min(n - 1)
}

impl Grid {
    /// An empty grid over a `w` by `h` envelope.
    #[must_use]
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "a count of cells"
    )]
    pub fn new(w: f64, h: f64) -> Self {
        let cols = ((w / CELL_FT).ceil() as usize).max(1);
        let rows = ((h / CELL_FT).ceil() as usize).max(1);
        Self {
            cols,
            rows,
            cells: vec![Vec::new(); cols * rows],
            stamp: Vec::new(),
            now: 0,
            ents: Vec::new(),
        }
    }

    fn span(&self, b: Bx) -> (usize, usize, usize, usize) {
        (
            cell(b.0, self.cols),
            cell(b.1, self.rows),
            cell(b.2, self.cols),
            cell(b.3, self.rows),
        )
    }

    /// File an entry in every cell its box overlaps; its id.
    pub fn file(&mut self, bx: Bx, what: What) -> usize {
        let id = self.ents.len();
        let (c0, r0, c1, r1) = self.span(bx);
        for r in r0..=r1 {
            for c in c0..=c1 {
                count_at("index_insert", "compound_file", 1);
                self.cells[r * self.cols + c].push(u32::try_from(id).unwrap_or(u32::MAX));
            }
        }
        self.ents.push(Ent { bx, what });
        self.stamp.push(0);
        id
    }

    /// The ids of the entries whose boxes overlap `q`, each read once; counted under `f`.
    pub fn query(&mut self, q: Bx, f: &str) -> Vec<usize> {
        count_at("index_query", f, 1);
        self.now += 1;
        let (c0, r0, c1, r1) = self.span(q);
        let mut out = Vec::new();
        for r in r0..=r1 {
            for c in c0..=c1 {
                count_at("index_cell", f, 1);
                for &id in &self.cells[r * self.cols + c] {
                    let i = id as usize;
                    if self.stamp[i] == self.now {
                        continue;
                    }
                    self.stamp[i] = self.now;
                    count_at("index_entry", f, 1);
                    if overlaps(self.ents[i].bx, q) {
                        out.push(i);
                    }
                }
            }
        }
        out
    }
}
