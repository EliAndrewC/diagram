//! Each form the Python's parser takes, and each it refuses.

use super::parse;

/// 2026-10-11T00:00:00Z.
const MIDNIGHT: f64 = 1_791_676_800.0;

fn same(a: &str, want: f64) {
    assert!(parse(a).is_some_and(|g| (g - want).abs() < 1e-6), "{a}");
}

#[test]
fn every_date_form_is_the_same_day() {
    for date in ["2026-10-11", "20261011", "2026-W41-7", "2026W417"] {
        same(&format!("{date}T00:00:00Z"), MIDNIGHT);
    }
    same("2026-W42T00:00:00Z", MIDNIGHT + 86_400.0);
    same("2026W42T00:00:00Z", MIDNIGHT + 86_400.0);
}

#[test]
fn a_date_alone_and_a_naive_time_are_local() {
    let offset = f64::from(i32::try_from(super::offset_at(1_791_676_800)).unwrap());
    same("2026-10-11", MIDNIGHT - offset);
    same("2026-10-11T01:00:00", MIDNIGHT + 3600.0 - offset);
}

#[test]
fn every_time_form_and_any_one_separator() {
    same("2026-10-11T21Z", MIDNIGHT + 75_600.0);
    same("2026-10-11 21:08Z", MIDNIGHT + 76_080.0);
    same("2026-10-11x2108Z", MIDNIGHT + 76_080.0);
    same("2026-10-11T210834Z", MIDNIGHT + 76_114.0);
    same("2026-10-11T21:08:34.5Z", MIDNIGHT + 76_114.5);
    same("2026-10-11T21:08:34,25Z", MIDNIGHT + 76_114.25);
    same("2026-10-11T21:08:34.1234569Z", MIDNIGHT + 76_114.123_456);
    same("2026-10-11T24:00:00Z", MIDNIGHT + 86_400.0);
}

#[test]
fn every_zone_form() {
    let at = MIDNIGHT + 76_114.0;
    same("2026-10-11T21:08:34+00:00", at);
    same("2026-10-11T21:08:34-04:00", at + 14_400.0);
    same("2026-10-11T21:08:34+01", at - 3600.0);
    same("2026-10-11T21:08:34+0130", at - 5400.0);
    same("2026-10-11T21:08:34+01:30:15", at - 5415.0);
}

#[test]
fn what_python_refuses_is_refused() {
    for bad in [
        "",
        "soon",
        "2026",
        "2026-10",
        "2026-13-01",
        "2026-02-30",
        "0000-01-01",
        "2026-W54-1",
        "2026-W00-1",
        "2026-W41-8",
        "2026-1011",
        "2026-10-11T",
        "2026-10-11T2",
        "2026-10-11T25:00:00",
        "2026-10-11T24:01:00",
        "2026-10-11T21:60:00",
        "2026-10-11T21:08:60",
        "2026-10-11T21.5",
        "2026-10-11T21:08:34.",
        "2026-10-11T21:08:34+24:00",
        "2026-10-11T21:08:34+x",
        "2026-10-11T21:08:34:01",
        "2026-10-11T2108:34:1",
        "2026-10-11Tab:cd:ef",
        "2026-1a-11",
        "2026-W4x",
        "2026Wxx",
        "2026-Wxx-1",
        "2026-W41-x",
    ] {
        assert!(parse(bad).is_none(), "{bad} should be refused");
    }
}

#[test]
fn a_leap_day_is_a_day_only_in_a_leap_year() {
    assert!(parse("2024-02-29T00:00:00Z").is_some());
    assert!(parse("2000-02-29T00:00:00Z").is_some());
    assert!(parse("2023-02-29T00:00:00Z").is_none());
    assert!(parse("1900-02-29T00:00:00Z").is_none());
    assert!(parse("2026-04-31T00:00:00Z").is_none());
    assert!(parse("2026-01-15T00:00:00Z").is_some());
}

#[test]
fn week_years_vary_in_length() {
    assert!(parse("2026-W53-1T00:00:00Z").is_some());
    assert!(parse("2025-W53-1T00:00:00Z").is_none());
    assert!(parse("0000-W01-1T00:00:00Z").is_none());
}

#[test]
fn the_parsers_odd_corners_are_kept() {
    let at = MIDNIGHT + 76_114.0;
    same("2026-10-11T21:08:34.Z", at);
    same("2026-10-11T21:08:34,+01", at - 3600.0);
    same("2026-10-11T21:08.+00", MIDNIGHT + 76_080.0);
    same("2026-W41-04:00Z", MIDNIGHT - 518_400.0 + 14_400.0);
    same("2026-10-11\u{e9}21:08:34Z", at);
    same("2026-10-11T210834,5Z", at + 0.5);
    same("2026-10-11T2108349Z", at);
    same("2026-10-11T21:08:34+01:99", at - 9540.0);
    assert!(parse("2026-10-11T21:08:34:01").is_none());
    assert!(parse("2026-10-11T21:08:34.12xZ").is_none());
    assert!(parse("2026-10-11T21:08:34+01:").is_none());
    assert!(parse("2026-10-11T21:08:34Zz").is_none());
    assert!(parse("9999-12-31T24:00:00Z").is_none());
    assert!(parse("0001-01-01T21:08:34").is_none());
    assert!(parse("0001-01-03T21:08:34").is_some());
    assert!(parse("0001-01-01T21:08:34Z").is_some());
    assert!(parse("2026-W4").is_none());
    assert!(parse("2026-W41-").is_none());
    assert!(parse("2026W41T00Z").is_some());
    assert!(parse("2026W417").is_some());
}

#[test]
fn a_repeated_hour_is_its_first_and_a_skipped_one_moves_on() {
    let at = 1_000_000;
    let west = |t: i64| if t < at { -14_400 } else { -18_000 };
    assert_eq!(super::local_to_utc(at - 16_000, &west), at - 1_600);
    assert_eq!(super::local_to_utc(at + 1_000, &west), at + 19_000);
    let east = |t: i64| if t < at { 3_600 } else { 0 };
    assert_eq!(super::local_to_utc(at + 1_000, &east), at - 2_600);
    let forward = |t: i64| if t < at { 0 } else { 3_600 };
    assert_eq!(super::local_to_utc(at + 1_000, &forward), at + 1_000);
}

#[test]
fn the_last_year_reads_its_offset_from_four_centuries_before() {
    let late = 253_402_232_400;
    assert_eq!(
        super::offset_at(late),
        super::offset_at(late - 12_622_780_800)
    );
}

#[test]
fn a_long_digit_run_after_a_week_date_is_told_by_its_parity() {
    assert!(parse("2026W41700").is_some());
    assert!(parse("2026W417000").is_some());
    assert!(parse("2026-10-11T21:08x34Z").is_none());
}
