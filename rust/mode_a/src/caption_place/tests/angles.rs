//! The placer's rules of a caption's angle (feature 449 T202), split from the rule tests at the file-size bar: research/questions/0242's
//! drawing page, "A caption turns with the thing it names", one test a rule.
//!
//! Research: the angle tests - NONE: tests of the angle rules claimed where the placer decides them, deciding nothing themselves

use super::super::captions::readable;
use super::super::geom::{turn, Pt};
use super::super::placed;
use super::super::search::How;
use super::{block_at, of, seats, sheet};

/// 0242: a caption takes its feature's angle, is never drawn upside down, and a quarter turn keeps it level.
#[test]
fn a_caption_turns_with_its_feature_never_upside_down() {
    let turned = |deg: i32| {
        sheet(
            400,
            300,
            &format!(
                r##"<g data-kind="hall" transform="rotate({deg} 200 150)"><rect x="140" y="120" width="120" height="60" fill="#DDB87A"/><text font-size="8">hall</text></g>"##
            ),
        )
    };
    assert!((of(&seats(&turned(30)), "hall").angle - 30.0).abs() < 1e-6);
    assert!((of(&seats(&turned(150)), "hall").angle + 30.0).abs() < 1e-6);
    assert!(of(&seats(&turned(90)), "hall").angle.abs() < 1e-9);
    let out = placed(&turned(30)).unwrap();
    assert!(out.contains("transform=\"rotate("), "{out}");
    assert!(readable(270.0).abs() < 1e-12);
    assert!((readable(-150.0) - 30.0).abs() < 1e-9);
}

/// 0242: a road's name follows the road, at its bearing.
#[test]
fn a_roads_name_follows_its_bearing() {
    let src = sheet(
        400,
        300,
        r##"<g data-kind="road"><path d="M 30 261.5 L 50 250 L 350 77" stroke="#B89060" stroke-width="6" fill="none"/><text font-size="8">the road</text></g>"##,
    );
    let all = seats(&src);
    let s = of(&all, "the road");
    assert!((s.angle + 30.0).abs() < 0.1);
    // above the road as the words read: in the road's own frame the caption stands on the smaller-y side of its line
    let back = |p: Pt| turn(p, -s.angle);
    assert!(back(s.center).1 < back((200.0, 163.5)).1);
}

/// 0242: a road's name follows the road - a road running north-south is named along it, turned a quarter, not level across it (the
/// quarter-turn rule is a turned outline's, which has a level edge of its own; a road has none).
#[test]
fn a_north_south_roads_name_runs_along_it() {
    for d in ["M 200 20 L 200 280", "M 200 280 L 200 20"] {
        let src = sheet(
            400,
            300,
            &format!(
                r##"<g data-kind="road"><path d="{d}" stroke="#B89060" stroke-width="6" fill="none"/><text font-size="8">the road</text></g>"##
            ),
        );
        let all = seats(&src);
        assert!((of(&all, "the road").angle - 90.0).abs() < 1e-6, "{d}");
    }
}

/// A turned feature's caption is searched in its own frame: inside off a blocked middle, and swept when every place at the gap is
/// taken.
#[test]
fn a_turned_features_places_are_read_in_its_frame() {
    let src = sheet(
        400,
        300,
        r##"<g data-kind="hall" transform="rotate(20 200 150)"><rect x="120" y="110" width="160" height="80" fill="#DDB87A"/><text font-size="8">hall</text></g><rect x="190" y="140" width="20" height="20" fill="#333" data-kind="pillar"/>"##,
    );
    let all = seats(&src);
    let s = of(&all, "hall");
    let d = s.how.offset().unwrap();
    assert!(d > 0.0);
    let boxed = sheet(
        400,
        300,
        &format!(
            r##"<g data-kind="well" transform="rotate(20 200 150)"><rect x="194" y="146" width="12" height="8" fill="#9C8C70"/><text font-size="8">well</text></g>{}"##,
            [
                block_at((150, 100, 100, 44)),
                block_at((150, 156, 100, 60)),
                block_at((120, 100, 74, 116)),
                block_at((206, 100, 74, 116))
            ]
            .concat()
        ),
    );
    let all = seats(&boxed);
    assert!(matches!(
        of(&all, "well").how,
        How::Swept(..) | How::CoverLeast(_)
    ));
}

/// A caption beside a turned feature, written outside the turned group, carries its own turn; a leader with no ink of its own is drawn
/// in the sheet's caption ink.
#[test]
fn a_caption_outside_its_turned_group_carries_its_turn() {
    let src = sheet(
        400,
        300,
        r##"<g transform="rotate(30 200 150)"><rect data-id="h" x="140" y="120" width="120" height="60" fill="#DDB87A"/></g><g data-kind="hall"><text font-size="8" data-names="h">hall</text></g>"##,
    );
    let out = placed(&src).unwrap();
    assert!(out.contains("transform=\"rotate(30.0"), "{out}");
    let walls = [
        block_at((150, 100, 100, 44)),
        block_at((150, 156, 100, 60)),
        block_at((120, 100, 74, 116)),
        block_at((206, 100, 74, 116)),
    ]
    .concat();
    let out = placed(&sheet(400, 300, &format!(r#"{walls}<g data-kind="well"><circle cx="200" cy="150" r="5"/><text font-size="8">well</text></g>"#))).unwrap();
    assert!(out.contains("stroke=\"#3A2E1C\""), "{out}");
}
