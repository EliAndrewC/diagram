//! A Mode A sheet read into the audit's geometry (feature 449 T170): `l7r/diagram/tools/pack_audit/parse.py`'s [`parse_svg`] and its
//! records ([`Rect`], [`Label`], [`ParsedPlan`]) ported, the fill, stroke and pattern vocabulary with them. The notes census counts a
//! sheet's fire-water tubs by it ([`crate::census`]); the rest of the audit (`pack_audit`'s checks) is the plan's step 1 to come.
//!
//! Every number and refusal is the Python's: a float is read as `float()` reads it ([`crate::py::float`]), a `min`, `max` or `sum` as
//! Python's, an offset as the Python's code-point offset ([`crate::sheet::Offsets`]), and a malformed sheet is refused with the
//! exception the Python raised, in the order it raised them (FR-002 binds a check's verdict exactly, `engine-plan.md`).
//!
//! LOCKSTEP (`ask:449-engine-order` condition 3): `parse.py` stays the implementation for `pack_audit`'s Python checks, the generators and
//! the page until step 3; an edit of it makes the same change here in the same commit, and `parse/lockstep.rs` holds the two equal on
//! every pool sheet. Its claims stay keyed to the `.py` units (`ask:449-phase4-slices` Q10); each copy here carries the same claim.
//!
//! Research:
//!     the sheet's parse - NONE: a sheet's drawing read into rects and labels by its palette, deciding nothing about a building

use std::collections::{BTreeMap, BTreeSet};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_research::pyre::{py, WORD};
use l7r_gate_research::Error;

use crate::py::{float, max, min};
use crate::sheet::{element_kinds, Offsets};
use crate::tagged::{marks, Mark};

mod labels;
mod shapes;

pub use labels::parse_labels;
pub use shapes::{path_rings, rooms_folded};

/// The court's earth.
pub const INTERIOR_FILL: &str = "url(#court-earth)";
/// The building fills of the palette.
pub const BUILDING_FILLS: [&str; 8] = [
    "#DDB87A", "#C9A57A", "#E8D2A8", "#F2EFE4", "#C9876C", "#B89868", "#8C6F3E", "#6B4030",
];
/// The building patterns.
pub const BUILDING_PATTERNS: [&str; 2] = ["url(#granary-slats)", "url(#colonnade-hatch)"];
/// The hearing court's floor, either form the record allows (feature 267 R22): white gravel, or river cobbles.
pub const COURT_FLOORS: [&str; 2] = ["url(#oshirasu-sand)", "url(#court-cobbles)"];
/// A hearing court drawn ROOFED carries a building's solid outline in this ink (feature 267 R22).
pub const ROOF_STROKES: [&str; 1] = ["#5A3F1E"];
/// The open ground's patterns, the court floors among them.
pub const OPEN_PATTERNS: [&str; 5] = [
    "url(#garden-stipple)",
    "url(#vegetable-rows)",
    "url(#keiko-earth)",
    COURT_FLOORS[0],
    COURT_FLOORS[1],
];
/// The least building mass, px2: below it a rect is furniture.
///
/// Research:
///     building area floor - GUESS: no page gives a least building footprint; a rect under 500 px2 (about 55 sq ft) is furniture, not a building mass.
pub const MIN_BLDG_AREA_PX: f64 = 500.0;
/// The id a sheet declares its precinct by (feature 254, spec FR-002).
pub const PRECINCT_ID: &str = "precinct";
/// The internal court-divider wall's ink.
pub const DIVIDER_STROKE: &str = "#3F3A30";
/// The fire-water tubs' fill (tensuioke, gutter-fed).
pub const FIRE_WATER_FILL: &str = "#8FB0C6";
/// The canopy green a tree is known by (feature 257).
pub const TREE_FILL: &str = "#7A8C5C";
/// The glyph floor: a canopy-green dot smaller than this is a pattern's stipple.
///
/// Research:
///     tree radius floor - NONE: a canopy-green dot under 4 px radius is a pattern's stipple, not a tree, an audit glyph floor.
pub const MIN_TREE_R_PX: f64 = 4.0;
/// A serif glyph's advance as a fraction of the font size (the bbox estimate).
///
/// Research:
///     caption character width - NONE: a serif glyph advances 0.55 of the font size, a text-width estimate for the bbox.
pub const CHAR_W_FRAC: f64 = 0.55;
/// Bold all-caps band labels run widest.
///
/// Research:
///     bold caps character width - NONE: bold all-caps labels advance 0.72 em per character, a text-width figure measured by rendering.
pub const CHAR_W_BOLD: f64 = 0.72;
/// Mixed-case bold (building names) is narrower than caps.
///
/// Research:
///     bold mixed-case character width - NONE: bold mixed-case names advance 0.60 em per character, a text-width figure measured by rendering.
pub const CHAR_W_BOLD_MIXED: f64 = 0.60;
/// A label with at least this share of upper-case letters is a caps label.
///
/// Research:
///     caps label share - NONE: a label with 0.8 or more of its letters upper-case is a caps label, a parser classification.
pub const CAPS_RATIO: f64 = 0.8;
/// The well curb's stone.
pub const WELL_FILL: &str = "#9C8C70";
/// The compound wall's ink (gate posts and well mouths share it).
pub const WALL_STROKE: &str = "#2D2A24";
/// The dark inks: a small rect in one is a door glyph.
pub const DARK_FILLS: [&str; 10] = [
    "#2D2A24", "#3A2010", "#3A2418", "#1A1410", "#4A3318", "#5C0A04", "#3A2E1C", "#6B4030",
    "#5A3F1E", "#5C1A0A",
];
/// A rect below the building floor is furniture.
pub const FURNITURE_MAX_AREA_PX: f64 = MIN_BLDG_AREA_PX;
/// A door glyph is small; a bigger dark rect is a hearth or a block.
///
/// Research:
///     door glyph area ceiling - NONE: a dark rect over 250 px2 is a hearth or block, not a door, a parser classification.
pub const DOOR_MAX_AREA_PX: f64 = 250.0;
/// The fireproof plaster kura's fill: a fire-gap beside it IS correct (feature 449 T175, the audit's gaps and tubs read it).
pub const KURA_FILLS: [&str; 1] = ["#F2EFE4"];
/// Privies, sheds and well curbs: built things with no area floor.
pub const UTILITY_FILLS: [&str; 2] = ["#7E726A", WELL_FILL];

/// Every roofed or built footprint's fill or pattern, with no area floor.
#[must_use]
pub fn is_structure(fill: &str) -> bool {
    BUILDING_FILLS.contains(&fill)
        || BUILDING_PATTERNS.contains(&fill)
        || UTILITY_FILLS.contains(&fill)
}

/// The ink of a wall a structure may abut and never occupy, with its name (`WALL_KIND`).
#[must_use]
pub fn wall_kind(stroke: &str) -> Option<&'static str> {
    match stroke {
        WALL_STROKE => Some("compound wall"),
        DIVIDER_STROKE => Some("court divider"),
        _ => None,
    }
}

/// An axis-aligned rectangle in the sheet's pixels, with its fill, its code-point offset (draw order) and its declared `id`.
#[derive(Debug, Clone, PartialEq, Default)]
pub struct Rect {
    pub x: f64,
    pub y: f64,
    pub w: f64,
    pub h: f64,
    pub fill: String,
    pub pos: i64,
    pub ident: String,
}

impl Rect {
    /// A rect with no declared id.
    #[must_use]
    pub fn new(x: f64, y: f64, w: f64, h: f64, fill: &str, pos: i64) -> Self {
        Self {
            x,
            y,
            w,
            h,
            fill: fill.to_owned(),
            pos,
            ident: String::new(),
        }
    }

    #[must_use]
    pub fn precinct(&self) -> bool {
        self.ident == PRECINCT_ID
    }

    #[must_use]
    pub fn area_px(&self) -> f64 {
        self.w * self.h
    }

    /// Its right edge (feature 449 T175: the audit's checks measure edges).
    #[must_use]
    pub fn x2(&self) -> f64 {
        self.x + self.w
    }

    /// Its bottom edge.
    #[must_use]
    pub fn y2(&self) -> f64 {
        self.y + self.h
    }

    /// Filled as a plaster kura.
    #[must_use]
    pub fn is_kura(&self) -> bool {
        KURA_FILLS.contains(&self.fill.as_str())
    }
}

/// A text label with an ESTIMATED box (px) and its draw-order offset.
#[derive(Debug, Clone, PartialEq)]
pub struct Label {
    pub x: f64,
    pub y: f64,
    pub w: f64,
    pub h: f64,
    pub text: String,
    pub pos: i64,
}

/// The classified geometry of one compound plan.
#[derive(Debug, Clone, PartialEq, Default)]
pub struct ParsedPlan {
    pub interior: Vec<Rect>,
    pub buildings: Vec<Rect>,
    pub open_features: Vec<Rect>,
    pub glyphs: Vec<Rect>,
    pub dividers: Vec<Rect>,
    pub tubs: Vec<Rect>,
    pub labels: Vec<Label>,
    pub wall_segs: Vec<Rect>,
    pub wells: Vec<Rect>,
    pub door_rects: Vec<Rect>,
    pub wall_bands: Vec<Rect>,
    pub structures: Vec<Rect>,
    pub fills: Vec<Rect>,
    pub furniture: Vec<Rect>,
    pub ids: BTreeSet<String>,
    pub trees: Vec<Rect>,
    pub fence_segs: Vec<Rect>,
    pub label_kinds: BTreeMap<i64, String>,
    pub kinds: BTreeSet<String>,
    pub gate_posts: Vec<Rect>,
    pub roofed_courts: Vec<Rect>,
}

impl ParsedPlan {
    /// The rects the sheet marked `id="<ident>"`, in draw order: its fills, then its interior (feature 449 T175).
    #[must_use]
    pub fn by_id(&self, ident: &str) -> Vec<&Rect> {
        self.fills
            .iter()
            .chain(&self.interior)
            .filter(|r| r.ident == ident)
            .collect()
    }

    /// The walled interior's extent, `(minx, miny, maxx, maxy)` - the Python's `bounds` property, which the grid measures size their
    /// grids by (ported with them, feature 449 T174).
    ///
    /// # Errors
    /// No interior: the Python's `min()` of nothing.
    pub fn bounds(&self) -> Result<(f64, f64, f64, f64), Error> {
        let Some(first) = self.interior.first() else {
            return Err(Error::new("ValueError", "min() iterable argument is empty"));
        };
        let start = (first.x, first.y, first.x + first.w, first.y + first.h);
        Ok(self.interior[1..].iter().fold(start, |(a, b, c, d), r| {
            (
                min(a, r.x),
                min(b, r.y),
                max(c, r.x + r.w),
                max(d, r.y + r.h),
            )
        }))
    }
}

static ID: LazyLock<Regex> = LazyLock::new(|| py(r#"\sid="([^"]+)""#));
static CIRCLE: LazyLock<Regex> =
    LazyLock::new(|| py(r#"<circle cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)""#));
static ELLIPSE: LazyLock<Regex> =
    LazyLock::new(|| py(r#"<ellipse cx="([\d.]+)" cy="([\d.]+)" rx="([\d.]+)" ry="([\d.]+)""#));
static DIV_GROUP: LazyLock<Regex> =
    LazyLock::new(|| py(r##"(?s)<g stroke="#3F3A30"[^>]*>(.*?)</g>"##));
static LINE: LazyLock<Regex> = LazyLock::new(|| {
    py(r#"<line x1="([\-\d.]+)" y1="([\-\d.]+)" x2="([\-\d.]+)" y2="([\-\d.]+)""#)
});
static TUB_GROUP: LazyLock<Regex> =
    LazyLock::new(|| py(r##"(?s)<g fill="#8FB0C6"[^>]*>(.*?)</g>"##));
static FENCE_GROUP: LazyLock<Regex> = LazyLock::new(|| {
    py(&format!(
        r#"(?s)<g[^>{WORD}](?:[^>]*[^>{WORD}])?id="fence"[^>]*>(.*?)</g>"#
    ))
});
static WALL_GROUP: LazyLock<Regex> =
    LazyLock::new(|| py(r##"(?s)<g stroke="#2D2A24"[^>]*>(.*?)</g>"##));

/// The thin rects of the lines inside each match of `group`: a segment, at least 2 px either way.
///
/// Research:
///     its salts, guards and sentinels - NONE: they decide nothing about the place - 2.0 (a wall, fence or divider segment's least thickness, px)
fn segments(group: &Regex, text: &str) -> Result<Vec<Rect>, Error> {
    let mut out = Vec::new();
    for grp in group.captures_iter(text).flatten() {
        for ln in LINE.captures_iter(&grp[1]).flatten() {
            let mut v = [0.0; 4];
            for (i, slot) in v.iter_mut().enumerate() {
                *slot = float(&ln[i + 1])?;
            }
            let [x1, y1, x2, y2] = v;
            out.push(Rect::new(
                min(x1, x2),
                min(y1, y2),
                max((x2 - x1).abs(), 2.0),
                max((y2 - y1).abs(), 2.0),
                "",
                // the Python's `Rect(...)` takes the default `pos`
                -1,
            ));
        }
    }
    Ok(out)
}

/// Every match's three or four numbers as floats.
fn numbers<const N: usize>(c: &fancy_regex::Captures<'_>) -> Result<[f64; N], Error> {
    let mut v = [0.0; N];
    for (i, slot) in v.iter_mut().enumerate() {
        *slot = float(&c[i + 1])?;
    }
    Ok(v)
}

fn cp(offsets: &Offsets, byte: usize) -> i64 {
    i64::try_from(offsets.at(byte)).unwrap_or(i64::MAX)
}

/// Parse a sheet into interior, building, open-feature and point-glyph rects, labels and walls.
///
/// Research:
///     its guard - NONE: a sheet with no rect marked `id="precinct"` is refused before anything else is read of it, deciding nothing about the place
///
/// # Errors
/// The Python's refusals, in its order: a sheet with no rect marked `id="precinct"`, a number `float()` refuses, a path's missing
/// coordinate, an unbalanced sheet, a wall line or roofed court missing an attribute.
pub fn parse_svg(text: &str) -> Result<ParsedPlan, Error> {
    let rects = shapes::rects(text, true)?;
    precinct(&rects)?;
    parse_with(text, &rects, None)
}

fn precinct(rects: &[Rect]) -> Result<(), Error> {
    if rects.iter().any(Rect::precinct) {
        return Ok(());
    }
    Err(Error::new(
        "ValueError",
        format!("no rect marked id=\"{PRECINCT_ID}\" in the SVG - a Mode A sheet declares its precinct on the rect(s) bounding the ground the checks reason over (feature 254)"),
    ))
}

/// [`parse_svg`] over the marks a caller already read ([`crate::census::sheet_counts`] reads them first, as the Python's did through
/// its memo); the rects are read and the precinct checked here, before the marks are used, in the Python's order.
///
/// # Errors
/// As [`parse_svg`].
pub fn parse_marked(text: &str, marked: &[Mark]) -> Result<ParsedPlan, Error> {
    let rects = shapes::rects(text, true)?;
    precinct(&rects)?;
    parse_with(text, &rects, Some(marked))
}

/// The point glyphs, fences, dividers, tubs and walls, read in the Python's order (so its first refusal is this port's).
struct Ink {
    glyphs: Vec<Rect>,
    fence_segs: Vec<Rect>,
    dividers: Vec<Rect>,
    tubs: Vec<Rect>,
    wall_segs: Vec<Rect>,
}

/// [`Ink`] read from the sheet.
///
/// Research:
///     its salts, guards and sentinels - NONE: they decide nothing about the place - 4.0 (a point glyph's least radius, px)
fn ink(text: &str, offsets: &Offsets, trees: &[Rect]) -> Result<Ink, Error> {
    let tree_pos: BTreeSet<i64> = trees.iter().map(|t| t.pos).collect();
    let mut glyphs = Vec::new();
    for c in CIRCLE.captures_iter(text).flatten() {
        let [cx, cy, rad] = numbers::<3>(&c)?;
        let at = cp(offsets, c.get(0).map_or(0, |m| m.start()));
        if rad >= 4.0 && !tree_pos.contains(&at) {
            glyphs.push(Rect::new(cx - rad, cy - rad, 2.0 * rad, 2.0 * rad, "", at));
        }
    }
    let fence_segs = segments(&FENCE_GROUP, text)?;
    for e in ELLIPSE.captures_iter(text).flatten() {
        let [ex, ey, rx, ry] = numbers::<4>(&e)?;
        let at = cp(offsets, e.get(0).map_or(0, |m| m.start()));
        glyphs.push(Rect::new(ex - rx, ey - ry, 2.0 * rx, 2.0 * ry, "", at));
    }
    let dividers = segments(&DIV_GROUP, text)?;
    let mut tubs = Vec::new();
    for grp in TUB_GROUP.captures_iter(text).flatten() {
        let (whole, inner) = (grp.get(0), grp.get(1));
        let (start, inner_at) = (
            whole.map_or(0, |m| m.start()),
            inner.map_or(0, |m| m.start()),
        );
        for c in CIRCLE.captures_iter(&grp[1]).flatten() {
            let [cx, cy, rad] = numbers::<3>(&c)?;
            // the Python's `grp.start() + c.start()`: the group's offset plus the circle's within the group's BODY
            let within = c.get(0).map_or(0, |m| m.start());
            let at = cp(offsets, start) + cp(offsets, inner_at + within) - cp(offsets, inner_at);
            tubs.push(Rect::new(
                cx - rad,
                cy - rad,
                2.0 * rad,
                2.0 * rad,
                FIRE_WATER_FILL,
                at,
            ));
        }
    }
    let wall_segs = segments(&WALL_GROUP, text)?;
    Ok(Ink {
        glyphs,
        fence_segs,
        dividers,
        tubs,
        wall_segs,
    })
}

/// The parse past the precinct; the marks read where the Python read them (after the walls) when no caller read them first.
fn parse_with(text: &str, rects: &[Rect], marked: Option<&[Mark]>) -> Result<ParsedPlan, Error> {
    let offsets = Offsets::new(text);
    let interior: Vec<Rect> = rects.iter().filter(|r| r.precinct()).cloned().collect();
    let buildings = rooms_folded(
        rects
            .iter()
            .filter(|r| {
                (BUILDING_FILLS.contains(&r.fill.as_str())
                    || BUILDING_PATTERNS.contains(&r.fill.as_str()))
                    && r.area_px() >= MIN_BLDG_AREA_PX
            })
            .cloned()
            .collect(),
    );
    let open_features = rects
        .iter()
        .filter(|r| OPEN_PATTERNS.contains(&r.fill.as_str()))
        .cloned()
        .collect();
    let trees = shapes::trees(text, &offsets)?;
    let Ink {
        glyphs,
        fence_segs,
        dividers,
        tubs,
        wall_segs,
    } = ink(text, &offsets, &trees)?;
    let wells = rects
        .iter()
        .filter(|r| r.fill == WELL_FILL)
        .cloned()
        .collect();
    let fills: Vec<Rect> = rects.iter().filter(|r| !r.precinct()).cloned().collect();
    let furniture = fills
        .iter()
        .filter(|r| r.area_px() < FURNITURE_MAX_AREA_PX)
        .cloned()
        .collect();
    // a kamado tagged `hearth` shares a door's ink and size; the sheet says what it is (feature 374 wave 113)
    let read;
    let marked = if let Some(m) = marked {
        m
    } else {
        read = marks(text)?;
        &read
    };
    let hearths: BTreeSet<i64> = marked
        .iter()
        .filter(|m| m.tag == "rect" && m.kind.as_deref() == Some("hearth"))
        .map(|m| m.pos)
        .collect();
    let door_rects = rects
        .iter()
        .filter(|r| {
            DARK_FILLS.contains(&r.fill.as_str())
                && r.area_px() < DOOR_MAX_AREA_PX
                && !hearths.contains(&r.pos)
        })
        .cloned()
        .collect();
    let kinds = element_kinds(text)?;
    let labels = parse_labels(text)?;
    let wall_bands = shapes::wall_bands(text, &offsets)?;
    let structures = rects
        .iter()
        .filter(|r| is_structure(&r.fill))
        .cloned()
        .collect();
    let ids = ID
        .captures_iter(text)
        .flatten()
        .map(|c| c[1].to_owned())
        .collect();
    let gate_posts = shapes::rects(text, false)?
        .into_iter()
        .filter(|r| kinds.get(&r.pos).map(String::as_str) == Some("main gate"))
        .collect();
    let roofed_courts = shapes::roofed_courts(text, &offsets)?;
    Ok(ParsedPlan {
        interior,
        buildings,
        open_features,
        glyphs,
        dividers,
        tubs,
        labels,
        wall_segs,
        wells,
        door_rects,
        wall_bands,
        structures,
        fills,
        furniture,
        ids,
        trees,
        fence_segs,
        kinds: kinds.values().cloned().collect(),
        label_kinds: kinds,
        gate_posts,
        roofed_courts,
    })
}

#[cfg(test)]
mod check_fixtures;
#[cfg(test)]
pub(crate) mod fixtures;
#[cfg(test)]
pub(crate) mod lockstep;
#[cfg(test)]
mod lockstep_audit;
#[cfg(test)]
mod lockstep_checks;
#[cfg(test)]
mod lockstep_keep;
#[cfg(test)]
mod tests;
