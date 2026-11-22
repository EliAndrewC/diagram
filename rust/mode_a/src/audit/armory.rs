//! The armory's SITE (feature 449 T303; docs/building-programs.md knob 4): one choice rolled from the map's seed among the sites a sheet
//! offers - the gate range where the main gate is drawn as one, the office hall's west end bay, or a store of its own - and the sheet
//! drawing its armory where the roll says, its `**Form**:` line naming the form. Where a store of its own stands is the sheet's: no
//! source places one, and a seat rule would forbid what the round arbiter's ruling allows (spec-fidelity MODE 4, 2026-11-22).
//!
//! Research:
//!     one choice among the sites a sheet offers - research/questions/0123-the-magistrates-manor-in-a-town-where-it-stands-and-which-way-it-faces-jinya-and-yamen.html, research/questions/0093-the-main-gate-and-its-gatekeepers-nagaya-mon.html: three attested sites for a seat's arms - Kaibara's store of arms a room of its gate range (0093), Pingyao's armory its great hall's west end bay (0123), and a weapons store a building of its own at Nirayama, late Edo, and one named among Hamamashike's storehouses, finished 1860 (0123) - so a knob rolled from the map's seed (the round arbiter's ask:armory-store-ubame, route (a), 2026-11-22: one choice, no nested roll); the gate range is offered only where the main gate is drawn as one, so a one-bay gate's sheet rolls between the hall's bay and a store
//!     the drawn site read from the sheet - NONE: an armory inside the office hall's footprint is the hall's bay, a room of the gate range the main gate's passage runs through is the range's, else a store of its own (a gatehouse beside a one-bay gate offers no range)

use super::checks::main_gate_passage;
use super::labels::footprint;
use crate::compound::roll;
use crate::parse::{ParsedPlan, Rect};
use crate::py::fixed;

/// The roll's key, `<sheet>:armory site` (the docs' formula, as Ubame's and Hayakawa's notes record it, 449 T276).
pub const KEY: &str = "armory site";
/// The three sites, by the names the sheets' notes roll them under.
pub const GATE_RANGE: &str = "gate range";
pub const HALL: &str = "office hall";
pub const STORE: &str = "a store of its own";
/// The `**Form**:` line a sheet declares for the two sites that are not the hall's bay (the armory's forms in `types.json`).
pub const GATE_RANGE_FORM: &str = "armory in the gate range";
pub const STORE_FORM: &str = "armory as a store of its own";

/// The sheet's name the roll is keyed by: its file's stem.
///
/// Research:
///     the roll's sheet name - NONE: a sheet's file stem, the key the roll is read under, deciding nothing
#[must_use]
pub fn stem(path: &str) -> &str {
    let name = path.rsplit('/').next().unwrap_or(path);
    name.strip_suffix(".svg").unwrap_or(name)
}

/// The sites a sheet offers, in the roll's order: the gate range first where the main gate is drawn as one, then the hall's bay, then a
/// store of its own - the order that keeps every pool sheet's two-way roll of 449 T276 (measured 2026-11-22).
///
/// Research:
///     the sites offered - research/questions/0123-the-magistrates-manor-in-a-town-where-it-stands-and-which-way-it-faces-jinya-and-yamen.html, research/questions/0093-the-main-gate-and-its-gatekeepers-nagaya-mon.html: the one choice among the sites a sheet offers - the gate range (0093) only where the main gate is drawn as one, the hall's west end bay (0123), a store of its own (0123)
#[must_use]
pub fn sites(gate_range: bool) -> Vec<String> {
    let all: &[&str] = if gate_range {
        &[GATE_RANGE, HALL, STORE]
    } else {
        &[HALL, STORE]
    };
    all.iter().map(|s| (*s).to_owned()).collect()
}

/// The site the sheet's seed rolls: `random.Random(zlib.crc32(b"<sheet>:armory site")).choice(sites)`.
///
/// Research:
///     the site rolled - research/questions/0123-the-magistrates-manor-in-a-town-where-it-stands-and-which-way-it-faces-jinya-and-yamen.html, research/questions/0093-the-main-gate-and-its-gatekeepers-nagaya-mon.html: the one choice among the sites a sheet offers, rolled from the map's seed as several attested forms are, one choice and no nested roll
#[must_use]
pub fn rolled(sheet: &str, gate_range: bool) -> String {
    roll::choice(sheet, KEY, &sites(gate_range))
        .cloned()
        .unwrap_or_default()
}

/// The `**Form**:` line the site's band is read under: None for the hall's bay, the default band.
#[must_use]
pub fn form_of(site: &str) -> Option<&'static str> {
    match site {
        GATE_RANGE => Some(GATE_RANGE_FORM),
        STORE => Some(STORE_FORM),
        _ => None,
    }
}

/// Whether `r` holds the point.
///
/// Research:
///     a rect holding a point - NONE: geometry, deciding nothing
fn holds(r: &Rect, (x, y): (f64, f64)) -> bool {
    r.x <= x && x <= r.x2() && r.y <= y && y <= r.y2()
}

/// The rect's center.
///
/// Research:
///     a rect's center - NONE: geometry, deciding nothing
fn center(r: &Rect) -> (f64, f64) {
    (r.x + r.w / 2.0, r.y + r.h / 2.0)
}

/// The structures the sheet tags `kind`.
///
/// Research:
///     the structures tagged a kind - NONE: a lookup of the sheet's tags, deciding nothing
fn tagged<'p>(plan: &'p ParsedPlan, kind: &str) -> Vec<&'p Rect> {
    plan.structures
        .iter()
        .filter(|r| plan.label_kinds.get(&r.pos).map(String::as_str) == Some(kind))
        .collect()
}

/// The rooms of the gate range, when the main gate is drawn as one: the gatehouse (or armory) structures the gate's passage runs
/// THROUGH - one holding the passage (Hayakawa's range drawn across it), or one standing at each of the posts across the passage's line
/// (Ubame's two rooms, the passage open between them); empty for a one-bay gate, whose gatehouse stands beside it.
#[must_use]
pub fn range_rooms(plan: &ParsedPlan) -> Vec<&Rect> {
    let posts = &plan.gate_posts;
    let Some(p) = main_gate_passage(plan).into_iter().next() else {
        return Vec::new();
    };
    let mut rooms = tagged(plan, "gatehouse");
    rooms.extend(tagged(plan, "armory"));
    let holding: Vec<&Rect> = rooms.iter().copied().filter(|r| holds(r, p)).collect();
    if !holding.is_empty() {
        return rooms
            .into_iter()
            .filter(|r| holding.iter().any(|h| holds(h, center(r))))
            .collect();
    }
    let lo = |f: fn(&Rect) -> f64| posts.iter().map(f).fold(f64::INFINITY, f64::min);
    let hi = |f: fn(&Rect) -> f64| posts.iter().map(f).fold(f64::NEG_INFINITY, f64::max);
    let (x0, x1, y0, y1) = (lo(|r| r.x), hi(Rect::x2), lo(|r| r.y), hi(Rect::y2));
    // a wall run east-west: a room either side, across the passage's line; north-south, the same turned
    let across = |r: &&Rect| r.y <= p.1 && p.1 <= r.y2();
    let along = |r: &&Rect| r.x <= p.0 && p.0 <= r.x2();
    let west: Vec<&Rect> = rooms
        .iter()
        .copied()
        .filter(across)
        .filter(|r| r.x2() >= x0 && r.x2() <= p.0)
        .collect();
    let east: Vec<&Rect> = rooms
        .iter()
        .copied()
        .filter(across)
        .filter(|r| r.x <= x1 && r.x >= p.0)
        .collect();
    let north: Vec<&Rect> = rooms
        .iter()
        .copied()
        .filter(along)
        .filter(|r| r.y2() >= y0 && r.y2() <= p.1)
        .collect();
    let south: Vec<&Rect> = rooms
        .iter()
        .copied()
        .filter(along)
        .filter(|r| r.y <= y1 && r.y >= p.1)
        .collect();
    if !west.is_empty() && !east.is_empty() {
        return west.into_iter().chain(east).collect();
    }
    if !north.is_empty() && !south.is_empty() {
        return north.into_iter().chain(south).collect();
    }
    Vec::new()
}

/// Whether the main gate is drawn as a gate range ([`range_rooms`]).
#[must_use]
pub fn gate_range_drawn(plan: &ParsedPlan) -> bool {
    !range_rooms(plan).is_empty()
}

/// Where the sheet draws its armory, with its footprint: None without one. Inside the office hall, the hall's bay; a room of the gate
/// range, the gate range; else a store of its own - a gatehouse beside a one-bay gate offers no range, so an armory in it is a store.
#[must_use]
pub fn drawn_site(plan: &ParsedPlan) -> Option<(&'static str, &Rect)> {
    let a = footprint(plan, "armory")?;
    let c = center(a);
    let site = if footprint(plan, "office hall").is_some_and(|r| holds(r, c)) {
        HALL
    } else if range_rooms(plan).iter().any(|r| holds(r, c)) {
        GATE_RANGE
    } else {
        STORE
    };
    Some((site, a))
}

/// The armory stands where the sheet's seed rolls it, its form declared; empty is a pass
/// (a sheet with no armory is the program check's business).
#[must_use]
pub fn armory_site(plan: &ParsedPlan, sheet: &str, form: Option<&str>) -> Vec<String> {
    let Some((site, a)) = drawn_site(plan) else {
        return Vec::new();
    };
    let range = gate_range_drawn(plan);
    let want = rolled(sheet, range);
    let at = format!("svg({},{})", fixed(a.x, 0), fixed(a.y, 0));
    let mut out = Vec::new();
    if site != want {
        out.push(format!(
            "the armory at {at} is drawn as {site:?}, but the sheet's seed rolls {want:?} among {:?} (`{sheet}:{KEY}`)",
            sites(range)
        ));
    }
    let declared = form.filter(|f| [GATE_RANGE_FORM, STORE_FORM].contains(f));
    if declared != form_of(site) {
        out.push(format!(
            "the armory drawn as {site:?} reads its band under the form {:?}, but the notes declare {declared:?}",
            form_of(site)
        ));
    }
    out
}

#[cfg(test)]
mod tests;
