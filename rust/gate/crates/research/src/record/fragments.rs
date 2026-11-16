//! Where a fragment of the REGISTRY lives and what its name means (`record/fragments.py`, features 258, 303; ported by feature 449 T144):
//! `sources/`, its front matter and closing, a group per `<prefix>-<heading id>.html` and the group's entries beside it. The prefixes are
//! gapped, counting by ten (the GM, 2026-09-20), so an insertion renumbers nothing. `free_prefix`, which nothing calls, is not ported.

use std::sync::LazyLock;

use fancy_regex::Regex;

use crate::{re, Error, Result};

/// The fragments that are not entries: placed by the assembly, never by sorting.
pub const FRONT: &str = "_front.html";
pub const TAIL: &str = "_tail.html";
pub const SECTION_DIGITS: usize = 3;
/// A registry entry's heading id is its key with this in front.
pub const WORK_PREFIX: &str = "work-";

static PREFIXED: LazyLock<Regex> = LazyLock::new(|| re(r"^(\d+)-(.+)\.html\n?\z"));

/// The directory a page's fragments live in: the registry `SOURCES.html` is `sources`, any other page its own name.
#[must_use]
pub fn page_dir(page_rel: &str) -> String {
    if page_rel == "SOURCES.html" {
        return "sources".to_owned();
    }
    page_rel
        .strip_suffix(".html")
        .unwrap_or(page_rel)
        .to_owned()
}

/// A registry entry's source key: `work-fei-1939` is `fei-1939`.
#[must_use]
pub fn key_of(heading_id: &str) -> &str {
    heading_id.strip_prefix(WORK_PREFIX).unwrap_or(heading_id)
}

/// The prefix of a name `<prefix>-<id>.html`, as Python's `int()` reads its digits; None for another name.
fn prefix(name: &str) -> Option<u128> {
    let c = PREFIXED.captures(name).ok().flatten()?;
    let value = c[1].chars().try_fold(0_u128, |n, d| {
        n.checked_mul(10)?
            .checked_add(u128::from(crate::digit_value(d)?))
    });
    Some(value.unwrap_or(u128::MAX))
}

/// The entry fragments of a directory, in prefix order (then by name); names that carry no prefix are left to the caller.
#[must_use]
pub fn ordered(names: &[String]) -> Vec<String> {
    let mut out: Vec<(u128, &String)> =
        names.iter().filter_map(|n| Some((prefix(n)?, n))).collect();
    out.sort();
    out.into_iter().map(|(_, n)| n.clone()).collect()
}

/// The prefix a fragment's name carries, as a number.
///
/// # Errors
/// A name of no `<prefix>-<id>.html` form.
pub fn position_of(name: &str) -> Result<u128> {
    prefix(name).ok_or_else(|| {
        Error::new(
            "ValueError",
            format!("{name}: a fragment of an ordered kind must be named <prefix>-<id>.html"),
        )
    })
}

#[cfg(test)]
mod tests;
