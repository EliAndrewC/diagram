//! The rest of the parts (derivation T208, "The algorithm"): the privies, the notice board, the shrine's tree, the practice ground's rack
//! and posts, the roji and the kitchen garden's sun - each by its rule against its anchor, one face strip a face tried.
//!
//! Research: the fixtures' plumbing - NONE: lookups and the hatch's box; each fixture's rule is claimed on its unit

#![expect(
    clippy::many_single_char_names,
    reason = "geometry in feet: boxes, edges and points named as the derivation names them"
)]
use l7r_gate_research::Error;

use super::count;
use super::grid::What;
use super::layout::{court_face, Layout, CLEAR, DIVIDER_HALF, POST, WALL_HALF};
use super::parts::{along, face_strip, of_kind, part_rule, rear, seat_in, Privy, Seated};
use super::span::Strip;
use super::spec::{Bx, Face, Program, Wall};

/// A privy's side (feet).
///
/// Research: privy size - GUESS research/questions/0101-privies-setchin.drawing.html#privy-5-ft-square: 5 ft square (15 px), a one-seat privy
pub const PRIVY: f64 = 5.0;
/// How far a privy stands from any well (feet).
///
/// Research: privies away from water - GUESS research/questions/0101-privies-setchin.drawing.html#privy-stands-least-15: at least 15 ft from any well
pub const PRIVY_WELL_FT: f64 = 15.0;
/// The notice board's drawn frame (feet).
///
/// Research:
///     the gate board drawn - GUESS: the bench's board drawn 6 x 1.7 ft, smaller than the measured town frames; no page measures a magistracy's gate board
pub const BOARD: (f64, f64) = (6.0, 5.0 / 3.0);
/// The shrine tree's crown radius, its clearance off the hall (feet).
///
/// Research: shrine tree's crown and seat - GUESS: one 20 ft crown, its trunk within 15 ft of the hall; no source sizes a household god's tree or says how near it stood - the crown 3.5 ft off the hall, clear of a tub and the step before its door, so its trunk stands 13.5 ft off
pub const TREE: (f64, f64) = (10.0, 3.5);
/// The weapon rack (feet).
///
/// Research:
///     practice ground weapon rack - GUESS research/questions/0165-martial-training-grounds-and-dojo.drawing.html: ~8x2 ft rack just inside the practice ground's edge toward the watch's lodging
pub const RACK: (f64, f64) = (8.0, 2.0);
/// A striking post's radius (feet).
///
/// Research: practice ground striking posts - GUESS research/questions/0165-martial-training-grounds-and-dojo.drawing.html#striking-post-small-marker: 1-2 posts, ~1 ft across, drawn as small markers
pub const POST_R: f64 = 2.0 / 3.0;
/// The roji's stepping stones between the middle gate and the shoe stone.
///
/// Research: roji stones - GUESS research/questions/0104-the-formal-entrance-and-a-guests-arrival-genkan.drawing.html: the no-genkan form's stepping-stone path from the middle gate to a stone at the reception's veranda; eleven stones between, the spacing a guess
pub const ROJI_STONES: usize = 11;
/// The shoe stone (feet).
///
/// Research: shoe stone - GUESS: the stone a guest steps up from at the reception's veranda, drawn 4 x 1.7 ft
pub const SHOE: (f64, f64) = (4.0, 5.0 / 3.0);

fn refuse(message: String) -> Error {
    Error::new("ValueError", message)
}

fn room_span(p: &Program, i: usize, bx: Bx, kind: &str, face: Face) -> Option<(f64, f64)> {
    let r = p.buildings[i].rooms.iter().find(|r| r.kind == kind)?;
    Some(if face.along_x() {
        (bx.0 + r.bx.0, bx.0 + r.bx.2)
    } else {
        (bx.1 + r.bx.1, bx.1 + r.bx.3)
    })
}

/// The privies: the house's two attached to its rear face (the guests' behind the reception, the family's at the back corner by the
/// family's rooms), and one against a service wall by each building the program names, each at least 15 ft from any well; a privy against
/// the compound wall takes a hatch through it.
///
///
/// # Errors
/// No room for a privy by its anchor.
///
/// Research:
///     residence privy attached - research/questions/0101-privies-setchin.drawing.html: two, the guests' at the rear of the reception room and the family's at a back corner by the living rooms (a GUESS); each pit toward a service edge, the project's rule
///     outer privies by their buildings - GUESS research/questions/0101-privies-setchin.drawing.html: the page puts them against service walls near a gate for the night-soil cart; a generated plan seats each against the compound wall its building backs, nearest the building's middle, which stands by a gate where the building does
///     the collection hatch - GUESS research/questions/0101-privies-setchin.drawing.html: a hatch through the wall behind a privy against the compound wall, for the collector; none is recorded
pub fn privies(p: &Program, l: &mut Layout, out: &mut Seated) -> Result<(), Error> {
    if let Some((h, hb)) = of_kind(p, l, "residence") {
        let face = rear(p, h);
        let (a0, a1) = along(hb, face);
        let rule = part_rule(p, Some(h), None, 0.0, PRIVY_WELL_FT);
        let guests = room_span(p, h, hb, "reception room", face).unwrap_or((a0, a1));
        let family = room_span(p, h, hb, "family quarters", face).unwrap_or((a0, a1));
        let corner = if f64::midpoint(family.0, family.1) < f64::midpoint(a0, a1) {
            a0
        } else {
            a1
        };
        for ((lo, hi), from) in [
            (guests, f64::midpoint(guests.0, guests.1)),
            (family, corner),
        ] {
            let strip = face_strip(hb, face, 0.0, PRIVY, lo, hi);
            let bx = seat_in(&mut l.grid, strip, PRIVY, &rule, from, "compound_privy").ok_or_else(
                || refuse("no room for the house's privy on its rear face".to_owned()),
            )?;
            l.grid.file(bx, What::Part("privy", None));
            out.privies.push(Privy {
                bx,
                house: true,
                hatch: None,
            });
        }
    }
    for name in &p.parts.privies {
        let (a, ab) = p
            .buildings
            .iter()
            .position(|b| &b.name == name)
            .and_then(|i| l.seats[i].map(|s| (i, s)))
            .ok_or_else(|| refuse(format!("a privy by the {name}, which is not seated")))?;
        let Wall::Side(wall) = p.buildings[a].wall else {
            return Err(refuse(format!(
                "the privy by the {name} wants a compound wall, not the divider"
            )));
        };
        let off = WALL_HALF + CLEAR;
        let (along_x, p0) = match wall {
            Face::N => (true, off),
            Face::S => (true, p.h - off - PRIVY),
            Face::W => (false, off),
            Face::E => (false, p.w - off - PRIVY),
        };
        let (c0, c1) = if along_x {
            (off, p.w - off)
        } else {
            super::layout::court_range(p, p.buildings[a].court)
        };
        let strip = Strip {
            along_x,
            p0,
            p1: p0 + PRIVY,
            lo: c0,
            hi: c1,
        };
        let rule = part_rule(p, None, None, 0.5, PRIVY_WELL_FT);
        let (s0, s1) = along(ab, if along_x { Face::N } else { Face::W });
        let bx = seat_in(
            &mut l.grid,
            strip,
            PRIVY,
            &rule,
            f64::midpoint(s0, s1),
            "compound_privy",
        )
        .ok_or_else(|| {
            refuse(format!(
                "no room for the privy by the {name} against its wall"
            ))
        })?;
        l.grid.file(bx, What::Part("privy", None));
        out.privies.push(Privy {
            bx,
            house: false,
            hatch: Some(hatch(p, bx, wall)),
        });
    }
    Ok(())
}

/// The hatch through the wall behind a privy: 2 ft wide, across the wall's ink.
///
/// Research:
///     the collection hatch - GUESS research/questions/0101-privies-setchin.drawing.html: a hatch through the wall behind the privy, level with its middle, 2 ft wide; none is recorded
fn hatch(p: &Program, bx: Bx, wall: Face) -> Bx {
    let (cx, cy) = (f64::midpoint(bx.0, bx.2), f64::midpoint(bx.1, bx.3));
    match wall {
        Face::N => (cx - 1.0, -WALL_HALF, cx + 1.0, WALL_HALF),
        Face::S => (cx - 1.0, p.h - WALL_HALF, cx + 1.0, p.h + WALL_HALF),
        Face::W => (-WALL_HALF, cy - 1.0, WALL_HALF, cy + 1.0),
        Face::E => (p.w - WALL_HALF, cy - 1.0, p.w + WALL_HALF, cy + 1.0),
    }
}

/// The notice board just outside the main gate, beside its passage.
///
/// Research: notice board at the gate - GUESS research/questions/0190-notice-boards-kosatsuba.drawing.html#magistracy-kept-freestanding-board: the bench's freestanding board just outside the main gate, apart from the town's kosatsuba
pub fn board(p: &Program, l: &mut Layout, out: &mut Seated) {
    if !p.parts.board {
        return;
    }
    let g = &p.gates[0];
    let x1 = g.at - g.width / 2.0 - POST - 2.0;
    let y0 = p.h + WALL_HALF + 1.5;
    let bx = (x1 - BOARD.0, y0, x1, y0 + BOARD.1);
    let _ = l.grid.query(bx, "compound_board");
    count("seat@compound_board", 1);
    out.board = Some(bx);
}

/// The shrine's tree beside the compound shrine: its faces in rank order - the end away from the corner, its court face, the other end -
/// the crown 2 ft off the hall and inside the walls.
///
///
/// # Errors
/// No face of the shrine with room for its tree.
///
/// Research:
///     compound shrine tree - GUESS research/questions/0218-the-compounds-own-shrine-yashikigami.drawing.html#shrine-tree: every compound shrine in a corner of its grounds beside one tree, no grove or garden round it
///     the tree's side - GUESS: the hall's end toward the court's middle first, where the shrine's seat held the tree's ground, then its court face, then its other end
pub fn tree(p: &Program, l: &mut Layout, out: &mut Seated) -> Result<(), Error> {
    let Some((s, sb)) = of_kind(p, l, "compound shrine") else {
        return Ok(());
    };
    let b = &p.buildings[s];
    let cf = court_face(b);
    let ends = if cf.along_x() {
        [Face::W, Face::E]
    } else {
        [Face::N, Face::S]
    };
    let mid = (p.w / 2.0, f64::midpoint(0.0, p.divider));
    let away = if cf.along_x() {
        if f64::midpoint(sb.0, sb.2) < mid.0 {
            Face::E
        } else {
            Face::W
        }
    } else if f64::midpoint(sb.1, sb.3) < mid.1 {
        Face::S
    } else {
        Face::N
    };
    let other = if ends[0] == away { ends[1] } else { ends[0] };
    let (r, off) = TREE;
    let rule = |e: &super::grid::Ent| match &e.what {
        What::Building(k) if *k == s => None,
        What::Held(_) => None,
        What::Zone(i) if super::parts::OPEN_ZONES.contains(&p.zones[*i].kind.as_str()) => None,
        What::Building(_) => Some((0.5, 0.5)),
        _ => Some((0.0, 0.0)),
    };
    let m = WALL_HALF + CLEAR;
    for face in [away, cf, other] {
        let (a0, a1) = along(sb, face);
        let end = if face.along_x() {
            p.w - m
        } else {
            p.divider - DIVIDER_HALF - CLEAR
        };
        let strip = face_strip(sb, face, off, 2.0 * r, (a0 - r).max(m), (a1 + r).min(end));
        let got = seat_in(
            &mut l.grid,
            strip,
            2.0 * r,
            &rule,
            f64::midpoint(a0, a1),
            "compound_tree",
        );
        let Some(bx) = got else {
            continue;
        };
        // the walls' ink is filed, so a crown the strip found stands inside them; its trunk 13.5 ft off the hall by the strip's offset
        let c = (f64::midpoint(bx.0, bx.2), f64::midpoint(bx.1, bx.3));
        l.grid.file(bx, What::Part("tree", Some((c.0, c.1, r))));
        out.tree = Some((c.0, c.1, r));
        return Ok(());
    }
    Err(refuse(
        "no face of the compound shrine has room for its tree".to_owned(),
    ))
}

/// The practice ground's weapon rack flush inside its edge facing the watch's lodging, and its striking posts.
///
///
/// # Errors
/// A rack whose lodging is not seated, or no room for it.
///
/// Research:
///     practice ground placement and gear - research/questions/0165-martial-training-grounds-and-dojo.drawing.html: in the outer court beside the watch, striking posts and a weapon rack
///     the posts' seats - GUESS: the posts spaced evenly along the ground's diagonal, a third and two thirds across for two; no page places them
pub fn practice(p: &Program, l: &mut Layout, out: &mut Seated) -> Result<(), Error> {
    let Some(z) = p.zones.iter().position(|z| z.kind == "practice ground") else {
        return Ok(());
    };
    let g = p.zones[z].bx;
    if let Some(name) = &p.parts.rack_by {
        let ab = p
            .buildings
            .iter()
            .position(|b| &b.name == name)
            .and_then(|i| l.seats[i])
            .ok_or_else(|| refuse(format!("the rack faces the {name}, which is not seated")))?;
        let (ax, ay) = (f64::midpoint(ab.0, ab.2), f64::midpoint(ab.1, ab.3));
        let face = if ax > g.2 {
            Face::E
        } else if ax < g.0 {
            Face::W
        } else if ay < g.1 {
            Face::N
        } else {
            Face::S
        };
        let inner = match face {
            Face::N => (g.0, g.1 - RACK.1, g.2, g.1),
            Face::S => (g.0, g.3, g.2, g.3 + RACK.1),
            Face::W => (g.0 - RACK.1, g.1, g.0, g.3),
            Face::E => (g.2, g.1, g.2 + RACK.1, g.3),
        };
        // the strip just inside the ground's edge: the face of a box one rack deep outside it, turned in
        let strip = face_strip(
            inner,
            face.opposite(),
            0.0,
            RACK.1,
            along(g, face).0,
            along(g, face).1,
        );
        let rule = part_rule(p, None, Some(z), 0.5, 0.5);
        let from = if face.along_x() { ax } else { ay };
        let bx = seat_in(&mut l.grid, strip, RACK.0, &rule, from, "compound_rack")
            .ok_or_else(|| refuse("no room for the weapon rack".to_owned()))?;
        l.grid.file(bx, What::Part("rack", None));
        out.rack = Some(bx);
    }
    for k in 0..p.parts.posts {
        #[expect(clippy::cast_precision_loss, reason = "a post's ordinal")]
        let f = (k as f64 + 1.0) / (p.parts.posts as f64 + 1.0);
        let c = (g.0 + (g.2 - g.0) * f, g.1 + (g.3 - g.1) * f);
        count("seat@compound_post", 1);
        l.grid.file(
            (c.0 - POST_R, c.1 - POST_R, c.0 + POST_R, c.1 + POST_R),
            What::Part("post", Some((c.0, c.1, POST_R))),
        );
        out.posts.push(c);
    }
    Ok(())
}

/// The roji: the shoe stone at the reception's garden face and the stepping stones on one line from the middle gate to it, the line's box
/// asked once clear of every building and part.
///
///
/// # Errors
/// No middle gate or reception, or a building or part on the line.
///
/// Research:
///     genkan - research/questions/0104-the-formal-entrance-and-a-guests-arrival-genkan.html: on the office hall or none with a roji path, a knob; the no-genkan form's middle gate and a stepping-stone path to a stone at the zashiki's veranda
///     roji stones - GUESS: stones about 2 x 1.3 ft laid on one straight line from the middle gate to the shoe stone; no page sizes or lays them
pub fn roji(p: &Program, l: &mut Layout, out: &mut Seated) -> Result<(), Error> {
    if !p.parts.roji {
        return Ok(());
    }
    let (h, hb) =
        of_kind(p, l, "residence").ok_or_else(|| refuse("a roji with no house".to_owned()))?;
    let (m0, m1) = l
        .middle
        .ok_or_else(|| refuse("a roji with no middle gate".to_owned()))?;
    let face = court_face(&p.buildings[h]);
    let (r0, r1) = room_span(p, h, hb, "reception room", face).unwrap_or(along(hb, face));
    let cx = f64::midpoint(r0, r1);
    let y = hb.3;
    let shoe = (cx - SHOE.0 / 2.0, y, cx + SHOE.0 / 2.0, y + SHOE.1);
    let start = (f64::midpoint(m0, m1), p.divider - DIVIDER_HALF - 2.0);
    let end = (cx, y + SHOE.1 + 1.0);
    let line = (
        start.0.min(end.0) - 1.0,
        end.1,
        start.0.max(end.0) + 1.0,
        start.1,
    );
    let hits = l.grid.query(line, "compound_roji");
    count("rule_check@compound_roji", 1);
    let blocked = hits.iter().any(|&e| match l.grid.ents[e].what {
        What::Building(_) | What::Part(..) => true,
        What::Zone(i) => p.zones[i].kind == "vegetable garden",
        _ => false,
    });
    if blocked {
        return Err(refuse(
            "a building or part stands on the roji's line".to_owned(),
        ));
    }
    l.grid.file(shoe, What::Part("shoe stone", None));
    out.shoe = Some(shoe);
    for k in 1..=ROJI_STONES {
        #[expect(clippy::cast_precision_loss, reason = "a stone's ordinal")]
        let f = k as f64 / (ROJI_STONES as f64 + 1.0);
        count("seat@compound_roji", 1);
        let c = (
            start.0 + (end.0 - start.0) * f,
            start.1 + (end.1 - start.1) * f,
        );
        l.grid.file(
            (c.0 - 1.0, c.1 - 0.67, c.0 + 1.0, c.1 + 0.67),
            What::Part("stone", None),
        );
        out.roji.push(c);
    }
    Ok(())
}

/// The kitchen garden's sun: the bed's autumn day walked in half hours as the audit's `garden_sun` walks it, every building, the bath and
/// the privies, the walls and the shrine's tree casting their shadows at the least heights the record gives (a building 20 ft, a small one
/// 6 ft, a wall 5 ft, a tree 33 ft), and the bed held to six lit hours - the one predicate the audit judges the drawn sheet by
/// (`crate::audit::sun`).
///
///
/// # Errors
/// A bed with under six lit hours.
///
/// Research:
///     manor kitchen garden by the sun - research/questions/0109-vegetable-gardens-at-a-samurai-residence-saien.drawing.html, research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: no site with under six hours of direct autumn sun, counted as 0038's six-hour check counts it - each shadow cast at the least height the record gives each thing, a building at the farmhouse ridge's 20 ft, a compound wall at the surviving earth wall's ~5 ft, a tree at a working windbreak's ~33 ft
///     a small roofed thing's 6 ft - GUESS: a built box under 100 sq ft (the bath, a privy) cast at 6 ft, the audit's own rule (`crate::audit::sun::SMALL_BUILDING_FT`); no page gives its height
pub fn garden_sun(p: &Program, l: &Layout, s: &Seated) -> Result<(), Error> {
    use crate::audit::sun::{
        box_ring, circle_ring, lit_hours, Bed, Caster, BUILDING_FT, SMALL_BUILDING_FT,
        SMALL_BUILDING_SQFT, SUN_BED_H, TREE_FT, WALL_FT,
    };
    let ring = |b: Bx| {
        let (a, c) = (super::emit::px(b.0, b.1), super::emit::px(b.2, b.3));
        box_ring(a.0, a.1, c.0, c.1)
    };
    let caster = |b: Bx, height_ft: f64, what: &str| Caster {
        ring: ring(b),
        height_ft,
        what: what.to_owned(),
        tree: false,
    };
    let mut casters: Vec<Caster> = Vec::new();
    let built = l
        .seats
        .iter()
        .flatten()
        .copied()
        .chain(s.bath)
        .chain(s.privies.iter().map(|pr| pr.bx));
    for b in built {
        let small = (b.2 - b.0) * (b.3 - b.1) < SMALL_BUILDING_SQFT;
        casters.push(caster(
            b,
            if small {
                SMALL_BUILDING_FT
            } else {
                BUILDING_FT
            },
            "building",
        ));
    }
    for e in l.grid.ents.iter().filter(|e| e.what == What::Wall) {
        casters.push(caster(e.bx, WALL_FT, "wall"));
    }
    if let Some((x, y, r)) = s.tree {
        let c = super::emit::px(x, y);
        casters.push(Caster {
            ring: circle_ring(c.0, c.1, super::emit::PX * r),
            height_ft: TREE_FT,
            what: "tree".to_owned(),
            tree: true,
        });
    }
    for z in p.zones.iter().filter(|z| z.kind == "vegetable garden") {
        let (a, c) = (
            super::emit::px(z.bx.0, z.bx.1),
            super::emit::px(z.bx.2, z.bx.3),
        );
        let rect = crate::parse::Rect::new(a.0, a.1, c.0 - a.0, c.1 - a.1, "", 0);
        count("rule_check@compound_sun", 1);
        count(
            "exact_test@compound_sun",
            u64::try_from(casters.len()).unwrap_or(u64::MAX),
        );
        let hours = lit_hours(&Bed::new(&rect), &casters, false);
        if hours < SUN_BED_H {
            return Err(refuse(format!(
                "the kitchen garden gets {hours} hours of autumn sun - six hours wanted (0109, 0038's six-hour check)"
            )));
        }
    }
    Ok(())
}
