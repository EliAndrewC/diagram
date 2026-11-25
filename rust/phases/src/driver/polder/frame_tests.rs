//! The sluices' frames kept clear of the dike's crowns (449 T427), apart from `tests.rs`, which stands at the file-size bar.
//!
//! Research:
//!     the frame's tests - NONE: fixtures and assertions; the rule's claim is at `field::dike::FRAME_REACH_FT`

use super::{sluice_channel, sluice_frame};
use crate::driver::{roll, spec::parse};
use crate::field::geom::{dist, inside, seg_dist};

/// NO CROWN ON A SLUICE'S FRAME (449 T427): the rows' 15 ft gap (`GAP_HALF_FT`) let the broadest willow (5.5 ft) reach 9.5 ft
/// from a channel's middle line, inside the post's outer face 10 ft out - on seed 66 of the dike-pond form a crown overlapped a
/// post by 0.17 ft, on seed 37 of the rice polder one touched it.
#[test]
fn no_dike_crown_stands_on_a_sluices_frame() {
    use crate::field::dike::FRAME_REACH_FT;
    // the dike's keep-clear reaches every corner of a polder sluice's frame, on the feeder and on the outfall's run, a rice
    // polder's or a dike-pond block's at up to its widest creek (449 T431): the span's 20 ft holds them all
    let creeks = crate::field::polder::creeks::CREEK_FT;
    for w in [super::FEEDER_W, super::RUN_W, creeks.0, creeks.1] {
        let f = sluice_frame((0.0, 0.0), (0.0, 1.0), w);
        let far = f
            .posts
            .iter()
            .chain([&f.board, &f.drum])
            .flatten()
            .map(|&q| dist(q, (0.0, 0.0)))
            .fold(0.0, f64::max);
        let reaches = far <= FRAME_REACH_FT + 1e-9 && far > FRAME_REACH_FT - 0.05;
        assert!(reaches, "{far}");
    }
    for (seed, form) in [
        (66, "mulberry_dike_fishpond"),
        (37, "polder_grid"),
        (76, "mulberry_dike_fishpond"),
    ] {
        let spec = format!(
            r#"{{"name": "P", "seed": {seed}, "households": 15, "down_deg": 90, "field_archetype": "{form}"}}"#
        );
        let stage = roll(&parse(&spec).unwrap()).unwrap().polder.unwrap();
        let channels = super::sluice_channels(&stage);
        for &at in &stage.polder.sluices {
            let (dir, width) = sluice_channel(at, &channels).unwrap();
            let frame = sluice_frame(at, dir, width);
            for ring in frame.posts.iter().chain([&frame.board, &frame.drum]) {
                for &(x, y, r) in stage.dike.trees.iter().flat_map(|(_, row)| row) {
                    let sides = ring.len();
                    let gap = (0..sides)
                        .map(|i| seg_dist((x, y), ring[i], ring[(i + 1) % sides]))
                        .fold(f64::INFINITY, f64::min);
                    assert!(!inside((x, y), ring) && gap >= r, "{form} seed {seed}: a crown of radius {r} ft stands {gap:.2} ft from the frame");
                }
            }
        }
    }
}
