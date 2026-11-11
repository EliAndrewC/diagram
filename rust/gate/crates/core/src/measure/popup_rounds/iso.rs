//! An ISO time as Python's `datetime.fromisoformat(...).timestamp()` reads it (`ask:449-T77-bad-since`: which values parse stays the Python's): a date
//! in any of its forms, any one separator, a time to any precision and a zone in any of its forms; a time with no zone is the machine's local time.

use std::process::Command;

fn digits(text: &str) -> Option<i64> {
    (!text.is_empty() && text.bytes().all(|b| b.is_ascii_digit())).then(|| text.parse().ok())?
}

fn leap(year: i64) -> bool {
    year % 4 == 0 && (year % 100 != 0 || year % 400 == 0)
}

fn days_in(year: i64, month: i64) -> i64 {
    match month {
        2 => 28 + i64::from(leap(year)),
        4 | 6 | 9 | 11 => 30,
        _ => 31,
    }
}

/// Days since 1970-01-01 of a proleptic Gregorian date.
fn epoch_days(year: i64, month: i64, day: i64) -> i64 {
    let (y, m) = if month <= 2 {
        (year - 1, month + 9)
    } else {
        (year, month - 3)
    };
    let era = y.div_euclid(400);
    let of_era = y - era * 400;
    era * 146_097 + of_era * 365 + of_era / 4 - of_era / 100 + (153 * m + 2) / 5 + day - 1 - 719_468
}

fn calendar(year: i64, month: i64, day: i64) -> Option<i64> {
    ((1..=9999).contains(&year)
        && (1..=12).contains(&month)
        && (1..=days_in(year, month)).contains(&day))
    .then(|| epoch_days(year, month, day))
}

/// An ISO week date's day number: week 1 holds the year's first Thursday.
fn week_date(year: i64, week: i64, day: i64) -> Option<i64> {
    if !(1..=9999).contains(&year) || !(1..=7).contains(&day) || week < 1 {
        return None;
    }
    let weekday = |n: i64| (n + 3).rem_euclid(7);
    let jan4 = epoch_days(year, 1, 4);
    let start = jan4 - weekday(jan4);
    let next = epoch_days(year + 1, 1, 4);
    let last_week = (next - weekday(next) - start) / 7;
    (week <= last_week).then_some(start + (week - 1) * 7 + day - 1)
}

/// Where the date ends, `CPython`'s `_find_isoformat_datetime_separator`: a week date and a hyphen separator are told apart as far as they can be.
fn separator(b: &[u8]) -> Option<usize> {
    let digit = |i: usize| b.get(i).is_some_and(u8::is_ascii_digit);
    if b.len() == 7 {
        return Some(7);
    }
    match (b.get(4), b.get(5)) {
        (Some(b'-'), Some(b'W')) => {
            if b.len() < 8 || b.len() == 9 && b[8] == b'-' {
                return None;
            }
            Some(if b.get(8) == Some(&b'-') && !digit(10) {
                10
            } else {
                8
            })
        }
        (Some(b'-'), _) => Some(10),
        (Some(b'W'), _) => {
            let end = (7..b.len()).find(|i| !digit(*i)).unwrap_or(b.len().max(7));
            Some(if end < 9 {
                end
            } else if end % 2 == 0 {
                7
            } else {
                8
            })
        }
        _ => Some(8),
    }
}

/// A date of exactly the forms the Python's parser takes, as days since the epoch.
fn date_days(d: &str) -> Option<i64> {
    let at = |r: std::ops::Range<usize>| d.get(r).and_then(digits);
    let year = at(0..4)?;
    let hyphen = d.as_bytes().get(4) == Some(&b'-');
    let rest = usize::from(hyphen) + 4;
    if d.as_bytes().get(rest) == Some(&b'W') {
        let week = at(rest + 1..rest + 3)?;
        let after = rest + 3;
        if d.len() == after {
            return week_date(year, week, 1);
        }
        // `separator` has already placed the hyphen and the day
        let day_at = after + usize::from(hyphen);
        return week_date(year, week, d.get(day_at..=day_at).and_then(digits)?);
    }
    if d.len() != rest + 4 + usize::from(hyphen) || (hyphen && d.as_bytes()[7] != b'-') {
        return None;
    }
    calendar(
        year,
        at(rest..rest + 2)?,
        at(rest + 2 + usize::from(hyphen)..d.len())?,
    )
}

/// Hours, minutes, seconds, microseconds, and whether a stray character followed: `CPython`'s `parse_hh_mm_ss_ff`, whose stray character passes only
/// when a zone comes after it.
struct Clock {
    parts: [i64; 3],
    micros: i64,
    stray: bool,
}

fn clock(b: &[u8], end: usize) -> Option<Clock> {
    let two = |p: usize| digits(std::str::from_utf8(b.get(p..p + 2)?).ok()?);
    let (mut parts, mut p, mut colons) = ([0i64; 3], 0, false);
    for i in 0..3 {
        parts[i] = two(p)?;
        let c = b.get(p + 2).copied().unwrap_or(0);
        p += 3;
        if i == 0 {
            colons = c == b':';
        }
        if p >= end {
            return Some(Clock {
                parts,
                micros: 0,
                stray: c != 0,
            });
        }
        if colons && c == b':' {
            if i == 2 {
                return None;
            }
        } else if c == b'.' || c == b',' {
            if i < 2 {
                return None;
            }
            break;
        } else if colons {
            return None;
        } else {
            p -= 1;
        }
    }
    let take = (end - p).min(6);
    let text = std::str::from_utf8(b.get(p..p + take)?).ok()?;
    let micros = digits(text)? * 10i64.pow(u32::try_from(6 - take).unwrap_or(0));
    let mut q = p + take;
    while b.get(q).is_some_and(u8::is_ascii_digit) {
        q += 1;
    }
    Some(Clock {
        parts,
        micros,
        stray: b.get(q).is_some(),
    })
}

/// The moment in microseconds from midnight and the zone's offset in microseconds, none for a naive time.
fn time_part(bytes: &[u8]) -> Option<(i64, Option<i64>)> {
    let found = bytes.iter().position(|c| matches!(c, b'Z' | b'+' | b'-'));
    let tz = found.unwrap_or(bytes.len());
    let c = clock(bytes, tz)?;
    let [h, m, s] = c.parts;
    let micro =
        |parts: [i64; 3], us: i64| (parts[0] * 3600 + parts[1] * 60 + parts[2]) * 1_000_000 + us;
    let next_day = h == 24 && m == 0 && s == 0 && c.micros == 0;
    if !((0..24).contains(&h) || next_day) || !(0..60).contains(&m) || !(0..60).contains(&s) {
        return None;
    }
    let local = micro(c.parts, c.micros);
    if found.is_none() {
        return (!c.stray).then_some((local, None));
    }
    if bytes[tz] == b'Z' {
        return (bytes.len() == tz + 1).then_some((local, Some(0)));
    }
    let sign = if bytes[tz] == b'-' { -1 } else { 1 };
    let zone = clock(&bytes[tz + 1..], bytes.len() - tz - 1)?;
    let size = micro(zone.parts, zone.micros);
    (!zone.stray && size < 86_400 * 1_000_000).then_some((local, Some(sign * size)))
}

/// The machine's offset from UTC, in seconds, at a moment.
fn offset_at(moment: i64) -> i64 {
    let done = Command::new("date")
        .args(["-d", &format!("@{moment}"), "+%::z"])
        .output();
    let text = done
        .ok()
        .map(|o| String::from_utf8_lossy(&o.stdout).trim().to_owned())
        .unwrap_or_default();
    // `date` reads no moment past about the year 9999, and the calendar and the zone's rules repeat every 400 years
    if text.is_empty() && moment > 200_000_000_000 {
        return offset_at(moment - 12_622_780_800);
    }
    let cell = |r: std::ops::Range<usize>| text.get(r).and_then(digits).unwrap_or(0);
    let sign = if text.starts_with('-') { -1 } else { 1 };
    sign * (cell(1..3) * 3600 + cell(4..6) * 60 + cell(7..9))
}

/// The UTC moment of a local time, `CPython`'s `local_to_seconds` at `fold=0`: the earlier of a repeated hour, and past a skipped one.
fn local_to_utc(local: i64, offset_at: &dyn Fn(i64) -> i64) -> i64 {
    let a = offset_at(local);
    let u1 = local - a;
    let t1 = u1 + offset_at(u1);
    let b = if t1 == local {
        let other = offset_at(u1 - 86_400);
        if other == a {
            return u1;
        }
        other
    } else {
        t1 - u1
    };
    let u2 = local - b;
    if u2 + offset_at(u2) == local {
        u2
    } else if t1 == local {
        u1
    } else {
        u1.max(u2)
    }
}

/// The epoch seconds of `text`, none when Python's parser or its `.timestamp()` would refuse it.
#[must_use]
pub fn parse(text: &str) -> Option<f64> {
    const MICROS: i64 = 1_000_000;
    let at = separator(text.as_bytes())?;
    let day = date_days(text.get(..at)?)?;
    let after = text.get(at..)?;
    let time = after.chars().next().map_or("", |c| &after[c.len_utf8()..]);
    let (local, zone) = if after.is_empty() {
        (0, None)
    } else {
        time_part(time.as_bytes())?
    };
    // hour 24 is the next day's midnight, and 9999-12-31 has none
    if local == 86_400 * MICROS && day == epoch_days(9999, 12, 31) {
        return None;
    }
    let moment = day * 86_400 * MICROS + local;
    let whole = moment.div_euclid(MICROS);
    #[expect(
        clippy::cast_precision_loss,
        reason = "microseconds since the epoch; a time is only compared"
    )]
    let fine = moment.rem_euclid(MICROS) as f64 / 1e6;
    #[expect(
        clippy::cast_precision_loss,
        reason = "seconds since the epoch, far inside f64's exact range"
    )]
    match zone {
        Some(offset) => Some(
            (moment - offset).div_euclid(MICROS) as f64
                + (moment - offset).rem_euclid(MICROS) as f64 / 1e6,
        ),
        // the local-time conversion probes a day earlier, and a day before year 1 is out of range
        None => (whole - 86_400 >= epoch_days(1, 1, 1) * 86_400)
            .then(|| local_to_utc(whole, &offset_at) as f64 + fine),
    }
}

#[cfg(test)]
mod tests;
