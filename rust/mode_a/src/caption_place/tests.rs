//! The placer's rules (feature 449 T202), each on a small sheet where the rule decides: research/questions/0242's and 0330's drawing
//! pages, one test a rule.
//!
//! Research: the placer's rule tests - NONE: tests of the rules claimed where the placer decides them, deciding nothing themselves

use std::fmt::Write as _;

use super::captions::{declared, feature_angle};
use super::geom::{bbox, block, dist, Bx, Pt};
use super::search::{How, Seat};
use super::{placed, seat, Caption};
use crate::labels::hand_sheet::read_sheet;

mod angles;

/// A sheet of `body` over a view `w` x `h`.
fn sheet(w: u32, h: u32, body: &str) -> String {
    format!(
        r##"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}"><rect x="0" y="0" width="{w}" height="{h}" fill="#EFE3C2" data-kind="-"/>{body}</svg>"##
    )
}

fn seats(src: &str) -> Vec<(Caption, Seat)> {
    let (shapes, view) = read_sheet(src).unwrap();
    seat(src, &shapes, view).unwrap()
}

/// The seat of the caption whose words are `text`.
fn of<'a>(all: &'a [(Caption, Seat)], text: &str) -> &'a Seat {
    &all.iter().find(|(c, _)| c.text() == text).unwrap().1
}

/// Do two boxes stand apart (touching at most)?
fn apart(a: Bx, b: Bx) -> bool {
    let eps = 1e-6;
    !(a.0 < b.2 - eps && b.0 < a.2 - eps && a.1 < b.3 - eps && b.1 < a.3 - eps)
}

fn block_box(s: &Seat) -> Bx {
    bbox(&block(s.center, s.w, s.h, s.angle))
}

/// A building of `kind` at `x, y`, `w` x `h`, filled and stroked, with its caption inside.
fn building(kind: &str, (x, y, w, h): (u32, u32, u32, u32), caption: &str) -> String {
    format!(
        r##"<g data-kind="{kind}"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#DDB87A" stroke="#5A3F1E" stroke-width="1"/><text font-size="8">{caption}</text></g>"##
    )
}

/// A well: a disc of radius 5 at `cx, cy` with its caption.
fn well(cx: u32, cy: u32, caption: &str) -> String {
    format!(
        r##"<g data-kind="well"><circle cx="{cx}" cy="{cy}" r="5" fill="#9C8C70"/><text font-size="8">{caption}</text></g>"##
    )
}

/// A plain blocking building with no caption.
fn block_at((x, y, w, h): (u32, u32, u32, u32)) -> String {
    format!(
        r##"<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#C9A57A" data-kind="storehouse"/>"##
    )
}

/// 0242: a feature large enough to hold its name is named on itself, over its middle.
#[test]
fn a_large_feature_is_named_over_its_middle() {
    let all = seats(&sheet(
        400,
        300,
        &building("hall", (100, 100, 120, 60), "hall"),
    ));
    let s = of(&all, "hall");
    assert_eq!(s.how, How::Inside(0.0));
    assert!(dist(s.center, (160.0, 130.0)) < 1e-9, "{:?}", s.center);
    assert!(s.leader.is_none());
}

/// 0242: a small feature is named beside it, directly above first, half the letter height off its drawn edge.
#[test]
fn a_small_feature_is_named_above_it_at_the_usual_gap() {
    let all = seats(&sheet(400, 300, &well(200, 150, "well")));
    let s = of(&all, "well");
    assert_eq!(s.how, How::Gap(0));
    let b = block_box(s);
    assert!((145.0 - b.3 - 4.0).abs() < 1e-9);
    assert!((s.center.0 - 200.0).abs() < 1e-9);
}

/// 0242: the ranked places in the readers' order - above, then below, then right.
#[test]
fn the_places_are_tried_in_the_readers_order() {
    let above = block_at((185, 120, 30, 19));
    let all = seats(&sheet(
        400,
        300,
        &format!("{above}{}", well(200, 150, "well")),
    ));
    assert_eq!(of(&all, "well").how, How::Gap(1), "above taken: below");
    let below = block_at((185, 161, 30, 19));
    let all = seats(&sheet(
        400,
        300,
        &format!("{above}{below}{}", well(200, 150, "well")),
    ));
    assert_eq!(of(&all, "well").how, How::Gap(2));
}

/// 0242: a place that would run off the edge of the picture is never taken.
#[test]
fn a_place_off_the_picture_is_never_taken() {
    let all = seats(&sheet(400, 300, &well(200, 8, "well")));
    let s = of(&all, "well");
    assert_eq!(s.how, How::Gap(1));
    assert!(block_box(s).1 >= 0.0);
}

/// 0242: at the usual gap a caption stands nearer its own feature than any other - a place with another building within a gap of it is
/// refused, though nothing covers it.
#[test]
fn at_the_usual_gap_a_caption_stands_nearer_its_own_feature() {
    // a building just above where the caption would stand, clear of it by under the 4 px gap
    let near = block_at((170, 118, 60, 12));
    let all = seats(&sheet(
        400,
        300,
        &format!("{near}{}", well(200, 150, "well")),
    ));
    assert_eq!(of(&all, "well").how, How::Gap(1));
}

/// 0242 and 0330: every place at the usual gap taken, the same places are tried further out; within twice the gap no leader is drawn.
#[test]
fn a_step_out_within_twice_the_gap_has_no_leader() {
    // every place at the usual gap taken - a lid 0.5 px under the place above, buildings on the other seven - and the place a step out
    // (1.5 gaps) clear of the lid by 0.5 px: nearer the lid than its own disc, which a place at the usual gap may not be, and taken
    let walls = [
        block_at((150, 158, 100, 58)),
        block_at((150, 100, 40, 116)),
        block_at((210, 100, 40, 116)),
        // and a building farther above in the same chunk, past the free offset: the scan stops before it
        block_at((185, 100, 30, 10)),
    ]
    .concat();
    let lid = r##"<rect x="195" y="139.5" width="10" height="2" fill="#C9A57A" data-kind="lid"/>"##;
    let all = seats(&sheet(
        400,
        300,
        &format!("{walls}{lid}{}", well(200, 150, "well")),
    ));
    let s = of(&all, "well");
    assert!(matches!(s.how, How::Swept(d, 0) if (d - 6.0).abs() < 1e-6));
    assert!(s.leader.is_none());
    assert!(139.5 - block_box(s).3 < s.h / 2.0);
}

/// 0330: a caption more than twice the usual gap from its feature is tied to it by a leader ending on the feature's drawn edge.
#[test]
fn past_twice_the_gap_a_leader_ends_on_the_drawn_edge() {
    let walls = [
        block_at((150, 100, 100, 44)),
        block_at((150, 156, 100, 60)),
        block_at((120, 100, 74, 116)),
        block_at((206, 100, 74, 116)),
    ]
    .concat();
    let all = seats(&sheet(
        400,
        300,
        &format!("{walls}{}", well(200, 150, "well")),
    ));
    let s = of(&all, "well");
    let d = s.how.offset().unwrap();
    assert!(d > 8.0);
    let (a, b) = s.leader.expect("a leader past twice the gap");
    assert!((dist(b, (200.0, 150.0)) - 5.0).abs() < 1e-6);
    let bx = block_box(s);
    assert!(a.0 >= bx.0 - 1e-6 && a.0 <= bx.2 + 1e-6 && a.1 >= bx.1 - 1e-6 && a.1 <= bx.3 + 1e-6);
}

/// 0242: fields, gardens and open ground are not in the way at all.
#[test]
fn open_ground_never_blocks() {
    let court = r##"<rect x="100" y="100" width="200" height="100" fill="#E8D9B0" data-kind="outer court"/>"##;
    let all = seats(&sheet(
        400,
        300,
        &format!("{court}{}", well(200, 150, "well")),
    ));
    assert_eq!(of(&all, "well").how, How::Gap(0));
}

/// 0242: a ground's drawn border is ink though its floor is free (a dashed garden edge is not written over).
#[test]
fn a_grounds_drawn_border_is_ink() {
    let garden = r##"<rect x="150" y="128" width="100" height="10" fill="none" stroke="#7A9A5A" stroke-width="1" data-kind="garden"/>"##;
    let all = seats(&sheet(
        400,
        300,
        &format!("{garden}{}", well(200, 150, "well")),
    ));
    assert_ne!(of(&all, "well").how, How::Gap(0));
}

/// 0242: a caption never covers another caption while any other choice exists.
#[test]
fn a_caption_never_covers_another() {
    let all = seats(&sheet(
        400,
        300,
        &format!("{}{}", well(200, 150, "well"), well(200, 140, "tub")),
    ));
    let (a, b) = (block_box(of(&all, "well")), block_box(of(&all, "tub")));
    assert!(!(a.0 < b.2 && b.0 < a.2 && a.1 < b.3 && b.1 < a.3));
}

/// 0242: with no free ground, a caption still goes down where it covers the least - a road crossed at half a building, before a
/// building - and never off the picture.
#[test]
fn with_no_free_ground_it_covers_the_least_a_way_before_a_building() {
    let road = r##"<rect x="0" y="0" width="100" height="25" fill="#C8B080" data-kind="road"/>"##;
    let rest = [
        block_at((0, 25, 46, 35)),
        block_at((54, 25, 46, 35)),
        block_at((46, 36, 8, 24)),
    ]
    .concat();
    let src = format!(
        r#"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 60">{road}{rest}{}</svg>"#,
        well(50, 30, "well")
    );
    let all = seats(&src);
    let s = of(&all, "well");
    assert_eq!(s.how, How::CoverLeast(0.5));
    assert!(block_box(s).3 <= 25.0 + 1e-6);
}

/// 0242: a caption breaks across lines where one line would not fit its feature, cut where the longest line is shortest.
#[test]
fn a_caption_wraps_to_fit_its_feature() {
    let river = r##"<g data-kind="river"><rect data-id="r" x="300" y="0" width="60" height="300" fill="#9CB4C8"/><text font-size="10" data-names="r">the swift river</text></g>"##;
    let all = seats(&sheet(400, 300, river));
    let s = of(&all, "the swift river");
    assert_eq!(s.how, How::Inside(0.0));
    let cut = s.cut.clone().unwrap();
    assert_eq!(cut.len(), 2, "{cut:?}");
    let out = placed(&sheet(400, 300, river)).unwrap();
    assert!(out.contains("<tspan"), "{out}");
}

/// 0242: two names on one feature - the second takes the nearest free row off the middle.
#[test]
fn a_second_name_takes_the_nearest_free_row() {
    let river = r##"<g data-kind="river"><rect data-id="r" x="300" y="0" width="80" height="300" fill="#9CB4C8"/><text font-size="10" data-names="r">river</text><text font-size="10" data-names="r">east bank</text></g>"##;
    let all = seats(&sheet(400, 300, river));
    let (a, b) = (of(&all, "river"), of(&all, "east bank"));
    assert_eq!(a.how, How::Inside(0.0));
    let d = b.how.offset().unwrap();
    assert!(d > 0.0 && b.center.1 < a.center.1);
}

/// 0242: among loose parts, a caption is seated beside the box holding them all, never on the bare ground between them.
#[test]
fn loose_parts_are_named_beside_their_box() {
    let tubs = r##"<g data-kind="fire-water tubs"><circle cx="100" cy="150" r="4" fill="#7A9AB0"/><circle cx="260" cy="150" r="4" fill="#7A9AB0"/><text font-size="8">tubs</text></g>"##;
    let all = seats(&sheet(400, 300, tubs));
    assert_eq!(of(&all, "tubs").how, How::Gap(0));
}

/// 0242: a caption is plainly the name of its feature and no other - a building's name avoids a named room inside it.
#[test]
fn a_name_avoids_another_named_area_on_its_feature() {
    let src = sheet(
        400,
        300,
        r##"<g data-kind="hall"><rect x="100" y="100" width="160" height="80" fill="#DDB87A"/><text font-size="8">hall</text></g><g data-kind="study"><rect x="150" y="120" width="60" height="40" fill="none"/><text font-size="6">study</text></g>"##,
    );
    let all = seats(&src);
    let (hall, study) = (of(&all, "hall"), of(&all, "study"));
    assert_eq!(study.how, How::Inside(0.0));
    let h = block_box(hall);
    assert!(
        h.2 <= 150.0 + 1e-6 || h.0 >= 210.0 - 1e-6 || h.3 <= 120.0 + 1e-6 || h.1 >= 160.0 - 1e-6
    );
}

/// 0242: a ground's name set on another named ground reads as naming it; a building's name on open ground does not.
#[test]
fn a_grounds_name_avoids_another_named_ground() {
    let src = sheet(
        400,
        300,
        r##"<g data-kind="inner court"><rect x="0" y="0" width="400" height="300" fill="#E8D9B0"/><text font-size="10">COURT</text></g><g data-kind="garden"><rect x="150" y="120" width="100" height="60" fill="#BCD0A0"/><text font-size="8">garden</text></g>"##,
    );
    let all = seats(&src);
    let court = block_box(of(&all, "COURT"));
    assert!(apart(court, (150.0, 120.0, 250.0, 180.0)));
}

/// Anything painted after a caption lies over it: open ground drawn later hides the middle of the building it names.
#[test]
fn ink_painted_after_a_caption_hides_it() {
    let src = sheet(
        400,
        300,
        &format!(
            "{}{}",
            building("hall", (100, 100, 160, 80), "hall"),
            r##"<rect x="150" y="120" width="60" height="40" fill="#BCD0A0" data-kind="garden"/>"##
        ),
    );
    let all = seats(&src);
    let s = of(&all, "hall");
    let b = block_box(s);
    assert!(
        b.2 <= 150.0 + 1e-6 || b.0 >= 210.0 - 1e-6 || b.3 <= 120.0 + 1e-6 || b.1 >= 160.0 - 1e-6
    );
}

/// A part another caption names is that caption's: a building's name is not set on its own room that a room's caption names.
#[test]
fn a_part_another_caption_names_is_theirs() {
    let src = sheet(
        400,
        300,
        r##"<rect data-id="a" x="100" y="100" width="160" height="80" fill="#DDB87A" stroke="#5A3F1E" stroke-width="1"/><rect data-id="b" x="140" y="110" width="80" height="60" fill="#C9A57A"/><g data-kind="hall"><text font-size="8" data-names="a b">hall</text></g><g data-kind="room"><text font-size="6" data-names="b">room</text></g>"##,
    );
    let all = seats(&src);
    let h = block_box(of(&all, "hall"));
    assert!(
        h.2 <= 140.0 + 1e-6 || h.0 >= 220.0 - 1e-6 || h.3 <= 110.0 + 1e-6 || h.1 >= 170.0 - 1e-6
    );
}

/// A caption naming nothing drawn has no feature to stand by: refused, naming it.
#[test]
fn a_caption_naming_nothing_is_refused() {
    let src = sheet(
        100,
        100,
        r#"<g data-kind="well"><text font-size="8" data-names="gone">well</text></g>"#,
    );
    let (shapes, view) = read_sheet(&src).unwrap();
    let e = seat(&src, &shapes, view).unwrap_err();
    assert!(e.message.contains("well"), "{}", e.message);
}

/// The declared captions: a `data-cont` line joins the caption before it; furniture at its own `x` is no declaration.
#[test]
fn the_declarations_are_read_as_declared() {
    let src = sheet(
        400,
        300,
        r##"<text x="10" y="20" font-size="20" data-kind="-">Title</text><g data-kind="hall"><rect x="100" y="100" width="160" height="80" fill="#DDB87A"/><text font-size="10">reception</text><text font-size="8" data-cont="1">(zashiki)</text></g>"##,
    );
    let (shapes, view) = read_sheet(&src).unwrap();
    assert_eq!(seat(&src, &shapes, view).unwrap().len(), 1);
    let caps = declared(&shapes);
    assert_eq!(caps.len(), 1);
    assert_eq!(caps[0].text(), "reception (zashiki)");
    assert_eq!(caps[0].elems.len(), 2);
    assert!(!caps[0].cuttable());
    assert!(caps[0].head() > 0);
    assert!(feature_angle(&shapes, &caps[0].parts).abs() < 1e-9);
}

/// The placed text: each line element at its seat, the declaration's marks dropped, a leader marked and kinded after the caption.
#[test]
fn the_placed_text_writes_each_line_and_its_leader() {
    let walls = [
        block_at((150, 100, 100, 44)),
        block_at((150, 156, 100, 60)),
        block_at((120, 100, 74, 116)),
        block_at((206, 100, 74, 116)),
    ]
    .concat();
    let src = sheet(
        400,
        300,
        &format!(
            r##"{walls}<circle data-id="w" cx="200" cy="150" r="5" fill="#9C8C70"/>
  <text font-size="8" fill="#123456" data-kind="well" data-names="w">well</text><text font-size="6" data-cont="1">deep</text>"##
        ),
    );
    let out = placed(&src).unwrap();
    assert!(!out.contains("data-cont") && !out.contains("data-names"));
    assert!(out.contains("text-anchor=\"middle\" font-size=\"8\" fill=\"#123456\" data-kind=\"well\">well</text>"), "{out}");
    assert!(out.contains("data-kind=\"well\" data-leader=\"1\"/>"));
    assert!(out.contains("stroke=\"#123456\""), "{out}");
    assert!(out.contains("\n  <line"));
}

/// A sheet written with a namespace prefix keeps it on what is written.
#[test]
fn a_prefixed_sheet_keeps_its_prefix() {
    let src = r##"<s:svg xmlns:s="http://www.w3.org/2000/svg" viewBox="0 0 400 300"><s:g data-kind="hall"><s:rect x="100" y="100" width="40" height="20" fill="#DDB87A"/><s:text font-size="8">a long name for it</s:text></s:g></s:svg>"##;
    let out = placed(src).unwrap();
    assert!(out.contains("<s:text x="), "{out}");
}

/// A placed caption's seat and its leader are written in the frame of the group the caption stands in.
#[test]
fn a_seat_is_written_in_its_groups_frame() {
    let src = sheet(
        400,
        300,
        r##"<g transform="translate(100 50)"><g data-kind="hall"><rect x="0" y="0" width="120" height="60" fill="#DDB87A"/><text font-size="8">hall</text></g></g>"##,
    );
    let out = placed(&src).unwrap();
    assert!(out.contains("<text x=\"60.0\""), "{out}");
}

/// An empty text element (written `<text .../>`) is rewritten in place.
#[test]
fn a_self_closed_text_is_rewritten() {
    let src = sheet(
        400,
        300,
        r##"<g data-kind="hall"><rect x="100" y="100" width="120" height="60" fill="#DDB87A"/><text font-size="8"/></g>"##,
    );
    let out = placed(&src).unwrap();
    assert!(out.contains("text-anchor=\"middle\""), "{out}");
}

/// A leader point's helper: nothing further to check than the seat's own block.
#[test]
fn a_blocks_corners_hold_its_center() {
    let q = block((1.0, 2.0), 4.0, 2.0, 0.0);
    let c: Pt = (f64::midpoint(q[0].0, q[2].0), f64::midpoint(q[0].1, q[2].1));
    assert_eq!(c, (1.0, 2.0));
}

/// 0242: a place at the usual gap whose neighbor's box comes near but whose ink stands far off it is nearer its own feature.
#[test]
fn a_neighbor_a_full_gap_away_does_not_refuse_the_usual_gap() {
    // a disc beside the place above, its box within a gap of the block's box but its curve a full gap off
    // an L whose box holds the place above, its ink 60 px off it
    let l = r##"<polygon points="100,60 300,60 300,70 110,70 110,135 100,135" fill="#555" data-kind="wall"/>"##;
    let all = seats(&sheet(400, 300, &format!("{l}{}", well(200, 150, "well"))));
    assert_eq!(of(&all, "well").how, How::Gap(0));
}

/// What blocks: a filled polygon, and an unfilled outline by its stroke alone (its floor free).
#[test]
fn a_polygon_and_an_unfilled_outline_block_by_their_ink() {
    let poly =
        r##"<polygon points="170,120 230,120 230,142 170,142" fill="#555" data-kind="shed"/>"##;
    let all = seats(&sheet(
        400,
        300,
        &format!("{poly}{}", well(200, 150, "well")),
    ));
    assert_eq!(of(&all, "well").how, How::Gap(1));
    let frame = r##"<rect x="150" y="125" width="100" height="50" fill="none" stroke="#333" stroke-width="1" data-kind="fence"/>"##;
    let all = seats(&sheet(
        400,
        300,
        &format!("{frame}{}", well(200, 150, "well")),
    ));
    assert_eq!(of(&all, "well").how, How::Gap(0));
}

/// A ground painted between two captions hides only the earlier one; a named garden is no obstacle to a building's name.
#[test]
fn ground_hides_only_what_it_is_painted_over() {
    let src = sheet(
        400,
        300,
        &format!(
            "{}{}{}{}",
            building("hall", (20, 20, 60, 40), "hall"),
            r##"<rect x="150" y="100" width="100" height="40" fill="#BCD0A0" data-kind="garden"/>"##,
            r##"<g data-kind="garden"><rect x="150" y="160" width="100" height="40" fill="#BCD0A0"/><text font-size="8">garden</text></g>"##,
            well(200, 150, "well")
        ),
    );
    let all = seats(&src);
    assert_eq!(of(&all, "well").how, How::Gap(0));
}

/// The view clips the search: a feature at the picture's edge is searched only where its block stays on the picture, and a place whose
/// still axis runs off the picture is dead.
#[test]
fn the_pictures_edge_clips_every_search() {
    // a long hall running off the top, its middle on the picture blocked: the rows above run off first
    let src = sheet(
        400,
        300,
        &format!(
            r##"<g data-kind="hall"><rect x="100" y="-40" width="200" height="100" fill="#DDB87A"/><text font-size="8">hall</text></g>{}"##,
            block_at((100, 2, 200, 16))
        ),
    );
    let all = seats(&src);
    assert!(matches!(of(&all, "hall").how, How::Inside(d) if d > 0.0));
    // a well at the left edge: the places above and below would run off it
    let all = seats(&sheet(400, 300, &well(4, 150, "a well by the edge")));
    assert!(block_box(of(&all, "a well by the edge")).0 >= 0.0);
    // a hall mostly off the picture, too little of it on the picture for its name
    let src = sheet(
        400,
        300,
        r##"<g data-kind="hall"><rect x="-80" y="100" width="100" height="40" fill="#DDB87A"/><text font-size="8">a hall</text></g>"##,
    );
    assert!(!matches!(of(&seats(&src), "a hall").how, How::Inside(_)));
    // a picture narrower than the caption: nowhere on it
    let all = seats(&sheet(
        30,
        300,
        &building("hall", (0, 100, 30, 40), "a very long hall name"),
    ));
    assert!(matches!(
        of(&all, "a very long hall name").how,
        How::CoverLeast(_)
    ));
}

/// An outline that is not a box: a free place in its notch is not on it, so the search goes on to a row that is.
#[test]
fn a_place_in_an_outlines_notch_is_not_on_it() {
    let l = r##"<g data-kind="hall"><polygon points="100,100 300,100 300,140 160,140 160,200 100,200" fill="#DDB87A"/><text font-size="8">hall</text></g>"##;
    let pillar = block_at((190, 105, 20, 30));
    let all = seats(&sheet(400, 300, &format!("{l}{pillar}")));
    let s = of(&all, "hall");
    assert!(matches!(s.how, How::Inside(_)), "{:?}", s.how);
    let (shapes, _) = read_sheet(&sheet(400, 300, l)).unwrap();
    let outline = &shapes.iter().find(|x| x.tag == "polygon").unwrap().poly;
    assert!(super::geom::inside(s.center, outline), "{:?}", s.center);
}

/// A feature whose every inside place is taken, and every place beside it: it covers least, its middle among the places scored; a
/// caption that cuts into lines clears the place with its cut.
#[test]
fn the_last_resort_scores_the_middle_and_cuts_where_that_clears() {
    let hall = r##"<g data-kind="hall"><rect x="10" y="10" width="40" height="20" fill="#DDB87A"/><text font-size="8">the hall</text></g><g data-kind="hearth"><rect x="20" y="10" width="20" height="20" fill="#333"/><text font-size="1">h</text></g>"##;
    let src = format!(
        r#"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 60 40">{hall}{}</svg>"#,
        [
            block_at((0, 0, 60, 10)),
            block_at((0, 30, 60, 10)),
            block_at((0, 10, 10, 20)),
            block_at((50, 10, 10, 20))
        ]
        .concat()
    );
    let all = seats(&src);
    let s = of(&all, "the hall");
    assert!(matches!(s.how, How::CoverLeast(c) if c > 0.0));
    assert!(s.cut.is_none());
    // a picture narrower than the caption's one line, its feature near the foot: no place is on it, and the middle moved onto it
    let src = r##"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 12 40"><g data-kind="post"><circle cx="6" cy="38" r="1" fill="#555"/><text font-size="6">abcdefgh</text></g></svg>"##;
    let all = seats(src);
    let s = of(&all, "abcdefgh");
    assert_eq!(s.how, How::CoverLeast(f64::INFINITY));
    assert_eq!(s.how.offset(), None);
    assert!(block_box(s).3 <= 40.0 + 1e-6);
}

/// The sweep's intervals: an obstacle further out along a direction than its first free offset ends the scan there.
#[test]
fn the_sweep_stops_at_the_first_free_offset() {
    // a box of buildings round the disc, open above past y = 100: the nearest free offset is above, 45 px off the disc's box, the block's
    // foot on the buildings' top edge - not the farther ones the strip also reads
    let walls = [
        block_at((150, 100, 100, 44)),
        block_at((150, 156, 100, 60)),
        block_at((120, 100, 74, 116)),
        block_at((206, 140, 74, 76)),
        block_at((206, 100, 20, 38)),
        block_at((240, 100, 40, 38)),
    ]
    .concat();
    let all = seats(&sheet(
        400,
        300,
        &format!("{walls}{}", well(200, 150, "well")),
    ));
    let s = of(&all, "well");
    assert!(matches!(s.how, How::Swept(d, 0) if (d - 45.0).abs() < 1e-5));
    assert!((block_box(s).3 - 100.0).abs() < 1e-5);
    assert!(s.leader.is_some());
}

/// A building's name may lie on a named garden; only another ground's name may not.
#[test]
fn a_buildings_name_may_lie_on_a_named_ground() {
    let src = sheet(
        500,
        300,
        &format!(
            r##"<rect data-id="g" x="150" y="110" width="300" height="34" fill="#BCD0A0" data-kind="garden"/>{}<g data-kind="garden"><text font-size="8" data-names="g">garden</text></g>"##,
            well(200, 150, "well")
        ),
    );
    let all = seats(&src);
    assert_eq!(of(&all, "well").how, How::Gap(0));
}

/// 0242: an outline holding the others is named on itself though a step is drawn a little past its wall.
#[test]
fn a_step_past_the_wall_leaves_the_building_its_name() {
    let src = sheet(
        400,
        300,
        r##"<g data-kind="hall"><rect x="100" y="100" width="160" height="80" fill="#DDB87A"/><rect x="150" y="180" width="60" height="6" fill="#E8D2A8"/><text font-size="8">hall</text></g>"##,
    );
    assert_eq!(of(&seats(&src), "hall").how, How::Inside(0.0));
}

/// 0242: captions are placed last - a caption declared before its building's shapes is written at its group's end, painted after them,
/// and so may stand on its building; its kind is kept with its group.
#[test]
fn a_caption_declared_first_is_written_last_in_its_group() {
    let src = sheet(
        400,
        300,
        r##"<g data-kind="hall"><text font-size="8">hall</text><rect x="100" y="100" width="120" height="60" fill="#DDB87A"/></g>"##,
    );
    assert_eq!(of(&seats(&src), "hall").how, How::Inside(0.0));
    let out = placed(&src).unwrap();
    let (text, rect) = (
        out.find("<text x=").unwrap(),
        out.find("<rect x=\"100\"").unwrap(),
    );
    assert!(text > rect);
    assert!(out.contains("</text></g>"));
}

/// A caption inside an element within its group (a nested frame) is left where it is declared.
#[test]
fn a_caption_in_a_nested_element_stays_in_place() {
    let src = sheet(
        400,
        300,
        r##"<g data-kind="hall"><g transform="translate(0 0)"><text font-size="8">hall</text></g><rect x="100" y="100" width="120" height="60" fill="#DDB87A"/></g>"##,
    );
    let out = placed(&src).unwrap();
    assert!(out.find("<text x=").unwrap() < out.find("<rect x=\"100\"").unwrap());
}

/// A group's end is found past comments, CDATA, a quoted `>` and self-closed children; a group written `<g/>` has none.
#[test]
fn a_groups_end_is_found_by_its_tags() {
    let src = r#"<g a="1"><!-- <x> --><![CDATA[ <y> ]]><?p x?><!d><r b=">"/><g><t/></g><t c='>'>q</t></g>"#;
    let open = (0, 9);
    let child = src.find("<t c=").unwrap();
    let nested = src.find("<t/>").unwrap();
    let (close, direct) = super::write::group_end(src, open, &[child, nested]).unwrap();
    assert_eq!(&src[close..], "</g>");
    assert_eq!(direct, [true, false]);
    assert!(super::write::group_end("<g/>", (0, 4), &[]).is_none());
    assert!(super::write::group_end("<g>", (0, 3), &[]).is_none());
}

/// Ink painted before a building's filled outline lies beneath it: a house's floor under the kitchen drawn over its end does not keep
/// the kitchen's name off the kitchen.
#[test]
fn ink_beneath_a_features_outline_is_hidden_there() {
    let src = sheet(
        400,
        300,
        r##"<rect x="100" y="60" width="200" height="60" fill="#C9A57A" data-kind="house"/><g data-kind="kitchen"><rect x="100" y="100" width="70" height="50" fill="#DDB87A"/><text font-size="8">kitchen</text></g>"##,
    );
    assert!(matches!(of(&seats(&src), "kitchen").how, How::Inside(_)));
}

/// A caption is not seated across a wall from its feature (a convention): the nearer place past the wall is passed over; a feature
/// the wall runs through (a gate) keeps a side each way.
#[test]
fn a_caption_is_not_seated_across_a_wall() {
    // a well hard by a wall above it, every other side built up: past the wall would be nearest, but the place is on the well's side
    let wall = r##"<g data-kind="compound wall" stroke="#2D2A24" stroke-width="8" fill="none"><path d="M 0 136 L 400 136"/></g>"##;
    let walls = [
        block_at((150, 156, 100, 60)),
        block_at((120, 140, 74, 76)),
        block_at((206, 140, 74, 76)),
    ]
    .concat();
    let all = seats(&sheet(
        400,
        300,
        &format!("{wall}{walls}{}", well(200, 150, "well")),
    ));
    let b = block_box(of(&all, "well"));
    assert!(b.1 >= 136.0);
    // a gate the wall runs through is named on either side of it
    let gate = r##"<g data-kind="side gate"><rect x="190" y="126" width="20" height="20" fill="#555"/><text font-size="8">side gate</text></g>"##;
    let all = seats(&sheet(400, 300, &format!("{wall}{gate}")));
    let s = of(&all, "side gate");
    assert!(!matches!(s.how, How::CoverLeast(_)));
    assert!(dist(s.center, (200.0, 136.0)) < 40.0);
}

/// 0242 on loose parts: scattered tubs are named beside one of them, the nearest the middle of them all first - never on the bare
/// ground between; a house of two blocks is named on one of its blocks.
#[test]
fn loose_parts_are_named_by_a_member() {
    let tubs = r##"<g data-kind="fire-water tubs"><circle cx="100" cy="150" r="4" fill="#7A9AB0"/><circle cx="300" cy="150" r="4" fill="#7A9AB0"/><circle cx="190" cy="150" r="4" fill="#7A9AB0"/><text font-size="8">tubs</text></g>"##;
    let all = seats(&sheet(400, 300, tubs));
    let s = of(&all, "tubs");
    assert_eq!(s.how, How::Gap(0));
    assert!((s.center.0 - 190.0).abs() < 1e-6);
    let house = r##"<g data-kind="house"><rect x="50" y="100" width="100" height="60" fill="#DDB87A"/><rect x="250" y="100" width="100" height="60" fill="#DDB87A"/><text font-size="8">house</text></g>"##;
    let all = seats(&sheet(400, 300, house));
    assert!(matches!(of(&all, "house").how, How::Inside(_)));
}

/// A region's name (a house whose rooms are named) is seated after its rooms' names, and on the house across the rooms' floors where no
/// place on it is clear of them - never across the rooms' names.
#[test]
fn a_regions_name_is_set_after_and_across_its_rooms() {
    let src = sheet(
        400,
        300,
        r##"<g data-kind="residence"><text font-size="8">RESIDENCE</text><rect x="100" y="100" width="160" height="60" fill="#DDB87A"/><rect data-id="a" x="100" y="100" width="80" height="60" fill="#DDB87A" data-kind="room"/><rect data-id="b" x="180" y="100" width="80" height="60" fill="#DDB87A" data-kind="room"/><text font-size="8" data-kind="room" data-names="a">west</text><text font-size="8" data-kind="room" data-names="b">east</text></g>"##,
    );
    let all = seats(&src);
    let (r, w, e) = (of(&all, "RESIDENCE"), of(&all, "west"), of(&all, "east"));
    assert_eq!((w.how, e.how), (How::Inside(0.0), How::Inside(0.0)));
    assert!(matches!(r.how, How::Inside(_)));
    assert!(apart(block_box(r), block_box(w)) && apart(block_box(r), block_box(e)));
}

/// A row past the feature's edge is tried at the edge: a kitchen two blocks tall, its middle taken, is named on its free edge row.
#[test]
fn the_last_row_is_at_the_features_edge() {
    let src = sheet(
        400,
        300,
        r##"<g data-kind="kitchen"><rect x="100" y="100" width="72" height="44" fill="#DDB87A"/><text font-size="8">kitchen</text><text font-size="8" data-cont="1">pantries</text></g><rect x="100" y="126" width="72" height="18" fill="#555" data-kind="well"/>"##,
    );
    assert!(matches!(of(&seats(&src), "kitchen pantries").how, How::Inside(d) if d > 0.0));
}

/// A concave outline is met by its part in the strip searched, not its box: a garden reaching round a house leaves the house's side free.
#[test]
fn a_concave_outline_is_met_by_its_part_in_the_strip() {
    let garden = r##"<polygon points="100,40 300,40 300,200 280,200 280,60 100,60" fill="#BCD0A0" stroke="#7A9A5A" stroke-width="1" data-kind="garden"/>"##;
    let all = seats(&sheet(
        400,
        300,
        &format!("{}{garden}", well(200, 150, "well")),
    ));
    assert_eq!(of(&all, "well").how, How::Gap(0));
}

/// 0242 on wraps: where one line clears no place at the usual gap, the first of two then three lines that does is taken there.
#[test]
fn a_caption_cuts_to_clear_its_usual_gap() {
    // a slot 20 px wide over the well: the one line (about 21 px) covers its sides, the cut (about 8 px) clears them by a gap
    let walls = [
        block_at((150, 156, 100, 60)),
        block_at((120, 80, 70, 136)),
        block_at((210, 80, 70, 136)),
    ]
    .concat();
    let all = seats(&sheet(
        400,
        300,
        &format!("{walls}{}", well(200, 150, "aa bb")),
    ));
    let s = of(&all, "aa bb");
    assert_eq!(s.how, How::Gap(0));
    assert_eq!(s.cut.clone().unwrap(), ["aa", "bb"]);
}

/// A house whose every part is a room some other caption names (a gate range of named rooms): its name is set across the rooms and in
/// the air about their names, clear of the names' letters.
#[test]
fn a_region_of_named_parts_is_named_across_them() {
    let src = sheet(
        400,
        300,
        r##"<rect data-id="g" x="100" y="100" width="140" height="30" fill="#8A6A3A"/><rect data-id="a" x="100" y="100" width="70" height="30" fill="#DDB87A"/><rect data-id="b" x="170" y="100" width="70" height="30" fill="#DDB87A"/><g data-kind="room"><text font-size="16" data-names="a">aa</text></g><g data-kind="room"><text font-size="16" data-names="b">bb</text></g><g data-kind="gate range"><text font-size="8" data-names="g a b">gate range</text></g>"##,
    );
    let all = seats(&src);
    let (r, a, b) = (of(&all, "gate range"), of(&all, "aa"), of(&all, "bb"));
    assert!(matches!(r.how, How::Inside(_)));
    assert!(apart(block_box(r), block_box(a)) && apart(block_box(r), block_box(b)));
}

/// On its feature a caption keeps off the feature's own lines where it can, and lies across them only where it cannot.
#[test]
fn own_lines_are_kept_off_where_they_can_be() {
    let src = sheet(
        400,
        300,
        r##"<g data-kind="hall"><rect x="100" y="100" width="120" height="40" fill="#DDB87A"/><line x1="160" y1="100" x2="160" y2="140" stroke="#333"/><text font-size="8">hall</text></g>"##,
    );
    let s = of(&seats(&src), "hall").clone();
    assert!(matches!(s.how, How::Inside(d) if d > 0.0));
    assert!(block_box(&s).2 <= 160.0 || block_box(&s).0 >= 160.0);
    let lines = (0..12).fold(String::new(), |mut out, k| {
        let _ = write!(
            out,
            r##"<line x1="{x}" y1="100" x2="{x}" y2="140" stroke="#333"/>"##,
            x = 104 + 10 * k
        );
        out
    });
    let src = sheet(
        400,
        300,
        &format!(
            r##"<g data-kind="hall"><rect x="100" y="100" width="120" height="40" fill="#DDB87A"/>{lines}<text font-size="8">hall</text></g>"##
        ),
    );
    assert_eq!(of(&seats(&src), "hall").how, How::Inside(0.0));
}

/// A concave outline met in a row of the search on a feature is read by its part in the row: a garden hugging a hall's top and left
/// edges, painted over it, leaves the hall's floor free.
#[test]
fn a_concave_outline_is_met_by_its_part_in_a_row() {
    let src = sheet(
        400,
        300,
        r##"<g data-kind="hall"><rect x="100" y="100" width="200" height="100" fill="#DDB87A"/><text font-size="8">hall</text></g><rect x="190" y="140" width="20" height="20" fill="#333" data-kind="pillar"/><polygon points="90,90 310,90 310,100 100,100 100,210 90,210" fill="#BCD0A0" data-kind="garden"/>"##,
    );
    assert!(matches!(of(&seats(&src), "hall").how, How::Inside(d) if d > 0.0));
}

/// A name may lie across its own feature's details - ink in its own group that no caption names, of a kind none names (a weighing
/// floor's steelyard and bales) - never across another feature's (a well's gear drawn in a kitchen, its kind the well's).
#[test]
fn a_name_lies_across_its_own_details_not_anothers() {
    let floor = r##"<g data-kind="weighing floor"><rect data-id="f" x="100" y="100" width="60" height="40" fill="#C9A57A"/><g data-kind="steelyard"><rect x="104" y="104" width="52" height="32" fill="#4A3318"/></g><text font-size="8" data-names="f">weighing</text></g>"##;
    assert!(matches!(
        of(&seats(&sheet(400, 300, floor)), "weighing").how,
        How::Inside(_)
    ));
    let kitchen = r##"<g data-kind="kitchen"><rect x="100" y="100" width="60" height="40" fill="#C9A57A"/><g data-kind="well"><rect x="104" y="104" width="52" height="32" fill="#4A3318"/></g><text font-size="8">kitchen</text></g><g data-kind="well"><rect data-id="w" x="300" y="100" width="20" height="20" fill="#555"/><text font-size="8" data-names="w">well</text></g>"##;
    assert!(!matches!(
        of(&seats(&sheet(400, 300, kitchen)), "kitchen").how,
        How::Inside(_)
    ));
}

/// A name as wide as its feature but not its feature's inside lies across the outline's own stroke, its feature's last pass.
#[test]
fn a_name_as_wide_as_its_feature_lies_across_its_own_outline() {
    let shed = r##"<g data-kind="shed"><rect data-id="s" x="100" y="100" width="18" height="30" fill="#C9A57A" stroke="#333" stroke-width="4"/><text font-size="8" data-names="s">shed</text></g><g data-kind="other"><rect data-id="o" x="90" y="80" width="40" height="70" fill="none"/><text font-size="8" data-names="o">x</text></g>"##;
    // with room beside it, it is named beside it, not across its outline
    assert!(matches!(
        of(&seats(&sheet(400, 300, shed)), "shed").how,
        How::Gap(_)
    ));
    // every place at the usual gap built up: named on itself, across its own outline's stroke, before it is led away
    let walls = [
        block_at((60, 60, 100, 38)),
        block_at((60, 132, 100, 40)),
        block_at((60, 98, 38, 34)),
        block_at((120, 98, 40, 34)),
    ]
    .concat();
    let all = seats(&sheet(400, 300, &format!("{shed}{walls}")));
    let b = block_box(of(&all, "shed"));
    assert!(matches!(of(&all, "shed").how, How::Inside(_)));
    assert!(b.0 >= 100.0 - 1e-6 && b.2 <= 118.0 + 1e-6);
}

/// Across its rooms a region's name keeps a line's height above and below another caption's letters, so the two do not read as one
/// block: a house of two rooms whose names stand in their rooms' upper halves is named in its lower band.
#[test]
fn a_regions_name_is_not_stacked_on_a_rooms() {
    let src = sheet(
        400,
        300,
        r##"<rect data-id="h" x="100" y="100" width="160" height="80" fill="#DDB87A"/><rect data-id="a" x="100" y="100" width="80" height="40" fill="#DDB87A"/><rect data-id="b" x="180" y="100" width="80" height="40" fill="#DDB87A"/><g data-kind="room"><text font-size="8" data-names="a">west room</text></g><g data-kind="room"><text font-size="8" data-names="b">east room</text></g><g data-kind="house"><text font-size="8" data-names="h a b">HOUSE</text></g>"##,
    );
    let all = seats(&src);
    let (h, w) = (
        block_box(of(&all, "HOUSE")),
        block_box(of(&all, "west room")),
    );
    assert!(h.1 >= w.3 + 9.2 - 1e-6 || h.3 <= w.1 - 9.2 + 1e-6);
}

/// The names that fit on their own feature are seated before points' names: a yard's name takes its yard before the posts in it are
/// named beside them.
#[test]
fn areas_are_named_before_the_points_in_them() {
    let src = sheet(
        400,
        300,
        r##"<g data-kind="practice ground"><rect x="100" y="100" width="90" height="40" fill="#E8D2A8"/><text font-size="8">practice ground</text><g data-kind="striking posts"><circle cx="145" cy="120" r="2" fill="#555"/><text font-size="7">posts</text></g></g>"##,
    );
    assert!(matches!(
        of(&seats(&src), "practice ground").how,
        How::Inside(_)
    ));
}

/// A slanting band (a leader already drawn) is met by its part in the strip searched, not its box.
#[test]
fn a_slanting_band_is_met_by_its_part_in_the_strip() {
    let src = sheet(
        400,
        300,
        r##"<g data-kind="hall"><rect x="100" y="100" width="200" height="100" fill="#DDB87A"/><text font-size="8">hall</text></g><rect x="190" y="140" width="20" height="20" fill="#333" data-kind="pillar"/><line x1="100" y1="200" x2="300" y2="100" stroke="#333" stroke-width="1" data-kind="beam"/>"##,
    );
    assert!(matches!(of(&seats(&src), "hall").how, How::Inside(_)));
}
