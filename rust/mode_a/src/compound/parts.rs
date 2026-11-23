//! The parts seated (derivation T208, "The algorithm"): each part by its rule against its anchor, one face strip asked of the grid per
//! face tried, its faces in rank order, the first free span read off - the bath on the kitchen's service side, the wells by use, the
//! fire-water tubs beside the doors of the wooden buildings. The privies, the board, the shrine tree, the practice ground's gear and the
//! roji are [`super::fixtures`].
//!
//! Research: the parts' plumbing - NONE: the strips, gap rules and lookups each seat is asked through; each seat's rule is claimed on its unit

#![expect(
    clippy::many_single_char_names,
    reason = "geometry in feet: boxes, edges and points named as the derivation names them"
)]
use l7r_gate_research::Error;

use super::count;
use super::grid::{Ent, Grid, What};
use super::layout::{back_face, court_face, Door, Layout};
use super::roll;
use super::span::{nearest, Ask, Strip};
use super::spec::{Bx, Face, Program};

/// A fire-water tub's radius (feet).
///
/// Research: tub glyph - GUESS research/questions/0100-fire-and-the-fireproof-storehouses-dozo.drawing.html: a tub about 2.5 ft across (~r3.8 px at 3 px = 1 ft)
pub const TUB_R: f64 = 3.8 / 3.0;
/// A tub's glyph off its wall (feet).
///
/// Research: tub seat off the wall - CONVENTION: the glyph seated ~2.2 px (~0.7 ft at 3 px = 1 ft) off the wall, its outline clear of the wall's ink
pub const TUB_OFF: f64 = 2.2 / 3.0;
/// The well's curb marker (feet).
///
/// Research: well curb size - CONVENTION: the curb drawn ~22x22 px (~7.3 ft), a marker larger than the ~4 ft curb it stands for, as 0196's drawing page draws its wells
pub const CURB: f64 = 22.0 / 3.0;
/// The ground a well keeps: its curb, and its rolled roof's posts round it (feet).
///
/// Research: the roof's outline round the curb - research/questions/0196-communal-wells-ido.drawing.html: a roof on four corner posts over the curb, drawn about 30 px square, so a well keeps that ground
pub const WELL_KEEP: f64 = 30.0 / 3.0;
/// How far the kitchen's well may stand from the kitchen (feet).
///
/// Research: kitchen well - GUESS research/questions/0105-baths-furo.drawing.html: on a generated plan past the bath within 20 ft of the kitchen; no page places a samurai kitchen's well
pub const KITCHEN_WELL_FT: f64 = 20.0;
/// A tub's center within this of a door of its building (feet).
///
/// Research: tub within 10.5 ft of a door - research/questions/0100-fire-and-the-fireproof-storehouses-dozo.drawing.html: within about 10 ft, a CONVENTION of this project - the kitchen's two tubs side by side at one 6 ft door put the far one ~10.2 ft off
pub const TUB_DOOR_FT: f64 = crate::compound::TUB_DOOR_MAX_FT;
/// The grounds no small part stands on: the roofed hearing court, the practice ground, a worked bed and the garden.
///
/// Research: parts off the spine's grounds - research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.drawing.html: the named courts stay open, so no part stands in the garden, the hearing court (roofed: a tub there is inside a building), the practice ground or a worked bed except a part that belongs there (a garden's well, the practice ground's gear); the yards and the bare court ground take parts
pub const OPEN_ZONES: [&str; 4] = ["outer court", "inner court", "cart yard", "rear yard"];

/// A well seated: its curb, its use and its rolled gear and roof.
#[derive(Clone, Debug, PartialEq)]
pub struct Well {
    /// The curb.
    pub bx: Bx,
    /// Its use: kitchen, garden or stables.
    pub use_: String,
    /// Its lifting gear.
    pub gear: String,
    /// Whether it is roofed.
    pub roof: bool,
}

/// A privy: its box, whether it is the house's own, and the collection hatch through a wall it stands against.
#[derive(Clone, Debug, PartialEq)]
pub struct Privy {
    /// Its box.
    pub bx: Bx,
    /// Attached to the house.
    pub house: bool,
    /// The hatch through the compound wall.
    pub hatch: Option<Bx>,
}

/// Every part seated, and the rolls the sheet took.
#[derive(Clone, Debug, PartialEq, Default)]
pub struct Seated {
    /// The bath.
    pub bath: Option<Bx>,
    /// The wells.
    pub wells: Vec<Well>,
    /// The tubs' centers.
    pub tubs: Vec<(f64, f64)>,
    /// The privies.
    pub privies: Vec<Privy>,
    /// The notice board.
    pub board: Option<Bx>,
    /// The shrine tree: its trunk and its crown's radius.
    pub tree: Option<(f64, f64, f64)>,
    /// The weapon rack.
    pub rack: Option<Bx>,
    /// The striking posts.
    pub posts: Vec<(f64, f64)>,
    /// The roji's stones.
    pub roji: Vec<(f64, f64)>,
    /// The shoe stone.
    pub shoe: Option<Bx>,
    /// The rolls: key, value.
    pub rolls: Vec<(String, String)>,
    /// What the generator reports and did not refuse.
    pub notes: Vec<String>,
}

/// The rule a part's strip keeps: its anchor and its host ground ignored, every building `bg` off, every well `wg` off, doors, gates and
/// the closed grounds edge to edge, other parts half a foot off.
pub fn part_rule(
    p: &Program,
    anchor: Option<usize>,
    host: Option<usize>,
    bg: f64,
    wg: f64,
) -> impl Fn(&Ent) -> Option<(f64, f64)> + '_ {
    move |e: &Ent| match &e.what {
        What::Building(k) if Some(*k) == anchor => None,
        What::Building(_) => Some((bg, bg)),
        What::Held(_) => None,
        What::Zone(i) if Some(*i) == host || OPEN_ZONES.contains(&p.zones[*i].kind.as_str()) => {
            None
        }
        What::Wall | What::Door(_) | What::Gate | What::Zone(_) => Some((0.0, 0.0)),
        What::Part("well", _) => Some((wg, wg)),
        What::Part(..) => Some((0.5, 0.5)),
    }
}

/// A face's strip: `off` out from the face, `depth` deep, over `[lo, hi]` along it.
#[must_use]
pub fn face_strip(a: Bx, f: Face, off: f64, depth: f64, lo: f64, hi: f64) -> Strip {
    let (along_x, p0) = match f {
        Face::N => (true, a.1 - off - depth),
        Face::S => (true, a.3 + off),
        Face::W => (false, a.0 - off - depth),
        Face::E => (false, a.2 + off),
    };
    Strip {
        along_x,
        p0,
        p1: p0 + depth,
        lo,
        hi,
    }
}

/// A face's extent along it.
#[must_use]
pub fn along(a: Bx, f: Face) -> (f64, f64) {
    if f.along_x() {
        (a.0, a.2)
    } else {
        (a.1, a.3)
    }
}

/// A part of `len` along a strip, nearest `from` (a point along it): its box.
pub fn seat_in(
    grid: &mut Grid,
    strip: Strip,
    len: f64,
    rule: &dyn Fn(&Ent) -> Option<(f64, f64)>,
    from: f64,
    f: &'static str,
) -> Option<Bx> {
    let ask = Ask {
        strip,
        len,
        rule,
        reach: 15.5,
        f,
    };
    nearest(grid, &ask, from - len / 2.0).map(|s| strip.bx(s, s + len, 0.0))
}

fn refuse(message: String) -> Error {
    Error::new("ValueError", message)
}

/// The index of the first building of `kind`.
#[must_use]
pub fn of_kind(p: &Program, l: &Layout, kind: &str) -> Option<(usize, Bx)> {
    p.buildings
        .iter()
        .position(|b| b.kind == kind)
        .and_then(|i| l.seats[i].map(|s| (i, s)))
}

/// The bath on the kitchen's service side: against its court face, from the end by the house.
///
///
/// # Errors
/// No kitchen, or no room on its service side.
///
/// Research:
///     bath - research/questions/0105-baths-furo.html, research/questions/0105-baths-furo.drawing.html: a room or small addition on the service side by kitchen and well; drawn 10 x 8 ft, a GUESS
///     the bath by the house - GUESS: against the kitchen's court face from the end nearer the residence; no page places a bath along its kitchen
pub fn bath(p: &Program, l: &mut Layout, out: &mut Seated) -> Result<(), Error> {
    let Some((w, h)) = p.parts.bath else {
        return Ok(());
    };
    let (k, kb) =
        of_kind(p, l, "kitchen").ok_or_else(|| refuse("a bath with no kitchen".to_owned()))?;
    let face = court_face(&p.buildings[k]);
    let (a0, a1) = along(kb, face);
    let (len, depth) = if face.along_x() { (w, h) } else { (h, w) };
    let house = of_kind(p, l, "residence").map(|(_, hb)| hb);
    let from = house.map_or(a0, |hb| {
        let (h0, h1) = along(hb, face);
        if f64::midpoint(h0, h1) < f64::midpoint(a0, a1) {
            a0 + len / 2.0
        } else {
            a1 - len / 2.0
        }
    });
    let rule = part_rule(p, Some(k), None, 0.0, 0.0);
    let strip = face_strip(kb, face, 0.0, depth, a0, a1);
    let bx = seat_in(&mut l.grid, strip, len, &rule, from, "compound_bath")
        .ok_or_else(|| refuse("no room for the bath on the kitchen's service side".to_owned()))?;
    l.grid.file(bx, What::Part("bath", None));
    out.bath = Some(bx);
    Ok(())
}

/// The water's depth: the landform the notes record, or rolled.
///
/// Research: water depth from the landform - GUESS research/questions/0196-communal-wells-ido.drawing.html: a valley floor or river plain shallow, an upland or terrace deep; a sheet whose notes record no landform rolls it
fn depth(p: &Program, out: &mut Seated) -> String {
    let d = match p.parts.landform.as_deref() {
        Some("valley floor" | "river plain") => "shallow".to_owned(),
        Some(_) => "deep".to_owned(),
        None => {
            let forms = ["shallow".to_owned(), "deep".to_owned()];
            roll::choice(&p.name, "water depth", &forms)
                .cloned()
                .unwrap_or_default()
        }
    };
    out.rolls.push(("water depth".to_owned(), d.clone()));
    d
}

/// The wells by use - the kitchen's past the bath within 20 ft of the kitchen, the garden's in the garden, the stables' just outside them
/// - each with its gear and roof rolled from the sheet's seed.
///
///
/// # Errors
/// A well's anchor missing, or no room by it.
///
/// Research:
///     wells by use - GUESS research/questions/0105-baths-furo.drawing.html: the kitchen well by the kitchen, kept with the kitchen and bath on the project's reading
///     garden and stables wells - GUESS: a well for the garden and one for the stables; no page places them
///     well gear a knob - research/questions/0196-communal-wells-ido.drawing.html: a sweep or a pulley frame over the curb, about three wells in four taking the gear the water's depth favors (a sweep over shallow water, a pulley frame over deep), rolled per sheet
///     a roof on one well in three - research/questions/0196-communal-wells-ido.drawing.html: a roof on about one well in three, rolled per sheet
pub fn wells(p: &Program, l: &mut Layout, out: &mut Seated) -> Result<(), Error> {
    if p.parts.wells.is_empty() {
        return Ok(());
    }
    let water = depth(p, out);
    for (n, use_) in p.parts.wells.iter().enumerate() {
        let keep = match use_.as_str() {
            "kitchen" => kitchen_well(p, l, out)?,
            "garden" => garden_well(p, l)?,
            _ => stables_well(p, l)?,
        };
        l.grid.file(keep, What::Part("well", None));
        let i = n + 1;
        let favored = if water == "shallow" {
            "sweep"
        } else {
            "pulley frame"
        };
        let other = if water == "shallow" {
            "pulley frame"
        } else {
            "sweep"
        };
        let gear = if roll::chance(&p.name, &format!("well gear {i}"), 0.75) {
            favored
        } else {
            other
        };
        let roof = roll::chance(&p.name, &format!("well roof {i}"), 1.0 / 3.0);
        out.rolls.push((format!("well gear {i}"), gear.to_owned()));
        out.rolls.push((
            format!("well roof {i}"),
            if roof { "roof" } else { "open" }.to_owned(),
        ));
        let (cx, cy) = (f64::midpoint(keep.0, keep.2), f64::midpoint(keep.1, keep.3));
        let half = CURB / 2.0;
        out.wells.push(Well {
            bx: (cx - half, cy - half, cx + half, cy + half),
            use_: use_.clone(),
            gear: gear.to_owned(),
            roof,
        });
    }
    Ok(())
}

/// Research: kitchen well - GUESS research/questions/0105-baths-furo.drawing.html: on a generated plan past the bath within 20 ft of the kitchen; no page places a samurai kitchen's well
fn kitchen_well(p: &Program, l: &mut Layout, out: &Seated) -> Result<Bx, Error> {
    let (k, kb) = of_kind(p, l, "kitchen")
        .ok_or_else(|| refuse("a kitchen well with no kitchen".to_owned()))?;
    let face = court_face(&p.buildings[k]);
    // past the bath: out from the bath's own outer face where there is a bath, else out from the kitchen's
    let anchor = out.bath.unwrap_or(kb);
    let (a0, a1) = along(anchor, face);
    let rule = part_rule(p, Some(k), None, 0.5, 0.5);
    let strip = face_strip(
        anchor,
        face,
        0.5,
        WELL_KEEP,
        a0 - KITCHEN_WELL_FT / 2.0,
        a1 + KITCHEN_WELL_FT / 2.0,
    );
    let bx = seat_in(
        &mut l.grid,
        strip,
        WELL_KEEP,
        &rule,
        f64::midpoint(a0, a1),
        "compound_well",
    )
    .ok_or_else(|| refuse("no room for the kitchen's well past the bath".to_owned()))?;
    count("rule_check@compound_well", 1);
    let gap = crate::compound::gap(bx, kb);
    if gap > KITCHEN_WELL_FT {
        return Err(refuse(format!(
            "the kitchen's well stands {gap:.1} ft from the kitchen, past 20 ft"
        )));
    }
    Ok(bx)
}

/// Research:
///     garden well - GUESS: searched, the record silent (feature 417 T36 pass P4, 2026-10-25); in the inner garden, along its north edge from its east end
fn garden_well(p: &Program, l: &mut Layout) -> Result<Bx, Error> {
    let z = p
        .zones
        .iter()
        .position(|z| z.kind == "garden")
        .ok_or_else(|| refuse("a garden well with no garden".to_owned()))?;
    let g = p.zones[z].bx;
    // inside the garden, along its north edge: its east end first
    let strip = Strip {
        along_x: true,
        p0: g.1 + 1.0,
        p1: g.1 + 1.0 + WELL_KEEP,
        lo: g.0 + 1.0,
        hi: g.2 - 1.0,
    };
    let rule = part_rule(p, None, Some(z), 0.5, 0.5);

    seat_in(&mut l.grid, strip, WELL_KEEP, &rule, g.2, "compound_well")
        .ok_or_else(|| refuse("no room for the garden's well in the garden".to_owned()))
}

/// Research:
///     stables well - GUESS: searched, the record silent (feature 417 T36 pass P4, 2026-10-25); just outside the stables for watering, before its court face and within that face's own span, its ground never past the building's ends (449 T384: seated from 4 ft past the face's west end, the county example's stables' well stood over the lane's mouth beside them)
///     the well at its face's low end - GUESS: searched, the record silent (feature 417 T36 pass P4, 2026-10-25); seated at the first free place from the court face's west (or north) end (`seat_in` from `a0`), so it stands at the end a default gable door opens on
fn stables_well(p: &Program, l: &mut Layout) -> Result<Bx, Error> {
    let (s, sb) = of_kind(p, l, "stables")
        .ok_or_else(|| refuse("a stables well with no stables".to_owned()))?;
    let face = court_face(&p.buildings[s]);
    let (a0, a1) = along(sb, face);
    let rule = part_rule(p, Some(s), None, 0.5, 0.5);
    let strip = face_strip(sb, face, 1.0, WELL_KEEP, a0, a1);

    seat_in(&mut l.grid, strip, WELL_KEEP, &rule, a0, "compound_well")
        .ok_or_else(|| refuse("no room for the stables' well before the stables".to_owned()))
}

/// The buildings that take a tub, and how many: every wooden building one, the kitchen two, the plaster kura none.
///
/// Research:
///     one tub per wooden building - research/questions/0100-fire-and-the-fireproof-storehouses-dozo.drawing.html: ~8-12 tubs, one at each wooden building
///     kitchen weighting - research/questions/0100-fire-and-the-fireproof-storehouses-dozo.drawing.html: 2 tubs at the kitchen
///     no tub at the plaster kura - research/questions/0100-fire-and-the-fireproof-storehouses-dozo.drawing.html: none at the kura, one may stand at a wooden granary
#[must_use]
pub fn tubs_owed(p: &Program, i: usize) -> usize {
    let b = &p.buildings[i];
    count("rule_check@compound_tubs_owed", 1);
    match (b.role.as_str(), b.kind.as_str()) {
        ("kura", _) => 0,
        (_, "kitchen") => 2,
        _ => 1,
    }
}

/// The fire-water tubs: each beside a door of its building on the door's face, nearest the door, else round the nearer corner; the bath's on
/// its yard side. A building the audit names (`program_rules::TUB_KINDS`) with no seat refuses the program; another is reported.
///
///
/// # Errors
/// A building the audit holds to a tub with no seat beside its door.
///
/// Research:
///     tub against its wall - research/questions/0100-fire-and-the-fireproof-storehouses-dozo.drawing.html: tubs stand at the wooden buildings, at the entrance - each beside a door of its building
///     a short face's tub round the corner nearest its door - GUESS: no source could speak to it, a value of ours; a face that leaves no seat beside its door takes the tub round the nearer corner, still within the 10.5 ft
///     tub clear of the footprint - CANON: the GM's ruling of 2026-07-25, tightened 2026-07-26, no part of a tub glyph in a building's footprint
///     a bath's tub judged by no door - research/questions/0100-fire-and-the-fireproof-storehouses-dozo.drawing.html: a bath is entered from the house, so its tub stands on its yard side, the kitchen's court face; else at an end, tried in a fixed order by that face - the west end before the east where the yard side faces north or south, the north end before the south where it faces east or west (the ends and their order a GUESS)
pub fn tubs(p: &Program, l: &mut Layout, out: &mut Seated) -> Result<(), Error> {
    for &i in &l.order.clone() {
        let doors: Vec<Door> = l.doors.iter().filter(|d| d.b == i).cloned().collect();
        let bx = l.seats[i].unwrap_or_default();
        for _ in 0..tubs_owed(p, i) {
            let seat = doors.iter().find_map(|d| tub_by_door(p, l, i, bx, d));
            match seat {
                Some(c) => file_tub(l, out, c),
                None if crate::audit::program_rules::TUB_KINDS
                    .contains(&p.buildings[i].kind.as_str()) =>
                {
                    return Err(refuse(format!(
                        "no seat for the {}'s fire-water tub beside its door - give the door room",
                        p.buildings[i].name
                    )));
                }
                None => out.notes.push(format!(
                    "the {} takes no tub: no seat beside its door",
                    p.buildings[i].name
                )),
            }
        }
    }
    if let Some(bb) = out.bath {
        let k = of_kind(p, l, "kitchen").map(|(k, _)| k);
        let face = k.map_or(Face::S, |k| court_face(&p.buildings[k]));
        let ends = if face.along_x() {
            [Face::W, Face::E]
        } else {
            [Face::N, Face::S]
        };
        let rule = part_rule(p, None, None, 0.3, 0.5);
        let seat = [face, ends[0], ends[1]].into_iter().find_map(|f| {
            let (a0, a1) = along(bb, f);
            let strip = face_strip(bb, f, TUB_OFF, 2.0 * TUB_R, a0, a1);
            seat_in(
                &mut l.grid,
                strip,
                2.0 * TUB_R,
                &rule,
                f64::midpoint(a0, a1),
                "compound_tub",
            )
        });
        match seat {
            Some(t) => file_tub(l, out, (f64::midpoint(t.0, t.2), f64::midpoint(t.1, t.3))),
            None => out
                .notes
                .push("the bath takes no tub: no seat on its yard side or its ends".to_owned()),
        }
    }
    Ok(())
}

fn file_tub(l: &mut Layout, out: &mut Seated, c: (f64, f64)) {
    let b = (c.0 - TUB_R, c.1 - TUB_R, c.0 + TUB_R, c.1 + TUB_R);
    l.grid.file(b, What::Part("tub", Some((c.0, c.1, TUB_R))));
    out.tubs.push(c);
}

/// A tub's seat beside a door: on the door's face within reach, else on the face round the nearer corner.
///
/// Research: tub beside its door - research/questions/0100-fire-and-the-fireproof-storehouses-dozo.drawing.html: each tub beside a door of its building, within 10.5 ft (a CONVENTION of this project), round the nearer corner where the face has no seat (a GUESS)
fn tub_by_door(p: &Program, l: &mut Layout, i: usize, bx: Bx, d: &Door) -> Option<(f64, f64)> {
    let rule = part_rule(p, Some(i), None, 0.3, 0.5);
    let (dx, dy) = d.mid();
    let c = if d.face.along_x() { dx } else { dy };
    let (a0, a1) = along(bx, d.face);
    let reach = TUB_DOOR_FT - TUB_R;
    let strip = face_strip(
        bx,
        d.face,
        TUB_OFF,
        2.0 * TUB_R,
        (c - reach).max(a0),
        (c + reach).min(a1),
    );
    // the audit's own two predicates: beside a door of its building, by its eaves
    let fits = |t: (f64, f64)| {
        count("rule_check@compound_tub", 2);
        crate::compound::tub_by_its_door(t, &[(dx, dy)]) && crate::compound::tub_by_its_eaves(t, bx)
    };
    let mid = |b: Bx| (f64::midpoint(b.0, b.2), f64::midpoint(b.1, b.3));
    if let Some(t) = seat_in(&mut l.grid, strip, 2.0 * TUB_R, &rule, c, "compound_tub").map(mid) {
        return fits(t).then_some(t);
    }
    // round the nearer corner
    let (corner, side) = if c - a0 <= a1 - c {
        (a0, if d.face.along_x() { Face::W } else { Face::N })
    } else {
        (a1, if d.face.along_x() { Face::E } else { Face::S })
    };
    let (s0, s1) = along(bx, side);
    let near_start = d.face == Face::N || d.face == Face::W;
    let toward = if near_start { s0 } else { s1 };
    let span = (reach - (c - corner).abs()).max(2.0 * TUB_R);
    let (lo, hi) = if near_start {
        (s0, (s0 + span).min(s1))
    } else {
        ((s1 - span).max(s0), s1)
    };
    let strip = face_strip(bx, side, TUB_OFF, 2.0 * TUB_R, lo, hi);
    let t = seat_in(
        &mut l.grid,
        strip,
        2.0 * TUB_R,
        &rule,
        toward,
        "compound_tub",
    )
    .map(mid)?;
    fits(t).then_some(t)
}

/// The house's rear face: the face it turns to its wall.
#[must_use]
pub fn rear(p: &Program, i: usize) -> Face {
    back_face(&p.buildings[i])
}
