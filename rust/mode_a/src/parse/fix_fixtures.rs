//! The sheets of step 1's defect fixes (feature 449 T177, T182): each draws the form a fixed rule now judges as its page says, held here
//! to the verdict the fix gives - each test fails on the rule as it stood before its fix; `check_fixtures.rs` reports each too.
//!
//! Research:
//!     the defect fixes' sheets - NONE: test sheets, deciding nothing about a building

/// A kitchen bed north of a notice board, which casts from 0190's 10 ft (T177) - it stood in `NOT_STANDING` and cast nothing.
pub(crate) const BOARD: &str = r##"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
<rect id="precinct" x="20" y="20" width="360" height="260" fill="url(#court-earth)"/>
<rect x="180" y="128" width="30" height="12" fill="url(#vegetable-rows)" data-kind="vegetable garden"/>
<rect x="171" y="142" width="48" height="18" fill="#E8D2A8" data-kind="notice board"/>
</svg>
"##;

/// A shrine whose two arches stand 12 ft apart, the innermost 12 ft off the hall and the first moved inward with it (T177): the count is
/// refused, the first arch's place is not, 0220 letting the innermost hold.
pub(crate) const ARCHES_HELD: &str = r##"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
<rect id="precinct" x="20" y="20" width="360" height="260" fill="url(#court-earth)"/>
<rect id="approach" x="190" y="80" width="20" height="200" fill="url(#keiko-earth)"/>
<rect id="hall" x="150" y="40" width="100" height="40" fill="#DDB87A"/>
<rect id="sanctuary" x="190" y="22" width="20" height="16" fill="#C9876C"/>
<rect id="arch" x="185" y="116" width="30" height="4" fill="#8C6F3E"/>
<rect id="arch" x="185" y="152" width="30" height="4" fill="#8C6F3E"/>
<rect id="well" x="220" y="100" width="10" height="10" fill="#9C8C70"/>
</svg>
"##;

/// Three arches, the innermost first in the document and 20 ft off the hall, the outermost at the precinct's edge (T177): passed, the
/// first arch now the one farthest from the hall - the old check took the document's first and refused it.
pub(crate) const ARCHES_ORDER: &str = r##"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
<rect id="precinct" x="20" y="20" width="360" height="260" fill="url(#court-earth)"/>
<rect id="approach" x="190" y="80" width="20" height="200" fill="url(#keiko-earth)"/>
<rect id="hall" x="150" y="40" width="100" height="40" fill="#DDB87A"/>
<rect id="sanctuary" x="190" y="22" width="20" height="16" fill="#C9876C"/>
<rect id="arch" x="185" y="140" width="30" height="4" fill="#8C6F3E"/>
<rect id="arch" x="185" y="272" width="30" height="4" fill="#8C6F3E"/>
<rect id="arch" x="185" y="206" width="30" height="4" fill="#8C6F3E"/>
<rect id="well" x="220" y="100" width="10" height="10" fill="#9C8C70"/>
</svg>
"##;

/// Three arches, one off the approach, the first inside the precinct and the innermost 20 ft off the hall (T177): every arch is held
/// to the approach, and the first arch's place is refused, the innermost not holding its 12 ft.
pub(crate) const ARCHES_ADRIFT: &str = r##"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
<rect id="precinct" x="20" y="20" width="360" height="260" fill="url(#court-earth)"/>
<rect id="approach" x="190" y="80" width="20" height="200" fill="url(#keiko-earth)"/>
<rect id="hall" x="150" y="40" width="100" height="40" fill="#DDB87A"/>
<rect id="sanctuary" x="190" y="22" width="20" height="16" fill="#C9876C"/>
<rect id="arch" x="185" y="140" width="30" height="4" fill="#8C6F3E"/>
<rect id="arch" x="230" y="176" width="30" height="4" fill="#8C6F3E"/>
<rect id="arch" x="185" y="212" width="30" height="4" fill="#8C6F3E"/>
<rect id="well" x="220" y="100" width="10" height="10" fill="#9C8C70"/>
</svg>
"##;

/// A fence round the sanctuary alone (T177): refused, 0223 drawing none however rich the parish - it passed as a donation.
pub(crate) const SANCTUARY_FENCE: &str = r##"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
<rect id="precinct" x="20" y="20" width="360" height="260" fill="url(#court-earth)"/>
<rect id="approach" x="190" y="100" width="20" height="180" fill="url(#keiko-earth)"/>
<rect id="hall" x="150" y="60" width="100" height="40" fill="#DDB87A"/>
<rect id="sanctuary" x="190" y="30" width="20" height="16" fill="#C9876C"/>
<rect id="arch" x="185" y="272" width="30" height="4" fill="#8C6F3E"/>
<g id="fence"><line x1="184" y1="26" x2="216" y2="26"/><line x1="184" y1="26" x2="184" y2="52"/><line x1="216" y1="26" x2="216" y2="52"/><line x1="184" y1="52" x2="216" y2="52"/></g>
</svg>
"##;

/// A walled compound (T177): the Imperial road at its own 30 ft ending at the main gate (passed, 0088 - it was refused as wider than the
/// gate), a 10 ft lane into a 7 ft side gate (refused), a barracks of four dwellings with three doors (refused - one door on the block
/// passed every dwelling), a servants' common room behind one door, its bays behind a dashed sliding partition (0097), and a residence's
/// rooms behind the house's door (both passed).
pub(crate) const ROWS: &str = r##"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
<rect id="precinct" x="20" y="20" width="360" height="260" fill="url(#court-earth)" data-kind="outer court"/>
<g stroke="#2D2A24" stroke-width="9" stroke-linecap="square">
<line x1="20" y1="20" x2="380" y2="20"/><line x1="20" y1="20" x2="20" y2="280"/>
<line x1="20" y1="280" x2="170" y2="280"/><line x1="216" y1="280" x2="380" y2="280"/>
<line x1="380" y1="20" x2="380" y2="100"/><line x1="380" y1="130" x2="380" y2="280"/>
</g>
<g data-kind="main gate"><rect x="168" y="274" width="6" height="12"/><rect x="212" y="274" width="6" height="12"/></g>
<g data-kind="road" stroke="#B8A27A" stroke-width="90" fill="none"><path d="M 193 330 L 193 282"/></g>
<g data-kind="road" stroke="#B8A27A" stroke-width="30" fill="none"><path d="M 430 115 L 382 115"/></g>
<g data-kind="barracks"><rect x="60" y="200" width="120" height="40" fill="#C9A57A" stroke="#6B4F2A"/>
<line x1="90" y1="200" x2="90" y2="240" stroke="#6B4F2A"/><line x1="120" y1="200" x2="120" y2="240" stroke="#6B4F2A"/>
<line x1="150" y1="200" x2="150" y2="240" stroke="#6B4F2A"/>
<rect x="68" y="236" width="14" height="4" fill="#B89868" data-kind="door"/><rect x="98" y="236" width="14" height="4" fill="#B89868" data-kind="door"/>
<rect x="128" y="236" width="14" height="4" fill="#B89868" data-kind="door"/></g>
<g data-kind="servants' quarters"><rect x="250" y="40" width="80" height="40" fill="#C9A57A" stroke="#6B4F2A"/>
<line x1="300" y1="40" x2="300" y2="80" stroke="#6B4F2A" stroke-dasharray="4 3"/>
<rect x="280" y="76" width="14" height="4" fill="#B89868" data-kind="door"/></g>
<g data-kind="residence"><rect x="60" y="40" width="120" height="60" fill="#DDB87A" stroke="#5A3F1E"/>
<line x1="100" y1="40" x2="100" y2="100" stroke="#5A3F1E"/><rect x="70" y="96" width="14" height="4" fill="#B89868" data-kind="door"/></g>
<text x="200" y="14" font-size="14" font-weight="bold">THE ROWS</text>
</svg>
"##;

/// A shrine whose basin stands on its approach and whose well stands under its second arch (T182): both refused - the basin was judged by
/// nothing, and an arch past the first by none.
pub(crate) const BASIN: &str = r##"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
<rect id="precinct" x="20" y="20" width="360" height="260" fill="url(#court-earth)"/>
<rect id="approach" x="190" y="80" width="20" height="200" fill="url(#keiko-earth)"/>
<rect id="hall" x="150" y="40" width="100" height="40" fill="#DDB87A"/>
<rect id="sanctuary" x="190" y="22" width="20" height="16" fill="#C9876C"/>
<rect id="arch" x="185" y="116" width="30" height="4" fill="#8C6F3E"/>
<rect id="arch" x="185" y="152" width="30" height="4" fill="#8C6F3E"/>
<rect id="arch" x="185" y="272" width="30" height="4" fill="#8C6F3E"/>
<rect id="basin" x="195" y="200" width="9" height="9" fill="#9C8C70"/>
<rect id="well" x="208" y="150" width="15" height="15" fill="#9C8C70"/>
</svg>
"##;

/// A residence with one privy of its own (T182): refused, 0101 giving the house two, the guests' and the family's - one passed.
pub(crate) const ONE_PRIVY: &str = r##"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
<rect id="precinct" x="20" y="20" width="360" height="260" fill="url(#court-earth)"/>
<g data-kind="residence"><rect x="60" y="40" width="120" height="60" fill="#DDB87A"/></g>
<rect x="180" y="50" width="15" height="15" fill="#7E726A" data-kind="latrine" data-part-of="residence"/>
<rect x="300" y="200" width="15" height="15" fill="#7E726A" data-kind="latrine"/>
<rect x="320" y="200" width="15" height="15" fill="#7E726A" data-kind="latrine"/>
</svg>
"##;

/// A bath's tub equally near the bath and the house (T182): passed, the bath tied for nearest - the check took the first host in plan
/// order, the house, and judged the tub by the house's door 38 ft away.
pub(crate) const BATH_TUB: &str = r##"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
<rect id="precinct" x="20" y="20" width="360" height="260" fill="url(#court-earth)"/>
<rect x="60" y="40" width="120" height="60" fill="#DDB87A" data-kind="residence"/>
<rect x="70" y="96" width="14" height="4" fill="#4A3318" data-kind="door"/>
<rect x="188" y="40" width="30" height="24" fill="#C9A57A" data-kind="bath"/>
<g fill="#8FB0C6" data-kind="fire-water tubs"><circle cx="184" cy="60" r="3.8"/></g>
</svg>
"##;

/// A walled compound's three lodgings each behind one door (T187): an undivided barracks and an undivided retainers' long-house refused,
/// 0097 dividing a barracks into dwellings and 0106 giving each long-house dwelling its door - one door passed both as a common room -
/// and an undivided servants' quarters passed, 0097's common room.
pub(crate) const UNDIVIDED: &str = r##"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
<rect id="precinct" x="20" y="20" width="360" height="260" fill="url(#court-earth)" data-kind="outer court"/>
<g data-kind="barracks"><rect x="60" y="200" width="120" height="40" fill="#C9A57A" stroke="#6B4F2A"/>
<rect x="68" y="236" width="14" height="4" fill="#B89868" data-kind="door"/></g>
<g data-kind="retainers' quarters"><rect x="60" y="60" width="120" height="40" fill="#C9A57A" stroke="#6B4F2A"/>
<rect x="68" y="96" width="14" height="4" fill="#B89868" data-kind="door"/></g>
<g data-kind="servants' quarters"><rect x="250" y="40" width="80" height="40" fill="#C9A57A" stroke="#6B4F2A"/>
<rect x="280" y="76" width="14" height="4" fill="#B89868" data-kind="door"/></g>
</svg>
"##;

/// The defect fixes' sheets by name, a name's prefix giving its tier as the red fixtures' do.
pub(crate) fn sheets() -> Vec<(&'static str, &'static str)> {
    vec![
        ("plain-fix-board.svg", BOARD),
        ("hoshigaoka-fix-arches-held.svg", ARCHES_HELD),
        ("hoshigaoka-fix-arches-order.svg", ARCHES_ORDER),
        ("hoshigaoka-fix-arches-adrift.svg", ARCHES_ADRIFT),
        ("hoshigaoka-fix-sanctuary-fence.svg", SANCTUARY_FENCE),
        ("ochiba-fix-rows.svg", ROWS),
        ("hoshigaoka-fix-basin.svg", BASIN),
        ("ochiba-fix-one-privy.svg", ONE_PRIVY),
        ("ochiba-fix-bath-tub.svg", BATH_TUB),
        ("ochiba-fix-undivided.svg", UNDIVIDED),
    ]
}

#[cfg(test)]
mod tests {
    use super::{ARCHES_ADRIFT, ARCHES_HELD, ARCHES_ORDER, BOARD, ROWS, SANCTUARY_FENCE};
    use super::{BASIN, BATH_TUB, ONE_PRIVY, UNDIVIDED};
    use crate::audit::checks::{gap_tag, tubs_off_their_doors, Gap, DOOR_FLUSH_TOL_PX};
    use crate::audit::program_rules::{lodging_entrances, privies_by_zone, PRIVY_MIN};
    use crate::audit::roads::{gate_feeds_its_road, side_gates_met, ROAD_GATE_TOL_FT};
    use crate::audit::shared::{
        arch_on_approach, gate_widths, no_precinct_enclosure, well_clear_of_arch, EDGE_TOL_FT,
        GATE_MAX_FT, GATE_MIN_FT,
    };
    use crate::audit::sun::{casters, garden_sun, gardens, Bed, NOTICE_BOARD_FT};
    use crate::audit::Sheet;
    use crate::parse::parse_svg;

    const INSIDE: &str =
        "the arch stands inside the precinct rather than at its edge, where the way enters";

    #[test]
    fn the_notice_board_casts_from_0190_s_ten_feet() {
        let (plan, svg) = (parse_svg(BOARD).unwrap(), Sheet::new(BOARD));
        let beds = gardens(&plan, &svg).unwrap();
        let bed = Bed::new(beds[0].0);
        let cs = casters(&plan, &svg, &bed).unwrap();
        assert_eq!(
            cs.iter()
                .map(|c| (c.what.as_str(), c.height_ft))
                .collect::<Vec<_>>(),
            vec![("notice board", NOTICE_BOARD_FT)]
        );
        let found = garden_sun(&plan, &svg).unwrap();
        assert_eq!(
            found
                .iter()
                .map(|f| f.rsplit(" - ").next().unwrap())
                .collect::<Vec<_>>(),
            ["shaded by notice board"]
        );
    }

    #[test]
    fn an_avenue_is_judged_by_its_count_its_first_arch_and_its_innermost() {
        let check = |s: &str| arch_on_approach(&parse_svg(s).unwrap(), EDGE_TOL_FT).unwrap();
        assert_eq!(
            check(ARCHES_HELD),
            vec!["the approach runs under 2 arches - a shrine's avenue is one, three or seven"]
        );
        assert_eq!(check(ARCHES_ORDER), Vec::<String>::new());
        assert_eq!(
            check(ARCHES_ADRIFT),
            vec![
                "the arch does not straddle the approach - a gateway stands over the way",
                INSIDE
            ]
        );
        // with no hall the first arch is the document's first, and no innermost holds
        let no_hall = ARCHES_ORDER.replace(r#"id="hall""#, r#"id="nave""#);
        assert_eq!(check(&no_hall), vec![INSIDE]);
    }

    #[test]
    fn a_wide_break_s_fix_gives_an_attested_gate_width() {
        // T177: the fix text gave ~13 ft, a width no page gives; 0093 gives a magistrate's gate about 6 to 12 ft
        let sheet = r##"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
<rect id="precinct" x="20" y="20" width="360" height="260" fill="url(#court-earth)"/>
<g stroke="#2D2A24" stroke-width="9" stroke-linecap="square"><line x1="20" y1="280" x2="100" y2="280"/><line x1="180" y1="280" x2="380" y2="280"/></g>
</svg>"##;
        let found = gate_widths(&parse_svg(sheet).unwrap(), GATE_MIN_FT, GATE_MAX_FT);
        assert_eq!(
            found
                .iter()
                .map(|f| f.rsplit(" - ").next().unwrap())
                .collect::<Vec<_>>(),
            ["a gate is drawn at passage width (about 6 to 12 ft, 0093), or a structure stands in the break"]
        );
    }

    #[test]
    fn a_fence_round_the_precinct_is_refused_with_no_donation_offered() {
        // T177: the message offered a sanctuary fence as a richer shrine's donation, where 0223 draws none however rich the parish
        let ringed = SANCTUARY_FENCE.replace(
            r#"<line x1="184" y1="26" x2="216" y2="26"/>"#,
            r#"<line x1="140" y1="22" x2="260" y2="110"/>"#,
        );
        assert_eq!(
            no_precinct_enclosure(&parse_svg(&ringed).unwrap()).unwrap(),
            vec!["a fence rings the precinct (its extent takes in the hall) - a village shrine's ground is marked by its arch and its wood, with no fence round its precinct or its sanctuary"]
        );
    }

    #[test]
    fn a_fence_round_the_sanctuary_is_refused() {
        assert_eq!(
            no_precinct_enclosure(&parse_svg(SANCTUARY_FENCE).unwrap()).unwrap(),
            vec!["a fence rings the sanctuary - no fence is drawn round a village shrine's sanctuary, however rich the parish"]
        );
    }

    #[test]
    fn the_road_at_the_main_gate_keeps_its_width_and_a_lane_its_side_gate_s() {
        let (plan, svg) = (parse_svg(ROWS).unwrap(), Sheet::new(ROWS));
        assert_eq!(
            gate_feeds_its_road(&svg, &plan, ROAD_GATE_TOL_FT).unwrap(),
            vec!["a 10.0 ft road meets a 7.0 ft side gate at svg(382,115) - a lane is no wider than the side gate it feeds"]
        );
    }

    #[test]
    fn an_end_in_the_main_gate_s_opening_is_the_main_gate_s_though_its_posts_stand_off() {
        // the posts stand in the middle of a wide opening: an end at the opening's far side meets the main gate's own opening
        let sheet = r##"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
<rect id="precinct" x="20" y="20" width="360" height="260" fill="url(#court-earth)"/>
<g stroke="#2D2A24" stroke-width="9" stroke-linecap="square"><line x1="20" y1="280" x2="100" y2="280"/><line x1="160" y1="280" x2="380" y2="280"/></g>
<g data-kind="main gate"><rect x="125" y="276" width="3" height="8"/><rect x="132" y="276" width="3" height="8"/></g>
</svg>"##;
        let plan = parse_svg(sheet).unwrap();
        assert_eq!(side_gates_met((108.0, 280.0), 3.0, &plan), None);
        assert_eq!(side_gates_met((130.0, 280.0), 3.0, &plan), None);
        assert_eq!(side_gates_met((300.0, 150.0), 3.0, &plan), Some(Vec::new()));
    }

    #[test]
    fn the_basin_and_the_well_are_held_off_the_way_and_every_arch() {
        assert_eq!(
            well_clear_of_arch(&parse_svg(BASIN).unwrap()),
            vec![
                "the basin at svg(195,200) stands on the approach",
                "the well at svg(208,150) stands on the approach",
                "the well at svg(208,150) stands on the arch"
            ]
        );
        // T182 (its claims round): a well no longer stands in for the basin - a sheet with its well and no basin is refused
        let well_only = BASIN.replace(
            r##"<rect id="basin" x="195" y="200" width="9" height="9" fill="#9C8C70"/>"##,
            "",
        );
        assert_eq!(
            well_clear_of_arch(&parse_svg(&well_only).unwrap()),
            vec!["no basin on the sheet - a village shrine has its stone basin beside the approach (mark it id=\"basin\"); a well comes in addition, never in its place"]
        );
        // a basin alone is the shrine's water; with no arch the approach is not judged
        let basin_only = BASIN.replace(
            r##"<rect id="well" x="208" y="150" width="15" height="15" fill="#9C8C70"/>"##,
            "",
        );
        assert_eq!(
            well_clear_of_arch(&parse_svg(&basin_only).unwrap()).len(),
            1
        );
        let no_arch = basin_only.replace(r#"id="arch""#, r#"id="gate""#);
        assert_eq!(
            well_clear_of_arch(&parse_svg(&no_arch).unwrap()),
            vec!["the sheet declares no approach / arch (mark the rects id=\"approach\", id=\"arch\")"]
        );
    }

    #[test]
    fn the_residence_has_two_privies_of_its_own() {
        assert_eq!(
            privies_by_zone(&Sheet::new(ONE_PRIVY), PRIVY_MIN).unwrap(),
            vec!["1 privy is the residence's own - the house has 2, the guests' and the family's (attach the other to a block)"]
        );
    }

    #[test]
    fn a_kura_gap_under_the_six_foot_floor_is_tight() {
        let gap = |ft: f64, kura: bool| Gap {
            ft,
            orient: "H",
            mx: 0.0,
            my: 0.0,
            kura,
        };
        assert_eq!(
            [5.0, 6.0, 10.0, 11.0].map(|ft| gap_tag(&gap(ft, true))),
            [
                "TIGHT (kura gap <6 ft)",
                "fire-gap OK (kura)",
                "fire-gap OK (kura)",
                "LOOSE (kura gap >10 ft)"
            ]
        );
        assert_eq!(gap_tag(&gap(5.0, false)), "tight");
    }

    #[test]
    fn a_bath_tied_for_nearest_spares_its_tub_the_door() {
        let plan = parse_svg(BATH_TUB).unwrap();
        assert_eq!(tubs_off_their_doors(&plan), Vec::new());
        // the bath gone, the house's door judges the tub
        let alone = parse_svg(&BATH_TUB.replace(
            r##"<rect x="188" y="40" width="30" height="24" fill="#C9A57A" data-kind="bath"/>"##,
            "",
        ))
        .unwrap();
        assert_eq!(tubs_off_their_doors(&alone).len(), 1);
    }

    #[test]
    fn each_dwelling_of_a_divided_row_has_a_door_of_its_own() {
        let (plan, svg) = (parse_svg(ROWS).unwrap(), Sheet::new(ROWS));
        assert_eq!(
            lodging_entrances(&svg, &plan, DOOR_FLUSH_TOL_PX).unwrap(),
            vec!["the barracks at svg(60,200) has 1 of its 4 dwellings with no door of its own on its outer wall - each dwelling of a row is entered by its own door"]
        );
    }

    #[test]
    fn a_barracks_or_a_long_house_behind_one_door_is_refused_a_servants_common_room_passed() {
        let (plan, svg) = (parse_svg(UNDIVIDED).unwrap(), Sheet::new(UNDIVIDED));
        assert_eq!(
            lodging_entrances(&svg, &plan, DOOR_FLUSH_TOL_PX).unwrap(),
            vec![
                "the barracks at svg(60,200) is undivided - a barracks is divided into dwellings, each with a door of its own; only a servants' quarters is drawn as one common room behind one door",
                "the retainers' quarters at svg(60,60) is undivided - a retainers' quarters is divided into dwellings, each with a door of its own; only a servants' quarters is drawn as one common room behind one door",
            ]
        );
    }
}
