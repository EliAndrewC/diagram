//! The polder's tests: the sluices across their channels, the waterside strips off the cuts, the seat's ring and its ground off
//! the dike, the landward shore and the banks' denser reeds.
//!
//! Research:
//!     the polder's tests - NONE: fixtures and assertions; each rule's claim is at the unit it tests

use super::{draw_sluices, sluice_channel, sluice_frame, Svg, SLUICE_SPAN_FT, SLUICE_TIMBER_FT};
use crate::driver::{roll, spec::parse};
use crate::field::fan::Pt;
use crate::field::geom::{dist, inside, seg_dist};

fn dot(a: Pt, b: Pt) -> f64 {
    a.0 * b.0 + a.1 * b.1
}

/// A ring's extent along `d` about `at`: its least and greatest projection.
fn extent(ring: &[Pt], at: Pt, d: Pt) -> (f64, f64) {
    ring.iter()
        .map(|p| dot((p.0 - at.0, p.1 - at.1), d))
        .fold((f64::INFINITY, f64::NEG_INFINITY), |(lo, hi), x| {
            (lo.min(x), hi.max(x))
        })
}

/// The frame lies across its channel: its span `span`, the board running post to post across `dir` and thin along it, each
/// post at a span's end and wholly on its bank, the crossbeam across, the drum up the channel from the board.
fn assert_across(at: Pt, dir: Pt, w: f64, span: f64) {
    let f = sluice_frame(at, dir, w);
    let across = (-dir.1, dir.0);
    let (post_a, _) = SLUICE_TIMBER_FT.1;
    assert!((f.span - span).abs() < 1e-9);
    let (lo, hi) = extent(&f.board, at, across);
    assert!((hi - lo - (span - post_a)).abs() < 1e-9);
    let (lo, hi) = extent(&f.board, at, dir);
    assert!(hi - lo <= SLUICE_TIMBER_FT.0 + 1e-9);
    let (l, r) = (
        extent(&f.posts[0], at, across),
        extent(&f.posts[1], at, across),
    );
    assert!((l.0 + span / 2.0).abs() < 1e-9 && (r.1 - span / 2.0).abs() < 1e-9);
    assert!(-l.1 >= w / 2.0 - 1e-9 && r.0 >= w / 2.0 - 1e-9);
    let beam = (f.beam[1].0 - f.beam[0].0, f.beam[1].1 - f.beam[0].1);
    assert!(dot(beam, dir).abs() < 1e-9 && dot(beam, across) > 0.0);
    assert!(extent(&f.drum, at, dir).1 < 0.0);
}

/// THE GATE SPANS ITS CHANNEL, ACROSS IT (449 T234): a field channel's sluice 20 ft post to post, a wider channel's bank to bank,
/// on a channel running obliquely.
#[test]
fn a_sluice_spans_its_channel_across_its_direction() {
    let dir = (30f64.to_radians().cos(), 30f64.to_radians().sin());
    assert!((16.0..=24.0).contains(&SLUICE_SPAN_FT));
    assert_across((100.0, 50.0), dir, 5.5, SLUICE_SPAN_FT);
    assert_across((100.0, 50.0), (0.0, 1.0), 3.0, SLUICE_SPAN_FT);
    // Shiro Daika's 66 ft feeder: its posts on the banks
    assert_across((0.0, 0.0), dir, 66.0, 66.0 + 2.0 * SLUICE_TIMBER_FT.1 .0);
}

#[test]
fn a_sluice_finds_the_channel_through_its_point() {
    let feeder: [Pt; 3] = [(0.0, 0.0), (0.0, 0.0), (0.0, 40.0)];
    let drain: [Pt; 2] = [(10.0, 10.0), (20.0, 20.0)];
    let channels = [(&feeder[..], 3.0), (&drain[..], 5.5)];
    assert_eq!(
        sluice_channel((0.0, 40.0), &channels),
        Some(((0.0, 1.0), 3.0))
    );
    let (d, w) = sluice_channel((15.0, 15.0), &channels).unwrap();
    assert!((d.0 - d.1).abs() < 1e-12 && (w - 5.5).abs() < 1e-12);
    assert_eq!(sluice_channel((5.0, 0.0), &channels), None);
}

/// THE OLD SQUARE IS GONE (449 T234): on a rolled polder falling obliquely and on Kuwabata, both sluices are drawn as frames
/// across their channels - the inlet across the feeder, the outfall across its drain's diagonal leg, two different
/// directions - each of five marks (board, beam, two posts, drum), and the deleted 8 ft square on the point is drawn nowhere.
#[test]
fn a_rolled_polder_draws_its_sluices_across_their_channels_not_as_the_old_square() {
    for spec in [
        r#"{"name": "R", "seed": 5, "households": 12, "down_deg": 30, "field_archetype": "polder_grid"}"#,
        r#"{"name": "Kuwabata", "seed": 21, "households": 16, "down_deg": 90, "field_archetype": "mulberry_dike_fishpond", "pond_layout": "mosaic", "dike_crop": "mulberry"}"#,
    ] {
        let r = roll(&parse(spec).unwrap()).unwrap();
        let s = r.polder.as_ref().unwrap();
        let channels = super::sluice_channels(s);
        let found: Vec<(Pt, f64)> = s
            .polder
            .sluices
            .iter()
            .filter_map(|&at| sluice_channel(at, &channels))
            .collect();
        assert_eq!(found.len(), 2);
        assert!(dot(found[0].0, found[1].0).abs() < 0.9);
        for (&at, &(d, w)) in s.polder.sluices.iter().zip(&found) {
            assert_across(at, d, w, SLUICE_SPAN_FT);
            let h = 4.0;
            let mut old = Svg::default();
            old.polygon(
                &[
                    (at.0 - h, at.1 - h),
                    (at.0 + h, at.1 - h),
                    (at.0 + h, at.1 + h),
                    (at.0 - h, at.1 + h),
                ],
                super::SLUICE.0,
                Some((super::SLUICE.1, 0.8)),
            );
            let doc = old.finish(1e4, 1e4, 0.0);
            let square = doc.lines().find(|l| l.starts_with("<path")).unwrap();
            assert!(!r.svg.contains(square));
        }
        assert_eq!(r.ink.get("sluice gate"), Some(&10));
        assert!(!r.refusals.join("\n").contains("sluice"));
    }
}

/// Whether segments `ab` and `cd` cross or touch.
fn crosses(a: Pt, b: Pt, c: Pt, d: Pt) -> bool {
    let side = |p: Pt, q: Pt, r: Pt| (q.0 - p.0) * (r.1 - p.1) - (q.1 - p.1) * (r.0 - p.0);
    let (d1, d2) = (side(c, d, a), side(c, d, b));
    let (d3, d4) = (side(a, b, c), side(a, b, d));
    d1 * d2 <= 0.0 && d3 * d4 <= 0.0
}

/// The least distance between segments `ab` and `cd`: nothing where they cross.
fn seg_seg(a: Pt, b: Pt, c: Pt, d: Pt) -> f64 {
    let apart = [
        seg_dist(a, c, d),
        seg_dist(b, c, d),
        seg_dist(c, a, b),
        seg_dist(d, a, b),
    ]
    .into_iter()
    .fold(f64::INFINITY, f64::min);
    f64::from(u8::from(!crosses(a, b, c, d))) * apart
}

/// The segment `a` to `b` walked every foot, both ends included.
#[expect(
    clippy::cast_possible_truncation,
    clippy::cast_sign_loss,
    reason = "a segment's length in whole feet, a small positive count"
)]
fn walk(a: Pt, b: Pt) -> impl Iterator<Item = Pt> {
    let n = dist(a, b).ceil().max(1.0) as u32;
    (0..=n).map(move |k| {
        let t = f64::from(k) / f64::from(n);
        (a.0 + (b.0 - a.0) * t, a.1 + (b.1 - a.1) * t)
    })
}

/// Feet of a channel's course (each of its segments walked every foot) lying in a strip or within its half-width of one.
fn feet_under(strip: &[Pt], course: &[Pt], w: f64) -> usize {
    let edges: Vec<(Pt, Pt)> = (0..strip.len())
        .map(|i| (strip[i], strip[(i + 1) % strip.len()]))
        .collect();
    course
        .windows(2)
        .flat_map(|s| walk(s[0], s[1]))
        .filter(|&p| {
            inside(p, strip)
                || edges
                    .iter()
                    .any(|&(a, b)| seg_dist(p, a, b) < w / 2.0 - 1e-6)
        })
        .count()
}

/// THE REEDS STOP AT THE CUT (449 T236): on Kuwabata and a polder falling obliquely, no waterside strip crosses a sluice's
/// channel - the feeder into the inlet, the outfall's drain out of the tail - or comes within its half-width of one; no strip
/// lies on the dike: each strip's edges, walked every foot, stay off the band inside its outer face (half a foot of rounding
/// allowed); and on Kuwabata the foot's reeds reach the outfall's bank. Red before T236: Kuwabata's west strip had 57 ft of
/// the feeder and 45 ft of the outfall under its reeds and its foot strip 341 ft of the outfall, and its three strips 258, 258
/// and 259 ft of edge on the dike.
#[test]
fn the_waterside_strips_stop_at_the_sluices_channels_and_keep_off_the_dike() {
    let (mut got, mut want) = (Vec::new(), Vec::new());
    for spec in [
        r#"{"name": "Kuwabata", "seed": 21, "households": 16, "down_deg": 90, "field_archetype": "mulberry_dike_fishpond", "pond_layout": "mosaic", "dike_crop": "mulberry"}"#,
        r#"{"name": "R", "seed": 5, "households": 12, "down_deg": 30, "field_archetype": "polder_grid"}"#,
    ] {
        let r = roll(&parse(spec).unwrap()).unwrap();
        let s = r.polder.as_ref().unwrap();
        let ward = r.waterward.as_ref().unwrap();
        assert!(!ward.strips.is_empty());
        let name = &r.plan.name;
        let [(feeder, fw), (outfall, rw)] = super::sluice_channels(s);
        let channels = [("feeder", feeder, fw), ("outfall", outfall, rw)];
        for (i, strip) in ward.strips.iter().enumerate() {
            for &(channel, course, w) in &channels {
                let near = (0..strip.len())
                    .flat_map(|j| {
                        course.windows(2).map(move |c| {
                            seg_seg(strip[j], strip[(j + 1) % strip.len()], c[0], c[1])
                        })
                    })
                    .fold(f64::INFINITY, f64::min);
                let under = feet_under(strip, course, w);
                got.push(format!(
                    "{name} strip {i} over the {channel}: {under} ft of its course under the reeds, within its half-width {}",
                    near < w / 2.0 - 1e-6
                ));
                want.push(format!(
                    "{name} strip {i} over the {channel}: 0 ft of its course under the reeds, within its half-width false"
                ));
            }
            let on_dike = (0..strip.len())
                .flat_map(|j| walk(strip[j], strip[(j + 1) % strip.len()]))
                .filter(|&p| {
                    // both asked of every point, so the walk off the band is read whole
                    let deep = (0..s.dike.outer.len()).all(|k| {
                        seg_dist(
                            p,
                            s.dike.outer[k],
                            s.dike.outer[(k + 1) % s.dike.outer.len()],
                        ) > 0.5
                    });
                    inside(p, &s.dike.outer) && deep
                })
                .count();
            got.push(format!(
                "{name} strip {i} on the dike: {on_dike} ft of its edge inside the outer face"
            ));
            want.push(format!(
                "{name} strip {i} on the dike: 0 ft of its edge inside the outer face"
            ));
        }
        // on Kuwabata the foot's reeds run to the outfall's bank where it runs straight out down the fall, not short of it
        if name == "Kuwabata" {
            let run = (s.outfall[1], s.outfall[2]);
            assert!(ward
                .strips
                .iter()
                .flatten()
                .any(|&p| (seg_dist(p, run.0, run.1) - rw / 2.0).abs() < 1e-6));
        }
    }
    assert_eq!(got, want);
}

/// The settlement's ground walked on a one-foot grid: the square feet of it inside the dike's outer face (deeper than half a
/// foot past it, the rounding allowed), and those within the head canal's half-width of its course.
#[expect(
    clippy::cast_possible_truncation,
    reason = "a grid's bounds in whole feet"
)]
fn ground_over(ground: &[Pt], s: &crate::field::staged::PolderStage) -> (usize, usize) {
    let outer = &s.dike.outer;
    let head = s.polder.ditches.iter().find(|d| d.seg == "feeder").unwrap();
    let (lo, hi) = ground.iter().fold(
        (
            (f64::INFINITY, f64::INFINITY),
            (f64::NEG_INFINITY, f64::NEG_INFINITY),
        ),
        |(lo, hi), p| {
            (
                (lo.0.min(p.0), lo.1.min(p.1)),
                (hi.0.max(p.0), hi.1.max(p.1)),
            )
        },
    );
    let (mut dike, mut canal) = (0, 0);
    for x in (lo.0.floor() as i64)..=(hi.0.ceil() as i64) {
        for y in (lo.1.floor() as i64)..=(hi.1.ceil() as i64) {
            #[expect(clippy::cast_precision_loss, reason = "whole feet on a map")]
            let p = (x as f64 + 0.5, y as f64 + 0.5);
            if !inside(p, ground) {
                continue;
            }
            let deep =
                (0..outer.len()).all(|k| seg_dist(p, outer[k], outer[(k + 1) % outer.len()]) > 0.5);
            dike += usize::from(inside(p, outer) && deep);
            canal += usize::from(
                head.pts
                    .windows(2)
                    .any(|c| seg_dist(p, c[0], c[1]) < head.w / 2.0),
            );
        }
    }
    (dike, canal)
}

/// The ring off the dike holds the whole outer face, each side touching it at its widest, on a block turned obliquely.
#[test]
fn the_ring_off_the_dike_holds_the_outer_face_and_touches_it() {
    let (c, sn) = (30f64.to_radians().cos(), 30f64.to_radians().sin());
    let at = |x: f64, y: f64| (100.0 + x * c - y * sn, 50.0 + x * sn + y * c);
    let outline = [
        at(0.0, 0.0),
        at(0.0, 200.0),
        at(300.0, 200.0),
        at(300.0, 0.0),
    ];
    // a waving face, 20 to 40 ft out on each side
    let outer: Vec<Pt> = (0..40)
        .map(|k| {
            let w = 30.0 + 10.0 * (f64::from(k) * 0.7).sin();
            let t = f64::from(k % 10) / 10.0;
            match k / 10 {
                0 => at(-w, 200.0 * t),
                1 => at(300.0 * t, 200.0 + w),
                2 => at(300.0 + w, 200.0 * (1.0 - t)),
                _ => at(300.0 * (1.0 - t), -w),
            }
        })
        .collect();
    let ring = super::off_the_dike(&outline, &outer, &mut std::collections::HashMap::new());
    assert_eq!(ring.len(), 4);
    // the same ring whichever way the block's corners turn
    let mut back = outline;
    back.reverse();
    let mut turned = super::off_the_dike(&back, &outer, &mut std::collections::HashMap::new());
    turned.reverse();
    for (p, q) in ring.iter().zip(&turned) {
        assert!(dist(*p, *q) < 1e-9, "{ring:?} against {turned:?}");
    }
    for &p in &outer {
        let edge = (0..4)
            .map(|i| seg_dist(p, ring[i], ring[(i + 1) % 4]))
            .fold(f64::INFINITY, f64::min);
        assert!(inside(p, &ring) || edge < 1e-9, "{p:?} outside {ring:?}");
    }
    for i in 0..4 {
        let near = outer
            .iter()
            .map(|&p| seg_dist(p, ring[i], ring[(i + 1) % 4]))
            .fold(f64::INFINITY, f64::min);
        assert!(near < 1e-9, "side {i} stands {near} ft off the face");
    }
}

/// A POLDER SEAT'S BELT STANDS TO WINDWARD ON ITS DRY SIDE (449 T292): Kuwabata backs onto its landward shore (east) with the
/// polder to the west, under the northwest wind, so its belt takes the windward side the polder leaves dry, the band's north end -
/// the settlement's ground reaches past the band's half-length there, never toward the dike. Red before T292: the ground ran the
/// band's half-length either way, the belt's room asked of the shore's way.
#[test]
fn a_polder_seats_belt_stands_to_windward_on_its_dry_side() {
    let r = roll(&parse(r#"{"name": "Kuwabata", "seed": 21, "households": 16, "down_deg": 90, "field_archetype": "mulberry_dike_fishpond", "pond_layout": "mosaic", "dike_crop": "mulberry"}"#).unwrap()).unwrap();
    let f = &r.seated.as_ref().expect("a seat").frames[0];
    let w = crate::driver::wind(&r.plan.windward);
    let side = (w.0 * f.along.0 + w.1 * f.along.1).signum();
    let ground = crate::driver::settlement_ground(f, w);
    let past = ground
        .iter()
        .map(|p| ((p.0 - f.anchor.0) * f.along.0 + (p.1 - f.anchor.1) * f.along.1) * side)
        .fold(f64::MIN, f64::max);
    let half = f.band.0;
    assert!(past > half + 50.0, "{past} against the half-length {half}");
    let toward = ground
        .iter()
        .map(|p| (p.0 - f.anchor.0) * f.out.0 + (p.1 - f.anchor.1) * f.out.1)
        .fold(f64::MAX, f64::min);
    assert!(toward > -1e-6, "{toward}");
}

/// THE SETTLEMENT STANDS OFF THE DIKE (449 T239): on Kuwabata and on a grid polder falling obliquely, no square foot of the
/// settlement's ground lies inside the dike's outer face - on the dike, the ring canal or the fields - nor within the head
/// canal's half-width of its course. Red before T239, the seat handed the plots' edge as its ring: Kuwabata's ground had
/// 27,322 ft2 inside the outer face and 2,784 ft2 on the head canal, the oblique polder's 26,583 and 3,168.
#[test]
fn the_settlement_stands_off_the_dike_and_the_head_canal() {
    let (mut got, mut want) = (Vec::new(), Vec::new());
    for spec in [
        r#"{"name": "Kuwabata", "seed": 21, "households": 16, "down_deg": 90, "field_archetype": "mulberry_dike_fishpond", "pond_layout": "mosaic", "dike_crop": "mulberry"}"#,
        r#"{"name": "R", "seed": 5, "households": 12, "down_deg": 30, "field_archetype": "polder_grid"}"#,
    ] {
        let r = roll(&parse(spec).unwrap()).unwrap();
        let s = r.polder.as_ref().unwrap();
        let frame = &r.seated.as_ref().expect("a seat").frames[0];
        let (dike, head) = ground_over(
            &crate::driver::settlement_ground(frame, crate::driver::wind(&r.plan.windward)),
            s,
        );
        got.push(format!(
            "{}: {dike} ft2 inside the dike's outer face, {head} ft2 on the head canal",
            r.plan.name
        ));
        want.push(format!(
            "{}: 0 ft2 inside the dike's outer face, 0 ft2 on the head canal",
            r.plan.name
        ));
    }
    assert_eq!(got, want);
}

/// THE SLUICES ON TOP (449 T416): on a rolled polder no reeds and no water are drawn after the first sluice mark, so nothing
/// the frame stands over is painted across it - only the settlement's ground mark follows.
#[test]
fn the_sluices_are_drawn_after_the_water_and_the_reeds() {
    for spec in [
        r#"{"name": "R", "seed": 5, "households": 12, "down_deg": 30, "field_archetype": "polder_grid"}"#,
        r#"{"name": "Kuwabata", "seed": 21, "households": 16, "down_deg": 90, "field_archetype": "mulberry_dike_fishpond", "pond_layout": "mosaic", "dike_crop": "mulberry"}"#,
    ] {
        let r = roll(&parse(spec).unwrap()).unwrap();
        let body = r.svg.split_once("</defs>").unwrap().1;
        let first = body.find(super::SLUICE.0).unwrap();
        let (before, after) = body.split_at(first);
        assert!(before.contains("url(#reed-ticks)") && before.contains("url(#reed-bank)"));
        for ink in [
            "url(#reed",
            super::super::svg::ink::SUPPLY,
            super::super::svg::ink::DRAIN,
            super::super::svg::ink::POND_WATER,
            super::super::svg::ink::FLOODED,
        ] {
            assert!(!after.contains(ink), "{ink} drawn over a sluice");
        }
    }
}

/// A sluice whose channel is not known is not drawn: the gap is named, not guessed.
#[test]
fn a_sluice_with_no_channel_is_named_not_drawn() {
    let r = roll(&parse(r#"{"name": "R", "seed": 5, "households": 12, "down_deg": 30, "field_archetype": "polder_grid"}"#).unwrap()).unwrap();
    let mut s = r.polder.unwrap();
    s.polder.feeder.clear();
    let (mut svg, mut missing) = (Svg::default(), Vec::new());
    draw_sluices(&mut svg, &s, &mut missing);
    assert_eq!(missing.len(), 1, "{missing:?}");
    assert!(missing[0].contains("(sluice 0) not drawn: no channel"));
    assert_eq!(svg.census().get("sluice gate"), Some(&5));
}

/// THE VILLAGE ON THE LANDWARD SHORE (449 T240): on Kuwabata the settlement's back faces east, the dry landward shore of 0019's
/// drawing, and the waterside reeds lie along the west flank and the low south foot; on a grid polder falling obliquely its back
/// faces the cross flank turned away from the wild pond. Red before T240: both seats faced the head, their backs up the fall
/// beside the wild pond - Kuwabata's to the north, its reeds on the west, east and south.
#[test]
fn the_seat_stands_on_the_landward_shore() {
    let mut got = Vec::new();
    for spec in [
        r#"{"name": "Kuwabata", "seed": 21, "households": 16, "down_deg": 90, "field_archetype": "mulberry_dike_fishpond", "pond_layout": "mosaic", "dike_crop": "mulberry"}"#,
        r#"{"name": "R", "seed": 5, "households": 12, "down_deg": 30, "field_archetype": "polder_grid"}"#,
    ] {
        let r = roll(&parse(spec).unwrap()).unwrap();
        let s = r.polder.as_ref().unwrap();
        let out = r.seated.as_ref().expect("a seat").frames[0].out;
        let rad = r.plan.down_deg.to_radians();
        let ring = &s.polder.outline;
        #[expect(clippy::cast_precision_loss, reason = "a ring's few corners")]
        let n = ring.len() as f64;
        let mid = (
            ring.iter().map(|q| q.0).sum::<f64>() / n,
            ring.iter().map(|q| q.1).sum::<f64>() / n,
        );
        let pond = s.polder.pond.0;
        let (across, away) = (
            dot(out, (rad.cos(), rad.sin())).abs() < 1e-9,
            dot(out, (pond.0 - mid.0, pond.1 - mid.1)) < 0.0,
        );
        let flanks: String = r.waterward.as_ref().unwrap().flanks.iter().collect();
        got.push(format!(
            "{}: across the fall {across}, away from the pond {away}, reeds {flanks}",
            r.plan.name
        ));
    }
    let want = vec![
        "Kuwabata: across the fall true, away from the pond true, reeds WS".to_owned(),
        "R: across the fall true, away from the pond true, reeds SE".to_owned(),
    ];
    assert_eq!(got, want);
}

/// THE DENSER REEDS ON EACH BANK (449 T240): on Kuwabata the feeder and the outfall's drain, where they run through the reeds,
/// are lined on both banks by a band of denser reeds, each band in the reeds and none on the wild pond's water. Red before T240:
/// nothing drew the band, though 98 ft of the feeder and 319 ft of the outfall ran through the reeds.
#[test]
#[expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]
fn a_channel_through_the_reeds_is_lined_on_each_bank() {
    let r = roll(&parse(r#"{"name": "Kuwabata", "seed": 21, "households": 16, "down_deg": 90, "field_archetype": "mulberry_dike_fishpond", "pond_layout": "mosaic", "dike_crop": "mulberry"}"#).unwrap()).unwrap();
    let s = r.polder.as_ref().unwrap();
    let strips = &r.waterward.as_ref().unwrap().strips;
    let bands = super::bank_bands(s, strips, &mut std::collections::HashMap::new());
    let (c, rx, ry) = s.polder.pond;
    let wet = bands
        .iter()
        .flatten()
        .filter(|q| ((q.0 - c.0) / rx).powi(2) + ((q.1 - c.1) / ry).powi(2) < 1.0)
        .count();
    let mut got = vec![format!("{wet} band points on the pond")];
    for (name, course) in [("feeder", &s.polder.feeder), ("outfall", &s.outfall)] {
        for side in [1.0, -1.0] {
            let lined = bands.iter().any(|b| {
                let (q, k) = (
                    b[0],
                    (0..course.len() - 1)
                        .min_by(|&i, &j| {
                            seg_dist(b[0], course[i], course[i + 1]).total_cmp(&seg_dist(
                                b[0],
                                course[j],
                                course[j + 1],
                            ))
                        })
                        .unwrap(),
                );
                let (a, z) = (course[k], course[k + 1]);
                (((z.0 - a.0) * (q.1 - a.1) - (z.1 - a.1) * (q.0 - a.0)) > 0.0) == (side > 0.0)
            });
            got.push(format!("{name} bank {side}: lined {lined}"));
        }
    }
    let want = vec![
        "0 band points on the pond".to_owned(),
        "feeder bank 1: lined true".to_owned(),
        "feeder bank -1: lined true".to_owned(),
        "outfall bank 1: lined true".to_owned(),
        "outfall bank -1: lined true".to_owned(),
    ];
    assert_eq!(got, want);
    let (census, marks) = (
        r.ink.get("marsh").copied().unwrap_or(0),
        1 + strips.len() + bands.len(),
    );
    assert_eq!(census, marks);
}

/// THE TIE (449 T240): a wild pond standing square on the head's middle names neither cross flank, so the shore is the one nearer
/// the wind - west under Kuwabata's north-west wind, east under an east wind.
#[test]
fn a_pond_on_the_heads_middle_turns_the_shore_to_the_wind() {
    let mut rolled = roll(&parse(r#"{"name": "Kuwabata", "seed": 21, "households": 16, "down_deg": 90, "field_archetype": "mulberry_dike_fishpond", "pond_layout": "mosaic", "dike_crop": "mulberry"}"#).unwrap()).unwrap();
    let stage = rolled.polder.as_mut().unwrap();
    let ring = &stage.polder.outline;
    #[expect(clippy::cast_precision_loss, reason = "a ring's few corners")]
    let mid_x = ring.iter().map(|q| q.0).sum::<f64>() / ring.len() as f64;
    stage.polder.pond.0 .0 = mid_x;
    let mut plan = rolled.plan.clone();
    let stage = rolled.polder.as_ref().unwrap();
    let north_west = super::landward(&plan, stage);
    plan.windward = "E".to_owned();
    let east = super::landward(&plan, stage);
    let got = (north_west.0.round(), east.0.round());
    assert_eq!(got, (-1.0, 1.0));
}

/// The rolls the bank bands are pinned on (449 T250): Kuwabata, and the budget run's grid polder on its four seeds at 10 and 20
/// households (`hamlet --budget polder`).
fn bank_rolls() -> Vec<crate::driver::Rolled> {
    let mut specs = vec![r#"{"name": "Kuwabata", "seed": 21, "households": 16, "down_deg": 90, "field_archetype": "mulberry_dike_fishpond", "pond_layout": "mosaic", "dike_crop": "mulberry"}"#.to_owned()];
    for households in [10, 20] {
        for seed in [4, 25, 39, 47] {
            specs.push(format!(r#"{{"name": "Inashiro", "seed": {seed}, "households": {households}, "down_deg": 90, "water_sink": "pond", "settlement_form": "nucleated", "field_archetype": "polder_grid"}}"#));
        }
    }
    specs
        .iter()
        .map(|s| roll(&parse(s).unwrap()).unwrap())
        .collect()
}

/// THE BANDS DRAWN AS THEY WERE (449 T250): each roll's bank bands, their points and a weighted sum of them, as T240 drew them
/// before the bands' search was cut to the reeds' boxes - the cheaper search keeps every point; Kuwabata re-pinned by 449 T431, its feeder and run
/// widened to its ring canal's 6.2 ft.
#[test]
fn the_bank_bands_hold_their_points() {
    let mut got = Vec::new();
    for r in bank_rolls() {
        let (s, strips) = (
            r.polder.as_ref().unwrap(),
            &r.waterward.as_ref().unwrap().strips,
        );
        let bands = super::bank_bands(s, strips, &mut std::collections::HashMap::new());
        let sum: f64 = bands.iter().flatten().map(|q| q.0 * 1.3 + q.1).sum();
        got.push(format!(
            "{}: {} bands, {} points, {sum:.3}",
            r.plan.name,
            bands.len(),
            bands.iter().map(Vec::len).sum::<usize>()
        ));
    }
    let want: Vec<String> = [
        "Kuwabata: 4 bands, 207 points, 1311377.321",
        "Inashiro: 4 bands, 216 points, 1114273.530",
        "Inashiro: 4 bands, 217 points, 1119742.822",
        "Inashiro: 4 bands, 211 points, 1088477.999",
        "Inashiro: 4 bands, 209 points, 1078031.454",
        "Inashiro: 4 bands, 219 points, 1585297.570",
        "Inashiro: 4 bands, 211 points, 1526196.408",
        "Inashiro: 4 bands, 217 points, 1570540.983",
        "Inashiro: 4 bands, 219 points, 1500569.042",
    ]
    .map(str::to_owned)
    .to_vec();
    assert_eq!(got, want);
}

/// THE BANDS' SEARCH IS THE REEDS' REACH, NOT THE CHANNEL'S (449 T250): every test the bands make - the reeds' boxes, each ring's
/// edges crossed by a reach, each sample's crossings read, the pond's rim - is at most ten for each point they draw, so the work follows the reach of bank in the reeds
/// and not the outfall's whole run to the canvas edge. Red before T250: about 46 tests a point, each of a 2,000 ft outfall's
/// samples asked of every ring of reeds.
#[test]
#[cfg(feature = "counters")]
fn the_bank_bands_search_only_the_reeds() {
    let mut got = Vec::new();
    for r in bank_rolls() {
        let (s, strips) = (
            r.polder.as_ref().unwrap(),
            &r.waterward.as_ref().unwrap().strips,
        );
        let mut counts = std::collections::HashMap::new();
        let _ = super::bank_bands(s, strips, &mut counts);
        let (tests, drawn) = (
            counts.get("test@bank").copied().unwrap_or(0),
            counts.get("write@bank").copied().unwrap_or(0),
        );
        got.push(format!(
            "{}: {tests} tests, {drawn} points, within ten a point {}",
            r.plan.name,
            tests <= 10 * drawn
        ));
    }
    let broke: Vec<&String> = got.iter().filter(|x| x.ends_with("false")).collect();
    assert!(broke.is_empty(), "{got:#?}");
}

/// THE CLIPPED SEARCH FINDS THE BANDS EVERY SAMPLE WOULD (449 T250): on grid polders at falls off the axes, and on Kuwabata, the
/// bands equal those of the plain search - each bank sampled at `BANK_STEP_FT` along its whole run, every sample asked of every
/// ring of reeds and of the pond's rim, the runs of two samples or more kept - and every roll lined somewhere, so none passes empty.
#[test]
fn the_clipped_bank_search_equals_the_plain_one() {
    let mut specs = vec![r#"{"name": "Kuwabata", "seed": 21, "households": 16, "down_deg": 90, "field_archetype": "mulberry_dike_fishpond", "pond_layout": "mosaic", "dike_crop": "mulberry"}"#.to_owned()];
    for (seed, down) in [(5, 30), (7, 0), (11, 135), (13, 210), (17, 300), (19, 255)] {
        specs.push(format!(r#"{{"name": "R", "seed": {seed}, "households": 14, "down_deg": {down}, "field_archetype": "polder_grid"}}"#));
    }
    let mut got = Vec::new();
    for spec in &specs {
        let r = roll(&parse(spec).unwrap()).unwrap();
        let (s, strips) = (
            r.polder.as_ref().unwrap(),
            &r.waterward.as_ref().unwrap().strips,
        );
        let bands = super::bank_bands(s, strips, &mut std::collections::HashMap::new());
        let (same, lined) = (bands == plain_bands(s, strips), !bands.is_empty());
        got.push(format!(
            "{} at {}: the plain search's {same}, lined {lined}",
            r.plan.name, r.plan.down_deg
        ));
    }
    let want: Vec<String> = [
        "Kuwabata at 90",
        "R at 30",
        "R at 0",
        "R at 135",
        "R at 210",
        "R at 300",
        "R at 255",
    ]
    .map(|x| format!("{x}: the plain search's true, lined true"))
    .to_vec();
    assert_eq!(got, want);
}

/// The bank bands by the plain search: every sample of each bank asked of every ring and of the pond's rim.
#[expect(
    clippy::many_single_char_names,
    clippy::cast_possible_truncation,
    clippy::cast_sign_loss,
    reason = "the plane geometry's own names; a reach's samples, a few thousand at most"
)]
fn plain_bands(s: &crate::field::staged::PolderStage, strips: &[Vec<Pt>]) -> Vec<Vec<Pt>> {
    let (c, rx, ry) = s.polder.pond;
    let rings: Vec<&Vec<Pt>> = strips
        .iter()
        .chain(std::iter::once(&s.polder.fringe))
        .filter(|r| r.len() >= 3)
        .collect();
    let mut bands = Vec::new();
    for (course, w) in super::sluice_channels(s) {
        for side in [1.0, -1.0] {
            let off = side * (w + super::BANK_FT) / 2.0;
            let mut samples: Vec<(Pt, bool)> = Vec::new();
            for seg in course.windows(2) {
                let (a, b) = (seg[0], seg[1]);
                let d = crate::field::geom::unit(a, b);
                let nrm = (-d.1 * off, d.0 * off);
                let n = (dist(a, b) / super::BANK_STEP_FT).ceil().max(1.0) as u32;
                for k in 0..=n {
                    let t = f64::from(k) / f64::from(n);
                    let q = (a.0 + (b.0 - a.0) * t + nrm.0, a.1 + (b.1 - a.1) * t + nrm.1);
                    let (dx, dy) = (
                        (q.0 - c.0) / (rx + super::BANK_FT),
                        (q.1 - c.1) / (ry + super::BANK_FT),
                    );
                    samples.push((
                        q,
                        dx * dx + dy * dy >= 1.0 && rings.iter().any(|r| inside(q, r)),
                    ));
                }
            }
            bands.extend(
                samples
                    .split(|x| !x.1)
                    .filter(|run| run.len() >= 2)
                    .map(|run| run.iter().map(|x| x.0).collect::<Vec<Pt>>()),
            );
        }
    }
    bands
}

/// THE REEDS LAID AS THEY WERE (449 T250): each roll's waterside strips, their points and a weighted sum of them, on Kuwabata, the
/// budget run's grid polders and grid polders falling off the axes, as the fringe laid them before its dike corners were filed once
/// for all the flanks - filing them once moves no reed; Kuwabata re-pinned by 449 T431 (its feeder and run 6.2 ft); seeds 5, 11 and 19
/// re-pinned by 449 T417, a row or a scattered settlement's canvas keeping no belt's reach, every strip and point as before, each
/// carried 150 ft (each sum moved by its points times 2.3 times 150 ft, the canvas 300 ft smaller).
#[test]
fn the_waterside_strips_hold_their_points() {
    let mut rolls = bank_rolls();
    for (seed, down) in [(5, 30), (7, 0), (11, 135), (13, 210), (17, 300), (19, 255)] {
        let spec = format!(
            r#"{{"name": "R", "seed": {seed}, "households": 14, "down_deg": {down}, "field_archetype": "polder_grid"}}"#
        );
        rolls.push(roll(&parse(&spec).unwrap()).unwrap());
    }
    let mut got = Vec::new();
    for r in rolls {
        let f = r.waterward.as_ref().unwrap();
        let sum: f64 = f.strips.iter().flatten().map(|q| q.0 * 1.3 + q.1).sum();
        got.push(format!(
            "{} at {}: {:?}, {} strips, {} points, {sum:.3}",
            r.plan.name,
            r.plan.down_deg,
            f.flanks,
            f.strips.len(),
            f.strips.iter().map(Vec::len).sum::<usize>()
        ));
    }
    let want: Vec<String> = [
        "Kuwabata at 90: ['W', 'S'], 4 strips, 104 points, 679313.718",
        "Inashiro at 90: ['W', 'S'], 4 strips, 82 points, 433114.843",
        "Inashiro at 90: ['W', 'S'], 4 strips, 82 points, 433193.563",
        "Inashiro at 90: ['W', 'S'], 4 strips, 82 points, 433085.352",
        "Inashiro at 90: ['W', 'S'], 4 strips, 82 points, 433305.217",
        "Inashiro at 90: ['W', 'S'], 4 strips, 111 points, 810437.934",
        "Inashiro at 90: ['W', 'S'], 4 strips, 111 points, 810452.957",
        "Inashiro at 90: ['W', 'S'], 4 strips, 111 points, 810400.342",
        "Inashiro at 90: ['W', 'S'], 4 strips, 111 points, 804339.444",
        "R at 30: ['S', 'E'], 3 strips, 100 points, 662798.551",
        "R at 0: ['S', 'E'], 4 strips, 96 points, 657993.993",
        "R at 135: ['W', 'S'], 3 strips, 100 points, 569748.322",
        "R at 210: ['N', 'W'], 3 strips, 100 points, 546248.438",
        "R at 300: ['E', 'N'], 3 strips, 101 points, 635830.374",
        "R at 255: ['E', 'N'], 5 strips, 116 points, 704295.705",
    ]
    .map(str::to_owned)
    .to_vec();
    assert_eq!(got, want);
}

/// THE SAMPLES EACH ONCE, IN ORDER (449 T250): the met rings' spans, out of order, overlapping, abutting and apart, merge into the
/// runs they hold, a comparison a sort step and a test a span counted.
#[test]
fn the_met_spans_merge_into_runs_each_sample_once() {
    let mut tests = 0;
    let spans = vec![(40, 50), (0, 10), (5, 12), (13, 20), (60, 60)];
    let runs = super::merged(spans, &mut tests);
    let samples: Vec<u32> = runs.iter().flat_map(|&(lo, hi)| lo..=hi).collect();
    let got = (runs, samples.len(), tests >= 5 + 4);
    let want = (vec![(0, 20), (40, 50), (60, 60)], 33, true);
    assert_eq!(got, want);
}

/// The drawn map's unfilled strokes, each its course as written: the channels, read back off the SVG rather than off the records.
fn drawn_strokes(svg: &str) -> Vec<Vec<Pt>> {
    svg.lines()
        .filter(|l| l.starts_with("<path d=\"M") && l.contains("fill=\"none\""))
        .filter_map(|l| l.split('"').nth(1))
        .map(|d| {
            d.split_whitespace()
                .filter_map(|t| {
                    let (x, y) = t.trim_start_matches(['M', 'L']).split_once(',')?;
                    Some((x.parse().ok()?, y.parse().ok()?))
                })
                .collect()
        })
        .collect()
}

/// THE WATER RUNS ON THROUGH THE SLUICE (449 T263): on Kuwabata and a polder falling obliquely, each sluice's point is joined by a
/// drawn stroke to the ring canal's corner it opens on - the head canal's at the inlet, the drain trunk's at the outfall - 8.5 ft
/// in from it, on the field side of the dike's inner face where the dike's band does not cover it; before 449 T263 nothing was
/// drawn across that hop, the feeder and the outfall stopping at their sluices with the ring's strokes starting 8.5 ft on.
#[test]
fn each_sluice_is_joined_to_its_ring_canal_corner_by_a_drawn_reach() {
    for spec in [
        r#"{"name": "R", "seed": 5, "households": 12, "down_deg": 30, "field_archetype": "polder_grid"}"#,
        r#"{"name": "Kuwabata", "seed": 21, "households": 16, "down_deg": 90, "field_archetype": "mulberry_dike_fishpond", "pond_layout": "mosaic", "dike_crop": "mulberry"}"#,
    ] {
        let r = roll(&parse(spec).unwrap()).unwrap();
        let s = r.polder.as_ref().unwrap();
        let strokes = drawn_strokes(&r.svg);
        let trunk = |seg: &str| s.polder.ditches.iter().find(|d| d.seg == seg).unwrap();
        // the ring corner each sluice opens on: the head canal's start at the inlet, the drain trunk's end at the outfall
        let corners = [trunk("feeder").pts[0], *trunk("drain").pts.last().unwrap()];
        let near = |p: Pt, q: Pt| dist(p, q) < 0.2;
        for (&at, &corner) in s.polder.sluices.iter().zip(&corners) {
            let gap = dist(at, corner);
            let joined = strokes.iter().any(|p| {
                p.windows(2).any(|w| {
                    (near(w[0], at) && near(w[1], corner)) || (near(w[1], at) && near(w[0], corner))
                })
            });
            let mid = (f64::midpoint(at.0, corner.0), f64::midpoint(at.1, corner.1));
            let open = inside(mid, &s.polder.inner_env);
            let (got, want) = (
                (joined, open, format!("{gap:.1}")),
                (true, true, "8.5".to_owned()),
            );
            assert_eq!(got, want, "{at:?}");
        }
    }
}

/// THE WATER RUNS THROUGH THE DIKE, NOT UNDER IT (449 T419): on Kuwabata and a polder falling obliquely the feeder and the
/// outfall each run some feet between the dike's two faces, the dike's band is drawn before every channel's stroke - so the water
/// reads through a cut in the earthwork its own width - and no crown of the dike's rows stands on either channel; before 449 T419
/// the band was painted after the water, unbroken over both crossings, and the rows were cut only round the sluice's point.
#[test]
fn the_dikes_band_and_rows_are_cut_where_the_feeder_and_the_outfall_cross() {
    for spec in [
        r#"{"name": "R", "seed": 5, "households": 12, "down_deg": 30, "field_archetype": "polder_grid"}"#,
        r#"{"name": "Kuwabata", "seed": 21, "households": 16, "down_deg": 90, "field_archetype": "mulberry_dike_fishpond", "pond_layout": "mosaic", "dike_crop": "mulberry"}"#,
    ] {
        let r = roll(&parse(spec).unwrap()).unwrap();
        let s = r.polder.as_ref().unwrap();
        let body = r.svg.split_once("</defs>").unwrap().1;
        let band = body.find("fill-rule=\"evenodd\"").unwrap();
        let water = [
            super::super::svg::ink::SUPPLY,
            super::super::svg::ink::DRAIN,
        ]
        .iter()
        .filter_map(|ink| body.find(&format!("stroke=\"{ink}\"")))
        .min()
        .unwrap();
        let channels = super::sluice_channels(s);
        // the least clear water between a crown's edge and a channel's bank, over every tree and both channels (feet)
        let mut clear = f64::INFINITY;
        for (course, w) in channels {
            // the channel's feet through the band: a walked point outside the inner face and inside the outer one
            let through = course
                .windows(2)
                .flat_map(|g| walk(g[0], g[1]))
                .filter(|&p| inside(p, &s.dike.outer) && !inside(p, &s.dike.inner))
                .count();
            assert!(through >= 10, "{through} ft through the band");
            for &(x, y, c) in s.dike.trees.iter().flat_map(|(_, row)| row) {
                let d = course
                    .windows(2)
                    .map(|g| seg_dist((x, y), g[0], g[1]))
                    .fold(f64::INFINITY, f64::min);
                clear = clear.min(d - c - w / 2.0);
            }
        }
        let (got, want) = ((band < water, clear >= 0.0), (true, true));
        assert_eq!(got, want);
    }
}

/// THE DIKE AND THE BANKS MOTTLED (449 T422): 0027's band is mottled with patches of earth of different ages, never one flat
/// fill, and 0018's bank is mottled earth like it - painted on the band's fill, under the channels that cut the dike.
#[test]
fn a_polder_s_dike_and_its_ponds_banks_are_mottled_under_their_water() {
    for (spec, groups) in [
        (
            r#"{"name": "R", "seed": 5, "households": 12, "down_deg": 30, "field_archetype": "polder_grid"}"#,
            1,
        ),
        (
            r#"{"name": "Kuwabata", "seed": 21, "households": 16, "down_deg": 90, "field_archetype": "mulberry_dike_fishpond", "pond_layout": "mosaic", "dike_crop": "mulberry"}"#,
            2,
        ),
    ] {
        let r = roll(&parse(spec).unwrap()).unwrap();
        let body = r.svg.split_once("</defs>").unwrap().1;
        assert_eq!(body.matches(r#"<clipPath id="earth"#).count(), groups);
        // the dike's patches right after its band, before any channel's water
        let band = body.find(r#"fill-rule="evenodd""#).unwrap();
        let after = &body[band..];
        let mottle = after.find(r#"<clipPath id="earth"#).unwrap();
        let water = after.find(super::super::svg::ink::SUPPLY).unwrap();
        assert!(mottle < water, "the dike's mottle under the channels");
        // the banks' patches before the first pond's water
        if groups == 2 {
            let first = body.find(r#"<clipPath id="earth"#).unwrap();
            assert!(first < band && first < body.find(super::NURSERY_WATER).unwrap());
        }
    }
}

#[test]
fn the_dike_s_patches_stand_on_its_band_a_step_apart_in_its_tones() {
    use super::mottle::{dike, DIKE_TONES, PATCH_FT, PATCH_STEP_FT};
    let stage = |seed: i64| {
        let spec = format!(
            r#"{{"name": "R", "seed": {seed}, "households": 12, "down_deg": 30, "field_archetype": "polder_grid"}}"#
        );
        roll(&parse(&spec).unwrap()).unwrap().polder.unwrap()
    };
    let s = stage(5);
    let patches = dike(&s.dike, 5);
    // one to every step of the inner face's length
    let n = s.dike.outer.len();
    let face: Vec<Pt> = (0..n)
        .map(|i| {
            let (c, o) = (s.dike.crest[i], s.dike.outer[i]);
            (2.0 * c.0 - o.0, 2.0 * c.1 - o.1)
        })
        .collect();
    let around: f64 = (0..n).map(|i| dist(face[i], face[(i + 1) % n])).sum();
    #[expect(clippy::cast_precision_loss, reason = "a few hundred patches")]
    let count = patches.len() as f64;
    assert!((count - around / PATCH_STEP_FT).abs() <= 1.0);
    for &(at, rx, ry, tone) in &patches {
        // on the band: inside the outer face, outside the inner
        assert!(inside(at, &s.dike.outer) && !inside(at, &face), "{at:?}");
        assert!(
            (PATCH_FT.0 .0..=PATCH_FT.0 .1).contains(&rx)
                && (PATCH_FT.1 .0..=PATCH_FT.1 .1).contains(&ry)
        );
        assert!(DIKE_TONES.contains(&tone));
    }
    // every tone drawn, and the patches spread across the band, not strung on one line
    assert!(DIKE_TONES.iter().all(|t| patches.iter().any(|p| p.3 == *t)));
    let off = |p: Pt| {
        (0..n)
            .map(|i| seg_dist(p, face[i], face[(i + 1) % n]))
            .fold(f64::INFINITY, f64::min)
    };
    let (near, far) = patches.iter().fold((0, 0), |(near, far), p| {
        if off(p.0) < 5.0 {
            (near + 1, far)
        } else {
            (near, far + 1)
        }
    });
    assert!(near > 0 && far > near, "{near} near, {far} out");
    // the same seed the same patches, another seed others
    assert_eq!(dike(&s.dike, 5), patches);
    assert_ne!(dike(&s.dike, 6), patches);
}

#[test]
fn a_bank_s_patches_stand_within_its_breadth_of_its_edge() {
    use super::mottle::{banks, BANK_TONES, PATCH_STEP_FT};
    // a bank 400 ft square, turning either way, its pond 40 ft in
    let ring = vec![(0.0, 0.0), (400.0, 0.0), (400.0, 400.0), (0.0, 400.0)];
    let back: Vec<Pt> = ring.iter().rev().copied().collect();
    for r in [&ring, &back] {
        let patches = banks(&[r.as_slice()], 40.0, 21);
        let per = (1600.0 / PATCH_STEP_FT).round();
        #[expect(clippy::cast_precision_loss, reason = "a few hundred patches")]
        let count = patches.len() as f64;
        assert!((count - per).abs() <= 1.0, "{count} of {per}");
        for &(at, _, _, tone) in &patches {
            // inside the bank's ring, no deeper than its breadth
            let deep = at.0.min(at.1).min(400.0 - at.0).min(400.0 - at.1);
            assert!((0.0..=40.0).contains(&deep), "{at:?}");
            assert!(BANK_TONES.contains(&tone));
        }
    }
    // two banks, one stream: the second bank's patches are not the first's moved
    let east: Vec<Pt> = ring.iter().map(|p| (p.0 + 500.0, p.1)).collect();
    let both = banks(&[ring.as_slice(), east.as_slice()], 40.0, 21);
    let half = both.len() / 2;
    assert_eq!(both.len(), 2 * banks(&[ring.as_slice()], 40.0, 21).len());
    assert!(
        (both[0].0 .0 + 500.0 - both[half].0 .0).abs() > 1e-6
            || (both[0].1 - both[half].1).abs() > 1e-6
    );
    assert!(banks(&[], 40.0, 21).is_empty());
}
