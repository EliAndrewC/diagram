//! The track out, chosen once (feature 444 T30): from the cluster's downslope edge out of the field, swept clear of the wet
//! ground, the steadings and the crop - and where that finds no dry way out, from a gateway on a bearing turned off the
//! downslope - then bent round the field and threaded through the steadings (`ways/track.py` `choose_track_out`,
//! `ways/cluster_edge.py` `_cluster_gateway`, `gate_out_of_the_field`, `ways/gateway.py` `gateway_track`,
//! `turned_gateway_track`, `clear_of_what_stands`).
//!
//! Research:
//!     the track out decided once - research/questions/0081-village-lanes.drawing.html: away from the field leaning downslope, off the wet, out past the frame
//!     track leaves downslope - research/questions/0081-village-lanes.drawing.html: from the cluster's downslope edge (or a bearing turned off it)
//!     gateway clear of what stands - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a track passing outside the cluster keeps 7 ft off every part of a homestead - the gateway is walked out from the house centers (8 px its first step) until it clears all that stands by that gap (`push_clear_of_fabric`)
//!     connector starts off the crop - research/questions/0081-village-lanes.drawing.html: the start pushed out of the field envelope
//!     a walled-in gateway - GUESS: searched, the record silent (feature 417 T29 pass D, 2026-10-25); from a gateway turned off the downslope
//!     nothing built on a lane - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: the gateway stepped half the connector's tread off every forbidden footprint

use super::dry_exit::{clear_of_bands, connector_dry_exit, push_out_of, DrySite};
use super::through::{connector_through, push_clear_of_fabric, Fabric, Law, SPUR_SETBACK_FT};
use super::track::{connector, Box4, Swept, TrackSite, FABRIC_GAP_FT};
use super::Counts;
use crate::field::fan::Pt;
use crate::law::rules::CONNECTOR_WIDTH_FT;

/// The bearings off the downslope a walled-in gateway is sought on, nearest first (degrees).
///
/// Research:
///     turned gateway bearings - GUESS: searched, the record silent (feature 417 T29 pass D, 2026-10-25) on the turns - the base bearing downslope follows the water-mouth way out (Wang, pass D); 30, 60 then 90 degrees either side of the downslope
pub const TURNS_DEG: [f64; 6] = [30.0, -30.0, 60.0, -60.0, 90.0, -90.0];

/// The gateway's first step past the cloud's downslope reach beyond the track's gap (ft).
///
/// Research:
///     gateway clear of what stands - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: 8 ft its first step past the gap
pub const FIRST_STEP_FT: f64 = 8.0;

/// The seat's axes: along the margin, and out of it away from the field.
#[derive(Clone, Copy)]
pub struct Axes {
    /// Along the margin.
    pub along: Pt,
    /// Out, away from the field.
    pub out: Pt,
}

/// Where a track leaves the settlement, from the placed houses: the cloud's downslope edge on its mean along the margin, walked
/// out until it clears every steading by the track's gap; turned `turn_deg` off the downslope where asked; `fallback` where no
/// house stands.
#[must_use]
pub fn cluster_gateway(
    houses: &[Pt],
    axes: Axes,
    fallback: Pt,
    turn_deg: f64,
    fabric: &[(Vec<Pt>, Box4)],
    tests: &mut Counts,
) -> Pt {
    if houses.is_empty() {
        return fallback;
    }
    let (mut a, mut o) = (axes.along, axes.out);
    if turn_deg != 0.0 {
        let (s, c) = turn_deg.to_radians().sin_cos();
        (o, a) = (
            (o.0 * c - o.1 * s, o.0 * s + o.1 * c),
            (a.0 * c - a.1 * s, a.0 * s + a.1 * c),
        );
    }
    #[expect(clippy::cast_precision_loss, reason = "a household count")]
    let n = houses.len() as f64;
    let c = houses
        .iter()
        .fold((0.0, 0.0), |s, h| (s.0 + h.0 / n, s.1 + h.1 / n));
    let reach = houses
        .iter()
        .map(|h| (h.0 - c.0) * o.0 + (h.1 - c.1) * o.1)
        .fold(f64::NEG_INFINITY, f64::max);
    let mid = houses
        .iter()
        .map(|h| (h.0 - c.0) * a.0 + (h.1 - c.1) * a.1)
        .sum::<f64>()
        / n;
    push_clear_of_fabric(
        (c.0 + a.0 * mid, c.1 + a.1 * mid),
        o,
        reach + FABRIC_GAP_FT + FIRST_STEP_FT,
        fabric,
        FABRIC_GAP_FT,
        tests,
    )
}

/// The connector's start: `gate` pushed out of the field's envelope by the setback.
#[must_use]
pub fn gate_out_of_the_field(envelope: &[Pt], gate: Pt) -> Pt {
    push_out_of(envelope, gate, SPUR_SETBACK_FT)
}

/// What the track out reads: the sweep's site, the dry exit's, the thread's fabric, the connector's law, the houses and the seat.
pub struct Choice<'a> {
    /// The sweep's ground.
    pub sweep: &'a TrackSite<'a>,
    /// The dry exit's ground.
    pub dry: &'a DrySite<'a>,
    /// The thread's fabric.
    pub fabric: &'a Fabric<'a>,
    /// The connector's law.
    pub law: &'a Law<'a>,
    /// The steadings and the buildings' boxes as polygons, each with its box, the gateway clears.
    pub standing: &'a [(Vec<Pt>, Box4)],
    /// The seat's axes.
    pub axes: Axes,
    /// The skeleton's gateway, where no house stands.
    pub fallback: Pt,
}

/// The sweep from one gateway: the clean bearing, the least-bad dry one, or the dry exit from the gateway pulled clear; None
/// where none leaves the frame.
fn swept(c: &Choice, gate: Pt, tests: &mut Counts) -> Option<Vec<Pt>> {
    match connector(c.sweep, gate, tests) {
        (_, Swept::Clean(p) | Swept::Least(p)) => Some(p),
        (start, Swept::DryExit) => connector_dry_exit(c.dry, start, tests),
    }
}

/// The track from the gateway, stepped half the connector's tread off every footprint a way may not run on and swept; where that
/// finds no dry way out, from the cloud's edge on a bearing turned off the downslope, the nearest turn first.
#[must_use]
pub fn gateway_track(c: &Choice, gate: Pt, tests: &mut Counts) -> Option<Vec<Pt>> {
    let walls: Vec<&[Pt]> = c.law.forbidding.iter().map(|e| e.0.as_slice()).collect();
    let gate = clear_of_bands(gate, &walls, CONNECTOR_WIDTH_FT / 2.0);
    swept(c, gate, tests).or_else(|| {
        TURNS_DEG.iter().find_map(|&deg| {
            let turned =
                cluster_gateway(c.fabric.houses, c.axes, c.fallback, deg, c.standing, tests);
            swept(c, gate_out_of_the_field(c.fabric.envelope, turned), tests)
        })
    })
}

/// The track out, chosen once the last house stands: the gateway on the cloud's downslope edge out of the field, swept, then
/// bent round the field and threaded through the steadings; the run and whether it gave up a wood seat, None where no way
/// leaves the frame.
#[must_use]
pub fn choose_track_out(c: &Choice, tests: &mut Counts) -> Option<(Vec<Pt>, bool)> {
    let first = cluster_gateway(c.fabric.houses, c.axes, c.fallback, 0.0, c.standing, tests);
    let track = gateway_track(c, gate_out_of_the_field(c.fabric.envelope, first), tests)?;
    connector_through(&track, c.fabric, c.law, c.dry, tests)
}
